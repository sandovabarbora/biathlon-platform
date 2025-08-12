import { useState, useEffect } from 'react'
import './czech-dashboard.css'

const API_URL = 'http://localhost:8000/api/v1'

function CzechDashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await fetch(`${API_URL}/czech-dashboard`)
      const data = await response.json()
      setDashboard(data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Načítám data z IBU...</div>

  return (
    <div className="czech-dashboard">
      <header className="header-czech">
        <div className="header-content">
          <h1>🇨🇿 Český Biatlon - Analytika</h1>
          <div className="team-summary">
            <span>Průměr: #{dashboard?.team_stats?.avg_world_rank?.toFixed(0)}</span>
            <span className="separator">|</span>
            <span>{dashboard?.team_stats?.vs_top_nations?.target}</span>
          </div>
        </div>
      </header>

      {/* Czech Athletes - ALWAYS ON TOP */}
      <section className="czech-athletes-section">
        <h2>Naši závodníci</h2>
        <div className="athletes-grid">
          {dashboard?.athletes?.map(athlete => (
            <div 
              key={athlete.name}
              className={`athlete-card-czech ${selectedAthlete?.name === athlete.name ? 'selected' : ''}`}
              onClick={() => setSelectedAthlete(athlete)}
            >
              <div className="athlete-header">
                <h3>{athlete.name}</h3>
                <span className={`status ${athlete.status.includes('Improving') ? 'improving' : 
                                           athlete.status.includes('attention') ? 'declining' : 
                                           'stable'}`}>
                  {athlete.status}
                </span>
              </div>
              
              <div className="athlete-stats">
                <div className="stat">
                  <label>Světový rank</label>
                  <value>#{athlete.world_rank || 'N/A'}</value>
                </div>
                <div className="stat">
                  <label>Průměr</label>
                  <value>#{athlete.performance?.season_stats?.avg_rank?.toFixed(0)}</value>
                </div>
                <div className="stat">
                  <label>Střelba</label>
                  <value className={athlete.performance?.shooting?.percentile > 50 ? 'good' : 'bad'}>
                    {athlete.performance?.shooting?.accuracy?.toFixed(0)}%
                  </value>
                </div>
                <div className="stat">
                  <label>vs TOP 10</label>
                  <value className="comparison">
                    +{athlete.performance?.comparison?.vs_top10?.rank_diff?.toFixed(1)}
                  </value>
                </div>
              </div>

              <div className="strengths-weaknesses">
                <div className="strengths">
                  ✅ {athlete.performance?.strengths?.[0]}
                </div>
                <div className="weaknesses">
                  ⚠️ {athlete.performance?.weaknesses?.[0]}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Team Priorities */}
      <section className="team-priorities">
        <h2>Týmové priority</h2>
        <div className="priorities-grid">
          {dashboard?.team_stats?.priorities?.map((priority, i) => (
            <div key={i} className="priority-card">
              <h3>{priority.area}</h3>
              <p>Ovlivněno: {priority.athletes_affected} závodníků</p>
              <p className="action">→ {priority.action}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Detailed Athlete View */}
      {selectedAthlete && (
        <section className="athlete-detail">
          <h2>{selectedAthlete.name} - Detailní analýza</h2>
          
          <div className="detail-grid">
            <div className="comparison-box">
              <h3>Srovnání s TOP 10</h3>
              <div className="comparison-stat">
                <span>Umístění</span>
                <span className="value">
                  {selectedAthlete.performance?.comparison?.vs_top10?.rank_diff > 0 ? '+' : ''}
                  {selectedAthlete.performance?.comparison?.vs_top10?.rank_diff?.toFixed(1)} pozic
                </span>
              </div>
              <div className="comparison-stat">
                <span>Střelba</span>
                <span className="value">
                  {selectedAthlete.performance?.comparison?.vs_top10?.shooting_diff > 0 ? '+' : ''}
                  {selectedAthlete.performance?.comparison?.vs_top10?.shooting_diff?.toFixed(1)} ran
                </span>
              </div>
              <p className="message">
                {selectedAthlete.performance?.comparison?.vs_top10?.message}
              </p>
            </div>

            <div className="trend-box">
              <h3>Trend</h3>
              <div className={`trend-indicator ${selectedAthlete.performance?.trend?.direction}`}>
                {selectedAthlete.performance?.trend?.direction?.replace('_', ' ')}
              </div>
              <p>
                Poslední závody: #{selectedAthlete.performance?.trend?.recent_avg?.toFixed(0)}<br/>
                Sezonní průměr: #{selectedAthlete.performance?.trend?.season_avg?.toFixed(0)}
              </p>
            </div>

            <div className="training-focus">
              <h3>Tréninkové priority</h3>
              <ol>
                {selectedAthlete.performance?.weaknesses?.map((weakness, i) => (
                  <li key={i} className={weakness.includes('CRITICAL') ? 'critical' : ''}>
                    {weakness}
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>
      )}

      {/* Recent Highlights */}
      <section className="highlights">
        <h2>Poslední úspěchy</h2>
        <div className="highlights-list">
          {dashboard?.recent_highlights?.map((highlight, i) => (
            <div key={i} className="highlight">
              🏆 {highlight}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default CzechDashboard
