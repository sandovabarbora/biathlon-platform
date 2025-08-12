import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './styles/global.css'
import Dashboard from './components/Dashboard'
import AthleteDetail from './components/AthleteDetail'
import ComparisonView from './components/ComparisonView'

const API_URL = 'http://localhost:8000'

function App() {
    const [currentView, setCurrentView] = useState('dashboard')
    const [selectedAthlete, setSelectedAthlete] = useState(null)
    const [athletes, setAthletes] = useState([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState('')

    useEffect(() => {
        loadAthletes()
    }, [])

    const loadAthletes = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/athletes?nation=CZE`)
            setAthletes(response.data.athletes || [])
        } catch (error) {
            console.error('Error loading athletes:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = async (e) => {
        e.preventDefault()
        if (!searchQuery.trim()) return

        try {
            const response = await axios.get(`${API_URL}/api/search?q=${searchQuery}`)
            if (response.data.results.length > 0) {
                setSelectedAthlete(response.data.results[0].name)
                setCurrentView('athlete')
            }
        } catch (error) {
            console.error('Search error:', error)
        }
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="header">
                <div className="container">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <h1 className="logo">🎿 Biathlon Pro</h1>
                            <span className="badge badge-primary">Trenérská verze</span>
                        </div>
                        
                        <nav className="nav">
                            <button 
                                className={`nav-link ${currentView === 'dashboard' ? 'active' : ''}`}
                                onClick={() => setCurrentView('dashboard')}
                            >
                                Přehled
                            </button>
                            <button 
                                className={`nav-link ${currentView === 'athlete' ? 'active' : ''}`}
                                onClick={() => setCurrentView('athlete')}
                            >
                                Závodník
                            </button>
                            <button 
                                className={`nav-link ${currentView === 'comparison' ? 'active' : ''}`}
                                onClick={() => setCurrentView('comparison')}
                            >
                                Srovnání
                            </button>
                        </nav>

                        <form onSubmit={handleSearch} className="search-form">
                            <input
                                type="text"
                                placeholder="Hledat závodníka..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="form-input"
                                style={{ width: '200px' }}
                            />
                            <button type="submit" className="btn btn-primary btn-sm">
                                Hledat
                            </button>
                        </form>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="main-content">
                <div className="container">
                    {loading ? (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p>Načítám data...</p>
                        </div>
                    ) : (
                        <>
                            {currentView === 'dashboard' && (
                                <Dashboard 
                                    athletes={athletes}
                                    onSelectAthlete={(name) => {
                                        setSelectedAthlete(name)
                                        setCurrentView('athlete')
                                    }}
                                />
                            )}
                            
                            {currentView === 'athlete' && (
                                <AthleteDetail 
                                    athleteName={selectedAthlete || athletes[0]?.name}
                                    athletes={athletes}
                                    onChangeAthlete={setSelectedAthlete}
                                />
                            )}
                            
                            {currentView === 'comparison' && (
                                <ComparisonView athletes={athletes} />
                            )}
                        </>
                    )}
                </div>
            </main>

            <style jsx>{`
                .app {
                    min-height: 100vh;
                    background: #f8f9fa;
                }

                .header {
                    background: white;
                    border-bottom: 1px solid #e5e7eb;
                    padding: 16px 0;
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                }

                .logo {
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin: 0;
                }

                .nav {
                    display: flex;
                    gap: 8px;
                }

                .nav-link {
                    padding: 8px 16px;
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    color: #6b7280;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .nav-link:hover {
                    background: #f3f4f6;
                    color: #374151;
                }

                .nav-link.active {
                    background: #dbeafe;
                    color: #1e40af;
                }

                .search-form {
                    display: flex;
                    gap: 8px;
                }

                .main-content {
                    padding: 32px 0;
                    min-height: calc(100vh - 80px);
                }
            `}</style>
        </div>
    )
}

export default App
