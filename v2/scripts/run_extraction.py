#!/usr/bin/env python3
"""
Convenient script to run the extraction pipeline with various options

This script provides a simple interface to run the extraction pipeline
with different modes and configurations.

Usage:
    python3 scripts/run_extraction.py [mode] [options]

Modes:
    test: Run in test mode with mock data
    real: Run with real data extraction
    merge: Only merge existing extracted data
    summary: Generate summary of existing data
    clean: Clean up extracted data files
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.real_extraction_pipeline import RealExtractionPipeline
from services.registry_config_manager import RegistryConfigManager
from utils.logger import setup_logging

async def run_test_mode():
    """Run extraction pipeline in test mode"""
    print("🧪 Running extraction pipeline in test mode")

    pipeline = RealExtractionPipeline(
        config_dir="rag_databases/registry_config",
        output_dir="rag_databases/test_output"
    )

    try:
        results = await pipeline.run_full_pipeline("shadcn")
        print("✅ Test mode completed successfully")
        print(f"📊 Results: {results['pipeline_run']['total_components']} components extracted")
    except Exception as e:
        print(f"❌ Test mode failed: {e}")
        return False

    return True

async def run_real_mode(registry=None, source=None):
    """Run extraction pipeline with real data"""
    print("🚀 Running extraction pipeline with real data")

    pipeline = RealExtractionPipeline(
        config_dir="rag_databases/registry_config",
        output_dir="rag_databases/extracted_data"
    )

    try:
        results = await pipeline.run_full_pipeline(registry, source)
        print("✅ Real extraction completed successfully")
        print(f"📊 Results: {results['pipeline_run']['total_components']} components extracted")
        print(f"⏱️  Duration: {results['pipeline_run']['duration_seconds']:.2f} seconds")
    except Exception as e:
        print(f"❌ Real extraction failed: {e}")
        return False

    return True

async def run_merge_mode(registry=None):
    """Only merge existing extracted data"""
    print("🔄 Running merge mode")

    pipeline = RealExtractionPipeline(
        config_dir="rag_databases/registry_config",
        output_dir="rag_databases/extracted_data"
    )

    try:
        if registry:
            result = await pipeline.merge_registry_components(registry)
            print(f"✅ Merged registry: {registry}")
            print(f"📊 Result: {result['total_components']} components merged")
        else:
            # Merge all registries
            output_dir = Path("rag_databases/extracted_data")
            merged_count = 0

            for extracted_file in output_dir.glob("*_extracted.json"):
                registry_name = extracted_file.stem.replace("_extracted", "")
                try:
                    result = await pipeline.merge_registry_components(registry_name)
                    merged_count += 1
                    print(f"✅ Merged registry: {registry_name} ({result['total_components']} components)")
                except Exception as e:
                    print(f"❌ Failed to merge {registry_name}: {e}")

            print(f"📊 Total merged: {merged_count} registries")

    except Exception as e:
        print(f"❌ Merge mode failed: {e}")
        return False

    return True

async def run_summary_mode():
    """Generate summary of existing data"""
    print("📊 Generating summary")

    pipeline = RealExtractionPipeline(
        config_dir="rag_databases/registry_config",
        output_dir="rag_databases/extracted_data"
    )

    try:
        summary = await pipeline.generate_registry_summary()
        print("✅ Summary generated successfully")
        print(f"📊 Total registries: {summary['total_registries']}")
        print(f"📊 Total components: {summary['total_components']}")

        if summary['components_by_category']:
            print("📊 Components by category:")
            for category, count in summary['components_by_category'].items():
                print(f"   - {category}: {count}")

    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        return False

    return True

async def run_clean_mode():
    """Clean up extracted data files"""
    print("🧹 Cleaning up extracted data files")

    output_dir = Path("rag_databases/extracted_data")
    if not output_dir.exists():
        print("ℹ️  No extracted data directory found")
        return True

    try:
        # Count files before cleanup
        files_before = len(list(output_dir.glob("*")))

        # Remove all files in the directory
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()

        print(f"✅ Cleaned up {files_before} files")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

    return True

async def run_list_mode():
    """List available registries and sources"""
    print("📋 Listing available registries and sources")

    try:
        manager = RegistryConfigManager("rag_databases/registry_config")
        registries = manager.list_registries()

        print(f"Found {len(registries)} registries:")
        for registry_name in registries:
            config = manager.load_registry_config(registry_name)
            if config:
                print(f"\n📁 {registry_name}:")
                print(f"   Name: {config['info']['name']}")
                print(f"   Platform: {config['info']['platform']}")
                print(f"   Categories: {', '.join(config['info']['categories'])}")

                for category_name, category_data in config['categories'].items():
                    print(f"   📂 {category_name}: {len(category_data['sources'])} sources")
                    for source_name, source_data in category_data['sources'].items():
                        status = "✅" if source_data.get('enabled', True) else "❌"
                        print(f"      {status} {source_name} ({source_data['type']})")

    except Exception as e:
        print(f"❌ Listing failed: {e}")
        return False

    return True

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run extraction pipeline with various modes")
    parser.add_argument("mode", choices=["test", "real", "merge", "summary", "clean", "list"],
                       help="Execution mode")
    parser.add_argument("--registry", "-r", help="Specific registry to process")
    parser.add_argument("--source", "-s", help="Specific source to process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)

    # Run selected mode
    success = False

    if args.mode == "test":
        success = await run_test_mode()
    elif args.mode == "real":
        success = await run_real_mode(args.registry, args.source)
    elif args.mode == "merge":
        success = await run_merge_mode(args.registry)
    elif args.mode == "summary":
        success = await run_summary_mode()
    elif args.mode == "clean":
        success = await run_clean_mode()
    elif args.mode == "list":
        success = await run_list_mode()

    if success:
        print("\n🎉 Mode completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Mode failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())