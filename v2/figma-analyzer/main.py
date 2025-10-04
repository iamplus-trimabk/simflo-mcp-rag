# -*- coding: utf-8 -*-
"""
Figma Analyzer Step - Step 1 of the SimFlo Figma-to-RAG Pipeline.

This module processes Figma-like data structures to extract design tokens,
component definitions, and screen specifications.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from common.validation import SchemaValidator
from common.schemas import (
    DesignTokenSet, ColorToken, TypographyToken, SpacingToken,
    ShadowToken, BorderRadiusToken, ComponentCatalog, ComponentDefinition,
    ComponentProperty, ComponentVariant, ComponentInstance, ScreenSpecification,
    ScreenSet, LayoutGrid, ResponsiveBreakpoint, NavigationRelationship
)
import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FigmaAnalysisResult:
    """Result of Figma data analysis."""
    design_tokens: DesignTokenSet
    component_catalog: ComponentCatalog
    screen_set: ScreenSet
    metadata: Dict[str, Any]
    processing_time: float
    errors: List[str]
    warnings: List[str]


class FigmaDataParser:
    """Parser for Figma-like data structures."""

    def __init__(self, validator: SchemaValidator):
        """
        Initialize the Figma data parser.

        Args:
            validator: Schema validator instance
        """
        self.validator = validator
        self.processed_nodes = {}
        self.component_lookup = {}
        self.style_lookup = {}

    def parse_figma_data(self, figma_data: Dict[str, Any]) -> FigmaAnalysisResult:
        """
        Parse complete Figma data structure and extract all artifacts.

        Args:
            figma_data: Dictionary containing Figma-like data

        Returns:
            FigmaAnalysisResult with extracted artifacts
        """
        start_time = datetime.now()
        errors = []
        warnings = []

        try:
            logger.info("Starting Figma data analysis...")

            # Extract design tokens
            logger.info("Extracting design tokens...")
            design_tokens = self._extract_design_tokens(figma_data)

            # Extract component catalog
            logger.info("Extracting component catalog...")
            component_catalog = self._extract_component_catalog(figma_data)

            # Extract screen specifications
            logger.info("Extracting screen specifications...")
            screen_set = self._extract_screen_set(figma_data, component_catalog)

            # Create metadata
            metadata = self._create_metadata(figma_data)

            processing_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"Figma analysis completed in {processing_time:.2f} seconds")

            return FigmaAnalysisResult(
                design_tokens=design_tokens,
                component_catalog=component_catalog,
                screen_set=screen_set,
                metadata=metadata,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            error_msg = f"Failed to parse Figma data: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

            processing_time = (datetime.now() - start_time).total_seconds()

            return FigmaAnalysisResult(
                design_tokens=DesignTokenSet(),
                component_catalog=ComponentCatalog(),
                screen_set=ScreenSet(),
                metadata={},
                processing_time=processing_time,
                errors=errors,
                warnings=warnings
            )

    def _extract_design_tokens(self, figma_data: Dict[str, Any]) -> DesignTokenSet:
        """Extract design tokens from Figma JSON (both real and sample formats)."""
        document = figma_data.get('document', {})

        # Check if this is real Figma JSON or sample format
        is_real_figma = self._is_real_figma_format(document)

        colors = []
        typography = []
        spacing = []
        shadows = []
        border_radius = []

        if is_real_figma:
            # Extract from real Figma JSON structure
            colors = self._extract_colors_from_real_figma(document)
            typography = self._extract_typography_from_real_figma(document)
            shadows = self._extract_shadows_from_real_figma(document)
            border_radius = self._extract_border_radius_from_real_figma(document)
            spacing = self._extract_spacing_from_real_figma(document)
            logger.info(f"Extracted from real Figma format: {len(colors)} colors, {len(typography)} typography styles")
        else:
            # Extract from sample format (existing logic)
            styles = document.get('styles', {})

            # Extract color tokens
            if 'colors' in styles:
                for color_style in styles['colors']:
                    try:
                        color_token = self._extract_color_token(color_style)
                        colors.append(color_token)
                    except Exception as e:
                        logger.warning(f"Failed to extract color token: {e}")

            # Extract typography tokens
            if 'text' in styles:
                for text_style in styles['text']:
                    try:
                        typography_token = self._extract_typography_token(text_style)
                        typography.append(typography_token)
                    except Exception as e:
                        logger.warning(f"Failed to extract typography token: {e}")

            # Extract effect tokens (shadows)
            if 'effects' in styles:
                for effect_style in styles['effects']:
                    try:
                        shadow_token = self._extract_shadow_token(effect_style)
                        shadows.append(shadow_token)
                    except Exception as e:
                        logger.warning(f"Failed to extract shadow token: {e}")

            # Extract spacing from layout grids and component properties
            spacing.extend(self._extract_spacing_tokens(figma_data))
            border_radius.extend(self._extract_border_radius_tokens(figma_data))
            logger.info(f"Extracted from sample format: {len(colors)} colors, {len(typography)} typography styles")

        return DesignTokenSet(
            colors=colors,
            typography=typography,
            spacing=spacing,
            shadows=shadows,
            border_radius=border_radius
        )

    def _is_real_figma_format(self, document: Dict[str, Any]) -> bool:
        """Check if the document is real Figma JSON or sample format."""
        # Real Figma JSON has 'children' array, sample format has 'styles' object
        has_children = 'children' in document and isinstance(document['children'], list)
        has_styles = 'styles' in document
        return has_children and not has_styles

    def _extract_colors_from_real_figma(self, document: Dict[str, Any]) -> List[ColorToken]:
        """Extract colors from real Figma JSON by traversing the document tree."""
        colors_map = {}  # color_hex -> ColorToken

        def traverse_node(node: Dict[str, Any], path: str = ""):
            # Extract colors from fills
            for fill in node.get('fills', []):
                if fill.get('type') == 'SOLID':
                    color_data = fill.get('color', {})
                    if color_data:
                        # Convert RGB to hex
                        r = int(color_data.get('r', 0) * 255)
                        g = int(color_data.get('g', 0) * 255)
                        b = int(color_data.get('b', 0) * 255)
                        hex_color = f'#{r:02x}{g:02x}{b:02x}'

                        # Only add unique colors
                        if hex_color not in colors_map:
                            # Create semantic name based on context
                            name = self._create_color_name(node.get('name', 'Color'), hex_color, path)
                            colors_map[hex_color] = ColorToken(
                                name=name,
                                value=hex_color,
                                category=self._categorize_color(hex_color),
                                description=f"Color from {path}/{node.get('name', 'unknown')}"
                            )

            # Recursively traverse children
            for child in node.get('children', []):
                child_path = f"{path}/{node.get('name', 'unknown')}"
                traverse_node(child, child_path)

        traverse_node(document)
        return list(colors_map.values())

    def _create_color_name(self, element_name: str, hex_color: str, path: str) -> str:
        """Create a semantic color name from element name and hex value."""
        # Common color patterns
        color_patterns = {
            '#ffffff': 'White',
            '#000000': 'Black',
            '#ef4444': 'Red',
            '#f59e0b': 'Amber',
            '#10b981': 'Green',
            '#3b82f6': 'Blue',
            '#8b5cf6': 'Purple',
            '#6b7280': 'Gray'
        }

        # Check if it's a common color
        if hex_color.lower() in color_patterns:
            return color_patterns[hex_color.lower()]

        # Generate name based on element context
        element_name = element_name.lower()
        if 'primary' in element_name or 'main' in element_name:
            return 'Primary'
        elif 'secondary' in element_name:
            return 'Secondary'
        elif 'success' in element_name or 'green' in element_name:
            return 'Success'
        elif 'error' in element_name or 'red' in element_name:
            return 'Error'
        elif 'warning' in element_name or 'amber' in element_name:
            return 'Warning'
        elif 'background' in element_name or 'bg' in element_name:
            return 'Background'
        elif 'border' in element_name:
            return 'Border'
        else:
            return element_name.replace(' ', '_').title()

    def _categorize_color(self, hex_color: str) -> str:
        """Categorize a color into semantic groups."""
        hex_color = hex_color.lower()

        # Common semantic colors
        semantic_colors = {
            '#ef4444': 'feedback',    # red - error
            '#f59e0b': 'feedback',    # amber - warning
            '#10b981': 'feedback',    # green - success
            '#3b82f6': 'primary',     # blue - primary
            '#8b5cf6': 'secondary',   # purple - secondary
            '#6b7280': 'neutral',     # gray - neutral
            '#ffffff': 'neutral',     # white
            '#000000': 'neutral',     # black
        }

        # Check for exact match
        if hex_color in semantic_colors:
            return semantic_colors[hex_color]

        # Check brightness and hue for semantic categorization
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000

        # Determine hue
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val

        if delta == 0:
            # Grayscale
            if brightness > 200:
                return 'neutral'  # light gray/white
            else:
                return 'neutral'  # dark gray/black
        elif r > g and r > b:
            # Red hues
            if r > 200:
                return 'feedback'  # bright red - error/alert
            else:
                return 'secondary'  # muted red
        elif g > r and g > b:
            # Green hues
            if g > 150:
                return 'feedback'  # bright green - success
            else:
                return 'secondary'  # muted green
        elif b > r and b > g:
            # Blue hues
            if b > 180:
                return 'primary'  # bright blue - primary
            else:
                return 'secondary'  # muted blue
        else:
            # Other hues (purple, orange, yellow)
            return 'secondary'

    def _extract_typography_from_real_figma(self, document: Dict[str, Any]) -> List[TypographyToken]:
        """Extract typography tokens from real Figma JSON by finding TEXT nodes."""
        typography_map = {}  # style_signature -> TypographyToken

        def traverse_node(node: Dict[str, Any]):
            if node.get('type') == 'TEXT':
                style = node.get('style', {})
                if style:
                    # Create a signature for this text style
                    signature = f"{style.get('fontFamily', '')}-{style.get('fontSize', 0)}-{style.get('fontWeight', 400)}-{style.get('lineHeight', {})}"

                    if signature not in typography_map:
                        # Extract font properties
                        font_family = style.get('fontFamily', 'Inter')
                        font_size = style.get('fontSize', 16)
                        font_weight = style.get('fontWeight', 400)

                        # Handle line height (can be percentage or pixels)
                        line_height = style.get('lineHeight', {})
                        if isinstance(line_height, dict):
                            if line_height.get('unit') == 'PIXELS':
                                line_height_value = line_height.get('value', font_size)
                            elif line_height.get('unit') == 'PERCENT':
                                line_height_value = font_size * (line_height.get('value', 100) / 100)
                            else:
                                line_height_value = font_size
                        else:
                            line_height_value = line_height or font_size

                        # Handle letter spacing (can be object or float)
                        letter_spacing = style.get('letterSpacing', 0)
                        if isinstance(letter_spacing, dict):
                            letter_spacing_value = letter_spacing.get('value', 0)
                        else:
                            letter_spacing_value = letter_spacing or 0

                        # Create semantic name
                        name = self._create_typography_name(node.get('name', 'Text'), font_size, font_weight)

                        typography_map[signature] = TypographyToken(
                            name=name,
                            font_family=font_family,
                            font_size=font_size,
                            font_weight=font_weight,
                            line_height=line_height_value,
                            letter_spacing=letter_spacing_value,
                            category=self._categorize_typography(font_size, font_weight)
                        )

            # Recursively traverse children
            for child in node.get('children', []):
                traverse_node(child)

        traverse_node(document)
        return list(typography_map.values())

    def _create_typography_name(self, element_name: str, font_size: float, font_weight: int) -> str:
        """Create a semantic typography name."""
        element_name = element_name.lower()

        # Size-based naming
        if font_size >= 32:
            size_name = 'Heading'
        elif font_size >= 24:
            size_name = 'Subheading'
        elif font_size >= 18:
            size_name = 'Body Large'
        elif font_size >= 16:
            size_name = 'Body'
        elif font_size >= 14:
            size_name = 'Body Small'
        else:
            size_name = 'Caption'

        # Weight modifier
        if font_weight >= 700:
            weight_name = 'Bold'
        elif font_weight >= 600:
            weight_name = 'Semibold'
        elif font_weight >= 500:
            weight_name = 'Medium'
        else:
            weight_name = 'Regular'

        return f"{size_name} {weight_name}"

    def _categorize_typography(self, font_size: float, font_weight: int) -> str:
        """Categorize typography into usage groups."""
        if font_size >= 24:
            return 'heading'
        elif font_size >= 18:
            return 'heading'  # Changed from 'subheading' to 'heading'
        elif font_weight >= 600:
            return 'label'   # Changed from 'emphasis' to 'label'
        elif font_size <= 12:
            return 'caption'
        else:
            return 'body'

    def _extract_shadows_from_real_figma(self, document: Dict[str, Any]) -> List[ShadowToken]:
        """Extract shadow tokens from real Figma JSON."""
        shadows_map = {}  # shadow_signature -> ShadowToken

        def traverse_node(node: Dict[str, Any]):
            for effect in node.get('effects', []):
                if effect.get('type') == 'DROP_SHADOW':
                    # Create signature for unique shadow
                    offset = effect.get('offset', {})
                    radius = effect.get('radius', 0)
                    color = effect.get('color', {})

                    if color:
                        r = int(color.get('r', 0) * 255)
                        g = int(color.get('g', 0) * 255)
                        b = int(color.get('b', 0) * 255)
                        a = color.get('a', 1.0)
                        hex_color = f'#{r:02x}{g:02x}{b:02x}'

                        signature = f"{offset.get('x', 0)}-{offset.get('y', 0)}-{radius}-{hex_color}-{a}"

                        if signature not in shadows_map:
                            shadows_map[signature] = ShadowToken(
                                name=f"Shadow {len(shadows_map) + 1}",
                                color=hex_color,
                                opacity=a,
                                offset_x=offset.get('x', 0),
                                offset_y=offset.get('y', 0),
                                blur_radius=radius,
                                spread_radius=0,
                                category='drop-shadow'
                            )

            # Recursively traverse children
            for child in node.get('children', []):
                traverse_node(child)

        traverse_node(document)
        return list(shadows_map.values())

    def _extract_border_radius_from_real_figma(self, document: Dict[str, Any]) -> List[BorderRadiusToken]:
        """Extract border radius tokens from real Figma JSON."""
        radius_map = {}  # radius_value -> BorderRadiusToken

        def traverse_node(node: Dict[str, Any]):
            # Check for corner radius
            corner_radius = node.get('cornerRadius')
            if corner_radius and corner_radius > 0:
                if corner_radius not in radius_map:
                    radius_map[corner_radius] = BorderRadiusToken(
                        name=f"Radius {int(corner_radius)}px",
                        value=corner_radius,
                        category='default'
                    )

            # Check for individual corner radii
            top_left = node.get('topLeftRadius')
            if top_left and top_left > 0:
                if top_left not in radius_map:
                    radius_map[top_left] = BorderRadiusToken(
                        name=f"Radius Top {int(top_left)}px",
                        value=top_left,
                        category='corner'
                    )

            # Recursively traverse children
            for child in node.get('children', []):
                traverse_node(child)

        traverse_node(document)
        return list(radius_map.values())

    def _extract_spacing_from_real_figma(self, document: Dict[str, Any]) -> List[SpacingToken]:
        """Extract spacing tokens from layout relationships in real Figma JSON."""
        spacing_set = {8, 16, 24, 32, 48, 64}  # Default spacing scale

        spacing_tokens = []
        for i, spacing in enumerate(sorted(spacing_set)):
            # Alternate between different spacing categories
            categories = ['margin', 'padding', 'gap']
            category = categories[i % len(categories)]

            spacing_tokens.append(SpacingToken(
                name=f"Spacing {i + 1}",
                value=spacing,
                unit='px',
                category=category,
                scale_position=i
            ))

        return spacing_tokens

    def _extract_color_token(self, color_style: Dict[str, Any]) -> ColorToken:
        """Extract a single color token from Figma color style."""
        value = color_style.get('value', '#000000')
        name = color_style.get('name', 'unnamed')
        description = color_style.get('description', '')

        # Determine color category from name
        category = 'semantic'
        if 'primary' in name.lower():
            category = 'primary'
        elif 'secondary' in name.lower():
            category = 'secondary'
        elif 'neutral' in name.lower() or 'gray' in name.lower():
            category = 'neutral'
        elif 'error' in name.lower() or 'red' in name.lower():
            category = 'feedback'

        return ColorToken(
            name=self._normalize_token_name(name),
            value=value,
            category=category,
            description=description
        )

    def _extract_typography_token(self, text_style: Dict[str, Any]) -> TypographyToken:
        """Extract a single typography token from Figma text style."""
        style = text_style.get('style', {})
        name = text_style.get('name', 'unnamed')
        description = text_style.get('description', '')

        # Extract font properties
        font_family = style.get('fontFamily', 'Inter')
        font_size = style.get('fontSize', 16)
        font_weight = style.get('fontWeight', 400)

        # Extract line height
        line_height = style.get('lineHeight', {})
        if isinstance(line_height, dict):
            line_height_value = line_height.get('value', font_size * 1.2)
        else:
            line_height_value = line_height or font_size * 1.2

        # Extract letter spacing
        letter_spacing = style.get('letterSpacing', {})
        if isinstance(letter_spacing, dict):
            letter_spacing_value = letter_spacing.get('value', 0)
        else:
            letter_spacing_value = letter_spacing or 0

        # Determine category from name
        category = 'custom'
        if 'heading' in name.lower():
            category = 'heading'
        elif 'body' in name.lower():
            category = 'body'
        elif 'caption' in name.lower():
            category = 'caption'
        elif 'button' in name.lower():
            category = 'label'

        return TypographyToken(
            name=self._normalize_token_name(name),
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            line_height=line_height_value,
            letter_spacing=letter_spacing_value,
            category=category,
            description=description
        )

    def _extract_shadow_token(self, effect_style: Dict[str, Any]) -> ShadowToken:
        """Extract a single shadow token from Figma effect style."""
        effects = effect_style.get('effects', [])
        name = effect_style.get('name', 'unnamed')
        description = effect_style.get('description', '')

        # Extract first drop shadow effect
        shadow_data = None
        for effect in effects:
            if effect.get('type') == 'DROP_SHADOW':
                shadow_data = effect
                break

        if not shadow_data:
            # Create default shadow
            return ShadowToken(
                name=self._normalize_token_name(name),
                description=description
            )

        color = shadow_data.get('color', {})
        offset = shadow_data.get('offset', {})

        # Convert RGB to hex
        r = int(color.get('r', 0) * 255)
        g = int(color.get('g', 0) * 255)
        b = int(color.get('b', 0) * 255)
        a = color.get('a', 1.0)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        return ShadowToken(
            name=self._normalize_token_name(name),
            offset_x=offset.get('x', 0),
            offset_y=offset.get('y', 4),
            blur=shadow_data.get('radius', 6),
            spread=shadow_data.get('spread', 0),
            color=hex_color,
            opacity=a,
            description=description
        )

    def _extract_spacing_tokens(self, figma_data: Dict[str, Any]) -> List[SpacingToken]:
        """Extract spacing tokens from layout data."""
        spacing_tokens = []

        # Define common spacing scale
        spacing_scale = [
            (4, 'xs'), (8, 'sm'), (16, 'md'), (24, 'lg'),
            (32, 'xl'), (48, '2xl'), (64, '3xl')
        ]

        for value, name in spacing_scale:
            spacing_tokens.append(SpacingToken(
                name=f"spacing-{name}",
                value=value,
                unit="px",
                category="margin",
                scale_position=len(spacing_tokens)
            ))

        return spacing_tokens

    def _extract_border_radius_tokens(self, figma_data: Dict[str, Any]) -> List[BorderRadiusToken]:
        """Extract border radius tokens from components."""
        radius_tokens = []

        # Define common border radius scale
        radius_scale = [
            (0, 'none'), (4, 'sm'), (8, 'md'), (12, 'lg'),
            (16, 'xl'), (9999, 'full')
        ]

        for value, name in radius_scale:
            radius_tokens.append(BorderRadiusToken(
                name=f"radius-{name}",
                value=value,
                unit="px",
                corners="all"
            ))

        return radius_tokens

    def _extract_component_catalog(self, figma_data: Dict[str, Any]) -> ComponentCatalog:
        """Extract component catalog from Figma components (both real and sample formats)."""
        document = figma_data.get('document', {})

        # Check if this is real Figma JSON or sample format
        is_real_figma = self._is_real_figma_format(document)

        components = []
        instances = []

        if is_real_figma:
            # Extract from real Figma JSON structure
            components = self._extract_components_from_real_figma(document)
            instances = self._extract_component_instances_from_real_figma(document)
            logger.info(f"Extracted from real Figma format: {len(components)} components, {len(instances)} instances")
        else:
            # Extract from sample format (existing logic)
            components_data = document.get('components', {})
            main_components = components_data.get('main', [])

            for comp_data in main_components:
                try:
                    # Handle component sets (variants)
                    if comp_data.get('componentType') == 'COMPONENT_SET':
                        component_def = self._extract_component_set(comp_data)
                        components.append(component_def)
                    else:
                        component_def = self._extract_single_component(comp_data)
                        components.append(component_def)
                except Exception as e:
                    logger.warning(f"Failed to extract component: {e}")

            # Extract component instances from screens
            instances = self._extract_component_instances(figma_data)
            logger.info(f"Extracted from sample format: {len(components)} components, {len(instances)} instances")

        # Build component relationships
        relationships = self._build_component_relationships(components, instances)

        return ComponentCatalog(
            components=components,
            instances=instances,
            relationships=relationships
        )

    def _extract_components_from_real_figma(self, document: Dict[str, Any]) -> List[ComponentDefinition]:
        """Extract components from real Figma JSON by finding COMPONENT and COMPONENT_SET nodes."""
        components = []

        def traverse_node(node: Dict[str, Any], path: str = ""):
            node_type = node.get('type')

            if node_type == 'COMPONENT':
                try:
                    component_def = self._extract_component_from_real_node(node, path)
                    components.append(component_def)
                except Exception as e:
                    logger.warning(f"Failed to extract component from {node.get('name', 'unknown')}: {e}")

            elif node_type == 'COMPONENT_SET':
                try:
                    component_set_def = self._extract_component_set_from_real_node(node, path)
                    components.append(component_set_def)
                except Exception as e:
                    logger.warning(f"Failed to extract component set from {node.get('name', 'unknown')}: {e}")

            # Recursively traverse children
            for child in node.get('children', []):
                child_path = f"{path}/{node.get('name', 'unknown')}"
                traverse_node(child, child_path)

        traverse_node(document)
        return components

    def _extract_component_from_real_node(self, node: Dict[str, Any], path: str) -> ComponentDefinition:
        """Extract a single component definition from a real Figma COMPONENT node."""
        name = node.get('name', 'Component')

        # Extract component properties from the node structure
        props = self._extract_component_properties_from_node(node)

        # Determine component category based on name and properties
        category = self._categorize_component(name, node)

        # Extract sizing information
        absolute_bounding_box = node.get('absoluteBoundingBox', {})
        width = absolute_bounding_box.get('width', 0)
        height = absolute_bounding_box.get('height', 0)

        # Extract layout properties
        layout_properties = {
            'autoLayout': node.get('autoLayout', {}),
            'constraints': node.get('constraints', {}),
            'primaryAxisAlignItems': node.get('primaryAxisAlignItems', 'NONE'),
            'counterAxisAlignItems': node.get('counterAxisAlignItems', 'NONE'),
        }

        return ComponentDefinition(
            id=node.get('id', ''),
            name=name,
            category=category,
            description=f"Component extracted from {path}",
            properties=props,
            variants={},
            examples=[],
            layout_properties=layout_properties,
            sizing={
                'width': width,
                'height': height,
                'resizable': 'auto' in layout_properties.get('autoLayout', {})
            }
        )

    def _extract_component_set_from_real_node(self, node: Dict[str, Any], path: str) -> ComponentDefinition:
        """Extract a component set definition from a real Figma COMPONENT_SET node."""
        name = node.get('name', 'Component Set')

        # Extract variants from component set children
        variants = {}
        children = node.get('children', [])

        # Base properties from first variant
        base_props = {}
        layout_properties = {}
        sizing = {'width': 0, 'height': 0, 'resizable': False}

        for child in children:
            if child.get('type') == 'COMPONENT':
                variant_name = child.get('name', 'Variant')
                variant_props = self._extract_component_properties_from_node(child)
                variants[variant_name] = variant_props

                # Use first variant for base properties
                if not base_props:
                    base_props = variant_props
                    absolute_bounding_box = child.get('absoluteBoundingBox', {})
                    sizing = {
                        'width': absolute_bounding_box.get('width', 0),
                        'height': absolute_bounding_box.get('height', 0),
                        'resizable': 'auto' in child.get('autoLayout', {})
                    }
                    layout_properties = {
                        'autoLayout': child.get('autoLayout', {}),
                        'constraints': child.get('constraints', {}),
                        'primaryAxisAlignItems': child.get('primaryAxisAlignItems', 'NONE'),
                        'counterAxisAlignItems': child.get('counterAxisAlignItems', 'NONE'),
                    }

        category = self._categorize_component(name, node)

        return ComponentDefinition(
            id=node.get('id', ''),
            name=name,
            category=category,
            description=f"Component set with {len(variants)} variants extracted from {path}",
            properties=base_props,
            variants=variants,
            examples=[],
            layout_properties=layout_properties,
            sizing=sizing
        )

    def _extract_component_properties_from_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract component properties from a Figma node."""
        props = {}

        # Extract visual properties
        if 'fills' in node:
            props['fills'] = node['fills']

        if 'strokes' in node:
            props['strokes'] = node['strokes']
            props['strokeWeight'] = node.get('strokeWeight', 0)

        if 'cornerRadius' in node:
            props['cornerRadius'] = node['cornerRadius']

        if 'effects' in node:
            props['effects'] = node['effects']

        # Extract text properties if it's a text node
        if node.get('type') == 'TEXT':
            style = node.get('style', {})
            props.update({
                'fontFamily': style.get('fontFamily', 'Inter'),
                'fontSize': style.get('fontSize', 16),
                'fontWeight': style.get('fontWeight', 400),
                'textAlignHorizontal': style.get('textAlignHorizontal', 'LEFT'),
                'textAlignVertical': style.get('textAlignVertical', 'TOP'),
                'characters': node.get('characters', '')
            })

        # Extract auto layout properties
        auto_layout = node.get('autoLayout', {})
        if auto_layout:
            props.update({
                'layoutMode': auto_layout.get('layoutMode', 'NONE'),
                'itemSpacing': auto_layout.get('itemSpacing', 0),
                'paddingLeft': auto_layout.get('paddingLeft', 0),
                'paddingRight': auto_layout.get('paddingRight', 0),
                'paddingTop': auto_layout.get('paddingTop', 0),
                'paddingBottom': auto_layout.get('paddingBottom', 0),
            })

        return props

    def _categorize_component(self, name: str, node: Dict[str, Any]) -> str:
        """Categorize a component based on its name and properties."""
        name_lower = name.lower()
        node_type = node.get('type', '').upper()

        # Check for common button patterns
        if any(keyword in name_lower for keyword in ['button', 'btn', 'submit', 'cancel']):
            return 'interactive'

        # Check for input/form patterns
        elif any(keyword in name_lower for keyword in ['input', 'field', 'textbox', 'textarea', 'select', 'dropdown']):
            return 'form'

        # Check for navigation patterns
        elif any(keyword in name_lower for keyword in ['nav', 'menu', 'tab', 'header', 'sidebar']):
            return 'navigation'

        # Check for card/container patterns
        elif any(keyword in name_lower for keyword in ['card', 'container', 'panel', 'box', 'wrapper']):
            return 'layout'

        # Check for display patterns
        elif any(keyword in name_lower for keyword in ['icon', 'avatar', 'image', 'logo', 'badge']):
            return 'display'

        # Default categorization based on node type
        elif node_type == 'TEXT':
            return 'display'
        elif node_type == 'FRAME':
            return 'layout'
        else:
            return 'layout'  # Default category

    def _extract_component_instances_from_real_figma(self, document: Dict[str, Any]) -> List[ComponentInstance]:
        """Extract component instances from real Figma JSON."""
        instances = []

        def traverse_node(node: Dict[str, Any], screen_name: str = ""):
            # Check if this node is a component instance
            if node.get('type') == 'INSTANCE':
                try:
                    instance = self._extract_instance_from_real_node(node, screen_name)
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Failed to extract instance: {e}")

            # Recursively traverse children
            for child in node.get('children', []):
                child_screen_name = screen_name or node.get('name', 'unknown')
                traverse_node(child, child_screen_name)

        traverse_node(document)
        return instances

    def _extract_instance_from_real_node(self, node: Dict[str, Any], screen_name: str) -> ComponentInstance:
        """Extract a component instance from a real Figma INSTANCE node."""
        component_id = node.get('componentId', '')

        # Extract position and size
        absolute_bounding_box = node.get('absoluteBoundingBox', {})
        x = absolute_bounding_box.get('x', 0)
        y = absolute_bounding_box.get('y', 0)
        width = absolute_bounding_box.get('width', 0)
        height = absolute_bounding_box.get('height', 0)

        # Extract instance properties
        props = self._extract_component_properties_from_node(node)

        return ComponentInstance(
            id=node.get('id', ''),
            component_id=component_id,
            screen_name=screen_name,
            position={'x': x, 'y': y},
            size={'width': width, 'height': height},
            properties=props,
            variant_properties={}  # TODO: Extract variant properties
        )

    def _extract_component_set(self, comp_data: Dict[str, Any]) -> ComponentDefinition:
        """Extract component definition from component set."""
        children = comp_data.get('children', [])
        if not children:
            return self._extract_single_component(comp_data)

        # Use first child as base template
        base_child = children[0]
        component_def = self._extract_single_component(base_child)

        # Extract variants
        variants = []
        for child in children:
            variant_name = child.get('name', 'Default')
            variant = ComponentVariant(
                name=self._normalize_variant_name(variant_name),
                properties=self._extract_component_properties(child),
                description=f"{component_def.description} - {variant_name}"
            )
            variants.append(variant)

        component_def.variants = variants
        return component_def

    def _extract_single_component(self, comp_data: Dict[str, Any]) -> ComponentDefinition:
        """Extract single component definition."""
        comp_id = comp_data.get('id', '')
        name = comp_data.get('name', 'Component')

        # Determine component category
        category = self._determine_component_category(name)

        # Extract properties from component structure
        properties = self._extract_component_properties(comp_data)

        # Create component definition
        return ComponentDefinition(
            id=comp_id,
            name=name,
            type="component",
            category=category,
            description=f"Component: {name}",
            properties=properties,
            figma_node_id=comp_id
        )

    def _extract_component_properties(self, comp_data: Dict[str, Any]) -> List[ComponentProperty]:
        """Extract component properties from component data."""
        properties = []

        # Add common properties based on component type
        name = comp_data.get('name', '').lower()

        if 'button' in name:
            properties.extend([
                ComponentProperty(
                    name="variant",
                    type="string",
                    default_value="primary",
                    required=True,
                    description="Button variant style",
                    allowed_values=["primary", "secondary", "outline"]
                ),
                ComponentProperty(
                    name="size",
                    type="string",
                    default_value="md",
                    required=True,
                    description="Button size",
                    allowed_values=["sm", "md", "lg"]
                ),
                ComponentProperty(
                    name="text",
                    type="string",
                    default_value="Button",
                    required=True,
                    description="Button text content"
                ),
                ComponentProperty(
                    name="disabled",
                    type="boolean",
                    default_value=False,
                    required=False,
                    description="Disable the button"
                )
            ])
        elif 'input' in name or 'field' in name:
            properties.extend([
                ComponentProperty(
                    name="placeholder",
                    type="string",
                    default_value="Enter text...",
                    required=False,
                    description="Input placeholder text"
                ),
                ComponentProperty(
                    name="value",
                    type="string",
                    default_value="",
                    required=False,
                    description="Input value"
                ),
                ComponentProperty(
                    name="type",
                    type="string",
                    default_value="text",
                    required=True,
                    description="Input type",
                    allowed_values=["text", "email", "password", "search"]
                )
            ])
        elif 'card' in name:
            properties.extend([
                ComponentProperty(
                    name="title",
                    type="string",
                    default_value="",
                    required=False,
                    description="Card title"
                ),
                ComponentProperty(
                    name="description",
                    type="string",
                    default_value="",
                    required=False,
                    description="Card description"
                ),
                ComponentProperty(
                    name="priority",
                    type="string",
                    default_value="medium",
                    required=False,
                    description="Priority level",
                    allowed_values=["low", "medium", "high"]
                )
            ])

        return properties

    def _extract_component_instances(self, figma_data: Dict[str, Any]) -> List[ComponentInstance]:
        """Extract component instances from screens."""
        instances = []

        pages = figma_data.get('document', {}).get('pages', [])

        for page in pages:
            page_instances = self._extract_instances_from_page(page)
            instances.extend(page_instances)

        return instances

    def _extract_instances_from_page(self, page: Dict[str, Any]) -> List[ComponentInstance]:
        """Extract component instances from a page."""
        instances = []
        children = page.get('children', [])

        for child in children:
            instances.extend(self._extract_instances_from_node(child))

        return instances

    def _extract_instances_from_node(self, node: Dict[str, Any]) -> List[ComponentInstance]:
        """Extract component instances from a node and its children."""
        instances = []

        if node.get('type') == 'INSTANCE':
            instance = self._create_component_instance(node)
            instances.append(instance)

        # Recursively process children
        children = node.get('children', [])
        for child in children:
            instances.extend(self._extract_instances_from_node(child))

        return instances

    def _create_component_instance(self, node: Dict[str, Any]) -> ComponentInstance:
        """Create a component instance from node data."""
        instance_id = node.get('id', '')
        component_id = node.get('componentId', '')
        name = node.get('name', 'Instance')

        # Extract position and size
        bbox = node.get('absoluteBoundingBox', {})
        position = {'x': bbox.get('x', 0), 'y': bbox.get('y', 0)}
        size = {'width': bbox.get('width', 0), 'height': bbox.get('height', 0)}

        # Extract component properties
        component_properties = node.get('componentProperties', {})

        return ComponentInstance(
            id=instance_id,
            component_id=component_id,
            name=name,
            properties=component_properties,
            position=position,
            size=size
        )

    def _build_component_relationships(
        self, components: List[ComponentDefinition],
        instances: List[ComponentInstance]
    ) -> Dict[str, List[str]]:
        """Build component relationships mapping."""
        relationships = {}

        # Map instances to components
        component_instances = {}
        for instance in instances:
            comp_id = instance.component_id
            if comp_id not in component_instances:
                component_instances[comp_id] = []
            component_instances[comp_id].append(instance.id)

        # Create relationships
        for component in components:
            relationships[component.id] = component_instances.get(component.id, [])

        return relationships

    def _extract_screen_set(
        self, figma_data: Dict[str, Any],
        component_catalog: ComponentCatalog
    ) -> ScreenSet:
        """Extract screen specifications from Figma pages (both real and sample formats)."""
        document = figma_data.get('document', {})

        # Check if this is real Figma JSON or sample format
        is_real_figma = self._is_real_figma_format(document)

        screens = []

        if is_real_figma:
            # Extract from real Figma JSON structure
            screens = self._extract_screens_from_real_figma(document, component_catalog)
            logger.info(f"Extracted from real Figma format: {len(screens)} screens")
        else:
            # Extract from sample format (existing logic)
            pages = document.get('pages', [])
            for page in pages:
                page_screens = self._extract_screens_from_page(page, component_catalog)
                screens.extend(page_screens)
            logger.info(f"Extracted from sample format: {len(screens)} screens")

        # Build navigation graph from prototype flows
        navigation_graph = self._build_navigation_graph(figma_data, screens)

        # Determine entry point
        entry_point = screens[0].id if screens else None

        return ScreenSet(
            screens=screens,
            navigation_graph=navigation_graph,
            entry_point=entry_point
        )

    def _extract_screens_from_real_figma(self, document: Dict[str, Any], component_catalog: ComponentCatalog) -> List[ScreenSpecification]:
        """Extract screens from real Figma JSON by finding CANVAS and FRAME nodes."""
        screens = []

        def traverse_node(node: Dict[str, Any], level: int = 0):
            node_type = node.get('type', '').upper()
            name = node.get('name', 'Unknown')

            # Check if this node could be a screen
            if node_type in ['CANVAS', 'FRAME'] and level == 1:  # Top-level frames/canvases
                try:
                    screen = self._extract_screen_from_real_node(node, component_catalog)
                    screens.append(screen)
                except Exception as e:
                    logger.warning(f"Failed to extract screen from {name}: {e}")

            # Recursively traverse children
            for child in node.get('children', []):
                traverse_node(child, level + 1)

        traverse_node(document)
        return screens

    def _extract_screen_from_real_node(self, node: Dict[str, Any], component_catalog: ComponentCatalog) -> ScreenSpecification:
        """Extract a screen specification from a real Figma CANVAS or FRAME node."""
        name = node.get('name', 'Screen')
        node_type = node.get('type', '').upper()

        # Extract layout information
        absolute_bounding_box = node.get('absoluteBoundingBox', {})
        width = absolute_bounding_box.get('width', 0)
        height = absolute_bounding_box.get('height', 0)

        # Determine screen type based on dimensions
        screen_type = self._determine_screen_type(width, height)

        # Extract layout grid
        layout_grid = self._extract_layout_grid_from_node(node)

        # Extract component instances from this screen
        component_instances = self._extract_component_instances_from_screen(node, component_catalog)

        # Extract responsive breakpoints
        responsive_breakpoints = self._extract_responsive_breakpoints(node)

        # Extract navigation patterns
        navigation_patterns = self._extract_navigation_patterns_from_screen(node)

        return ScreenSpecification(
            id=node.get('id', ''),
            name=name,
            type=screen_type,
            layout_grid=layout_grid,
            responsive_breakpoints=responsive_breakpoints,
            component_instances=component_instances,
            navigation_patterns=navigation_patterns,
            metadata={
                'node_type': node_type,
                'width': width,
                'height': height,
                'background_color': self._extract_background_color(node)
            }
        )

    def _determine_screen_type(self, width: int, height: int) -> str:
        """Determine screen type based on dimensions."""
        if width <= 450:
            return 'mobile_app'
        elif width <= 1200:
            return 'web_page'
        else:
            return 'desktop_app'

    def _extract_layout_grid_from_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract layout grid information from a Figma node."""
        # Default grid system
        default_grid = {
            'columns': 12,
            'gutter': 16,
            'margin': 24,
            'max_width': 1200,
            'type': 'responsive'
        }

        # Check for explicit grid settings
        layout_grid = node.get('layoutGrids', [])
        if layout_grid:
            # Use first grid if available
            grid = layout_grid[0]
            return {
                'columns': grid.get('count', default_grid['columns']),
                'gutter': grid.get('gutterSize', default_grid['gutter']),
                'margin': default_grid['margin'],  # Not explicitly stored in Figma
                'max_width': default_grid['max_width'],
                'type': 'explicit',
                'pattern': grid.get('pattern', 'GRID')
            }

        return default_grid

    def _extract_component_instances_from_screen(self, screen_node: Dict[str, Any], component_catalog: ComponentCatalog) -> List[Dict[str, Any]]:
        """Extract component instances that appear on a screen."""
        instances = []

        def traverse_node(node: Dict[str, Any]):
            if node.get('type') == 'INSTANCE':
                # Extract instance information
                component_id = node.get('componentId', '')
                component_name = node.get('name', 'Instance')

                # Find matching component in catalog
                matching_component = None
                for comp in component_catalog.components:
                    if comp.id == component_id or comp.name == component_name:
                        matching_component = comp
                        break

                # Extract position and size
                absolute_bounding_box = node.get('absoluteBoundingBox', {})

                instance_info = {
                    'id': node.get('id', ''),
                    'component_id': component_id,
                    'component_name': component_name,
                    'category': matching_component.category if matching_component else 'unknown',
                    'position': {
                        'x': absolute_bounding_box.get('x', 0),
                        'y': absolute_bounding_box.get('y', 0)
                    },
                    'size': {
                        'width': absolute_bounding_box.get('width', 0),
                        'height': absolute_bounding_box.get('height', 0)
                    },
                    'properties': self._extract_component_properties_from_node(node)
                }
                instances.append(instance_info)

            # Recursively traverse children
            for child in node.get('children', []):
                traverse_node(child)

        traverse_node(screen_node)
        return instances

    def _extract_responsive_breakpoints(self, node: Dict[str, Any]) -> Dict[str, int]:
        """Extract responsive breakpoints for the screen."""
        # Standard breakpoints based on screen width
        width = node.get('absoluteBoundingBox', {}).get('width', 1200)

        if width <= 450:
            return {
                'mobile': width,
                'tablet': 768,
                'desktop': 1024
            }
        elif width <= 768:
            return {
                'mobile': 375,
                'tablet': width,
                'desktop': 1024
            }
        elif width <= 1024:
            return {
                'mobile': 375,
                'tablet': 768,
                'desktop': width
            }
        else:
            return {
                'mobile': 375,
                'tablet': 768,
                'desktop': width
            }

    def _extract_navigation_patterns_from_screen(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract navigation patterns from screen elements."""
        patterns = []

        # Look for common navigation elements
        def find_navigation_elements(node: Dict[str, Any], path: str = ""):
            name = node.get('name', '').lower()
            node_type = node.get('type', '').upper()

            # Check for navigation elements
            if any(keyword in name for keyword in ['nav', 'menu', 'tab', 'header', 'sidebar', 'button']):
                element_info = {
                    'type': 'navigation_element',
                    'name': node.get('name', 'Navigation'),
                    'node_type': node_type,
                    'path': path,
                    'position': node.get('absoluteBoundingBox', {}),
                    'potential_action': self._infer_action_from_name(name)
                }
                patterns.append(element_info)

            # Recursively check children
            for child in node.get('children', []):
                find_navigation_elements(child, f"{path}/{node.get('name', 'unknown')}")

        find_navigation_elements(node)
        return patterns

    def _infer_action_from_name(self, name: str) -> str:
        """Infer potential action from element name."""
        name_lower = name.lower()

        if any(keyword in name_lower for keyword in ['back', 'previous']):
            return 'navigate_back'
        elif any(keyword in name_lower for keyword in ['next', 'forward', 'continue']):
            return 'navigate_forward'
        elif any(keyword in name_lower for keyword in ['submit', 'save', 'confirm']):
            return 'submit_form'
        elif any(keyword in name_lower for keyword in ['cancel', 'close', 'dismiss']):
            return 'cancel_action'
        elif any(keyword in name_lower for keyword in ['login', 'signin']):
            return 'login'
        elif any(keyword in name_lower for keyword in ['logout', 'signout']):
            return 'logout'
        elif any(keyword in name_lower for keyword in ['menu', 'hamburger']):
            return 'toggle_menu'
        else:
            return 'unknown_action'

    def _extract_background_color(self, node: Dict[str, Any]) -> str:
        """Extract background color from a node."""
        for fill in node.get('fills', []):
            if fill.get('type') == 'SOLID':
                color_data = fill.get('color', {})
                if color_data:
                    r = int(color_data.get('r', 0) * 255)
                    g = int(color_data.get('g', 0) * 255)
                    b = int(color_data.get('b', 0) * 255)
                    return f'#{r:02x}{g:02x}{b:02x}'
        return '#ffffff'  # Default white background

    def _extract_screens_from_page(
        self, page: Dict[str, Any],
        component_catalog: ComponentCatalog
    ) -> List[ScreenSpecification]:
        """Extract screen specifications from a page."""
        screens = []
        children = page.get('children', [])

        for child in children:
            if child.get('type') == 'FRAME':
                screen = self._create_screen_specification(child, component_catalog)
                screens.append(screen)

        return screens

    def _create_screen_specification(
        self, frame_data: Dict[str, Any],
        component_catalog: ComponentCatalog
    ) -> ScreenSpecification:
        """Create screen specification from frame data."""
        frame_id = frame_data.get('id', '')
        name = frame_data.get('name', 'Screen')

        # Determine screen type
        bbox = frame_data.get('absoluteBoundingBox', {})
        width = bbox.get('width', 0)

        screen_type = 'web_page'
        if width <= 450:
            screen_type = 'mobile_app'
        elif width >= 1200:
            screen_type = 'desktop_app'

        # Extract background color
        bg_color = frame_data.get('backgroundColor', {})
        if bg_color:
            r = int(bg_color.get('r', 1) * 255)
            g = int(bg_color.get('g', 1) * 255)
            b = int(bg_color.get('b', 1) * 255)
            background_color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            background_color = "#FFFFFF"

        # Create layout grid
        layout_grid = LayoutGrid(
            type="columns",
            columns=12,
            gutter_width=16,
            margin=24,
            max_width=1200
        )

        # Create responsive breakpoints
        breakpoints = [
            ResponsiveBreakpoint(name="mobile", max_width=767, description="Mobile devices"),
            ResponsiveBreakpoint(name="tablet", min_width=768, max_width=1023,
                                 description="Tablet devices"),
            ResponsiveBreakpoint(name="desktop", min_width=1024, description="Desktop devices")
        ]

        # Extract component instances from frame
        component_instances = self._extract_instances_from_node(frame_data)

        # Extract navigation flows
        navigation_flows = self._extract_navigation_flows(frame_data)

        return ScreenSpecification(
            id=frame_id,
            name=name,
            type=screen_type,
            layout_grid=layout_grid,
            breakpoints=breakpoints,
            component_instances=component_instances,
            navigation_flows=navigation_flows,
            figma_frame_id=frame_id,
            background_color=background_color
        )

    def _extract_navigation_flows(self, frame_data: Dict[str, Any]) -> List[NavigationRelationship]:
        """Extract navigation relationships from frame data."""
        # This is a simplified implementation
        # In a real scenario, this would parse prototype flow data
        flows = []

        # Look for common navigation patterns
        children = frame_data.get('children', [])
        for child in children:
            if 'navigation' in child.get('name', '').lower():
                # Create navigation relationship
                flows.append(NavigationRelationship(
                    from_screen_id=frame_data.get('id', ''),
                    to_screen_id="unknown",  # Would be determined from prototype data
                    trigger="click",
                    trigger_element_id=child.get('id', ''),
                    animation_type="slide_right"
                ))

        return flows

    def _build_navigation_graph(
        self, figma_data: Dict[str, Any],
        screens: List[ScreenSpecification]
    ) -> Dict[str, List[str]]:
        """Build navigation graph from prototype flows."""
        prototype = figma_data.get('document', {}).get('prototype', {})
        flows = prototype.get('flows', [])

        navigation_graph = {}
        screen_ids = {screen.id for screen in screens}

        for flow in flows:
            edges = flow.get('edges', [])
            for edge in edges:
                from_id = edge.get('nodeId', '')
                to_id = edge.get('toNodeId', '')

                if from_id in screen_ids and to_id in screen_ids:
                    if from_id not in navigation_graph:
                        navigation_graph[from_id] = []
                    navigation_graph[from_id].append(to_id)

        return navigation_graph

    def _create_metadata(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata from Figma data."""
        document = figma_data.get('document', {})
        metadata = figma_data.get('metadata', {})

        return {
            'figma_file_id': metadata.get('fileId', ''),
            'figma_file_name': metadata.get('name', ''),
            'last_modified': metadata.get('lastModified', ''),
            'document_version': document.get('version', 1),
            'total_components': len(document.get('components', {}).get('main', [])),
            'total_pages': len(document.get('pages', [])),
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _normalize_token_name(self, name: str) -> str:
        """Normalize token name to standard format."""
        return name.lower().replace('/', '-').replace('_', '-').replace(' ', '-')

    def _normalize_variant_name(self, name: str) -> str:
        """Normalize variant name to standard format."""
        return name.lower().replace(' ', '-').replace('_', '-')

    def _determine_component_category(self, name: str) -> str:
        """Determine component category from name."""
        name_lower = name.lower()

        if any(word in name_lower for word in ['button', 'btn']):
            return 'interactive'
        elif any(word in name_lower for word in ['input', 'field', 'form']):
            return 'form'
        elif any(word in name_lower for word in ['card', 'container', 'panel']):
            return 'layout'
        elif any(word in name_lower for word in ['nav', 'menu', 'tab']):
            return 'navigation'
        elif any(word in name_lower for word in ['icon', 'avatar', 'image']):
            return 'display'
        else:
            return 'interactive'


class FigmaAnalyzer:
    """Main Figma analyzer class."""

    def __init__(self, strict_validation: bool = False):
        """
        Initialize Figma analyzer.

        Args:
            strict_validation: Whether to use strict validation mode
        """
        self.validator = SchemaValidator(strict_mode=strict_validation)
        self.parser = FigmaDataParser(self.validator)

    def analyze_figma_file(self, input_path: Path, output_dir: Path) -> FigmaAnalysisResult:
        """
        Analyze Figma file and generate pipeline artifacts.

        Args:
            input_path: Path to input Figma JSON file
            output_dir: Output directory for generated files

        Returns:
            FigmaAnalysisResult with analysis results

        Raises:
            FileNotFoundError: If input file doesn't exist
            CustomValidationError: If validation fails
        """
        logger.info(f"Analyzing Figma file: {input_path}")

        # Validate input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load and validate Figma data
        with open(input_path, 'r', encoding='utf-8') as f:
            figma_data = json.load(f)

        # Parse Figma data
        result = self.parser.parse_figma_data(figma_data)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save results
        self._save_results(result, output_dir)

        # Validate outputs
        self._validate_outputs(output_dir)

        logger.info(f"Figma analysis completed. Results saved to: {output_dir}")

        return result

    def _save_results(self, result: FigmaAnalysisResult, output_dir: Path) -> None:
        """Save analysis results to files."""
        # Save design tokens
        design_tokens_path = output_dir / "design-tokens.json"
        result.design_tokens.to_json_file(design_tokens_path)
        logger.info(f"Saved design tokens: {design_tokens_path}")

        # Save component catalog
        component_catalog_path = output_dir / "component-catalog.json"
        result.component_catalog.to_json_file(component_catalog_path)
        logger.info(f"Saved component catalog: {component_catalog_path}")

        # Save screen specifications
        screens_dir = output_dir / "screen-specs"
        screens_dir.mkdir(exist_ok=True)

        for screen in result.screen_set.screens:
            screen_path = screens_dir / f"{screen.id}.json"
            screen.to_json_file(screen_path)

        # Save complete screen set
        screen_set_path = output_dir / "screen-set.json"
        result.screen_set.to_json_file(screen_set_path)
        logger.info(f"Saved screen specifications: {screens_dir}")

        # Save analysis metadata
        metadata_path = output_dir / "analysis-metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': result.metadata,
                'processing_time': result.processing_time,
                'errors': result.errors,
                'warnings': result.warnings,
                'summary': {
                    'total_design_tokens': len(result.design_tokens.colors) +
                    len(result.design_tokens.typography) +
                    len(result.design_tokens.spacing) +
                    len(result.design_tokens.shadows) +
                    len(result.design_tokens.border_radius),
                    'total_components': len(result.component_catalog.components),
                    'total_instances': len(result.component_catalog.instances),
                    'total_screens': len(result.screen_set.screens)
                }
            }, f, indent=2, default=str)

        logger.info(f"Saved analysis metadata: {metadata_path}")

    def _validate_outputs(self, output_dir: Path) -> None:
        """Validate generated output files."""
        logger.info("Validating generated outputs...")

        # Validate design tokens
        design_tokens_path = output_dir / "design-tokens.json"
        if design_tokens_path.exists():
            self.validator.load_and_validate(design_tokens_path, DesignTokenSet)

        # Validate component catalog
        component_catalog_path = output_dir / "component-catalog.json"
        if component_catalog_path.exists():
            self.validator.load_and_validate(component_catalog_path, ComponentCatalog)

        # Validate screen set
        screen_set_path = output_dir / "screen-set.json"
        if screen_set_path.exists():
            self.validator.load_and_validate(screen_set_path, ScreenSet)

        logger.info("Output validation completed successfully")


def main():
    """Command line interface for Figma analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze Figma data and extract design artifacts"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to input Figma JSON file"
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation mode"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create analyzer
        analyzer = FigmaAnalyzer(strict_validation=args.strict)

        # Analyze Figma file
        result = analyzer.analyze_figma_file(args.input, args.output)

        # Print summary
        print("\n[SUCCESS] Figma Analysis Complete!")
        print(f"[OUTPUT] Output directory: {args.output}")
        print(f"[TIME] Processing time: {result.processing_time:.2f} seconds")

        if result.design_tokens.colors:
            token_msg = (
                f"[TOKENS] Design tokens: {len(result.design_tokens.colors)} colors, "
                f"{len(result.design_tokens.typography)} typography styles"
            )
            print(token_msg)
        if result.component_catalog.components:
            comp_msg = (
                f"[COMPONENTS] Components: {len(result.component_catalog.components)} definitions, "
                f"{len(result.component_catalog.instances)} instances"
            )
            print(comp_msg)
        if result.screen_set.screens:
            print(f"[SCREENS] Screens: {len(result.screen_set.screens)} screen specifications")

        if result.warnings:
            print(f"[WARNINGS] Warnings: {len(result.warnings)}")
            for warning in result.warnings[:3]:  # Show first 3 warnings
                print(f"   - {warning}")

        if result.errors:
            print(f"[ERRORS] Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"   - {error}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"[ERROR] Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
