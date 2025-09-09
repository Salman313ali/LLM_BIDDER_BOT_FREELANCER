import React, { useState, useEffect } from 'react';
import { ExternalLink, Calendar, DollarSign, Clock, CheckCircle, XCircle, Users } from 'lucide-react';
import { bidsAPI } from '../services/api';
import { sessionsAPI } from '../services/sessionsAPI';

function Bids() {
  const [bids, setBids] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSession, setFilterSession] = useState('all');

  useEffect(() => {
    fetchBids();
    fetchSessions();
  }, []);

  const fetchBids = async () => {
    try {
      const response = await bidsAPI.getAll(100);
      setBids(response.data.bids || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch bids');
      console.error('Error fetching bids:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await sessionsAPI.getAll();
      setSessions(response.data.sessions || []);
    } catch (err) {
      console.error('Error fetching sessions:', err);
    }
  };

  const filteredBids = bids.filter(bid => {
    const matchesSearch = bid.project_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         bid.project_title?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || bid.status === filterStatus;
    const matchesSession = filterSession === 'all' || bid.session_id === filterSession;
    return matchesSearch && matchesStatus && matchesSession;
  });

  const getSessionName = (sessionId) => {
    const session = sessions.find(s => s.session_id === sessionId);
    return session ? session.name : 'Unknown Session';
  };

  const formatCurrency = (amount, currency) => {
    if (!amount) return 'N/A';
    return `${currency || 'USD'} ${amount.toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'placed':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'won':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'lost':
        return <XCircle className="w-4 h-4 text-danger-600" />;
      case 'withdrawn':
        return <XCircle className="w-4 h-4 text-gray-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'placed':
        return 'bg-primary-100 text-primary-800';
      case 'won':
        return 'bg-success-100 text-success-800';
      case 'lost':
        return 'bg-danger-100 text-danger-800';
      case 'withdrawn':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
        <button
          onClick={fetchBids}
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
        <h1 className="text-2xl font-bold text-gray-900">Bids</h1>
        <div className="text-sm text-gray-500">
          {filteredBids.length} of {bids.length} bids
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by project ID or title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input"
            >
              <option value="all">All Statuses</option>
              <option value="placed">Placed</option>
              <option value="won">Won</option>
              <option value="lost">Lost</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </div>
          <div>
            <select
              value={filterSession}
              onChange={(e) => setFilterSession(e.target.value)}
              className="input"
            >
              <option value="all">All Sessions</option>
              {sessions.map(session => (
                <option key={session.session_id} value={session.session_id}>
                  {session.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Bids List */}
      <div className="space-y-4">
        {filteredBids.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No bids found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || filterStatus !== 'all' || filterSession !== 'all'
                ? 'Try adjusting your search or filter criteria.'
                : 'No bids have been placed yet.'}
            </p>
          </div>
        ) : (
          filteredBids.map((bid) => (
            <div key={bid.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {bid.project_title || `Project ${bid.project_id}`}
                    </h3>
                    <span className={`status-badge ${getStatusColor(bid.status)}`}>
                      {getStatusIcon(bid.status)}
                      <span className="ml-1">{bid.status || 'Unknown'}</span>
                    </span>
                  </div>
                  
                  {bid.project_title && (
                    <div className="text-sm text-gray-500 mb-2">
                      Project ID: {bid.project_id}
                    </div>
                  )}
                  
                  {bid.session_id && (
                    <div className="flex items-center space-x-2 mb-2">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        Session: {getSessionName(bid.session_id)}
                      </span>
                    </div>
                  )}
                  
                  <p className="text-gray-600 mb-4 line-clamp-3">
                    {bid.bid_content || 'No bid content available'}
                  </p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">Amount:</span>
                      <span className="font-medium">
                        {formatCurrency(bid.bid_amount, bid.currency_code)}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">Timeline:</span>
                      <span className="font-medium">{bid.bid_period} days</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">Bid Date:</span>
                      <span className="font-medium">{formatDate(bid.bid_date)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="ml-4 flex-shrink-0">
                  {bid.project_link && (
                    <a
                      href={bid.project_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary flex items-center space-x-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>View Project</span>
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Bids;

