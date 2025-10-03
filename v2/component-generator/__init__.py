"""
Component Generator - Step 4 of SimFlo Figma-to-RAG Pipeline

Generates React components from component catalogs and design tokens.
Supports multiple component libraries (shadcn/ui, Gluestack) with TypeScript,
accessibility features, responsive design, and comprehensive documentation.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from .main import ComponentGenerator, GenerationConfig, ComponentLibrary, OutputFormat

__all__ = ['ComponentGenerator', 'GenerationConfig', 'ComponentLibrary', 'OutputFormat']

__version__ = "1.0.0"
