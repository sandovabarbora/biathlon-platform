import React from 'react'
import { motion } from 'framer-motion'

const HolographicCard = ({ athlete, onClick, selected }) => {
  return (
    <motion.div 
      className={`holographic-card ${selected ? 'selected' : ''}`}
      whileHover={{ scale: 1.05 }}
      onClick={onClick}
      style={{
        padding: '1.5rem',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRadius: '1rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        cursor: 'pointer'
      }}
    >
      <h3>{athlete.name}</h3>
      <p>Rank: #{athlete.rank}</p>
      <p>Trend: {athlete.trend}</p>
    </motion.div>
  )
}

export default HolographicCard
