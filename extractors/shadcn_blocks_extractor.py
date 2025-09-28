"""
Shadcn Blocks Extractor

Specialized extractor for UI blocks from shadcn/ui repositories.
Handles block composition, layout logic, responsive design patterns,
and configuration options extraction.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata, BlockComposition, UsageExample


class ShadcnBlocksExtractor(BaseExtractor):
    """Specialized extractor for shadcn/ui blocks"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.supported_types = ["block", "ui-block", "layout-block"]
        self.github_api_base = "https://api.github.com"
        self.github_raw_base = "https://raw.githubusercontent.com"

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return self.supported_types

    async def validate_source(self) -> bool:
        """Validate block source configuration"""
        try:
            # Check required fields
            required_fields = ["url", "branch", "extractor"]
            for field in required_fields:
                if field not in self.source_config:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate GitHub URL
            github_url = self.source_config.get("url", "")
            if not github_url.startswith("https://github.com/"):
                self.logger.error("Invalid GitHub URL format")
                return False

            # Check if repository exists (basic validation)
            repo_path = github_url.replace("https://github.com/", "")
            if not repo_path or "/" not in repo_path:
                self.logger.error("Invalid GitHub repository path")
                return False

            self.logger.info(f"✅ Block source validation passed: {self.source_name}")
            return True

        except Exception as e:
            self.logger.error(f"Block source validation failed: {e}")
            return False

    async def extract(self) -> ExtractionResult:
        """Extract blocks from shadcn/ui repository"""
        try:
            self.logger.info(f"🚀 Starting block extraction from {self.source_name}")

            # Initialize result
            result = ExtractionResult(
                success=True,
                data=[],
                metadata={
                    "extractor": "shadcn_blocks",
                    "source_name": self.source_name,
                    "extracted_at": datetime.now().isoformat(),
                    "total_blocks": 0
                },
                errors=[],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

            # Fetch block registry files
            block_configs = await self._fetch_block_configs()
            if not block_configs:
                result.success = False
                result.errors.append("No block configurations found")
                return result

            self.logger.info(f"📦 Found {len(block_configs)} block configurations")

            # Extract each block
            for block_config in block_configs:
                try:
                    extracted_block = await self._extract_single_block(block_config)
                    if extracted_block:
                        result.data.append(extracted_block)
                except Exception as e:
                    error_msg = f"Failed to extract block {block_config.get('name', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)

            result.metadata["total_blocks"] = len(result.data)
            result.metadata["extraction_time"] = str(datetime.now() - datetime.fromisoformat(result.metadata["extracted_at"]))

            self.logger.info(f"✅ Block extraction completed: {len(result.data)} blocks extracted")
            return result

        except Exception as e:
            error_msg = f"Block extraction failed: {e}"
            self.logger.error(error_msg)
            return ExtractionResult(
                success=False,
                data=[],
                metadata={"extractor": "shadcn_blocks", "source_name": self.source_name},
                errors=[error_msg],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

    async def _fetch_block_configs(self) -> List[Dict[str, Any]]:
        """Fetch block configurations from registry files"""
        block_configs = []

        try:
            # Try multiple registry file patterns
            registry_patterns = [
                "apps/www/registry/registry-blocks.ts",
                "apps/www/registry/registry-blocks.tsx",
                "apps/www/registry/blocks.ts",
                "apps/www/registry/blocks.tsx",
                "registry/blocks.ts",
                "registry/blocks.tsx"
            ]

            for registry_path in registry_patterns:
                try:
                    content = await self._fetch_github_file(registry_path)
                    if content:
                        parsed_configs = self._parse_blocks_registry(content)
                        if parsed_configs:
                            self.logger.info(f"📄 Found blocks registry: {registry_path}")
                            return parsed_configs
                except Exception as e:
                    self.logger.debug(f"Registry file not found: {registry_path}")
                    continue

            # Fallback: Try to find blocks in examples directory
            block_configs = await self._discover_blocks_from_examples()
            if block_configs:
                self.logger.info("🔍 Discovered blocks from examples directory")
                return block_configs

            self.logger.warning("⚠️ No block registry files found")
            return []

        except Exception as e:
            self.logger.error(f"Failed to fetch block configs: {e}")
            return []

    async def _fetch_github_file(self, file_path: str) -> Optional[str]:
        """Fetch file content from GitHub repository"""
        try:
            repo_url = self.source_config.get("url", "")
            branch = self.source_config.get("branch", "main")

            # Extract owner/repo from URL
            repo_path = repo_url.replace("https://github.com/", "")
            if repo_path.endswith("/"):
                repo_path = repo_path[:-1]

            # Try raw.githubusercontent.com first
            raw_url = f"{self.github_raw_base}/{repo_path}/{branch}/{file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(raw_url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 404:
                        # Try GitHub API as fallback
                        api_url = f"{self.github_api_base}/repos/{repo_path}/contents/{file_path}"
                        headers = {"Accept": "application/vnd.github.v3.raw"}

                        async with session.get(api_url, headers=headers) as api_response:
                            if api_response.status == 200:
                                return await api_response.text()
                    else:
                        self.logger.error(f"GitHub API error: {response.status}")
                        return None

            return None

        except Exception as e:
            self.logger.error(f"Failed to fetch GitHub file {file_path}: {e}")
            return None

    def _parse_blocks_registry(self, content: str) -> List[Dict[str, Any]]:
        """Parse blocks registry file (TypeScript/JavaScript)"""
        block_configs = []

        try:
            # Look for block export patterns
            patterns = [
                r'export\s+const\s+(\w+)\s*:\s*Block\s*=\s*({[^}]+})',
                r'export\s+const\s+(\w+)\s*=\s*({[^}]+})',
                r'const\s+(\w+)\s*:\s*Block\s*=\s*({[^}]+})',
                r'(\w+):\s*{\s*name:\s*["\']([^"\']+)["\']',
                r'["\']name["\']:\s*["\']([^"\']+)["\']'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    for match in matches:
                        block_config = self._extract_block_config_from_match(match, content)
                        if block_config:
                            block_configs.append(block_config)

            # If no structured patterns found, try to extract from object arrays
            if not block_configs:
                block_configs = self._extract_blocks_from_array(content)

            self.logger.info(f"📝 Parsed {len(block_configs)} block configurations")
            return block_configs

        except Exception as e:
            self.logger.error(f"Failed to parse blocks registry: {e}")
            return []

    def _extract_block_config_from_match(self, match: Tuple, content: str) -> Optional[Dict[str, Any]]:
        """Extract block configuration from regex match"""
        try:
            if len(match) == 2:
                block_name = match[0]
                config_text = match[1]
            elif len(match) == 1:
                # Extract from full content
                block_name = "unknown"
                config_text = match[0]
            else:
                return None

            # Parse configuration fields
            config = {
                "name": block_name,
                "description": self._extract_field(config_text, ["description", "desc"], content),
                "category": "blocks",
                "type": "block",
                "files": self._extract_files_field(config_text, content),
                "dependencies": self._extract_dependencies(config_text, content),
                "components": self._extract_components(config_text, content)
            }

            return config

        except Exception as e:
            self.logger.error(f"Failed to extract block config from match: {e}")
            return None

    def _extract_field(self, text: str, field_names: List[str], full_content: str) -> str:
        """Extract field value from configuration text"""
        for field_name in field_names:
            pattern = rf'{field_name}\s*[:=]\s*["\']([^"\']+)["\']'
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Try in full content
        for field_name in field_names:
            pattern = rf'{field_name}\s*[:=]\s*["\']([^"\']+)["\']'
            match = re.search(pattern, full_content)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_files_field(self, text: str, full_content: str) -> List[str]:
        """Extract files array from configuration"""
        patterns = [
            r'files\s*:\s*\[([^\]]+)\]',
            r'files\s*:\s*["\']([^"\']+)["\']'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                files_text = match.group(1)
                # Extract individual file paths
                file_paths = re.findall(r'["\']([^"\']+)["\']', files_text)
                return [f.strip() for f in file_paths if f.strip()]

        return []

    def _extract_dependencies(self, text: str, full_content: str) -> List[str]:
        """Extract dependencies from configuration"""
        patterns = [
            r'dependencies\s*:\s*\[([^\]]+)\]',
            r'dependencies\s*:\s*["\']([^"\']+)["\']'
        ]

        dependencies = []
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                deps_text = match.group(1)
                deps = re.findall(r'["\']([^"\']+)["\']', deps_text)
                dependencies.extend([d.strip() for d in deps if d.strip()])

        return list(set(dependencies))

    def _extract_components(self, text: str, full_content: str) -> List[str]:
        """Extract component names from block configuration"""
        patterns = [
            r'components\s*:\s*\[([^\]]+)\]',
            r'componentNames?\s*:\s*\[([^\]]+)\]'
        ]

        components = []
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                comps_text = match.group(1)
                comps = re.findall(r'["\']([^"\']+)["\']', comps_text)
                components.extend([c.strip() for c in comps if c.strip()])

        return list(set(components))

    def _extract_blocks_from_array(self, content: str) -> List[Dict[str, Any]]:
        """Extract blocks from array-like structures"""
        block_configs = []

        try:
            # Look for array patterns
            array_patterns = [
                r'export\s+const\s+\w+\s*=\s*\[([^\]]+)\]',
                r'const\s+\w+\s*=\s*\[([^\]]+)\]'
            ]

            for pattern in array_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    # Extract individual block objects
                    block_objects = re.findall(r'{[^}]+}', match)
                    for block_obj in block_objects:
                        config = self._parse_block_object(block_obj)
                        if config:
                            block_configs.append(config)

            return block_configs

        except Exception as e:
            self.logger.error(f"Failed to extract blocks from array: {e}")
            return []

    def _parse_block_object(self, obj_text: str) -> Optional[Dict[str, Any]]:
        """Parse individual block object"""
        try:
            config = {
                "name": self._extract_field(obj_text, ["name"], obj_text),
                "description": self._extract_field(obj_text, ["description", "desc"], obj_text),
                "category": "blocks",
                "type": "block",
                "files": self._extract_files_field(obj_text, obj_text),
                "dependencies": self._extract_dependencies(obj_text, obj_text),
                "components": self._extract_components(obj_text, obj_text)
            }

            if config["name"]:
                return config

            return None

        except Exception as e:
            self.logger.error(f"Failed to parse block object: {e}")
            return None

    async def _discover_blocks_from_examples(self) -> List[Dict[str, Any]]:
        """Discover blocks from examples directory structure"""
        block_configs = []

        try:
            # Try to fetch examples directory listing
            examples_patterns = [
                "examples/",
                "app/examples/",
                "docs/examples/",
                "blocks/"
            ]

            for pattern in examples_patterns:
                try:
                    # This is a simplified approach - in real implementation,
                    # you'd use GitHub API to list directory contents
                    # For now, return empty list
                    pass
                except Exception:
                    continue

            return block_configs

        except Exception as e:
            self.logger.error(f"Failed to discover blocks from examples: {e}")
            return []

    async def _extract_single_block(self, block_config: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Extract a single block with full metadata"""
        try:
            block_name = block_config.get("name", "")
            if not block_name:
                return None

            self.logger.info(f"🔧 Extracting block: {block_name}")

            # Fetch component files for detailed analysis
            component_files = await self._fetch_block_files(block_config)

            # Analyze block composition
            block_composition = await self._analyze_block_composition(component_files)

            # Extract usage examples
            usage_examples = await self._extract_usage_examples(block_config, component_files)

            # Calculate quality score
            quality_score = self._calculate_block_quality_score(block_config, component_files)

            # Create extracted component
            extracted_component = ExtractedComponent(
                name=block_name,
                category=ComponentCategory.BLOCKS,
                type=ComponentType.BLOCK,
                registry="shadcn",
                priority_source=self.source_name,
                sources=[self.source_name],
                display_name=block_name.replace("-", " ").title(),
                description=block_config.get("description", f"Shadcn UI block: {block_name}"),
                dependencies=block_config.get("dependencies", []),
                installation=f"npx shadcn@latest add {block_name}",
                platform=["reactjs"],
                framework="react",
                quality_score=quality_score,
                usage_examples=usage_examples,
                category_specific_data={
                    "block_composition": block_composition.to_dict() if block_composition else {},
                    "components": block_config.get("components", []),
                    "files": component_files
                }
            )

            # Add source metadata
            extracted_component.add_source_metadata(
                self.source_name,
                SourceMetadata(
                    source_name=self.source_name,
                    extracted_at=datetime.now(),
                    url=self.source_config.get("url"),
                    extraction_metadata={
                        "block_files": len(component_files),
                        "has_composition": block_composition is not None,
                        "usage_examples_count": len(usage_examples)
                    }
                )
            )

            return extracted_component

        except Exception as e:
            self.logger.error(f"Failed to extract single block {block_config.get('name', 'unknown')}: {e}")
            return None

    async def _fetch_block_files(self, block_config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Fetch and analyze block component files"""
        component_files = []

        try:
            file_paths = block_config.get("files", [])

            for file_path in file_paths:
                try:
                    content = await self._fetch_github_file(file_path)
                    if content:
                        component_files.append({
                            "path": file_path,
                            "content": content
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to fetch file {file_path}: {e}")
                    continue

            return component_files

        except Exception as e:
            self.logger.error(f"Failed to fetch block files: {e}")
            return []

    async def _analyze_block_composition(self, component_files: List[Dict[str, str]]) -> Optional[BlockComposition]:
        """Analyze block composition and structure"""
        try:
            if not component_files:
                return None

            composition = BlockComposition()

            # Analyze each file for composition patterns
            for file_info in component_files:
                content = file_info["content"]

                # Extract component imports
                imports = self._extract_imports(content)
                composition.components.extend(imports)

                # Extract layout type
                layout_type = self._extract_layout_type(content)
                if layout_type and not composition.layout_type:
                    composition.layout_type = layout_type

                # Extract responsive behavior
                responsive_behavior = self._extract_responsive_behavior(content)
                composition.responsive_behavior.update(responsive_behavior)

                # Extract configuration options
                config_options = self._extract_configuration_options(content)
                composition.configuration_options.extend(config_options)

            # Deduplicate components
            composition.components = list(set(composition.components))

            return composition

        except Exception as e:
            self.logger.error(f"Failed to analyze block composition: {e}")
            return None

    def _extract_imports(self, content: str) -> List[str]:
        """Extract component imports from file content"""
        imports = []

        # Import patterns
        patterns = [
            r'import\s+{\s*([^}]+)\s*}\s+from',
            r'import\s+(\w+)\s+from',
            r'from\s+["\']([^"\']+)["\']'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, str):
                    # Clean up import names
                    components = [comp.strip() for comp in match.split(",")]
                    imports.extend(components)

        # Filter out non-component imports
        component_imports = [
            imp for imp in imports
            if imp and not imp.startswith(('.', '/', 'react', 'next', 'node'))
        ]

        return component_imports

    def _extract_layout_type(self, content: str) -> Optional[str]:
        """Extract layout type from content"""
        layout_indicators = [
            ("grid", ["grid", "Grid"]),
            ("flex", ["flex", "Flex"]),
            ("stack", ["stack", "Stack"]),
            ("card", ["card", "Card"]),
            ("form", ["form", "Form"]),
            ("table", ["table", "Table"]),
            ("dialog", ["dialog", "Dialog"]),
            ("sheet", ["sheet", "Sheet"])
        ]

        for layout_type, indicators in layout_indicators:
            for indicator in indicators:
                if re.search(rf'\b{indicator}\b', content, re.IGNORECASE):
                    return layout_type

        return "custom"

    def _extract_responsive_behavior(self, content: str) -> Dict[str, Any]:
        """Extract responsive design patterns"""
        responsive_behavior = {}

        # Look for responsive breakpoints
        breakpoints = {
            "sm": r'sm:|@media\s*\(\s*min-width:\s*640px',
            "md": r'md:|@media\s*\(\s*min-width:\s*768px',
            "lg": r'lg:|@media\s*\(\s*min-width:\s*1024px',
            "xl": r'xl:|@media\s*\(\s*min-width:\s*1280px'
        }

        for bp_name, pattern in breakpoints.items():
            if re.search(pattern, content):
                responsive_behavior[bp_name] = True

        # Look for responsive utilities
        responsive_utilities = [
            "flex-col", "flex-row", "hidden", "block", "grid-cols",
            "flex-wrap", "overflow-x", "overflow-y", "aspect-ratio"
        ]

        for util in responsive_utilities:
            if util in content:
                responsive_behavior[f"has_{util.replace('-', '_')}"] = True

        return responsive_behavior

    def _extract_configuration_options(self, content: str) -> List[Dict[str, Any]]:
        """Extract configuration options from block"""
        config_options = []

        # Look for interface/type definitions
        interface_patterns = [
            r'interface\s+(\w+Props)\s*{([^}]+)}',
            r'type\s+(\w+Props)\s*=\s*{([^}]+)}'
        ]

        for pattern in interface_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                props_name = match[0]
                props_body = match[1]

                # Extract individual properties
                prop_pattern = r'(\w+)\s*:\s*([^;]+)'
                props = re.findall(prop_pattern, props_body)

                for prop_name, prop_type in props:
                    config_options.append({
                        "name": prop_name,
                        "type": prop_type.strip(),
                        "required": "?" not in prop_name,
                        "interface": props_name
                    })

        return config_options

    async def _extract_usage_examples(self, block_config: Dict[str, Any], component_files: List[Dict[str, str]]) -> List[UsageExample]:
        """Extract usage examples from block files"""
        usage_examples = []

        try:
            # Look for example patterns in component files
            for file_info in component_files:
                content = file_info["content"]

                # Extract code examples
                examples = self._extract_code_examples(content)
                usage_examples.extend(examples)

            # If no examples found in files, create basic usage example
            if not usage_examples:
                block_name = block_config.get("name", "")
                basic_example = UsageExample(
                    title=f"Basic {block_name} Usage",
                    description=f"Basic usage example for {block_name} block",
                    code=f"<{block_name} />",
                    language="typescript",
                    difficulty="beginner"
                )
                usage_examples.append(basic_example)

            return usage_examples

        except Exception as e:
            self.logger.error(f"Failed to extract usage examples: {e}")
            return []

    def _extract_code_examples(self, content: str) -> List[UsageExample]:
        """Extract code examples from file content"""
        examples = []

        # Look for example code blocks
        patterns = [
            r'// Example:\s*\n([^/]+)',
            r'// Usage:\s*\n([^/]+)',
            r'/\*\s*Example[^*]*\*/\s*\n([^/]+)',
            r'exampleCode\s*:\s*["\']([^"\']+)["\']'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                code = match.strip()
                if code and len(code) > 10:  # Minimum length check
                    example = UsageExample(
                        code=code,
                        language="typescript",
                        difficulty="intermediate"
                    )
                    examples.append(example)

        return examples

    def _calculate_block_quality_score(self, block_config: Dict[str, Any], component_files: List[Dict[str, str]]) -> float:
        """Calculate quality score for block"""
        score = 0.5  # Base score

        try:
            # Description quality
            description = block_config.get("description", "")
            if description and len(description) > 20:
                score += 0.1

            # File completeness
            if component_files:
                score += 0.1
                if len(component_files) > 1:
                    score += 0.1

            # Component count (more components = more complex)
            components = block_config.get("components", [])
            if components:
                score += min(0.1, len(components) * 0.02)

            # Dependencies (fewer dependencies = better)
            dependencies = block_config.get("dependencies", [])
            if len(dependencies) <= 2:
                score += 0.1
            elif len(dependencies) <= 5:
                score += 0.05

            return min(1.0, max(0.0, score))

        except Exception as e:
            self.logger.error(f"Failed to calculate quality score: {e}")
            return score