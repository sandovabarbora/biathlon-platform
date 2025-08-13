/**
 * API Test Utility - testuje všechny endpointy
 */

const BASE_URL = 'http://localhost:8000/api/v1'

export const testAllEndpoints = async () => {
  console.log('🔍 Testing all API endpoints...')
  
  const tests = [
    { name: 'Czech Athletes', url: `${BASE_URL}/athletes?nation=CZE` },
    { name: 'Recent Races', url: `${BASE_URL}/races/recent` },
    { name: 'Upcoming Races', url: `${BASE_URL}/races/upcoming` },
    { name: 'Davidova Performance', url: `${BASE_URL}/athletes/BTCZE20301199701/performance` },
  ]
  
  const results = []
  
  for (const test of tests) {
    try {
      const response = await fetch(test.url)
      const data = await response.json()
      
      results.push({
        name: test.name,
        status: response.ok ? '✅' : '❌',
        dataCount: Array.isArray(data) ? data.length : 'object',
        sample: data
      })
      
      console.log(`${response.ok ? '✅' : '❌'} ${test.name}:`, data)
    } catch (error) {
      results.push({
        name: test.name,
        status: '❌',
        error: error.message
      })
      console.error(`❌ ${test.name}:`, error)
    }
  }
  
  console.table(results)
  return results
}

// Auto-run při loadu
if (typeof window !== 'undefined') {
  window.testAPI = testAllEndpoints
  console.log('💡 TIP: Run window.testAPI() in console to test all endpoints')
}
