"""
Enhanced Extractor Factory with Smart Selection

A factory that can create and manage both specialized and language-based extractors.
Implements smart selection: specialized extractors first, then language-based fallbacks.
"""

import sys
import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SimpleExtractorFactory:
    """Enhanced factory with specialized + language-based extractor support"""

    def __init__(self):
        self._extractors = {}
        self._specialized_extractors = set()  # Track specialized vs language-based
        self._register_extractors()

    def _register_extractors(self):
        """Register both specialized and language-based extractors"""

        # === SPECIALIZED EXTRACTORS (High Quality) ===
        try:
            from shadcn_extractor import SimpleShadcnExtractor
            self._extractors["shadcn"] = SimpleShadcnExtractor
            self._specialized_extractors.add("shadcn")
            logger.info("Registered shadcn specialized extractor")
        except ImportError as e:
            logger.error(f"Failed to register shadcn extractor: {e}")

        try:
            from gluestack_extractor_simple import SimpleGluestackExtractor
            self._extractors["gluestack"] = SimpleGluestackExtractor
            self._specialized_extractors.add("gluestack")
            logger.info("Registered gluestack specialized extractor")
        except ImportError as e:
            logger.error(f"Failed to register gluestack extractor: {e}")

        # === LANGUAGE-BASED FALLBACK EXTRACTORS (Good Quality) ===
        try:
            from typescript_extractor import TypescriptExtractor
            self._extractors["typescript"] = TypescriptExtractor
            logger.info("Registered typescript language-based extractor")
        except ImportError as e:
            logger.error(f"Failed to register typescript extractor: {e}")

        try:
            from python_extractor import PythonExtractor
            self._extractors["python"] = PythonExtractor
            logger.info("Registered python language-based extractor")
        except ImportError as e:
            logger.error(f"Failed to register python extractor: {e}")

        try:
            from language_documentation_extractor import LanguageDocumentationExtractor
            self._extractors["language-documentation"] = LanguageDocumentationExtractor
            logger.info("Registered language-documentation language-based extractor")
        except ImportError as e:
            logger.error(f"Failed to register language-documentation extractor: {e}")

        try:
            from configuration_extractor import ConfigurationExtractor
            self._extractors["configuration"] = ConfigurationExtractor
            logger.info("Registered configuration language-based extractor")
        except ImportError as e:
            logger.error(f"Failed to register configuration extractor: {e}")

    def get_available_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available extractors with type classification"""
        extractors_info = {}

        for name, extractor_class in self._extractors.items():
            try:
                # Create a temporary instance to get info
                temp_instance = extractor_class()
                info = temp_instance.get_extractor_info()
                # Add classification
                info["is_specialized"] = name in self._specialized_extractors
                info["priority"] = "high" if name in self._specialized_extractors else "good"
                extractors_info[name] = info
            except Exception as e:
                extractors_info[name] = {
                    "name": name,
                    "type": "extractor",
                    "error": f"Failed to get extractor info: {e}",
                    "class": extractor_class.__name__ if extractor_class else "Failed to load",
                    "is_specialized": name in self._specialized_extractors,
                    "priority": "unknown"
                }

        return extractors_info

    def get_specialized_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Get only specialized extractors (high quality)"""
        specialized = {}
        all_extractors = self.get_available_extractors()
        for name, info in all_extractors.items():
            if info.get("is_specialized", False):
                specialized[name] = info
        return specialized

    def get_language_based_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Get only language-based extractors (good quality fallbacks)"""
        language_based = {}
        all_extractors = self.get_available_extractors()
        for name, info in all_extractors.items():
            if not info.get("is_specialized", False):
                language_based[name] = info
        return language_based

    def detect_repository_type(self, repo_url: str) -> Dict[str, Any]:
        """Detect repository type and recommend extractors"""
        repo_name = self._parse_repository_name(repo_url)

        # Check for specialized extractors first
        specialized_match = self._check_specialized_match(repo_name, repo_url)
        if specialized_match:
            return {
                "repository": repo_name,
                "repository_url": repo_url,
                "recommended_extractor": specialized_match,
                "extraction_type": "specialized",
                "quality": "high",
                "confidence": 1.0,
                "reason": f"Direct match for {specialized_match} specialized extractor"
            }

        # No specialized match - detect language-based extractors
        language_matches = self._detect_language_based_extractors(repo_url)

        if language_matches:
            # Return the best match
            best_match = language_matches[0]
            return {
                "repository": repo_name,
                "repository_url": repo_url,
                "recommended_extractor": best_match["name"],
                "extraction_type": "language-based",
                "quality": "good",
                "confidence": best_match["confidence"],
                "reason": best_match["reason"],
                "alternative_extractors": language_matches[1:3]  # Top alternatives
            }

        # No match found
        return {
            "repository": repo_name,
            "repository_url": repo_url,
            "recommended_extractor": None,
            "extraction_type": "none",
            "quality": "unknown",
            "confidence": 0.0,
            "reason": "No suitable extractor found",
            "available_extractors": list(self._extractors.keys())
        }

    def _parse_repository_name(self, repo_url: str) -> str:
        """Parse repository URL to get repository name"""
        patterns = [
            r'github\.com/([^/]+/[^/]+?)(?:\.git)?/?$',
            r'([^/]+/[^/]+)$',
        ]

        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1).strip('/')

        return repo_url

    def _check_specialized_match(self, repo_name: str, repo_url: str) -> Optional[str]:
        """Check if repository matches any specialized extractor"""
        repo_lower = repo_name.lower()

        # Shadcn specialized patterns
        shadcn_patterns = [
            "shadcn-ui/ui",
            "shadcn/ui",
            "shadcn-ui",
        ]
        if any(pattern in repo_lower for pattern in shadcn_patterns):
            return "shadcn"

        # Gluestack specialized patterns
        gluestack_patterns = [
            "gluestack/gluestack-ui",
            "gluestack-ui",
        ]
        if any(pattern in repo_lower for pattern in gluestack_patterns):
            return "gluestack"

        return None

    def _detect_language_based_extractors(self, repo_url: str) -> List[Dict[str, Any]]:
        """Detect appropriate language-based extractors for repository"""
        repo_name = self._parse_repository_name(repo_url)
        repo_lower = repo_name.lower()

        matches = []

        # TypeScript/JavaScript patterns
        typescript_patterns = [
            "typescript", "javascript", "react", "vue", "angular", "next",
            "nuxt", "svelte", "gatsby", "remix", "astro", "playwright",
            "testing-library", "jest", "mocha", "webpack", "vite",
            "node", "npm", "yarn", "pnpm", "deno", "bun"
        ]
        typescript_score = sum(1 for pattern in typescript_patterns if pattern in repo_lower)
        if typescript_score > 0:
            matches.append({
                "name": "typescript",
                "confidence": min(0.9, 0.3 + typescript_score * 0.2),
                "reason": f"Repository appears to be TypeScript/JavaScript based (score: {typescript_score})"
            })

        # Python patterns
        python_patterns = [
            "python", "django", "flask", "fastapi", "pytest", "pandas",
            "numpy", "tensorflow", "pytorch", "scipy", "requests"
        ]
        python_score = sum(1 for pattern in python_patterns if pattern in repo_lower)
        if python_score > 0:
            matches.append({
                "name": "python",
                "confidence": min(0.9, 0.3 + python_score * 0.2),
                "reason": f"Repository appears to be Python based (score: {python_score})"
            })

        # Documentation patterns (almost always applicable)
        matches.append({
            "name": "language-documentation",
            "confidence": 0.5,
            "reason": "Documentation extractor for markdown files"
        })

        # Configuration patterns (almost always applicable)
        matches.append({
            "name": "configuration",
            "confidence": 0.4,
            "reason": "Configuration extractor for config files"
        })

        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def smart_extract(self, repo_url: str, force_extractor: Optional[str] = None) -> Dict[str, Any]:
        """Smart extraction with automatic extractor selection"""
        if force_extractor:
            # Use forced extractor
            return self.run_extractor(force_extractor, repo_url)

        # Auto-detect best extractor
        detection = self.detect_repository_type(repo_url)

        if not detection["recommended_extractor"]:
            return {
                "success": False,
                "error": "No suitable extractor found",
                "detection": detection,
                "timestamp": "2025-10-02T00:00:00.000000"
            }

        extractor_name = detection["recommended_extractor"]

        try:
            result = self.run_extractor(extractor_name, repo_url)
            result["detection"] = detection
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Extraction failed: {str(e)}",
                "detection": detection,
                "timestamp": "2025-10-02T00:00:00.000000"
            }

    def run_all_applicable_extractors(self, repo_url: str) -> Dict[str, Any]:
        """Run all applicable extractors for a repository"""
        detection = self.detect_repository_type(repo_url)

        if detection["extraction_type"] == "specialized":
            # For specialized repositories, run specialized + language-based for completeness
            extractors_to_run = [detection["recommended_extractor"]]

            # Add language-based extractors
            language_matches = self._detect_language_based_extractors(repo_url)
            extractors_to_run.extend([match["name"] for match in language_matches[:2]])  # Top 2 language-based

        else:
            # For language-based, run the top language-based extractors
            extractors_to_run = [detection["recommended_extractor"]]
            if detection.get("alternative_extractors"):
                extractors_to_run.extend([alt["name"] for alt in detection["alternative_extractors"][:2]])

        results = []
        for extractor_name in extractors_to_run:
            try:
                result = self.run_extractor(extractor_name, repo_url)
                results.append(result)
            except Exception as e:
                results.append({
                    "extractor": extractor_name,
                    "error": str(e),
                    "success": False
                })

        return {
            "success": True,
            "repository": detection["repository"],
            "repository_url": repo_url,
            "extraction_strategy": detection["extraction_type"],
            "extractors_run": extractors_to_run,
            "results": results,
            "total_extractors": len(extractors_to_run),
            "successful_extractions": len([r for r in results if r.get("success", True) and "error" not in r]),
            "timestamp": "2025-10-02T00:00:00.000000"
        }

    def create_extractor(self, extractor_name: str, source_config: Optional[Dict[str, Any]] = None):
        """Create an extractor instance"""
        if extractor_name not in self._extractors:
            raise ValueError(f"Extractor '{extractor_name}' not found. Available: {list(self._extractors.keys())}")

        try:
            extractor_class = self._extractors[extractor_name]
            return extractor_class(source_config)
        except Exception as e:
            logger.error(f"Failed to create extractor {extractor_name}: {e}")
            raise

    def run_extractor(self, extractor_name: str, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Run an extractor and return results"""
        try:
            extractor = self.create_extractor(extractor_name)
            return extractor.extract(repo_url)
        except Exception as e:
            return {
                "extractor": extractor_name,
                "error": str(e),
                "timestamp": "2025-10-01T20:55:00.000000"
            }