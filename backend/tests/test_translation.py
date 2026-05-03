#!/usr/bin/env python3
"""
Comprehensive Translation API Test Script
Tests all aspects of the translation feature
"""

import requests
import json
import sys
from pathlib import Path

# Test configuration
BASE_URL = "https://smart-text-bot-backend.onrender.com"
TRANSLATE_ENDPOINT = f"{BASE_URL}/translate"
EXPLAIN_ENDPOINT = f"{BASE_URL}/explain"

# Test cases
TEST_CASES = [
    {
        "name": "Test 1: English to Hindi",
        "endpoint": "translate",
        "data": {
            "text": "Hello",
            "target_lang": "Hindi",
            "source_lang": "auto"
        },
        "expected_keys": ["translated_text", "source_lang", "target_lang"]
    },
    {
        "name": "Test 2: English to Spanish",
        "endpoint": "translate",
        "data": {
            "text": "Good morning",
            "target_lang": "Spanish"
        },
        "expected_keys": ["translated_text", "source_lang", "target_lang"]
    },
    {
        "name": "Test 3: French to German",
        "endpoint": "translate",
        "data": {
            "text": "Bonjour",
            "target_lang": "German",
            "source_lang": "French"
        },
        "expected_keys": ["translated_text", "source_lang", "target_lang"]
    },
    {
        "name": "Test 4: Complex sentence",
        "endpoint": "translate",
        "data": {
            "text": "The quick brown fox jumps over the lazy dog",
            "target_lang": "Chinese"
        },
        "expected_keys": ["translated_text", "source_lang", "target_lang"]
    },
    {
        "name": "Test 5: Translation explanation",
        "endpoint": "explain",
        "data": {
            "original": "Hello",
            "translation": "नमस्ते"
        },
        "expected_keys": ["explanation"]
    },
]

ERROR_TEST_CASES = [
    {
        "name": "Error Test 1: Empty text",
        "endpoint": "translate",
        "data": {
            "text": "",
            "target_lang": "Hindi"
        },
        "should_error": True,
        "expected_status": 400
    },
    {
        "name": "Error Test 2: Missing target language",
        "endpoint": "translate",
        "data": {
            "text": "Hello",
            "target_lang": ""
        },
        "should_error": True,
        "expected_status": 400
    },
]

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_translation_api():
    """Test the translation API endpoints"""
    
    print_section("TRANSLATION API TEST SUITE")
    print(f"Base URL: {BASE_URL}")
    
    passed = 0
    failed = 0
    
    # Check if server is running
    print("\n[*] Checking if server is running...")
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✓ Server is running")
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Server is not running!")
        print(f"  Please start the server with: python app.py")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    # Test successful cases
    print_section("TESTING SUCCESSFUL CASES")
    
    for test in TEST_CASES:
        print(f"\n[*] {test['name']}")
        print(f"    Endpoint: POST /{test['endpoint']}")
        print(f"    Data: {json.dumps(test['data'], indent=6)}")
        
        endpoint = EXPLAIN_ENDPOINT if test['endpoint'] == 'explain' else TRANSLATE_ENDPOINT
        
        try:
            response = requests.post(
                endpoint,
                json=test['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"    Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Response: {json.dumps(data, indent=6)}")
                
                # Check for expected keys
                missing_keys = [k for k in test['expected_keys'] if k not in data]
                if missing_keys:
                    print(f"    ✗ FAILED: Missing keys: {missing_keys}")
                    failed += 1
                else:
                    print(f"    ✓ PASSED")
                    passed += 1
            else:
                print(f"    ✗ FAILED: Unexpected status code {response.status_code}")
                print(f"    Response: {response.text}")
                failed += 1
                
        except requests.exceptions.Timeout:
            print(f"    ✗ FAILED: Request timeout (>10 seconds)")
            failed += 1
        except requests.exceptions.ConnectionError:
            print(f"    ✗ FAILED: Connection error")
            failed += 1
        except Exception as e:
            print(f"    ✗ FAILED: {e}")
            failed += 1
    
    # Test error cases
    print_section("TESTING ERROR CASES")
    
    for test in ERROR_TEST_CASES:
        print(f"\n[*] {test['name']}")
        print(f"    Expected to fail with status {test['expected_status']}")
        print(f"    Data: {json.dumps(test['data'], indent=6)}")
        
        try:
            response = requests.post(
                TRANSLATE_ENDPOINT,
                json=test['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"    Status Code: {response.status_code}")
            
            if response.status_code == test['expected_status']:
                print(f"    Response: {response.json()}")
                print(f"    ✓ PASSED (correctly returned error)")
                passed += 1
            else:
                print(f"    ✗ FAILED: Expected {test['expected_status']}, got {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"    ✗ FAILED: {e}")
            failed += 1
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"\nTotal Tests: {passed + failed}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed")
        return False

def test_env_loading():
    """Test if .env file is loading correctly"""
    print_section("ENVIRONMENT VARIABLES TEST")
    
    try:
        from dotenv import load_dotenv
        import os
        
        env_path = Path(__file__).parent.parent / ".env"
        print(f"[*] Loading .env from: {env_path}")
        print(f"[*] .env exists: {env_path.exists()}")
        
        load_dotenv(dotenv_path=env_path)
        
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key:
            print(f"✓ API key loaded successfully")
            print(f"  Key length: {len(api_key)}")
            print(f"  Starts with: {api_key[:10]}...")
            return True
        else:
            print(f"✗ API key not found in .env file")
            return False
            
    except Exception as e:
        print(f"✗ Error loading .env: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*18 + "TRANSLATION API TEST SUITE" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test env loading first
    env_ok = test_env_loading()
    
    if env_ok:
        # Test API
        api_ok = test_translation_api()
        
        if not api_ok:
            sys.exit(1)
    else:
        print("\n[!] Skipping API tests due to environment variable issues")
        sys.exit(1)
    
    print("\n✓ All checks completed!")
