#!/usr/bin/env python3
"""
Test script for Documentation Extractor

Tests the documentation extractor with a sample configuration.
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.extractor_factory import create_extractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_documentation_extractor():
    """Test the documentation extractor"""
    logger.info("Testing Documentation Extractor")

    # Load test configuration
    config_path = Path(__file__).parent.parent / "configs" / "documentation_config.json"
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    logger.info(f"Loaded configuration for: {config['name']}")

    # Create extractor
    extractor = create_extractor("documentation", config)
    if not extractor:
        logger.error("Failed to create documentation extractor")
        return False

    logger.info("Documentation extractor created successfully")

    # Test source validation
    if not extractor.validate_source():
        logger.error("Source validation failed")
        return False

    logger.info("Source validation passed")

    # Test extraction
    async with extractor:
        logger.info("Starting extraction...")
        result = await extractor.extract_with_validation()

    # Log results
    logger.info(f"Extraction completed:")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Components extracted: {len(result.data)}")
    logger.info(f"  Errors: {len(result.errors)}")
    logger.info(f"  Warnings: {len(result.warnings)}")
    logger.info(f"  Time: {result.extraction_time:.2f}s")

    if result.errors:
        logger.error("Errors encountered:")
        for error in result.errors:
            logger.error(f"  - {error}")

    if result.warnings:
        logger.warning("Warnings encountered:")
        for warning in result.warnings:
            logger.warning(f"  - {warning}")

    if result.data:
        logger.info("Sample extracted components:")
        for i, component in enumerate(result.data[:3]):  # Show first 3
            logger.info(f"  {i+1}. {component.get('name', 'Unknown')}")
            logger.info(f"     Type: {component.get('type', 'Unknown')}")
            logger.info(f"     Description: {component.get('description', 'No description')[:100]}...")
            if component.get('usage_examples'):
                logger.info(f"     Code examples: {len(component['usage_examples'])}")

    # Save results to file for inspection
    output_path = Path(__file__).parent.parent / "test_output" / "documentation_extraction_result.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            "success": result.success,
            "data": result.data,
            "errors": result.errors,
            "warnings": result.warnings,
            "metadata": result.metadata,
            "extraction_time": result.extraction_time
        }, f, indent=2, default=str)

    logger.info(f"Results saved to: {output_path}")

    return result.success

async def main():
    """Main test function"""
    try:
        success = await test_documentation_extractor()
        if success:
            logger.info("✅ Documentation extractor test PASSED")
            return 0
        else:
            logger.error("❌ Documentation extractor test FAILED")
            return 1

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))