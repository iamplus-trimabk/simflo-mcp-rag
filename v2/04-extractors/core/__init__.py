"""
Specialized Extractors Package

Contains extractor classes for different source types and content categories.
"""

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent
from .extractor_factory import ExtractorFactory, get_extractor_factory, create_extractor
from .shadcn_hooks_extractor import ShadcnHooksExtractor
from .shadcn_blocks_extractor import ShadcnBlocksExtractor
from .npm_hooks_extractor import NPMHooksExtractor
from .community_extractor import CommunityExtractor

__all__ = [
    "BaseExtractor",
    "ExtractionResult",
    "ExtractedComponent",
    "ExtractorFactory",
    "get_extractor_factory",
    "create_extractor",
    "ShadcnHooksExtractor",
    "ShadcnBlocksExtractor",
    "NPMHooksExtractor",
    "CommunityExtractor"
]