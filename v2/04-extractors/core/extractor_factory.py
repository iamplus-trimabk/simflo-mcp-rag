"""
Extractor Factory

Creates and manages specialized extractors for different source types.
"""

import logging
from typing import Dict, List, Optional, Type, Any
from base_extractor import BaseExtractor, ExtractionResult
import importlib
import inspect

logger = logging.getLogger(__name__)

class ExtractorFactory:
    """Factory for creating specialized extractors"""

    def __init__(self):
        self._extractors: Dict[str, Type[BaseExtractor]] = {}
        self._source_type_mapping: Dict[str, List[str]] = {}
        self._register_builtin_extractors()

    def _register_builtin_extractors(self):
        """Register all built-in extractors"""
        # Define available extractors and their source types
        builtin_extractors = {
            "shadcn": ["github"],
            "shadcn_hooks": ["github"],
            "shadcn_components": ["github"],
            "shadcn_blocks": ["github"],
            "gluestack": ["github"],
            "gluestack_hooks": ["github"],
            "gluestack_blocks": ["github"],
            "npm_hooks": ["npm"],
            "community": ["github", "api", "local"],
            "documentation": ["web", "docs"]
        }

        for extractor_name, source_types in builtin_extractors.items():
            self._source_type_mapping[extractor_name] = source_types

        logger.info(f"Registered {len(builtin_extractors)} built-in extractor types")

    def register_extractor(self, name: str, extractor_class: Type[BaseExtractor], source_types: List[str]):
        """Register a custom extractor"""
        self._extractors[name] = extractor_class
        self._source_type_mapping[name] = source_types
        logger.info(f"Registered custom extractor: {name}")

    def get_available_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available extractors"""
        extractors_info = {}

        # Built-in extractors
        for name, source_types in self._source_type_mapping.items():
            extractors_info[name] = {
                "name": name,
                "source_types": source_types,
                "type": "builtin",
                "class": self._extractors.get(name, "Not yet imported")
            }

        return extractors_info

    def create_extractor(self, extractor_name: str, source_config: Dict[str, Any]) -> Optional[BaseExtractor]:
        """Create an extractor instance"""
        try:
            # Get extractor class
            extractor_class = self._get_extractor_class(extractor_name)
            if not extractor_class:
                logger.error(f"Extractor class not found: {extractor_name}")
                return None

            # Validate extractor compatibility
            if not self.validate_extractor_compatibility(source_config, extractor_name):
                logger.error(f"Extractor {extractor_name} not compatible with source configuration")
                return None

            # Create extractor instance
            extractor_instance = extractor_class(source_config)
            logger.info(f"Created extractor: {extractor_name}")
            return extractor_instance

        except Exception as e:
            logger.error(f"Failed to create extractor {extractor_name}: {e}")
            return None

    def _get_extractor_class(self, extractor_name: str) -> Optional[Type[BaseExtractor]]:
        """Get extractor class by name"""
        # Check if already loaded
        if extractor_name in self._extractors:
            return self._extractors[extractor_name]

        # Try to import and load the extractor
        try:
            module_path = self._get_extractor_module_path(extractor_name)
            if not module_path:
                logger.error(f"Cannot determine module path for extractor: {extractor_name}")
                return None

            # Import the module
            module = importlib.import_module(module_path)

            # Find extractor class in module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if ((issubclass(obj, BaseExtractor) or
                     (hasattr(obj, '__bases__') and any(issubclass(base, BaseExtractor) for base in obj.__bases__))) and
                    obj != BaseExtractor and
                    obj.__module__ == module.__name__):
                    self._extractors[extractor_name] = obj
                    return obj

            logger.error(f"Extractor class not found in module {module_path}")
            return None

        except ImportError as e:
            logger.error(f"Failed to import extractor module {extractor_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading extractor {extractor_name}: {e}")
            return None

    def _get_extractor_module_path(self, extractor_name: str) -> Optional[str]:
        """Get the module path for an extractor"""
        # Convert extractor name to module name
        # Examples: shadcn_hooks -> shadcn_hooks_extractor
        #           npm_hooks -> npm_hooks_extractor

        if extractor_name.endswith("_extractor"):
            module_name = extractor_name
        else:
            module_name = f"{extractor_name}_extractor"

        # Try direct import from core directory first
        return module_name

    def validate_extractor_compatibility(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate that an extractor is compatible with a source configuration"""
        # Get supported source types for this extractor
        supported_types = self._source_type_mapping.get(extractor_name, [])
        if not supported_types:
            logger.error(f"No source types defined for extractor: {extractor_name}")
            return False

        # Check if source type is supported
        source_type = source_config.get("type")
        if source_type not in supported_types:
            logger.error(f"Source type '{source_type}' not supported by extractor '{extractor_name}'")
            logger.error(f"Supported types: {supported_types}")
            return False

        # Type-specific validation
        if source_type == "github":
            return self._validate_github_source(source_config, extractor_name)
        elif source_type == "gitlab":
            return self._validate_gitlab_source(source_config, extractor_name)
        elif source_type == "bitbucket":
            return self._validate_bitbucket_source(source_config, extractor_name)
        elif source_type == "npm":
            return self._validate_npm_source(source_config, extractor_name)
        elif source_type == "api":
            return self._validate_api_source(source_config, extractor_name)
        elif source_type == "local":
            return self._validate_local_source(source_config, extractor_name)
        elif source_type in ["web", "docs"]:
            return self._validate_web_source(source_config, extractor_name)

        return True

    def _validate_github_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate GitHub source configuration"""
        required_fields = ["url", "branch", "registry_file"]

        for field in required_fields:
            if not source_config.get(field):
                logger.error(f"GitHub source missing required field: {field}")
                return False

        # Validate URL format
        url = source_config["url"]
        if not (url.startswith("https://github.com/") or url.startswith("http://github.com/") or
                url.startswith("https://www.github.com/") or url.startswith("http://www.github.com/")):
            logger.error(f"Invalid GitHub URL: {url}")
            return False

        return True

    def _validate_npm_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate NPM source configuration"""
        if not source_config.get("package"):
            logger.error("NPM source missing required field: package")
            return False

        # Basic package name validation
        package = source_config["package"]
        if not isinstance(package, str) or len(package.strip()) == 0:
            logger.error(f"Invalid package name: {package}")
            return False

        return True

    def _validate_api_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate API source configuration"""
        if not source_config.get("url"):
            logger.error("API source missing required field: url")
            return False

        # Validate URL format
        url = source_config["url"]
        if not (url.startswith("http://") or url.startswith("https://")):
            logger.error(f"Invalid API URL: {url}")
            return False

        return True

    def _validate_local_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate local source configuration"""
        if not source_config.get("registry_file"):
            logger.error("Local source missing required field: registry_file")
            return False

        return True

    def _validate_web_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate web documentation source configuration"""
        required_fields = ["name", "base_url", "start_urls", "allowed_domains", "selectors"]

        for field in required_fields:
            if not source_config.get(field):
                logger.error(f"Web documentation source missing required field: {field}")
                return False

        # Validate URL format
        base_url = source_config.get("base_url", "")
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            logger.error(f"Invalid base URL: {base_url}")
            return False

        # Validate selectors
        selectors = source_config.get("selectors", {})
        required_selectors = ["content", "title", "navigation"]
        for selector in required_selectors:
            if selector not in selectors:
                logger.error(f"Missing required selector: {selector}")
                return False

        return True

    def _validate_gitlab_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate GitLab source configuration"""
        # Check for project_path or repo_slug
        if not (source_config.get("project_path") or source_config.get("repo_slug")):
            logger.error("GitLab source missing required field: project_path or repo_slug")
            return False

        # Check for registry_file
        if not source_config.get("registry_file"):
            logger.error("GitLab source missing required field: registry_file")
            return False

        # Validate URL if provided
        url = source_config.get("url")
        if url and not (url.startswith("https://gitlab.com/") or "gitlab" in url.lower()):
            logger.error(f"Invalid GitLab URL: {url}")
            return False

        return True

    def _validate_bitbucket_source(self, source_config: Dict[str, Any], extractor_name: str) -> bool:
        """Validate Bitbucket source configuration"""
        # Check for workspace and repo_slug
        if not source_config.get("workspace"):
            logger.error("Bitbucket source missing required field: workspace")
            return False

        if not source_config.get("repo_slug"):
            logger.error("Bitbucket source missing required field: repo_slug")
            return False

        # Check for registry_file
        if not source_config.get("registry_file"):
            logger.error("Bitbucket source missing required field: registry_file")
            return False

        # Validate URL if provided
        url = source_config.get("url")
        if url and not (url.startswith("https://bitbucket.org/") or "bitbucket" in url.lower()):
            logger.error(f"Invalid Bitbucket URL: {url}")
            return False

        return True

    def get_extractor_info(self, extractor_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific extractor"""
        if extractor_name not in self._source_type_mapping:
            return None

        extractor_class = self._get_extractor_class(extractor_name)
        if not extractor_class:
            return None

        return {
            "name": extractor_name,
            "source_types": self._source_type_mapping[extractor_name],
            "class": extractor_class.__name__,
            "module": extractor_class.__module__,
            "description": extractor_class.__doc__ or "No description available",
            "supported_types": self._get_supported_types(extractor_class)
        }

    def _get_supported_types(self, extractor_class: Type[BaseExtractor]) -> List[str]:
        """Get supported component types for an extractor class"""
        try:
            # Try to create a dummy instance to get supported types
            dummy_config = {"name": "dummy", "type": "github"}
            dummy_instance = extractor_class(dummy_config)
            return dummy_instance.get_supported_types()
        except Exception:
            return ["unknown"]

    def recommend_extractors(self, source_config: Dict[str, Any]) -> List[str]:
        """Recommend extractors for a given source configuration"""
        source_type = source_config.get("type")
        if not source_type:
            return []

        recommendations = []

        for extractor_name, supported_types in self._source_type_mapping.items():
            if source_type in supported_types:
                recommendations.append(extractor_name)

        return sorted(recommendations)

    def auto_select_extractor(self, source_config: Dict[str, Any]) -> Optional[str]:
        """Automatically select the best extractor for a source configuration"""
        recommendations = self.recommend_extractors(source_config)

        if not recommendations:
            return None

        # For now, return the first recommendation
        # In the future, this could be more sophisticated
        return recommendations[0]

    def create_auto_extractor(self, source_config: Dict[str, Any]) -> Optional[BaseExtractor]:
        """Create extractor using automatic selection"""
        extractor_name = self.auto_select_extractor(source_config)
        if not extractor_name:
            logger.error("No compatible extractor found for source configuration")
            return None

        return self.create_extractor(extractor_name, source_config)

    def get_statistics(self) -> Dict[str, Any]:
        """Get factory statistics"""
        return {
            "registered_extractors": len(self._extractors),
            "builtin_extractors": len(self._source_type_mapping),
            "loaded_extractors": len([name for name, cls in self._extractors.items() if cls]),
            "extractor_info": {
                name: {
                    "source_types": types,
                    "loaded": name in self._extractors
                }
                for name, types in self._source_type_mapping.items()
            }
        }

    def test_extractor(self, extractor_name: str, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test an extractor without running full extraction"""
        result = {
            "extractor_name": extractor_name,
            "success": False,
            "errors": [],
            "warnings": [],
            "compatible": False
        }

        try:
            # Test compatibility
            if not self.validate_extractor_compatibility(source_config, extractor_name):
                result["errors"].append("Extractor not compatible with source configuration")
                return result

            result["compatible"] = True

            # Test creation
            extractor = self.create_extractor(extractor_name, source_config)
            if not extractor:
                result["errors"].append("Failed to create extractor instance")
                return result

            # Test validation
            if not extractor.validate_source():
                result["warnings"].append("Extractor source validation failed")
            else:
                result["success"] = True

            # Get supported types
            result["supported_types"] = extractor.get_supported_types()

        except Exception as e:
            result["errors"].append(f"Test failed: {str(e)}")

        return result

    def create_batch_extractors(self, source_configs: List[Dict[str, Any]]) -> Dict[str, Optional[BaseExtractor]]:
        """Create multiple extractors from a list of source configurations"""
        extractors = {}

        for source_config in source_configs:
            source_name = source_config.get("name", f"source_{len(extractors)}")
            extractor_name = source_config.get("extractor")

            if not extractor_name:
                # Auto-select extractor
                extractor_name = self.auto_select_extractor(source_config)

            if extractor_name:
                extractor = self.create_extractor(extractor_name, source_config)
                extractors[source_name] = extractor
            else:
                logger.error(f"Could not create extractor for source: {source_name}")
                extractors[source_name] = None

        return extractors

# Global factory instance
_extractor_factory: Optional[ExtractorFactory] = None

def get_extractor_factory() -> ExtractorFactory:
    """Get the global extractor factory instance"""
    global _extractor_factory
    if _extractor_factory is None:
        _extractor_factory = ExtractorFactory()
    return _extractor_factory

def create_extractor(extractor_name: str, source_config: Dict[str, Any]) -> Optional[BaseExtractor]:
    """Convenience function to create an extractor"""
    factory = get_extractor_factory()
    return factory.create_extractor(extractor_name, source_config)

def create_auto_extractor(source_config: Dict[str, Any]) -> Optional[BaseExtractor]:
    """Convenience function to create an extractor with auto-selection"""
    factory = get_extractor_factory()
    return factory.create_auto_extractor(source_config)