// Define provider and model types
type Provider = 'openai' | 'anthropic' | 'gemini';
type ModelMap = {
  [key in Provider]: string[];
};

// Available models by provider - Updated with all latest models
export const AVAILABLE_MODELS: ModelMap = {
  openai: [
    // Latest GPT models
    'gpt-5',
    'gpt-5-mini', 
    'gpt-5-nano',
    'gpt-4.1',
    'gpt-4.1-mini',
    'gpt-4.1-nano',
    'gpt-4.1-2025-04-14',
    'gpt-4.5-preview',
    // O series models
    'o1',
    'o1-mini',
    'o1-pro',
    'o3',
    'o3-mini', 
    'o3-pro',
    'o4-mini',
    // Existing GPT-4 models
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4',
    'gpt-4-turbo',
    'gpt-3.5-turbo'
  ],
  anthropic: [
    // Latest Claude 4 models
    'claude-4-sonnet-20250514',
    'claude-4-opus-20250514',
    // Claude 3.7 models
    'claude-3-7-sonnet-20250219',
    // Existing Claude 3.5 models
    'claude-3-5-sonnet-20241022',
    'claude-3-5-haiku-20241022',
    // Legacy models
    'claude-3-opus-20240229'
  ],
  gemini: [
    // Latest Gemini 2.5 models
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    // Gemini 2.0 models
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    // Existing Gemini 1.5 models
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    // Legacy models
    'gemini-pro'
  ]
};

// Default configuration
const DEFAULT_PROVIDER = 'openai';
const DEFAULT_MODEL = 'gpt-4o-mini';
const DEFAULT_SYSTEM_MESSAGE = 'You are a helpful assistant.';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export class LlmService {
  private apiKey: string;
  
  constructor(apiKey: string = '') {
    this.apiKey = apiKey;
  }
  
  /**
   * Send a message to the LLM and get a response
   */
  async sendMessage(
    messages: ChatMessage[],
    provider: Provider = DEFAULT_PROVIDER,
    model: string = DEFAULT_MODEL,
    apiKey?: string
  ) {
    try {
      const key = apiKey || this.apiKey;
      
      if (!key) {
        throw new Error('API key is required');
      }

      // Validate model availability
      if (!AVAILABLE_MODELS[provider].includes(model)) {
        console.warn(`Model ${model} not found in available models for ${provider}. Using default.`);
        model = AVAILABLE_MODELS[provider][0];
      }
      
      // For now, we'll create a mock response since the emergentintegrations package is not available
      // In a real implementation, this would use the emergentintegrations library
      const response = await this.mockLLMResponse(messages, provider, model);
      
      return { success: true, data: response };
    } catch (error) {
      console.error('Error sending message to LLM:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  private async mockLLMResponse(messages: ChatMessage[], provider: Provider, model: string): Promise<string> {
    // This is a mock response for demonstration
    // In a real implementation, this would use the emergentintegrations library
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
    
    const lastMessage = messages[messages.length - 1]?.content || '';
    
    const mockResponses = [
      `Hello! I'm ${model} from ${provider}. I received your message: "${lastMessage}". How can I help you today?`,
      `Thank you for your question about "${lastMessage}". As ${model}, I'm here to assist you with any information or tasks you need.`,
      `I understand you're asking about "${lastMessage}". Let me provide you with a helpful response using ${model} from ${provider}.`,
      `That's an interesting question about "${lastMessage}". Using ${model}, I can help you explore this topic further.`
    ];
    
    return mockResponses[Math.floor(Math.random() * mockResponses.length)];
  }
}

// Export singleton instance
export const llmService = new LlmService();