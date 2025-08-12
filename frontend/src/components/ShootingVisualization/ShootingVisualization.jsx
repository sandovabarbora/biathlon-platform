import React, { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, Box, Sphere, Trail } from '@react-three/drei'
import { motion } from 'framer-motion'
import * as THREE from 'three'
import './ShootingVisualization.css'

// Target component
const Target = ({ position, hit, index, onHit }) => {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 2) * 0.1
    }
  })

  const color = hit ? '#00ff88' : '#ff0080'
  
  return (
    <group position={position}>
      {/* Target base */}
      <Box
        ref={meshRef}
        args={[1, 1, 0.1]}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={() => onHit(index)}
      >
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={hit ? 0.5 : 0.2}
          metalness={0.8}
          roughness={0.2}
        />
      </Box>
      
      {/* Target rings */}
      {[0.4, 0.3, 0.2, 0.1].map((radius, i) => (
        <mesh key={i} position={[0, 0, 0.06]}>
          <ringGeometry args={[radius - 0.05, radius, 32]} />
          <meshBasicMaterial 
            color={i === 3 ? '#ffdc00' : '#ffffff'} 
            opacity={0.8}
            transparent
          />
        </mesh>
      ))}
      
      {/* Hit indicator */}
      {hit !== null && (
        <Sphere args={[0.05]} position={[0, 0, 0.1]}>
          <meshStandardMaterial
            color={hit ? '#00ff88' : '#ff0080'}
            emissive={hit ? '#00ff88' : '#ff0080'}
            emissiveIntensity={1}
          />
        </Sphere>
      )}
      
      {/* Target number */}
      <Text
        position={[0, -0.7, 0.1]}
        fontSize={0.2}
        color="white"
      >
        {index + 1}
      </Text>
    </group>
  )
}

// Wind particles
const WindParticles = ({ strength = 0 }) => {
  const particlesRef = useRef()
  
  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.x = state.clock.elapsedTime * 0.1
      particlesRef.current.position.x = Math.sin(state.clock.elapsedTime) * strength
    }
  })
  
  return (
    <group ref={particlesRef}>
      {Array.from({ length: 50 }).map((_, i) => (
        <Sphere
          key={i}
          args={[0.01]}
          position={[
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 5,
            (Math.random() - 0.5) * 3
          ]}
        >
          <meshBasicMaterial color="#00d4ff" opacity={0.3} transparent />
        </Sphere>
      ))}
    </group>
  )
}

// Main visualization component
const ShootingVisualization = ({ shootingData, athleteName }) => {
  const [selectedRound, setSelectedRound] = useState(0)
  const [animating, setAnimating] = useState(false)
  
  const rounds = shootingData?.rounds || []
  const currentRound = rounds[selectedRound] || { shots: [true, true, true, true, true] }
  
  const handleTargetHit = (index) => {
    setAnimating(true)
    setTimeout(() => setAnimating(false), 500)
  }
  
  const accuracy = (shots) => {
    const hits = shots.filter(s => s).length
    return (hits / shots.length * 100).toFixed(0)
  }
  
  return (
    <div className="shooting-visualization">
      {/* 3D Canvas */}
      <div className="canvas-container">
        <Canvas 
          camera={{ position: [0, 2, 8], fov: 45 }}
          gl={{ antialias: true, alpha: true }}
        >
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00d4ff" />
          
          {/* Shooting range */}
          <group position={[0, 0, 0]}>
            {/* Targets */}
            {currentRound.shots.map((hit, i) => (
              <Target
                key={i}
                position={[(i - 2) * 1.5, 0, 0]}
                hit={hit}
                index={i}
                onHit={handleTargetHit}
              />
            ))}
            
            {/* Ground */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
              <planeGeometry args={[20, 10]} />
              <meshStandardMaterial color="#1c1c28" metalness={0.9} roughness={0.1} />
            </mesh>
            
            {/* Wind effect */}
            <WindParticles strength={shootingData?.windSpeed || 0} />
          </group>
          
          <OrbitControls 
            enablePan={false}
            maxPolarAngle={Math.PI / 2}
            minDistance={5}
            maxDistance={15}
          />
        </Canvas>
      </div>
      
      {/* Controls and stats */}
      <div className="visualization-controls glass">
        {/* Round selector */}
        <div className="round-selector">
          {rounds.map((round, i) => (
            <button
              key={i}
              className={`round-btn ${selectedRound === i ? 'active' : ''}`}
              onClick={() => setSelectedRound(i)}
            >
              <span className="round-type">{round.type}</span>
              <span className="round-accuracy">{accuracy(round.shots)}%</span>
            </button>
          ))}
        </div>
        
        {/* Stats display */}
        <div className="shooting-stats">
          <div className="stat-item">
            <span className="stat-label">Accuracy</span>
            <span className="stat-value neon-glow-green">
              {accuracy(currentRound.shots)}%
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Time</span>
            <span className="stat-value">{currentRound.time || '25.3'}s</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Wind</span>
            <span className="stat-value">{shootingData?.windSpeed || '2.1'} m/s</span>
          </div>
        </div>
        
        {/* Athlete name */}
        <div className="athlete-label holographic">
          {athleteName}
        </div>
      </div>
    </div>
  )
}

export default ShootingVisualization
