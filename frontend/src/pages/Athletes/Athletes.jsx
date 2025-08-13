import React, { useState, useEffect } from 'react'
import './Athletes.css'

const Athletes = () => {
  const [athletes, setAthletes] = useState([])
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [compareMode, setCompareMode] = useState(false)
  const [selectedForCompare, setSelectedForCompare] = useState([])
  const [filter, setFilter] = useState('all')
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
      console.error('Error fetching athletes:', err)
      setLoading(false)
    }
  }

  const fetchAthleteDetails = async (athleteId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/athletes/${athleteId}/performance`)
      const data = await response.json()
      setSelectedAthlete({...selectedAthlete, performance: data})
    } catch (err) {
      console.error('Error fetching athlete details:', err)
    }
  }

  const toggleCompareSelection = (athlete) => {
    if (selectedForCompare.find(a => a.id === athlete.id)) {
      setSelectedForCompare(selectedForCompare.filter(a => a.id !== athlete.id))
    } else if (selectedForCompare.length < 3) {
      setSelectedForCompare([...selectedForCompare, athlete])
    }
  }

  const filteredAthletes = athletes.filter(athlete => {
    const rank = parseInt(athlete.world_rank) || 999
    if (filter === 'top30') return rank <= 30
    if (filter === 'rising') return rank <= 50 && rank > 30
    return true
  })

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading Athletes Data...</p>
      </div>
    )
  }

  return (
    <div className="athletes-page">
      <div className="container">
        {/* PAGE HEADER */}
        <div className="page-header">
          <h1 className="page-title">ATHLETES MANAGEMENT</h1>
          <div className="header-actions">
            <button 
              className={`btn ${compareMode ? 'btn-primary' : ''}`}
              onClick={() => setCompareMode(!compareMode)}
            >
              COMPARE MODE {selectedForCompare.length > 0 && `(${selectedForCompare.length})`}
            </button>
            <button className="btn">ADD ATHLETE</button>
          </div>
        </div>

        {/* FILTERS */}
        <div className="filters-bar">
          <div className="filter-group">
            <button 
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              ALL ATHLETES ({athletes.length})
            </button>
            <button 
              className={`filter-btn ${filter === 'top30' ? 'active' : ''}`}
              onClick={() => setFilter('top30')}
            >
              TOP 30
            </button>
            <button 
              className={`filter-btn ${filter === 'rising' ? 'active' : ''}`}
              onClick={() => setFilter('rising')}
            >
              RISING STARS
            </button>
          </div>
          
          <div className="search-box">
            <input type="text" placeholder="SEARCH ATHLETE..." />
            <button className="search-btn">◼</button>
          </div>
        </div>

        {/* ATHLETES GRID */}
        <div className="athletes-grid">
          {filteredAthletes.map(athlete => {
            const rank = parseInt(athlete.world_rank) || 999
            const isSelected = selectedForCompare.find(a => a.id === athlete.id)
            
            return (
              <div 
                key={athlete.id} 
                className={`athlete-card ${isSelected ? 'selected' : ''} ${compareMode ? 'compare-mode' : ''}`}
                onClick={() => compareMode && toggleCompareSelection(athlete)}
              >
                {/* Rank Badge */}
                <div className={`rank-display ${rank <= 30 ? 'top' : ''}`}>
                  <span className="rank-number">#{athlete.world_rank || 'N/A'}</span>
                  <span className="rank-change">↑2</span>
                </div>
                
                {/* Main Info */}
                <div className="athlete-main">
                  <h3 className="athlete-name">{athlete.name}</h3>
                  <div className="athlete-meta">
                    <span className="meta-item">IBU: {athlete.id}</span>
                    <span className="meta-item">CZE</span>
                  </div>
                </div>
                
                {/* Stats Grid */}
                <div className="stats-grid">
                  <div className="stat-box">
                    <span className="stat-value">{athlete.world_cup_points || 0}</span>
                    <span className="stat-label">POINTS</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-value">87%</span>
                    <span className="stat-label">SHOOTING</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-value">24:32</span>
                    <span className="stat-label">AVG TIME</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-value good">↑12</span>
                    <span className="stat-label">FORM</span>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="card-actions">
                  <button 
                    className="action-btn primary"
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedAthlete(athlete)
                      fetchAthleteDetails(athlete.id)
                    }}
                  >
                    VIEW DETAILS
                  </button>
                  <button className="action-btn">TRAINING</button>
                </div>
                
                {/* Compare Checkbox */}
                {compareMode && (
                  <div className="compare-indicator">
                    {isSelected ? '✓' : '○'}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* COMPARISON PANEL */}
        {compareMode && selectedForCompare.length >= 2 && (
          <div className="comparison-panel">
            <h2 className="panel-title">PERFORMANCE COMPARISON</h2>
            <div className="comparison-grid">
              {selectedForCompare.map(athlete => (
                <div key={athlete.id} className="compare-column">
                  <h3>{athlete.name}</h3>
                  <div className="compare-stats">
                    <div className="compare-stat">
                      <span className="label">World Rank</span>
                      <span className="value">#{athlete.world_rank}</span>
                    </div>
                    <div className="compare-stat">
                      <span className="label">Points</span>
                      <span className="value">{athlete.world_cup_points}</span>
                    </div>
                    <div className="compare-stat">
                      <span className="label">Shooting</span>
                      <span className="value">87%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <button className="btn btn-primary">GENERATE COMPARISON REPORT</button>
          </div>
        )}

        {/* ATHLETE DETAILS MODAL */}
        {selectedAthlete && (
          <div className="modal-overlay" onClick={() => setSelectedAthlete(null)}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{selectedAthlete.name}</h2>
                <button className="close-btn" onClick={() => setSelectedAthlete(null)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">WORLD RANKING</span>
                    <span className="detail-value">#{selectedAthlete.world_rank}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">SEASON POINTS</span>
                    <span className="detail-value">{selectedAthlete.world_cup_points}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">RACES COMPLETED</span>
                    <span className="detail-value">15</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">PODIUMS</span>
                    <span className="detail-value">3</span>
                  </div>
                </div>
                
                <div className="performance-chart">
                  <h3>SEASON PERFORMANCE</h3>
                  <div className="mini-chart">
                    {[65, 78, 72, 85, 90, 88, 92, 87].map((height, i) => (
                      <div key={i} className="chart-bar" style={{height: `${height}%`}}></div>
                    ))}
                  </div>
                </div>
                
                <div className="modal-actions">
                  <button className="btn btn-primary">VIEW FULL PROFILE</button>
                  <button className="btn">EXPORT DATA</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Athletes
