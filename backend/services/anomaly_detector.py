import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import statistics
from models import WeatherData, Anomaly, AnomalyCreate, SensorType, AnomalyStatus

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Simple anomaly detection service for weather data
    Uses statistical methods to detect outliers and validate data ranges
    """
    
    # Define normal ranges for different sensors
    SENSOR_RANGES = {
        SensorType.TEMPERATURE: {'min': -50, 'max': 60, 'unit': '°C'},
        SensorType.HUMIDITY: {'min': 0, 'max': 100, 'unit': '%'},
        SensorType.AIR_QUALITY: {'min': 0, 'max': 500, 'unit': 'AQI'},
        SensorType.PM25: {'min': 0, 'max': 500, 'unit': 'μg/m³'},
        SensorType.PM10: {'min': 0, 'max': 1000, 'unit': 'μg/m³'},
        SensorType.CO2: {'min': 300, 'max': 5000, 'unit': 'ppm'},
        SensorType.PRESSURE: {'min': 950, 'max': 1050, 'unit': 'hPa'}
    }
    
    def __init__(self):
        self.z_score_threshold = 3.0  # Standard deviations for outlier detection
        self.rapid_change_threshold = {
            SensorType.TEMPERATURE: 10.0,  # °C per hour
            SensorType.HUMIDITY: 30.0,     # % per hour
            SensorType.AIR_QUALITY: 100,    # AQI per hour
            SensorType.PRESSURE: 15.0       # hPa per hour
        }
    
    async def detect_anomalies(self, current_data: WeatherData, historical_data: List[WeatherData]) -> List[AnomalyCreate]:
        """
        Detect anomalies in current data compared to historical patterns
        """
        anomalies = []
        
        try:
            # Check range-based anomalies
            range_anomalies = self._check_range_anomalies(current_data)
            anomalies.extend(range_anomalies)
            
            # Check statistical anomalies if we have enough historical data
            if len(historical_data) >= 10:
                statistical_anomalies = self._check_statistical_anomalies(current_data, historical_data)
                anomalies.extend(statistical_anomalies)
            
            # Check rapid change anomalies
            if len(historical_data) >= 1:
                rapid_change_anomalies = self._check_rapid_changes(current_data, historical_data[-1])
                anomalies.extend(rapid_change_anomalies)
            
            logger.info(f"Detected {len(anomalies)} anomalies in current data")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def _check_range_anomalies(self, data: WeatherData) -> List[AnomalyCreate]:
        """Check if values are within acceptable ranges"""
        anomalies = []
        
        sensor_values = {
            SensorType.TEMPERATURE: data.temperature,
            SensorType.HUMIDITY: data.humidity,
            SensorType.AIR_QUALITY: data.air_quality,
            SensorType.PRESSURE: data.pressure
        }
        
        if data.pm25 is not None:
            sensor_values[SensorType.PM25] = data.pm25
        if data.pm10 is not None:
            sensor_values[SensorType.PM10] = data.pm10
        if data.co2 is not None:
            sensor_values[SensorType.CO2] = data.co2
        
        for sensor_type, value in sensor_values.items():
            if value is None:
                continue
                
            sensor_range = self.SENSOR_RANGES.get(sensor_type)
            if not sensor_range:
                continue
            
            if value < sensor_range['min']:
                anomalies.append(AnomalyCreate(
                    sensorType=sensor_type,
                    originalValue=value,
                    reason=f"Значення {value} {sensor_range['unit']} нижче мінімального порогу {sensor_range['min']} {sensor_range['unit']}",
                    status=AnomalyStatus.DETECTED,
                    confidence=1.0
                ))
            elif value > sensor_range['max']:
                anomalies.append(AnomalyCreate(
                    sensorType=sensor_type,
                    originalValue=value,
                    reason=f"Значення {value} {sensor_range['unit']} вище максимального порогу {sensor_range['max']} {sensor_range['unit']}",
                    status=AnomalyStatus.DETECTED,
                    confidence=1.0
                ))
        
        return anomalies
    
    def _check_statistical_anomalies(self, current_data: WeatherData, historical_data: List[WeatherData]) -> List[AnomalyCreate]:
        """Check for statistical outliers using Z-score"""
        anomalies = []
        
        # Prepare historical values for different sensors
        historical_values = {
            SensorType.TEMPERATURE: [d.temperature for d in historical_data if d.temperature is not None],
            SensorType.HUMIDITY: [d.humidity for d in historical_data if d.humidity is not None],
            SensorType.AIR_QUALITY: [d.air_quality for d in historical_data if d.air_quality is not None],
            SensorType.PRESSURE: [d.pressure for d in historical_data if d.pressure is not None]
        }
        
        # Add PM data if available
        pm25_values = [d.pm25 for d in historical_data if d.pm25 is not None]
        if pm25_values:
            historical_values[SensorType.PM25] = pm25_values
            
        pm10_values = [d.pm10 for d in historical_data if d.pm10 is not None]
        if pm10_values:
            historical_values[SensorType.PM10] = pm10_values
            
        co2_values = [d.co2 for d in historical_data if d.co2 is not None]
        if co2_values:
            historical_values[SensorType.CO2] = co2_values
        
        # Current values
        current_values = {
            SensorType.TEMPERATURE: current_data.temperature,
            SensorType.HUMIDITY: current_data.humidity,
            SensorType.AIR_QUALITY: current_data.air_quality,
            SensorType.PRESSURE: current_data.pressure
        }
        
        if current_data.pm25 is not None:
            current_values[SensorType.PM25] = current_data.pm25
        if current_data.pm10 is not None:
            current_values[SensorType.PM10] = current_data.pm10
        if current_data.co2 is not None:
            current_values[SensorType.CO2] = current_data.co2
        
        # Calculate Z-scores and detect anomalies
        for sensor_type, current_value in current_values.items():
            if current_value is None or sensor_type not in historical_values:
                continue
                
            hist_values = historical_values[sensor_type]
            if len(hist_values) < 10:  # Need minimum samples for statistical analysis
                continue
            
            try:
                mean_val = statistics.mean(hist_values)
                std_val = statistics.stdev(hist_values)
                
                if std_val == 0:  # Avoid division by zero
                    continue
                
                z_score = abs(current_value - mean_val) / std_val
                
                if z_score > self.z_score_threshold:
                    sensor_range = self.SENSOR_RANGES.get(sensor_type, {})
                    unit = sensor_range.get('unit', '')
                    
                    anomalies.append(AnomalyCreate(
                        sensorType=sensor_type,
                        originalValue=current_value,
                        reason=f"Статистичне відхилення: Z-score {z_score:.2f} (середнє: {mean_val:.1f} {unit})",
                        status=AnomalyStatus.DETECTED,
                        confidence=min(1.0, z_score / 5.0)  # Scale confidence based on Z-score
                    ))
                    
            except Exception as e:
                logger.error(f"Error calculating Z-score for {sensor_type}: {str(e)}")
                continue
        
        return anomalies
    
    def _check_rapid_changes(self, current_data: WeatherData, previous_data: WeatherData) -> List[AnomalyCreate]:
        """Check for rapid changes between consecutive readings"""
        anomalies = []
        
        # Calculate time difference (assume 1 hour if timestamps are equal)
        time_diff = (current_data.timestamp - previous_data.timestamp).total_seconds() / 3600
        if time_diff <= 0:
            time_diff = 1.0  # Default to 1 hour
        
        # Check rapid changes for different sensors
        changes = {
            SensorType.TEMPERATURE: abs(current_data.temperature - previous_data.temperature) / time_diff,
            SensorType.HUMIDITY: abs(current_data.humidity - previous_data.humidity) / time_diff,
            SensorType.AIR_QUALITY: abs(current_data.air_quality - previous_data.air_quality) / time_diff,
            SensorType.PRESSURE: abs(current_data.pressure - previous_data.pressure) / time_diff
        }
        
        for sensor_type, rate_of_change in changes.items():
            threshold = self.rapid_change_threshold.get(sensor_type)
            if threshold and rate_of_change > threshold:
                sensor_range = self.SENSOR_RANGES.get(sensor_type, {})
                unit = sensor_range.get('unit', '')
                
                anomalies.append(AnomalyCreate(
                    sensorType=sensor_type,
                    originalValue=getattr(current_data, sensor_type.value),
                    reason=f"Різка зміна показника: {rate_of_change:.1f} {unit}/год (поріг: {threshold} {unit}/год)",
                    status=AnomalyStatus.DETECTED,
                    confidence=min(1.0, rate_of_change / (threshold * 2))
                ))
        
        return anomalies
    
    def filter_anomalous_value(self, original_value: float, sensor_type: SensorType, historical_data: List[float]) -> Tuple[float, str]:
        """
        Apply filtering to anomalous values
        Returns filtered value and reason for filtering
        """
        try:
            sensor_range = self.SENSOR_RANGES.get(sensor_type)
            if not sensor_range:
                return original_value, "Невідомий тип сенсора"
            
            # If value is out of absolute range, clamp it
            if original_value < sensor_range['min']:
                filtered_value = sensor_range['min']
                return filtered_value, f"Обмежено мінімальним значенням {sensor_range['min']} {sensor_range['unit']}"
            elif original_value > sensor_range['max']:
                filtered_value = sensor_range['max']
                return filtered_value, f"Обмежено максимальним значенням {sensor_range['max']} {sensor_range['unit']}"
            
            # If we have historical data, use median filtering for statistical outliers
            if len(historical_data) >= 5:
                median_value = statistics.median(historical_data)
                mean_value = statistics.mean(historical_data)
                
                # Use median if the original value is too far from historical patterns
                std_dev = statistics.stdev(historical_data) if len(historical_data) > 1 else 0
                if std_dev > 0 and abs(original_value - mean_value) > 3 * std_dev:
                    return median_value, f"Замінено медіанним значенням через статистичне відхилення"
            
            return original_value, "Значення в межах норми"
            
        except Exception as e:
            logger.error(f"Error filtering anomalous value: {str(e)}")
            return original_value, f"Помилка фільтрації: {str(e)}"

# Global instance
anomaly_detector = AnomalyDetector()
