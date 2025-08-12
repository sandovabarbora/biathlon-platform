import React, { useState, useEffect } from 'react'
import './Athletes.css'

const Athletes = () => {
  const [athletes, setAthletes] = useState([])
  const [selectedAthletes, setSelectedAthletes] = useState([])
  const [compareMode, setCompareMode] = useState(false)
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('rank')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAthletes()
  }, [])

  const fetchAthletes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=20')
      const data = await response.json()
      setAthletes(data)
      setLoading(false)
    } catch (err) {
      setLoading(false)
    }
  }

  const toggleAthleteSelection = (athlete) => {
    if (selectedAthletes.find(a => a.id === athlete.id)) {
      setSelectedAthletes(selectedAthletes.filter(a => a.id !== athlete.id))
    } else if (selectedAthletes.length < 3) {
      setSelectedAthletes([...selectedAthletes, athlete])
    }
  }

  const getPerformanceColor = (rank) => {
    if (rank <= 10) return '#10b981'
    if (rank <= 30) return '#3b82f6'
    if (rank <= 50) return '#f59e0b'
    return '#ef4444'
  }

  const sortedAthletes = [...athletes].sort((a, b) => {
    if (sortBy === 'rank') return parseInt(a.world_rank) - parseInt(b.world_rank)
    if (sortBy === 'points') return parseInt(b.world_cup_points) - parseInt(a.world_cup_points)
    if (sortBy === 'name') return a.name.localeCompare(b.name)
    return 0
  })

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>
  }

  return (
    <div className="athletes-page">
      {/* Header with Controls */}
      <div className="page-header">
        <div className="header-top">
          <h1>Athletes Management</h1>
          <button 
            className={`compare-btn ${compareMode ? 'active' : ''}`}
            onClick={() => setCompareMode(!compareMode)}
          >
            Compare Mode {selectedAthletes.length > 0 && `(${selectedAthletes.length})`}
          </button>
        </div>
        
        <div className="controls-bar">
          <div className="filter-group">
            <button 
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >All Athletes</button>
            <button 
              className={filter === 'top30' ? 'active' : ''}
              onClick={() => setFilter('top30')}
            >Top 30</button>
            <button 
              className={filter === 'rising' ? 'active' : ''}
              onClick={() => setFilter('rising')}
            >Rising Stars</button>
          </div>
          
          <div className="sort-group">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="rank">World Rank</option>
              <option value="points">Points</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>
      </div>

      {/* Athletes Grid */}
      <div className="athletes-grid">
        {sortedAthletes
          .filter(a => {
            if (filter === 'top30') return parseInt(a.world_rank) <= 30
            if (filter === 'rising') return parseInt(a.world_rank) <= 50
            return true
          })
          .map(athlete => {
            const rank = parseInt(athlete.world_rank)
            const isSelected = selectedAthletes.find(a => a.id === athlete.id)
            
            return (
              <div 
                key={athlete.id} 
                className={`athlete-card ${isSelected ? 'selected' : ''} ${compareMode ? 'compare-mode' : ''}`}
                onClick={() => compareMode && toggleAthleteSelection(athlete)}
              >
                {/* Performance Indicator */}
                <div 
                  className="performance-indicator"
                  style={{background: getPerformanceColor(rank)}}
                ></div>
                
                {/* Rank Badge */}
                <div className="rank-badge">
                  <span className="rank-number">#{rank}</span>
                  <span className="rank-change">
                    {rank <= 20 ? '↑2' : rank <= 40 ? '→' : '↓3'}
                  </span>
                </div>
                
                {/* Athlete Info */}
                <div className="athlete-main-info">
                  <h3>{athlete.name}</h3>
                  <div className="athlete-tags">
                    <span className="tag nation">CZE</span>
                    {rank <= 10 && <span className="tag elite">ELITE</span>}
                    {rank > 30 && rank <= 50 && <span className="tag potential">POTENTIAL</span>}
                  </div>
                </div>
                
                {/* Stats Grid */}
                <div className="athlete-stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">WC Points</span>
                    <span className="stat-value">{athlete.world_cup_points}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Shooting</span>
                    <span className="stat-value">82%</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Speed Rank</span>
                    <span className="stat-value">#{rank + 5}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Form</span>
                    <span className="stat-value trend-up">↑ Good</span>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="athlete-actions">
                  <button className="action-btn primary">View Details</button>
                  <button className="action-btn secondary">Training Plan</button>
                </div>
                
                {/* Compare Checkbox */}
                {compareMode && (
                  <div className="compare-checkbox">
                    <input 
                      type="checkbox" 
                      checked={isSelected}
                      onChange={() => {}}
                    />
                  </div>
                )}
              </div>
            )
          })}
      </div>

      {/* Comparison Panel */}
      {compareMode && selectedAthletes.length > 1 && (
        <div className="comparison-panel">
          <h2>Performance Comparison</h2>
          <div className="comparison-grid">
            {selectedAthletes.map(athlete => (
              <div key={athlete.id} className="comparison-column">
                <h3>{athlete.name}</h3>
                <div className="comparison-stats">
                  <div className="comparison-stat">
                    <span>World Rank</span>
                    <strong>#{athlete.world_rank}</strong>
                  </div>
                  <div className="comparison-stat">
                    <span>Points</span>
                    <strong>{athlete.world_cup_points}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="analyze-btn">
            Deep Analysis →
          </button>
        </div>
      )}
    </div>
  )
}

export default Athletes
