import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  LineChart, Line, BarChart, Bar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Activity, Target, TrendingUp, Trophy, Heart, Users } from 'lucide-react'

const API_URL = 'http://localhost:8000'

interface Athlete {
  id: string
  name: string
  nation: string
  avg_rank: number
  total_races: number
  top10_finishes: number
  podium_finishes: number
  avg_shooting_misses: number
  consistency_score: number
  recent_form: number | null
}

interface Metrics {
  shooting_accuracy: number
  ski_speed_percentile: number
  consistency_score: number
  mental_strength: number
  recent_form: number
}

interface TacticalAdvice {
  pacing_strategy: string
  risk_level: number
  key_message: string
  specific_actions: string[]
  success_probability: number
}

export default function App() {
  const [athletes, setAthletes] = useState<Athlete[]>([])
  const [selectedAthlete, setSelectedAthlete] = useState<string>('')
  const [athleteDetail, setAthleteDetail] = useState<any>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [tactical, setTactical] = useState<TacticalAdvice | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAthletes()
  }, [])

  const loadAthletes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/athletes?nation=CZE`)
      setAthletes(response.data)

      if (response.data.length > 0) {
        setSelectedAthlete(response.data[0].name)
      }
    } catch (error) {
      console.error('Error loading athletes:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedAthlete) {
      loadAthleteData()
    }
  }, [selectedAthlete])

  const loadAthleteData = async () => {
    try {
      const [detail, metricsRes, tacticalRes] = await Promise.all([
        axios.get(`${API_URL}/api/athlete/${selectedAthlete}`),
        axios.get(`${API_URL}/api/athlete/${selectedAthlete}/metrics`),
        axios.get(`${API_URL}/api/athlete/${selectedAthlete}/tactical`)
      ])

      setAthleteDetail(detail.data)
      setMetrics(metricsRes.data)
      setTactical(tacticalRes.data)
    } catch (error) {
      console.error('Error loading athlete data:', error)
    }
  }

  const radarData = metrics ? [
    { subject: 'Střelba', value: metrics.shooting_accuracy, fullMark: 100 },
    { subject: 'Rychlost', value: metrics.ski_speed_percentile, fullMark: 100 },
    { subject: 'Konzistence', value: metrics.consistency_score, fullMark: 100 },
    { subject: 'Mentální síla', value: metrics.mental_strength, fullMark: 100 },
    { subject: 'Forma', value: metrics.recent_form, fullMark: 100 }
  ] : []

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-2xl font-semibold">Načítám data...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-2xl mb-8 shadow-xl">
          <h1 className="text-5xl font-bold mb-2">🎿 Biathlon Analytics Platform</h1>
          <p className="text-xl opacity-90">Profesionální analýza výkonu s reálnými daty IBU</p>
        </div>

        {/* Athlete Selector */}
        <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
          <label className="block text-lg font-semibold mb-3">Vyberte závodníka:</label>
          <select
            value={selectedAthlete}
            onChange={(e) => setSelectedAthlete(e.target.value)}
            className="w-full p-4 text-lg border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition"
          >
            {athletes.map((athlete) => (
              <option key={athlete.id} value={athlete.name}>
                {athlete.name} ({athlete.nation}) - Ø {athlete.avg_rank}
              </option>
            ))}
          </select>
        </div>

        {athleteDetail && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition">
                <div className="flex items-center justify-between mb-2">
                  <Trophy className="h-8 w-8 text-yellow-500" />
                  <span className="text-sm text-gray-500">Průměr</span>
                </div>
                <div className="text-3xl font-bold text-gray-800">
                  {athleteDetail.statistics.avg_rank}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Nejlepší: #{athleteDetail.statistics.best_rank}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition">
                <div className="flex items-center justify-between mb-2">
                  <Target className="h-8 w-8 text-green-500" />
                  <span className="text-sm text-gray-500">TOP 10</span>
                </div>
                <div className="text-3xl font-bold text-gray-800">
                  {athleteDetail.statistics.top10_finishes}x
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Pódia: {athleteDetail.statistics.podium_finishes}x
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition">
                <div className="flex items-center justify-between mb-2">
                  <Activity className="h-8 w-8 text-red-500" />
                  <span className="text-sm text-gray-500">Střelba</span>
                </div>
                <div className="text-3xl font-bold text-gray-800">
                  {athleteDetail.statistics.avg_shooting_misses}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  chyb/závod
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition">
                <div className="flex items-center justify-between mb-2">
                  <Users className="h-8 w-8 text-purple-500" />
                  <span className="text-sm text-gray-500">Závody</span>
                </div>
                <div className="text-3xl font-bold text-gray-800">
                  {athleteDetail.statistics.total_races}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Konzistence: {athleteDetail.statistics.consistency_score}
                </div>
              </div>
            </div>

            {/* Tactical Advice */}
            {tactical && (
              <div className={`p-6 rounded-xl shadow-lg mb-8 ${
                tactical.pacing_strategy === 'PUSH' ? 'bg-green-50 border-2 border-green-300' :
                tactical.pacing_strategy === 'CONSERVE' ? 'bg-yellow-50 border-2 border-yellow-300' :
                'bg-blue-50 border-2 border-blue-300'
              }`}>
                <h3 className="text-2xl font-bold mb-4">🎯 Taktické doporučení</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <div className="text-sm text-gray-600">Strategie</div>
                    <div className="text-2xl font-bold">{tactical.pacing_strategy}</div>
                    <div className="text-sm mt-2">Risk level: {tactical.risk_level}/10</div>
                  </div>
                  <div className="md:col-span-2">
                    <div className="text-lg font-semibold mb-2">{tactical.key_message}</div>
                    <ul className="space-y-1">
                      {tactical.specific_actions.map((action, i) => (
                        <li key={i} className="text-sm">{action}</li>
                      ))}
                    </ul>
                    <div className="mt-3 text-sm">
                      Šance na úspěch: {(tactical.success_probability * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4">Výkonnostní profil</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar
                      name="Výkon"
                      dataKey="value"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4">Historie umístění</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={athleteDetail.recent_races || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="RaceId" />
                    <YAxis reversed domain={[1, 'dataMax']} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="Rank"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      dot={{ fill: '#3b82f6', r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
