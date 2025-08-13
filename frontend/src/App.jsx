import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard/Dashboard'
import Athletes from './pages/Athletes/Athletes'
import Races from './pages/Races/Races'
import Analytic from './pages/Analytic/Analytic'
import AICoach from './pages/AICoach/AICoach'
import './styles/design-system.css'
import './App.css'

function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/athletes', label: 'Athletes', icon: '🎿' },
    { path: '/races', label: 'Races', icon: '🏁' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/coach', label: 'AI Coach', icon: '🤖' }
  ]
  
  return (
    <nav className="top-navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <div className="flag-badge">
            <div className="flag-blue"></div>
            <div className="flag-red"></div>
          </div>
          <span className="brand-title">CZECH BIATHLON ANALYTICS 2.0</span>
        </div>
        
        <div className="nav-links">
          {navItems.map(item => (
            <Link 
              key={item.path}
              to={item.path} 
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </div>
        
        <div className="nav-status">
          <div className="live-indicator">
            <span className="status-dot active"></span>
            <span>FATIGUE ENGINE</span>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/athletes" element={<Athletes />} />
            <Route path="/races" element={<Races />} />
            <Route path="/analytics" element={<Analytic />} />
            <Route path="/coach" element={<AICoach />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
