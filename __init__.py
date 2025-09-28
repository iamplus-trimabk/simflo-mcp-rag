"""
SimFlo MCP RAG - Universal Component Discovery System

A comprehensive system for extracting, indexing, and searching technical components
and documentation from multiple sources with intelligent merging and quality scoring.
"""

__version__ = "2.0.0"
__author__ = "SimFlo Team"
__email__ = "team@simflo.ai"

# Core components
from .services.registry_config_manager import RegistryConfigManager
from .extractors.extractor_factory import ExtractorFactory
from .services.multi_source_merger import MultiSourceMerger
from .models.component_models import Component, ComponentCategory, ComponentType

__all__ = [
    "RegistryConfigManager",
    "ExtractorFactory",
    "MultiSourceMerger",
    "Component",
    "ComponentCategory",
    "ComponentType"
]