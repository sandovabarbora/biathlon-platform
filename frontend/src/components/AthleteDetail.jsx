import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

const API_URL = 'http://localhost:8000'

const AthleteDetail = ({ athleteName, athletes, onChangeAthlete }) => {
    const [athleteData, setAthleteData] = useState(null)
    const [training, setTraining] = useState([])
    const [trends, setTrends] = useState(null)
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('overview')

    useEffect(() => {
        if (athleteName) {
            loadAthleteData()
        }
    }, [athleteName])

    const loadAthleteData = async () => {
        setLoading(true)
        try {
            const [statsRes, trainingRes, trendsRes] = await Promise.all([
                axios.get(`${API_URL}/api/athlete/${athleteName}`),
                axios.get(`${API_URL}/api/athlete/${athleteName}/training`),
                axios.get(`${API_URL}/api/athlete/${athleteName}/trends?period=last10`)
            ])
            
            setAthleteData(statsRes.data)
            setTraining(trainingRes.data)
            setTrends(trendsRes.data)
        } catch (error) {
            console.error('Error loading athlete data:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Načítám data závodníka...</p>
            </div>
        )
    }

    if (!athleteData) {
        return <div className="alert alert-warning">Závodník nenalezen</div>
    }

    // Prepare radar chart data
    const radarData = [
        { metric: 'Střelba', value: athleteData.shooting_accuracy, max: 100 },
        { metric: 'Vleže', value: athleteData.prone_accuracy, max: 100 },
        { metric: 'Vstoje', value: athleteData.standing_accuracy, max: 100 },
        { metric: 'Rychlost', value: athleteData.ski_speed_index || 100, max: 120 },
        { metric: 'Konzistence', value: 100 - athleteData.consistency_score * 2, max: 100 },
        { metric: 'Top 10', value: athleteData.top10_rate, max: 100 }
    ]

    return (
        <div className="athlete-detail">
            {/* Athlete Header */}
            <div className="athlete-header">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <select 
                            className="form-select form-input"
                            value={athleteName}
                            onChange={(e) => onChangeAthlete(e.target.value)}
                        >
                            {athletes.map(a => (
                                <option key={a.name} value={a.name}>
                                    {a.name} ({a.nation})
                                </option>
                            ))}
                        </select>
                        
                        <div className="flex gap-2">
                            <span className="badge badge-primary">#{athleteData.avg_rank.toFixed(0)} průměr</span>
                            <span className="badge badge-gray">{athleteData.total_races} závodů</span>
                        </div>
                    </div>
                    
                    <div className="flex gap-2">
                        <button className="btn btn-secondary">
                            📊 Export
                        </button>
                        <button className="btn btn-primary">
                            📧 Poslat report
                        </button>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
                <button 
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Přehled
                </button>
                <button 
                    className={`tab ${activeTab === 'training' ? 'active' : ''}`}
                    onClick={() => setActiveTab('training')}
                >
                    Tréninkový plán
                </button>
                <button 
                    className={`tab ${activeTab === 'detailed' ? 'active' : ''}`}
                    onClick={() => setActiveTab('detailed')}
                >
                    Detailní analýza
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div>
                    {/* Key Metrics */}
                    <div className="grid grid-cols-4 mb-4">
                        <div className="stat-card">
                            <div className="stat-label">Nejlepší umístění</div>
                            <div className="stat-value">#{athleteData.best_rank}</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-label">Průměr / Medián</div>
                            <div className="stat-value">
                                {athleteData.avg_rank.toFixed(1)} / {athleteData.median_rank.toFixed(1)}
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-label">Pódia</div>
                            <div className="stat-value">{athleteData.top3_rate.toFixed(1)}%</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-label">Body/závod</div>
                            <div className="stat-value">{athleteData.points_per_race.toFixed(1)}</div>
                        </div>
                    </div>

                    {/* Performance Profile */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="card">
                            <h3 className="card-title mb-3">Výkonnostní profil</h3>
                            <ResponsiveContainer width="100%" height={350}>
                                <RadarChart data={radarData}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="metric" />
                                    <PolarRadiusAxis domain={[0, 100]} />
                                    <Radar 
                                        name="Výkon" 
                                        dataKey="value" 
                                        stroke="#2563eb" 
                                        fill="#2563eb" 
                                        fillOpacity={0.3} 
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="card">
                            <h3 className="card-title mb-3">Střelecká analýza</h3>
                            
                            <div className="shooting-stats">
                                <div className="shooting-row">
                                    <span className="label">Celková přesnost:</span>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill"
                                            style={{ width: `${athleteData.shooting_accuracy}%` }}
                                        />
                                        <span className="progress-text">{athleteData.shooting_accuracy.toFixed(1)}%</span>
                                    </div>
                                </div>
                                
                                <div className="shooting-row">
                                    <span className="label">Vleže:</span>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill success"
                                            style={{ width: `${athleteData.prone_accuracy}%` }}
                                        />
                                        <span className="progress-text">{athleteData.prone_accuracy.toFixed(1)}%</span>
                                    </div>
                                </div>
                                
                                <div className="shooting-row">
                                    <span className="label">Vstoje:</span>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill warning"
                                            style={{ width: `${athleteData.standing_accuracy}%` }}
                                        />
                                        <span className="progress-text">{athleteData.standing_accuracy.toFixed(1)}%</span>
                                    </div>
                                </div>

                                <div className="alert alert-info mt-3">
                                    <strong>Doporučení:</strong> Rozdíl mezi střelbou vleže a vstoje je {Math.abs(athleteData.prone_accuracy - athleteData.standing_accuracy).toFixed(1)}%. 
                                    {athleteData.standing_accuracy < athleteData.prone_accuracy - 10 && 
                                        " Zaměřte se na stabilizaci při střelbě vstoje."}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Trend Analysis */}
                    {trends && (
                        <div className="card mt-4">
                            <h3 className="card-title mb-3">Trend posledních 10 závodů</h3>
                            <div className={`alert alert-${trends.direction === 'IMPROVING' ? 'success' : trends.direction === 'DECLINING' ? 'danger' : 'info'}`}>
                                <strong>Směr vývoje:</strong> {
                                    trends.direction === 'IMPROVING' ? '📈 Zlepšování' :
                                    trends.direction === 'DECLINING' ? '📉 Zhoršování' :
                                    '➡️ Stabilní'
                                } ({trends.confidence_level.toFixed(0)}% jistota)
                            </div>
                            
                            {trends.key_factors.length > 0 && (
                                <div className="mt-3">
                                    <strong>Klíčové faktory:</strong>
                                    <ul className="mt-2">
                                        {trends.key_factors.map((factor, i) => (
                                            <li key={i}>{factor}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'training' && (
                <div>
                    <h3 className="mb-3">Tréninkový plán a doporučení</h3>
                    
                    {training.map((rec, i) => (
                        <div key={i} className="card mb-3">
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <span className={`badge badge-${
                                        rec.priority === 'HIGH' ? 'danger' :
                                        rec.priority === 'MEDIUM' ? 'warning' : 'gray'
                                    }`}>
                                        {rec.priority === 'HIGH' ? 'Vysoká' :
                                         rec.priority === 'MEDIUM' ? 'Střední' : 'Nízká'} priorita
                                    </span>
                                    <span className="badge badge-primary">{rec.area}</span>
                                </div>
                                <span className="text-sm text-gray">Časový rámec: {rec.time_frame}</span>
                            </div>
                            
                            <h4 className="font-semibold mb-2">{rec.specific_focus}</h4>
                            <p className="mb-3">{rec.recommendation}</p>
                            
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <strong className="text-sm">Cvičení:</strong>
                                    <ul className="mt-1">
                                        {rec.exercises.map((ex, j) => (
                                            <li key={j} className="text-sm">• {ex}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div>
                                    <strong className="text-sm">Metriky k sledování:</strong>
                                    <ul className="mt-1">
                                        {rec.metrics_to_track.map((metric, j) => (
                                            <li key={j} className="text-sm">• {metric}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                            
                            <div className="mt-3 pt-3 border-top">
                                <span className="text-sm text-primary">
                                    <strong>Očekávaný dopad:</strong> {rec.expected_impact}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {activeTab === 'detailed' && (
                <div>
                    <h3 className="mb-3">Detailní statistiky</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                        <div className="card">
                            <h4 className="font-semibold mb-3">Výkonnostní metriky</h4>
                            <table className="table">
                                <tbody>
                                    <tr>
                                        <td>DNF rate</td>
                                        <td className="text-right font-semibold">{athleteData.dnf_rate.toFixed(1)}%</td>
                                    </tr>
                                    <tr>
                                        <td>Konzistence (std dev)</td>
                                        <td className="text-right font-semibold">{athleteData.consistency_score.toFixed(1)}</td>
                                    </tr>
                                    <tr>
                                        <td>Trend (poslední vs průměr)</td>
                                        <td className="text-right font-semibold">
                                            {athleteData.improvement_trend > 0 ? '+' : ''}{athleteData.improvement_trend.toFixed(1)}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Index rychlosti lyží</td>
                                        <td className="text-right font-semibold">
                                            {athleteData.ski_speed_index?.toFixed(1) || 'N/A'}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div className="card">
                            <h4 className="font-semibold mb-3">Srovnání s průměrem</h4>
                            <div className="comparison-chart">
                                {/* Add comparison visualization here */}
                                <p className="text-gray">Grafické srovnání s týmovým průměrem</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <style jsx>{`
                .athlete-header {
                    margin-bottom: 24px;
                }

                .shooting-stats {
                    padding: 16px 0;
                }

                .shooting-row {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 16px;
                }

                .shooting-row .label {
                    width: 80px;
                    font-weight: 500;
                }

                .progress-bar {
                    flex: 1;
                    height: 24px;
                    background: #f3f4f6;
                    border-radius: 12px;
                    position: relative;
                    overflow: hidden;
                }

                .progress-fill {
                    position: absolute;
                    left: 0;
                    top: 0;
                    height: 100%;
                    background: #2563eb;
                    border-radius: 12px;
                    transition: width 0.5s ease;
                }

                .progress-fill.success {
                    background: #10b981;
                }

                .progress-fill.warning {
                    background: #f59e0b;
                }

                .progress-text {
                    position: absolute;
                    right: 8px;
                    top: 50%;
                    transform: translateY(-50%);
                    font-size: 0.75rem;
                    font-weight: 600;
                }

                .border-top {
                    border-top: 1px solid #e5e7eb;
                }
            `}</style>
        </div>
    )
}

export default AthleteDetail
