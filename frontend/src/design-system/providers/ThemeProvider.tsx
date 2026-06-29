/**
 * @module ThemeProvider
 * @description Manages application-wide theme state, persistence, and system preference detection.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

export type Theme = 'enterprise-dark' | 'enterprise-light' | 'high-contrast' | 'presentation';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children, defaultTheme = 'enterprise-dark' }: { children: React.ReactNode, defaultTheme?: Theme }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem('synapse-theme') as Theme;
    if (saved) return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'enterprise-light';
    }
    return defaultTheme;
  });

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('synapse-theme', newTheme);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.remove('dark', 'light', 'high-contrast', 'presentation');
    
    if (theme === 'enterprise-dark' || theme === 'high-contrast') {
      document.documentElement.classList.add('dark');
    }
    if (theme === 'high-contrast') {
      document.documentElement.classList.add('high-contrast');
    }
    if (theme === 'presentation') {
      document.documentElement.classList.add('presentation');
    }
  }, [theme]);

  // Listen to system changes if theme wasn't explicitly saved
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('synapse-theme')) {
        setThemeState(e.matches ? 'enterprise-light' : 'enterprise-dark');
      }
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
