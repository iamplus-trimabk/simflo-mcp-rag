#!/usr/bin/env python3
"""
End-to-End Documentation Pipeline Test

Tests the complete documentation ingestion pipeline:
1. Create documentation registry
2. Extract documentation using extractor
3. Store in vector database
4. Search and retrieve documentation
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
import sys
sys.path.append('data-pipeline')
sys.path.append('.')

from extractors.extractor_factory import create_extractor
from registry_manager import get_registry_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_documentation_pipeline():
    """Test the complete documentation pipeline"""
    logger.info("🚀 Starting End-to-End Documentation Pipeline Test")

    # Step 1: Initialize registry manager
    registry_manager = get_registry_manager()
    logger.info("✅ Registry manager initialized")

    # Step 2: Test configuration
    config_path = Path(__file__).parent.parent / "configs" / "documentation_config.json"
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Step 3: Create documentation registry
    registry_name = "test_docs"
    registry_config = {
        "name": "Test Documentation",
        "base_url": config["base_url"],
        "created_at": "2025-09-29T01:43:00Z",
        "pages_extracted": 0,
        "status": "created"
    }

    logger.info(f"Creating documentation registry: {registry_name}")
    success = registry_manager.create_documentation_registry(registry_name, registry_config)
    if not success:
        logger.error("❌ Failed to create documentation registry")
        return False
    logger.info("✅ Documentation registry created")

    # Step 4: Test extractor
    logger.info("Testing documentation extractor...")
    extractor = create_extractor("documentation", config)
    if not extractor:
        logger.error("❌ Failed to create documentation extractor")
        return False

    # Test source validation
    if not extractor.validate_source():
        logger.error("❌ Source validation failed")
        return False

    logger.info("✅ Documentation extractor created and validated")

    # Step 5: Extract documentation (mock data for testing)
    logger.info("Extracting documentation...")
    mock_pages = [
        {
            "name": "react_overview",
            "category": "documentation",
            "type": "guide",
            "description": "Overview of React library and its features",
            "installation": "# View documentation at: https://react.dev",
            "usage_examples": [
                "import React from 'react';\nfunction App() {\n  return <h1>Hello World</h1>;\n}"
            ],
            "dependencies": [],
            "peer_dependencies": [],
            "metadata": {
                "url": "https://react.dev",
                "page_type": "guide",
                "content_length": 1500,
                "code_examples_count": 1,
                "source_site": "react_docs_test"
            },
            "platform": ["web"],
            "registry": "documentation",
            "sources": ["test_docs"],
            "priority_source": "test_docs"
        },
        {
            "name": "react_hooks",
            "category": "documentation",
            "type": "reference",
            "description": "React hooks documentation and examples",
            "installation": "# View documentation at: https://react.dev/reference/react",
            "usage_examples": [
                "import { useState, useEffect } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  return <button onClick={() => setCount(count + 1)}>{count}</button>;\n}"
            ],
            "dependencies": [],
            "peer_dependencies": [],
            "metadata": {
                "url": "https://react.dev/reference/react",
                "page_type": "reference",
                "content_length": 2500,
                "code_examples_count": 1,
                "source_site": "react_docs_test"
            },
            "platform": ["web"],
            "registry": "documentation",
            "sources": ["test_docs"],
            "priority_source": "test_docs"
        }
    ]

    logger.info(f"✅ Extracted {len(mock_pages)} documentation pages (mock data)")

    # Step 6: Add to vector database
    logger.info("Adding documentation pages to vector database...")
    success = registry_manager.add_documentation_pages(registry_name, mock_pages)
    if not success:
        logger.error("❌ Failed to add documentation pages to vector database")
        return False
    logger.info("✅ Documentation pages added to vector database")

    # Step 7: Test search
    logger.info("Testing documentation search...")
    search_results = registry_manager.search_documentation("react hooks", limit=5)
    logger.info(f"✅ Found {len(search_results)} search results")

    if search_results:
        logger.info("Sample search results:")
        for i, result in enumerate(search_results[:2]):
            logger.info(f"  {i+1}. {result.component.get('name', 'Unknown')}")
            logger.info(f"     Score: {result.relevance_score:.2f}")
            logger.info(f"     Registry: {result.registry}")
            logger.info(f"     Type: {result.component.get('type', 'Unknown')}")

    # Step 8: Test statistics
    logger.info("Getting documentation statistics...")
    stats = registry_manager.get_documentation_stats()
    logger.info(f"✅ Documentation statistics:")
    logger.info(f"  Total registries: {stats['total_registries']}")
    logger.info(f"  Total pages: {stats['total_pages']}")
    for reg_name, reg_stats in stats['registries'].items():
        logger.info(f"  {reg_name}: {reg_stats['actual_pages']} pages")

    # Step 9: Test overall registry stats
    logger.info("Getting overall registry statistics...")
    all_stats = registry_manager.get_registry_stats()
    logger.info(f"✅ Overall system statistics:")
    logger.info(f"  Total registries: {all_stats['total_registries']}")
    logger.info(f"  Total components: {all_stats['total_components']}")

    # Save test results
    test_results = {
        "test_name": "end_to_end_documentation_pipeline",
        "success": True,
        "steps_completed": [
            "Registry manager initialized",
            "Documentation registry created",
            "Documentation extractor created and validated",
            "Documentation pages extracted (mock data)",
            "Documentation pages added to vector database",
            "Documentation search tested",
            "Documentation statistics retrieved",
            "Overall system statistics retrieved"
        ],
        "search_results_count": len(search_results),
        "documentation_stats": stats,
        "overall_stats": all_stats,
        "timestamp": "2025-09-29T01:43:00Z"
    }

    output_path = Path(__file__).parent.parent / "test_output" / "documentation_pipeline_test.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)

    logger.info(f"✅ Test results saved to: {output_path}")
    logger.info("🎉 End-to-End Documentation Pipeline Test PASSED")

    return True

async def main():
    """Main test function"""
    try:
        success = await test_documentation_pipeline()
        if success:
            logger.info("✅ All tests PASSED")
            return 0
        else:
            logger.error("❌ Tests FAILED")
            return 1

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))