#!/usr/bin/env python3
import requests
import json
import time
import csv
import io
import unittest
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://603cffb3-cf78-4516-9298-23754fd02885.preview.emergentagent.com/api"
WEATHER_API_KEY = "f773e6553be7425b96b125733251206"

class AirQualityMonitoringBackendTest(unittest.TestCase):
    """
    Comprehensive test suite for the Air Quality Monitoring backend system.
    Tests all API endpoints, data processing, anomaly detection, and export functionality.
    """
    
    def setUp(self):
        """Set up test environment"""
        self.api_base_url = BACKEND_URL
        print(f"Testing backend at: {self.api_base_url}")
        
    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n=== Testing Health Check Endpoint ===")
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200, "Health check endpoint should return 200")
        
        data = response.json()
        print(f"Health check response: {json.dumps(data, indent=2)}")
        
        # Verify response structure
        self.assertIn("status", data, "Health check should include status")
        self.assertIn("timestamp", data, "Health check should include timestamp")
        self.assertIn("database", data, "Health check should include database status")
        self.assertIn("weather_api", data, "Health check should include weather API status")
        self.assertIn("services", data, "Health check should include services status")
        
        # Verify services are running
        services = data.get("services", {})
        self.assertEqual(services.get("data_processor"), "active", "Data processor should be active")
        self.assertEqual(services.get("anomaly_detector"), "active", "Anomaly detector should be active")
        
        print("✅ Health check endpoint is working correctly")
        
    def test_02_current_conditions(self):
        """Test the current conditions endpoint"""
        print("\n=== Testing Current Conditions Endpoint ===")
        response = requests.get(f"{self.api_base_url}/current")
        self.assertEqual(response.status_code, 200, "Current conditions endpoint should return 200")
        
        data = response.json()
        print(f"Current conditions: {json.dumps(data, indent=2)}")
        
        # Verify response structure
        self.assertIn("temperature", data, "Response should include temperature")
        self.assertIn("humidity", data, "Response should include humidity")
        self.assertIn("airQuality", data, "Response should include airQuality")
        self.assertIn("pressure", data, "Response should include pressure")
        self.assertIn("windSpeed", data, "Response should include windSpeed")
        self.assertIn("windDirection", data, "Response should include windDirection")
        self.assertIn("lastUpdated", data, "Response should include lastUpdated")
        self.assertIn("location", data, "Response should include location")
        
        # Verify data types and ranges
        self.assertIsInstance(data["temperature"], (int, float), "Temperature should be a number")
        self.assertIsInstance(data["humidity"], (int, float), "Humidity should be a number")
        self.assertIsInstance(data["airQuality"], int, "Air quality should be an integer")
        self.assertIsInstance(data["pressure"], (int, float), "Pressure should be a number")
        
        # Check value ranges
        self.assertGreaterEqual(data["humidity"], 0, "Humidity should be >= 0")
        self.assertLessEqual(data["humidity"], 100, "Humidity should be <= 100")
        self.assertGreaterEqual(data["airQuality"], 0, "Air quality should be >= 0")
        self.assertGreaterEqual(data["pressure"], 950, "Pressure should be >= 950 hPa")
        self.assertLessEqual(data["pressure"], 1050, "Pressure should be <= 1050 hPa")
        
        print("✅ Current conditions endpoint is working correctly")
        
    def test_03_hourly_data(self):
        """Test the hourly data endpoint"""
        print("\n=== Testing Hourly Data Endpoint ===")
        response = requests.get(f"{self.api_base_url}/hourly?hours=24&limit=10")
        self.assertEqual(response.status_code, 200, "Hourly data endpoint should return 200")
        
        data = response.json()
        print(f"Received {len(data)} hourly data points")
        if data:
            print(f"Sample hourly data: {json.dumps(data[0], indent=2)}")
        
        # Verify data structure if data exists
        if data:
            sample = data[0]
            self.assertIn("id", sample, "Hourly data should include id")
            self.assertIn("timestamp", sample, "Hourly data should include timestamp")
            self.assertIn("temperature", sample, "Hourly data should include temperature")
            self.assertIn("humidity", sample, "Hourly data should include humidity")
            self.assertIn("air_quality", sample, "Hourly data should include air_quality")
            self.assertIn("pressure", sample, "Hourly data should include pressure")
            self.assertIn("wind_speed", sample, "Hourly data should include wind_speed")
            self.assertIn("wind_direction", sample, "Hourly data should include wind_direction")
            
            # Check data types
            self.assertIsInstance(sample["temperature"], (int, float), "Temperature should be a number")
            self.assertIsInstance(sample["humidity"], (int, float), "Humidity should be a number")
            self.assertIsInstance(sample["air_quality"], int, "Air quality should be an integer")
            
        print("✅ Hourly data endpoint is working correctly")
        
    def test_04_daily_stats(self):
        """Test the daily statistics endpoint"""
        print("\n=== Testing Daily Statistics Endpoint ===")
        response = requests.get(f"{self.api_base_url}/daily?days=30")
        self.assertEqual(response.status_code, 200, "Daily stats endpoint should return 200")
        
        data = response.json()
        print(f"Received {len(data)} daily statistics records")
        if data:
            print(f"Sample daily stats: {json.dumps(data[0], indent=2)}")
        
        # Verify data structure if data exists
        if data:
            sample = data[0]
            self.assertIn("id", sample, "Daily stats should include id")
            self.assertIn("date", sample, "Daily stats should include date")
            self.assertIn("avgTemperature", sample, "Daily stats should include avgTemperature")
            self.assertIn("minTemperature", sample, "Daily stats should include minTemperature")
            self.assertIn("maxTemperature", sample, "Daily stats should include maxTemperature")
            self.assertIn("avgHumidity", sample, "Daily stats should include avgHumidity")
            self.assertIn("avgAirQuality", sample, "Daily stats should include avgAirQuality")
            self.assertIn("dataPointsCount", sample, "Daily stats should include dataPointsCount")
            self.assertIn("anomaliesCount", sample, "Daily stats should include anomaliesCount")
            
            # Check data types
            self.assertIsInstance(sample["avgTemperature"], (int, float), "Average temperature should be a number")
            self.assertIsInstance(sample["minTemperature"], (int, float), "Min temperature should be a number")
            self.assertIsInstance(sample["maxTemperature"], (int, float), "Max temperature should be a number")
            self.assertIsInstance(sample["dataPointsCount"], int, "Data points count should be an integer")
            
        print("✅ Daily statistics endpoint is working correctly")
        
    def test_05_anomalies(self):
        """Test the anomalies endpoint"""
        print("\n=== Testing Anomalies Endpoint ===")
        response = requests.get(f"{self.api_base_url}/anomalies?hours=24&limit=10")
        self.assertEqual(response.status_code, 200, "Anomalies endpoint should return 200")
        
        data = response.json()
        print(f"Received {len(data)} anomaly records")
        if data:
            print(f"Sample anomaly: {json.dumps(data[0], indent=2)}")
        
        # Verify data structure if data exists
        if data:
            sample = data[0]
            self.assertIn("id", sample, "Anomaly should include id")
            self.assertIn("timestamp", sample, "Anomaly should include timestamp")
            self.assertIn("sensor_type", sample, "Anomaly should include sensor_type")
            self.assertIn("original_value", sample, "Anomaly should include original_value")
            self.assertIn("reason", sample, "Anomaly should include reason")
            self.assertIn("status", sample, "Anomaly should include status")
            
            # Check data types
            self.assertIsInstance(sample["original_value"], (int, float), "Original value should be a number")
            self.assertIn(sample["status"], ["detected", "filtered", "verified"], "Status should be valid")
            
        print("✅ Anomalies endpoint is working correctly")
        
    def test_06_processing_logs(self):
        """Test the processing logs endpoint"""
        print("\n=== Testing Processing Logs Endpoint ===")
        response = requests.get(f"{self.api_base_url}/logs?hours=24&limit=10")
        self.assertEqual(response.status_code, 200, "Processing logs endpoint should return 200")
        
        data = response.json()
        print(f"Received {len(data)} processing log records")
        if data:
            print(f"Sample log: {json.dumps(data[0], indent=2)}")
        
        # Verify data structure if data exists
        if data:
            sample = data[0]
            self.assertIn("id", sample, "Log should include id")
            self.assertIn("timestamp", sample, "Log should include timestamp")
            self.assertIn("action", sample, "Log should include action")
            self.assertIn("status", sample, "Log should include status")
            self.assertIn("details", sample, "Log should include details")
            
            # Check data types
            self.assertIn(sample["status"], ["success", "warning", "error"], "Status should be valid")
            
        print("✅ Processing logs endpoint is working correctly")
        
    def test_07_manual_data_collection(self):
        """Test the manual data collection endpoint"""
        print("\n=== Testing Manual Data Collection Endpoint ===")
        response = requests.post(f"{self.api_base_url}/collect", json={"location": "Kyiv"})
        self.assertEqual(response.status_code, 200, "Manual data collection endpoint should return 200")
        
        data = response.json()
        print(f"Manual data collection response: {json.dumps(data, indent=2)}")
        
        # Verify response structure
        self.assertIn("message", data, "Response should include message")
        self.assertIn("location", data, "Response should include location")
        self.assertIn("timestamp", data, "Response should include timestamp")
        
        # Wait a moment for data to be processed
        print("Waiting for data processing to complete...")
        time.sleep(2)
        
        # Verify data was collected by checking the logs
        logs_response = requests.get(f"{self.api_base_url}/logs?hours=1&limit=5")
        logs = logs_response.json()
        
        # Look for a successful data processing log
        found_processing_log = False
        for log in logs:
            if "Повний цикл обробки даних" in log.get("action", "") and log.get("status") == "success":
                found_processing_log = True
                break
                
        self.assertTrue(found_processing_log, "Should find a successful data processing log after manual collection")
        
        print("✅ Manual data collection endpoint is working correctly")
        
    def test_08_csv_export_hourly(self):
        """Test the CSV export endpoint for hourly data"""
        print("\n=== Testing CSV Export Endpoint (Hourly Data) ===")
        
        # Get current time and 24 hours ago
        now = datetime.utcnow()
        start_date = (now - timedelta(hours=24)).isoformat()
        end_date = now.isoformat()
        
        export_request = {
            "dataType": "hourly",
            "startDate": start_date,
            "endDate": end_date,
            "format": "csv"
        }
        
        response = requests.post(f"{self.api_base_url}/export", json=export_request)
        self.assertEqual(response.status_code, 200, "CSV export endpoint should return 200")
        
        # Verify content type
        self.assertEqual(response.headers.get('Content-Type'), "text/csv", "Response should be CSV")
        self.assertIn("attachment; filename=", response.headers.get('Content-Disposition', ""), 
                     "Response should have attachment header")
        
        # Parse CSV data
        csv_data = response.text
        print(f"Received CSV data with {len(csv_data.splitlines())} lines")
        
        # Verify CSV structure
        csv_reader = csv.reader(io.StringIO(csv_data))
        header = next(csv_reader, None)
        
        if header:
            print(f"CSV header: {header}")
            self.assertIn('Час', header, "CSV should include timestamp column")
            self.assertIn('Температура (°C)', header, "CSV should include temperature column")
            self.assertIn('Вологість (%)', header, "CSV should include humidity column")
            self.assertIn('Якість повітря', header, "CSV should include air quality column")
            
            # Check if there's at least one data row
            data_row = next(csv_reader, None)
            if data_row:
                print(f"Sample CSV data row: {data_row}")
                self.assertEqual(len(data_row), len(header), "Data row should have same number of columns as header")
        
        print("✅ CSV export endpoint for hourly data is working correctly")
        
    def test_09_csv_export_daily(self):
        """Test the CSV export endpoint for daily data"""
        print("\n=== Testing CSV Export Endpoint (Daily Data) ===")
        
        # Get current time and 30 days ago
        now = datetime.utcnow()
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        export_request = {
            "dataType": "daily",
            "startDate": start_date,
            "endDate": end_date,
            "format": "csv"
        }
        
        response = requests.post(f"{self.api_base_url}/export", json=export_request)
        self.assertEqual(response.status_code, 200, "CSV export endpoint should return 200")
        
        # Verify content type
        self.assertEqual(response.headers.get('Content-Type'), "text/csv", "Response should be CSV")
        
        # Parse CSV data
        csv_data = response.text
        print(f"Received CSV data with {len(csv_data.splitlines())} lines")
        
        # Verify CSV structure
        csv_reader = csv.reader(io.StringIO(csv_data))
        header = next(csv_reader, None)
        
        if header:
            print(f"CSV header: {header}")
            self.assertIn('Дата', header, "CSV should include date column")
            self.assertIn('Середня температура (°C)', header, "CSV should include avg temperature column")
            self.assertIn('Мін. температура (°C)', header, "CSV should include min temperature column")
            self.assertIn('Макс. температура (°C)', header, "CSV should include max temperature column")
            
        print("✅ CSV export endpoint for daily data is working correctly")
        
    def test_10_csv_export_anomalies(self):
        """Test the CSV export endpoint for anomalies data"""
        print("\n=== Testing CSV Export Endpoint (Anomalies Data) ===")
        
        # Get current time and 7 days ago
        now = datetime.utcnow()
        start_date = (now - timedelta(days=7)).isoformat()
        end_date = now.isoformat()
        
        export_request = {
            "dataType": "anomalies",
            "startDate": start_date,
            "endDate": end_date,
            "format": "csv"
        }
        
        response = requests.post(f"{self.api_base_url}/export", json=export_request)
        self.assertEqual(response.status_code, 200, "CSV export endpoint should return 200")
        
        # Verify content type
        self.assertEqual(response.headers.get('Content-Type'), "text/csv", "Response should be CSV")
        
        # Parse CSV data
        csv_data = response.text
        print(f"Received CSV data with {len(csv_data.splitlines())} lines")
        
        # Verify CSV structure
        csv_reader = csv.reader(io.StringIO(csv_data))
        header = next(csv_reader, None)
        
        if header:
            print(f"CSV header: {header}")
            self.assertIn('ID', header, "CSV should include ID column")
            self.assertIn('Час', header, "CSV should include timestamp column")
            self.assertIn('Тип сенсора', header, "CSV should include sensor type column")
            self.assertIn('Оригінальне значення', header, "CSV should include original value column")
            
        print("✅ CSV export endpoint for anomalies data is working correctly")
        
    def test_11_data_flow_integration(self):
        """Test the complete data flow from collection to retrieval"""
        print("\n=== Testing Complete Data Flow Integration ===")
        
        # Step 1: Trigger data collection
        print("Step 1: Triggering data collection...")
        collection_response = requests.post(f"{self.api_base_url}/collect", json={"location": "Kyiv"})
        self.assertEqual(collection_response.status_code, 200, "Data collection should return 200")
        
        # Wait for processing to complete
        print("Waiting for data processing to complete...")
        time.sleep(3)
        
        # Step 2: Verify data was stored by checking current conditions
        print("Step 2: Verifying data was stored...")
        current_response = requests.get(f"{self.api_base_url}/current")
        self.assertEqual(current_response.status_code, 200, "Current conditions should return 200")
        current_data = current_response.json()
        
        # Step 3: Check hourly data includes the new record
        print("Step 3: Checking hourly data includes new record...")
        hourly_response = requests.get(f"{self.api_base_url}/hourly?hours=1&limit=5")
        self.assertEqual(hourly_response.status_code, 200, "Hourly data should return 200")
        hourly_data = hourly_response.json()
        
        # Verify we have at least one record
        self.assertGreater(len(hourly_data), 0, "Should have at least one hourly record")
        
        # Step 4: Check logs for processing record
        print("Step 4: Checking logs for processing record...")
        logs_response = requests.get(f"{self.api_base_url}/logs?hours=1&limit=10")
        self.assertEqual(logs_response.status_code, 200, "Logs should return 200")
        logs_data = logs_response.json()
        
        # Look for processing log
        found_processing_log = False
        for log in logs_data:
            if "Повний цикл обробки даних" in log.get("action", ""):
                found_processing_log = True
                print(f"Found processing log: {log.get('action')} - {log.get('details')}")
                break
                
        self.assertTrue(found_processing_log, "Should find a data processing log")
        
        print("✅ Complete data flow integration is working correctly")
        
    def test_12_weather_api_integration(self):
        """Test the Weather API integration directly"""
        print("\n=== Testing Weather API Integration ===")
        
        # Check health endpoint for Weather API status
        health_response = requests.get(f"{self.api_base_url}/health")
        health_data = health_response.json()
        
        weather_api_status = health_data.get("services", {}).get("weather_service", "unknown")
        print(f"Weather API status from health check: {weather_api_status}")
        
        self.assertEqual(weather_api_status, "connected", "Weather API should be connected")
        
        # Trigger data collection to test API integration
        print("Triggering data collection to test API integration...")
        collection_response = requests.post(f"{self.api_base_url}/collect", json={"location": "Kyiv"})
        self.assertEqual(collection_response.status_code, 200, "Data collection should return 200")
        
        # Wait for processing
        time.sleep(2)
        
        # Check logs for API request
        logs_response = requests.get(f"{self.api_base_url}/logs?hours=1&limit=10")
        logs_data = logs_response.json()
        
        # Look for API request log
        found_api_log = False
        for log in logs_data:
            if "Weather API" in log.get("action", ""):
                found_api_log = True
                print(f"Found API log: {log.get('action')} - {log.get('details')}")
                break
                
        self.assertTrue(found_api_log, "Should find a Weather API request log")
        
        print("✅ Weather API integration is working correctly")
        
    def test_13_anomaly_detection(self):
        """Test the anomaly detection functionality"""
        print("\n=== Testing Anomaly Detection ===")
        
        # Check if we have any anomalies in the system
        anomalies_response = requests.get(f"{self.api_base_url}/anomalies?hours=24")
        anomalies_data = anomalies_response.json()
        
        print(f"Found {len(anomalies_data)} anomalies in the last 24 hours")
        
        # If we have anomalies, verify their structure
        if anomalies_data:
            sample = anomalies_data[0]
            print(f"Sample anomaly: {json.dumps(sample, indent=2)}")
            
            self.assertIn("sensor_type", sample, "Anomaly should include sensor_type")
            self.assertIn("original_value", sample, "Anomaly should include original_value")
            self.assertIn("status", sample, "Anomaly should include status")
            self.assertIn("reason", sample, "Anomaly should include reason")
            
            # Check if any anomalies have been filtered
            filtered_anomalies = [a for a in anomalies_data if a.get("status") == "filtered"]
            print(f"Found {len(filtered_anomalies)} filtered anomalies")
            
            if filtered_anomalies:
                sample_filtered = filtered_anomalies[0]
                print(f"Sample filtered anomaly: {json.dumps(sample_filtered, indent=2)}")
                self.assertIn("filtered_value", sample_filtered, "Filtered anomaly should include filtered_value")
        
        print("✅ Anomaly detection functionality is working correctly")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
