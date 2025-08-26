#!/usr/bin/env python3
"""
Railway Deployment Configuration and MongoDB Integration Testing
Tests Railway-specific features and MongoDB flexibility for AI Chatbot
"""

import requests
import json
import os
import time
import subprocess
from typing import Dict, Any, List

# Backend URL - using production URL from environment
BACKEND_URL = "https://easy-deploy-db-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test API key from environment
EMERGENT_API_KEY = "sk-emergent-a57065a3873E44634A"

def test_railway_port_configuration():
    """Test Railway PORT environment variable handling"""
    print("\n=== Testing Railway PORT Environment Variable Configuration ===")
    
    # Check if backend server is configured to use PORT environment variable
    try:
        # Read the server.py file to verify PORT handling
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
        
        # Check for Railway PORT configuration
        port_config_found = False
        if 'PORT' in server_code and 'os.getenv("PORT"' in server_code:
            port_config_found = True
            print("✅ Backend configured to use Railway PORT environment variable")
        else:
            print("❌ Backend not configured for Railway PORT environment variable")
        
        # Test if the server responds (indicating it's running on correct port)
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend server responding correctly on Railway-assigned port")
            server_responding = True
        else:
            print(f"❌ Backend server not responding correctly: {response.status_code}")
            server_responding = False
            
        return port_config_found and server_responding
        
    except Exception as e:
        print(f"❌ Railway PORT configuration test failed: {e}")
        return False

def test_mongodb_url_flexibility():
    """Test MongoDB connection flexibility (MONGO_URL vs MONGODB_URL)"""
    print("\n=== Testing MongoDB URL Flexibility ===")
    
    try:
        # Read the server.py file to verify MongoDB URL handling
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
        
        # Check for flexible MongoDB URL configuration
        mongo_flexibility = False
        if 'MONGO_URL' in server_code and 'MONGODB_URL' in server_code:
            if 'os.getenv("MONGO_URL") or os.getenv("MONGODB_URL")' in server_code:
                mongo_flexibility = True
                print("✅ Backend configured for flexible MongoDB URL (MONGO_URL or MONGODB_URL)")
            else:
                print("❌ Backend not configured for MongoDB URL flexibility")
        else:
            print("❌ Backend missing MongoDB URL flexibility configuration")
        
        # Test database connection through health endpoint
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("database") == "connected":
                print("✅ MongoDB connection working correctly")
                db_connected = True
            else:
                print("❌ MongoDB connection not working")
                db_connected = False
        else:
            print("❌ Cannot verify MongoDB connection via health endpoint")
            db_connected = False
            
        return mongo_flexibility and db_connected
        
    except Exception as e:
        print(f"❌ MongoDB URL flexibility test failed: {e}")
        return False

def test_railway_health_monitoring():
    """Test health check endpoint for Railway monitoring"""
    print("\n=== Testing Railway Health Check Monitoring ===")
    
    try:
        # Test health endpoint response time and format
        start_time = time.time()
        response = requests.get(f"{API_BASE}/health", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Health endpoint response time: {response_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields for Railway monitoring
            required_fields = ["status", "database"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Health endpoint has all required fields for Railway monitoring")
                
                # Check status values
                if data.get("status") == "healthy":
                    print("✅ Health status reporting correctly")
                    status_ok = True
                else:
                    print(f"❌ Health status not 'healthy': {data.get('status')}")
                    status_ok = False
                
                # Check database status
                if data.get("database") == "connected":
                    print("✅ Database status reporting correctly")
                    db_ok = True
                else:
                    print(f"❌ Database status not 'connected': {data.get('database')}")
                    db_ok = False
                
                # Check response time (should be fast for health checks)
                if response_time < 5.0:
                    print("✅ Health endpoint response time acceptable for monitoring")
                    time_ok = True
                else:
                    print(f"❌ Health endpoint too slow for monitoring: {response_time:.2f}s")
                    time_ok = False
                
                return status_ok and db_ok and time_ok
            else:
                print(f"❌ Health endpoint missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Railway health monitoring test failed: {e}")
        return False

def test_api_endpoints_railway_ready():
    """Test all critical API endpoints for Railway deployment readiness"""
    print("\n=== Testing API Endpoints for Railway Deployment ===")
    
    endpoints_to_test = [
        ("/api/health", "GET"),
        ("/api/models", "GET"),
        ("/api/chat", "POST")
    ]
    
    results = {}
    
    for endpoint, method in endpoints_to_test:
        print(f"\n--- Testing {method} {endpoint} ---")
        
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            elif method == "POST":
                # Test POST with minimal valid payload
                payload = {
                    "messages": [{"role": "user", "content": "Railway deployment test"}],
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "apiKey": EMERGENT_API_KEY
                }
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}", 
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                print(f"✅ {endpoint} responding correctly ({response.status_code})")
                results[endpoint] = True
            else:
                print(f"❌ {endpoint} returned status {response.status_code}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"❌ {endpoint} test failed: {e}")
            results[endpoint] = False
    
    # Check if all critical endpoints are working
    all_working = all(results.values())
    if all_working:
        print("✅ All critical API endpoints ready for Railway deployment")
    else:
        failed_endpoints = [ep for ep, result in results.items() if not result]
        print(f"❌ Failed endpoints: {failed_endpoints}")
    
    return all_working

def test_build_configuration():
    """Test build configuration and dependencies for Railway deployment"""
    print("\n=== Testing Build Configuration for Railway ===")
    
    try:
        # Check if requirements.txt exists and has necessary dependencies
        requirements_path = '/app/backend/requirements.txt'
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                requirements = f.read()
            
            # Check for critical dependencies
            critical_deps = ['fastapi', 'uvicorn', 'pymongo', 'emergentintegrations']
            missing_deps = []
            
            for dep in critical_deps:
                if dep not in requirements.lower():
                    missing_deps.append(dep)
            
            if not missing_deps:
                print("✅ All critical dependencies present in requirements.txt")
                deps_ok = True
            else:
                print(f"❌ Missing critical dependencies: {missing_deps}")
                deps_ok = False
        else:
            print("❌ requirements.txt not found")
            deps_ok = False
        
        # Check if Dockerfile exists (Railway deployment)
        dockerfile_path = '/app/Dockerfile'
        if os.path.exists(dockerfile_path):
            print("✅ Dockerfile found for Railway deployment")
            dockerfile_ok = True
        else:
            print("❌ Dockerfile not found")
            dockerfile_ok = False
        
        # Check if railway.toml exists
        railway_config_path = '/app/railway.toml'
        if os.path.exists(railway_config_path):
            print("✅ railway.toml configuration found")
            railway_config_ok = True
        else:
            print("❌ railway.toml configuration not found")
            railway_config_ok = False
        
        # Test if backend can start (check if it's currently running)
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend application starts successfully")
                startup_ok = True
            else:
                print("❌ Backend application not responding")
                startup_ok = False
        except:
            print("❌ Backend application not accessible")
            startup_ok = False
        
        return deps_ok and dockerfile_ok and startup_ok
        
    except Exception as e:
        print(f"❌ Build configuration test failed: {e}")
        return False

def test_environment_variables_flexibility():
    """Test API key configuration flexibility"""
    print("\n=== Testing Environment Variables Flexibility ===")
    
    try:
        # Test with Emergent Universal API key
        payload = {
            "messages": [{"role": "user", "content": "Test API key flexibility"}],
            "provider": "openai",
            "model": "gpt-4o-mini",
            "apiKey": EMERGENT_API_KEY
        }
        
        response = requests.post(
            f"{API_BASE}/chat", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Emergent Universal API key working correctly")
            emergent_key_ok = True
        else:
            print(f"❌ Emergent Universal API key failed: {response.status_code}")
            emergent_key_ok = False
        
        # Check if API key is not hardcoded in the backend
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
        
        # Look for hardcoded API keys (should not exist)
        hardcoded_patterns = ['sk-', 'api_key=', 'apikey=']
        hardcoded_found = False
        
        for pattern in hardcoded_patterns:
            if pattern in server_code.lower() and 'request.apiKey' not in server_code:
                # Check if it's actually a hardcoded key vs variable reference
                lines = server_code.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#') and 'request' not in line:
                        hardcoded_found = True
                        break
        
        if not hardcoded_found:
            print("✅ No hardcoded API keys found - configuration is flexible")
            no_hardcode = True
        else:
            print("❌ Hardcoded API keys detected - not flexible")
            no_hardcode = False
        
        # Test environment variable handling
        health_response = requests.get(f"{API_BASE}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if 'emergent_key' in health_data:
                print("✅ Environment variable handling working (emergent_key status available)")
                env_handling_ok = True
            else:
                print("❌ Environment variable handling not working properly")
                env_handling_ok = False
        else:
            print("❌ Cannot verify environment variable handling")
            env_handling_ok = False
        
        return emergent_key_ok and no_hardcode and env_handling_ok
        
    except Exception as e:
        print(f"❌ Environment variables flexibility test failed: {e}")
        return False

def run_railway_deployment_tests():
    """Run Railway deployment specific tests"""
    print("🚀 Starting Railway Deployment Configuration Tests")
    print(f"Testing Backend at: {BACKEND_URL}")
    print(f"Using Emergent API Key: {EMERGENT_API_KEY[:20]}...")
    
    test_results = {}
    
    # Railway-specific tests
    test_results["Railway PORT Configuration"] = test_railway_port_configuration()
    test_results["MongoDB URL Flexibility"] = test_mongodb_url_flexibility()
    test_results["Railway Health Monitoring"] = test_railway_health_monitoring()
    test_results["API Endpoints Railway Ready"] = test_api_endpoints_railway_ready()
    test_results["Build Configuration"] = test_build_configuration()
    test_results["Environment Variables Flexibility"] = test_environment_variables_flexibility()
    
    # Results summary
    print("\n" + "="*70)
    print("📊 RAILWAY DEPLOYMENT TEST RESULTS SUMMARY")
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
            # Mark critical failures for Railway deployment
            if test_name in ["Railway PORT Configuration", "MongoDB URL Flexibility", "Railway Health Monitoring", "API Endpoints Railway Ready"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All Railway deployment tests passed! Application is ready for Railway deployment.")
        print("✅ Railway PORT environment variable handling working")
        print("✅ MongoDB connection flexibility implemented")
        print("✅ Health check endpoint ready for Railway monitoring")
        print("✅ All critical API endpoints operational")
        print("✅ Build configuration complete")
        print("✅ Environment variables configured flexibly")
    else:
        print("⚠️  Some Railway deployment tests failed. Analysis:")
        if critical_failures:
            print(f"🚨 Critical Railway deployment failures: {', '.join(critical_failures)}")
        else:
            print("ℹ️  Only minor issues detected - core Railway deployment features working")
    
    return test_results

if __name__ == "__main__":
    run_railway_deployment_tests()