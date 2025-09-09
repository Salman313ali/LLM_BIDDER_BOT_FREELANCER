import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, AlertCircle } from 'lucide-react';
import { configAPI } from '../services/api';

function Configuration() {
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await configAPI.get();
      setConfig(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch configuration');
      console.error('Error fetching config:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await configAPI.update(config);
      setSuccess('Configuration saved successfully! Restart the bot to apply changes.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error && !config) {
    return (
      <div className="text-center py-12">
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
        <button
          onClick={fetchConfig}
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
        <h1 className="text-2xl font-bold text-gray-900">Configuration</h1>
        <button
          onClick={fetchConfig}
          disabled={isLoading}
          className="btn btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-danger-600 mr-2" />
            <span className="text-danger-700">{error}</span>
          </div>
        </div>
      )}

      {success && (
        <div className="p-4 bg-success-50 border border-success-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-success-600 mr-2" />
            <span className="text-success-700">{success}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="label">Freelancer OAuth Token</label>
              <input
                type="password"
                value={config?.oauth_token || ''}
                onChange={(e) => handleInputChange('oauth_token', e.target.value)}
                className="input"
                placeholder="Enter your Freelancer.com OAuth token"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your Freelancer.com OAuth token for API access
              </p>
            </div>

            <div>
              <label className="label">Groq API Key</label>
              <input
                type="password"
                value={config?.groq_api_key || ''}
                onChange={(e) => handleInputChange('groq_api_key', e.target.value)}
                className="input"
                placeholder="Enter your Groq API key"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your Groq API key for AI-powered project analysis
              </p>
            </div>
          </div>
        </div>

        {/* Bot Settings */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Bot Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="label">Bid Limit</label>
              <input
                type="number"
                value={config?.bid_limit || ''}
                onChange={(e) => handleInputChange('bid_limit', parseInt(e.target.value) || 0)}
                className="input"
                min="1"
                max="1000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum number of bids to place in a single session
              </p>
            </div>

            <div>
              <label className="label">Project Search Limit</label>
              <input
                type="number"
                value={config?.project_search_limit || ''}
                onChange={(e) => handleInputChange('project_search_limit', parseInt(e.target.value) || 0)}
                className="input"
                min="1"
                max="100"
              />
              <p className="text-xs text-gray-500 mt-1">
                Number of projects to fetch per search
              </p>
            </div>

            <div>
              <label className="label">Minimum Wait Time (seconds)</label>
              <input
                type="number"
                value={config?.min_wait_time || ''}
                onChange={(e) => handleInputChange('min_wait_time', parseInt(e.target.value) || 0)}
                className="input"
                min="1"
                max="300"
              />
              <p className="text-xs text-gray-500 mt-1">
                Minimum time to wait before placing a bid on a project
              </p>
            </div>

            <div>
              <label className="label">Retry Count</label>
              <input
                type="number"
                value={config?.retry_count || ''}
                onChange={(e) => handleInputChange('retry_count', parseInt(e.target.value) || 0)}
                className="input"
                min="1"
                max="10"
              />
              <p className="text-xs text-gray-500 mt-1">
                Number of retry attempts for failed operations
              </p>
            </div>

            <div>
              <label className="label">Retry Wait (seconds)</label>
              <input
                type="number"
                value={config?.retry_wait_seconds || ''}
                onChange={(e) => handleInputChange('retry_wait_seconds', parseInt(e.target.value) || 0)}
                className="input"
                min="1"
                max="60"
              />
              <p className="text-xs text-gray-500 mt-1">
                Time to wait between retry attempts
              </p>
            </div>
          </div>
        </div>

        {/* Filter Settings */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="label">Language Codes</label>
              <input
                type="text"
                value={config?.language_codes?.join(', ') || ''}
                onChange={(e) => handleInputChange('language_codes', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                className="input"
                placeholder="en, es, fr"
              />
              <p className="text-xs text-gray-500 mt-1">
                Comma-separated list of language codes
              </p>
            </div>

            <div>
              <label className="label">Unwanted Currencies</label>
              <input
                type="text"
                value={config?.unwanted_currencies?.join(', ') || ''}
                onChange={(e) => handleInputChange('unwanted_currencies', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                className="input"
                placeholder="INR, PKR, BDT"
              />
              <p className="text-xs text-gray-500 mt-1">
                Currencies to avoid (comma-separated)
              </p>
            </div>

            <div>
              <label className="label">Unwanted Countries</label>
              <textarea
                value={config?.unwanted_countries?.join(', ') || ''}
                onChange={(e) => handleInputChange('unwanted_countries', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                className="input"
                rows="3"
                placeholder="india, bangladesh, pakistan"
              />
              <p className="text-xs text-gray-500 mt-1">
                Countries to avoid (comma-separated)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bid Writing Configuration */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Bid Writing Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="label">Service Offerings</label>
            <textarea
              value={config?.service_offerings || ''}
              onChange={(e) => handleInputChange('service_offerings', e.target.value)}
              className="input"
              rows="6"
              placeholder="Describe your services that the bot should bid on..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Describe your services that the AI should look for when analyzing projects
            </p>
          </div>

          <div>
            <label className="label">Bid Writing Style</label>
            <textarea
              value={config?.bid_writing_style || ''}
              onChange={(e) => handleInputChange('bid_writing_style', e.target.value)}
              className="input"
              rows="8"
              placeholder="Customize how the AI writes your bids..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Customize the tone, style, and content of your bids
            </p>
          </div>

          <div>
            <label className="label">Portfolio Links</label>
            <textarea
              value={config?.portfolio_links || ''}
              onChange={(e) => handleInputChange('portfolio_links', e.target.value)}
              className="input"
              rows="4"
              placeholder="Enter your portfolio links (one per line)..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Your portfolio links that will be included in bids (one per line)
            </p>
          </div>

          <div>
            <label className="label">Signature</label>
            <input
              type="text"
              value={config?.signature || ''}
              onChange={(e) => handleInputChange('signature', e.target.value)}
              className="input"
              placeholder="Your name or signature for bids"
            />
            <p className="text-xs text-gray-500 mt-1">
              Your name or signature that will appear at the end of bids
            </p>
          </div>
        </div>
      </div>

      {/* Skill IDs */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill IDs</h3>
        <div>
          <label className="label">Skill IDs</label>
          <textarea
            value={config?.skill_ids?.join(', ') || ''}
            onChange={(e) => handleInputChange('skill_ids', e.target.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)))}
            className="input"
            rows="4"
            placeholder="3, 9, 13, 15, 17, 20, 21, 26, 32, 38, 44, 57, 69, 70, 77, 106, 107, 115, 116, 127, 137, 168, 170, 174, 196, 197, 204, 229, 232, 234, 247, 250, 262, 264, 277, 278, 284, 305, 310, 323, 324, 335, 359, 365, 368, 369, 371, 375, 408, 412, 433, 436, 444, 445, 482, 502, 564, 624, 662, 710, 759, 878, 950, 953, 959, 1063, 1185, 1314, 1623, 2071, 2128, 2222, 2245, 2338, 2342, 2507, 2586, 2587, 2589, 2605, 2625, 2645, 2673, 2698, 2717, 2745"
          />
          <p className="text-xs text-gray-500 mt-1">
            Comma-separated list of Freelancer.com skill IDs to search for
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>{isSaving ? 'Saving...' : 'Save Configuration'}</span>
        </button>
      </div>
    </div>
  );
}

export default Configuration;

