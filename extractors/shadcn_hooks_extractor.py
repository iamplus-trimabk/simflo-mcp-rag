"""
Shadcn Hooks Extractor

Specialized extractor for React hooks from shadcn/ui repositories.
Handles hook-specific patterns, dependencies, and metadata extraction.
"""

import re
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .github_cli_base import GitHubCLIBaseExtractor
from .base_extractor import ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, HookSignature, SourceMetadata

logger = logging.getLogger(__name__)

class ShadcnHooksExtractor(GitHubCLIBaseExtractor):
    """Specialized extractor for shadcn/ui hooks"""

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
        return ["hook"]

    async def extract(self) -> ExtractionResult:
        """Extract hooks from shadcn registry"""
        self.logger.info(f"🚀 Starting hook extraction from {self.name}")

        errors = []
        warnings = []
        hooks = []

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
            hook_configs = self._parse_registry(registry_content)
            self.logger.info(f"Found {len(hook_configs)} hook configurations")

            # Process each hook configuration
            for hook_config in hook_configs:
                try:
                    hook = await self._process_hook_config(hook_config)
                    if hook:
                        hooks.append(hook)
                except Exception as e:
                    logger.warning(f"Failed to process hook config {hook_config.get('name', 'unknown')}: {e}")
                    warnings.append(f"Failed to process {hook_config.get('name', 'unknown')}: {e}")

            # Calculate extraction time
            extraction_time = 0.0  # TODO: Track actual time

            self.logger.info(f"✅ Successfully extracted {len(hooks)} hooks")

            return ExtractionResult(
                success=True,
                data=[hook.to_dict() for hook in hooks],
                metadata={
                    "total_hooks": len(hooks),
                    "repository_info": self.repo_info,
                    "extraction_method": "github_cli_local"
                },
                errors=errors,
                warnings=warnings,
                extraction_time=extraction_time,
                source_info=self.source_config
            )

        except Exception as e:
            logger.error(f"❌ Hook extraction failed: {e}")
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
        """Parse the registry file to extract hook configurations"""
        hooks = []

        try:
            # Try to parse as JSON first
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    hooks.extend(data)
                elif isinstance(data, dict):
                    if "hooks" in data:
                        hooks.extend(data["hooks"])
                    elif "components" in data:
                        # Filter for hooks only
                        hooks.extend([item for item in data["components"] if self._is_hook_name(item.get("name", ""))])
            else:
                # Parse as TypeScript/JavaScript registry
                hooks.extend(self._parse_ts_registry(content))

        except json.JSONDecodeError:
            # Fallback to TypeScript parsing
            try:
                hooks.extend(self._parse_ts_registry(content))
            except Exception as e:
                self.logger.error(f"Failed to parse registry content: {e}")
                return []

        self.logger.info(f"Parsed {len(hooks)} hook configurations from registry")
        return hooks

    def _parse_ts_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse TypeScript registry file format"""
        hooks = []

        # Look for hook entries in various formats
        patterns = [
            # Format: { name: "use-form", ... }
            r'\{\s*name:\s*["\']([^"\']+)["\']',
            # Format: export const hooks = [ ... ]
            r'export\s+const\s+hooks\s*=\s*\[([^\]]+)\]',
            # Format: export const useSomething = ...
            r'export\s+(?:const|function|async\s+function)\s+(use[A-Z][a-zA-Z0-9]*)'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                if match.group(1):
                    hook_name = match.group(1)
                    if self._is_hook_name(hook_name):
                        # Extract additional context around the match
                        start_pos = max(0, match.start() - 500)
                        end_pos = min(len(content), match.end() + 500)
                        context = content[start_pos:end_pos]

                        hook_config = self._extract_hook_from_context(hook_name, context)
                        if hook_config:
                            hooks.append(hook_config)

        return hooks

    def _is_hook_name(self, name: str) -> bool:
        """Check if a name follows React hook naming conventions"""
        return name.startswith("use-") or name.startswith("use")

    def _extract_hook_from_context(self, hook_name: str, context: str) -> Optional[Dict[str, Any]]:
        """Extract hook configuration from surrounding context"""
        hook_config = {"name": hook_name}

        # Extract description
        desc_patterns = [
            r'description:\s*["\']([^"\']+)["\']',
            r'\/\*\*[\s\S]*?\*[\s*]@description[^\*]*\*[\s*]([^\n]+)',
            r'\/\/\s*(.+?)(?=\n|$)'
        ]

        for pattern in desc_patterns:
            desc_match = re.search(pattern, context)
            if desc_match:
                hook_config["description"] = desc_match.group(1).strip()
                break

        # Extract dependencies
        deps_pattern = r'dependencies:\s*\[([^\]]+)\]'
        deps_match = re.search(deps_pattern, context)
        if deps_match:
            deps_str = deps_match.group(1)
            hook_config["dependencies"] = [dep.strip().strip('"\'') for dep in deps_str.split(',')]

        # Extract files
        files_pattern = r'files:\s*\[([^\]]+)\]'
        files_match = re.search(files_pattern, context)
        if files_match:
            files_str = files_match.group(1)
            hook_config["files"] = [f.strip().strip('"\'') for f in files_str.split(',')]

        return hook_config

    async def _process_hook_config(self, hook_config: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Process a single hook configuration into an ExtractedComponent"""
        try:
            hook_name = hook_config.get("name", "")
            if not hook_name:
                return None

            # Find hook implementation files
            hook_files = self._find_hook_files(hook_name)
            if not hook_files:
                self.logger.warning(f"No implementation files found for hook: {hook_name}")
                return None

            # Extract hook signature and dependencies
            signature_info = self._extract_hook_signature(hook_files)
            dependencies = self._extract_dependencies(hook_files)

            # Generate installation command
            install_cmd = self._generate_install_command(hook_name, dependencies)

            # Create component
            component = ExtractedComponent(
                name=hook_name,
                category="hooks",
                type="hook",
                sources=[self.repo_url],
                priority_source=self.repo_url,
                description=hook_config.get("description", f"React hook: {hook_name}"),
                dependencies=dependencies,
                peer_dependencies=[],
                installation=install_cmd,
                usage_examples=[],  # TODO: Extract from files
                metadata={
                    "files": hook_files,
                    "signature": signature_info,
                    "repository": self.repo_info,
                    "registry_file": self.registry_file
                },
                quality_score=self._calculate_quality_score(hook_config, hook_files),
                last_updated=datetime.now(),
                platform=["reactjs"],
                registry="shadcn"
            )

            return component

        except Exception as e:
            self.logger.error(f"Failed to process hook config {hook_config.get('name', 'unknown')}: {e}")
            return None

    def _find_hook_files(self, hook_name: str) -> List[str]:
        """Find implementation files for a hook"""
        possible_paths = [
            f"hooks/{hook_name}.tsx",
            f"hooks/{hook_name}.ts",
            f"src/hooks/{hook_name}.tsx",
            f"src/hooks/{hook_name}.ts",
            f"components/ui/hooks/{hook_name}.tsx",
            f"components/ui/hooks/{hook_name}.ts",
            f"app/registry/hooks/{hook_name}.tsx",
            f"app/registry/hooks/{hook_name}.ts",
        ]

        found_files = []
        for path in possible_paths:
            if self._read_local_file(path):
                found_files.append(path)

        return found_files

    def _extract_hook_signature(self, hook_files: List[str]) -> Dict[str, Any]:
        """Extract hook signature information"""
        signature_info = {
            "parameters": [],
            "return_type": "unknown",
            "generics": []
        }

        for file_path in hook_files:
            content = self._read_local_file(file_path)
            if content:
                # Look for hook function signature
                hook_pattern = r'export\s+(?:function|const)\s+(use\w+)\s*[:\s]*(?:\([^)]*\)|\w+)[\s\S]*?(?=\nexport|\n\n\n|$)'
                match = re.search(hook_pattern, content, re.MULTILINE | re.DOTALL)
                if match:
                    signature_info["implementation_found"] = True
                    break

        return signature_info

    def _extract_dependencies(self, hook_files: List[str]) -> List[str]:
        """Extract dependencies from hook files"""
        dependencies = set()

        for file_path in hook_files:
            content = self._read_local_file(file_path)
            if content:
                # Look for import statements
                import_pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
                matches = re.findall(import_pattern, content)
                for match in matches:
                    if not match.startswith('.') and not match.startswith('/'):
                        dependencies.add(match)

        return list(dependencies)

    def _generate_install_command(self, hook_name: str, dependencies: List[str]) -> str:
        """Generate installation command for the hook"""
        if dependencies:
            deps_str = " ".join(dependencies)
            return f"npm install {deps_str}"
        else:
            return f"# Add {hook_name} hook to your project"

    def _calculate_quality_score(self, hook_config: Dict[str, Any], hook_files: List[str]) -> float:
        """Calculate quality score for the hook"""
        score = 0.5  # Base score

        # Bonus for description
        if hook_config.get("description"):
            score += 0.2

        # Bonus for implementation files
        if hook_files:
            score += 0.2

        # Bonus for dependencies (indicates integration)
        if hook_config.get("dependencies"):
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