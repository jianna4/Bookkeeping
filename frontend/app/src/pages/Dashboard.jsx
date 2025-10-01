// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE = 'http://127.0.0.1:8000/api'; // Update if needed

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);
  const [priceData, setPriceData] = useState(null);
  const [revenueData, setRevenueData] = useState(null);
  const [basePrice, setBasePrice] = useState(100); // Default in KSh

  // Run analysis on mount
  useEffect(() => {
    handleAnalyze();
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API_BASE}/analyze/`);
      setResults(res.data);

      // Fetch plots
      const trendRes = await axios.get(`${API_BASE}/plot/trend/`);
      const forecastRes = await axios.get(`${API_BASE}/plot/forecast/`);

      setResults((prev) => ({
        ...prev,
        trendPlot: trendRes.data.plot,
        forecastPlot: forecastRes.data.plot,
      }));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze sales data');
    }
    setLoading(false);
  };

  const handlePriceSuggestion = async () => {
    try {
      const res = await axios.post(`${API_BASE}/price/`, { base_price: basePrice });
      setPriceData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to suggest price');
    }
  };

  const handleRevenueCalculation = async () => {
    try {
      const res = await axios.post(`${API_BASE}/revenue/`, { base_price: basePrice });
      setRevenueData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate revenue');
    }
  };

  // Recalculate whenever basePrice or results change
  useEffect(() => {
    if (results && basePrice > 0) {
      handlePriceSuggestion();
      handleRevenueCalculation();
    }
  }, [basePrice, results]);

  if (loading) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Sales Intelligence Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Powered by Django & Machine Learning</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Controls */}
        <section className="bg-white p-6 rounded-xl shadow-md mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Pricing Engine</h2>
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Base Price (KSh)
              </label>
              <input
                type="number"
                step="0.01"
                value={basePrice}
                onChange={(e) => {
                  const value = e.target.value === '' ? '' : parseFloat(e.target.value) || 0;
                  setBasePrice(value); // Allow empty temporarily
                }}
                placeholder="Enter price"
                className="border border-gray-300 rounded-lg px-4 py-2 w-full sm:w-32 focus:ring-2 focus:ring-blue-500 focus:outline-none text-center font-medium"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-6 py-2 rounded-lg transition"
            >
              Refresh Data
            </button>
          </div>
        </section>

        {/* Metrics Grid */}
        {priceData && revenueData && (
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricCard title="Trend Slope" value={results?.slope?.toFixed(3)} unit="" />
            <MetricCard title="Fit Quality (R²)" value={results?.r2?.toFixed(3)} unit="" />
            <MetricCard
              title="Suggested Price"
              value={`KSh ${priceData.suggested_price.toFixed(2)}`}
              color="green"
            />
            <MetricCard
              title="Potential Weekly Gain"
              value={`KSh ${(revenueData.revenue_suggested_price - revenueData.revenue_base_price).toFixed(2)}`}
              color={revenueData.revenue_suggested_price > revenueData.revenue_base_price ? 'green' : 'red'}
            />
          </section>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Trend + Forecast Plot */}
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Sales Trend & Forecast</h3>
            {results?.trendPlot ? (
              <img
                src={`data:image/png;base64,${results.trendPlot}`}
                alt="Sales Trend"
                className="w-full rounded-lg"
              />
            ) : (
              <p className="text-gray-500 italic">Generating trend chart...</p>
            )}
          </div>

          {/* Predicted Week Only */}
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Next 7 Days Forecast</h3>
            {results?.forecastPlot ? (
              <img
                src={`data:image/png;base64,${results.forecastPlot}`}
                alt="Forecast"
                className="w-full rounded-lg"
              />
            ) : (
              <p className="text-gray-500 italic">Generating forecast...</p>
            )}
          </div>
        </div>

        {/* Revenue Breakdown */}
        {revenueData && (
          <section className="mt-8 bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 mb-6">Weekly Revenue Comparison</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                <span className="font-medium text-gray-700">At Base Price (KSh {revenueData.base_price})</span>
                <span className="text-xl font-bold text-blue-700">KSh {revenueData.revenue_base_price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                <span className="font-medium text-gray-700">At Suggested Price (KSh {revenueData.suggested_price})</span>
                <span className="text-xl font-bold text-green-700">KSh {revenueData.revenue_suggested_price.toFixed(2)}</span>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

// Reusable Metric Card
function MetricCard({ title, value, color = 'gray', unit = '' }) {
  const colorClasses = {
    green: 'text-green-700 bg-green-50',
    red: 'text-red-700 bg-red-50',
    gray: 'text-gray-700 bg-gray-50',
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className={`mt-1 text-2xl font-bold ${colorClasses[color] || colorClasses.gray} px-3 py-1 rounded-md inline-block`}>
        {value}
      </p>
      {unit && <p className="text-xs text-gray-500 mt-1">{unit}</p>}
    </div>
  );
}

// Loading Screen
function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-lg text-gray-700">Analyzing sales data...</p>
      </div>
    </div>
  );
}

export default App;