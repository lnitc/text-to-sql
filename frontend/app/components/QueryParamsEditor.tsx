'use client';

import React, { useState } from 'react';
import { X, Plus, RotateCcw } from 'lucide-react';

interface QueryParam {
  id: string;
  key: string;
  value: string;
  type: 'string' | 'number' | 'date' | 'boolean';
}

interface QueryParamsEditorProps {
  onApply: (query: string) => void;
  isDark: boolean;
  onClose: () => void;
}

const COMMON_PARAMS = [
  { key: 'limit', type: 'number', description: 'Limit results' },
  { key: 'offset', type: 'number', description: 'Skip results' },
  { key: 'startDate', type: 'date', description: 'Start date' },
  { key: 'endDate', type: 'date', description: 'End date' },
  { key: 'includeMetrics', type: 'boolean', description: 'Include metrics' },
];

// Must stay below the backend's 1000-character user_query limit
const MAX_QUERY_LENGTH = 1000;

const newParamId = () => Math.random().toString(36).slice(2, 11);

/** "startDate" / "start_date" -> "start date" */
const formatKey = (key: string) =>
  key
    .trim()
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .toLowerCase();

export const QueryParamsEditor: React.FC<QueryParamsEditorProps> = ({
  onApply,
  isDark,
  onClose,
}) => {
  const [params, setParams] = useState<QueryParam[]>([]);
  const [baseQuery, setBaseQuery] = useState('');

  const addParam = () => {
    setParams([
      ...params,
      {
        id: newParamId(),
        key: '',
        value: '',
        type: 'string',
      },
    ]);
  };

  const removeParam = (id: string) => {
    setParams(params.filter(p => p.id !== id));
  };

  const updateParam = (
    id: string,
    field: keyof Omit<QueryParam, 'id'>,
    value: string
  ) => {
    setParams(
      params.map(p => {
        if (p.id !== id) return p;
        // A value entered for one type (e.g. text) is usually invalid for
        // another (e.g. a date input), so reset it when the type changes
        if (field === 'type') {
          return { ...p, type: value as QueryParam['type'], value: value === 'boolean' ? 'true' : '' };
        }
        return { ...p, [field]: value };
      })
    );
  };

  /**
   * The result is sent to the LLM as a natural-language question, so render
   * parameters as readable constraints: "Top brands (limit: 10, start date: 2024-01-01)"
   */
  const buildQuery = (): string => {
    if (!baseQuery.trim()) return '';

    const query = baseQuery.trim();
    const filledParams = params.filter(p => p.key.trim() && p.value.trim());

    if (filledParams.length === 0) return query;

    const paramStrings = filledParams.map(p => {
      const value = p.type === 'boolean' ? (p.value === 'true' ? 'yes' : 'no') : p.value.trim();
      return `${formatKey(p.key)}: ${value}`;
    });

    return `${query} (${paramStrings.join(', ')})`;
  };

  const builtQuery = buildQuery();
  const isTooLong = builtQuery.length > MAX_QUERY_LENGTH;
  const canApply = builtQuery.trim().length > 0 && !isTooLong;

  const handleApply = () => {
    if (canApply) {
      onApply(builtQuery);
      onClose();
    }
  };

  const handleReset = () => {
    setParams([]);
    setBaseQuery('');
  };

  return (
    <div
      className={`flex flex-col h-full border-l ${
        isDark ? 'border-gray-700 bg-gray-950' : 'border-gray-200 bg-gray-50'
      }`}
    >
      {/* Header */}
      <div
        className={`p-4 border-b flex items-center justify-between ${
          isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-white'
        }`}
      >
        <h2 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Query Builder
        </h2>
        <button
          onClick={onClose}
          title="Close"
          className={`p-1 rounded ${
            isDark ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-200 text-gray-600'
          }`}
        >
          <X size={20} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Base Query */}
        <div>
          <label
            className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}
          >
            Base Query
          </label>
          <textarea
            value={baseQuery}
            onChange={e => setBaseQuery(e.target.value)}
            placeholder="e.g. Top 10 brands by revenue"
            rows={4}
            maxLength={MAX_QUERY_LENGTH}
            className={`w-full px-3 py-2 rounded border text-sm resize-none ${
              isDark
                ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-500'
                : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400'
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
        </div>

        {/* Parameters */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label
              className={`block text-sm font-medium ${
                isDark ? 'text-gray-300' : 'text-gray-700'
              }`}
            >
              Parameters
            </label>
            <button
              onClick={addParam}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition ${
                isDark
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              <Plus size={14} />
              Add
            </button>
          </div>

          <div className="space-y-2">
            {params.map(param => (
              <div key={param.id} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Key"
                  value={param.key}
                  onChange={e => updateParam(param.id, 'key', e.target.value)}
                  className={`flex-1 min-w-0 px-2 py-1 rounded text-sm border ${
                    isDark
                      ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-500'
                      : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400'
                  } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                />
                {param.type === 'boolean' ? (
                  <select
                    value={param.value}
                    onChange={e => updateParam(param.id, 'value', e.target.value)}
                    className={`flex-1 min-w-0 px-2 py-1 rounded text-sm border ${
                      isDark
                        ? 'border-gray-600 bg-gray-800 text-white'
                        : 'border-gray-300 bg-white text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  >
                    <option value="true">True</option>
                    <option value="false">False</option>
                  </select>
                ) : (
                  <input
                    type={
                      param.type === 'number'
                        ? 'number'
                        : param.type === 'date'
                          ? 'date'
                          : 'text'
                    }
                    placeholder="Value"
                    value={param.value}
                    onChange={e => updateParam(param.id, 'value', e.target.value)}
                    className={`flex-1 min-w-0 px-2 py-1 rounded text-sm border ${
                      isDark
                        ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-500'
                        : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                )}
                <select
                  value={param.type}
                  onChange={e => updateParam(param.id, 'type', e.target.value)}
                  className={`px-2 py-1 rounded text-sm border ${
                    isDark
                      ? 'border-gray-600 bg-gray-800 text-white'
                      : 'border-gray-300 bg-white text-gray-900'
                  } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                >
                  <option value="string">String</option>
                  <option value="number">Number</option>
                  <option value="date">Date</option>
                  <option value="boolean">Boolean</option>
                </select>
                <button
                  onClick={() => removeParam(param.id)}
                  title="Remove parameter"
                  className={`p-1 rounded transition ${
                    isDark
                      ? 'hover:bg-red-600 text-red-400'
                      : 'hover:bg-red-100 text-red-500'
                  }`}
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>

          {/* Quick Templates */}
          <div className="mt-3">
            <p
              className={`text-xs font-medium mb-2 ${
                isDark ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              Quick Templates:
            </p>
            <div className="flex flex-wrap gap-2">
              {COMMON_PARAMS.map(p => (
                <button
                  key={p.key}
                  onClick={() => {
                    const exists = params.some(param => param.key === p.key);
                    if (!exists) {
                      setParams([
                        ...params,
                        {
                          id: newParamId(),
                          key: p.key,
                          value: p.type === 'boolean' ? 'true' : '',
                          type: p.type as QueryParam['type'],
                        },
                      ]);
                    }
                  }}
                  className={`px-2 py-1 rounded text-xs font-medium transition ${
                    isDark
                      ? 'bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-600 border border-gray-300'
                  }`}
                >
                  {p.description}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Preview */}
        {builtQuery && (
          <div>
            <label
              className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-gray-300' : 'text-gray-700'
              }`}
            >
              Preview
            </label>
            <div
              className={`p-3 rounded text-sm break-words ${
                isDark
                  ? 'bg-gray-800 text-gray-100 border border-gray-700'
                  : 'bg-gray-100 text-gray-900 border border-gray-200'
              }`}
            >
              <code>{builtQuery}</code>
            </div>
            {isTooLong && (
              <p className="mt-1 text-xs text-red-500">
                Query is {builtQuery.length} characters; the limit is {MAX_QUERY_LENGTH}.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer Buttons */}
      <div
        className={`p-4 border-t flex gap-2 ${
          isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-white'
        }`}
      >
        <button
          onClick={handleReset}
          className={`flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded font-medium transition ${
            isDark
              ? 'bg-gray-700 hover:bg-gray-600 text-gray-100'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-900'
          }`}
        >
          <RotateCcw size={16} />
          Reset
        </button>
        <button
          onClick={handleApply}
          disabled={!canApply}
          className={`flex-1 px-3 py-2 rounded font-medium transition ${
            canApply
              ? isDark
                ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                : 'bg-blue-500 hover:bg-blue-600 text-white cursor-pointer'
              : isDark
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Apply Query
        </button>
      </div>
    </div>
  );
};
