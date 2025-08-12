import React, { useState, useEffect } from 'react'
import './HeadToHead.css'

const API_URL = 'http://localhost:8000/api/v1'

const HeadToHead = ({ athletes }) => {
  const [athlete1, setAthlete1] = useState(null)
  const [athlete2, setAthlete2] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [h2hHistory, setH2hHistory] = useState(null)
  const [loading, setLoading] = useState(false)
  const [searchTerm1, setSearchTerm1] = useState('')
  const [searchTerm2, setSearchTerm2] = useState('')
  const [allAthletes, setAllAthletes] = useState([])

  useEffect(() => {
    loadAllAthletes()
  }, [])

  const loadAllAthletes = async () => {
    try {
      // Load Czech athletes
      const czechResponse = await fetch(`${API_URL}/athletes?nation=CZE`)
      const czechData = await czechResponse.json()
      
      // Load top international athletes
      const topResponse = await fetch(`${API_URL}/athletes?limit=50`)
      const topData = await topResponse.json()
      
      // Combine and deduplicate
      const combined = [...czechData, ...topData]
      const unique = Array.from(new Map(combined.map(a => [a.id, a])).values())
      
      setAllAthletes(unique)
      
      // Pre-select first Czech athlete
      if (czechData.length > 0) {
        setAthlete1(czechData[0])
      }
    } catch (error) {
      console.error('Error loading athletes:', error)
    }
  }

  const loadComparison = async () => {
    if (!athlete1 || !athlete2) return
    
    setLoading(true)
    try {
      // Load both athletes' performance
      const [perf1Response, perf2Response] = await Promise.all([
        fetch(`${API_URL}/athletes/${athlete1.id}/performance`),
        fetch(`${API_URL}/athletes/${athlete2.id}/performance`)
      ])
      
      const perf1 = await perf1Response.json()
      const perf2 = await perf2Response.json()
      
      // Load head-to-head history
      const h2hResponse = await fetch(
        `${API_URL}/analytics/head-to-head?athlete1=${athlete1.id}&athlete2=${athlete2.id}`
      )
      const h2hData = await h2hResponse.json()
      
      setComparison({ athlete1: perf1, athlete2: perf2 })
      setH2hHistory(h2hData)
    } catch (error) {
      console.error('Error loading comparison:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (athlete1 && athlete2) {
      loadComparison()
    }
  }, [athlete1, athlete2])

  const getComparisonClass = (value1, value2, inverted = false) => {
    if (inverted) {
      return value1 > value2 ? 'worse' : value1 < value2 ? 'better' : 'equal'
    }
    return value1 < value2 ? 'worse' : value1 > value2 ? 'better' : 'equal'
  }

  const filteredAthletes1 = allAthletes.filter(a => 
    a.name.toLowerCase().includes(searchTerm1.toLowerCase()) ||
    a.nation.toLowerCase().includes(searchTerm1.toLowerCase())
  )

  const filteredAthletes2 = allAthletes.filter(a => 
    a.name.toLowerCase().includes(searchTerm2.toLowerCase()) ||
    a.nation.toLowerCase().includes(searchTerm2.toLowerCase())
  )

  return (
    <div className="head-to-head">
      <div className="h2h-header">
        <h1>Head to Head Comparison</h1>
        <p>Compare athletes directly to identify strengths and weaknesses</p>
      </div>

      {/* Athlete Selection */}
      <div className="athlete-selection">
        <div className="athlete-selector">
          <h3>Select Athlete 1 {athlete1?.nation === 'CZE' && '🇨🇿'}</h3>
          <input
            type="text"
            placeholder="Search athlete..."
            value={searchTerm1}
            onChange={(e) => setSearchTerm1(e.target.value)}
            className="search-input"
          />
          <div className="athlete-list">
            {filteredAthletes1.slice(0, 10).map(athlete => (
              <div
                key={athlete.id}
                className={`athlete-option ${athlete1?.id === athlete.id ? 'selected' : ''} ${athlete.nation === 'CZE' ? 'czech' : ''}`}
                onClick={() => setAthlete1(athlete)}
              >
                <span className="name">{athlete.name}</span>
                <span className="nation">{athlete.nation}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="vs-divider">
          <span>VS</span>
        </div>

        <div className="athlete-selector">
          <h3>Select Athlete 2 {athlete2?.nation === 'CZE' && '🇨🇿'}</h3>
          <input
            type="text"
            placeholder="Search athlete..."
            value={searchTerm2}
            onChange={(e) => setSearchTerm2(e.target.value)}
            className="search-input"
          />
          <div className="athlete-list">
            {filteredAthletes2.slice(0, 10).map(athlete => (
              <div
                key={athlete.id}
                className={`athlete-option ${athlete2?.id === athlete.id ? 'selected' : ''} ${athlete.nation === 'CZE' ? 'czech' : ''}`}
                onClick={() => setAthlete2(athlete)}
              >
                <span className="name">{athlete.name}</span>
                <span className="nation">{athlete.nation}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {loading && <div className="loading">Loading comparison...</div>}

      {comparison && !loading && (
        <>
          {/* Head to Head Record */}
          {h2hHistory && h2hHistory.total_races > 0 && (
            <div className="h2h-record">
              <h2>Direct Head-to-Head Record</h2>
              <div className="record-summary">
                <div className="athlete1-wins">
                  <span className="wins">{h2hHistory.athlete1_wins}</span>
                  <span className="label">Wins</span>
                  <span className="name">{athlete1.name}</span>
                </div>
                
                <div className="race-count">
                  <span className="total">{h2hHistory.total_races}</span>
                  <span className="label">Common Races</span>
                </div>
                
                <div className="athlete2-wins">
                  <span className="wins">{h2hHistory.athlete2_wins}</span>
                  <span className="label">Wins</span>
                  <span className="name">{athlete2.name}</span>
                </div>
              </div>

              {h2hHistory.recent_form && (
                <div className="recent-h2h">
                  <h3>Last 5 Head-to-Head</h3>
                  <div className="recent-races">
                    {h2hHistory.recent_form.map((race, i) => (
                      <div key={i} className="h2h-race">
                        <span className="location">{race.location}</span>
                        <span className={`winner ${race.winner === athlete1.id ? 'athlete1' : 'athlete2'}`}>
                          {race.winner === athlete1.id ? athlete1.name : athlete2.name} won
                        </span>
                        <span className="margin">by {race.margin} positions</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Performance Comparison */}
          <div className="performance-comparison">
            <h2>Performance Metrics</h2>
            
            <div className="comparison-table">
              <div className="comparison-row header">
                <div className="athlete1-name">{athlete1.name}</div>
                <div className="metric-name">Metric</div>
                <div className="athlete2-name">{athlete2.name}</div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.avg_rank, comparison.athlete2.avg_rank, true)}`}>
                  {comparison.athlete1.avg_rank?.toFixed(1)}
                </div>
                <div className="metric-name">Average Rank</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.avg_rank, comparison.athlete1.avg_rank, true)}`}>
                  {comparison.athlete2.avg_rank?.toFixed(1)}
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.best_rank, comparison.athlete2.best_rank, true)}`}>
                  {comparison.athlete1.best_rank}
                </div>
                <div className="metric-name">Best Rank</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.best_rank, comparison.athlete1.best_rank, true)}`}>
                  {comparison.athlete2.best_rank}
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.shooting?.total_accuracy, comparison.athlete2.shooting?.total_accuracy)}`}>
                  {comparison.athlete1.shooting?.total_accuracy?.toFixed(1)}%
                </div>
                <div className="metric-name">Shooting Accuracy</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.shooting?.total_accuracy, comparison.athlete1.shooting?.total_accuracy)}`}>
                  {comparison.athlete2.shooting?.total_accuracy?.toFixed(1)}%
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.shooting?.prone_accuracy, comparison.athlete2.shooting?.prone_accuracy)}`}>
                  {comparison.athlete1.shooting?.prone_accuracy?.toFixed(1)}%
                </div>
                <div className="metric-name">Prone Shooting</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.shooting?.prone_accuracy, comparison.athlete1.shooting?.prone_accuracy)}`}>
                  {comparison.athlete2.shooting?.prone_accuracy?.toFixed(1)}%
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.shooting?.standing_accuracy, comparison.athlete2.shooting?.standing_accuracy)}`}>
                  {comparison.athlete1.shooting?.standing_accuracy?.toFixed(1)}%
                </div>
                <div className="metric-name">Standing Shooting</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.shooting?.standing_accuracy, comparison.athlete1.shooting?.standing_accuracy)}`}>
                  {comparison.athlete2.shooting?.standing_accuracy?.toFixed(1)}%
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.consistency_score, comparison.athlete2.consistency_score)}`}>
                  {comparison.athlete1.consistency_score?.toFixed(0)}
                </div>
                <div className="metric-name">Consistency Score</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.consistency_score, comparison.athlete1.consistency_score)}`}>
                  {comparison.athlete2.consistency_score?.toFixed(0)}
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.points_total, comparison.athlete2.points_total)}`}>
                  {comparison.athlete1.points_total}
                </div>
                <div className="metric-name">World Cup Points</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.points_total, comparison.athlete1.points_total)}`}>
                  {comparison.athlete2.points_total}
                </div>
              </div>

              <div className="comparison-row">
                <div className={`value ${getComparisonClass(comparison.athlete1.recent_form, comparison.athlete2.recent_form)}`}>
                  {comparison.athlete1.recent_form > 0 ? '↑' : comparison.athlete1.recent_form < 0 ? '↓' : '→'}
                  {Math.abs(comparison.athlete1.recent_form).toFixed(1)}
                </div>
                <div className="metric-name">Recent Form</div>
                <div className={`value ${getComparisonClass(comparison.athlete2.recent_form, comparison.athlete1.recent_form)}`}>
                  {comparison.athlete2.recent_form > 0 ? '↑' : comparison.athlete2.recent_form < 0 ? '↓' : '→'}
                  {Math.abs(comparison.athlete2.recent_form).toFixed(1)}
                </div>
              </div>
            </div>
          </div>

          {/* Key Insights */}
          <div className="key-insights">
            <h2>Key Insights</h2>
            <div className="insights-grid">
              <div className="insight">
                <h3>Shooting Advantage</h3>
                <p>
                  {comparison.athlete1.shooting?.total_accuracy > comparison.athlete2.shooting?.total_accuracy
                    ? `${athlete1.name} has ${(comparison.athlete1.shooting.total_accuracy - comparison.athlete2.shooting.total_accuracy).toFixed(1)}% better shooting accuracy`
                    : `${athlete2.name} has ${(comparison.athlete2.shooting.total_accuracy - comparison.athlete1.shooting.total_accuracy).toFixed(1)}% better shooting accuracy`
                  }
                </p>
              </div>

              <div className="insight">
                <h3>Consistency</h3>
                <p>
                  {comparison.athlete1.consistency_score > comparison.athlete2.consistency_score
                    ? `${athlete1.name} is more consistent in race results`
                    : `${athlete2.name} is more consistent in race results`
                  }
                </p>
              </div>

              <div className="insight">
                <h3>Current Form</h3>
                <p>
                  {comparison.athlete1.recent_form > comparison.athlete2.recent_form
                    ? `${athlete1.name} is in better recent form`
                    : comparison.athlete2.recent_form > comparison.athlete1.recent_form
                    ? `${athlete2.name} is in better recent form`
                    : 'Both athletes showing similar form'
                  }
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default HeadToHead
