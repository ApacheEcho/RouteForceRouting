import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Brain, TrendingUp, Target, Zap } from 'lucide-react';
import { MLInsightsData } from '../../types/dashboard';

interface MLInsightsProps {
  data: MLInsightsData;
}

export const MLInsights: React.FC<MLInsightsProps> = ({ data }) => {
  if (!data.success) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ML Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-gray-500">
            ML insights not available
          </div>
        </CardContent>
      </Card>
    );
  }

  const { predictions = [], model_performance } = data;

  return (
    <div className="space-y-6">
      {/* Model Performance Overview */}
      {model_performance && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5" />
              <span>Model Performance</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {(model_performance.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Model Accuracy</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {(model_performance.confidence_score * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Confidence Score</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {model_performance.training_samples.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Training Samples</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Predictions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Recent ML Predictions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {predictions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No recent predictions available
            </div>
          ) : (
            <div className="space-y-4">
              {predictions.slice(0, 10).map((prediction) => (
                <div
                  key={prediction.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      prediction.type === 'route_optimization' ? 'bg-blue-100' :
                      prediction.type === 'demand_forecast' ? 'bg-green-100' :
                      prediction.type === 'efficiency_prediction' ? 'bg-purple-100' :
                      'bg-gray-100'
                    }`}>
                      {prediction.type === 'route_optimization' ? <Target className="w-4 h-4 text-blue-600" /> :
                       prediction.type === 'demand_forecast' ? <TrendingUp className="w-4 h-4 text-green-600" /> :
                       prediction.type === 'efficiency_prediction' ? <Zap className="w-4 h-4 text-purple-600" /> :
                       <Brain className="w-4 h-4 text-gray-600" />}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 capitalize">
                        {prediction.type.replace('_', ' ')}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {typeof prediction.prediction === 'object' 
                          ? JSON.stringify(prediction.prediction).substring(0, 100) + '...'
                          : String(prediction.prediction).substring(0, 100)
                        }
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      prediction.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                      prediction.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {(prediction.confidence * 100).toFixed(0)}% confidence
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(prediction.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ML Model Types */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Active ML Models</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium">Route Optimization</span>
                <span className="text-sm text-blue-600">Ensemble Model</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium">Demand Forecasting</span>
                <span className="text-sm text-green-600">Time Series</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="font-medium">Efficiency Prediction</span>
                <span className="text-sm text-purple-600">Neural Network</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <span className="font-medium">Anomaly Detection</span>
                <span className="text-sm text-orange-600">Isolation Forest</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Model Training Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Route Optimizer</span>
                  <span>95%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '95%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Demand Predictor</span>
                  <span>87%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '87%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Efficiency Model</span>
                  <span>92%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Anomaly Detector</span>
                  <span>78%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-orange-600 h-2 rounded-full" style={{ width: '78%' }}></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
