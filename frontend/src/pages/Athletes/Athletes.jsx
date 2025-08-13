import React, { useState, useEffect } from 'react'
import FatigueProfile from '../../components/Analytics/FatigueProfile/FatigueProfile'
import api from '../../services/api'
import './Athletes.css'

const Athletes = () => {
  const [athletes, setAthletes] = useState([])
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid', 'fatigue', 'comparison'
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [compareMode, setCompareMode] = useState(false)
  const [selectedForCompare, setSelectedForCompare] = useState([])

  useEffect(() => {
    fetchAthletes()
  }, [])

  const fetchAthletes = async () => {
    try {
      setLoading(true)
      const data = await api.athletes.getAll('CZE', 20)
      setAthletes(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching athletes:', err)
      setError('Failed to load athletes data')
    } finally {
      setLoading(false)
    }
  }

  const handleViewFatigueProfile = (athlete) => {
    setSelectedAthlete(athlete)
    setViewMode('fatigue')
  }

  const handleCompareAthletes = async () => {
    if (selectedForCompare.length === 2) {
      setViewMode('comparison')
    }
  }

  const toggleCompareSelection = (athlete) => {
    if (selectedForCompare.find(a => a.id === athlete.id)) {
      setSelectedForCompare(selectedForCompare.filter(a => a.id !== athlete.id))
    } else if (selectedForCompare.length < 2) {
      setSelectedForCompare([...selectedForCompare, athlete])
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading Athletes Data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <h2>Error</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchAthletes}>
          RETRY
        </button>
      </div>
    )
  }

  return (
    <div className="athletes-page">
      <div className="container">
        {/* PAGE HEADER */}
        <div className="page-header">
          <h1 className="page-title">
            {viewMode === 'fatigue' ? 'FATIGUE ANALYSIS' : 
             viewMode === 'comparison' ? 'ATHLETE COMPARISON' : 
             'ATHLETES MANAGEMENT'}
          </h1>
          <div className="header-actions">
            {viewMode !== 'grid' && (
              <button 
                className="btn"
                onClick={() => {
                  setViewMode('grid')
                  setSelectedAthlete(null)
                  setCompareMode(false)
                  setSelectedForCompare([])
                }}
              >
                ← BACK TO LIST
              </button>
            )}
            {viewMode === 'grid' && (
              <>
                <button 
                  className={`btn ${compareMode ? 'btn-primary' : ''}`}
                  onClick={() => setCompareMode(!compareMode)}
                >
                  COMPARE MODE {selectedForCompare.length > 0 && `(${selectedForCompare.length})`}
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => window.open('/api/v1/fatigue/team/analysis?nation=CZE', '_blank')}
                >
                  TEAM FATIGUE ANALYSIS
                </button>
              </>
            )}
          </div>
        </div>

        {/* FILTERS - only show in grid mode */}
        {viewMode === 'grid' && (
          <div className="filters-bar">
            <div className="filter-group">
              <button className="filter-btn active">
                ALL ATHLETES ({athletes.length})
              </button>
              <button className="filter-btn">TOP 30</button>
              <button className="filter-btn">RISING STARS</button>
            </div>
            <div className="search-box">
              <input type="text" placeholder="SEARCH ATHLETE..." />
              <button className="search-btn">◼</button>
            </div>
          </div>
        )}

        {/* CONTENT BASED ON VIEW MODE */}
        {viewMode === 'grid' ? (
          <>
            {/* Athletes Grid */}
            <div className="athletes-grid">
              {athletes.map(athlete => {
                const isSelected = selectedForCompare.find(a => a.id === athlete.id)
                
                return (
                  <div 
                    key={athlete.id} 
                    className={`athlete-card ${isSelected ? 'selected' : ''} ${compareMode ? 'compare-mode' : ''}`}
                    onClick={() => compareMode && toggleCompareSelection(athlete)}
                  >
                    {/* Rank Badge */}
                    <div className="rank-display">
                      <span className="rank-number">#{athlete.world_rank || 'N/A'}</span>
                    </div>
                    
                    {/* Main Info */}
                    <div className="athlete-main">
                      <h3 className="athlete-name">{athlete.name}</h3>
                      <div className="athlete-meta">
                        <span className="meta-item">IBU: {athlete.id}</span>
                        <span className="meta-item">CZE</span>
                      </div>
                    </div>
                    
                    {/* Quick Stats */}
                    <div className="stats-grid">
                      <div className="stat-box">
                        <span className="stat-value">{athlete.world_cup_points || 0}</span>
                        <span className="stat-label">POINTS</span>
                      </div>
                      <div className="stat-box">
                        <span className="stat-value">-</span>
                        <span className="stat-label">FATIGUE</span>
                      </div>
                      <div className="stat-box">
                        <span className="stat-value">-</span>
                        <span className="stat-label">SHOOTING</span>
                      </div>
                      <div className="stat-box">
                        <span className="stat-value good">↑</span>
                        <span className="stat-label">FORM</span>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="card-actions">
                      <button 
                        className="action-btn primary"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleViewFatigueProfile(athlete)
                        }}
                      >
                        FATIGUE PROFILE
                      </button>
                      <button 
                        className="action-btn"
                        onClick={(e) => {
                          e.stopPropagation()
                          // Handle details view
                        }}
                      >
                        DETAILS
                      </button>
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

            {/* Comparison Panel */}
            {compareMode && selectedForCompare.length === 2 && (
              <div className="comparison-panel">
                <h2 className="panel-title">READY TO COMPARE</h2>
                <div className="comparison-preview">
                  <div className="compare-athlete">
                    <h3>{selectedForCompare[0].name}</h3>
                    <span>#{selectedForCompare[0].world_rank}</span>
                  </div>
                  <span className="vs">VS</span>
                  <div className="compare-athlete">
                    <h3>{selectedForCompare[1].name}</h3>
                    <span>#{selectedForCompare[1].world_rank}</span>
                  </div>
                </div>
                <button 
                  className="btn btn-primary"
                  onClick={handleCompareAthletes}
                >
                  VIEW FATIGUE COMPARISON
                </button>
              </div>
            )}
          </>
        ) : viewMode === 'fatigue' ? (
          <FatigueProfile 
            athleteId={selectedAthlete.id}
            athleteName={selectedAthlete.name}
          />
        ) : viewMode === 'comparison' ? (
          <ComparisonView athletes={selectedForCompare} />
        ) : null}
      </div>
    </div>
  )
}

// Comparison Component
const ComparisonView = ({ athletes }) => {
  const [comparisonData, setComparisonData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (athletes.length === 2) {
      loadComparison()
    }
  }, [athletes])

  const loadComparison = async () => {
    try {
      const data = await api.fatigue.compareAthletes(
        athletes[0].id,
        athletes[1].id
      )
      setComparisonData(data)
    } catch (error) {
      console.error('Error loading comparison:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading comparison...</div>
  }

  if (!comparisonData) {
    return <div className="error">Failed to load comparison</div>
  }

  return (
    <div className="comparison-content">
      <div className="comparison-grid">
        <div className="athlete-column">
          <h2>{comparisonData.athlete1.name}</h2>
          <div className="comparison-metrics">
            <div className="metric">
              <span className="label">Fatigue Score</span>
              <span className="value">{comparisonData.athlete1.fatigue_score.toFixed(0)}</span>
            </div>
            <div className="metric">
              <span className="label">Recovery</span>
              <span className="value">{comparisonData.athlete1.recovery.toFixed(0)}%</span>
            </div>
            <div className="metric">
              <span className="label">Pressure</span>
              <span className="value">{comparisonData.athlete1.pressure.toFixed(0)}%</span>
            </div>
          </div>
        </div>
        
        <div className="vs-divider">VS</div>
        
        <div className="athlete-column">
          <h2>{comparisonData.athlete2.name}</h2>
          <div className="comparison-metrics">
            <div className="metric">
              <span className="label">Fatigue Score</span>
              <span className="value">{comparisonData.athlete2.fatigue_score.toFixed(0)}</span>
            </div>
            <div className="metric">
              <span className="label">Recovery</span>
              <span className="value">{comparisonData.athlete2.recovery.toFixed(0)}%</span>
            </div>
            <div className="metric">
              <span className="label">Pressure</span>
              <span className="value">{comparisonData.athlete2.pressure.toFixed(0)}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="comparison-insights">
        <h3>Key Advantages</h3>
        <div className="advantages-grid">
          <div className="advantage-card">
            <h4>{comparisonData.athlete1.name}</h4>
            <ul>
              {comparisonData.advantages.athlete1.map((adv, i) => (
                <li key={i}>{adv}</li>
              ))}
            </ul>
          </div>
          <div className="advantage-card">
            <h4>{comparisonData.athlete2.name}</h4>
            <ul>
              {comparisonData.advantages.athlete2.map((adv, i) => (
                <li key={i}>{adv}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Athletes
