import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making API request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get current weather conditions
  async getCurrentData() {
    try {
      const response = await apiClient.get('/current');
      return response.data;
    } catch (error) {
      console.error('Error fetching current data:', error);
      throw error;
    }
  },

  // Get hourly data
  async getHourlyData(hours = 24) {
    try {
      const response = await apiClient.get('/hourly', {
        params: { hours, limit: 100 }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching hourly data:', error);
      throw error;
    }
  },

  // Get daily statistics
  async getDailyData(days = 30) {
    try {
      const response = await apiClient.get('/daily', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching daily data:', error);
      throw error;
    }
  },

  // Get anomalies
  async getAnomalies(hours = 24) {
    try {
      const response = await apiClient.get('/anomalies', {
        params: { hours, limit: 100 }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      throw error;
    }
  },

  // Get processing logs
  async getProcessingLogs(hours = 24) {
    try {
      const response = await apiClient.get('/logs', {
        params: { hours, limit: 50 }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching processing logs:', error);
      throw error;
    }
  },

  // Trigger manual data collection
  async triggerDataCollection(location = 'Kyiv') {
    try {
      const response = await apiClient.post('/collect', null, {
        params: { location }
      });
      return response.data;
    } catch (error) {
      console.error('Error triggering data collection:', error);
      throw error;
    }
  },

  // Export data to CSV
  async exportData(dataType, startDate = null, endDate = null) {
    try {
      const response = await apiClient.post('/export', {
        dataType,
        startDate,
        endDate,
        format: 'csv'
      }, {
        responseType: 'blob'
      });

      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from response headers or create default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${dataType}_data_${new Date().toISOString().split('T')[0]}.csv`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      console.error('Error exporting data:', error);
      throw error;
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },

  // Transform data helpers
  transformCurrentData(data) {
    if (!data) return null;
    
    return {
      temperature: data.temperature || 0,
      humidity: data.humidity || 0,
      airQuality: data.airQuality || 0,
      pm25: data.pm25 || 0,
      pm10: data.pm10 || 0,
      co2: data.co2 || 400,
      pressure: data.pressure || 1013,
      windSpeed: data.windSpeed || 0,
      windDirection: data.windDirection || 0,
      uvIndex: data.uvIndex || 0,
      visibility: data.visibility || 10,
      lastUpdated: data.lastUpdated || new Date().toISOString(),
      location: data.location || 'Unknown'
    };
  },

  transformHourlyData(data) {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => ({
      timestamp: item.timestamp,
      temperature: item.temperature || 0,
      humidity: item.humidity || 0,
      airQuality: item.air_quality || item.airQuality || 0,
      pm25: item.pm25 || 0,
      pm10: item.pm10 || 0,
      co2: item.co2 || 400,
      pressure: item.pressure || 1013,
      windSpeed: item.wind_speed || item.windSpeed || 0,
      windDirection: item.wind_direction || item.windDirection || 0
    }));
  },

  transformDailyData(data) {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => ({
      date: item.date,
      avgTemperature: item.avg_temperature || item.avgTemperature || 0,
      minTemperature: item.min_temperature || item.minTemperature || 0,
      maxTemperature: item.max_temperature || item.maxTemperature || 0,
      avgHumidity: item.avg_humidity || item.avgHumidity || 0,
      avgAirQuality: item.avg_air_quality || item.avgAirQuality || 0,
      avgPressure: item.avg_pressure || item.avgPressure || 1013,
      dataPointsCount: item.data_points_count || item.dataPointsCount || 0,
      anomaliesCount: item.anomalies_count || item.anomaliesCount || 0
    }));
  },

  transformAnomalies(data) {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => ({
      id: item.id,
      timestamp: item.timestamp,
      type: item.sensor_type || item.sensorType || item.type,
      value: item.original_value || item.originalValue || item.value,
      filteredValue: item.filtered_value || item.filteredValue,
      reason: item.reason,
      status: item.status,
      confidence: item.confidence
    }));
  },

  transformProcessingLogs(data) {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => ({
      id: item.id,
      timestamp: item.timestamp,
      action: item.action,
      status: item.status,
      details: item.details,
      durationMs: item.duration_ms || item.durationMs,
      dataCount: item.data_count || item.dataCount
    }));
  }
};
