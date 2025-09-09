import React, { useState, useEffect } from 'react';
import { Play, Square, Settings, Trash2, Eye, BarChart3 } from 'lucide-react';
import { sessionsAPI } from '../services/sessionsAPI';

function SessionCard({ session, onUpdate, onDelete }) {
  const [botStatus, setBotStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBotStatus();
    const interval = setInterval(fetchBotStatus, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [session.session_id]);

  const fetchBotStatus = async () => {
    try {
      const response = await sessionsAPI.getBotStatus(session.session_id);
      setBotStatus(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch bot status');
    }
  };

  const startBot = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await sessionsAPI.startBot(session.session_id);
      await fetchBotStatus();
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
      await sessionsAPI.stopBot(session.session_id);
      await fetchBotStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop bot');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSession = async () => {
    if (window.confirm(`Are you sure you want to delete session "${session.name}"?`)) {
      try {
        await sessionsAPI.delete(session.session_id);
        onDelete(session.session_id);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete session');
      }
    }
  };

  const getStatusColor = (isRunning) => {
    return isRunning ? 'text-success-600 bg-success-100' : 'text-gray-600 bg-gray-100';
  };

  const getStatusIcon = (isRunning) => {
    return isRunning ? (
      <div className="w-2 h-2 bg-success-600 rounded-full animate-pulse" />
    ) : (
      <div className="w-2 h-2 bg-gray-400 rounded-full" />
    );
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{session.name}</h3>
            <div className="flex items-center space-x-2">
              {getStatusIcon(botStatus?.is_running)}
              <span className={`status-badge ${getStatusColor(botStatus?.is_running)}`}>
                {botStatus?.is_running ? 'Running' : 'Stopped'}
              </span>
            </div>
          </div>
          
          <div className="text-sm text-gray-600 space-y-1">
            <div>Session ID: <span className="font-mono text-xs">{session.session_id.slice(0, 8)}...</span></div>
            <div>Created: {new Date(session.created_at).toLocaleDateString()}</div>
            <div>Bid Limit: {session.bid_limit}</div>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => onUpdate(session)}
            className="btn btn-secondary p-2"
            title="Edit Session"
          >
            <Settings className="w-4 h-4" />
          </button>
          <button
            onClick={deleteSession}
            className="btn btn-danger p-2"
            title="Delete Session"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg">
          <div className="text-danger-700 text-sm">{error}</div>
        </div>
      )}

      <div className="flex space-x-2 mb-4">
        <button
          onClick={startBot}
          disabled={isLoading || botStatus?.is_running}
          className="btn btn-success flex items-center space-x-2 flex-1"
        >
          <Play className="w-4 h-4" />
          <span>{isLoading ? 'Starting...' : 'Start Bot'}</span>
        </button>

        <button
          onClick={stopBot}
          disabled={isLoading || !botStatus?.is_running}
          className="btn btn-danger flex items-center space-x-2 flex-1"
        >
          <Square className="w-4 h-4" />
          <span>{isLoading ? 'Stopping...' : 'Stop Bot'}</span>
        </button>
      </div>

      {botStatus && (
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <div className="text-sm text-gray-500">Bids Placed</div>
            <div className="text-xl font-bold text-gray-900">
              {botStatus.bid_counter || 0}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Processed Projects</div>
            <div className="text-xl font-bold text-gray-900">
              {botStatus.processed_projects || 0}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SessionCard;




