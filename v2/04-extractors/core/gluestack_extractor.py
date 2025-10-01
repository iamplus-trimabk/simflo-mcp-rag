"""
⚠️  V4 IMPLEMENTATION REQUIRED ⚠️

This extractor is NOT IMPLEMENTED and must be fully implemented in v4.0 or above.
Current version uses simple extractors instead (shadcn_extractor.py, gluestack_extractor_simple.py).

Gluestack Extractor

Specialized extractor for gluestack UI components.
Handles the unique structure of gluestack's monorepo with components in packages/gluestack-core/src/
"""

import re
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .github_cli_base import GitHubCLIBaseExtractor
from .base_extractor import ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, HookSignature, SourceMetadata

logger = logging.getLogger(__name__)

class GluestackExtractor(GitHubCLIBaseExtractor):
    """Specialized extractor for gluestack UI components"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.registry_file = source_config.get("registry_file", "")

    def validate_source(self) -> bool:
        """Validate source configuration for this extractor"""
        if not super().validate_source():
            return False

        # Validate GitHub URL format
        url = self.source_config["url"]
        if not url.startswith("https://github.com/gluestack/gluestack-ui"):
            logger.error(f"Invalid gluestack GitHub URL: {url}")
            return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return ["component"]

    async def extract(self) -> ExtractionResult:
        """Extract components from gluestack repository"""
        self.logger.info(f"🚀 Starting component extraction from {self.name}")

        errors = []
        warnings = []
        components = []

        try:
            # Get all available components
            component_configs = self._discover_components()
            self.logger.info(f"Found {len(component_configs)} component configurations")

            # Process each component configuration
            for component_config in component_configs:
                try:
                    component = await self._process_component_config(component_config)
                    if component:
                        components.append(component)
                except Exception as e:
                    logger.warning(f"Failed to process component config {component_config.get('name', 'unknown')}: {e}")
                    warnings.append(f"Failed to process {component_config.get('name', 'unknown')}: {e}")

            # Calculate extraction time
            extraction_time = 0.0  # TODO: Track actual time

            self.logger.info(f"✅ Successfully extracted {len(components)} components")

            return ExtractionResult(
                success=True,
                data=[component.to_dict() for component in components],
                metadata={
                    "total_components": len(components),
                    "repository_info": self.repo_info,
                    "extraction_method": "github_cli_local"
                },
                errors=errors,
                warnings=warnings,
                extraction_time=extraction_time,
                source_info=self.source_config
            )

        except Exception as e:
            logger.error(f"❌ Component extraction failed: {e}")
            errors.append(f"Extraction failed: {str(e)}")
            return ExtractionResult(
                success=False,
                data=[],
                metadata={},
                errors=errors,
                warnings=warnings,
                extraction_time=0.0,
                source_info=self.source_config
            )

    def _discover_components(self) -> List[Dict[str, Any]]:
        """Discover all available components in gluestack repository"""
        components = []

        # Look for component directories in packages/gluestack-core/src/
        component_dirs = self._find_component_directories()

        for component_name in component_dirs:
            component_info = {
                "name": component_name,
                "files": self._find_component_files(component_name),
                "type": "component"
            }
            components.append(component_info)

        return components

    def _find_component_directories(self) -> List[str]:
        """Find all component directories in the gluestack repository"""
        components = []

        # Look for directories in packages/gluestack-core/src/
        core_src_path = "packages/gluestack-core/src"

        # Check if the directory exists
        if self._read_local_file(core_src_path):
            # Get directory listing by looking for common component files
            patterns = [
                f"{core_src_path}/*/creator/index.tsx",
                f"{core_src_path}/*/creator/index.ts",
                f"{core_src_path}/*/index.tsx",
                f"{core_src_path}/*/index.ts"
            ]

            component_names = set()
            for pattern in patterns:
                # Try to find files matching the pattern
                files = self._find_files_by_pattern(pattern)
                for file_path in files:
                    # Extract component name from path
                    relative_path = str(file_path.relative_to(self.repo_path))
                    if "/" in relative_path:
                        component_name = relative_path.split("/")[3]  # packages/gluestack-core/src/{component_name}/...
                        if component_name and component_name not in ["src", ""]:
                            component_names.add(component_name)

            components = sorted(list(component_names))

        # Add known gluestack components
        known_components = [
            "accordion", "actionsheet", "alert", "alert-dialog", "avatar", "button",
            "checkbox", "divider", "fab", "form-control", "icon", "image", "input",
            "link", "menu", "modal", "overlay", "popover", "pressable", "progress",
            "radio", "select", "slider", "spinner", "switch", "textarea", "toast", "tooltip"
        ]

        # Merge discovered and known components
        all_components = list(set(components + known_components))
        all_components.sort()

        return all_components

    def _find_files_by_pattern(self, pattern: str) -> List[Path]:
        """Find files matching a pattern in the cloned repository"""
        found_files = []

        try:
            # Convert glob pattern to path and find matching files
            # This is a simplified implementation - in practice, you might want to use glob
            path_parts = pattern.split("/")
            current_path = self.repo_path

            for part in path_parts[:-1]:
                if part == "*":
                    # Handle wildcard
                    if current_path.exists() and current_path.is_dir():
                        for item in current_path.iterdir():
                            if item.is_dir() and not item.name.startswith("."):
                                # Try to find the file in this directory
                                test_path = item / path_parts[-1]
                                if test_path.exists():
                                    found_files.append(test_path)
                    return found_files
                else:
                    current_path = current_path / part
                    if not current_path.exists():
                        break

            if current_path.exists():
                final_file = current_path / path_parts[-1]
                if final_file.exists():
                    found_files.append(final_file)

        except Exception as e:
            self.logger.warning(f"Error finding files with pattern {pattern}: {e}")

        return found_files

    def _find_component_files(self, component_name: str) -> List[str]:
        """Find implementation files for a component"""
        files = []

        # Look for different file patterns
        patterns = [
            f"packages/gluestack-core/src/{component_name}/creator/index.tsx",
            f"packages/gluestack-core/src/{component_name}/creator/index.ts",
            f"packages/gluestack-core/src/{component_name}/index.tsx",
            f"packages/gluestack-core/src/{component_name}/index.ts",
            f"packages/gluestack-core/src/{component_name}/creator/*.tsx",
            f"packages/gluestack-core/src/{component_name}/creator/*.ts",
        ]

        for pattern in patterns:
            found_files = self._find_files_by_pattern(pattern)
            for file_path in found_files:
                files.append(str(file_path.relative_to(self.repo_path)))

        return list(set(files))  # Remove duplicates

    async def _process_component_config(self, component_config: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Process a single component configuration into an ExtractedComponent"""
        try:
            component_name = component_config.get("name", "")
            if not component_name:
                return None

            # Get component files
            component_files = component_config.get("files", [])
            if not component_files:
                self.logger.warning(f"No implementation files found for component: {component_name}")
                return None

            # Extract component metadata
            metadata = self._extract_component_metadata(component_name, component_files)
            dependencies = self._extract_dependencies(component_files)

            # Generate installation command
            install_cmd = self._generate_install_command(component_name, dependencies)

            # Create component
            component = ExtractedComponent(
                name=component_name,
                category="components",
                type="component",
                sources=[self.repo_url],
                priority_source=self.repo_url,
                description=metadata.get("description", f"Gluestack UI component: {component_name}"),
                dependencies=dependencies,
                peer_dependencies=metadata.get("peer_dependencies", []),
                installation=install_cmd,
                usage_examples=metadata.get("usage_examples", []),
                metadata={
                    "files": component_files,
                    "component_type": metadata.get("component_type", "ui"),
                    "repository": self.repo_info,
                    "exports": metadata.get("exports", [])
                },
                quality_score=self._calculate_quality_score(component_config, component_files),
                last_updated=datetime.now(),
                platform=["reactjs", "react-native"],
                registry="gluestack"
            )

            return component

        except Exception as e:
            self.logger.error(f"Failed to process component config {component_config.get('name', 'unknown')}: {e}")
            return None

    def _extract_component_metadata(self, component_name: str, component_files: List[str]) -> Dict[str, Any]:
        """Extract metadata from component files"""
        metadata = {
            "description": f"Gluestack UI {component_name} component",
            "peer_dependencies": [],
            "usage_examples": [],
            "component_type": "ui",
            "exports": []
        }

        for file_path in component_files:
            content = self._read_local_file(file_path)
            if content:
                # Extract exports
                export_pattern = r'export\s+(?:const|function|class|default)\s+(\w+)'
                export_matches = re.findall(export_pattern, content)
                metadata["exports"].extend(export_matches)

                # Extract description from comments
                comment_patterns = [
                    r'/\*\*[\s\S]*?\*/',
                    r'//.*'
                ]

                for pattern in comment_patterns:
                    comments = re.findall(pattern, content)
                    for comment in comments:
                        if "description" in comment.lower() or component_name.lower() in comment.lower():
                            # Use comment as description if it's meaningful
                            clean_comment = re.sub(r'/\*\*|\*/|//', '', comment).strip()
                            if len(clean_comment) > 10 and len(clean_comment) < 200:
                                metadata["description"] = clean_comment
                                break

        # Remove duplicate exports
        metadata["exports"] = list(set(metadata["exports"]))

        return metadata

    def _extract_dependencies(self, component_files: List[str]) -> List[str]:
        """Extract dependencies from component files"""
        dependencies = set()

        for file_path in component_files:
            content = self._read_local_file(file_path)
            if content:
                # Look for import statements
                import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
                matches = re.findall(import_pattern, content)
                for match in matches:
                    if not match.startswith('.') and not match.startswith('/'):
                        dependencies.add(match)

        return list(dependencies)

    def _generate_install_command(self, component_name: str, dependencies: List[str]) -> str:
        """Generate installation command for the component"""
        base_deps = ["@gluestack-ui/themed", "@gluestack-style/react"]

        if dependencies:
            all_deps = base_deps + dependencies
            deps_str = " ".join(list(set(all_deps)))
            return f"npm install {deps_str}"
        else:
            return f"npm install @gluestack-ui/themed @gluestack-style/react"

    def _calculate_quality_score(self, component_config: Dict[str, Any], component_files: List[str]) -> float:
        """Calculate quality score for the component"""
        score = 0.6  # Base score for gluestack components

        # Bonus for having implementation files
        if component_files:
            score += 0.2

        # Bonus for multiple files (indicates comprehensive implementation)
        if len(component_files) > 1:
            score += 0.1

        # Bonus for exports (indicates proper API)
        total_exports = sum(len(self._extract_component_metadata("", component_files).get("exports", [])) for _ in [1])
        if total_exports > 0:
            score += 0.1

        return min(score, 1.0)

    async def validate_repository(self) -> bool:
        """Validate repository accessibility and structure"""
        try:
            # Test repository access
            repo_info = self._parse_repo_identifier()
            self.logger.info(f"Validating repository: {repo_info['owner']}/{repo_info['repo']}")

            # Check if GitHub CLI can access the repository
            result = subprocess.run(
                ['gh', 'repo', 'view', f"{repo_info['owner']}/{repo_info['repo']}"],
                capture_output=True,
                text=True
            )

            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Repository validation failed: {e}")
            return False