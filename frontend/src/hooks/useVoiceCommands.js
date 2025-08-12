import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'

const useVoiceCommands = () => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [recognition, setRecognition] = useState(null)

  useEffect(() => {
    // Check if browser supports Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.log('Speech recognition not supported')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognitionInstance = new SpeechRecognition()

    // Configure recognition
    recognitionInstance.continuous = true
    recognitionInstance.interimResults = true
    recognitionInstance.lang = 'cs-CZ' // Czech language

    // Set up event handlers
    recognitionInstance.onstart = () => {
      setIsListening(true)
      toast.success('Voice control activated', {
        icon: '🎤',
        style: {
          background: 'var(--color-midnight)',
          color: 'var(--color-neon-green)',
          border: '1px solid var(--color-neon-green)',
        }
      })
    }

    recognitionInstance.onresult = (event) => {
      const current = event.resultIndex
      const transcript = event.results[current][0].transcript.toLowerCase()
      setTranscript(transcript)
      
      // Process commands
      processCommand(transcript)
    }

    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      
      if (event.error === 'no-speech') {
        toast.error('No speech detected', {
          style: {
            background: 'var(--color-midnight)',
            color: 'var(--color-czech-red)',
            border: '1px solid var(--color-czech-red)',
          }
        })
      }
    }

    recognitionInstance.onend = () => {
      setIsListening(false)
    }

    setRecognition(recognitionInstance)

    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop()
      }
    }
  }, [])

  const processCommand = useCallback((command) => {
    // Czech commands
    const commands = {
      'davidová': () => navigateToAthlete('davidova'),
      'jislová': () => navigateToAthlete('jislova'),
      'charvátová': () => navigateToAthlete('charvatova'),
      'střelba': () => showShootingAnalysis(),
      'trénink': () => navigateToTraining(),
      'závody': () => navigateToRaces(),
      'analýza': () => navigateToAnalytics(),
      'live': () => toggleLiveMode(),
      'nápověda': () => showHelp(),
      'zavřít': () => closeCurrentView(),
    }

    // English commands fallback
    const englishCommands = {
      'shooting': () => showShootingAnalysis(),
      'training': () => navigateToTraining(),
      'races': () => navigateToRaces(),
      'analytics': () => navigateToAnalytics(),
      'help': () => showHelp(),
    }

    // Check for command matches
    Object.entries({ ...commands, ...englishCommands }).forEach(([key, action]) => {
      if (command.includes(key)) {
        action()
        toast.success(`Command: ${key}`, {
          icon: '✅',
          style: {
            background: 'var(--color-midnight)',
            color: 'var(--color-neon-blue)',
            border: '1px solid var(--color-neon-blue)',
          }
        })
      }
    })
  }, [])

  const navigateToAthlete = (athleteId) => {
    window.location.href = `/athletes/${athleteId}`
  }

  const showShootingAnalysis = () => {
    window.location.href = '/analytics#shooting'
  }

  const navigateToTraining = () => {
    window.location.href = '/training'
  }

  const navigateToRaces = () => {
    window.location.href = '/races'
  }

  const navigateToAnalytics = () => {
    window.location.href = '/analytics'
  }

  const toggleLiveMode = () => {
    document.dispatchEvent(new CustomEvent('toggleLiveMode'))
  }

  const showHelp = () => {
    toast.custom((t) => (
      <div className="voice-help-toast glass">
        <h3>🎤 Voice Commands</h3>
        <ul>
          <li>"Davidová" - Show Markéta Davidová</li>
          <li>"Střelba" - Shooting analysis</li>
          <li>"Trénink" - Training recommendations</li>
          <li>"Závody" - Race schedule</li>
          <li>"Live" - Toggle live mode</li>
        </ul>
        <button onClick={() => toast.dismiss(t.id)}>Close</button>
      </div>
    ), { duration: 10000 })
  }

  const closeCurrentView = () => {
    window.history.back()
  }

  const startListening = () => {
    if (recognition && !isListening) {
      recognition.start()
    }
  }

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop()
    }
  }

  const toggleListening = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    toggleListening,
    isSupported: !!recognition
  }
}

export default useVoiceCommands
