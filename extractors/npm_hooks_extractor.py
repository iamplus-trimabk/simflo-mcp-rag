"""
NPM Hooks Extractor

Specialized extractor for React hooks from NPM packages without registry files.
Handles package.json parsing, type definition analysis, version management,
and documentation extraction from README and JSDoc comments.
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
import semver

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata, HookSignature, UsageExample


class NPMHooksExtractor(BaseExtractor):
    """Specialized extractor for NPM package hooks"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.supported_types = ["hook", "react-hook", "custom-hook"]
        self.npm_api_base = "https://registry.npmjs.org"
        self.npm_cdn_base = "https://unpkg.com"
        self.github_raw_base = "https://raw.githubusercontent.com"
        self.session: Optional[aiohttp.ClientSession] = None

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return self.supported_types

    async def __aenter__(self):
        """Initialize async context"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context"""
        if self.session:
            await self.session.close()

    async def validate_source(self) -> bool:
        """Validate NPM source configuration"""
        try:
            # Check required fields
            required_fields = ["package", "extractor"]
            for field in required_fields:
                if field not in self.source_config:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate package name
            package_name = self.source_config.get("package", "")
            if not self._is_valid_package_name(package_name):
                self.logger.error(f"Invalid package name: {package_name}")
                return False

            # Check if package exists on NPM
            package_exists = await self._check_package_exists(package_name)
            if not package_exists:
                self.logger.error(f"Package not found on NPM: {package_name}")
                return False

            self.logger.info(f"✅ NPM source validation passed: {self.source_name}")
            return True

        except Exception as e:
            self.logger.error(f"NPM source validation failed: {e}")
            return False

    async def extract(self) -> ExtractionResult:
        """Extract hooks from NPM package"""
        try:
            self.logger.info(f"🚀 Starting NPM hook extraction from {self.source_name}")

            # Initialize result
            result = ExtractionResult(
                success=True,
                data=[],
                metadata={
                    "extractor": "npm_hooks",
                    "source_name": self.source_name,
                    "extracted_at": datetime.now().isoformat(),
                    "total_hooks": 0
                },
                errors=[],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

            # Get package metadata
            package_name = self.source_config.get("package", "")
            package_metadata = await self._fetch_package_metadata(package_name)
            if not package_metadata:
                result.success = False
                result.errors.append(f"Failed to fetch package metadata: {package_name}")
                return result

            self.logger.info(f"📦 Package metadata fetched: {package_metadata.get('name', package_name)}")

            # Extract hooks from package
            hooks = await self._extract_hooks_from_package(package_metadata)
            if not hooks:
                self.logger.warning("⚠️ No hooks found in package")
                result.warnings.append("No hooks found in package")
                return result

            self.logger.info(f"🪝 Found {len(hooks)} hooks")

            # Process each hook
            for hook_info in hooks:
                try:
                    extracted_hook = await self._extract_single_hook(hook_info, package_metadata)
                    if extracted_hook:
                        result.data.append(extracted_hook)
                except Exception as e:
                    error_msg = f"Failed to extract hook {hook_info.get('name', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)

            result.metadata["total_hooks"] = len(result.data)
            result.metadata["extraction_time"] = str(datetime.now() - datetime.fromisoformat(result.metadata["extracted_at"]))

            self.logger.info(f"✅ NPM hook extraction completed: {len(result.data)} hooks extracted")
            return result

        except Exception as e:
            error_msg = f"NPM hook extraction failed: {e}"
            self.logger.error(error_msg)
            return ExtractionResult(
                success=False,
                data=[],
                metadata={"extractor": "npm_hooks", "source_name": self.source_name},
                errors=[error_msg],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

    async def _fetch_package_metadata(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch package metadata from NPM registry"""
        try:
            if not self.session:
                return None

            url = f"{self.npm_api_base}/{package_name}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    self.logger.warning(f"Package not found: {package_name}")
                    return None
                else:
                    self.logger.error(f"NPM API error: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch package metadata: {e}")
            return None

    async def _check_package_exists(self, package_name: str) -> bool:
        """Check if package exists on NPM"""
        try:
            metadata = await self._fetch_package_metadata(package_name)
            return metadata is not None
        except Exception:
            return False

    def _is_valid_package_name(self, package_name: str) -> bool:
        """Validate NPM package name format"""
        if not package_name or not isinstance(package_name, str):
            return False

        # Basic NPM package name validation
        # https://www.npmjs.com/package/validate-npm-package-name
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        return bool(re.match(pattern, package_name))

    async def _extract_hooks_from_package(self, package_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract hooks from package metadata and files"""
        hooks = []

        try:
            package_name = package_metadata.get("name", "")
            package_version = package_metadata.get("dist-tags", {}).get("latest", "")

            # Get package files
            package_files = await self._fetch_package_files(package_name, package_version)
            if not package_files:
                return hooks

            # Find hook files
            hook_files = self._find_hook_files(package_files)
            if not hook_files:
                return hooks

            # Analyze each hook file
            for file_info in hook_files:
                try:
                    file_hooks = await self._analyze_hook_file(file_info, package_metadata)
                    hooks.extend(file_hooks)
                except Exception as e:
                    self.logger.error(f"Failed to analyze hook file {file_info.get('path', 'unknown')}: {e}")

            return hooks

        except Exception as e:
            self.logger.error(f"Failed to extract hooks from package: {e}")
            return hooks

    async def _fetch_package_files(self, package_name: str, version: str) -> Optional[Dict[str, Any]]:
        """Fetch package file structure from NPM CDN"""
        try:
            if not self.session:
                return None

            # Try to get package.json first
            package_json_url = f"{self.npm_cdn_base}/{package_name}@{version}/package.json"
            async with self.session.get(package_json_url) as response:
                if response.status == 200:
                    package_json = await response.json()
                    return package_json
                else:
                    self.logger.warning(f"Failed to fetch package.json: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch package files: {e}")
            return None

    def _find_hook_files(self, package_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential hook files in package"""
        hook_files = []

        try:
            # Look for files in main/export fields
            main_file = package_json.get("main", "")
            if main_file and self._is_hook_file(main_file):
                hook_files.append({"path": main_file, "type": "main"})

            # Look in module field
            module_file = package_json.get("module", "")
            if module_file and self._is_hook_file(module_file):
                hook_files.append({"path": module_file, "type": "module"})

            # Look in exports field
            exports = package_json.get("exports", {})
            if isinstance(exports, dict):
                for export_key, export_value in exports.items():
                    if isinstance(export_value, str) and self._is_hook_file(export_value):
                        hook_files.append({"path": export_value, "type": f"export.{export_key}"})
                    elif isinstance(export_value, dict):
                        for import_key, import_value in export_value.items():
                            if isinstance(import_value, str) and self._is_hook_file(import_value):
                                hook_files.append({"path": import_value, "type": f"export.{export_key}.{import_key}"})

            # Look in types field
            types_file = package_json.get("types", "")
            if types_file and self._is_hook_file(types_file):
                hook_files.append({"path": types_file, "type": "types"})

            # Look in files field
            files = package_json.get("files", [])
            for file_path in files:
                if self._is_hook_file(file_path):
                    hook_files.append({"path": file_path, "type": "files"})

            return hook_files

        except Exception as e:
            self.logger.error(f"Failed to find hook files: {e}")
            return []

    def _is_hook_file(self, file_path: str) -> bool:
        """Check if file is likely to contain hooks"""
        if not file_path:
            return False

        hook_indicators = [
            "hook", "hooks", "use-", "Use", "HOOK",
            ".ts", ".js", ".tsx", ".jsx"
        ]

        file_lower = file_path.lower()
        return any(indicator in file_lower for indicator in hook_indicators)

    async def _analyze_hook_file(self, file_info: Dict[str, Any], package_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a hook file and extract hook information"""
        hooks = []

        try:
            file_path = file_info.get("path", "")
            package_name = package_metadata.get("name", "")
            package_version = package_metadata.get("dist-tags", {}).get("latest", "")

            # Fetch file content
            content = await self._fetch_file_content(package_name, package_version, file_path)
            if not content:
                return hooks

            # Extract hooks from content
            if file_path.endswith(".d.ts"):
                hooks.extend(self._extract_hooks_from_typescript(content, file_path))
            elif file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
                hooks.extend(self._extract_hooks_from_javascript(content, file_path))

            return hooks

        except Exception as e:
            self.logger.error(f"Failed to analyze hook file: {e}")
            return hooks

    async def _fetch_file_content(self, package_name: str, version: str, file_path: str) -> Optional[str]:
        """Fetch file content from NPM CDN"""
        try:
            if not self.session:
                return None

            url = f"{self.npm_cdn_base}/{package_name}@{version}/{file_path}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"Failed to fetch file {file_path}: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch file content: {e}")
            return None

    def _extract_hooks_from_typescript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract hooks from TypeScript definitions"""
        hooks = []

        try:
            # Look for hook export patterns
            patterns = [
                r'export\s+(?:const|function|async\s+function)\s+(use\w+)\s*[:=]',
                r'export\s+default\s+(?:const|function|async\s+function)\s+(use\w+)\s*[:=]',
                r'declare\s+(?:const|function)\s+(use\w+)\s*[:=]',
                r'export\s*{\s*([^}]+use\w+)[^}]*}',
                r'(?:const|function|async\s+function)\s+(use\w+)\s*[=:]'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        hook_name = match[0] if match[0] else match[1]
                    else:
                        hook_name = match

                    if hook_name and hook_name.startswith("use"):
                        hook_info = self._parse_hook_from_typescript(hook_name, content, file_path)
                        if hook_info:
                            hooks.append(hook_info)

            return hooks

        except Exception as e:
            self.logger.error(f"Failed to extract hooks from TypeScript: {e}")
            return hooks

    def _extract_hooks_from_javascript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract hooks from JavaScript/TypeScript source code"""
        hooks = []

        try:
            # Look for hook patterns
            patterns = [
                r'export\s+(?:const|function|async\s+function)\s+(use\w+)\s*[=(]',
                r'export\s+default\s+(?:const|function|async\s+function)\s+(use\w+)\s*[=(]',
                r'(?:const|function|async\s+function)\s+(use\w+)\s*[=(]'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for hook_name in matches:
                    if hook_name.startswith("use"):
                        hook_info = self._parse_hook_from_javascript(hook_name, content, file_path)
                        if hook_info:
                            hooks.append(hook_info)

            return hooks

        except Exception as e:
            self.logger.error(f"Failed to extract hooks from JavaScript: {e}")
            return hooks

    def _parse_hook_from_typescript(self, hook_name: str, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse hook information from TypeScript definitions"""
        try:
            # Extract hook signature
            signature = self._extract_hook_signature(hook_name, content)

            # Extract JSDoc comments
            jsdoc = self._extract_jsdoc(hook_name, content)

            # Extract dependencies
            dependencies = self._extract_hook_dependencies(content)

            return {
                "name": hook_name,
                "description": jsdoc.get("description", ""),
                "signature": signature,
                "parameters": jsdoc.get("parameters", []),
                "returns": jsdoc.get("returns", ""),
                "examples": jsdoc.get("examples", []),
                "dependencies": dependencies,
                "file_path": file_path,
                "type": "typescript"
            }

        except Exception as e:
            self.logger.error(f"Failed to parse hook from TypeScript: {e}")
            return None

    def _parse_hook_from_javascript(self, hook_name: str, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse hook information from JavaScript source code"""
        try:
            # Extract function signature
            signature = self._extract_hook_signature(hook_name, content)

            # Extract JSDoc comments
            jsdoc = self._extract_jsdoc(hook_name, content)

            # Extract dependencies
            dependencies = self._extract_hook_dependencies(content)

            return {
                "name": hook_name,
                "description": jsdoc.get("description", ""),
                "signature": signature,
                "parameters": jsdoc.get("parameters", []),
                "returns": jsdoc.get("returns", ""),
                "examples": jsdoc.get("examples", []),
                "dependencies": dependencies,
                "file_path": file_path,
                "type": "javascript"
            }

        except Exception as e:
            self.logger.error(f"Failed to parse hook from JavaScript: {e}")
            return None

    def _extract_hook_signature(self, hook_name: str, content: str) -> str:
        """Extract hook function signature"""
        try:
            # Find hook declaration
            patterns = [
                rf'(?:export\s+)?(?:const|function|async\s+function)\s+{hook_name}\s*[:=]\s*(.+)',
                rf'declare\s+(?:const|function)\s+{hook_name}\s*[:=]\s*(.+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    signature = match.group(1).strip()
                    # Clean up signature
                    signature = re.sub(r'\s+', ' ', signature)
                    signature = re.sub(r';.*', '', signature)
                    return signature[:200]  # Limit length

            return f"function {hook_name}()"

        except Exception as e:
            self.logger.error(f"Failed to extract hook signature: {e}")
            return f"function {hook_name}()"

    def _extract_jsdoc(self, hook_name: str, content: str) -> Dict[str, Any]:
        """Extract JSDoc comments for hook"""
        jsdoc = {
            "description": "",
            "parameters": [],
            "returns": "",
            "examples": []
        }

        try:
            # Find JSDoc comment before hook
            jsdoc_pattern = rf'/\*\*([^*]+|\*[^/])*\*/\s*(?:export\s+)?(?:const|function|async\s+function)\s+{hook_name}'
            match = re.search(jsdoc_pattern, content, re.DOTALL)

            if match:
                jsdoc_text = match.group(0)

                # Extract description
                desc_pattern = r'/\*\*\s*\n\s*\*\s*([^@\n]+)'
                desc_match = re.search(desc_pattern, jsdoc_text)
                if desc_match:
                    jsdoc["description"] = desc_match.group(1).strip()

                # Extract parameters
                param_pattern = r'@param\s+{([^}]+)}\s+(\w+)\s+([^\n@]+)'
                param_matches = re.findall(param_pattern, jsdoc_text)
                for param_type, param_name, param_desc in param_matches:
                    jsdoc["parameters"].append({
                        "name": param_name,
                        "type": param_type,
                        "description": param_desc.strip()
                    })

                # Extract return value
                return_pattern = r'@returns?\s+{([^}]+)}\s+([^\n@]+)'
                return_match = re.search(return_pattern, jsdoc_text)
                if return_match:
                    jsdoc["returns"] = return_match.group(2).strip()

                # Extract examples
                example_pattern = r'@example\s+([^\n@]+(?:\n\s*\*[^\n@]*)*)'
                example_matches = re.findall(example_pattern, jsdoc_text)
                for example in example_matches:
                    # Clean up example code
                    example = re.sub(r'^\s*\*\s*', '', example, flags=re.MULTILINE)
                    example = example.strip()
                    if example:
                        jsdoc["examples"].append(example)

            return jsdoc

        except Exception as e:
            self.logger.error(f"Failed to extract JSDoc: {e}")
            return jsdoc

    def _extract_hook_dependencies(self, content: str) -> List[str]:
        """Extract hook dependencies from content"""
        dependencies = []

        try:
            # Look for React hook usage patterns
            react_hooks = [
                "useState", "useEffect", "useContext", "useReducer", "useCallback",
                "useMemo", "useRef", "useLayoutEffect", "useImperativeHandle",
                "useDebugValue", "useDeferredValue", "useTransition", "useId"
            ]

            for hook in react_hooks:
                if re.search(rf'\b{hook}\b', content):
                    dependencies.append(f"react/{hook}")

            # Look for import statements
            import_pattern = r'import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"]'
            import_matches = re.findall(import_pattern, content)

            for imports, source in import_matches:
                for imp in [i.strip() for i in imports.split(",")]:
                    if imp.startswith("use"):
                        dependencies.append(f"{source}/{imp}")

            return list(set(dependencies))

        except Exception as e:
            self.logger.error(f"Failed to extract hook dependencies: {e}")
            return dependencies

    async def _extract_single_hook(self, hook_info: Dict[str, Any], package_metadata: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Extract a single hook with full metadata"""
        try:
            hook_name = hook_info.get("name", "")
            if not hook_name:
                return None

            self.logger.info(f"🔧 Extracting hook: {hook_name}")

            # Get package information
            package_name = package_metadata.get("name", "")
            package_version = package_metadata.get("dist-tags", {}).get("latest", "")

            # Fetch additional documentation
            documentation = await self._fetch_hook_documentation(hook_info, package_metadata)

            # Calculate quality score
            quality_score = self._calculate_hook_quality_score(hook_info, package_metadata, documentation)

            # Create hook signature
            hook_signature = HookSignature(
                signature=hook_info.get("signature", f"function {hook_name}()"),
                generics=[],
                return_types={"return": hook_info.get("returns", "any")},
                parameters=hook_info.get("parameters", []),
                type_parameters=[]
            )

            # Create usage examples
            usage_examples = self._create_usage_examples(hook_info, documentation)

            # Create extracted component
            extracted_component = ExtractedComponent(
                name=hook_name,
                category=ComponentCategory.HOOKS,
                type=ComponentType.HOOK,
                registry="npm",
                priority_source=self.source_name,
                sources=[self.source_name],
                display_name=hook_name.replace("-", " ").title(),
                description=hook_info.get("description", f"NPM hook: {hook_name}"),
                dependencies=hook_info.get("dependencies", []),
                installation=f"npm install {package_name}",
                platform=["reactjs"],
                framework="react",
                quality_score=quality_score,
                usage_examples=usage_examples,
                category_specific_data={
                    "hook_signature": hook_signature.to_dict(),
                    "package_name": package_name,
                    "package_version": package_version,
                    "file_path": hook_info.get("file_path", ""),
                    "hook_type": hook_info.get("type", "unknown")
                }
            )

            # Add source metadata
            extracted_component.add_source_metadata(
                self.source_name,
                SourceMetadata(
                    source_name=self.source_name,
                    extracted_at=datetime.now(),
                    package_version=package_version,
                    url=f"https://www.npmjs.com/package/{package_name}",
                    extraction_metadata={
                        "hook_file": hook_info.get("file_path", ""),
                        "has_documentation": len(documentation) > 0,
                        "jsdoc_complete": len(hook_info.get("parameters", [])) > 0
                    }
                )
            )

            return extracted_component

        except Exception as e:
            self.logger.error(f"Failed to extract single hook {hook_info.get('name', 'unknown')}: {e}")
            return None

    async def _fetch_hook_documentation(self, hook_info: Dict[str, Any], package_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch additional documentation for hook"""
        documentation = {}

        try:
            package_name = package_metadata.get("name", "")

            # Get README from package metadata
            readme = package_metadata.get("readme", "")
            if readme:
                documentation["readme"] = readme

            # Get repository URL
            repository = package_metadata.get("repository", {})
            if isinstance(repository, dict):
                repo_url = repository.get("url", "")
            elif isinstance(repository, str):
                repo_url = repository
            else:
                repo_url = ""

            if repo_url:
                documentation["repository"] = repo_url

            # Get homepage
            homepage = package_metadata.get("homepage", "")
            if homepage:
                documentation["homepage"] = homepage

            return documentation

        except Exception as e:
            self.logger.error(f"Failed to fetch hook documentation: {e}")
            return documentation

    def _create_usage_examples(self, hook_info: Dict[str, Any], documentation: Dict[str, Any]) -> List[UsageExample]:
        """Create usage examples for hook"""
        usage_examples = []

        try:
            hook_name = hook_info.get("name", "")

            # Add examples from JSDoc
            jsdoc_examples = hook_info.get("examples", [])
            for example in jsdoc_examples:
                usage_example = UsageExample(
                    title=f"Example usage of {hook_name}",
                    code=example,
                    language="typescript",
                    difficulty="intermediate"
                )
                usage_examples.append(usage_example)

            # If no examples, create basic example
            if not usage_examples:
                basic_example = UsageExample(
                    title=f"Basic {hook_name} usage",
                    code=f"const {hook_name} = require('{hook_info.get('package_name', 'package')}');\n// Use {hook_name} here",
                    language="typescript",
                    difficulty="beginner"
                )
                usage_examples.append(basic_example)

            return usage_examples

        except Exception as e:
            self.logger.error(f"Failed to create usage examples: {e}")
            return usage_examples

    def _calculate_hook_quality_score(self, hook_info: Dict[str, Any], package_metadata: Dict[str, Any], documentation: Dict[str, Any]) -> float:
        """Calculate quality score for hook"""
        score = 0.5  # Base score

        try:
            # Description quality
            description = hook_info.get("description", "")
            if description and len(description) > 20:
                score += 0.1

            # Documentation completeness
            if hook_info.get("parameters"):
                score += 0.1
            if hook_info.get("returns"):
                score += 0.1
            if hook_info.get("examples"):
                score += 0.1

            # Package popularity
            weekly_downloads = package_metadata.get("downloads", {}).get("last_week", 0)
            if weekly_downloads > 1000000:
                score += 0.2
            elif weekly_downloads > 100000:
                score += 0.15
            elif weekly_downloads > 10000:
                score += 0.1

            # Package maintenance
            maintainers = len(package_metadata.get("maintainers", []))
            if maintainers > 0:
                score += min(0.1, maintainers * 0.05)

            # Dependencies (fewer = better)
            dependencies = hook_info.get("dependencies", [])
            if len(dependencies) <= 2:
                score += 0.1
            elif len(dependencies) <= 5:
                score += 0.05

            return min(1.0, max(0.0, score))

        except Exception as e:
            self.logger.error(f"Failed to calculate quality score: {e}")
            return score