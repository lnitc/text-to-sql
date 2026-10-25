'use client';

import { useEffect } from 'react';
import { Message, useChatStore } from '../store';
import { formatDate } from '../utils/export';

const STORAGE_KEY = 'text-to-sql-messages';
const MAX_MESSAGES = 100;

let hydrated = false;

/** "Processing..." placeholders are transient and must not survive a reload. */
const isPlaceholder = (msg: Message) =>
  msg.type === 'assistant' && !msg.agentResponse && !msg.error;

function saveMessages(msgs: Message[]) {
  try {
    // Only keep last MAX_MESSAGES
    const toSave = msgs.filter((msg) => !isPlaceholder(msg)).slice(-MAX_MESSAGES);
    if (toSave.length === 0) {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
    }
  } catch (error) {
    console.error('Failed to persist messages:', error);
  }
}

/**
 * Load persisted messages into the store once, then save on every change
 * (including clearing, so cleared conversations stay cleared after reload).
 */
function hydrateFromStorage() {
  if (hydrated) return;
  hydrated = true;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as Message[];
      // Convert date strings back to Date objects
      const withDates = parsed
        .filter((msg) => !isPlaceholder(msg))
        .map((msg) => ({ ...msg, timestamp: new Date(msg.timestamp) }));
      useChatStore.setState({ messages: withDates });
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
  }

  useChatStore.subscribe((state, prev) => {
    if (state.messages !== prev.messages) {
      saveMessages(state.messages);
    }
  });
}

/**
 * Hook for persisting messages to localStorage
 * Auto-loads on mount and auto-saves on message changes
 */
export function useMessagePersistence() {
  const { messages, clearMessages } = useChatStore();

  // Load persisted messages on mount
  useEffect(() => {
    hydrateFromStorage();
  }, []);

  const clearPersistedMessages = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      clearMessages();
    } catch (error) {
      console.error('Failed to clear messages:', error);
    }
  };

  const exportMessages = (): string => {
    const export_data = {
      exportedAt: new Date().toISOString(),
      messageCount: messages.length,
      messages: messages.map((msg) => ({
        type: msg.type,
        timestamp: msg.timestamp.toISOString(),
        content: msg.content,
        sqlQuery: msg.agentResponse?.sql_query,
        chartType: msg.agentResponse?.chart.chart_type,
        error: msg.error,
      })),
    };
    return JSON.stringify(export_data, null, 2);
  };

  const downloadConversation = () => {
    const json = exportMessages();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversation-${formatDate(new Date()).split(' ').join('_')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return {
    clearPersistedMessages,
    exportMessages,
    downloadConversation,
  };
}
