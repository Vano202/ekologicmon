// Mock data service for air quality monitoring
const generateRandomData = (baseValue, variance) => {
  return baseValue + (Math.random() - 0.5) * variance;
};

const generateHourlyData = () => {
  const data = [];
  const now = new Date();
  
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    
    data.push({
      timestamp: time.toISOString(),
      temperature: generateRandomData(22, 10),
      humidity: generateRandomData(45, 20),
      airQuality: Math.floor(generateRandomData(50, 40)),
      pm25: generateRandomData(15, 10),
      pm10: generateRandomData(25, 15),
      co2: Math.floor(generateRandomData(400, 200)),
      pressure: generateRandomData(1013, 20),
    });
  }
  
  return data;
};

const generateDailyData = () => {
  const data = [];
  const now = new Date();
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
    
    data.push({
      date: date.toISOString().split('T')[0],
      avgTemperature: generateRandomData(20, 8),
      avgHumidity: generateRandomData(50, 15),
      avgAirQuality: Math.floor(generateRandomData(45, 30)),
      minTemperature: generateRandomData(15, 5),
      maxTemperature: generateRandomData(25, 7),
      anomaliesCount: Math.floor(Math.random() * 5),
    });
  }
  
  return data;
};

const getCurrentData = () => ({
  temperature: generateRandomData(23, 2),
  humidity: generateRandomData(48, 5),
  airQuality: Math.floor(generateRandomData(42, 10)),
  pm25: generateRandomData(12, 3),
  pm10: generateRandomData(18, 5),
  co2: Math.floor(generateRandomData(420, 50)),
  pressure: generateRandomData(1015, 5),
  windSpeed: generateRandomData(3.5, 2),
  windDirection: Math.floor(Math.random() * 360),
  uvIndex: Math.floor(generateRandomData(3, 2)),
  lastUpdated: new Date().toISOString(),
});

const getAnomalies = () => [
  {
    id: 1,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    type: 'temperature',
    value: -5,
    reason: 'Значення нижче мінімального порогу',
    status: 'filtered'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    type: 'humidity',
    value: 105,
    reason: 'Значення вище максимального порогу',
    status: 'filtered'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    type: 'airQuality',
    value: 300,
    reason: 'Різка зміна показника',
    status: 'verified'
  }
];

const getProcessingLog = () => [
  {
    id: 1,
    timestamp: new Date().toISOString(),
    action: 'Отримання даних з API',
    status: 'success',
    details: 'Успішно отримано 24 записи'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    action: 'Фільтрація аномалій',
    status: 'success',
    details: 'Відфільтровано 2 аномальні значення'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    action: 'Валідація даних',
    status: 'warning',
    details: 'Виявлено 1 підозріле значення'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    action: 'Збереження в CSV',
    status: 'success',
    details: 'Дані збережено у файл air_quality_data.csv'
  }
];

export const mockDataService = {
  getCurrentData,
  getHourlyData: generateHourlyData,
  getDailyData: generateDailyData,
  getAnomalies,
  getProcessingLog,
  
  // Simulate API delay
  delay: (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms))
};
