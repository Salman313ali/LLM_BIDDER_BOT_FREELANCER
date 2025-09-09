import React, { useState, useEffect } from 'react';
import { Plus, RefreshCw, Users, Activity } from 'lucide-react';
import SessionCard from '../components/SessionCard';
import SessionModal from '../components/SessionModal';
import { sessionsAPI } from '../services/sessionsAPI';

function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await sessionsAPI.getAll();
      setSessions(response.data.sessions || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSession = async (sessionData) => {
    try {
      await sessionsAPI.create(sessionData);
      await fetchSessions();
    } catch (err) {
      throw err;
    }
  };

  const handleUpdateSession = async (sessionData) => {
    try {
      await sessionsAPI.update(editingSession.session_id, sessionData);
      await fetchSessions();
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteSession = (sessionId) => {
    setSessions(prev => prev.filter(s => s.session_id !== sessionId));
  };

  const openCreateModal = () => {
    setEditingSession(null);
    setIsEditing(false);
    setIsModalOpen(true);
  };

  const openEditModal = (session) => {
    setEditingSession(session);
    setIsEditing(true);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingSession(null);
    setIsEditing(false);
  };

  const getTotalStats = () => {
    const totalSessions = sessions.length;
    const runningSessions = sessions.filter(s => s.is_active).length;
    const totalBids = sessions.reduce((sum, s) => sum + (s.total_bids_placed || 0), 0);
    
    return { totalSessions, runningSessions, totalBids };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const stats = getTotalStats();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sessions</h1>
        <div className="flex space-x-3">
          <button
            onClick={fetchSessions}
            disabled={isLoading}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={openCreateModal}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Session</span>
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Sessions</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalSessions}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary-100">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running Sessions</p>
              <p className="text-3xl font-bold text-gray-900">{stats.runningSessions}</p>
            </div>
            <div className="p-3 rounded-lg bg-success-100">
              <Activity className="w-6 h-6 text-success-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Bids</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalBids}</p>
            </div>
            <div className="p-3 rounded-lg bg-warning-100">
              <Activity className="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
          <div className="text-danger-700">{error}</div>
        </div>
      )}

      {/* Sessions Grid */}
      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No sessions</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first session.
          </p>
          <div className="mt-6">
            <button
              onClick={openCreateModal}
              className="btn btn-primary flex items-center space-x-2 mx-auto"
            >
              <Plus className="w-4 h-4" />
              <span>Create Session</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {sessions.map((session) => (
            <SessionCard
              key={session.session_id}
              session={session}
              onUpdate={openEditModal}
              onDelete={handleDeleteSession}
            />
          ))}
        </div>
      )}

      {/* Session Modal */}
      <SessionModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSave={isEditing ? handleUpdateSession : handleCreateSession}
        session={editingSession}
        isEditing={isEditing}
      />
    </div>
  );
}

export default Sessions;
