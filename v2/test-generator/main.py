#!/usr/bin/env python3
"""
Test Generator - Step 6 of SimFlo Figma-to-RAG Pipeline

Generates comprehensive Playwright E2E test suites from test scenarios and page implementations.
Supports TypeScript, Page Object Model, test data fixtures, visual regression testing,
accessibility testing, mobile device testing, and comprehensive test reporting.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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
    from common.validation import validate_and_load, CustomValidationError
    from common.schemas import (
        TestScenario, TestSuite, TestStep, TestAction, TestDataRequirement,
        ScreenSpecification, ComponentCatalog, ComponentDefinition, ComponentInstance,
        NavigationRelationship, DesignTokenSet, ComponentProperty
    )
except ImportError as e:
    logger.warning(f"Could not import from common module: {e}")
    # Define fallback schemas for testing
    from pydantic import BaseModel, Field

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


class TestFramework(Enum):
    """Supported test frameworks."""
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    SELENIUM = "selenium"


class TestType(Enum):
    """Types of tests to generate."""
    E2E = "e2e"
    INTEGRATION = "integration"
    COMPONENT = "component"
    VISUAL = "visual"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class BrowserType(Enum):
    """Supported browsers for testing."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"


class DeviceType(Enum):
    """Device types for mobile testing."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


@dataclass
class TestGenerationConfig:
    """Configuration for test generation."""
    framework: TestFramework = TestFramework.PLAYWRIGHT
    test_types: List[TestType] = None
    browsers: List[BrowserType] = None
    devices: List[DeviceType] = None
    output_directory: str = "./output/"
    tests_directory: str = "./output/tests/"
    fixtures_directory: str = "./output/tests/fixtures/"
    utils_directory: str = "./output/tests/utils/"
    pages_directory: str = "./output/tests/pages/"
    reports_directory: str = "./output/test-results/"
    include_visual_testing: bool = True
    include_accessibility_testing: bool = True
    include_mobile_testing: bool = True
    include_performance_testing: bool = False
    include_api_mocking: bool = True
    use_typescript: bool = True
    use_page_object_model: bool = True
    generate_data_driven_tests: bool = True
    generate_error_scenarios: bool = True
    parallel_execution: bool = True
    retry_failed_tests: int = 2
    timeout: int = 30000
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True
    custom_templates: Optional[Dict[str, str]] = None
    indent_size: int = 2
    base_url: str = "http://localhost:3000"
    test_environment: str = "test"

    def __post_init__(self):
        if self.test_types is None:
            self.test_types = [TestType.E2E, TestType.INTEGRATION, TestType.COMPONENT]
        if self.browsers is None:
            self.browsers = [BrowserType.CHROMIUM, BrowserType.FIREFOX, BrowserType.WEBKIT]
        if self.devices is None:
            self.devices = [DeviceType.DESKTOP, DeviceType.MOBILE, DeviceType.TABLET]


class TestGenerator:
    """
    Main test generator class.

    Generates comprehensive Playwright test suites with support for:
    - Multiple test frameworks (Playwright primary)
    - TypeScript interfaces and type safety
    - Page Object Model (POM) architecture
    - Test data fixtures and management
    - Visual regression testing
    - Accessibility testing (WCAG compliance)
    - Mobile device testing
    - Performance testing
    - API mocking and data management
    - Comprehensive test reporting
    """

    def __init__(self, config: Optional[TestGenerationConfig] = None):
        """Initialize test generator with configuration."""
        self.config = config or TestGenerationConfig()
        self.test_suite: Optional[TestSuite] = None
        self.screen_specifications: List[ScreenSpecification] = []
        self.component_catalog: Optional[ComponentCatalog] = None
        self.processing_stats = {
            "scenarios_processed": 0,
            "tests_generated": 0,
            "page_objects_generated": 0,
            "fixtures_generated": 0,
            "utilities_generated": 0,
            "visual_tests_generated": 0,
            "accessibility_tests_generated": 0,
            "mobile_tests_generated": 0,
            "total_files_created": 0,
            "tests_by_category": {},
            "tests_by_priority": {},
            "estimated_test_duration": 0
        }

    def load_test_scenarios(self, scenarios_path: str) -> None:
        """Load and validate test scenarios from markdown files."""
        logger.info(f"Loading test scenarios from: {scenarios_path}")

        scenarios_dir = Path(scenarios_path)
        if not scenarios_dir.exists():
            raise FileNotFoundError(f"Test scenarios directory not found: {scenarios_path}")

        scenarios = []

        # Load markdown test scenario files
        for md_file in scenarios_dir.glob("*.md"):
            try:
                scenario = self._parse_markdown_scenario(md_file)
                scenarios.append(scenario)
                logger.info(f"Loaded scenario: {scenario.name}")
            except Exception as e:
                logger.error(f"Error loading scenario from {md_file}: {e}")

        # Also load JSON test scenario files if they exist
        for json_file in scenarios_dir.glob("*.json"):
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
                else:
                    # Single scenario
                    scenario = TestScenario(**data)
                    scenarios.append(scenario)
                logger.info(f"Loaded scenario from JSON: {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading scenario from {json_file}: {e}")

        self.test_suite = TestSuite(
            name="Generated Test Suite",
            description="Test scenarios generated from prototype analyzer",
            scenarios=scenarios,
            configuration={"generated_at": datetime.now().isoformat()}
        )

        logger.info(f"Loaded {len(scenarios)} test scenarios")

    def _parse_markdown_scenario(self, md_file: Path) -> TestScenario:
        """Parse test scenario from markdown file."""
        content = md_file.read_text()

        # Extract scenario metadata from frontmatter or headers
        scenario_id = md_file.stem
        name = scenario_id.replace("-", " ").title()
        description = ""
        category = "custom"
        priority = "medium"
        tags = []
        steps = []
        test_data = []
        success_criteria = []
        estimated_duration = None

        # Parse markdown content
        lines = content.split('\n')
        current_section = None
        current_step = None

        for line in lines:
            line = line.strip()

            # Extract metadata from headers
            if line.startswith("**ID**:"):
                scenario_id = line.split(":", 1)[1].strip()
            elif line.startswith("**Name**:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("**Description**:"):
                description = line.split(":", 1)[1].strip()
            elif line.startswith("**Category**:"):
                category = line.split(":", 1)[1].strip().lower()
            elif line.startswith("**Priority**:"):
                priority = line.split(":", 1)[1].strip().lower()
            elif line.startswith("**Tags**:"):
                tags_str = line.split(":", 1)[1].strip()
                tags = [tag.strip() for tag in tags_str.split(",")]
            elif line.startswith("**Estimated Duration**:"):
                duration_str = line.split(":", 1)[1].strip()
                # Extract duration in seconds
                import re
                match = re.search(r'(\d+)', duration_str)
                if match:
                    estimated_duration = int(match.group(1))

            # Section headers
            elif line.startswith("## "):
                current_section = line[3:].lower()
            elif line.startswith("### Step"):
                if current_step:
                    steps.append(current_step)
                # Parse step number
                step_match = re.search(r'Step (\d+)', line)
                step_number = int(step_match.group(1)) if step_match else len(steps) + 1
                current_step = TestStep(
                    step_number=step_number,
                    description="",
                    actions=[],
                    validations=[]
                )
            elif line.startswith("**Description**:") and current_step:
                current_step.description = line.split(":", 1)[1].strip()
            elif line.startswith("**Actions**:") and current_step:
                # Parse actions (simplified - would need more sophisticated parsing)
                current_section = "actions"
            elif line.startswith("**Validations**:") and current_step:
                # Parse validations
                current_section = "validations"
            elif line.startswith("**Preconditions**:") and current_step:
                # Parse preconditions
                current_section = "preconditions"
            elif line.startswith("**Postconditions**:") and current_step:
                # Parse postconditions
                current_section = "postconditions"
            elif line.startswith("## Success Criteria"):
                current_section = "success_criteria"
            elif line.startswith("## Test Data Requirements"):
                current_section = "test_data"

            # Content parsing based on current section
            elif current_section == "success_criteria" and line.startswith("- ["):
                criterion = line.lstrip("- [ ] ").strip()
                if criterion:
                    success_criteria.append(criterion)
            elif current_section == "test_data" and line.startswith("- **"):
                # Parse test data requirement
                if "**Type**:" in line:
                    data_type = line.split("**Type**:")[1].split("**")[0].strip()
                    description = ""
                    if "**Description**:" in line:
                        description = line.split("**Description**:")[1].split("**")[0].strip()

                    test_data.append(TestDataRequirement(
                        type=data_type,
                        description=description
                    ))
            elif current_section and line.startswith("- ") and current_step:
                # Parse list items for actions, validations, etc.
                item = line[2:].strip()
                if item and current_section in ["actions", "validations"]:
                    action = self._parse_action_from_text(item)
                    if current_section == "actions":
                        current_step.actions.append(action)
                    else:
                        current_step.validations.append(action)
                elif item and current_section in ["preconditions"] and current_step:
                    current_step.preconditions.append(item)
                elif item and current_section in ["postconditions"] and current_step:
                    current_step.postconditions.append(item)

        # Add last step if exists
        if current_step:
            steps.append(current_step)

        return TestScenario(
            id=scenario_id,
            name=name,
            description=description,
            category=category,
            priority=priority,
            tags=tags,
            steps=steps,
            test_data=test_data,
            success_criteria=success_criteria,
            estimated_duration=estimated_duration
        )

    def _parse_action_from_text(self, text: str) -> TestAction:
        """Parse action from text description."""
        # Simple action parsing - would need more sophisticated NLP in production
        action_type = "click"
        target = {"type": "element", "selector": "button"}
        parameters = {}
        description = text

        # Detect action type
        if "click" in text.lower() or "tap" in text.lower():
            action_type = "click"
        elif "type" in text.lower() or "enter" in text.lower():
            action_type = "type"
        elif "navigate" in text.lower():
            action_type = "navigate"
        elif "wait" in text.lower():
            action_type = "wait"
        elif "assert" in text.lower() or "verify" in text.lower():
            action_type = "assert"
        elif "scroll" in text.lower():
            action_type = "scroll"
        elif "select" in text.lower():
            action_type = "select"

        # Extract target from text
        if "button" in text.lower():
            target["selector"] = "button"
        elif "input" in text.lower() or "field" in text.lower():
            target["selector"] = "input"
        elif "email" in text.lower():
            target["selector"] = "input[type='email']"
        elif "password" in text.lower():
            target["selector"] = "input[type='password']"
        elif "link" in text.lower() or "anchor" in text.lower():
            target["selector"] = "a"
        elif "navigation" in text.lower():
            target["type"] = "navigation"

        return TestAction(
            action_type=action_type,
            target=target,
            parameters=parameters,
            description=description
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
                logger.error(f"Error loading screen specification from {json_file}: {e}")

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
            logger.info(f"Loaded component catalog with {len(self.component_catalog.components)} components")
        except Exception as e:
            logger.error(f"Error loading component catalog: {e}")

    def generate_tests(self) -> Dict[str, str]:
        """Generate all test files."""
        logger.info("Starting test generation...")

        if not self.test_suite:
            raise ValueError("No test suite loaded. Call load_test_scenarios() first.")

        generated_files = {}

        # Create output directories
        self._create_output_directories()

        # Generate Playwright configuration
        if self.config.framework == TestFramework.PLAYWRIGHT:
            playwright_config = self._generate_playwright_config()
            config_path = Path(self.config.output_directory) / "playwright.config.ts"
            config_path.write_text(playwright_config, encoding='utf-8')
            generated_files["playwright.config.ts"] = str(config_path)
            logger.info("Generated Playwright configuration")

        # Generate TypeScript configuration
        if self.config.use_typescript:
            ts_config = self._generate_typescript_config()
            ts_config_path = Path(self.config.output_directory) / "tsconfig.json"
            ts_config_path.write_text(ts_config, encoding='utf-8')
            generated_files["tsconfig.json"] = str(ts_config_path)
            logger.info("Generated TypeScript configuration")

        # Generate Page Object Models
        if self.config.use_page_object_model:
            page_objects = self._generate_page_objects()
            generated_files.update(page_objects)
            logger.info(f"Generated {len(page_objects)} page object files")

        # Generate test data fixtures
        fixtures = self._generate_test_fixtures()
        generated_files.update(fixtures)
        logger.info(f"Generated {len(fixtures)} test fixture files")

        # Generate test utilities
        utilities = self._generate_test_utilities()
        generated_files.update(utilities)
        logger.info(f"Generated {len(utilities)} test utility files")

        # Generate test files for each scenario
        for scenario in self.test_suite.scenarios:
            scenario_files = self._generate_scenario_tests(scenario)
            generated_files.update(scenario_files)
            self.processing_stats["scenarios_processed"] += 1

        # Generate test runner and reports
        runner_files = self._generate_test_runner()
        generated_files.update(runner_files)
        logger.info("Generated test runner and report configuration")

        # Update statistics
        self._update_processing_stats()

        logger.info(f"Generated {len(generated_files)} total test files")
        return generated_files

    def _create_output_directories(self) -> None:
        """Create output directories if they don't exist."""
        directories = [
            self.config.output_directory,
            self.config.tests_directory,
            self.config.fixtures_directory,
            self.config.utils_directory,
            self.config.pages_directory,
            self.config.reports_directory
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _generate_playwright_config(self) -> str:
        """Generate Playwright configuration file."""
        config = f'''import {{ defineConfig, devices }} from '@playwright/test';

/**
 * Playwright configuration for SimFlo test suite
 * Generated on: {datetime.now().isoformat()}
 */
export default defineConfig({{
  testDir: './tests',
  fullyParallel: {str(self.config.parallel_execution).lower()},
  forbidOnly: !!process.env.CI,
  retries: {self.config.retry_failed_tests},
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', {{ outputFile: 'test-results/results.json' }}],
    ['junit', {{ outputFile: 'test-results/results.xml' }}],
    ['line'],
  ],
  use: {{
    baseURL: '{self.config.base_url}',
    trace: 'on-first-retry',
    screenshot: {str(self.config.screenshot_on_failure).lower()},
    video: {str(self.config.video_on_failure).lower()},
  }},
  projects: [
    {{
      name: 'chromium',
      use: {{ ...devices['Desktop Chrome'] }},
    }},
    {{
      name: 'firefox',
      use: {{ ...devices['Desktop Firefox'] }},
    }},
    {{
      name: 'webkit',
      use: {{ ...devices['Desktop Safari'] }},
    }},
    {{#if include_mobile_testing}}
    {{
      name: 'Mobile Chrome',
      use: {{ ...devices['Pixel 5'] }},
    }},
    {{
      name: 'Mobile Safari',
      use: {{ ...devices['iPhone 12'] }},
    }},
    {{/if}}
  ],
  webServer: {{
    command: 'npm start',
    url: '{self.config.base_url}',
    reuseExistingServer: !process.env.CI,
  }},
}});
'''
        return config

    def _generate_typescript_config(self) -> str:
        """Generate TypeScript configuration for tests."""
        config = '''{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "types": ["node", "playwright"],
    "esModuleInterop": True,
    "allowSyntheticDefaultImports": True,
    "strict": True,
    "skipLibCheck": True,
    "forceConsistentCasingInFileNames": True,
    "resolveJsonModule": True,
    "isolatedModules": True,
    "noEmit": True,
    "declaration": True,
    "outDir": "./dist",
    "rootDir": "./src",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/tests/*": ["./tests/*"],
      "@/pages/*": ["./tests/pages/*"],
      "@/fixtures/*": ["./tests/fixtures/*"],
      "@/utils/*": ["./tests/utils/*"]
    }
  },
  "include": [
    "tests/**/*",
    "types/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "test-results"
  ]
}'''
        return config

    def _generate_page_objects(self) -> Dict[str, str]:
        """Generate Page Object Model files."""
        page_objects = {}

        # Generate base page class
        base_page = self._generate_base_page_class()
        base_page_path = Path(self.config.pages_directory) / "BasePage.ts"
        base_page_path.write_text(base_page, encoding='utf-8')
        page_objects["BasePage.ts"] = str(base_page_path)

        # Generate page objects for each screen
        for screen in self.screen_specifications:
            page_object = self._generate_screen_page_object(screen)
            page_object_path = Path(self.config.pages_directory) / f"{screen.id.title()}Page.ts"
            page_object_path.write_text(page_object, encoding='utf-8')
            page_objects[f"{screen.id.title()}Page.ts"] = str(page_object_path)
            self.processing_stats["page_objects_generated"] += 1

        return page_objects

    def _generate_base_page_class(self) -> str:
        """Generate base Page Object Model class."""
        return '''import { Page, Locator, expect } from '@playwright/test';

/**
 * Base Page Object Model class
 * Provides common functionality for all page objects
 */
export abstract class BasePage {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to a URL
   */
  async navigate(path: string = ''): Promise<void> {
    await this.page.goto(path);
  }

  /**
   * Wait for page to load completely
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Take a screenshot
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png` });
  }

  /**
   * Wait for element to be visible
   */
  async waitForElement(selector: string): Promise<Locator> {
    return this.page.waitForSelector(selector, { state: 'visible' });
  }

  /**
   * Click on an element
   */
  async click(selector: string): Promise<void> {
    await this.page.waitForSelector(selector);
    await this.page.click(selector);
  }

  /**
   * Type text into an input field
   */
  async type(selector: string, text: string): Promise<void> {
    await this.page.waitForSelector(selector);
    await this.page.fill(selector, text);
  }

  /**
   * Get text from an element
   */
  async getText(selector: string): Promise<string> {
    await this.page.waitForSelector(selector);
    return this.page.textContent(selector) || '';
  }

  /**
   * Check if element is visible
   */
  async isVisible(selector: string): Promise<boolean> {
    return await this.page.isVisible(selector);
  }

  /**
   * Wait for navigation to complete
   */
  async waitForNavigation(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Check accessibility of the page
   */
  async checkAccessibility(): Promise<void> {
    // Basic accessibility checks
    await expect(this.page.locator('h1')).toBeVisible();
    await expect(this.page.locator('main')).toBeVisible();
  }

  /**
   * Abstract method to get page title
   */
  abstract getPageTitle(): string;

  /**
   * Abstract method to check if page is loaded
   */
  abstract async isLoaded(): Promise<boolean>;
}'''

    def _generate_screen_page_object(self, screen: ScreenSpecification) -> str:
        """Generate Page Object Model for a specific screen."""
        class_name = f"{screen.id.title()}Page"

        # Extract elements from component instances
        elements = []
        for instance in screen.component_instances:
            component_name = instance.name.lower().replace(" ", "_")
            selector = self._generate_selector_for_component(instance)
            elements.append({
                "name": component_name,
                "selector": selector,
                "type": "Locator"
            })

        # Generate page class
        page_class = f'''import {{ Page, Locator, expect }} from '@playwright/test';
import {{ BasePage }} from './BasePage';

/**
 * Page Object Model for {screen.name}
 * Generated from screen specification: {screen.id}
 */
export class {class_name} extends BasePage {{
  // Page elements
{self._generate_page_elements(elements)}

  constructor(page: Page) {{
    super(page);
  }}

  /**
   * Get the page title
   */
  getPageTitle(): string {{
    return '{screen.name}';
  }}

  /**
   * Check if the page is loaded
   */
  async isLoaded(): Promise<boolean> {{
    try {{
      await this.waitForLoad();
      // Check for key elements that indicate page is loaded
      return await this.isVisible('body');
    }} catch (error) {{
      return False;
    }}
  }}

  /**
   * Navigate to this page
   */
  async navigateToPage(): Promise<void> {{
    await this.navigate('/{screen.id}');
    await this.isLoaded();
  }}

{self._generate_page_methods(screen, elements)}
}}'''
        return page_class

    def _generate_selector_for_component(self, instance: ComponentInstance) -> str:
        """Generate CSS selector for a component instance."""
        # Use component ID as primary selector
        if instance.id:
            return f"[data-testid='{instance.id}']"

        # Use component name and type
        component_name = instance.name.lower().replace(" ", "-")
        if instance.component_id:
            return f"[data-component='{instance.component_id}']"

        return f".{component_name}"

    def _generate_page_elements(self, elements: List[Dict[str, str]]) -> str:
        """Generate element definitions for page object."""
        if not elements:
            return "  // No elements defined"

        elements_code = []
        for element in elements:
            elements_code.append(f"  {element['name']}: Locator;")

        return "\n".join(elements_code)

    def _generate_page_methods(self, screen: ScreenSpecification, elements: List[Dict[str, str]]) -> str:
        """Generate page-specific methods."""
        methods = []

        # Generate element initialization
        if elements:
            init_code = "  // Initialize elements in constructor\n"
            for element in elements:
                init_code += f"  this.{element['name']} = this.page.locator('{element['selector']}');\n"
            methods.append(init_code)

        # Generate navigation methods based on flows
        for flow in screen.navigation_flows:
            if isinstance(flow, dict) and 'target_screen_id' in flow:
                target_screen = flow['target_screen_id']
                trigger_element = flow.get('trigger_element_id', '')
                methods.append(f'''
  /**
   * Navigate to {target_screen}
   */
  async navigateTo{target_screen.title()}(): Promise<void> {{
    await this.click('{trigger_element}');
    await this.waitForNavigation();
  }}''')

        # Generate common interaction methods
        for element in elements:
            element_name = element['name']
            methods.append(f'''
  /**
   * Click on {element_name.replace('_', ' ')}
   */
  async click{element_name.title().replace('_', '')}(): Promise<void> {{
    await this.{element_name}.click();
  }}

  /**
   * Get text from {element_name.replace('_', ' ')}
   */
  async get{element_name.title().replace('_', '')}Text(): Promise<string> {{
    return await this.{element_name}.textContent() || '';
  }}''')

        return "\n".join(methods)

    def _generate_test_fixtures(self) -> Dict[str, str]:
        """Generate test data fixtures."""
        fixtures = {}

        # Generate test data from scenarios
        if self.test_suite:
            for scenario in self.test_suite.scenarios:
                if scenario.test_data:
                    fixture_data = self._generate_scenario_fixture(scenario)
                    fixture_path = Path(self.config.fixtures_directory) / f"{scenario.id}.json"
                    fixture_path.write_text(fixture_data, encoding='utf-8')
                    fixtures[f"{scenario.id}.json"] = str(fixture_path)
                    self.processing_stats["fixtures_generated"] += 1

        # Generate common fixtures
        common_fixtures = self._generate_common_fixtures()
        for fixture_name, fixture_content in common_fixtures.items():
            fixture_path = Path(self.config.fixtures_directory) / fixture_name
            fixture_path.write_text(fixture_content, encoding='utf-8')
            fixtures[fixture_name] = str(fixture_path)

        return fixtures

    def _generate_scenario_fixture(self, scenario: TestScenario) -> str:
        """Generate fixture data for a specific scenario."""
        fixture_data = {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "test_data": {}
        }

        for data_req in scenario.test_data:
            fixture_data["test_data"][data_req.type] = data_req.data

        return json.dumps(fixture_data, indent=2)

    def _generate_common_fixtures(self) -> Dict[str, str]:
        """Generate common test data fixtures."""
        return {
            "users.json": json.dumps({
                "valid_user": {
                    "email": "test@example.com",
                    "password": "TestPassword123!",
                    "name": "Test User"
                },
                "invalid_user": {
                    "email": "invalid@example.com",
                    "password": "WrongPassword",
                    "name": "Invalid User"
                },
                "admin_user": {
                    "email": "admin@example.com",
                    "password": "AdminPassword123!",
                    "name": "Admin User",
                    "role": "admin"
                }
            }, indent=2),

            "endpoints.json": json.dumps({
                "login": "/api/auth/login",
                "logout": "/api/auth/logout",
                "profile": "/api/user/profile",
                "tasks": "/api/tasks",
                "task_detail": "/api/tasks/{id}"
            }, indent=2),

            "responses.json": json.dumps({
                "login_success": {
                    "status": 200,
                    "body": {
                        "success": True,
                        "token": "mock-jwt-token",
                        "user": {
                            "id": "123",
                            "email": "test@example.com",
                            "name": "Test User"
                        }
                    }
                },
                "login_error": {
                    "status": 401,
                    "body": {
                        "success": False,
                        "error": "Invalid credentials"
                    }
                },
                "tasks_list": {
                    "status": 200,
                    "body": {
                        "tasks": [
                            {
                                "id": "1",
                                "title": "Test Task 1",
                                "description": "Description for test task 1",
                                "completed": False
                            },
                            {
                                "id": "2",
                                "title": "Test Task 2",
                                "description": "Description for test task 2",
                                "completed": True
                            }
                        ]
                    }
                }
            }, indent=2)
        }

    def _generate_test_utilities(self) -> Dict[str, str]:
        """Generate test utility files."""
        utilities = {}

        # Generate test helpers
        test_helpers = self._generate_test_helpers()
        helpers_path = Path(self.config.utils_directory) / "testHelpers.ts"
        helpers_path.write_text(test_helpers, encoding='utf-8')
        utilities["testHelpers.ts"] = str(helpers_path)

        # Generate API mocking utilities
        if self.config.include_api_mocking:
            api_mocks = self._generate_api_mocks()
            mocks_path = Path(self.config.utils_directory) / "apiMocks.ts"
            mocks_path.write_text(api_mocks, encoding='utf-8')
            utilities["apiMocks.ts"] = str(mocks_path)

        # Generate accessibility testing utilities
        if self.config.include_accessibility_testing:
            accessibility_utils = self._generate_accessibility_utils()
            accessibility_path = Path(self.config.utils_directory) / "accessibility.ts"
            accessibility_path.write_text(accessibility_utils, encoding='utf-8')
            utilities["accessibility.ts"] = str(accessibility_path)

        # Generate visual testing utilities
        if self.config.include_visual_testing:
            visual_utils = self._generate_visual_testing_utils()
            visual_path = Path(self.config.utils_directory) / "visualTesting.ts"
            visual_path.write_text(visual_utils, encoding='utf-8')
            utilities["visualTesting.ts"] = str(visual_path)

        # Generate data generator utilities
        data_generator = self._generate_data_generator()
        generator_path = Path(self.config.utils_directory) / "dataGenerator.ts"
        generator_path.write_text(data_generator, encoding='utf-8')
        utilities["dataGenerator.ts"] = str(generator_path)

        self.processing_stats["utilities_generated"] = len(utilities)
        return utilities

    def _generate_test_helpers(self) -> str:
        """Generate test helper utilities."""
        return '''import { Page, expect } from '@playwright/test';

/**
 * Test helper utilities
 */
export class TestHelpers {
  /**
   * Wait for a specific duration
   */
  static async wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Take screenshot with timestamp
   */
  static async takeScreenshot(page: Page, name: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await page.screenshot({
      path: `test-results/screenshots/${name}-${timestamp}.png`,
      fullPage: True
    });
  }

  /**
   * Check if element exists and is visible
   */
  static async isElementVisible(page: Page, selector: string): Promise<boolean> {
    try {
      await page.waitForSelector(selector, { state: 'visible', timeout: 5000 });
      return True;
    } catch {
      return False;
    }
  }

  /**
   * Wait for API response
   */
  static async waitForApiResponse(page: Page, url: string): Promise<any> {
    return await page.waitForResponse(response =>
      response.url().includes(url) && response.status() === 200
    );
  }

  /**
   * Login helper function
   */
  static async login(page: Page, email: string, password: string): Promise<void> {
    await page.goto('/login');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  }

  /**
   * Logout helper function
   */
  static async logout(page: Page): Promise<void> {
    await page.click('[data-testid="logout-button"]');
    await page.waitForURL('/login');
  }

  /**
   * Generate random test data
   */
  static generateRandomEmail(): string {
    return `test-${Date.now()}@example.com`;
  }

  static generateRandomString(length: number = 10): string {
    return Math.random().toString(36).substring(2, length + 2);
  }

  /**
   * Clear browser storage
   */
  static async clearStorage(page: Page): Promise<void> {
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }

  /**
   * Set viewport size
   */
  static async setViewport(page: Page, width: number, height: number): Promise<void> {
    await page.setViewportSize({ width, height });
  }

  /**
   * Check console errors
   */
  static async checkConsoleErrors(page: Page): Promise<string[]> {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    return errors;
  }
}'''

    def _generate_api_mocks(self) -> str:
        """Generate API mocking utilities."""
        return '''import { Route, Request, Response } from '@playwright/test';

/**
 * API mocking utilities
 */
export class ApiMocks {
  private static mockRoutes = new Map<string, any>();

  /**
   * Mock API route
   */
  static mockRoute(page: any, url: string, response: any, status: number = 200): void {
    page.route(url, (route: Route) => {
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * Mock login API
   */
  static mockLogin(page: any, success: boolean = True): void {
    const response = success ? {
      success: True,
      token: 'mock-jwt-token',
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User'
      }
    } : {
      success: False,
      error: 'Invalid credentials'
    };

    this.mockRoute(page, '**/api/auth/login', response, success ? 200 : 401);
  }

  /**
   * Mock tasks API
   */
  static mockTasks(page: any): void {
    const response = {
      tasks: [
        {
          id: '1',
          title: 'Test Task 1',
          description: 'Description for test task 1',
          completed: False,
          priority: 'high'
        },
        {
          id: '2',
          title: 'Test Task 2',
          description: 'Description for test task 2',
          completed: True,
          priority: 'medium'
        }
      ]
    };

    this.mockRoute(page, '**/api/tasks', response);
  }

  /**
   * Mock user profile API
   */
  static mockUserProfile(page: any): void {
    const response = {
      id: '123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user',
      avatar: 'https://example.com/avatar.jpg'
    };

    this.mockRoute(page, '**/api/user/profile', response);
  }

  /**
   * Mock error responses
   */
  static mockError(page: any, url: string, errorMessage: string, status: number = 500): void {
    const response = {
      success: False,
      error: errorMessage
    };

    this.mockRoute(page, url, response, status);
  }

  /**
   * Mock network offline
   */
  static mockNetworkOffline(page: any): void {
    page.context().setOffline(True);
  }

  /**
   * Mock slow network
   */
  static mockSlowNetwork(page: any, delay: number = 3000): void {
    page.route('**/*', (route: Route) => {
      setTimeout(() => route.continue(), delay);
    });
  }

  /**
   * Intercept and log API calls
   */
  static interceptApiCalls(page: any): any[] {
    const apiCalls: any[] = [];

    page.route('**/api/**', (route: Route, request: Request) => {
      apiCalls.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        postData: request.postData(),
        timestamp: new Date().toISOString()
      });
      route.continue();
    });

    return apiCalls;
  }
}'''

    def _generate_accessibility_utils(self) -> str:
        """Generate accessibility testing utilities."""
        return '''import { Page, expect } from '@playwright/test';

/**
 * Accessibility testing utilities
 */
export class AccessibilityTests {
  /**
   * Run automated accessibility tests
   */
  static async runAccessibilityTests(page: Page): Promise<void> {
    // Check for proper heading structure
    await this.checkHeadingStructure(page);

    // Check for alt text on images
    await this.checkImageAltText(page);

    // Check for form labels
    await this.checkFormLabels(page);

    // Check for ARIA attributes
    await this.checkAriaAttributes(page);

    // Check color contrast (basic check)
    await this.checkColorContrast(page);

    // Check keyboard navigation
    await this.checkKeyboardNavigation(page);
  }

  /**
   * Check heading structure
   */
  private static async checkHeadingStructure(page: Page): Promise<void> {
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
    expect(headings).toBeGreaterThan(0);

    // Check that there's exactly one h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
  }

  /**
   * Check image alt text
   */
  private static async checkImageAltText(page: Page): Promise<void> {
    const images = await page.locator('img').all();

    for (const image of images) {
      const altText = await image.getAttribute('alt');
      const role = await image.getAttribute('role');

      // Skip decorative images
      if (role === 'presentation') continue;

      expect(altText).toBeDefined();
    }
  }

  /**
   * Check form labels
   */
  private static async checkFormLabels(page: Page): Promise<void> {
    const inputs = await page.locator('input, select, textarea').all();

    for (const input of inputs) {
      const type = await input.getAttribute('type');

      // Skip hidden inputs
      if (type === 'hidden') continue;

      const label = await page.locator(`label[for="${await input.getAttribute('id')}"]`).count();
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');

      expect(label + (ariaLabel ? 1 : 0) + (ariaLabelledBy ? 1 : 0) + (placeholder ? 1 : 0)).toBeGreaterThan(0);
    }
  }

  /**
   * Check ARIA attributes
   */
  private static async checkAriaAttributes(page: Page): Promise<void> {
    // Check for proper ARIA roles
    const landmarks = await page.locator('[role], main, nav, header, footer, section, article, aside').count();
    expect(landmarks).toBeGreaterThan(0);

    // Check for ARIA labels on interactive elements
    const buttons = await page.locator('button').all();
    for (const button of buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');

      if (!text || text.trim() === '') {
        expect(ariaLabel).toBeDefined();
      }
    }
  }

  /**
   * Check color contrast (basic check)
   */
  private static async checkColorContrast(page: Page): Promise<void> {
    // This is a basic implementation - a full implementation would use a color contrast library
    const elements = await page.locator('*').all();

    for (const element of elements) {
      const styles = await element.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
          fontSize: computed.fontSize
        };
      });

      // Basic check - ensure text is visible
      if (styles.color && styles.backgroundColor &&
          styles.color !== 'rgba(0, 0, 0, 0)' &&
          styles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
        // More sophisticated contrast checking would go here
        expect(styles.color).not.toBe(styles.backgroundColor);
      }
    }
  }

  /**
   * Check keyboard navigation
   */
  private static async checkKeyboardNavigation(page: Page): Promise<void> {
    // Check focus management
    const focusableElements = await page.locator(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ).all();

    expect(focusableElements.length).toBeGreaterThan(0);

    // Test tab navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.locator(':focus').count();
    expect(focusedElement).toBeGreaterThan(0);
  }

  /**
   * Check screen reader support
   */
  static async checkScreenReaderSupport(page: Page): Promise<void> {
    // Check for ARIA live regions
    const liveRegions = await page.locator('[aria-live]').count();

    // Check for skip links
    const skipLinks = await page.locator('a[href^="#"], [role="navigation"]').count();

    // Check for page title
    const title = await page.title();
    expect(title).not.toBe('');

    // Check for language attribute
    const lang = await page.getAttribute('html', 'lang');
    expect(lang).toBeDefined();
  }

  /**
   * Check focus traps in modals
   */
  static async checkFocusTrap(page: Page, modalSelector: string): Promise<void> {
    // Open modal (implementation depends on specific modal)
    await page.click(modalSelector);

    // Check that focus is trapped within modal
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const focusedElement = await page.locator(':focus').first();
    const modal = await page.locator(modalSelector);

    // Focus should still be within modal
    const isWithinModal = await modal.evaluate((modal, focused) => {
      return modal.contains(focused);
    }, await focusedElement.elementHandle());

    expect(isWithinModal).toBe(True);
  }
}'''

    def _generate_visual_testing_utils(self) -> str:
        """Generate visual testing utilities."""
        return '''import { Page, expect } from '@playwright/test';

/**
 * Visual testing utilities
 */
export class VisualTests {
  /**
   * Take and compare screenshot
   */
  static async compareScreenshot(
    page: Page,
    name: string,
    options: {
      fullPage?: boolean;
      threshold?: number;
      animations?: 'disabled' | 'allow';
    } = {}
  ): Promise<void> {
    const {
      fullPage = True,
      threshold = 0.2,
      animations = 'disabled'
    } = options;

    // Disable animations for consistent screenshots
    if (animations === 'disabled') {
      await page.addStyleTag({
        content: `
          *, *::before, *::after {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
          }
        `
      });
    }

    await expect(page).toHaveScreenshot(name, {
      fullPage,
      threshold,
      animations: animations === 'disabled' ? 'disabled' : 'allow'
    });
  }

  /**
   * Compare element screenshot
   */
  static async compareElementScreenshot(
    page: Page,
    selector: string,
    name: string,
    options: {
      threshold?: number;
      animations?: 'disabled' | 'allow';
    } = {}
  ): Promise<void> {
    const { threshold = 0.2, animations = 'disabled' } = options;
    const element = page.locator(selector);

    if (animations === 'disabled') {
      await page.addStyleTag({
        content: `
          *, *::before, *::after {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
          }
        `
      });
    }

    await expect(element).toHaveScreenshot(name, {
      threshold,
      animations: animations === 'disabled' ? 'disabled' : 'allow'
    });
  }

  /**
   * Test responsive design
   */
  static async testResponsiveDesign(
    page: Page,
    name: string,
    viewports: Array<{ width: number; height: number; name: string }> = [
      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }
    ]
  ): Promise<void> {
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500); // Wait for responsive adjustments

      await this.compareScreenshot(
        page,
        `${name}-${viewport.name}`,
        { fullPage: True }
      );
    }
  }

  /**
   * Test component states
   */
  static async testComponentStates(
    page: Page,
    selector: string,
    name: string,
    states: Array<{
      name: string;
      action: (page: Page, element: any) => Promise<void>;
    }> = []
  ): Promise<void> {
    const element = page.locator(selector);

    for (const state of states) {
      // Reset to default state
      await page.reload();

      // Apply state
      await state.action(page, element);
      await page.waitForTimeout(500);

      // Take screenshot
      await this.compareElementScreenshot(
        page,
        selector,
        `${name}-${state.name}`
      );
    }
  }

  /**
   * Test hover states
   */
  static async testHoverStates(page: Page, selector: string, name: string): Promise<void> {
    await this.testComponentStates(page, selector, name, [
      {
        name: 'default',
        action: async () => {} // No action needed for default state
      },
      {
        name: 'hover',
        action: async (page, element) => {
          await element.hover();
        }
      }
    ]);
  }

  /**
   * Test focus states
   */
  static async testFocusStates(page: Page, selector: string, name: string): Promise<void> {
    await this.testComponentStates(page, selector, name, [
      {
        name: 'focus',
        action: async (page, element) => {
          await element.focus();
        }
      }
    ]);
  }

  /**
   * Test loading states
   */
  static async testLoadingStates(page: Page, selector: string, name: string): Promise<void> {
    await this.testComponentStates(page, selector, name, [
      {
        name: 'loading',
        action: async (page, element) => {
          // Add loading class or attribute
          await element.evaluate((el) => {
            el.classList.add('loading');
            el.setAttribute('data-loading', 'True');
          });
        }
      }
    ]);
  }

  /**
   * Test error states
   */
  static async testErrorStates(page: Page, selector: string, name: string): Promise<void> {
    await this.testComponentStates(page, selector, name, [
      {
        name: 'error',
        action: async (page, element) => {
          // Add error class or attribute
          await element.evaluate((el) => {
            el.classList.add('error');
            el.setAttribute('data-error', 'True');
          });
        }
      }
    ]);
  }

  /**
   * Test disabled states
   */
  static async testDisabledStates(page: Page, selector: string, name: string): Promise<void> {
    await this.testComponentStates(page, selector, name, [
      {
        name: 'disabled',
        action: async (page, element) => {
          await element.evaluate((el) => {
            el.setAttribute('disabled', 'True');
            el.classList.add('disabled');
          });
        }
      }
    ]);
  }

  /**
   * Create visual regression test template
   */
  static createVisualTest(
    testName: string,
    url: string,
    selector?: string,
    options: {
      viewports?: Array<{ width: number; height: number; name: string }>;
      states?: Array<{ name: string; action: string }>;
      threshold?: number;
    } = {}
  ): string {
    const { viewports, states, threshold = 0.2 } = options;

    const viewportCode = viewports
      ? viewports.map(vp => `      { width: ${vp.width}, height: ${vp.height}, name: '${vp.name}' }`).join(',\n')
      : `      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }`;

    const statesCode = states
      ? states.map(state => `      {
        name: '${state.name}',
        action: async (page, element) => {
          ${state.action}
        }
      }`).join(',\n')
      : '';

    return `
import { test, expect } from '@playwright/test';
import { VisualTests } from '../utils/visualTesting';

test('${testName}', async ({ page }) => {
  await page.goto('${url}');

  ${selector ? `const element = page.locator('${selector}');` : ''}

  // Test responsive design
  await VisualTests.testResponsiveDesign(
    page,
    '${testName}',
    [
${viewportCode}
    ]
  );

  ${states ? `
  // Test different states
  await VisualTests.testComponentStates(
    page,
    '${selector}',
    '${testName}',
    [
${statesCode}
    ]
  );
  ` : ''}
});
`;
  }
}'''

    def _generate_data_generator(self) -> str:
        """Generate data generator utilities."""
        return '''import { faker } from '@faker-js/faker';

/**
 * Data generator utilities for testing
 */
export class DataGenerator {
  /**
   * Generate user data
   */
  static generateUser(options: {
    role?: 'user' | 'admin' | 'moderator';
    verified?: boolean;
  } = {}): any {
    const { role = 'user', verified = False } = options;

    return {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      firstName: faker.person.firstName(),
      lastName: faker.person.lastName(),
      name: faker.person.fullName(),
      password: faker.internet.password({ length: 12, memorable: True }),
      phone: faker.phone.number(),
      avatar: faker.image.avatar(),
      role,
      verified,
      createdAt: faker.date.past(),
      updatedAt: faker.date.recent()
    };
  }

  /**
   * Generate task data
   */
  static generateTask(options: {
    completed?: boolean;
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    assignee?: string;
  } = {}): any {
    const { completed = False, priority = 'medium', assignee } = options;

    return {
      id: faker.string.uuid(),
      title: faker.lorem.sentence({ min: 3, max: 8 }),
      description: faker.lorem.paragraph(),
      completed,
      priority,
      assignee: assignee || faker.person.fullName(),
      dueDate: faker.date.future(),
      createdAt: faker.date.past(),
      updatedAt: faker.date.recent(),
      tags: faker.helpers.arrayElements(['work', 'personal', 'urgent', 'meeting', 'review'], { min: 1, max: 3 })
    };
  }

  /**
   * Generate form data
   */
  static generateFormData(fields: Array<{ name: string; type: string; required?: boolean }>): any {
    const formData: any = {};

    for (const field of fields) {
      switch (field.type) {
        case 'email':
          formData[field.name] = faker.internet.email();
          break;
        case 'password':
          formData[field.name] = faker.internet.password({ length: 12 });
          break;
        case 'text':
          formData[field.name] = faker.lorem.words({ min: 1, max: 3 });
          break;
        case 'textarea':
          formData[field.name] = faker.lorem.paragraph();
          break;
        case 'number':
          formData[field.name] = faker.number.int({ min: 1, max: 100 });
          break;
        case 'tel':
          formData[field.name] = faker.phone.number();
          break;
        case 'date':
          formData[field.name] = faker.date.future().toISOString().split('T')[0];
          break;
        case 'select':
          formData[field.name] = faker.helpers.arrayElement(['option1', 'option2', 'option3']);
          break;
        case 'checkbox':
          formData[field.name] = faker.datatype.boolean();
          break;
        default:
          formData[field.name] = faker.lorem.words({ min: 1, max: 2 });
      }

      // Handle required fields
      if (field.required && !formData[field.name]) {
        formData[field.name] = faker.lorem.words(1);
      }
    }

    return formData;
  }

  /**
   * Generate invalid data for negative testing
   */
  static generateInvalidData(originalData: any): any {
    const invalidData = { ...originalData };

    // Find a field to invalidate
    const fields = Object.keys(invalidData);
    if (fields.length === 0) return invalidData;

    const fieldToInvalidate = faker.helpers.arrayElement(fields);
    const fieldValue = invalidData[fieldToInvalidate];

    // Generate invalid value based on field type
    if (typeof fieldValue === 'string') {
      if (fieldToInvalidate.toLowerCase().includes('email')) {
        invalidData[fieldToInvalidate] = 'invalid-email';
      } else {
        invalidData[fieldToInvalidate] = '';
      }
    } else if (typeof fieldValue === 'number') {
      invalidData[fieldToInvalidate] = -1;
    } else if (typeof fieldValue === 'boolean') {
      invalidData[fieldToInvalidate] = null;
    }

    return invalidData;
  }

  /**
   * Generate API response data
   */
  static generateApiResponse(success: boolean = True, data?: any): any {
    return {
      success,
      data: data || null,
      error: success ? null : faker.lorem.sentence(),
      timestamp: faker.date.recent().toISOString()
    };
  }

  /**
   * Generate error responses
   */
  static generateErrorResponses(): any {
    return {
      validationError: {
        success: False,
        error: 'Validation failed',
        details: [
          { field: 'email', message: 'Invalid email format' },
          { field: 'password', message: 'Password too short' }
        ]
      },
      authenticationError: {
        success: False,
        error: 'Authentication failed',
        code: 'AUTH_FAILED'
      },
      authorizationError: {
        success: False,
        error: 'Access denied',
        code: 'ACCESS_DENIED'
      },
      notFoundError: {
        success: False,
        error: 'Resource not found',
        code: 'NOT_FOUND'
      },
      serverError: {
        success: False,
        error: 'Internal server error',
        code: 'SERVER_ERROR'
      }
    };
  }

  /**
   * Generate pagination data
   */
  static generatePaginationData<T>(
    dataGenerator: () => T,
    page: number = 1,
    limit: number = 10,
    total?: number
  ): any {
    const totalItems = total || faker.number.int({ min: 50, max: 200 });
    const totalPages = Math.ceil(totalItems / limit);
    const items = Array.from({ length: Math.min(limit, totalItems - (page - 1) * limit) }, dataGenerator);

    return {
      items,
      pagination: {
        page,
        limit,
        total: totalItems,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    };
  }

  /**
   * Generate search results
   */
  static generateSearchResults(query: string, resultsGenerator: () => any): any {
    const total = faker.number.int({ min: 0, max: 100 });
    const results = total > 0 ? Array.from({ length: Math.min(total, 20) }, resultsGenerator) : [];

    return {
      query,
      results,
      total,
      took: faker.number.int({ min: 10, max: 500 })
    };
  }

  /**
   * Generate file data
   */
  static generateFileData(type: 'image' | 'document' | 'video' | 'audio' = 'image'): any {
    const extensions = {
      image: ['jpg', 'png', 'gif', 'webp'],
      document: ['pdf', 'doc', 'docx', 'txt'],
      video: ['mp4', 'avi', 'mov'],
      audio: ['mp3', 'wav', 'ogg']
    };

    const extension = faker.helpers.arrayElement(extensions[type]);
    const filename = faker.system.fileName({ extensionCount: 1, extension: extension });

    return {
      name: filename,
      type: `${type}/${extension}`,
      size: faker.number.int({ min: 1000, max: 10000000 }),
      lastModified: faker.date.past()
    };
  }
}'''

    def _generate_scenario_tests(self, scenario: TestScenario) -> Dict[str, str]:
        """Generate test files for a specific scenario."""
        test_files = {}

        # Generate main test file
        main_test = self._generate_main_test_file(scenario)
        test_path = Path(self.config.tests_directory) / f"{scenario.id}.spec.ts"
        test_path.write_text(main_test, encoding='utf-8')
        test_files[f"{scenario.id}.spec.ts"] = str(test_path)
        self.processing_stats["tests_generated"] += 1

        # Generate visual tests if enabled
        if self.config.include_visual_testing:
            visual_test = self._generate_visual_test_file(scenario)
            visual_test_path = Path(self.config.tests_directory) / f"{scenario.id}-visual.spec.ts"
            visual_test_path.write_text(visual_test, encoding='utf-8')
            test_files[f"{scenario.id}-visual.spec.ts"] = str(visual_test_path)
            self.processing_stats["visual_tests_generated"] += 1

        # Generate accessibility tests if enabled
        if self.config.include_accessibility_testing:
            accessibility_test = self._generate_accessibility_test_file(scenario)
            accessibility_test_path = Path(self.config.tests_directory) / f"{scenario.id}-accessibility.spec.ts"
            accessibility_test_path.write_text(accessibility_test, encoding='utf-8')
            test_files[f"{scenario.id}-accessibility.spec.ts"] = str(accessibility_test_path)
            self.processing_stats["accessibility_tests_generated"] += 1

        # Generate mobile tests if enabled
        if self.config.include_mobile_testing:
            mobile_test = self._generate_mobile_test_file(scenario)
            mobile_test_path = Path(self.config.tests_directory) / f"{scenario.id}-mobile.spec.ts"
            mobile_test_path.write_text(mobile_test, encoding='utf-8')
            test_files[f"{scenario.id}-mobile.spec.ts"] = str(mobile_test_path)
            self.processing_stats["mobile_tests_generated"] += 1

        # Update category and priority stats
        category = scenario.category or 'custom'
        priority = scenario.priority or 'medium'

        if category not in self.processing_stats["tests_by_category"]:
            self.processing_stats["tests_by_category"][category] = 0
        self.processing_stats["tests_by_category"][category] += 1

        if priority not in self.processing_stats["tests_by_priority"]:
            self.processing_stats["tests_by_priority"][priority] = 0
        self.processing_stats["tests_by_priority"][priority] += 1

        return test_files

    def _generate_main_test_file(self, scenario: TestScenario) -> str:
        """Generate main test file for scenario."""
        test_imports = [
            "import { test, expect } from '@playwright/test';"
        ]

        if self.config.use_page_object_model:
            test_imports.extend([
                "import { TestHelpers } from '../utils/testHelpers';",
                "import { ApiMocks } from '../utils/apiMocks';"
            ])

        test_description = scenario.description or scenario.name
        test_tags = scenario.tags or []

        # Generate test steps
        test_steps = []
        for step in scenario.steps:
            step_code = self._generate_test_step(step)
            test_steps.append(step_code)

        test_content = f'''{chr(10).join(test_imports)}

/**
 * Test suite for: {scenario.name}
 * Description: {test_description}
 * Category: {scenario.category}
 * Priority: {scenario.priority}
 * Generated on: {datetime.now().isoformat()}
 */

{self._generate_test_describe(scenario, test_steps)}

}}'''

        return test_content

    def _generate_test_describe(self, scenario: TestScenario, test_steps: List[str]) -> str:
        """Generate test describe block."""
        tags_str = ", ".join([f"'{tag}'" for tag in scenario.tags]) if scenario.tags else ""

        return f'''test.describe('{scenario.name}', {{ tag: [{tags_str}] }}, () => {{
  test.beforeEach(async ({{ page }}) => {{
    // Setup before each test
    await TestHelpers.clearStorage(page);

    // Mock API calls if enabled
    {self._generate_api_mocks_for_scenario(scenario)}
  }});

  test('should complete {scenario.name.lower()}', async ({{ page }}) => {{
{chr(10).join(test_steps)}
  }});

  // Generate negative test scenarios if enabled
  {self._generate_negative_tests(scenario)}
}});'''

    def _generate_api_mocks_for_scenario(self, scenario: TestScenario) -> str:
        """Generate API mocking code for scenario."""
        if not self.config.include_api_mocking:
          return "// API mocking disabled"

        mocks = []

        # Add common mocks based on scenario category
        if scenario.category == 'authentication':
            mocks.extend([
                "// Mock authentication APIs",
                "ApiMocks.mockLogin(page, True);",
                "ApiMocks.mockUserProfile(page);"
            ])
        elif scenario.category == 'form_interaction':
            mocks.extend([
                "// Mock form submission APIs",
                "ApiMocks.mockLogin(page, True);"
            ])
        elif scenario.category == 'data_display':
            mocks.extend([
                "// Mock data APIs",
                "ApiMocks.mockTasks(page);"
            ])
        else:
            mocks.extend([
                "// Mock common APIs",
                "ApiMocks.mockUserProfile(page);"
            ])

        return chr(10).join(f"    {mock}" for mock in mocks)

    def _generate_test_step(self, step: TestStep) -> str:
        """Generate test step code."""
        step_code = []

        # Add preconditions
        if step.preconditions:
            step_code.append(f"    // Preconditions: {', '.join(step.preconditions)}")

        # Add step description
        step_code.append(f"    // Step {step.step_number}: {step.description}")

        # Generate actions
        for action in step.actions:
            action_code = self._generate_test_action(action)
            step_code.append(f"    {action_code}")

        # Generate validations
        for validation in step.validations:
            validation_code = self._generate_test_action(validation)
            step_code.append(f"    {validation_code}")

        # Add postconditions
        if step.postconditions:
            step_code.append(f"    // Postconditions: {', '.join(step.postconditions)}")

        return chr(10).join(step_code)

    def _generate_test_action(self, action: TestAction) -> str:
        """Generate test action code."""
        action_type = action.action_type
        target = action.target
        parameters = action.parameters
        description = action.description

        if action_type == "navigate":
            if target.get("type") == "url":
                url = target.get("selector", "/")
                return f"await page.goto('{url}');"
            else:
                return f"// Navigate action: {description}"

        elif action_type == "click":
            selector = target.get("selector", "button")
            timeout = parameters.get("timeout", 5000)
            return f"""await page.waitForSelector('{selector}', {{ state: 'visible', timeout: {timeout} }});
    await page.click('{selector}');"""

        elif action_type == "type":
            selector = target.get("selector", "input")
            value = parameters.get("value", "test value")
            return f"""await page.waitForSelector('{selector}');
    await page.fill('{selector}', '{value}');"""

        elif action_type == "wait":
            duration = parameters.get("duration", 1000)
            return f"await page.waitForTimeout({duration});"

        elif action_type == "assert":
            selector = target.get("selector", "*")
            assertion_type = parameters.get("assertion", "visible")

            if assertion_type == "visible":
                return f"await expect(page.locator('{selector}')).toBeVisible();"
            elif assertion_type == "hidden":
                return f"await expect(page.locator('{selector}')).toBeHidden();"
            elif assertion_type == "text":
                expected_text = parameters.get("text", "")
                return f"await expect(page.locator('{selector}')).toContainText('{expected_text}');"
            else:
                return f"// Assertion: {description}"

        elif action_type == "scroll":
            selector = target.get("selector", "body")
            return f"await page.locator('{selector}').scrollIntoViewIfNeeded();"

        elif action_type == "select":
            selector = target.get("selector", "select")
            value = parameters.get("value", "")
            return f"await page.selectOption('{selector}', '{value}');"

        else:
            return f"// Unsupported action type: {action_type} - {description}"

    def _generate_negative_tests(self, scenario: TestScenario) -> str:
        """Generate negative test scenarios."""
        if not self.config.generate_error_scenarios:
            return "// Error scenario generation disabled"

        negative_tests = []

        # Generate common negative scenarios based on category
        if scenario.category == 'authentication':
            negative_tests.extend([
                '''
  test('should show error with invalid credentials', async ({ page }) => {
    // Mock failed login
    ApiMocks.mockLogin(page, False);

    await page.goto('/login');
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');

    // Verify still on login page
    await expect(page).toHaveURL('/login');
  });'''
            ])

        elif scenario.category == 'form_interaction':
            negative_tests.extend([
                '''
  test('should validate required fields', async ({ page }) => {
    await page.goto('/form');

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // Verify validation errors
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('input:invalid')).toHaveCount(1);
  });'''
            ])

        return chr(10).join(negative_tests)

    def _generate_visual_test_file(self, scenario: TestScenario) -> str:
        """Generate visual regression test file."""
        return f'''import {{ test, expect }} from '@playwright/test';
import {{ VisualTests }} from '../utils/visualTesting';

/**
 * Visual regression tests for: {scenario.name}
 * Generated on: {datetime.now().isoformat()}
 */

test.describe('Visual Tests - {scenario.name}', () => {{
  test('should match screenshots across viewports', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Test responsive design
    await VisualTests.testResponsiveDesign(
      page,
      '{scenario.id}',
      [
        {{ width: 375, height: 667, name: 'mobile' }},
        {{ width: 768, height: 1024, name: 'tablet' }},
        {{ width: 1920, height: 1080, name: 'desktop' }}
      ]
    );
  }});

  test('should match component screenshots', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Test key components
    await VisualTests.compareElementScreenshot(
      page,
      'header',
      '{scenario.id}-header'
    );

    await VisualTests.compareElementScreenshot(
      page,
      'main',
      '{scenario.id}-content'
    );
  }});
}});'''

    def _generate_accessibility_test_file(self, scenario: TestScenario) -> str:
        """Generate accessibility test file."""
        return f'''import {{ test, expect }} from '@playwright/test';
import {{ AccessibilityTests }} from '../utils/accessibility';

/**
 * Accessibility tests for: {scenario.name}
 * Generated on: {datetime.now().isoformat()}
 */

test.describe('Accessibility Tests - {scenario.name}', () => {{
  test('should meet accessibility standards', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Run comprehensive accessibility tests
    await AccessibilityTests.runAccessibilityTests(page);
  }});

  test('should support screen readers', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Check screen reader support
    await AccessibilityTests.checkScreenReaderSupport(page);
  }});

  test('should support keyboard navigation', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();

    // Test tab through all interactive elements
    const interactiveElements = await page.locator(
      'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
    ).all();

    for (let i = 0; i < interactiveElements.length; i++) {{
      await page.keyboard.press('Tab');
      const focusedElement = await page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    }}
  }});

  test('should have proper color contrast', async ({{ page }}) => {{
    await page.goto('/{scenario.id}');

    // Check color contrast (basic implementation)
    const elements = await page.locator('*').all();

    for (const element of elements.slice(0, 10)) {{ // Limit to avoid too many checks
      const styles = await element.evaluate((el) => {{
        const computed = window.getComputedStyle(el);
        return {{
          color: computed.color,
          backgroundColor: computed.backgroundColor
        }};
      }});

      // Basic contrast check
      if (styles.color && styles.backgroundColor) {{
        expect(styles.color).not.toBe(styles.backgroundColor);
      }}
    }}
  }});
}});'''

    def _generate_mobile_test_file(self, scenario: TestScenario) -> str:
        """Generate mobile-specific test file."""
        return f'''import {{ test, devices }} from '@playwright/test';
import {{ TestHelpers }} from '../utils/testHelpers';

/**
 * Mobile tests for: {scenario.name}
 * Generated on: {datetime.now().isoformat()}
 */

test.describe('Mobile Tests - {scenario.name}', () => {{
  test('should work on mobile devices', async ({{ page }}) => {{
    // Use mobile device viewport
    await page.setViewportSize({{ width: 375, height: 667 }});

    await page.goto('/{scenario.id}');

    // Test mobile-specific interactions
    await TestHelpers.wait(1000);

    // Test touch interactions
    const buttons = await page.locator('button').all();
    for (const button of buttons.slice(0, 3)) {{
      await button.tap();
      await TestHelpers.wait(500);
    }}

    // Test swipe gestures if applicable
    await page.mouse.wheel(0, 300);
    await TestHelpers.wait(500);
  }});

  test('should work on tablets', async ({{ page }}) => {{
    // Use tablet device viewport
    await page.setViewportSize({{ width: 768, height: 1024 }});

    await page.goto('/{scenario.id}');

    // Test tablet-specific layout
    await expect(page.locator('body')).toBeVisible();

    // Test orientation changes
    await page.setViewportSize({{ width: 1024, height: 768 }});
    await TestHelpers.wait(1000);

    await expect(page.locator('body')).toBeVisible();
  }});

  // Test on specific devices using Playwright device descriptors
  ['iPhone 12', 'Pixel 5'].forEach(deviceName => {{
    test(`should work on ${{deviceName}}`, async ({{ browserName }}) => {{
      const context = await browser.newContext(devices[deviceName]);
      const page = await context.newPage();

      await page.goto('/{scenario.id}');

      // Device-specific tests
      await expect(page.locator('body')).toBeVisible();

      await context.close();
    }});
  }});
}});'''

    def _generate_test_runner(self) -> Dict[str, str]:
        """Generate test runner and configuration files."""
        runner_files = {}

        # Generate package.json scripts
        package_scripts = self._generate_package_scripts()
        scripts_path = Path(self.config.output_directory) / "package-scripts.json"
        scripts_path.write_text(package_scripts, encoding='utf-8')
        runner_files["package-scripts.json"] = str(scripts_path)

        # Generate GitHub Actions workflow
        github_workflow = self._generate_github_workflow()
        workflow_path = Path(self.config.output_directory) / ".github" / "workflows" / "tests.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_path.write_text(github_workflow, encoding='utf-8')
        runner_files[".github/workflows/tests.yml"] = str(workflow_path)

        # Generate test report configuration
        report_config = self._generate_report_config()
        report_config_path = Path(self.config.output_directory) / "report-config.json"
        report_config_path.write_text(report_config, encoding='utf-8')
        runner_files["report-config.json"] = str(report_config_path)

        return runner_files

    def _generate_package_scripts(self) -> str:
        """Generate npm scripts for testing."""
        return json.dumps({
            "scripts": {
                "test": "playwright test",
                "test:headed": "playwright test --headed",
                "test:debug": "playwright test --debug",
                "test:ui": "playwright test --ui",
                "test:report": "playwright show-report",
                "test:visual": "playwright test --grep=Visual",
                "test:accessibility": "playwright test --grep=Accessibility",
                "test:mobile": "playwright test --grep=Mobile",
                "test:update": "playwright test --update-snapshots",
                "test:install": "playwright install",
                "test:codegen": "playwright codegen"
            }
        }, indent=2)

    def _generate_github_workflow(self) -> str:
        """Generate GitHub Actions workflow for testing."""
        return '''name: Playwright Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright Browsers
      run: npx playwright install --with-deps

    - name: Run Playwright tests
      run: npx playwright test

    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30

    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: test-results
        path: test-results/
        retention-days: 30

  test-matrix:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      matrix:
        project: [chromium, firefox, webkit]
        shard: [1, 2, 3, 4]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright Browsers
      run: npx playwright install --with-deps

    - name: Run Playwright tests
      run: npx playwright test --project=${{ matrix.project }} --shard=${{ matrix.shard }}/${{ strategy.job-total }}

    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report-${{ matrix.project }}-${{ matrix.shard }}
        path: playwright-report/
        retention-days: 30'''

    def _generate_report_config(self) -> str:
        """Generate test report configuration."""
        return json.dumps({
            "reporter": [
                ["html"],
                ["json", {"outputFile": "test-results/results.json"}],
                ["junit", {"outputFile": "test-results/results.xml"}],
                ["line"]
            ],
            "report_config": {
                "output_folder": "playwright-report",
                "open_browser": "never",
                "host": "localhost",
                "port": 9323
            },
            "screenshots": {
                "mode": "only-on-failure",
                "path": "test-results/screenshots",
                "full_page": True
            },
            "videos": {
                "mode": "retain-on-failure",
                "path": "test-results/videos"
            },
            "traces": {
                "mode": "retain-on-failure",
                "path": "test-results/traces"
            }
        }, indent=2)

    def _update_processing_stats(self) -> None:
        """Update processing statistics."""
        if self.test_suite:
            # Calculate estimated test duration
            total_duration = 0
            for scenario in self.test_suite.scenarios:
                if scenario.estimated_duration:
                    total_duration += scenario.estimated_duration
                else:
                    # Default estimate based on step count
                    step_count = len(scenario.steps)
                    total_duration += step_count * 10  # 10 seconds per step

            self.processing_stats["estimated_test_duration"] = total_duration

    def save_generated_files(self, generated_files: Dict[str, str]) -> None:
        """Save metadata about generated files."""
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "config": self.config.__dict__,
            "processing_stats": self.processing_stats,
            "generated_files": generated_files,
            "test_suite_info": {
                "name": self.test_suite.name if self.test_suite else None,
                "description": self.test_suite.description if self.test_suite else None,
                "scenario_count": len(self.test_suite.scenarios) if self.test_suite else 0,
                "categories": list(self.processing_stats["tests_by_category"].keys()),
                "priorities": list(self.processing_stats["tests_by_priority"].keys())
            }
        }

        metadata_path = Path(self.config.output_directory) / "test-generation-metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding='utf-8')
        logger.info(f"Saved generation metadata to: {metadata_path}")

    def generate_metadata(self) -> Dict[str, Any]:
        """Generate comprehensive metadata about the test generation."""
        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "config": self.config.__dict__,
            "processing_stats": self.processing_stats,
            "test_suite_summary": {
                "total_scenarios": len(self.test_suite.scenarios) if self.test_suite else 0,
                "categories": self.processing_stats["tests_by_category"],
                "priorities": self.processing_stats["tests_by_priority"],
                "estimated_duration": self.processing_stats["estimated_test_duration"]
            }
        }


def main():
    """Main entry point for test generator."""
    parser = argparse.ArgumentParser(
        description="Generate Playwright test suites from test scenarios and page implementations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests with default settings
  python3 main.py --scenarios examples/sample-test-scenarios/ --output ./output/

  # Generate tests with custom configuration
  python3 main.py --scenarios examples/sample-test-scenarios/ --screens examples/sample-screen-specs/ --catalog examples/sample-component-catalog.json --output ./output/ --framework playwright --include-visual --include-accessibility

  # Dry run to preview generation
  python3 main.py --scenarios examples/sample-test-scenarios/ --output ./output/ --dry-run --verbose
        """
    )

    # Input arguments
    parser.add_argument(
        "--scenarios",
        required=True,
        help="Path to test scenarios directory (markdown or JSON files)"
    )
    parser.add_argument(
        "--screens",
        help="Path to screen specifications directory"
    )
    parser.add_argument(
        "--catalog",
        help="Path to component catalog JSON file"
    )

    # Output arguments
    parser.add_argument(
        "--output",
        default="./output/",
        help="Output directory for generated tests (default: ./output/)"
    )

    # Framework and type arguments
    parser.add_argument(
        "--framework",
        choices=["playwright", "cypress", "selenium"],
        default="playwright",
        help="Test framework to use (default: playwright)"
    )
    parser.add_argument(
        "--typescript",
        action="store_True",
        default=True,
        help="Generate TypeScript tests (default: True)"
    )
    parser.add_argument(
        "--javascript",
        action="store_True",
        help="Generate JavaScript tests instead of TypeScript"
    )

    # Feature arguments
    parser.add_argument(
        "--include-visual",
        action="store_True",
        default=True,
        help="Include visual regression tests (default: True)"
    )
    parser.add_argument(
        "--exclude-visual",
        action="store_True",
        help="Exclude visual regression tests"
    )
    parser.add_argument(
        "--include-accessibility",
        action="store_True",
        default=True,
        help="Include accessibility tests (default: True)"
    )
    parser.add_argument(
        "--exclude-accessibility",
        action="store_True",
        help="Exclude accessibility tests"
    )
    parser.add_argument(
        "--include-mobile",
        action="store_True",
        default=True,
        help="Include mobile device tests (default: True)"
    )
    parser.add_argument(
        "--exclude-mobile",
        action="store_True",
        help="Exclude mobile device tests"
    )
    parser.add_argument(
        "--include-performance",
        action="store_True",
        help="Include performance tests"
    )
    parser.add_argument(
        "--include-api-mocks",
        action="store_True",
        default=True,
        help="Include API mocking utilities (default: True)"
    )
    parser.add_argument(
        "--exclude-api-mocks",
        action="store_True",
        help="Exclude API mocking utilities"
    )

    # Architecture arguments
    parser.add_argument(
        "--page-object-model",
        action="store_True",
        default=True,
        help="Use Page Object Model (default: True)"
    )
    parser.add_argument(
        "--no-page-object-model",
        action="store_True",
        help="Don't use Page Object Model"
    )
    parser.add_argument(
        "--data-driven",
        action="store_True",
        default=True,
        help="Generate data-driven tests (default: True)"
    )
    parser.add_argument(
        "--no-data-driven",
        action="store_True",
        help="Don't generate data-driven tests"
    )

    # Test execution arguments
    parser.add_argument(
        "--parallel",
        action="store_True",
        default=True,
        help="Enable parallel test execution (default: True)"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_True",
        help="Disable parallel test execution"
    )
    parser.add_argument(
        "--retry",
        type=int,
        default=2,
        help="Number of retry attempts for failed tests (default: 2)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Test timeout in milliseconds (default: 30000)"
    )

    # Configuration arguments
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:3000",
        help="Base URL for tests (default: http://localhost:3000)"
    )
    parser.add_argument(
        "--environment",
        default="test",
        help="Test environment (default: test)"
    )

    # Browser and device arguments
    parser.add_argument(
        "--browsers",
        nargs="+",
        choices=["chromium", "firefox", "webkit", "chrome", "edge"],
        default=["chromium", "firefox", "webkit"],
        help="Browsers to test against (default: chromium firefox webkit)"
    )
    parser.add_argument(
        "--devices",
        nargs="+",
        choices=["mobile", "tablet", "desktop"],
        default=["desktop", "mobile", "tablet"],
        help="Device types to test (default: desktop mobile tablet)"
    )

    # Other arguments
    parser.add_argument(
        "--dry-run",
        action="store_True",
        help="Preview what would be generated without creating files"
    )
    parser.add_argument(
        "--verbose",
        action="store_True",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Test Generator v1.0.0"
    )

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create configuration
        config = TestGenerationConfig(
            framework=TestFramework(args.framework),
            output_directory=args.output,
            tests_directory=f"{args.output}/tests/",
            fixtures_directory=f"{args.output}/tests/fixtures/",
            utils_directory=f"{args.output}/tests/utils/",
            pages_directory=f"{args.output}/tests/pages/",
            reports_directory=f"{args.output}/test-results/",
            include_visual_testing=args.include_visual and not args.exclude_visual,
            include_accessibility_testing=args.include_accessibility and not args.exclude_accessibility,
            include_mobile_testing=args.include_mobile and not args.exclude_mobile,
            include_performance_testing=args.include_performance,
            include_api_mocking=args.include_api_mocks and not args.exclude_api_mocks,
            use_typescript=args.typescript and not args.javascript,
            use_page_object_model=args.page_object_model and not args.no_page_object_model,
            generate_data_driven_tests=args.data_driven and not args.no_data_driven,
            parallel_execution=args.parallel and not args.no_parallel,
            retry_failed_tests=args.retry,
            timeout=args.timeout,
            base_url=args.base_url,
            test_environment=args.environment,
            browsers=[BrowserType(browser) for browser in args.browsers],
            devices=[DeviceType(device) for device in args.devices]
        )

        # Override with config file if provided
        if args.config:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

        # Initialize generator
        generator = TestGenerator(config)

        # Load inputs
        logger.info("Loading test scenarios...")
        generator.load_test_scenarios(args.scenarios)

        if args.screens:
            logger.info("Loading screen specifications...")
            generator.load_screen_specifications(args.screens)

        if args.catalog:
            logger.info("Loading component catalog...")
            generator.load_component_catalog(args.catalog)

        # Generate tests
        if args.dry_run:
            logger.info("DRY RUN: Would generate the following:")
            logger.info(f"- {len(generator.test_suite.scenarios) if generator.test_suite else 0} test scenarios")
            logger.info(f"- Playwright configuration")
            logger.info(f"- TypeScript configuration")
            logger.info(f"- Page Object Models")
            logger.info(f"- Test data fixtures")
            logger.info(f"- Test utilities")
            logger.info(f"- Visual regression tests")
            logger.info(f"- Accessibility tests")
            logger.info(f"- Mobile device tests")
            logger.info("Use --no-dry-run to actually generate files.")
            return

        generated_files = generator.generate_tests()
        generator.save_generated_files(generated_files)

        # Generate and display metadata
        metadata = generator.generate_metadata()
        logger.info("Test generation completed successfully!")
        logger.info(f"Generated {len(generated_files)} files in {args.output}")
        logger.info(f"Processed {metadata['processing_stats']['scenarios_processed']} test scenarios")
        logger.info(f"Generated {metadata['processing_stats']['tests_generated']} test files")
        logger.info(f"Estimated test duration: {metadata['processing_stats']['estimated_test_duration']} seconds")

    except Exception as e:
        logger.error(f"Error during test generation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
