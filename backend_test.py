#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Chatbot
Tests all backend endpoints with various LLM models and scenarios
"""

import requests
import json
import os
import time
from typing import Dict, Any, List

# Backend URL - using production URL from environment
BACKEND_URL = "https://easy-deploy-db-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test API key from environment
EMERGENT_API_KEY = "sk-emergent-a57065a3873E44634A"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n=== Testing GET /api/health ===")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("database") == "connected":
                print("✅ Health endpoint working - database connected")
                return True
            else:
                print("❌ Health endpoint response indicates issues")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Health endpoint response is not valid JSON: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint to verify all LLM models are available"""
    print("\n=== Testing GET /api/models ===")
    try:
        response = requests.get(f"{API_BASE}/models", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", {})
            
            # Check if all expected providers are present
            expected_providers = ["openai", "anthropic", "gemini"]
            missing_providers = []
            
            for provider in expected_providers:
                if provider not in models:
                    missing_providers.append(provider)
                else:
                    print(f"✅ {provider.upper()} models available: {len(models[provider])} models")
                    # Print first few models for verification
                    print(f"   Sample models: {models[provider][:3]}")
            
            if missing_providers:
                print(f"❌ Missing providers: {missing_providers}")
                return False
            
            # Check for latest models
            latest_models_check = {
                "openai": ["gpt-5", "o3", "gpt-4.1"],
                "anthropic": ["claude-4-sonnet-20250514", "claude-3-7-sonnet-20250219"],
                "gemini": ["gemini-2.5-flash", "gemini-2.0-flash"]
            }
            
            for provider, expected_models in latest_models_check.items():
                available_models = models.get(provider, [])
                missing_latest = [model for model in expected_models if model not in available_models]
                if missing_latest:
                    print(f"⚠️  {provider.upper()} missing latest models: {missing_latest}")
                else:
                    print(f"✅ {provider.upper()} has all latest models")
            
            print("✅ Models endpoint working correctly")
            return True
        else:
            print(f"❌ Models endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Models endpoint request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Models endpoint response is not valid JSON: {e}")
        return False

def test_chat_endpoint_openai():
    """Test chat endpoint with OpenAI models"""
    print("\n=== Testing POST /api/chat with OpenAI GPT-4o-mini ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello! Please respond with exactly: 'OpenAI GPT-4o-mini is working'"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'session_id' in data:
                print("✅ OpenAI chat endpoint working correctly")
                print(f"Response: {data['response'][:100]}...")
                print(f"Session ID: {data['session_id']}")
                return True, data['session_id']
            else:
                print("❌ OpenAI chat response missing required fields")
                print(f"Response: {response.text}")
                return False, None
        else:
            print(f"❌ OpenAI chat returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI chat request failed: {e}")
        return False, None
    except json.JSONDecodeError as e:
        print(f"❌ OpenAI chat response is not valid JSON: {e}")
        return False, None

def test_chat_endpoint_anthropic():
    """Test chat endpoint with Anthropic Claude models"""
    print("\n=== Testing POST /api/chat with Claude-3-5-sonnet ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello! Please respond with exactly: 'Claude-3-5-sonnet is working'"}],
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'session_id' in data:
                print("✅ Anthropic chat endpoint working correctly")
                print(f"Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Anthropic chat response missing required fields")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Anthropic chat returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Anthropic chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Anthropic chat response is not valid JSON: {e}")
        return False

def test_chat_endpoint_gemini():
    """Test chat endpoint with Google Gemini models"""
    print("\n=== Testing POST /api/chat with Gemini-1.5-flash ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello! Please respond with exactly: 'Gemini-1.5-flash is working'"}],
        "provider": "gemini",
        "model": "gemini-1.5-flash",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'session_id' in data:
                print("✅ Gemini chat endpoint working correctly")
                print(f"Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Gemini chat response missing required fields")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Gemini chat returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Gemini chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Gemini chat response is not valid JSON: {e}")
        return False

def test_chat_validation():
    """Test chat endpoint input validation"""
    print("\n=== Testing Chat Input Validation ===")
    
    # Test missing API key
    print("\n--- Testing missing API key ---")
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "provider": "openai",
        "model": "gpt-4o-mini"
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat", json=payload, timeout=10)
        if response.status_code == 422:  # FastAPI validation error
            print("✅ Correctly validates missing API key")
            validation_passed = True
        else:
            print(f"❌ Expected 422 for missing API key, got {response.status_code}")
            validation_passed = False
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        validation_passed = False
    
    # Test invalid provider
    print("\n--- Testing invalid provider ---")
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "provider": "invalid_provider",
        "model": "some-model",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat", json=payload, timeout=10)
        if response.status_code == 400:
            print("✅ Correctly validates invalid provider")
            validation_passed = validation_passed and True
        else:
            print(f"❌ Expected 400 for invalid provider, got {response.status_code}")
            validation_passed = False
    except Exception as e:
        print(f"❌ Provider validation test failed: {e}")
        validation_passed = False
    
    return validation_passed

def test_session_endpoint(session_id):
    """Test session history endpoint"""
    if not session_id:
        print("\n=== Skipping session test - no session ID available ===")
        return False
        
    print(f"\n=== Testing GET /api/sessions/{session_id} ===")
    
    try:
        response = requests.get(f"{API_BASE}/sessions/{session_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'session_id' in data and 'chats' in data:
                print("✅ Session endpoint working correctly")
                print(f"Session ID: {data['session_id']}")
                print(f"Number of chats: {len(data['chats'])}")
                return True
            else:
                print("❌ Session response missing required fields")
                return False
        else:
            print(f"❌ Session endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Session endpoint request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Session endpoint response is not valid JSON: {e}")
        return False

def test_response_completion():
    """Test that AI responses are complete and not cut off mid-sentence"""
    print("\n=== Testing Response Completion (No Truncation) ===")
    
    # Ask for a longer response to test completion
    payload = {
        "messages": [{"role": "user", "content": "Please write a detailed explanation of how machine learning works, including at least 3 key concepts and examples. Make sure to end your response with the phrase 'This completes my explanation.'"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Longer timeout for detailed response
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            
            # Check if response ends properly (not cut off)
            if ai_response.strip().endswith('This completes my explanation.'):
                print("✅ Response completion test passed - response ends properly")
                print(f"Response length: {len(ai_response)} characters")
                return True, data.get('session_id')
            else:
                print("❌ Response appears to be cut off - doesn't end with expected phrase")
                print(f"Response ends with: '...{ai_response[-100:]}'")
                return False, data.get('session_id')
        else:
            print(f"❌ Response completion test failed with status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Response completion test failed: {e}")
        return False, None

def test_conversation_context():
    """Test that conversation context is preserved across multiple messages"""
    print("\n=== Testing Conversation Context Preservation ===")
    
    # First message - establish context
    first_payload = {
        "messages": [{"role": "user", "content": "My name is Alice and I love programming in Python. What's your favorite programming language?"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        # Send first message
        response1 = requests.post(f"{API_BASE}/chat", json=first_payload, timeout=30)
        
        if response1.status_code != 200:
            print(f"❌ First message failed with status {response1.status_code}")
            return False
            
        data1 = response1.json()
        session_id = data1.get('session_id')
        first_response = data1.get('response', '')
        
        print(f"First response received, session_id: {session_id}")
        
        # Second message - test context preservation
        second_payload = {
            "messages": [
                {"role": "user", "content": "My name is Alice and I love programming in Python. What's your favorite programming language?"},
                {"role": "assistant", "content": first_response},
                {"role": "user", "content": "Do you remember my name and what programming language I mentioned I love?"}
            ],
            "provider": "openai",
            "model": "gpt-4o-mini",
            "apiKey": EMERGENT_API_KEY,
            "session_id": session_id
        }
        
        # Send second message with context
        response2 = requests.post(f"{API_BASE}/chat", json=second_payload, timeout=30)
        
        if response2.status_code != 200:
            print(f"❌ Second message failed with status {response2.status_code}")
            return False
            
        data2 = response2.json()
        second_response = data2.get('response', '').lower()
        
        # Check if AI remembers the context (name and programming language)
        context_preserved = ('alice' in second_response and 'python' in second_response)
        
        if context_preserved:
            print("✅ Conversation context preserved - AI remembers name and programming language")
            print(f"Context response: {data2.get('response')[:200]}...")
            return True
        else:
            print("❌ Conversation context not preserved - AI doesn't remember previous context")
            print(f"Context response: {data2.get('response')[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Conversation context test failed: {e}")
        return False

def test_session_management_detailed():
    """Test detailed session management and ID handling"""
    print("\n=== Testing Detailed Session Management ===")
    
    # Test 1: New conversation without session_id
    payload1 = {
        "messages": [{"role": "user", "content": "Start a new conversation. Remember this number: 12345"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response1 = requests.post(f"{API_BASE}/chat", json=payload1, timeout=30)
        
        if response1.status_code != 200:
            print(f"❌ New session test failed with status {response1.status_code}")
            return False
            
        data1 = response1.json()
        session_id = data1.get('session_id')
        
        if not session_id:
            print("❌ No session_id returned for new conversation")
            return False
            
        print(f"✅ New session created with ID: {session_id}")
        
        # Test 2: Continue conversation with same session_id
        payload2 = {
            "messages": [
                {"role": "user", "content": "Start a new conversation. Remember this number: 12345"},
                {"role": "assistant", "content": data1.get('response', '')},
                {"role": "user", "content": "What number did I ask you to remember?"}
            ],
            "provider": "openai",
            "model": "gpt-4o-mini",
            "apiKey": EMERGENT_API_KEY,
            "session_id": session_id
        }
        
        response2 = requests.post(f"{API_BASE}/chat", json=payload2, timeout=30)
        
        if response2.status_code != 200:
            print(f"❌ Session continuation test failed with status {response2.status_code}")
            return False
            
        data2 = response2.json()
        returned_session_id = data2.get('session_id')
        
        # Verify same session_id is returned
        if returned_session_id != session_id:
            print(f"❌ Session ID mismatch: expected {session_id}, got {returned_session_id}")
            return False
            
        # Check if the number is remembered
        response_text = data2.get('response', '').lower()
        if '12345' in response_text:
            print("✅ Session management working - same session_id maintained and context preserved")
            return True
        else:
            print("❌ Session context not preserved despite same session_id")
            print(f"Response: {data2.get('response')[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_mongodb_storage():
    """Test if chat data is being stored in MongoDB"""
    print("\n=== Testing MongoDB Chat Storage ===")
    
    # Send a unique test message
    test_message = f"MongoDB storage test - {int(time.time())}"
    payload = {
        "messages": [{"role": "user", "content": test_message}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": EMERGENT_API_KEY
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            
            # Wait a moment for database write
            time.sleep(1)
            
            # Check if the chat was stored
            session_response = requests.get(f"{API_BASE}/sessions/{session_id}", timeout=10)
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                chats = session_data.get('chats', [])
                
                # Look for our test message in the stored chats
                found_message = False
                for chat in chats:
                    messages = chat.get('messages', [])
                    for msg in messages:
                        if msg.get('content') == test_message:
                            found_message = True
                            break
                    if found_message:
                        break
                
                if found_message:
                    print("✅ MongoDB storage working - chat data persisted correctly")
                    return True
                else:
                    print("❌ MongoDB storage issue - test message not found in stored data")
                    return False
            else:
                print("❌ Could not retrieve session data to verify storage")
                return False
        else:
            print("❌ Chat request failed, cannot test storage")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB storage test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive backend tests"""
    print("🚀 Starting Comprehensive Backend API Tests for AI Chatbot")
    print(f"Testing Backend at: {BACKEND_URL}")
    print(f"Using Emergent API Key: {EMERGENT_API_KEY[:20]}...")
    
    test_results = {}
    session_id = None
    
    # Core endpoint tests
    test_results["Health Check"] = test_health_endpoint()
    test_results["Models API"] = test_models_endpoint()
    
    # LLM integration tests
    openai_result, session_id = test_chat_endpoint_openai()
    test_results["OpenAI Integration"] = openai_result
    test_results["Anthropic Integration"] = test_chat_endpoint_anthropic()
    test_results["Gemini Integration"] = test_chat_endpoint_gemini()
    
    # NEW TESTS - Response completion and context preservation
    completion_result, completion_session = test_response_completion()
    test_results["Response Completion"] = completion_result
    test_results["Conversation Context"] = test_conversation_context()
    test_results["Session Management Detailed"] = test_session_management_detailed()
    
    # Validation and storage tests
    test_results["Input Validation"] = test_chat_validation()
    test_results["Session Endpoint"] = test_session_endpoint(session_id or completion_session)
    test_results["MongoDB Storage"] = test_mongodb_storage()
    
    # Results summary
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
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
            if test_name in ["Health Check", "Models API", "OpenAI Integration", "Response Completion", "Conversation Context", "Session Management Detailed"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The AI Chatbot backend is fully functional.")
        print("✅ All LLM integrations working")
        print("✅ Response completion working - no truncation")
        print("✅ Conversation context preserved across messages")
        print("✅ Session management operational")
        print("✅ Database storage operational")
        print("✅ All endpoints responding correctly")
    else:
        print("⚠️  Some tests failed. Analysis:")
        if critical_failures:
            print(f"🚨 Critical failures: {', '.join(critical_failures)}")
        else:
            print("ℹ️  Only minor issues detected - core functionality working")
    
    return test_results

if __name__ == "__main__":
    run_comprehensive_tests()