"""
Test Generator - Step 6 of SimFlo Figma-to-RAG Pipeline

This module generates comprehensive Playwright E2E test suites from test scenarios
and page implementations. Supports TypeScript, Page Object Model, visual regression
testing, accessibility testing, mobile device testing, and comprehensive test reporting.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from .main import TestGenerator, TestGenerationConfig, TestFramework, TestType, BrowserType, DeviceType

__version__ = "1.0.0"
__author__ = "SimFlo Pipeline Team"

__all__ = [
    "TestGenerator",
    "TestGenerationConfig",
    "TestFramework",
    "TestType",
    "BrowserType",
    "DeviceType"
]
