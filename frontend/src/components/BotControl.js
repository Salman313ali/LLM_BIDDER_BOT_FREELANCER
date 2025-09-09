import React, { useState, useEffect } from 'react';
import { Play, Square, RefreshCw, AlertCircle } from 'lucide-react';
import { botAPI } from '../services/api';

function BotControl() {
  const [botStatus, setBotStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bidLimit, setBidLimit] = useState(75);

  useEffect(() => {
    fetchBotStatus();
    const interval = setInterval(fetchBotStatus, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchBotStatus = async () => {
    try {
      const response = await botAPI.getStatus();
      setBotStatus(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch bot status');
      console.error('Error fetching bot status:', err);
    }
  };

  const startBot = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await botAPI.start(bidLimit);
      setBotStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start bot');
    } finally {
      setIsLoading(false);
    }
  };

  const stopBot = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await botAPI.stop();
      setBotStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop bot');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'text-success-600 bg-success-100';
      case 'stopped':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-danger-600 bg-danger-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <div className="w-2 h-2 bg-success-600 rounded-full animate-pulse" />;
      case 'stopped':
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />;
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Bot Control</h2>
        <div className="flex items-center space-x-2">
          {getStatusIcon(botStatus?.is_running ? 'running' : 'stopped')}
          <span className={`status-badge ${getStatusColor(botStatus?.is_running ? 'running' : 'stopped')}`}>
            {botStatus?.is_running ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-danger-600 mr-2" />
            <span className="text-danger-700">{error}</span>
          </div>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="label">Bid Limit</label>
          <input
            type="number"
            value={bidLimit}
            onChange={(e) => setBidLimit(parseInt(e.target.value) || 0)}
            className="input"
            min="1"
            max="1000"
            disabled={botStatus?.is_running}
          />
        </div>

        <div className="flex space-x-3">
          <button
            onClick={startBot}
            disabled={isLoading || botStatus?.is_running}
            className="btn btn-success flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>{isLoading ? 'Starting...' : 'Start Bot'}</span>
          </button>

          <button
            onClick={stopBot}
            disabled={isLoading || !botStatus?.is_running}
            className="btn btn-danger flex items-center space-x-2"
          >
            <Square className="w-4 h-4" />
            <span>{isLoading ? 'Stopping...' : 'Stop Bot'}</span>
          </button>

          <button
            onClick={fetchBotStatus}
            disabled={isLoading}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {botStatus && (
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
            <div>
              <div className="text-sm text-gray-500">Bids Placed</div>
              <div className="text-2xl font-bold text-gray-900">
                {botStatus.bid_counter || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Processed Projects</div>
              <div className="text-2xl font-bold text-gray-900">
                {botStatus.processed_projects || 0}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BotControl;


