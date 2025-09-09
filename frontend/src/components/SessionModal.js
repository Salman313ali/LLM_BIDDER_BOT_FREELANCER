import React, { useState, useEffect } from 'react';
import { X, Save, Eye, EyeOff } from 'lucide-react';

function SessionModal({ isOpen, onClose, onSave, session = null, isEditing = false }) {
  const [formData, setFormData] = useState({
    name: '',
    oauth_token: '',
    groq_api_key: '',
    service_offerings: '',
    bid_writing_style: '',
    portfolio_links: '',
    signature: '',
    bid_limit: 75,
    project_search_limit: 10,
    min_wait_time: 32,
    skill_ids: '',
    language_codes: 'en',
    unwanted_currencies: 'INR, PKR, BDT',
    unwanted_countries: 'india, bangladesh, pakistan, jamaica, srilanka, sri lanka, nepal, south africa, kenya, uganda, egypt, indonesia, philippines, afganistan'
  });

  const [showOAuthToken, setShowOAuthToken] = useState(false);
  const [showGroqKey, setShowGroqKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      if (isEditing && session) {
        setFormData({
          name: session.name || '',
          oauth_token: session.oauth_token || '',
          groq_api_key: session.groq_api_key || '',
          service_offerings: session.service_offerings || '',
          bid_writing_style: session.bid_writing_style || '',
          portfolio_links: session.portfolio_links || '',
          signature: session.signature || '',
          bid_limit: session.bid_limit || 75,
          project_search_limit: session.project_search_limit || 10,
          min_wait_time: session.min_wait_time || 32,
          skill_ids: session.skill_ids ? session.skill_ids.join(', ') : '',
          language_codes: session.language_codes ? session.language_codes.join(', ') : 'en',
          unwanted_currencies: session.unwanted_currencies ? session.unwanted_currencies.join(', ') : 'INR, PKR, BDT',
          unwanted_countries: session.unwanted_countries ? session.unwanted_countries.join(', ') : 'india, bangladesh, pakistan, jamaica, srilanka, sri lanka, nepal, south africa, kenya, uganda, egypt, indonesia, philippines, afganistan'
        });
      } else {
        // Reset form for new session
        setFormData({
          name: '',
          oauth_token: '',
          groq_api_key: '',
          service_offerings: '',
          bid_writing_style: '',
          portfolio_links: '',
          signature: '',
          bid_limit: 75,
          project_search_limit: 10,
          min_wait_time: 32,
          skill_ids: '3, 9, 13, 15, 17, 20, 21, 26, 32, 38, 44, 57, 69, 70, 77, 106, 107, 115, 116, 127, 137, 168, 170, 174, 196, 197, 204, 229, 232, 234, 247, 250, 262, 264, 277, 278, 284, 305, 310, 323, 324, 335, 359, 365, 368, 369, 371, 375, 408, 412, 433, 436, 444, 445, 482, 502, 564, 624, 662, 710, 759, 878, 950, 953, 959, 1063, 1185, 1314, 1623, 2071, 2128, 2222, 2245, 2338, 2342, 2507, 2586, 2587, 2589, 2605, 2625, 2645, 2673, 2698, 2717, 2745',
          language_codes: 'en',
          unwanted_currencies: 'INR, PKR, BDT',
          unwanted_countries: 'india, bangladesh, pakistan, jamaica, srilanka, sri lanka, nepal, south africa, kenya, uganda, egypt, indonesia, philippines, afganistan'
        });
      }
      setError(null);
    }
  }, [isOpen, isEditing, session]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Process form data
      const processedData = {
        ...formData,
        skill_ids: formData.skill_ids.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)),
        language_codes: formData.language_codes.split(',').map(s => s.trim()).filter(Boolean),
        unwanted_currencies: formData.unwanted_currencies.split(',').map(s => s.trim()).filter(Boolean),
        unwanted_countries: formData.unwanted_countries.split(',').map(s => s.trim()).filter(Boolean)
      };

      await onSave(processedData);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save session');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {isEditing ? 'Edit Session' : 'Create New Session'}
                </h3>
                <button
                  type="button"
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg">
                  <div className="text-danger-700">{error}</div>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900">Basic Information</h4>
                  
                  <div>
                    <label className="label">Session Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="input"
                      placeholder="e.g., My Freelancer Account"
                      required
                    />
                  </div>

                  <div>
                    <label className="label">Freelancer OAuth Token</label>
                    <div className="relative">
                      <input
                        type={showOAuthToken ? "text" : "password"}
                        value={formData.oauth_token}
                        onChange={(e) => handleInputChange('oauth_token', e.target.value)}
                        className="input pr-10"
                        placeholder="Enter your OAuth token"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowOAuthToken(!showOAuthToken)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showOAuthToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="label">Groq API Key</label>
                    <div className="relative">
                      <input
                        type={showGroqKey ? "text" : "password"}
                        value={formData.groq_api_key}
                        onChange={(e) => handleInputChange('groq_api_key', e.target.value)}
                        className="input pr-10"
                        placeholder="Enter your Groq API key"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowGroqKey(!showGroqKey)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showGroqKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="label">Signature</label>
                    <input
                      type="text"
                      value={formData.signature}
                      onChange={(e) => handleInputChange('signature', e.target.value)}
                      className="input"
                      placeholder="Your name for bids"
                    />
                  </div>
                </div>

                {/* Bot Settings */}
                <div className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900">Bot Settings</h4>
                  
                  <div>
                    <label className="label">Bid Limit</label>
                    <input
                      type="number"
                      value={formData.bid_limit}
                      onChange={(e) => handleInputChange('bid_limit', parseInt(e.target.value) || 0)}
                      className="input"
                      min="1"
                      max="1000"
                    />
                  </div>

                  <div>
                    <label className="label">Project Search Limit</label>
                    <input
                      type="number"
                      value={formData.project_search_limit}
                      onChange={(e) => handleInputChange('project_search_limit', parseInt(e.target.value) || 0)}
                      className="input"
                      min="1"
                      max="100"
                    />
                  </div>

                  <div>
                    <label className="label">Minimum Wait Time (seconds)</label>
                    <input
                      type="number"
                      value={formData.min_wait_time}
                      onChange={(e) => handleInputChange('min_wait_time', parseInt(e.target.value) || 0)}
                      className="input"
                      min="1"
                      max="300"
                    />
                  </div>
                </div>
              </div>

              {/* Service Offerings */}
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Service Offerings</h4>
                <textarea
                  value={formData.service_offerings}
                  onChange={(e) => handleInputChange('service_offerings', e.target.value)}
                  className="input"
                  rows="4"
                  placeholder="Describe your services that the bot should look for..."
                />
              </div>

              {/* Bid Writing Style */}
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Bid Writing Style</h4>
                <textarea
                  value={formData.bid_writing_style}
                  onChange={(e) => handleInputChange('bid_writing_style', e.target.value)}
                  className="input"
                  rows="6"
                  placeholder="Customize how the AI writes your bids..."
                />
              </div>

              {/* Portfolio Links */}
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Portfolio Links</h4>
                <textarea
                  value={formData.portfolio_links}
                  onChange={(e) => handleInputChange('portfolio_links', e.target.value)}
                  className="input"
                  rows="3"
                  placeholder="Enter your portfolio links (one per line)..."
                />
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>{isLoading ? 'Saving...' : (isEditing ? 'Update Session' : 'Create Session')}</span>
              </button>
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary mt-3 sm:mt-0 sm:mr-3"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SessionModal;




