import { NextResponse } from 'next/server';

// Railway deployment: backend runs on port 8001, frontend proxies API calls
const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:8001'  // Internal communication in Railway
  : (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001');

export async function GET(request, { params }) {
  const path = params.path ? params.path.join('/') : '';
  
  try {
    // Forward GET requests to Python backend
    const response = await fetch(`${BACKEND_URL}/api/${path}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Backend proxy error (GET):', error);
    return NextResponse.json({ error: 'Backend service unavailable' }, { status: 503 });
  }
}

export async function POST(request, { params }) {
  try {
    const path = params.path ? params.path.join('/') : '';
    const body = await request.json();
    
    // Forward POST requests to Python backend
    const response = await fetch(`${BACKEND_URL}/api/${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
    
  } catch (error) {
    console.error('Backend proxy error (POST):', error);
    return NextResponse.json({ 
      error: 'Backend service unavailable',
      details: error.message 
    }, { status: 503 });
  }
}