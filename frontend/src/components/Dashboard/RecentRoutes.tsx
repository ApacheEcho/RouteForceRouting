import React from 'react';
import { dashboardApi } from '../../services/api';
import { Card, CardHeader, CardContent, CardTitle } from '../ui/Card';
import Skeleton from '../ui/Skeleton';

interface RouteItem {
  id: number | string;
  name: string;
  status: string;
  distance?: number;
  created_at?: string;
}

export const RecentRoutes: React.FC = () => {
  const [routes, setRoutes] = React.useState<RouteItem[]>([]);
  const [loading, setLoading] = React.useState(true);

  const load = async () => {
    try {
      const data = await dashboardApi.getRecentRoutes();
      setRoutes(data || []);
    } catch {
      setRoutes([]);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => { load(); }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Routes</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3" aria-busy="true" aria-live="polite">
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-2/5" />
            <Skeleton className="h-4 w-1/4" />
          </div>
        ) : routes.length === 0 ? (
          <p className="text-gray-500">No routes yet. Generate your first route to see it here.</p>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-800">
            {routes.slice(0, 6).map((r) => (
              <li key={r.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="font-medium">{r.name || `Route ${r.id}`}</p>
                  <p className="text-xs text-gray-500">
                    {r.created_at ? new Date(r.created_at).toLocaleString() : ''}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                    r.status === 'completed' ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                    r.status === 'in_progress' ? 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300' :
                    'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                  }`}>
                    {r.status}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentRoutes;
