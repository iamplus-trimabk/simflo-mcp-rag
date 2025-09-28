"""
Multi-Source Merger

Handles merging components from multiple sources with conflict resolution,
quality scoring, and source boosting.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime
import json

from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata
from services.registry_config_manager import SourceConfig

logger = logging.getLogger(__name__)

class ConflictResolution:
    """Strategy for resolving conflicts between sources"""
    PRIORITY_BASED = "priority_based"
    QUALITY_BASED = "quality_based"
    MERGE_BASED = "merge_based"
    MANUAL = "manual"

class MultiSourceMerger:
    """Merges components from multiple sources with intelligent conflict resolution"""

    def __init__(self, resolution_strategy: str = ConflictResolution.PRIORITY_BASED):
        self.resolution_strategy = resolution_strategy
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def merge_sources(
        self,
        components: List[Dict[str, Any]],
        sources: List[SourceConfig]
    ) -> List[Dict[str, Any]]:
        """
        Merge components from multiple sources using the configured strategy
        """
        if not components:
            return []

        if not sources:
            self.logger.warning("No sources provided for merging")
            return components

        # Create source priority mapping
        source_priority = {source.name: source.priority for source in sources}
        self.logger.info(f"Merging {len(components)} components from {len(sources)} sources")

        # Group components by name
        component_groups = self._group_components_by_name(components)

        # Merge each group
        merged_components = []
        for name, variants in component_groups.items():
            try:
                merged = self._merge_component_group(name, variants, source_priority)
                if merged:
                    merged_components.append(merged)
            except Exception as e:
                self.logger.error(f"Failed to merge component group {name}: {e}")
                continue

        self.logger.info(f"Merged {len(merged_components)} components from {len(component_groups)} groups")
        return merged_components

    def _group_components_by_name(self, components: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group components by their name"""
        groups = defaultdict(list)

        for component in components:
            name = component.get("name", "unknown")
            groups[name].append(component)

        self.logger.debug(f"Grouped {len(components)} components into {len(groups)} groups")
        return groups

    def _merge_component_group(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Merge a group of component variants using the resolution strategy"""
        if not variants:
            return None

        if len(variants) == 1:
            # Single variant, just normalize it
            return self._normalize_component(variants[0])

        self.logger.debug(f"Merging {len(variants)} variants of component '{name}'")

        if self.resolution_strategy == ConflictResolution.PRIORITY_BASED:
            return self._merge_priority_based(name, variants, source_priority)
        elif self.resolution_strategy == ConflictResolution.QUALITY_BASED:
            return self._merge_quality_based(name, variants)
        elif self.resolution_strategy == ConflictResolution.MERGE_BASED:
            return self._merge_based(name, variants, source_priority)
        else:
            self.logger.warning(f"Unknown resolution strategy: {self.resolution_strategy}")
            return self._merge_priority_based(name, variants, source_priority)

    def _merge_priority_based(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> Dict[str, Any]:
        """Merge using priority-based resolution"""
        # Select highest priority variant as base
        base_variant = self._select_highest_priority_variant(variants, source_priority)
        if not base_variant:
            return self._merge_quality_based(name, variants)

        # Collect information from all variants
        all_sources = set()
        source_metadata = {}
        quality_scores = []

        for variant in variants:
            # Collect sources
            sources = variant.get("sources", [])
            all_sources.update(sources)

            # Collect source metadata
            variant_metadata = variant.get("source_metadata", {})
            source_metadata.update(variant_metadata)

            # Collect quality scores
            quality_scores.append(variant.get("quality_score", 0.5))

        # Create merged component
        merged = base_variant.copy()
        merged["sources"] = list(all_sources)
        merged["source_metadata"] = source_metadata

        # Set priority source
        merged["priority_source"] = self._get_priority_source(all_sources, source_priority)

        # Calculate merged quality score
        merged["quality_score"] = max(quality_scores) if quality_scores else 0.5

        # Merge metadata intelligently
        merged = self._merge_metadata(merged, variants)

        self.logger.debug(f"Priority-based merge for '{name}': selected {merged['priority_source']} as priority source")
        return merged

    def _merge_quality_based(
        self,
        name: str,
        variants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge using quality-based resolution"""
        # Select highest quality variant as base
        base_variant = self._select_highest_quality_variant(variants)
        if not base_variant:
            # Fallback to first variant
            base_variant = variants[0]

        # Collect information from all variants
        all_sources = set()
        source_metadata = {}

        for variant in variants:
            sources = variant.get("sources", [])
            all_sources.update(sources)

            variant_metadata = variant.get("source_metadata", {})
            source_metadata.update(variant_metadata)

        # Create merged component
        merged = base_variant.copy()
        merged["sources"] = list(all_sources)
        merged["source_metadata"] = source_metadata

        # Set priority source based on quality
        merged["priority_source"] = self._get_quality_based_priority_source(variants)

        # Calculate average quality score
        quality_scores = [v.get("quality_score", 0.5) for v in variants]
        merged["quality_score"] = sum(quality_scores) / len(quality_scores)

        # Merge metadata intelligently
        merged = self._merge_metadata(merged, variants)

        self.logger.debug(f"Quality-based merge for '{name}': quality score {merged['quality_score']:.3f}")
        return merged

    def _merge_based(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> Dict[str, Any]:
        """Merge using smart merging strategy"""
        # Start with the highest priority variant
        base_variant = self._select_highest_priority_variant(variants, source_priority)
        if not base_variant:
            base_variant = variants[0]

        merged = base_variant.copy()

        # Merge fields intelligently
        merged["sources"] = self._merge_sources(variants)
        merged["dependencies"] = self._merge_dependencies(variants)
        merged["platform"] = self._merge_platforms(variants)
        merged["usage_examples"] = self._merge_usage_examples(variants)

        # Handle conflicts in critical fields
        merged["description"] = self._resolve_description_conflict(variants, source_priority)
        merged["installation"] = self._resolve_installation_conflict(variants, source_priority)
        merged["quality_score"] = self._calculate_merged_quality_score(variants)

        # Set priority source
        merged["priority_source"] = self._get_priority_source(merged["sources"], source_priority)

        # Merge source metadata
        source_metadata = {}
        for variant in variants:
            source_metadata.update(variant.get("source_metadata", {}))
        merged["source_metadata"] = source_metadata

        self.logger.debug(f"Smart merge for '{name}': merged {len(variants)} variants")
        return merged

    def _select_highest_priority_variant(
        self,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Select the variant with the highest priority source"""
        if not variants:
            return None

        best_variant = None
        best_priority = float('inf')

        for variant in variants:
            sources = variant.get("sources", [])
            if not sources:
                continue

            # Get the highest priority source in this variant
            variant_priority = min(source_priority.get(source, 999) for source in sources)

            if variant_priority < best_priority:
                best_priority = variant_priority
                best_variant = variant

        return best_variant

    def _select_highest_quality_variant(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the variant with the highest quality score"""
        if not variants:
            return None

        best_variant = None
        best_score = -1

        for variant in variants:
            score = variant.get("quality_score", 0.0)
            if score > best_score:
                best_score = score
                best_variant = variant

        return best_variant

    def _get_priority_source(self, sources: List[str], source_priority: Dict[str, int]) -> str:
        """Get the priority source from a list of sources"""
        if not sources:
            return "unknown"

        # Return source with highest priority (lowest priority number)
        return min(sources, key=lambda s: source_priority.get(s, 999))

    def _get_quality_based_priority_source(self, variants: List[Dict[str, Any]]) -> str:
        """Get priority source based on quality"""
        best_variant = self._select_highest_quality_variant(variants)
        if best_variant:
            sources = best_variant.get("sources", [])
            return sources[0] if sources else "unknown"
        return "unknown"

    def _merge_metadata(self, base: Dict[str, Any], variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Intelligently merge metadata from multiple variants"""
        # Start with base metadata
        metadata = base.get("metadata", {}).copy()

        # Collect all unique values for each field
        for field in ["tags", "keywords", "accessibility_features", "browser_support"]:
            all_values = set()
            for variant in variants:
                variant_metadata = variant.get("metadata", {})
                values = variant_metadata.get(field, [])
                if isinstance(values, list):
                    all_values.update(values)

            if all_values:
                metadata[field] = list(all_values)

        # For scalar fields, prefer the highest quality variant
        scalar_fields = ["author", "license", "repository_url", "documentation_url"]
        best_variant = self._select_highest_quality_variant(variants)
        if best_variant:
            best_metadata = best_variant.get("metadata", {})
            for field in scalar_fields:
                if field in best_metadata:
                    metadata[field] = best_metadata[field]

        return metadata

    def _merge_sources(self, variants: List[Dict[str, Any]]) -> List[str]:
        """Merge sources from all variants"""
        all_sources = set()
        for variant in variants:
            sources = variant.get("sources", [])
            all_sources.update(sources)
        return list(all_sources)

    def _merge_dependencies(self, variants: List[Dict[str, Any]]) -> List[str]:
        """Merge dependencies from all variants"""
        all_deps = set()
        for variant in variants:
            deps = variant.get("dependencies", [])
            all_deps.update(deps)
        return list(all_deps)

    def _merge_platforms(self, variants: List[Dict[str, Any]]) -> List[str]:
        """Merge platform support from all variants"""
        all_platforms = set()
        for variant in variants:
            platforms = variant.get("platform", [])
            all_platforms.update(platforms)
        return list(all_platforms)

    def _merge_usage_examples(self, variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge usage examples, removing duplicates"""
        all_examples = []
        seen_examples = set()

        for variant in variants:
            examples = variant.get("usage_examples", [])
            for example in examples:
                # Create a signature for deduplication
                example_sig = f"{example.get('title', '')}:{example.get('code', '')}"
                if example_sig not in seen_examples:
                    seen_examples.add(example_sig)
                    all_examples.append(example)

        return all_examples

    def _resolve_description_conflict(
        self,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> str:
        """Resolve description conflicts using priority"""
        # Try to find the best description
        descriptions = []

        for variant in variants:
            desc = variant.get("description", "")
            if desc and len(desc.strip()) > 10:
                sources = variant.get("sources", [])
                priority = min(source_priority.get(source, 999) for source in sources)
                descriptions.append((desc, priority))

        if not descriptions:
            return "No description available"

        # Sort by priority and return the best
        descriptions.sort(key=lambda x: x[1])
        return descriptions[0][0]

    def _resolve_installation_conflict(
        self,
        variants: List[Dict[str, Any]],
        source_priority: Dict[str, int]
    ) -> str:
        """Resolve installation command conflicts using priority"""
        installations = []

        for variant in variants:
            install = variant.get("installation", "")
            if install and len(install.strip()) > 5:
                sources = variant.get("sources", [])
                priority = min(source_priority.get(source, 999) for source in sources)
                installations.append((install, priority))

        if not installations:
            return "# Installation command not available"

        installations.sort(key=lambda x: x[1])
        return installations[0][0]

    def _calculate_merged_quality_score(self, variants: List[Dict[str, Any]]) -> float:
        """Calculate quality score for merged component"""
        if not variants:
            return 0.0

        scores = [variant.get("quality_score", 0.5) for variant in variants]

        # Use weighted average based on source completeness
        weights = []
        for variant in variants:
            weight = 0.0

            # Base weight for having core fields
            if variant.get("description"):
                weight += 0.2
            if variant.get("installation"):
                weight += 0.2
            if variant.get("usage_examples"):
                weight += 0.3
            if variant.get("dependencies"):
                weight += 0.1

            # Source diversity bonus
            sources = variant.get("sources", [])
            weight += min(0.2, len(sources) * 0.1)

            weights.append(max(0.1, weight))  # Minimum weight of 0.1

        # Calculate weighted average
        total_weight = sum(weights)
        if total_weight == 0:
            return sum(scores) / len(scores)

        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return weighted_sum / total_weight

    def _normalize_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a component to ensure all required fields are present"""
        normalized = component.copy()

        # Ensure required fields
        normalized.setdefault("sources", ["default"])
        normalized.setdefault("priority_source", normalized["sources"][0])
        normalized.setdefault("source_metadata", {})
        normalized.setdefault("dependencies", [])
        normalized.setdefault("platform", ["any"])
        normalized.setdefault("usage_examples", [])
        normalized.setdefault("quality_score", 0.5)
        normalized.setdefault("metadata", {})

        return normalized

    def apply_source_boosting(self, components: List[Dict[str, Any]], source_configs: List[SourceConfig]) -> List[Dict[str, Any]]:
        """Apply source boosting to search relevance scores"""
        if not components:
            return []

        # Create source boosting map
        source_boost = {}
        for config in source_configs:
            source_boost[config.name] = getattr(config, 'boost_factor', 1.0)

        boosted_components = []
        for component in components:
            boosted = component.copy()

            # Calculate boost factor
            boost_factor = 1.0
            sources = component.get("sources", [])

            for source in sources:
                boost_factor *= source_boost.get(source, 1.0)

            # Apply boost to relevance score
            if "relevance_score" in boosted:
                boosted["relevance_score"] *= boost_factor
            else:
                boosted["relevance_score"] = boosted.get("quality_score", 0.5) * boost_factor

            # Cap the score at 1.0
            boosted["relevance_score"] = min(1.0, boosted["relevance_score"])

            boosted_components.append(boosted)

        self.logger.debug(f"Applied source boosting to {len(components)} components")
        return boosted_components

    def calculate_quality_scores(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate or update quality scores for components"""
        scored_components = []

        for component in components:
            scored = component.copy()

            # Calculate quality score if not present
            if "quality_score" not in scored:
                scored["quality_score"] = self._calculate_component_quality_score(component)

            scored_components.append(scored)

        return scored_components

    def _calculate_component_quality_score(self, component: Dict[str, Any]) -> float:
        """Calculate quality score for a single component"""
        score = 0.0
        max_score = 1.0

        # Description quality (0.2)
        description = component.get("description", "")
        if len(description) > 100:
            score += 0.2
        elif len(description) > 50:
            score += 0.15
        elif len(description) > 20:
            score += 0.1

        # Installation command (0.1)
        if component.get("installation"):
            score += 0.1

        # Usage examples (0.2)
        examples = component.get("usage_examples", [])
        score += min(0.2, len(examples) * 0.1)

        # Dependencies (0.1)
        deps = component.get("dependencies", [])
        if deps:
            score += 0.1

        # Platform support (0.1)
        platforms = component.get("platform", [])
        if platforms and len(platforms) > 0:
            score += 0.1

        # Metadata completeness (0.2)
        metadata = component.get("metadata", {})
        metadata_fields = ["author", "license", "repository_url", "documentation_url"]
        complete_fields = sum(1 for field in metadata_fields if field in metadata)
        score += (complete_fields / len(metadata_fields)) * 0.2

        # Source diversity (0.1)
        sources = component.get("sources", [])
        score += min(0.1, len(sources) * 0.05)

        return min(score, max_score)

    def get_merge_statistics(self, original_count: int, merged_count: int) -> Dict[str, Any]:
        """Get statistics about the merge process"""
        return {
            "original_components": original_count,
            "merged_components": merged_count,
            "compression_ratio": (1 - merged_count / original_count) if original_count > 0 else 0,
            "resolution_strategy": self.resolution_strategy,
            "timestamp": datetime.now().isoformat()
        }

    def validate_merged_component(self, component: Dict[str, Any]) -> List[str]:
        """Validate a merged component"""
        errors = []

        # Required fields
        required_fields = ["name", "category", "type", "description", "installation"]
        for field in required_fields:
            if field not in component:
                errors.append(f"Missing required field: {field}")

        # Sources validation
        sources = component.get("sources", [])
        if not sources:
            errors.append("Component must have at least one source")

        priority_source = component.get("priority_source")
        if priority_source and priority_source not in sources:
            errors.append("Priority source must be in sources list")

        # Quality score validation
        quality_score = component.get("quality_score", 0.0)
        if not (0.0 <= quality_score <= 1.0):
            errors.append("Quality score must be between 0.0 and 1.0")

        return errors