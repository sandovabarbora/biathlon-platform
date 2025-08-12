import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard/Dashboard'
import Athletes from './pages/Athletes/Athletes'
import Races from './pages/Races/Races'
import Reports from './pages/Reports/Reports'
import AICoach from './pages/AICoach/AICoach'
import './App.css'

// Navigační komponenta
function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/athletes', label: 'Athletes', icon: '🎿' },
    { path: '/races', label: 'Races', icon: '🏁' },
    { path: '/analytics', label: 'Reports', icon: '📈' },
    { path: '/coach', label: 'AI Coach', icon: '🤖' }
  ]
  
  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <span style={{fontSize: '2rem', marginRight: '1rem'}}>🇨🇿</span>
          <div>
            <h1>BIATHLON ANALYTICS</h1>
            <span className="nav-subtitle">2024/2025 Season</span>
          </div>
        </Link>
        
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
        
        <div className="nav-actions">
          <button className="live-btn">
            <span className="live-dot"></span>
            LIVE
          </button>
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
            <Route path="/analytics" element={<Reports />} />
            <Route path="/coach" element={<AICoach />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
