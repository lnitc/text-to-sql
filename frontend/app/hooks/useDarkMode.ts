'use client';

import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'text-to-sql-theme';

/**
 * Hook for managing dark mode theme preference
 */
export function useDarkMode() {
  const [theme, setTheme] = useState<Theme>('system');
  const [isDark, setIsDark] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load theme preference on mount
  useEffect(() => {
    loadTheme();
    setIsLoaded(true);
  }, []);

  // Watch for system theme changes
  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = (e: MediaQueryListEvent) => {
        setIsDark(e.matches);
        applyTheme(e.matches);
      };

      // Set initial value
      setIsDark(mediaQuery.matches);
      applyTheme(mediaQuery.matches);

      // Listen for changes
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  // Apply theme when explicit light/dark is selected
  useEffect(() => {
    if (theme === 'light') {
      setIsDark(false);
      applyTheme(false);
    } else if (theme === 'dark') {
      setIsDark(true);
      applyTheme(true);
    }
  }, [theme]);

  const loadTheme = () => {
    try {
      const stored = (localStorage.getItem(STORAGE_KEY) as Theme) || 'system';
      setTheme(stored);

      // Apply initial theme
      if (stored === 'dark') {
        setIsDark(true);
        applyTheme(true);
      } else if (stored === 'light') {
        setIsDark(false);
        applyTheme(false);
      } else {
        // System theme
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setIsDark(prefersDark);
        applyTheme(prefersDark);
      }
    } catch (error) {
      console.error('Failed to load theme:', error);
    }
  };

  const applyTheme = (dark: boolean) => {
    const html = document.documentElement;
    if (dark) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  };

  const setUserTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  };

  const toggleDarkMode = () => {
    if (theme === 'light') {
      setUserTheme('dark');
    } else if (theme === 'dark') {
      setUserTheme('light');
    } else {
      // Toggle from system default
      setUserTheme(isDark ? 'light' : 'dark');
    }
  };

  return {
    theme,
    isDark,
    isLoaded,
    setTheme: setUserTheme,
    toggleDarkMode,
  };
}
