import React from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const Dashboard = ({ athletes, onSelectAthlete }) => {
    // Top performers
    const topAthletes = athletes.slice(0, 10)
    
    // Calculate team statistics
    const teamStats = {
        avgRank: athletes.reduce((sum, a) => sum + a.avg_rank, 0) / athletes.length || 0,
        avgShooting: athletes.reduce((sum, a) => sum + a.shooting_accuracy, 0) / athletes.length || 0,
        totalRaces: athletes.reduce((sum, a) => sum + a.total_races, 0),
        totalPodiums: athletes.reduce((sum, a) => sum + (a.top3_rate * a.races_finished / 100), 0)
    }

    // Prepare chart data
    const rankingData = topAthletes.map(a => ({
        name: a.name.split(' ').pop(), // Last name only
        rank: a.avg_rank,
        shooting: a.shooting_accuracy
    }))

    return (
        <div className="dashboard">
            <h2 className="mb-4">Týmový přehled - Česká republika</h2>
            
            {/* Team Stats */}
            <div className="grid grid-cols-4 mb-4">
                <div className="stat-card">
                    <div className="stat-label">Průměrné umístění</div>
                    <div className="stat-value">{teamStats.avgRank.toFixed(1)}</div>
                    <div className="stat-change positive">
                        ↑ 2.3 vs minulý měsíc
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Přesnost střelby</div>
                    <div className="stat-value">{teamStats.avgShooting.toFixed(1)}%</div>
                    <div className="stat-change negative">
                        ↓ 0.8% vs minulý měsíc
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Celkem závodů</div>
                    <div className="stat-value">{teamStats.totalRaces}</div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Pódia tuto sezónu</div>
                    <div className="stat-value">{Math.round(teamStats.totalPodiums)}</div>
                </div>
            </div>

            {/* Athletes Table */}
            <div className="card mb-4">
                <div className="card-header">
                    <h3 className="card-title">Závodníci - aktuální forma</h3>
                    <button className="btn btn-sm btn-secondary">
                        Export CSV
                    </button>
                </div>
                
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Jméno</th>
                                <th>Průměr</th>
                                <th>Medián</th>
                                <th>Střelba</th>
                                <th>Lyže</th>
                                <th>Top 10</th>
                                <th>Forma</th>
                                <th>Akce</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topAthletes.map((athlete, i) => (
                                <tr key={i}>
                                    <td>
                                        <strong>{athlete.name}</strong>
                                        <span className="text-gray text-sm"> ({athlete.nation})</span>
                                    </td>
                                    <td>{athlete.avg_rank.toFixed(1)}</td>
                                    <td>{athlete.median_rank?.toFixed(1) || '-'}</td>
                                    <td>
                                        <span className={`badge ${athlete.shooting_accuracy > 80 ? 'badge-success' : 'badge-warning'}`}>
                                            {athlete.shooting_accuracy.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td>{athlete.ski_speed_index?.toFixed(0) || '-'}</td>
                                    <td>{athlete.top10_rate.toFixed(1)}%</td>
                                    <td>
                                        {athlete.improvement_trend > 0 ? (
                                            <span className="text-success">↑ {athlete.improvement_trend.toFixed(1)}</span>
                                        ) : athlete.improvement_trend < 0 ? (
                                            <span className="text-danger">↓ {Math.abs(athlete.improvement_trend).toFixed(1)}</span>
                                        ) : (
                                            <span className="text-gray">→ 0.0</span>
                                        )}
                                    </td>
                                    <td>
                                        <button 
                                            className="btn btn-sm btn-primary"
                                            onClick={() => onSelectAthlete(athlete.name)}
                                        >
                                            Detail
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-2 gap-4">
                <div className="card">
                    <h3 className="card-title mb-3">Průměrné umístění</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={rankingData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis domain={[0, 50]} />
                            <Tooltip />
                            <Bar dataKey="rank" fill="#2563eb" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                
                <div className="card">
                    <h3 className="card-title mb-3">Přesnost střelby</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={rankingData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis domain={[60, 100]} />
                            <Tooltip />
                            <Bar dataKey="shooting" fill="#10b981" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
