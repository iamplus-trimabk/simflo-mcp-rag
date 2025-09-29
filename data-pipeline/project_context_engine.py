#!/usr/bin/env python3
"""
Enhanced Project Context Engine

Intelligent project type detection and context-aware search enhancement system.
"""

import json
import logging
import re
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
from collections import defaultdict


class ProjectType(Enum):
    """Supported project types with detailed characteristics"""
    REACT_WEB = "react_web"
    REACT_NATIVE = "react_native"
    NEXT_JS = "next_js"
    VITE_REACT = "vite_react"
    EXPO = "expo"
    NATIVEWIND = "nativewind"
    GLUESTACK_UI = "gluestack_ui"
    SHADCN_UI = "shadcn_ui"
    VANILLA_REACT = "vanilla_react"
    CUSTOM_COMPONENT_LIB = "custom_component_lib"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    HYBRID_APP = "hybrid_app"
    DESIGN_SYSTEM = "design_system"
    UNKNOWN = "unknown"


@dataclass
class ProjectCharacteristics:
    """Characteristics that define a project type"""
    frameworks: List[str]
    platforms: List[str]
    ui_libraries: List[str]
    build_tools: List[str]
    file_patterns: List[str]
    dependencies: List[str]
    keywords: List[str]
    score_threshold: float = 0.5


@dataclass
class ProjectContext:
    """Enhanced project context with detailed information"""
    project_type: ProjectType
    confidence: float
    characteristics: Dict[str, Any]
    detected_from: List[str]
    timestamp: float
    session_id: str
    user_agent: Optional[str] = None


@dataclass
class ContextualSearchResult:
    """Search result enhanced with project context"""
    original_result: Dict[str, Any]
    context_boost: float
    relevance_explanation: List[str]
    project_type_match: float
    platform_alignment: float
    library_compatibility: float
    final_context_score: float


class ProjectContextEngine:
    """Enhanced project context detection and search enhancement engine"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the project context engine"""
        self.config_path = config_path or "config/project_context_config.json"
        self.current_context: Optional[ProjectContext] = None
        self.context_history: List[ProjectContext] = []
        self.session_counter = 0
        self.lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize project type definitions
        self.project_definitions = self._initialize_project_definitions()

        # Load configuration
        self.load_config()

    def _initialize_project_definitions(self) -> Dict[ProjectType, ProjectCharacteristics]:
        """Initialize project type definitions with characteristics"""
        return {
            ProjectType.REACT_WEB: ProjectCharacteristics(
                frameworks=["react"],
                platforms=["web"],
                ui_libraries=["shadcn", "tailwind", "styled-components"],
                build_tools=["webpack", "vite", "create-react-app"],
                file_patterns=["*.jsx", "*.tsx", "public/index.html"],
                dependencies=["react", "react-dom"],
                keywords=["web", "browser", "dom", "jsx", "tsx"],
                score_threshold=0.3
            ),
            ProjectType.REACT_NATIVE: ProjectCharacteristics(
                frameworks=["react-native"],
                platforms=["ios", "android"],
                ui_libraries=["nativewind", "gluestack", "react-native-paper"],
                build_tools=["expo", "react-native-cli", "eas-build"],
                file_patterns=["*.js", "*.ts", "*.jsx", "*.tsx", "App.js", "App.tsx"],
                dependencies=["react-native"],
                keywords=["mobile", "ios", "android", "native", "touchable"],
                score_threshold=0.3
            ),
            ProjectType.NEXT_JS: ProjectCharacteristics(
                frameworks=["next"],
                platforms=["web"],
                ui_libraries=["shadcn", "tailwind"],
                build_tools=["next", "vercel"],
                file_patterns=["pages/**/*.tsx", "pages/**/*.jsx", "next.config.*"],
                dependencies=["next", "nextjs"],
                keywords=["next", "ssr", "ssg", "vercel", "app router"],
                score_threshold=0.4
            ),
            ProjectType.VITE_REACT: ProjectCharacteristics(
                frameworks=["react", "vite"],
                platforms=["web"],
                ui_libraries=["shadcn", "tailwind"],
                build_tools=["vite"],
                file_patterns=["vite.config.*", "*.jsx", "*.tsx"],
                dependencies=["react", "vite"],
                keywords=["vite", "fast", "hmr", "bundling"],
                score_threshold=0.4
            ),
            ProjectType.EXPO: ProjectCharacteristics(
                frameworks=["expo", "react-native"],
                platforms=["ios", "android", "web"],
                ui_libraries=["nativewind", "gluestack"],
                build_tools=["expo", "eas"],
                file_patterns=["app.json", "babel.config.*", "*.js", "*.ts"],
                dependencies=["expo", "expo-*"],
                keywords=["expo", "managed", "eas", "ota"],
                score_threshold=0.5
            ),
            ProjectType.NATIVEWIND: ProjectCharacteristics(
                frameworks=["react-native"],
                platforms=["ios", "android"],
                ui_libraries=["nativewind"],
                build_tools=["expo", "react-native-cli"],
                file_patterns=["nativewind.config.*", "*.js", "*.ts"],
                dependencies=["nativewind"],
                keywords=["nativewind", "tailwind", "native", "css"],
                score_threshold=0.6
            ),
            ProjectType.GLUESTACK_UI: ProjectCharacteristics(
                frameworks=["react", "react-native"],
                platforms=["web", "ios", "android"],
                ui_libraries=["gluestack"],
                build_tools=["expo", "vite", "next"],
                file_patterns=["gluestack.config.*", "*.js", "*.ts"],
                dependencies=["@gluestack-ui/*"],
                keywords=["gluestack", "universal", "cross-platform"],
                score_threshold=0.6
            ),
            ProjectType.SHADCN_UI: ProjectCharacteristics(
                frameworks=["react", "next"],
                platforms=["web"],
                ui_libraries=["shadcn"],
                build_tools=["next", "vite"],
                file_patterns=["components.json", "components/ui/*", "*.tsx"],
                dependencies=["@radix-ui/*", "class-variance-authority"],
                keywords=["shadcn", "radix", "accessibility", "components"],
                score_threshold=0.6
            ),
            ProjectType.DESIGN_SYSTEM: ProjectCharacteristics(
                frameworks=["react", "react-native"],
                platforms=["web", "ios", "android"],
                ui_libraries=["custom"],
                build_tools=["storybook", "custom"],
                file_patterns=["*.story.*", "tokens/**/*.ts", "components/**/*.ts"],
                dependencies=["storybook", "@storybook/*"],
                keywords=["design system", "tokens", "storybook", "components"],
                score_threshold=0.5
            ),
            ProjectType.CUSTOM_COMPONENT_LIB: ProjectCharacteristics(
                frameworks=["react", "react-native"],
                platforms=["web", "ios", "android"],
                ui_libraries=["custom"],
                build_tools=["rollup", "typescript"],
                file_patterns=["src/components/*", "index.ts", "package.json"],
                dependencies=["react", "typescript"],
                keywords=["component library", "npm package", "ui kit"],
                score_threshold=0.4
            )
        }

    def load_config(self):
        """Load project context configuration from file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Override default definitions if provided
                    if "project_definitions" in config:
                        self.project_definitions.update(
                            self._parse_project_definitions(config["project_definitions"])
                        )
                    self.logger.info("Project context configuration loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load project context config: {e}")

    def _parse_project_definitions(self, config_definitions: Dict[str, Any]) -> Dict[ProjectType, ProjectCharacteristics]:
        """Parse project definitions from configuration"""
        definitions = {}
        for project_type_str, characteristics in config_definitions.items():
            try:
                project_type = ProjectType(project_type_str)
                definitions[project_type] = ProjectCharacteristics(**characteristics)
            except ValueError:
                self.logger.warning(f"Unknown project type in config: {project_type_str}")
        return definitions

    def detect_project_type_from_files(self, file_list: List[str]) -> Tuple[ProjectType, float, List[str]]:
        """Detect project type from file patterns and content"""
        scores = defaultdict(float)
        evidence = defaultdict(list)

        # Convert file list to lowercase for pattern matching
        file_paths_lower = [f.lower() for f in file_list]

        for project_type, definition in self.project_definitions.items():
            score = 0.0
            detected_evidence = []

            # Check file patterns
            for pattern in definition.file_patterns:
                pattern_matches = sum(1 for file_path in file_paths_lower if pattern in file_path)
                if pattern_matches > 0:
                    score += 0.3
                    detected_evidence.append(f"File pattern match: {pattern}")

            # Check dependencies (if package.json content is available)
            for dep in definition.dependencies:
                dep_matches = sum(1 for file_path in file_paths_lower if dep in file_path)
                if dep_matches > 0:
                    score += 0.4
                    detected_evidence.append(f"Dependency detected: {dep}")

            # Check keywords in file paths
            for keyword in definition.keywords:
                keyword_matches = sum(1 for file_path in file_paths_lower if keyword in file_path)
                if keyword_matches > 0:
                    score += 0.2
                    detected_evidence.append(f"Keyword match: {keyword}")

            scores[project_type] = score
            evidence[project_type] = detected_evidence

        # Find the best match
        if not scores:
            return ProjectType.UNKNOWN, 0.0, []

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        best_evidence = evidence[best_type]

        # Check if score meets threshold
        if best_score >= self.project_definitions[best_type].score_threshold:
            return best_type, best_score, best_evidence
        else:
            return ProjectType.UNKNOWN, best_score, best_evidence

    def detect_project_type_from_query(self, query: str) -> Tuple[ProjectType, float, List[str]]:
        """Detect project type from natural language query"""
        query_lower = query.lower()
        scores = defaultdict(float)
        evidence = defaultdict(list)

        for project_type, definition in self.project_definitions.items():
            score = 0.0
            detected_evidence = []

            # Check keyword matches in query
            for keyword in definition.keywords:
                if keyword in query_lower:
                    score += 0.5
                    detected_evidence.append(f"Keyword in query: {keyword}")

            # Check framework mentions
            for framework in definition.frameworks:
                if framework in query_lower:
                    score += 0.4
                    detected_evidence.append(f"Framework mentioned: {framework}")

            # Check UI library mentions
            for ui_lib in definition.ui_libraries:
                if ui_lib in query_lower:
                    score += 0.6
                    detected_evidence.append(f"UI library mentioned: {ui_lib}")

            # Check platform mentions
            for platform in definition.platforms:
                if platform in query_lower:
                    score += 0.3
                    detected_evidence.append(f"Platform mentioned: {platform}")

            scores[project_type] = score
            evidence[project_type] = detected_evidence

        # Find the best match
        if not scores:
            return ProjectType.UNKNOWN, 0.0, []

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        best_evidence = evidence[best_type]

        # Check if score meets threshold
        if best_score >= self.project_definitions[best_type].score_threshold:
            return best_type, best_score, best_evidence
        else:
            return ProjectType.UNKNOWN, best_score, best_evidence

    def detect_project_type_from_package_json(self, package_json: Dict[str, Any]) -> Tuple[ProjectType, float, List[str]]:
        """Detect project type from package.json content"""
        scores = defaultdict(float)
        evidence = defaultdict(list)

        dependencies = {
            **package_json.get("dependencies", {}),
            **package_json.get("devDependencies", {})
        }

        for project_type, definition in self.project_definitions.items():
            score = 0.0
            detected_evidence = []

            # Check direct dependencies
            for dep in definition.dependencies:
                if dep in dependencies:
                    score += 0.6
                    detected_evidence.append(f"Dependency found: {dep}")

            # Check UI library dependencies
            for ui_lib in definition.ui_libraries:
                # Check for common package patterns
                ui_dep_patterns = [
                    ui_lib,
                    f"@{ui_lib}/*",
                    f"{ui_lib}-*",
                    f"react-{ui_lib}",
                    f"native-{ui_lib}"
                ]
                for pattern in ui_dep_patterns:
                    matches = [dep for dep in dependencies.keys() if pattern in dep]
                    if matches:
                        score += 0.5
                        detected_evidence.append(f"UI library detected: {matches[0]}")

            # Check build tools
            for build_tool in definition.build_tools:
                build_tool_patterns = [
                    build_tool,
                    f"{build_tool}-*",
                    f"@{build_tool}/*"
                ]
                for pattern in build_tool_patterns:
                    matches = [dep for dep in dependencies.keys() if pattern in dep]
                    if matches:
                        score += 0.4
                        detected_evidence.append(f"Build tool detected: {matches[0]}")

            scores[project_type] = score
            evidence[project_type] = detected_evidence

        # Find the best match
        if not scores:
            return ProjectType.UNKNOWN, 0.0, []

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        best_evidence = evidence[best_type]

        # Check if score meets threshold
        if best_score >= self.project_definitions[best_type].score_threshold:
            return best_type, best_score, best_evidence
        else:
            return ProjectType.UNKNOWN, best_score, best_evidence

    def detect_project_type(
        self,
        query: Optional[str] = None,
        file_list: Optional[List[str]] = None,
        package_json: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> ProjectContext:
        """Comprehensive project type detection from multiple sources"""
        with self.lock:
            scores = defaultdict(float)
            all_evidence = defaultdict(list)
            detection_sources = []

            # Generate session ID if not provided
            if not session_id:
                self.session_counter += 1
                session_id = f"session_{self.session_counter}_{int(time.time())}"

            # Detection from query
            if query:
                query_type, query_score, query_evidence = self.detect_project_type_from_query(query)
                scores[query_type] += query_score
                all_evidence[query_type].extend(query_evidence)
                detection_sources.append("query")

            # Detection from files
            if file_list:
                file_type, file_score, file_evidence = self.detect_project_type_from_files(file_list)
                scores[file_type] += file_score
                all_evidence[file_type].extend(file_evidence)
                detection_sources.append("files")

            # Detection from package.json
            if package_json:
                pkg_type, pkg_score, pkg_evidence = self.detect_project_type_from_package_json(package_json)
                scores[pkg_type] += pkg_score
                all_evidence[pkg_type].extend(pkg_evidence)
                detection_sources.append("package.json")

            # Find the best match
            if not scores:
                best_type = ProjectType.UNKNOWN
                best_score = 0.0
                best_evidence = []
            else:
                best_type = max(scores, key=scores.get)
                best_score = scores[best_type]
                best_evidence = all_evidence[best_type]

            # Normalize score to 0-1 range
            max_possible_score = len(detection_sources) if detection_sources else 1
            confidence = min(best_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0

            # Create project context
            context = ProjectContext(
                project_type=best_type,
                confidence=confidence,
                characteristics=self._get_project_characteristics(best_type),
                detected_from=detection_sources,
                timestamp=time.time(),
                session_id=session_id
            )

            # Update current context and history
            if self.current_context:
                self.context_history.append(self.current_context)

            self.current_context = context

            # Keep history manageable
            if len(self.context_history) > 50:
                self.context_history = self.context_history[-50:]

            self.logger.info(f"Detected project type: {best_type.value} with confidence {confidence:.2f}")
            return context

    def _get_project_characteristics(self, project_type: ProjectType) -> Dict[str, Any]:
        """Get characteristics for a project type"""
        if project_type in self.project_definitions:
            definition = self.project_definitions[project_type]
            return {
                "frameworks": definition.frameworks,
                "platforms": definition.platforms,
                "ui_libraries": definition.ui_libraries,
                "build_tools": definition.build_tools,
                "score_threshold": definition.score_threshold
            }
        return {}

    def enhance_search_results(
        self,
        search_results: List[Dict[str, Any]],
        query: str
    ) -> List[ContextualSearchResult]:
        """Enhance search results with project context awareness"""
        if not self.current_context or self.current_context.project_type == ProjectType.UNKNOWN:
            # No context available, return results as-is
            return [
                ContextualSearchResult(
                    original_result=result,
                    context_boost=1.0,
                    relevance_explanation=["No project context available"],
                    project_type_match=0.0,
                    platform_alignment=0.0,
                    library_compatibility=0.0,
                    final_context_score=1.0
                )
                for result in search_results
            ]

        enhanced_results = []
        project_type = self.current_context.project_type
        characteristics = self.current_context.characteristics

        for result in search_results:
            # Calculate various compatibility scores
            project_type_match = self._calculate_project_type_match(result, project_type)
            platform_alignment = self._calculate_platform_alignment(result, characteristics.get("platforms", []))
            library_compatibility = self._calculate_library_compatibility(result, characteristics.get("ui_libraries", []))

            # Calculate overall context boost
            context_boost = self._calculate_context_boost(
                project_type_match,
                platform_alignment,
                library_compatibility
            )

            # Generate relevance explanation
            explanation = self._generate_relevance_explanation(
                result,
                project_type_match,
                platform_alignment,
                library_compatibility,
                project_type
            )

            # Create contextual result
            contextual_result = ContextualSearchResult(
                original_result=result,
                context_boost=context_boost,
                relevance_explanation=explanation,
                project_type_match=project_type_match,
                platform_alignment=platform_alignment,
                library_compatibility=library_compatibility,
                final_context_score=project_type_match * 0.4 + platform_alignment * 0.3 + library_compatibility * 0.3
            )

            enhanced_results.append(contextual_result)

        # Sort by final context score
        enhanced_results.sort(key=lambda x: x.final_context_score, reverse=True)
        return enhanced_results

    def _calculate_project_type_match(self, result: Dict[str, Any], project_type: ProjectType) -> float:
        """Calculate how well a result matches the current project type"""
        result_registry = result.get("registry", "")
        result_platforms = result.get("platform", [])
        result_type = result.get("type", "")

        score = 0.0

        # Registry-specific matching
        if project_type == ProjectType.GLUESTACK_UI and "gluestack" in result_registry:
            score += 1.0
        elif project_type == ProjectType.SHADCN_UI and "shadcn" in result_registry:
            score += 1.0
        elif project_type == ProjectType.REACT_NATIVE and "gluestack" in result_registry:
            score += 0.8
        elif project_type == ProjectType.REACT_WEB and "shadcn" in result_registry:
            score += 0.8

        # Platform alignment
        if project_type in [ProjectType.REACT_NATIVE, ProjectType.EXPO] and "react-native" in result_platforms:
            score += 0.6
        elif project_type in [ProjectType.REACT_WEB, ProjectType.NEXT_JS, ProjectType.VITE_REACT] and "web" in result_platforms:
            score += 0.6

        return min(score, 1.0)

    def _calculate_platform_alignment(self, result: Dict[str, Any], project_platforms: List[str]) -> float:
        """Calculate platform alignment between result and project"""
        result_platforms = result.get("platform", [])
        if not project_platforms or not result_platforms:
            return 0.5

        # Calculate overlap between project platforms and result platforms
        overlap = set(project_platforms) & set(result_platforms)
        if not overlap:
            return 0.0

        return len(overlap) / max(len(project_platforms), len(result_platforms))

    def _calculate_library_compatibility(self, result: Dict[str, Any], project_libraries: List[str]) -> float:
        """Calculate UI library compatibility"""
        result_registry = result.get("registry", "").lower()
        result_type = result.get("type", "").lower()

        if not project_libraries:
            return 0.5

        for lib in project_libraries:
            if lib in result_registry or lib in result_type:
                return 1.0

        return 0.0

    def _calculate_context_boost(self, project_type_match: float, platform_alignment: float, library_compatibility: float) -> float:
        """Calculate overall context boost factor"""
        base_score = project_type_match * 0.4 + platform_alignment * 0.3 + library_compatibility * 0.3

        # Apply boost factor (1.0 to 2.0 range)
        return 1.0 + base_score

    def _generate_relevance_explanation(
        self,
        result: Dict[str, Any],
        project_type_match: float,
        platform_alignment: float,
        library_compatibility: float,
        project_type: ProjectType
    ) -> List[str]:
        """Generate human-readable relevance explanation"""
        explanation = []

        if project_type_match > 0.7:
            explanation.append(f"Excellent match for {project_type.value} project")
        elif project_type_match > 0.4:
            explanation.append(f"Good match for {project_type.value} project")

        if platform_alignment > 0.7:
            explanation.append("Perfect platform alignment")
        elif platform_alignment > 0.4:
            explanation.append("Good platform alignment")

        if library_compatibility > 0.7:
            explanation.append("Compatible UI library")
        elif library_compatibility > 0.4:
            explanation.append("Acceptable library compatibility")

        if not explanation:
            explanation.append("Basic relevance match")

        return explanation

    def get_project_type_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get project type suggestions based on query"""
        suggestions = []

        for project_type, definition in self.project_definitions.items():
            relevance_score = 0.0
            matched_keywords = []

            query_lower = query.lower()

            # Check keyword matches
            for keyword in definition.keywords:
                if keyword in query_lower:
                    relevance_score += 0.3
                    matched_keywords.append(keyword)

            # Check framework matches
            for framework in definition.frameworks:
                if framework in query_lower:
                    relevance_score += 0.4
                    matched_keywords.append(framework)

            # Check UI library matches
            for ui_lib in definition.ui_libraries:
                if ui_lib in query_lower:
                    relevance_score += 0.5
                    matched_keywords.append(ui_lib)

            if relevance_score > 0.1:
                suggestions.append({
                    "project_type": project_type.value,
                    "relevance_score": relevance_score,
                    "matched_keywords": matched_keywords,
                    "description": f"{project_type.value.replace('_', ' ').title()} project",
                    "frameworks": definition.frameworks,
                    "platforms": definition.platforms,
                    "ui_libraries": definition.ui_libraries
                })

        # Sort by relevance score
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions

    def get_context_stats(self) -> Dict[str, Any]:
        """Get context engine statistics"""
        with self.lock:
            project_type_counts = defaultdict(int)
            for context in self.context_history + ([self.current_context] if self.current_context else []):
                if context:
                    project_type_counts[context.project_type.value] += 1

            return {
                "total_sessions": self.session_counter,
                "current_project_type": self.current_context.project_type.value if self.current_context else "unknown",
                "current_confidence": self.current_context.confidence if self.current_context else 0.0,
                "project_type_distribution": dict(project_type_counts),
                "history_size": len(self.context_history),
                "available_project_types": list(self.project_definitions.keys()),
                "detection_sources": {
                    type_name: sum(1 for ctx in self.context_history if type_name in ctx.detected_from)
                    for type_name in ["query", "files", "package.json"]
                }
            }

    def export_context(self, format: str = "json") -> str:
        """Export current context configuration"""
        data = {
            "current_context": asdict(self.current_context) if self.current_context else None,
            "project_definitions": {
                project_type.value: asdict(definition)
                for project_type, definition in self.project_definitions.items()
            },
            "stats": self.get_context_stats()
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global context engine instance
_context_engine = None

def get_project_context_engine() -> ProjectContextEngine:
    """Get global project context engine instance"""
    global _context_engine
    if _context_engine is None:
        _context_engine = ProjectContextEngine()
    return _context_engine


# Convenience functions
def detect_project_type(
    query: Optional[str] = None,
    file_list: Optional[List[str]] = None,
    package_json: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> ProjectContext:
    """Convenience function to detect project type"""
    engine = get_project_context_engine()
    return engine.detect_project_type(query, file_list, package_json, session_id)

def enhance_search_with_context(
    search_results: List[Dict[str, Any]],
    query: str
) -> List[ContextualSearchResult]:
    """Convenience function to enhance search results with context"""
    engine = get_project_context_engine()
    return engine.enhance_search_results(search_results, query)

def get_project_type_suggestions(query: str) -> List[Dict[str, Any]]:
    """Convenience function to get project type suggestions"""
    engine = get_project_context_engine()
    return engine.get_project_type_suggestions(query)


if __name__ == "__main__":
    # Test the project context engine
    engine = ProjectContextEngine()

    # Test query-based detection
    context = engine.detect_project_type(
        query="I'm building a mobile app with React Native and Gluestack UI"
    )
    print(f"Detected project type: {context.project_type.value} with confidence {context.confidence:.2f}")

    # Test file-based detection
    files = ["App.tsx", "package.json", "components/Button.tsx", "nativewind.config.js"]
    context2 = engine.detect_project_type(file_list=files)
    print(f"Detected from files: {context2.project_type.value} with confidence {context2.confidence:.2f}")

    # Test suggestions
    suggestions = engine.get_project_type_suggestions("I need a button component for my Next.js app")
    print("Project type suggestions:")
    for suggestion in suggestions:
        print(f"  {suggestion['project_type']}: {suggestion['relevance_score']:.2f}")