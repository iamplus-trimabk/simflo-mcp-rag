"""
⚠️  V4 IMPLEMENTATION REQUIRED ⚠️

This extractor is NOT IMPLEMENTED and must be fully implemented in v4.0 or above.
Current version uses simple extractors instead (shadcn_extractor.py, gluestack_extractor_simple.py).

Shadcn Components Extractor

Specialized extractor for shadcn UI components from the shadcn-ui/ui repository.
Handles components like button, input, card, etc. from the registry.
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

class ShadcnComponentsExtractor(GitHubCLIBaseExtractor):
    """Specialized extractor for shadcn UI components"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.registry_file = source_config.get("registry_file", "")

    def validate_source(self) -> bool:
        """Validate source configuration for this extractor"""
        if not super().validate_source():
            return False

        # Validate GitHub URL format
        url = self.source_config["url"]
        if not (url.startswith("https://github.com/shadcn-ui/") or url.startswith("https://github.com/shadcn/")):
            logger.error(f"Invalid shadcn GitHub URL: {url}")
            return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return ["component"]

    async def extract(self) -> ExtractionResult:
        """Extract components from shadcn registry"""
        self.logger.info(f"🚀 Starting component extraction from {self.name}")

        errors = []
        warnings = []
        components = []

        try:
            # Read registry file locally
            registry_content = self._read_local_file(self.registry_file)
            if not registry_content:
                errors.append("Failed to read registry file")
                return ExtractionResult(
                    success=False,
                    data=[],
                    metadata={},
                    errors=errors,
                    warnings=warnings,
                    extraction_time=0.0,
                    source_info=self.source_config
                )

            self.logger.info(f"Successfully read registry file ({len(registry_content)} characters)")

            # Parse registry content
            component_configs = self._parse_registry(registry_content)
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

    def _parse_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse the registry file to extract component configurations"""
        components = []

        try:
            # Try to parse as JSON first
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    components.extend(data)
                elif isinstance(data, dict):
                    if "components" in data:
                        components.extend(data["components"])
                    elif "ui" in data:
                        components.extend(data["ui"])
            else:
                # Parse as TypeScript/JavaScript registry
                components.extend(self._parse_ts_registry(content))

        except json.JSONDecodeError:
            # Fallback to TypeScript parsing
            try:
                components.extend(self._parse_ts_registry(content))
            except Exception as e:
                self.logger.error(f"Failed to parse registry content: {e}")
                return []

        # Filter for components only (not hooks or blocks)
        ui_components = []
        for component in components:
            name = component.get("name", "")
            component_type = component.get("type", "")

            # Include UI components but exclude hooks and blocks
            if (self._is_component_name(name) and
                component_type in ["registry:ui", "registry:component", ""]):
                ui_components.append(component)

        self.logger.info(f"Parsed {len(ui_components)} UI component configurations from registry")
        return ui_components

    def _parse_ts_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse TypeScript registry file format for UI components"""
        components = []

        # Parse shadcn registry format: "component-name": { name: "component-name", type: "registry:ui", files: [...] }
        component_pattern = r'"([^"]+)":\s*\{\s*name:\s*["\'][^"\']*["\'][^}]*type:\s*["\']registry:(ui|component)["\'][^}]*files:\s*\[\s*\{\s*path:\s*["\']([^"\']+)["\'][^}]*\}\s*\]'

        matches = re.finditer(component_pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            component_name = match.group(1)
            component_type = match.group(2)
            file_path = match.group(3)

            # Skip hooks and blocks
            if self._is_hook_name(component_name) or "block" in component_name.lower():
                continue

            component_config = {
                "name": component_name,
                "files": [file_path],
                "type": f"registry:{component_type}"
            }
            components.append(component_config)

        return components

    def _is_component_name(self, name: str) -> bool:
        """Check if a name is a UI component (not a hook or block)"""
        # Exclude hooks and blocks
        if self._is_hook_name(name):
            return False

        # Exclude obvious blocks
        block_indicators = ["block", "dashboard", "card", "section", "layout"]
        if any(indicator in name.lower() for indicator in block_indicators):
            return False

        # Common UI component patterns
        ui_patterns = [
            "button", "input", "card", "dialog", "alert", "avatar", "badge",
            "breadcrumb", "calendar", "carousel", "checkbox", "combobox", "command",
            "context-menu", "data-table", "date-picker", "dropdown", "form", "hover-card",
            "input-otp", "label", "menubar", "navigation-menu", "pagination", "popover",
            "progress", "radio-group", "scroll-area", "select", "separator", "sheet",
            "skeleton", "slider", "switch", "table", "tabs", "textarea", "toast",
            "toggle", "tooltip", "resizable", "aspect-ratio"
        ]

        return any(pattern in name.lower() for pattern in ui_patterns)

    def _is_hook_name(self, name: str) -> bool:
        """Check if a name follows React hook naming conventions"""
        return name.startswith("use-") or name.startswith("use")

    async def _process_component_config(self, component_config: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Process a single component configuration into an ExtractedComponent"""
        try:
            component_name = component_config.get("name", "")
            if not component_name:
                return None

            # Get file paths from component config and convert to full paths
            registry_files = component_config.get("files", [])
            component_files = []

            for file_path in registry_files:
                # Convert relative path from registry to full path
                full_paths = [
                    f"apps/www/{file_path}",
                    f"apps/v4/{file_path}",
                    file_path  # Try as-is
                ]

                for full_path in full_paths:
                    if self._read_local_file(full_path):
                        component_files.append(full_path)
                        break

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
                description=metadata.get("description", f"Shadcn UI component: {component_name}"),
                dependencies=dependencies,
                peer_dependencies=metadata.get("peer_dependencies", []),
                installation=install_cmd,
                usage_examples=metadata.get("usage_examples", []),
                metadata={
                    "files": component_files,
                    "component_type": metadata.get("component_type", "ui"),
                    "repository": self.repo_info,
                    "exports": metadata.get("exports", []),
                    "registry_file": self.registry_file
                },
                quality_score=self._calculate_quality_score(component_config, component_files),
                last_updated=datetime.now(),
                platform=["reactjs"],
                registry="shadcn"
            )

            return component

        except Exception as e:
            self.logger.error(f"Failed to process component config {component_config.get('name', 'unknown')}: {e}")
            return None

    def _extract_component_metadata(self, component_name: str, component_files: List[str]) -> Dict[str, Any]:
        """Extract metadata from component files"""
        metadata = {
            "description": f"Shadcn UI {component_name} component",
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
        if dependencies:
            deps_str = " ".join(dependencies)
            return f"npm install {deps_str}"
        else:
            return f"# Add {component_name} component to your project"

    def _calculate_quality_score(self, component_config: Dict[str, Any], component_files: List[str]) -> float:
        """Calculate quality score for the component"""
        score = 0.6  # Base score for shadcn components

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