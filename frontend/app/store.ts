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

export interface SavedQuery {
  id: string;
  query: string;
  tags: string[];
  isFavorite: boolean;
  createdAt: Date;
  lastUsed: Date;
  resultCount: number;
}

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  favorites: SavedQuery[];
  addMessage: (message: Message) => void;
  removeMessage: (id: string) => void;
  clearMessages: () => void;
  setIsLoading: (loading: boolean) => void;
  setFavorites: (favorites: SavedQuery[]) => void;
  addFavorite: (query: SavedQuery) => void;
  removeFavorite: (id: string) => void;
  updateFavorite: (id: string, updates: Partial<SavedQuery>) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  favorites: [],
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
  setFavorites: (favorites: SavedQuery[]) =>
    set(() => ({
      favorites,
    })),
  addFavorite: (query: SavedQuery) =>
    set((state) => ({
      favorites: [query, ...state.favorites],
    })),
  removeFavorite: (id: string) =>
    set((state) => ({
      favorites: state.favorites.filter((f) => f.id !== id),
    })),
  updateFavorite: (id: string, updates: Partial<SavedQuery>) =>
    set((state) => ({
      favorites: state.favorites.map((f) =>
        f.id === id ? { ...f, ...updates } : f
      ),
    })),
}));
