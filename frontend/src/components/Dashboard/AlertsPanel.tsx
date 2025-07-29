import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { AlertTriangle, Info, AlertCircle, CheckCircle } from 'lucide-react';
import { AlertsData } from '../../types/dashboard';

interface AlertsPanelProps {
  alerts: AlertsData;
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts }) => {
  if (!alerts.real_time_alerts) {
    return null;
  }

  const { active_alerts, health_score, alert_summary } = alerts.real_time_alerts;

  if (active_alerts.length === 0) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardContent className="p-4">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <h3 className="font-medium text-green-800">All Systems Operational</h3>
              <p className="text-sm text-green-600">No active alerts. Health score: {health_score}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getAlertIcon = (priority: string, severity?: string) => {
    if (severity === 'critical' || priority === 'high') {
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    } else if (severity === 'warning' || priority === 'medium') {
      return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
    return <Info className="w-5 h-5 text-blue-500" />;
  };

  const getAlertStyles = (priority: string, severity?: string) => {
    if (severity === 'critical' || priority === 'high') {
      return 'border-red-200 bg-red-50';
    } else if (severity === 'warning' || priority === 'medium') {
      return 'border-yellow-200 bg-yellow-50';
    }
    return 'border-blue-200 bg-blue-50';
  };

  return (
    <Card className="border-orange-200 bg-orange-50">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-orange-800">Active Alerts</CardTitle>
          <div className="flex items-center space-x-4 text-sm text-orange-600">
            <span>Health Score: {health_score}%</span>
            <span>Total: {alert_summary.total_alerts}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {active_alerts.slice(0, 5).map((alert) => (
            <div
              key={alert.id}
              className={`p-3 rounded-lg border ${getAlertStyles(alert.priority, alert.severity)}`}
            >
              <div className="flex items-start space-x-3">
                {getAlertIcon(alert.priority, alert.severity)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{alert.title}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.priority === 'high' ? 'bg-red-100 text-red-800' :
                      alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                  {alert.action && (
                    <p className="text-sm text-gray-500 mt-2 italic">
                      Action: {alert.action}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {active_alerts.length > 5 && (
            <div className="text-center pt-2">
              <button className="text-sm text-orange-600 hover:text-orange-800 font-medium">
                View {active_alerts.length - 5} more alerts
              </button>
            </div>
          )}
        </div>

        {/* Alert Summary */}
        <div className="mt-4 pt-4 border-t border-orange-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-red-600">{alert_summary.high_priority}</div>
              <div className="text-xs text-gray-500">High Priority</div>
            </div>
            <div>
              <div className="text-lg font-bold text-yellow-600">{alert_summary.medium_priority}</div>
              <div className="text-xs text-gray-500">Medium Priority</div>
            </div>
            <div>
              <div className="text-lg font-bold text-blue-600">{alert_summary.low_priority}</div>
              <div className="text-xs text-gray-500">Low Priority</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
