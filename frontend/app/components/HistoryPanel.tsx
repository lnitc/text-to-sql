'use client';

import React, { useState } from 'react';
import { Clock, Copy, Search, Star } from 'lucide-react';
import { useFavorites } from '../hooks/useFavorites';
import { SavedQuery } from '../store';

interface HistoryPanelProps {
  onSelectQuery: (query: string) => void;
  isDark: boolean;
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({ onSelectQuery, isDark }) => {
  const { getHistory, getFavorites, toggleFavorite, addQuery } = useFavorites();
  const [searchTerm, setSearchTerm] = useState('');

  const history = getHistory();
  const favorites = getFavorites();

  const filteredHistory = searchTerm
    ? history.filter((item: SavedQuery) =>
        item.query.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : history;

  const isFavorite = (id: string): boolean => {
    return favorites.some((fav: SavedQuery) => fav.id === id);
  };

  const handleSelectQuery = (query: string) => {
    addQuery(query);
    onSelectQuery(query);
  };

  const handleCopyQuery = (e: React.MouseEvent, query: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(query);
  };

  const handleToggleFavorite = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    toggleFavorite(id);
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
          <Clock
            size={20}
            className={isDark ? 'text-blue-400' : 'text-blue-500'}
          />
          <h2 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            History ({history.length})
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
            placeholder="Search history..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className={`w-full pl-9 pr-3 py-2 rounded text-sm border ${
              isDark
                ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-500'
                : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400'
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto">
        {filteredHistory.length === 0 ? (
          <div
            className={`flex flex-col items-center justify-center h-full text-center p-4 ${
              isDark ? 'text-gray-500' : 'text-gray-400'
            }`}
          >
            <Clock size={32} className="mb-2 opacity-50" />
            <p className="text-sm font-medium">
              {history.length === 0 ? 'No history yet' : 'No matches found'}
            </p>
            <p className="text-xs mt-1 opacity-75">
              {history.length === 0
                ? 'Your queries will appear here'
                : 'Try adjusting your search'}
            </p>
          </div>
        ) : (
          <div className="space-y-2 p-3">
            {filteredHistory.map((item: SavedQuery) => (
              <div
                key={item.id}
                onClick={() => handleSelectQuery(item.query)}
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
                  {item.query}
                </p>

                <p
                  className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}
                >
                  {new Date(item.lastUsed).toLocaleDateString()} at{' '}
                  {new Date(item.lastUsed).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition">
                  <button
                    onClick={e => handleCopyQuery(e, item.query)}
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
                    onClick={e => handleToggleFavorite(e, item.id)}
                    className={`flex items-center justify-center px-2 py-1 rounded text-xs font-medium transition ${
                      isFavorite(item.id)
                        ? isDark
                          ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                          : 'bg-yellow-500 hover:bg-yellow-600 text-white'
                        : isDark
                          ? 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                          : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
                    }`}
                  >
                    <Star
                      size={12}
                      fill={isFavorite(item.id) ? 'currentColor' : 'none'}
                    />
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
