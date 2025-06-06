// frontend/src/App.jsx
import React, { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import HomePage from './components/layout/HomePage'
import MainLayout from './components/layout/MainLayout'
import { useAnalytics } from './hooks/useAnalytics'

function App() {
  const location = useLocation()
  const { trackPageView } = useAnalytics()

  useEffect(() => {
    // Track page views
    trackPageView(location.pathname)
  }, [location.pathname, trackPageView])

  useEffect(() => {
    // Set global project files for algorithms
    window.projectFiles = []
    
    // Initialize app-level services
    console.log('🌟 CodeFlow 3D initialized')
    console.log('📊 Version:', __APP_VERSION__)
    console.log('🔨 Built:', __BUILD_TIME__)
  }, [])

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/project/:projectId" element={<MainLayout />} />
        <Route path="*" element={
          <div className="not-found">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/">← Go Home</a>
          </div>
        } />
      </Routes>
    </div>
  )
}

export default App