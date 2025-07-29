import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { TrendingUp, MapPin, Users, BarChart } from 'lucide-react';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { PredictiveData } from '../../types/dashboard';

interface PredictiveAnalyticsProps {
  data: PredictiveData;
}

export const PredictiveAnalytics: React.FC<PredictiveAnalyticsProps> = ({ data }) => {
  if (!data.success) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Predictive Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-gray-500">
            Predictive analytics not available
          </div>
        </CardContent>
      </Card>
    );
  }

  const { demand_forecast = [], capacity_optimization } = data;

  // Prepare chart data
  const chartData = demand_forecast.map(item => ({
    location: item.location.length > 15 ? item.location.substring(0, 15) + '...' : item.location,
    demand: item.predicted_demand,
    confidence: item.confidence * 100
  }));

  return (
    <div className="space-y-6">
      {/* Capacity Optimization Overview */}
      {capacity_optimization && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart className="w-5 h-5" />
                <span>Current Utilization</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {(capacity_optimization.current_utilization * 100).toFixed(1)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${capacity_optimization.current_utilization * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">Fleet capacity currently in use</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Predicted Peak</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {(capacity_optimization.predicted_peak * 100).toFixed(1)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className="bg-orange-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${capacity_optimization.predicted_peak * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">Expected peak utilization</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>Optimization Score</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {((1 - capacity_optimization.current_utilization + capacity_optimization.predicted_peak) * 50).toFixed(0)}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className="bg-green-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${((1 - capacity_optimization.current_utilization + capacity_optimization.predicted_peak) * 50)}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">Overall optimization efficiency</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Demand Forecast Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="w-5 h-5" />
            <span>Demand Forecast by Location</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {demand_forecast.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No demand forecast data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <RechartsBarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="location" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="demand" fill="#3B82F6" name="Predicted Demand" />
              </RechartsBarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Detailed Demand Forecast */}
      <Card>
        <CardHeader>
          <CardTitle>Detailed Demand Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          {demand_forecast.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No detailed predictions available
            </div>
          ) : (
            <div className="space-y-4">
              {demand_forecast.map((forecast, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{forecast.location}</h4>
                    <p className="text-sm text-gray-600">
                      Predicted demand: <span className="font-semibold">{forecast.predicted_demand.toFixed(0)} units</span>
                    </p>
                    {forecast.factors.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-500 mb-1">Influencing factors:</p>
                        <div className="flex flex-wrap gap-1">
                          {forecast.factors.map((factor, factorIndex) => (
                            <span
                              key={factorIndex}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                            >
                              {factor}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      forecast.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                      forecast.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {(forecast.confidence * 100).toFixed(0)}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      {capacity_optimization?.recommendations && capacity_optimization.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Optimization Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {capacity_optimization.recommendations.map((recommendation, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"
                >
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-sm font-semibold">
                    {index + 1}
                  </div>
                  <p className="text-sm text-gray-700">{recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
