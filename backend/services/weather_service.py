import aiohttp
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class WeatherAPIService:
    def __init__(self):
        self.api_key = os.environ.get('WEATHER_API_KEY')
        self.base_url = os.environ.get('WEATHER_API_URL', 'http://api.weatherapi.com/v1')
        self.session = None
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_current_weather(self, location: str = "Kyiv") -> Optional[Dict[str, Any]]:
        """
        Get current weather data from WeatherAPI
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': location,
                'aqi': 'yes'  # Include air quality data
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._transform_current_data(data)
                else:
                    error_text = await response.text()
                    logger.error(f"Weather API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching current weather: {str(e)}")
            return None
    
    async def get_historical_weather(self, location: str = "Kyiv", date: str = None) -> Optional[Dict[str, Any]]:
        """
        Get historical weather data for a specific date
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/history.json"
            params = {
                'key': self.api_key,
                'q': location,
                'dt': date,
                'aqi': 'yes'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._transform_historical_data(data)
                else:
                    error_text = await response.text()
                    logger.error(f"Weather API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching historical weather: {str(e)}")
            return None
    
    def _transform_current_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform WeatherAPI current data to our format"""
        try:
            current = data.get('current', {})
            air_quality = current.get('air_quality', {})
            location_data = data.get('location', {})
            
            # Calculate simple air quality index from available data
            # WeatherAPI provides various pollutant readings, we'll create a simple index
            aqi_value = self._calculate_aqi(air_quality)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'temperature': current.get('temp_c', 0.0),
                'humidity': current.get('humidity', 0.0),
                'airQuality': aqi_value,
                'pm25': air_quality.get('pm2_5'),
                'pm10': air_quality.get('pm10'),
                'co2': int(air_quality.get('co', 0) * 1000) if air_quality.get('co') else None,  # Convert mg/m3 to ppm roughly
                'pressure': current.get('pressure_mb', 1013.0),
                'windSpeed': current.get('wind_kph', 0.0) / 3.6,  # Convert kph to m/s
                'windDirection': current.get('wind_degree', 0),
                'uvIndex': current.get('uv'),
                'visibility': current.get('vis_km'),
                'location': f"{location_data.get('name', '')}, {location_data.get('country', '')}",
                'rawData': data
            }
        except Exception as e:
            logger.error(f"Error transforming current data: {str(e)}")
            return {}
    
    def _transform_historical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform WeatherAPI historical data to our format"""
        try:
            forecast = data.get('forecast', {})
            forecastday = forecast.get('forecastday', [])
            
            if not forecastday:
                return {}
            
            day_data = forecastday[0]
            day = day_data.get('day', {})
            location_data = data.get('location', {})
            
            return {
                'date': day_data.get('date'),
                'avgTemperature': day.get('avgtemp_c', 0.0),
                'minTemperature': day.get('mintemp_c', 0.0),
                'maxTemperature': day.get('maxtemp_c', 0.0),
                'avgHumidity': day.get('avghumidity', 0.0),
                'avgAirQuality': 50,  # Default value as historical AQI might not be available
                'location': f"{location_data.get('name', '')}, {location_data.get('country', '')}",
                'rawData': data
            }
        except Exception as e:
            logger.error(f"Error transforming historical data: {str(e)}")
            return {}
    
    def _calculate_aqi(self, air_quality: Dict[str, Any]) -> int:
        """
        Calculate a simple Air Quality Index from available pollutant data
        This is a simplified calculation based on PM2.5, PM10, and other available data
        """
        try:
            pm25 = air_quality.get('pm2_5', 0)
            pm10 = air_quality.get('pm10', 0)
            no2 = air_quality.get('no2', 0)
            o3 = air_quality.get('o3', 0)
            so2 = air_quality.get('so2', 0)
            co = air_quality.get('co', 0)
            
            # Simple AQI calculation (this is a basic approximation)
            aqi = 0
            
            # PM2.5 contribution (0-500 scale)
            if pm25 <= 12:
                aqi = max(aqi, int(pm25 * 50 / 12))
            elif pm25 <= 35.4:
                aqi = max(aqi, int(50 + (pm25 - 12) * 50 / 23.4))
            else:
                aqi = max(aqi, min(500, int(100 + (pm25 - 35.4) * 100 / 55.4)))
            
            # PM10 contribution
            if pm10 <= 54:
                pm10_aqi = int(pm10 * 50 / 54)
            elif pm10 <= 154:
                pm10_aqi = int(50 + (pm10 - 54) * 50 / 100)
            else:
                pm10_aqi = min(500, int(100 + (pm10 - 154) * 100 / 250))
            
            aqi = max(aqi, pm10_aqi)
            
            # Ensure AQI is within reasonable bounds
            return max(1, min(500, aqi)) if aqi > 0 else 25  # Default to 25 if no data
            
        except Exception as e:
            logger.error(f"Error calculating AQI: {str(e)}")
            return 50  # Default moderate value

# Global instance
weather_service = WeatherAPIService()
