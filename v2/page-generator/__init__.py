"""
Page Generator - Step 5 of SimFlo Figma-to-RAG Pipeline

This package generates complete React pages from screen specifications,
component catalogs, and interaction flows.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from .main import PageGenerator, PageGenerationConfig, PageType, RoutingLibrary, StateManagement

__version__ = "1.0.0"
__all__ = [
    "PageGenerator",
    "PageGenerationConfig",
    "PageType",
    "RoutingLibrary",
    "StateManagement"
]
