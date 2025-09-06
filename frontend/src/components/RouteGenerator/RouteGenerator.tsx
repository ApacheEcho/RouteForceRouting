import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { routeApi } from '../../services/api';

const RouteGenerator: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const parseCsv = async (file: File): Promise<Array<{ name?: string; address?: string; lat?: number; lon?: number }>> => {
    const text = await file.text();
    const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length === 0) return [];
    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    const idx = (name: string) => header.findIndex(h => h === name);
    const nameIdx = idx('name') !== -1 ? idx('name') : idx('store_name');
    const addrIdx = idx('address');
    const latIdx = idx('lat') !== -1 ? idx('lat') : idx('latitude');
    const lonIdx = idx('lon') !== -1 ? idx('lon') : idx('lng') !== -1 ? idx('lng') : idx('longitude');
    const rows = lines.slice(1).map(line => line.split(',')).filter(cols => cols.some(c => c && c.trim().length > 0));
    const stops = rows.map(cols => {
      const stop: any = {};
      if (nameIdx !== -1) stop.name = (cols[nameIdx] || '').trim();
      if (addrIdx !== -1) stop.address = (cols[addrIdx] || '').trim();
      const latStr = latIdx !== -1 ? (cols[latIdx] || '').trim() : '';
      const lonStr = lonIdx !== -1 ? (cols[lonIdx] || '').trim() : '';
      const lat = latStr ? Number(latStr) : undefined;
      const lon = lonStr ? Number(lonStr) : undefined;
      if (!Number.isNaN(lat as number) && !Number.isNaN(lon as number)) {
        stop.lat = lat;
        stop.lon = lon;
      }
      return stop;
    });
    return stops.filter(s => s.address || (typeof s.lat === 'number' && typeof s.lon === 'number'));
  };

  const handleGenerate = async () => {
    if (!file) return;
    setIsGenerating(true);
    try {
      const stops = await parseCsv(file);
      if (stops.length === 0) {
        throw new Error('No valid rows found. Ensure CSV has headers and at least one row.');
      }
      const data = await routeApi.optimize({ stops });
      setResults(data);
    } catch (error) {
      console.error('Error generating route:', error);
      setResults({ error: (error as Error).message });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link to="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📍 Route Generator</h1>
        <p className="text-gray-600">Upload your store data and generate optimized routes</p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Upload Store Data</h3>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">📁</div>
          
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          
          <label
            htmlFor="file-upload"
            className="cursor-pointer text-blue-600 hover:text-blue-800"
          >
            <div className="text-lg font-medium">Choose file or drag and drop</div>
            <div className="text-sm text-gray-500 mt-1">CSV, Excel files supported</div>
          </label>
          
          {file && (
            <div className="mt-4 text-sm text-gray-700">
              Selected: {file.name}
            </div>
          )}
        </div>

        {/* Options */}
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Optimization Type
            </label>
            <select className="w-full border border-gray-300 rounded-md p-2">
              <option>Distance Optimization</option>
              <option>Time Optimization</option>
              <option>Fuel Efficiency</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Stops per Route
            </label>
            <input
              type="number"
              defaultValue={20}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
        </div>

        {/* Generate Button */}
        <div className="mt-6">
          <button
            onClick={handleGenerate}
            disabled={!file || isGenerating}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {isGenerating ? 'Generating Route...' : 'Generate Optimized Route'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Optimization Results</h3>
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {(results.metadata?.optimization_score ?? results.total_distance) || 'N/A'}
          </div>
          <div className="text-sm text-gray-600">Total Distance</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {results.metadata?.processing_time || results.total_time || 'N/A'}
          </div>
          <div className="text-sm text-gray-600">Estimated Time</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">
            {results.route?.length ?? results.data?.route?.length ?? 'N/A'}
          </div>
          <div className="text-sm text-gray-600">Optimization %</div>
        </div>
          </div>
          
          <div className="mt-4">
            <Link
              to="/dashboard"
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
            >
              View in Dashboard
            </Link>
          </div>
        </div>
      )}

      {/* Sample Data Info */}
      <div className="bg-blue-50 rounded-lg p-6 mt-6">
        <h4 className="font-semibold mb-2">📋 Expected Data Format</h4>
        <p className="text-sm text-gray-700 mb-2">
          Your CSV should include columns for: store_name, address, city, state, zip_code
        </p>
        <p className="text-sm text-gray-600">
          Optional: priority, sales_volume, time_window_start, time_window_end
        </p>
      </div>
    </div>
  );
};

export default RouteGenerator;
