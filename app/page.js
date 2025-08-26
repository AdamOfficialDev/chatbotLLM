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

// Memoized Message Component for better performance
const MessageItem = memo(({ message, index, darkMode }) => {
  return (
    <div
      className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      {message.role === 'assistant' && (
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <Bot className="h-5 w-5 text-white" />
        </div>
      )}
      
      <div
        className={`max-w-[70%] p-4 rounded-2xl ${
          message.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
        }`}
      >
        {message.role === 'user' ? (
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap m-0 leading-relaxed text-white">
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
  const [sidebarOpen, setSidebarOpen] = useState(true);
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

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

  // Save chat messages to localStorage
  useEffect(() => {
    try {
      if (messages.length > 0) {
        localStorage.setItem('chat_messages', JSON.stringify(messages));
      }
    } catch (error) {
      console.error('Error saving messages to localStorage:', error);
    }
  }, [messages]);

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

    const userMessage = { role: 'user', content: input };
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
        content: data.response 
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
    <div className={`flex h-screen ${darkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col`}>
        {sidebarOpen && (
          <>
            {/* Sidebar Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <Button 
                onClick={newChat}
                className="w-full justify-start gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <Plus className="h-4 w-4" />
                New Chat
              </Button>
            </div>

            {/* Model Configuration */}
            <div className="p-4 space-y-4 border-b border-gray-200 dark:border-gray-700">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Provider</label>
                <Select value={provider} onValueChange={setProvider}>
                  <SelectTrigger className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
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
                  <SelectTrigger className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels[provider]?.map(m => (
                      <SelectItem key={m} value={m}>{m}</SelectItem>
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
                  className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 font-mono text-xs"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Get your universal key from Profile → Universal Key
                </p>
              </div>

              {/* Current Configuration */}
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="text-xs">{provider}</Badge>
                <Badge variant="outline" className="text-xs">{model}</Badge>
                {apiKey && <Badge variant="default" className="text-xs">API Key Set</Badge>}
              </div>
            </div>

            {/* Chat History Placeholder */}
            <div className="flex-1 p-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Recent Chats</h3>
              <div className="space-y-2">
                <div className="text-xs text-gray-500 dark:text-gray-400 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  Previous conversations will appear here
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white dark:bg-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-600 dark:text-gray-400"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <h1 className="text-lg font-semibold text-gray-800 dark:text-gray-200">AI Chatbot</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDarkMode(!darkMode)}
              className="text-gray-600 dark:text-gray-400"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="icon"
                onClick={clearChat}
                className="text-gray-600 dark:text-gray-400"
              >
                <RotateCcw className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-4xl mx-auto p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-20">
                  <div className="bg-gradient-to-br from-blue-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center mb-6">
                    <Bot className="h-8 w-8 text-white" />
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
                    How can I help you today?
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 max-w-md">
                    I'm powered by the latest AI models from OpenAI, Anthropic, and Google. 
                    Choose your preferred model and start chatting!
                  </p>
                </div>
              ) : (
                <div className="space-y-6 pb-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.role === 'assistant' && (
                        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[70%] p-4 rounded-2xl ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white rounded-br-md'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
                        }`}
                      >
                        {message.role === 'user' ? (
                          <div className="prose prose-sm max-w-none">
                            <p className="whitespace-pre-wrap m-0 leading-relaxed text-white">
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
                  ))}

                  {loading && (
                    <div className="flex gap-4 justify-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-2xl rounded-bl-md">
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

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-4">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                <span className="text-sm font-medium">Error:</span>
                <span className="text-sm">{error}</span>
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="max-w-4xl mx-auto p-4">
            <form onSubmit={handleSubmit} className="flex gap-3 items-end">
              <div className="flex-1 relative">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={apiKey ? "Message AI..." : "Enter API key first..."}
                  disabled={loading || !apiKey}
                  className="min-h-[44px] pr-12 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-xl resize-none"
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
                className="h-11 w-11 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
              AI can make mistakes. Consider checking important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}