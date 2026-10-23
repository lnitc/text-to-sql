import { create } from 'zustand';
import { AgentResponse } from './api';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  agentResponse?: AgentResponse;
  timestamp: Date;
  error?: string;
  userQuery?: string; // Store the original user query for assistant messages
}

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  addMessage: (message: Message) => void;
  removeMessage: (id: string) => void;
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
  removeMessage: (id: string) =>
    set((state) => ({
      messages: state.messages.filter((m) => m.id !== id),
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
