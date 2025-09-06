import React from 'react';
import { systemApi } from '../../services/api';

export const HealthStatus: React.FC = () => {
  const [status, setStatus] = React.useState<'healthy' | 'degraded' | 'unhealthy' | 'loading'>('loading');
  const [latency, setLatency] = React.useState<number | null>(null);

  const fetchHealth = async () => {
    try {
      const t0 = performance.now();
      const data = await systemApi.getHealth();
      const t1 = performance.now();
      setLatency(Math.round(t1 - t0));
      setStatus((data?.status as any) || 'healthy');
    } catch {
      setStatus('unhealthy');
    }
  };

  React.useEffect(() => {
    fetchHealth();
    const id = setInterval(fetchHealth, 30000);
    return () => clearInterval(id);
  }, []);

  const color = status === 'healthy' ? 'bg-green-500' : status === 'degraded' ? 'bg-yellow-500' : status === 'loading' ? 'bg-gray-400' : 'bg-red-500';
  const label = status === 'loading' ? 'Checking' : status;

  return (
    <div className="inline-flex items-center space-x-2 text-sm" title={`Backend status: ${label}${latency ? ` (${latency}ms)` : ''}`}>
      <span className={`inline-block w-2.5 h-2.5 rounded-full ${color}`}></span>
      <span className="capitalize text-gray-700 dark:text-gray-300">{label}</span>
      {latency !== null && <span className="text-gray-400">{latency}ms</span>}
    </div>
  );
};

export default HealthStatus;

