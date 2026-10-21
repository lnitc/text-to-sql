'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useChatStore, Message } from './store';
import { ChatMessage } from './ChatMessage';
import { Send, Trash2 } from 'lucide-react';
import { sendQuery, checkHealth } from './api';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, addMessage, clearMessages, setIsLoading } = useChatStore();
  const [inputValue, setInputValue] = useState('');
  const [backendReady, setBackendReady] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      const isHealthy = await checkHealth();
      setBackendReady(isHealthy);
      if (!isHealthy) {
        setBackendError(
          'Backend is not responding. Make sure FastAPI server is running on port 8000.'
        );
      }
    };
    checkBackend();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading || !backendReady) {
      return;
    }

    const userQuery = inputValue.trim();
    setInputValue('');

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: userQuery,
      timestamp: new Date(),
    };
    addMessage(userMessage);

    // Start loading
    setIsLoading(true);

    // Add loading placeholder
    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      type: 'assistant',
      content: 'Processing your query...',
      timestamp: new Date(),
    };
    addMessage(loadingMessage);

    try {
      const response = await sendQuery(userQuery);

      // Remove loading message and add response
      messages.pop();

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: '',
        agentResponse: response,
        timestamp: new Date(),
      };
      addMessage(assistantMessage);
    } catch (error) {
      // Remove loading message and add error
      messages.pop();

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Text-to-SQL Data Analyst</h1>
            <p className="text-sm text-gray-600 mt-1">
              Ask questions about BigQuery data in natural language
            </p>
          </div>
          {backendReady ? (
            <div className="flex items-center gap-2 text-green-600">
              <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              <span className="text-sm font-medium">Backend Ready</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-red-600">
              <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Backend Error</span>
            </div>
          )}
        </div>
      </div>

      {/* Backend Error Alert */}
      {backendError && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3">
          <p className="text-sm text-red-700">{backendError}</p>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 py-20">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Welcome to Text-to-SQL Data Analyst
              </h2>
              <p className="text-gray-600 mb-6 max-w-md">
                Ask natural language questions about the BigQuery ecommerce dataset. The AI
                will generate SQL, execute it, and visualize the results.
              </p>
              <div className="text-left bg-gray-100 p-4 rounded-lg max-w-md text-sm">
                <p className="font-semibold text-gray-700 mb-2">Example questions:</p>
                <ul className="space-y-1 text-gray-600">
                  <li>• What were the top 5 product categories by revenue last month?</li>
                  <li>• How many orders were placed in the last 7 days?</li>
                  <li>• What is the average order value by product category?</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message: Message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about the data..."
              disabled={isLoading || !backendReady}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={isLoading || !backendReady || !inputValue.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"
            >
              <Send size={18} />
              Send
            </button>
            {messages.length > 0 && (
              <button
                type="button"
                onClick={() => {
                  clearMessages();
                  setBackendError(null);
                }}
                className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-2"
                title="Clear all messages"
              >
                <Trash2 size={18} />
              </button>
            )}
          </form>
          <p className="text-xs text-gray-500 mt-2">
            Backend: {backendReady ? 'Connected' : 'Disconnected'} | API Base: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
          </p>
        </div>
      </div>
    </div>
  );
};
