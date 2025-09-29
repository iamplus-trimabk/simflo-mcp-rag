#!/usr/bin/env python3
"""
Universal Search Test Script

Tests the unified search interface across components and documentation
with various scenarios and filtering options.
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the current directory to the Python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)
os.chdir(script_dir)  # Change to the project directory

# Import modules directly
sys.path.append('data-pipeline')
sys.path.append('.')

from universal_search import (
    get_universal_search_engine,
    UniversalSearchParams,
    SearchSourceType,
    SearchFilter,
    universal_search
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_basic_universal_search():
    """Test basic universal search functionality"""
    logger.info("🚀 Testing Basic Universal Search")

    engine = get_universal_search_engine()

    # Test 1: Component-only search
    logger.info("Test 1: Component-only search")
    results = universal_search(
        query="button",
        source_types=["component"],
        limit=3
    )

    logger.info(f"  Found {len(results)} component results")
    for result in results[:2]:
        logger.info(f"    {result.title} from {result.registry} (score: {result.final_score:.2f})")
    logger.info("")

    # Test 2: Documentation-only search
    logger.info("Test 2: Documentation-only search")
    results = universal_search(
        query="react hooks",
        source_types=["documentation"],
        limit=3
    )

    logger.info(f"  Found {len(results)} documentation results")
    for result in results[:2]:
        logger.info(f"    {result.title} from {result.registry} (score: {result.final_score:.2f})")
    logger.info("")

    # Test 3: Combined search
    logger.info("Test 3: Combined search (components + documentation)")
    results = universal_search(
        query="button",
        source_types=["component", "documentation"],
        limit=5
    )

    logger.info(f"  Found {len(results)} total results")
    source_types = {}
    for result in results:
        source_type = result.source_type.value
        source_types[source_type] = source_types.get(source_type, 0) + 1

    for source_type, count in source_types.items():
        logger.info(f"    {source_type}: {count} results")
    logger.info("")

    return True

async def test_context_aware_search():
    """Test context-aware universal search"""
    logger.info("🚀 Testing Context-Aware Universal Search")

    # Test different project contexts
    test_scenarios = [
        {
            "name": "React Native Mobile App",
            "query": "button component",
            "context": "I'm building a React Native mobile app with navigation"
        },
        {
            "name": "Next.js Web Application",
            "query": "button component",
            "context": "I need components for my Next.js web application"
        },
        {
            "name": "Generic React Project",
            "query": "button component",
            "context": None
        }
    ]

    for scenario in test_scenarios:
        logger.info(f"  Scenario: {scenario['name']}")
        logger.info(f"  Query: {scenario['query']}")

        results = universal_search(
            query=scenario['query'],
            source_types=["component"],
            project_context_query=scenario['context'],
            limit=3
        )

        logger.info(f"  Results found: {len(results)}")
        for result in results[:2]:
            logger.info(f"    {result.title} ({result.source_type.value})")
            logger.info(f"      Score: {result.final_score:.2f}")
            logger.info(f"      Context: {result.detected_project_type}")
            if result.context_explanations:
                logger.info(f"      Why: {'; '.join(result.context_explanations[:1])}")
        logger.info("")

    return True

async def test_advanced_filtering():
    """Test advanced filtering capabilities"""
    logger.info("🚀 Testing Advanced Filtering")

    engine = get_universal_search_engine()

    # Test registry filtering
    logger.info("Test 1: Registry filtering")
    results = universal_search(
        query="button",
        filters={"registry": "gluestack_db"},
        limit=5
    )

    logger.info(f"  Gluestack-only results: {len(results)}")
    for result in results[:2]:
        logger.info(f"    {result.title} from {result.registry}")
    logger.info("")

    # Test platform filtering
    logger.info("Test 2: Platform filtering")
    results = universal_search(
        query="button",
        filters={"platform": "reactnative"},
        limit=5
    )

    logger.info(f"  React Native results: {len(results)}")
    for result in results[:2]:
        logger.info(f"    {result.title} - Platforms: {result.metadata.get('platform', [])}")
    logger.info("")

    # Test combined filtering
    logger.info("Test 3: Combined filtering")
    results = universal_search(
        query="button",
        filters={
            "registry": "shadcn_db",
            "platform": "reactjs"
        },
        limit=5
    )

    logger.info(f"  Shadcn + ReactJS results: {len(results)}")
    for result in results[:2]:
        logger.info(f"    {result.title} from {result.registry}")
    logger.info("")

    return True

async def test_search_statistics():
    """Test search statistics and available filters"""
    logger.info("🚀 Testing Search Statistics")

    engine = get_universal_search_engine()

    # Get system statistics
    stats = engine.get_search_statistics()
    logger.info("System Statistics:")
    logger.info(f"  Total Registries: {stats['total_registries']}")
    logger.info(f"  Components: {stats['total_components']}")
    logger.info(f"  Documentation Pages: {stats['total_documentation_pages']}")
    logger.info("")

    # Get available filters
    filters = stats['available_filters']
    logger.info("Available Filters:")
    for filter_type, options in filters.items():
        if options:
            logger.info(f"  {filter_type}: {len(options)} options")
            logger.info(f"    {options[:5]}{'...' if len(options) > 5 else ''}")
    logger.info("")

    return True

async def test_ranking_and_scoring():
    """Test result ranking and scoring mechanisms"""
    logger.info("🚀 Testing Ranking and Scoring")

    # Test the same query with different contexts
    queries = [
        ("button", "React Native mobile app development"),
        ("button", "Next.js web application"),
        ("button", None)
    ]

    for query, context in queries:
        context_desc = context if context else "No context"
        logger.info(f"  Query: '{query}' with context: '{context_desc}'")

        results = universal_search(
            query=query,
            source_types=["component"],
            project_context_query=context,
            limit=3
        )

        if results:
            logger.info(f"  Top result: {results[0].title}")
            logger.info(f"    Final Score: {results[0].final_score:.2f}")
            logger.info(f"    Relevance: {results[0].relevance_score:.2f}")
            logger.info(f"    Context: {results[0].context_score:.2f}")
            logger.info(f"    Project Type: {results[0].detected_project_type}")
        logger.info("")

    return True

async def test_error_handling():
    """Test error handling and edge cases"""
    logger.info("🚀 Testing Error Handling")

    engine = get_universal_search_engine()

    # Test empty query
    logger.info("Test 1: Empty query")
    try:
        results = universal_search(query="", limit=5)
        logger.info(f"  Empty query returned {len(results)} results")
    except Exception as e:
        logger.info(f"  Empty query handled: {e}")
    logger.info("")

    # Test non-existent filters
    logger.info("Test 2: Non-existent filters")
    try:
        results = universal_search(
            query="button",
            filters={"registry": "non_existent_registry"},
            limit=5
        )
        logger.info(f"  Non-existent filter returned {len(results)} results")
    except Exception as e:
        logger.info(f"  Non-existent filter handled: {e}")
    logger.info("")

    # Test very high limit
    logger.info("Test 3: High limit")
    try:
        results = universal_search(query="button", limit=1000)
        logger.info(f"  High limit returned {len(results)} results")
    except Exception as e:
        logger.info(f"  High limit handled: {e}")
    logger.info("")

    return True

async def main():
    """Main test function"""
    logger.info("🧪 Starting Universal Search Test Suite")

    tests = [
        ("Basic Universal Search", test_basic_universal_search),
        ("Context-Aware Search", test_context_aware_search),
        ("Advanced Filtering", test_advanced_filtering),
        ("Search Statistics", test_search_statistics),
        ("Ranking and Scoring", test_ranking_and_scoring),
        ("Error Handling", test_error_handling)
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
        logger.info("🎉 All universal search tests PASSED!")
        return True
    else:
        logger.error("❌ Some universal search tests FAILED")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)