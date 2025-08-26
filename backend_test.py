#!/usr/bin/env python3
"""
Backend API Testing for AI Chatbot
Tests the /api/chat endpoint with various scenarios
"""

import requests
import json
import os
from typing import Dict, Any

# Get the base URL from environment
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://smart-converse-16.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

def test_get_chat_endpoint():
    """Test GET request to /api/chat endpoint"""
    print("\n=== Testing GET /api/chat ===")
    try:
        response = requests.get(f"{API_BASE}/chat", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'message' in data:
                print("✅ GET /api/chat endpoint is accessible and returns expected message")
                return True
            else:
                print("❌ GET /api/chat response missing 'message' field")
                return False
        else:
            print(f"❌ GET /api/chat returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /api/chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ GET /api/chat response is not valid JSON: {e}")
        return False

def test_post_chat_valid_payload():
    """Test POST request to /api/chat with valid payload"""
    print("\n=== Testing POST /api/chat with valid payload ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": "test-key"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print("✅ POST /api/chat with valid payload works correctly")
                print(f"Response content: {data['response']}")
                return True
            else:
                print("❌ POST /api/chat response missing 'response' field")
                return False
        else:
            print(f"❌ POST /api/chat returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /api/chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ POST /api/chat response is not valid JSON: {e}")
        print(f"Raw response: {response.text}")
        return False

def test_post_chat_missing_api_key():
    """Test POST request to /api/chat without API key"""
    print("\n=== Testing POST /api/chat without API key ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "provider": "openai",
        "model": "gpt-4o-mini"
        # apiKey is intentionally missing
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'API key is required' in data['error']:
                print("✅ POST /api/chat correctly handles missing API key")
                return True
            else:
                print("❌ POST /api/chat error message doesn't match expected format")
                return False
        else:
            print(f"❌ POST /api/chat should return 400 for missing API key, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /api/chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ POST /api/chat response is not valid JSON: {e}")
        return False

def test_post_chat_missing_messages():
    """Test POST request to /api/chat without messages"""
    print("\n=== Testing POST /api/chat without messages ===")
    
    payload = {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": "test-key"
        # messages is intentionally missing
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'Messages array is required' in data['error']:
                print("✅ POST /api/chat correctly handles missing messages")
                return True
            else:
                print("❌ POST /api/chat error message doesn't match expected format")
                return False
        else:
            print(f"❌ POST /api/chat should return 400 for missing messages, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /api/chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ POST /api/chat response is not valid JSON: {e}")
        return False

def test_post_chat_empty_messages():
    """Test POST request to /api/chat with empty messages array"""
    print("\n=== Testing POST /api/chat with empty messages array ===")
    
    payload = {
        "messages": [],  # Empty array
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": "test-key"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'Messages array is required' in data['error']:
                print("✅ POST /api/chat correctly handles empty messages array")
                return True
            else:
                print("❌ POST /api/chat error message doesn't match expected format")
                return False
        else:
            print(f"❌ POST /api/chat should return 400 for empty messages, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /api/chat request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ POST /api/chat response is not valid JSON: {e}")
        return False

def test_response_format():
    """Test if the response format is correct JSON and has expected structure"""
    print("\n=== Testing Response Format ===")
    
    payload = {
        "messages": [{"role": "user", "content": "Test message for format validation"}],
        "provider": "openai",
        "model": "gpt-4o-mini",
        "apiKey": "test-key"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"Response Length: {len(response.text)} characters")
        
        # Check if response is valid JSON
        try:
            data = response.json()
            print("✅ Response is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ Response is not valid JSON: {e}")
            print(f"Raw response: {response.text}")
            return False
        
        # Check response structure
        if response.status_code == 200:
            if isinstance(data, dict) and 'response' in data:
                print("✅ Response has correct structure with 'response' field")
                if isinstance(data['response'], str) and len(data['response']) > 0:
                    print("✅ Response content is a non-empty string")
                    return True
                else:
                    print("❌ Response content is not a non-empty string")
                    return False
            else:
                print("❌ Response structure is incorrect")
                return False
        else:
            print(f"❌ Expected 200 status code, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def run_all_tests():
    """Run all backend tests for the chatbot API"""
    print("🚀 Starting Backend API Tests for AI Chatbot")
    print(f"Testing API at: {API_BASE}")
    
    test_results = {
        "GET /api/chat endpoint": test_get_chat_endpoint(),
        "POST /api/chat with valid payload": test_post_chat_valid_payload(),
        "POST /api/chat missing API key": test_post_chat_missing_api_key(),
        "POST /api/chat missing messages": test_post_chat_missing_messages(),
        "POST /api/chat empty messages": test_post_chat_empty_messages(),
        "Response format validation": test_response_format()
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot backend API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the detailed output above.")
    
    return test_results

if __name__ == "__main__":
    run_all_tests()