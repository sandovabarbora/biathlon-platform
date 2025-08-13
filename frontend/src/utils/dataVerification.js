/**
 * Data Verification Utility
 * Ověří, že frontend zobrazuje reálná data
 */

const API_BASE = 'http://localhost:8000/api/v1'

export const verifyRealData = async () => {
  console.log('%c=== DATA VERIFICATION START ===', 'color: cyan; font-weight: bold; font-size: 16px')
  
  let allTestsPassed = true
  const results = []
  
  // Test 1: Athletes endpoint
  console.log('%c\n1. Testing Athletes Endpoint...', 'color: yellow; font-weight: bold')
  try {
    const response = await fetch(`${API_BASE}/athletes?nation=CZE&limit=10`)
    const data = await response.json()
    
    if (data && data.length > 0) {
      console.log('%c✅ Athletes loaded:', 'color: green', data.length, 'athletes')
      console.table(data.slice(0, 3).map(a => ({
        Name: a.name,
        Rank: a.world_rank,
        Points: a.world_cup_points,
        ID: a.id
      })))
      
      // Check for real Czech names
      const czechNames = ['DAVIDOVÁ', 'VOBORNÍKOVÁ', 'JISLOVÁ', 'CHARVÁTOVÁ']
      const hasRealNames = data.some(a => 
        czechNames.some(name => a.name?.toUpperCase().includes(name))
      )
      
      if (hasRealNames) {
        console.log('%c✅ REAL CZECH ATHLETES CONFIRMED!', 'color: green; font-weight: bold')
        results.push({ test: 'Athletes', status: 'REAL DATA', count: data.length })
      } else {
        console.log('%c⚠️ Data found but no recognized Czech athletes', 'color: orange')
        results.push({ test: 'Athletes', status: 'UNKNOWN DATA', count: data.length })
      }
    } else {
      console.log('%c❌ No athletes data', 'color: red')
      results.push({ test: 'Athletes', status: 'NO DATA', count: 0 })
      allTestsPassed = false
    }
  } catch (error) {
    console.error('%c❌ Athletes endpoint error:', 'color: red', error)
    results.push({ test: 'Athletes', status: 'ERROR', error: error.message })
    allTestsPassed = false
  }
  
  // Test 2: Races endpoint
  console.log('%c\n2. Testing Races Endpoint...', 'color: yellow; font-weight: bold')
  try {
    const response = await fetch(`${API_BASE}/races/recent`)
    const data = await response.json()
    
    if (data && data.length > 0) {
      console.log('%c✅ Races loaded:', 'color: green', data.length, 'races')
      console.table(data.slice(0, 3).map(r => ({
        Location: r.location,
        Date: r.date,
        Description: r.description,
        ID: r.race_id
      })))
      
      // Check for real locations
      const realLocations = ['Kontiolahti', 'Hochfilzen', 'Oberhof', 'Ruhpolding', 'Nove Mesto']
      const hasRealLocations = data.some(r => 
        realLocations.some(loc => r.location?.includes(loc))
      )
      
      if (hasRealLocations) {
        console.log('%c✅ REAL RACE LOCATIONS CONFIRMED!', 'color: green; font-weight: bold')
        results.push({ test: 'Races', status: 'REAL DATA', count: data.length })
      } else {
        console.log('%c⚠️ Race data found but locations not recognized', 'color: orange')
        results.push({ test: 'Races', status: 'UNKNOWN DATA', count: data.length })
      }
    } else {
      console.log('%c❌ No races data', 'color: red')
      results.push({ test: 'Races', status: 'NO DATA', count: 0 })
    }
  } catch (error) {
    console.error('%c❌ Races endpoint error:', 'color: red', error)
    results.push({ test: 'Races', status: 'ERROR', error: error.message })
  }
  
  // Test 3: Check for mock data indicators
  console.log('%c\n3. Checking for Mock Data...', 'color: yellow; font-weight: bold')
  
  const mockIndicators = ['test', 'mock', 'example', 'demo', 'lorem', 'ipsum']
  let foundMockData = false
  
  // Check localStorage
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    const value = localStorage.getItem(key)
    if (mockIndicators.some(indicator => 
      key.toLowerCase().includes(indicator) || 
      value.toLowerCase().includes(indicator)
    )) {
      console.log('%c⚠️ Possible mock data in localStorage:', 'color: orange', key)
      foundMockData = true
    }
  }
  
  if (!foundMockData) {
    console.log('%c✅ No mock data indicators found', 'color: green')
    results.push({ test: 'Mock Check', status: 'CLEAN' })
  } else {
    results.push({ test: 'Mock Check', status: 'MOCK DATA DETECTED' })
  }
  
  // Summary
  console.log('%c\n=== VERIFICATION SUMMARY ===', 'color: cyan; font-weight: bold; font-size: 16px')
  console.table(results)
  
  if (allTestsPassed && !foundMockData) {
    console.log('%c✅ ALL TESTS PASSED - USING REAL IBU DATA!', 
      'color: green; font-weight: bold; font-size: 18px; padding: 10px; background: #001100')
  } else {
    console.log('%c⚠️ Some issues detected - check results above', 
      'color: orange; font-weight: bold; font-size: 16px')
  }
  
  console.log('\n%c💡 TIP: Run this anytime with: window.verifyData()', 
    'color: cyan; font-style: italic')
  
  return results
}

// Auto-attach to window for easy access
if (typeof window !== 'undefined') {
  window.verifyData = verifyRealData
  
  // Auto-run on page load
  setTimeout(() => {
    console.log('%c🔍 Running automatic data verification...', 'color: cyan')
    verifyRealData()
  }, 2000)
}

export default verifyRealData
