from fastapi import FastAPI, APIRouter, HTTPException, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from io import StringIO
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

# Import models and services
from .models import (
    WeatherData, WeatherDataCreate, CurrentConditions, DailyStats,
    Anomaly, ProcessingLog, DataFilter, ExportRequest
)
from .services.weather_service import weather_service
from .services.data_processor import DataProcessor
from .services.anomaly_detector import anomaly_detector

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize data processor
data_processor = DataProcessor(db)

# Create the main app without a prefix
app = FastAPI(title="Air Quality Monitor API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task for continuous data collection
async def continuous_data_collection():
    """Background task to collect data every hour"""
    while True:
        try:
            logger.info("Starting scheduled data collection...")
            result = await data_processor.process_weather_data("Kyiv")
            if result:
                logger.info(f"Successfully processed weather data: {result.id}")
            else:
                logger.warning("Failed to process weather data")
        except Exception as e:
            logger.error(f"Error in continuous data collection: {str(e)}")
        
        # Wait for 1 hour (3600 seconds) - for demo, let's make it 5 minutes
        await asyncio.sleep(300)  # 5 minutes for demo purposes

# Start background task on startup
@app.on_event("startup")
async def startup_event():
    # Start background data collection
    asyncio.create_task(continuous_data_collection())
    logger.info("Started continuous data collection background task")

@app.on_event("shutdown")
async def shutdown_db_client():
    await weather_service.close()
    client.close()

# API Routes

@api_router.get("/")
async def root():
    return {"message": "Air Quality Monitor API", "status": "active", "version": "1.0.0"}

@api_router.get("/current", response_model=CurrentConditions)
async def get_current_conditions():
    """Get current weather and air quality conditions"""
    try:
        # Get the most recent data from database
        latest_data = await db.weather_data.find_one(
            {},
            sort=[("timestamp", -1)]
        )
        
        if not latest_data:
            # If no data in DB, fetch from API directly
            logger.info("No data in database, fetching from API...")
            result = await data_processor.process_weather_data("Kyiv")
            if not result:
                raise HTTPException(status_code=503, detail="Unable to fetch weather data")
            latest_data = result.dict()
        
        # Transform to CurrentConditions format
        current_conditions = CurrentConditions(
            temperature=latest_data.get('temperature', 0),
            humidity=latest_data.get('humidity', 0),
            airQuality=latest_data.get('air_quality', 0),
            pm25=latest_data.get('pm25'),
            pm10=latest_data.get('pm10'),
            co2=latest_data.get('co2'),
            pressure=latest_data.get('pressure', 1013),
            windSpeed=latest_data.get('wind_speed', 0),
            windDirection=latest_data.get('wind_direction', 0),
            uvIndex=latest_data.get('uv_index'),
            visibility=latest_data.get('visibility'),
            lastUpdated=latest_data.get('timestamp', datetime.utcnow()),
            location=latest_data.get('location', 'Kyiv, Ukraine')
        )
        
        return current_conditions
        
    except Exception as e:
        logger.error(f"Error getting current conditions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/hourly", response_model=List[WeatherData])
async def get_hourly_data(hours: int = 24, limit: int = 100):
    """Get hourly weather data for the specified number of hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        cursor = db.weather_data.find(
            {"timestamp": {"$gte": cutoff_time}},
            sort=[("timestamp", -1)],
            limit=limit
        )
        
        data = await cursor.to_list(limit)
        return [WeatherData(**item) for item in data]
        
    except Exception as e:
        logger.error(f"Error getting hourly data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(days: int = 30):
    """Get daily statistics for the specified number of days"""
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor = db.daily_stats.find(
            {"date": {"$gte": cutoff_date}},
            sort=[("date", -1)],
            limit=days
        )
        
        data = await cursor.to_list(days)
        return [DailyStats(**item) for item in data]
        
    except Exception as e:
        logger.error(f"Error getting daily stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/anomalies", response_model=List[Anomaly])
async def get_anomalies(hours: int = 24, limit: int = 100):
    """Get detected anomalies for the specified time period"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        cursor = db.anomalies.find(
            {"timestamp": {"$gte": cutoff_time}},
            sort=[("timestamp", -1)],
            limit=limit
        )
        
        data = await cursor.to_list(limit)
        return [Anomaly(**item) for item in data]
        
    except Exception as e:
        logger.error(f"Error getting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/logs", response_model=List[ProcessingLog])
async def get_processing_logs(hours: int = 24, limit: int = 50):
    """Get processing logs for the specified time period"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        cursor = db.processing_logs.find(
            {"timestamp": {"$gte": cutoff_time}},
            sort=[("timestamp", -1)],
            limit=limit
        )
        
        data = await cursor.to_list(limit)
        return [ProcessingLog(**item) for item in data]
        
    except Exception as e:
        logger.error(f"Error getting processing logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.post("/collect")
async def trigger_data_collection(background_tasks: BackgroundTasks, location: str = "Kyiv"):
    """Manually trigger data collection"""
    try:
        # Run data collection in background
        background_tasks.add_task(data_processor.process_weather_data, location)
        
        return {
            "message": "Data collection triggered",
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering data collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.post("/export")
async def export_data(export_request: ExportRequest):
    """Export data in CSV format"""
    try:
        csv_data = await data_processor.export_to_csv(
            export_request.data_type,
            export_request.start_date,
            export_request.end_date
        )
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No data found for the specified criteria")
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{export_request.data_type}_data_{timestamp}.csv"
        
        # Return CSV as streaming response
        def generate_csv():
            yield csv_data
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.command("ping")
        
        # Check last data collection
        latest_data = await db.weather_data.find_one({}, sort=[("timestamp", -1)])
        last_collection = None
        if latest_data:
            last_collection = latest_data.get('timestamp')
        
        # Check Weather API
        weather_status = "unknown"
        try:
            test_data = await weather_service.get_current_weather("Kyiv")
            weather_status = "connected" if test_data else "error"
        except:
            weather_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "weather_api": weather_status,
            "last_collection": last_collection.isoformat() if last_collection else None,
            "services": {
                "data_processor": "active",
                "anomaly_detector": "active",
                "weather_service": weather_status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
