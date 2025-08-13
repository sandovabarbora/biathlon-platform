import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import './FatigueProfile.css'

const FatigueProfile = ({ athleteId, athleteName }) => {
  const [profile, setProfile] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [teamComparison, setTeamComparison] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedView, setSelectedView] = useState('overview')

  useEffect(() => {
    if (athleteId) {
      loadFatigueProfile()
      loadTrends()
    }
  }, [athleteId])

  const loadFatigueProfile = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/fatigue/profile/${athleteId}?include_history=true`
      )
      const data = await response.json()
      
      setProfile(data.profile)
      setRecommendations(data.recommendations)
      setTeamComparison(data.team_comparison)
    } catch (error) {
      console.error('Error loading fatigue profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTrends = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/fatigue/trends/${athleteId}?period_days=180`
      )
      const data = await response.json()
      setTrends(data)
    } catch (error) {
      console.error('Error loading trends:', error)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#00ff88'
    if (score >= 60) return '#ffaa00'
    return '#ff3b3b'
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'EXCELLENT'
    if (score >= 70) return 'GOOD'
    if (score >= 60) return 'AVERAGE'
    return 'NEEDS WORK'
  }

  if (loading) {
    return (
      <div className="fatigue-loading">
        <div className="loading-spinner"></div>
        <p>Analyzing fatigue patterns...</p>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="fatigue-error">
        <p>Insufficient data for fatigue analysis</p>
      </div>
    )
  }

  // Prepare data for radar chart
  const radarData = [
    {
      metric: 'Overall Resistance',
      value: profile.fatigue_resistance_score,
      fullMark: 100
    },
    {
      metric: 'Recovery Efficiency',
      value: profile.recovery_efficiency,
      fullMark: 100
    },
    {
      metric: 'Pressure Response',
      value: profile.pressure_response,
      fullMark: 100
    },
    {
      metric: 'Prone Resistance',
      value: profile.prone_resistance,
      fullMark: 100
    },
    {
      metric: 'Standing Resistance',
      value: profile.standing_resistance,
      fullMark: 100
    }
  ]

  // Prepare trend data for line chart
  const trendData = trends?.monthly_data || []

  return (
    <div className="fatigue-profile">
      {/* Header Section */}
      <div className="fatigue-header">
        <div className="athlete-info">
          <h1>{athleteName || profile.name}</h1>
          <div className="athlete-meta">
            <span className="czech-rank">Czech Team #{profile.czech_rank}</span>
            <span className="world-percentile">World Top {profile.world_rank_percentile}%</span>
          </div>
        </div>
        
        <div className="overall-score">
          <div className="score-circle" style={{ borderColor: getScoreColor(profile.fatigue_resistance_score) }}>
            <span className="score-value">{profile.fatigue_resistance_score.toFixed(0)}</span>
            <span className="score-label">FATIGUE SCORE</span>
          </div>
          <div className="score-status" style={{ color: getScoreColor(profile.fatigue_resistance_score) }}>
            {getScoreLabel(profile.fatigue_resistance_score)}
          </div>
        </div>
      </div>

      {/* View Selector */}
      <div className="view-tabs">
        <button 
          className={selectedView === 'overview' ? 'active' : ''}
          onClick={() => setSelectedView('overview')}
        >
          OVERVIEW
        </button>
        <button 
          className={selectedView === 'detailed' ? 'active' : ''}
          onClick={() => setSelectedView('detailed')}
        >
          DETAILED METRICS
        </button>
        <button 
          className={selectedView === 'trends' ? 'active' : ''}
          onClick={() => setSelectedView('trends')}
        >
          TRENDS
        </button>
        <button 
          className={selectedView === 'recommendations' ? 'active' : ''}
          onClick={() => setSelectedView('recommendations')}
        >
          TRAINING PLAN
        </button>
      </div>

      {/* Content Based on Selected View */}
      {selectedView === 'overview' && (
        <div className="overview-content">
          {/* Key Metrics Grid */}
          <div className="metrics-grid">
            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="metric-icon">❤️</div>
              <div className="metric-details">
                <span className="metric-label">HR-Shooting Correlation</span>
                <span className="metric-value">
                  {(profile.hr_shooting_correlation * 100).toFixed(1)}%
                </span>
                <span className="metric-sublabel">
                  {profile.hr_shooting_correlation < -0.3 ? 'Struggles under high HR' : 'Handles HR well'}
                </span>
              </div>
            </motion.div>

            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="metric-icon">⏱️</div>
              <div className="metric-details">
                <span className="metric-label">Time Penalty</span>
                <span className="metric-value">
                  +{profile.lactate_time_penalty.toFixed(1)}s
                </span>
                <span className="metric-sublabel">Extra time when fatigued</span>
              </div>
            </motion.div>

            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="metric-icon">📈</div>
              <div className="metric-details">
                <span className="metric-label">Recovery Rate</span>
                <span className="metric-value" style={{ color: getScoreColor(profile.recovery_efficiency) }}>
                  {profile.recovery_efficiency.toFixed(0)}/100
                </span>
                <span className="metric-sublabel">HR recovery on range</span>
              </div>
            </motion.div>

            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="metric-icon">🎯</div>
              <div className="metric-details">
                <span className="metric-label">Optimal HR</span>
                <span className="metric-value">
                  {profile.optimal_hr_threshold} BPM
                </span>
                <span className="metric-sublabel">Best shooting HR</span>
              </div>
            </motion.div>
          </div>

          {/* Radar Chart */}
          <div className="radar-section">
            <h3>Performance Profile</h3>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#333" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#999', fontSize: 12 }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#666' }} />
                <Radar
                  name="Current"
                  dataKey="value"
                  stroke="#00ff88"
                  fill="#00ff88"
                  fillOpacity={0.3}
                />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                  labelStyle={{ color: '#fff' }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {selectedView === 'detailed' && (
        <div className="detailed-content">
          <div className="detail-cards">
            <div className="detail-card">
              <h3>Pressure Performance Analysis</h3>
              <div className="pressure-zones">
                <div className="zone">
                  <span className="zone-label">Low Pressure</span>
                  <div className="zone-bar">
                    <div className="zone-fill" style={{ width: '85%', background: '#00ff88' }}></div>
                  </div>
                  <span className="zone-value">85%</span>
                </div>
                <div className="zone">
                  <span className="zone-label">High Pressure</span>
                  <div className="zone-bar">
                    <div className="zone-fill" style={{ width: `${profile.pressure_response}%`, background: getScoreColor(profile.pressure_response) }}></div>
                  </div>
                  <span className="zone-value">{profile.pressure_response.toFixed(0)}%</span>
                </div>
              </div>
              <p className="insight">
                {profile.pressure_response > 80 
                  ? "✅ Excellent clutch performer - maintains composure under pressure"
                  : "⚠️ Performance drops in high-pressure situations - focus on mental training"}
              </p>
            </div>

            <div className="detail-card">
              <h3>Position-Specific Resistance</h3>
              <div className="position-comparison">
                <div className="position-stat">
                  <span className="position-label">PRONE</span>
                  <div className="position-score" style={{ color: getScoreColor(profile.prone_resistance) }}>
                    {profile.prone_resistance.toFixed(0)}%
                  </div>
                </div>
                <div className="vs-divider">VS</div>
                <div className="position-stat">
                  <span className="position-label">STANDING</span>
                  <div className="position-score" style={{ color: getScoreColor(profile.standing_resistance) }}>
                    {profile.standing_resistance.toFixed(0)}%
                  </div>
                </div>
              </div>
              <p className="insight">
                {Math.abs(profile.prone_resistance - profile.standing_resistance) > 15
                  ? `⚠️ Significant gap - focus on ${profile.prone_resistance < profile.standing_resistance ? 'prone' : 'standing'} position`
                  : "✅ Well-balanced between positions"}
              </p>
            </div>

            <div className="detail-card">
              <h3>Optimal Performance Zones</h3>
              <div className="optimal-zones">
                <div className="zone-item">
                  <span className="zone-metric">Arrival HR</span>
                  <span className="zone-optimal">{profile.optimal_arrival_hr} BPM</span>
                </div>
                <div className="zone-item">
                  <span className="zone-metric">Shooting HR</span>
                  <span className="zone-optimal">{profile.optimal_hr_threshold} BPM</span>
                </div>
                <div className="zone-item">
                  <span className="zone-metric">Recovery Time</span>
                  <span className="zone-optimal">{(30 / profile.recovery_efficiency * 100).toFixed(0)}s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedView === 'trends' && trends && (
        <div className="trends-content">
          <div className="trend-header">
            <h3>Historical Progression</h3>
            <div className={`trend-indicator ${trends.trend_direction}`}>
              {trends.trend_direction === 'improving' ? '📈' : 
               trends.trend_direction === 'declining' ? '📉' : '➡️'}
              <span>{trends.trend_direction.toUpperCase()}</span>
              <span className="improvement">
                {trends.total_improvement > 0 ? '+' : ''}{trends.total_improvement.toFixed(1)}%
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="month" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="fatigue_shooting_accuracy"
                name="Shooting Under Fatigue %"
                stroke="#00ff88"
                strokeWidth={2}
                dot={{ fill: '#00ff88' }}
              />
              <Line
                type="monotone"
                dataKey="avg_hr_recovery"
                name="HR Recovery (BPM)"
                stroke="#00d4ff"
                strokeWidth={2}
                dot={{ fill: '#00d4ff' }}
              />
            </LineChart>
          </ResponsiveContainer>

          <div className="trend-insights">
            <h4>Key Insights</h4>
            <ul>
              {profile.improvement_rate > 0 && (
                <li>📈 Improving at {profile.improvement_rate.toFixed(1)}% per month</li>
              )}
              {profile.recovery_efficiency > 80 && (
                <li>✅ Elite-level recovery efficiency</li>
              )}
              {profile.trend_direction === 'improving' && (
                <li>🎯 Positive trajectory - training is working</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {selectedView === 'recommendations' && recommendations && (
        <div className="recommendations-content">
          <h3>Personalized Training Recommendations</h3>
          
          {recommendations.map((rec, index) => (
            <motion.div 
              key={index}
              className={`recommendation-card priority-${rec.priority.toLowerCase()}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="rec-header">
                <span className={`priority-badge ${rec.priority.toLowerCase()}`}>
                  {rec.priority} PRIORITY
                </span>
                <span className="expected-impact">{rec.expected_improvement}</span>
              </div>
              
              <h4>{rec.area}</h4>
              <p className="issue">{rec.issue}</p>
              <p className="recommendation">{rec.recommendation}</p>
              
              <div className="exercises">
                <h5>Specific Exercises:</h5>
                <ul>
                  {rec.exercises.map((exercise, i) => (
                    <li key={i}>{exercise}</li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}

          {teamComparison && (
            <div className="team-comparison-card">
              <h4>Team Comparison</h4>
              <div className="comparison-stats">
                <div className="stat">
                  <span className="label">Team Average</span>
                  <span className="value">{teamComparison.team_avg_fatigue_score.toFixed(0)}</span>
                </div>
                <div className="stat">
                  <span className="label">Your Score</span>
                  <span className="value" style={{ color: getScoreColor(profile.fatigue_resistance_score) }}>
                    {profile.fatigue_resistance_score.toFixed(0)}
                  </span>
                </div>
                <div className="stat">
                  <span className="label">Team Rank</span>
                  <span className="value">#{teamComparison.rank_in_team}</span>
                </div>
              </div>
              <p className="comparison-message">
                {teamComparison.comparison === 'above_average' 
                  ? "✅ Performing above team average"
                  : "⚠️ Below team average - see recommendations above"}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default FatigueProfile
