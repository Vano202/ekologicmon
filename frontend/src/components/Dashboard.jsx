import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Thermometer, 
  Droplets, 
  Wind, 
  Eye,
  Download,
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { mockDataService } from '../services/mockData';
import { exportToCSV, formatDataForCSV } from '../utils/csvExport';
import ChartsSection from './ChartsSection';

const Dashboard = () => {
  const [currentData, setCurrentData] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [dailyData, setDailyData] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [processingLog, setProcessingLog] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await mockDataService.delay(800); // Simulate API delay
      
      setCurrentData(mockDataService.getCurrentData());
      setHourlyData(mockDataService.getHourlyData());
      setDailyData(mockDataService.getDailyData());
      setAnomalies(mockDataService.getAnomalies());
      setProcessingLog(mockDataService.getProcessingLog());
      
      setLoading(false);
    };

    loadData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getAirQualityStatus = (value) => {
    if (value <= 50) return { label: 'Добра', color: 'bg-green-500', textColor: 'text-green-700' };
    if (value <= 100) return { label: 'Помірна', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (value <= 150) return { label: 'Шкідлива для чутливих груп', color: 'bg-orange-500', textColor: 'text-orange-700' };
    if (value <= 200) return { label: 'Шкідлива', color: 'bg-red-500', textColor: 'text-red-700' };
    return { label: 'Небезпечна', color: 'bg-purple-500', textColor: 'text-purple-700' };
  };

  const handleExport = (type) => {
    let exportData;
    
    switch (type) {
      case 'hourly':
        exportData = formatDataForCSV(hourlyData, 'hourly');
        break;
      case 'daily':
        exportData = formatDataForCSV(dailyData, 'daily');
        break;
      case 'anomalies':
        exportData = formatDataForCSV(anomalies, 'anomalies');
        break;
      default:
        return;
    }
    
    exportToCSV(exportData.data, exportData.filename);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Завантаження даних...</p>
        </div>
      </div>
    );
  }

  const airQualityStatus = getAirQualityStatus(currentData?.airQuality || 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Моніторинг якості повітря
          </h1>
          <p className="text-gray-600">
            Останнє оновлення: {currentData ? new Date(currentData.lastUpdated).toLocaleString('uk-UA') : '--'}
          </p>
        </div>

        {/* Current Data Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm font-medium text-gray-600">
                <span>Температура</span>
                <Thermometer className="h-4 w-4 text-red-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {currentData?.temperature?.toFixed(1) || '--'}°C
              </div>
              <Progress value={Math.max(0, Math.min(100, (currentData?.temperature + 20) * 2))} className="h-2" />
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm font-medium text-gray-600">
                <span>Вологість</span>
                <Droplets className="h-4 w-4 text-blue-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {currentData?.humidity?.toFixed(1) || '--'}%
              </div>
              <Progress value={currentData?.humidity || 0} className="h-2" />
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm font-medium text-gray-600">
                <span>Якість повітря</span>
                <Eye className="h-4 w-4 text-purple-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 mb-2">
                {currentData?.airQuality || '--'}
              </div>
              <Badge className={`${airQualityStatus.color} text-white text-xs`}>
                {airQualityStatus.label}
              </Badge>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm font-medium text-gray-600">
                <span>Швидкість вітру</span>
                <Wind className="h-4 w-4 text-green-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {currentData?.windSpeed?.toFixed(1) || '--'} м/с
              </div>
              <div className="text-sm text-gray-500">
                Напрямок: {currentData?.windDirection || '--'}°
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="charts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/50 backdrop-blur-sm">
            <TabsTrigger value="charts" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Графіки
            </TabsTrigger>
            <TabsTrigger value="data" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Дані
            </TabsTrigger>
            <TabsTrigger value="anomalies" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Аномалії
            </TabsTrigger>
            <TabsTrigger value="logs" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Логи
            </TabsTrigger>
          </TabsList>

          <TabsContent value="charts">
            <ChartsSection hourlyData={hourlyData} dailyData={dailyData} />
          </TabsContent>

          <TabsContent value="data">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Детальні дані</CardTitle>
                  <div className="flex gap-2">
                    <Button 
                      onClick={() => handleExport('hourly')} 
                      variant="outline" 
                      size="sm"
                      className="hover:bg-blue-50"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Погодинні дані
                    </Button>
                    <Button 
                      onClick={() => handleExport('daily')} 
                      variant="outline" 
                      size="sm"
                      className="hover:bg-green-50"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Денні дані
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Якість повітря (PM)</h4>
                    <div className="text-sm space-y-1">
                      <div>PM2.5: {currentData?.pm25?.toFixed(1) || '--'} μg/m³</div>
                      <div>PM10: {currentData?.pm10?.toFixed(1) || '--'} μg/m³</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Атмосферні умови</h4>
                    <div className="text-sm space-y-1">
                      <div>CO2: {currentData?.co2 || '--'} ppm</div>
                      <div>Тиск: {currentData?.pressure?.toFixed(1) || '--'} hPa</div>
                      <div>УФ індекс: {currentData?.uvIndex || '--'}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Статистика</h4>
                    <div className="text-sm space-y-1">
                      <div>Записів за годину: {hourlyData.length}</div>
                      <div>Записів за місяць: {dailyData.length}</div>
                      <div>Відфільтровано аномалій: {anomalies.filter(a => a.status === 'filtered').length}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="anomalies">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Виявлені аномалії</CardTitle>
                  <Button 
                    onClick={() => handleExport('anomalies')} 
                    variant="outline" 
                    size="sm"
                    className="hover:bg-red-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Експорт аномалій
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {anomalies.map((anomaly) => (
                    <Alert key={anomaly.id} className="border-l-4 border-l-orange-400">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-semibold">{anomaly.type}</span> - {anomaly.reason}
                            <div className="text-sm text-gray-500 mt-1">
                              Значення: {anomaly.value} | {new Date(anomaly.timestamp).toLocaleString('uk-UA')}
                            </div>
                          </div>
                          <Badge variant={anomaly.status === 'filtered' ? 'destructive' : 'default'}>
                            {anomaly.status === 'filtered' ? 'Відфільтровано' : 'Перевірено'}
                          </Badge>
                        </div>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="logs">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Журнал обробки даних</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {processingLog.map((log) => (
                    <div key={log.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0">
                        {log.status === 'success' && <CheckCircle className="h-5 w-5 text-green-500" />}
                        {log.status === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-500" />}
                        {log.status === 'error' && <AlertTriangle className="h-5 w-5 text-red-500" />}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{log.action}</div>
                        <div className="text-sm text-gray-600">{log.details}</div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(log.timestamp).toLocaleTimeString('uk-UA')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
