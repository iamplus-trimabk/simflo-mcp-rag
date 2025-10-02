#!/usr/bin/env python3
"""
Centralized Database Manager for SimFlo RAG

Single source of truth for all ChromaDB operations across the entire system.
Provides unified database creation, management, and cleanup for all registries.

This replaces the multiple independent database creation flows that were
causing massive database duplication (86+ files across 6 databases).
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json
import shutil
from datetime import datetime
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Centralized manager for all ChromaDB operations.

    Provides a single, consistent interface for:
    - Creating databases
    - Rebuilding databases
    - Cleaning up duplicates
    - Managing database lifecycle
    """

    def __init__(self, registries_base_path: str = None):
        """Initialize DatabaseManager with base registry path"""
        if registries_base_path is None:
            # Default to the standard registries directory
            registries_base_path = str(Path(__file__).parent.parent.parent / "00-rag-registry" / "registries")

        self.registries_base_path = Path(registries_base_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Standardized database path: {registry}/chroma_db/
        self.db_path_suffix = "chroma_db"

    def get_registry_db_path(self, registry_name: str) -> Path:
        """Get the standardized database path for a registry"""
        return self.registries_base_path / registry_name / self.db_path_suffix

    def get_registry_files_path(self, registry_name: str) -> Path:
        """Get the source files path for a registry"""
        return self.registries_base_path / registry_name / "files"

    def registry_exists(self, registry_name: str) -> bool:
        """Check if a registry directory exists"""
        registry_dir = self.registries_base_path / registry_name
        return registry_dir.exists() and registry_dir.is_dir()

    def database_exists(self, registry_name: str) -> bool:
        """Check if database exists for a registry"""
        db_path = self.get_registry_db_path(registry_name)
        return db_path.exists() and db_path.is_dir()

    def cleanup_duplicate_databases(self, registry_name: str) -> Dict[str, Any]:
        """
        Clean up all duplicate database directories for a registry.
        Removes old database locations and keeps only the standardized one.

        Old locations to remove:
        - {registry}/db/
        - {registry}/db/chroma_db/

        Standard location to keep:
        - {registry}/chroma_db/
        """
        try:
            registry_dir = self.registries_base_path / registry_name
            if not registry_dir.exists():
                return {"success": False, "error": f"Registry {registry_name} does not exist"}

            removed_paths = []
            removed_files = []

            # Remove old {registry}/db/ directory (but preserve {registry}/files/)
            old_db_dir = registry_dir / "db"
            if old_db_dir.exists():
                # Only remove database-related files, preserve source files
                for item in old_db_dir.iterdir():
                    if item.is_file() and item.suffix in ['.sqlite3', '.marker', '.json']:
                        item.unlink()
                        removed_files.append(str(item))
                    elif item.is_dir() and item.name == 'chroma_db':
                        # Remove nested chroma_db directory
                        shutil.rmtree(item)
                        removed_paths.append(str(item))
                    elif item.is_dir() and item.name.replace('-', '').replace('_', '').isalnum():
                        # Remove UUID directories (ChromaDB collections)
                        shutil.rmtree(item)
                        removed_paths.append(str(item))

                # If db_dir is now empty or only contains non-database files, remove it
                remaining_items = list(old_db_dir.iterdir())
                if not remaining_items or all(item.is_file() and item.suffix not in ['.sqlite3', '.marker', '.json'] for item in remaining_items):
                    if not remaining_items:
                        shutil.rmtree(old_db_dir)
                        removed_paths.append(str(old_db_dir))

            # Remove any other chroma_db directories in wrong locations
            for chroma_candidate in registry_dir.rglob("chroma_db"):
                if chroma_candidate != self.get_registry_db_path(registry_name):
                    shutil.rmtree(chroma_candidate)
                    removed_paths.append(str(chroma_candidate))

            self.logger.info(f"Cleaned up {len(removed_files)} files and {len(removed_paths)} directories for {registry_name}")

            return {
                "success": True,
                "registry": registry_name,
                "removed_files": removed_files,
                "removed_directories": removed_paths,
                "message": f"Removed {len(removed_files)} files and {len(removed_paths)} directories"
            }

        except Exception as e:
            self.logger.error(f"Failed to cleanup duplicate databases for {registry_name}: {e}")
            return {"success": False, "error": str(e)}

    def create_database(self, registry_name: str, source_files: List[Path], collection_name: str = "components") -> Dict[str, Any]:
        """
        Create a simple ChromaDB database for a registry from source files.
        No UUID complexity - just clean, straightforward database structure.
        """
        try:
            if not self.registry_exists(registry_name):
                return {"success": False, "error": f"Registry {registry_name} does not exist"}

            if not source_files:
                return {"success": False, "error": f"No source files provided for {registry_name}"}

            # Create standardized database directory
            db_path = self.get_registry_db_path(registry_name)
            db_path.mkdir(parents=True, exist_ok=True)

            # Remove any existing database at this location
            if db_path.exists():
                for item in db_path.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # Create ChromaDB client
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Create collection - ChromaDB handles the internal structure
            collection = client.create_collection(name=collection_name)

            # Process source files and add to database
            documents = []
            metadatas = []
            ids = []

            for source_file in source_files:
                try:
                    relative_path = source_file.relative_to(self.get_registry_files_path(registry_name))

                    with open(source_file, 'r', encoding='utf-8') as f:
                        if source_file.suffix == '.json':
                            # Parse JSON file and extract meaningful content
                            try:
                                json_data = json.load(f)
                                if isinstance(json_data, list):
                                    # Handle large lists efficiently
                                    self.logger.info(f"Processing large JSON file with {len(json_data)} items: {source_file.name}")

                                    # If list is too large (>1000 items), sample important items
                                    if len(json_data) > 1000:
                                        # Sample first 500 items and prioritize items with descriptions
                                        sampled_items = []

                                        # First, add items with descriptions (higher quality)
                                        for item in json_data:
                                            if len(sampled_items) >= 500:
                                                break
                                            if isinstance(item, dict) and item.get('description') and item['description'].strip():
                                                sampled_items.append(item)

                                        # If still need more items, add from the beginning
                                        for item in json_data:
                                            if len(sampled_items) >= 1000:
                                                break
                                            if item not in sampled_items:
                                                sampled_items.append(item)

                                        content = json.dumps(sampled_items, indent=2)
                                        self.logger.info(f"Sampled {len(sampled_items)} items from {len(json_data)} total items")
                                    else:
                                        content = json.dumps(json_data, indent=2)
                                elif isinstance(json_data, dict):
                                    # Convert JSON to readable text for search
                                    content = json.dumps(json_data, indent=2)
                                else:
                                    content = str(json_data)
                            except json.JSONDecodeError:
                                # If JSON parsing fails, read as raw text
                                f.seek(0)  # Reset file pointer
                                content = f.read()
                        else:
                            # Read text files normally
                            content = f.read()

                    # Simple, clean metadata
                    metadata = {
                        "name": source_file.stem,
                        "registry": registry_name,
                        "source_file": str(relative_path),
                        "file_type": source_file.suffix[1:] if source_file.suffix else "unknown",
                        "type": "component",
                        "timestamp": datetime.now().isoformat()
                    }

                    documents.append(content)
                    metadatas.append(metadata)
                    # Use simple IDs - component names are unique enough within a registry
                    ids.append(f"{registry_name}_{source_file.stem}")

                except Exception as e:
                    self.logger.warning(f"Failed to process {source_file}: {e}")
                    continue

            if not documents:
                return {"success": False, "error": f"No valid documents processed for {registry_name}"}

            # Add all documents at once - simple and clean
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            # Create simple marker file
            marker_file = db_path / f"{registry_name}_db.marker"
            with open(marker_file, 'w') as f:
                f.write(f"Registry: {registry_name}\n")
                f.write(f"Documents: {len(documents)}\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")

            self.logger.info(f"Created simple database for {registry_name} with {len(documents)} documents")

            return {
                "success": True,
                "registry": registry_name,
                "database_path": str(db_path),
                "collection_name": collection_name,
                "documents_processed": len(documents),
                "message": f"Successfully created simple database with {len(documents)} documents"
            }

        except Exception as e:
            self.logger.error(f"Failed to create database for {registry_name}: {e}")
            return {"success": False, "error": str(e)}

    def get_database_client(self, registry_name: str, collection_name: str = "components") -> Optional[chromadb.Collection]:
        """
        Get ChromaDB client for a registry.
        Creates database if it doesn't exist.
        """
        try:
            if not self.database_exists(registry_name):
                # Database doesn't exist, try to create it from source files
                files_path = self.get_registry_files_path(registry_name)
                if files_path.exists():
                    source_files = list(files_path.rglob("*.md")) + list(files_path.rglob("*.json"))
                    if source_files:
                        create_result = self.create_database(registry_name, source_files, collection_name)
                        if not create_result["success"]:
                            self.logger.error(f"Failed to create database for {registry_name}: {create_result['error']}")
                            return None
                    else:
                        self.logger.error(f"No source files found for {registry_name}")
                        return None
                else:
                    self.logger.error(f"Registry files directory not found: {files_path}")
                    return None

            # Get database client
            db_path = self.get_registry_db_path(registry_name)
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            try:
                collection = client.get_collection(name=collection_name)
            except (ValueError, chromadb.errors.NotFoundError):
                collection = client.create_collection(name=collection_name)

            return collection

        except Exception as e:
            self.logger.error(f"Failed to get database client for {registry_name}: {e}")
            return None

    def rebuild_database(self, registry_name: str, collection_name: str = "components") -> Dict[str, Any]:
        """
        Rebuild database for a registry from source files.
        This is the standard method for all database rebuilding.
        """
        try:
            files_path = self.get_registry_files_path(registry_name)
            if not files_path.exists():
                return {"success": False, "error": f"Source files directory not found for {registry_name}"}

            # Get all source files (support both .md and .json files)
            source_files = list(files_path.rglob("*.md")) + list(files_path.rglob("*.json"))
            if not source_files:
                return {"success": False, "error": f"No source files found for {registry_name}"}

            # Create fresh database
            result = self.create_database(registry_name, source_files, collection_name)

            if result["success"]:
                result["message"] = f"Successfully rebuilt database for {registry_name}"

            return result

        except Exception as e:
            self.logger.error(f"Failed to rebuild database for {registry_name}: {e}")
            return {"success": False, "error": str(e)}

    def get_database_stats(self, registry_name: str) -> Dict[str, Any]:
        """Get statistics about a registry's database"""
        try:
            collection = self.get_database_client(registry_name)
            if collection is None:
                return {"success": False, "error": f"Database not found for {registry_name}"}

            # Get collection stats
            count = collection.count()

            # Get database path and size
            db_path = self.get_registry_db_path(registry_name)
            db_size = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file()) if db_path.exists() else 0

            return {
                "success": True,
                "registry": registry_name,
                "database_path": str(db_path),
                "document_count": count,
                "database_size_bytes": db_size,
                "database_exists": True
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_all_duplicates(self) -> Dict[str, Any]:
        """Clean up duplicate databases for all registries"""
        try:
            results = {}
            total_removed_files = 0
            total_removed_directories = 0

            for registry_dir in self.registries_base_path.iterdir():
                if registry_dir.is_dir() and registry_dir.name != '__pycache__':
                    result = self.cleanup_duplicate_databases(registry_dir.name)
                    results[registry_dir.name] = result

                    if result["success"]:
                        total_removed_files += len(result.get("removed_files", []))
                        total_removed_directories += len(result.get("removed_directories", []))

            return {
                "success": True,
                "results": results,
                "total_removed_files": total_removed_files,
                "total_removed_directories": total_removed_directories,
                "message": f"Cleaned up {total_removed_files} files and {total_removed_directories} directories across all registries"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

# Singleton instance for global use
_database_manager_instance = None

def get_database_manager(registries_base_path: str = None) -> DatabaseManager:
    """Get singleton DatabaseManager instance"""
    global _database_manager_instance
    if _database_manager_instance is None:
        _database_manager_instance = DatabaseManager(registries_base_path)
    return _database_manager_instance