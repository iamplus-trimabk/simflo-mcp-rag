#!/usr/bin/env python3
"""
Test suite for test-runner module.

This module contains unit tests for the test-runner functionality.
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
import sys
current_dir = Path(__file__).parent
v2_dir = current_dir.parent
sys.path.insert(0, str(v2_dir))

try:
    # Import main module directly since 'test-runner' is not a valid Python module name
    import main as test_runner_module
    TestRunner = test_runner_module.TestRunner
    TestRunnerConfig = test_runner_module.TestRunnerConfig
    TestExecutionMode = test_runner_module.TestExecutionMode
    BrowserType = test_runner_module.BrowserType
    TestStatus = test_runner_module.TestStatus
except ImportError as e:
    print(f"Could not import test-runner module: {e}")
    sys.exit(1)


class TestTestRunner(unittest.TestCase):
    """Test cases for TestRunner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TestRunnerConfig(
            mode=TestExecutionMode.SIMULATION,
            output_directory=self.temp_dir,
            test_directory=f"{self.temp_dir}/tests/",
            demo_directory=f"{self.temp_dir}/demo/",
            report_directory=f"{self.temp_dir}/test-results/",
            screenshots_directory=f"{self.temp_dir}/test-results/screenshots/",
            videos_directory=f"{self.temp_dir}/test-results/videos/",
            traces_directory=f"{self.temp_dir}/test-results/traces/",
            coverage_directory=f"{self.temp_dir}/coverage/",
            simulate_failures=False
        )
        self.runner = TestRunner(self.config)

    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertEqual(self.config.mode, TestExecutionMode.SIMULATION)
        self.assertEqual(self.config.browsers, [
                         BrowserType.CHROMIUM, BrowserType.FIREFOX, BrowserType.WEBKIT])
        self.assertTrue(self.config.generate_demo)
        self.assertTrue(self.config.generate_coverage)

    def test_runner_initialization(self):
        """Test test runner initialization."""
        self.assertIsInstance(self.runner.config, TestRunnerConfig)
        self.assertEqual(self.runner.execution_stats["total_tests"], 0)
        self.assertEqual(self.runner.execution_stats["executed_tests"], 0)

    def test_create_output_directories(self):
        """Test output directory creation."""
        self.runner._create_output_directories()

        expected_dirs = [
            self.temp_dir,
            f"{self.temp_dir}/tests/",
            f"{self.temp_dir}/demo/",
            f"{self.temp_dir}/test-results/",
            f"{self.temp_dir}/test-results/screenshots/",
            f"{self.temp_dir}/test-results/videos/",
            f"{self.temp_dir}/test-results/traces/",
            f"{self.temp_dir}/coverage/"
        ]

        for dir_path in expected_dirs:
            self.assertTrue(Path(dir_path).exists(),
                            f"Directory {dir_path} should exist")

    def test_generate_simulated_screenshot(self):
        """Test simulated screenshot generation."""
        screenshot_path = self.runner._generate_simulated_screenshot(
            "test-scenario", "test-id")

        self.assertTrue(Path(screenshot_path).exists())
        self.assertTrue(screenshot_path.endswith('.png'))

    def test_validation_results(self):
        """Test result validation."""
        from main import TestSuiteResult, TestExecutionResult

        # Create test results with high success rate
        good_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=100.0,
            started_at=datetime.now(),
            test_results=[]
        )

        validation = self.runner.validate_results(good_results)
        self.assertTrue(validation["validation_passed"])
        self.assertEqual(len(validation["validation_errors"]), 0)

        # Create test results with low success rate
        bad_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=10,
            passed_tests=5,
            failed_tests=5,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=100.0,
            started_at=datetime.now(),
            test_results=[]
        )

        validation = self.runner.validate_results(bad_results)
        self.assertFalse(validation["validation_passed"])
        self.assertGreater(len(validation["validation_errors"]), 0)

    def test_generate_html_report(self):
        """Test HTML report generation."""
        from main import TestSuiteResult, TestExecutionResult, TestStatus

        # Create test results
        test_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=2,
            passed_tests=1,
            failed_tests=1,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=50.0,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            test_results=[
                TestExecutionResult(
                    test_id="test-1",
                    test_name="Test 1",
                    status=TestStatus.PASSED,
                    duration=25.0
                ),
                TestExecutionResult(
                    test_id="test-2",
                    test_name="Test 2",
                    status=TestStatus.FAILED,
                    duration=25.0,
                    error_message="Test failed"
                )
            ]
        )

        html_report = self.runner._generate_html_report(test_results)

        self.assertIsInstance(html_report, str)
        self.assertIn("Test Suite", html_report)
        self.assertIn("Test 1", html_report)
        self.assertIn("Test 2", html_report)
        self.assertIn("50.0%", html_report)  # Success rate

    def test_generate_json_report(self):
        """Test JSON report generation."""
        from main import TestSuiteResult, TestExecutionResult, TestStatus

        test_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=25.0,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            test_results=[
                TestExecutionResult(
                    test_id="test-1",
                    test_name="Test 1",
                    status=TestStatus.PASSED,
                    duration=25.0
                )
            ]
        )

        json_report = self.runner._generate_json_report(test_results)
        report_data = json.loads(json_report)

        self.assertEqual(report_data["suite_name"], "Test Suite")
        self.assertEqual(report_data["summary"]["total_tests"], 1)
        self.assertEqual(report_data["summary"]["passed_tests"], 1)
        self.assertEqual(report_data["summary"]["success_rate"], 100.0)
        self.assertEqual(len(report_data["test_results"]), 1)

    def test_generate_demo_html(self):
        """Test demo HTML generation."""
        from main import TestSuiteResult, DemoApplicationConfig, TestExecutionResult, TestStatus

        test_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=25.0,
            started_at=datetime.now(),
            test_results=[
                TestExecutionResult(
                    test_id="test-1",
                    test_name="Test 1",
                    status=TestStatus.PASSED,
                    duration=25.0
                )
            ]
        )

        from main import DemoApplicationConfig
        demo_config = DemoApplicationConfig(
            title="Test Demo",
            description="Test demo application"
        )

        demo_html = self.runner._generate_demo_html(test_results, demo_config)

        self.assertIsInstance(demo_html, str)
        self.assertIn("Test Demo", demo_html)
        self.assertIn("Test demo application", demo_html)
        self.assertIn("Test Suite", demo_html)
        self.assertIn("Test 1", demo_html)

    def test_coverage_report_generation(self):
        """Test coverage report generation."""
        coverage_path = self.runner.generate_coverage_report()

        self.assertIsNotNone(coverage_path)
        self.assertTrue(Path(coverage_path).exists())

        # Check HTML coverage report
        html_path = Path(self.config.coverage_directory) / "index.html"
        self.assertTrue(html_path.exists())

        html_content = html_path.read_text()
        self.assertIn("Code Coverage Report", html_content)
        self.assertIn("coverage", html_content.lower())

    def test_demo_assets_generation(self):
        """Test demo assets generation."""
        from main import TestSuiteResult, TestExecutionResult, TestStatus

        test_results = TestSuiteResult(
            suite_name="Test Suite",
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=25.0,
            started_at=datetime.now(),
            test_results=[]
        )

        from main import DemoApplicationConfig
        demo_config = DemoApplicationConfig()
        assets = self.runner._generate_demo_assets(test_results, demo_config)

        self.assertIn("styles.css", assets)
        self.assertIn("app.js", assets)

        # Check if files exist
        css_path = Path(self.config.demo_directory) / "styles.css"
        js_path = Path(self.config.demo_directory) / "app.js"

        self.assertTrue(css_path.exists())
        self.assertTrue(js_path.exists())

        # Check content
        css_content = css_path.read_text()
        js_content = js_path.read_text()

        self.assertIn("/* Demo Application Styles */", css_content)
        self.assertIn("// Demo Application JavaScript", js_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestTestRunnerConfig(unittest.TestCase):
    """Test cases for TestRunnerConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TestRunnerConfig()

        self.assertEqual(config.mode, TestExecutionMode.SIMULATION)
        self.assertEqual(len(config.browsers), 3)
        self.assertTrue(config.parallel_execution)
        self.assertEqual(config.timeout, 30000)
        self.assertEqual(config.retry_failed, 2)
        self.assertTrue(config.generate_demo)
        self.assertTrue(config.generate_coverage)

    def test_custom_config(self):
        """Test custom configuration values."""
        custom_config = TestRunnerConfig(
            mode=TestExecutionMode.HEADED,
            browsers=[BrowserType.CHROMIUM],
            parallel_execution=False,
            timeout=60000,
            retry_failed=3,
            generate_demo=False
        )

        self.assertEqual(custom_config.mode, TestExecutionMode.HEADED)
        self.assertEqual(custom_config.browsers, [BrowserType.CHROMIUM])
        self.assertFalse(custom_config.parallel_execution)
        self.assertEqual(custom_config.timeout, 60000)
        self.assertEqual(custom_config.retry_failed, 3)
        self.assertFalse(custom_config.generate_demo)


class TestDemoApplicationConfig(unittest.TestCase):
    """Test cases for DemoApplicationConfig class."""

    @classmethod
    def setUpClass(cls):
        """Import DemoApplicationConfig for this test class."""
        from main import DemoApplicationConfig
        cls.DemoApplicationConfig = DemoApplicationConfig

    def test_default_demo_config(self):
        """Test default demo configuration."""
        config = self.DemoApplicationConfig()

        self.assertEqual(config.title, "SimFlo Application Demo")
        self.assertEqual(config.description,
                         "Interactive demo of generated components and pages")
        self.assertEqual(config.theme, "light")
        self.assertEqual(config.layout, "sidebar")
        self.assertTrue(config.show_code)
        self.assertTrue(config.show_tests)
        self.assertTrue(config.show_screenshots)
        self.assertTrue(config.interactive_mode)
        self.assertFalse(config.auto_start_demo)
        self.assertEqual(config.demo_port, 8080)

    def test_custom_demo_config(self):
        """Test custom demo configuration."""
        custom_config = self.DemoApplicationConfig(
            title="Custom Demo",
            description="Custom demo application",
            theme="dark",
            layout="topbar",
            show_code=False,
            auto_start_demo=True,
            demo_port=3000
        )

        self.assertEqual(custom_config.title, "Custom Demo")
        self.assertEqual(custom_config.description, "Custom demo application")
        self.assertEqual(custom_config.theme, "dark")
        self.assertEqual(custom_config.layout, "topbar")
        self.assertFalse(custom_config.show_code)
        self.assertTrue(custom_config.auto_start_demo)
        self.assertEqual(custom_config.demo_port, 3000)


if __name__ == "__main__":
    unittest.main()
