import { create } from 'zustand';
import { AgentResponse } from './api';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  agentResponse?: AgentResponse;
  timestamp: Date;
  error?: string;
}

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setIsLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  addMessage: (message: Message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () =>
    set(() => ({
      messages: [],
    })),
  setIsLoading: (loading: boolean) =>
    set(() => ({
      isLoading: loading,
    })),
}));
