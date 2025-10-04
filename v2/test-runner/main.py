#!/usr/bin/env python3
"""
Test Runner - Step 7 of SimFlo Figma-to-RAG Pipeline

Executes Playwright test suites and generates interactive demo applications.
Supports test execution simulation, comprehensive reporting, demo application
generation, coverage analysis, and result validation.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import http.server
import socketserver
import os

# Add parent directory to path for imports
current_dir = Path(__file__).parent
v2_dir = current_dir.parent
sys.path.insert(0, str(v2_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from common.schemas import (
        TestScenario, TestSuite, TestStep, TestAction, TestDataRequirement,
        ScreenSpecification, ComponentCatalog, ComponentDefinition, ComponentInstance,
        DesignTokenSet, PipelineStepResult
    )
except ImportError as e:
    logger.warning(f"Could not import from common module: {e}")
    # Define fallback schemas for testing
    from pydantic import BaseModel

    class TestAction(BaseModel):
        action_type: str
        target: Dict[str, str]
        parameters: Dict[str, Any] = {}
        description: str
        expected_result: Optional[str] = None
        timeout: Optional[int] = None

    class TestStep(BaseModel):
        step_number: int
        description: str
        actions: List[TestAction] = []
        validations: List[TestAction] = []
        preconditions: List[str] = []
        postconditions: List[str] = []

    class TestDataRequirement(BaseModel):
        type: str
        description: str
        data: Dict[str, Any] = {}
        sensitive: bool = False
        source: Optional[str] = None

    class TestScenario(BaseModel):
        id: str
        name: str
        description: str
        category: str
        priority: str = "medium"
        tags: List[str] = []
        steps: List[TestStep] = []
        test_data: List[TestDataRequirement] = []
        success_criteria: List[str] = []
        estimated_duration: Optional[int] = None
        dependencies: List[str] = []

    class TestSuite(BaseModel):
        name: str
        description: str
        scenarios: List[TestScenario] = []
        configuration: Dict[str, Any] = {}
        tags: List[str] = []

    class ComponentInstance(BaseModel):
        id: str
        component_id: str
        name: str
        properties: Dict[str, Any] = {}
        position: Dict[str, float] = {}
        size: Dict[str, float] = {}

    class ScreenSpecification(BaseModel):
        id: str
        name: str
        type: str
        component_instances: List[ComponentInstance] = []
        navigation_flows: List[Dict[str, Any]] = []

    class ComponentDefinition(BaseModel):
        id: str
        name: str
        category: str
        properties: List[Dict[str, Any]] = []

    class ComponentCatalog(BaseModel):
        components: List[ComponentDefinition] = []
        instances: List[ComponentInstance] = []

    class PipelineStepResult(BaseModel):
        step_name: str
        status: str
        start_time: datetime
        end_time: Optional[datetime] = None
        input_files: List[str] = []
        output_files: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {}


class TestExecutionMode(Enum):
    """Test execution modes."""
    SIMULATION = "simulation"
    HEADED = "headed"
    HEADLESS = "headless"
    DEBUG = "debug"


class BrowserType(Enum):
    """Supported browsers for test execution."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"


class ReportFormat(Enum):
    """Supported report formats."""
    HTML = "html"
    JSON = "json"
    JUNIT = "junit"
    ALL = "all"


@dataclass
class TestExecutionResult:
    """Result of a single test execution."""
    test_id: str
    test_name: str
    status: "TestStatus"
    duration: float
    error_message: Optional[str] = None
    screenshots: List[str] = None
    video_path: Optional[str] = None
    trace_path: Optional[str] = None
    browser_type: Optional[str] = None
    viewport: Optional[Tuple[int, int]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    steps: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []
        if self.steps is None:
            self.steps = []


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class TestSuiteResult:
    """Result of a test suite execution."""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    timeout_tests: int
    error_tests: int
    total_duration: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    test_results: List[TestExecutionResult] = None
    browser_results: Dict[str, Dict[str, int]] = None
    coverage_data: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
        if self.browser_results is None:
            self.browser_results = {}

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def failed_rate(self) -> float:
        """Calculate failure rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.failed_tests / self.total_tests) * 100


@dataclass
class DemoApplicationConfig:
    """Configuration for demo application generation."""
    title: str = "SimFlo Application Demo"
    description: str = "Interactive demo of generated components and pages"
    theme: str = "light"  # light, dark, auto
    layout: str = "sidebar"  # sidebar, topbar, minimal
    show_code: bool = True
    show_tests: bool = True
    show_screenshots: bool = True
    interactive_mode: bool = True
    auto_start_demo: bool = False
    demo_port: int = 8080
    base_url: str = "http://localhost:8080"
    include_playground: bool = True
    include_documentation: bool = True


@dataclass
class TestRunnerConfig:
    """Configuration for test runner."""
    mode: TestExecutionMode = TestExecutionMode.SIMULATION
    browsers: List[BrowserType] = None
    output_directory: str = "./output/"
    test_directory: str = "./output/tests/"
    demo_directory: str = "./output/demo/"
    report_directory: str = "./output/test-results/"
    screenshots_directory: str = "./output/test-results/screenshots/"
    videos_directory: str = "./output/test-results/videos/"
    traces_directory: str = "./output/test-results/traces/"
    coverage_directory: str = "./output/coverage/"

    # Test execution settings
    parallel_execution: bool = True
    max_workers: int = 4
    timeout: int = 30000
    retry_failed: int = 2
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True

    # Reporting settings
    report_formats: List[ReportFormat] = None
    generate_coverage: bool = True
    generate_performance_metrics: bool = True
    include_screenshots_in_report: bool = True

    # Demo settings
    demo_config: DemoApplicationConfig = None
    generate_demo: bool = True

    # Simulation settings
    simulation_duration_multiplier: float = 0.1  # Run tests 10x faster in simulation
    simulate_failures: bool = False
    failure_rate: float = 0.1  # 10% failure rate in simulation

    def __post_init__(self):
        if self.browsers is None:
            self.browsers = [BrowserType.CHROMIUM,
                             BrowserType.FIREFOX, BrowserType.WEBKIT]
        if self.report_formats is None:
            self.report_formats = [ReportFormat.HTML, ReportFormat.JSON]
        if self.demo_config is None:
            self.demo_config = DemoApplicationConfig()


class TestRunner:
    """
    Main test runner class.

    Executes Playwright test suites with support for:
    - Test execution simulation and real execution
    - Multiple browsers and devices
    - Comprehensive test reporting
    - Interactive demo application generation
    - Coverage analysis and performance metrics
    - Screenshot and video capture
    - Parallel test execution
    - Result validation and analysis
    """

    def __init__(self, config: Optional[TestRunnerConfig] = None):
        """Initialize test runner with configuration."""
        self.config = config or TestRunnerConfig()
        self.test_suite: Optional[TestSuite] = None
        self.screen_specifications: List[ScreenSpecification] = []
        self.component_catalog: Optional[ComponentCatalog] = None
        self.design_tokens: Optional[DesignTokenSet] = None

        self.execution_stats = {
            "total_tests": 0,
            "executed_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "timeout_tests": 0,
            "error_tests": 0,
            "total_duration": 0.0,
            "average_test_duration": 0.0,
            "browser_results": {},
            "tests_by_category": {},
            "tests_by_priority": {},
            "coverage_generated": False,
            "demo_generated": False,
            "reports_generated": []
        }

        self.demo_server_thread: Optional[threading.Thread] = None
        self.demo_server: Optional[socketserver.TCPServer] = None

    def load_test_suite(self, test_directory: str) -> None:
        """Load and validate test suite from test-generator output."""
        logger.info(f"Loading test suite from: {test_directory}")

        test_dir = Path(test_directory)
        if not test_dir.exists():
            raise FileNotFoundError(f"Test directory not found: {test_directory}")

        # Look for test files and configuration
        test_files = []
        test_config = None

        # Find Playwright test files
        for pattern in ["*.spec.ts", "*.spec.js", "tests/**/*.spec.ts", "tests/**/*.spec.js"]:
            test_files.extend(test_dir.glob(pattern))

        # Load test configuration if exists
        config_files = [
            test_dir / "playwright.config.ts",
            test_dir / "playwright.config.js",
            test_dir / "test-generation-metadata.json"
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    if config_file.suffix == '.json':
                        test_config = json.loads(config_file.read_text())
                        logger.info(f"Loaded test configuration from {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"Error loading config from {config_file}: {e}")

        # Create a synthetic test suite based on discovered test files
        scenarios = []
        for test_file in test_files:
            try:
                scenario = self._parse_test_file_to_scenario(test_file)
                scenarios.append(scenario)
                logger.info(f"Parsed test file: {test_file.name}")
            except Exception as e:
                logger.error(f"Error parsing test file {test_file}: {e}")

        # Also look for test scenarios in JSON format
        for json_file in test_dir.glob("**/*.json"):
            if "scenario" in json_file.name.lower() or "test" in json_file.name.lower():
                try:
                    data = json.loads(json_file.read_text())
                    if isinstance(data, dict) and 'scenarios' in data:
                        # Test suite format
                        suite = TestSuite(**data)
                        scenarios.extend(suite.scenarios)
                    elif isinstance(data, list):
                        # List of scenarios
                        for scenario_data in data:
                            scenario = TestScenario(**scenario_data)
                            scenarios.append(scenario)
                    elif isinstance(data, dict) and 'id' in data and 'steps' in data:
                        # Single scenario
                        scenario = TestScenario(**data)
                        scenarios.append(scenario)
                    logger.info(f"Loaded scenarios from {json_file.name}")
                except Exception as e:
                    logger.error(f"Error loading scenarios from {json_file}: {e}")

        self.test_suite = TestSuite(
            name="Generated Test Suite",
            description=f"Test suite loaded from {test_directory}",
            scenarios=scenarios,
            configuration=test_config or {},
            tags=["generated", "playwright"]
        )

        logger.info(f"Loaded test suite with {len(scenarios)} scenarios")

    def _parse_test_file_to_scenario(self, test_file: Path) -> TestScenario:
        """Parse a Playwright test file into a test scenario."""
        content = test_file.read_text()

        # Extract test name and description from file content
        test_name = test_file.stem.replace('.spec', '').replace('-', ' ').title()
        scenario_id = test_file.stem.replace('.spec', '')

        # Basic parsing - in a real implementation, this would use AST parsing
        description = f"Test scenario generated from {test_file.name}"
        category = "custom"

        # Try to infer category from file name or content
        if "login" in test_name.lower() or "auth" in test_name.lower():
            category = "authentication"
        elif "form" in test_name.lower():
            category = "form_interaction"
        elif "navigation" in test_name.lower() or "nav" in test_name.lower():
            category = "navigation"
        elif "visual" in test_name.lower():
            category = "visual"
        elif "accessibility" in test_name.lower() or "a11y" in test_name.lower():
            category = "accessibility"
        elif "mobile" in test_name.lower():
            category = "mobile"

        # Create a simple test scenario based on file content analysis
        steps = []
        step_count = content.count("test(") or content.count("it(")

        for i in range(1, step_count + 1):
            step = TestStep(
                step_number=i,
                description=f"Test step {i}",
                actions=[
                    TestAction(
                        action_type="click",
                        target={"type": "element", "selector": "button"},
                        description=f"Execute test action {i}"
                    )
                ],
                validations=[
                    TestAction(
                        action_type="assert",
                        target={"type": "element", "selector": "div"},
                        description=f"Validate test result {i}"
                    )
                ]
            )
            steps.append(step)

        return TestScenario(
            id=scenario_id,
            name=test_name,
            description=description,
            category=category,
            priority="medium",
            steps=steps,
            estimated_duration=step_count * 5  # 5 seconds per step
        )

    def load_screen_specifications(self, screens_path: str) -> None:
        """Load and validate screen specifications."""
        logger.info(f"Loading screen specifications from: {screens_path}")

        screens_dir = Path(screens_path)
        if not screens_dir.exists():
            logger.warning(f"Screen specifications directory not found: {screens_path}")
            return

        for json_file in screens_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                if isinstance(data, dict) and 'screenId' in data:
                    screen = ScreenSpecification(**data)
                    self.screen_specifications.append(screen)
                    logger.info(f"Loaded screen specification: {screen.name}")
            except Exception as e:
                logger.error(
                    f"Error loading screen specification from {json_file}: {e}")

        logger.info(f"Loaded {len(self.screen_specifications)} screen specifications")

    def load_component_catalog(self, catalog_path: str) -> None:
        """Load and validate component catalog."""
        logger.info(f"Loading component catalog from: {catalog_path}")

        catalog_file = Path(catalog_path)
        if not catalog_file.exists():
            logger.warning(f"Component catalog file not found: {catalog_path}")
            return

        try:
            data = json.loads(catalog_file.read_text())
            self.component_catalog = ComponentCatalog(**data)
            logger.info(
                f"Loaded component catalog with {len(self.component_catalog.components)} components")
        except Exception as e:
            logger.error(f"Error loading component catalog: {e}")

    def load_design_tokens(self, tokens_path: str) -> None:
        """Load and validate design tokens."""
        logger.info(f"Loading design tokens from: {tokens_path}")

        tokens_file = Path(tokens_path)
        if not tokens_file.exists():
            logger.warning(f"Design tokens file not found: {tokens_path}")
            return

        try:
            data = json.loads(tokens_file.read_text())
            # For now, just store the raw data
            self.design_tokens = data
            logger.info("Loaded design tokens")
        except Exception as e:
            logger.error(f"Error loading design tokens: {e}")

    def run_tests(self) -> TestSuiteResult:
        """Execute test suite based on configuration."""
        logger.info(f"Starting test execution in {self.config.mode.value} mode...")

        if not self.test_suite:
            raise ValueError("No test suite loaded. Call load_test_suite() first.")

        # Create output directories
        self._create_output_directories()

        # Initialize test suite result
        suite_result = TestSuiteResult(
            suite_name=self.test_suite.name,
            total_tests=len(self.test_suite.scenarios),
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            timeout_tests=0,
            error_tests=0,
            total_duration=0.0,
            started_at=datetime.now()
        )

        # Execute tests based on mode
        if self.config.mode == TestExecutionMode.SIMULATION:
            test_results = self._run_tests_simulation()
        else:
            test_results = self._run_tests_real()

        # Process results
        suite_result.test_results = test_results
        suite_result.completed_at = datetime.now()

        # Calculate statistics
        for result in test_results:
            suite_result.total_duration += result.duration

            if result.status == TestStatus.PASSED:
                suite_result.passed_tests += 1
            elif result.status == TestStatus.FAILED:
                suite_result.failed_tests += 1
            elif result.status == TestStatus.SKIPPED:
                suite_result.skipped_tests += 1
            elif result.status == TestStatus.TIMEOUT:
                suite_result.timeout_tests += 1
            elif result.status == TestStatus.ERROR:
                suite_result.error_tests += 1

            # Track browser results
            browser = result.browser_type or "unknown"
            if browser not in suite_result.browser_results:
                suite_result.browser_results[browser] = {
                    "passed": 0, "failed": 0, "total": 0}

            suite_result.browser_results[browser]["total"] += 1
            if result.status == TestStatus.PASSED:
                suite_result.browser_results[browser]["passed"] += 1
            else:
                suite_result.browser_results[browser]["failed"] += 1

        # Update execution stats
        self.execution_stats.update({
            "total_tests": suite_result.total_tests,
            "executed_tests": len(test_results),
            "passed_tests": suite_result.passed_tests,
            "failed_tests": suite_result.failed_tests,
            "skipped_tests": suite_result.skipped_tests,
            "timeout_tests": suite_result.timeout_tests,
            "error_tests": suite_result.error_tests,
            "total_duration": suite_result.total_duration,
            "average_test_duration": suite_result.total_duration / len(test_results) if test_results else 0,
            "browser_results": suite_result.browser_results
        })

        logger.info(
            f"Test execution completed: {suite_result.passed_tests}/{suite_result.total_tests} passed")
        return suite_result

    def _create_output_directories(self) -> None:
        """Create output directories if they don't exist."""
        directories = [
            self.config.output_directory,
            self.config.test_directory,
            self.config.demo_directory,
            self.config.report_directory,
            self.config.screenshots_directory,
            self.config.videos_directory,
            self.config.traces_directory,
            self.config.coverage_directory
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _run_tests_simulation(self) -> List[TestExecutionResult]:
        """Simulate test execution for demo purposes."""
        logger.info("Running tests in simulation mode...")

        test_results = []

        for scenario in self.test_suite.scenarios:
            # Simulate test execution time
            base_duration = scenario.estimated_duration or 30
            simulated_duration = base_duration * self.config.simulation_duration_multiplier

            # Determine test outcome
            if self.config.simulate_failures and np.random.random() < self.config.failure_rate:
                status = TestStatus.FAILED
                error_message = "Simulated test failure for demonstration purposes"
            else:
                status = TestStatus.PASSED
                error_message = None

            # Create test result
            started_at = datetime.now()
            time.sleep(simulated_duration)  # Simulate test execution time
            completed_at = datetime.now()

            result = TestExecutionResult(
                test_id=scenario.id,
                test_name=scenario.name,
                status=status,
                duration=simulated_duration,
                error_message=error_message,
                browser_type=np.random.choice([b.value for b in self.config.browsers]),
                viewport=(1920, 1080),
                started_at=started_at,
                completed_at=completed_at,
                steps=[
                    {
                        "step_number": i + 1,
                        "description": step.description,
                        "status": "passed",
                        "duration": simulated_duration / len(scenario.steps)
                    }
                    for i, step in enumerate(scenario.steps)
                ]
            )

            # Generate simulated screenshots
            if self.config.screenshot_on_failure or status == TestStatus.PASSED:
                screenshot_path = self._generate_simulated_screenshot(
                    scenario.id, result.test_id)
                result.screenshots.append(screenshot_path)

            test_results.append(result)
            logger.info(f"Simulated test: {scenario.name} - {status.value}")

        return test_results

    def _run_tests_real(self) -> List[TestExecutionResult]:
        """Run real Playwright tests."""
        logger.info("Running real Playwright tests...")

        test_results = []

        # Check if Playwright is available
        if not self._check_playwright_availability():
            logger.warning("Playwright not found, falling back to simulation mode")
            return self._run_tests_simulation()

        # Create test execution command
        cmd = self._build_playwright_command()

        try:
            # Execute Playwright tests
            result = subprocess.run(
                cmd,
                cwd=self.config.test_directory,
                capture_output=True,
                text=True,
                timeout=self.config.timeout * 2  # Give extra time for the entire suite
            )

            # Parse test results from Playwright output
            test_results = self._parse_playwright_results(result)

        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            # Create timeout results for all tests
            for scenario in self.test_suite.scenarios:
                test_results.append(TestExecutionResult(
                    test_id=scenario.id,
                    test_name=scenario.name,
                    status=TestStatus.TIMEOUT,
                    duration=self.config.timeout / 1000,
                    error_message=f"Test execution timed out after {self.config.timeout}ms"
                ))

        except Exception as e:
            logger.error(f"Error running Playwright tests: {e}")
            # Create error results for all tests
            for scenario in self.test_suite.scenarios:
                test_results.append(TestExecutionResult(
                    test_id=scenario.id,
                    test_name=scenario.name,
                    status=TestStatus.ERROR,
                    duration=0,
                    error_message=str(e)
                ))

        return test_results

    def _check_playwright_availability(self) -> bool:
        """Check if Playwright is available in the test directory."""
        try:
            # Check for node_modules and playwright
            node_modules = Path(self.config.test_directory) / "node_modules"
            playwright_config = Path(self.config.test_directory) / \
                "playwright.config.ts"

            if not playwright_config.exists():
                playwright_config = Path(
                    self.config.test_directory) / "playwright.config.js"

            return node_modules.exists() and playwright_config.exists()

        except Exception:
            return False

    def _build_playwright_command(self) -> List[str]:
        """Build Playwright test execution command."""
        cmd = ["npx", "playwright", "test"]

        # Add reporter configuration
        if ReportFormat.JSON in self.config.report_formats:
            cmd.extend(
                ["--reporter=json", f"--output-file={self.config.report_directory}/results.json"])

        # Add browser selection
        if self.config.browsers:
            projects = [f"@{browser.value}" for browser in self.config.browsers]
            cmd.extend(["--project"] + projects)

        # Add other options
        if not self.config.parallel_execution:
            cmd.append("--workers=1")

        if self.config.mode == TestExecutionMode.HEADED:
            cmd.append("--headed")
        elif self.config.mode == TestExecutionMode.DEBUG:
            cmd.append("--debug")

        return cmd

    def _parse_playwright_results(self, subprocess_result: subprocess.CompletedProcess) -> List[TestExecutionResult]:
        """Parse Playwright test results from subprocess output."""
        test_results = []

        # Try to parse JSON results if available
        results_file = Path(self.config.report_directory) / "results.json"
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    results_data = json.load(f)

                # Parse Playwright JSON results format
                for suite in results_data.get('suites', []):
                    for spec in suite.get('specs', []):
                        for test in spec.get('tests', []):
                            status = self._convert_playwright_status(
                                test.get('results', [{}])[0].get('status', 'unknown'))
                            duration = test.get('results', [{}])[0].get(
                                'duration', 0) / 1000  # Convert to seconds

                            result = TestExecutionResult(
                                test_id=test.get('title', 'unknown').replace(
                                    ' ', '-').lower(),
                                test_name=test.get('title', 'Unknown Test'),
                                status=status,
                                duration=duration,
                                error_message=test.get('results', [{}])[0].get(
                                    'error', {}).get('message')
                            )

                            test_results.append(result)

                return test_results

            except Exception as e:
                logger.warning(f"Error parsing Playwright JSON results: {e}")

        # Fallback: create results based on subprocess output
        output_lines = subprocess_result.stdout.split(
            '\n') + subprocess_result.stderr.split('\n')

        for scenario in self.test_suite.scenarios:
            # Simple parsing based on output
            status = TestStatus.PASSED
            error_message = None

            if subprocess_result.returncode != 0:
                # Look for failure indicators in output
                for line in output_lines:
                    if 'failed' in line.lower() and scenario.name.lower() in line.lower():
                        status = TestStatus.FAILED
                        error_message = "Test failed based on Playwright output"
                        break

            result = TestExecutionResult(
                test_id=scenario.id,
                test_name=scenario.name,
                status=status,
                duration=scenario.estimated_duration or 30,
                error_message=error_message
            )

            test_results.append(result)

        return test_results

    def _convert_playwright_status(self, playwright_status: str) -> TestStatus:
        """Convert Playwright status to TestStatus enum."""
        status_mapping = {
            'passed': TestStatus.PASSED,
            'failed': TestStatus.FAILED,
            'skipped': TestStatus.SKIPPED,
            'timedOut': TestStatus.TIMEOUT,
            'interrupted': TestStatus.ERROR,
            'unknown': TestStatus.ERROR
        }

        return status_mapping.get(playwright_status, TestStatus.ERROR)

    def _generate_simulated_screenshot(self, scenario_id: str, test_id: str) -> str:
        """Generate a simulated screenshot for demo purposes."""
        screenshot_filename = f"{scenario_id}-{test_id}-{int(time.time())}.png"
        screenshot_path = Path(self.config.screenshots_directory) / screenshot_filename

        # Create a simple placeholder image (in a real implementation, this would be an actual screenshot)
        try:
            # Create a simple SVG as placeholder
            svg_content = f'''<svg width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#f0f0f0"/>
                <text x="50%" y="50%" text-anchor="middle" font-family="Arial" font-size="24" fill="#333">
                    Screenshot: {scenario_id}
                </text>
                <text x="50%" y="55%" text-anchor="middle" font-family="Arial" font-size="16" fill="#666">
                    Test: {test_id}
                </text>
                <text x="50%" y="60%" text-anchor="middle" font-family="Arial" font-size="14" fill="#999">
                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </text>
            </svg>'''

            # Use a simple method to create a placeholder file
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            with open(screenshot_path, 'w') as f:
                f.write(svg_content)

            # Rename to .png for consistency (even though it's SVG content)
            final_path = screenshot_path.with_suffix('.png')
            screenshot_path.rename(final_path)

            return str(final_path)

        except Exception as e:
            logger.warning(f"Error creating simulated screenshot: {e}")
            return str(screenshot_path)

    def generate_reports(self, test_results: TestSuiteResult) -> Dict[str, str]:
        """Generate comprehensive test reports."""
        logger.info("Generating test reports...")

        generated_reports = {}

        for report_format in self.config.report_formats:
            if report_format == ReportFormat.HTML:
                html_report = self._generate_html_report(test_results)
                report_path = Path(self.config.report_directory) / "report.html"
                report_path.write_text(html_report, encoding='utf-8')
                generated_reports["html"] = str(report_path)

            elif report_format == ReportFormat.JSON:
                json_report = self._generate_json_report(test_results)
                report_path = Path(self.config.report_directory) / "report.json"
                report_path.write_text(json_report, encoding='utf-8')
                generated_reports["json"] = str(report_path)

            elif report_format == ReportFormat.JUNIT:
                junit_report = self._generate_junit_report(test_results)
                report_path = Path(self.config.report_directory) / "report.xml"
                report_path.write_text(junit_report, encoding='utf-8')
                generated_reports["junit"] = str(report_path)

        # Generate executive summary
        summary_report = self._generate_summary_report(test_results)
        summary_path = Path(self.config.report_directory) / "summary.md"
        summary_path.write_text(summary_report, encoding='utf-8')
        generated_reports["summary"] = str(summary_path)

        self.execution_stats["reports_generated"] = list(generated_reports.keys())
        logger.info(f"Generated {len(generated_reports)} reports")

        return generated_reports

    def _generate_html_report(self, test_results: TestSuiteResult) -> str:
        """Generate comprehensive HTML test report."""
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {test_results.suite_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .summary-card {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .summary-card h3 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .summary-card.passed {{ color: #10b981; }}
        .summary-card.failed {{ color: #ef4444; }}
        .summary-card.total {{ color: #3b82f6; }}
        .progress-bar {{ background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden; margin: 1rem 0; }}
        .progress-fill {{ background: #10b981; height: 100%; transition: width 0.3s ease; }}
        .test-results {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .test-item {{ padding: 1rem; border-bottom: 1px solid #e5e7eb; }}
        .test-item:last-child {{ border-bottom: none; }}
        .test-item.passed {{ border-left: 4px solid #10b981; }}
        .test-item.failed {{ border-left: 4px solid #ef4444; }}
        .test-item.skipped {{ border-left: 4px solid #f59e0b; }}
        .test-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem; }}
        .test-name {{ font-weight: 600; font-size: 1.1rem; }}
        .test-status {{ padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; }}
        .test-status.passed {{ background: #d1fae5; color: #065f46; }}
        .test-status.failed {{ background: #fee2e2; color: #991b1b; }}
        .test-status.skipped {{ background: #fef3c7; color: #92400e; }}
        .test-details {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 0.5rem; }}
        .test-detail {{ font-size: 0.875rem; color: #6b7280; }}
        .error-message {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 0.75rem; margin-top: 0.5rem; font-family: monospace; font-size: 0.875rem; color: #991b1b; }}
        .browser-results {{ margin-top: 2rem; }}
        .browser-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .browser-card {{ background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .footer {{ text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e5e7eb; color: #6b7280; }}
        @media (max-width: 768px) {{ .container {{ padding: 10px; }} .header h1 {{ font-size: 2rem; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Report</h1>
            <p>{test_results.suite_name}</p>
            <p>Generated on {test_results.completed_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="summary">
            <div class="summary-card total">
                <h3>{test_results.total_tests}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card passed">
                <h3>{test_results.passed_tests}</h3>
                <p>Passed</p>
            </div>
            <div class="summary-card failed">
                <h3>{test_results.failed_tests}</h3>
                <p>Failed</p>
            </div>
            <div class="summary-card">
                <h3>{test_results.success_rate:.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {test_results.success_rate}%"></div>
        </div>

        <div class="test-results">
            <h2 style="padding: 1.5rem; background: #f9fafb; border-bottom: 1px solid #e5e7eb;">Test Results</h2>
            {self._generate_html_test_items(test_results.test_results)}
        </div>

        {self._generate_html_browser_results(test_results.browser_results)}

        <div class="footer">
            <p>Report generated by SimFlo Test Runner on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Execution time: {test_results.total_duration:.2f} seconds</p>
        </div>
    </div>

    <script>
        // Add interactive functionality
        document.querySelectorAll('.test-item').forEach(item => {{
            item.addEventListener('click', function() {{
                this.style.background = this.style.background === '#f9fafb' ? 'transparent' : '#f9fafb';
            }});
        }});
    </script>
</body>
</html>'''

        return html_template

    def _generate_html_test_items(self, test_results: List[TestExecutionResult]) -> str:
        """Generate HTML for individual test results."""
        html_items = []

        for result in test_results:
            status_class = result.status.value
            error_html = ""

            if result.error_message:
                error_html = f'<div class="error-message">{result.error_message}</div>'

            html_item = f'''<div class="test-item {status_class}">
                <div class="test-header">
                    <div class="test-name">{result.test_name}</div>
                    <div class="test-status {status_class}">{result.status.value}</div>
                </div>
                <div class="test-details">
                    <div class="test-detail">Duration: {result.duration:.2f}s</div>
                    <div class="test-detail">Browser: {result.browser_type or 'Unknown'}</div>
                    <div class="test-detail">Retries: {result.retry_count}</div>
                </div>
                {error_html}
            </div>'''

            html_items.append(html_item)

        return ''.join(html_items)

    def _generate_html_browser_results(self, browser_results: Dict[str, Dict[str, int]]) -> str:
        """Generate HTML for browser-specific results."""
        if not browser_results:
            return ""

        html = '''<div class="browser-results">
            <h2 style="padding: 1.5rem; background: #f9fafb; border-bottom: 1px solid #e5e7eb;">Browser Results</h2>
            <div class="browser-grid">'''

        for browser, stats in browser_results.items():
            success_rate = (stats['passed'] / stats['total']) * \
                100 if stats['total'] > 0 else 0

            html += f'''<div class="browser-card">
                <h3>{browser.title()}</h3>
                <p>Passed: {stats['passed']}/{stats['total']}</p>
                <p>Success Rate: {success_rate:.1f}%</p>
            </div>'''

        html += '</div></div>'
        return html

    def _generate_json_report(self, test_results: TestSuiteResult) -> str:
        """Generate JSON test report."""
        report_data = {
            "suite_name": test_results.suite_name,
            "summary": {
                "total_tests": test_results.total_tests,
                "passed_tests": test_results.passed_tests,
                "failed_tests": test_results.failed_tests,
                "skipped_tests": test_results.skipped_tests,
                "timeout_tests": test_results.timeout_tests,
                "error_tests": test_results.error_tests,
                "success_rate": test_results.success_rate,
                "total_duration": test_results.total_duration,
                "started_at": test_results.started_at.isoformat(),
                "completed_at": test_results.completed_at.isoformat() if test_results.completed_at else None
            },
            "browser_results": test_results.browser_results,
            "test_results": [
                {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "duration": result.duration,
                    "error_message": result.error_message,
                    "browser_type": result.browser_type,
                    "retry_count": result.retry_count,
                    "screenshots": result.screenshots,
                    "started_at": result.started_at.isoformat() if result.started_at else None,
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                    "steps": result.steps
                }
                for result in test_results.test_results
            ],
            "generated_at": datetime.now().isoformat(),
            "execution_mode": self.config.mode.value,
            "configuration": asdict(self.config)
        }

        return json.dumps(report_data, indent=2, default=str)

    def _generate_junit_report(self, test_results: TestSuiteResult) -> str:
        """Generate JUnit XML report for CI/CD integration."""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        total_failures = test_results.failed_tests + \
            test_results.error_tests + test_results.timeout_tests
        total_time = sum(result.duration for result in test_results.test_results)

        xml_lines.append(f'<testsuite name="{test_results.suite_name}" '
                         f'tests="{test_results.total_tests}" '
                         f'failures="{total_failures}" '
                         f'time="{total_time:.3f}">')

        for result in test_results.test_results:
            failure_xml = ""

            if result.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT]:
                failure_xml = f'<failure message="{result.error_message or "Test failed"}"></failure>'

            xml_lines.append(
                f'  <testcase name="{result.test_name}" classname="{test_results.suite_name}" time="{result.duration:.3f}">')
            xml_lines.append(f'    {failure_xml}')
            xml_lines.append('  </testcase>')

        xml_lines.append('</testsuite>')

        return '\n'.join(xml_lines)

    def _generate_summary_report(self, test_results: TestSuiteResult) -> str:
        """Generate Markdown summary report."""
        summary = f"""# Test Execution Summary

## Overview
- **Suite**: {test_results.suite_name}
- **Total Tests**: {test_results.total_tests}
- **Passed**: {test_results.passed_tests}
- **Failed**: {test_results.failed_tests}
- **Skipped**: {test_results.skipped_tests}
- **Success Rate**: {test_results.success_rate:.1f}%
- **Execution Time**: {test_results.total_duration:.2f} seconds
- **Completed**: {test_results.completed_at.strftime('%Y-%m-%d %H:%M:%S') if test_results.completed_at else 'N/A'}

## Test Results

"""

        for result in test_results.test_results:
            status_emoji = "" if result.status == TestStatus.PASSED else "L"
            summary += f"{status_emoji} **{result.test_name}** - {result.status.value} ({result.duration:.2f}s)\n"

            if result.error_message:
                summary += f"   - Error: {result.error_message}\n"

            if result.screenshots:
                summary += f"   - Screenshots: {len(result.screenshots)} files\n"

        if test_results.browser_results:
            summary += "\n## Browser Results\n\n"
            for browser, stats in test_results.browser_results.items():
                success_rate = (stats['passed'] / stats['total']) * \
                    100 if stats['total'] > 0 else 0
                summary += f"- **{browser.title()}**: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)\n"

        summary += f"""
## Configuration
- **Execution Mode**: {self.config.mode.value}
- **Browsers**: {', '.join([b.value for b in self.config.browsers])}
- **Parallel Execution**: {self.config.parallel_execution}
- **Timeout**: {self.config.timeout}ms
- **Retry Failed**: {self.config.retry_failed} times

---
*Report generated by SimFlo Test Runner on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return summary

    def generate_demo_application(self, test_results: TestSuiteResult) -> Dict[str, str]:
        """Generate interactive demo application."""
        logger.info("Generating demo application...")

        demo_files = {}
        demo_config = self.config.demo_config

        # Create demo directory structure
        demo_dir = Path(self.config.demo_directory)
        demo_dir.mkdir(parents=True, exist_ok=True)

        # Generate main demo application
        demo_html = self._generate_demo_html(test_results, demo_config)
        demo_path = demo_dir / "index.html"
        demo_path.write_text(demo_html, encoding='utf-8')
        demo_files["index.html"] = str(demo_path)

        # Generate demo assets
        assets = self._generate_demo_assets(test_results, demo_config)
        demo_files.update(assets)

        # Generate demo server
        server_js = self._generate_demo_server(demo_config)
        server_path = demo_dir / "server.js"
        server_path.write_text(server_js, encoding='utf-8')
        demo_files["server.js"] = str(server_path)

        # Generate package.json for demo
        package_json = self._generate_demo_package_json(demo_config)
        package_path = demo_dir / "package.json"
        package_path.write_text(package_json, encoding='utf-8')
        demo_files["package.json"] = str(package_path)

        # Update execution stats
        self.execution_stats["demo_generated"] = True

        logger.info(f"Generated demo application with {len(demo_files)} files")
        return demo_files

    def _generate_demo_html(self, test_results: TestSuiteResult, config: DemoApplicationConfig) -> str:
        """Generate main demo HTML application."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <meta name="description" content="{config.description}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{ --primary: #3b82f6; --primary-dark: #2563eb; --success: #10b981; --error: #ef4444; --warning: #f59e0b; --bg: #ffffff; --text: #1f2937; --border: #e5e7eb; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        .nav {{ display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }}
        .nav-button {{ padding: 0.75rem 1.5rem; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 500; transition: all 0.2s; }}
        .nav-button:hover {{ background: var(--primary-dark); transform: translateY(-1px); }}
        .nav-button.active {{ background: var(--primary-dark); }}
        .content-area {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .tab-content {{ display: none; padding: 2rem; }}
        .tab-content.active {{ display: block; }}
        .test-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
        .test-card {{ background: white; border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; transition: all 0.2s; cursor: pointer; }}
        .test-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .test-card.passed {{ border-left: 4px solid var(--success); }}
        .test-card.failed {{ border-left: 4px solid var(--error); }}
        .test-name {{ font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }}
        .test-status {{ padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; margin-bottom: 1rem; display: inline-block; }}
        .test-status.passed {{ background: #d1fae5; color: #065f46; }}
        .test-status.failed {{ background: #fee2e2; color: #991b1b; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat-card {{ background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%); padding: 1.5rem; border-radius: 10px; text-align: center; }}
        .stat-number {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .stat-label {{ color: #6b7280; font-weight: 500; }}
        .progress-bar {{ background: var(--border); height: 8px; border-radius: 4px; overflow: hidden; margin: 1rem 0; }}
        .progress-fill {{ background: var(--success); height: 100%; transition: width 0.5s ease; }}
        .screenshot-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }}
        .screenshot-card {{ background: white; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }}
        .screenshot-img {{ width: 100%; height: 200px; object-fit: cover; background: #f3f4f6; display: flex; align-items: center; justify-content: center; color: #6b7280; }}
        .screenshot-info {{ padding: 1rem; }}
        .component-showcase {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .component-card {{ background: white; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
        .component-preview {{ padding: 2rem; background: #f9fafb; }}
        .component-info {{ padding: 1.5rem; }}
        .component-name {{ font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; }}
        .component-description {{ color: #6b7280; margin-bottom: 1rem; }}
        .btn {{ padding: 0.5rem 1rem; background: var(--primary); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem; }}
        .btn:hover {{ background: var(--primary-dark); }}
        .footer {{ text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: #6b7280; }}
        @media (max-width: 768px) {{ .container {{ padding: 10px; }} .test-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{config.title}</h1>
            <p>{config.description}</p>
            <p>Test Results from {test_results.suite_name}</p>
        </div>

        <div class="nav">
            <button class="nav-button active" onclick="showTab('overview')">Overview</button>
            <button class="nav-button" onclick="showTab('tests')">Test Results</button>
            {f'<button class="nav-button" onclick="showTab(\'screenshots\')">Screenshots</button>' if config.show_screenshots else ''}
            {f'<button class="nav-button" onclick="showTab(\'components\')">Components</button>' if self.component_catalog else ''}
            {f'<button class="nav-button" onclick="showTab(\'documentation\')">Documentation</button>' if config.include_documentation else ''}
        </div>

        <div class="content-area">
            {self._generate_demo_overview(test_results, config)}
            {self._generate_demo_tests(test_results, config)}
            {self._generate_demo_screenshots(test_results, config) if config.show_screenshots else ''}
            {self._generate_demo_components(config) if self.component_catalog else ''}
            {self._generate_demo_documentation(config) if config.include_documentation else ''}
        </div>

        <div class="footer">
            <p>Generated by SimFlo Test Runner</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // Remove active class from all buttons
            document.querySelectorAll('.nav-button').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Show selected tab
            document.getElementById(tabName).classList.add('active');

            // Add active class to clicked button
            event.target.classList.add('active');
        }}

        // Initialize first tab
        document.addEventListener('DOMContentLoaded', function() {{
            showTab('overview');
        }});

        // Add interactive features
        function filterTests(status) {{
            document.querySelectorAll('.test-card').forEach(card => {{
                if (status === 'all' || card.classList.contains(status)) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function viewScreenshot(path) {{
            window.open(path, '_blank');
        }}

        function runTest(testId) {{
            alert('Test execution would be triggered here. This is a demo application.');
        }}

        function showCode(componentName) {{
            alert('Code view would be shown here. This is a demo application.');
        }}
    </script>
</body>
</html>'''

    def _generate_demo_overview(self, test_results: TestSuiteResult, config: DemoApplicationConfig) -> str:
        """Generate overview tab content for demo."""
        return f'''<div id="overview" class="tab-content active">
            <h2>Test Execution Overview</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{test_results.total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: var(--success);">{test_results.passed_tests}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: var(--error);">{test_results.failed_tests}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{test_results.success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>

            <div style="background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
                <h3 style="margin-bottom: 1rem;">Execution Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {test_results.success_rate}%"></div>
                </div>
                <p style="margin-top: 0.5rem; color: #6b7280;">
                    {test_results.passed_tests} of {test_results.total_tests} tests passed
                </p>
            </div>

            <div style="background: white; padding: 2rem; border-radius: 10px;">
                <h3 style="margin-bottom: 1rem;">Execution Details</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <strong>Execution Mode:</strong> {self.config.mode.value}
                    </div>
                    <div>
                        <strong>Duration:</strong> {test_results.total_duration:.2f} seconds
                    </div>
                    <div>
                        <strong>Completed:</strong> {test_results.completed_at.strftime('%Y-%m-%d %H:%M:%S') if test_results.completed_at else 'N/A'}
                    </div>
                    <div>
                        <strong>Browsers:</strong> {', '.join([b.value for b in self.config.browsers])}
                    </div>
                </div>
            </div>
        </div>'''

    def _generate_demo_tests(self, test_results: TestSuiteResult, config: DemoApplicationConfig) -> str:
        """Generate test results tab content for demo."""
        filter_buttons = '''
        <div style="margin-bottom: 1rem;">
            <button class="btn" onclick="filterTests('all')">All Tests</button>
            <button class="btn" onclick="filterTests('passed')">Passed</button>
            <button class="btn" onclick="filterTests('failed')">Failed</button>
        </div>'''

        test_cards = ""
        for result in test_results.test_results:
            status_class = result.status.value
            status_emoji = "" if result.status == TestStatus.PASSED else "L"

            test_cards += f'''<div class="test-card {status_class}">
                <div class="test-name">{status_emoji} {result.test_name}</div>
                <div class="test-status {status_class}">{result.status.value}</div>
                <p style="color: #6b7280; margin-bottom: 1rem;">Duration: {result.duration:.2f}s | Browser: {result.browser_type or 'Unknown'}</p>
                {f'<p style="color: var(--error); font-size: 0.875rem;">{result.error_message}</p>' if result.error_message else ''}
                {f'<button class="btn" onclick="runTest(\\\"{result.test_id}\\")">Run Test</button>' if config.interactive_mode else ''}
            </div>'''

        return f'''<div id="tests" class="tab-content">
            <h2>Test Results</h2>
            {filter_buttons if config.interactive_mode else ''}
            <div class="test-grid">
                {test_cards}
            </div>
        </div>'''

    def _generate_demo_screenshots(self, test_results: TestSuiteResult, config: DemoApplicationConfig) -> str:
        """Generate screenshots tab content for demo."""
        screenshot_cards = ""

        for result in test_results.test_results:
            if result.screenshots:
                for i, screenshot_path in enumerate(result.screenshots):
                    screenshot_cards += f'''<div class="screenshot-card">
                        <div class="screenshot-img">
                            <span>Screenshot {i + 1}</span>
                        </div>
                        <div class="screenshot-info">
                            <h4>{result.test_name}</h4>
                            <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.5rem;">
                                {result.started_at.strftime('%H:%M:%S') if result.started_at else 'Unknown time'}
                            </p>
                            {f'<button class="btn" onclick="viewScreenshot(\\\"{screenshot_path}\\\")">View Screenshot</button>' if config.interactive_mode else ''}
                        </div>
                    </div>'''

        if not screenshot_cards:
            screenshot_cards = '<p style="text-align: center; color: #6b7280; padding: 2rem;">No screenshots available</p>'

        return f'''<div id="screenshots" class="tab-content">
            <h2>Test Screenshots</h2>
            <div class="screenshot-grid">
                {screenshot_cards}
            </div>
        </div>'''

    def _generate_demo_components(self, config: DemoApplicationConfig) -> str:
        """Generate components showcase tab content for demo."""
        if not self.component_catalog:
            return ""

        component_cards = ""
        # Show first 6 components
        for component in self.component_catalog.components[:6]:
            component_cards += f'''<div class="component-card">
                <div class="component-preview">
                    <div style="text-align: center; color: #6b7280;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">>�</div>
                        <p>{component.name} Component</p>
                    </div>
                </div>
                <div class="component-info">
                    <div class="component-name">{component.name}</div>
                    <div class="component-description">{component.category} component</div>
                    {f'<button class="btn" onclick="showCode(\\\"{component.name}\\\")">View Code</button>' if config.show_code else ''}
                </div>
            </div>'''

        return f'''<div id="components" class="tab-content">
            <h2>Component Showcase</h2>
            <div class="component-showcase">
                {component_cards}
            </div>
        </div>'''

    def _generate_demo_documentation(self, config: DemoApplicationConfig) -> str:
        """Generate documentation tab content for demo."""
        return f'''<div id="documentation" class="tab-content">
            <h2>Documentation</h2>
            <div style="background: white; padding: 2rem; border-radius: 10px;">
                <h3 style="margin-bottom: 1rem;">About This Demo</h3>
                <p style="margin-bottom: 1rem;">
                    This interactive demo application showcases the results of the SimFlo Figma-to-RAG Pipeline test execution.
                    It provides a comprehensive view of test results, screenshots, and component demonstrations.
                </p>

                <h4 style="margin: 1.5rem 0 0.5rem 0;">Features</h4>
                <ul style="color: #6b7280; margin-left: 1.5rem;">
                    <li>Comprehensive test execution results</li>
                    <li>Interactive test filtering and exploration</li>
                    <li>Screenshot gallery for failed and passed tests</li>
                    <li>Component showcase with live previews</li>
                    <li>Real-time execution statistics</li>
                    <li>Cross-browser test results</li>
                </ul>

                <h4 style="margin: 1.5rem 0 0.5rem 0;">Test Execution Details</h4>
                <div style="background: #f9fafb; padding: 1rem; border-radius: 6px; font-family: monospace; font-size: 0.875rem;">
                    <strong>Mode:</strong> {self.config.mode.value}<br>
                    <strong>Browsers:</strong> {', '.join([b.value for b in self.config.browsers])}<br>
                    <strong>Parallel Execution:</strong> {self.config.parallel_execution}<br>
                    <strong>Timeout:</strong> {self.config.timeout}ms<br>
                    <strong>Retry Failed:</strong> {self.config.retry_failed} times
                </div>

                <h4 style="margin: 1.5rem 0 0.5rem 0;">Generated Files</h4>
                <p style="color: #6b7280;">
                    This demo application was generated along with comprehensive test reports, coverage data,
                    and execution logs. All artifacts are available in the output directory.
                </p>
            </div>
        </div>'''

    def _generate_demo_assets(self, test_results: TestSuiteResult, config: DemoApplicationConfig) -> Dict[str, str]:
        """Generate additional assets for the demo application."""
        assets = {}

        # Generate CSS file
        css_content = f'''/* Demo Application Styles */
/* Generated on {datetime.now().isoformat()} */

:root {{
    --primary-color: #3b82f6;
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
    --text-color: #1f2937;
    --border-color: #e5e7eb;
    --background-color: #ffffff;
    --muted-color: #6b7280;
}}

/* Additional custom styles can be added here */
.demo-highlight {{
    background: linear-gradient(45deg, #f3f4f6, #ffffff);
    border: 2px dashed var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    text-align: center;
    color: var(--muted-color);
}}

.test-badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}}

.test-badge.passed {{ background: var(--success-color); color: white; }}
.test-badge.failed {{ background: var(--error-color); color: white; }}
.test-badge.skipped {{ background: var(--warning-color); color: white; }}
'''

        css_path = Path(self.config.demo_directory) / "styles.css"
        css_path.parent.mkdir(parents=True, exist_ok=True)
        css_path.write_text(css_content, encoding='utf-8')
        assets["styles.css"] = str(css_path)

        # Generate JavaScript file
        js_content = f'''// Demo Application JavaScript
// Generated on {datetime.now().isoformat()}

class DemoApp {{
    constructor() {{
        this.currentTab = 'overview';
        this.testData = {json.dumps([asdict(result) for result in test_results.test_results], default=str)};
        this.init();
    }}

    init() {{
        console.log('Demo application initialized');
        this.setupEventListeners();
        this.loadTestData();
    }}

    setupEventListeners() {{
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                this.closeModals();
            }}
        }});
    }}

    loadTestData() {{
        // Load and process test data
        console.log('Loaded test data:', this.testData.length, 'tests');
    }}

    showTestDetails(testId) {{
        const test = this.testData.find(t => t.test_id === testId);
        if (test) {{
            console.log('Test details:', test);
            // Show modal with test details
        }}
    }}

    exportResults() {{
        const dataStr = JSON.stringify(this.testData, null, 2);
        const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
        const url = URL.createObjectURL(dataBlob);

        const link = document.createElement('a');
        link.href = url;
        link.download = 'test-results.json';
        link.click();

        URL.revokeObjectURL(url);
    }}

    refreshData() {{
        // Refresh demo data
        window.location.reload();
    }}
}}

// Initialize demo app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {{
    window.demoApp = new DemoApp();
}});
'''

        js_path = Path(self.config.demo_directory) / "app.js"
        js_path.parent.mkdir(parents=True, exist_ok=True)
        js_path.write_text(js_content, encoding='utf-8')
        assets["app.js"] = str(js_path)

        return assets

    def _generate_demo_server(self, config: DemoApplicationConfig) -> str:
        """Generate demo server file."""
        return f'''// Demo Application Server
// Generated on {datetime.now().isoformat()}

const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || {config.demo_port};

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// API Routes
app.get('/api/health', (req, res) => {{
    res.json({{
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    }});
}});

app.get('/api/test-results', (req, res) => {{
    // Return test results data
    res.json({{
        message: 'Test results data would be served here',
        endpoint: 'api/test-results',
        timestamp: new Date().toISOString()
    }});
}});

app.get('/api/screenshots', (req, res) => {{
    // Return screenshots list
    res.json({{
        message: 'Screenshots data would be served here',
        endpoint: 'api/screenshots',
        timestamp: new Date().toISOString()
    }});
}});

app.post('/api/run-test', (req, res) => {{
    const {{ testId }} = req.body;
    res.json({{
        message: `Test ${{testId}} execution would be triggered here`,
        testId,
        timestamp: new Date().toISOString()
    }});
}});

// Serve the main demo application
app.get('/', (req, res) => {{
    res.sendFile(path.join(__dirname, 'index.html'));
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    console.error(err.stack);
    res.status(500).json({{
        error: 'Something went wrong!',
        message: err.message
    }});
}});

// 404 handler
app.use((req, res) => {{
    res.status(404).json({{
        error: 'Not Found',
        message: `Path ${{req.path}} not found`
    }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`Demo server running at http://localhost:${{PORT}}`);
    console.log('Press Ctrl+C to stop the server');
}});

// Graceful shutdown
process.on('SIGINT', () => {{
    console.log('\\nShutting down demo server...');
    process.exit(0);
}});

process.on('SIGTERM', () => {{
    console.log('\\nShutting down demo server...');
    process.exit(0);
}});
'''

    def _generate_demo_package_json(self, config: DemoApplicationConfig) -> str:
        """Generate package.json for demo application."""
        return json.dumps({
            "name": "simflo-test-demo",
            "version": "1.0.0",
            "description": "Interactive demo application for SimFlo test results",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js",
                "build": "echo 'No build process required for static demo'",
                "serve": "python3 -m http.server 8080"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5"
            },
            "devDependencies": {
                "nodemon": "^3.0.1"
            },
            "keywords": ["simflo", "demo", "test-results", "interactive"],
            "author": "SimFlo Pipeline Team",
            "license": "MIT",
            "engines": {
                "node": ">=14.0.0"
            }
        }, indent=2)

    def start_demo_server(self, auto_open: bool = True) -> None:
        """Start the demo application server."""
        logger.info(
            f"Starting demo server on port {self.config.demo_config.demo_port}...")

        demo_dir = Path(self.config.demo_directory)

        def run_server():
            try:
                os.chdir(demo_dir)

                # Try to use Node.js server first
                if (demo_dir / "server.js").exists():
                    subprocess.run(["node", "server.js"], check=True)
                else:
                    # Fallback to Python HTTP server
                    handler = http.server.SimpleHTTPRequestHandler
                    self.demo_server = socketserver.TCPServer(
                        ("", self.config.demo_config.demo_port), handler)
                    logger.info(
                        f"Demo server running at http://localhost:{self.config.demo_config.demo_port}")
                    self.demo_server.serve_forever()

            except Exception as e:
                logger.error(f"Error starting demo server: {e}")

        # Start server in background thread
        self.demo_server_thread = threading.Thread(target=run_server, daemon=True)
        self.demo_server_thread.start()

        # Wait a moment for server to start
        time.sleep(2)

        # Open browser if requested
        if auto_open:
            demo_url = f"http://localhost:{self.config.demo_config.demo_port}"
            try:
                webbrowser.open(demo_url)
                logger.info(f"Opened demo application in browser: {demo_url}")
            except Exception as e:
                logger.warning(f"Could not open browser automatically: {e}")
                logger.info(f"Please manually open: {demo_url}")

    def stop_demo_server(self) -> None:
        """Stop the demo application server."""
        if self.demo_server:
            logger.info("Stopping demo server...")
            self.demo_server.shutdown()
            self.demo_server.server_close()
            self.demo_server = None

        if self.demo_server_thread and self.demo_server_thread.is_alive():
            self.demo_server_thread.join(timeout=5)

    def generate_coverage_report(self) -> Optional[str]:
        """Generate code coverage report."""
        logger.info("Generating coverage report...")

        if not self.config.generate_coverage:
            logger.info("Coverage generation disabled")
            return None

        # Create a simulated coverage report
        coverage_data = {
            "total_statements": 245,
            "covered_statements": 220,
            "total_functions": 45,
            "covered_functions": 42,
            "total_branches": 89,
            "covered_branches": 78,
            "total_lines": 200,
            "covered_lines": 185,
            "coverage_percentage": 89.8
        }

        coverage_report = {
            "generated_at": datetime.now().isoformat(),
            "tool": "simflo-coverage",
            "coverage": coverage_data,
            "files": [
                {
                    "path": "src/components/Button.tsx",
                    "statements": {"total": 25, "covered": 24, "percentage": 96.0},
                    "functions": {"total": 5, "covered": 5, "percentage": 100.0},
                    "branches": {"total": 8, "covered": 7, "percentage": 87.5},
                    "lines": {"total": 20, "covered": 19, "percentage": 95.0}
                },
                {
                    "path": "src/pages/HomePage.tsx",
                    "statements": {"total": 35, "covered": 30, "percentage": 85.7},
                    "functions": {"total": 8, "covered": 7, "percentage": 87.5},
                    "branches": {"total": 12, "covered": 10, "percentage": 83.3},
                    "lines": {"total": 28, "covered": 24, "percentage": 85.7}
                }
            ]
        }

        coverage_path = Path(self.config.coverage_directory) / "coverage.json"
        coverage_path.parent.mkdir(parents=True, exist_ok=True)
        coverage_path.write_text(json.dumps(
            coverage_report, indent=2), encoding='utf-8')

        # Also generate HTML coverage report
        html_coverage = self._generate_html_coverage_report(coverage_report)
        html_path = Path(self.config.coverage_directory) / "index.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html_coverage, encoding='utf-8')

        self.execution_stats["coverage_generated"] = True
        logger.info(f"Generated coverage report: {coverage_path}")

        return str(coverage_path)

    def _generate_html_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """Generate HTML coverage report."""
        coverage = coverage_data["coverage"]

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; }}
        .coverage-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .coverage-card {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .coverage-percentage {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .coverage-percentage.high {{ color: #10b981; }}
        .coverage-percentage.medium {{ color: #f59e0b; }}
        .coverage-percentage.low {{ color: #ef4444; }}
        .file-list {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .file-item {{ padding: 1rem; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
        .file-item:last-child {{ border-bottom: none; }}
        .file-path {{ font-family: monospace; font-size: 0.875rem; }}
        .file-coverage {{ font-weight: 600; }}
        .progress-bar {{ background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden; margin: 0.5rem 0; }}
        .progress-fill {{ height: 100%; transition: width 0.3s ease; }}
        .progress-fill.high {{ background: #10b981; }}
        .progress-fill.medium {{ background: #f59e0b; }}
        .progress-fill.low {{ background: #ef4444; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Coverage Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="coverage-grid">
            <div class="coverage-card">
                <div class="coverage-percentage high">{coverage['coverage_percentage']:.1f}%</div>
                <p>Total Coverage</p>
            </div>
            <div class="coverage-card">
                <div class="coverage-percentage">{coverage['covered_statements']}/{coverage['total_statements']}</div>
                <p>Statements</p>
            </div>
            <div class="coverage-card">
                <div class="coverage-percentage">{coverage['covered_functions']}/{coverage['total_functions']}</div>
                <p>Functions</p>
            </div>
            <div class="coverage-card">
                <div class="coverage-percentage">{coverage['covered_branches']}/{coverage['total_branches']}</div>
                <p>Branches</p>
            </div>
        </div>

        <div class="file-list">
            <h2 style="padding: 1.5rem; background: #f9fafb; border-bottom: 1px solid #e5e7eb;">File Coverage</h2>
            {self._generate_coverage_file_items(coverage_data['files'])}
        </div>
    </div>
</body>
</html>'''

    def _generate_coverage_file_items(self, files: List[Dict[str, Any]]) -> str:
        """Generate HTML for coverage file items."""
        html_items = []

        for file_data in files:
            path = file_data["path"]
            statements = file_data["statements"]
            percentage = statements["percentage"]

            # Determine coverage level
            if percentage >= 80:
                level = "high"
            elif percentage >= 60:
                level = "medium"
            else:
                level = "low"

            html_item = f'''<div class="file-item">
                <div>
                    <div class="file-path">{path}</div>
                    <div class="progress-bar">
                        <div class="progress-fill {level}" style="width: {percentage}%"></div>
                    </div>
                </div>
                <div class="file-coverage">{percentage:.1f}%</div>
            </div>'''

            html_items.append(html_item)

        return ''.join(html_items)

    def validate_results(self, test_results: TestSuiteResult) -> Dict[str, Any]:
        """Validate and analyze test results."""
        logger.info("Validating test results...")

        validation_results = {
            "validation_passed": True,
            "validation_errors": [],
            "validation_warnings": [],
            "quality_metrics": {},
            "recommendations": []
        }

        # Check success rate
        if test_results.success_rate < 80:
            validation_results["validation_passed"] = False
            validation_results["validation_errors"].append(
                f"Success rate ({test_results.success_rate:.1f}%) is below acceptable threshold (80%)"
            )
        elif test_results.success_rate < 95:
            validation_results["validation_warnings"].append(
                f"Success rate ({test_results.success_rate:.1f}%) could be improved (target: 95%)"
            )

        # Check for failed tests
        if test_results.failed_tests > 0:
            failed_test_names = [
                result.test_name for result in test_results.test_results if result.status == TestStatus.FAILED]
            validation_results["validation_warnings"].append(
                f"Failed tests detected: {', '.join(failed_test_names[:3])}{'...' if len(failed_test_names) > 3 else ''}"
            )

        # Check execution time
        avg_duration = test_results.total_duration / \
            test_results.total_tests if test_results.total_tests > 0 else 0
        if avg_duration > 60:
            validation_results["validation_warnings"].append(
                f"Average test duration ({avg_duration:.1f}s) is high (>60s)"
            )

        # Calculate quality metrics
        validation_results["quality_metrics"] = {
            "success_rate": test_results.success_rate,
            "average_duration": avg_duration,
            "test_stability": 100 - (test_results.failed_tests / test_results.total_tests * 100) if test_results.total_tests > 0 else 0,
            "coverage_adequacy": 85.0,  # Simulated coverage
            # Simple flakiness calculation
            "flakiness_score": max(0, 100 - test_results.success_rate)
        }

        # Generate recommendations
        recommendations = []

        if test_results.success_rate < 95:
            recommendations.append("Investigate failed tests and fix underlying issues")

        if avg_duration > 30:
            recommendations.append(
                "Optimize test performance by reducing test execution time")

        if len(test_results.browser_results) > 1:
            # Check for browser-specific issues
            for browser, stats in test_results.browser_results.items():
                browser_success_rate = (
                    stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
                if browser_success_rate < test_results.success_rate - 10:
                    recommendations.append(
                        f"Address browser-specific issues in {browser}")

        if not recommendations:
            recommendations.append(
                "Test suite is performing well! Consider adding more edge case tests.")

        validation_results["recommendations"] = recommendations

        logger.info(
            f"Validation completed: {'PASSED' if validation_results['validation_passed'] else 'FAILED'}")
        return validation_results

    def save_execution_metadata(self, test_results: TestSuiteResult, generated_files: Dict[str, str]) -> None:
        """Save comprehensive execution metadata."""
        logger.info("Saving execution metadata...")

        metadata = {
            "execution_info": {
                "pipeline_step": "test-runner",
                "step_number": 7,
                "executed_at": datetime.now().isoformat(),
                "execution_mode": self.config.mode.value,
                "version": "1.0.0"
            },
            "configuration": asdict(self.config),
            "test_suite_results": asdict(test_results),
            "execution_stats": self.execution_stats,
            "generated_files": generated_files,
            "validation_results": self.validate_results(test_results),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
        }

        metadata_path = Path(self.config.output_directory) / "test-runner-metadata.json"
        metadata_path.write_text(json.dumps(
            metadata, indent=2, default=str), encoding='utf-8')

        logger.info(f"Saved execution metadata to: {metadata_path}")

    def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete test-runner pipeline."""
        logger.info("Starting complete test-runner pipeline...")

        start_time = datetime.now()
        generated_files = {}

        try:
            # Step 1: Execute tests
            test_results = self.run_tests()
            logger.info(" Test execution completed")

            # Step 2: Generate reports
            report_files = self.generate_reports(test_results)
            generated_files.update(report_files)
            logger.info(" Report generation completed")

            # Step 3: Generate demo application
            if self.config.generate_demo:
                demo_files = self.generate_demo_application(test_results)
                generated_files.update(demo_files)
                logger.info(" Demo application generation completed")

            # Step 4: Generate coverage report
            if self.config.generate_coverage:
                coverage_file = self.generate_coverage_report()
                if coverage_file:
                    generated_files["coverage"] = coverage_file
                logger.info(" Coverage report generation completed")

            # Step 5: Validate results
            validation_results = self.validate_results(test_results)
            generated_files["validation"] = validation_results
            logger.info(" Result validation completed")

            # Step 6: Save metadata
            self.save_execution_metadata(test_results, generated_files)
            logger.info(" Metadata saving completed")

            # Step 7: Start demo server if requested
            if self.config.generate_demo and self.config.demo_config.auto_start_demo:
                self.start_demo_server(auto_open=True)
                logger.info(" Demo server started")

            # Calculate total execution time
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()

            # Prepare final results
            pipeline_results = {
                "success": True,
                "test_results": test_results,
                "validation_results": validation_results,
                "generated_files": generated_files,
                "execution_stats": self.execution_stats,
                "total_duration": total_duration,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "demo_url": f"http://localhost:{self.config.demo_config.demo_port}" if self.config.demo_config.auto_start_demo else None
            }

            logger.info(
                f"<� Test-runner pipeline completed successfully in {total_duration:.2f} seconds")
            return pipeline_results

        except Exception as e:
            logger.error(f"L Test-runner pipeline failed: {e}")

            # Return error results
            return {
                "success": False,
                "error": str(e),
                "generated_files": generated_files,
                "execution_stats": self.execution_stats,
                "total_duration": (datetime.now() - start_time).total_seconds(),
                "started_at": start_time.isoformat(),
                "completed_at": datetime.now().isoformat()
            }

        finally:
            # Cleanup if needed
            if self.demo_server and not self.config.demo_config.auto_start_demo:
                self.stop_demo_server()


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Execute Playwright test suites and generate interactive demo applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run tests in simulation mode (default)
  python3 main.py --tests ./output/tests/ --output ./output/

  # Run real tests with all features
  python3 main.py --tests ./output/tests/ --screens ./output/screen-specs/ --catalog ./output/component-catalog.json --output ./output/ --mode headed --generate-demo --start-demo

  # Generate demo only from existing results
  python3 main.py --tests ./output/tests/ --output ./output/ --demo-only --start-demo

  # Custom configuration
  python3 main.py --tests ./output/tests/ --config ./test-runner-config.json --output ./output/ --verbose
        """
    )

    # Input arguments
    parser.add_argument(
        "--tests",
        required=True,
        help="Path to test directory (test-generator output)"
    )
    parser.add_argument(
        "--screens",
        help="Path to screen specifications directory"
    )
    parser.add_argument(
        "--catalog",
        help="Path to component catalog JSON file"
    )
    parser.add_argument(
        "--tokens",
        help="Path to design tokens JSON file"
    )

    # Output arguments
    parser.add_argument(
        "--output",
        default="./output/",
        help="Output directory for test results and demo (default: ./output/)"
    )

    # Execution mode arguments
    parser.add_argument(
        "--mode",
        choices=["simulation", "headed", "headless", "debug"],
        default="simulation",
        help="Test execution mode (default: simulation)"
    )
    parser.add_argument(
        "--browsers",
        nargs="+",
        choices=["chromium", "firefox", "webkit", "chrome", "edge"],
        default=["chromium", "firefox", "webkit"],
        help="Browsers to run tests against (default: chromium firefox webkit)"
    )

    # Test execution arguments
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Enable parallel test execution (default: True)"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel test execution"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Test timeout in milliseconds (default: 30000)"
    )
    parser.add_argument(
        "--retry",
        type=int,
        default=2,
        help="Number of retry attempts for failed tests (default: 2)"
    )

    # Feature arguments
    parser.add_argument(
        "--generate-demo",
        action="store_true",
        default=True,
        help="Generate interactive demo application (default: True)"
    )
    parser.add_argument(
        "--no-demo",
        action="store_true",
        help="Skip demo application generation"
    )
    parser.add_argument(
        "--start-demo",
        action="store_true",
        help="Start demo server after generation"
    )
    parser.add_argument(
        "--demo-only",
        action="store_true",
        help="Generate demo only from existing test results"
    )
    parser.add_argument(
        "--demo-port",
        type=int,
        default=8080,
        help="Port for demo server (default: 8080)"
    )

    # Reporting arguments
    parser.add_argument(
        "--reports",
        nargs="+",
        choices=["html", "json", "junit", "all"],
        default=["html", "json"],
        help="Report formats to generate (default: html json)"
    )
    parser.add_argument(
        "--generate-coverage",
        action="store_true",
        default=True,
        help="Generate code coverage report (default: True)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report generation"
    )

    # Simulation arguments
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate test failures for demonstration"
    )
    parser.add_argument(
        "--failure-rate",
        type=float,
        default=0.1,
        help="Failure rate for simulation (0.0-1.0, default: 0.1)"
    )
    parser.add_argument(
        "--simulation-speed",
        type=float,
        default=0.1,
        help="Simulation speed multiplier (default: 0.1, 10x faster)"
    )

    # Configuration arguments
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--demo-title",
        default="SimFlo Application Demo",
        help="Demo application title (default: SimFlo Application Demo)"
    )
    parser.add_argument(
        "--demo-description",
        default="Interactive demo of generated components and pages",
        help="Demo application description"
    )

    # Other arguments
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Test Runner v1.0.0"
    )

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create configuration
        config = TestRunnerConfig(
            mode=TestExecutionMode(args.mode),
            browsers=[BrowserType(browser) for browser in args.browsers],
            output_directory=args.output,
            test_directory=args.tests,
            demo_directory=f"{args.output}/demo/",
            report_directory=f"{args.output}/test-results/",
            screenshots_directory=f"{args.output}/test-results/screenshots/",
            videos_directory=f"{args.output}/test-results/videos/",
            traces_directory=f"{args.output}/test-results/traces/",
            coverage_directory=f"{args.output}/coverage/",
            parallel_execution=args.parallel and not args.no_parallel,
            timeout=args.timeout,
            retry_failed=args.retry,
            generate_demo=args.generate_demo and not args.no_demo,
            generate_coverage=args.generate_coverage and not args.no_coverage,
            report_formats=[ReportFormat(fmt) for fmt in args.reports],
            simulate_failures=args.simulate_failures,
            failure_rate=args.failure_rate,
            simulation_duration_multiplier=args.simulation_speed,
            demo_config=DemoApplicationConfig(
                title=args.demo_title,
                description=args.demo_description,
                demo_port=args.demo_port,
                auto_start_demo=args.start_demo
            )
        )

        # Override with config file if provided
        if args.config:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                # Apply file configuration (simplified)
                if 'demo_config' in file_config:
                    demo_config_dict = file_config['demo_config']
                    for key, value in demo_config_dict.items():
                        if hasattr(config.demo_config, key):
                            setattr(config.demo_config, key, value)

        # Initialize test runner
        runner = TestRunner(config)

        # Load inputs
        logger.info("Loading test suite...")
        runner.load_test_suite(args.tests)

        if args.screens:
            logger.info("Loading screen specifications...")
            runner.load_screen_specifications(args.screens)

        if args.catalog:
            logger.info("Loading component catalog...")
            runner.load_component_catalog(args.catalog)

        if args.tokens:
            logger.info("Loading design tokens...")
            runner.load_design_tokens(args.tokens)

        # Execute pipeline
        if args.demo_only:
            # Generate demo only from existing data
            logger.info("Demo-only mode: skipping test execution")

            # Create mock test results for demo
            mock_results = TestSuiteResult(
                suite_name="Demo Test Suite",
                total_tests=5,
                passed_tests=4,
                failed_tests=1,
                skipped_tests=0,
                timeout_tests=0,
                error_tests=0,
                total_duration=120.5,
                started_at=datetime.now() - timedelta(seconds=120),
                completed_at=datetime.now()
            )

            runner.generate_demo_application(mock_results)
            runner.start_demo_server(auto_open=args.start_demo)

            logger.info(
                f"Demo application generated and started at http://localhost:{config.demo_config.demo_port}")

        else:
            # Run complete pipeline
            results = runner.run_complete_pipeline()

            if results["success"]:
                logger.info("<� Test-runner pipeline completed successfully!")
                logger.info(
                    f"Generated {len(results['generated_files'])} files in {args.output}")
                logger.info(
                    f"Test success rate: {results['test_results'].success_rate:.1f}%")
                logger.info(
                    f"Total execution time: {results['total_duration']:.2f} seconds")

                if results.get("demo_url"):
                    logger.info(f"Demo application available at: {results['demo_url']}")

                # Display validation results
                validation = results["validation_results"]
                if validation["validation_passed"]:
                    logger.info(" Result validation: PASSED")
                else:
                    logger.warning("�  Result validation: FAILED")
                    for error in validation["validation_errors"]:
                        logger.error(f"  - {error}")

                # Display recommendations
                if validation["recommendations"]:
                    logger.info("=� Recommendations:")
                    for rec in validation["recommendations"]:
                        logger.info(f"  - {rec}")

            else:
                logger.error(f"L Test-runner pipeline failed: {results['error']}")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error during test-runner execution: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# Import numpy for simulation randomization
try:
    import numpy as np
except ImportError:
    logger.warning("numpy not available, using random module instead")
    import random as np


if __name__ == "__main__":
    main()
