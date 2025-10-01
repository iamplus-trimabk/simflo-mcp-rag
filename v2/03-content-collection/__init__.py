"""
Content Collection Component (03)

Content discovery and acquisition system for gathering information from various sources.
Provides the source discovery and content fetching capabilities that feed into the RAG pipeline.
"""

from .source_discovery import SourceDiscovery
from .content_fetching import ContentFetcher

__all__ = ['SourceDiscovery', 'ContentFetcher']