'use client';

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { TrendingUp, BarChart3, Clock } from 'lucide-react';
import { useChatStore, Message, SavedQuery } from '../store';
import { useFavorites } from '../hooks/useFavorites';

interface AnalyticsDashboardProps {
  isDark: boolean;
}

const SQL_KEYWORDS: [string, RegExp][] = [
  ['JOIN', /\bjoin\b/i],
  ['WHERE', /\bwhere\b/i],
  ['GROUP BY', /\bgroup\s+by\b/i],
  ['ORDER BY', /\border\s+by\b/i],
  ['WITH (CTE)', /^\s*with\b/i],
];

const StatCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string | number;
  isDark: boolean;
}> = ({ icon, label, value, isDark }) => (
  <div
    className={`p-4 rounded-lg border ${
      isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'
    }`}
  >
    <div className="flex items-center gap-3">
      <div
        className={`p-2 rounded ${
          isDark
            ? 'bg-gray-800 text-blue-400'
            : 'bg-blue-100 text-blue-600'
        }`}
      >
        {icon}
      </div>
      <div>
        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          {label}
        </p>
        <p
          className={`text-2xl font-bold ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}
        >
          {value}
        </p>
      </div>
    </div>
  </div>
);

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  isDark,
}) => {
  const { messages } = useChatStore();
  const { queries } = useFavorites();

  const chartColors = isDark
    ? ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6']
    : ['#2563eb', '#db2777', '#059669', '#d97706', '#7c3aed'];

  const analytics = useMemo(() => {
    const history = queries;
    const totalQueries = messages.filter(
      (m: Message) => m.type === 'user'
    ).length;
    const responses = messages
      .filter((m: Message) => m.type === 'assistant' && m.agentResponse)
      .map((m: Message) => m.agentResponse!);
    const successfulQueries = responses.length;
    const uniqueQueries = new Set(
      history.map((h: SavedQuery) => h.query.toLowerCase().trim())
    ).size;

    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    });

    const queriesByDay = last7Days.map((day) => ({
      day,
      queries: history.filter((h: SavedQuery) => {
        const historyDate = new Date(h.lastUsed).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        });
        return historyDate === day;
      }).length,
    }));

    // Count SQL features used in the generated queries (the saved questions
    // are natural language, so they don't contain SQL keywords)
    const queryKeywords: Record<string, number> = {};
    responses.forEach((r) => {
      SQL_KEYWORDS.forEach(([name, pattern]) => {
        if (pattern.test(r.sql_query)) {
          queryKeywords[name] = (queryKeywords[name] || 0) + 1;
        }
      });
    });

    const queryTypeData = Object.entries(queryKeywords).map(([type, count]) => ({
      name: type,
      value: count,
    }));

    const timings = responses
      .map((r) => r.execution_time_ms)
      .filter((t): t is number => typeof t === 'number');
    const avgResponseTime =
      timings.length > 0
        ? `${(timings.reduce((sum, t) => sum + t, 0) / timings.length / 1000).toFixed(2)}s`
        : '—';

    return {
      totalQueries,
      successfulQueries,
      uniqueQueries,
      successRate:
        totalQueries > 0
          ? ((successfulQueries / totalQueries) * 100).toFixed(1)
          : '0.0',
      avgResponseTime,
      queriesByDay,
      queryTypeData,
    };
  }, [messages, queries]);

  return (
    <div
      className={`flex flex-col h-full border-l overflow-y-auto ${
        isDark ? 'border-gray-700 bg-gray-950' : 'border-gray-200 bg-gray-50'
      }`}
    >
      {/* Header */}
      <div
        className={`p-4 border-b sticky top-0 ${
          isDark
            ? 'border-gray-700 bg-gray-900'
            : 'border-gray-200 bg-white'
        }`}
      >
        <div className="flex items-center gap-2">
          <BarChart3
            size={20}
            className={isDark ? 'text-purple-400' : 'text-purple-500'}
          />
          <h2 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Analytics
          </h2>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            icon={<TrendingUp size={20} />}
            label="Total Queries"
            value={analytics.totalQueries}
            isDark={isDark}
          />
          <StatCard
            icon={<Clock size={20} />}
            label="Success Rate"
            value={`${analytics.successRate}%`}
            isDark={isDark}
          />
          <StatCard
            icon={<BarChart3 size={20} />}
            label="Unique Queries"
            value={analytics.uniqueQueries}
            isDark={isDark}
          />
          <StatCard
            icon={<Clock size={20} />}
            label="Avg Response"
            value={analytics.avgResponseTime}
            isDark={isDark}
          />
        </div>

        {/* Queries Over Time */}
        {analytics.queriesByDay.some((d) => d.queries > 0) && (
          <div
            className={`p-4 rounded-lg border ${
              isDark
                ? 'bg-gray-900 border-gray-700'
                : 'bg-white border-gray-200'
            }`}
          >
            <h3
              className={`text-sm font-semibold mb-3 ${
                isDark ? 'text-white' : 'text-gray-900'
              }`}
            >
              Queries Over Time
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={analytics.queriesByDay}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={isDark ? '#374151' : '#e5e7eb'}
                />
                <XAxis
                  dataKey="day"
                  stroke={isDark ? '#9ca3af' : '#6b7280'}
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  stroke={isDark ? '#9ca3af' : '#6b7280'}
                  style={{ fontSize: '12px' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#1f2937' : '#f9fafb',
                    border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                    borderRadius: '6px',
                    color: isDark ? '#f3f4f6' : '#111827',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="queries"
                  stroke={chartColors[0]}
                  strokeWidth={2}
                  dot={{ fill: chartColors[0], r: 4 }}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Query Keywords Distribution */}
        {analytics.queryTypeData.length > 0 && (
          <div
            className={`p-4 rounded-lg border ${
              isDark
                ? 'bg-gray-900 border-gray-700'
                : 'bg-white border-gray-200'
            }`}
          >
            <h3
              className={`text-sm font-semibold mb-3 ${
                isDark ? 'text-white' : 'text-gray-900'
              }`}
            >
              SQL Features Used
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={analytics.queryTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  isAnimationActive={false}
                >
                  {analytics.queryTypeData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={chartColors[index % chartColors.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#1f2937' : '#f9fafb',
                    border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                    borderRadius: '6px',
                    color: isDark ? '#f3f4f6' : '#111827',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Empty State */}
        {analytics.totalQueries === 0 && (
          <div
            className={`flex flex-col items-center justify-center p-6 rounded-lg text-center ${
              isDark ? 'text-gray-500' : 'text-gray-400'
            }`}
          >
            <BarChart3 size={32} className="mb-2 opacity-50" />
            <p className="text-sm font-medium">No analytics data yet</p>
            <p className="text-xs mt-1 opacity-75">
              Start querying to see analytics and insights
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
