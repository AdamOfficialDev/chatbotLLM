'use client';

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Bot, User, Send, Settings, MessageSquare, Plus, Menu, Moon, Sun, RotateCcw } from 'lucide-react';
import { AVAILABLE_MODELS } from '@/lib/llm-service.ts';
import MarkdownMessage from '@/components/MarkdownMessage';
import { memo } from 'react';

// Memoized Message Component for better performance with responsive design
const MessageItem = memo(({ message, index, darkMode }) => {
  return (
    <div
      className={`flex gap-3 sm:gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      {message.role === 'assistant' && (
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <Bot className="h-5 w-5 text-white" />
        </div>
      )}
      
      <div
        className={`max-w-[85%] sm:max-w-[75%] lg:max-w-[70%] p-3 sm:p-4 rounded-2xl ${
          message.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
        }`}
      >
        {message.role === 'user' ? (
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap m-0 leading-relaxed text-white text-sm sm:text-base">
              {message.content}
            </p>
          </div>
        ) : (
          <MarkdownMessage content={message.content} darkMode={darkMode} />
        )}
      </div>
      
      {message.role === 'user' && (
        <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <User className="h-5 w-5 text-white" />
        </div>
      )}
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default function ChatbotApp() {
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('gpt-4o-mini');
  const [apiKey, setApiKey] = useState('');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false); // Default closed on mobile
  const [availableModels, setAvailableModels] = useState(AVAILABLE_MODELS);
  const [sessionId, setSessionId] = useState(null); // Add session management
  const messagesEndRef = useRef(null);

  // Update model when provider changes and fetch available models
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/models');
        const data = await response.json();
        if (data.models && data.models[provider]) {
          setAvailableModels(data.models);
          setModel(data.models[provider][0]);
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
        // Fallback to static models
        setModel(AVAILABLE_MODELS[provider][0]);
      }
    };
    
    fetchModels();
  }, [provider]);

  // Scroll to bottom when messages change - optimized with debouncing
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  useEffect(() => {
    // Debounce scroll to bottom to prevent excessive scrolling
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages.length, scrollToBottom]); // Only trigger on message count change

  // Load API key and chat data from localStorage
  useEffect(() => {
    try {
      const savedKey = localStorage.getItem('emergent_api_key');
      const savedDarkMode = localStorage.getItem('dark_mode') === 'true';
      const savedMessages = localStorage.getItem('chat_messages');
      const savedSessionId = localStorage.getItem('current_session_id');
      const savedProvider = localStorage.getItem('selected_provider');
      const savedModel = localStorage.getItem('selected_model');

      if (savedKey) {
        setApiKey(savedKey);
      }
      if (savedMessages) {
        const parsedMessages = JSON.parse(savedMessages);
        setMessages(parsedMessages);
      }
      if (savedSessionId) {
        setSessionId(savedSessionId);
      }
      if (savedProvider && ['openai', 'anthropic', 'gemini'].includes(savedProvider)) {
        setProvider(savedProvider);
      }
      if (savedModel) {
        setModel(savedModel);
      }
      
      setDarkMode(savedDarkMode);
    } catch (error) {
      console.error('Error loading data from localStorage:', error);
      // Clear corrupted data
      localStorage.removeItem('chat_messages');
      localStorage.removeItem('current_session_id');
    }
  }, []);

  // Save chat messages to localStorage - throttled for performance
  const saveMessagesToStorage = useCallback((messagesToSave) => {
    try {
      if (messagesToSave.length > 0) {
        localStorage.setItem('chat_messages', JSON.stringify(messagesToSave));
      }
    } catch (error) {
      console.error('Error saving messages to localStorage:', error);
    }
  }, []);

  // Throttled localStorage save
  useEffect(() => {
    if (messages.length > 0) {
      const timeoutId = setTimeout(() => {
        saveMessagesToStorage(messages);
      }, 1000); // Save after 1 second of inactivity
      return () => clearTimeout(timeoutId);
    }
  }, [messages, saveMessagesToStorage]);

  // Save session ID to localStorage
  useEffect(() => {
    try {
      if (sessionId) {
        localStorage.setItem('current_session_id', sessionId);
      }
    } catch (error) {
      console.error('Error saving session ID:', error);
    }
  }, [sessionId]);

  // Save provider and model preferences
  useEffect(() => {
    localStorage.setItem('selected_provider', provider);
  }, [provider]);

  useEffect(() => {
    localStorage.setItem('selected_model', model);
  }, [model]);

  // Save API key to localStorage
  useEffect(() => {
    if (apiKey) {
      localStorage.setItem('emergent_api_key', apiKey);
    }
  }, [apiKey]);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem('dark_mode', darkMode.toString());
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !apiKey.trim()) return;

    const timestamp = Date.now();
    const userMessage = { 
      role: 'user', 
      content: input,
      timestamp
    };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const requestBody = {
        messages: newMessages,
        provider,
        model,
        apiKey
      };

      // Include session_id if we have one for context continuity
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      // Store session_id for context continuity
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const assistantMessage = { 
        role: 'assistant', 
        content: data.response,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message);
      // Remove the user message if there was an error
      setMessages(messages);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
    setSessionId(null); // Reset session for new conversation
    
    // Clear chat data from localStorage
    try {
      localStorage.removeItem('chat_messages');
      localStorage.removeItem('current_session_id');
    } catch (error) {
      console.error('Error clearing chat data from localStorage:', error);
    }
  };

  const newChat = () => {
    clearChat();
  };

  return (
    <div className={`flex h-screen ${darkMode ? 'dark' : ''} relative`}>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Responsive Sidebar */}
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} 
        lg:translate-x-0 
        ${sidebarOpen ? 'w-80 sm:w-96' : 'w-0 lg:w-80'} 
        fixed lg:relative 
        z-50 lg:z-auto 
        h-full 
        transition-all duration-300 ease-in-out
        bg-gray-50 dark:bg-gray-900 
        border-r border-gray-200 dark:border-gray-700 
        overflow-hidden flex flex-col
      `}>
        <div className={`${sidebarOpen ? 'block' : 'hidden'} lg:block h-full flex flex-col`}>
          <>
            {/* Sidebar Header */}
            <div className="p-3 sm:p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3 lg:mb-0">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 lg:hidden">
                  Settings
                </h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSidebarOpen(false)}
                  className="lg:hidden text-gray-600 dark:text-gray-400"
                >
                  <Menu className="h-5 w-5" />
                </Button>
              </div>
              <Button 
                onClick={newChat}
                className="w-full justify-start gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 min-h-[44px]"
              >
                <Plus className="h-4 w-4" />
                New Chat
              </Button>
            </div>

            {/* Model Configuration */}
            <div className="p-3 sm:p-4 space-y-4 border-b border-gray-200 dark:border-gray-700">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Provider</label>
                <Select value={provider} onValueChange={setProvider}>
                  <SelectTrigger className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 min-h-[44px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="anthropic">Anthropic</SelectItem>
                    <SelectItem value="gemini">Google Gemini</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Model</label>
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 min-h-[44px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels[provider]?.map(m => (
                      <SelectItem key={m} value={m} className="text-sm">{m}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">API Key</label>
                <Input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your Emergent API key..."
                  className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 font-mono text-xs min-h-[44px]"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Get your universal key from Profile → Universal Key
                </p>
              </div>

              {/* Current Configuration */}
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="text-xs">{provider}</Badge>
                <Badge variant="outline" className="text-xs break-all">{model}</Badge>
                {apiKey && <Badge variant="default" className="text-xs">API Key Set</Badge>}
              </div>
            </div>

            {/* Chat History Placeholder */}
            <div className="flex-1 p-3 sm:p-4 overflow-y-auto">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Recent Chats</h3>
              <div className="space-y-2">
                <div className="text-xs text-gray-500 dark:text-gray-400 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  Previous conversations will appear here
                </div>
              </div>
            </div>
          </div>
        </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 min-w-0">
        {/* Responsive Header */}
        <div className="flex items-center justify-between p-3 sm:p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-600 dark:text-gray-400 flex-shrink-0 min-h-[44px] min-w-[44px]"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2 min-w-0">
              <MessageSquare className="h-5 w-5 text-gray-600 dark:text-gray-400 flex-shrink-0" />
              <h1 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200 truncate">
                AI Chatbot
              </h1>
            </div>
          </div>
          
          <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDarkMode(!darkMode)}
              className="text-gray-600 dark:text-gray-400 min-h-[44px] min-w-[44px]"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="icon"
                onClick={clearChat}
                className="text-gray-600 dark:text-gray-400 min-h-[44px] min-w-[44px]"
              >
                <RotateCcw className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>

        {/* Chat Messages Area - Responsive */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-4xl mx-auto p-3 sm:p-4 lg:p-6">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-10 sm:py-20">
                  <div className="bg-gradient-to-br from-blue-500 to-purple-600 w-12 h-12 sm:w-16 sm:h-16 rounded-full flex items-center justify-center mb-4 sm:mb-6">
                    <Bot className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                  </div>
                  <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2 px-4">
                    How can I help you today?
                  </h2>
                  <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 max-w-md px-4">
                    I'm powered by the latest AI models from OpenAI, Anthropic, and Google. 
                    Choose your preferred model and start chatting!
                  </p>
                </div>
              ) : (
                <div className="space-y-4 sm:space-y-6 pb-4">
                  {/* Use memoized MessageItem components for better performance */}
                  {messages.map((message, index) => (
                    <MessageItem 
                      key={`${message.timestamp || index}-${index}`} 
                      message={message} 
                      index={index} 
                      darkMode={darkMode} 
                    />
                  ))}

                  {loading && (
                    <div className="flex gap-3 sm:gap-4 justify-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-700 p-3 sm:p-4 rounded-2xl rounded-bl-md">
                        <div className="flex items-center gap-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                          <span className="text-sm text-gray-500 dark:text-gray-400">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Responsive Error Display */}
        {error && (
          <div className="mx-3 sm:mx-4 mb-3 sm:mb-4">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <div className="flex items-start gap-2 text-red-600 dark:text-red-400">
                <span className="text-sm font-medium flex-shrink-0">Error:</span>
                <span className="text-sm break-words">{error}</span>
              </div>
            </div>
          </div>
        )}

        {/* Responsive Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="max-w-4xl mx-auto p-3 sm:p-4 lg:p-6">
            <form onSubmit={handleSubmit} className="flex gap-2 sm:gap-3 items-end">
              <div className="flex-1 relative min-w-0">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={apiKey ? "Message AI..." : "Enter API key first..."}
                  disabled={loading || !apiKey}
                  className="min-h-[48px] sm:min-h-[52px] pr-12 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-xl resize-none text-sm sm:text-base"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                />
              </div>
              <Button 
                type="submit" 
                disabled={loading || !input.trim() || !apiKey}
                className="h-12 w-12 sm:h-13 sm:w-13 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 flex-shrink-0"
              >
                <Send className="h-4 w-4 sm:h-5 sm:w-5" />
              </Button>
            </form>
            <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-2 text-center px-2">
              AI can make mistakes. Consider checking important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}