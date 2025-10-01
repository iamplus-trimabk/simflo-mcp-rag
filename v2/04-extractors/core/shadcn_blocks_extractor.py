"""
⚠️  V4 IMPLEMENTATION REQUIRED ⚠️

This extractor is NOT IMPLEMENTED and must be fully implemented in v4.0 or above.
Current version uses simple extractors instead (shadcn_extractor.py, gluestack_extractor_simple.py).

Shadcn Blocks Extractor

Specialized extractor for UI blocks from shadcn/ui repositories.
Handles block composition, layout logic, responsive design patterns,
and configuration options extraction.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .github_cli_base import GitHubCLIBaseExtractor
from .base_extractor import ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata, BlockComposition, UsageExample

logger = logging.getLogger(__name__)


class ShadcnBlocksExtractor(GitHubCLIBaseExtractor):
    """Specialized extractor for shadcn/ui blocks"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.supported_types = ["block", "ui-block", "layout-block"]

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return self.supported_types

    def validate_source(self) -> bool:
        """Validate block source configuration"""
        if not super().validate_source():
            return False

        # Validate GitHub URL format
        github_url = self.source_config.get("url", "")
        if not github_url.startswith("https://github.com/"):
            logger.error("Invalid GitHub URL format")
            return False

        return True

    async def extract(self) -> ExtractionResult:
        """Extract blocks from shadcn repository"""
        self.logger.info(f"🚀 Starting block extraction from {self.name}")

        errors = []
        warnings = []
        blocks = []

        try:
            # Find block registry files
            registry_files = self._find_block_registry_files()
            if not registry_files:
                errors.append("No block registry files found")
                return ExtractionResult(
                    success=False,
                    data=[],
                    metadata={},
                    errors=errors,
                    warnings=warnings,
                    extraction_time=0.0,
                    source_info=self.source_config
                )

            self.logger.info(f"Found {len(registry_files)} potential registry files")

            # Process each registry file
            for registry_file in registry_files:
                try:
                    file_content = self._read_local_file(registry_file)
                    if file_content:
                        block_configs = self._parse_block_registry(file_content)
                        self.logger.info(f"Found {len(block_configs)} blocks in {registry_file}")

                        for block_config in block_configs:
                            block = await self._process_block_config(block_config, registry_file)
                            if block:
                                blocks.append(block)
                except Exception as e:
                    logger.warning(f"Failed to process registry file {registry_file}: {e}")
                    warnings.append(f"Failed to process {registry_file}: {e}")

            # Also search for block files directly
            direct_blocks = await self._extract_blocks_from_files()
            blocks.extend(direct_blocks)

            # Remove duplicates
            unique_blocks = self._remove_duplicate_blocks(blocks)

            # Calculate extraction time
            extraction_time = 0.0  # TODO: Track actual time

            self.logger.info(f"✅ Successfully extracted {len(unique_blocks)} unique blocks")

            return ExtractionResult(
                success=True,
                data=[block.to_dict() for block in unique_blocks],
                metadata={
                    "total_blocks": len(unique_blocks),
                    "registry_files_found": len(registry_files),
                    "direct_blocks_found": len(direct_blocks),
                    "repository_info": self.repo_info,
                    "extraction_method": "github_cli_local"
                },
                errors=errors,
                warnings=warnings,
                extraction_time=extraction_time,
                source_info=self.source_config
            )

        except Exception as e:
            logger.error(f"❌ Block extraction failed: {e}")
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

    def _find_block_registry_files(self) -> List[str]:
        """Find block registry files in the repository"""
        possible_paths = [
            "apps/www/registry/registry-blocks.ts",
            "apps/www/registry/registry-blocks.tsx",
            "registry/blocks.ts",
            "registry/blocks.tsx",
            "src/registry/blocks.ts",
            "src/registry/blocks.tsx",
            "blocks.ts",
            "blocks.tsx"
        ]

        found_files = []
        for path in possible_paths:
            if self._read_local_file(path):
                found_files.append(path)

        return found_files

    def _parse_block_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse block registry file content"""
        blocks = []

        try:
            # Try JSON first
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    blocks.extend(data)
                elif isinstance(data, dict):
                    if "blocks" in data:
                        blocks.extend(data["blocks"])
                    elif "components" in data:
                        # Filter for blocks
                        blocks.extend([item for item in data["components"] if self._is_block_name(item.get("name", ""))])
            else:
                # Parse TypeScript registry
                blocks.extend(self._parse_ts_registry(content))

        except json.JSONDecodeError:
            try:
                blocks.extend(self._parse_ts_registry(content))
            except Exception as e:
                logger.error(f"Failed to parse block registry: {e}")

        return blocks

    def _parse_ts_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse TypeScript block registry"""
        blocks = []

        # Look for block patterns
        patterns = [
            r'\{\s*name:\s*["\']([^"\']+)["\'][^}]*type:\s*["\']block["\']',
            r'export\s+const\s+blocks\s*=\s*\[([^\]]+)\]',
            r'export\s+(?:const|function)\s+([A-Z][a-zA-Z0-9]*Block)'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                block_name = match.group(1)
                if self._is_block_name(block_name):
                    context_start = max(0, match.start() - 800)
                    context_end = min(len(content), match.end() + 800)
                    context = content[context_start:context_end]

                    block_config = self._extract_block_from_context(block_name, context)
                    if block_config:
                        blocks.append(block_config)

        return blocks

    def _is_block_name(self, name: str) -> bool:
        """Check if a name indicates a block"""
        block_indicators = ["block", "layout", "section", "component", "card", "dashboard", "form", "table", "nav"]
        name_lower = name.lower()
        return any(indicator in name_lower for indicator in block_indicators)

    def _extract_block_from_context(self, block_name: str, context: str) -> Optional[Dict[str, Any]]:
        """Extract block configuration from context"""
        block_config = {"name": block_name}

        # Extract description
        desc_patterns = [
            r'description:\s*["\']([^"\']+)["\']',
            r'\/\*\*[\s\S]*?\*[\s*]@description[^\*]*\*[\s*]([^\n]+)',
            r'\/\/\s*(.+?)(?=\n)'
        ]

        for pattern in desc_patterns:
            desc_match = re.search(pattern, context)
            if desc_match:
                block_config["description"] = desc_match.group(1).strip()
                break

        # Extract components used in the block
        components_pattern = r'components:\s*\[([^\]]+)\]'
        components_match = re.search(components_pattern, context)
        if components_match:
            components_str = components_match.group(1)
            block_config["components"] = [comp.strip().strip('"\'') for comp in components_str.split(',')]

        return block_config

    async def _process_block_config(self, block_config: Dict[str, Any], registry_file: str) -> Optional[ExtractedComponent]:
        """Process a block configuration into an ExtractedComponent"""
        try:
            block_name = block_config.get("name", "")
            if not block_name:
                return None

            # Find block implementation files
            block_files = self._find_block_files(block_name)
            if not block_files:
                logger.warning(f"No implementation files found for block: {block_name}")
                return None

            # Extract block composition and dependencies
            composition = self._extract_block_composition(block_files, block_config)
            dependencies = self._extract_block_dependencies(block_files)

            # Create component
            component = ExtractedComponent(
                name=block_name,
                category="blocks",
                type="block",
                sources=[self.repo_url],
                priority_source=self.repo_url,
                description=block_config.get("description", f"UI block: {block_name}"),
                dependencies=dependencies,
                peer_dependencies=[],
                installation=self._generate_block_install_command(block_name, dependencies),
                usage_examples=self._extract_usage_examples(block_files),
                metadata={
                    "files": block_files,
                    "composition": composition,
                    "components": block_config.get("components", []),
                    "registry_file": registry_file,
                    "repository": self.repo_info
                },
                quality_score=self._calculate_block_quality_score(block_config, block_files),
                last_updated=datetime.now(),
                platform=["reactjs"],
                registry="shadcn"
            )

            return component

        except Exception as e:
            logger.error(f"Failed to process block config {block_config.get('name', 'unknown')}: {e}")
            return None

    def _find_block_files(self, block_name: str) -> List[str]:
        """Find block implementation files"""
        possible_paths = [
            f"blocks/{block_name}.tsx",
            f"blocks/{block_name}.ts",
            f"components/blocks/{block_name}.tsx",
            f"components/blocks/{block_name}.ts",
            f"src/blocks/{block_name}.tsx",
            f"src/blocks/{block_name}.ts",
            f"app/blocks/{block_name}.tsx",
            f"app/blocks/{block_name}.ts",
        ]

        found_files = []
        for path in possible_paths:
            if self._read_local_file(path):
                found_files.append(path)

        return found_files

    async def _extract_blocks_from_files(self) -> List[ExtractedComponent]:
        """Extract blocks by scanning the repository directly"""
        blocks = []

        # Look for files that might contain blocks
        block_files = self._find_files_by_pattern("*block*.tsx") + self._find_files_by_pattern("*Block*.tsx")

        for file_path in block_files:
            try:
                content = self._read_local_file(str(file_path))
                if content:
                    block_configs = self._parse_ts_registry(content)
                    for block_config in block_configs:
                        block = await self._process_block_config(block_config, str(file_path))
                        if block:
                            blocks.append(block)
            except Exception as e:
                logger.warning(f"Failed to extract blocks from {file_path}: {e}")

        return blocks

    def _extract_block_composition(self, block_files: List[str], block_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract block composition information"""
        composition = {
            "components": block_config.get("components", []),
            "layout_type": "unknown",
            "responsive": False,
            "accessibility_features": []
        }

        # Analyze files to determine composition
        for file_path in block_files:
            content = self._read_local_file(file_path)
            if content:
                # Check for responsive design patterns
                if "responsive" in content.lower() or "useMediaQuery" in content:
                    composition["responsive"] = True

                # Check for accessibility features
                if "aria-" in content or "accessibility" in content.lower():
                    composition["accessibility_features"].append("aria-support")

        return composition

    def _extract_block_dependencies(self, block_files: List[str]) -> List[str]:
        """Extract dependencies from block files"""
        dependencies = set()

        for file_path in block_files:
            content = self._read_local_file(file_path)
            if content:
                # Extract import statements
                import_pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
                matches = re.findall(import_pattern, content)
                for match in matches:
                    if not match.startswith('.') and not match.startswith('/'):
                        dependencies.add(match)

        return list(dependencies)

    def _extract_usage_examples(self, block_files: List[str]) -> List[str]:
        """Extract usage examples from block files"""
        examples = []

        for file_path in block_files:
            content = self._read_local_file(file_path)
            if content:
                # Look for example code blocks
                example_pattern = r'```(?:tsx|typescript|jsx|javascript)\n([\s\S]*?)\n```'
                matches = re.findall(example_pattern, content)
                examples.extend(matches)

                # Look for usage comments
                usage_pattern = r'\/\/\s*@usage\s*([^\n]+)'
                usage_matches = re.findall(usage_pattern, content)
                examples.extend(usage_matches)

        return examples[:5]  # Limit to 5 examples

    def _generate_block_install_command(self, block_name: str, dependencies: List[str]) -> str:
        """Generate installation command for the block"""
        if dependencies:
            deps_str = " ".join(dependencies)
            return f"npm install {deps_str}\n# Add {block_name} block to your project"
        else:
            return f"# Add {block_name} block to your project"

    def _calculate_block_quality_score(self, block_config: Dict[str, Any], block_files: List[str]) -> float:
        """Calculate quality score for the block"""
        score = 0.5  # Base score

        # Bonus for description
        if block_config.get("description"):
            score += 0.2

        # Bonus for implementation files
        if block_files:
            score += 0.2

        # Bonus for component composition
        if block_config.get("components"):
            score += 0.1

        return min(score, 1.0)

    def _remove_duplicate_blocks(self, blocks: List[ExtractedComponent]) -> List[ExtractedComponent]:
        """Remove duplicate blocks based on name"""
        seen = set()
        unique_blocks = []
        for block in blocks:
            if block.name not in seen:
                seen.add(block.name)
                unique_blocks.append(block)
        return unique_blocks