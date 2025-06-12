import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const ChartsSection = ({ hourlyData, dailyData }) => {
  // Prepare data for charts
  const hourlyChartData = hourlyData.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString('uk-UA', { 
      hour: '2-digit', 
      minute: '2-digit' 
    }),
    температура: Math.round(item.temperature * 10) / 10,
    вологість: Math.round(item.humidity * 10) / 10,
    'якість повітря': item.airQuality,
    'PM2.5': Math.round(item.pm25 * 10) / 10,
    'PM10': Math.round(item.pm10 * 10) / 10,
    'CO2': item.co2,
    тиск: Math.round(item.pressure * 10) / 10,
  }));

  const dailyChartData = dailyData.map(item => ({
    date: new Date(item.date).toLocaleDateString('uk-UA', { 
      month: 'short', 
      day: 'numeric' 
    }),
    'середня температура': Math.round(item.avgTemperature * 10) / 10,
    'середня вологість': Math.round(item.avgHumidity * 10) / 10,
    'середня якість повітря': item.avgAirQuality,
    'кількість аномалій': item.anomaliesCount,
  }));

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}
              {entry.name.includes('температура') && '°C'}
              {entry.name.includes('вологість') && '%'}
              {entry.name.includes('PM') && ' μg/m³'}
              {entry.name.includes('CO2') && ' ppm'}
              {entry.name.includes('тиск') && ' hPa'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Calculate trends
  const getTemperatureTrend = () => {
    if (hourlyData.length < 2) return { value: 0, direction: 'neutral' };
    const recent = hourlyData.slice(-6).map(d => d.temperature);
    const older = hourlyData.slice(-12, -6).map(d => d.temperature);
    const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
    const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
    const diff = recentAvg - olderAvg;
    return {
      value: Math.abs(diff).toFixed(1),
      direction: diff > 0.5 ? 'up' : diff < -0.5 ? 'down' : 'neutral'
    };
  };

  const getAirQualityTrend = () => {
    if (hourlyData.length < 2) return { value: 0, direction: 'neutral' };
    const recent = hourlyData.slice(-6).map(d => d.airQuality);
    const older = hourlyData.slice(-12, -6).map(d => d.airQuality);
    const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
    const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
    const diff = recentAvg - olderAvg;
    return {
      value: Math.abs(diff).toFixed(0),
      direction: diff > 5 ? 'up' : diff < -5 ? 'down' : 'neutral'
    };
  };

  const temperatureTrend = getTemperatureTrend();
  const airQualityTrend = getAirQualityTrend();

  return (
    <div className="space-y-6">
      {/* Trend Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Тренд температури</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-lg font-semibold">
                    {temperatureTrend.direction === 'neutral' ? 'Стабільна' : `${temperatureTrend.value}°C`}
                  </span>
                  {temperatureTrend.direction === 'up' && <TrendingUp className="h-4 w-4 text-red-500" />}
                  {temperatureTrend.direction === 'down' && <TrendingDown className="h-4 w-4 text-blue-500" />}
                  {temperatureTrend.direction === 'neutral' && <Activity className="h-4 w-4 text-gray-500" />}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Тренд якості повітря</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-lg font-semibold">
                    {airQualityTrend.direction === 'neutral' ? 'Стабільна' : airQualityTrend.value}
                  </span>
                  {airQualityTrend.direction === 'up' && <TrendingUp className="h-4 w-4 text-red-500" />}
                  {airQualityTrend.direction === 'down' && <TrendingDown className="h-4 w-4 text-green-500" />}
                  {airQualityTrend.direction === 'neutral' && <Activity className="h-4 w-4 text-gray-500" />}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Активність системи</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-lg font-semibold text-green-600">Активна</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Temperature and Humidity Chart */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            Температура та вологість (24 години)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={hourlyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="температура"
                stroke="#ef4444"
                strokeWidth={3}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#ef4444', strokeWidth: 2 }}
              />
              <Line
                type="monotone"
                dataKey="вологість"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Air Quality Chart */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-600" />
            Якість повітря та забруднювачі
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={hourlyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="якість повітря"
                stackId="1"
                stroke="#8b5cf6"
                fill="url(#colorAirQuality)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="PM2.5"
                stackId="2"
                stroke="#f59e0b"
                fill="url(#colorPM25)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="PM10"
                stackId="3"
                stroke="#10b981"
                fill="url(#colorPM10)"
                strokeWidth={2}
              />
              <defs>
                <linearGradient id="colorAirQuality" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorPM25" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorPM10" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Daily Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              Середні показники (30 днів)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="середня температура"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={{ fill: '#ef4444', r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="середня вологість"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-orange-600" />
              Аномалії за день
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar
                  dataKey="кількість аномалій"
                  fill="url(#colorAnomalies)"
                  radius={[4, 4, 0, 0]}
                />
                <defs>
                  <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* CO2 and Pressure Chart */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-600" />
            CO2 та атмосферний тиск
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={hourlyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis yAxisId="left" stroke="#6b7280" fontSize={12} />
              <YAxis yAxisId="right" orientation="right" stroke="#6b7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="CO2"
                stroke="#6366f1"
                strokeWidth={3}
                dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#6366f1', strokeWidth: 2 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="тиск"
                stroke="#06b6d4"
                strokeWidth={3}
                dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChartsSection;
