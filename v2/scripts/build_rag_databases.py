#!/usr/bin/env python3
"""
Build RAG Databases using Specialized Extractors

This script uses the new specialized extractor system to populate
the RAG databases with real component data from multiple sources.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from services.registry_config_manager import RegistryConfigManager
from extractors.extractor_factory import ExtractorFactory
from services.multi_source_merger import MultiSourceMerger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGDatabaseBuilder:
    """Builds RAG databases using specialized extractors"""

    def __init__(self):
        self.config_manager = RegistryConfigManager()
        self.extractor_factory = ExtractorFactory()
        self.merger = MultiSourceMerger()
        self.output_dir = Path("rag_databases")

    async def build_registry_database(self, registry_name: str) -> bool:
        """Build RAG database for a specific registry"""
        try:
            logger.info(f"🔧 Building database for registry: {registry_name}")

            # Get registry configuration
            config = self.config_manager.get_registry_config(registry_name)
            if not config:
                logger.error(f"❌ Registry config not found: {registry_name}")
                return False

            # Get all categories and sources
            categories = config.categories
            all_components = []

            for category_name, category_config in categories.items():
                if not category_config.enabled:
                    continue

                logger.info(f"📁 Processing category: {category_name}")
                sources = category_config.sources

                category_components = await self.extract_from_sources(sources, category_name)
                all_components.extend(category_components)

            # Merge components from all sources
            if all_components:
                merged_components = self.merger.merge_sources(all_components, [])

                # Apply quality scoring
                scored_components = self.merger.calculate_quality_scores(merged_components)

                # Save to database
                await self.save_to_database(registry_name, scored_components)

                logger.info(f"✅ Successfully built {registry_name} database with {len(scored_components)} components")
                return True
            else:
                logger.warning(f"⚠️ No components found for registry: {registry_name}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to build {registry_name} database: {e}")
            return False

    async def extract_from_sources(self, sources: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Extract components from multiple sources"""
        all_components = []

        for source_config in sources:
            try:
                logger.info(f"🔍 Extracting from source: {source_config.name}")

                # Create extractor
                extractor_type = source_config.extractor
                if not extractor_type:
                    logger.warning(f"⚠️ No extractor specified for source: {source_config.name}")
                    continue

                # Convert SourceConfig to dict if needed
                if hasattr(source_config, '__dict__'):
                    source_dict = {
                        "name": source_config.name,
                        "type": source_config.type.value,
                        "url": source_config.url,
                        "branch": source_config.branch,
                        "registry_file": source_config.registry_file,
                        "package": source_config.package,
                        "extractor": extractor_type
                    }
                else:
                    source_dict = dict(source_config)
                    source_dict["extractor"] = extractor_type

                extractor = self.extractor_factory.create_extractor(extractor_type, source_dict)
                if not extractor:
                    logger.warning(f"⚠️ Failed to create extractor: {extractor_type}")
                    continue

                # Extract components
                async with extractor:
                    result = await extractor.extract()

                    if result.success:
                        components = result.data  # Already dictionaries
                        all_components.extend(components)
                        logger.info(f"✅ Extracted {len(components)} components from {source_config.name}")
                    else:
                        logger.error(f"❌ Extraction failed for {source_config.name}: {result.errors}")

            except Exception as e:
                logger.error(f"❌ Error extracting from source {source_config.name}: {e}")
                continue

        return all_components

    def component_to_dict(self, component) -> Dict[str, Any]:
        """Convert Component object to dictionary"""
        if hasattr(component, '__dict__'):
            # Component object
            comp_dict = {}
            for key, value in vars(component).items():
                if not key.startswith('_'):
                    comp_dict[key] = value
            return comp_dict
        else:
            # Already a dictionary
            return component

    async def save_to_database(self, registry_name: str, components: List[Dict[str, Any]]):
        """Save components to RAG database"""
        registry_dir = self.output_dir / f"{registry_name}_db"
        registry_dir.mkdir(exist_ok=True)

        output_file = registry_dir / "components.json"

        # Save components
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(components, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved {len(components)} components to {output_file}")

        # TODO: Create vector embeddings and ChromaDB
        # This would integrate with the existing vector_store.py

    async def build_all_databases(self) -> Dict[str, bool]:
        """Build databases for all configured registries"""
        results = {}

        # Get all available registry configs
        registries = ["shadcn", "gluestack"]  # Add more as needed

        for registry_name in registries:
            success = await self.build_registry_database(registry_name)
            results[registry_name] = success

        return results

async def main():
    """Main execution function"""
    builder = RAGDatabaseBuilder()

    print("🚀 Building RAG Databases with Specialized Extractors")
    print("=" * 60)

    # Build all databases
    results = await builder.build_all_databases()

    print("\n📊 Results:")
    print("=" * 60)
    for registry, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{registry}: {status}")

    # Summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)

    print(f"\n🎯 Summary: {successful}/{total} databases built successfully")

    if successful == total:
        print("🎉 All RAG databases built successfully!")
        return 0
    else:
        print("⚠️ Some databases failed to build")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)