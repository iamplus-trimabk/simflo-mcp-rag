#!/usr/bin/env python3
"""
Page Generator - Step 5 of SimFlo Figma-to-RAG Pipeline

Generates complete React pages from screen specifications, component catalogs,
and interaction flows. Supports React Router, state management, custom hooks,
error boundaries, responsive design, and comprehensive TypeScript support.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import re

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
        ScreenSpecification, ScreenSet, ComponentCatalog, ComponentDefinition,
        ComponentInstance, NavigationRelationship, LayoutGrid, ResponsiveBreakpoint
    )
except ImportError as e:
    logger.warning(f"Could not import from common module: {e}")
    # Define fallback schemas for testing
    from pydantic import BaseModel

    class ComponentInstance(BaseModel):
        id: str
        componentId: str
        name: str
        x: float = 0.0
        y: float = 0.0
        width: float = 100.0
        height: float = 50.0
        properties: Dict[str, Any] = {}
        variant: Dict[str, Any] = {}

    class LayoutGrid(BaseModel):
        type: str = "columns"
        columns: int = 12
        gutter_width: float = 16.0
        margin: float = 24.0
        max_width: float = 1200.0

    class ResponsiveBreakpoint(BaseModel):
        name: str = "md"
        value: int = 768

    class NavigationRelationship(BaseModel):
        source_screen_id: str
        target_screen_id: str
        trigger_element_id: str
        action_type: str = "navigate"

    class ComponentDefinition(BaseModel):
        id: str
        name: str
        category: str
        description: str
        variants: List[Dict[str, Any]] = []
        default_properties: Dict[str, Any] = {}

    class ComponentCatalog(BaseModel):
        components: Dict[str, ComponentDefinition] = {}
        design_tokens: Dict[str, Any] = {}

    class ScreenSpecification(BaseModel):
        screenId: str
        name: str
        description: str = ""
        width: float = 375.0
        height: float = 812.0
        componentInstances: List[ComponentInstance] = []
        layout_grid: LayoutGrid = LayoutGrid()
        responsive_breakpoints: List[ResponsiveBreakpoint] = []
        navigation: List[NavigationRelationship] = []
        backgroundColor: str = "#ffffff"
        backgroundImage: Dict[str, Any] = {}

    class ScreenSet(BaseModel):
        screens: Dict[str, ScreenSpecification] = {}
        navigation_flows: List[NavigationRelationship] = []

    class CustomValidationError(Exception):
        pass

    def validate_and_load(data: Any, schema_class):
        if isinstance(data, dict):
            return schema_class(**data)
        return data


class PageType(Enum):
    """Supported page types."""
    REACT_PAGE = "react_page"
    REACT_LAYOUT = "react_layout"
    REACT_MODAL = "react_modal"
    REACT_FORM = "react_form"


class RoutingLibrary(Enum):
    """Supported routing libraries."""
    REACT_ROUTER = "react_router"
    NEXT_ROUTER = "next_router"
    REACH_ROUTER = "reach_router"


class StateManagement(Enum):
    """Supported state management solutions."""
    REACT_CONTEXT = "react_context"
    REDUX = "redux"
    ZUSTAND = "zustand"
    CUSTOM_HOOKS = "custom_hooks"


@dataclass
class PageGenerationConfig:
    """Configuration for page generation."""
    page_type: PageType = PageType.REACT_PAGE
    routing_library: RoutingLibrary = RoutingLibrary.REACT_ROUTER
    state_management: StateManagement = StateManagement.REACT_CONTEXT
    include_typescript: bool = True
    include_responsive: bool = True
    include_error_boundaries: bool = True
    include_loading_states: bool = True
    include_accessibility: bool = True
    output_directory: str = "./output/"
    pages_directory: str = "./output/pages/"
    hooks_directory: str = "./output/hooks/"
    contexts_directory: str = "./output/contexts/"
    routes_directory: str = "./output/routes/"
    component_import_path: str = "@/components"
    utils_import_path: str = "@/utils"
    indent_size: int = 2
    use_strict_mode: bool = True


class PageGenerator:
    """
    Main page generator class.

    Generates complete React pages from screen specifications with support for:
    - Screen layout and component composition
    - React Router integration and navigation
    - State management with Context API and custom hooks
    - Error boundaries and loading states
    - Responsive design and accessibility
    - Form handling and validation
    - Data fetching hooks
    - TypeScript interfaces and type safety
    """

    def __init__(self, config: Optional[PageGenerationConfig] = None):
        """Initialize page generator with configuration."""
        self.config = config or PageGenerationConfig()
        self.screen_set: Optional[ScreenSet] = None
        self.component_catalog: Optional[ComponentCatalog] = None
        self.processing_stats = {
            "screens_processed": 0,
            "pages_generated": 0,
            "hooks_generated": 0,
            "contexts_generated": 0,
            "routes_generated": 0,
            "error_boundaries_generated": 0,
            "total_files_created": 0,
            "navigation_flows_processed": 0,
            "component_instances_processed": 0,
            "forms_processed": 0,
            "responsive_layouts": 0
        }

    def load_screen_specifications(self, screens_path: str) -> None:
        """
        Load and validate screen specifications from directory or file.

        Args:
            screens_path: Path to screen specifications directory or JSON file

        Raises:
            CustomValidationError: If screens are invalid
        """
        logger.info(f"Loading screen specifications from: {screens_path}")

        screens_dir = Path(screens_path)

        if screens_dir.is_file():
            # Load single file
            try:
                with open(screens_dir, 'r') as f:
                    data = json.load(f)

                if 'screens' in data:
                    # Load as ScreenSet
                    self.screen_set = validate_and_load(screens_dir, ScreenSet)
                else:
                    # Load as single ScreenSpecification
                    screen = validate_and_load(screens_dir, ScreenSpecification)
                    self.screen_set = ScreenSet(screens=[screen])

                logger.info(f"Loaded {len(self.screen_set.screens)} screens from file")

            except FileNotFoundError:
                raise CustomValidationError(f"Screen specifications file not found: {screens_path}")
            except json.JSONDecodeError as e:
                raise CustomValidationError(f"Invalid JSON in screen specifications: {e}")

        elif screens_dir.is_dir():
            # Load all JSON files in directory
            screens = []
            for json_file in screens_dir.glob("*.json"):
                try:
                    screen = validate_and_load(json_file, ScreenSpecification)
                    screens.append(screen)
                    logger.debug(f"Loaded screen: {screen.name}")
                except Exception as e:
                    logger.warning(f"Error loading screen file {json_file}: {e}")

            if not screens:
                raise CustomValidationError(
                    f"No valid screen specifications found in: {screens_path}")

            self.screen_set = ScreenSet(screens=screens)
            logger.info(f"Loaded {len(screens)} screens from directory")

        else:
            raise CustomValidationError(f"Screen specifications path not found: {screens_path}")

        # Update processing stats
        self.processing_stats["screens_processed"] = len(self.screen_set.screens)

        # Process navigation flows
        total_flows = sum(len(screen.navigation_flows) for screen in self.screen_set.screens)
        self.processing_stats["navigation_flows_processed"] = total_flows

        # Process component instances
        total_instances = sum(len(screen.component_instances) for screen in self.screen_set.screens)
        self.processing_stats["component_instances_processed"] = total_instances

    def load_component_catalog(self, catalog_path: str) -> None:
        """
        Load and validate component catalog from JSON file.

        Args:
            catalog_path: Path to component catalog JSON file

        Raises:
            CustomValidationError: If catalog is invalid
        """
        logger.info(f"Loading component catalog from: {catalog_path}")

        try:
            self.component_catalog = validate_and_load(Path(catalog_path), ComponentCatalog)
            logger.info(f"Successfully loaded {len(self.component_catalog.components)} components")
        except FileNotFoundError:
            raise CustomValidationError(f"Component catalog file not found: {catalog_path}")
        except json.JSONDecodeError as e:
            raise CustomValidationError(f"Invalid JSON in component catalog: {e}")

    def generate_pages(self) -> Dict[str, str]:
        """
        Generate all pages from screen specifications.

        Returns:
            Dictionary mapping file paths to generated content
        """
        if not self.screen_set:
            raise CustomValidationError("Screen specifications not loaded")

        if not self.component_catalog:
            raise CustomValidationError("Component catalog not loaded")

        logger.info("Starting page generation...")

        generated_files = {}

        # Ensure output directories exist
        self._ensure_output_directories()

        # Generate pages for each screen
        for screen in self.screen_set.screens:
            try:
                page_files = self._generate_single_page(screen)
                generated_files.update(page_files)

                # Update stats
                self.processing_stats["pages_generated"] += 1
                self.processing_stats["hooks_generated"] += 1  # At least one hook per page

            except Exception as e:
                logger.error(f"Error generating page for screen {screen.name}: {e}")
                continue

        # Generate routing configuration
        routing_files = self._generate_routing_configuration()
        generated_files.update(routing_files)
        self.processing_stats["routes_generated"] = len(routing_files)

        # Generate shared contexts and hooks
        shared_files = self._generate_shared_utilities()
        generated_files.update(shared_files)

        # Generate error boundaries
        if self.config.include_error_boundaries:
            error_boundary_files = self._generate_error_boundaries()
            generated_files.update(error_boundary_files)
            self.processing_stats["error_boundaries_generated"] = len(error_boundary_files)

        self.processing_stats["total_files_created"] = len(generated_files)

        logger.info(
            f"Generated {len(generated_files)} files for "
            f"{len(self.screen_set.screens)} screens")
        return generated_files

    def _generate_single_page(self, screen: ScreenSpecification) -> Dict[str, str]:
        """
        Generate a single page with all supporting files.

        Args:
            screen: Screen specification to generate

        Returns:
            Dictionary mapping file paths to generated content
        """
        generated_files = {}
        page_name = self._sanitize_screen_name(screen.name)

        # Generate main page file
        page_content = self._generate_page_file(screen)
        page_filename = self._get_page_filename(screen)
        page_path = Path(self.config.pages_directory) / page_filename
        generated_files[str(page_path)] = page_content

        # Generate TypeScript interface file
        if self.config.include_typescript:
            interface_content = self._generate_page_interface_file(screen)
            interface_filename = self._get_page_interface_filename(screen)
            interface_path = Path(self.config.pages_directory) / interface_filename
            generated_files[str(interface_path)] = interface_content

        # Generate custom hooks for the page
        hooks_content = self._generate_page_hooks(screen)
        for hook_name, hook_content in hooks_content.items():
            hook_filename = f"{hook_name}.ts"
            hook_path = Path(self.config.hooks_directory) / hook_filename
            generated_files[str(hook_path)] = hook_content

        # Generate form-specific logic if page has forms
        if self._page_has_forms(screen):
            form_content = self._generate_form_logic(screen)
            form_filename = f"{page_name}Form.ts"
            form_path = Path(self.config.hooks_directory) / form_filename
            generated_files[str(form_path)] = form_content
            self.processing_stats["forms_processed"] += 1

        return generated_files

    def _generate_page_file(self, screen: ScreenSpecification) -> str:
        """
        Generate the main React page file.

        Args:
            screen: Screen specification

        Returns:
            Generated React page code
        """
        logger.info(f"Generating page: {screen.name}")

        # Import statements
        imports = self._generate_page_imports(screen)

        # Page interface definition
        interface = self._generate_page_interface(screen)

        # Page implementation
        implementation = self._generate_page_implementation(screen)

        # Export statement
        export = f"export default {self._get_page_component_name(screen)};"

        return f"{imports}\n\n{interface}\n\n{implementation}\n\n{export}"

    def _generate_page_imports(self, screen: ScreenSpecification) -> str:
        """Generate import statements for page."""
        imports = ["import React from 'react';"]

        # Add routing imports
        if self.config.routing_library == RoutingLibrary.REACT_ROUTER:
            imports.extend([
                "import {useParams, useNavigate, useLocation} from 'react-router-dom';"
            ])

        # Add component imports based on screen instances
        used_components = self._get_used_components(screen)
        for component_id in used_components:
            component = self.component_catalog.get_component_by_id(component_id)
            if component:
                component_name = component.name
                component_path = f"{self.config.component_import_path}/{component_name}"
                imports.append(f"import {{{component_name}}} from '{component_path}';")

        # Add hook imports
        page_name = self._sanitize_screen_name(screen.name)
        imports.append(f"import use{page_name}Data from '@/hooks/use{page_name}Data';")
        imports.append(f"import use{page_name}Handlers from '@/hooks/use{page_name}Handlers';")

        # Add form imports if page has forms
        if self._page_has_forms(screen):
            imports.append(f"import use{page_name}Form from '@/hooks/use{page_name}Form';")

        # Add utility imports
        if self.config.include_error_boundaries:
            imports.append("import {PageErrorBoundary} from '@/components/ErrorBoundary';")

        # Add accessibility imports
        if self.config.include_accessibility:
            imports.append(
                "import {AriaLiveRegion} from '@/components/accessibility/AriaLiveRegion';")

        return "\n".join(sorted(set(imports)))

    def _generate_page_interface(self, screen: ScreenSpecification) -> str:
        """Generate TypeScript interface for page props."""
        page_name = self._get_page_component_name(screen)
        interface_name = f"{page_name}Props"

        properties = [
            "  className?: string;",
            "  children?: React.ReactNode;"
        ]

        # Add screen-specific props based on navigation parameters
        navigation_params = self._get_navigation_parameters(screen)
        for param_name, param_type in navigation_params.items():
            properties.append(f"  {param_name}?: {param_type};")

        return f"interface {interface_name} {{\n" + "\n".join(properties) + "\n}"

    def _generate_page_implementation(self, screen: ScreenSpecification) -> str:
        """Generate the main page implementation."""
        page_name = self._get_page_component_name(screen)

        # Function signature
        props = self._generate_props_destructuring(screen)
        signature = f"const {page_name}: React.FC<{page_name}Props> = ({{{props}}}) => {{"

        # Component body
        body_lines = []

        # Custom hooks
        body_lines.append("  // Custom hooks for data and state management")
        body_lines.append("  const {{ data, loading, error, refetch }} = use{page_name}Data();")
        body_lines.append("  const {{ handlers }} = use{page_name}Handlers();")

        # Form hook if needed
        if self._page_has_forms(screen):
            body_lines.append("  const {{ formData, formErrors, isSubmitting, handleFormChange, handleFormSubmit }} "
                              "= use{page_name}Form();")

        # Loading state
        if self.config.include_loading_states:
            body_lines.extend(self._generate_loading_state_logic(screen))

        # Error handling
        body_lines.extend(self._generate_error_handling_logic(screen))

        # Navigation logic
        body_lines.extend(self._generate_navigation_logic(screen))

        # Page JSX
        body_lines.extend(self._generate_page_jsx(screen))

        implementation = signature + "\n" + "\n".join(body_lines) + "\n};"

        return implementation

    def _generate_props_destructuring(self, screen: ScreenSpecification) -> str:
        """Generate props destructuring with defaults."""
        props = ["className", "children"]

        # Add navigation parameters
        navigation_params = self._get_navigation_parameters(screen)
        props.extend(navigation_params.keys())

        return ", ".join(props)

    def _generate_loading_state_logic(self, screen: ScreenSpecification) -> List[str]:
        """Generate loading state logic."""
        return [
            "  // Loading state",
            "  if (loading) {",
            "    return <PageLoadingState />;",
            "  }"
        ]

    def _generate_error_handling_logic(self, screen: ScreenSpecification) -> List[str]:
        """Generate error handling logic."""
        return [
            "  // Error handling",
            "  if (error) {",
            "    return (",
            "      <div className=\"flex flex-col items-center justify-center min-h-screen p-4\">",
            "        <h2 className=\"text-2xl font-semibold text-gray-900 mb-2\">",
            "          Something went wrong",
            "        </h2>",
            "        <p className=\"text-gray-600 mb-4\">{error.message}</p>",
            "        <button ",
            "          onClick={refetch} ",
            "          className=\"px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600\"",
            "        >",
            "          Try Again",
            "        </button>",
            "      </div>",
            "    );",
            "  }"
        ]

    def _generate_navigation_logic(self, screen: ScreenSpecification) -> List[str]:
        """Generate navigation logic."""
        if self.config.routing_library != RoutingLibrary.REACT_ROUTER:
            return []

        return [
            "  // Navigation",
            "  const navigate = useNavigate();",
            "  const location = useLocation();",
            "  const params = useParams();"
        ]

    def _generate_page_jsx(self, screen: ScreenSpecification) -> List[str]:
        """Generate the page JSX structure."""
        jsx_lines = []

        # Page wrapper with error boundary
        if self.config.include_error_boundaries:
            jsx_lines.append("  return (")
            jsx_lines.append("    <PageErrorBoundary>")
            jsx_lines.append("      <div className={{{className}}}>")
        else:
            jsx_lines.append("  return (")
            jsx_lines.append("    <div className={{{className}}}>")

        # Screen layout
        if screen.layout_grid:
            layout_classes = self._generate_layout_classes(screen.layout_grid)
            jsx_lines.append(f"        <div className=\"{layout_classes}\">")

        # Generate component instances
        component_tree = self._build_component_tree(screen)
        jsx_lines.extend(component_tree)

        # Close layout div
        if screen.layout_grid:
            jsx_lines.append("        </div>")

        # Accessibility announcements
        if self.config.include_accessibility:
            jsx_lines.append("      <AriaLiveRegion />")

        # Close main div and error boundary
        if self.config.include_error_boundaries:
            jsx_lines.append("      </div>")
            jsx_lines.append("    </PageErrorBoundary>")
        else:
            jsx_lines.append("    </div>")

        jsx_lines.append("  );")

        return jsx_lines

    def _build_component_tree(self, screen: ScreenSpecification) -> List[str]:
        """Build the component tree JSX from screen instances."""
        jsx_lines = []

        # Group component instances by parent
        root_instances = [inst for inst in screen.component_instances if inst.parent_id is None]

        for instance in root_instances:
            component_jsx = self._generate_component_jsx(instance, screen.component_instances)
            jsx_lines.extend(f"        {line}" for line in component_jsx.split('\n'))

        return jsx_lines

    def _generate_component_jsx(self, instance: ComponentInstance, all_instances: List[ComponentInstance],
                                indent_level: int = 0) -> str:
        """Generate JSX for a single component instance."""
        component = self.component_catalog.get_component_by_id(instance.component_id)
        if not component:
            logger.warning(f"Component not found for instance: {instance.component_id}")
            return f"<!-- Component {instance.component_id} not found -->"

        indent = "  " * (indent_level + 2)

        # Build component props
        props_lines = []
        for prop_name, prop_value in instance.properties.items():
            formatted_value = self._format_prop_value(prop_value)
            props_lines.append(f"{indent}    {prop_name}={formatted_value}")

        # Find child instances
        child_instances = [inst for inst in all_instances if inst.parent_id == instance.id]

        # Build component JSX
        if child_instances:
            # Component with children
            jsx_lines = [
                f"{indent}<{component.name}",
                *props_lines,
                f"{indent}>"
            ]

            # Add children
            for child in child_instances:
                child_jsx = self._generate_component_jsx(child, all_instances, indent_level + 1)
                jsx_lines.append(child_jsx)

            jsx_lines.append(f"{indent}</{component.name}>")
        else:
            # Component without children
            if props_lines:
                jsx_lines = [
                    f"{indent}<{component.name}",
                    *props_lines,
                    f"{indent} />"
                ]
            else:
                jsx_lines = [f"{indent}<{component.name} />"]

        return "\n".join(jsx_lines)

    def _format_prop_value(self, value: Any) -> str:
        """Format a prop value for JSX."""
        if value is None:
            return "{null}"
        elif isinstance(value, bool):
            return "{true}" if value else "{false}"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, (int, float)):
            return f"{{{value}}}"
        elif isinstance(value, list):
            formatted_items = [self._format_prop_value(item) for item in value]
            return f"{{[{', '.join(formatted_items)}]}}"
        elif isinstance(value, dict):
            formatted_items = [f"{k}: {self._format_prop_value(v)}" for k, v in value.items()]
            return f"{{{{{', '.join(formatted_items)}}}}}"
        else:
            return f'{{"{str(value)}"}}'

    def _generate_layout_classes(self, layout_grid: LayoutGrid) -> str:
        """Generate CSS classes for layout grid."""
        classes = []

        if layout_grid.type == "columns":
            if layout_grid.columns:
                classes.append(f"grid grid-cols-{layout_grid.columns}")
            if layout_grid.gutter_width:
                classes.append(f"gap-{layout_grid.gutter_width // 4}")  # Convert to Tailwind units
            if layout_grid.margin:
                classes.append(f"p-{layout_grid.margin // 4}")
            if layout_grid.max_width:
                classes.append(f"max-w-{layout_grid.max_width}")
        elif layout_grid.type == "flex":
            classes.extend(["flex", "flex-col"])
            if layout_grid.gutter_width:
                classes.append(f"gap-{layout_grid.gutter_width // 4}")
            if layout_grid.margin:
                classes.append(f"p-{layout_grid.margin // 4}")
        else:  # absolute
            classes.append("relative")

        return " ".join(classes)

    def _generate_page_interface_file(self, screen: ScreenSpecification) -> str:
        """Generate separate TypeScript interface file."""
        page_name = self._get_page_component_name(screen)
        interface_name = f"{page_name}Props"

        imports = [
            "import React from 'react';"
        ]

        properties = [
            "  className?: string;",
            "  children?: React.ReactNode;"
        ]

        # Add navigation parameters
        navigation_params = self._get_navigation_parameters(screen)
        for param_name, param_type in navigation_params.items():
            properties.append(f"  {param_name}?: {param_type};")

        # Add data interfaces
        data_interface = self._generate_data_interface(screen)

        interface_content = (
            f"{'\n'.join(imports)}\n\n"
            f"export interface {interface_name} {{\n"
            f"{'\n'.join(properties)}\n"
            f"}}\n\n"
            f"{data_interface}"
        )

        return interface_content

    def _generate_data_interface(self, screen: ScreenSpecification) -> str:
        """Generate data interface for the page."""
        page_name = self._sanitize_screen_name(screen.name)
        interface_name = f"{page_name}Data"

        # Extract data structure from component instances
        data_properties = []

        for instance in screen.component_instances:
            component = self.component_catalog.get_component_by_id(instance.component_id)
            if component:
                # Add properties based on component type
                if component.category == "form":
                    data_properties.append(f"  {instance.id}?: Record<string, any>;")
                elif component.category == "display":
                    if "title" in instance.properties:
                        data_properties.append(f"  {instance.id}_title?: string;")
                    if "description" in instance.properties:
                        data_properties.append(f"  {instance.id}_description?: string;")

        if data_properties:
            return (
                f"export interface {interface_name} {{\n"
                f"{'\n'.join(data_properties)}\n"
                f"}}"
            )
        return ""

    def _generate_page_hooks(self, screen: ScreenSpecification) -> Dict[str, str]:
        """Generate custom hooks for the page."""
        page_name = self._sanitize_screen_name(screen.name)
        hooks = {}

        # Data fetching hook
        data_hook_content = self._generate_data_hook(screen)
        hooks[f"use{page_name}Data"] = data_hook_content

        # Event handlers hook
        handlers_hook_content = self._generate_handlers_hook(screen)
        hooks[f"use{page_name}Handlers"] = handlers_hook_content

        return hooks

    def _generate_data_hook(self, screen: ScreenSpecification) -> str:
        """Generate data fetching hook."""
        page_name = self._sanitize_screen_name(screen.name)
        page_name_snake = self._to_snake_case(screen.name)
        hook_name = f"use{page_name}Data"

        imports = [
            "import { useState, useEffect, useCallback } from 'react';",
            "import { api } from '@/utils/api';"
        ]

        hook_content = f"""
{'\\n'.join(imports)}

export interface {hook_name}Return {{
  data: any;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}}

export const {hook_name} = (): {hook_name}Return => {{
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {{
    try {{
      setLoading(true);
      setError(null);

      // TODO: Implement actual API call based on screen requirements
      // const response = await api.get('/{page_name_snake.lower()}');
      // setData(response.data);

      // Mock data for now
      setData({{}});
    }} catch (err) {{
      setError(err instanceof Error ? err : new Error('Unknown error'));
    }} finally {{
      setLoading(false);
    }}
  }}, []);

  useEffect(() => {{
    fetchData();
  }}, [fetchData]);

  return {{
    data,
    loading,
    error,
    refetch: fetchData
  }};
}};
"""
        return hook_content.strip()

    def _generate_handlers_hook(self, screen: ScreenSpecification) -> str:
        """Generate event handlers hook."""
        page_name = self._sanitize_screen_name(screen.name)
        hook_name = f"use{page_name}Handlers"

        imports = [
            "import { useCallback } from 'react';",
            "import { useNavigate } from 'react-router-dom';"
        ]

        handlers = []

        # Generate navigation handlers
        for flow in screen.navigation_flows:
            handler_name = f"handleNavigateTo{flow.to_screen_id.title()}"
            handlers.append(f"""
  const {handler_name} = useCallback(() => {{
    navigate('/{flow.to_screen_id}'{{#if flow.parameters}}{{{flow.parameters}}}{{/if}});
  }}, [navigate]);
""")

        # Generate component interaction handlers
        for instance in screen.component_instances:
            component = self.component_catalog.get_component_by_id(instance.component_id)
            if component and component.category == "interactive":
                handler_name = f"handle{instance.name.replace(' ', '')}Click"
                handlers.append(f"""
  const {handler_name} = useCallback(() => {{
    // TODO: Implement {instance.name} handler logic
    console.log('{instance.name} clicked');
  }}, []);
""")

        hook_content = f"""
{'\\n'.join(imports)}

export const {hook_name} = () => {{
  const navigate = useNavigate();
{'\\n'.join(handlers)}
  return {{
{','.join([h.split('=')[0].strip() for h in handlers if h.strip()])}
  }};
}};
"""
        return hook_content.strip()

    def _generate_form_logic(self, screen: ScreenSpecification) -> str:
        """Generate form-specific logic."""
        page_name = self._sanitize_screen_name(screen.name)
        page_name_snake = self._to_snake_case(screen.name)
        hook_name = f"use{page_name}Form"

        imports = [
            "import { useState, useCallback } from 'react';",
            "import { useFormValidation } from '@/hooks/useFormValidation';"
        ]

        hook_content = f"""
{'\\n'.join(imports)}

export interface {hook_name}Return {{
  formData: Record<string, any>;
  formErrors: Record<string, string>;
  isSubmitting: boolean;
  handleFormChange: (field: string, value: any) => void;
  handleFormSubmit: (event: React.FormEvent) => Promise<void>;
  resetForm: () => void;
}}

export const {hook_name} = (): {hook_name}Return => {{
  const [formData, setFormData] = useState<Record<string, any>>({{}});
  const [formErrors, setFormErrors] = useState<Record<string, string>>({{}});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleFormChange = useCallback((field: string, value: any) => {{
    setFormData(prev => ({{
      ...prev,
      [field]: value
    }}));

    // Clear error for this field
    if (formErrors[field]) {{
      setFormErrors(prev => ({{
        ...prev,
        [field]: ''
      }}));
    }}
  }}, [formErrors]);

  const handleFormSubmit = useCallback(async (event: React.FormEvent) => {{
    event.preventDefault();

    try {{
      setIsSubmitting(true);

      // TODO: Implement form validation
      // const validationErrors = await validateForm(formData);
      // if (validationErrors) {{
      //   setFormErrors(validationErrors);
      //   return;
      // }}

      // TODO: Implement form submission
      // await api.post('/{page_name_snake.lower()}', formData);

      console.log('Form submitted:', formData);
    }} catch (error) {{
      console.error('Form submission error:', error);
    }} finally {{
      setIsSubmitting(false);
    }}
  }}, [formData]);

  const resetForm = useCallback(() => {{
    setFormData({{}});
    setFormErrors({{}});
    setIsSubmitting(false);
  }}, []);

  return {{
    formData,
    formErrors,
    isSubmitting,
    handleFormChange,
    handleFormSubmit,
    resetForm
  }};
}};
"""
        return hook_content.strip()

    def _generate_routing_configuration(self) -> Dict[str, str]:
        """Generate routing configuration files."""
        routing_files = {}

        if self.config.routing_library == RoutingLibrary.REACT_ROUTER:
            # Generate main routes file
            routes_content = self._generate_react_router_routes()
            routes_path = Path(self.config.routes_directory) / "index.tsx"
            routing_files[str(routes_path)] = routes_content

            # Generate route types
            if self.config.include_typescript:
                types_content = self._generate_route_types()
                types_path = Path(self.config.routes_directory) / "types.ts"
                routing_files[str(types_path)] = types_content

        return routing_files

    def _generate_react_router_routes(self) -> str:
        """Generate React Router configuration."""
        imports = [
            "import React from 'react';",
            "import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';",
            "import Layout from '@/components/Layout';"
        ]

        # Import page components
        for screen in self.screen_set.screens:
            page_name = self._get_page_component_name(screen)
            # page_path = f"../pages/{screen.name}"
            imports.append(f"import {page_name} from '@/pages/{screen.name}';")

        routes = []

        # Add routes for each screen
        for screen in self.screen_set.screens:
            route_path = f"/{screen.id}"
            page_name = self._get_page_component_name(screen)

            route = {
                "path": route_path,
                "element": f"<{page_name} />"
            }

            # Add navigation parameters if any
            params = self._get_navigation_parameters(screen)
            if params:
                route["path"] += f"/:{':'.join(params.keys())}"

            routes.append(route)

        # Create router configuration
        routes_config = ",\n  ".join([
            f"{{\n    path: '{route['path']}',\n    element: {route['element']}\n  }}"
            for route in routes
        ])

        # Build the router content using string concatenation to avoid brace conflicts
        imports_section = chr(10).join(imports)

        router_content = f"""
{imports_section}

const router = createBrowserRouter([
  {{
    path: '/',
    element: <Layout />,
    errorElement: <div>Something went wrong!</div>,
    children: [
      {routes_config},
      {{
        path: '*',
        element: <Navigate to="/" replace />
      }}
    ]
  }}
]);

export const AppRouter: React.FC = () => {{
  return <RouterProvider router={{router}} />;
}};

export default AppRouter;
"""
        return router_content.strip()

    def _generate_route_types(self) -> str:
        """Generate TypeScript types for routes."""
        type_definitions = []

        for screen in self.screen_set.screens:
            screen_name = self._sanitize_screen_name(screen.name)
            route_name = f"{screen_name}RouteParams"

            params = self._get_navigation_parameters(screen)
            if params:
                param_types = ", ".join([f"{name}: {type_}" for name, type_ in params.items()])
                type_def = f"export interface {route_name} {{ {param_types}; }}"
            else:
                type_def = f"export interface {route_name} {{}}"

            type_definitions.append(type_def)

        return "\n\n".join(type_definitions)

    def _generate_shared_utilities(self) -> Dict[str, str]:
        """Generate shared utilities and contexts."""
        shared_files = {}

        # Generate contexts
        if self.config.state_management == StateManagement.REACT_CONTEXT:
            app_context_content = self._generate_app_context()
            context_path = Path(self.config.contexts_directory) / "AppContext.tsx"
            shared_files[str(context_path)] = app_context_content
            self.processing_stats["contexts_generated"] += 1

        # Generate loading states
        if self.config.include_loading_states:
            loading_content = self._generate_loading_states()
            loading_path = Path(self.config.pages_directory) / "LoadingStates.tsx"
            shared_files[str(loading_path)] = loading_content

        return shared_files

    def _generate_app_context(self) -> str:
        """Generate application context."""
        return """
import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface AppState {
  user: any | null;
  loading: boolean;
  error: string | null;
  theme: 'light' | 'dark';
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<any>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

type AppAction =
  | { type: 'SET_USER'; payload: any }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' };

const initialState: AppState = {
  user: null,
  loading: false,
  error: null,
  theme: 'light'
};

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    default:
      return state;
  }
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
"""

    def _generate_loading_states(self) -> str:
        """Generate loading state components."""
        return """
import React from 'react';

export const PageLoadingState: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );
};

export const ComponentLoadingState: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-500"></div>
    </div>
  );
};

export const SkeletonLoader: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`}></div>
  );
};
"""

    def _generate_error_boundaries(self) -> Dict[str, str]:
        """Generate error boundary components."""
        error_files = {}

        # Main error boundary
        error_boundary_content = self._generate_error_boundary_component()
        error_boundary_path = Path(self.config.pages_directory) / "ErrorBoundary.tsx"
        error_files[str(error_boundary_path)] = error_boundary_content

        return error_files

    def _generate_error_boundary_component(self) -> str:
        """Generate error boundary component."""
        return """
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto "
                              "bg-red-100 rounded-full mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5
                      L13.732 4c-.77-.833-1.964-.833-2.732 0 L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              </svg>
            </div>

            <h1 className="text-xl font-semibold text-gray-900 text-center mb-2">
              Something went wrong
            </h1>

            <p className="text-gray-600 text-center mb-6">
              We're sorry, but something unexpected happened. The error has been logged and we'll look into it.
            </p>

            <div className="space-y-3">
              <button
                onClick={this.handleReset}
                className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>

              <button
                onClick={() => window.location.href = '/'}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Go Home
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 p-4 bg-gray-100 rounded text-sm">
                <summary className="cursor-pointer font-medium text-gray-700 mb-2">
                  Error Details (Development Only)
                </summary>
                <pre className="whitespace-pre-wrap text-xs text-red-600 overflow-auto">
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export const PageErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary fallback={
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Page Error</h2>
        <p className="text-gray-600 mb-4">This page encountered an error.</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Reload Page
        </button>
      </div>
    </div>
  }>
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;
"""

    # Helper methods
    def _get_used_components(self, screen: ScreenSpecification) -> Set[str]:
        """Get set of component IDs used in screen."""
        return set(instance.component_id for instance in screen.component_instances)

    def _get_navigation_parameters(self, screen: ScreenSpecification) -> Dict[str, str]:
        """Extract navigation parameters from screen flows."""
        params = {}
        for flow in screen.navigation_flows:
            if flow.parameters:
                for param_name, param_value in flow.parameters.items():
                    if isinstance(param_value, str):
                        params[param_name] = "string"
                    elif isinstance(param_value, int):
                        params[param_name] = "number"
                    elif isinstance(param_value, bool):
                        params[param_name] = "boolean"
                    else:
                        params[param_name] = "any"
        return params

    def _page_has_forms(self, screen: ScreenSpecification) -> bool:
        """Check if page contains form components."""
        for instance in screen.component_instances:
            component = self.component_catalog.get_component_by_id(instance.component_id)
            if component and component.category == "form":
                return True
        return False

    def _get_page_component_name(self, screen: ScreenSpecification) -> str:
        """Get component name for screen."""
        return self._sanitize_screen_name(screen.name).replace(' ', '')

    def _sanitize_screen_name(self, screen_name: str) -> str:
        """Sanitize screen name for use in code."""
        # Remove special characters, convert to camelCase
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', screen_name)
        words = sanitized.split()
        if not words:
            return "Page"

        return words[0].title() + ''.join(word.title() for word in words[1:])

    def _to_snake_case(self, screen_name: str) -> str:
        """Convert screen name to snake_case for API endpoints."""
        # Remove special characters, convert to snake_case
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', screen_name)
        words = sanitized.split()
        if not words:
            return "page"

        return '_'.join(word.lower() for word in words)

    def _get_page_filename(self, screen: ScreenSpecification) -> str:
        """Get filename for page file."""
        ext = "tsx" if self.config.include_typescript else "jsx"
        return f"{screen.name}.{ext}"

    def _get_page_interface_filename(self, screen: ScreenSpecification) -> str:
        """Get filename for page interface file."""
        return f"{screen.name}.props.ts"

    def _ensure_output_directories(self) -> None:
        """Ensure all output directories exist."""
        directories = [
            self.config.output_directory,
            self.config.pages_directory,
            self.config.hooks_directory,
            self.config.contexts_directory,
            self.config.routes_directory
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def save_generated_files(self, generated_files: Dict[str, str]) -> None:
        """
        Save generated files to filesystem.

        Args:
            generated_files: Dictionary mapping file paths to content
        """
        logger.info(f"Saving {len(generated_files)} generated files...")

        for file_path, content in generated_files.items():
            try:
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.debug(f"Saved: {file_path}")
            except Exception as e:
                logger.error(f"Error saving file {file_path}: {e}")

    def generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata about the generation process."""
        return {
            "generation_info": {
                "timestamp": datetime.now().isoformat(),
                "page_type": self.config.page_type.value,
                "routing_library": self.config.routing_library.value,
                "state_management": self.config.state_management.value,
                "config": {
                    "include_typescript": self.config.include_typescript,
                    "include_responsive": self.config.include_responsive,
                    "include_error_boundaries": self.config.include_error_boundaries,
                    "include_loading_states": self.config.include_loading_states,
                    "include_accessibility": self.config.include_accessibility
                }
            },
            "processing_stats": self.processing_stats,
            "screens_summary": {
                "total": len(self.screen_set.screens) if self.screen_set else 0,
                "navigation_flows": self.processing_stats.get("navigation_flows_processed", 0),
                "component_instances": self.processing_stats.get("component_instances_processed", 0),
                "forms_detected": self.processing_stats.get("forms_processed", 0)
            }
        }

    def validate_generation(self, generated_files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate generated files for correctness.

        Args:
            generated_files: Dictionary of generated files

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Basic syntax validation
        for file_path, content in generated_files.items():
            if file_path.endswith('.tsx') or file_path.endswith('.ts'):
                if not content.strip():
                    errors.append(f"Empty file: {file_path}")
                elif ('export default' not in content and
                      'export interface' not in content and
                      'export const' not in content):
                    errors.append(f"Missing export in: {file_path}")

        return len(errors) == 0, errors


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Page Generator - Step 5 of SimFlo Figma-to-RAG Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate pages with default settings
  python3 v2/page-generator/main.py \\
    --screens examples/sample-screen-specs/ \\
    --catalog examples/sample-component-catalog.json \\
    --output ./output/

  # Generate with specific configuration
  python3 v2/page-generator/main.py \\
    --screens examples/sample-screen-specs/ \\
    --catalog examples/sample-component-catalog.json \\
    --output ./output/ \\
    --routing react_router \\
    --state-management react_context \\
    --include-typescript \\
    --include-error-boundaries

  # Generate with custom configuration
  python3 v2/page-generator/main.py \\
    --screens examples/sample-screen-specs/ \\
    --catalog examples/sample-component-catalog.json \\
    --output ./output/ \\
    --config custom-config.json \\
    --verbose
        """
    )

    # Required arguments
    parser.add_argument(
        '--screens', '-s',
        required=True,
        help='Path to screen specifications directory or JSON file'
    )

    parser.add_argument(
        '--catalog', '-c',
        required=True,
        help='Path to component catalog JSON file'
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for generated files'
    )

    # Optional arguments
    parser.add_argument(
        '--routing',
        choices=['react_router', 'next_router', 'reach_router'],
        default='react_router',
        help='Routing library to use (default: react_router)'
    )

    parser.add_argument(
        '--state-management',
        choices=['react_context', 'redux', 'zustand', 'custom_hooks'],
        default='react_context',
        help='State management solution (default: react_context)'
    )

    parser.add_argument(
        '--config',
        help='Path to custom configuration JSON file'
    )

    # Feature flags
    parser.add_argument(
        '--include-typescript',
        action='store_true',
        default=True,
        help='Include TypeScript interfaces and types (default: True)'
    )

    parser.add_argument(
        '--no-typescript',
        action='store_true',
        help='Disable TypeScript generation'
    )

    parser.add_argument(
        '--include-responsive',
        action='store_true',
        default=True,
        help='Include responsive design patterns (default: True)'
    )

    parser.add_argument(
        '--include-error-boundaries',
        action='store_true',
        default=True,
        help='Include error boundary components (default: True)'
    )

    parser.add_argument(
        '--include-loading-states',
        action='store_true',
        default=True,
        help='Include loading state components (default: True)'
    )

    parser.add_argument(
        '--include-accessibility',
        action='store_true',
        default=True,
        help='Include accessibility features (default: True)'
    )

    # Utility arguments
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate files but do not save to disk'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input files, do not generate pages'
    )

    return parser


def load_config(config_path: Optional[str]) -> Optional[Dict[str, Any]]:
    """Load custom configuration from JSON file."""
    if not config_path:
        return None

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}")
        return None


def main():
    """Main entry point for page generator."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting Page Generator - Step 5 of SimFlo Figma-to-RAG Pipeline")

    try:
        # Load custom configuration
        config_data = load_config(args.config)

        # Create generation configuration
        config = PageGenerationConfig(
            routing_library=RoutingLibrary(args.routing),
            state_management=StateManagement(args.state_management),
            include_typescript=args.include_typescript and not args.no_typescript,
            include_responsive=args.include_responsive,
            include_error_boundaries=args.include_error_boundaries,
            include_loading_states=args.include_loading_states,
            include_accessibility=args.include_accessibility,
            output_directory=args.output,
            pages_directory=f"{args.output}/pages/",
            hooks_directory=f"{args.output}/hooks/",
            contexts_directory=f"{args.output}/contexts/",
            routes_directory=f"{args.output}/routes/"
        )

        # Override with custom config if provided
        if config_data:
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Initialize generator
        generator = PageGenerator(config)

        # Load and validate inputs
        generator.load_screen_specifications(args.screens)
        generator.load_component_catalog(args.catalog)

        if args.validate_only:
            logger.info("Validation complete - inputs are valid")
            return 0

        # Generate pages
        generated_files = generator.generate_pages()

        # Validate generated files
        is_valid, errors = generator.validate_generation(generated_files)
        if not is_valid:
            logger.error("Validation errors found:")
            for error in errors:
                logger.error(f"  - {error}")
            return 1

        # Save files (unless dry run)
        if not args.dry_run:
            generator.save_generated_files(generated_files)

            # Save metadata
            metadata = generator.generate_metadata()
            metadata_path = Path(args.output) / "page-generation-metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Generation complete! Files saved to: {args.output}")
            logger.info(f"Generated {len(generated_files)} files")
        else:
            logger.info("Dry run complete - no files saved")
            logger.info(f"Would generate {len(generated_files)} files")

        return 0

    except CustomValidationError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
