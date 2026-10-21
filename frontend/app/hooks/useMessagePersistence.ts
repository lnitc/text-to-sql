'use client';

import { useEffect } from 'react';
import { Message, useChatStore } from '../store';
import { formatDate } from '../utils/export';

const STORAGE_KEY = 'text-to-sql-messages';
const MAX_MESSAGES = 100;

/**
 * Hook for persisting messages to localStorage
 * Auto-loads on mount and auto-saves on message changes
 */
export function useMessagePersistence() {
  const { messages, addMessage, clearMessages } = useChatStore();

  // Load persisted messages on mount
  useEffect(() => {
    loadMessages();
  }, []);

  // Save messages whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      saveMessages(messages);
    }
  }, [messages]);

  const saveMessages = (msgs: Message[]) => {
    try {
      // Only keep last MAX_MESSAGES
      const toSave = msgs.slice(-MAX_MESSAGES);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
    } catch (error) {
      console.error('Failed to persist messages:', error);
    }
  };

  const loadMessages = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Message[];
        // Convert date strings back to Date objects
        const withDates = parsed.map((msg) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));

        // Clear current messages and add persisted ones
        clearMessages();
        withDates.forEach((msg) => addMessage(msg));
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

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
    loadMessages,
    clearPersistedMessages,
    exportMessages,
    downloadConversation,
  };
}
