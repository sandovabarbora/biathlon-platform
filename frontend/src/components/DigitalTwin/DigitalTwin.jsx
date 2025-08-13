import React, { useState, useEffect } from 'react'
import { LineChart, Line, RadarChart, Radar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts'
import './DigitalTwin.css'

const DigitalTwin = ({ athleteId, athleteName }) => {
  const [twin, setTwin] = useState(null)
  const [simulation, setSimulation] = useState(null)
  const [scenarios, setScenarios] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (athleteId) {
      createOrLoadTwin()
    }
  }, [athleteId])

  const createOrLoadTwin = async () => {
    setLoading(true)
    try {
      // Check if twin exists
      const statusRes = await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/status`)
      const status = await statusRes.json()
      
      if (!status.exists) {
        // Create new twin
        await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/create`, {
          method: 'POST'
        })
      }
      
      // Load twin data
      const twinRes = await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/status`)
      const twinData = await twinRes.json()
      setTwin(twinData)
      
    } catch (error) {
      console.error('Error loading digital twin:', error)
    } finally {
      setLoading(false)
    }
  }

  const runSimulation = async (raceType = 'sprint') => {
    setLoading(true)
    try {
      const raceParams = {
        type: raceType,
        distance: raceType === 'sprint' ? 7.5 : 10,
        laps: raceType === 'sprint' ? 3 : 4,
        temperature: -5,
        altitude: 500,
        wind_speed: 2,
        snow: 'hard'
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(raceParams)
      })
      
      const result = await response.json()
      setSimulation(result)
      
    } catch (error) {
      console.error('Error running simulation:', error)
    } finally {
      setLoading(false)
    }
  }

  const runWhatIfScenarios = async () => {
    setLoading(true)
    try {
      const scenarioList = [
        {
          name: 'Perfect Shooting',
          modifications: { shooting_technique: 1.0 }
        },
        {
          name: '+5% VO2 Max',
          modifications: { vo2_max: '+5percent' }
        },
        {
          name: 'Better Recovery',
          modifications: { hr_recovery_rate: 1.8 }
        },
        {
          name: 'Mental Training',
          modifications: { pressure_resistance: 0.95 }
        }
      ]
      
      const response = await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/batch-scenarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenarioList)
      })
      
      const results = await response.json()
      setScenarios(results.results)
      
    } catch (error) {
      console.error('Error running scenarios:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="twin-loading">
        <div className="loading-spinner"></div>
        <p>Loading Digital Twin...</p>
      </div>
    )
  }

  if (!twin || !twin.exists) {
    return (
      <div className="twin-empty">
        <p>No digital twin available</p>
        <button onClick={createOrLoadTwin}>Create Digital Twin</button>
      </div>
    )
  }

  // Prepare data for radar chart
  const physiologyData = [
    { metric: 'VO2 Max', value: twin.parameters.vo2_max, max: 75 },
    { metric: 'Lactate Threshold', value: twin.parameters.lactate_threshold * 100, max: 100 },
    { metric: 'Ski Efficiency', value: twin.parameters.ski_efficiency * 100, max: 100 },
    { metric: 'Shooting', value: twin.parameters.shooting_technique * 100, max: 100 },
    { metric: 'HR Max', value: (twin.parameters.hr_max / 200) * 100, max: 100 }
  ]

  return (
    <div className="digital-twin">
      <div className="twin-header">
        <h2>Digital Twin: {athleteName}</h2>
        <div className="twin-tabs">
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            OVERVIEW
          </button>
          <button 
            className={activeTab === 'simulation' ? 'active' : ''}
            onClick={() => setActiveTab('simulation')}
          >
            RACE SIMULATION
          </button>
          <button 
            className={activeTab === 'whatif' ? 'active' : ''}
            onClick={() => setActiveTab('whatif')}
          >
            WHAT-IF ANALYSIS
          </button>
          <button 
            className={activeTab === 'training' ? 'active' : ''}
            onClick={() => setActiveTab('training')}
          >
            OPTIMAL TRAINING
          </button>
        </div>
      </div>

      {activeTab === 'overview' && (
        <div className="twin-overview">
          <div className="physiology-chart">
            <h3>Physiological Profile</h3>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={physiologyData}>
                <PolarGrid stroke="#333" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#999' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#666' }} />
                <Radar
                  name="Current"
                  dataKey="value"
                  stroke="#00ff88"
                  fill="#00ff88"
                  fillOpacity={0.3}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="parameters-grid">
            <div className="param-card">
              <h4>Aerobic Capacity</h4>
              <div className="param-value">{twin.parameters.vo2_max.toFixed(1)}</div>
              <div className="param-label">ml/kg/min</div>
            </div>
            <div className="param-card">
              <h4>Max Heart Rate</h4>
              <div className="param-value">{twin.parameters.hr_max}</div>
              <div className="param-label">BPM</div>
            </div>
            <div className="param-card">
              <h4>Ski Efficiency</h4>
              <div className="param-value">{(twin.parameters.ski_efficiency * 100).toFixed(0)}%</div>
              <div className="param-label">Technical Score</div>
            </div>
            <div className="param-card">
              <h4>Shooting Technique</h4>
              <div className="param-value">{(twin.parameters.shooting_technique * 100).toFixed(0)}%</div>
              <div className="param-label">Accuracy Score</div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'simulation' && (
        <div className="race-simulation">
          <div className="sim-controls">
            <h3>Race Simulation</h3>
            <div className="race-buttons">
              <button onClick={() => runSimulation('sprint')}>Simulate Sprint</button>
              <button onClick={() => runSimulation('pursuit')}>Simulate Pursuit</button>
              <button onClick={() => runSimulation('individual')}>Simulate Individual</button>
            </div>
          </div>
          
          {simulation && (
            <div className="sim-results">
              <div className="result-cards">
                <div className="result-card">
                  <h4>Total Time</h4>
                  <div className="result-value">
                    {Math.floor(simulation.total_time / 60)}:{(simulation.total_time % 60).toFixed(0).padStart(2, '0')}
                  </div>
                </div>
                <div className="result-card">
                  <h4>Shooting</h4>
                  <div className="result-value">{simulation.total_misses} misses</div>
                </div>
                <div className="result-card">
                  <h4>Estimated Position</h4>
                  <div className="result-value">#{simulation.final_position}</div>
                </div>
                <div className="result-card">
                  <h4>Max HR</h4>
                  <div className="result-value">{simulation.max_hr} BPM</div>
                </div>
              </div>
              
              {simulation.segments && (
                <div className="race-timeline">
                  <h4>Race Timeline</h4>
                  <div className="timeline-segments">
                    {simulation.segments.map((segment, i) => (
                      <div key={i} className={`segment ${segment.type}`}>
                        <span className="segment-type">{segment.type}</span>
                        <span className="segment-time">{segment.time.toFixed(1)}s</span>
                        {segment.type === 'shooting' && (
                          <span className="segment-detail">
                            {segment.hits}/5 hits
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'whatif' && (
        <div className="whatif-analysis">
          <div className="whatif-controls">
            <h3>What-If Scenarios</h3>
            <button onClick={runWhatIfScenarios}>Run All Scenarios</button>
          </div>
          
          {scenarios.length > 0 && (
            <div className="scenarios-grid">
              {scenarios.map((scenario, i) => (
                <div key={i} className="scenario-card">
                  <h4>{scenario.scenario}</h4>
                  {scenario.result && (
                    <>
                      <div className="scenario-metric">
                        <span>Time Saved</span>
                        <span className="value positive">
                          {scenario.result.time_saved.toFixed(1)}s
                        </span>
                      </div>
                      <div className="scenario-metric">
                        <span>Positions Gained</span>
                        <span className="value positive">
                          +{scenario.result.positions_gained}
                        </span>
                      </div>
                      <div className="scenario-metric">
                        <span>Shooting Improvement</span>
                        <span className="value">
                          -{scenario.result.shooting_improvement} misses
                        </span>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'training' && (
        <div className="training-optimization">
          <h3>Optimal Training Plan</h3>
          <button onClick={async () => {
            const response = await fetch(`http://localhost:8000/api/v1/digital-twin/${athleteId}/optimize-training`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ weeks: 8, goal: 'performance' })
            })
            const plan = await response.json()
            console.log('Training plan:', plan)
          }}>
            Generate 8-Week Plan
          </button>
          
          <div className="training-preview">
            <p>AI-optimized training plan based on digital twin analysis</p>
            <ul>
              <li>Focus on weakest areas first</li>
              <li>Progressive overload principle</li>
              <li>Recovery optimization</li>
              <li>Mental training integration</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default DigitalTwin
