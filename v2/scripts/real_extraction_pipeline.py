#!/usr/bin/env python3
"""
Real Data Extraction Pipeline for SimFlo RAG

This script implements a production-ready pipeline for extracting real data
from shadcn/ui repositories and other sources, then building comprehensive
registries with specialized extractors.

Usage:
    python3 scripts/real_extraction_pipeline.py [--registry REGISTRY] [--source SOURCE] [--output OUTPUT]

    --registry: Registry configuration to process (default: all)
    --source: Specific source to process (default: all)
    --output: Output directory for extracted data (default: rag_databases/extracted_data)
"""

import asyncio
import argparse
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors import ExtractorFactory, get_extractor_factory
from services.multi_source_merger import MultiSourceMerger
from models import Component, ComponentCategory, ComponentType
from services.registry_config_manager import RegistryConfigManager
from utils.logger import setup_logging

class RealExtractionPipeline:
    """Production-ready data extraction pipeline"""

    def __init__(self, config_dir: str = "rag_databases/registry_config", output_dir: str = "rag_databases/extracted_data"):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.registry_manager = RegistryConfigManager(config_dir)
        self.extractor_factory = get_extractor_factory()
        self.merger = MultiSourceMerger()

        # Setup logging
        setup_logging(level="INFO")
        self.logger = logging.getLogger(__name__)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process_registry(self, registry_name: str, specific_source: Optional[str] = None) -> Dict[str, Any]:
        """Process a single registry configuration"""
        self.logger.info(f"Processing registry: {registry_name}")

        # Load registry configuration
        registry_config = self.registry_manager.get_registry_config(registry_name)
        if not registry_config:
            raise ValueError(f"Registry configuration not found: {registry_name}")

        results = {
            "registry_name": registry_name,
            "registry_info": {
                "name": registry_config.display_name,
                "description": registry_config.description,
                "platforms": registry_config.platforms,
                "status": registry_config.status.value
            },
            "extraction_timestamp": datetime.now().isoformat(),
            "sources_processed": [],
            "categories_extracted": {},
            "total_components": 0,
            "components_by_category": {},
            "errors": [],
            "warnings": []
        }

        # Process each category in the registry
        for category_name, category_config in registry_config.categories.items():
            self.logger.info(f"Processing category: {category_name}")

            category_results = {
                "category": category_name,
                "sources_count": len(category_config.sources),
                "components_extracted": 0,
                "sources": []
            }

            # Process each source in the category
            for source_config in category_config.sources:
                source_name = source_config.name
                if specific_source and source_name != specific_source:
                    continue

                try:
                    source_result = await self._process_source(source_name, source_config, category_name)
                    category_results["sources"].append(source_result)
                    category_results["components_extracted"] += len(source_result["components"])

                    # Add components to overall results
                    if category_name not in results["components_by_category"]:
                        results["components_by_category"][category_name] = []

                    results["components_by_category"][category_name].extend(source_result["components"])

                except Exception as e:
                    error_msg = f"Failed to process source {source_name}: {str(e)}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    category_results["sources"].append({
                        "source_name": source_name,
                        "error": error_msg,
                        "components": []
                    })

            results["categories_extracted"][category_name] = category_results
            results["total_components"] += category_results["components_extracted"]

        # Save registry results
        await self._save_registry_results(registry_name, results)

        return results

    async def _process_source(self, source_name: str, source_config: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Process a single source configuration"""
        self.logger.info(f"Processing source: {source_name}")

        result = {
            "source_name": source_name,
            "source_type": source_config["type"],
            "category": category,
            "extraction_time": datetime.now().isoformat(),
            "components": [],
            "errors": [],
            "warnings": [],
            "metadata": {
                "url": source_config.get("url", ""),
                "branch": source_config.get("branch", ""),
                "package": source_config.get("package", ""),
                "registry_file": source_config.get("registry_file", "")
            }
        }

        try:
            # Auto-select and create extractor
            extractor = self.extractor_factory.create_auto_extractor(source_config)
            if not extractor:
                raise ValueError(f"No compatible extractor found for source: {source_name}")

            self.logger.info(f"Using extractor: {extractor.__class__.__name__}")

            # Extract components
            extraction_result = await extractor.extract()

            # Process extraction results
            if extraction_result.success:
                result["components"] = [component.to_dict() for component in extraction_result.components]
                result["warnings"] = extraction_result.warnings

                # Add source metadata to each component
                for component_data in result["components"]:
                    component_data["source_metadata"] = {
                        "source_name": source_name,
                        "extraction_timestamp": extraction_result.extraction_time,
                        "extractor_type": extractor.__class__.__name__
                    }

                self.logger.info(f"Extracted {len(result['components'])} components from {source_name}")
            else:
                result["errors"].extend(extraction_result.errors)
                self.logger.warning(f"Extraction from {source_name} had issues: {extraction_result.errors}")

        except Exception as e:
            error_msg = f"Error processing source {source_name}: {str(e)}"
            result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return result

    async def _save_registry_results(self, registry_name: str, results: Dict[str, Any]) -> None:
        """Save registry extraction results to file"""
        output_file = self.output_dir / f"{registry_name}_extracted.json"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved registry results to: {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save registry results: {e}")
            # Create a backup in temp directory
            backup_dir = Path("/tmp") / "simflo_extraction"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"{registry_name}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved backup to: {backup_file}")

    async def merge_registry_components(self, registry_name: str) -> Dict[str, Any]:
        """Merge components from all sources in a registry"""
        self.logger.info(f"Merging components for registry: {registry_name}")

        # Load extracted data
        extracted_file = self.output_dir / f"{registry_name}_extracted.json"
        if not extracted_file.exists():
            raise ValueError(f"No extracted data found for registry: {registry_name}")

        with open(extracted_file, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)

        merged_results = {
            "registry_name": registry_name,
            "merge_timestamp": datetime.now().isoformat(),
            "categories": {},
            "total_components": 0,
            "merge_stats": {
                "total_original": 0,
                "total_merged": 0,
                "conflicts_resolved": 0,
                "duplicates_removed": 0
            }
        }

        # Process each category
        for category_name, category_data in extracted_data["components_by_category"].items():
            self.logger.info(f"Merging category: {category_name}")

            # Convert dict components back to Component objects
            components = []
            for component_dict in category_data:
                component = Component.from_dict(component_dict)
                components.append(component)

            # Merge components
            merged_components = self.merger.merge_components(components, strategy="priority_based")

            # Convert back to dict for storage
            merged_components_dict = [comp.to_dict() for comp in merged_components]

            merged_results["categories"][category_name] = {
                "components": merged_components_dict,
                "count": len(merged_components_dict),
                "original_count": len(components)
            }

            merged_results["total_components"] += len(merged_components_dict)
            merged_results["merge_stats"]["total_original"] += len(components)
            merged_results["merge_stats"]["total_merged"] += len(merged_components_dict)

        # Save merged results
        merged_file = self.output_dir / f"{registry_name}_merged.json"
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(merged_results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved merged results to: {merged_file}")

        return merged_results

    async def generate_registry_summary(self) -> Dict[str, Any]:
        """Generate a summary of all processed registries"""
        self.logger.info("Generating registry summary")

        summary = {
            "summary_timestamp": datetime.now().isoformat(),
            "registries": {},
            "total_registries": 0,
            "total_components": 0,
            "components_by_type": {},
            "components_by_category": {},
            "extraction_stats": {
                "successful_extractions": 0,
                "failed_extractions": 0,
                "total_sources": 0
            }
        }

        # Process all registry files
        for extracted_file in self.output_dir.glob("*_extracted.json"):
            registry_name = extracted_file.stem.replace("_extracted", "")

            try:
                with open(extracted_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)

                summary["registries"][registry_name] = {
                    "info": registry_data["registry_info"],
                    "extraction_timestamp": registry_data["extraction_timestamp"],
                    "total_components": registry_data["total_components"],
                    "categories": list(registry_data["categories_extracted"].keys()),
                    "errors_count": len(registry_data["errors"])
                }

                summary["total_registries"] += 1
                summary["total_components"] += registry_data["total_components"]

                # Aggregate by category
                for category_name, category_data in registry_data["categories_extracted"].items():
                    if category_name not in summary["components_by_category"]:
                        summary["components_by_category"][category_name] = 0
                    summary["components_by_category"][category_name] += category_data["components_extracted"]

            except Exception as e:
                self.logger.error(f"Error processing registry file {extracted_file}: {e}")

        # Save summary
        summary_file = self.output_dir / "extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved extraction summary to: {summary_file}")

        return summary

    async def run_full_pipeline(self, registry_name: Optional[str] = None, source_name: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete extraction pipeline"""
        self.logger.info("Starting full extraction pipeline")

        start_time = datetime.now()

        # Determine which registries to process
        if registry_name:
            registries = [registry_name]
        else:
            # Get all available registry configurations
            registries = []
            for config_file in self.config_dir.glob("*.json"):
                registries.append(config_file.stem)

        self.logger.info(f"Processing registries: {registries}")

        # Process each registry
        all_results = {}
        for reg_name in registries:
            try:
                registry_result = await self.process_registry(reg_name, source_name)
                all_results[reg_name] = registry_result

                # Merge components
                await self.merge_registry_components(reg_name)

            except Exception as e:
                self.logger.error(f"Failed to process registry {reg_name}: {e}")
                all_results[reg_name] = {"error": str(e)}

        # Generate summary
        summary = await self.generate_registry_summary()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info(f"Pipeline completed in {duration:.2f} seconds")
        self.logger.info(f"Processed {len(registries)} registries")
        self.logger.info(f"Total components extracted: {summary['total_components']}")

        return {
            "pipeline_run": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "registries_processed": len(registries),
                "total_components": summary["total_components"]
            },
            "results": all_results,
            "summary": summary
        }

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Real Data Extraction Pipeline for SimFlo RAG")
    parser.add_argument("--registry", "-r", help="Registry configuration to process (default: all)")
    parser.add_argument("--source", "-s", help="Specific source to process (default: all)")
    parser.add_argument("--output", "-o", default="rag_databases/extracted_data", help="Output directory")
    parser.add_argument("--config", "-c", default="rag_databases/registry_config", help="Configuration directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)

    # Create and run pipeline
    pipeline = RealExtractionPipeline(args.config, args.output)

    try:
        results = await pipeline.run_full_pipeline(args.registry, args.source)

        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION PIPELINE COMPLETE")
        print("="*60)
        print(f"Duration: {results['pipeline_run']['duration_seconds']:.2f} seconds")
        print(f"Registries processed: {results['pipeline_run']['registries_processed']}")
        print(f"Total components: {results['pipeline_run']['total_components']}")
        print(f"Output directory: {args.output}")
        print("="*60)

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())