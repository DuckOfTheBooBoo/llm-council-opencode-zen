import { useState, useEffect } from 'react';
import { api } from '../api';
import './ConfigInfo.css';

export default function ConfigInfo() {
  const [config, setConfig] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const configData = await api.getConfig();
      setConfig(configData);
    } catch (err) {
      setError('Failed to load configuration');
      console.error('Failed to load config:', err);
    }
  };

  if (error) {
    return null; // Silently fail - config display is not critical
  }

  if (!config) {
    return null; // Loading
  }

  return (
    <div className="config-info">
      <button
        className="config-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        title="Show council configuration"
      >
        <span className="config-icon">⚙️</span>
        <span className="config-label">
          {config.council_models_count} Council Models
        </span>
        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="config-details">
          <div className="config-section">
            <div className="config-section-title">Council Models</div>
            <ul className="model-list">
              {config.council_models.map((model, index) => (
                <li key={index} className="model-item">
                  {model}
                </li>
              ))}
            </ul>
          </div>

          <div className="config-section">
            <div className="config-section-title">Chairman</div>
            <div className="model-item chairman">{config.chairman_model}</div>
          </div>

          <div className="config-section">
            <div className="config-info-text">
              Minimum required: {config.min_required_models} models
            </div>
            {!config.validation.is_valid && (
              <div className="config-warning">
                ⚠️ {config.validation.error_message}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
