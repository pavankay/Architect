// Centralized configuration for API endpoints
// Change these values to update all API calls throughout the application
export const API_BASE_URL = 'http://localhost:8000';
export const WS_URL = 'ws://localhost:8000/ws';

// For convenience
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  WS_URL: WS_URL,
  
  // Convenience methods
  getApiUrl: (path: string = '') => {
    return `${API_BASE_URL}${path}`;
  },
  
  getWsUrl: () => {
    return WS_URL;
  }
};