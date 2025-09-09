import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  FolderOpen, 
  FileText, 
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';
import BotControl from '../components/BotControl';
import StatsCard from '../components/StatsCard';
import { analyticsAPI, botAPI } from '../services/api';

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsResponse, statusResponse] = await Promise.all([
        analyticsAPI.getOverview(),
        botAPI.getStatus()
      ]);
      
      setAnalytics(analyticsResponse.data);
      setBotStatus(statusResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <XCircle className="mx-auto h-12 w-12 text-danger-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 btn btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Bot Control Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BotControl />
        </div>
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Bot Status</span>
                <span className={`status-badge ${botStatus?.is_running ? 'status-running' : 'status-stopped'}`}>
                  {botStatus?.is_running ? 'Running' : 'Stopped'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Current Bids</span>
                <span className="font-medium">{botStatus?.bid_counter || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Session ID</span>
                <span className="font-mono text-xs text-gray-500">
                  {botStatus?.session_id ? botStatus.session_id.slice(0, 8) + '...' : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Projects"
          value={analytics?.total_projects || 0}
          icon={FolderOpen}
          color="primary"
        />
        <StatsCard
          title="Total Bids"
          value={analytics?.total_bids || 0}
          icon={FileText}
          color="success"
        />
        <StatsCard
          title="Success Rate"
          value={`${analytics?.success_rate || 0}%`}
          icon={TrendingUp}
          color="warning"
        />
        <StatsCard
          title="Active Sessions"
          value={analytics?.recent_sessions?.filter(s => s.status === 'running').length || 0}
          icon={Bot}
          color="danger"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions</h3>
          <div className="space-y-3">
            {analytics?.recent_sessions?.slice(0, 5).map((session, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    session.status === 'running' ? 'bg-success-500' : 
                    session.status === 'stopped' ? 'bg-gray-400' : 'bg-danger-500'
                  }`} />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      Session {session.session_id?.slice(0, 8)}...
                    </div>
                    <div className="text-xs text-gray-500">
                      {session.start_time ? new Date(session.start_time).toLocaleString() : 'N/A'}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {session.total_bids_placed || 0} bids
                  </div>
                  <div className={`text-xs ${
                    session.status === 'running' ? 'text-success-600' : 
                    session.status === 'stopped' ? 'text-gray-500' : 'text-danger-600'
                  }`}>
                    {session.status}
                  </div>
                </div>
              </div>
            )) || (
              <div className="text-center py-4 text-gray-500">
                No recent sessions found
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Status</span>
              <span className="status-badge status-running">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className="status-badge status-running">Connected</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">AI Service</span>
              <span className="status-badge status-running">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Freelancer API</span>
              <span className="status-badge status-running">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

