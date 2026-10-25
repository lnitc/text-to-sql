'use client';

import { useEffect } from 'react';
import { useChatStore, SavedQuery } from '../store';

const STORAGE_KEY = 'text-to-sql-queries';
const MAX_HISTORY = 20;
const MAX_FAVORITES = 50;

let hydrated = false;

/**
 * Load saved queries from localStorage into the store once, then keep
 * localStorage in sync with every later change. Many components use
 * useFavorites at the same time, so this runs once per page load rather
 * than once per hook instance.
 */
function hydrateFromStorage() {
  if (hydrated) return;
  hydrated = true;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as SavedQuery[];
      // Convert date strings back to Date objects
      useChatStore.getState().setFavorites(
        parsed.map((q) => ({
          ...q,
          createdAt: new Date(q.createdAt),
          lastUsed: new Date(q.lastUsed),
        }))
      );
    }
  } catch (error) {
    console.error('Failed to load queries:', error);
  }

  useChatStore.subscribe((state, prev) => {
    if (state.favorites === prev.favorites) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.favorites));
    } catch (error) {
      console.error('Failed to save queries:', error);
    }
  });
}

/**
 * Keep at most MAX_FAVORITES favorites and MAX_HISTORY non-favorite history
 * entries, dropping the least recently used ones.
 */
function prune(queries: SavedQuery[]): SavedQuery[] {
  const byRecency = [...queries].sort((a, b) => b.lastUsed.getTime() - a.lastUsed.getTime());
  const keep = new Set([
    ...byRecency.filter((q) => q.isFavorite).slice(0, MAX_FAVORITES).map((q) => q.id),
    ...byRecency.filter((q) => !q.isFavorite).slice(0, MAX_HISTORY).map((q) => q.id),
  ]);
  return queries.filter((q) => keep.has(q.id));
}

function newSavedQuery(query: string, tags: string[], isFavorite: boolean): SavedQuery {
  return {
    id: `q-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    query,
    tags,
    isFavorite,
    createdAt: new Date(),
    lastUsed: new Date(),
    resultCount: 0,
  };
}

/**
 * Hook for managing saved queries, favorites, and history
 */
export function useFavorites() {
  const { favorites, setFavorites, addFavorite, removeFavorite, updateFavorite } = useChatStore();

  // Load from localStorage on mount
  useEffect(() => {
    hydrateFromStorage();
  }, []);

  const addQuery = (query: string, tags: string[] = []): SavedQuery => {
    const newQuery = newSavedQuery(query, tags, false);
    addFavorite(newQuery);
    return newQuery;
  };

  const addQueryAsFavorite = (query: string, tags: string[] = []): SavedQuery => {
    const newQuery = newSavedQuery(query, tags, true);
    addFavorite(newQuery);
    return newQuery;
  };

  /**
   * Record that a query was run: bump an existing entry with the same text,
   * or add a new history entry.
   */
  const recordQuery = (query: string, resultCount = 0) => {
    const current = useChatStore.getState().favorites;
    const existing = current.find((q) => q.query === query);
    const updated = existing
      ? current.map((q) =>
          q.id === existing.id ? { ...q, lastUsed: new Date(), resultCount } : q
        )
      : [{ ...newSavedQuery(query, [], false), resultCount }, ...current];
    setFavorites(prune(updated));
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
    addQuery,
    addQueryAsFavorite,
    recordQuery,
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
