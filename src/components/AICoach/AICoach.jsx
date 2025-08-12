import React from 'react'

const AICoach = ({ athlete, onInsight }) => {
  return (
    <div className="ai-coach" style={{
      padding: '2rem',
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <h3>AI Coach Assistant</h3>
      {athlete ? (
        <p>Analyzing {athlete.name}...</p>
      ) : (
        <p>Select an athlete for AI insights</p>
      )}
    </div>
  )
}

export default AICoach
