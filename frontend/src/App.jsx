import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import AthleteTimeline from './components/AthleteTimeline'
import RaceAnalysis from './components/RaceAnalysis'
import HeadToHead from './components/HeadToHead'
import './App.css'

const API_URL = 'http://localhost:8000/api/v1'

function App() {
  const [view, setView] = useState('dashboard')
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [selectedRace, setSelectedRace] = useState(null)
  const [czechAthletes, setCzechAthletes] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadCzechAthletes()
  }, [])

  const loadCzechAthletes = async () => {
    try {
      const response = await fetch(`${API_URL}/athletes?nation=CZE`)
      const data = await response.json()
      setCzechAthletes(data)
    } catch (error) {
      console.error('Error loading athletes:', error)
    }
  }

  return (
    <div className="app">
      {/* Fixed Navigation Bar */}
      <nav className="nav-bar">
        <div className="nav-logo">
          <span className="flag">🇨🇿</span>
          <h1>Biathlon Analytics</h1>
        </div>
        
        <div className="nav-tabs">
          <button 
            className={view === 'dashboard' ? 'active' : ''}
            onClick={() => setView('dashboard')}
          >
            <span className="icon">📊</span>
            Dashboard
          </button>
          <button 
            className={view === 'timeline' ? 'active' : ''}
            onClick={() => setView('timeline')}
          >
            <span className="icon">📈</span>
            Timeline
          </button>
          <button 
            className={view === 'race' ? 'active' : ''}
            onClick={() => setView('race')}
          >
            <span className="icon">🏁</span>
            Race Analysis
          </button>
          <button 
            className={view === 'h2h' ? 'active' : ''}
            onClick={() => setView('h2h')}
          >
            <span className="icon">⚔️</span>
            Head to Head
          </button>
        </div>

        <div className="nav-actions">
          <div className="next-race">
            <span className="label">Next Race</span>
            <span className="race-name">Oberhof Sprint</span>
            <span className="countdown">2d 14h</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {view === 'dashboard' && (
          <Dashboard 
            athletes={czechAthletes}
            onSelectAthlete={(athlete) => {
              setSelectedAthlete(athlete)
              setView('timeline')
            }}
          />
        )}
        
        {view === 'timeline' && selectedAthlete && (
          <AthleteTimeline 
            athlete={selectedAthlete}
            onSelectRace={(race) => {
              setSelectedRace(race)
              setView('race')
            }}
          />
        )}
        
        {view === 'race' && (
          <RaceAnalysis 
            raceId={selectedRace?.race_id}
            czechAthletes={czechAthletes}
          />
        )}
        
        {view === 'h2h' && (
          <HeadToHead 
            athletes={czechAthletes}
          />
        )}
      </main>
    </div>
  )
}

export default App
