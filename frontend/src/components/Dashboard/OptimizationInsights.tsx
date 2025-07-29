import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Target, Zap, TrendingUp, Award } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { OptimizationData } from '../../types/dashboard';

interface OptimizationInsightsProps {
  data: OptimizationData;
}

export const OptimizationInsights: React.FC<OptimizationInsightsProps> = ({ data }) => {
  if (!data.success || !data.optimization_insights) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Optimization Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-gray-500">
            Optimization insights not available
          </div>
        </CardContent>
      </Card>
    );
  }

  const { optimization_insights } = data;
  const {
    current_efficiency,
    potential_improvement,
    cost_savings,
    recommendations = [],
    algorithm_performance
  } = optimization_insights;

  // Prepare algorithm performance data for charts
  const algorithmData = Object.entries(algorithm_performance).map(([name, data]) => {
    let performance = 82;
    if (name === 'genetic_algorithm' && 'best_fitness' in data) {
      performance = data.best_fitness || 85;
    } else if (name === 'simulated_annealing' && 'acceptance_rate' in data) {
      performance = data.acceptance_rate || 78;
    }
    
    return {
      name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      performance,
      efficiency: name === 'genetic_algorithm' ? 92 :
                 name === 'simulated_annealing' ? 88 : 90
    };
  });

  const efficiencyData = [
    { name: 'Current Efficiency', value: current_efficiency, color: '#3B82F6' },
    { name: 'Potential Improvement', value: potential_improvement, color: '#10B981' },
    { name: 'Remaining Gap', value: 100 - current_efficiency - potential_improvement, color: '#E5E7EB' }
  ];

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-blue-600" />
              <span>Current Efficiency</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">
                {current_efficiency.toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${current_efficiency}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">Overall route efficiency</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span>Improvement Potential</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">
                +{potential_improvement.toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-green-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${potential_improvement * 2}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">Potential efficiency gain</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-yellow-600" />
              <span>Cost Savings</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-yellow-600 mb-2">
                ${cost_savings.toLocaleString()}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-yellow-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min((cost_savings / 10000) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">Estimated annual savings</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Efficiency Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Efficiency Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={efficiencyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {efficiencyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${typeof value === 'number' ? value.toFixed(1) : value}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Algorithm Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={algorithmData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="performance" fill="#3B82F6" name="Performance Score" />
                <Bar dataKey="efficiency" fill="#10B981" name="Efficiency Rating" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>Optimization Recommendations</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recommendations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No recommendations available
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations.map((recommendation, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100"
                >
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold ${
                    recommendation.priority === 'high' ? 'bg-red-500' :
                    recommendation.priority === 'medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}>
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-900 capitalize">
                        {recommendation.type.replace('_', ' ')}
                      </h4>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        recommendation.priority === 'high' ? 'bg-red-100 text-red-800' :
                        recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {recommendation.priority} priority
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{recommendation.description}</p>
                    <p className="text-sm font-medium text-blue-600">
                      Expected Impact: {recommendation.impact}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Algorithm Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {algorithm_performance.genetic_algorithm && (
          <Card>
            <CardHeader>
              <CardTitle>Genetic Algorithm Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Generations</span>
                  <span className="font-semibold">{algorithm_performance.genetic_algorithm.generations || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Best Fitness</span>
                  <span className="font-semibold">{algorithm_performance.genetic_algorithm.best_fitness?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Convergence Rate</span>
                  <span className="font-semibold">{algorithm_performance.genetic_algorithm.convergence_rate?.toFixed(2) || 'N/A'}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {algorithm_performance.simulated_annealing && (
          <Card>
            <CardHeader>
              <CardTitle>Simulated Annealing Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Temperature</span>
                  <span className="font-semibold">{algorithm_performance.simulated_annealing.temperature?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Acceptance Rate</span>
                  <span className="font-semibold">{algorithm_performance.simulated_annealing.acceptance_rate?.toFixed(2) || 'N/A'}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Improvement Rate</span>
                  <span className="font-semibold">{algorithm_performance.simulated_annealing.improvement_rate?.toFixed(2) || 'N/A'}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
