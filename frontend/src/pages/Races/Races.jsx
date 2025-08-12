import React, { useState, useEffect } from 'react'
import './Races.css'

const Races = () => {
  const [races, setRaces] = useState([])
  const [selectedRace, setSelectedRace] = useState(null)
  const [liveMode, setLiveMode] = useState(false)
  const [loading, setLoading] = useState(true)
  const [raceResults, setRaceResults] = useState(null)
  const [czechPerformance, setCzechPerformance] = useState(null)

  useEffect(() => {
    fetchRaces()
    // Simulace live dat každých 30 sekund
    if (liveMode) {
      const interval = setInterval(fetchLiveData, 30000)
      return () => clearInterval(interval)
    }
  }, [liveMode])

  const fetchRaces = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/races/recent')
      const data = await response.json()
      setRaces(data)
      setLoading(false)
    } catch (err) {
      // Fallback data
      setRaces([
        {
          race_id: 'BT2425SWRLCP07SWSP',
          date: '2025-01-05',
          location: 'Nove Mesto',
          description: 'Women Sprint',
          discipline: 'Sprint'
        },
        {
          race_id: 'BT2425SWRLCP02SWPU',
          date: '2024-12-15',
          location: 'Hochfilzen',
          description: 'Women Pursuit',
          discipline: 'Pursuit'
        }
      ])
      setLoading(false)
    }
  }

  const fetchRaceAnalysis = async (raceId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/races/${raceId}/analysis`)
      const data = await response.json()
      setRaceResults(data)
      
      // Extrahuj české výsledky
      if (data.czech_athletes) {
        setCzechPerformance(data.czech_athletes)
      }
    } catch (err) {
      console.error('Error fetching race analysis:', err)
    }
  }

  const fetchLiveData = async () => {
    // Simulace live dat
    console.log('Fetching live data...')
  }

  const getPrediction = (athlete) => {
    // AI predikce na základě formy
    const rank = parseInt(athlete.world_rank)
    if (rank <= 10) return { finish: '1-5', confidence: 85 }
    if (rank <= 30) return { finish: '6-15', confidence: 70 }
    if (rank <= 50) return { finish: '16-30', confidence: 60 }
    return { finish: '31+', confidence: 45 }
  }

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>
  }

  return (
    <div className="races-page">
      {/* Header */}
      <div className="races-header">
        <div className="header-main">
          <h1>Race Central</h1>
          <button 
            className={`live-toggle ${liveMode ? 'active' : ''}`}
            onClick={() => setLiveMode(!liveMode)}
          >
            <span className="live-dot"></span>
            {liveMode ? 'LIVE MODE ON' : 'LIVE MODE OFF'}
          </button>
        </div>
        
        {liveMode && (
          <div className="live-ticker">
            <span className="ticker-item">🔴 LIVE: World Cup Oberhof</span>
            <span className="ticker-item">Next Start: 14:45 CET</span>
            <span className="ticker-item">Weather: -5°C, Light Snow</span>
          </div>
        )}
      </div>

      {/* Race Calendar */}
      <div className="races-container">
        <div className="races-sidebar">
          <h2>Upcoming Races</h2>
          <div className="races-list">
            {races.map(race => (
              <div 
                key={race.race_id}
                className={`race-item ${selectedRace?.race_id === race.race_id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedRace(race)
                  fetchRaceAnalysis(race.race_id)
                }}
              >
                <div className="race-date">
                  {new Date(race.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="race-info">
                  <h3>{race.location}</h3>
                  <p>{race.description}</p>
                </div>
                <div className="race-type">
                  {race.discipline}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="races-main">
          {selectedRace ? (
            <>
              {/* Race Details */}
              <div className="race-details-card">
                <div className="race-header">
                  <div>
                    <h2>{selectedRace.location}</h2>
                    <p>{selectedRace.description} • {selectedRace.date}</p>
                  </div>
                  <div className="race-status">
                    {new Date(selectedRace.date) > new Date() ? (
                      <span className="status-upcoming">UPCOMING</span>
                    ) : (
                      <span className="status-completed">COMPLETED</span>
                    )}
                  </div>
                </div>

                {/* Czech Team Performance */}
                {czechPerformance && (
                  <div className="czech-performance">
                    <h3>🇨🇿 Czech Team Results</h3>
                    <div className="performance-grid">
                      {czechPerformance.map(athlete => (
                        <div key={athlete.ibu_id} className="athlete-result">
                          <div className="result-rank">
                            #{athlete.rank}
                          </div>
                          <div className="result-info">
                            <h4>{athlete.name}</h4>
                            <div className="result-stats">
                              <span>Shooting: {athlete.shooting?.pattern?.join('+') || 'N/A'}</span>
                              <span>Time: {athlete.time_behind || 'N/A'}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Race Predictions */}
                <div className="predictions-section">
                  <h3>AI Predictions</h3>
                  <div className="predictions-grid">
                    <div className="prediction-card">
                      <h4>Weather Impact</h4>
                      <div className="prediction-value">HIGH</div>
                      <p>Strong wind expected to affect shooting</p>
                    </div>
                    <div className="prediction-card">
                      <h4>Czech Medal Chance</h4>
                      <div className="prediction-value">35%</div>
                      <p>Based on current form and conditions</p>
                    </div>
                    <div className="prediction-card">
                      <h4>Key Factor</h4>
                      <div className="prediction-value">SHOOTING</div>
                      <p>Standing shooting will be crucial</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Live Race Tracker */}
              {liveMode && (
                <div className="live-tracker">
                  <h3>Live Race Tracker</h3>
                  <div className="tracker-map">
                    <svg viewBox="0 0 800 400" className="race-map">
                      {/* Track outline */}
                      <path 
                        d="M 100 200 Q 200 100, 400 150 T 700 200 Q 600 300, 400 250 T 100 200"
                        fill="none"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="40"
                      />
                      
                      {/* Shooting ranges */}
                      <circle cx="200" cy="150" r="30" fill="rgba(239, 68, 68, 0.2)" stroke="#ef4444"/>
                      <circle cx="600" cy="175" r="30" fill="rgba(239, 68, 68, 0.2)" stroke="#ef4444"/>
                      
                      {/* Athletes positions */}
                      <circle cx="320" cy="180" r="8" fill="#3b82f6" className="athlete-dot">
                        <animate attributeName="cx" values="320;340;360" dur="2s" repeatCount="indefinite"/>
                      </circle>
                      
                      <text x="200" y="150" fill="white" fontSize="12" textAnchor="middle">SHOOTING</text>
                      <text x="600" y="175" fill="white" fontSize="12" textAnchor="middle">SHOOTING</text>
                    </svg>
                  </div>
                  
                  <div className="live-standings">
                    <h4>Current Top 5</h4>
                    <div className="standings-list">
                      {[
                        { pos: 1, name: 'BRAISAZ-BOUCHET J.', nation: 'FRA', time: '23:45.2' },
                        { pos: 2, name: 'OEBERG E.', nation: 'SWE', time: '+12.3' },
                        { pos: 3, name: 'DAVIDOVA M.', nation: 'CZE', time: '+18.7' },
                        { pos: 4, name: 'PREUSS F.', nation: 'GER', time: '+22.1' },
                        { pos: 5, name: 'SIMON J.', nation: 'FRA', time: '+28.5' }
                      ].map(athlete => (
                        <div key={athlete.pos} className="standing-row">
                          <span className="standing-pos">{athlete.pos}</span>
                          <span className="standing-name">{athlete.name}</span>
                          <span className="standing-nation">{athlete.nation}</span>
                          <span className="standing-time">{athlete.time}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="no-race-selected">
              <h2>Select a race to view details</h2>
              <p>Choose from upcoming or recent races to see analysis and predictions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Races
