'use client';

import React, { useState } from 'react';
import { Message } from './store';
import { ChartRenderer } from './ChartRenderer';
import { Copy, ChevronDown, ChevronUp, Download, FileJson, FileText } from 'lucide-react';
import { downloadCSV, downloadJSON, copyToClipboard } from './utils/export';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [showSql, setShowSql] = useState(false);
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleCopySql = () => {
    if (message.agentResponse?.sql_query) {
      navigator.clipboard.writeText(message.agentResponse.sql_query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportCSV = async () => {
    if (message.agentResponse?.chart.data) {
      setExporting(true);
      try {
        downloadCSV(message.agentResponse.chart.data, message.agentResponse.chart);
      } finally {
        setExporting(false);
      }
    }
  };

  const handleExportJSON = async () => {
    if (message.agentResponse?.chart.data) {
      setExporting(true);
      try {
        downloadJSON(message.agentResponse.chart.data, message.agentResponse.chart);
      } finally {
        setExporting(false);
      }
    }
  };

  const handleCopyData = async (format: 'json' | 'csv') => {
    if (message.agentResponse?.chart.data) {
      const success = await copyToClipboard(message.agentResponse.chart.data, format);
      if (success) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    }
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-xs lg:max-w-md bg-blue-600 text-white rounded-lg px-4 py-2">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="flex justify-start mb-4">
        <div className="max-w-2xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3">
          <p className="text-sm text-red-700 dark:text-red-400 font-medium">Error</p>
          <p className="text-sm text-red-600 dark:text-red-300 mt-1">{message.error}</p>
        </div>
      </div>
    );
  }

  if (!message.agentResponse) {
    return (
      <div className="flex justify-start mb-4">
        <div className="max-w-2xl bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3 animate-pulse">
          <p className="text-sm text-gray-600 dark:text-gray-400">Processing your query...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-4xl w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        {/* Thought Process */}
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Analysis</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{message.agentResponse.thought_process}</p>
        </div>

        {/* SQL Query */}
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setShowSql(!showSql)}
            className="flex items-center gap-2 w-full text-left font-medium text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            {showSql ? (
              <ChevronUp size={18} />
            ) : (
              <ChevronDown size={18} />
            )}
            <span>SQL Query</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCopySql();
              }}
              className="ml-auto p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
              title="Copy SQL"
            >
              <Copy size={16} className={copied ? 'text-green-600' : 'text-gray-600 dark:text-gray-400'} />
            </button>
          </button>

          {showSql && (
            <pre className="mt-3 bg-gray-900 dark:bg-black text-gray-100 p-3 rounded overflow-x-auto text-xs font-mono">
              {message.agentResponse.sql_query}
            </pre>
          )}
        </div>

        {/* Chart Visualization */}
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Visualization</p>
            {/* Export Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleExportCSV}
                disabled={exporting}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 disabled:opacity-50"
                title="Export as CSV"
              >
                <FileText size={16} />
              </button>
              <button
                onClick={handleExportJSON}
                disabled={exporting}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 disabled:opacity-50"
                title="Export as JSON"
              >
                <FileJson size={16} />
              </button>
              <button
                onClick={() => handleCopyData('json')}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                title="Copy data to clipboard"
              >
                <Copy size={16} />
              </button>
            </div>
          </div>
          <ChartRenderer chartData={message.agentResponse.chart} />
        </div>
      </div>
    </div>
  );
};
