import React, { useState, useEffect } from 'react'
import './AICoach.css'

const AICoach = () => {
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [athletes, setAthletes] = useState([])
  const [trainingPlan, setTrainingPlan] = useState(null)
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [activeModule, setActiveModule] = useState('overview')

  useEffect(() => {
    fetchAthletes()
  }, [])

  const fetchAthletes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=10')
      const data = await response.json()
      setAthletes(data)
    } catch (err) {
      console.error('Error fetching athletes:', err)
    }
  }

  const generateTrainingPlan = async (athlete) => {
    // Simulace AI analýzy
    setAiAnalysis({
      strengths: ['Prone shooting', 'Sprint performance', 'Mental toughness'],
      weaknesses: ['Standing shooting', 'Mass start positioning', 'Altitude adaptation'],
      recommendations: [
        {
          priority: 'high',
          area: 'Standing Shooting',
          description: 'Increase dry-fire training to 45 min/day',
          expectedImprovement: '+12% accuracy in 4 weeks'
        },
        {
          priority: 'medium',
          area: 'Interval Training',
          description: 'Add 2x weekly high-intensity intervals',
          expectedImprovement: '-30s on 10km time'
        },
        {
          priority: 'low',
          area: 'Recovery',
          description: 'Implement yoga sessions 2x/week',
          expectedImprovement: 'Injury prevention'
        }
      ]
    })

    // Generuj týdenní plán
    setTrainingPlan({
      week: 'January 8-14, 2025',
      focus: 'Pre-competition preparation',
      sessions: [
        {
          day: 'Monday',
          morning: 'Easy ski 90min Z1-Z2',
          afternoon: 'Shooting technique 60min',
          evening: 'Stretching + recovery'
        },
        {
          day: 'Tuesday',
          morning: 'Intervals 5x4min Z4',
          afternoon: 'Gym - upper body',
          evening: 'Massage'
        },
        {
          day: 'Wednesday',
          morning: 'Shooting + ski combo 120min',
          afternoon: 'Rest',
          evening: 'Video analysis'
        },
        {
          day: 'Thursday',
          morning: 'Tempo ski 60min Z3',
          afternoon: 'Core + stability',
          evening: 'Mental training'
        },
        {
          day: 'Friday',
          morning: 'Race simulation',
          afternoon: 'Recovery ski 45min',
          evening: 'Equipment prep'
        },
        {
          day: 'Saturday',
          morning: 'Competition',
          afternoon: 'Cool down',
          evening: 'Analysis'
        },
        {
          day: 'Sunday',
          morning: 'Recovery activities',
          afternoon: 'Rest',
          evening: 'Planning'
        }
      ]
    })
  }

  return (
    <div className="aicoach-page">
      {/* Header */}
      <div className="coach-header">
        <div className="header-content">
          <h1>AI Training Coach</h1>
          <p>Personalized training optimization powered by performance data</p>
        </div>
        <div className="ai-status">
          <span className="status-indicator active"></span>
          AI System Active
        </div>
      </div>

      {/* Athlete Selector */}
      <div className="athlete-selector">
        <h2>Select Athlete</h2>
        <div className="athlete-cards">
          {athletes.map(athlete => (
            <div 
              key={athlete.id}
              className={`athlete-select-card ${selectedAthlete?.id === athlete.id ? 'selected' : ''}`}
              onClick={() => {
                setSelectedAthlete(athlete)
                generateTrainingPlan(athlete)
              }}
            >
              <h3>{athlete.name}</h3>
              <div className="athlete-quick-stats">
                <span>Rank #{athlete.world_rank}</span>
                <span>{athlete.world_cup_points} pts</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedAthlete && (
        <>
          {/* Module Tabs */}
          <div className="module-tabs">
            <button 
              className={activeModule === 'overview' ? 'active' : ''}
              onClick={() => setActiveModule('overview')}
            >
              Overview
            </button>
            <button 
              className={activeModule === 'training' ? 'active' : ''}
              onClick={() => setActiveModule('training')}
            >
              Training Plan
            </button>
            <button 
              className={activeModule === 'analysis' ? 'active' : ''}
              onClick={() => setActiveModule('analysis')}
            >
              AI Analysis
            </button>
            <button 
              className={activeModule === 'nutrition' ? 'active' : ''}
              onClick={() => setActiveModule('nutrition')}
            >
              Nutrition
            </button>
            <button 
              className={activeModule === 'mental' ? 'active' : ''}
              onClick={() => setActiveModule('mental')}
            >
              Mental Training
            </button>
          </div>

          {/* Content */}
          <div className="coach-content">
            {activeModule === 'overview' && (
              <div className="overview-module">
                <div className="overview-grid">
                  {/* Current Status */}
                  <div className="status-card">
                    <h3>Current Status</h3>
                    <div className="status-metrics">
                      <div className="metric">
                        <span className="label">Form Index</span>
                        <span className="value good">8.2/10</span>
                      </div>
                      <div className="metric">
                        <span className="label">Fatigue Level</span>
                        <span className="value medium">5.1/10</span>
                      </div>
                      <div className="metric">
                        <span className="label">Injury Risk</span>
                        <span className="value good">Low</span>
                      </div>
                      <div className="metric">
                        <span className="label">Peak Performance</span>
                        <span className="value">In 2 weeks</span>
                      </div>
                    </div>
                  </div>

                  {/* Next Competition */}
                  <div className="competition-card">
                    <h3>Next Competition</h3>
                    <div className="competition-info">
                      <h4>World Cup Oberhof</h4>
                      <p>Sprint 7.5km • January 11, 2025</p>
                      <div className="preparation-status">
                        <div className="prep-item">
                          <span>Physical: </span>
                          <div className="progress-bar">
                            <div className="progress" style={{width: '85%'}}></div>
                          </div>
                        </div>
                        <div className="prep-item">
                          <span>Technical: </span>
                          <div className="progress-bar">
                            <div className="progress" style={{width: '72%'}}></div>
                          </div>
                        </div>
                        <div className="prep-item">
                          <span>Mental: </span>
                          <div className="progress-bar">
                            <div className="progress" style={{width: '90%'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Recommendations */}
                  {aiAnalysis && (
                    <div className="recommendations-card">
                      <h3>Today's Focus</h3>
                      <div className="recommendations-list">
                        {aiAnalysis.recommendations.slice(0, 2).map((rec, i) => (
                          <div key={i} className={`recommendation priority-${rec.priority}`}>
                            <h4>{rec.area}</h4>
                            <p>{rec.description}</p>
                            <span className="impact">{rec.expectedImprovement}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeModule === 'training' && trainingPlan && (
              <div className="training-module">
                <div className="training-header">
                  <h3>Weekly Training Plan</h3>
                  <p>{trainingPlan.week} • Focus: {trainingPlan.focus}</p>
                </div>
                
                <div className="training-calendar">
                  {trainingPlan.sessions.map((session, i) => (
                    <div key={i} className="training-day">
                      <h4>{session.day}</h4>
                      <div className="sessions">
                        <div className="session morning">
                          <span className="time">Morning</span>
                          <p>{session.morning}</p>
                        </div>
                        {session.afternoon !== 'Rest' && (
                          <div className="session afternoon">
                            <span className="time">Afternoon</span>
                            <p>{session.afternoon}</p>
                          </div>
                        )}
                        <div className="session evening">
                          <span className="time">Evening</span>
                          <p>{session.evening}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="training-notes">
                  <h4>Coach Notes</h4>
                  <ul>
                    <li>Focus on standing shooting stability this week</li>
                    <li>Maintain aerobic base with Z1-Z2 sessions</li>
                    <li>Taper intensity 2 days before competition</li>
                    <li>Hydration critical in cold conditions</li>
                  </ul>
                </div>
              </div>
            )}

            {activeModule === 'analysis' && aiAnalysis && (
              <div className="analysis-module">
                <div className="analysis-grid">
                  <div className="strengths-card">
                    <h3>Strengths</h3>
                    <ul>
                      {aiAnalysis.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="weaknesses-card">
                    <h3>Areas to Improve</h3>
                    <ul>
                      {aiAnalysis.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="detailed-recommendations">
                  <h3>Detailed Recommendations</h3>
                  {aiAnalysis.recommendations.map((rec, i) => (
                    <div key={i} className={`detailed-rec priority-${rec.priority}`}>
                      <div className="rec-header">
                        <h4>{rec.area}</h4>
                        <span className={`priority ${rec.priority}`}>{rec.priority} priority</span>
                      </div>
                      <p>{rec.description}</p>
                      <div className="rec-footer">
                        <span className="impact">Expected: {rec.expectedImprovement}</span>
                        <button className="implement-btn">Implement →</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeModule === 'nutrition' && (
              <div className="nutrition-module">
                <h3>Nutrition Plan</h3>
                <div className="nutrition-grid">
                  <div className="meal-plan">
                    <h4>Competition Day -1</h4>
                    <div className="meals">
                      <div className="meal">
                        <span className="meal-time">Breakfast (7:00)</span>
                        <p>Oatmeal with berries, 2 eggs, whole grain toast</p>
                        <span className="calories">650 kcal</span>
                      </div>
                      <div className="meal">
                        <span className="meal-time">Lunch (12:30)</span>
                        <p>Chicken breast, quinoa, mixed vegetables</p>
                        <span className="calories">720 kcal</span>
                      </div>
                      <div className="meal">
                        <span className="meal-time">Dinner (18:30)</span>
                        <p>Salmon, sweet potato, salad</p>
                        <span className="calories">680 kcal</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="hydration-plan">
                    <h4>Hydration Strategy</h4>
                    <ul>
                      <li>3.5L total fluid intake</li>
                      <li>Electrolyte drink during training</li>
                      <li>500ml 2h before competition</li>
                      <li>150ml every 20min during race</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeModule === 'mental' && (
              <div className="mental-module">
                <h3>Mental Training</h3>
                <div className="mental-exercises">
                  <div className="exercise-card">
                    <h4>Visualization</h4>
                    <p>10 minutes daily - visualize perfect shooting sequence</p>
                    <button className="start-exercise">Start Session</button>
                  </div>
                  <div className="exercise-card">
                    <h4>Breathing Techniques</h4>
                    <p>4-7-8 breathing pattern for pre-race anxiety</p>
                    <button className="start-exercise">Practice Now</button>
                  </div>
                  <div className="exercise-card">
                    <h4>Focus Training</h4>
                    <p>Attention control exercises for shooting</p>
                    <button className="start-exercise">Begin Training</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default AICoach
