'use client';

import { useEffect } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  cmd?: boolean;
  action: () => void;
}

/**
 * Hook for managing keyboard shortcuts
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[] = []) {
  const defaultShortcuts: KeyboardShortcut[] = [
    {
      key: 'Enter',
      ctrl: true,
      action: () => {
        // Send message - will be provided by parent
        const sendBtn = document.querySelector('button[title="Send"]') as HTMLButtonElement;
        sendBtn?.click();
      },
    },
    {
      key: 'Enter',
      cmd: true,
      action: () => {
        const sendBtn = document.querySelector('button[title="Send"]') as HTMLButtonElement;
        sendBtn?.click();
      },
    },
    {
      key: 'k',
      ctrl: true,
      action: () => {
        // Focus input
        const input = document.querySelector('input[placeholder*="Ask"]') as HTMLInputElement;
        input?.focus();
      },
    },
    {
      key: 'k',
      cmd: true,
      action: () => {
        const input = document.querySelector('input[placeholder*="Ask"]') as HTMLInputElement;
        input?.focus();
      },
    },
    {
      key: 'Escape',
      action: () => {
        // Close panels/dialogs
        const event = new CustomEvent('closePanel');
        window.dispatchEvent(event);
      },
    },
  ];

  const allShortcuts = [...defaultShortcuts, ...shortcuts];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      for (const shortcut of allShortcuts) {
        const matchesKey = e.key.toLowerCase() === shortcut.key.toLowerCase();
        const matchesCtrl = shortcut.ctrl ? e.ctrlKey : !e.ctrlKey || !shortcut.ctrl;
        const matchesShift = shortcut.shift ? e.shiftKey : !e.shiftKey || !shortcut.shift;
        const matchesAlt = shortcut.alt ? e.altKey : !e.altKey || !shortcut.alt;
        const matchesCmd = shortcut.cmd ? e.metaKey : !e.metaKey || !shortcut.cmd;

        if (
          matchesKey &&
          ((shortcut.ctrl && e.ctrlKey) || (shortcut.cmd && e.metaKey) || (!shortcut.ctrl && !shortcut.cmd)) &&
          matchesShift &&
          matchesAlt
        ) {
          e.preventDefault();
          shortcut.action();
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [allShortcuts]);

  return {
    shortcuts: allShortcuts,
  };
}

/**
 * Common keyboard shortcuts documentation
 */
export const KEYBOARD_SHORTCUTS_HELP = [
  { combo: 'Ctrl/Cmd + Enter', action: 'Send query' },
  { combo: 'Ctrl/Cmd + K', action: 'Focus search input' },
  { combo: 'Escape', action: 'Close panels' },
];
