import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [athletes, setAthletes] = useState([])
  const [teamFatigue, setTeamFatigue] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState('fatigue')
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load athletes
      const athletesData = await api.athletes.getAll('CZE', 10)
      setAthletes(athletesData)
      
      // Load team fatigue analysis
      try {
        const fatigueData = await api.fatigue.getTeamAnalysis('CZE')
        setTeamFatigue(fatigueData)
      } catch (err) {
        console.log('Fatigue data not available yet')
      }
      
    } catch (err) {
      console.error('Error loading dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const getFatigueColor = (score) => {
    if (score >= 80) return 'good'
    if (score >= 60) return 'medium'
    return 'bad'
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading Czech Team Dashboard...</p>
      </div>
    )
  }

  const topAthlete = athletes[0]
  const totalPoints = athletes.reduce((sum, a) => sum + (parseInt(a.world_cup_points) || 0), 0)
  const avgFatigue = teamFatigue?.team_stats?.avg_resistance_score || 75

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

        {/* MAIN METRICS */}
        <div className="metrics-grid">
          <div className="metric-card primary">
            <div className="metric-label">TEAM FATIGUE RESISTANCE</div>
            <div className="metric-value large">{avgFatigue.toFixed(1)}</div>
            <div className={`metric-change ${avgFatigue >= 75 ? 'positive' : 'negative'}`}>
              <span className="arrow up"></span>
              {avgFatigue >= 75 ? 'OPTIMAL' : 'NEEDS WORK'}
            </div>
            <div className="metric-secondary">
              <div className="metric-label">Athletes Analyzed</div>
              <div className="metric-value">{teamFatigue?.team_stats?.athletes_analyzed || 0}</div>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">BEST RANKING</div>
            <div className="metric-value">#{topAthlete?.world_rank || 'N/A'}</div>
            <div className="metric-sublabel">{topAthlete?.name}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">AVG RECOVERY</div>
            <div className="metric-value">{teamFatigue?.team_stats?.avg_recovery_efficiency?.toFixed(0) || '-'}%</div>
            <div className="metric-sublabel">HR Recovery</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">PRESSURE HANDLING</div>
            <div className="metric-value">{teamFatigue?.team_stats?.avg_pressure_response?.toFixed(0) || '-'}%</div>
            <div className="metric-sublabel">Under pressure</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">TEAM POINTS</div>
            <div className="metric-value">{totalPoints}</div>
            <div className="metric-sublabel">World Cup</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">NEXT RACE</div>
            <div className="metric-value small">Ruhpolding</div>
            <div className="metric-sublabel">In 3 days</div>
          </div>
        </div>

        {/* FATIGUE QUICK ACTIONS */}
        <div className="quick-actions">
          <button 
            className="action-card"
            onClick={() => navigate('/athletes')}
          >
            <span className="action-icon">💪</span>
            <span className="action-label">Fatigue Profiles</span>
          </button>
          <button className="action-card">
            <span className="action-icon">📈</span>
            <span className="action-label">Recovery Tracking</span>
          </button>
          <button className="action-card">
            <span className="action-icon">🎯</span>
            <span className="action-label">Shooting Analysis</span>
          </button>
          <button className="action-card">
            <span className="action-icon">🏃</span>
            <span className="action-label">Training Load</span>
          </button>
        </div>

        {/* ATHLETES TABLE WITH FATIGUE */}
        <div className="section">
          <div className="section-header">
            <h2 className="section-title">ATHLETES FATIGUE STATUS</h2>
            <div className="filter-tabs">
              <button 
                className={`filter-tab ${selectedMetric === 'fatigue' ? 'active' : ''}`}
                onClick={() => setSelectedMetric('fatigue')}
              >
                FATIGUE
              </button>
              <button 
                className={`filter-tab ${selectedMetric === 'performance' ? 'active' : ''}`}
                onClick={() => setSelectedMetric('performance')}
              >
                PERFORMANCE
              </button>
              <button 
                className={`filter-tab ${selectedMetric === 'recovery' ? 'active' : ''}`}
                onClick={() => setSelectedMetric('recovery')}
              >
                RECOVERY
              </button>
            </div>
          </div>

          <div className="athletes-table">
            {teamFatigue?.athlete_profiles?.map((profile) => {
              const athlete = athletes.find(a => a.id === profile.athlete_id) || {}
              
              return (
                <div key={profile.athlete_id} className="athlete-row">
                  <div className="rank-badge">
                    #{profile.world_rank || athlete.world_rank || 'N/A'}
                  </div>
                  <div className="athlete-info">
                    <div className="athlete-name">{profile.name}</div>
                    <div className="athlete-id">IBU: {profile.athlete_id}</div>
                  </div>
                  <div className="athlete-stat">
                    <span className={`stat-value ${getFatigueColor(profile.fatigue_score)}`}>
                      {profile.fatigue_score.toFixed(0)}
                    </span>
                    <span className="stat-label">FATIGUE</span>
                  </div>
                  <div className="athlete-stat">
                    <span className="stat-value">{profile.recovery_efficiency.toFixed(0)}%</span>
                    <span className="stat-label">RECOVERY</span>
                  </div>
                  <div className="athlete-stat">
                    <span className="stat-value">{profile.pressure_response.toFixed(0)}%</span>
                    <span className="stat-label">PRESSURE</span>
                  </div>
                  <button 
                    className="btn-analyze"
                    onClick={() => {
                      navigate('/athletes', { 
                        state: { 
                          viewMode: 'fatigue', 
                          athleteId: profile.athlete_id 
                        }
                      })
                    }}
                  >
                    ANALYZE
                  </button>
                </div>
              )
            })}
          </div>
        </div>

        {/* TEAM WEAKNESSES */}
        {teamFatigue?.team_stats?.weakest_areas?.length > 0 && (
          <div className="section">
            <h2 className="section-title">TEAM FOCUS AREAS</h2>
            <div className="recommendations-grid">
              {teamFatigue.team_stats.weakest_areas.map((area, i) => (
                <div key={i} className="recommendation-card priority-high">
                  <h3>{area.area}</h3>
                  <p>Team Average: {area.score.toFixed(0)}%</p>
                  <p>{area.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STATUS BAR */}
        <div className="status-bar">
          <div className="status-item">
            <span className="status-dot active"></span>
            Fatigue analysis active
          </div>
          <div className="status-item">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
