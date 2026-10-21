'use client';

import React, { useMemo } from 'react';
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

export const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData }) => {
  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>No data available to display</p>
      </div>
    );
  }

  const colorMap = useMemo(() => {
    const map: Record<string, string> = {};
    chartData.data.forEach((item: any, index: number) => {
      const key = String(item[chartData.x_axis_key]);
      map[key] = COLORS[index % COLORS.length];
    });
    return map;
  }, [chartData]);

  try {
    switch (chartData.chart_type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={chartData.x_axis_key} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey={chartData.y_axis_key}
                fill="#3b82f6"
                name={chartData.y_axis_key}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={chartData.x_axis_key} />
              <YAxis />
              <Tooltip />
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
                {chartData.data.map((_entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'table':
        return (
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  {Object.keys(chartData.data[0] || {}).map((key) => (
                    <th
                      key={key}
                      className="border-b border-gray-200 px-4 py-2 text-left font-semibold text-gray-700"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {chartData.data.map((row: any, rowIndex: number) => (
                  <tr
                    key={rowIndex}
                    className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                  >
                    {Object.values(row).map((value: any, cellIndex: number) => (
                      <td
                        key={cellIndex}
                        className="border-b border-gray-200 px-4 py-2 text-gray-600"
                      >
                        {typeof value === 'number'
                          ? value.toLocaleString(undefined, {
                              maximumFractionDigits: 2,
                            })
                          : String(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      default:
        return (
          <div className="flex items-center justify-center p-8 text-gray-500">
            <p>Unknown chart type: {chartData.chart_type}</p>
          </div>
        );
    }
  } catch (error) {
    return (
      <div className="flex items-center justify-center p-8 text-red-500">
        <p>Error rendering chart: {String(error)}</p>
      </div>
    );
  }
};
