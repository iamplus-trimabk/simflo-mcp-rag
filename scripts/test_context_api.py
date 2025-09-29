#!/usr/bin/env python3
"""Test script for context engine API endpoints"""

import requests
import json
import sys

def test_context_detection():
    """Test project context detection endpoint"""
    base_url = "http://localhost:8000"

    print("🚀 Testing Context Engine API Endpoints")

    # Test 1: Context detection
    print("\nTest 1: Project Context Detection")
    context_request = {
        "query": "I'm building a React Native mobile app with Gluestack UI",
        "file_list": ["App.tsx", "nativewind.config.js"],
        "package_json": {
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.0",
                "@gluestack-ui/themed": "^1.0.0"
            }
        }
    }

    try:
        response = requests.post(f"{base_url}/api/v2/context/detect", json=context_request)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                context_data = result.get('data', {})
                print(f"  ✓ Detected: {context_data.get('project_type', 'Unknown')}")
                print(f"  ✓ Confidence: {context_data.get('confidence', 0.0):.2f}")
                print(f"  ✓ Evidence: {context_data.get('detected_from', [])}")
            else:
                print(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  ✗ Connection Error: {e}")

    # Test 2: Project type suggestions
    print("\nTest 2: Project Type Suggestions")
    try:
        response = requests.get(f"{base_url}/api/v2/context/suggestions?query=mobile app with react native")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                suggestions = result.get('data', {}).get('suggestions', [])
                print(f"  ✓ Got {len(suggestions)} suggestions")
                for suggestion in suggestions[:3]:
                    print(f"    {suggestion['project_type']}: {suggestion['relevance_score']:.2f}")
            else:
                print(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Suggestions Error: {e}")

    # Test 3: Context engine stats
    print("\nTest 3: Context Engine Statistics")
    try:
        response = requests.get(f"{base_url}/api/v2/context/stats")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                stats = result.get('data', {})
                print(f"  ✓ Total Sessions: {stats.get('total_sessions', 0)}")
                print(f"  ✓ Current Project Type: {stats.get('current_project_type', 'Unknown')}")
                print(f"  ✓ Available Project Types: {len(stats.get('available_project_types', []))}")
            else:
                print(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Stats Error: {e}")

    # Test 4: Contextual search
    print("\nTest 4: Contextual Search")
    search_request = {
        "query": "button component",
        "project_context_query": "I'm building a React Native mobile app",
        "limit": 5
    }

    try:
        response = requests.post(f"{base_url}/api/v2/search/contextual", json=search_request)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                results = result.get('data', {}).get('results', [])
                context_info = result.get('data', {}).get('context_info', {})
                print(f"  ✓ Found {len(results)} results")
                if context_info:
                    print(f"  ✓ Project Type: {context_info.get('detected_project_type', 'Unknown')}")
                    print(f"  ✓ Context Confidence: {context_info.get('context_confidence', 0.0):.2f}")
                for result in results[:2]:
                    print(f"    {result.get('name', 'Unknown')} (Score: {result.get('final_context_score', 0.0):.2f})")
            else:
                print(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Search Error: {e}")

if __name__ == "__main__":
    test_context_detection()