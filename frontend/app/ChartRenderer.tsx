'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartData } from './api';

const COLORS = [
  '#3b82f6',
  '#ef4444',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
  '#f97316',
];

interface ChartRendererProps {
  chartData: ChartData;
}

const formatNumber = (value: unknown) =>
  typeof value === 'number'
    ? value.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : String(value);

// Category labels longer than this are cut with an ellipsis; the tooltip
// still shows the full value
const MAX_LABEL_CHARS = 32;
const AXIS_TICK = { fontSize: 12 };
// Generous width of one 12px character, used to size the category axis
// (Recharts wraps a label onto two lines if the axis is too narrow)
const CHAR_WIDTH_PX = 7.5;
const MAX_CATEGORY_AXIS_PX = 250;

const truncateLabel = (value: unknown) => {
  const label = String(value ?? '');
  return label.length > MAX_LABEL_CHARS ? `${label.slice(0, MAX_LABEL_CHARS - 1)}…` : label;
};

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return formatNumber(value);
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData }) => {
  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500 dark:text-gray-400">
        <p>No data available to display</p>
      </div>
    );
  }

  switch (chartData.chart_type) {
    case 'bar': {
      const labels = chartData.data.map((row) => truncateLabel(row[chartData.x_axis_key]));
      const longestLabel = Math.max(...labels.map((label) => label.length));

      // Recharts silently drops x-axis labels that would overlap. With many or
      // long category names, lay the bars out horizontally so every label gets
      // its own row; otherwise keep columns but force every label to render.
      if (labels.length > 6 || longestLabel > 12) {
        return (
          <ResponsiveContainer width="100%" height={Math.max(250, labels.length * 36 + 60)}>
            <BarChart data={chartData.data} layout="vertical" margin={{ left: 8, right: 24 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={formatNumber} tick={AXIS_TICK} />
              <YAxis
                type="category"
                dataKey={chartData.x_axis_key}
                width={Math.min(longestLabel * CHAR_WIDTH_PX + 16, MAX_CATEGORY_AXIS_PX)}
                interval={0}
                tick={AXIS_TICK}
                tickFormatter={truncateLabel}
              />
              <Tooltip formatter={formatNumber} />
              <Legend />
              <Bar
                dataKey={chartData.y_axis_key}
                fill="#3b82f6"
                name={chartData.y_axis_key}
              />
            </BarChart>
          </ResponsiveContainer>
        );
      }

      return (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey={chartData.x_axis_key}
              interval={0}
              tick={AXIS_TICK}
              tickFormatter={truncateLabel}
            />
            <YAxis tickFormatter={formatNumber} tick={AXIS_TICK} />
            <Tooltip formatter={formatNumber} />
            <Legend />
            <Bar
              dataKey={chartData.y_axis_key}
              fill="#3b82f6"
              name={chartData.y_axis_key}
            />
          </BarChart>
        </ResponsiveContainer>
      );
    }

    case 'line':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={chartData.x_axis_key} />
            <YAxis tickFormatter={formatNumber} />
            <Tooltip formatter={formatNumber} />
            <Legend />
            <Line
              type="monotone"
              dataKey={chartData.y_axis_key}
              stroke="#3b82f6"
              name={chartData.y_axis_key}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      );

    case 'pie':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={chartData.data}
              dataKey={chartData.y_axis_key}
              nameKey={chartData.x_axis_key}
              cx="50%"
              cy="50%"
              outerRadius={120}
              label
            >
              {chartData.data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={formatNumber} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );

    case 'table': {
      const columns = Object.keys(chartData.data[0] || {});
      return (
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 dark:bg-gray-800">
              <tr>
                {columns.map((key) => (
                  <th
                    key={key}
                    className="border-b border-gray-200 dark:border-gray-700 px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200"
                  >
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {chartData.data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={
                    rowIndex % 2 === 0
                      ? 'bg-white dark:bg-gray-900'
                      : 'bg-gray-50 dark:bg-gray-800/50'
                  }
                >
                  {columns.map((key) => (
                    <td
                      key={key}
                      className={`border-b border-gray-200 dark:border-gray-700 px-4 py-2 text-gray-600 dark:text-gray-300 ${
                        typeof row[key] === 'number' ? 'text-right tabular-nums' : ''
                      }`}
                    >
                      {formatCell(row[key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    default:
      return (
        <div className="flex items-center justify-center p-8 text-gray-500 dark:text-gray-400">
          <p>Unknown chart type: {chartData.chart_type}</p>
        </div>
      );
  }
};
