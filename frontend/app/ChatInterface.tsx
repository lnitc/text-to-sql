'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useChatStore, Message } from './store';
import { ChatMessage } from './ChatMessage';
import { Send, Trash2, Download, Moon, Sun, Sidebar, Clock, Star, BarChart3 } from 'lucide-react';
import { sendQuery, checkHealth } from './api';
import { useMessagePersistence } from './hooks/useMessagePersistence';
import { useDarkMode } from './hooks/useDarkMode';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { FavoritesPanel } from './components/FavoritesPanel';
import { HistoryPanel } from './components/HistoryPanel';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';

type SidebarPanel = 'favorites' | 'history' | 'analytics' | null;

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, addMessage, removeMessage, clearMessages, setIsLoading } = useChatStore();
  const [inputValue, setInputValue] = useState('');
  const [backendReady, setBackendReady] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [sidebarPanel, setSidebarPanel] = useState<SidebarPanel>(null);
  const { downloadConversation } = useMessagePersistence();
  const { isDark, toggleDarkMode } = useDarkMode();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Setup keyboard shortcuts
  useKeyboardShortcuts([]);

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

    // Add loading placeholder with unique ID
    const loadingMessageId = `loading-${Date.now()}`;
    const loadingMessage: Message = {
      id: loadingMessageId,
      type: 'assistant',
      content: 'Processing your query...',
      timestamp: new Date(),
    };
    addMessage(loadingMessage);

    try {
      const response = await sendQuery(userQuery);

      // Remove loading message
      removeMessage(loadingMessageId);

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: '',
        agentResponse: response,
        userQuery: userQuery,
        timestamp: new Date(),
      };
      addMessage(assistantMessage);
    } catch (error) {
      // Remove loading message
      removeMessage(loadingMessageId);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        userQuery: userQuery,
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectQuery = (query: string) => {
    setInputValue(query);
  };

  const handleApplyQuery = (query: string) => {
    setInputValue(query);
    setSidebarPanel(null);
  };

  const toggleSidebar = (panel: SidebarPanel) => {
    setSidebarPanel(sidebarPanel === panel ? null : panel);
  };

  return (
    <div className={`flex h-screen ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`${isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} border-b px-6 py-4 shadow-sm`}>
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Text-to-SQL Data Analyst</h1>
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'} mt-1`}>
                Ask questions about BigQuery data in natural language
              </p>
            </div>
            <div className="flex items-center gap-4">
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
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                title="Toggle dark mode"
              >
                {isDark ? <Sun size={20} className="text-yellow-500" /> : <Moon size={20} className="text-gray-600" />}
              </button>
            </div>
          </div>
        </div>

        {/* Backend Error Alert */}
        {backendError && (
          <div className={`${isDark ? 'bg-red-900/20 border-red-800' : 'bg-red-50 border-red-200'} border-b px-6 py-3`}>
            <p className={`text-sm ${isDark ? 'text-red-400' : 'text-red-700'}`}>{backendError}</p>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <div className={`flex flex-col items-center justify-center h-full text-center ${isDark ? 'text-gray-400' : 'text-gray-500'} py-20`}>
                <div className="text-6xl mb-4">📊</div>
                <h2 className={`text-2xl font-semibold ${isDark ? 'text-white' : 'text-gray-700'} mb-2`}>
                  Welcome to Text-to-SQL Data Analyst
                </h2>
                <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'} mb-6 max-w-md`}>
                  Ask natural language questions about the BigQuery ecommerce dataset. The AI
                  will generate SQL, execute it, and visualize the results.
                </p>
                <div className={`text-left ${isDark ? 'bg-gray-800' : 'bg-gray-100'} p-4 rounded-lg max-w-md text-sm`}>
                  <p className={`font-semibold ${isDark ? 'text-gray-200' : 'text-gray-700'} mb-2`}>Example questions:</p>
                  <ul className={`space-y-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
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
        <div className={`${isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} border-t px-6 py-4 shadow-lg`}>
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask a question about the data..."
                disabled={isLoading || !backendReady}
                className={`flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  isDark
                    ? 'border-gray-600 bg-gray-800 text-white placeholder-gray-400 disabled:bg-gray-700 disabled:text-gray-500'
                    : 'border-gray-300 bg-white text-gray-900 placeholder-gray-400 disabled:bg-gray-100 disabled:text-gray-500'
                } disabled:cursor-not-allowed`}
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
                  onClick={downloadConversation}
                  className={`px-4 py-3 rounded-lg transition flex items-center gap-2 ${
                    isDark
                      ? 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                  title="Download conversation"
                >
                  <Download size={18} />
                </button>
              )}
              {messages.length > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    clearMessages();
                    setBackendError(null);
                  }}
                  className={`px-4 py-3 rounded-lg transition flex items-center gap-2 ${
                    isDark
                      ? 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                  title="Clear all messages"
                >
                  <Trash2 size={18} />
                </button>
              )}
            </form>
            <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mt-2`}>
              Backend: {backendReady ? 'Connected' : 'Disconnected'} | API Base: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            </p>
          </div>
        </div>
      </div>

      {/* Sidebar Toggle Buttons */}
      <div className={`w-12 border-l flex flex-col items-center py-4 gap-2 ${
        isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-white'
      }`}>
        <button
          onClick={() => toggleSidebar('favorites')}
          className={`p-3 rounded-lg transition ${
            sidebarPanel === 'favorites'
              ? isDark ? 'bg-yellow-600 text-white' : 'bg-yellow-500 text-white'
              : isDark ? 'hover:bg-gray-800 text-gray-400 hover:text-gray-200' : 'hover:bg-gray-100 text-gray-600'
          }`}
          title="Favorites"
        >
          <Star size={20} />
        </button>

        <button
          onClick={() => toggleSidebar('history')}
          className={`p-3 rounded-lg transition ${
            sidebarPanel === 'history'
              ? isDark ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white'
              : isDark ? 'hover:bg-gray-800 text-gray-400 hover:text-gray-200' : 'hover:bg-gray-100 text-gray-600'
          }`}
          title="History"
        >
          <Clock size={20} />
        </button>

        <button
          onClick={() => toggleSidebar('analytics')}
          className={`p-3 rounded-lg transition ${
            sidebarPanel === 'analytics'
              ? isDark ? 'bg-purple-600 text-white' : 'bg-purple-500 text-white'
              : isDark ? 'hover:bg-gray-800 text-gray-400 hover:text-gray-200' : 'hover:bg-gray-100 text-gray-600'
          }`}
          title="Analytics"
        >
          <BarChart3 size={20} />
        </button>

        {/* Query Builder button hidden for now - will be enabled in future phase */}
      </div>

      {/* Sidebar Panel */}
      {sidebarPanel && (
        <div className="w-80 border-l flex flex-col overflow-hidden">
          {sidebarPanel === 'favorites' && (
            <FavoritesPanel onSelectQuery={handleSelectQuery} isDark={isDark} />
          )}
          {sidebarPanel === 'history' && (
            <HistoryPanel onSelectQuery={handleSelectQuery} isDark={isDark} />
          )}
          {sidebarPanel === 'analytics' && (
            <AnalyticsDashboard isDark={isDark} />
          )}
        </div>
      )}
    </div>
  );
};
