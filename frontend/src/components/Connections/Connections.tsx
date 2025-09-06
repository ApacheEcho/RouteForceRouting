import React from 'react';
import { connectionsApi } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import Skeleton from '../ui/Skeleton';

interface Provider {
  key: string;
  name: string;
  type: string;
  auth: string;
  docs: string;
}

export const Connections: React.FC = () => {
  const [loading, setLoading] = React.useState(true);
  const [providers, setProviders] = React.useState<Provider[]>([]);
  const [status, setStatus] = React.useState<Record<string, any>>({});
  const [error, setError] = React.useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = React.useState<Record<string, string>>({});

  const load = async () => {
    try {
      setLoading(true);
      const [p, s] = await Promise.all([
        connectionsApi.listProviders(),
        connectionsApi.getStatus(),
      ]);
      setProviders(p);
      setStatus(s);
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => { load(); }, []);

  const handleConnect = async (provider: Provider) => {
    try {
      if (provider.auth.includes('api_key')) {
        const token = apiKeyInput[provider.key];
        await connectionsApi.connect(provider.key, token);
      } else {
        const url = await connectionsApi.oauthStart(provider.key);
        if (url) window.open(url, '_blank');
      }
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDisconnect = async (provider: Provider) => {
    try {
      await connectionsApi.disconnect(provider.key);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">🔗 Connections</h1>
        <p className="text-gray-600">Bring your own keys and securely connect your services</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded p-4 mb-6">{error}</div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 3xl:grid-cols-3 4k:grid-cols-4 8k:grid-cols-6 rf-grid-gap">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}><CardContent><Skeleton className="h-24 w-full" /></CardContent></Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 3xl:grid-cols-3 4k:grid-cols-4 8k:grid-cols-6 rf-grid-gap">
          {providers.map((p) => {
            const st = status[p.key] || {};
            const connected = !!st.connected;
            return (
              <Card key={p.key}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{p.name}</span>
                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${connected ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'}`}>
                      {connected ? 'Connected' : 'Not connected'}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-3">Type: {p.type.toUpperCase()} • Auth: {p.auth}</p>
                  <div className="space-x-2">
                    {p.auth.includes('api_key') && !connected && (
                      <input
                        type="password"
                        placeholder="Enter API Key"
                        className="border border-gray-300 rounded px-2 py-1 text-sm mb-2"
                        onChange={(e) => setApiKeyInput((s) => ({ ...s, [p.key]: e.target.value }))}
                      />
                    )}
                  </div>
                  <div className="flex items-center space-x-2 mt-2">
                    {!connected ? (
                      <button onClick={() => handleConnect(p)} className="px-3 py-2 text-sm rounded bg-blue-600 text-white hover:bg-blue-700">Connect</button>
                    ) : (
                      <button onClick={() => handleDisconnect(p)} className="px-3 py-2 text-sm rounded bg-gray-200 hover:bg-gray-300">Disconnect</button>
                    )}
                    <a href={p.docs} target="_blank" rel="noreferrer" className="text-sm text-blue-600 hover:underline">Docs</a>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Connections;

