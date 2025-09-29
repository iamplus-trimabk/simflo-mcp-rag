#!/usr/bin/env python3
"""
Universal Search Interface

Provides unified search across components and documentation with
smart ranking, filtering, and cross-source result aggregation.
"""

import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Add the data-pipeline directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data-pipeline'))

from registry_manager import get_registry_manager, SearchResult
from project_context_engine import get_project_context_engine
from context_manager import PlatformContext

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchSourceType(Enum):
    """Types of search sources"""
    COMPONENT = "component"
    DOCUMENTATION = "documentation"
    ALL = "all"


class SearchFilter(Enum):
    """Search filter options"""
    PLATFORM = "platform"
    REGISTRY = "registry"
    CATEGORY = "category"
    TYPE = "type"


@dataclass
class UniversalSearchParams:
    """Parameters for universal search"""
    query: str
    source_types: List[SearchSourceType] = None
    filters: Dict[SearchFilter, Any] = None
    platform_context: Optional[PlatformContext] = None
    project_context_query: Optional[str] = None
    file_list: Optional[List[str]] = None
    package_json: Optional[Dict[str, Any]] = None
    limit: int = 10
    include_context: bool = True
    include_explanations: bool = True

    def __post_init__(self):
        if self.source_types is None:
            self.source_types = [SearchSourceType.ALL]
        if self.filters is None:
            self.filters = {}


@dataclass
class UniversalSearchResult:
    """Result from universal search with enhanced metadata"""
    source_type: SearchSourceType
    registry: str
    content: Dict[str, Any]
    title: str
    description: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    context_score: float = 0.0
    final_score: float = 0.0
    platform_relevance: float = 0.0
    context_explanations: List[str] = None
    detected_project_type: str = "unknown"
    context_confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.context_explanations is None:
            self.context_explanations = []
        if self.metadata is None:
            self.metadata = {}


class UniversalSearchEngine:
    """Universal search engine that combines component and documentation search"""

    def __init__(self):
        self.registry_manager = get_registry_manager()
        self.context_engine = get_project_context_engine()
        logger.info("Universal Search Engine initialized")

    def search(self, params: UniversalSearchParams) -> List[UniversalSearchResult]:
        """
        Perform universal search across all configured sources

        Args:
            params: Search parameters including query, filters, and context

        Returns:
            List of ranked search results from all sources
        """
        logger.info(f"Universal search for: '{params.query}' across {params.source_types}")

        # Detect project context if requested
        project_context = None
        if params.include_context and (params.project_context_query or params.file_list or params.package_json):
            project_context = self.context_engine.detect_project_type(
                query=params.project_context_query,
                file_list=params.file_list,
                package_json=params.package_json
            )
            logger.info(f"Detected project context: {project_context.project_type.value} "
                       f"with confidence {project_context.confidence:.2f}")

        # Collect results from different sources
        all_results = []

        # Search components if requested
        if SearchSourceType.ALL in params.source_types or SearchSourceType.COMPONENT in params.source_types:
            component_results = self._search_components(params, project_context)
            all_results.extend(component_results)
            logger.info(f"Found {len(component_results)} component results")

        # Search documentation if requested
        if SearchSourceType.ALL in params.source_types or SearchSourceType.DOCUMENTATION in params.source_types:
            doc_results = self._search_documentation(params, project_context)
            all_results.extend(doc_results)
            logger.info(f"Found {len(doc_results)} documentation results")

        # Apply filters
        if params.filters:
            all_results = self._apply_filters(all_results, params.filters)
            logger.info(f"After filtering: {len(all_results)} results")

        # Rank and sort results
        ranked_results = self._rank_results(all_results, project_context)
        logger.info(f"Ranked {len(ranked_results)} results")

        # Apply limit
        final_results = ranked_results[:params.limit]

        logger.info(f"Returning {len(final_results)} results for '{params.query}'")
        return final_results

    def _search_components(self, params: UniversalSearchParams, project_context) -> List[UniversalSearchResult]:
        """Search for components"""
        try:
            # Use context-aware search if project context is available
            if project_context and params.include_context:
                component_results = self.registry_manager.search_components_with_context(
                    query=params.query,
                    platform_context=params.platform_context,
                    project_context_query=params.project_context_query,
                    file_list=params.file_list,
                    package_json=params.package_json,
                    limit=params.limit * 2  # Get more for ranking
                )
            else:
                component_results = self.registry_manager.search_components(
                    query=params.query,
                    platform_context=params.platform_context,
                    limit=params.limit * 2
                )

            # Convert to universal results
            universal_results = []

            # Handle different return types
            for result in component_results:
                if isinstance(result, dict):
                    # Context-aware search returns dictionaries
                    component_data = result.get("component", {})
                    registry = result.get("registry", "unknown")
                    relevance_score = result.get("relevance_score", 0.0)
                    context_score = result.get("final_context_score", 1.0)
                    context_explanations = result.get("context_explanation", [])
                    project_type = result.get("detected_project_type", "unknown")
                    context_confidence = result.get("context_confidence", 0.0)
                else:
                    # Regular search returns SearchResult objects
                    component_data = result.component
                    registry = result.registry
                    relevance_score = result.relevance_score
                    context_score = 1.0
                    context_explanations = []
                    project_type = "unknown"
                    context_confidence = 0.0

                universal_result = UniversalSearchResult(
                    source_type=SearchSourceType.COMPONENT,
                    registry=registry,
                    content=component_data,
                    title=component_data.get("name", "Unknown Component"),
                    description=component_data.get("description", ""),
                    url=component_data.get("sources", [""])[0] if component_data.get("sources") else None,
                    relevance_score=relevance_score,
                    context_score=context_score,
                    platform_relevance=getattr(result, 'platform_relevance', 0.0),
                    context_explanations=context_explanations,
                    detected_project_type=project_type,
                    context_confidence=context_confidence,
                    metadata={
                        "category": component_data.get("category", ""),
                        "type": component_data.get("type", ""),
                        "platform": component_data.get("platform", []),
                        "dependencies": component_data.get("dependencies", []),
                        "quality_score": component_data.get("quality_score", 0.0)
                    }
                )

                universal_results.append(universal_result)

            return universal_results

        except Exception as e:
            logger.error(f"Component search failed: {e}")
            return []

    def _search_documentation(self, params: UniversalSearchParams, project_context) -> List[UniversalSearchResult]:
        """Search for documentation"""
        try:
            doc_results = self.registry_manager.search_documentation(
                query=params.query,
                limit=params.limit * 2
            )

            # Convert to universal results
            universal_results = []
            for result in doc_results:
                # SearchResult objects have component attribute for content
                doc_content = getattr(result, 'component', {})
                if not doc_content:
                    doc_content = getattr(result, 'content', {})

                universal_result = UniversalSearchResult(
                    source_type=SearchSourceType.DOCUMENTATION,
                    registry=result.registry,
                    content=doc_content,
                    title=doc_content.get("title", doc_content.get("name", "Unknown Document")),
                    description=doc_content.get("description", doc_content.get("summary", "")),
                    url=doc_content.get("url", ""),
                    relevance_score=getattr(result, 'relevance_score', 0.0) or 0.0,
                    metadata={
                        "page_type": doc_content.get("type", ""),
                        "section": doc_content.get("section", ""),
                        "tags": doc_content.get("tags", []),
                        "last_updated": doc_content.get("last_updated", ""),
                        "author": doc_content.get("author", "")
                    }
                )

                # Apply context scoring if project context is available
                if project_context and params.include_context:
                    context_score = self._calculate_document_context_score(
                        doc_content, project_context.project_type.value
                    )
                    universal_result.context_score = context_score
                    universal_result.context_explanations = self._get_document_context_explanations(
                        doc_content, project_context.project_type.value
                    )
                    universal_result.detected_project_type = project_context.project_type.value
                    universal_result.context_confidence = project_context.confidence

                universal_results.append(universal_result)

            return universal_results

        except Exception as e:
            logger.error(f"Documentation search failed: {e}")
            return []

    def _apply_filters(self, results: List[UniversalSearchResult], filters: Dict[SearchFilter, Any]) -> List[UniversalSearchResult]:
        """Apply filters to search results"""
        filtered_results = results.copy()

        for filter_type, filter_value in filters.items():
            if filter_type == SearchFilter.PLATFORM:
                filtered_results = [
                    r for r in filtered_results
                    if filter_value in r.metadata.get("platform", [])
                ]
            elif filter_type == SearchFilter.REGISTRY:
                filtered_results = [r for r in filtered_results if r.registry == filter_value]
            elif filter_type == SearchFilter.CATEGORY:
                filtered_results = [r for r in filtered_results if r.metadata.get("category") == filter_value]
            elif filter_type == SearchFilter.TYPE:
                filtered_results = [r for r in filtered_results if r.metadata.get("type") == filter_value]

        return filtered_results

    def _rank_results(self, results: List[UniversalSearchResult], project_context) -> List[UniversalSearchResult]:
        """Rank results by relevance and context"""
        for result in results:
            # Calculate final score combining relevance and context
            if result.context_score > 0:
                result.final_score = (result.relevance_score * 0.6) + (result.context_score * 0.4)
            else:
                result.final_score = result.relevance_score

        # Sort by final score (descending)
        return sorted(results, key=lambda x: x.final_score, reverse=True)

    def _calculate_document_context_score(self, doc_content: Dict[str, Any], project_type: str) -> float:
        """Calculate context score for documentation"""
        score = 0.0

        # Platform-specific scoring
        if project_type == "react_native":
            if "native" in doc_content.get("title", "").lower() or "mobile" in doc_content.get("title", "").lower():
                score += 0.8
        elif project_type == "next_js":
            if "next" in doc_content.get("title", "").lower() or "web" in doc_content.get("title", "").lower():
                score += 0.8
        elif project_type in ["react_web", "vite_react"]:
            if "react" in doc_content.get("title", "").lower() or "web" in doc_content.get("title", "").lower():
                score += 0.6

        return min(score, 1.0)

    def _get_document_context_explanations(self, doc_content: Dict[str, Any], project_type: str) -> List[str]:
        """Generate context explanations for documentation"""
        explanations = []

        if project_type == "react_native":
            if "native" in doc_content.get("title", "").lower():
                explanations.append("Relevant for React Native development")
        elif project_type == "next_js":
            if "next" in doc_content.get("title", "").lower():
                explanations.append("Relevant for Next.js development")
        elif project_type in ["react_web", "vite_react"]:
            if "react" in doc_content.get("title", "").lower():
                explanations.append("Relevant for React web development")

        if not explanations:
            explanations.append("General documentation")

        return explanations

    def get_available_filters(self) -> Dict[str, List[Any]]:
        """Get available filter options"""
        # Get all registries
        registries = self.registry_manager.get_available_registries()
        registry_names = [reg.name for reg in registries]

        # Get unique platforms, categories, and types from registries
        platforms = set()
        categories = set()
        types = set()

        for registry in registries:
            if hasattr(registry, 'platform'):
                platforms.update(registry.platform)
            # Could extract more metadata from actual content

        return {
            "platform": sorted(list(platforms)),
            "registry": registry_names,
            "category": sorted(list(categories)),
            "type": sorted(list(types))
        }

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics and system info"""
        registries = self.registry_manager.get_available_registries()

        component_count = sum(reg.component_count for reg in registries if reg.registry_type == "component")
        doc_count = sum(reg.component_count for reg in registries if reg.registry_type == "documentation")

        return {
            "total_registries": len(registries),
            "component_registries": len([r for r in registries if r.registry_type == "component"]),
            "documentation_registries": len([r for r in registries if r.registry_type == "documentation"]),
            "total_components": component_count,
            "total_documentation_pages": doc_count,
            "available_filters": self.get_available_filters()
        }


def get_universal_search_engine() -> UniversalSearchEngine:
    """Get singleton instance of universal search engine"""
    global _universal_search_engine
    if _universal_search_engine is None:
        _universal_search_engine = UniversalSearchEngine()
    return _universal_search_engine


# Global instance
_universal_search_engine = None


# Convenience functions
def universal_search(
    query: str,
    source_types: List[str] = None,
    filters: Dict[str, Any] = None,
    platform_context: Optional[PlatformContext] = None,
    project_context_query: Optional[str] = None,
    file_list: Optional[List[str]] = None,
    package_json: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> List[UniversalSearchResult]:
    """Convenience function for universal search"""
    engine = get_universal_search_engine()

    # Convert string source types to enum
    source_enums = []
    if source_types:
        for st in source_types:
            if st == "component":
                source_enums.append(SearchSourceType.COMPONENT)
            elif st == "documentation":
                source_enums.append(SearchSourceType.DOCUMENTATION)
            elif st == "all":
                source_enums.append(SearchSourceType.ALL)
    else:
        source_enums = [SearchSourceType.ALL]

    # Convert string filters to enum
    filter_enums = {}
    if filters:
        for key, value in filters.items():
            if key == "platform":
                filter_enums[SearchFilter.PLATFORM] = value
            elif key == "registry":
                filter_enums[SearchFilter.REGISTRY] = value
            elif key == "category":
                filter_enums[SearchFilter.CATEGORY] = value
            elif key == "type":
                filter_enums[SearchFilter.TYPE] = value

    params = UniversalSearchParams(
        query=query,
        source_types=source_enums,
        filters=filter_enums,
        platform_context=platform_context,
        project_context_query=project_context_query,
        file_list=file_list,
        package_json=package_json,
        limit=limit
    )

    return engine.search(params)


if __name__ == "__main__":
    # Test the universal search engine
    engine = get_universal_search_engine()

    # Get statistics
    stats = engine.get_search_statistics()
    print("Universal Search Engine Statistics:")
    print(f"  Total Registries: {stats['total_registries']}")
    print(f"  Components: {stats['total_components']}")
    print(f"  Documentation Pages: {stats['total_documentation_pages']}")
    print()

    # Test a search
    results = universal_search(
        query="button",
        source_types=["component", "documentation"],
        project_context_query="I'm building a React Native mobile app",
        limit=5
    )

    print(f"Search Results for 'button' (React Native context):")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.title} ({result.source_type.value} from {result.registry})")
        print(f"     Score: {result.final_score:.2f} (Relevance: {result.relevance_score:.2f}, Context: {result.context_score:.2f})")
        if result.context_explanations:
            print(f"     Context: {'; '.join(result.context_explanations)}")
        print(f"     Description: {result.description[:100]}...")
        print()