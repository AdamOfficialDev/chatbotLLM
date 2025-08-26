from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import uuid
import sqlite3
import json
from dotenv import load_dotenv
from datetime import datetime
import asyncio

# Load environment variables
load_dotenv()

# Import emergentintegrations
from emergentintegrations.llm.chat import LlmChat, UserMessage

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite Database setup - Simple and no configuration needed!
DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create chats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            model TEXT NOT NULL,
            provider TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Available models - comprehensive list from playbook
AVAILABLE_MODELS = {
    "openai": [
        # Latest GPT models
        "gpt-5",
        "gpt-5-mini", 
        "gpt-5-nano",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-4.1-2025-04-14",
        "gpt-4.5-preview",
        # O series models
        "o1",
        "o1-mini",
        "o1-pro",
        "o3",
        "o3-mini", 
        "o3-pro",
        "o4-mini",
        # Existing GPT-4 models
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ],
    "anthropic": [
        # Latest Claude 4 models
        "claude-4-sonnet-20250514",
        "claude-4-opus-20250514",
        # Claude 3.7 models
        "claude-3-7-sonnet-20250219",
        # Existing Claude 3.5 models
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        # Legacy models
        "claude-3-opus-20240229"
    ],
    "gemini": [
        # Latest Gemini 2.5 models
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        # Gemini 2.0 models
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp",
        # Legacy Gemini models
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
}

# Request models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    model: str
    provider: str
    apiKey: str = None  # Optional, uses Emergent Universal Key if not provided

class HealthResponse(BaseModel):
    status: str
    database: str
    emergent_key: str

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring"""
    try:
        # Test database connection
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        db_status = "connected" if len(tables) >= 2 else "no_tables"
        
        # Check Emergent API key
        emergent_key_status = "configured" if os.getenv("EMERGENT_LLM_KEY") else "not_configured"
        
        return HealthResponse(
            status="healthy",
            database=db_status,
            emergent_key=emergent_key_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/models")
async def get_models():
    """Get available models for all providers"""
    return AVAILABLE_MODELS

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with AI using emergentintegrations"""
    try:
        # Validate provider and model
        if request.provider not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        if request.model not in AVAILABLE_MODELS[request.provider]:
            raise HTTPException(status_code=400, detail="Invalid model for provider")

        # Create LLM chat client using new unified API
        provider_model = f"{request.provider}/{request.model}"
        llm_chat = LlmChat.from_provider(
            provider_model,
            api_key=request.apiKey or os.getenv("EMERGENT_LLM_KEY")
        )

        # Get conversation history for context
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_message, ai_response 
            FROM chats 
            WHERE session_id = ? 
            ORDER BY timestamp ASC 
            LIMIT 10
        """, (request.session_id,))
        
        history = cursor.fetchall()
        conn.close()

        # Build messages with conversation context
        messages = []
        
        # Add system message for better AI responses
        system_message = """You are a helpful AI assistant. Please provide complete, well-structured responses. 
        Use markdown formatting when appropriate for better readability. 
        Be comprehensive in your answers and maintain context throughout the conversation."""
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history for context
        for user_msg, ai_resp in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_resp})
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # Send to LLM
        user_message = UserMessage(content=request.message, context=messages[:-1])  # Exclude current message from context
        response = await llm_chat.send_message(user_message)
        
        if not response or not hasattr(response, 'content'):
            raise HTTPException(status_code=500, detail="Invalid response from AI")

        # Store chat in database
        chat_id = str(uuid.uuid4())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert chat record
        cursor.execute("""
            INSERT INTO chats (id, session_id, user_message, ai_response, model, provider, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, request.session_id, request.message, response.content, request.model, request.provider, datetime.utcnow()))
        
        # Update or create session
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, updated_at)
            VALUES (?, ?)
        """, (request.session_id, datetime.utcnow()))
        
        conn.commit()
        conn.close()

        return {"response": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_message, ai_response, model, provider, timestamp
            FROM chats 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        chats = []
        for row in cursor.fetchall():
            chats.append({
                "id": row[0],
                "user_message": row[1],
                "ai_response": row[2], 
                "model": row[3],
                "provider": row[4],
                "timestamp": row[5]
            })
        
        conn.close()
        return {"chats": chats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)