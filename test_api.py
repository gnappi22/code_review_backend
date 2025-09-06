#!/usr/bin/env python3
"""
Simple test script to verify the Code Review API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_snippet():
    """Test creating a code snippet"""
    print("Testing snippet creation...")
    
    test_snippet = {
        "language": "python",
        "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        "lines": "1-4"
    }
    
    response = requests.post(
        f"{BASE_URL}/snippets",
        json=test_snippet,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Snippet ID: {data['id']}")
        print(f"Review Summary: {data['review']['summary']}")
        print(f"Rating: {data['review']['rating']}")
        print(f"Suggestions: {data['review']['suggestions']}")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_get_snippet(snippet_id):
    """Test retrieving a snippet"""
    if not snippet_id:
        print("No snippet ID to test")
        return
        
    print(f"Testing snippet retrieval for ID {snippet_id}...")
    response = requests.get(f"{BASE_URL}/snippets/{snippet_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved snippet: {data['language']} code")
        print(f"Review: {data['review']['summary']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_list_snippets():
    """Test listing all snippets"""
    print("Testing snippet listing...")
    response = requests.get(f"{BASE_URL}/snippets")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} snippets")
        for snippet in data:
            print(f"  - ID {snippet['id']}: {snippet['language']} ({snippet['review']['rating']}/10)")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("Code Review API Test Suite")
    print("=" * 40)
    
    # Wait a moment for the service to be ready
    print("Waiting for service to be ready...")
    time.sleep(2)
    
    try:
        test_health_check()
        snippet_id = test_create_snippet()
        test_get_snippet(snippet_id)
        test_list_snippets()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the service is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

