import React, { useState } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const ComparisonView = ({ athletes }) => {
    const [selectedAthletes, setSelectedAthletes] = useState([])
    const [comparisonData, setComparisonData] = useState(null)
    const [loading, setLoading] = useState(false)

    const handleCompare = async () => {
        if (selectedAthletes.length < 2) {
            alert('Vyberte alespoň 2 závodníky pro srovnání')
            return
        }

        setLoading(true)
        try {
            const response = await axios.get(
                `${API_URL}/api/compare?athletes=${selectedAthletes.join(',')}`
            )
            setComparisonData(response.data)
        } catch (error) {
            console.error('Comparison error:', error)
        } finally {
            setLoading(false)
        }
    }

    const toggleAthlete = (name) => {
        if (selectedAthletes.includes(name)) {
            setSelectedAthletes(selectedAthletes.filter(a => a !== name))
        } else if (selectedAthletes.length < 4) {
            setSelectedAthletes([...selectedAthletes, name])
        }
    }

    return (
        <div className="comparison-view">
            <h2 className="mb-4">Srovnání závodníků</h2>
            
            {/* Selection */}
            <div className="card mb-4">
                <h3 className="card-title mb-3">Vyberte závodníky (max 4)</h3>
                <div className="grid grid-cols-4 gap-2 mb-3">
                    {athletes.slice(0, 12).map(athlete => (
                        <button
                            key={athlete.name}
                            className={`btn ${selectedAthletes.includes(athlete.name) ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => toggleAthlete(athlete.name)}
                        >
                            {athlete.name.split(' ').pop()}
                        </button>
                    ))}
                </div>
                
                <button 
                    className="btn btn-success"
                    onClick={handleCompare}
                    disabled={selectedAthletes.length < 2 || loading}
                >
                    {loading ? 'Načítám...' : 'Porovnat'}
                </button>
            </div>

            {/* Comparison Results */}
            {comparisonData && (
                <div className="card">
                    <h3 className="card-title mb-3">Výsledky srovnání</h3>
                    
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Metrika</th>
                                    {comparisonData.athletes.map(a => (
                                        <th key={a.name}>{a.name}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {comparisonData.comparison_metrics.map(metric => (
                                    <tr key={metric}>
                                        <td><strong>{metric}</strong></td>
                                        {comparisonData.athletes.map(a => (
                                            <td key={a.name}>
                                                <span className={`badge badge-${
                                                    a[`${metric}_relative`] === 'BEST' ? 'success' :
                                                    a[`${metric}_relative`] === 'WORST' ? 'danger' : 'gray'
                                                }`}>
                                                    {a[metric]?.toFixed(1) || 'N/A'}
                                                </span>
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ComparisonView
