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
from database_manager import get_database_manager, DatabaseManager


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

    def __init__(self, base_path: str = None):
        """Initialize registry manager"""
        if base_path is None:
            # Default to the correct absolute path
            base_path = str(Path(__file__).parent.parent.parent / "00-rag-registry" / "registries")
        self.base_path = Path(base_path)
        self.registries: Dict[str, RegistryInfo] = {}
        self.collections: Dict[str, chromadb.Collection] = {}
        self.lock = threading.Lock()

        # Setup logging and dependencies
        self.logger = logging.getLogger(__name__)
        self.context_manager = get_context_manager()
        self.project_context_engine = get_project_context_engine()

        # Initialize centralized database manager
        self.database_manager = get_database_manager(base_path)

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

                    # Handle all directories as potential registries
                    # Check for registry structure (db/ and files/ directories)
                    db_dir = registry_dir / "db"
                    files_dir = registry_dir / "files"

                    if db_dir.exists() or files_dir.exists():
                        self._discover_registry_from_structure(registry_dir, registry_name)

                    # Handle component registries (ending with _db) - legacy support
                    elif registry_name.endswith("_db"):
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

    def _discover_registry_from_structure(self, registry_dir: Path, registry_name: str):
        """Discover registry from directory structure (db/ and files/)"""
        try:
            # Count source files
            source_files = []
            files_dir = registry_dir / "files"
            if files_dir.exists():
                for file_path in files_dir.rglob("*.md"):
                    source_files.append(file_path)
                for file_path in files_dir.rglob("*.json"):
                    source_files.append(file_path)

            # Determine platform support based on registry name
            platforms = ["reactjs", "reactnative", "web"]
            if "shadcn" in registry_name.lower():
                platforms = ["reactjs", "web"]
            elif "gluestack" in registry_name.lower():
                platforms = ["reactjs", "reactnative", "web"]
            elif "community" in registry_name.lower():
                platforms = ["reactjs", "reactnative", "web", "vue", "angular"]
            elif "radix" in registry_name.lower():
                platforms = ["reactjs", "web"]

            registry_info = RegistryInfo(
                name=registry_name,
                path=str(registry_dir),
                platform=platforms,
                description=f"Component registry for {registry_name}",
                component_count=len(source_files),
                last_updated=registry_dir.stat().st_mtime if registry_dir.exists() else 0,
                is_active=True,
                registry_type="component"
            )

            self.registries[registry_name] = registry_info
            self.logger.info(f"Discovered registry from structure: {registry_name} with {len(source_files)} files")

        except Exception as e:
            self.logger.error(f"Failed to discover registry {registry_name} from structure: {e}")

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
        """Initialize ChromaDB collections for each registry using centralized DatabaseManager"""
        for registry_name, registry_info in self.registries.items():
            try:
                # Get collection using centralized database manager
                if registry_info.registry_type == "component":
                    collection_name = "components"  # Standardized collection name
                else:  # documentation
                    collection_name = "documentation"  # Standardized collection name

                collection = self.database_manager.get_database_client(registry_name, collection_name)

                if collection:
                    self.collections[registry_name] = collection
                    self.logger.info(f"Initialized collection for {registry_name} ({registry_info.registry_type})")
                else:
                    self.logger.error(f"Failed to get collection for {registry_name}")

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
                    # Calculate limit per registry, ensuring at least 1 result per registry
                    per_registry_limit = max(1, limit // len(registries)) if len(registries) > 1 else limit
                    results = self._search_single_registry(
                        registry_name,
                        query,
                        limit=per_registry_limit
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

        # If vector search returns no results, try fallback text search
        if not results or not results['documents'] or not results['documents'][0]:
            self.logger.info(f"Vector search empty for {registry_name}, trying fallback text search")
            return self._fallback_text_search(registry_name, query, limit)

        search_results: List[SearchResult] = []

        if results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] or [{}] * len(documents)
            distances = results['distances'][0] if 'distances' in results else [None] * len(documents)

            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Skip empty documents
                if not doc or (isinstance(doc, str) and doc.strip() == ''):
                    continue

                # Reconstruct component data from metadata (since vector DB stores search text, not JSON)
                try:
                    # Build component dictionary from metadata
                    component = {
                        "name": metadata.get("name", ""),
                        "title": metadata.get("title", ""),
                        "registry": metadata.get("registry", registry_name),
                        "source_file": metadata.get("source_file", ""),
                        "type": metadata.get("type", "component"),
                        "file_path": metadata.get("file_path", "")
                    }

                    # Parse JSON fields from metadata
                    try:
                        component["tags"] = json.loads(metadata.get("tags", "[]"))
                    except:
                        component["tags"] = []

                    try:
                        component["platform"] = json.loads(metadata.get("platform", "[]"))
                    except:
                        component["platform"] = []

                    # Add installation and usage if available
                    if metadata.get("installation"):
                        component["installation"] = metadata["installation"]
                    if metadata.get("usage"):
                        component["usage"] = metadata["usage"]

                    # Skip if component name is empty
                    if not component.get("name"):
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

                except Exception as e:
                    self.logger.warning(f"Failed to process vector search result {i}: {e}")
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

    def _is_component_match(self, search_name: str, stored_name: str) -> bool:
        """Check if search name matches stored component name using various strategies"""
        search_name = search_name.lower().strip()
        stored_name = stored_name.lower().strip()

        # Exact match
        if search_name == stored_name:
            return True

        # Check if search name is contained in stored name
        if search_name in stored_name or stored_name in search_name:
            return True

        # Handle registry prefixes (e.g., "shadcn_button" matches "button")
        prefixes = ["shadcn_", "gluestack_", "radix_", "mui_", "ant_"]
        clean_stored = stored_name
        for prefix in prefixes:
            if stored_name.startswith(prefix):
                clean_stored = stored_name[len(prefix):]
                break

        if search_name == clean_stored:
            return True

        # Handle suffixes and partial matches
        # Split on common separators and check parts
        search_parts = search_name.replace('-', ' ').replace('_', ' ').split()
        stored_parts = stored_name.replace('-', ' ').replace('_', ' ').split()

        # If any part matches exactly
        for search_part in search_parts:
            for stored_part in stored_parts:
                if search_part == stored_part and len(search_part) > 2:  # Only match meaningful parts
                    return True

        # Handle common variations
        variations = {
            'button': 'btn',
            'dialog': 'modal',
            'input': 'textfield',
            'select': 'dropdown',
            'checkbox': 'check',
            'radio': 'radiobutton'
        }

        for standard, variation in variations.items():
            if (search_name == standard and clean_stored == variation) or \
               (search_name == variation and clean_stored == standard):
                return True

        return False

    def _parse_component_from_markdown(self, doc: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Parse component information from raw markdown content"""
        try:
            # Parse the raw markdown content directly
            lines = doc.split('\n')

            # Extract component information from markdown structure
            title = ''
            description = ''
            installation = ''
            usage = ''
            tags = []

            # Parse the markdown content structure
            current_section = None
            content_lines = []
            in_code_block = False

            for line in lines:
                original_line = line
                line = line.strip()

                if line.startswith('# '):
                    title = line[2:].strip()
                elif line.startswith('## '):
                    current_section = line[3:].lower()
                    content_lines = []
                    in_code_block = False
                elif line.startswith('```'):
                    if not in_code_block:
                        # Start of code block
                        in_code_block = True
                        if current_section not in ['installation', 'usage']:
                            content_lines = []  # Reset for new code block
                    else:
                        # End of code block
                        in_code_block = False
                        if content_lines:
                            content = '\n'.join(content_lines)
                            if current_section == 'installation' and not installation:
                                installation = content
                            elif current_section == 'usage' and not usage:
                                usage = content
                        content_lines = []
                elif in_code_block:
                    # Inside code block - preserve original formatting
                    content_lines.append(original_line.rstrip())
                elif line and not line.startswith('```'):
                    if current_section == 'installation':
                        if '```bash' not in line:
                            content_lines.append(line.strip())
                    elif current_section == 'usage':
                        if '```tsx' not in line and not line.startswith('```'):
                            content_lines.append(line.strip())
                    elif not current_section and not line.startswith('#') and not line.startswith('-') and not line.startswith('**') and not line.startswith('*Extracted'):
                        # Description content (before any ## sections)
                        if not description and line.strip():
                            description = line.strip()
                    elif '**Tags**:' in line:
                        # Extract tags from Component Details section
                        tags_line = line.split('**Tags**:')[-1].strip()
                        if tags_line:
                            tags = [tag.strip() for tag in tags_line.split(',')]

            # If installation or usage weren't found in code blocks, try to extract them from content_lines
            if not installation and content_lines and current_section == 'installation':
                installation = '\n'.join(content_lines)
            if not usage and content_lines and current_section == 'usage':
                usage = '\n'.join(content_lines)

            # Clean up installation and usage formatting
            if installation and not installation.startswith('```'):
                installation = f"```bash\n{installation}\n```"
            if usage and not usage.startswith('```'):
                usage = f"```tsx\n{usage}\n```"

            # Extract platform from metadata or default to reactjs
            platform = ['reactjs']  # Default for shadcn
            if metadata.get('platform'):
                if isinstance(metadata['platform'], str):
                    if metadata['platform'].startswith('['):  # JSON array format
                        try:
                            platform = json.loads(metadata['platform'])
                        except:
                            platform = [metadata['platform']]
                    else:
                        platform = [metadata['platform']]
                elif isinstance(metadata['platform'], list):
                    platform = metadata['platform']

            # Build component dict from parsed markdown (not from metadata)
            component = {
                'name': metadata.get('name', ''),
                'title': title,
                'description': description or f"A {metadata.get('name', 'component')} component",
                'installation': installation,
                'usage': usage,
                'tags': tags,
                'category': 'ui',
                'registry': metadata.get('registry', ''),
                'file_path': metadata.get('file_path', ''),
                'source_file': metadata.get('source_file', ''),
                'platform': platform,
                'type': metadata.get('type', 'component')
            }

            return component

        except Exception as e:
            self.logger.warning(f"Error parsing component from markdown: {e}")
            # Fallback to metadata only
            return {
                'name': metadata.get('name', ''),
                'title': metadata.get('title', ''),
                'description': f"A {metadata.get('name', 'component')} component",
                'installation': '',
                'usage': '',
                'tags': [],
                'category': metadata.get('type', 'ui'),
                'registry': metadata.get('registry', ''),
                'file_path': metadata.get('file_path', ''),
                'platform': ['reactjs'],
                'type': metadata.get('type', 'component')
            }

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
            # First, try exact match
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0] or [{}]):
                try:
                    # Use metadata instead of trying to parse document as JSON
                    if metadata.get('name') == component_name:
                        component = self._parse_component_from_markdown(doc, metadata)
                        return {
                            **component,
                            'registry': registry_name,
                            'found_in_registry': registry_name
                        }
                except Exception as e:
                    self.logger.error(f"Error processing component for exact match: {e}")
                    raise e  # Fail fast - don't hide the problem

            # If no exact match, try fuzzy matching
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0] or [{}]):
                try:
                    # Use metadata for component matching
                    stored_name = metadata.get('name', '')

                    # Try various matching strategies
                    if self._is_component_match(component_name, stored_name):
                        component = self._parse_component_from_markdown(doc, metadata)
                        return {
                            **component,
                            'registry': registry_name,
                            'found_in_registry': registry_name,
                            'match_type': 'fuzzy'
                        }
                except Exception as e:
                    self.logger.error(f"Error processing component for fuzzy match: {e}")
                    raise e  # Fail fast - don't hide the problem

        # If vector search found nothing, try fallback text search
        self.logger.info(f"Vector search for component '{component_name}' in {registry_name} returned no results, trying fallback")
        fallback_results = self._fallback_text_search(registry_name, component_name, 10)

        for result in fallback_results:
            if result.component.get('name') == component_name:
                return {
                    **result.component,
                    'registry': registry_name,
                    'found_in_registry': registry_name,
                    'relevance_score': result.relevance_score,
                    'platform_relevance': result.platform_relevance
                }

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

                # First try to load from components.json file
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
                else:
                    # Fallback: search for markdown files in the files directory
                    files_dir = Path(registry_info.path) / "files"
                    if files_dir.exists():
                        try:
                            for file_path in files_dir.rglob("*.md"):
                                if len(components) >= limit:
                                    break

                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()

                                    # Parse component from markdown
                                    component = self._parse_component_from_file(file_path, content, reg_name)
                                    if component:
                                        components.append(component)

                                except Exception as e:
                                    self.logger.warning(f"Failed to parse component from {file_path}: {e}")
                                    continue

                        except Exception as e:
                            self.logger.error(f"Failed to scan files directory for {reg_name}: {e}")

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

    def _fallback_text_search(self, registry_name: str, query: str, limit: int) -> List[SearchResult]:
        """Fallback text search when vector search is empty"""
        try:
            registry_info = self.registries.get(registry_name)
            if not registry_info:
                return []

            # Search through the files directory for markdown files
            files_dir = Path(registry_info.path) / "files"
            if not files_dir.exists():
                self.logger.warning(f"Files directory not found for registry {registry_name}: {files_dir}")
                return []

            query_lower = query.lower()
            search_results: List[SearchResult] = []

            # Recursively search through markdown files
            for file_path in files_dir.rglob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Simple text matching - also check filename for exact component name matches
                    filename_match = file_path.stem.lower() == query_lower
                    content_match = query_lower in content.lower()

                    if filename_match or content_match:
                        # Extract component information from file
                        component = self._parse_component_from_file(file_path, content, registry_name)
                        if component:
                            # Calculate relevance score based on text matching
                            # Give higher score for exact filename matches
                            if filename_match:
                                relevance_score = 1.0  # Perfect match for component name
                            else:
                                relevance_score = self._calculate_text_relevance(query_lower, content, component)

                            search_result = SearchResult(
                                registry=registry_name,
                                component=component,
                                relevance_score=relevance_score,
                                context_match=self._is_context_match(registry_name, component),
                                platform_relevance=self._calculate_platform_relevance(registry_name, component),
                                distance=None  # No vector distance in text search
                            )
                            search_results.append(search_result)

                except Exception as e:
                    self.logger.warning(f"Failed to search file {file_path}: {e}")
                    continue

            # Sort by relevance score and limit results
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return search_results[:limit]

        except Exception as e:
            self.logger.error(f"Fallback text search failed for {registry_name}: {e}")
            return []

    def _parse_component_from_file(self, file_path: Path, content: str, registry_name: str) -> Optional[Dict[str, Any]]:
        """Parse component information from markdown file"""
        try:
            # Extract basic component info from markdown
            lines = content.split('\n')
            component = {}

            # Default component name from filename
            component['name'] = file_path.stem
            component['registry'] = registry_name
            component['source_file'] = str(file_path.relative_to(Path(self.base_path)))

            # Extract title from first # header
            for line in lines:
                if line.startswith('# '):
                    component['title'] = line[2:].strip()
                    break

            # Extract description from first paragraph after title (before any ## sections)
            description_lines = []
            found_title = False
            for line in lines:
                if line.startswith('# '):
                    found_title = True
                    continue
                elif found_title and line.strip() and not line.startswith('#') and not line.startswith('##') and not line.startswith('-') and not line.startswith('**') and not line.startswith('*Extracted'):
                    if line.strip():
                        description_lines.append(line.strip())
                    else:
                        break  # Stop at empty line
                elif found_title and line.startswith('##'):
                    break  # Stop at first section header

            if description_lines:
                component['description'] = ' '.join(description_lines)

            # Extract installation instructions
            installation_started = False
            installation_lines = []
            for line in lines:
                if '## Installation' in line:
                    installation_started = True
                    continue  # Skip the ## Installation line
                if installation_started and line.startswith('```bash'):
                    installation_lines.append(line.strip())
                elif installation_started and line.startswith('```') and not line.startswith('```bash'):
                    break  # End of installation section
                elif installation_started and line.strip():
                    installation_lines.append(line.strip())

            if installation_lines:
                # Join lines and format as code block if not already
                installation = '\n'.join(installation_lines)
                if not installation.startswith('```bash'):
                    installation = f"```bash\n{installation}\n```"
                component['installation'] = installation

            # Extract usage example
            usage_started = False
            usage_lines = []
            for line in lines:
                if '## Usage' in line:
                    usage_started = True
                    continue
                elif usage_started and line.startswith('##'):
                    break
                elif usage_started and (line.startswith('```') or line.strip()):
                    usage_lines.append(line)

            if usage_lines:
                component['usage'] = '\n'.join(usage_lines)

            # Add some default tags based on content
            tags = []
            content_lower = content.lower()
            if 'button' in content_lower:
                tags.append('button')
            if 'dialog' in content_lower or 'modal' in content_lower:
                tags.append('dialog')
            if 'react' in content_lower:
                tags.append('react')
            if 'typescript' in content_lower or 'tsx' in content_lower:
                tags.append('typescript')
            if 'accessible' in content_lower or 'accessibility' in content_lower:
                tags.append('accessible')

            component['tags'] = tags
            component['platform'] = ['reactjs']  # Default platform

            return component

        except Exception as e:
            self.logger.warning(f"Failed to parse component from {file_path}: {e}")
            return None

    def _calculate_text_relevance(self, query_lower: str, content: str, component: Dict[str, Any]) -> float:
        """Calculate relevance score based on text matching"""
        score = 0.0
        content_lower = content.lower()

        # Name matches are worth more
        if 'name' in component:
            component_name = component['name'].lower()
            if query_lower in component_name:
                score += 0.8
            elif component_name in query_lower:
                score += 0.6

        # Title matches
        if 'title' in component:
            title_lower = component['title'].lower()
            if query_lower in title_lower:
                score += 0.7

        # Description matches
        if 'description' in component:
            desc_lower = component['description'].lower()
            if query_lower in desc_lower:
                score += 0.5

        # Count occurrences in content (but cap the contribution)
        occurrences = content_lower.count(query_lower)
        score += min(occurrences * 0.1, 0.3)

        # Tag matches
        if 'tags' in component and isinstance(component['tags'], list):
            for tag in component['tags']:
                if query_lower in tag.lower():
                    score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    def index_registry_files(self, registry_name: str) -> bool:
        """Index markdown files from registry into vector database using centralized DatabaseManager"""
        try:
            # Use centralized database manager to rebuild the database
            result = self.database_manager.rebuild_database(registry_name, "components")

            if result["success"]:
                # Refresh the collection reference
                collection = self.database_manager.get_database_client(registry_name, "components")
                if collection:
                    self.collections[registry_name] = collection

                self.logger.info(f"Successfully indexed {registry_name} with {result['documents_processed']} documents")
                return True
            else:
                self.logger.error(f"Failed to index {registry_name}: {result['error']}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to index registry {registry_name}: {e}")
            return False

    def _create_search_text_from_component(self, component: Dict[str, Any]) -> str:
        """Create searchable text from component dictionary"""
        parts = []

        # Add name and title
        if component.get("name"):
            parts.append(f"Name: {component['name']}")
        if component.get("title"):
            parts.append(f"Title: {component['title']}")

        # Add description
        if component.get("description"):
            parts.append(f"Description: {component['description']}")

        # Add tags
        if component.get("tags"):
            tags_str = " ".join(component["tags"]) if isinstance(component["tags"], list) else str(component["tags"])
            parts.append(f"Tags: {tags_str}")

        # Add platform info
        if component.get("platform"):
            platform_str = " ".join(component["platform"]) if isinstance(component["platform"], list) else str(component["platform"])
            parts.append(f"Platform: {platform_str}")

        # Add installation info
        if component.get("installation"):
            parts.append(f"Installation: {component['installation']}")

        # Add usage info
        if component.get("usage"):
            parts.append(f"Usage: {component['usage']}")

        # Add source file
        if component.get("source_file"):
            parts.append(f"Source: {component['source_file']}")

        return "\n".join(parts)

    def index_all_registries(self) -> Dict[str, bool]:
        """Index all registries into vector database"""
        results = {}

        for registry_name in self.registries.keys():
            self.logger.info(f"Indexing registry: {registry_name}")
            results[registry_name] = self.index_registry_files(registry_name)

        return results


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