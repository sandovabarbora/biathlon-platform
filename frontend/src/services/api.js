const API_BASE_URL = 'http://localhost:8000/api/v1'

// Helper for API calls
const apiCall = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API Call failed:', error)
    throw error
  }
}

// Athletes endpoints
export const athletesAPI = {
  getAll: (nation = 'CZE', limit = 20) => 
    apiCall(`/athletes?nation=${nation}&limit=${limit}`),
  
  getPerformance: (athleteId) => 
    apiCall(`/athletes/${athleteId}/performance`),
  
  getHistory: (athleteId, limit = 50) => 
    apiCall(`/athletes/${athleteId}/history?limit=${limit}`),
}

// Fatigue Analysis endpoints
export const fatigueAPI = {
  getProfile: (athleteId, includeHistory = true) => 
    apiCall(`/fatigue/profile/${athleteId}?include_history=${includeHistory}`),
  
  getTeamAnalysis: (nation = 'CZE') => 
    apiCall(`/fatigue/team/analysis?nation=${nation}`),
  
  compareAthletes: (athlete1Id, athlete2Id) => 
    apiCall(`/fatigue/compare?athlete1_id=${athlete1Id}&athlete2_id=${athlete2Id}`),
  
  getRaceStrategy: (athleteId, raceType, conditions = {}) => 
    apiCall(`/fatigue/race-strategy/${athleteId}?race_type=${raceType}`, {
      method: 'POST',
      body: JSON.stringify(conditions)
    }),
  
  getTrends: (athleteId, periodDays = 90) => 
    apiCall(`/fatigue/trends/${athleteId}?period_days=${periodDays}`),
}

// Analytics endpoints  
export const analyticsAPI = {
  getTrainingRecommendations: (athleteId) => 
    apiCall(`/analytics/training/${athleteId}`),
  
  getHeadToHead: (athlete1, athlete2) => 
    apiCall(`/analytics/head-to-head?athlete1=${athlete1}&athlete2=${athlete2}`),
  
  getComparison: (athlete1, athlete2) => 
    apiCall(`/analytics/comparison?athlete1=${athlete1}&athlete2=${athlete2}`),
  
  getTrends: (athleteId, period = 'season') => 
    apiCall(`/analytics/trends/${athleteId}?period=${period}`),
}

// Races endpoints
export const racesAPI = {
  getRecent: (limit = 10) => 
    apiCall(`/races/recent?limit=${limit}`),
  
  getUpcoming: () => 
    apiCall('/races/upcoming'),
  
  getAnalysis: (raceId) => 
    apiCall(`/races/${raceId}/analysis`),
  
  getLive: (raceId) => 
    apiCall(`/races/${raceId}/live`),
}

// Czech-specific endpoints
export const czechAPI = {
  getDashboard: () => 
    apiCall('/analytics/czech-dashboard'),
  
  getAthleteVsWorld: (ibuId, compareWith = null) => {
    let url = `/analytics/athlete/${ibuId}/vs-world`
    if (compareWith) url += `?compare_with=${compareWith}`
    return apiCall(url)
  },
  
  getTrainingPriorities: () => 
    apiCall('/analytics/training-priorities'),
  
  getMedalChances: () => 
    apiCall('/analytics/medal-chances'),
}

export default {
  athletes: athletesAPI,
  fatigue: fatigueAPI,
  analytics: analyticsAPI,
  races: racesAPI,
  czech: czechAPI,
}
