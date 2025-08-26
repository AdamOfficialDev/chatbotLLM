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

# Backend URL - testing directly against the FastAPI backend
BACKEND_URL = "http://localhost:8001"
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
    
    # Validation and storage tests
    test_results["Input Validation"] = test_chat_validation()
    test_results["Session Management"] = test_session_endpoint(session_id)
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
            if test_name in ["Health Check", "Models API", "OpenAI Integration", "MongoDB Storage"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The AI Chatbot backend is fully functional.")
        print("✅ All LLM integrations working")
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