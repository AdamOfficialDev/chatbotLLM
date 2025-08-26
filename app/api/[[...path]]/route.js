import { NextResponse } from 'next/server';
import { llmService } from '../../../lib/llm-service.ts';

export async function GET(request) {
  return NextResponse.json({ message: 'AI Chatbot API is running!' });
}

export async function POST(request) {
  try {
    const body = await request.json();
    const { 
      messages, 
      provider = 'openai', 
      model = 'gpt-4o-mini',
      apiKey
    } = body;
    
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      );
    }

    if (!apiKey) {
      return NextResponse.json(
        { error: 'API key is required' },
        { status: 400 }
      );
    }
    
    const result = await llmService.sendMessage(
      messages,
      provider,
      model,
      apiKey
    );
    
    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 500 }
      );
    }
    
    return NextResponse.json({ response: result.data });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}