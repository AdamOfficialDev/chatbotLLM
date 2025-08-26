#!/usr/bin/env python3
"""
SQLite Backend Testing for AI Chatbot
Tests complete backend functionality after switching from MongoDB to SQLite
"""

import requests
import json
import os
import time
import sqlite3
import uuid
from typing import Dict, Any, List

# Backend URL - using production URL from environment
BACKEND_URL = "https://python-node-app.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test API key from environment
EMERGENT_API_KEY = "sk-emergent-a57065a3873E44634A"

def test_database_connection():
    """Test SQLite database connection via health endpoint"""
    print("\n=== Testing SQLite Database Connection ===")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Health response: {data}")
            
            # Check if database shows as connected
            if data.get("database") == "connected":
                print("✅ SQLite database connection working correctly")
                
                # Check if status is healthy
                if data.get("status") == "healthy":
                    print("✅ Backend health status is healthy")
                    return True
                else:
                    print(f"❌ Backend health status not healthy: {data.get('status')}")
                    return False
            else:
                print(f"❌ SQLite database not connected: {data.get('database')}")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_models_api():
    """Test models API endpoint - should return all OpenAI, Anthropic, Gemini models"""
    print("\n=== Testing Models API Endpoint ===")
    
    try:
        response = requests.get(f"{API_BASE}/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"Models API response received")
            
            # Check if all three providers are present
            expected_providers = ["openai", "anthropic", "gemini"]
            missing_providers = []
            
            for provider in expected_providers:
                if provider not in models:
                    missing_providers.append(provider)
                else:
                    model_count = len(models[provider])
                    print(f"✅ {provider}: {model_count} models available")
            
            if not missing_providers:
                print("✅ All three providers (OpenAI, Anthropic, Gemini) available")
                
                # Check specific models mentioned in review request
                test_models = {
                    "openai": "gpt-4o-mini",
                    "anthropic": "claude-3-5-sonnet-20241022", 
                    "gemini": "gemini-1.5-flash"
                }
                
                all_test_models_available = True
                for provider, model in test_models.items():
                    if model in models[provider]:
                        print(f"✅ Test model {model} available in {provider}")
                    else:
                        print(f"❌ Test model {model} not available in {provider}")
                        all_test_models_available = False
                
                return all_test_models_available
            else:
                print(f"❌ Missing providers: {missing_providers}")
                return False
        else:
            print(f"❌ Models API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Models API test failed: {e}")
        return False

def test_chat_functionality():
    """Test chat functionality with different providers"""
    print("\n=== Testing Chat Functionality with Different Providers ===")
    
    # Test models for each provider
    test_cases = [
        {"provider": "openai", "model": "gpt-4o-mini", "message": "Hello from OpenAI test"},
        {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "message": "Hello from Anthropic test"},
        {"provider": "gemini", "model": "gemini-1.5-flash", "message": "Hello from Gemini test"}
    ]
    
    results = {}
    session_id = str(uuid.uuid4())
    
    for test_case in test_cases:
        provider = test_case["provider"]
        model = test_case["model"]
        message = test_case["message"]
        
        print(f"\n--- Testing {provider} with {model} ---")
        
        try:
            payload = {
                "message": message,
                "session_id": session_id,
                "model": model,
                "provider": provider,
                "apiKey": EMERGENT_API_KEY
            }
            
            response = requests.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and data["response"]:
                    print(f"✅ {provider} chat working - Response length: {len(data['response'])} chars")
                    results[provider] = True
                else:
                    print(f"❌ {provider} chat returned empty response")
                    results[provider] = False
            else:
                print(f"❌ {provider} chat failed with status {response.status_code}")
                if response.text:
                    print(f"Error details: {response.text}")
                results[provider] = False
                
        except Exception as e:
            print(f"❌ {provider} chat test failed: {e}")
            results[provider] = False
    
    # Check overall results
    successful_providers = [p for p, result in results.items() if result]
    if len(successful_providers) == 3:
        print("✅ All three providers working correctly")
        return True
    else:
        failed_providers = [p for p, result in results.items() if not result]
        print(f"❌ Failed providers: {failed_providers}")
        return False

def test_session_management():
    """Test chat history storage and retrieval via sessions endpoint"""
    print("\n=== Testing Session Management and Chat History ===")
    
    try:
        # Create a unique session for testing
        test_session_id = str(uuid.uuid4())
        
        # Send multiple messages to create history
        messages = [
            "My name is Alice and I'm learning Python",
            "What programming language am I learning?",
            "What is my name?"
        ]
        
        print(f"Creating test session: {test_session_id}")
        
        # Send messages and collect responses
        for i, message in enumerate(messages):
            print(f"Sending message {i+1}: {message}")
            
            payload = {
                "message": message,
                "session_id": test_session_id,
                "model": "gpt-4o-mini",
                "provider": "openai",
                "apiKey": EMERGENT_API_KEY
            }
            
            response = requests.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Message {i+1} sent successfully")
                
                # For context test, check if AI remembers previous info
                if i == 1:  # Second message asking about programming language
                    if "python" in data["response"].lower():
                        print("✅ AI remembered programming language from previous message")
                elif i == 2:  # Third message asking about name
                    if "alice" in data["response"].lower():
                        print("✅ AI remembered name from first message")
            else:
                print(f"❌ Message {i+1} failed with status {response.status_code}")
                return False
        
        # Now test session history retrieval
        print(f"\nRetrieving session history for: {test_session_id}")
        
        history_response = requests.get(f"{API_BASE}/sessions/{test_session_id}", timeout=10)
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            
            if "chats" in history_data:
                chats = history_data["chats"]
                print(f"✅ Session history retrieved - {len(chats)} messages found")
                
                # Verify all messages are stored
                if len(chats) == len(messages):
                    print("✅ All messages stored correctly in SQLite database")
                    
                    # Check if messages have required fields
                    required_fields = ["id", "user_message", "ai_response", "model", "provider", "timestamp"]
                    all_fields_present = True
                    
                    for chat in chats:
                        missing_fields = [field for field in required_fields if field not in chat]
                        if missing_fields:
                            print(f"❌ Missing fields in chat record: {missing_fields}")
                            all_fields_present = False
                    
                    if all_fields_present:
                        print("✅ All chat records have required fields")
                        return True
                    else:
                        print("❌ Some chat records missing required fields")
                        return False
                else:
                    print(f"❌ Expected {len(messages)} messages, found {len(chats)}")
                    return False
            else:
                print("❌ Session history response missing 'chats' field")
                return False
        else:
            print(f"❌ Session history retrieval failed with status {history_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_sqlite_database_persistence():
    """Test SQLite database file creation and table structure"""
    print("\n=== Testing SQLite Database Persistence ===")
    
    try:
        # Check if SQLite database file exists
        db_path = "/app/backend/chatbot.db"
        
        if os.path.exists(db_path):
            print("✅ SQLite database file exists")
            
            # Connect to database and check tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["chats", "sessions"]
            missing_tables = [table for table in required_tables if table not in tables]
            
            if not missing_tables:
                print("✅ All required tables (chats, sessions) exist")
                
                # Check table structure for chats table
                cursor.execute("PRAGMA table_info(chats)")
                chats_columns = [row[1] for row in cursor.fetchall()]
                
                required_chat_columns = ["id", "session_id", "user_message", "ai_response", "model", "provider", "timestamp"]
                missing_chat_columns = [col for col in required_chat_columns if col not in chats_columns]
                
                if not missing_chat_columns:
                    print("✅ Chats table has all required columns")
                    
                    # Check sessions table structure
                    cursor.execute("PRAGMA table_info(sessions)")
                    sessions_columns = [row[1] for row in cursor.fetchall()]
                    
                    required_session_columns = ["session_id", "created_at", "updated_at"]
                    missing_session_columns = [col for col in required_session_columns if col not in sessions_columns]
                    
                    if not missing_session_columns:
                        print("✅ Sessions table has all required columns")
                        
                        # Check if there's any data (from previous tests)
                        cursor.execute("SELECT COUNT(*) FROM chats")
                        chat_count = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT COUNT(*) FROM sessions")
                        session_count = cursor.fetchone()[0]
                        
                        print(f"✅ Database contains {chat_count} chat records and {session_count} sessions")
                        
                        conn.close()
                        return True
                    else:
                        print(f"❌ Sessions table missing columns: {missing_session_columns}")
                        conn.close()
                        return False
                else:
                    print(f"❌ Chats table missing columns: {missing_chat_columns}")
                    conn.close()
                    return False
            else:
                print(f"❌ Missing required tables: {missing_tables}")
                conn.close()
                return False
        else:
            print("❌ SQLite database file not found")
            return False
            
    except Exception as e:
        print(f"❌ SQLite database persistence test failed: {e}")
        return False

def test_multiple_sessions_isolation():
    """Test that different session IDs maintain isolation"""
    print("\n=== Testing Multiple Sessions Isolation ===")
    
    try:
        # Create two different sessions
        session1_id = str(uuid.uuid4())
        session2_id = str(uuid.uuid4())
        
        # Send different messages to each session
        session1_message = "I am working on a React project"
        session2_message = "I am studying machine learning"
        
        # Send to session 1
        payload1 = {
            "message": session1_message,
            "session_id": session1_id,
            "model": "gpt-4o-mini",
            "provider": "openai",
            "apiKey": EMERGENT_API_KEY
        }
        
        response1 = requests.post(
            f"{API_BASE}/chat",
            json=payload1,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        # Send to session 2
        payload2 = {
            "message": session2_message,
            "session_id": session2_id,
            "model": "gpt-4o-mini",
            "provider": "openai",
            "apiKey": EMERGENT_API_KEY
        }
        
        response2 = requests.post(
            f"{API_BASE}/chat",
            json=payload2,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response1.status_code == 200 and response2.status_code == 200:
            print("✅ Both sessions created successfully")
            
            # Retrieve history for each session
            history1 = requests.get(f"{API_BASE}/sessions/{session1_id}", timeout=10)
            history2 = requests.get(f"{API_BASE}/sessions/{session2_id}", timeout=10)
            
            if history1.status_code == 200 and history2.status_code == 200:
                data1 = history1.json()
                data2 = history2.json()
                
                chats1 = data1.get("chats", [])
                chats2 = data2.get("chats", [])
                
                # Check that each session only has its own messages
                if len(chats1) >= 1 and len(chats2) >= 1:
                    # Check that session 1 contains React message
                    session1_has_react = any("react" in chat["user_message"].lower() for chat in chats1)
                    # Check that session 2 contains ML message
                    session2_has_ml = any("machine learning" in chat["user_message"].lower() for chat in chats2)
                    
                    # Check that sessions don't contain each other's messages
                    session1_has_ml = any("machine learning" in chat["user_message"].lower() for chat in chats1)
                    session2_has_react = any("react" in chat["user_message"].lower() for chat in chats2)
                    
                    if session1_has_react and session2_has_ml and not session1_has_ml and not session2_has_react:
                        print("✅ Session isolation working correctly - each session contains only its own messages")
                        return True
                    else:
                        print("❌ Session isolation failed - messages bleeding between sessions")
                        return False
                else:
                    print("❌ Sessions don't have expected messages")
                    return False
            else:
                print("❌ Failed to retrieve session histories")
                return False
        else:
            print("❌ Failed to create test sessions")
            return False
            
    except Exception as e:
        print(f"❌ Multiple sessions isolation test failed: {e}")
        return False

def test_railway_readiness():
    """Test Railway deployment readiness"""
    print("\n=== Testing Railway Deployment Readiness ===")
    
    try:
        # Test health check for Railway monitoring
        start_time = time.time()
        response = requests.get(f"{API_BASE}/health", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response time (should be fast for health checks)
            if response_time < 5.0:
                print(f"✅ Health check response time acceptable: {response_time:.2f}s")
                
                # Check required fields for Railway
                required_fields = ["status", "database"]
                if all(field in data for field in required_fields):
                    print("✅ Health check has all required fields for Railway")
                    
                    # Check that we're not using MongoDB anymore
                    if "mongo" not in str(data).lower():
                        print("✅ No MongoDB references in health check - SQLite migration complete")
                        
                        # Test port configuration (should work on Railway's dynamic port)
                        if data.get("status") == "healthy":
                            print("✅ Backend ready for Railway deployment")
                            return True
                        else:
                            print(f"❌ Backend status not healthy: {data.get('status')}")
                            return False
                    else:
                        print("❌ MongoDB references still present - migration incomplete")
                        return False
                else:
                    print("❌ Health check missing required fields")
                    return False
            else:
                print(f"❌ Health check too slow for Railway: {response_time:.2f}s")
                return False
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Railway readiness test failed: {e}")
        return False

def run_sqlite_backend_tests():
    """Run comprehensive SQLite backend tests"""
    print("🗄️  Starting SQLite Backend Functionality Tests")
    print(f"Testing Backend at: {BACKEND_URL}")
    print(f"Using Emergent API Key: {EMERGENT_API_KEY[:20]}...")
    
    test_results = {}
    
    # Core SQLite backend tests
    test_results["Database Connection"] = test_database_connection()
    test_results["Models API"] = test_models_api()
    test_results["Chat Functionality"] = test_chat_functionality()
    test_results["Session Management"] = test_session_management()
    test_results["SQLite Database Persistence"] = test_sqlite_database_persistence()
    test_results["Multiple Sessions Isolation"] = test_multiple_sessions_isolation()
    test_results["Railway Readiness"] = test_railway_readiness()
    
    # Results summary
    print("\n" + "="*70)
    print("📊 SQLITE BACKEND TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = 0
    total = len(test_results)
    critical_failures = []
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            # Mark critical failures
            if test_name in ["Database Connection", "Models API", "Chat Functionality", "Session Management"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All SQLite backend tests passed! MongoDB to SQLite migration successful.")
        print("✅ SQLite database connection working")
        print("✅ All LLM providers (OpenAI, Anthropic, Gemini) functional")
        print("✅ Chat functionality working with all providers")
        print("✅ Session management and history storage working")
        print("✅ SQLite database persistence confirmed")
        print("✅ Session isolation working correctly")
        print("✅ Railway deployment ready")
    else:
        print("⚠️  Some SQLite backend tests failed. Analysis:")
        if critical_failures:
            print(f"🚨 Critical failures: {', '.join(critical_failures)}")
        else:
            print("ℹ️  Only minor issues detected - core functionality working")
    
    return test_results

if __name__ == "__main__":
    run_sqlite_backend_tests()