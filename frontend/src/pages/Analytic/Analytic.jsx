import React, { useState, useEffect } from 'react'
import './Analytic.css'

const Analytic = () => {
  const [activeTab, setActiveTab] = useState('performance')
  const [timeRange, setTimeRange] = useState('month')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)

  // Mock data pro vizualizaci
  const performanceData = {
    shooting: {
      prone: 92,
      standing: 78,
      overall: 85,
      trend: '+3.2%'
    },
    speed: {
      averageTime: '24:32',
      percentile: 72,
      trend: '-0:45'
    },
    rankings: [
      { race: 'Kontiolahti', rank: 21, date: '2024-12-01' },
      { race: 'Hochfilzen', rank: 27, date: '2024-12-15' },
      { race: 'Nove Mesto', rank: 32, date: '2025-01-05' }
    ]
  }

  return (
    <div className="analytics-page">
      <div className="container">
        {/* PAGE HEADER */}
        <div className="page-header">
          <h1 className="page-title">PERFORMANCE ANALYTICS</h1>
          <div className="header-controls">
            <div className="time-selector">
              <button 
                className={timeRange === 'week' ? 'active' : ''}
                onClick={() => setTimeRange('week')}
              >WEEK</button>
              <button 
                className={timeRange === 'month' ? 'active' : ''}
                onClick={() => setTimeRange('month')}
              >MONTH</button>
              <button 
                className={timeRange === 'season' ? 'active' : ''}
                onClick={() => setTimeRange('season')}
              >SEASON</button>
            </div>
            <button className="btn btn-primary">EXPORT ANALYTICS</button>
          </div>
        </div>

        {/* TAB NAVIGATION */}
        <div className="analytics-tabs">
          <button 
            className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            PERFORMANCE METRICS
          </button>
          <button 
            className={`tab ${activeTab === 'shooting' ? 'active' : ''}`}
            onClick={() => setActiveTab('shooting')}
          >
            SHOOTING ANALYSIS
          </button>
          <button 
            className={`tab ${activeTab === 'competition' ? 'active' : ''}`}
            onClick={() => setActiveTab('competition')}
          >
            COMPETITION INSIGHTS
          </button>
          <button 
            className={`tab ${activeTab === 'training' ? 'active' : ''}`}
            onClick={() => setActiveTab('training')}
          >
            TRAINING LOAD
          </button>
        </div>

        {/* CONTENT AREA */}
        <div className="analytics-content">
          {activeTab === 'performance' && (
            <div className="performance-dashboard">
              {/* KEY METRICS */}
              <div className="metrics-row">
                <div className="metric-box primary">
                  <div className="metric-header">
                    <span className="metric-label">SHOOTING ACCURACY</span>
                    <span className="metric-trend positive">+3.2%</span>
                  </div>
                  <div className="metric-main">
                    <span className="metric-value">{performanceData.shooting.overall}%</span>
                  </div>
                  <div className="metric-breakdown">
                    <div className="breakdown-item">
                      <span className="label">PRONE</span>
                      <span className="value">{performanceData.shooting.prone}%</span>
                    </div>
                    <div className="breakdown-item">
                      <span className="label">STANDING</span>
                      <span className="value">{performanceData.shooting.standing}%</span>
                    </div>
                  </div>
                </div>

                <div className="metric-box">
                  <div className="metric-header">
                    <span className="metric-label">SKI SPEED</span>
                    <span className="metric-trend positive">-0:45</span>
                  </div>
                  <div className="metric-main">
                    <span className="metric-value">{performanceData.speed.averageTime}</span>
                  </div>
                  <div className="metric-sublabel">AVG LAP TIME</div>
                </div>

                <div className="metric-box">
                  <div className="metric-header">
                    <span className="metric-label">CONSISTENCY</span>
                  </div>
                  <div className="metric-main">
                    <span className="metric-value">82%</span>
                  </div>
                  <div className="metric-sublabel">PERFORMANCE STABILITY</div>
                </div>

                <div className="metric-box">
                  <div className="metric-header">
                    <span className="metric-label">RACE FINISHES</span>
                  </div>
                  <div className="metric-main">
                    <span className="metric-value">15/18</span>
                  </div>
                  <div className="metric-sublabel">THIS SEASON</div>
                </div>
              </div>

              {/* PERFORMANCE CHART */}
              <div className="chart-container">
                <div className="chart-header">
                  <h3>RANKING PROGRESSION</h3>
                  <div className="chart-legend">
                    <span className="legend-item czech">CZECH ATHLETES</span>
                    <span className="legend-item average">WORLD AVG</span>
                  </div>
                </div>
                <div className="chart-area">
                  <div className="chart-grid">
                    {[100, 80, 60, 40, 20, 0].map(val => (
                      <div key={val} className="grid-line">
                        <span className="grid-label">{val}</span>
                      </div>
                    ))}
                  </div>
                  <div className="chart-bars">
                    {[65, 78, 72, 85, 80, 88, 92, 87, 83, 90].map((height, i) => (
                      <div key={i} className="bar-group">
                        <div className="bar czech" style={{height: `${height}%`}}>
                          <span className="bar-value">{height}</span>
                        </div>
                        <div className="bar average" style={{height: `${height - 10}%`}}></div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* RECOMMENDATIONS */}
              <div className="recommendations-section">
                <h3 className="section-title">AI RECOMMENDATIONS</h3>
                <div className="recommendations-grid">
                  <div className="recommendation-card priority-high">
                    <div className="rec-header">
                      <span className="priority">HIGH PRIORITY</span>
                      <span className="impact">+15% POTENTIAL</span>
                    </div>
                    <h4>Improve Standing Shooting</h4>
                    <p>Standing accuracy is 14% below prone. Focus on breathing techniques and stability training.</p>
                    <button className="rec-action">VIEW TRAINING PLAN</button>
                  </div>
                  
                  <div className="recommendation-card priority-medium">
                    <div className="rec-header">
                      <span className="priority">MEDIUM PRIORITY</span>
                      <span className="impact">+8% POTENTIAL</span>
                    </div>
                    <h4>Optimize Race Pacing</h4>
                    <p>Analysis shows energy distribution can be improved in final loops.</p>
                    <button className="rec-action">SEE ANALYSIS</button>
                  </div>
                  
                  <div className="recommendation-card priority-low">
                    <div className="rec-header">
                      <span className="priority">OPPORTUNITY</span>
                      <span className="impact">+5% POTENTIAL</span>
                    </div>
                    <h4>Mental Preparation</h4>
                    <p>Performance dips in high-pressure situations. Consider sports psychology sessions.</p>
                    <button className="rec-action">LEARN MORE</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'shooting' && (
            <div className="shooting-analysis">
              <div className="shooting-grid">
                <div className="shooting-card">
                  <h3>PRONE POSITION</h3>
                  <div className="target-display">
                    <div className="target-grid">
                      {[1,1,1,1,0,1,1,1,1,1].map((hit, i) => (
                        <div key={i} className={`target ${hit ? 'hit' : 'miss'}`}>
                          {hit ? '●' : '○'}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="shooting-stats">
                    <div className="stat">
                      <span className="label">ACCURACY</span>
                      <span className="value">92%</span>
                    </div>
                    <div className="stat">
                      <span className="label">AVG TIME</span>
                      <span className="value">24.3s</span>
                    </div>
                    <div className="stat">
                      <span className="label">PATTERN</span>
                      <span className="value">CONSISTENT</span>
                    </div>
                  </div>
                </div>
                
                <div className="shooting-card">
                  <h3>STANDING POSITION</h3>
                  <div className="target-display">
                    <div className="target-grid">
                      {[1,0,1,1,0,1,0,1,1,0].map((hit, i) => (
                        <div key={i} className={`target ${hit ? 'hit' : 'miss'}`}>
                          {hit ? '●' : '○'}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="shooting-stats">
                    <div className="stat">
                      <span className="label">ACCURACY</span>
                      <span className="value">78%</span>
                    </div>
                    <div className="stat">
                      <span className="label">AVG TIME</span>
                      <span className="value">28.7s</span>
                    </div>
                    <div className="stat">
                      <span className="label">PATTERN</span>
                      <span className="value">NEEDS WORK</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'competition' && (
            <div className="competition-insights">
              <h2>HEAD-TO-HEAD COMPARISONS</h2>
              <p>Competition analysis coming soon...</p>
            </div>
          )}

          {activeTab === 'training' && (
            <div className="training-load">
              <h2>TRAINING LOAD MONITORING</h2>
              <p>Training metrics coming soon...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analytic
