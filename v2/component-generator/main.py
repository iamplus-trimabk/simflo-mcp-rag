#!/usr/bin/env python3
"""
Component Generator - Step 4 of SimFlo Figma-to-RAG Pipeline

Generates React components from component catalogs and design tokens.
Supports multiple component libraries (shadcn/ui, Gluestack) with TypeScript,
accessibility features, responsive design, and comprehensive documentation.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from common.validation import validate_and_load, CustomValidationError
from common.schemas import (
    ComponentCatalog, ComponentDefinition, ComponentProperty, ComponentVariant, DesignTokenSet
)
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
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


class ComponentLibrary(Enum):
    """Supported component libraries."""
    SHADCN = "shadcn"
    GLUESTACK = "gluestack"


class OutputFormat(Enum):
    """Output file formats."""
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    STORIES = "stories"
    USER_STORIES = "user_stories"


@dataclass
class GenerationConfig:
    """Configuration for component generation."""
    library: ComponentLibrary = ComponentLibrary.SHADCN
    output_format: OutputFormat = OutputFormat.TYPESCRIPT
    include_accessibility: bool = True
    include_responsive: bool = True
    include_stories: bool = True
    include_user_stories: bool = True
    output_directory: str = "./output/"
    component_directory: str = "./output/components/"
    stories_directory: str = "./output/stories/"
    user_stories_directory: str = "./output/user-stories/"
    custom_templates: Optional[Dict[str, str]] = None
    indent_size: int = 2
    use_semantic_tokens: bool = True


class ComponentGenerator:
    """
    Main component generator class.

    Generates React components from component catalogs with support for:
    - Multiple component libraries (shadcn/ui, Gluestack)
    - TypeScript interfaces and type safety
    - Accessibility attributes and ARIA labels
    - Responsive design patterns
    - Component variants and theming
    - Storybook stories
    - User stories documentation
    """

    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize component generator with configuration."""
        self.config = config or GenerationConfig()
        self.component_catalog: Optional[ComponentCatalog] = None
        self.design_tokens: Optional[DesignTokenSet] = None
        self.processing_stats = {
            "components_processed": 0,
            "interfaces_generated": 0,
            "stories_generated": 0,
            "user_stories_generated": 0,
            "accessibility_features_added": 0,
            "responsive_patterns_added": 0,
            "total_files_created": 0,
            "components_by_category": {},
            "libraries_supported": []
        }

    def load_component_catalog(self, input_path: str) -> None:
        """
        Load and validate component catalog from JSON file.

        Args:
            input_path: Path to component catalog JSON file

        Raises:
            CustomValidationError: If catalog is invalid
        """
        logger.info(f"Loading component catalog from: {input_path}")

        try:
            self.component_catalog = validate_and_load(Path(input_path), ComponentCatalog)

            # Update processing stats
            categories = {}
            for component in self.component_catalog.components:
                categories[component.category] = categories.get(component.category, 0) + 1

            self.processing_stats.update({
                "components_processed": len(self.component_catalog.components),
                "components_by_category": categories
            })

            logger.info(f"Successfully loaded {len(self.component_catalog.components)} components")

        except FileNotFoundError:
            raise CustomValidationError(f"Component catalog file not found: {input_path}")
        except json.JSONDecodeError as e:
            raise CustomValidationError(f"Invalid JSON in component catalog: {e}")

    def load_design_tokens(self, tokens_path: str) -> None:
        """
        Load and validate design tokens from JSON file.

        Args:
            tokens_path: Path to design tokens JSON file

        Raises:
            CustomValidationError: If tokens are invalid
        """
        logger.info(f"Loading design tokens from: {tokens_path}")

        try:
            self.design_tokens = validate_and_load(Path(tokens_path), DesignTokenSet)
            logger.info(f"Successfully loaded design tokens")
        except FileNotFoundError:
            raise CustomValidationError(f"Design tokens file not found: {tokens_path}")
        except json.JSONDecodeError as e:
            raise CustomValidationError(f"Invalid JSON in design tokens: {e}")

    def generate_components(self) -> Dict[str, str]:
        """
        Generate all components from the catalog.

        Returns:
            Dictionary mapping component names to generated file content
        """
        if not self.component_catalog:
            raise CustomValidationError("Component catalog not loaded")

        logger.info("Starting component generation...")

        generated_files = {}

        # Ensure output directories exist
        self._ensure_output_directories()

        for component in self.component_catalog.components:
            try:
                component_files = self._generate_single_component(component)
                generated_files.update(component_files)

                # Update stats
                self.processing_stats["interfaces_generated"] += 1
                if self.config.include_stories:
                    self.processing_stats["stories_generated"] += 1
                if self.config.include_user_stories:
                    self.processing_stats["user_stories_generated"] += 1

            except Exception as e:
                logger.error(f"Error generating component {component.name}: {e}")
                continue

        self.processing_stats["total_files_created"] = len(generated_files)
        self.processing_stats["libraries_supported"] = [self.config.library.value]

        logger.info(
            f"Generated {len(generated_files)} files for "
            f"{len(self.component_catalog.components)} components")
        return generated_files

    def _generate_single_component(self, component: ComponentDefinition) -> Dict[str, str]:
        """
        Generate a single component with all supporting files.

        Args:
            component: Component definition to generate

        Returns:
            Dictionary mapping file paths to generated content
        """
        generated_files = {}

        # Generate main component file
        component_content = self._generate_component_file(component)
        component_filename = self._get_component_filename(component)
        component_path = Path(self.config.component_directory) / component_filename
        generated_files[str(component_path)] = component_content

        # Generate TypeScript interface file
        interface_content = self._generate_interface_file(component)
        interface_filename = self._get_interface_filename(component)
        interface_path = Path(self.config.component_directory) / interface_filename
        generated_files[str(interface_path)] = interface_content

        # Generate Storybook story
        if self.config.include_stories:
            story_content = self._generate_story_file(component)
            story_filename = self._get_story_filename(component)
            story_path = Path(self.config.stories_directory) / story_filename
            generated_files[str(story_path)] = story_content

        # Generate user stories
        if self.config.include_user_stories:
            user_stories_content = self._generate_user_stories_file(component)
            user_stories_filename = self._get_user_stories_filename(component)
            user_stories_path = Path(self.config.user_stories_directory) / user_stories_filename
            generated_files[str(user_stories_path)] = user_stories_content

        return generated_files

    def _generate_component_file(self, component: ComponentDefinition) -> str:
        """
        Generate the main React component file.

        Args:
            component: Component definition

        Returns:
            Generated TypeScript React component code
        """
        logger.info(f"Generating component: {component.name}")

        # Import statements
        imports = self._generate_imports(component)

        # Interface definition (if not separate file)
        interface = self._generate_inline_interface(component)

        # Component implementation
        implementation = self._generate_component_implementation(component)

        # Export statement
        export = f"export default {component.name};"

        return f"{imports}\n\n{interface}\n\n{implementation}\n\n{export}"

    def _generate_imports(self, component: ComponentDefinition) -> str:
        """Generate import statements for component."""
        imports = ["import React from 'react';"]

        # Add library-specific imports
        if self.config.library == ComponentLibrary.SHADCN:
            imports.extend([
                "import {cn} from '@/lib/utils';",
                "import {cva, type VariantProps} from 'class-variance-authority';"
            ])
        elif self.config.library == ComponentLibrary.GLUESTACK:
            imports.extend([
                "import {useTheme} from '@gluestack-ui/themed';"
            ])

        # Add icon imports if component uses icons
        if self._has_icon_properties(component):
            imports.append("import {Icon} from '@/components/ui/icon';")

        # Add accessibility imports
        if self.config.include_accessibility:
            imports.append("import {AriaAttributes} from 'react';")

        return "\n".join(imports)

    def _generate_inline_interface(self, component: ComponentDefinition) -> str:
        """Generate TypeScript interface inline in component file."""
        interface_name = f"{component.name}Props"

        # Base interface properties
        properties = []
        properties.append("  className?: string;")
        properties.append("  children?: React.ReactNode;")

        # Add component-specific properties
        for prop in component.properties:
            prop_type = self._map_property_type(prop)
            optional = "" if prop.required else "?"
            default_value = f" = {
                self._format_default_value(prop)}" if prop.default_value is not None else ""
            properties.append(f"  {prop.name}{optional}: {prop_type}{default_value};")

        # Add accessibility attributes
        if self.config.include_accessibility:
            properties.append("  'aria-label'?: string;")
            properties.append("  'aria-labelledby'?: string;")
            properties.append("  'aria-describedby'?: string;")

        return f"interface {interface_name} {{\n" + "\n".join(properties) + "\n}"

    def _generate_component_implementation(self, component: ComponentDefinition) -> str:
        """Generate the main component implementation."""
        component_name = component.name

        # Function signature
        signature = f"const {component_name} = React.forwardRef<"

        # Determine ref type based on component category
        ref_type = self._get_ref_type(component)
        signature += f"{ref_type}, {component_name}Props>"

        signature += f">(({component_name}Props) => {{"

        # Component body
        body = self._generate_component_body(component)

        return f"{signature}\n{body}\n}});\n\n"

    def _generate_component_body(self, component: ComponentDefinition) -> str:
        """Generate the component body implementation."""
        lines = []

        # Destructure props
        props_destructuring = self._generate_props_destructuring(component)
        if props_destructuring:
            lines.append(props_destructuring)

        # Generate component variants (CVA for shadcn)
        if self.config.library == ComponentLibrary.SHADCN and component.variants:
            cva_definition = self._generate_cva_definition(component)
            if cva_definition:
                lines.append(cva_definition)

        # Generate accessibility attributes
        if self.config.include_accessibility:
            aria_props = self._generate_aria_attributes(component)
            if aria_props:
                lines.append(aria_props)

        # Generate responsive classes
        if self.config.include_responsive:
            responsive_classes = self._generate_responsive_classes(component)
            if responsive_classes:
                lines.append(responsive_classes)

        # Generate component JSX
        jsx = self._generate_component_jsx(component)
        lines.append(jsx)

        return "\n".join(lines)

    def _generate_props_destructuring(self, component: ComponentDefinition) -> str:
        """Generate props destructuring with defaults."""
        props = []

        # Common props
        props.append("className")
        props.append("children")

        # Component-specific props
        for prop in component.properties:
            if prop.default_value is not None:
                props.append(f"{prop.name} = {self._format_default_value(prop)}")
            else:
                props.append(prop.name)

        return f"const {{{', '.join(props)}}} = props;"

    def _generate_cva_definition(self, component: ComponentDefinition) -> str:
        """Generate class-variance-authority definition for shadcn components."""
        if not component.variants:
            return ""

        base_classes = self._get_base_classes(component)
        variant_configs = []

        for variant in component.variants:
            variant_class = self._get_variant_class(component, variant)
            if variant_class:
                variant_configs.append(f"    {variant.name}: '{variant_class}'")

        if not variant_configs:
            return ""

        cva_name = f"{component.name.lower()}Variants"
        return (
            f"const {cva_name} = cva(\n"
            f"  '{base_classes}',\n"
            f"  {{\n"
            f"    variants: {{\n"
            f"{',\n'.join(variant_configs)}\n"
            f"   }}\n"
            f" }}\n"
            f");"
        )

    def _generate_aria_attributes(self, component: ComponentDefinition) -> str:
        """Generate accessibility attributes."""
        if component.category not in ["interactive", "form"]:
            return ""

        return (
            "const ariaProps: AriaAttributes = {\n"
            "  'aria-label': ariaLabel,\n"
            "  'aria-labelledby': ariaLabelledby,\n"
            "  'aria-describedby': ariaDescribedby\n"
            "};"
        )

    def _generate_responsive_classes(self, component: ComponentDefinition) -> str:
        """Generate responsive design classes."""
        if not self.config.include_responsive:
            return ""

        # Generate responsive breakpoint classes based on design tokens
        responsive_tokens = []

        if self.design_tokens:
            # Add spacing-based responsive classes
            spacing_tokens = [t for t in self.design_tokens.spacing if t.category == "margin"]
            if spacing_tokens:
                responsive_tokens.append(
                    "// Responsive spacing classes from design tokens"
                )

        return "\n".join(responsive_tokens)

    def _generate_component_jsx(self, component: ComponentDefinition) -> str:
        """Generate the component JSX."""
        component_type = self._get_jsx_element_type(component)

        # Build className
        class_names = self._build_class_names(component)

        # Build props
        props = self._build_jsx_props(component, class_names)

        # Build children
        children = self._build_jsx_children(component)

        return f"return (\n  <{component_type}{props}>{children}</{component_type}>\n);"

    def _get_jsx_element_type(self, component: ComponentDefinition) -> str:
        """Get the appropriate JSX element type for the component."""
        type_mapping = {
            "interactive": "button",
            "form": "div",
            "display": "div",
            "navigation": "nav",
            "layout": "div"
        }
        return type_mapping.get(component.category, "div")

    def _build_class_names(self, component: ComponentDefinition) -> str:
        """Build className string for component."""
        class_names = []

        # Base classes
        base_classes = self._get_base_classes(component)
        if base_classes:
            class_names.append(f"'{base_classes}'")

        # Dynamic classes from variants
        if self.config.library == ComponentLibrary.SHADCN and component.variants:
            class_names.append(f"{component.name.lower()}Variants({{")
            variant_names = [v.name for v in component.variants]
            class_names.append(", ".join(variant_names))
            class_names.append("})")

        # User-provided className
        class_names.append("className")

        # Utility function call
        if self.config.library == ComponentLibrary.SHADCN:
            return f"cn({', '.join(class_names)})"
        else:
            return f"{', '.join(class_names)}.join(' ')"

    def _build_jsx_props(self, component: ComponentDefinition, class_names: str) -> str:
        """Build JSX props string."""
        props = []

        # className
        props.append(f" className={{{class_names}}}")

        # Accessibility props
        if self.config.include_accessibility:
            props.append(" {...ariaProps}")

        # Component-specific props
        for prop in component.properties:
            if prop.name not in ["className", "children"] and prop.type != "array":
                props.append(f" {prop.name}={{{prop.name}}}")

        return "".join(props)

    def _build_jsx_children(self, component: ComponentDefinition) -> str:
        """Build JSX children content."""
        # Handle icon properties
        icon_content = self._build_icon_children(component)

        # Handle text content
        text_content = self._build_text_children(component)

        # Handle children prop
        children_content = "{children}" if any(
            p.name == "children" for p in component.properties) else ""

        return f"{icon_content}{text_content}{children_content}"

    def _build_icon_children(self, component: ComponentDefinition) -> str:
        """Build icon JSX if component has icon properties."""
        icon_props = [p for p in component.properties if p.name in ["icon_left", "icon_right"]]
        if not icon_props:
            return ""

        icons = []
        for prop in icon_props:
            icons.append(
                f"{{{prop.name} && <Icon name={{{prop.name}}} className=\"w-4 h-4\" />}}"
            )

        return " ".join(icons)

    def _build_text_children(self, component: ComponentDefinition) -> str:
        """Build text content JSX."""
        text_props = [p for p in component.properties if p.name == "text"]
        if not text_props:
            return ""

        return "{text}"

    def _generate_interface_file(self, component: ComponentDefinition) -> str:
        """Generate separate TypeScript interface file."""
        interface_name = f"{component.name}Props"

        # Imports
        imports = [
            "import React from 'react';"
        ]

        if self.config.include_accessibility:
            imports.append("import {AriaAttributes} from 'react';")

        # Interface definition
        properties = []
        properties.append("  className?: string;")
        properties.append("  children?: React.ReactNode;")

        for prop in component.properties:
            prop_type = self._map_property_type(prop)
            optional = "" if prop.required else "?"
            default_value = f" = {
                self._format_default_value(prop)}" if prop.default_value is not None else ""
            properties.append(f"  {prop.name}{optional}: {prop_type}{default_value};")

        if self.config.include_accessibility:
            properties.append("  'aria-label'?: string;")
            properties.append("  'aria-labelledby'?: string;")
            properties.append("  'aria-describedby'?: string;")

        interface_content = (
            f"{'\n'.join(imports)}\n\n"
            f"export interface {interface_name} {{\n"
            f"{'\n'.join(properties)}\n"
            f"}}"
        )

        return interface_content

    def _generate_story_file(self, component: ComponentDefinition) -> str:
        """Generate Storybook story file."""
        story_name = component.name

        # Imports
        imports = [
            "import type {Meta, StoryObj} from '@storybook/react';",
            f"import {{component.name}} from './{component.name}';"
        ]

        # Meta configuration
        meta = (
            "const meta: Meta<typeof {story_name}> = {{\n"
            f"  title: 'Components/{component.name}',\n"
            f"  component: {component.name},\n"
            f"  parameters: {{\n"
            "    layout: 'centered',\n"
            " },\n"
            f"  tags: ['autodocs'],\n"
            "  argTypes: {\n"
        )

        # ArgTypes
        arg_types = []
        for prop in component.properties:
            arg_types.append(
                f"    {prop.name}: {{\n"
                f"      description: '{prop.description or ''}',\n"
                f"      control: {self._get_story_control_type(prop)},\n"
                f"   }},"
            )

        meta += "\n".join(arg_types) + "\n },\n};"

        # Default export
        default_export = f"export default meta;\n"

        # Template
        template = (
            f"type Story = StoryObj<typeof {component.name}>;\n\n"
            f"const Template: Story = {{\n"
            f"  args: {{{self._get_default_story_args(component)}}},\n"
            "}};"
        )

        # Stories for variants
        variant_stories = []
        for variant in component.variants:
            story_name_lower = variant.name.lower().replace(' ', '_')
            variant_args = self._get_variant_story_args(variant)
            variant_stories.append(
                f"export const {story_name_lower}: Story = {{\n"
                f"  args: {{{variant_args}}},\n"
                f"  name: '{variant.name}',\n"
                "};"
            )

        return (
            f"{'\n'.join(imports)}\n\n"
            f"{meta}\n\n"
            f"{default_export}\n\n"
            f"{template}\n\n"
            f"{'\n\n'.join(variant_stories)}"
        )

    def _generate_user_stories_file(self, component: ComponentDefinition) -> str:
        """Generate user stories documentation."""
        stories = []

        # Generate 2-3 user stories per component
        user_story_templates = [
            {
                "title": f"As a user, I want to interact with the {component.name}",
                "scenario": f"When I use the {component.name}",
                "acceptance": f"The {component.name} should function correctly with proper styling"
            },
            {
                "title": f"As a developer, I want to customize the {component.name}",
                "scenario": f"When I pass different props to the {component.name}",
                "acceptance": f"The component should render correctly with different configurations"
            },
            {
                "title": f"As an accessibility user, I want the {component.name} to be accessible",
                "scenario": f"When I use assistive technologies with the {component.name}",
                "acceptance": f"The component should have proper ARIA attributes and keyboard navigation"
            }
        ]

        for i, template in enumerate(user_story_templates[:3]):
            story = (
                f"## User Story {i + 1}\n\n"
                f"**Title**: {template['title']}\n\n"
                f"**Scenario**: {template['scenario']}\n\n"
                f"**Acceptance Criteria**:\n"
                f"- {template['acceptance']}\n"
            )

            # Add component-specific acceptance criteria
            if component.properties:
                story += "- All component properties should work as documented\n"

            if component.variants:
                story += "- All component variants should render correctly\n"

            if self.config.include_accessibility:
                story += "- Component should be keyboard accessible\n"
                story += "- Component should have proper ARIA labels\n"

            stories.append(story)

        # Component information header
        header = (
            f"# {component.name} User Stories\n\n"
            f"**Component Category**: {component.category}\n\n"
            f"**Description**: {component.description or 'No description provided'}\n\n"
            f"**Generated**: {datetime.now().isoformat()}\n\n"
            f"---\n\n"
        )

        return header + "\n\n".join(stories)

    def _map_property_type(self, prop: ComponentProperty) -> str:
        """Map component property type to TypeScript type."""
        type_mapping = {
            "string": "string",
            "number": "number",
            "boolean": "boolean",
            "array": "any[]",
            "object": "Record<string, any>",
            "enum": "string"
        }

        base_type = type_mapping.get(prop.type, "any")

        # Handle enum types with allowed values
        if prop.type == "enum" and prop.allowed_values:
            enum_values = " | ".join([f"'{v}'" for v in prop.allowed_values])
            return enum_values

        return base_type

    def _format_default_value(self, prop: ComponentProperty) -> str:
        """Format default value for TypeScript."""
        if prop.default_value is None:
            return "undefined"

        if prop.type == "string":
            return f"'{prop.default_value}'"
        elif prop.type == "boolean":
            return str(prop.default_value).lower()
        elif prop.type == "number":
            return str(prop.default_value)
        elif prop.type == "array":
            return str(prop.default_value) if prop.default_value else "[]"
        elif prop.type == "object":
            return str(prop.default_value) if prop.default_value else "{}"
        else:
            return str(prop.default_value)

    def _get_ref_type(self, component: ComponentDefinition) -> str:
        """Get appropriate ref type for component."""
        if component.category == "interactive":
            return "HTMLButtonElement"
        elif component.category == "form":
            return "HTMLDivElement"
        else:
            return "HTMLDivElement"

    def _has_icon_properties(self, component: ComponentDefinition) -> bool:
        """Check if component has icon-related properties."""
        icon_prop_names = ["icon", "icon_left", "icon_right", "start_icon", "end_icon"]
        return any(prop.name in icon_prop_names for prop in component.properties)

    def _get_base_classes(self, component: ComponentDefinition) -> str:
        """Get base CSS classes for component."""
        # This would be enhanced with design token integration
        base_classes = {
            "interactive": "inline-flex items-center justify-center\n rounded-md text-sm font-medium transition-colors",
            "form": "flex flex-col space-y-1.5",
            "display": "flex flex-col",
            "navigation": "flex items-center space-x-4",
            "layout": "relative"
        }
        return base_classes.get(component.category, "")

    def _get_variant_class(self, component: ComponentDefinition, variant: ComponentVariant) -> str:
        """Get CSS class for a specific variant."""
        # This would be enhanced with design token integration
        if component.category == "interactive":
            variant_classes = {
                "primary": "bg-primary-500 text-white hover:bg-primary-600",
                "secondary": "bg-secondary-500 text-white hover:bg-secondary-600",
                "outline": "border border-primary-500 text-primary-500 hover:bg-primary-50",
                "ghost": "text-primary-500 hover:bg-primary-100",
                "danger": "bg-red-500 text-white hover:bg-red-600"
            }
            return variant_classes.get(variant.name, "")
        return ""

    def _get_story_control_type(self, prop: ComponentProperty) -> str:
        """Get Storybook control type for property."""
        control_mapping = {
            "string": "'text'",
            "number": "'number'",
            "boolean": "'boolean'",
            "array": "'object'",
            "object": "'object'",
            "enum": f"'select'" if prop.allowed_values else "'text'"
        }
        return control_mapping.get(prop.type, "'text'")

    def _get_default_story_args(self, component: ComponentDefinition) -> str:
        """Get default args for Storybook stories."""
        args = []

        for prop in component.properties:
            if prop.default_value is not None:
                args.append(f"{prop.name}: {self._format_default_value(prop)}")
            elif prop.type == "string":
                args.append(f"{prop.name}: 'Sample {prop.name}'")
            elif prop.type == "boolean":
                args.append(f"{prop.name}: false")
            elif prop.type == "number":
                args.append(f"{prop.name}: 0")

        return ", ".join(args)

    def _get_variant_story_args(self, variant: ComponentVariant) -> str:
        """Get args for variant-specific story."""
        args = []

        for prop_name, prop_value in variant.properties.items():
            if isinstance(prop_value, str):
                args.append(f"{prop_name}: '{prop_value}'")
            else:
                args.append(f"{prop_name}: {prop_value}")

        return ", ".join(args)

    def _ensure_output_directories(self) -> None:
        """Ensure all output directories exist."""
        directories = [
            self.config.output_directory,
            self.config.component_directory,
            self.config.stories_directory,
            self.config.user_stories_directory
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _get_component_filename(self, component: ComponentDefinition) -> str:
        """Get filename for component file."""
        ext = "tsx" if self.config.output_format == OutputFormat.TYPESCRIPT else "jsx"
        return f"{component.name}.{ext}"

    def _get_interface_filename(self, component: ComponentDefinition) -> str:
        """Get filename for interface file."""
        return f"{component.name}.props.ts"

    def _get_story_filename(self, component: ComponentDefinition) -> str:
        """Get filename for story file."""
        return f"{component.name}.stories.tsx"

    def _get_user_stories_filename(self, component: ComponentDefinition) -> str:
        """Get filename for user stories file."""
        return f"{component.name}.user-stories.md"

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
                "library": self.config.library.value,
                "output_format": self.config.output_format.value,
                "config": {
                    "include_accessibility": self.config.include_accessibility,
                    "include_responsive": self.config.include_responsive,
                    "include_stories": self.config.include_stories,
                    "include_user_stories": self.config.include_user_stories
                }
            },
            "processing_stats": self.processing_stats,
            "components_summary": {
                "total": len(self.component_catalog.components) if self.component_catalog else 0,
                "by_category": self.processing_stats.get("components_by_category", {})
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
                elif 'export default' not in content and 'export interface' not in content:
                    errors.append(f"Missing export in: {file_path}")

        return len(errors) == 0, errors


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Component Generator - Step 4 of SimFlo Figma-to-RAG Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate components with default settings
  python3 v2/component-generator/main.py \\
    --catalog examples/sample-component-catalog.json \\
    --tokens examples/sample-design-tokens.json \\
    --output ./output/

  # Generate with specific library and formats
  python3 v2/component-generator/main.py \\
    --catalog examples/sample-component-catalog.json \\
    --tokens examples/sample-design-tokens.json \\
    --output ./output/ \\
    --library shadcn \\
    --format typescript \\
    --include-stories \\
    --include-user-stories

  # Generate with custom configuration
  python3 v2/component-generator/main.py \\
    --catalog examples/sample-component-catalog.json \\
    --tokens examples/sample-design-tokens.json \\
    --output ./output/ \\
    --config custom-config.json \\
    --verbose
        """
    )

    # Required arguments
    parser.add_argument(
        '--catalog', '-c',
        required=True,
        help='Path to component catalog JSON file'
    )

    parser.add_argument(
        '--tokens', '-t',
        required=True,
        help='Path to design tokens JSON file'
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for generated files'
    )

    # Optional arguments
    parser.add_argument(
        '--library', '-l',
        choices=['shadcn', 'gluestack'],
        default='shadcn',
        help='Component library to generate for (default: shadcn)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['typescript', 'javascript'],
        default='typescript',
        help='Output format (default: typescript)'
    )

    parser.add_argument(
        '--config',
        help='Path to custom configuration JSON file'
    )

    # Feature flags
    parser.add_argument(
        '--include-stories',
        action='store_true',
        help='Generate Storybook stories'
    )

    parser.add_argument(
        '--include-user-stories',
        action='store_true',
        help='Generate user stories documentation'
    )

    parser.add_argument(
        '--include-accessibility',
        action='store_true',
        default=True,
        help='Include accessibility features (default: True)'
    )

    parser.add_argument(
        '--include-responsive',
        action='store_true',
        default=True,
        help='Include responsive design patterns (default: True)'
    )

    parser.add_argument(
        '--no-stories',
        action='store_true',
        help='Skip generating Storybook stories'
    )

    parser.add_argument(
        '--no-user-stories',
        action='store_true',
        help='Skip generating user stories'
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
        help='Only validate input files, do not generate components'
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
    """Main entry point for component generator."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting Component Generator - Step 4 of SimFlo Figma-to-RAG Pipeline")

    try:
        # Load custom configuration
        config_data = load_config(args.config)

        # Create generation configuration
        config = GenerationConfig(
            library=ComponentLibrary(args.library),
            output_format=OutputFormat(args.format),
            include_accessibility=args.include_accessibility,
            include_responsive=args.include_responsive,
            include_stories=args.include_stories and not args.no_stories,
            include_user_stories=args.include_user_stories and not args.no_user_stories,
            output_directory=args.output,
            component_directory=f"{args.output}/components/",
            stories_directory=f"{args.output}/stories/",
            user_stories_directory=f"{args.output}/user-stories/"
        )

        # Override with custom config if provided
        if config_data:
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Initialize generator
        generator = ComponentGenerator(config)

        # Load and validate inputs
        generator.load_component_catalog(args.catalog)
        generator.load_design_tokens(args.tokens)

        if args.validate_only:
            logger.info("Validation complete - inputs are valid")
            return 0

        # Generate components
        generated_files = generator.generate_components()

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
            metadata_path = Path(args.output) / "component-generation-metadata.json"
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
