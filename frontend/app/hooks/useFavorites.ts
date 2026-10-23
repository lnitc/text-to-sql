'use client';

import { useState, useEffect } from 'react';
import { useChatStore, SavedQuery } from '../store';

const STORAGE_KEY = 'text-to-sql-queries';
const MAX_HISTORY = 20;
const MAX_FAVORITES = 50;

/**
 * Hook for managing saved queries, favorites, and history
 */
export function useFavorites() {
  const { favorites, setFavorites, addFavorite, removeFavorite, updateFavorite } = useChatStore();
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    loadQueries();
    setIsLoaded(true);
  }, []);

  // Save to localStorage whenever favorites change
  useEffect(() => {
    if (isLoaded) {
      saveToStorage(favorites);
    }
  }, [favorites, isLoaded]);

  const loadQueries = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as SavedQuery[];
        // Convert date strings back to Date objects
        const withDates = parsed.map((q) => ({
          ...q,
          createdAt: new Date(q.createdAt),
          lastUsed: new Date(q.lastUsed),
        }));
        setFavorites(withDates);
      }
    } catch (error) {
      console.error('Failed to load queries:', error);
    }
  };

  const saveToStorage = (updated: SavedQuery[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save queries:', error);
    }
  };

  const addQuery = (query: string, tags: string[] = []): SavedQuery => {
    const id = `q-${Date.now()}`;
    const newQuery: SavedQuery = {
      id,
      query,
      tags,
      isFavorite: false,
      createdAt: new Date(),
      lastUsed: new Date(),
      resultCount: 0,
    };

    addFavorite(newQuery);
    return newQuery;
  };

  const toggleFavorite = (id: string): boolean => {
    const query = favorites.find((q) => q.id === id);
    if (query) {
      const newFavoriteState = !query.isFavorite;
      updateFavorite(id, { isFavorite: newFavoriteState });
      return newFavoriteState;
    }
    return false;
  };

  const updateQuery = (id: string, updates: Partial<SavedQuery>) => {
    updateFavorite(id, { ...updates, lastUsed: new Date() });
  };

  const deleteQuery = (id: string) => {
    removeFavorite(id);
  };

  const getFavorites = (): SavedQuery[] => {
    return favorites
      .filter((q) => q.isFavorite)
      .sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime());
  };

  const getHistory = (): SavedQuery[] => {
    return [...favorites].sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime());
  };

  const searchQueries = (term: string): SavedQuery[] => {
    const lower = term.toLowerCase();
    return favorites.filter(
      (q) =>
        q.query.toLowerCase().includes(lower) ||
        q.tags.some((tag) => tag.toLowerCase().includes(lower))
    );
  };

  const clearHistory = () => {
    setFavorites([]);
  };

  const addTag = (id: string, tag: string) => {
    const query = favorites.find((q) => q.id === id);
    if (query && !query.tags.includes(tag)) {
      updateFavorite(id, { tags: [...query.tags, tag] });
    }
  };

  const removeTag = (id: string, tag: string) => {
    const query = favorites.find((q) => q.id === id);
    if (query) {
      updateFavorite(id, { tags: query.tags.filter((t) => t !== tag) });
    }
  };

  return {
    queries: favorites,
    isLoaded,
    addQuery,
    toggleFavorite,
    updateQuery,
    deleteQuery,
    getFavorites,
    getHistory,
    searchQueries,
    clearHistory,
    addTag,
    removeTag,
  };
}
