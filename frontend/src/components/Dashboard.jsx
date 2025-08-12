import React, { useState, useEffect } from 'react'
import './Dashboard.css'

const Dashboard = ({ athletes, onSelectAthlete }) => {
  const [performances, setPerformances] = useState({})
  const [recommendations, setRecommendations] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAllPerformances()
  }, [athletes])

  const loadAllPerformances = async () => {
    setLoading(true)
    
    for (const athlete of athletes) {
      try {
        // Load performance
        const perfResponse = await fetch(`/api/v1/athletes/${athlete.id}/performance`)
        const perfData = await perfResponse.json()
        setPerformances(prev => ({ ...prev, [athlete.id]: perfData }))
        
        // Load recommendations
        const recResponse = await fetch(`/api/v1/analytics/training/${athlete.id}`)
        const recData = await recResponse.json()
        setRecommendations(prev => ({ ...prev, [athlete.id]: recData }))
      } catch (error) {
        console.error(`Error loading data for ${athlete.name}:`, error)
      }
    }
    
    setLoading(false)
  }

  const getStatusColor = (performance) => {
    if (!performance) return 'neutral'
    if (performance.recent_form > 5) return 'improving'
    if (performance.recent_form < -5) return 'declining'
    return 'stable'
  }

  const getPriorityAlerts = () => {
    const alerts = []
    
    for (const athlete of athletes) {
      const perf = performances[athlete.id]
      const recs = recommendations[athlete.id]
      
      if (perf?.shooting?.total_accuracy < 75) {
        alerts.push({
          athlete,
          type: 'critical',
          issue: `Shooting accuracy ${perf.shooting.total_accuracy.toFixed(1)}%`,
          action: 'Immediate shooting session needed'
        })
      }
      
      if (perf?.recent_form < -10) {
        alerts.push({
          athlete,
          type: 'warning',
          issue: 'Declining form',
          action: 'Review training load'
        })
      }
    }
    
    return alerts.sort((a, b) => 
      a.type === 'critical' ? -1 : b.type === 'critical' ? 1 : 0
    )
  }

  if (loading) {
    return <div className="loading-spinner">Loading Czech team data...</div>
  }

  const alerts = getPriorityAlerts()

  return (
    <div className="dashboard">
      {/* Morning Brief Section */}
      <section className="morning-brief">
        <h2>Morning Brief - {new Date().toLocaleDateString('cs-CZ')}</h2>
        
        {alerts.length > 0 && (
          <div className="alerts">
            <h3>⚠️ Priority Alerts</h3>
            {alerts.map((alert, i) => (
              <div key={i} className={`alert ${alert.type}`}>
                <div className="alert-header">
                  <span className="athlete-name">{alert.athlete.name}</span>
                  <span className={`badge ${alert.type}`}>{alert.type}</span>
                </div>
                <p className="issue">{alert.issue}</p>
                <p className="action">→ {alert.action}</p>
              </div>
            ))}
          </div>
        )}

        <div className="positive-momentum">
          <h3>✅ Positive Trends</h3>
          {athletes.filter(a => performances[a.id]?.recent_form > 5).map(athlete => (
            <div key={athlete.id} className="momentum-item">
              <span className="name">{athlete.name}</span>
              <span className="trend">↑ {performances[athlete.id].recent_form.toFixed(1)}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Athletes Grid */}
      <section className="athletes-grid">
        <h2>Czech Team Overview</h2>
        <div className="athlete-cards">
          {athletes.map(athlete => {
            const perf = performances[athlete.id]
            const status = getStatusColor(perf)
            
            return (
              <div 
                key={athlete.id} 
                className={`athlete-card ${status}`}
                onClick={() => onSelectAthlete(athlete)}
              >
                <div className="card-header">
                  <h3>{athlete.name}</h3>
                  <span className={`status-dot ${status}`}></span>
                </div>
                
                {perf && (
                  <div className="card-stats">
                    <div className="stat">
                      <label>Avg Rank</label>
                      <value>{perf.avg_rank?.toFixed(1)}</value>
                    </div>
                    <div className="stat">
                      <label>Shooting</label>
                      <value className={perf.shooting?.total_accuracy > 80 ? 'good' : 'bad'}>
                        {perf.shooting?.total_accuracy?.toFixed(0)}%
                      </value>
                    </div>
                    <div className="stat">
                      <label>Form</label>
                      <value className={status}>
                        {perf.recent_form > 0 ? '↑' : perf.recent_form < 0 ? '↓' : '→'}
                        {Math.abs(perf.recent_form).toFixed(1)}
                      </value>
                    </div>
                    <div className="stat">
                      <label>Points</label>
                      <value>{perf.points_total}</value>
                    </div>
                  </div>
                )}
                
                <div className="card-actions">
                  <button className="view-details">View Timeline →</button>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Team Summary */}
      <section className="team-summary">
        <h2>Team Statistics</h2>
        <div className="summary-stats">
          <div className="summary-stat">
            <label>Team Average Rank</label>
            <value>
              {(athletes.reduce((sum, a) => 
                sum + (performances[a.id]?.avg_rank || 0), 0) / athletes.length
              ).toFixed(1)}
            </value>
          </div>
          <div className="summary-stat">
            <label>Team Shooting Average</label>
            <value>
              {(athletes.reduce((sum, a) => 
                sum + (performances[a.id]?.shooting?.total_accuracy || 0), 0) / athletes.length
              ).toFixed(1)}%
            </value>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard
