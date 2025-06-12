from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    AIR_QUALITY = "airQuality"
    PM25 = "pm25"
    PM10 = "pm10"
    CO2 = "co2"
    PRESSURE = "pressure"

class AnomalyStatus(str, Enum):
    DETECTED = "detected"
    FILTERED = "filtered"
    VERIFIED = "verified"

class LogStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class WeatherData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temperature: float
    humidity: float
    air_quality: int = Field(alias="airQuality")
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co2: Optional[int] = None
    pressure: float
    wind_speed: float = Field(alias="windSpeed")
    wind_direction: int = Field(alias="windDirection")
    uv_index: Optional[int] = Field(alias="uvIndex", default=None)
    visibility: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = Field(alias="rawData", default=None)
    location: Optional[str] = None
    
    class Config:
        validate_by_name = True

class WeatherDataCreate(BaseModel):
    temperature: float
    humidity: float
    air_quality: int = Field(alias="airQuality")
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co2: Optional[int] = None
    pressure: float
    wind_speed: float = Field(alias="windSpeed")
    wind_direction: int = Field(alias="windDirection")
    uv_index: Optional[int] = Field(alias="uvIndex", default=None)
    visibility: Optional[float] = None
    location: Optional[str] = None
    
    class Config:
        validate_by_name = True

class Anomaly(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sensor_type: SensorType = Field(alias="sensorType")
    original_value: float = Field(alias="originalValue")
    filtered_value: Optional[float] = Field(alias="filteredValue", default=None)
    reason: str
    status: AnomalyStatus
    confidence: Optional[float] = None
    
    class Config:
        validate_by_name = True

class AnomalyCreate(BaseModel):
    sensor_type: SensorType = Field(alias="sensorType")
    original_value: float = Field(alias="originalValue")
    filtered_value: Optional[float] = Field(alias="filteredValue", default=None)
    reason: str
    status: AnomalyStatus
    confidence: Optional[float] = None
    
    class Config:
        validate_by_name = True

class ProcessingLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    status: LogStatus
    details: str
    duration_ms: Optional[int] = Field(alias="durationMs", default=None)
    data_count: Optional[int] = Field(alias="dataCount", default=None)
    
    class Config:
        validate_by_name = True

class ProcessingLogCreate(BaseModel):
    action: str
    status: LogStatus
    details: str
    duration_ms: Optional[int] = Field(alias="durationMs", default=None)
    data_count: Optional[int] = Field(alias="dataCount", default=None)
    
    class Config:
        validate_by_name = True

class DataFilter(BaseModel):
    start_date: Optional[datetime] = Field(alias="startDate", default=None)
    end_date: Optional[datetime] = Field(alias="endDate", default=None)
    limit: Optional[int] = 100
    sensor_types: Optional[List[SensorType]] = Field(alias="sensorTypes", default=None)
    
    class Config:
        validate_by_name = True

class ExportRequest(BaseModel):
    data_type: str = Field(alias="dataType")  # "hourly", "daily", "anomalies"
    start_date: Optional[datetime] = Field(alias="startDate", default=None)
    end_date: Optional[datetime] = Field(alias="endDate", default=None)
    format: str = "csv"
    
    class Config:
        validate_by_name = True

class DailyStats(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # YYYY-MM-DD format
    avg_temperature: float = Field(alias="avgTemperature")
    min_temperature: float = Field(alias="minTemperature")
    max_temperature: float = Field(alias="maxTemperature")
    avg_humidity: float = Field(alias="avgHumidity")
    avg_air_quality: float = Field(alias="avgAirQuality")
    avg_pressure: float = Field(alias="avgPressure")
    data_points_count: int = Field(alias="dataPointsCount")
    anomalies_count: int = Field(alias="anomaliesCount")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    
    class Config:
        validate_by_name = True

class CurrentConditions(BaseModel):
    temperature: float
    humidity: float
    air_quality: int = Field(alias="airQuality")
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co2: Optional[int] = None
    pressure: float
    wind_speed: float = Field(alias="windSpeed")
    wind_direction: int = Field(alias="windDirection")
    uv_index: Optional[int] = Field(alias="uvIndex", default=None)
    visibility: Optional[float] = None
    last_updated: datetime = Field(alias="lastUpdated")
    location: Optional[str] = None
    
    class Config:
        validate_by_name = True
