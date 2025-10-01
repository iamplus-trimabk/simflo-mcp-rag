#!/usr/bin/env python3
"""
Category-Aware Search Service

Enhanced search service that provides intelligent category filtering,
weighting, and ranking for component discovery across multiple registries.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio

from models import Component, ComponentCategory, ComponentType
from services.registry_config_manager import RegistryConfigManager

# Add path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    sys.path.append(str(Path(__file__).parent.parent / "data-pipeline"))
    from registry_manager import get_registry_manager, SearchResult
    from context_manager import PlatformContext
except ImportError:
    # Fallback for testing
    SearchResult = None
    PlatformContext = None
    get_registry_manager = None

logger = logging.getLogger(__name__)

class SearchStrategy(Enum):
    """Search strategies for different use cases"""
    EXACT_MATCH = "exact_match"      # Perfect category matches only
    SEMANTIC_SEARCH = "semantic"      # Include related components
    CROSS_CATEGORY = "cross_category" # Search across related categories
    WEIGHTED_BLEND = "weighted"       # Blend results with category weights

@dataclass
class CategoryWeights:
    """Configurable weights for different component categories"""
    components: float = 0.6
    hooks: float = 0.3
    blocks: float = 0.1

    def normalize(self) -> 'CategoryWeights':
        """Normalize weights to sum to 1.0"""
        total = self.components + self.hooks + self.blocks
        if total == 0:
            return CategoryWeights(0.33, 0.33, 0.34)

        return CategoryWeights(
            components=self.components / total,
            hooks=self.hooks / total,
            blocks=self.blocks / total
        )

@dataclass
class SearchFilters:
    """Search filters and parameters"""
    categories: List[ComponentCategory] = field(default_factory=list)
    component_types: List[ComponentType] = field(default_factory=list)
    registries: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    quality_threshold: float = 0.0
    exclude_deprecated: bool = True

    def has_category_filter(self) -> bool:
        """Check if any category filters are set"""
        return len(self.categories) > 0

    def matches_category(self, category: ComponentCategory) -> bool:
        """Check if a category matches the filters"""
        if not self.has_category_filter():
            return True
        return category in self.categories

@dataclass
class SearchQuery:
    """Enhanced search query with context"""
    query: str
    filters: SearchFilters = field(default_factory=SearchFilters)
    strategy: SearchStrategy = SearchStrategy.WEIGHTED_BLEND
    category_weights: CategoryWeights = field(default_factory=CategoryWeights)
    boost_factors: Dict[str, float] = field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Post-initialization processing"""
        # Normalize category weights
        self.category_weights = self.category_weights.normalize()

        # Set default boost factors
        if not self.boost_factors:
            self.boost_factors = {
                "exact_name_match": 2.0,
                "category_match": 1.5,
                "platform_relevance": 1.3,
                "quality_score": 1.2,
                "recency": 1.1
            }

@dataclass
class EnhancedSearchResult:
    """Enhanced search result with detailed scoring"""
    component: Component
    registry: str
    relevance_score: float
    category_relevance: float
    platform_relevance: float
    quality_bonus: float
    final_score: float
    match_explanation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.component.name,
            "display_name": self.component.display_name,
            "description": self.component.description,
            "category": self.component.category.value,
            "type": self.component.type.value,
            "registry": self.registry,
            "relevance_score": self.relevance_score,
            "category_relevance": self.category_relevance,
            "platform_relevance": self.platform_relevance,
            "quality_bonus": self.quality_bonus,
            "final_score": self.final_score,
            "match_explanation": self.match_explanation,
            "quality_score": self.component.quality_score,
            "quality_tier": self.component.quality_tier.value,
            "dependencies": self.component.dependencies,
            "installation": self.component.installation,
            "platform": self.component.platform,
            "framework": self.component.framework,
            "tags": self.component.metadata.tags,
            "search_keywords": self.component.search_keywords
        }

class CategorySearchService:
    """Enhanced category-aware search service"""

    def __init__(self):
        self.registry_manager = None
        self.config_manager = RegistryConfigManager()
        self.logger = logging.getLogger(__name__)

        # Initialize registry manager
        self._initialize_registry_manager()

        # Category keyword mappings for better semantic understanding
        self.category_keywords = {
            ComponentCategory.COMPONENTS: [
                "component", "ui", "element", "widget", "control", "interface",
                "button", "input", "form", "card", "dialog", "modal", "menu"
            ],
            ComponentCategory.HOOKS: [
                "hook", "use", "effect", "state", "context", "reducer",
                "callback", "event", "handler", "lifecycle", "custom"
            ],
            ComponentCategory.BLOCKS: [
                "block", "section", "layout", "container", "grid", "flex",
                "template", "pattern", "composition", "arrangement"
            ]
        }

        # Cross-category relationships
        self.category_relationships = {
            ComponentCategory.COMPONENTS: [ComponentCategory.HOOKS, ComponentCategory.BLOCKS],
            ComponentCategory.HOOKS: [ComponentCategory.COMPONENTS],
            ComponentCategory.BLOCKS: [ComponentCategory.COMPONENTS]
        }

    def _initialize_registry_manager(self):
        """Initialize registry manager with error handling"""
        try:
            self.registry_manager = get_registry_manager()
            self.logger.info("Registry manager initialized successfully")
        except Exception as e:
            self.logger.warning(f"Could not initialize registry manager: {e}")
            self.registry_manager = None

    def create_search_query(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        component_types: Optional[List[str]] = None,
        registries: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        strategy: SearchStrategy = SearchStrategy.WEIGHTED_BLEND,
        quality_threshold: float = 0.0,
        category_weights: Optional[Dict[str, float]] = None
    ) -> SearchQuery:
        """Create an enhanced search query"""

        # Parse categories
        category_filters = []
        if categories:
            for cat_str in categories:
                try:
                    category_filters.append(ComponentCategory(cat_str))
                except ValueError:
                    self.logger.warning(f"Invalid category: {cat_str}")

        # Parse component types
        type_filters = []
        if component_types:
            for type_str in component_types:
                try:
                    type_filters.append(ComponentType(type_str))
                except ValueError:
                    self.logger.warning(f"Invalid component type: {type_str}")

        # Create filters
        filters = SearchFilters(
            categories=category_filters,
            component_types=type_filters,
            registries=registries or [],
            platforms=platforms or [],
            quality_threshold=quality_threshold
        )

        # Set category weights
        weights = CategoryWeights()
        if category_weights:
            weights = CategoryWeights(
                components=category_weights.get("components", 0.6),
                hooks=category_weights.get("hooks", 0.3),
                blocks=category_weights.get("blocks", 0.1)
            ).normalize()

        return SearchQuery(
            query=query,
            filters=filters,
            strategy=strategy,
            category_weights=weights
        )

    async def search_components(self, search_query: SearchQuery, limit: int = 10) -> List[EnhancedSearchResult]:
        """Perform category-aware component search"""
        if not self.registry_manager:
            self.logger.error("Registry manager not available")
            return []

        try:
            # Get platform context if available
            platform_context = None
            if search_query.filters.platforms and search_query.filters.platforms[0]:
                try:
                    platform_context = PlatformContext(search_query.filters.platforms[0])
                except (ValueError, TypeError):
                    pass

            # Perform base search
            base_results = self.registry_manager.search_components(
                query=search_query.query,
                platform_context=platform_context,
                limit=limit * 3  # Get more results for filtering
            )

            # Convert and enhance results
            enhanced_results = await self._enhance_search_results(
                base_results, search_query
            )

            # Apply category-based filtering and ranking
            filtered_results = self._apply_category_filters(
                enhanced_results, search_query
            )

            # Apply strategy-specific ranking
            ranked_results = self._apply_search_strategy(
                filtered_results, search_query
            )

            # Sort by final score and limit results
            ranked_results.sort(key=lambda x: x.final_score, reverse=True)

            return ranked_results[:limit]

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    async def _enhance_search_results(
        self,
        base_results: List[SearchResult],
        search_query: SearchQuery
    ) -> List[EnhancedSearchResult]:
        """Convert base search results to enhanced results with detailed scoring"""
        enhanced_results = []

        for result in base_results:
            try:
                # Convert component data to Component object
                component_data = result.component
                component = self._create_component_from_data(component_data)

                # Calculate category relevance
                category_relevance = self._calculate_category_relevance(
                    component, search_query
                )

                # Calculate quality bonus
                quality_bonus = self._calculate_quality_bonus(component)

                # Create enhanced result
                enhanced_result = EnhancedSearchResult(
                    component=component,
                    registry=result.registry,
                    relevance_score=result.relevance_score,
                    category_relevance=category_relevance,
                    platform_relevance=result.platform_relevance or 0.0,
                    quality_bonus=quality_bonus,
                    final_score=0.0,  # Will be calculated later
                    match_explanation=[]
                )

                enhanced_results.append(enhanced_result)

            except Exception as e:
                self.logger.warning(f"Failed to enhance result: {e}")
                continue

        return enhanced_results

    def _create_component_from_data(self, component_data: Dict[str, Any]) -> Component:
        """Create Component object from legacy data format"""
        # Handle legacy format conversion
        if "categories" in component_data:
            # This appears to be legacy format
            return Component(
                name=component_data.get("name", "unknown"),
                category=self._determine_category_from_legacy(component_data),
                type=self._determine_type_from_legacy(component_data),
                registry=component_data.get("registry", "unknown"),
                priority_source=component_data.get("registry", "unknown"),
                sources=[component_data.get("registry", "unknown")],
                description=component_data.get("description", ""),
                dependencies=component_data.get("dependencies", []),
                installation=component_data.get("installCommand", ""),
                platform=component_data.get("platform", []),
                framework=component_data.get("framework", "react"),
                quality_score=component_data.get("relevance_score", 0.5)
            )
        else:
            # Try to use new format
            return Component.from_dict(component_data)

    def _determine_category_from_legacy(self, data: Dict[str, Any]) -> ComponentCategory:
        """Determine component category from legacy data"""
        categories = data.get("categories", [])
        component_type = data.get("type", "").lower()

        # Check explicit categories
        for cat in categories:
            try:
                return ComponentCategory(cat)
            except ValueError:
                continue

        # Infer from type
        if "hook" in component_type:
            return ComponentCategory.HOOKS
        elif "block" in component_type:
            return ComponentCategory.BLOCKS
        else:
            return ComponentCategory.COMPONENTS

    def _determine_type_from_legacy(self, data: Dict[str, Any]) -> ComponentType:
        """Determine component type from legacy data"""
        component_type = data.get("type", "").lower()

        if "hook" in component_type:
            return ComponentType.HOOK
        elif "block" in component_type:
            return ComponentType.BLOCK
        elif "utility" in component_type:
            return ComponentType.UTILITY
        elif "layout" in component_type:
            return ComponentType.LAYOUT
        else:
            return ComponentType.UI

    def _calculate_category_relevance(self, component: Component, search_query: SearchQuery) -> float:
        """Calculate category relevance score"""
        relevance = 0.0

        # Exact category match
        if search_query.filters.matches_category(component.category):
            relevance += 1.0

        # Keyword-based category relevance
        query_lower = search_query.query.lower()
        category_keywords = self.category_keywords.get(component.category, [])

        for keyword in category_keywords:
            if keyword in query_lower:
                relevance += 0.3

        # Cross-category relevance
        if not search_query.filters.has_category_filter():
            related_categories = self.category_relationships.get(component.category, [])
            for related_cat in related_categories:
                related_keywords = self.category_keywords.get(related_cat, [])
                for keyword in related_keywords:
                    if keyword in query_lower:
                        relevance += 0.1

        return min(relevance, 1.0)

    def _calculate_quality_bonus(self, component: Component) -> float:
        """Calculate quality bonus based on component quality"""
        return component.quality_score * 0.2  # Up to 20% bonus

    def _apply_category_filters(
        self,
        results: List[EnhancedSearchResult],
        search_query: SearchQuery
    ) -> List[EnhancedSearchResult]:
        """Apply category-based filtering"""
        filtered_results = []

        for result in results:
            # Quality threshold filter
            if result.component.quality_score < search_query.filters.quality_threshold:
                continue

            # Deprecated filter
            if search_query.filters.exclude_deprecated and result.component.status == "deprecated":
                continue

            # Registry filter
            if search_query.filters.registries and result.registry not in search_query.filters.registries:
                continue

            # Component type filter
            if search_query.filters.component_types and result.component.type not in search_query.filters.component_types:
                continue

            # Category filter
            if search_query.filters.has_category_filter():
                if not search_query.filters.matches_category(result.component.category):
                    continue

            filtered_results.append(result)

        return filtered_results

    def _apply_search_strategy(
        self,
        results: List[EnhancedSearchResult],
        search_query: SearchQuery
    ) -> List[EnhancedSearchResult]:
        """Apply search strategy for ranking"""
        for result in results:
            explanation = []
            final_score = result.relevance_score

            # Apply category weights
            category_weight = self._get_category_weight(result.component.category, search_query.category_weights)
            final_score *= category_weight
            explanation.append(f"Category weight: {category_weight:.2f}")

            # Apply category relevance boost
            if result.category_relevance > 0:
                boost = 1.0 + (result.category_relevance * search_query.boost_factors.get("category_match", 1.5))
                final_score *= boost
                explanation.append(f"Category relevance boost: {boost:.2f}x")

            # Apply quality bonus
            if result.quality_bonus > 0:
                final_score += result.quality_bonus
                explanation.append(f"Quality bonus: +{result.quality_bonus:.2f}")

            # Apply exact name match boost
            if result.component.name.lower() == search_query.query.lower():
                final_score *= search_query.boost_factors.get("exact_name_match", 2.0)
                explanation.append("Exact name match boost")

            # Apply platform relevance
            if result.platform_relevance > 0:
                platform_boost = 1.0 + (result.platform_relevance * search_query.boost_factors.get("platform_relevance", 1.3))
                final_score *= platform_boost
                explanation.append(f"Platform relevance: {platform_boost:.2f}x")

            result.final_score = final_score
            result.match_explanation = explanation

        return results

    def _get_category_weight(self, category: ComponentCategory, weights: CategoryWeights) -> float:
        """Get weight for a specific category"""
        if category == ComponentCategory.COMPONENTS:
            return weights.components
        elif category == ComponentCategory.HOOKS:
            return weights.hooks
        elif category == ComponentCategory.BLOCKS:
            return weights.blocks
        else:
            return 1.0

    def get_category_statistics(self) -> Dict[str, Any]:
        """Get statistics about component categories across registries"""
        if not self.registry_manager:
            return {}

        try:
            stats = {
                "total_components": 0,
                "categories": {},
                "registries": {}
            }

            # Get all registries
            registries = self.registry_manager.get_available_registries()

            for registry in registries:
                registry_stats = {
                    "name": registry.name,
                    "total_components": registry.component_count,
                    "categories": {
                        "components": 0,
                        "hooks": 0,
                        "blocks": 0
                    }
                }

                # Get components from this registry
                try:
                    components = self.registry_manager.list_components(registry.name, limit=1000)

                    for comp_data in components:
                        try:
                            component = self._create_component_from_data(comp_data)
                            stats["total_components"] += 1

                            # Update category counts
                            cat_key = component.category.value
                            if cat_key not in stats["categories"]:
                                stats["categories"][cat_key] = 0
                            stats["categories"][cat_key] += 1

                            # Update registry category counts
                            if cat_key in registry_stats["categories"]:
                                registry_stats["categories"][cat_key] += 1

                        except Exception as e:
                            continue

                    stats["registries"][registry.name] = registry_stats

                except Exception as e:
                    self.logger.warning(f"Failed to get components for registry {registry.name}: {e}")
                    continue

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get category statistics: {e}")
            return {}

    def suggest_categories(self, query: str) -> List[Dict[str, Any]]:
        """Suggest relevant categories based on search query"""
        query_lower = query.lower()
        suggestions = []

        for category, keywords in self.category_keywords.items():
            match_score = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword in query_lower:
                    match_score += 1
                    matched_keywords.append(keyword)

            if match_score > 0:
                suggestions.append({
                    "category": category.value,
                    "match_score": match_score,
                    "matched_keywords": matched_keywords,
                    "description": f"Components related to {category.value}"
                })

        # Sort by match score
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)

        return suggestions

# Global instance
_category_search_service: Optional[CategorySearchService] = None

def get_category_search_service() -> CategorySearchService:
    """Get the global category search service instance"""
    global _category_search_service
    if _category_search_service is None:
        _category_search_service = CategorySearchService()
    return _category_search_service

# Convenience functions
async def search_components_by_category(
    query: str,
    categories: Optional[List[str]] = None,
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """Convenience function for category-aware search"""
    service = get_category_search_service()
    search_query = service.create_search_query(
        query=query,
        categories=categories,
        **kwargs
    )

    results = await service.search_components(search_query, limit)
    return [result.to_dict() for result in results]

def suggest_search_categories(query: str) -> List[Dict[str, Any]]:
    """Convenience function to get category suggestions"""
    service = get_category_search_service()
    return service.suggest_categories(query)

def get_component_category_stats() -> Dict[str, Any]:
    """Convenience function to get category statistics"""
    service = get_category_search_service()
    return service.get_category_statistics()