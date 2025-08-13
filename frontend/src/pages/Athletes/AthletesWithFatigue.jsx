import React, { useState, useEffect } from 'react'
import FatigueProfile from '../../components/Analytics/FatigueProfile/FatigueProfile'
import './Athletes.css'

const AthletesWithFatigue = () => {
  const [athletes, setAthletes] = useState([])
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [viewMode, setViewMode] = useState('list') // 'list' or 'fatigue'
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

  const handleViewFatigueProfile = (athlete) => {
    setSelectedAthlete(athlete)
    setViewMode('fatigue')
  }

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
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">
            {viewMode === 'list' ? 'ATHLETES MANAGEMENT' : 'FATIGUE ANALYSIS'}
          </h1>
          <div className="header-actions">
            {viewMode === 'fatigue' && (
              <button 
                className="btn"
                onClick={() => setViewMode('list')}
              >
                ← BACK TO LIST
              </button>
            )}
            <button className="btn btn-primary">TEAM ANALYSIS</button>
          </div>
        </div>

        {viewMode === 'list' ? (
          <div className="athletes-grid">
            {athletes.map(athlete => (
              <div key={athlete.id} className="athlete-card">
                <div className="rank-display">
                  <span className="rank-number">#{athlete.world_rank || 'N/A'}</span>
                </div>
                
                <div className="athlete-main">
                  <h3 className="athlete-name">{athlete.name}</h3>
                  <div className="athlete-meta">
                    <span className="meta-item">IBU: {athlete.id}</span>
                    <span className="meta-item">CZE</span>
                  </div>
                </div>
                
                <div className="card-actions">
                  <button 
                    className="action-btn primary"
                    onClick={() => handleViewFatigueProfile(athlete)}
                  >
                    FATIGUE PROFILE
                  </button>
                  <button className="action-btn">DETAILS</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <FatigueProfile 
            athleteId={selectedAthlete.id}
            athleteName={selectedAthlete.name}
          />
        )}
      </div>
    </div>
  )
}

export default AthletesWithFatigue
