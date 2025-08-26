// Define provider and model types
type Provider = 'openai' | 'anthropic' | 'gemini';
type ModelMap = {
  [key in Provider]: string[];
};

// Available models by provider
export const AVAILABLE_MODELS: ModelMap = {
  openai: [
    'gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'
  ],
  anthropic: [
    'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'
  ],
  gemini: [
    'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'
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