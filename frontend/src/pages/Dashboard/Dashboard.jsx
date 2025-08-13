import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Dashboard.css'

const Dashboard = () => {
  const [athletes, setAthletes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=10')
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.status}`)
      }
      
      const data = await response.json()
      setAthletes(data)
      setError(null)
    } catch (err) {
      console.error('Error loading dashboard:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Mock fatigue data (dokud nemáme skutečná HR data)
  const getMockFatigueScore = (rank) => {
    const baseScore = 85 - (parseInt(rank) || 50) * 0.5
    return Math.max(50, Math.min(95, baseScore + (Math.random() * 10 - 5)))
  }

  const getMockRecovery = () => 70 + Math.random() * 25
  const getMockPressure = () => 65 + Math.random() * 30

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading Czech Team Dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchDashboardData}>
          RETRY
        </button>
      </div>
    )
  }

  const topAthlete = athletes[0]
  const totalPoints = athletes.reduce((sum, a) => sum + (parseInt(a.world_cup_points) || 0), 0)
  const avgRank = Math.round(athletes.reduce((sum, a) => sum + (parseInt(a.world_rank) || 100), 0) / athletes.length)
  
  // Mock team averages
  const teamFatigue = 75.0
  const teamRecovery = getMockRecovery()
  const teamPressure = getMockPressure()

  return (
    <div className="dashboard">
      <div className="container">
        {/* HEADER */}
        <div className="page-header">
          <h1 className="page-title">CZECH TEAM DASHBOARD</h1>
          <div className="header-actions">
            <button 
              className="btn"
              onClick={() => navigate('/athletes')}
            >
              VIEW ATHLETES
            </button>
            <button className="btn btn-primary">TEAM ANALYSIS</button>
          </div>
        </div>

        {/* MAIN METRICS GRID - 2x4 layout */}
        <div className="metrics-grid">
          {/* Primary large card - spans 2 columns and 2 rows */}
          <div className="metric-card primary">
            <div>
              <div className="metric-label">TEAM FATIGUE RESISTANCE</div>
              <div className="metric-value large">{teamFatigue.toFixed(1)}</div>
              <div className="metric-change positive">
                <span>↑ OPTIMAL</span>
              </div>
            </div>
            <div className="metric-secondary">
              <div className="metric-label">Athletes Analyzed</div>
              <div className="metric-value">{athletes.length}</div>
            </div>
          </div>
          
          {/* Top row - 4 metrics */}
          <div className="metric-card">
            <div className="metric-label">BEST RANKING</div>
            <div className="metric-value">#{topAthlete?.world_rank || '21'}</div>
            <div className="metric-sublabel">{topAthlete?.name || 'VOBORNÍKOVÁ TEREZA'}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">AVG RECOVERY</div>
            <div className="metric-value">{teamRecovery.toFixed(0)}%</div>
            <div className="metric-sublabel">HR Recovery</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">PRESSURE</div>
            <div className="metric-value">{teamPressure.toFixed(0)}%</div>
            <div className="metric-sublabel">Under Pressure</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">TEAM POINTS</div>
            <div className="metric-value">{totalPoints || 886}</div>
            <div className="metric-sublabel">World Cup</div>
          </div>
          
          {/* Bottom row - 4 metrics */}
          <div className="metric-card">
            <div className="metric-label">NEXT RACE</div>
            <div className="metric-value small">Ruhpolding</div>
            <div className="metric-sublabel">In 3 days</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">AVG RANK</div>
            <div className="metric-value">#{avgRank || 45}</div>
            <div className="metric-sublabel">Team Average</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">SHOOTING</div>
            <div className="metric-value">87%</div>
            <div className="metric-sublabel">Team Average</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">ACTIVE</div>
            <div className="metric-value">{athletes.length || 5}</div>
            <div className="metric-sublabel">Athletes</div>
          </div>
        </div>

        {/* QUICK ACTIONS */}
        <div className="quick-actions">
          <button 
            className="action-card"
            onClick={() => navigate('/athletes')}
          >
            <span className="action-icon">💪</span>
            <span className="action-label">Fatigue Profiles</span>
          </button>
          <button 
            className="action-card"
            onClick={() => navigate('/analytics')}
          >
            <span className="action-icon">📈</span>
            <span className="action-label">Recovery Tracking</span>
          </button>
          <button 
            className="action-card"
            onClick={() => navigate('/analytics')}
          >
            <span className="action-icon">🎯</span>
            <span className="action-label">Shooting Analysis</span>
          </button>
          <button 
            className="action-card"
            onClick={() => navigate('/coach')}
          >
            <span className="action-icon">🏃</span>
            <span className="action-label">Training Load</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
