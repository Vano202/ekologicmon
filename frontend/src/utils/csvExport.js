// CSV export utilities
export const exportToCSV = (data, filename) => {
  if (!data || data.length === 0) {
    console.error('No data to export');
    return;
  }

  // Get headers from the first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  let csv = headers.join(',') + '\n';
  
  data.forEach(row => {
    const values = headers.map(header => {
      const value = row[header];
      // Handle values that might contain commas
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value}"`;
      }
      return value;
    });
    csv += values.join(',') + '\n';
  });

  // Create and trigger download
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

export const formatDataForCSV = (data, type) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  switch (type) {
    case 'hourly':
      return {
        data: data.map(item => ({
          'Час': new Date(item.timestamp).toLocaleString('uk-UA'),
          'Температура (°C)': item.temperature.toFixed(1),
          'Вологість (%)': item.humidity.toFixed(1),
          'Якість повітря': item.airQuality,
          'PM2.5 (μg/m³)': item.pm25.toFixed(1),
          'PM10 (μg/m³)': item.pm10.toFixed(1),
          'CO2 (ppm)': item.co2,
          'Тиск (hPa)': item.pressure.toFixed(1)
        })),
        filename: `hourly_data_${timestamp}.csv`
      };
      
    case 'daily':
      return {
        data: data.map(item => ({
          'Дата': item.date,
          'Середня температура (°C)': item.avgTemperature.toFixed(1),
          'Середня вологість (%)': item.avgHumidity.toFixed(1),
          'Середня якість повітря': item.avgAirQuality,
          'Мін. температура (°C)': item.minTemperature.toFixed(1),
          'Макс. температура (°C)': item.maxTemperature.toFixed(1),
          'Кількість аномалій': item.anomaliesCount
        })),
        filename: `daily_data_${timestamp}.csv`
      };
      
    case 'anomalies':
      return {
        data: data.map(item => ({
          'ID': item.id,
          'Час': new Date(item.timestamp).toLocaleString('uk-UA'),
          'Тип': item.type,
          'Значення': item.value,
          'Причина': item.reason,
          'Статус': item.status
        })),
        filename: `anomalies_${timestamp}.csv`
      };
      
    default:
      return { data: [], filename: 'data.csv' };
  }
};
