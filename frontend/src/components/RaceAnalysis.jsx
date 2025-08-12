import React, { useState, useEffect } from 'react'
import './RaceAnalysis.css'

const API_URL = 'http://localhost:8000/api/v1'

const RaceAnalysis = ({ raceId, czechAthletes }) => {
  const [raceData, setRaceData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedAthlete, setSelectedAthlete] = useState(null)

  useEffect(() => {
    if (raceId) {
      loadRaceAnalysis()
    } else {
      // Load last race
      loadLastRace()
    }
  }, [raceId])

  const loadRaceAnalysis = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/races/${raceId}/analysis`)
      const data = await response.json()
      setRaceData(data)
      
      // Auto-select first Czech athlete
      if (data.czech_athletes?.length > 0) {
        setSelectedAthlete(data.czech_athletes[0])
      }
    } catch (error) {
      console.error('Error loading race analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadLastRace = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/races/last`)
      const data = await response.json()
      setRaceData(data)
    } catch (error) {
      console.error('Error loading last race:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (timeStr) => {
    if (!timeStr) return ''
    return timeStr.replace('+', '')
  }

  const getShootingVisual = (shooting) => {
    if (!shooting) return null
    
    const pattern = shooting.pattern || []
    const rounds = []
    
    // Split into prone and standing (usually 2+2 for Sprint/Pursuit)
    const prone = pattern.slice(0, 2)
    const standing = pattern.slice(2, 4)
    
    return (
      <div className="shooting-visual">
        {prone.length > 0 && (
          <div className="shooting-round prone">
            <span className="label">Prone</span>
            <div className="targets">
              {prone.map((misses, i) => (
                <div key={i} className="shot-group">
                  {[...Array(5)].map((_, j) => (
                    <span key={j} className={j < (5 - misses) ? 'hit' : 'miss'}>
                      {j < (5 - misses) ? '●' : '○'}
                    </span>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {standing.length > 0 && (
          <div className="shooting-round standing">
            <span className="label">Standing</span>
            <div className="targets">
              {standing.map((misses, i) => (
                <div key={i} className="shot-group">
                  {[...Array(5)].map((_, j) => (
                    <span key={j} className={j < (5 - misses) ? 'hit' : 'miss'}>
                      {j < (5 - misses) ? '●' : '○'}
                    </span>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return <div className="loading">Loading race analysis...</div>
  }

  if (!raceData) {
    return <div className="no-data">No race data available</div>
  }

  return (
    <div className="race-analysis">
      {/* Race Header */}
      <div className="race-header">
        <div className="race-title">
          <h1>{raceData.competition?.Description || 'Race Analysis'}</h1>
          <div className="race-meta">
            <span className="location">{raceData.competition?.Place}</span>
            <span className="date">{new Date(raceData.competition?.StartTime).toLocaleDateString('cs-CZ')}</span>
          </div>
        </div>
        
        <div className="race-conditions">
          {raceData.weather && (
            <>
              {raceData.weather.AirTemp && (
                <div className="condition">
                  <span className="icon">🌡️</span>
                  <span>{raceData.weather.AirTemp}°C</span>
                </div>
              )}
              {raceData.weather.WindSpeed && (
                <div className="condition">
                  <span className="icon">💨</span>
                  <span>{raceData.weather.WindSpeed} m/s</span>
                </div>
              )}
              {raceData.weather.SnowCondition && (
                <div className="condition">
                  <span className="icon">❄️</span>
                  <span>{raceData.weather.SnowCondition}</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Winner Info */}
      <div className="winner-section">
        <h2>🏆 Winner</h2>
        <div className="winner-card">
          <div className="winner-info">
            <span className="name">{raceData.winner?.name}</span>
            <span className="nation">{raceData.winner?.nation}</span>
            <span className="time">{raceData.winner?.time}</span>
          </div>
        </div>
      </div>

      {/* Czech Athletes Performance */}
      <div className="czech-section">
        <h2>🇨🇿 Czech Team Results</h2>
        
        {/* Athlete Selector */}
        <div className="athlete-tabs">
          {raceData.czech_athletes?.map(athlete => (
            <button
              key={athlete.ibu_id}
              className={selectedAthlete?.ibu_id === athlete.ibu_id ? 'active' : ''}
              onClick={() => setSelectedAthlete(athlete)}
            >
              <span className="name">{athlete.name}</span>
              <span className="rank">#{athlete.rank}</span>
            </button>
          ))}
        </div>

        {/* Selected Athlete Analysis */}
        {selectedAthlete && (
          <div className="athlete-analysis">
            <div className="result-summary">
              <div className="stat-card rank">
                <label>Final Position</label>
                <value>{selectedAthlete.rank}</value>
                <span className="behind">{formatTime(selectedAthlete.time_behind)} behind</span>
              </div>
              
              <div className="stat-card shooting">
                <label>Shooting</label>
                <value>{selectedAthlete.shooting?.total_misses || 0}</value>
                <span className="detail">misses</span>
              </div>
              
              <div className="stat-card ski">
                <label>Ski Rank</label>
                <value>{selectedAthlete.ski_rank || 'N/A'}</value>
                {selectedAthlete.gained_positions_skiing > 0 && (
                  <span className="gain">↑ {selectedAthlete.gained_positions_skiing}</span>
                )}
              </div>
              
              <div className="stat-card shooting-rank">
                <label>Shooting Rank</label>
                <value>{selectedAthlete.shooting_rank || 'N/A'}</value>
                {selectedAthlete.lost_positions_shooting > 0 && (
                  <span className="loss">↓ {selectedAthlete.lost_positions_shooting}</span>
                )}
              </div>
            </div>

            {/* Shooting Detail */}
            <div className="shooting-detail">
              <h3>Shooting Detail</h3>
              {getShootingVisual(selectedAthlete.shooting)}
              
              <div className="shooting-stats">
                <div className="stat">
                  <label>Prone Accuracy</label>
                  <value>{selectedAthlete.shooting?.prone_accuracy?.toFixed(0)}%</value>
                </div>
                <div className="stat">
                  <label>Standing Accuracy</label>
                  <value>{selectedAthlete.shooting?.standing_accuracy?.toFixed(0)}%</value>
                </div>
              </div>
            </div>

            {/* What-If Analysis */}
            {selectedAthlete.potential_with_clean_shooting && (
              <div className="what-if-section">
                <h3>What If Analysis</h3>
                <div className="scenarios">
                  <div className="scenario clean">
                    <div className="scenario-title">Clean Shooting (0 misses)</div>
                    <div className="scenario-result">
                      <span className="potential-rank">
                        #{selectedAthlete.potential_with_clean_shooting.rank}
                      </span>
                      <span className="positions-gained">
                        ↑ {selectedAthlete.potential_with_clean_shooting.positions_gained} positions
                      </span>
                      <span className="time-saved">
                        {selectedAthlete.potential_with_clean_shooting.time_saved}s saved
                      </span>
                    </div>
                  </div>
                  
                  {selectedAthlete.shooting?.total_misses > 1 && (
                    <div className="scenario one-miss">
                      <div className="scenario-title">With 1 miss only</div>
                      <div className="scenario-result">
                        <span className="potential-rank">
                          #{Math.max(selectedAthlete.rank - Math.floor(selectedAthlete.shooting.total_misses * 0.7), 1)}
                        </span>
                        <span className="positions-gained">
                          ↑ {Math.floor(selectedAthlete.shooting.total_misses * 0.7)} positions
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Race Flow Visualization */}
            <div className="race-flow">
              <h3>Race Progress</h3>
              <div className="flow-chart">
                <div className="checkpoint start">
                  <span className="label">Start</span>
                  <span className="position">→</span>
                </div>
                
                <div className="checkpoint shooting">
                  <span className="label">Prone</span>
                  <span className="position">#{selectedAthlete.position_after_prone || '?'}</span>
                  <span className="misses">{selectedAthlete.shooting?.prone} misses</span>
                </div>
                
                <div className="checkpoint skiing">
                  <span className="label">Lap 2</span>
                  <span className="position">#{selectedAthlete.position_after_lap2 || '?'}</span>
                </div>
                
                <div className="checkpoint shooting">
                  <span className="label">Standing</span>
                  <span className="position">#{selectedAthlete.position_after_standing || '?'}</span>
                  <span className="misses">{selectedAthlete.shooting?.standing} misses</span>
                </div>
                
                <div className="checkpoint finish">
                  <span className="label">Finish</span>
                  <span className="position">#{selectedAthlete.rank}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Race Statistics */}
      <div className="race-stats">
        <h2>Race Statistics</h2>
        <div className="stats-grid">
          <div className="stat">
            <label>Total Finishers</label>
            <value>{raceData.total_finishers}</value>
          </div>
          <div className="stat">
            <label>DNF</label>
            <value>{raceData.dnf_count}</value>
          </div>
          <div className="stat">
            <label>Czech Athletes</label>
            <value>{raceData.czech_athletes?.length || 0}</value>
          </div>
          <div className="stat">
            <label>Best Czech</label>
            <value>
              #{Math.min(...(raceData.czech_athletes?.map(a => a.rank) || [999]))}
            </value>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RaceAnalysis
