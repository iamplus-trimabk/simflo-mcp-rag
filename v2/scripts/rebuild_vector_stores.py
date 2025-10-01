#!/usr/bin/env python3
"""
Rebuild Vector Stores for Multi-Registry System

This script rebuilds the ChromaDB vector stores for each registry
using the new component data format from the specialized extractors.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the data-pipeline directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data-pipeline'))

from registry_manager import get_registry_manager
from vector_store import VectorStore
from parse_registry import ShadcnComponent, RegistryFile
import chromadb
from chromadb.config import Settings
import chromadb.errors

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_components_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load components from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Handle different formats
            if isinstance(data, list):
                return data  # New format - direct list of components
            elif isinstance(data, dict):
                if "components" in data:
                    return data["components"]  # Old format - components in dict
                elif "repository" in data and "extraction_metadata" in data:
                    return []  # Radix format - no actual components extracted
                else:
                    return [data]  # Single component in dict format
            else:
                logger.error(f"Unknown data format in {file_path}")
                return []
    except Exception as e:
        logger.error(f"Failed to load components from {file_path}: {e}")
        return []


def convert_to_shadcn_component(component_data: Dict[str, Any]) -> ShadcnComponent:
    """Convert new component format to ShadcnComponent format"""
    # Convert files data
    files_data = component_data.get("metadata", {}).get("files", [])
    files = []
    for file_data in files_data:
        if isinstance(file_data, dict):
            files.append(RegistryFile(
                path=file_data.get("path", ""),
                content=file_data.get("content", ""),
                type=file_data.get("type", "source")
            ))
        elif isinstance(file_data, str):
            files.append(RegistryFile(path=file_data, content="", type="source"))

    # Determine component type
    component_type = "ui"
    if component_data.get("type") == "component":
        if "hook" in component_data.get("name", "").lower():
            component_type = "hook"
        elif any(block_keyword in component_data.get("name", "").lower()
                for block_keyword in ["block", "dashboard", "card", "section", "layout"]):
            component_type = "block"
        else:
            component_type = "ui"
    elif component_data.get("type") in ["ui", "block", "hook"]:
        component_type = component_data.get("type")

    component = ShadcnComponent(
        name=component_data.get("name", ""),
        type=component_type,
        description=component_data.get("description", ""),
        dependencies=component_data.get("dependencies", []),
        registryDependencies=component_data.get("peer_dependencies", []),
        categories=[component_data.get("category", "components")],
        installCommand=component_data.get("installation", ""),
        files=files
    )

    # Add additional metadata for search
    component.registry = component_data.get("priority_source", "unknown")
    component.platform = component_data.get("platform", ["reactjs", "reactnative"])
    component.metadata = component_data.get("metadata", {})

    return component


def rebuild_registry_vector_store(registry_name: str, registry_path: Path) -> bool:
    """Rebuild vector store for a specific registry"""
    try:
        logger.info(f"Rebuilding vector store for {registry_name}...")

        # Load components data
        components_file = registry_path / "components.json"
        if not components_file.exists():
            logger.error(f"Components file not found: {components_file}")
            return False

        components_data = load_components_from_file(components_file)
        logger.info(f"Loaded {len(components_data)} components from {components_file}")

        # Initialize ChromaDB for this registry
        chroma_path = registry_path / "chroma_db"
        chroma_path.mkdir(exist_ok=True)

        client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Collection name should match what registry manager expects
        collection_name = f"components_{registry_name.replace('_db', '')}"

        # Delete existing collection if it exists
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")
        except (ValueError, chromadb.errors.NotFoundError):
            # Collection doesn't exist, that's fine
            pass

        # Create new collection
        try:
            collection = client.create_collection(name=collection_name)
            logger.info(f"Created new collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

        # Convert and add components to vector store
        for i, component_data in enumerate(components_data):
            try:
                component = convert_to_shadcn_component(component_data)

                # Create searchable text
                search_text = f"{component.name} {component.description} {' '.join(component.categories)}"
                if component.dependencies:
                    search_text += " " + " ".join(component.dependencies)
                if component.registry:
                    search_text += f" {component.registry}"

                # Add to collection
                collection.add(
                    documents=[search_text],
                    metadatas=[{
                        "name": component.name,
                        "type": component.type,
                        "description": component.description or "",
                        "registry": component.registry or "unknown",
                        "install_command": component.installCommand,
                        "categories": ",".join(component.categories),
                        "platform": ",".join(component.platform) if isinstance(component.platform, list) else component.platform
                    }],
                    ids=[f"{component.name}_{i}"]
                )

            except Exception as e:
                logger.error(f"Failed to process component {component_data.get('name', 'unknown')}: {e}")
                continue

        logger.info(f"Successfully rebuilt vector store for {registry_name} with {collection.count()} components")
        return True

    except Exception as e:
        logger.error(f"Failed to rebuild vector store for {registry_name}: {e}")
        return False


def main():
    """Main function to rebuild all vector stores"""
    logger.info("Starting vector store rebuild process...")

    # Base path for RAG databases
    rag_databases_path = Path("./rag_databases")

    if not rag_databases_path.exists():
        logger.error(f"RAG databases path not found: {rag_databases_path}")
        return 1

    # Find all registry directories
    registries = []
    for registry_dir in rag_databases_path.iterdir():
        if registry_dir.is_dir() and registry_dir.name.endswith("_db"):
            registries.append((registry_dir.name, registry_dir))

    logger.info(f"Found {len(registries)} registries to rebuild")

    # Rebuild each registry
    success_count = 0
    for registry_name, registry_path in registries:
        if rebuild_registry_vector_store(registry_name, registry_path):
            success_count += 1
        else:
            logger.error(f"Failed to rebuild {registry_name}")

    logger.info(f"Vector store rebuild completed: {success_count}/{len(registries)} successful")

    # Test registry manager
    logger.info("Testing registry manager...")
    try:
        registry_manager = get_registry_manager()
        available_registries = registry_manager.get_available_registries()
        logger.info(f"Registry manager found {len(available_registries)} available registries")

        for registry in available_registries:
            logger.info(f"  - {registry.name}: {registry.component_count} components")
    except Exception as e:
        logger.error(f"Failed to test registry manager: {e}")

    return 0 if success_count == len(registries) else 1


if __name__ == "__main__":
    exit(main())