#!/usr/bin/env python3
"""
Backend Verification Test - Quick verification before Railway deployment
Tests the specific requirements from the review request:
1. Health check endpoint
2. Models API 
3. Basic chat functionality
4. MongoDB connection
5. Emergency integrations
"""

import requests
import json
import time
from typing import Dict, Any

# Backend URL from environment
BACKEND_URL = "https://pip-install-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test API key
EMERGENT_API_KEY = "sk-emergent-a57065a3873E44634A"

def test_health_check():
    """Test health check endpoint - ensure it returns proper status"""
    print("\n=== Testing Health Check Endpoint ===")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint responding with status 200")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Emergent Key: {data.get('emergent_key')}")
            
            # Verify expected fields
            if data.get('status') == 'healthy' and data.get('database') == 'connected':
                print("✅ Health check returning proper status")
                return True
            else:
                print("❌ Health check not returning expected status")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_models_api():
    """Test Models API - verify it returns all available LLM models"""
    print("\n=== Testing Models API ===")
    
    try:
        response = requests.get(f"{API_BASE}/models", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Models API responding with status 200")
            
            # Check if models data is present
            if 'models' in data:
                models = data['models']
                print(f"   Providers available: {list(models.keys())}")
                
                # Count total models
                total_models = sum(len(provider_models) for provider_models in models.values())
                print(f"   Total models available: {total_models}")
                
                # Check for expected providers
                expected_providers = ['openai', 'anthropic', 'gemini']
                missing_providers = [p for p in expected_providers if p not in models]
                
                if not missing_providers:
                    print("✅ All expected providers (OpenAI, Anthropic, Gemini) available")
                    
                    # Check for some key models
                    openai_models = models.get('openai', [])
                    anthropic_models = models.get('anthropic', [])
                    gemini_models = models.get('gemini', [])
                    
                    print(f"   OpenAI models: {len(openai_models)} (including {openai_models[:3]}...)")
                    print(f"   Anthropic models: {len(anthropic_models)} (including {anthropic_models[:2]}...)")
                    print(f"   Gemini models: {len(gemini_models)} (including {gemini_models[:2]}...)")
                    
                    return True
                else:
                    print(f"❌ Missing expected providers: {missing_providers}")
                    return False
            else:
                print("❌ Models API response missing 'models' field")
                return False
        else:
            print(f"❌ Models API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Models API test failed: {e}")
        return False

def test_basic_chat():
    """Test basic chat functionality - test with a simple message"""
    print("\n=== Testing Basic Chat Functionality ===")
    
    try:
        # Test payload with a simple message
        payload = {
            "messages": [
                {"role": "user", "content": "Hello! This is a verification test. Please respond with 'Backend verification successful' if you can process this message."}
            ],
            "provider": "openai",
            "model": "gpt-4o-mini",
            "apiKey": EMERGENT_API_KEY
        }
        
        print("   Sending test message to chat endpoint...")
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint responding with status 200")
            
            if 'response' in data and 'session_id' in data:
                ai_response = data['response']
                session_id = data['session_id']
                
                print(f"   AI Response: {ai_response[:100]}...")
                print(f"   Session ID: {session_id}")
                
                # Check if response is meaningful (not empty and contains text)
                if ai_response and len(ai_response.strip()) > 10:
                    print("✅ Chat functionality working - AI generated meaningful response")
                    return True
                else:
                    print("❌ Chat response too short or empty")
                    return False
            else:
                print("❌ Chat response missing required fields")
                return False
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Basic chat test failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection - verify database connectivity"""
    print("\n=== Testing MongoDB Connection ===")
    
    try:
        # Test database connectivity through health endpoint
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('database') == 'connected':
                print("✅ MongoDB connection verified through health endpoint")
                
                # Additional test: Try to create a chat session to verify database write
                test_payload = {
                    "messages": [
                        {"role": "user", "content": "Database connectivity test"}
                    ],
                    "provider": "openai", 
                    "model": "gpt-4o-mini",
                    "apiKey": EMERGENT_API_KEY
                }
                
                chat_response = requests.post(
                    f"{API_BASE}/chat",
                    json=test_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    session_id = chat_data.get('session_id')
                    
                    if session_id:
                        print(f"✅ Database write operation successful (session: {session_id})")
                        
                        # Test session retrieval
                        session_response = requests.get(f"{API_BASE}/sessions/{session_id}", timeout=10)
                        
                        if session_response.status_code == 200:
                            print("✅ Database read operation successful")
                            return True
                        else:
                            print("❌ Database read operation failed")
                            return False
                    else:
                        print("❌ Database write operation failed - no session ID returned")
                        return False
                else:
                    print("❌ Database write test failed")
                    return False
            else:
                print(f"❌ Database not connected according to health endpoint: {data.get('database')}")
                return False
        else:
            print(f"❌ Cannot verify database connection - health endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
        return False

def test_emergent_integrations():
    """Test Emergency integrations - ensure the package is properly installed and working"""
    print("\n=== Testing Emergent Integrations Package ===")
    
    try:
        # Test multiple providers to verify emergentintegrations is working
        providers_to_test = [
            ("openai", "gpt-4o-mini"),
            ("anthropic", "claude-3-5-sonnet-20241022"),
            ("gemini", "gemini-1.5-flash")
        ]
        
        successful_providers = []
        
        for provider, model in providers_to_test:
            print(f"   Testing {provider} with {model}...")
            
            payload = {
                "messages": [
                    {"role": "user", "content": f"Test {provider} integration - respond with 'OK'"}
                ],
                "provider": provider,
                "model": model,
                "apiKey": EMERGENT_API_KEY
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/chat",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('response'):
                        print(f"   ✅ {provider} integration working")
                        successful_providers.append(provider)
                    else:
                        print(f"   ❌ {provider} integration failed - no response")
                else:
                    print(f"   ❌ {provider} integration failed - status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {provider} integration failed - {e}")
        
        if len(successful_providers) >= 2:
            print(f"✅ Emergent integrations working - {len(successful_providers)}/3 providers successful")
            print(f"   Working providers: {successful_providers}")
            return True
        else:
            print(f"❌ Emergent integrations not working properly - only {len(successful_providers)}/3 providers successful")
            return False
            
    except Exception as e:
        print(f"❌ Emergent integrations test failed: {e}")
        return False

def run_verification_tests():
    """Run all verification tests"""
    print("🔍 Starting Backend Verification Tests")
    print(f"Testing Backend at: {BACKEND_URL}")
    print("="*60)
    
    test_results = {}
    
    # Run all verification tests
    test_results["Health Check Endpoint"] = test_health_check()
    test_results["Models API"] = test_models_api()
    test_results["Basic Chat Functionality"] = test_basic_chat()
    test_results["MongoDB Connection"] = test_mongodb_connection()
    test_results["Emergent Integrations"] = test_emergent_integrations()
    
    # Results summary
    print("\n" + "="*60)
    print("📊 BACKEND VERIFICATION TEST RESULTS")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    critical_failures = []
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            critical_failures.append(test_name)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All verification tests passed! Backend is ready for Railway deployment.")
        print("✅ Health check endpoint working properly")
        print("✅ Models API returning all available LLM models")
        print("✅ Basic chat functionality operational")
        print("✅ MongoDB connection verified")
        print("✅ Emergent integrations package working")
    else:
        print("⚠️  Some verification tests failed:")
        for failure in critical_failures:
            print(f"   🚨 {failure}")
    
    return test_results

if __name__ == "__main__":
    run_verification_tests()