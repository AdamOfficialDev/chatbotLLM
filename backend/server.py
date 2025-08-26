from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import uuid
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
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

# MongoDB connection - Railway compatible
MONGO_URL = os.getenv("MONGO_URL") or os.getenv("MONGODB_URL") or "mongodb://localhost:27017/chatbot_db"
client = MongoClient(MONGO_URL)
db = client.chatbot_db
chats_collection = db.chats
sessions_collection = db.sessions

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
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        # Existing Gemini 1.5 models
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        # Legacy models
        "gemini-pro"
    ]
}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    apiKey: str
    session_id: str = None  # Optional session ID for context

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ModelsResponse(BaseModel):
    models: Dict[str, List[str]]

@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running!"}

@app.get("/api/models", response_model=ModelsResponse)
async def get_models():
    """Get all available models for each provider"""
    return ModelsResponse(models=AVAILABLE_MODELS)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Validate provider and model
        if request.provider not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail=f"Provider {request.provider} not supported")
        
        if request.model not in AVAILABLE_MODELS[request.provider]:
            # Use first available model if requested model not found
            print(f"Model {request.model} not found for {request.provider}. Using default.")
            request.model = AVAILABLE_MODELS[request.provider][0]

        # Use existing session ID or generate new one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create LLM chat instance with better configuration
        chat = LlmChat(
            api_key=request.apiKey,
            session_id=session_id,
            system_message="You are a helpful AI assistant. Provide clear, accurate, and comprehensive responses. Always complete your responses fully without cutting off mid-sentence. Use markdown formatting when appropriate for better readability."
        )
        
        # Configure the model
        chat.with_model(request.provider, request.model)
        
        # Get the last user message for the current request
        last_user_message = request.messages[-1]
        if last_user_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # If we have conversation history and this is continuing a session,
        # we need to send all messages in the correct format
        if len(request.messages) > 1:
            # Create a comprehensive conversation context by building the full conversation
            conversation_text = ""
            for i, msg in enumerate(request.messages[:-1]):
                if msg.role == "user":
                    conversation_text += f"User: {msg.content}\n\n"
                elif msg.role == "assistant":
                    conversation_text += f"Assistant: {msg.content}\n\n"
            
            # Add context to the current user message
            current_message = f"Previous conversation:\n{conversation_text}Current question: {last_user_message.content}"
            user_message = UserMessage(text=current_message)
        else:
            user_message = UserMessage(text=last_user_message.content)
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        # Store conversation in database
        chat_record = {
            "_id": str(uuid.uuid4()),
            "session_id": session_id,
            "provider": request.provider,
            "model": request.model,
            "messages": [msg.dict() for msg in request.messages],
            "response": response,
            "timestamp": datetime.utcnow(),
            "api_key_used": "emergent_universal" if request.apiKey.startswith("sk-emergent") else "custom"
        }
        
        chats_collection.insert_one(chat_record)
        
        return ChatResponse(response=response, session_id=session_id)
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get chat history for a session"""
    try:
        chats = list(chats_collection.find({"session_id": session_id}))
        for chat in chats:
            chat["_id"] = str(chat["_id"])
        return {"session_id": session_id, "chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "emergent_key": "configured" if os.getenv("EMERGENT_LLM_KEY") else "not_configured"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    # Railway will provide PORT environment variable
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)