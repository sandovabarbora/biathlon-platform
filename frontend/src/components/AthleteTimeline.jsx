import React, { useState, useEffect } from 'react'
import './AthleteTimeline.css'

const API_URL = 'http://localhost:8000/api/v1'

const AthleteTimeline = ({ athlete, onSelectRace }) => {
  const [history, setHistory] = useState([])
  const [patterns, setPatterns] = useState([])
  const [trends, setTrends] = useState({})
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('season')

  useEffect(() => {
    if (athlete?.id) {
      loadAthleteHistory()
    }
  }, [athlete])

  const loadAthleteHistory = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/athletes/${athlete.id}/history`)
      const data = await response.json()
      
      setHistory(data.history || [])
      setPatterns(data.patterns || [])
      setTrends(data.trends || {})
    } catch (error) {
      console.error('Error loading history:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankColor = (rank) => {
    if (!rank || rank === 'DNF' || rank === 'DNS') return '#666'
    if (rank <= 3) return '#ffd700'
    if (rank <= 10) return '#00ff88'
    if (rank <= 20) return '#0095ff'
    return '#a0a0a0'
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('cs-CZ', { day: 'numeric', month: 'short' })
  }

  if (loading) {
    return <div className="loading">Loading athlete history...</div>
  }

  return (
    <div className="athlete-timeline">
      {/* Header */}
      <div className="timeline-header">
        <div className="athlete-info">
          <h1>{athlete.name}</h1>
          <span className="nation">{athlete.nation}</span>
        </div>
        
        <div className="timeline-controls">
          <button 
            className={timeRange === 'month' ? 'active' : ''}
            onClick={() => setTimeRange('month')}
          >
            Last Month
          </button>
          <button 
            className={timeRange === 'season' ? 'active' : ''}
            onClick={() => setTimeRange('season')}
          >
            Season
          </button>
          <button 
            className={timeRange === 'year' ? 'active' : ''}
            onClick={() => setTimeRange('year')}
          >
            Full Year
          </button>
        </div>

        <div className="trend-indicator">
          <span className="label">Current Form</span>
          <span className={`trend ${trends.direction}`}>
            {trends.direction === 'improving' ? '📈 Improving' :
             trends.direction === 'declining' ? '📉 Declining' :
             trends.direction === 'stable' ? '➡️ Stable' : 'No Data'}
          </span>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="performance-chart">
        <svg viewBox="0 0 1000 300" className="chart-svg">
          {/* Grid lines */}
          {[10, 20, 30, 40].map(rank => (
            <g key={rank}>
              <line 
                x1="50" 
                y1={rank * 6} 
                x2="950" 
                y2={rank * 6} 
                stroke="rgba(255,255,255,0.1)"
              />
              <text x="30" y={rank * 6 + 5} fill="#666" fontSize="12">
                {rank}
              </text>
            </g>
          ))}
          
          {/* Performance line */}
          <polyline
            points={history.map((race, i) => {
              const x = 50 + (i * (900 / history.length))
              const y = race.rank ? race.rank * 6 : 300
              return `${x},${y}`
            }).join(' ')}
            fill="none"
            stroke="#00ff88"
            strokeWidth="2"
          />
          
          {/* Data points */}
          {history.map((race, i) => {
            const x = 50 + (i * (900 / history.length))
            const y = race.rank ? race.rank * 6 : 300
            
            return (
              <g key={i}>
                <circle
                  cx={x}
                  cy={y}
                  r="6"
                  fill={getRankColor(race.rank)}
                  stroke="#fff"
                  strokeWidth="2"
                  className="data-point"
                  onClick={() => onSelectRace(race)}
                />
                {/* Event markers */}
                {race.event_type === 'problem' && (
                  <text x={x} y={y - 10} fontSize="16">⚠️</text>
                )}
                {race.event_type === 'success' && (
                  <text x={x} y={y - 10} fontSize="16">🏆</text>
                )}
              </g>
            )
          })}
        </svg>
        
        {/* X-axis labels */}
        <div className="chart-labels">
          {history.map((race, i) => (
            <div 
              key={i} 
              className="race-label"
              style={{ left: `${5 + (i * (90 / history.length))}%` }}
            >
              <span className="date">{formatDate(race.date)}</span>
              <span className="location">{race.location}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Race List */}
      <div className="race-list">
        <h2>Race Details</h2>
        <div className="race-items">
          {history.slice(0, 20).map((race, i) => (
            <div 
              key={i} 
              className="race-item"
              onClick={() => onSelectRace(race)}
            >
              <div className="race-date">
                {formatDate(race.date)}
              </div>
              
              <div className="race-info">
                <div className="race-header">
                  <span className="location">{race.location}</span>
                  <span className="type">{race.race_type}</span>
                </div>
                
                <div className="race-result">
                  <span className="rank" style={{ color: getRankColor(race.rank) }}>
                    #{race.rank || 'DNF'}
                  </span>
                  
                  {race.shooting && (
                    <span className="shooting">
                      🎯 {race.shooting.total_misses} misses
                      ({race.shooting.prone}+{race.shooting.standing})
                    </span>
                  )}
                  
                  {race.ski_rank && (
                    <span className="ski">
                      ⛷️ Ski #{race.ski_rank}
                    </span>
                  )}
                </div>
                
                {race.weather && (
                  <div className="race-conditions">
                    {race.temperature && <span>🌡️ {race.temperature}°C</span>}
                    {race.wind && <span>💨 {race.wind} m/s</span>}
                  </div>
                )}
              </div>
              
              <button className="analyze-btn">
                Analyze →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Patterns Section */}
      {patterns.length > 0 && (
        <div className="patterns-section">
          <h2>Detected Patterns</h2>
          <div className="pattern-cards">
            {patterns.map((pattern, i) => (
              <div key={i} className={`pattern-card ${pattern.type}`}>
                <div className="pattern-icon">
                  {pattern.type === 'discipline_preference' ? '🎯' :
                   pattern.type === 'weather_sensitivity' ? '🌡️' :
                   pattern.type === 'improvement' ? '📈' : '📊'}
                </div>
                <div className="pattern-content">
                  <h3>{pattern.message}</h3>
                  <p>{pattern.impact}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AthleteTimeline
