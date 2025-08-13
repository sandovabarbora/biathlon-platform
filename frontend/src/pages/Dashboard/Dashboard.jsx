import React, { useState, useEffect } from 'react'
import './Dashboard.css'

const Dashboard = () => {
  const [athletes, setAthletes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedMetric, setSelectedMetric] = useState('performance')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const athletesRes = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=10')
      if (!athletesRes.ok) throw new Error(`Athletes fetch failed: ${athletesRes.status}`)
      const athletesData = await athletesRes.json()
      setAthletes(athletesData)
      
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading IBU Data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchData}>
          RETRY CONNECTION
        </button>
      </div>
    )
  }

  const topAthlete = athletes[0]
  const totalPoints = athletes.reduce((sum, a) => sum + (parseInt(a.world_cup_points) || 0), 0)
  const avgRank = Math.round(athletes.reduce((sum, a) => sum + (parseInt(a.world_rank) || 100), 0) / athletes.length)

  return (
    <div className="dashboard">
      <div className="container">
        {/* HEADER */}
        <div className="page-header">
          <h1 className="page-title">TEAM DASHBOARD</h1>
          <div className="header-actions">
            <button className="btn">EXPORT REPORT</button>
            <button className="btn btn-primary">TEAM MEETING</button>
          </div>
        </div>

        {/* MAIN METRICS */}
        <div className="metrics-grid">
          <div className="metric-card primary">
            <div className="metric-label">TEAM PERFORMANCE INDEX</div>
            <div className="metric-value large">87.3</div>
            <div className="metric-change positive">
              <span className="arrow up"></span>
              +5.2 vs last week
            </div>
            <div className="metric-secondary">
              <div className="metric-label">World Cup Points</div>
              <div className="metric-value">{totalPoints}</div>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">BEST RANKING</div>
            <div className="metric-value">#{topAthlete?.world_rank || 'N/A'}</div>
            <div className="metric-sublabel">{topAthlete?.name}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">SHOOTING AVG</div>
            <div className="metric-value">87%</div>
            <div className="metric-change negative">
              <span className="arrow down"></span>
              -2.1%
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">ACTIVE ATHLETES</div>
            <div className="metric-value">{athletes.length}</div>
            <div className="metric-sublabel">All healthy</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">NEXT RACE</div>
            <div className="metric-value small">Oberhof</div>
            <div className="metric-sublabel">In 3 days</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">AVG TEAM RANK</div>
            <div className="metric-value">#{avgRank}</div>
            <div className="metric-sublabel">World Cup</div>
          </div>
        </div>

        {/* QUICK ACTIONS */}
        <div className="quick-actions">
          <button className="action-card">
            <span className="action-icon">▲</span>
            <span className="action-label">Training Plans</span>
          </button>
          <button className="action-card">
            <span className="action-icon">■</span>
            <span className="action-label">Competition Analysis</span>
          </button>
          <button className="action-card">
            <span className="action-icon">●</span>
            <span className="action-label">Shooting Stats</span>
          </button>
          <button className="action-card">
            <span className="action-icon">◆</span>
            <span className="action-label">Recovery Status</span>
          </button>
        </div>

        {/* ATHLETES TABLE */}
        <div className="section">
          <div className="section-header">
            <h2 className="section-title">ATHLETES PERFORMANCE</h2>
            <div className="filter-tabs">
              <button className="filter-tab active">ALL</button>
              <button className="filter-tab">TOP FORM</button>
              <button className="filter-tab">NEEDS ATTENTION</button>
            </div>
          </div>

          <div className="athletes-table">
            {athletes.map((athlete) => {
              const rank = parseInt(athlete.world_rank) || 999
              const rankClass = rank <= 30 ? 'top' : rank <= 50 ? 'mid' : ''
              
              return (
                <div key={athlete.id} className="athlete-row">
                  <div className={`rank-badge ${rankClass}`}>
                    #{athlete.world_rank || 'N/A'}
                  </div>
                  <div className="athlete-info">
                    <div className="athlete-name">{athlete.name}</div>
                    <div className="athlete-id">IBU: {athlete.id}</div>
                  </div>
                  <div className="athlete-stat">
                    <span className="stat-value">{athlete.world_cup_points || 0}</span>
                    <span className="stat-label">POINTS</span>
                  </div>
                  <div className="athlete-stat">
                    <span className="stat-value">87%</span>
                    <span className="stat-label">SHOOTING</span>
                  </div>
                  <div className="athlete-stat">
                    <span className="stat-value positive">+2</span>
                    <span className="stat-label">TREND</span>
                  </div>
                  <button className="btn-analyze">ANALYZE</button>
                </div>
              )
            })}
          </div>
        </div>

        {/* PERFORMANCE CHART */}
        <div className="chart-section">
          <div className="chart-header">
            <h3 className="chart-title">TEAM PERFORMANCE TREND</h3>
            <div className="time-range">
              <button className="time-btn">WEEK</button>
              <button className="time-btn active">MONTH</button>
              <button className="time-btn">SEASON</button>
            </div>
          </div>
          <div className="chart-container">
            <div className="chart-bar" style={{height: '60%'}}></div>
            <div className="chart-bar" style={{height: '75%'}}></div>
            <div className="chart-bar" style={{height: '70%'}}></div>
            <div className="chart-bar" style={{height: '85%'}}></div>
            <div className="chart-bar" style={{height: '80%'}}></div>
            <div className="chart-bar" style={{height: '90%'}}></div>
            <div className="chart-bar" style={{height: '95%'}}></div>
            <div className="chart-bar" style={{height: '88%'}}></div>
          </div>
        </div>

        {/* STATUS BAR */}
        <div className="status-bar">
          <div className="status-item">
            <span className="status-dot active"></span>
            Data synchronized 2 minutes ago
          </div>
          <div className="status-item">
            IBU Data API v2.1
          </div>
          <div className="status-item">
            Next update in 28 minutes
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
