"""
Test Runner - Step 7 of SimFlo Figma-to-RAG Pipeline

This package provides comprehensive test execution, reporting, and demo application
generation capabilities for Playwright test suites.

Main Components:
- TestRunner: Main class for test execution and reporting
- TestExecutionResult: Data structures for test results
- TestRunnerConfig: Configuration management
- DemoApplicationConfig: Demo application configuration

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

# Import classes for package-level access
try:
    # Try relative import first (when used as a package)
    from .main import TestRunner, TestRunnerConfig, DemoApplicationConfig, TestExecutionResult, TestSuiteResult, TestStatus
except ImportError:
    # Fallback to absolute import (when main.py is imported directly)
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    # Import main module and extract classes
    import main as test_runner_module
    TestRunner = test_runner_module.TestRunner
    TestRunnerConfig = test_runner_module.TestRunnerConfig
    DemoApplicationConfig = test_runner_module.DemoApplicationConfig
    TestExecutionResult = test_runner_module.TestExecutionResult
    TestSuiteResult = test_runner_module.TestSuiteResult
    TestStatus = test_runner_module.TestStatus

__version__ = "1.0.0"
__author__ = "SimFlo Pipeline Team"
__description__ = "Test execution and demo generation for SimFlo Figma-to-RAG Pipeline"

__all__ = [
    "TestRunner",
    "TestRunnerConfig",
    "DemoApplicationConfig",
    "TestExecutionResult",
    "TestSuiteResult",
    "TestStatus"
]
