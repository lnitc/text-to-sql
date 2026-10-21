'use client';

import React, { useState } from 'react';
import { Message } from './store';
import { ChartRenderer } from './ChartRenderer';
import { Copy, ChevronDown, ChevronUp } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [showSql, setShowSql] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopySql = () => {
    if (message.agentResponse?.sql_query) {
      navigator.clipboard.writeText(message.agentResponse.sql_query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
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
        <div className="max-w-2xl bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <p className="text-sm text-red-700 font-medium">Error</p>
          <p className="text-sm text-red-600 mt-1">{message.error}</p>
        </div>
      </div>
    );
  }

  if (!message.agentResponse) {
    return (
      <div className="flex justify-start mb-4">
        <div className="max-w-2xl bg-gray-100 rounded-lg px-4 py-3 animate-pulse">
          <p className="text-sm text-gray-600">Processing your query...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-4xl w-full bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Thought Process */}
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <p className="text-sm font-medium text-gray-700">Analysis</p>
          <p className="text-sm text-gray-600 mt-1">{message.agentResponse.thought_process}</p>
        </div>

        {/* SQL Query */}
        <div className="px-4 py-3 border-b border-gray-200">
          <button
            onClick={() => setShowSql(!showSql)}
            className="flex items-center gap-2 w-full text-left font-medium text-gray-700 hover:text-gray-900 transition-colors"
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
              className="ml-auto p-1 hover:bg-gray-200 rounded transition-colors"
              title="Copy SQL"
            >
              <Copy size={16} className={copied ? 'text-green-600' : 'text-gray-600'} />
            </button>
          </button>

          {showSql && (
            <pre className="mt-3 bg-gray-900 text-gray-100 p-3 rounded overflow-x-auto text-xs font-mono">
              {message.agentResponse.sql_query}
            </pre>
          )}
        </div>

        {/* Chart Visualization */}
        <div className="px-4 py-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Visualization</p>
          <ChartRenderer chartData={message.agentResponse.chart} />
        </div>
      </div>
    </div>
  );
};
