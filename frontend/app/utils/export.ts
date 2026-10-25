/**
 * Export utilities for query results and data
 * Supports CSV and JSON formats
 */

import { ChartData } from '../api';

interface ExportOptions {
  filename?: string;
  timestamp?: boolean;
}

/**
 * Convert chart data to CSV format
 */
export function convertToCSV(data: Record<string, unknown>[]): string {
  if (!data || data.length === 0) {
    return '';
  }

  const headers = Object.keys(data[0]);
  const rows = data.map((row) =>
    headers.map((header) => {
      const value = row[header];
      // Escape quotes and wrap in quotes if contains a comma, quote or newline
      if (typeof value === 'string' && /[",\r\n]/.test(value)) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      if (value !== null && typeof value === 'object') {
        return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
      }
      return value ?? '';
    })
  );

  return [
    headers.join(','),
    ...rows.map((row) => row.join(',')),
  ].join('\n');
}

/**
 * Download data as CSV file
 */
export function downloadCSV(
  data: Record<string, unknown>[],
  options: ExportOptions = {}
): void {
  const csv = convertToCSV(data);
  const filename =
    options.filename ||
    `export-${options.timestamp !== false ? new Date().toISOString().split('T')[0] : 'data'}.csv`;

  downloadFile(csv, filename, 'text/csv');
}

/**
 * Download data as JSON file
 */
export function downloadJSON(
  data: Record<string, unknown>[],
  chartData: ChartData,
  options: ExportOptions = {}
): void {
  const jsonData = {
    exportedAt: new Date().toISOString(),
    chartType: chartData.chart_type,
    xAxisKey: chartData.x_axis_key,
    yAxisKey: chartData.y_axis_key,
    rowCount: data.length,
    data,
  };

  const json = JSON.stringify(jsonData, null, 2);
  const filename =
    options.filename ||
    `export-${options.timestamp !== false ? new Date().toISOString().split('T')[0] : 'data'}.json`;

  downloadFile(json, filename, 'application/json');
}

/**
 * Copy data to clipboard as JSON
 */
export async function copyToClipboard(
  data: Record<string, unknown>[],
  format: 'json' | 'csv' = 'json'
): Promise<boolean> {
  try {
    let text: string;

    if (format === 'csv') {
      text = data
        .map((row) =>
          Object.values(row)
            .map((v) => (typeof v === 'string' ? `"${v}"` : v))
            .join(',')
        )
        .join('\n');
    } else {
      text = JSON.stringify(data, null, 2);
    }

    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/**
 * Export full conversation as JSON
 */
export interface ConversationExport {
  exportedAt: string;
  version: string;
  messages: Array<{
    timestamp: string;
    type: 'user' | 'assistant';
    content: string;
    sqlQuery?: string;
    chartType?: string;
  }>;
}

export function exportConversation(
  conversationJson: string,
  options: ExportOptions = {}
): void {
  const filename =
    options.filename ||
    `conversation-${options.timestamp !== false ? new Date().toISOString().split('T')[0] : ''}.json`;

  downloadFile(conversationJson, filename, 'application/json');
}

/**
 * Helper function to trigger file download
 */
function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Format number for display
 */
export function formatNumber(value: unknown): string {
  if (typeof value === 'number') {
    if (value >= 1_000_000) {
      return (value / 1_000_000).toFixed(1) + 'M';
    } else if (value >= 1_000) {
      return (value / 1_000).toFixed(1) + 'K';
    }
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(value);
}

/**
 * Format date for display
 */
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
}
