'use client';

import { useEffect, useRef } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  cmd?: boolean;
  action: () => void;
}

const clickSendButton = () => {
  const sendBtn = document.querySelector('button[title="Send"]') as HTMLButtonElement | null;
  sendBtn?.click();
};

const focusQueryInput = () => {
  const input = document.querySelector('input[placeholder*="Ask"]') as HTMLInputElement | null;
  input?.focus();
};

const defaultShortcuts: KeyboardShortcut[] = [
  { key: 'Enter', ctrl: true, action: clickSendButton },
  { key: 'Enter', cmd: true, action: clickSendButton },
  { key: 'k', ctrl: true, action: focusQueryInput },
  { key: 'k', cmd: true, action: focusQueryInput },
  {
    key: 'Escape',
    action: () => {
      // Close panels/dialogs
      window.dispatchEvent(new CustomEvent('closePanel'));
    },
  },
];

function matches(e: KeyboardEvent, shortcut: KeyboardShortcut): boolean {
  return (
    e.key.toLowerCase() === shortcut.key.toLowerCase() &&
    e.ctrlKey === !!shortcut.ctrl &&
    e.metaKey === !!shortcut.cmd &&
    e.shiftKey === !!shortcut.shift &&
    e.altKey === !!shortcut.alt
  );
}

/**
 * Hook for managing keyboard shortcuts
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[] = []) {
  // Keep the latest shortcuts in a ref so the listener is registered once
  // instead of on every render
  const shortcutsRef = useRef(shortcuts);
  useEffect(() => {
    shortcutsRef.current = shortcuts;
  });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const shortcut = [...defaultShortcuts, ...shortcutsRef.current].find((s) =>
        matches(e, s)
      );
      if (shortcut) {
        e.preventDefault();
        shortcut.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}

/**
 * Common keyboard shortcuts documentation
 */
export const KEYBOARD_SHORTCUTS_HELP = [
  { combo: 'Ctrl/Cmd + Enter', action: 'Send query' },
  { combo: 'Ctrl/Cmd + K', action: 'Focus search input' },
  { combo: 'Escape', action: 'Close panels' },
];
