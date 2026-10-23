'use client';

import React, { useState } from 'react';
import { Star, Trash2, Copy, Search, X, Tag } from 'lucide-react';
import { useFavorites } from '../hooks/useFavorites';
import { SavedQuery } from '../store';

interface FavoritesPanelProps {
  onSelectQuery: (query: string) => void;
  isDark: boolean;
}

export const FavoritesPanel: React.FC<FavoritesPanelProps> = ({
  onSelectQuery,
  isDark,
}) => {
  const { getFavorites, deleteQuery, searchQueries, removeTag, addTag } =
    useFavorites();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const favorites = getFavorites();

  const filteredFavorites = selectedTag
    ? favorites.filter((fav: SavedQuery) => fav.tags?.includes(selectedTag))
    : searchTerm
      ? searchQueries(searchTerm)
      : favorites;

  const allTags = Array.from(
    new Set(favorites.flatMap((fav: SavedQuery) => fav.tags || []))
  ).sort();

  const handleSelectQuery = (query: string) => {
    onSelectQuery(query);
  };

  const handleCopyQuery = (e: React.MouseEvent, query: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(query);
  };

  const handleRemove = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    deleteQuery(id);
  };

  return (
    <div
      className={`flex flex-col h-full border-l ${
        isDark ? 'border-gray-700 bg-gray-950' : 'border-gray-200 bg-gray-50'
      }`}
    >
      {/* Header */}
      <div
        className={`p-4 border-b ${
          isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-white'
        }`}
      >
        <div className="flex items-center gap-2 mb-3">
          <Star
            size={20}
            className={isDark ? 'text-yellow-400' : 'text-yellow-500'}
            fill="currentColor"
          />
          <h2 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Favorites ({favorites.length})
          </h2>
        </div>

        {/* Search Box */}
        <div className="relative">
          <Search
            size={16}
            className={`absolute left-3 top-1/2 -translate-y-1/2 ${
              isDark ? 'text-gray-600' : 'text-gray-400'
            }`}
          />
          <input
            type="text"
            placeholder="Search queries..."
            value={searchTerm}
            onChange={e => {
              setSearchTerm(e.target.value);
              setSelectedTag(null);
            }}
            className={`w-full pl-9 pr-3 py-2 rounded text-sm border ${
              isDark
                ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-500'
                : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400'
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
        </div>
      </div>

      {/* Tags Filter */}
      {allTags.length > 0 && (
        <div
          className={`px-4 py-2 border-b overflow-x-auto flex gap-2 ${
            isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-white'
          }`}
        >
          {allTags.map((tag: string) => (
            <button
              key={tag}
              onClick={() => {
                setSelectedTag(selectedTag === tag ? null : tag);
                setSearchTerm('');
              }}
              className={`px-2 py-1 rounded text-xs whitespace-nowrap font-medium transition ${
                selectedTag === tag
                  ? isDark
                    ? 'bg-blue-600 text-white'
                    : 'bg-blue-500 text-white'
                  : isDark
                    ? 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      {/* Favorites List */}
      <div className="flex-1 overflow-y-auto">
        {filteredFavorites.length === 0 ? (
          <div
            className={`flex flex-col items-center justify-center h-full text-center p-4 ${
              isDark ? 'text-gray-500' : 'text-gray-400'
            }`}
          >
            <Star size={32} className="mb-2 opacity-50" />
            <p className="text-sm font-medium">
              {favorites.length === 0 ? 'No favorites yet' : 'No matches found'}
            </p>
            <p className="text-xs mt-1 opacity-75">
              {favorites.length === 0
                ? 'Save queries to access them quickly'
                : 'Try adjusting your search'}
            </p>
          </div>
        ) : (
          <div className="space-y-2 p-3">
            {filteredFavorites.map((favorite: SavedQuery) => (
              <div
                key={favorite.id}
                onClick={() => handleSelectQuery(favorite.query)}
                className={`p-3 rounded cursor-pointer transition group ${
                  isDark
                    ? 'bg-gray-800 hover:bg-gray-700 border border-gray-700'
                    : 'bg-white hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <p
                  className={`text-sm font-medium mb-1 line-clamp-2 ${
                    isDark ? 'text-gray-100' : 'text-gray-900'
                  }`}
                >
                  {favorite.query}
                </p>

                {favorite.tags && favorite.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {favorite.tags.map((tag: string) => (
                      <span
                        key={tag}
                        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs ${
                          isDark
                            ? 'bg-gray-700 text-gray-300'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        <Tag size={10} />
                        {tag}
                        <button
                          onClick={e => {
                            e.stopPropagation();
                            removeTag(favorite.id, tag);
                          }}
                          className="ml-1 hover:opacity-70"
                        >
                          <X size={10} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                <p
                  className={`text-xs mb-2 ${
                    isDark ? 'text-gray-500' : 'text-gray-500'
                  }`}
                >
                  {new Date(favorite.lastUsed).toLocaleDateString()} at{' '}
                  {new Date(favorite.lastUsed).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                  <button
                    onClick={e => handleCopyQuery(e, favorite.query)}
                    className={`flex-1 flex items-center justify-center gap-1 px-2 py-1 rounded text-xs font-medium transition ${
                      isDark
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                  >
                    <Copy size={12} />
                    Copy
                  </button>
                  <button
                    onClick={e => handleRemove(e, favorite.id)}
                    className={`flex items-center justify-center px-2 py-1 rounded text-xs font-medium transition ${
                      isDark
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-red-500 hover:bg-red-600 text-white'
                    }`}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
