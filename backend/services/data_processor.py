import logging
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from models import WeatherData, WeatherDataCreate, Anomaly, ProcessingLog, ProcessingLogCreate, LogStatus, DailyStats
from services.anomaly_detector import anomaly_detector
from services.weather_service import weather_service

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Service for processing weather data, detecting anomalies, and managing data flow
    """
    
    def __init__(self, db):
        self.db = db
        self.weather_collection: AsyncIOMotorCollection = db.weather_data
        self.anomaly_collection: AsyncIOMotorCollection = db.anomalies
        self.logs_collection: AsyncIOMotorCollection = db.processing_logs
        self.daily_stats_collection: AsyncIOMotorCollection = db.daily_stats
    
    async def process_weather_data(self, location: str = "Kyiv") -> Optional[WeatherData]:
        """
        Main processing pipeline: fetch -> validate -> filter -> store
        """
        start_time = datetime.utcnow()
        processing_steps = []
        
        try:
            # Step 1: Fetch data from Weather API
            await self._log_action("Отримання даних з Weather API", LogStatus.SUCCESS, "Початок запиту до API")
            
            raw_weather_data = await weather_service.get_current_weather(location)
            if not raw_weather_data:
                await self._log_action("Отримання даних з Weather API", LogStatus.ERROR, "Не вдалося отримати дані з API")
                return None
            
            processing_steps.append("API запит виконано")
            
            # Step 2: Create weather data object
            weather_data = WeatherData(**raw_weather_data)
            processing_steps.append("Дані структуровано")
            
            # Step 3: Get historical data for anomaly detection
            historical_data = await self._get_recent_historical_data(hours=24)
            processing_steps.append(f"Отримано {len(historical_data)} історичних записів")
            
            # Step 4: Detect anomalies
            anomalies = await anomaly_detector.detect_anomalies(weather_data, historical_data)
            processing_steps.append(f"Виявлено {len(anomalies)} аномалій")
            
            # Step 5: Process and filter anomalies
            filtered_data = await self._process_anomalies(weather_data, anomalies, historical_data)
            processing_steps.append("Аномалії оброблено")
            
            # Step 6: Store processed data
            await self._store_weather_data(filtered_data)
            processing_steps.append("Дані збережено в БД")
            
            # Step 7: Store anomalies
            if anomalies:
                await self._store_anomalies(anomalies)
                processing_steps.append(f"Збережено {len(anomalies)} аномалій")
            
            # Step 8: Update daily statistics
            await self._update_daily_stats(filtered_data.timestamp.date())
            processing_steps.append("Статистику оновлено")
            
            # Log successful processing
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._log_action(
                "Повний цикл обробки даних", 
                LogStatus.SUCCESS, 
                f"Успішно оброблено дані. Кроки: {' -> '.join(processing_steps)}",
                duration_ms=int(duration),
                data_count=1
            )
            
            return filtered_data
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = f"Помилка обробки даних: {str(e)}"
            logger.error(error_msg)
            await self._log_action(
                "Повний цикл обробки даних", 
                LogStatus.ERROR, 
                error_msg,
                duration_ms=int(duration)
            )
            return None
    
    async def _get_recent_historical_data(self, hours: int = 24) -> List[WeatherData]:
        """Get recent historical data for analysis"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cursor = self.weather_collection.find(
                {"timestamp": {"$gte": cutoff_time}},
                sort=[("timestamp", -1)],
                limit=100
            )
            
            data = await cursor.to_list(length=100)
            return [WeatherData(**item) for item in data]
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return []
    
    async def _process_anomalies(self, weather_data: WeatherData, anomalies: List[Any], historical_data: List[WeatherData]) -> WeatherData:
        """Process detected anomalies and apply filtering"""
        try:
            filtered_data = weather_data.copy()
            
            for anomaly in anomalies:
                sensor_type = anomaly.sensor_type
                original_value = anomaly.original_value
                
                # Get historical values for this sensor type
                historical_values = []
                for hist_data in historical_data:
                    if sensor_type.value == "temperature":
                        historical_values.append(hist_data.temperature)
                    elif sensor_type.value == "humidity":
                        historical_values.append(hist_data.humidity)
                    elif sensor_type.value == "airQuality":
                        historical_values.append(hist_data.air_quality)
                    elif sensor_type.value == "pressure":
                        historical_values.append(hist_data.pressure)
                    elif sensor_type.value == "pm25" and hist_data.pm25 is not None:
                        historical_values.append(hist_data.pm25)
                    elif sensor_type.value == "pm10" and hist_data.pm10 is not None:
                        historical_values.append(hist_data.pm10)
                    elif sensor_type.value == "co2" and hist_data.co2 is not None:
                        historical_values.append(hist_data.co2)
                
                # Filter the anomalous value
                filtered_value, filter_reason = anomaly_detector.filter_anomalous_value(
                    original_value, sensor_type, historical_values
                )
                
                # Apply the filtered value to the data
                if sensor_type.value == "temperature":
                    filtered_data.temperature = filtered_value
                elif sensor_type.value == "humidity":
                    filtered_data.humidity = filtered_value
                elif sensor_type.value == "airQuality":
                    filtered_data.air_quality = int(filtered_value)
                elif sensor_type.value == "pressure":
                    filtered_data.pressure = filtered_value
                elif sensor_type.value == "pm25":
                    filtered_data.pm25 = filtered_value
                elif sensor_type.value == "pm10":
                    filtered_data.pm10 = filtered_value
                elif sensor_type.value == "co2":
                    filtered_data.co2 = int(filtered_value)
                
                # Update anomaly with filtered value and status
                anomaly.filtered_value = filtered_value
                anomaly.status = "filtered" if filtered_value != original_value else "verified"
                anomaly.reason += f" | Фільтрація: {filter_reason}"
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error processing anomalies: {str(e)}")
            return weather_data
    
    async def _store_weather_data(self, weather_data: WeatherData):
        """Store processed weather data in database"""
        try:
            data_dict = weather_data.dict()
            await self.weather_collection.insert_one(data_dict)
            logger.info(f"Stored weather data with ID: {weather_data.id}")
        except Exception as e:
            logger.error(f"Error storing weather data: {str(e)}")
            raise
    
    async def _store_anomalies(self, anomalies: List[Any]):
        """Store detected anomalies in database"""
        try:
            if anomalies:
                anomaly_dicts = [anomaly.dict() for anomaly in anomalies]
                await self.anomaly_collection.insert_many(anomaly_dicts)
                logger.info(f"Stored {len(anomalies)} anomalies")
        except Exception as e:
            logger.error(f"Error storing anomalies: {str(e)}")
            raise
    
    async def _update_daily_stats(self, date):
        """Update daily statistics for the given date"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            # Get all data for the day
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_date, "$lt": end_date}}},
                {"$group": {
                    "_id": None,
                    "avgTemperature": {"$avg": "$temperature"},
                    "minTemperature": {"$min": "$temperature"},
                    "maxTemperature": {"$max": "$temperature"},
                    "avgHumidity": {"$avg": "$humidity"},
                    "avgAirQuality": {"$avg": "$air_quality"},
                    "avgPressure": {"$avg": "$pressure"},
                    "dataPointsCount": {"$sum": 1}
                }}
            ]
            
            result = await self.weather_collection.aggregate(pipeline).to_list(1)
            
            if result:
                stats_data = result[0]
                
                # Count anomalies for the day
                anomaly_count = await self.anomaly_collection.count_documents({
                    "timestamp": {"$gte": start_date, "$lt": end_date}
                })
                
                daily_stats = DailyStats(
                    date=date_str,
                    avgTemperature=round(stats_data["avgTemperature"], 1),
                    minTemperature=round(stats_data["minTemperature"], 1),
                    maxTemperature=round(stats_data["maxTemperature"], 1),
                    avgHumidity=round(stats_data["avgHumidity"], 1),
                    avgAirQuality=round(stats_data["avgAirQuality"], 1),
                    avgPressure=round(stats_data["avgPressure"], 1),
                    dataPointsCount=stats_data["dataPointsCount"],
                    anomaliesCount=anomaly_count
                )
                
                # Upsert daily stats
                await self.daily_stats_collection.replace_one(
                    {"date": date_str},
                    daily_stats.dict(),
                    upsert=True
                )
                
                logger.info(f"Updated daily stats for {date_str}")
                
        except Exception as e:
            logger.error(f"Error updating daily stats: {str(e)}")
    
    async def _log_action(self, action: str, status: LogStatus, details: str, duration_ms: Optional[int] = None, data_count: Optional[int] = None):
        """Log processing action"""
        try:
            log_entry = ProcessingLogCreate(
                action=action,
                status=status,
                details=details,
                durationMs=duration_ms,
                dataCount=data_count
            )
            
            log_dict = ProcessingLog(**log_entry.dict()).dict()
            await self.logs_collection.insert_one(log_dict)
            
        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")
    
    async def export_to_csv(self, data_type: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Export data to CSV format"""
        try:
            if data_type == "hourly":
                return await self._export_hourly_data_csv(start_date, end_date)
            elif data_type == "daily":
                return await self._export_daily_data_csv(start_date, end_date)
            elif data_type == "anomalies":
                return await self._export_anomalies_csv(start_date, end_date)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
                
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            raise
    
    async def _export_hourly_data_csv(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """Export hourly weather data to CSV"""
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.weather_collection.find(query).sort("timestamp", -1).limit(1000)
        data = await cursor.to_list(1000)
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Час', 'Температура (°C)', 'Вологість (%)', 'Якість повітря',
            'PM2.5 (μg/m³)', 'PM10 (μg/m³)', 'CO2 (ppm)', 'Тиск (hPa)',
            'Швидкість вітру (м/с)', 'Напрямок вітру (°)', 'Локація'
        ])
        
        # Write data
        for item in data:
            writer.writerow([
                datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if isinstance(item['timestamp'], str) else item['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                round(item.get('temperature', 0), 1),
                round(item.get('humidity', 0), 1),
                item.get('air_quality', 0),
                round(item.get('pm25', 0), 1) if item.get('pm25') else '',
                round(item.get('pm10', 0), 1) if item.get('pm10') else '',
                item.get('co2', '') if item.get('co2') else '',
                round(item.get('pressure', 0), 1),
                round(item.get('wind_speed', 0), 1),
                item.get('wind_direction', 0),
                item.get('location', '')
            ])
        
        return output.getvalue()
    
    async def _export_daily_data_csv(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """Export daily statistics to CSV"""
        query = {}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date.strftime("%Y-%m-%d")
            if end_date:
                date_query["$lte"] = end_date.strftime("%Y-%m-%d")
            query["date"] = date_query
        
        cursor = self.daily_stats_collection.find(query).sort("date", -1).limit(100)
        data = await cursor.to_list(100)
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Дата', 'Середня температура (°C)', 'Мін. температура (°C)', 'Макс. температура (°C)',
            'Середня вологість (%)', 'Середня якість повітря', 'Середній тиск (hPa)',
            'Кількість записів', 'Кількість аномалій'
        ])
        
        # Write data
        for item in data:
            writer.writerow([
                item.get('date', ''),
                round(item.get('avg_temperature', 0), 1),
                round(item.get('min_temperature', 0), 1),
                round(item.get('max_temperature', 0), 1),
                round(item.get('avg_humidity', 0), 1),
                round(item.get('avg_air_quality', 0), 1),
                round(item.get('avg_pressure', 0), 1),
                item.get('data_points_count', 0),
                item.get('anomalies_count', 0)
            ])
        
        return output.getvalue()
    
    async def _export_anomalies_csv(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """Export anomalies to CSV"""
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.anomaly_collection.find(query).sort("timestamp", -1).limit(500)
        data = await cursor.to_list(500)
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Час', 'Тип сенсора', 'Оригінальне значення', 'Відфільтроване значення',
            'Причина', 'Статус', 'Достовірність'
        ])
        
        # Write data
        for item in data:
            writer.writerow([
                item.get('id', ''),
                datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if isinstance(item['timestamp'], str) else item['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                item.get('sensor_type', ''),
                item.get('original_value', ''),
                item.get('filtered_value', '') if item.get('filtered_value') else '',
                item.get('reason', ''),
                item.get('status', ''),
                round(item.get('confidence', 0), 2) if item.get('confidence') else ''
            ])
        
        return output.getvalue()

# Global instance will be created in server.py
data_processor = None
