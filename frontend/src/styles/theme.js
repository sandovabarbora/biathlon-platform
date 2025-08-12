// Aurora Design System - Cutting Edge Theme
export const theme = {
  // Core colors - Dark base with neon accents
  colors: {
    // Base palette - deep space
    void: '#0a0a0f',
    midnight: '#13131a', 
    shadow: '#1c1c28',
    slate: '#2a2a3e',
    
    // Czech national colors
    czechBlue: '#11457e',
    czechRed: '#d7141a',
    czechWhite: '#ffffff',
    
    // Aurora neon palette
    neonGreen: '#00ff88',
    neonBlue: '#00d4ff',
    neonPurple: '#b794f6',
    neonPink: '#ff0080',
    neonYellow: '#ffdc00',
    
    // Semantic colors with gradients
    success: {
      solid: '#00ff88',
      gradient: 'linear-gradient(135deg, #00ff88 0%, #00cc6a 100%)',
      glow: '0 0 20px rgba(0, 255, 136, 0.5)'
    },
    danger: {
      solid: '#ff0080',
      gradient: 'linear-gradient(135deg, #ff0080 0%, #cc0066 100%)',
      glow: '0 0 20px rgba(255, 0, 128, 0.5)'
    },
    warning: {
      solid: '#ffaa00',
      gradient: 'linear-gradient(135deg, #ffaa00 0%, #ff8800 100%)',
      glow: '0 0 20px rgba(255, 170, 0, 0.5)'
    },
    
    // Text colors
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
      muted: 'rgba(255, 255, 255, 0.4)',
      inverse: '#0a0a0f'
    }
  },
  
  // Glassmorphism effects
  glass: {
    light: {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(40px) saturate(200%)',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    },
    dark: {
      background: 'rgba(0, 0, 0, 0.3)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.05)'
    },
    colored: (color, opacity = 0.1) => ({
      background: `${color}${Math.round(opacity * 255).toString(16)}`,
      backdropFilter: 'blur(40px) saturate(150%)',
      border: `1px solid ${color}33`
    })
  },
  
  // Advanced shadows
  shadows: {
    neon: (color) => `0 0 20px ${color}66, 0 0 40px ${color}33, 0 0 60px ${color}1a`,
    depth: {
      sm: '0 2px 8px rgba(0, 0, 0, 0.3)',
      md: '0 10px 40px rgba(0, 0, 0, 0.4)',
      lg: '0 20px 60px rgba(0, 0, 0, 0.5)',
      xl: '0 30px 80px rgba(0, 0, 0, 0.6)'
    },
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.5)'
  },
  
  // Typography
  typography: {
    fonts: {
      display: '"Orbitron", "Inter", sans-serif',
      body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace'
    },
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem', 
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '2rem',
      '4xl': '2.5rem',
      '5xl': '3rem'
    }
  },
  
  // Animation presets
  animations: {
    pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
    float: 'float 6s ease-in-out infinite',
    glow: 'glow 2s ease-in-out infinite alternate',
    slideIn: 'slideIn 0.3s ease-out',
    fadeIn: 'fadeIn 0.5s ease-out'
  },
  
  // Spacing system
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem'
  },
  
  // Border radius
  radii: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px'
  }
}

// CSS Variables for global usage
export const cssVariables = `
  :root {
    --color-void: ${theme.colors.void};
    --color-midnight: ${theme.colors.midnight};
    --color-neon-green: ${theme.colors.neonGreen};
    --color-neon-blue: ${theme.colors.neonBlue};
    --color-neon-purple: ${theme.colors.neonPurple};
    --color-czech-blue: ${theme.colors.czechBlue};
    --color-czech-red: ${theme.colors.czechRed};
    
    --font-display: ${theme.typography.fonts.display};
    --font-body: ${theme.typography.fonts.body};
    --font-mono: ${theme.typography.fonts.mono};
  }
`
