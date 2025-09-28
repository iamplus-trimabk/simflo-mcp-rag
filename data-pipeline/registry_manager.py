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
from chromadb.config import Settings
import threading
import time

from context_manager import get_context_manager, PlatformContext


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

    def __init__(self, base_path: str = "../rag_databases"):
        """Initialize registry manager"""
        self.base_path = Path(base_path)
        self.registries: Dict[str, RegistryInfo] = {}
        self.clients: Dict[str, chromadb.Client] = {}
        self.collections: Dict[str, chromadb.Collection] = {}
        self.lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.context_manager = get_context_manager()

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
                if registry_dir.is_dir() and registry_dir.name.endswith("_db"):
                    registry_name = registry_dir.name
                    components_file = registry_dir / "components.json"

                    if components_file.exists():
                        # Load registry info
                        try:
                            with open(components_file, 'r') as f:
                                data = json.load(f)

                            # Determine platform support
                            platforms = self._extract_platforms_from_data(data)

                            registry_info = RegistryInfo(
                                name=registry_name,
                                path=str(registry_dir),
                                platform=platforms,
                                description=f"Registry for {registry_name.replace('_db', '')}",
                                component_count=len(data.get("components", [])),
                                last_updated=components_file.stat().st_mtime,
                                is_active=True
                            )

                            self.registries[registry_name] = registry_info
                            self.logger.info(f"Discovered registry: {registry_name} with {registry_info.component_count} components")

                        except Exception as e:
                            self.logger.error(f"Failed to load registry {registry_name}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to discover registries: {e}")

    def _extract_platforms_from_data(self, data: Dict[str, Any]) -> List[str]:
        """Extract platform information from registry data"""
        platforms = set()

        for component in data.get("components", []):
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

                # Get or create collection
                collection_name = f"components_{registry_name.replace('_db', '')}"
                try:
                    collection = client.get_collection(name=collection_name)
                except ValueError:
                    # Collection doesn't exist, create it
                    collection = client.create_collection(name=collection_name)

                self.clients[registry_name] = client
                self.collections[registry_name] = collection

                self.logger.info(f"Initialized ChromaDB client for {registry_name}")

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

            search_results: List[SearchResult] = []

            if results and results['documents']:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] or [{}] * len(documents)
                distances = results['distances'][0] if 'distances' in results else [None] * len(documents)

                for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    # Parse document back to component data
                    try:
                        component = json.loads(doc) if isinstance(doc, str) else doc

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

                    except Exception as e:
                        self.logger.warning(f"Failed to parse search result {i}: {e}")

            return search_results

        except Exception as e:
            self.logger.error(f"Vector search failed for {registry_name}: {e}")
            return []

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

        except Exception as e:
            self.logger.error(f"Failed to get component {component_name} from {registry_name}: {e}")
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
                            for component in data.get("components", [])[:limit]:
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