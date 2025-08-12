import React, { useState, useEffect } from 'react'
import './Dashboard.css'

const Dashboard = () => {
  const [athletes, setAthletes] = useState([])
  const [loading, setLoading] = useState(true)
  const [hoveredCard, setHoveredCard] = useState(null)
  const [selectedMetric, setSelectedMetric] = useState('rank')

  useEffect(() => {
    fetchAthletes()
  }, [])

  const fetchAthletes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=10')
      const data = await response.json()
      setAthletes(data)
      setLoading(false)
    } catch (err) {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-dots">
          <div></div><div></div><div></div>
        </div>
      </div>
    )
  }

  const topAthlete = athletes[0]
  const totalPoints = athletes.reduce((sum, a) => sum + (parseInt(a.world_cup_points) || 0), 0)
  const avgRank = Math.round(athletes.reduce((sum, a) => sum + parseInt(a.world_rank || 100), 0) / athletes.length)

  return (
    <div className="dashboard-modern">
      {/* Floating Header */}
      <header className="floating-header">
        <div className="header-content">
          <div className="header-title">
            <h1>Czech Biathlon</h1>
            <div className="live-indicator">
              <span className="pulse"></span>
              LIVE DATA
            </div>
          </div>
          <div className="metric-selector">
            <button 
              className={selectedMetric === 'rank' ? 'active' : ''}
              onClick={() => setSelectedMetric('rank')}
            >
              Rankings
            </button>
            <button 
              className={selectedMetric === 'points' ? 'active' : ''}
              onClick={() => setSelectedMetric('points')}
            >
              Points
            </button>
            <button 
              className={selectedMetric === 'trend' ? 'active' : ''}
              onClick={() => setSelectedMetric('trend')}
            >
              Trends
            </button>
          </div>
        </div>
      </header>

      {/* Bento Grid Layout */}
      <div className="bento-grid">
        {/* Hero Card - Top Athlete */}
        <div 
          className="bento-card hero-card"
          onMouseEnter={() => setHoveredCard('hero')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="card-header">
            <span className="card-label">TOP PERFORMER</span>
            <span className="card-badge">RANK #{topAthlete?.world_rank}</span>
          </div>
          <div className="hero-content">
            <h2 className="hero-name">{topAthlete?.name}</h2>
            <div className="hero-stats">
              <div className="hero-stat">
                <span className="stat-value">{topAthlete?.world_cup_points}</span>
                <span className="stat-label">WC Points</span>
              </div>
              <div className="hero-stat">
                <span className="stat-value">CZE</span>
                <span className="stat-label">Nation</span>
              </div>
            </div>
          </div>
          <div className="card-visual">
            <svg viewBox="0 0 200 100" className="performance-chart">
              <polyline
                points="0,80 40,70 80,40 120,45 160,20 200,25"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="2"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.2"/>
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="1"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>

        {/* Team Overview Card */}
        <div 
          className="bento-card team-card"
          onMouseEnter={() => setHoveredCard('team')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="card-header">
            <span className="card-label">TEAM OVERVIEW</span>
          </div>
          <div className="team-metrics">
            <div className="metric">
              <div className="metric-value">{totalPoints}</div>
              <div className="metric-label">Total Points</div>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: '75%'}}></div>
              </div>
            </div>
            <div className="metric">
              <div className="metric-value">#{avgRank}</div>
              <div className="metric-label">Avg Rank</div>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: `${100 - avgRank}%`}}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Cards */}
        <div className="bento-card stat-card accent-blue">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-number">{athletes.filter(a => parseInt(a.world_rank) <= 30).length}</div>
            <div className="stat-text">Top 30</div>
          </div>
        </div>

        <div className="bento-card stat-card accent-purple">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-number">{athletes.length}</div>
            <div className="stat-text">Athletes</div>
          </div>
        </div>

        {/* Athletes List Card */}
        <div className="bento-card athletes-list-card">
          <div className="card-header">
            <span className="card-label">ATHLETE ROSTER</span>
            <button className="view-all">View All →</button>
          </div>
          <div className="athletes-list">
            {athletes.slice(0, 5).map((athlete, index) => (
              <div 
                key={athlete.id} 
                className="athlete-row"
                style={{animationDelay: `${index * 0.1}s`}}
              >
                <div className="athlete-position">{index + 1}</div>
                <div className="athlete-info">
                  <div className="athlete-name">{athlete.name}</div>
                  <div className="athlete-meta">Rank #{athlete.world_rank}</div>
                </div>
                <div className="athlete-points">
                  <div className="points-value">{athlete.world_cup_points}</div>
                  <div className="points-label">pts</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Activity Card */}
        <div className="bento-card activity-card">
          <div className="card-header">
            <span className="card-label">RECENT ACTIVITY</span>
            <span className="activity-indicator"></span>
          </div>
          <div className="activity-feed">
            <div className="activity-item">
              <div className="activity-dot"></div>
              <div className="activity-content">
                <div className="activity-title">World Cup Update</div>
                <div className="activity-time">2 hours ago</div>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-dot"></div>
              <div className="activity-content">
                <div className="activity-title">Training Session</div>
                <div className="activity-time">5 hours ago</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Button */}
      <button className="fab">
        <span>+</span>
      </button>
    </div>
  )
}

export default Dashboard
