'use client';

import { useState, useEffect } from 'react';

export interface SavedQuery {
  id: string;
  query: string;
  tags: string[];
  isFavorite: boolean;
  createdAt: Date;
  lastUsed: Date;
  resultCount: number;
}

const STORAGE_KEY = 'text-to-sql-queries';
const MAX_HISTORY = 20;
const MAX_FAVORITES = 50;

/**
 * Hook for managing saved queries, favorites, and history
 */
export function useFavorites() {
  const [queries, setQueries] = useState<SavedQuery[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    loadQueries();
    setIsLoaded(true);
  }, []);

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
        setQueries(withDates);
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

    const updated = [newQuery, ...queries].slice(0, MAX_HISTORY);
    setQueries(updated);
    saveToStorage(updated);
    return newQuery;
  };

  const toggleFavorite = (id: string): boolean => {
    const updated = queries.map((q) =>
      q.id === id ? { ...q, isFavorite: !q.isFavorite } : q
    );

    // Ensure we don't exceed max favorites
    const favoriteCount = updated.filter((q) => q.isFavorite).length;
    if (favoriteCount > MAX_FAVORITES) {
      const oldestFav = updated.find((q) => q.isFavorite);
      if (oldestFav) {
        oldestFav.isFavorite = false;
      }
    }

    setQueries(updated);
    saveToStorage(updated);
    return updated.find((q) => q.id === id)?.isFavorite || false;
  };

  const updateQuery = (id: string, updates: Partial<SavedQuery>) => {
    const updated = queries.map((q) =>
      q.id === id ? { ...q, ...updates, lastUsed: new Date() } : q
    );
    setQueries(updated);
    saveToStorage(updated);
  };

  const deleteQuery = (id: string) => {
    const updated = queries.filter((q) => q.id !== id);
    setQueries(updated);
    saveToStorage(updated);
  };

  const getFavorites = (): SavedQuery[] => {
    return queries.filter((q) => q.isFavorite).sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime());
  };

  const getHistory = (): SavedQuery[] => {
    return [...queries].sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime());
  };

  const searchQueries = (term: string): SavedQuery[] => {
    const lower = term.toLowerCase();
    return queries.filter(
      (q) =>
        q.query.toLowerCase().includes(lower) ||
        q.tags.some((tag) => tag.toLowerCase().includes(lower))
    );
  };

  const clearHistory = () => {
    setQueries([]);
    saveToStorage([]);
  };

  const addTag = (id: string, tag: string) => {
    const query = queries.find((q) => q.id === id);
    if (query && !query.tags.includes(tag)) {
      updateQuery(id, { tags: [...query.tags, tag] });
    }
  };

  const removeTag = (id: string, tag: string) => {
    const query = queries.find((q) => q.id === id);
    if (query) {
      updateQuery(id, { tags: query.tags.filter((t) => t !== tag) });
    }
  };

  return {
    queries,
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
