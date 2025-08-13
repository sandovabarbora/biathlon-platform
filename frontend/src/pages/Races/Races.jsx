import React, { useState, useEffect } from 'react'
import './Races.css'

const Races = () => {
  const [races, setRaces] = useState([])
  const [selectedRace, setSelectedRace] = useState(null)
  const [viewMode, setViewMode] = useState('upcoming')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRaces()
  }, [])

  const fetchRaces = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/races/recent')
      const data = await response.json()
      setRaces(data)
      setLoading(false)
    } catch (err) {
      // Mock data
      setRaces([
        {
          race_id: 'BT2425SWRLCP07SWSP',
          date: '2025-01-15',
          location: 'Ruhpolding',
          description: 'Women Sprint',
          discipline: 'Sprint',
          status: 'upcoming'
        },
        {
          race_id: 'BT2425SWRLCP08SWPU',
          date: '2025-01-17',
          location: 'Ruhpolding',
          description: 'Women Pursuit',
          discipline: 'Pursuit',
          status: 'upcoming'
        },
        {
          race_id: 'BT2425SWRLCP06SWSP',
          date: '2025-01-05',
          location: 'Oberhof',
          description: 'Women Sprint',
          discipline: 'Sprint',
          status: 'completed'
        }
      ])
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading Race Calendar...</p>
      </div>
    )
  }

  const upcomingRaces = races.filter(r => r.status === 'upcoming' || new Date(r.date) > new Date())
  const completedRaces = races.filter(r => r.status === 'completed' || new Date(r.date) <= new Date())

  return (
    <div className="races-page">
      <div className="container">
        {/* PAGE HEADER */}
        <div className="page-header">
          <h1 className="page-title">RACE CALENDAR</h1>
          <div className="header-actions">
            <div className="view-toggle">
              <button 
                className={viewMode === 'upcoming' ? 'active' : ''}
                onClick={() => setViewMode('upcoming')}
              >
                UPCOMING
              </button>
              <button 
                className={viewMode === 'results' ? 'active' : ''}
                onClick={() => setViewMode('results')}
              >
                RESULTS
              </button>
            </div>
            <button className="btn btn-primary">EXPORT CALENDAR</button>
          </div>
        </div>

        {/* LIVE RACE BANNER */}
        <div className="live-race-banner">
          <div className="live-indicator">
            <span className="live-dot"></span>
            LIVE NOW
          </div>
          <div className="live-info">
            <h2>WORLD CUP RUHPOLDING</h2>
            <p>Women 7.5km Sprint • Started 14:30 CET</p>
          </div>
          <button className="btn-watch">WATCH LIVE TRACKING</button>
        </div>

        {/* RACES GRID */}
        <div className="races-grid">
          {viewMode === 'upcoming' ? (
            <>
              <h2 className="section-title">UPCOMING RACES</h2>
              {upcomingRaces.map(race => (
                <div key={race.race_id} className="race-card upcoming">
                  <div className="race-date">
                    <span className="day">{new Date(race.date).getDate()}</span>
                    <span className="month">{new Date(race.date).toLocaleDateString('en', { month: 'short' })}</span>
                    <span className="year">{new Date(race.date).getFullYear()}</span>
                  </div>
                  <div className="race-info">
                    <h3 className="race-location">{race.location}</h3>
                    <p className="race-description">{race.description}</p>
                    <div className="race-meta">
                      <span className="discipline">{race.discipline}</span>
                      <span className="time">14:30 CET</span>
                    </div>
                  </div>
                  <div className="race-actions">
                    <button className="action-btn">SET REMINDER</button>
                    <button className="action-btn primary">VIEW DETAILS</button>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <>
              <h2 className="section-title">RACE RESULTS</h2>
              {completedRaces.map(race => (
                <div key={race.race_id} className="race-card completed">
                  <div className="race-date">
                    <span className="day">{new Date(race.date).getDate()}</span>
                    <span className="month">{new Date(race.date).toLocaleDateString('en', { month: 'short' })}</span>
                  </div>
                  <div className="race-info">
                    <h3 className="race-location">{race.location}</h3>
                    <p className="race-description">{race.description}</p>
                    <div className="race-results">
                      <div className="result-item">
                        <span className="position">CZE BEST:</span>
                        <span className="athlete">#21 VOBORNÍKOVÁ</span>
                      </div>
                    </div>
                  </div>
                  <div className="race-actions">
                    <button className="action-btn">VIEW RESULTS</button>
                    <button className="action-btn">ANALYSIS</button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Races
