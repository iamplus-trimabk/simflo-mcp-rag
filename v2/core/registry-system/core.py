#!/usr/bin/env python3
"""
SimFlo MCP RAG - Registry Manager

Manages multiple vector databases for different component libraries
with context-aware routing and search capabilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import chromadb
import chromadb.errors
from chromadb.config import Settings
import threading
import time

from context_manager import get_context_manager, PlatformContext
from project_context_engine import (
    ProjectContextEngine,
    get_project_context_engine,
    enhance_search_with_context,
    detect_project_type
)


@dataclass
class RegistryInfo:
    """Information about a component registry"""
    name: str
    path: str
    platform: List[str]  # Supported platforms
    description: str
    component_count: int = 0
    last_updated: float = 0
    is_active: bool = True
    registry_type: str = "component"  # "component" or "documentation"


@dataclass
class SearchResult:
    """Enhanced search result with context information"""
    registry: str
    component: Dict[str, Any]
    relevance_score: float
    context_match: bool
    platform_relevance: float
    distance: Optional[float] = None


class RegistryManager:
    """Manages multiple vector databases for component libraries"""

    def __init__(self, base_path: str = "./rag_databases"):
        """Initialize registry manager"""
        self.base_path = Path(base_path)
        self.registries: Dict[str, RegistryInfo] = {}
        self.clients: Dict[str, chromadb.Client] = {}
        self.collections: Dict[str, chromadb.Collection] = {}
        self.lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.context_manager = get_context_manager()
        self.project_context_engine = get_project_context_engine()

        # Initialize registries
        self.discover_registries()
        self.initialize_clients()

    def discover_registries(self):
        """Discover available registries in the base path"""
        try:
            if not self.base_path.exists():
                self.logger.warning(f"Base path does not exist: {self.base_path}")
                return

            # Look for registry directories
            for registry_dir in self.base_path.iterdir():
                if registry_dir.is_dir():
                    registry_name = registry_dir.name

                    # Handle component registries (ending with _db)
                    if registry_name.endswith("_db"):
                        components_file = registry_dir / "components.json"
                        config_file = registry_dir / "config.json"

                        if components_file.exists():
                            self._discover_component_registry(registry_dir, components_file)
                        elif config_file.exists():
                            self._discover_documentation_registry(registry_dir, config_file)

                    # Handle documentation registries (ending with _docs)
                    elif registry_name.endswith("_docs"):
                        config_file = registry_dir / "config.json"
                        if config_file.exists():
                            self._discover_documentation_registry(registry_dir, config_file)

        except Exception as e:
            self.logger.error(f"Failed to discover registries: {e}")

    def _discover_component_registry(self, registry_dir: Path, components_file: Path):
        """Discover a component registry"""
        try:
            with open(components_file, 'r') as f:
                data = json.load(f)

            # Determine platform support
            platforms = self._extract_platforms_from_data(data)

            registry_info = RegistryInfo(
                name=registry_dir.name,
                path=str(registry_dir),
                platform=platforms,
                description=f"Component registry for {registry_dir.name.replace('_db', '')}",
                component_count=len(data) if isinstance(data, list) else len(data.get("components", [])),
                last_updated=components_file.stat().st_mtime,
                is_active=True,
                registry_type="component"
            )

            self.registries[registry_dir.name] = registry_info
            self.logger.info(f"Discovered component registry: {registry_dir.name} with {registry_info.component_count} components")

        except Exception as e:
            self.logger.error(f"Failed to load component registry {registry_dir.name}: {e}")

    def _discover_documentation_registry(self, registry_dir: Path, config_file: Path):
        """Discover a documentation registry"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Documentation registries support all platforms by default
            platforms = ["web", "reactjs", "reactnative", "docs"]

            registry_info = RegistryInfo(
                name=registry_dir.name,
                path=str(registry_dir),
                platform=platforms,
                description=f"Documentation registry for {config.get('name', registry_dir.name)}",
                component_count=config.get("pages_extracted", 0),
                last_updated=config_file.stat().st_mtime,
                is_active=True,
                registry_type="documentation"
            )

            self.registries[registry_dir.name] = registry_info
            self.logger.info(f"Discovered documentation registry: {registry_dir.name} with {registry_info.component_count} pages")

        except Exception as e:
            self.logger.error(f"Failed to load documentation registry {registry_dir.name}: {e}")

    def _extract_platforms_from_data(self, data: Union[Dict[str, Any], List[Any]]) -> List[str]:
        """Extract platform information from registry data"""
        platforms = set()

        components = data if isinstance(data, list) else data.get("components", [])
        for component in components:
            if "platform" in component:
                if isinstance(component["platform"], list):
                    platforms.update(component["platform"])
                else:
                    platforms.add(component["platform"])

        # Default to both platforms if none specified
        if not platforms:
            platforms = {"reactjs", "reactnative"}

        return list(platforms)

    def initialize_clients(self):
        """Initialize ChromaDB clients for each registry"""
        for registry_name, registry_info in self.registries.items():
            try:
                # Create ChromaDB client for this registry
                client_path = Path(registry_info.path) / "chroma_db"
                client_path.mkdir(parents=True, exist_ok=True)

                client = chromadb.PersistentClient(
                    path=str(client_path),
                    settings=Settings(anonymized_telemetry=False)
                )

                # Get or create collection with appropriate name
                if registry_info.registry_type == "component":
                    collection_name = f"components_{registry_name.replace('_db', '')}"
                else:  # documentation
                    collection_name = f"documentation_{registry_name.replace('_docs', '').replace('_db', '')}"

                try:
                    collection = client.get_collection(name=collection_name)
                except (ValueError, chromadb.errors.NotFoundError):
                    # Collection doesn't exist, create it
                    collection = client.create_collection(name=collection_name)

                self.clients[registry_name] = client
                self.collections[registry_name] = collection

                self.logger.info(f"Initialized ChromaDB client for {registry_name} ({registry_info.registry_type})")

            except Exception as e:
                self.logger.error(f"Failed to initialize client for {registry_name}: {e}")

    def get_available_registries(self, platform: Optional[PlatformContext] = None) -> List[RegistryInfo]:
        """Get list of available registries, optionally filtered by platform"""
        registries = list(self.registries.values())

        if platform:
            platform_value = platform.value if hasattr(platform, 'value') else str(platform)
            registries = [
                reg for reg in registries
                if platform_value in reg.platform or "both" in reg.platform
            ]

        return sorted(registries, key=lambda x: x.name)

    def get_registries_for_context(self, context: Optional[PlatformContext] = None) -> List[str]:
        """Get appropriate registries for given context"""
        return self.context_manager.get_registries_for_context(context)

    def search_components(
        self,
        query: str,
        platform_context: Optional[PlatformContext] = None,
        limit: int = 10,
        include_fallback: bool = True
    ) -> List[SearchResult]:
        """Search components across context-appropriate registries"""
        registries = self.get_registries_for_context(platform_context)
        all_results: List[SearchResult] = []

        for registry_name in registries:
            if registry_name in self.collections:
                try:
                    results = self._search_single_registry(
                        registry_name,
                        query,
                        limit=limit // len(registries) if len(registries) > 1 else limit
                    )
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"Search failed for {registry_name}: {e}")

        # Sort by combined relevance score
        all_results.sort(key=lambda x: (
            -x.context_match,  # Context matches first
            -x.relevance_score,  # Then by relevance
            x.distance or float('inf')  # Finally by distance
        ))

        return all_results[:limit]

    def search_components_with_context(
        self,
        query: str,
        platform_context: Optional[PlatformContext] = None,
        project_context_query: Optional[str] = None,
        file_list: Optional[List[str]] = None,
        package_json: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Enhanced search with project context awareness"""

        # Detect project type if context information is provided
        if project_context_query or file_list or package_json:
            project_context = self.project_context_engine.detect_project_type(
                query=project_context_query,
                file_list=file_list,
                package_json=package_json
            )

            self.logger.info(f"Detected project context: {project_context.project_type.value} "
                           f"with confidence {project_context.confidence:.2f}")
        else:
            project_context = None

        # Get base search results
        base_results = self.search_components(
            query=query,
            platform_context=platform_context,
            limit=limit * 2  # Get more results for context filtering
        )

        # Convert base results to dictionaries for context enhancement
        base_results_dict = []
        for result in base_results:
            result_dict = result.component.copy()
            result_dict.update({
                "registry": result.registry,
                "relevance_score": result.relevance_score,
                "context_match": result.context_match,
                "platform_relevance": result.platform_relevance,
                "distance": result.distance
            })
            base_results_dict.append(result_dict)

        # Enhance results with project context
        if project_context and project_context.project_type.value != "unknown":
            enhanced_results = self.project_context_engine.enhance_search_results(
                base_results_dict, query
            )

            # Convert enhanced results back to search results with context info
            final_results = []
            for enhanced_result in enhanced_results:
                # Create enhanced result dictionary
                enhanced_dict = enhanced_result.original_result.copy()
                enhanced_dict.update({
                    "context_boost": enhanced_result.context_boost,
                    "context_explanation": enhanced_result.relevance_explanation,
                    "project_type_match": enhanced_result.project_type_match,
                    "platform_alignment": enhanced_result.platform_alignment,
                    "library_compatibility": enhanced_result.library_compatibility,
                    "final_context_score": enhanced_result.final_context_score,
                    "detected_project_type": project_context.project_type.value,
                    "context_confidence": project_context.confidence
                })
                final_results.append(enhanced_dict)

            self.logger.info(f"Enhanced {len(final_results)} results with project context")
        else:
            # No project context detected, return base results with minimal context info
            final_results = []
            for result in base_results_dict:
                result.update({
                    "context_boost": 1.0,
                    "context_explanation": ["No project context detected"],
                    "project_type_match": 0.0,
                    "platform_alignment": 0.0,
                    "library_compatibility": 0.0,
                    "final_context_score": 1.0,
                    "detected_project_type": "unknown",
                    "context_confidence": 0.0
                })
                final_results.append(result)

        # Sort by final context score if available, otherwise by relevance score
        final_results.sort(
            key=lambda x: x.get("final_context_score", x.get("relevance_score", 0.0)),
            reverse=True
        )

        return final_results[:limit]

    def _search_single_registry(
        self,
        registry_name: str,
        query: str,
        limit: int
    ) -> List[SearchResult]:
        """Search within a single registry"""
        collection = self.collections.get(registry_name)
        if not collection:
            return []

        try:
            # Perform vector search
            results = collection.query(
                query_texts=[query],
                n_results=limit
            )
        except (ValueError, chromadb.errors.NotFoundError) as e:
            self.logger.warning(f"Vector search failed for {registry_name}: {e}")
            return []

        search_results: List[SearchResult] = []

        if results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] or [{}] * len(documents)
            distances = results['distances'][0] if 'distances' in results else [None] * len(documents)

            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Skip empty documents
                if not doc or (isinstance(doc, str) and doc.strip() == ''):
                    continue

                # Parse document back to component data
                try:
                    component = json.loads(doc) if isinstance(doc, str) else doc

                    # Skip if component is not a dictionary
                    if not isinstance(component, dict):
                        continue

                    # Calculate relevance scores
                    relevance_score = self._calculate_relevance_score(query, component, metadata)
                    platform_relevance = self._calculate_platform_relevance(registry_name, component)
                    context_match = self._is_context_match(registry_name, component)

                    search_result = SearchResult(
                        registry=registry_name,
                        component=component,
                        relevance_score=relevance_score,
                        context_match=context_match,
                        platform_relevance=platform_relevance,
                        distance=distance
                    )

                    search_results.append(search_result)

                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON for search result {i}: {e}")
                    continue
                except Exception as e:
                    self.logger.warning(f"Failed to process search result {i}: {e}")
                    continue

        return search_results

    def _calculate_relevance_score(self, query: str, component: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate relevance score for a component"""
        score = 0.0

        # Name relevance
        if 'name' in component:
            component_name = component['name'].lower()
            query_lower = query.lower()
            if query_lower in component_name:
                score += 0.5

        # Description relevance
        if 'description' in component and component['description']:
            desc_lower = component['description'].lower()
            query_lower = query.lower()
            if query_lower in desc_lower:
                score += 0.3

        # Tags relevance
        if 'tags' in component and isinstance(component['tags'], list):
            for tag in component['tags']:
                if query.lower() in tag.lower():
                    score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_platform_relevance(self, registry_name: str, component: Dict[str, Any]) -> float:
        """Calculate how relevant this component is to the current context"""
        current_platform = self.context_manager.get_current_platform()
        if current_platform == PlatformContext.NONE:
            return 0.5  # Neutral relevance

        registry_priority = self.context_manager.get_registry_priority(registry_name, current_platform)

        # Check if component explicitly supports current platform
        if 'platform' in component:
            component_platforms = component['platform']
            if isinstance(component_platforms, list):
                if current_platform.value in component_platforms:
                    return 0.8 + (registry_priority / 20.0)
            elif current_platform.value == component_platforms:
                return 0.8 + (registry_priority / 20.0)

        # Fallback to registry-level relevance
        return min(0.3 + (registry_priority / 20.0), 0.7)

    def _is_context_match(self, registry_name: str, component: Dict[str, Any]) -> bool:
        """Check if component matches current context"""
        current_platform = self.context_manager.get_current_platform()
        if current_platform == PlatformContext.NONE:
            return True  # No filtering when no context

        # Check if registry is appropriate for current platform
        registries_for_context = self.get_registries_for_context(current_platform)
        return registry_name in registries_for_context

    def get_component_details(self, component_name: str, registry_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific component"""
        if registry_name:
            # Search specific registry
            return self._get_component_from_registry(registry_name, component_name)
        else:
            # Search all registries
            for reg_name in self.registries:
                component = self._get_component_from_registry(reg_name, component_name)
                if component:
                    return component
            return None

    def _get_component_from_registry(self, registry_name: str, component_name: str) -> Optional[Dict[str, Any]]:
        """Get component from specific registry"""
        collection = self.collections.get(registry_name)
        if not collection:
            return None

        try:
            # Search for component by name
            results = collection.query(
                query_texts=[component_name],
                n_results=1
            )
        except (ValueError, chromadb.errors.NotFoundError) as e:
            self.logger.warning(f"Collection query failed for {registry_name}: {e}")
            return None

        if results and results['documents'] and results['documents'][0]:
            # Find exact match
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0] or [{}]):
                try:
                    component = json.loads(doc) if isinstance(doc, str) else doc
                    if component.get('name') == component_name:
                        return {
                            **component,
                            'registry': registry_name,
                            'found_in_registry': registry_name
                        }
                except:
                    continue

        return None

    def list_components(
        self,
        registry_name: Optional[str] = None,
        platform_context: Optional[PlatformContext] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List components from registry/registries"""
        components = []

        if registry_name:
            registries_to_check = [registry_name]
        else:
            registries_to_check = self.get_registries_for_context(platform_context)

        for reg_name in registries_to_check:
            if reg_name in self.registries:
                registry_info = self.registries[reg_name]
                # Load components from file (simplified approach)
                components_file = Path(registry_info.path) / "components.json"
                if components_file.exists():
                    try:
                        with open(components_file, 'r') as f:
                            data = json.load(f)
                            # Handle both old format (dict with components) and new format (direct list)
                            if isinstance(data, dict) and "components" in data:
                                component_list = data["components"]
                            elif isinstance(data, list):
                                component_list = data
                            else:
                                component_list = []

                            for component in component_list[:limit]:
                                components.append({
                                    **component,
                                    'registry': reg_name
                                })
                    except Exception as e:
                        self.logger.error(f"Failed to load components from {reg_name}: {e}")

        return components[:limit]

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about all registries"""
        stats = {
            "total_registries": len(self.registries),
            "active_registries": sum(1 for reg in self.registries.values() if reg.is_active),
            "total_components": sum(reg.component_count for reg in self.registries.values()),
            "registries": {}
        }

        for name, registry in self.registries.items():
            stats["registries"][name] = {
                "component_count": registry.component_count,
                "platforms": registry.platform,
                "last_updated": registry.last_updated,
                "is_active": registry.is_active
            }

        return stats

    def add_component_to_registry(self, registry_name: str, component: Dict[str, Any]) -> bool:
        """Add a component to a registry (for testing/custom components)"""
        try:
            collection = self.collections.get(registry_name)
            if not collection:
                self.logger.error(f"Registry {registry_name} not found")
                return False

            # Add to vector store
            collection.add(
                documents=[json.dumps(component)],
                metadatas=[{
                    "name": component.get("name", ""),
                    "platform": component.get("platform", "both"),
                    "type": component.get("type", "component"),
                    "registry": registry_name,
                    "timestamp": time.time()
                }],
                ids=[f"{registry_name}_{component.get('name', 'unknown')}_{int(time.time())}"]
            )

            self.logger.info(f"Added component {component.get('name')} to {registry_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add component to {registry_name}: {e}")
            return False

    def add_documentation_pages(self, registry_name: str, pages: List[Dict[str, Any]]) -> bool:
        """Add documentation pages to a registry"""
        if registry_name not in self.registries:
            self.logger.error(f"Registry {registry_name} not found")
            return False

        if self.registries[registry_name].registry_type != "documentation":
            self.logger.error(f"Registry {registry_name} is not a documentation registry")
            return False

        collection = self.collections.get(registry_name)
        if not collection:
            self.logger.error(f"Collection not found for {registry_name}")
            return False

        try:
            # Prepare documents and metadata
            documents = []
            metadatas = []
            ids = []

            for i, page in enumerate(pages):
                # Create document content
                doc_content = json.dumps(page)

                # Create metadata
                metadata = {
                    "name": page.get("name", f"page_{i}"),
                    "type": page.get("type", "documentation"),
                    "category": page.get("category", "documentation"),
                    "url": page.get("metadata", {}).get("url", ""),
                    "page_type": page.get("metadata", {}).get("page_type", "reference"),
                    "source_site": page.get("metadata", {}).get("source_site", "unknown"),
                    "content_length": page.get("metadata", {}).get("content_length", 0),
                    "code_examples_count": page.get("metadata", {}).get("code_examples_count", 0),
                    "registry_type": "documentation",
                    "registry": registry_name
                }

                # Add to batch
                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"{registry_name}_{page.get('name', f'page_{i}')}")

            # Add to collection in batch
            if documents:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

            self.logger.info(f"Added {len(pages)} documentation pages to {registry_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add documentation pages to {registry_name}: {e}")
            return False

    def create_documentation_registry(self, registry_name: str, config: Dict[str, Any]) -> bool:
        """Create a new documentation registry"""
        try:
            # Create registry directory
            registry_path = self.base_path / registry_name
            registry_path.mkdir(parents=True, exist_ok=True)

            # Create config file
            config_file = registry_path / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Create ChromaDB directory
            chroma_path = registry_path / "chroma_db"
            chroma_path.mkdir(parents=True, exist_ok=True)

            # Rediscover registries to pick up the new one
            self.discover_registries()
            self.initialize_clients()

            self.logger.info(f"Created documentation registry: {registry_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create documentation registry {registry_name}: {e}")
            return False

    def search_documentation(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search documentation across all documentation registries"""
        all_results = []

        # Find documentation registries
        doc_registries = [
            name for name, info in self.registries.items()
            if info.registry_type == "documentation"
        ]

        for registry_name in doc_registries:
            if registry_name in self.collections:
                try:
                    results = self._search_single_registry(registry_name, query, limit)
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"Documentation search failed for {registry_name}: {e}")

        # Sort by relevance score
        all_results.sort(key=lambda x: (-x.relevance_score, x.distance or float('inf')))

        return all_results[:limit]

    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get statistics for documentation registries"""
        doc_stats = {
            "total_registries": 0,
            "total_pages": 0,
            "registries": {}
        }

        for name, info in self.registries.items():
            if info.registry_type == "documentation":
                doc_stats["total_registries"] += 1
                doc_stats["total_pages"] += info.component_count

                collection = self.collections.get(name)
                page_count = collection.count() if collection else 0

                doc_stats["registries"][name] = {
                    "component_count": info.component_count,
                    "actual_pages": page_count,
                    "description": info.description,
                    "platforms": info.platform,
                    "last_updated": info.last_updated
                }

        return doc_stats

    def universal_search(
        self,
        query: str,
        platform_context: Optional[PlatformContext] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """Universal search across components and documentation with multi-dimensional context"""
        all_results = []

        # Search components
        component_results = self.search_components(
            query=query,
            limit=limit,
            platform_context=platform_context
        )
        all_results.extend(component_results)

        # Search documentation
        doc_results = self.search_documentation(
            query=query,
            limit=limit
        )
        all_results.extend(doc_results)

        # Sort by relevance score
        all_results.sort(key=lambda x: (-x.relevance_score, x.distance or float('inf')))

        return all_results[:limit]

    def get_project_type_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get project type suggestions based on query"""
        return self.project_context_engine.get_project_type_suggestions(query)

    def detect_project_context(
        self,
        query: Optional[str] = None,
        file_list: Optional[List[str]] = None,
        package_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Detect project context and return detailed information"""
        project_context = self.project_context_engine.detect_project_type(
            query=query,
            file_list=file_list,
            package_json=package_json
        )

        return {
            "project_type": project_context.project_type.value,
            "confidence": project_context.confidence,
            "characteristics": project_context.characteristics,
            "detected_from": project_context.detected_from,
            "timestamp": project_context.timestamp,
            "session_id": project_context.session_id
        }

    def get_context_engine_stats(self) -> Dict[str, Any]:
        """Get context engine statistics"""
        return self.project_context_engine.get_context_stats()


# Global registry manager instance
_registry_manager = None

def get_registry_manager() -> RegistryManager:
    """Get global registry manager instance"""
    global _registry_manager
    if _registry_manager is None:
        _registry_manager = RegistryManager()
    return _registry_manager

def search_components(
    query: str,
    platform_context: Optional[PlatformContext] = None,
    limit: int = 10
) -> List[SearchResult]:
    """Convenience function for component search"""
    return get_registry_manager().search_components(query, platform_context, limit)

def get_component_details(component_name: str, registry_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Convenience function to get component details"""
    return get_registry_manager().get_component_details(component_name, registry_name)

def list_components(
    registry_name: Optional[str] = None,
    platform_context: Optional[PlatformContext] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Convenience function to list components"""
    return get_registry_manager().list_components(registry_name, platform_context, limit)


if __name__ == "__main__":
    # Test the registry manager
    manager = RegistryManager()

    print("Available registries:")
    for registry in manager.get_available_registries():
        print(f"  - {registry.name}: {registry.component_count} components")

    print("\nRegistry stats:")
    print(json.dumps(manager.get_registry_stats(), indent=2))

    # Test search
    print("\nTesting search for 'button':")
    results = manager.search_components("button", limit=5)
    for result in results:
        print(f"  - {result.component.get('name')} in {result.registry} (score: {result.relevance_score:.2f})")