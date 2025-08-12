import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './Navigation.css'

const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/athletes', label: 'Athletes', icon: '🎿' },
    { path: '/races', label: 'Races', icon: '🏁' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/training', label: 'AI Coach', icon: '🤖' }
  ]

  return (
    <nav className={`navigation ${isScrolled ? 'scrolled' : ''}`}>
      <div className="nav-container">
        <div className="nav-logo" onClick={() => navigate('/')}>
          <span className="logo-flag">🇨🇿</span>
          <div className="logo-text">
            <h1>BIATHLON</h1>
            <span className="logo-subtitle">ANALYTICS 2.0</span>
          </div>
        </div>

        <div className="nav-menu">
          {navItems.map((item) => (
            <button
              key={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="nav-actions">
          <button className="nav-live-btn">
            <span className="live-dot"></span>
            LIVE
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
