import React, { useState, useEffect } from 'react'
import './Reports.css'

const Reports = () => {
  const [activeTab, setActiveTab] = useState('performance')
  const [timeRange, setTimeRange] = useState('season')
  const [loading, setLoading] = useState(true)
  
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
      { race: 'Kontiolahti', rank: 1, date: '2024-12-01' },
      { race: 'Hochfilzen', rank: 7, date: '2024-12-15' },
      { race: 'Nove Mesto', rank: 52, date: '2025-01-05' }
    ]
  }

  useEffect(() => {
    setTimeout(() => setLoading(false), 1000)
  }, [])

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>
  }

  return (
    <div className="analytics-page">
      {/* Header */}
      <div className="analytics-header">
        <h1>Performance Analytics</h1>
        <div className="time-selector">
          <button 
            className={timeRange === 'week' ? 'active' : ''}
            onClick={() => setTimeRange('week')}
          >Week</button>
          <button 
            className={timeRange === 'month' ? 'active' : ''}
            onClick={() => setTimeRange('month')}
          >Month</button>
          <button 
            className={timeRange === 'season' ? 'active' : ''}
            onClick={() => setTimeRange('season')}
          >Season</button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="analytics-tabs">
        <button 
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          Performance Metrics
        </button>
        <button 
          className={`tab ${activeTab === 'shooting' ? 'active' : ''}`}
          onClick={() => setActiveTab('shooting')}
        >
          Shooting Analysis
        </button>
        <button 
          className={`tab ${activeTab === 'competition' ? 'active' : ''}`}
          onClick={() => setActiveTab('competition')}
        >
          Competition Insights
        </button>
        <button 
          className={`tab ${activeTab === 'training' ? 'active' : ''}`}
          onClick={() => setActiveTab('training')}
        >
          Training Optimization
        </button>
      </div>

      {/* Content */}
      <div className="analytics-content">
        {activeTab === 'performance' && (
          <div className="performance-dashboard">
            {/* Key Metrics */}
            <div className="metrics-grid">
              <div className="metric-card gradient-blue">
                <div className="metric-icon">🎯</div>
                <div className="metric-details">
                  <h3>Shooting Accuracy</h3>
                  <div className="metric-value">{performanceData.shooting.overall}%</div>
                  <div className="metric-trend positive">{performanceData.shooting.trend}</div>
                </div>
                <div className="metric-chart">
                  <div className="mini-bar-chart">
                    <div className="bar" style={{height: '92%', background: '#10b981'}}></div>
                    <div className="bar" style={{height: '78%', background: '#f59e0b'}}></div>
                    <div className="bar" style={{height: '85%', background: '#3b82f6'}}></div>
                  </div>
                  <div className="chart-labels">
                    <span>Prone</span>
                    <span>Stand</span>
                    <span>Avg</span>
                  </div>
                </div>
              </div>

              <div className="metric-card gradient-purple">
                <div className="metric-icon">⚡</div>
                <div className="metric-details">
                  <h3>Speed Performance</h3>
                  <div className="metric-value">{performanceData.speed.averageTime}</div>
                  <div className="metric-trend positive">{performanceData.speed.trend}</div>
                </div>
                <div className="speed-gauge">
                  <div className="gauge-fill" style={{width: `${performanceData.speed.percentile}%`}}></div>
                  <span className="gauge-label">Top {100 - performanceData.speed.percentile}%</span>
                </div>
              </div>

              <div className="metric-card gradient-green">
                <div className="metric-icon">📈</div>
                <div className="metric-details">
                  <h3>Season Progress</h3>
                  <div className="metric-value">15 Races</div>
                  <div className="metric-subtext">3 Podiums</div>
                </div>
                <div className="progress-rings">
                  <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="35" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8"/>
                    <circle cx="50" cy="50" r="35" fill="none" stroke="#10b981" strokeWidth="8"
                            strokeDasharray="220" strokeDashoffset="66" strokeLinecap="round"/>
                  </svg>
                  <span className="ring-value">70%</span>
                </div>
              </div>
            </div>

            {/* Performance Chart */}
            <div className="performance-chart-container">
              <h2>Ranking Progression</h2>
              <div className="chart-wrapper">
                <svg viewBox="0 0 800 300" className="performance-chart">
                  {/* Grid */}
                  {[0, 10, 20, 30, 40, 50].map(y => (
                    <g key={y}>
                      <line x1="50" y1={50 + y * 4} x2="750" y2={50 + y * 4} 
                            stroke="rgba(255,255,255,0.05)" strokeDasharray="5,5"/>
                      <text x="30" y={55 + y * 4} fill="rgba(255,255,255,0.3)" fontSize="12">
                        {y === 0 ? '1' : y}
                      </text>
                    </g>
                  ))}
                  
                  {/* Data line */}
                  <polyline
                    points="100,50 200,78 300,70 400,110 500,85 600,95 700,210"
                    fill="none"
                    stroke="url(#performanceGradient)"
                    strokeWidth="3"
                  />
                  
                  {/* Data points */}
                  {[
                    {x: 100, y: 50, rank: 1},
                    {x: 200, y: 78, rank: 7},
                    {x: 300, y: 70, rank: 5},
                    {x: 400, y: 110, rank: 20},
                    {x: 500, y: 85, rank: 10},
                    {x: 600, y: 95, rank: 15},
                    {x: 700, y: 210, rank: 52}
                  ].map((point, i) => (
                    <g key={i}>
                      <circle cx={point.x} cy={point.y} r="6" fill="#3b82f6"/>
                      <text x={point.x} y={point.y - 10} fill="white" fontSize="12" textAnchor="middle">
                        #{point.rank}
                      </text>
                    </g>
                  ))}
                  
                  <defs>
                    <linearGradient id="performanceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#10b981"/>
                      <stop offset="50%" stopColor="#3b82f6"/>
                      <stop offset="100%" stopColor="#ef4444"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>

            {/* Recommendations */}
            <div className="recommendations-section">
              <h2>AI-Powered Recommendations</h2>
              <div className="recommendations-grid">
                <div className="recommendation-card priority-high">
                  <div className="rec-header">
                    <span className="rec-priority">HIGH PRIORITY</span>
                    <span className="rec-impact">+15% potential</span>
                  </div>
                  <h3>Improve Standing Shooting</h3>
                  <p>Standing accuracy is 14% below prone. Focus on breathing techniques and stability training.</p>
                  <button className="rec-action">View Training Plan →</button>
                </div>
                
                <div className="recommendation-card priority-medium">
                  <div className="rec-header">
                    <span className="rec-priority">MEDIUM PRIORITY</span>
                    <span className="rec-impact">+8% potential</span>
                  </div>
                  <h3>Optimize Race Pacing</h3>
                  <p>Analysis shows energy distribution can be improved in final loops.</p>
                  <button className="rec-action">See Analysis →</button>
                </div>
                
                <div className="recommendation-card priority-low">
                  <div className="rec-header">
                    <span className="rec-priority">OPPORTUNITY</span>
                    <span className="rec-impact">+5% potential</span>
                  </div>
                  <h3>Mental Preparation</h3>
                  <p>Performance dips in high-pressure situations. Consider sports psychology sessions.</p>
                  <button className="rec-action">Learn More →</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'shooting' && (
          <div className="shooting-analysis">
            <h2>Detailed Shooting Analysis</h2>
            <div className="shooting-grid">
              <div className="shooting-stat-card">
                <h3>Prone Position</h3>
                <div className="shooting-visual">
                  <div className="target-grid">
                    {[1,1,1,1,0,1,1,1,1,1].map((hit, i) => (
                      <div key={i} className={`target ${hit ? 'hit' : 'miss'}`}></div>
                    ))}
                  </div>
                  <div className="shooting-stats">
                    <div>Accuracy: 92%</div>
                    <div>Avg Time: 24.3s</div>
                    <div>Pattern: Consistent</div>
                  </div>
                </div>
              </div>
              
              <div className="shooting-stat-card">
                <h3>Standing Position</h3>
                <div className="shooting-visual">
                  <div className="target-grid">
                    {[1,0,1,1,0,1,0,1,1,0].map((hit, i) => (
                      <div key={i} className={`target ${hit ? 'hit' : 'miss'}`}></div>
                    ))}
                  </div>
                  <div className="shooting-stats">
                    <div>Accuracy: 78%</div>
                    <div>Avg Time: 28.7s</div>
                    <div>Pattern: Needs work</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'competition' && (
          <div className="competition-insights">
            <h2>Competition Analysis</h2>
            <p>Head-to-head comparisons and race strategies...</p>
          </div>
        )}

        {activeTab === 'training' && (
          <div className="training-optimization">
            <h2>Training Recommendations</h2>
            <p>Personalized training plans based on performance data...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Reports
