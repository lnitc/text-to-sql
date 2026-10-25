'use client';

import { useEffect, useSyncExternalStore } from 'react';

type Theme = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'text-to-sql-theme';
const DARK_QUERY = '(prefers-color-scheme: dark)';

// Theme lives outside React (localStorage + OS setting), so read it with
// useSyncExternalStore instead of mirroring it into state inside effects.
const listeners = new Set<() => void>();

function readTheme(): Theme {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : 'system';
  } catch {
    return 'system';
  }
}

function readIsDark(): boolean {
  const theme = readTheme();
  return theme === 'dark' || (theme === 'system' && window.matchMedia(DARK_QUERY).matches);
}

function subscribe(callback: () => void) {
  listeners.add(callback);
  const mediaQuery = window.matchMedia(DARK_QUERY);
  mediaQuery.addEventListener('change', callback);
  // Theme changes made in other tabs
  window.addEventListener('storage', callback);
  return () => {
    listeners.delete(callback);
    mediaQuery.removeEventListener('change', callback);
    window.removeEventListener('storage', callback);
  };
}

/**
 * Hook for managing dark mode theme preference
 */
export function useDarkMode() {
  const theme = useSyncExternalStore(subscribe, readTheme, () => 'system' as Theme);
  const isDark = useSyncExternalStore(subscribe, readIsDark, () => false);

  // Tailwind's dark: variant is keyed off the .dark class (see globals.css)
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  const setUserTheme = (newTheme: Theme) => {
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
    listeners.forEach((listener) => listener());
  };

  const toggleDarkMode = () => {
    setUserTheme(isDark ? 'light' : 'dark');
  };

  return {
    theme,
    isDark,
    setTheme: setUserTheme,
    toggleDarkMode,
  };
}
