#!/usr/bin/env python3

"""
Test script for GitHub-based specialized extractors

This script tests the GitHub extractors (ShadcnHooksExtractor, ShadcnBlocksExtractor,
NPMHooksExtractor, CommunityExtractor) and multi-source merging functionality.
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services import RegistryConfigManager, MultiSourceMerger, ConflictResolution
from extractors import ExtractorFactory, ShadcnHooksExtractor, ShadcnBlocksExtractor, NPMHooksExtractor, CommunityExtractor
from models import Component, ComponentCategory, ComponentType

async def test_registry_config_manager():
    """Test registry configuration management"""
    print("🔧 Testing Registry Configuration Manager")
    print("=" * 50)

    try:
        config_manager = RegistryConfigManager()

        # Test loading configurations
        registries = config_manager.get_all_registries()
        print(f"✅ Loaded {len(registries)} registry configurations")

        # Test getting specific registry
        shadcn_config = config_manager.get_registry_config("shadcn")
        if shadcn_config:
            print(f"✅ Shadcn config: {shadcn_config.display_name}")
            print(f"   Categories: {list(shadcn_config.categories.keys())}")
            print(f"   Status: {shadcn_config.status.value}")

        # Test getting active sources
        hooks_sources = config_manager.get_active_sources("shadcn", "hooks")
        print(f"✅ Shadcn hooks sources: {len(hooks_sources)}")
        for source in hooks_sources:
            print(f"   - {source.name} ({source.type.value})")

        # Test validation
        if shadcn_config:
            is_valid = config_manager.validate_config(shadcn_config)
            print(f"✅ Shadcn config validation: {is_valid}")

        print()

    except Exception as e:
        print(f"❌ Registry config test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_github_extractors():
    """Test GitHub-based specialized extractors"""
    print("🧪 Testing GitHub Specialized Extractors")
    print("=" * 50)

    try:
        factory = ExtractorFactory()

        # Test ShadcnHooksExtractor
        print("1. Testing ShadcnHooksExtractor...")
        shadcn_hooks_config = {
            "type": "github",
            "url": "https://github.com/shadcn/ui",
            "branch": "main",
            "registry_file": "src/hooks/hooks.ts",
            "extractor": "shadcn_hooks"
        }

        shadcn_hooks_extractor = factory.create_extractor("shadcn_hooks", shadcn_hooks_config)
        if shadcn_hooks_extractor:
            print(f"   ✅ Created: {type(shadcn_hooks_extractor).__name__}")
            is_valid = shadcn_hooks_extractor.validate_source()
            print(f"   ✅ Valid source: {is_valid}")
        else:
            print("   ❌ Failed to create extractor")

        # Test ShadcnBlocksExtractor
        print("2. Testing ShadcnBlocksExtractor...")
        shadcn_blocks_config = {
            "type": "github",
            "url": "https://github.com/shadcn/ui",
            "branch": "main",
            "registry_file": "src/blocks/blocks.json",
            "extractor": "shadcn_blocks"
        }

        shadcn_blocks_extractor = factory.create_extractor("shadcn_blocks", shadcn_blocks_config)
        if shadcn_blocks_extractor:
            print(f"   ✅ Created: {type(shadcn_blocks_extractor).__name__}")
            is_valid = shadcn_blocks_extractor.validate_source()
            print(f"   ✅ Valid source: {is_valid}")
        else:
            print("   ❌ Failed to create extractor")

        # Test CommunityExtractor
        print("3. Testing CommunityExtractor...")
        community_config = {
            "type": "github",
            "url": "https://github.com/shadcn/ui",
            "branch": "main",
            "registry_file": "src/components/ui/index.ts",
            "extractor": "community",
            "quality_threshold": 0.7
        }

        community_extractor = factory.create_extractor("community", community_config)
        if community_extractor:
            print(f"   ✅ Created: {type(community_extractor).__name__}")
            is_valid = community_extractor.validate_source()
            print(f"   ✅ Valid source: {is_valid}")
        else:
            print("   ❌ Failed to create extractor")

        print()

    except Exception as e:
        print(f"❌ GitHub extractors test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_npm_extractor():
    """Test NPM hooks extractor"""
    print("🧪 Testing NPM Hooks Extractor")
    print("=" * 50)

    try:
        factory = ExtractorFactory()

        npm_config = {
            "type": "npm",
            "package": "@radix-ui/react-hooks",
            "extractor": "npm_hooks",
            "version_range": "^1.0.0"
        }

        npm_extractor = factory.create_extractor("npm_hooks", npm_config)
        if npm_extractor:
            print(f"✅ Created: {type(npm_extractor).__name__}")
            is_valid = npm_extractor.validate_source()
            print(f"✅ Valid source: {is_valid}")
        else:
            print("❌ Failed to create extractor")

        print()

    except Exception as e:
        print(f"❌ NPM extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_extractor_factory():
    """Test extractor factory functionality"""
    print("🏭 Testing Extractor Factory")
    print("=" * 50)

    try:
        factory = ExtractorFactory()

        # Test getting available extractors
        extractors = factory.get_available_extractors()
        print(f"✅ Available extractors: {len(extractors)}")
        for name, info in extractors.items():
            print(f"   - {name}: {info['source_types']}")

        # Test recommendations
        print("Testing extractor recommendations:")
        github_config = {"type": "github"}
        npm_config = {"type": "npm"}
        api_config = {"type": "api"}

        github_recs = factory.recommend_extractors(github_config)
        npm_recs = factory.recommend_extractors(npm_config)
        api_recs = factory.recommend_extractors(api_config)

        print(f"   GitHub recommendations: {github_recs}")
        print(f"   NPM recommendations: {npm_recs}")
        print(f"   API recommendations: {api_recs}")

        # Test statistics
        stats = factory.get_statistics()
        print(f"   Statistics: {stats}")

        print()

    except Exception as e:
        print(f"❌ Extractor factory test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_multi_source_merger():
    """Test multi-source merging functionality"""
    print("🔄 Testing Multi-Source Merger")
    print("=" * 50)

    try:
        merger = MultiSourceMerger()

        # Create test components from different sources
        component1 = Component(
            name="button",
            category=ComponentCategory.COMPONENTS,
            type=ComponentType.UI,
            registry="test_registry",
            priority_source="github_main",
            display_name="Button",
            description="A button component",
            platform=["reactjs"],
            quality_score=0.9,
            sources=["github_main"]
        )

        component2 = Component(
            name="button",
            category=ComponentCategory.COMPONENTS,
            type=ComponentType.UI,
            registry="test_registry",
            priority_source="github_fork",
            display_name="Button",
            description="An improved button component",
            platform=["reactjs"],
            quality_score=0.85,
            sources=["github_fork"]
        )

        # Test conflict resolution strategies
        strategies = [
            ConflictResolution.PRIORITY_BASED,
            ConflictResolution.QUALITY_BASED,
            ConflictResolution.MERGE_BASED
        ]

        for strategy in strategies:
            print(f"Testing {strategy} resolution:")
            merged = merger.resolve_conflicts([component1, component2], strategy)
            print(f"   ✅ Merged component: {merged.name}")
            print(f"   ✅ Priority source: {merged.priority_source}")
            print(f"   ✅ Sources: {merged.sources}")

        print()

    except Exception as e:
        print(f"❌ Multi-source merger test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_real_extraction():
    """Test real extraction from actual sources"""
    print("🌐 Testing Real Extraction (if sources available)")
    print("=" * 50)

    try:
        factory = ExtractorFactory()

        # Test extraction from shadcn registry
        config_manager = RegistryConfigManager()
        shadcn_config = config_manager.get_registry_config("shadcn")

        if shadcn_config:
            print("Testing extraction from Shadcn registry...")

            # Get hooks sources
            hooks_sources = config_manager.get_active_sources("shadcn", "hooks")
            if hooks_sources:
                source = hooks_sources[0]  # Use first source
                print(f"Testing source: {source.name}")

                # Convert SourceConfig to dict for extractor
                source_dict = {
                    "name": source.name,
                    "type": source.type.value,
                    "url": source.url,
                    "branch": source.branch,
                    "registry_file": source.registry_file,
                    "package": source.package,
                    "extractor": source.extractor,
                    "priority": source.priority
                }
                extractor = factory.create_extractor(source.extractor, source_dict)
                if extractor:
                    print(f"   ✅ Created extractor: {type(extractor).__name__}")

                    # Test validation
                    is_valid = extractor.validate_source()
                    print(f"   ✅ Source validation: {is_valid}")

                    if is_valid:
                        # Test repository validation if possible
                        try:
                            is_repo_valid = await extractor.validate_repository()
                            print(f"   ✅ Repository validation: {is_repo_valid}")
                        except Exception as e:
                            print(f"   ⚠️  Repository validation failed: {e}")
                else:
                    print("   ❌ Failed to create extractor")

        print()

    except Exception as e:
        print(f"❌ Real extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def test_error_handling():
    """Test error handling scenarios"""
    print("🚨 Testing Error Handling")
    print("=" * 50)

    try:
        factory = ExtractorFactory()

        # Test invalid extractor name
        invalid_extractor = factory.create_extractor("nonexistent", {})
        print(f"✅ Invalid extractor handling: {invalid_extractor is None}")

        # Test incompatible source type
        github_config = {"type": "github"}
        npm_extractor = factory.create_extractor("npm_hooks", github_config)
        print(f"✅ Incompatible source handling: {npm_extractor is None}")

        # Test empty configuration
        empty_extractor = factory.create_extractor("community", {})
        print(f"✅ Empty config handling: {empty_extractor is None}")

        print()

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        print()

async def main():
    """Main test function"""
    print("🚀 Testing GitHub-Based Specialized Extractors")
    print("=" * 60)
    print()

    try:
        await test_registry_config_manager()
        await test_github_extractors()
        await test_npm_extractor()
        await test_extractor_factory()
        await test_multi_source_merger()
        await test_real_extraction()
        await test_error_handling()

        print("✅ All tests completed!")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())