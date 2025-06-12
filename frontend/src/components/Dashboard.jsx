import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { useToast } from '../hooks/use-toast';
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
  Clock,
  RefreshCw,
  Wifi,
  WifiOff
} from 'lucide-react';
import { apiService } from '../services/apiService';
import ChartsSection from './ChartsSection';

const Dashboard = () => {
  const [currentData, setCurrentData] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [dailyData, setDailyData] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [processingLog, setProcessingLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setError(null);
      
      // Get current data
      const currentResponse = await apiService.getCurrentData();
      const transformedCurrent = apiService.transformCurrentData(currentResponse);
      setCurrentData(transformedCurrent);

      // Get hourly data
      const hourlyResponse = await apiService.getHourlyData(24);
      const transformedHourly = apiService.transformHourlyData(hourlyResponse);
      setHourlyData(transformedHourly);

      // Get daily data
      const dailyResponse = await apiService.getDailyData(30);
      const transformedDaily = apiService.transformDailyData(dailyResponse);
      setDailyData(transformedDaily);

      // Get anomalies
      const anomaliesResponse = await apiService.getAnomalies(24);
      const transformedAnomalies = apiService.transformAnomalies(anomaliesResponse);
      setAnomalies(transformedAnomalies);

      // Get processing logs
      const logsResponse = await apiService.getProcessingLogs(24);
      const transformedLogs = apiService.transformProcessingLogs(logsResponse);
      setProcessingLog(transformedLogs);

      setIsOnline(true);
      setLastUpdate(new Date());
      
      if (loading) {
        toast({
          title: "Дані завантажено",
          description: "Поточні дані про якість повітря успішно оновлено",
        });
      }
      
    } catch (error) {
      console.error('Error loading data:', error);
      setError(error.message);
      setIsOnline(false);
      
      toast({
        title: "Помилка завантаження",
        description: "Не вдалося завантажити дані. Перевірте підключення до мережі.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await loadData();
  };

  const handleManualCollection = async () => {
    try {
      await apiService.triggerDataCollection('Kyiv');
      toast({
        title: "Збір даних запущено",
        description: "Ручний збір даних розпочато. Дані будуть оновлені незабаром.",
      });
      
      // Refresh data after a short delay
      setTimeout(loadData, 3000);
    } catch (error) {
      toast({
        title: "Помилка",
        description: "Не вдалося запустити збір даних",
        variant: "destructive",
      });
    }
  };

  const handleExport = async (type) => {
    try {
      await apiService.exportData(type);
      toast({
        title: "Експорт успішний",
        description: `Файл ${type} даних завантажено`,
      });
    } catch (error) {
      toast({
        title: "Помилка експорту",
        description: "Не вдалося експортувати дані",
        variant: "destructive",
      });
    }
  };

  const getAirQualityStatus = (value) => {
    if (value <= 50) return { label: 'Добра', color: 'bg-green-500', textColor: 'text-green-700' };
    if (value <= 100) return { label: 'Помірна', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (value <= 150) return { label: 'Шкідлива для чутливих груп', color: 'bg-orange-500', textColor: 'text-orange-700' };
    if (value <= 200) return { label: 'Шкідлива', color: 'bg-red-500', textColor: 'text-red-700' };
    return { label: 'Небезпечна', color: 'bg-purple-500', textColor: 'text-purple-700' };
  };

  if (loading && !currentData) {
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                Моніторинг якості повітря
              </h1>
              <div className="flex items-center gap-4 text-gray-600">
                <span>
                  Останнє оновлення: {lastUpdate ? lastUpdate.toLocaleString('uk-UA') : '--'}
                </span>
                <div className="flex items-center gap-2">
                  {isOnline ? (
                    <><Wifi className="h-4 w-4 text-green-500" /> <span className="text-green-600">Онлайн</span></>
                  ) : (
                    <><WifiOff className="h-4 w-4 text-red-500" /> <span className="text-red-600">Офлайн</span></>
                  )}
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleRefresh} disabled={loading} variant="outline">
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Оновити
              </Button>
              <Button onClick={handleManualCollection} variant="outline">
                <Activity className="h-4 w-4 mr-2" />
                Зібрати дані
              </Button>
            </div>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-700">
              Помилка: {error}
            </AlertDescription>
          </Alert>
        )}

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
              Аномалії ({anomalies.length})
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
                      <div>Видимість: {currentData?.visibility?.toFixed(1) || '--'} км</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Статистика</h4>
                    <div className="text-sm space-y-1">
                      <div>Записів за годину: {hourlyData.length}</div>
                      <div>Записів за місяць: {dailyData.length}</div>
                      <div>Відфільтровано аномалій: {anomalies.filter(a => a.status === 'filtered').length}</div>
                      <div>Локація: {currentData?.location || '--'}</div>
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
                  {anomalies.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
                      <p>Аномалій не виявлено</p>
                    </div>
                  ) : (
                    anomalies.map((anomaly) => (
                      <Alert key={anomaly.id} className="border-l-4 border-l-orange-400">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-semibold">{anomaly.type}</span> - {anomaly.reason}
                              <div className="text-sm text-gray-500 mt-1">
                                Значення: {anomaly.value} | {new Date(anomaly.timestamp).toLocaleString('uk-UA')}
                                {anomaly.confidence && (
                                  <span className="ml-2">Достовірність: {(anomaly.confidence * 100).toFixed(0)}%</span>
                                )}
                              </div>
                            </div>
                            <Badge variant={anomaly.status === 'filtered' ? 'destructive' : 'default'}>
                              {anomaly.status === 'filtered' ? 'Відфільтровано' : 
                               anomaly.status === 'verified' ? 'Перевірено' : 'Виявлено'}
                            </Badge>
                          </div>
                        </AlertDescription>
                      </Alert>
                    ))
                  )}
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
                  {processingLog.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Clock className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                      <p>Немає записів у журналі</p>
                    </div>
                  ) : (
                    processingLog.map((log) => (
                      <div key={log.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-shrink-0">
                          {log.status === 'success' && <CheckCircle className="h-5 w-5 text-green-500" />}
                          {log.status === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-500" />}
                          {log.status === 'error' && <AlertTriangle className="h-5 w-5 text-red-500" />}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{log.action}</div>
                          <div className="text-sm text-gray-600">{log.details}</div>
                          {log.durationMs && (
                            <div className="text-xs text-gray-500 mt-1">
                              Тривалість: {log.durationMs}мс
                              {log.dataCount && ` | Записів: ${log.dataCount}`}
                            </div>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(log.timestamp).toLocaleTimeString('uk-UA')}
                        </div>
                      </div>
                    ))
                  )}
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
