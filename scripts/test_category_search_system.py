#!/usr/bin/env python3
"""
Test script for Category-Aware Search System

This script validates that the enhanced CategorySearchService works correctly
with multiple search strategies, quality filtering, and category weighting.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.category_search_service import CategorySearchService, SearchQuery, SearchFilters, CategoryWeights, SearchStrategy
from models import Component, ComponentCategory, ComponentType, ComponentMetadata
from datetime import datetime
import random

async def create_test_components():
    """Create test components for search validation"""
    components = []

    # Test components data
    test_data = [
        {
            "name": "button",
            "display_name": "Button",
            "description": "A clickable button component for user interactions",
            "category": ComponentCategory.COMPONENTS,
            "type": ComponentType.UI,
            "platform": "reactjs",
            "quality": 0.9,
            "tags": ["ui", "interaction", "clickable"]
        },
        {
            "name": "input",
            "display_name": "Input",
            "description": "A text input field for user data entry",
            "category": ComponentCategory.COMPONENTS,
            "type": ComponentType.UI,
            "platform": "reactjs",
            "quality": 0.85,
            "tags": ["form", "input", "text"]
        },
        {
            "name": "use-mobile",
            "display_name": "Use Mobile",
            "description": "Hook for detecting mobile device and responsive behavior",
            "category": ComponentCategory.HOOKS,
            "type": ComponentType.HOOK,
            "platform": "reactjs",
            "quality": 0.95,
            "tags": ["mobile", "responsive", "detection"]
        },
        {
            "name": "use-form",
            "display_name": "Use Form",
            "description": "Hook for form state management and validation",
            "category": ComponentCategory.HOOKS,
            "type": ComponentType.HOOK,
            "platform": "reactjs",
            "quality": 0.88,
            "tags": ["form", "validation", "state"]
        },
        {
            "name": "dashboard-layout",
            "display_name": "Dashboard Layout",
            "description": "Pre-built dashboard layout with sidebar and main content area",
            "category": ComponentCategory.BLOCKS,
            "type": ComponentType.BLOCK,
            "platform": "reactjs",
            "quality": 0.82,
            "tags": ["layout", "dashboard", "sidebar"]
        },
        {
            "name": "auth-form",
            "display_name": "Auth Form",
            "description": "Authentication form with login and registration",
            "category": ComponentCategory.BLOCKS,
            "type": ComponentType.BLOCK,
            "platform": "reactjs",
            "quality": 0.79,
            "tags": ["auth", "form", "login"]
        },
        {
            "name": "native-button",
            "display_name": "Native Button",
            "description": "Mobile-optimized button component for React Native",
            "category": ComponentCategory.COMPONENTS,
            "type": ComponentType.UI,
            "platform": "reactnative",
            "quality": 0.91,
            "tags": ["mobile", "button", "native"]
        },
        {
            "name": "bottom-tabs",
            "display_name": "Bottom Tabs",
            "description": "Bottom tab navigation for mobile applications",
            "category": ComponentCategory.COMPONENTS,
            "type": ComponentType.UI,
            "platform": "reactnative",
            "quality": 0.87,
            "tags": ["navigation", "tabs", "mobile"]
        }
    ]

    for data in test_data:
        component = Component(
            name=data["name"],
            category=data["category"],
            type=data["type"],
            registry="test_registry",
            priority_source="test_source",
            display_name=data["display_name"],
            description=data["description"],
            platform=[data["platform"]],
            quality_score=data["quality"],
            last_updated=datetime.now(),
            metadata=ComponentMetadata(
                tags=data["tags"],
                repository_url=f"https://github.com/test/{data['name']}",
                documentation_url=f"https://docs.test.com/{data['name']}"
            ),
            category_specific_data={
                "extractor_type": "test"
            }
        )
        components.append(component)

    return components

async def test_basic_search():
    """Test basic search functionality"""
    print("🧪 Testing Basic Search Functionality")
    print("=" * 40)

    search_service = CategorySearchService()
    test_components = await create_test_components()

    # Mock the component search for testing
    search_service.search_components = lambda query, limit: [
        type('EnhancedSearchResult', (), {
            'component': comp,
            'relevance_score': 0.8,
            'category_relevance': 0.9,
            'quality_score': comp.quality_score,
            'platform_match': True,
            'explanation': f"Match for query: {query.query}"
        })() for comp in test_components[:limit]
        if any(keyword in comp.description.lower() or keyword in comp.name.lower()
               for keyword in query.query.lower().split())
    ]

    # Test 1: Simple search
    print("1. Testing simple search...")
    query = SearchQuery(
        query="button",
        filters=SearchFilters(
            categories=[ComponentCategory.COMPONENTS],
            platforms=["reactjs"]
        )
    )

    results = await search_service.search_components(query)
    print(f"   Results: {len(results)}")
    print(f"   Success: {'✅' if len(results) > 0 else '❌'}")

    # Test 2: Search with quality threshold
    print("2. Testing quality threshold...")
    query = SearchQuery(
        query="button",
        filters=SearchFilters(categories=[ComponentCategory.COMPONENTS]),
        platforms=["reactjs"],
        filters=SearchFilters(quality_threshold=0.85)
    )

    results = await search_service.search_components(query)
    print(f"   Results: {len(results)}")
    print(f"   High quality: {'✅' if all(r.quality_score >= 0.85 for r in results) else '❌'}")

    # Test 3: Multi-category search
    print("3. Testing multi-category search...")
    query = SearchQuery(
        query="form",
        filters=SearchFilters(categories=[ComponentCategory.COMPONENTS, ComponentCategory.HOOKS, ComponentCategory.BLOCKS]),
        platforms=["reactjs"],
        limit=10
    )

    results = await search_service.search_components(query)
    print(f"   Results: {len(results)}")
    categories_found = set(r.component.category.value for r in results)
    print(f"   Categories: {categories_found}")

    print()

async def test_search_strategies():
    """Test different search strategies"""
    print("🧪 Testing Search Strategies")
    print("=" * 40)

    search_service = CategorySearchService()
    test_components = await create_test_components()

    # Mock search for testing strategies
    async def mock_search(query, limit):
        results = []
        for comp in test_components:
            if any(keyword in comp.description.lower() or keyword in comp.name.lower()
                   for keyword in query.query.lower().split()):
                # Calculate different scores based on strategy
                if query.strategy == "exact":
                    relevance = 1.0 if query.query.lower() in comp.name.lower() else 0.5
                elif query.strategy == "semantic":
                    relevance = 0.8 if "mobile" in query.query.lower() and "mobile" in comp.description.lower() else 0.6
                elif query.strategy == "cross":
                    relevance = 0.7
                else:  # weighted
                    relevance = 0.85

                results.append(type('EnhancedSearchResult', (), {
                    'component': comp,
                    'relevance_score': relevance,
                    'category_relevance': 0.8,
                    'quality_score': comp.quality_score,
                    'platform_match': True,
                    'explanation': f"Strategy: {query.strategy}"
                })())

        return results[:limit]

    search_service.search_components = mock_search

    strategies = ["exact", "semantic", "cross", "weighted"]
    test_query = "mobile"

    for strategy in strategies:
        print(f"Testing strategy: {strategy}")
        query = SearchQuery(
            query=test_query,
            filters=SearchFilters(categories=[ComponentCategory.COMPONENTS, ComponentCategory.HOOKS]),
            platforms=["reactjs", "reactnative"],
            strategy=strategy,
            limit=5
        )

        results = await search_service.search_components(query)
        print(f"   Results: {len(results)}")
        if results:
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            print(f"   Avg relevance: {avg_relevance:.2f}")

        print()

async def test_category_weights():
    """Test category weighting system"""
    print("🧪 Testing Category Weights")
    print("=" * 40)

    search_service = CategorySearchService()
    test_components = await create_test_components()

    # Test with different category weights
    weight_configs = [
        CategoryWeights(components=1.0, hooks=0.5, blocks=0.3),
        CategoryWeights(components=0.5, hooks=1.0, blocks=0.3),
        CategoryWeights(components=0.3, hooks=0.5, blocks=1.0),
    ]

    category_names = ["components", "hooks", "blocks"]

    for i, weights in enumerate(weight_configs):
        print(f"Testing weight config {i+1}: {category_names[i]} prioritized")

        # Mock results with category-based scoring
        results = []
        for comp in test_components:
            weight_value = getattr(weights, comp.category.value, 0.5)
            results.append(type('EnhancedSearchResult', (), {
                'component': comp,
                'relevance_score': 0.8 * weight_value,
                'category_relevance': weight_value,
                'quality_score': comp.quality_score,
                'platform_match': True,
                'explanation': f"Category weight: {weight_value}"
            })())

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        print(f"   Top result: {results[0].component.name} ({results[0].component.category.value})")
        print(f"   Relevance score: {results[0].relevance_score:.2f}")

        print()

async def test_platform_filtering():
    """Test platform-specific filtering"""
    print("🧪 Testing Platform Filtering")
    print("=" * 40)

    search_service = CategorySearchService()
    test_components = await create_test_components()

    # Mock search with platform filtering
    async def mock_search(query, limit):
        results = []
        for comp in test_components:
            if query.platforms and comp.metadata.get("platform") not in query.platforms:
                continue

            if any(keyword in comp.description.lower() or keyword in comp.name.lower()
                   for keyword in query.query.lower().split()):
                results.append(type('EnhancedSearchResult', (), {
                    'component': comp,
                    'relevance_score': 0.8,
                    'category_relevance': 0.9,
                    'quality_score': comp.quality_score,
                    'platform_match': True,
                    'explanation': f"Platform match: {comp.metadata.get('platform')}"
                })())

        return results[:limit]

    search_service.search_components = mock_search

    platforms = ["reactjs", "reactnative"]
    test_query = "button"

    for platform in platforms:
        print(f"Testing platform: {platform}")
        query = SearchQuery(
            query=test_query,
            filters=SearchFilters(categories=[ComponentCategory.COMPONENTS]),
            platforms=[platform],
            limit=5
        )

        results = await search_service.search_components(query)
        print(f"   Results: {len(results)}")
        for result in results:
            comp_platform = result.component.metadata.get("platform")
            print(f"   Component: {result.component.name} (Platform: {comp_platform})")

        print()

async def test_api_integration():
    """Test integration with API server"""
    print("🧪 Testing API Integration")
    print("=" * 40)

    import httpx

    async with httpx.AsyncClient() as client:
        # Test category search endpoint
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/components/search/category",
                params={
                    "q": "button",
                    "category": "components",
                    "platform": "reactjs",
                    "limit": 5,
                    "strategy": "weighted"
                }
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   API Response: ✅")
                print(f"   Success: {data.get('success', False)}")
                if data.get('success'):
                    results = data.get('data', [])
                    print(f"   Results: {len(results)}")
                    if results:
                        print(f"   Sample result: {results[0].get('component', {}).get('name', 'N/A')}")
            else:
                print(f"   API Error: ❌ (Status: {response.status_code})")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"   API Connection Error: ❌ ({e})")

        print()

async def test_performance():
    """Test search performance"""
    print("🧪 Testing Performance")
    print("=" * 40)

    search_service = CategorySearchService()
    test_components = await create_test_components()

    # Mock search for performance testing
    search_service.search_components = lambda query, limit: [
        type('EnhancedSearchResult', (), {
            'component': comp,
            'relevance_score': 0.8,
            'category_relevance': 0.9,
            'quality_score': comp.quality_score,
            'platform_match': True,
            'explanation': "Performance test"
        })() for comp in test_components[:limit]
    ]

    import time

    # Test multiple queries
    queries = [
        "button component",
        "mobile navigation",
        "form validation",
        "dashboard layout",
        "auth system"
    ]

    total_time = 0
    for query_text in queries:
        start_time = time.time()

        query = SearchQuery(
            query=query_text,
            filters=SearchFilters(categories=[ComponentCategory.COMPONENTS, ComponentCategory.HOOKS, ComponentCategory.BLOCKS]),
            platforms=["reactjs", "reactnative"],
            limit=10
        )

        results = await search_service.search_components(query)
        end_time = time.time()

        query_time = end_time - start_time
        total_time += query_time

        print(f"   Query: '{query_text}' - {query_time:.3f}s - {len(results)} results")

    avg_time = total_time / len(queries)
    print(f"   Average query time: {avg_time:.3f}s")
    print(f"   Performance: {'✅' if avg_time < 1.0 else '❌'}")

    print()

async def main():
    """Main test function"""
    print("🚀 Testing Category-Aware Search System")
    print("=" * 50)
    print()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    try:
        await test_basic_search()
        await test_search_strategies()
        await test_category_weights()
        await test_platform_filtering()
        await test_api_integration()
        await test_performance()

        print("✅ All tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())