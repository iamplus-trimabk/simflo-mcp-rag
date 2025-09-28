"""
Community Extractor

Specialized extractor for community-contributed components and hooks.
Performs security scanning, quality assessment, license validation,
and code standardization for community submissions.
"""

import asyncio
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import ast
import subprocess
import tempfile
import os

from .github_cli_base import GitHubCLIBaseExtractor
from .base_extractor import ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata, UsageExample

logger = logging.getLogger(__name__)


class SecurityVulnerability:
    """Represents a security vulnerability found in code"""

    def __init__(self, severity: str, type: str, description: str, line_number: Optional[int] = None):
        self.severity = severity  # "critical", "high", "medium", "low"
        self.type = type
        self.description = description
        self.line_number = line_number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "type": self.type,
            "description": self.description,
            "line_number": self.line_number
        }


class CodeQualityMetrics:
    """Metrics for code quality assessment"""

    def __init__(self):
        self.complexity_score: float = 0.0
        self.maintainability_index: float = 100.0
        self.test_coverage: float = 0.0
        self.documentation_score: float = 0.0
        self.best_practices_violations: List[str] = []
        self.code_smells: List[str] = []
        self.style_issues: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "complexity_score": self.complexity_score,
            "maintainability_index": self.maintainability_index,
            "test_coverage": self.test_coverage,
            "documentation_score": self.documentation_score,
            "best_practices_violations": self.best_practices_violations,
            "code_smells": self.code_smells,
            "style_issues": self.style_issues
        }


class LicenseInfo:
    """Information about software license"""

    def __init__(self, license_name: str, spdx_id: str, is_compatible: bool, restrictions: List[str]):
        self.license_name = license_name
        self.spdx_id = spdx_id
        self.is_compatible = is_compatible
        self.restrictions = restrictions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "license_name": self.license_name,
            "spdx_id": self.spdx_id,
            "is_compatible": self.is_compatible,
            "restrictions": self.restrictions
        }


class CommunityExtractor(GitHubCLIBaseExtractor):
    """Specialized extractor for community-contributed components"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.supported_types = ["component", "hook", "utility", "block"]

        # Security patterns
        self.security_patterns = self._initialize_security_patterns()

        # Compatible licenses
        self.compatible_licenses = {
            "MIT": True,
            "Apache-2.0": True,
            "BSD-2-Clause": True,
            "BSD-3-Clause": True,
            "ISC": True,
            "Unlicense": True,
            "CC0-1.0": True,
            "WTFPL": True
        }

    def get_supported_types(self) -> List[str]:
        """Get supported component types"""
        return self.supported_types


    def _initialize_security_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize security vulnerability detection patterns"""
        return {
            "eval_usage": [
                re.compile(r'eval\s*\([^)]*\)', re.IGNORECASE),
                re.compile(r'Function\s*\([^)]*\)', re.IGNORECASE)
            ],
            "innerHTML": [
                re.compile(r'innerHTML\s*=', re.IGNORECASE),
                re.compile(r'outerHTML\s*=', re.IGNORECASE)
            ],
            "dangerous_globals": [
                re.compile(r'window\[.*\]\s*=', re.IGNORECASE),
                re.compile(r'document\.write\s*\(', re.IGNORECASE)
            ],
            "crypto_misuse": [
                re.compile(r'Math\.random\s*\(\)', re.IGNORECASE),
                re.compile(r'crypto\.getRandomValues\s*\([^)]*\)', re.IGNORECASE)
            ],
            "sql_injection": [
                re.compile(r'execute\s*\(\s*[\'"][^\'"]*\s*\+\s*[^\'"]*[\'"]', re.IGNORECASE),
                re.compile(r'query\s*\(\s*[\'"][^\'"]*\s*\+\s*[^\'"]*[\'"]', re.IGNORECASE)
            ],
            "xss_vectors": [
                re.compile(r'document\.cookie\s*=', re.IGNORECASE),
                re.compile(r'location\.href\s*=', re.IGNORECASE)
            ]
        }

    def validate_source(self) -> bool:
        """Validate community source configuration"""
        try:
            # Use GitHub CLI base validation
            if not super().validate_source():
                return False

            # Validate URL format
            url = self.source_config.get("url", "")
            if not self._is_valid_url(url):
                self.logger.error(f"Invalid URL format: {url}")
                return False

            self.logger.info(f"✅ Community source validation passed: {self.source_name}")
            return True

        except Exception as e:
            self.logger.error(f"Community source validation failed: {e}")
            return False

    async def extract(self) -> ExtractionResult:
        """Extract community components with security and quality assessment"""
        try:
            self.logger.info(f"🚀 Starting community extraction from {self.name}")

            # Initialize result
            result = ExtractionResult(
                success=True,
                data=[],
                metadata={
                    "extractor": "community",
                    "source_name": self.name,
                    "extracted_at": datetime.now().isoformat(),
                    "total_components": 0,
                    "security_issues": 0,
                    "quality_issues": 0
                },
                errors=[],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

            # Repository is already cloned by GitHubCLIBaseExtractor
            # Use repository info from base class
            source_info = {
                "type": "github",
                "repo_data": self.repo_info,
                "url": self.repo_url,
                "repo_path": f"{self._parse_repo_identifier()['owner']}/{self._parse_repo_identifier()['repo']}"
            }

            # Find component files locally
            component_files = self._find_component_files_local()
            if not component_files:
                result.warnings.append("No component files found")
                return result

            self.logger.info(f"📦 Found {len(component_files)} component files")

            # Process each component file
            for file_info in component_files:
                try:
                    extracted_component = await self._extract_community_component(file_info, source_info)
                    if extracted_component:
                        result.data.append(extracted_component)
                except Exception as e:
                    error_msg = f"Failed to extract component from {file_info.get('path', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)

            # Aggregate security and quality metrics
            result.metadata["total_components"] = len(result.data)
            result.metadata["security_issues"] = self._count_security_issues(result.data)
            result.metadata["quality_issues"] = self._count_quality_issues(result.data)
            result.metadata["extraction_time"] = str(datetime.now() - datetime.fromisoformat(result.metadata["extracted_at"]))

            self.logger.info(f"✅ Community extraction completed: {len(result.data)} components extracted")
            return result

        except Exception as e:
            error_msg = f"Community extraction failed: {e}"
            logger.error(error_msg)
            return ExtractionResult(
                success=False,
                data=[],
                metadata={"extractor": "community", "source_name": self.name},
                errors=[error_msg],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

    def _find_component_files_local(self) -> List[Dict[str, Any]]:
        """Find component files in the local repository"""
        component_files = []

        try:
            # Look for component file patterns
            patterns = [
                "src/components/**/*.tsx",
                "src/components/**/*.ts",
                "src/hooks/**/*.ts",
                "src/hooks/**/*.tsx",
                "src/lib/**/*.ts",
                "src/utils/**/*.ts",
                "components/**/*.tsx",
                "hooks/**/*.ts",
                "lib/**/*.ts",
                "utils/**/*.ts"
            ]

            for pattern in patterns:
                try:
                    files = self._find_files_by_pattern(pattern)
                    for file_path in files:
                        component_files.append({
                            "path": str(file_path.relative_to(self.repo_path)),
                            "type": self._determine_file_type(str(file_path))
                        })
                except Exception:
                    continue

            return component_files

        except Exception as e:
            logger.error(f"Failed to find component files: {e}")
            return []

    def _determine_file_type(self, file_path: str) -> str:
        """Determine component type from file path"""
        file_lower = file_path.lower()
        if "hook" in file_lower:
            return "hook"
        elif "block" in file_lower or "layout" in file_lower:
            return "block"
        elif "util" in file_lower or "helper" in file_lower:
            return "utility"
        else:
            return "component"

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False



    async def _extract_community_component(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Extract a single community component with full analysis"""
        try:
            file_path = file_info.get("path", "")
            file_type = file_info.get("type", "unknown")

            self.logger.info(f"🔧 Extracting community component: {file_path}")

            # Fetch file content locally
            content = self._fetch_file_content_local(file_info.get("path", ""))
            if not content:
                return None

            # Perform security analysis
            security_vulnerabilities = await self._analyze_security(content, file_path)

            # Perform quality analysis
            quality_metrics = await self._analyze_quality(content, file_path)

            # Extract license information
            license_info = self._extract_license_info(source_info)

            # Standardize code format
            standardized_content = await self._standardize_code(content)

            # Extract component metadata
            component_metadata = await self._extract_component_metadata(standardized_content, file_path)

            # Calculate overall quality score
            quality_score = self._calculate_community_quality_score(
                security_vulnerabilities, quality_metrics, license_info, component_metadata
            )

            # Determine component type
            component_type = self._determine_component_type(file_path, content)

            # Create extracted component
            extracted_component = ExtractedComponent(
                name=component_metadata.get("name", Path(file_path).stem),
                category=self._determine_category(component_type),
                type=component_type,
                sources=[self.repo_url],
                priority_source=self.repo_url,
                description=component_metadata.get("description", f"Community component: {Path(file_path).stem}"),
                dependencies=component_metadata.get("dependencies", []),
                peer_dependencies=[],
                installation=component_metadata.get("installation", ""),
                usage_examples=component_metadata.get("usage_examples", []),
                metadata={
                    "security_vulnerabilities": [v.to_dict() for v in security_vulnerabilities],
                    "quality_metrics": quality_metrics.to_dict(),
                    "license_info": license_info.to_dict(),
                    "standardization_applied": True,
                    "source_file": file_path,
                    "original_metadata": component_metadata,
                    "repository": self.repo_info
                },
                quality_score=quality_score,
                last_updated=datetime.now(),
                platform=["reactjs"],
                registry="community"
            )

            return extracted_component

        except Exception as e:
            self.logger.error(f"Failed to extract community component: {e}")
            return None

    def _fetch_file_content_local(self, file_path: str) -> Optional[str]:
        """Fetch file content from local repository"""
        try:
            return self._read_local_file(file_path)
        except Exception as e:
            logger.error(f"Failed to fetch local file content: {e}")
            return None

    async def _analyze_security(self, content: str, file_path: str) -> List[SecurityVulnerability]:
        """Analyze code for security vulnerabilities"""
        vulnerabilities = []

        try:
            lines = content.split('\n')

            for line_number, line in enumerate(lines, 1):
                # Check each security pattern
                for vuln_type, patterns in self.security_patterns.items():
                    for pattern in patterns:
                        if pattern.search(line):
                            severity = self._determine_vulnerability_severity(vuln_type)
                            description = f"Potential {vuln_type} vulnerability detected"
                            vulnerabilities.append(
                                SecurityVulnerability(severity, vuln_type, description, line_number)
                            )

            # Additional security checks
            vulnerabilities.extend(await self._perform_advanced_security_checks(content))

            return vulnerabilities

        except Exception as e:
            self.logger.error(f"Failed to analyze security: {e}")
            return vulnerabilities

    def _determine_vulnerability_severity(self, vuln_type: str) -> str:
        """Determine severity level for vulnerability type"""
        severity_map = {
            "eval_usage": "critical",
            "innerHTML": "high",
            "dangerous_globals": "high",
            "crypto_misuse": "medium",
            "sql_injection": "critical",
            "xss_vectors": "high"
        }
        return severity_map.get(vuln_type, "medium")

    async def _perform_advanced_security_checks(self, content: str) -> List[SecurityVulnerability]:
        """Perform additional security checks"""
        vulnerabilities = []

        try:
            # Check for hardcoded secrets
            secret_patterns = [
                r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']',
                r'password\s*=\s*["\'][^"\']{6,}["\']',
                r'secret\s*=\s*["\'][^"\']{10,}["\']'
            ]

            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append(
                        SecurityVulnerability("high", "hardcoded_secrets", "Potential hardcoded secret detected")
                    )

            # Check for dangerous imports
            dangerous_imports = [
                r'import\s+.*\s+from\s+["\']child_process["\']',
                r'import\s+.*\s+from\s+["\']fs["\']',
                r'require\s*\(\s*["\']child_process["\']\)',
                r'require\s*\(\s*["\']fs["\']\)'
            ]

            for pattern in dangerous_imports:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append(
                        SecurityVulnerability("medium", "dangerous_import", "Potentially dangerous module import")
                    )

            return vulnerabilities

        except Exception as e:
            self.logger.error(f"Failed to perform advanced security checks: {e}")
            return vulnerabilities

    async def _analyze_quality(self, content: str, file_path: str) -> CodeQualityMetrics:
        """Analyze code quality metrics"""
        metrics = CodeQualityMetrics()

        try:
            # Basic complexity analysis
            metrics.complexity_score = self._calculate_complexity(content)

            # Documentation analysis
            metrics.documentation_score = self._analyze_documentation(content)

            # Best practices analysis
            metrics.best_practices_violations = self._check_best_practices(content)

            # Code style analysis
            metrics.style_issues = self._check_code_style(content)

            # Estimate maintainability index
            metrics.maintainability_index = self._calculate_maintainability(metrics)

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to analyze quality: {e}")
            return metrics

    def _calculate_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        try:
            complexity_keywords = [
                "if", "else if", "else", "for", "while", "do", "switch", "case",
                "try", "catch", "finally", "&&", "||", "?"
            ]

            complexity = 1  # Base complexity
            for keyword in complexity_keywords:
                complexity += len(re.findall(rf'\b{keyword}\b', content))

            # Normalize to 0-1 scale
            return min(1.0, complexity / 50.0)

        except Exception:
            return 0.5

    def _analyze_documentation(self, content: str) -> float:
        """Analyze documentation quality"""
        try:
            lines = content.split('\n')
            total_lines = len(lines)

            if total_lines == 0:
                return 0.0

            # Count comment lines
            comment_lines = 0
            jsdoc_blocks = re.findall(r'/\*\*.*?\*/', content, re.DOTALL)
            comment_blocks = re.findall(r'/\*.*?\*/', content, re.DOTALL)
            line_comments = re.findall(r'//.*$', content, re.MULTILINE)

            comment_lines += sum(len(block.split('\n')) for block in jsdoc_blocks)
            comment_lines += sum(len(block.split('\n')) for block in comment_blocks)
            comment_lines += len(line_comments)

            # Calculate documentation ratio
            doc_ratio = comment_lines / total_lines
            return min(1.0, doc_ratio * 2)  # Cap at 1.0

        except Exception:
            return 0.0

    def _check_best_practices(self, content: str) -> List[str]:
        """Check for best practices violations"""
        violations = []

        try:
            # Check for console.log in production code
            if re.search(r'console\.(log|warn|error)', content):
                violations.append("Console statements found")

            # Check for var usage
            if re.search(r'\bvar\s+', content):
                violations.append("var keyword usage (prefer const/let)")

            # Check for empty catch blocks
            if re.search(r'catch\s*\([^)]*\)\s*{\s*}', content):
                violations.append("Empty catch block")

            # Check for long functions (basic heuristic)
            function_lengths = []
            functions = re.findall(r'(?:function\s+\w+\s*\([^)]*\)|\w+\s*=\s*\([^)]*\)\s*=>|class\s+\w+)[^}]*\{(?:[^{}]*\{[^}]*\})*[^}]*\}', content, re.DOTALL)
            for func in functions:
                lines = func.split('\n')
                if len(lines) > 50:
                    violations.append(f"Long function detected ({len(lines)} lines)")

            return violations

        except Exception as e:
            self.logger.error(f"Failed to check best practices: {e}")
            return []

    def _check_code_style(self, content: str) -> List[str]:
        """Check for code style issues"""
        style_issues = []

        try:
            # Check for mixed tabs and spaces
            has_tabs = '\t' in content
            has_spaces = any(line.startswith('  ') for line in content.split('\n'))
            if has_tabs and has_spaces:
                style_issues.append("Mixed tabs and spaces")

            # Check for trailing whitespace
            trailing_lines = [line for line in content.split('\n') if line.rstrip() != line]
            if len(trailing_lines) > len(content.split('\n')) * 0.1:  # More than 10%
                style_issues.append("Trailing whitespace found")

            # Check for inconsistent naming
            camel_case = re.findall(r'\b[a-z][a-zA-Z0-9]*\b', content)
            snake_case = re.findall(r'\b[a-z][a-z0-9_]*\b', content)

            # Basic inconsistency check
            if camel_case and snake_case:
                style_issues.append("Inconsistent naming conventions detected")

            return style_issues

        except Exception as e:
            self.logger.error(f"Failed to check code style: {e}")
            return []

    def _calculate_maintainability(self, metrics: CodeQualityMetrics) -> float:
        """Calculate maintainability index"""
        try:
            # Simple maintainability calculation
            maintainability = 100.0

            # Reduce based on complexity
            maintainability -= metrics.complexity_score * 30

            # Reduce based on documentation
            maintainability -= (1.0 - metrics.documentation_score) * 20

            # Reduce based on best practices violations
            maintainability -= len(metrics.best_practices_violations) * 5

            # Reduce based on style issues
            maintainability -= len(metrics.style_issues) * 2

            return max(0.0, min(100.0, maintainability))

        except Exception:
            return 50.0

    def _extract_license_info(self, source_info: Dict[str, Any]) -> LicenseInfo:
        """Extract license information"""
        try:
            # Get license from repository info (fetched by GitHub CLI)
            license_name = "Unknown"
            spdx_id = "UNKNOWN"
            is_compatible = False
            restrictions = []

            repo_data = self.repo_info or {}
            license_info = repo_data.get("license")

            if license_info and isinstance(license_info, dict):
                license_name = license_info.get("name", "Unknown")
                spdx_id = license_info.get("spdx_id", "UNKNOWN")
            elif license_info and isinstance(license_info, str):
                license_name = license_info
                spdx_id = license_name

            # Check compatibility
            is_compatible = self.compatible_licenses.get(license_name, False)

            # Get restrictions based on license type
            restrictions = self._get_license_restrictions(license_name)

            return LicenseInfo(license_name, spdx_id, is_compatible, restrictions)

        except Exception as e:
            logger.error(f"Failed to extract license info: {e}")
            return LicenseInfo("Unknown", "UNKNOWN", False, ["Unknown license restrictions"])

    def _get_license_restrictions(self, license_name: str) -> List[str]:
        """Get restrictions for a given license"""
        restrictions_map = {
            "MIT": ["Include license and copyright notice"],
            "Apache-2.0": ["Include license", "State changes", "Include copyright notice"],
            "GPL": ["Disclose source", "Same license", "Include copyright notice"],
            "LGPL": ["Include license", "Disclose source modifications"],
            "BSD": ["Include license and copyright notice", "No endorsement"]
        }
        return restrictions_map.get(license_name, ["Unknown restrictions"])

    async def _standardize_code(self, content: str) -> str:
        """Standardize code format"""
        try:
            # Basic code standardization
            standardized = content

            # Remove excessive blank lines
            standardized = re.sub(r'\n\s*\n\s*\n', '\n\n', standardized)

            # Ensure consistent spacing around operators
            standardized = re.sub(r'([=+\-*/])', r' \1 ', standardized)
            standardized = re.sub(r'\s+', ' ', standardized)

            # Standardize quotes (prefer single quotes)
            standardized = re.sub(r'"([^"]*)"', r"'\1'", standardized)

            return standardized

        except Exception as e:
            self.logger.error(f"Failed to standardize code: {e}")
            return content

    async def _extract_component_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract component metadata"""
        metadata = {
            "name": Path(file_path).stem,
            "display_name": Path(file_path).stem.replace("-", " ").title(),
            "description": "",
            "dependencies": [],
            "installation": "",
            "usage_examples": []
        }

        try:
            # Extract component name from file
            file_name = Path(file_path).stem

            # Look for JSDoc comments
            jsdoc_pattern = r'/\*\*([^*]+|\*[^/])*\*/'
            jsdoc_matches = re.findall(jsdoc_pattern, content, re.DOTALL)

            for jsdoc in jsdoc_matches:
                # Extract description
                desc_pattern = r'/\*\*\s*\n\s*\*\s*([^@\n]+)'
                desc_match = re.search(desc_pattern, jsdoc)
                if desc_match:
                    metadata["description"] = desc_match.group(1).strip()
                    break

            # Extract imports for dependencies
            import_pattern = r'import\s+.*\s+from\s+["\']([^"\']+)["\']'
            imports = re.findall(import_pattern, content)
            metadata["dependencies"] = list(set(imports))

            # Extract export information
            export_pattern = r'export\s+(?:default\s+)?(?:function|const|class)\s+(\w+)'
            export_match = re.search(export_pattern, content)
            if export_match:
                metadata["name"] = export_match.group(1)
                metadata["display_name"] = re.sub(r'([A-Z])', r' \1', export_match.group(1)).title().strip()

            return metadata

        except Exception as e:
            self.logger.error(f"Failed to extract component metadata: {e}")
            return metadata

    def _determine_component_type(self, file_path: str, content: str) -> ComponentType:
        """Determine component type"""
        try:
            file_lower = file_path.lower()

            if "hook" in file_lower or any(hook in content for hook in ["useState", "useEffect", "useContext"]):
                return ComponentType.HOOK
            elif "block" in file_lower or "layout" in file_lower:
                return ComponentType.BLOCK
            elif "util" in file_lower or "helper" in file_lower:
                return ComponentType.UTILITY
            else:
                return ComponentType.UI

        except Exception:
            return ComponentType.UI

    def _determine_category(self, component_type: ComponentType) -> ComponentCategory:
        """Determine component category"""
        category_map = {
            ComponentType.HOOK: ComponentCategory.HOOKS,
            ComponentType.BLOCK: ComponentCategory.BLOCKS,
            ComponentType.UI: ComponentCategory.COMPONENTS,
            ComponentType.UTILITY: ComponentCategory.COMPONENTS
        }
        return category_map.get(component_type, ComponentCategory.COMPONENTS)

    def _calculate_community_quality_score(self,
                                           security_vulnerabilities: List[SecurityVulnerability],
                                           quality_metrics: CodeQualityMetrics,
                                           license_info: LicenseInfo,
                                           component_metadata: Dict[str, Any]) -> float:
        """Calculate overall quality score for community component"""
        score = 0.5  # Base score

        try:
            # Security impact (critical: -0.4, high: -0.3, medium: -0.2, low: -0.1)
            for vuln in security_vulnerabilities:
                severity_penalties = {"critical": 0.4, "high": 0.3, "medium": 0.2, "low": 0.1}
                score -= severity_penalties.get(vuln.severity, 0.1)

            # Quality metrics impact
            score += quality_metrics.maintainability_index / 200.0  # 0-0.5
            score += quality_metrics.documentation_score * 0.2  # 0-0.2

            # License compatibility
            if license_info.is_compatible:
                score += 0.1
            else:
                score -= 0.2

            # Metadata completeness
            if component_metadata.get("description"):
                score += 0.05
            if component_metadata.get("dependencies"):
                score += 0.05

            return max(0.0, min(1.0, score))

        except Exception as e:
            self.logger.error(f"Failed to calculate community quality score: {e}")
            return max(0.0, score)

    def _count_security_issues(self, components: List[Dict[str, Any]]) -> int:
        """Count total security issues"""
        total = 0
        for component in components:
            sec_data = component.get("category_specific_data", {}).get("security_vulnerabilities", [])
            total += len(sec_data)
        return total

    def _count_quality_issues(self, components: List[Dict[str, Any]]) -> int:
        """Count total quality issues"""
        total = 0
        for component in components:
            quality_data = component.get("category_specific_data", {}).get("quality_metrics", {})
            violations = len(quality_data.get("best_practices_violations", []))
            style_issues = len(quality_data.get("style_issues", []))
            total += violations + style_issues
        return total