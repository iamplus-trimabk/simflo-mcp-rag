#!/usr/bin/env python3
"""
Test script for GitLab and Bitbucket extractors

This script validates that the new GitLab and Bitbucket extractors work correctly
with the updated ExtractorFactory and configuration system.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.registry_config_manager import RegistryConfigManager
from extractors.extractor_factory import get_extractor_factory
from utils.logger import setup_logging

async def test_gitlab_extractor():
    """Test GitLab extractor with sample configuration"""
    print("🧪 Testing GitLab Extractor")
    print("=" * 40)

    # Test configuration
    gitlab_config = {
        "name": "gitlab_test",
        "type": "gitlab",
        "project_path": "gitlab-org/gitlab-ui",
        "branch": "main",
        "registry_file": "src/components/index.js",
        "extractor": "community",
        "url": "https://gitlab.com/gitlab-org/gitlab-ui"
    }

    factory = get_extractor_factory()

    # Test extractor compatibility
    print("1. Testing extractor compatibility...")
    compatible = factory.validate_extractor_compatibility(gitlab_config, "community")
    print(f"   Compatible: {'✅' if compatible else '❌'}")

    # Test extractor creation
    print("2. Testing extractor creation...")
    extractor = factory.create_extractor("community", gitlab_config)
    print(f"   Created: {'✅' if extractor else '❌'}")

    if extractor:
        # Test validation
        print("3. Testing source validation...")
        valid = extractor.validate_source()
        print(f"   Valid: {'✅' if valid else '❌'}")

        # Test factory test method
        print("4. Testing factory test method...")
        test_result = factory.test_extractor("community", gitlab_config)
        print(f"   Test result: {'✅' if test_result['success'] else '❌'}")
        if test_result['errors']:
            print(f"   Errors: {test_result['errors']}")
        if test_result['warnings']:
            print(f"   Warnings: {test_result['warnings']}")

    print()

async def test_bitbucket_extractor():
    """Test Bitbucket extractor with sample configuration"""
    print("🧪 Testing Bitbucket Extractor")
    print("=" * 40)

    # Test configuration
    bitbucket_config = {
        "name": "bitbucket_test",
        "type": "bitbucket",
        "workspace": "atlassian",
        "repo_slug": "atlassian-frontend",
        "branch": "master",
        "registry_file": "packages/design-system/src/components/index.ts",
        "extractor": "community",
        "url": "https://bitbucket.org/atlassian/atlassian-frontend"
    }

    factory = get_extractor_factory()

    # Test extractor compatibility
    print("1. Testing extractor compatibility...")
    compatible = factory.validate_extractor_compatibility(bitbucket_config, "community")
    print(f"   Compatible: {'✅' if compatible else '❌'}")

    # Test extractor creation
    print("2. Testing extractor creation...")
    extractor = factory.create_extractor("community", bitbucket_config)
    print(f"   Created: {'✅' if extractor else '❌'}")

    if extractor:
        # Test validation
        print("3. Testing source validation...")
        valid = extractor.validate_source()
        print(f"   Valid: {'✅' if valid else '❌'}")

        # Test factory test method
        print("4. Testing factory test method...")
        test_result = factory.test_extractor("community", bitbucket_config)
        print(f"   Test result: {'✅' if test_result['success'] else '❌'}")
        if test_result['errors']:
            print(f"   Errors: {test_result['errors']}")
        if test_result['warnings']:
            print(f"   Warnings: {test_result['warnings']}")

    print()

async def test_registry_config():
    """Test registry configuration with new source types"""
    print("🧪 Testing Registry Configuration")
    print("=" * 40)

    config_manager = RegistryConfigManager()

    # Test GitLab config loading
    print("1. Testing GitLab config loading...")
    try:
        gitlab_config = config_manager.load_registry_config("gitlab_test")
        print(f"   Loaded: {'✅' if gitlab_config else '❌'}")
        if gitlab_config:
            print(f"   Registry name: {gitlab_config.registry_name}")
            if hasattr(gitlab_config, 'categories') and hasattr(gitlab_config.categories, 'components'):
                print(f"   Components sources: {len(gitlab_config.categories.components.sources)}")
            if hasattr(gitlab_config, 'categories') and hasattr(gitlab_config.categories, 'hooks'):
                print(f"   Hooks sources: {len(gitlab_config.categories.hooks.sources)}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test Bitbucket config loading
    print("2. Testing Bitbucket config loading...")
    try:
        bitbucket_config = config_manager.load_registry_config("bitbucket_test")
        print(f"   Loaded: {'✅' if bitbucket_config else '❌'}")
        if bitbucket_config:
            print(f"   Registry name: {bitbucket_config.registry_name}")
            if hasattr(bitbucket_config, 'categories') and hasattr(bitbucket_config.categories, 'components'):
                print(f"   Components sources: {len(bitbucket_config.categories.components.sources)}")
            if hasattr(bitbucket_config, 'categories') and hasattr(bitbucket_config.categories, 'hooks'):
                print(f"   Hooks sources: {len(bitbucket_config.categories.hooks.sources)}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

async def test_factory_capabilities():
    """Test factory capabilities with new source types"""
    print("🧪 Testing Factory Capabilities")
    print("=" * 40)

    factory = get_extractor_factory()

    # Test available extractors
    print("1. Testing available extractors...")
    extractors = factory.get_available_extractors()
    print(f"   Total extractors: {len(extractors)}")

    # Check if extractors support new source types
    gitlab_supported = False
    bitbucket_supported = False
    for name, info in extractors.items():
        if "gitlab" in info["source_types"]:
            gitlab_supported = True
            print(f"   {name} supports GitLab ✅")
        if "bitbucket" in info["source_types"]:
            bitbucket_supported = True
            print(f"   {name} supports Bitbucket ✅")

    if not gitlab_supported:
        print("   No extractors support GitLab ❌")
    if not bitbucket_supported:
        print("   No extractors support Bitbucket ❌")

    # Test recommendations
    print("2. Testing extractor recommendations...")
    gitlab_config = {"type": "gitlab"}
    bitbucket_config = {"type": "bitbucket"}

    gitlab_recs = factory.recommend_extractors(gitlab_config)
    bitbucket_recs = factory.recommend_extractors(bitbucket_config)

    print(f"   GitLab recommendations: {gitlab_recs}")
    print(f"   Bitbucket recommendations: {bitbucket_recs}")

    # Test statistics
    print("3. Testing factory statistics...")
    stats = factory.get_statistics()
    print(f"   Registered extractors: {stats['registered_extractors']}")
    print(f"   Built-in extractors: {stats['builtin_extractors']}")
    print(f"   Loaded extractors: {stats['loaded_extractors']}")

    print()

async def main():
    """Main test function"""
    print("🚀 Testing GitLab and Bitbucket Extractors")
    print("=" * 50)
    print()

    # Setup logging
    setup_logging(level="INFO")

    try:
        await test_gitlab_extractor()
        await test_bitbucket_extractor()
        await test_registry_config()
        await test_factory_capabilities()

        print("✅ All tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())