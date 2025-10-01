"""
Simple Extractor Factory

A working factory that can create and manage simple extractors.
"""

import sys
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SimpleExtractorFactory:
    """Simple factory for creating working extractors"""

    def __init__(self):
        self._extractors = {}
        self._register_extractors()

    def _register_extractors(self):
        """Register available extractors"""
        # Import simple extractors
        try:
            from shadcn_extractor import SimpleShadcnExtractor
            self._extractors["shadcn"] = SimpleShadcnExtractor
            logger.info("Registered shadcn extractor")
        except ImportError as e:
            logger.error(f"Failed to register shadcn extractor: {e}")

        try:
            from gluestack_extractor_simple import SimpleGluestackExtractor
            self._extractors["gluestack"] = SimpleGluestackExtractor
            logger.info("Registered gluestack extractor")
        except ImportError as e:
            logger.error(f"Failed to register gluestack extractor: {e}")

    def get_available_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available extractors"""
        extractors_info = {}

        for name, extractor_class in self._extractors.items():
            try:
                # Create a temporary instance to get info
                temp_instance = extractor_class()
                info = temp_instance.get_extractor_info()
                extractors_info[name] = info
            except Exception as e:
                extractors_info[name] = {
                    "name": name,
                    "type": "extractor",
                    "error": f"Failed to get extractor info: {e}",
                    "class": extractor_class.__name__ if extractor_class else "Failed to load"
                }

        return extractors_info

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