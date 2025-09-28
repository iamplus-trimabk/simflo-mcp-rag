"""
Community Extractor

Specialized extractor for community-contributed components and hooks.
Performs security scanning, quality assessment, license validation,
and code standardization for community submissions.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import ast
import subprocess
import tempfile
import os

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent
from models.component_models import Component, ComponentCategory, ComponentType, SourceMetadata, UsageExample


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


class CommunityExtractor(BaseExtractor):
    """Specialized extractor for community-contributed components"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.supported_types = ["component", "hook", "utility", "block"]
        self.github_api_base = "https://api.github.com"
        self.github_raw_base = "https://raw.githubusercontent.com"
        self.session: Optional[aiohttp.ClientSession] = None

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

    async def __aenter__(self):
        """Initialize async context"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context"""
        if self.session:
            await self.session.close()

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

    async def validate_source(self) -> bool:
        """Validate community source configuration"""
        try:
            # Check required fields
            required_fields = ["url", "extractor"]
            for field in required_fields:
                if field not in self.source_config:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate URL format
            url = self.source_config.get("url", "")
            if not self._is_valid_url(url):
                self.logger.error(f"Invalid URL format: {url}")
                return False

            # Check if source is accessible
            is_accessible = await self._check_source_accessibility(url)
            if not is_accessible:
                self.logger.error(f"Source not accessible: {url}")
                return False

            self.logger.info(f"✅ Community source validation passed: {self.source_name}")
            return True

        except Exception as e:
            self.logger.error(f"Community source validation failed: {e}")
            return False

    async def extract(self) -> ExtractionResult:
        """Extract community components with security and quality assessment"""
        try:
            self.logger.info(f"🚀 Starting community extraction from {self.source_name}")

            # Initialize result
            result = ExtractionResult(
                success=True,
                data=[],
                metadata={
                    "extractor": "community",
                    "source_name": self.source_name,
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

            # Fetch repository/package information
            source_info = await self._fetch_source_info()
            if not source_info:
                result.success = False
                result.errors.append("Failed to fetch source information")
                return result

            # Find component files
            component_files = await self._find_component_files(source_info)
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
                    self.logger.error(error_msg)

            # Aggregate security and quality metrics
            result.metadata["total_components"] = len(result.data)
            result.metadata["security_issues"] = self._count_security_issues(result.data)
            result.metadata["quality_issues"] = self._count_quality_issues(result.data)
            result.metadata["extraction_time"] = str(datetime.now() - datetime.fromisoformat(result.metadata["extracted_at"]))

            self.logger.info(f"✅ Community extraction completed: {len(result.data)} components extracted")
            return result

        except Exception as e:
            error_msg = f"Community extraction failed: {e}"
            self.logger.error(error_msg)
            return ExtractionResult(
                success=False,
                data=[],
                metadata={"extractor": "community", "source_name": self.source_name},
                errors=[error_msg],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )

    async def _fetch_source_info(self) -> Optional[Dict[str, Any]]:
        """Fetch source repository/package information"""
        try:
            url = self.source_config.get("url", "")
            source_type = self.source_config.get("type", "github")

            if source_type == "github":
                return await self._fetch_github_repo_info(url)
            elif source_type == "npm":
                return await self._fetch_npm_package_info(url)
            elif source_type == "api":
                return await self._fetch_api_source_info(url)
            else:
                self.logger.error(f"Unsupported source type: {source_type}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to fetch source info: {e}")
            return None

    async def _fetch_github_repo_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch GitHub repository information"""
        try:
            if not self.session:
                return None

            # Extract owner/repo from URL
            repo_path = url.replace("https://github.com/", "").replace("https://www.github.com/", "")
            if repo_path.endswith("/"):
                repo_path = repo_path[:-1]

            api_url = f"{self.github_api_base}/repos/{repo_path}"
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    repo_data = await response.json()

                    # Fetch README
                    readme_url = f"{self.github_api_base}/repos/{repo_path}/readme"
                    async with self.session.get(readme_url) as readme_response:
                        readme_content = ""
                        if readme_response.status == 200:
                            readme_data = await readme_response.json()
                            import base64
                            readme_content = base64.b64decode(readme_data["content"]).decode('utf-8')

                    return {
                        "type": "github",
                        "repo_data": repo_data,
                        "readme": readme_content,
                        "url": url,
                        "repo_path": repo_path
                    }
                else:
                    self.logger.error(f"GitHub API error: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch GitHub repo info: {e}")
            return None

    async def _fetch_npm_package_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch NPM package information"""
        try:
            if not self.session:
                return None

            # Extract package name from URL or use directly
            package_name = self.source_config.get("package", "")
            if not package_name:
                # Try to extract from URL
                if "npmjs.com/package/" in url:
                    package_name = url.split("npmjs.com/package/")[-1]
                else:
                    package_name = url.split("/")[-1]

            npm_api_url = f"https://registry.npmjs.org/{package_name}"
            async with self.session.get(npm_api_url) as response:
                if response.status == 200:
                    package_data = await response.json()
                    return {
                        "type": "npm",
                        "package_data": package_data,
                        "url": url,
                        "package_name": package_name
                    }
                else:
                    self.logger.error(f"NPM API error: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch NPM package info: {e}")
            return None

    async def _fetch_api_source_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch information from generic API source"""
        try:
            if not self.session:
                return None

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "type": "api",
                        "data": data,
                        "url": url
                    }
                else:
                    self.logger.error(f"API error: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch API source info: {e}")
            return None

    async def _check_source_accessibility(self, url: str) -> bool:
        """Check if source is accessible"""
        try:
            if not self.session:
                return False

            async with self.session.get(url) as response:
                return response.status < 400

        except Exception:
            return False

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    async def _find_component_files(self, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find component files in the source"""
        component_files = []

        try:
            source_type = source_info.get("type")

            if source_type == "github":
                component_files = await self._find_github_components(source_info)
            elif source_type == "npm":
                component_files = await self._find_npm_components(source_info)
            elif source_type == "api":
                component_files = await self._find_api_components(source_info)

            return component_files

        except Exception as e:
            self.logger.error(f"Failed to find component files: {e}")
            return []

    async def _find_github_components(self, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find component files in GitHub repository"""
        component_files = []

        try:
            repo_path = source_info.get("repo_path", "")
            default_branch = source_info.get("repo_data", {}).get("default_branch", "main")

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
                    files = await self._fetch_github_files(repo_path, default_branch, pattern)
                    component_files.extend(files)
                except Exception:
                    continue

            return component_files

        except Exception as e:
            self.logger.error(f"Failed to find GitHub components: {e}")
            return []

    async def _fetch_github_files(self, repo_path: str, branch: str, pattern: str) -> List[Dict[str, Any]]:
        """Fetch files from GitHub repository matching pattern"""
        files = []

        try:
            if not self.session:
                return files

            # This is a simplified implementation
            # In a real implementation, you would use GitHub's search API or tree API
            # For now, we'll return some mock files based on the pattern
            mock_files = [
                {"path": "src/components/MyComponent.tsx", "type": "component"},
                {"path": "src/hooks/useCustomHook.ts", "type": "hook"},
                {"path": "src/utils/helper.ts", "type": "utility"}
            ]

            return mock_files

        except Exception as e:
            self.logger.error(f"Failed to fetch GitHub files: {e}")
            return []

    async def _find_npm_components(self, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find component files in NPM package"""
        component_files = []

        try:
            package_data = source_info.get("package_data", {})

            # Look at main, module, and exports fields
            main_file = package_data.get("main", "")
            if main_file and self._is_component_file(main_file):
                component_files.append({"path": main_file, "type": "main"})

            module_file = package_data.get("module", "")
            if module_file and self._is_component_file(module_file):
                component_files.append({"path": module_file, "type": "module"})

            return component_files

        except Exception as e:
            self.logger.error(f"Failed to find NPM components: {e}")
            return []

    async def _find_api_components(self, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find component files from API source"""
        component_files = []

        try:
            data = source_info.get("data", {})

            # Look for component definitions in API response
            if "components" in data:
                for component in data["components"]:
                    if "file" in component:
                        component_files.append({
                            "path": component["file"],
                            "type": "api",
                            "data": component
                        })

            return component_files

        except Exception as e:
            self.logger.error(f"Failed to find API components: {e}")
            return []

    def _is_component_file(self, file_path: str) -> bool:
        """Check if file is likely a component file"""
        component_extensions = [".ts", ".tsx", ".js", ".jsx"]
        component_indicators = ["component", "hook", "util", "lib"]

        file_lower = file_path.lower()
        return (
            any(file_path.endswith(ext) for ext in component_extensions) and
            any(indicator in file_lower for indicator in component_indicators)
        )

    async def _extract_community_component(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[ExtractedComponent]:
        """Extract a single community component with full analysis"""
        try:
            file_path = file_info.get("path", "")
            file_type = file_info.get("type", "unknown")

            self.logger.info(f"🔧 Extracting community component: {file_path}")

            # Fetch file content
            content = await self._fetch_file_content(file_info, source_info)
            if not content:
                return None

            # Perform security analysis
            security_vulnerabilities = await self._analyze_security(content, file_path)

            # Perform quality analysis
            quality_metrics = await self._analyze_quality(content, file_path)

            # Extract license information
            license_info = await self._extract_license_info(source_info)

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
                registry="community",
                priority_source=self.source_name,
                sources=[self.source_name],
                display_name=component_metadata.get("display_name", Path(file_path).stem.replace("-", " ").title()),
                description=component_metadata.get("description", f"Community component: {Path(file_path).stem}"),
                dependencies=component_metadata.get("dependencies", []),
                installation=component_metadata.get("installation", ""),
                platform=["reactjs"],
                framework="react",
                quality_score=quality_score,
                usage_examples=component_metadata.get("usage_examples", []),
                category_specific_data={
                    "security_vulnerabilities": [v.to_dict() for v in security_vulnerabilities],
                    "quality_metrics": quality_metrics.to_dict(),
                    "license_info": license_info.to_dict(),
                    "standardization_applied": True,
                    "source_file": file_path,
                    "original_metadata": component_metadata
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
                        "security_issues": len(security_vulnerabilities),
                        "quality_score": quality_metrics.maintainability_index,
                        "license_compatible": license_info.is_compatible,
                        "standardized": True
                    }
                )
            )

            return extracted_component

        except Exception as e:
            self.logger.error(f"Failed to extract community component: {e}")
            return None

    async def _fetch_file_content(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[str]:
        """Fetch file content from source"""
        try:
            source_type = source_info.get("type")

            if source_type == "github":
                return await self._fetch_github_file_content(file_info, source_info)
            elif source_type == "npm":
                return await self._fetch_npm_file_content(file_info, source_info)
            elif source_type == "api":
                return await self._fetch_api_file_content(file_info, source_info)

            return None

        except Exception as e:
            self.logger.error(f"Failed to fetch file content: {e}")
            return None

    async def _fetch_github_file_content(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[str]:
        """Fetch file content from GitHub"""
        try:
            if not self.session:
                return None

            repo_path = source_info.get("repo_path", "")
            default_branch = source_info.get("repo_data", {}).get("default_branch", "main")
            file_path = file_info.get("path", "")

            raw_url = f"{self.github_raw_base}/{repo_path}/{default_branch}/{file_path}"
            async with self.session.get(raw_url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.error(f"Failed to fetch GitHub file: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch GitHub file content: {e}")
            return None

    async def _fetch_npm_file_content(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[str]:
        """Fetch file content from NPM package"""
        try:
            if not self.session:
                return None

            package_name = source_info.get("package_name", "")
            package_version = source_info.get("package_data", {}).get("dist-tags", {}).get("latest", "")
            file_path = file_info.get("path", "")

            url = f"https://unpkg.com/{package_name}@{package_version}/{file_path}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.error(f"Failed to fetch NPM file: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch NPM file content: {e}")
            return None

    async def _fetch_api_file_content(self, file_info: Dict[str, Any], source_info: Dict[str, Any]) -> Optional[str]:
        """Fetch file content from API source"""
        try:
            # For API sources, the content might be in the file_info
            return file_info.get("content", "")

        except Exception as e:
            self.logger.error(f"Failed to fetch API file content: {e}")
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

    async def _extract_license_info(self, source_info: Dict[str, Any]) -> LicenseInfo:
        """Extract license information"""
        try:
            source_type = source_info.get("type")
            license_name = "Unknown"
            spdx_id = "UNKNOWN"
            is_compatible = False
            restrictions = []

            if source_type == "github":
                repo_data = source_info.get("repo_data", {})
                license_info = repo_data.get("license")

                if license_info and isinstance(license_info, dict):
                    license_name = license_info.get("name", "Unknown")
                    spdx_id = license_info.get("spdx_id", "UNKNOWN")
                elif license_info and isinstance(license_info, str):
                    license_name = license_info
                    spdx_id = license_info

            elif source_type == "npm":
                package_data = source_info.get("package_data", {})
                license_name = package_data.get("license", "Unknown")
                spdx_id = license_name

            # Check compatibility
            is_compatible = self.compatible_licenses.get(license_name, False)

            # Get restrictions based on license type
            restrictions = self._get_license_restrictions(license_name)

            return LicenseInfo(license_name, spdx_id, is_compatible, restrictions)

        except Exception as e:
            self.logger.error(f"Failed to extract license info: {e}")
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