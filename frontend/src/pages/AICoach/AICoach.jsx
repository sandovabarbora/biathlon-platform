import React, { useState, useEffect } from 'react'
import './AICoach.css'

const AICoach = () => {
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [athletes, setAthletes] = useState([])
  const [activeModule, setActiveModule] = useState('overview')
  const [trainingPlan, setTrainingPlan] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAthletes()
  }, [])

  const fetchAthletes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/athletes?nation=CZE&limit=10')
      const data = await response.json()
      setAthletes(data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching athletes:', err)
      setLoading(false)
    }
  }

  const generateTrainingPlan = (athlete) => {
    // AI-generated training plan
    setTrainingPlan({
      week: 'WEEK 3 - JANUARY 2025',
      focus: 'PRE-COMPETITION PREPARATION',
      loadIndex: 72,
      sessions: [
        {
          day: 'MONDAY',
          morning: { type: 'SKI', intensity: 'Z2', duration: '90min', description: 'Easy distance ski' },
          afternoon: { type: 'SHOOTING', intensity: 'TECH', duration: '60min', description: 'Standing position focus' },
          recovery: 'Stretching + Massage'
        },
        {
          day: 'TUESDAY',
          morning: { type: 'INTERVALS', intensity: 'Z4', duration: '75min', description: '5x4min intervals' },
          afternoon: { type: 'GYM', intensity: 'STRENGTH', duration: '45min', description: 'Upper body power' },
          recovery: 'Ice bath'
        },
        {
          day: 'WEDNESDAY',
          morning: { type: 'COMBO', intensity: 'Z3', duration: '120min', description: 'Ski + Shooting combo' },
          afternoon: { type: 'REST', intensity: '-', duration: '-', description: 'Complete rest' },
          recovery: 'Yoga session'
        },
        {
          day: 'THURSDAY',
          morning: { type: 'SKI', intensity: 'Z3', duration: '60min', description: 'Tempo skiing' },
          afternoon: { type: 'CORE', intensity: 'MOD', duration: '30min', description: 'Stability work' },
          recovery: 'Foam rolling'
        },
        {
          day: 'FRIDAY',
          morning: { type: 'SIMULATION', intensity: 'RACE', duration: '90min', description: 'Race simulation' },
          afternoon: { type: 'RECOVERY', intensity: 'Z1', duration: '30min', description: 'Easy recovery' },
          recovery: 'Mental prep'
        },
        {
          day: 'SATURDAY',
          morning: { type: 'COMPETITION', intensity: 'MAX', duration: 'RACE', description: 'Sprint 7.5km' },
          afternoon: { type: 'COOLDOWN', intensity: 'Z1', duration: '20min', description: 'Cool down' },
          recovery: 'Analysis'
        },
        {
          day: 'SUNDAY',
          morning: { type: 'RECOVERY', intensity: 'Z1', duration: '45min', description: 'Active recovery' },
          afternoon: { type: 'REST', intensity: '-', duration: '-', description: 'Rest' },
          recovery: 'Planning'
        }
      ]
    })
  }

  const aiAnalysis = {
    strengths: ['Prone shooting accuracy', 'Mental toughness', 'Sprint performance'],
    weaknesses: ['Standing stability', 'Altitude adaptation', 'Mass start positioning'],
    recommendations: [
      {
        priority: 'HIGH',
        area: 'Standing Shooting',
        action: 'Increase dry-fire training to 45 min/day',
        impact: '+12% accuracy potential'
      },
      {
        priority: 'MEDIUM',
        area: 'Interval Training',
        action: 'Add 2x weekly high-intensity intervals',
        impact: '-30s on 10km time'
      },
      {
        priority: 'LOW',
        area: 'Recovery',
        action: 'Implement yoga sessions 2x/week',
        impact: 'Injury prevention'
      }
    ]
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading AI Coach...</p>
      </div>
    )
  }

  return (
    <div className="aicoach-page">
      <div className="container">
        {/* PAGE HEADER */}
        <div className="page-header">
          <h1 className="page-title">AI TRAINING COACH</h1>
          <div className="header-actions">
            <div className="ai-status">
              <span className="status-dot active"></span>
              AI SYSTEM ACTIVE
            </div>
            <button className="btn btn-primary">GENERATE REPORT</button>
          </div>
        </div>

        {/* ATHLETE SELECTOR */}
        <div className="athlete-selector">
          <h2 className="selector-title">SELECT ATHLETE FOR PERSONALIZED TRAINING</h2>
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
                <div className="athlete-rank">#{athlete.world_rank}</div>
                <div className="athlete-name">{athlete.name}</div>
                <div className="athlete-points">{athlete.world_cup_points} pts</div>
              </div>
            ))}
          </div>
        </div>

        {selectedAthlete && (
          <>
            {/* MODULE TABS */}
            <div className="module-tabs">
              <button 
                className={activeModule === 'overview' ? 'active' : ''}
                onClick={() => setActiveModule('overview')}
              >
                OVERVIEW
              </button>
              <button 
                className={activeModule === 'training' ? 'active' : ''}
                onClick={() => setActiveModule('training')}
              >
                TRAINING PLAN
              </button>
              <button 
                className={activeModule === 'analysis' ? 'active' : ''}
                onClick={() => setActiveModule('analysis')}
              >
                AI ANALYSIS
              </button>
              <button 
                className={activeModule === 'nutrition' ? 'active' : ''}
                onClick={() => setActiveModule('nutrition')}
              >
                NUTRITION
              </button>
              <button 
                className={activeModule === 'mental' ? 'active' : ''}
                onClick={() => setActiveModule('mental')}
              >
                MENTAL
              </button>
              <button 
                className={activeModule === 'recovery' ? 'active' : ''}
                onClick={() => setActiveModule('recovery')}
              >
                RECOVERY
              </button>
            </div>

            {/* CONTENT AREA */}
            <div className="coach-content">
              {activeModule === 'overview' && (
                <div className="overview-module">
                  <div className="overview-grid">
                    {/* Current Status */}
                    <div className="status-card">
                      <h3>CURRENT STATUS</h3>
                      <div className="status-metrics">
                        <div className="metric">
                          <span className="label">FORM INDEX</span>
                          <span className="value good">8.2/10</span>
                        </div>
                        <div className="metric">
                          <span className="label">FATIGUE LEVEL</span>
                          <span className="value medium">5.1/10</span>
                        </div>
                        <div className="metric">
                          <span className="label">INJURY RISK</span>
                          <span className="value good">LOW</span>
                        </div>
                        <div className="metric">
                          <span className="label">PEAK TIMING</span>
                          <span className="value">IN 2 WEEKS</span>
                        </div>
                      </div>
                    </div>

                    {/* Next Competition */}
                    <div className="competition-card">
                      <h3>NEXT COMPETITION</h3>
                      <div className="competition-info">
                        <h4>WORLD CUP RUHPOLDING</h4>
                        <p>Sprint 7.5km • January 15, 2025</p>
                        <div className="preparation-bars">
                          <div className="prep-item">
                            <span>PHYSICAL</span>
                            <div className="progress-bar">
                              <div className="progress" style={{width: '85%'}}></div>
                            </div>
                            <span className="percentage">85%</span>
                          </div>
                          <div className="prep-item">
                            <span>TECHNICAL</span>
                            <div className="progress-bar">
                              <div className="progress" style={{width: '72%'}}></div>
                            </div>
                            <span className="percentage">72%</span>
                          </div>
                          <div className="prep-item">
                            <span>MENTAL</span>
                            <div className="progress-bar">
                              <div className="progress" style={{width: '90%'}}></div>
                            </div>
                            <span className="percentage">90%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Today's Focus */}
                    <div className="focus-card">
                      <h3>TODAY'S FOCUS</h3>
                      <div className="focus-items">
                        <div className="focus-item priority-high">
                          <span className="time">09:00</span>
                          <span className="activity">Interval Training Z4</span>
                          <span className="duration">75min</span>
                        </div>
                        <div className="focus-item priority-medium">
                          <span className="time">15:00</span>
                          <span className="activity">Shooting Practice</span>
                          <span className="duration">60min</span>
                        </div>
                        <div className="focus-item priority-low">
                          <span className="time">19:00</span>
                          <span className="activity">Recovery Yoga</span>
                          <span className="duration">30min</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeModule === 'training' && trainingPlan && (
                <div className="training-module">
                  <div className="training-header">
                    <h3>{trainingPlan.week}</h3>
                    <p>Focus: {trainingPlan.focus}</p>
                    <div className="load-indicator">
                      <span>TRAINING LOAD</span>
                      <div className="load-bar">
                        <div className="load-fill" style={{width: `${trainingPlan.loadIndex}%`}}></div>
                      </div>
                      <span className="load-value">{trainingPlan.loadIndex}%</span>
                    </div>
                  </div>
                  
                  <div className="training-calendar">
                    {trainingPlan.sessions.map((session, i) => (
                      <div key={i} className="training-day">
                        <div className="day-header">
                          <h4>{session.day}</h4>
                        </div>
                        <div className="sessions">
                          <div className={`session morning ${session.morning.intensity}`}>
                            <span className="session-time">MORNING</span>
                            <span className="session-type">{session.morning.type}</span>
                            <span className="session-duration">{session.morning.duration}</span>
                            <p className="session-desc">{session.morning.description}</p>
                          </div>
                          {session.afternoon.type !== 'REST' && (
                            <div className={`session afternoon ${session.afternoon.intensity}`}>
                              <span className="session-time">AFTERNOON</span>
                              <span className="session-type">{session.afternoon.type}</span>
                              <span className="session-duration">{session.afternoon.duration}</span>
                              <p className="session-desc">{session.afternoon.description}</p>
                            </div>
                          )}
                          <div className="session recovery">
                            <span className="session-time">RECOVERY</span>
                            <p className="session-desc">{session.recovery}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="training-notes">
                    <h4>COACH NOTES</h4>
                    <ul>
                      <li>Focus on standing shooting stability this week</li>
                      <li>Maintain aerobic base with Z1-Z2 sessions</li>
                      <li>Taper intensity 2 days before competition</li>
                      <li>Hydration critical in cold conditions</li>
                    </ul>
                  </div>
                </div>
              )}

              {activeModule === 'analysis' && (
                <div className="analysis-module">
                  <div className="analysis-grid">
                    <div className="strengths-card">
                      <h3>STRENGTHS</h3>
                      <ul>
                        {aiAnalysis.strengths.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="weaknesses-card">
                      <h3>AREAS TO IMPROVE</h3>
                      <ul>
                        {aiAnalysis.weaknesses.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="recommendations">
                    <h3>AI RECOMMENDATIONS</h3>
                    {aiAnalysis.recommendations.map((rec, i) => (
                      <div key={i} className={`recommendation priority-${rec.priority.toLowerCase()}`}>
                        <div className="rec-header">
                          <span className="priority">{rec.priority} PRIORITY</span>
                          <span className="impact">{rec.impact}</span>
                        </div>
                        <h4>{rec.area}</h4>
                        <p>{rec.action}</p>
                        <button className="implement-btn">IMPLEMENT</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeModule === 'nutrition' && (
                <div className="nutrition-module">
                  <h3>NUTRITION PLAN</h3>
                  <div className="nutrition-grid">
                    <div className="meal-plan">
                      <h4>COMPETITION DAY -1</h4>
                      <div className="meals">
                        <div className="meal">
                          <span className="meal-time">07:00 BREAKFAST</span>
                          <p>Oatmeal with berries, 2 eggs, whole grain toast</p>
                          <span className="calories">650 kcal</span>
                        </div>
                        <div className="meal">
                          <span className="meal-time">10:00 SNACK</span>
                          <p>Banana, almond butter</p>
                          <span className="calories">220 kcal</span>
                        </div>
                        <div className="meal">
                          <span className="meal-time">12:30 LUNCH</span>
                          <p>Chicken breast, quinoa, mixed vegetables</p>
                          <span className="calories">720 kcal</span>
                        </div>
                        <div className="meal">
                          <span className="meal-time">15:30 SNACK</span>
                          <p>Protein shake, apple</p>
                          <span className="calories">280 kcal</span>
                        </div>
                        <div className="meal">
                          <span className="meal-time">18:30 DINNER</span>
                          <p>Salmon, sweet potato, salad</p>
                          <span className="calories">680 kcal</span>
                        </div>
                      </div>
                      <div className="total-nutrition">
                        <span>TOTAL: 2550 kcal</span>
                        <span>CARBS: 55%</span>
                        <span>PROTEIN: 25%</span>
                        <span>FAT: 20%</span>
                      </div>
                    </div>
                    
                    <div className="hydration-plan">
                      <h4>HYDRATION STRATEGY</h4>
                      <ul>
                        <li>3.5L total daily fluid intake</li>
                        <li>500ml upon waking</li>
                        <li>250ml every hour during training</li>
                        <li>Electrolyte drink during intervals</li>
                        <li>500ml 2h before competition</li>
                        <li>150ml every 20min during race</li>
                      </ul>
                      <div className="supplements">
                        <h4>SUPPLEMENTS</h4>
                        <ul>
                          <li>Vitamin D3 - 2000 IU</li>
                          <li>Omega-3 - 2g</li>
                          <li>Magnesium - 400mg</li>
                          <li>Iron - as prescribed</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeModule === 'mental' && (
                <div className="mental-module">
                  <h3>MENTAL TRAINING</h3>
                  <div className="mental-exercises">
                    <div className="exercise-card">
                      <h4>VISUALIZATION</h4>
                      <p>10 minutes daily - visualize perfect shooting sequence</p>
                      <div className="exercise-steps">
                        <ol>
                          <li>Find quiet space, close eyes</li>
                          <li>Visualize approaching shooting range</li>
                          <li>Feel the rifle, see the targets</li>
                          <li>Execute perfect 5 shots</li>
                          <li>Feel the success and confidence</li>
                        </ol>
                      </div>
                      <button className="start-btn">START SESSION</button>
                    </div>
                    
                    <div className="exercise-card">
                      <h4>BREATHING TECHNIQUES</h4>
                      <p>4-7-8 breathing pattern for pre-race anxiety</p>
                      <div className="breathing-guide">
                        <div className="breath-step">
                          <span className="count">4</span>
                          <span>INHALE</span>
                        </div>
                        <div className="breath-step">
                          <span className="count">7</span>
                          <span>HOLD</span>
                        </div>
                        <div className="breath-step">
                          <span className="count">8</span>
                          <span>EXHALE</span>
                        </div>
                      </div>
                      <button className="start-btn">PRACTICE NOW</button>
                    </div>
                    
                    <div className="exercise-card">
                      <h4>FOCUS TRAINING</h4>
                      <p>Attention control exercises for shooting</p>
                      <ul>
                        <li>Target fixation drills</li>
                        <li>Distraction management</li>
                        <li>Reset routines</li>
                        <li>Positive self-talk scripts</li>
                      </ul>
                      <button className="start-btn">BEGIN TRAINING</button>
                    </div>
                  </div>
                </div>
              )}

              {activeModule === 'recovery' && (
                <div className="recovery-module">
                  <h3>RECOVERY PROTOCOL</h3>
                  <div className="recovery-grid">
                    <div className="recovery-card">
                      <h4>TODAY'S RECOVERY STATUS</h4>
                      <div className="recovery-metrics">
                        <div className="metric">
                          <span className="label">HRV</span>
                          <span className="value">58ms</span>
                          <span className="status good">GOOD</span>
                        </div>
                        <div className="metric">
                          <span className="label">RESTING HR</span>
                          <span className="value">48bpm</span>
                          <span className="status good">OPTIMAL</span>
                        </div>
                        <div className="metric">
                          <span className="label">SLEEP QUALITY</span>
                          <span className="value">7.5h</span>
                          <span className="status medium">ADEQUATE</span>
                        </div>
                        <div className="metric">
                          <span className="label">MUSCLE SORENESS</span>
                          <span className="value">3/10</span>
                          <span className="status good">LOW</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="recovery-card">
                      <h4>RECOVERY ACTIVITIES</h4>
                      <div className="activities-schedule">
                        <div className="activity">
                          <span className="time">08:00</span>
                          <span className="type">Mobility Work</span>
                          <span className="duration">15min</span>
                        </div>
                        <div className="activity">
                          <span className="time">12:00</span>
                          <span className="type">Foam Rolling</span>
                          <span className="duration">20min</span>
                        </div>
                        <div className="activity">
                          <span className="time">16:00</span>
                          <span className="type">Ice Bath</span>
                          <span className="duration">10min</span>
                        </div>
                        <div className="activity">
                          <span className="time">20:00</span>
                          <span className="type">Stretching</span>
                          <span className="duration">30min</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default AICoach
