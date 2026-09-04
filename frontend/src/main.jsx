import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import './index.css'

// Support VITE_API_BASE_URL for decoupled cloud deployments (e.g., Vercel frontend + Render backend)
const apiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BACKEND_URL;
if (apiBase) {
  axios.defaults.baseURL = apiBase.replace(/\/+$/, '');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)

