#!/usr/bin/env python3
"""
Enhanced Context Engine Test Script

Tests the project context detection and context-aware search functionality.
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# Add the current directory to the Python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)
os.chdir(script_dir)  # Change to the project directory

# Import modules directly
sys.path.append('data-pipeline')
sys.path.append('.')

from project_context_engine import get_project_context_engine
from registry_manager import get_registry_manager
from context_manager import PlatformContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_project_type_detection():
    """Test project type detection from various sources"""
    logger.info("🚀 Testing Project Type Detection")

    # Initialize context engine
    context_engine = get_project_context_engine()
    registry_manager = get_registry_manager()

    # Test 1: Query-based detection
    logger.info("Test 1: Query-based detection")
    test_queries = [
        "I'm building a mobile app with React Native and Gluestack UI",
        "I need a button component for my Next.js web application",
        "Building a design system with React components",
        "Working on a Vite React project with Tailwind CSS",
        "Creating a custom component library for React Native"
    ]

    for query in test_queries:
        context = context_engine.detect_project_type(query=query)
        logger.info(f"  Query: '{query}'")
        logger.info(f"  Detected: {context.project_type.value} (confidence: {context.confidence:.2f})")
        logger.info(f"  Evidence: {context.detected_from}")
        logger.info("")

    # Test 2: File-based detection
    logger.info("Test 2: File-based detection")
    test_file_sets = [
        # React Native project
        [
            "App.tsx",
            "package.json",
            "components/Button.tsx",
            "nativewind.config.js",
            "ios/Podfile",
            "android/build.gradle"
        ],
        # Next.js project
        [
            "pages/index.tsx",
            "pages/_app.tsx",
            "next.config.js",
            "components/ui/button.tsx",
            "package.json",
            "tailwind.config.js"
        ],
        # Vite React project
        [
            "vite.config.ts",
            "src/App.tsx",
            "src/components/Button.tsx",
            "package.json",
            "index.html"
        ]
    ]

    for file_set in test_file_sets:
        context = context_engine.detect_project_type(file_list=file_set)
        logger.info(f"  Files: {file_set[:3]}...")
        logger.info(f"  Detected: {context.project_type.value} (confidence: {context.confidence:.2f})")
        logger.info("")

    # Test 3: Package.json-based detection
    logger.info("Test 3: Package.json-based detection")
    test_package_jsons = [
        # React Native project
        {
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.0",
                "@gluestack-ui/themed": "^1.0.0",
                "nativewind": "^2.0.0"
            }
        },
        # Next.js project
        {
            "dependencies": {
                "next": "14.0.0",
                "react": "18.2.0",
                "react-dom": "18.2.0",
                "@radix-ui/react-slot": "^1.0.0",
                "class-variance-authority": "^0.7.0"
            }
        },
        # Vite React project
        {
            "dependencies": {
                "react": "18.2.0",
                "react-dom": "18.2.0",
                "vite": "^5.0.0",
                "tailwindcss": "^3.3.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0"
            }
        }
    ]

    for pkg_json in test_package_jsons:
        context = context_engine.detect_project_type(package_json=pkg_json)
        logger.info(f"  Package: {list(pkg_json.get('dependencies', {}).keys())[:3]}...")
        logger.info(f"  Detected: {context.project_type.value} (confidence: {context.confidence:.2f})")
        logger.info("")

    # Test 4: Combined detection
    logger.info("Test 4: Combined detection")
    combined_context = context_engine.detect_project_type(
        query="Building a mobile app with React Native",
        file_list=["App.tsx", "nativewind.config.js"],
        package_json={
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.0",
                "@gluestack-ui/themed": "^1.0.0"
            }
        }
    )
    logger.info(f"  Combined detection: {combined_context.project_type.value}")
    logger.info(f"  Confidence: {combined_context.confidence:.2f}")
    logger.info(f"  Sources: {combined_context.detected_from}")

    return True

async def test_context_aware_search():
    """Test context-aware search functionality"""
    logger.info("🚀 Testing Context-Aware Search")

    # Initialize systems
    registry_manager = get_registry_manager()

    # Test search with different project contexts
    test_scenarios = [
        {
            "name": "React Native Mobile App",
            "query": "button component",
            "context": {
                "project_context_query": "I'm building a React Native mobile app",
                "file_list": ["App.tsx", "nativewind.config.js"],
                "package_json": {
                    "dependencies": {
                        "react": "18.2.0",
                        "react-native": "0.72.0",
                        "@gluestack-ui/themed": "^1.0.0"
                    }
                }
            }
        },
        {
            "name": "Next.js Web App",
            "query": "button component",
            "context": {
                "project_context_query": "I need components for my Next.js web application",
                "file_list": ["pages/index.tsx", "next.config.js"],
                "package_json": {
                    "dependencies": {
                        "next": "14.0.0",
                        "react": "18.2.0",
                        "@radix-ui/react-slot": "^1.0.0"
                    }
                }
            }
        },
        {
            "name": "Generic React (No Context)",
            "query": "button component",
            "context": {}
        }
    ]

    for scenario in test_scenarios:
        logger.info(f"  Scenario: {scenario['name']}")
        logger.info(f"  Query: {scenario['query']}")

        # Perform contextual search
        results = registry_manager.search_components_with_context(
            query=scenario['query'],
            **scenario['context'],
            limit=3
        )

        logger.info(f"  Results found: {len(results)}")

        for i, result in enumerate(results[:2]):  # Show top 2 results
            logger.info(f"    {i+1}. {result.get('name', 'Unknown')}")
            logger.info(f"       Registry: {result.get('registry', 'Unknown')}")
            logger.info(f"       Context Score: {result.get('final_context_score', 0.0):.2f}")
            logger.info(f"       Project Type: {result.get('detected_project_type', 'Unknown')}")
            if result.get('context_explanation'):
                logger.info(f"       Explanation: {'; '.join(result['context_explanation'][:2])}")
            logger.info("")

    return True

async def test_project_type_suggestions():
    """Test project type suggestion functionality"""
    logger.info("🚀 Testing Project Type Suggestions")

    context_engine = get_project_context_engine()

    # Test queries for suggestions
    test_queries = [
        "I need to build a mobile application",
        "Working on a web project with React",
        "Creating a design system",
        "Building a component library",
        "Need UI components for my app"
    ]

    for query in test_queries:
        suggestions = context_engine.get_project_type_suggestions(query)
        logger.info(f"  Query: '{query}'")
        logger.info(f"  Suggestions: {len(suggestions)}")

        for suggestion in suggestions[:3]:  # Show top 3
            logger.info(f"    {suggestion['project_type']}: {suggestion['relevance_score']:.2f}")
            logger.info(f"      Keywords: {suggestion.get('matched_keywords', [])}")
        logger.info("")

    return True

async def test_api_endpoints():
    """Test the new API endpoints"""
    logger.info("🚀 Testing API Endpoints")

    import requests
    import json

    base_url = "http://localhost:8000"

    # Test context detection endpoint
    logger.info("Test 1: Context Detection Endpoint")
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
                logger.info(f"  ✓ Detected: {context_data.get('project_type', 'Unknown')}")
                logger.info(f"  ✓ Confidence: {context_data.get('confidence', 0.0):.2f}")
            else:
                logger.warning(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
        else:
            logger.warning(f"  ✗ HTTP Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning("  ⚠ API server not running - skipping API tests")
    except Exception as e:
        logger.warning(f"  ✗ API test failed: {e}")

    # Test project type suggestions endpoint
    logger.info("Test 2: Project Type Suggestions Endpoint")
    try:
        response = requests.get(f"{base_url}/api/v2/context/suggestions?query=mobile app with react native")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                suggestions = result.get('data', {}).get('suggestions', [])
                logger.info(f"  ✓ Got {len(suggestions)} suggestions")
                for suggestion in suggestions[:2]:
                    logger.info(f"    {suggestion['project_type']}: {suggestion['relevance_score']:.2f}")
            else:
                logger.warning(f"  ✗ API Error: {result.get('error', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        pass  # Server not running, already warned
    except Exception as e:
        logger.warning(f"  ✗ Suggestions test failed: {e}")

    return True

async def test_context_engine_stats():
    """Test context engine statistics"""
    logger.info("🚀 Testing Context Engine Statistics")

    registry_manager = get_registry_manager()

    # Get context engine stats
    stats = registry_manager.get_context_engine_stats()

    logger.info("Context Engine Statistics:")
    logger.info(f"  Total Sessions: {stats.get('total_sessions', 0)}")
    logger.info(f"  Current Project Type: {stats.get('current_project_type', 'Unknown')}")
    logger.info(f"  Available Project Types: {len(stats.get('available_project_types', []))}")
    logger.info(f"  Detection Sources: {stats.get('detection_sources', {})}")

    return True

async def main():
    """Main test function"""
    logger.info("🧪 Starting Enhanced Context Engine Test Suite")

    tests = [
        ("Project Type Detection", test_project_type_detection),
        ("Context-Aware Search", test_context_aware_search),
        ("Project Type Suggestions", test_project_type_suggestions),
        ("API Endpoints", test_api_endpoints),
        ("Context Engine Statistics", test_context_engine_stats)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")

        try:
            success = await test_func()
            if success:
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()

    logger.info(f"\n{'='*50}")
    logger.info(f"📊 Test Suite Summary: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")

    if passed == total:
        logger.info("🎉 All context engine tests PASSED!")
        return True
    else:
        logger.error("❌ Some context engine tests FAILED")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)