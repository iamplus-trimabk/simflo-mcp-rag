"""
Shadcn Hooks Extractor

Specialized extractor for React hooks from shadcn/ui repositories.
Handles hook-specific patterns, dependencies, and metadata extraction.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, HookSignature, SourceMetadata

logger = logging.getLogger(__name__)

class ShadcnHooksExtractor(BaseExtractor):
    """Specialized extractor for shadcn/ui hooks"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.registry_file = source_config.get("registry_file", "")

    def validate_source(self) -> bool:
        """Validate source configuration for this extractor"""
        if self.source_config.get("type") != "github":
            return False

        required_fields = ["url", "branch", "registry_file"]
        for field in required_fields:
            if not self.source_config.get(field):
                self.logger.error(f"Missing required field: {field}")
                return False

        # Validate GitHub URL format
        url = self.source_config["url"]
        if not (url.startswith("https://github.com/shadcn-ui/") or url.startswith("https://github.com/shadcn/")):
            self.logger.error(f"Invalid shadcn GitHub URL: {url}")
            return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return ["hook"]

    async def extract(self) -> ExtractionResult:
        """Extract hooks from shadcn/ui repository"""
        self.log_extraction_start()

        try:
            # Get registry file content
            registry_content = await self._fetch_registry_file()
            if not registry_content:
                return self.create_extraction_result(
                    success=False,
                    errors=["Failed to fetch registry file"]
                )

            # Parse registry to get hook list
            hook_configs = self._parse_registry(registry_content)
            if not hook_configs:
                return self.create_extraction_result(
                    success=False,
                    errors=["No hooks found in registry"]
                )

            # Extract detailed information for each hook
            hooks = []
            for hook_config in hook_configs:
                try:
                    hook = await self._extract_hook_details(hook_config)
                    if hook:
                        hooks.append(hook)
                except Exception as e:
                    self.logger.warning(f"Failed to extract hook {hook_config.get('name', 'unknown')}: {e}")
                    continue

            return self.create_extraction_result(
                success=True,
                data=[hook.to_dict() for hook in hooks],
                metadata={
                    "total_hooks": len(hooks),
                    "registry_file": self.source_config["registry_file"],
                    "repository": self.source_config["url"],
                    "branch": self.source_config["branch"]
                }
            )

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return self.create_extraction_result(
                success=False,
                errors=[f"Extraction error: {str(e)}"]
            )

    async def _fetch_registry_file(self) -> Optional[str]:
        """Fetch the hooks registry file from GitHub"""
        url = self.source_config["url"]
        branch = self.source_config["branch"]
        registry_file = self.source_config["registry_file"]

        # Construct raw GitHub URL
        raw_url = url.replace("github.com", "raw.githubusercontent.com")
        raw_url = f"{raw_url}/{branch}/{registry_file}"

        self.logger.info(f"Fetching registry file from: {raw_url}")

        content = await self.fetch_content(raw_url)
        if content:
            self.logger.info(f"Successfully fetched registry file ({len(content)} characters)")
        return content

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
        deps_patterns = [
            r'dependencies:\s*\[([^\]]+)\]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import.*from\s*[\'"]([^\'"]+)[\'"]'
        ]

        dependencies = []
        for pattern in deps_patterns:
            deps_matches = re.finditer(pattern, context)
            for match in deps_matches:
                deps = match.group(1)
                if deps:
                    # Clean up dependency names
                    deps = re.sub(r'["\']', '', deps)
                    deps = [dep.strip() for dep in deps.split(',') if dep.strip()]
                    dependencies.extend(deps)

        if dependencies:
            hook_config["dependencies"] = list(set(dependencies))

        # Extract installation command
        if "description" not in hook_config:
            hook_config["description"] = f"React hook: {hook_name}"

        return hook_config

    async def _extract_hook_details(self, hook_config: Dict[str, Any]) -> Optional[Component]:
        """Extract detailed information for a single hook"""
        hook_name = hook_config["name"]

        try:
            # Get hook file content
            file_content = await self._fetch_hook_file(hook_name)
            if not file_content:
                return None

            # Parse hook code
            hook_details = self._parse_hook_code(hook_name, file_content)

            # Create component object
            component = Component(
                name=hook_name,
                category=ComponentCategory.HOOKS,
                type=ComponentType.HOOK,
                registry="shadcn",
                sources=[self.source_name],
                priority_source=self.source_name,
                description=hook_config.get("description", f"React hook: {hook_name}"),
                dependencies=hook_details.get("dependencies", []),
                installation=f"npx shadcn@latest add {hook_name}",
                platform=["reactjs"],
                quality_score=hook_details.get("quality_score", 0.7),
                last_updated=datetime.now()
            )

            # Add category-specific data
            component.category_specific_data = {
                "hook_signature": hook_details.get("signature"),
                "return_types": hook_details.get("return_types"),
                "parameters": hook_details.get("parameters"),
                "generics": hook_details.get("generics", []),
                "custom_logic": hook_details.get("custom_logic", [])
            }

            # Add usage examples
            if hook_details.get("usage_examples"):
                for example in hook_details["usage_examples"]:
                    component.usage_examples.append(example)

            # Add source metadata
            source_metadata = SourceMetadata(
                source_name=self.source_name,
                extracted_at=datetime.now(),
                version="latest",
                url=self.source_config["url"],
                extraction_metadata={
                    "registry_file": self.source_config["registry_file"],
                    "branch": self.source_config["branch"]
                }
            )
            component.add_source_metadata(self.source_name, source_metadata)

            return component

        except Exception as e:
            self.logger.error(f"Failed to extract details for hook {hook_name}: {e}")
            return None

    async def _fetch_hook_file(self, hook_name: str) -> Optional[str]:
        """Fetch the actual hook implementation file"""
        # Convert hook name to file path
        # Example: use-form -> src/hooks/use-form.ts
        hook_file_path = f"src/hooks/ui/{hook_name}.tsx"

        url = self.source_config["url"]
        branch = self.source_config["branch"]

        # Construct raw GitHub URL
        raw_url = url.replace("github.com", "raw.githubusercontent.com")
        raw_url = f"{raw_url}/{branch}/{hook_file_path}"

        self.logger.debug(f"Fetching hook file from: {raw_url}")

        content = await self.fetch_content(raw_url)
        if content:
            self.logger.debug(f"Successfully fetched hook file {hook_name} ({len(content)} characters)")
        return content

    def _parse_hook_code(self, hook_name: str, content: str) -> Dict[str, Any]:
        """Parse hook implementation code to extract details"""
        details = {
            "dependencies": [],
            "signature": None,
            "return_types": {},
            "parameters": [],
            "generics": [],
            "usage_examples": [],
            "quality_score": 0.7,
            "custom_logic": []
        }

        try:
            # Extract hook signature
            signature_pattern = rf'(?:export\s+)?(?:const|function)\s+{re.escape(hook_name)}\s*(<[^>]+>)?\s*\(([^)]*)\)'
            signature_match = re.search(signature_pattern, content)
            if signature_match:
                generics = signature_match.group(1)
                params = signature_match.group(2)

                details["signature"] = signature_match.group(0)
                details["generics"] = self._parse_generics(generics) if generics else []
                details["parameters"] = self._parse_parameters(params)

            # Extract return type if available
            return_pattern = rf'{re.escape(hook_name)}\s*:\s*([^;\n]+)'
            return_match = re.search(return_pattern, content)
            if return_match:
                details["return_types"] = {"main": return_match.group(1).strip()}

            # Extract dependencies from imports
            details["dependencies"] = self._extract_hook_dependencies(content)

            # Extract JSDoc comments for usage examples
            details["usage_examples"] = self._extract_usage_examples(content)

            # Analyze hook complexity for quality scoring
            complexity_score = self._analyze_hook_complexity(content)
            details["quality_score"] = min(1.0, 0.5 + complexity_score * 0.5)

            # Extract custom logic patterns
            details["custom_logic"] = self._extract_custom_logic(content)

        except Exception as e:
            self.logger.warning(f"Error parsing hook code for {hook_name}: {e}")

        return details

    def _parse_generics(self, generics_str: str) -> List[str]:
        """Parse TypeScript generics from string"""
        if not generics_str:
            return []

        # Remove angle brackets and split
        generics = generics_str.strip('<>')
        return [g.strip() for g in generics_str.split(',') if g.strip()]

    def _parse_parameters(self, params_str: str) -> List[Dict[str, Any]]:
        """Parse function parameters"""
        if not params_str:
            return []

        parameters = []
        param_parts = [p.strip() for p in params_str.split(',') if p.strip()]

        for param in param_parts:
            param_info = {"name": "", "type": "any", "optional": False}

            # Handle optional parameters
            if param.endswith('?'):
                param_info["optional"] = True
                param = param[:-1].strip()

            # Split parameter name and type
            if ':' in param:
                name, type_info = param.split(':', 1)
                param_info["name"] = name.strip()
                param_info["type"] = type_info.strip()
            else:
                param_info["name"] = param.strip()

            # Handle default values
            if '=' in param_info["name"]:
                name, default = param_info["name"].split('=', 1)
                param_info["name"] = name.strip()
                param_info["default"] = default.strip()

            parameters.append(param_info)

        return parameters

    def _extract_hook_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from hook code"""
        dependencies = []

        # Import patterns
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)'
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)

        # Look for hook calls within the hook (composition)
        hook_calls = re.findall(r'(use\w+)\s*\(', content)
        dependencies.extend(hook_calls)

        # Clean and deduplicate
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]
        dependencies = [dep for dep in dependencies if not dep.startswith('.')]  # Remove relative imports

        return list(set(dependencies))

    def _extract_usage_examples(self, content: str) -> List[Any]:
        """Extract usage examples from JSDoc comments"""
        examples = []

        # Look for @example tags in JSDoc
        example_pattern = r'@example\s*([^\n@]+(?:\n[^@]+)*)'
        matches = re.findall(example_pattern, content)

        for match in matches:
            example = match.strip()
            if example:
                # Try to find code blocks within the example
                code_blocks = re.findall(r'```(?:typescript|tsx|javascript|js)\n([\s\S]*?)\n```', example)
                if code_blocks:
                    for code in code_blocks:
                        examples.append({
                            "title": "Usage Example",
                            "code": code.strip(),
                            "language": "typescript"
                        })
                else:
                    # Use the example as-is
                    examples.append({
                        "title": "Usage Example",
                        "code": example,
                        "language": "markdown"
                    })

        return examples

    def _analyze_hook_complexity(self, content: str) -> float:
        """Analyze hook complexity for quality scoring"""
        score = 0.0
        max_score = 1.0

        # Length complexity (longer hooks are more complex)
        lines = content.split('\n')
        if len(lines) > 10:
            score += 0.1
        if len(lines) > 20:
            score += 0.1

        # Control flow complexity
        control_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bswitch\b', r'\btry\b', r'\bcatch\b'
        ]

        for pattern in control_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            score += min(0.2, len(matches) * 0.05)

        # Hook composition (using other hooks)
        hook_usage = len(re.findall(r'\b(use\w+)\s*\(', content))
        score += min(0.3, hook_usage * 0.1)

        # Type annotations (better quality)
        type_annotations = len(re.findall(r':\s*\w+', content))
        score += min(0.2, type_annotations * 0.02)

        # Comments and documentation
        comments = len(re.findall(r'\/\/|\/\*', content))
        score += min(0.2, comments * 0.02)

        return min(score, max_score)

    def _extract_custom_logic(self, content: str) -> List[str]:
        """Extract custom logic patterns from hook"""
        logic_patterns = []

        # Look for common hook patterns
        patterns = [
            (r'useEffect\([^)]+\)', "Side effects"),
            (r'useState\([^)]+\)', "State management"),
            (r'useRef\([^)]+\)', "References"),
            (r'useMemo\([^)]+\)', "Memoization"),
            (r'useCallback\([^)]+\)', "Callback optimization"),
            (r'useContext\([^)]+\)', "Context consumption"),
            (r'useReducer\([^)]+\)', "Reducer pattern"),
            (r'addEventListener\([^)]+\)', "Event handling"),
            (r'setTimeout|setInterval', "Timing operations"),
            (r'fetch\(|axios\.', "API calls"),
            (r'localStorage|sessionStorage', "Storage operations")
        ]

        for pattern, description in patterns:
            if re.search(pattern, content):
                logic_patterns.append(description)

        return logic_patterns

    def calculate_quality_score(self, component: Dict[str, Any]) -> float:
        """Override quality score calculation for hooks"""
        base_score = super().calculate_quality_score(component)

        # Hook-specific quality factors
        hook_score = 0.0

        # Signature completeness
        if component.get("signature"):
            hook_score += 0.2

        # Return type information
        if component.get("return_types"):
            hook_score += 0.1

        # Parameter documentation
        params = component.get("parameters", [])
        if params:
            hook_score += min(0.2, len(params) * 0.05)

        # Usage examples
        examples = component.get("usage_examples", [])
        if examples:
            hook_score += min(0.3, len(examples) * 0.15)

        # Generics support
        generics = component.get("generics", [])
        if generics:
            hook_score += 0.1

        # Custom logic patterns
        custom_logic = component.get("custom_logic", [])
        if custom_logic:
            hook_score += min(0.1, len(custom_logic) * 0.02)

        return min(1.0, base_score + hook_score)

    def validate_component(self, component: Dict[str, Any]) -> List[str]:
        """Validate hook component with hook-specific rules"""
        errors = super().validate_component(component)

        # Hook-specific validation
        name = component.get("name", "")
        if not self._is_hook_name(name):
            errors.append(f"Invalid hook name: {name}. Must start with 'use-' or 'use'")

        # Check for required hook fields
        if not component.get("signature"):
            errors.append("Hook signature is required")

        # Validate hook dependencies
        dependencies = component.get("dependencies", [])
        for dep in dependencies:
            if dep.startswith("use-") or dep.startswith("use"):
                # Validate that hook dependencies are valid
                if not self._is_hook_name(dep):
                    errors.append(f"Invalid hook dependency: {dep}")

        return errors

    async def validate_repository(self) -> bool:
        """Validate that the GitHub repository is accessible"""
        try:
            # Try to fetch the registry file to validate repository access
            content = await self.fetch_content(self.registry_file)
            if content:
                self.logger.info(f"Repository validation successful for {self.source_name}")
                return True
            else:
                self.logger.warning(f"Repository validation failed for {self.source_name}: Could not fetch registry file")
                return False
        except Exception as e:
            self.logger.error(f"Repository validation failed for {self.source_name}: {e}")
            return False