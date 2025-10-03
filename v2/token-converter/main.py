#!/usr/bin/env python3
"""
Token Converter - Step 3 of SimFlo Figma-to-RAG Pipeline

Converts design tokens from figma-analyzer output to framework-specific definitions
including Tailwind CSS, NativeWind, CSS custom properties, SCSS variables, and JavaScript objects.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from common.schemas import DesignTokenSet
from common.validation import validate_and_load, CustomValidationError
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TokenConverter:
    """
    Converts design tokens to various framework-specific formats.

    Supports:
    - Tailwind CSS configuration
    - NativeWind configuration (React Native)
    - CSS custom properties
    - SCSS variables
    - JavaScript objects
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize token converter with configuration."""
        self.config = config or {}
        self.design_tokens: Optional[DesignTokenSet] = None
        self.processing_stats = {
            "colors_processed": 0,
            "typography_processed": 0,
            "spacing_processed": 0,
            "shadows_processed": 0,
            "border_radius_processed": 0,
            "total_tokens": 0,
            "frameworks_generated": []
        }

    def load_design_tokens(self, input_path: str) -> None:
        """
        Load and validate design tokens from JSON file.

        Args:
            input_path: Path to design tokens JSON file

        Raises:
            CustomValidationError: If tokens are invalid
        """
        logger.info(f"Loading design tokens from: {input_path}")

        try:
            # Validate and load tokens against schema
            self.design_tokens = validate_and_load(Path(input_path), DesignTokenSet)

            # Update processing stats
            self.processing_stats.update({
                "colors_processed": len(self.design_tokens.colors),
                "typography_processed": len(self.design_tokens.typography),
                "spacing_processed": len(self.design_tokens.spacing),
                "shadows_processed": len(self.design_tokens.shadows),
                "border_radius_processed": len(self.design_tokens.border_radius),
                "total_tokens": (
                    len(self.design_tokens.colors) +
                    len(self.design_tokens.typography) +
                    len(self.design_tokens.spacing) +
                    len(self.design_tokens.shadows) +
                    len(self.design_tokens.border_radius)
                )
            })

            logger.info(
                f"Successfully loaded {self.processing_stats['total_tokens']} design tokens")

        except FileNotFoundError:
            raise CustomValidationError(f"Design tokens file not found: {input_path}")
        except json.JSONDecodeError as e:
            raise CustomValidationError(f"Invalid JSON in design tokens file: {e}")

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def hex_to_rgba(self, hex_color: str, opacity: float = 1.0) -> str:
        """Convert hex color and opacity to RGBA string."""
        r, g, b = self.hex_to_rgb(hex_color)
        return f"rgba({r}, {g}, {b}, {opacity})"

    def generate_css_variable_name(self, token_name: str, category: str = "") -> str:
        """Generate CSS variable name from token name."""
        # Remove common prefixes and clean up name
        clean_name = token_name.replace('-', '--').replace('_', '--')
        if category and not token_name.startswith(category):
            clean_name = f"--{category}-{clean_name.lstrip('-')}"
        return clean_name

    def generate_tailwind_colors(self) -> Dict[str, Any]:
        """Generate Tailwind CSS color configuration from color tokens."""
        if not self.design_tokens:
            return {}

        colors = {}
        color_groups = {}

        # Group colors by category (primary, secondary, etc.)
        for color_token in self.design_tokens.colors:
            category = color_token.category

            if category not in color_groups:
                color_groups[category] = {}

            # Extract shade number from name (e.g., "primary-500" -> "500")
            name_parts = color_token.name.split('-')
            if len(name_parts) >= 2 and name_parts[-1].isdigit():
                shade = name_parts[-1]
                color_groups[category][shade] = color_token.value
            else:
                # Handle named colors (white, black, etc.)
                color_groups[category][color_token.name] = color_token.value

            # Add variants if present
            for variant_name, variant_value in color_token.variants.items():
                if category not in colors:
                    colors[category] = {}
                colors[category][variant_name] = variant_value

        # Merge structured colors with variants
        for category, shades in color_groups.items():
            if category not in colors:
                colors[category] = {}
            colors[category].update(shades)

        return colors

    def generate_tailwind_spacing(self) -> Dict[str, Any]:
        """Generate Tailwind CSS spacing configuration from spacing tokens."""
        if not self.design_tokens:
            return {}

        spacing = {}

        for spacing_token in self.design_tokens.spacing:
            # Convert to rem unit (assuming 16px = 1rem)
            if spacing_token.unit == "px":
                value_in_rem = spacing_token.value / 16
                spacing[spacing_token.name] = f"{value_in_rem}rem"
            else:
                spacing[spacing_token.name] = f"{spacing_token.value}{spacing_token.unit}"

        return spacing

    def generate_tailwind_fonts(self) -> Dict[str, Any]:
        """Generate Tailwind CSS font family configuration from typography tokens."""
        if not self.design_tokens:
            return {}

        font_families = {}
        font_sizes = {}
        font_weights = {}
        line_heights = {}
        letter_spacing = {}

        for typo_token in self.design_tokens.typography:
            # Font families
            if typo_token.font_family not in font_families:
                font_families[typo_token.font_family] = [typo_token.font_family]

            # Font sizes
            font_sizes[typo_token.name] = [
                f"{typo_token.font_size}px",
                {
                    "lineHeight": typo_token.line_height,
                    "letterSpacing": f"{typo_token.letter_spacing}px"
                }
            ]

            # Font weights
            weight_name = typo_token.name.replace('-', '')
            if typo_token.font_weight not in font_weights.values():
                font_weights[weight_name] = typo_token.font_weight

            # Line heights
            line_heights[typo_token.name] = typo_token.line_height

            # Letter spacing
            if typo_token.letter_spacing != 0:
                letter_spacing[typo_token.name] = f"{typo_token.letter_spacing}px"

        return {
            "fontFamily": font_families,
            "fontSize": font_sizes,
            "fontWeight": font_weights,
            "lineHeight": line_heights,
            "letterSpacing": letter_spacing
        }

    def generate_tailwind_config(self) -> Dict[str, Any]:
        """Generate complete Tailwind CSS configuration."""
        if not self.design_tokens:
            return {}

        config = {
            "content": [
                "./src/**/*.{js,jsx,ts,tsx}",
                "./app/**/*.{js,jsx,ts,tsx}",
                "./pages/**/*.{js,jsx,ts,tsx}",
                "./components/**/*.{js,jsx,ts,tsx}"
            ],
            "theme": {
                "extend": {}
            },
            "plugins": []
        }

        # Add colors
        colors = self.generate_tailwind_colors()
        if colors:
            config["theme"]["extend"]["colors"] = colors

        # Add spacing
        spacing = self.generate_tailwind_spacing()
        if spacing:
            config["theme"]["extend"]["spacing"] = spacing

        # Add typography
        fonts = self.generate_tailwind_fonts()
        if fonts:
            config["theme"]["extend"].update(fonts)

        # Add shadows
        if self.design_tokens.shadows:
            shadows = {}
            for shadow in self.design_tokens.shadows:
                shadows[shadow.name] = f"{shadow.offset_x}px {shadow.offset_y}px {shadow.blur}px {shadow.spread}px {shadow.color}"
            config["theme"]["extend"]["boxShadow"] = shadows

        # Add border radius
        if self.design_tokens.border_radius:
            border_radius = {}
            for radius in self.design_tokens.border_radius:
                border_radius[radius.name] = f"{radius.value}{radius.unit}"
            config["theme"]["extend"]["borderRadius"] = border_radius

        return config

    def generate_css_variables(self) -> str:
        """Generate CSS custom properties from all design tokens."""
        if not self.design_tokens:
            return ""

        css_vars = []
        css_vars.append(":root {")

        # Color variables
        for color_token in self.design_tokens.colors:
            var_name = self.generate_css_variable_name(color_token.name, "color")
            css_vars.append(f"  {var_name}: {color_token.value};")

            # Add variants
            for variant_name, variant_value in color_token.variants.items():
                variant_var_name = self.generate_css_variable_name(
                    f"{color_token.name}-{variant_name}", "color")
                css_vars.append(f"  {variant_var_name}: {variant_value};")

        # Typography variables
        for typo_token in self.design_tokens.typography:
            font_var_name = self.generate_css_variable_name(typo_token.name, "font")
            css_vars.append(f"  {font_var_name}-family: '{typo_token.font_family}';")
            css_vars.append(f"  {font_var_name}-size: {typo_token.font_size}px;")
            css_vars.append(f"  {font_var_name}-weight: {typo_token.font_weight};")
            css_vars.append(f"  {font_var_name}-line-height: {typo_token.line_height};")
            css_vars.append(f"  {font_var_name}-letter-spacing: {typo_token.letter_spacing}px;")

        # Spacing variables
        for spacing_token in self.design_tokens.spacing:
            spacing_var_name = self.generate_css_variable_name(spacing_token.name, "spacing")
            css_vars.append(f"  {spacing_var_name}: {spacing_token.value}{spacing_token.unit};")

        # Shadow variables
        for shadow_token in self.design_tokens.shadows:
            shadow_var_name = self.generate_css_variable_name(shadow_token.name, "shadow")
            shadow_value = f"{shadow_token.offset_x}px {shadow_token.offset_y}px {shadow_token.blur}px {shadow_token.spread}px {shadow_token.color}"
            css_vars.append(f"  {shadow_var_name}: {shadow_value};")

        # Border radius variables
        for radius_token in self.design_tokens.border_radius:
            radius_var_name = self.generate_css_variable_name(radius_token.name, "radius")
            css_vars.append(f"  {radius_var_name}: {radius_token.value}{radius_token.unit};")

        css_vars.append("}")
        css_vars.append("")

        return "\n".join(css_vars)

    def generate_scss_variables(self) -> str:
        """Generate SCSS variables from all design tokens."""
        if not self.design_tokens:
            return ""

        scss_vars = []
        scss_vars.append("// Design System Variables")
        scss_vars.append("// Generated by SimFlo Token Converter")
        scss_vars.append("")

        # Color variables
        scss_vars.append("// Colors")
        for color_token in self.design_tokens.colors:
            var_name = f"${color_token.name.replace('-', '-')}"
            scss_vars.append(f"{var_name}: {color_token.value};")

            # Add variants
            for variant_name, variant_value in color_token.variants.items():
                variant_var_name = f"${color_token.name}-{variant_name}"
                scss_vars.append(f"{variant_var_name}: {variant_value};")

        scss_vars.append("")

        # Typography variables
        scss_vars.append("// Typography")
        for typo_token in self.design_tokens.typography:
            font_var_name = f"${typo_token.name.replace('-', '-')}"
            scss_vars.append(f"{font_var_name}-font-family: '{typo_token.font_family}';")
            scss_vars.append(f"{font_var_name}-font-size: {typo_token.font_size}px;")
            scss_vars.append(f"{font_var_name}-font-weight: {typo_token.font_weight};")
            scss_vars.append(f"{font_var_name}-line-height: {typo_token.line_height};")
            scss_vars.append(f"{font_var_name}-letter-spacing: {typo_token.letter_spacing}px;")

        scss_vars.append("")

        # Spacing variables
        scss_vars.append("// Spacing")
        for spacing_token in self.design_tokens.spacing:
            spacing_var_name = f"${spacing_token.name.replace('-', '-')}"
            scss_vars.append(f"{spacing_var_name}: {spacing_token.value}{spacing_token.unit};")

        scss_vars.append("")

        # Shadow variables
        scss_vars.append("// Shadows")
        for shadow_token in self.design_tokens.shadows:
            shadow_var_name = f"${shadow_token.name.replace('-', '-')}"
            shadow_value = f"{shadow_token.offset_x}px {shadow_token.offset_y}px {shadow_token.blur}px {shadow_token.spread}px {shadow_token.color}"
            scss_vars.append(f"{shadow_var_name}: {shadow_value};")

        scss_vars.append("")

        # Border radius variables
        scss_vars.append("// Border Radius")
        for radius_token in self.design_tokens.border_radius:
            radius_var_name = f"${radius_token.name.replace('-', '-')}"
            scss_vars.append(f"{radius_var_name}: {radius_token.value}{radius_token.unit};")

        return "\n".join(scss_vars)

    def generate_nativewind_config(self) -> Dict[str, Any]:
        """Generate NativeWind configuration for React Native."""
        if not self.design_tokens:
            return {}

        config = {
            "theme": {
                "extend": {}
            },
            "plugins": []
        }

        # Colors for NativeWind
        colors = self.generate_tailwind_colors()
        if colors:
            config["theme"]["extend"]["colors"] = colors

        # Spacing for NativeWind
        spacing = self.generate_tailwind_spacing()
        if spacing:
            config["theme"]["extend"]["spacing"] = spacing

        # Typography for NativeWind
        fonts = self.generate_tailwind_fonts()
        if fonts:
            config["theme"]["extend"].update(fonts)

        # Border radius for NativeWind
        if self.design_tokens.border_radius:
            border_radius = {}
            for radius in self.design_tokens.border_radius:
                border_radius[radius.name] = f"{radius.value}{radius.unit}"
            config["theme"]["extend"]["borderRadius"] = border_radius

        return config

    def generate_javascript_tokens(self) -> Dict[str, Any]:
        """Generate JavaScript object with all design tokens."""
        if not self.design_tokens:
            return {}

        tokens = {
            "colors": {},
            "typography": {},
            "spacing": {},
            "shadows": {},
            "borderRadius": {},
            "metadata": {
                "generated_at": self.design_tokens.created_at.isoformat() if self.design_tokens.created_at else None,
                "version": self.design_tokens.version,
                "total_tokens": self.processing_stats["total_tokens"]
            }
        }

        # Colors
        for color_token in self.design_tokens.colors:
            tokens["colors"][color_token.name] = {
                "value": color_token.value,
                "category": color_token.category,
                "description": color_token.description,
                "variants": color_token.variants,
                "opacity": color_token.opacity
            }

        # Typography
        for typo_token in self.design_tokens.typography:
            tokens["typography"][typo_token.name] = {
                "fontFamily": typo_token.font_family,
                "fontSize": typo_token.font_size,
                "fontWeight": typo_token.font_weight,
                "lineHeight": typo_token.line_height,
                "letterSpacing": typo_token.letter_spacing,
                "category": typo_token.category,
                "textTransform": typo_token.text_transform
            }

        # Spacing
        for spacing_token in self.design_tokens.spacing:
            tokens["spacing"][spacing_token.name] = {
                "value": spacing_token.value,
                "unit": spacing_token.unit,
                "category": spacing_token.category,
                "scalePosition": spacing_token.scale_position
            }

        # Shadows
        for shadow_token in self.design_tokens.shadows:
            tokens["shadows"][shadow_token.name] = {
                "offsetX": shadow_token.offset_x,
                "offsetY": shadow_token.offset_y,
                "blur": shadow_token.blur,
                "spread": shadow_token.spread,
                "color": shadow_token.color,
                "opacity": shadow_token.opacity,
                "type": shadow_token.type
            }

        # Border radius
        for radius_token in self.design_tokens.border_radius:
            tokens["borderRadius"][radius_token.name] = {
                "value": radius_token.value,
                "unit": radius_token.unit,
                "corners": radius_token.corners
            }

        return tokens

    def save_tailwind_config(self, output_path: str) -> None:
        """Save Tailwind CSS configuration to file."""
        config = self.generate_tailwind_config()

        # Generate JavaScript module format
        js_content = "/** @type {import('tailwindcss').Config} */\n"
        js_content += "module.exports = " + json.dumps(config, indent=2) + ";\n"

        with open(output_path, 'w') as f:
            f.write(js_content)

        logger.info(f"Tailwind config saved to: {output_path}")
        self.processing_stats["frameworks_generated"].append("tailwind")

    def save_nativewind_config(self, output_path: str) -> None:
        """Save NativeWind configuration to file."""
        config = self.generate_nativewind_config()

        js_content = "module.exports = " + json.dumps(config, indent=2) + ";\n"

        with open(output_path, 'w') as f:
            f.write(js_content)

        logger.info(f"NativeWind config saved to: {output_path}")
        self.processing_stats["frameworks_generated"].append("nativewind")

    def save_css_variables(self, output_path: str) -> None:
        """Save CSS custom properties to file."""
        css_content = self.generate_css_variables()

        with open(output_path, 'w') as f:
            f.write(css_content)

        logger.info(f"CSS variables saved to: {output_path}")
        self.processing_stats["frameworks_generated"].append("css")

    def save_scss_variables(self, output_path: str) -> None:
        """Save SCSS variables to file."""
        scss_content = self.generate_scss_variables()

        with open(output_path, 'w') as f:
            f.write(scss_content)

        logger.info(f"SCSS variables saved to: {output_path}")
        self.processing_stats["frameworks_generated"].append("scss")

    def save_javascript_tokens(self, output_path: str) -> None:
        """Save JavaScript tokens to file."""
        tokens = self.generate_javascript_tokens()

        js_content = "// Design Tokens\n"
        js_content += "// Generated by SimFlo Token Converter\n"
        js_content += "export const designTokens = " + json.dumps(tokens, indent=2) + ";\n\n"

        # Add TypeScript types comment
        js_content += "// TypeScript Types\n"
        js_content += "// export type DesignTokens = typeof designTokens;\n"

        with open(output_path, 'w') as f:
            f.write(js_content)

        logger.info(f"JavaScript tokens saved to: {output_path}")
        self.processing_stats["frameworks_generated"].append("javascript")

    def save_metadata(self, output_path: str) -> None:
        """Save processing metadata to file."""
        metadata = {
            "processing_stats": self.processing_stats,
            "design_system_info": {
                "name": self.design_tokens.metadata.get("design_system", "Unknown") if self.design_tokens else "Unknown",
                "description": self.design_tokens.metadata.get("description", "No description") if self.design_tokens else "No description",
                "version": self.design_tokens.version if self.design_tokens else "1.0.0"
            },
            "generated_files": {
                "tailwind_config": "tailwind.config.js",
                "nativewind_config": "nativewind.config.js",
                "css_variables": "design-tokens.css",
                "scss_variables": "design-tokens.scss",
                "javascript_tokens": "design-tokens.js"
            },
            "supported_frameworks": ["tailwind", "nativewind", "css", "scss", "javascript"]
        }

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to: {output_path}")

    def convert_tokens(self, input_path: str, output_dir: str, frameworks: List[str]) -> None:
        """
        Convert design tokens to specified framework formats.

        Args:
            input_path: Path to design tokens JSON file
            output_dir: Directory to save generated files
            frameworks: List of frameworks to generate
        """
        logger.info(f"Converting design tokens for frameworks: {', '.join(frameworks)}")

        # Load and validate design tokens
        self.load_design_tokens(input_path)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate files for each framework
        if "tailwind" in frameworks:
            self.save_tailwind_config(output_path / "tailwind.config.js")

        if "nativewind" in frameworks:
            self.save_nativewind_config(output_path / "nativewind.config.js")

        if "css" in frameworks:
            self.save_css_variables(output_path / "design-tokens.css")

        if "scss" in frameworks:
            self.save_scss_variables(output_path / "design-tokens.scss")

        if "javascript" in frameworks:
            self.save_javascript_tokens(output_path / "design-tokens.js")

        # Always save metadata
        self.save_metadata(output_path / "token-metadata.json")

        logger.info(
            f"Token conversion completed. Generated {len(self.processing_stats['frameworks_generated'])} framework files.")
        logger.info(f"Processing stats: {self.processing_stats}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert design tokens to framework-specific configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to all frameworks
  python main.py --input examples/sample-design-tokens.json --output ./output/

  # Convert to specific frameworks
  python main.py --input examples/sample-design-tokens.json --output ./output/ --frameworks tailwind css javascript

  # Use custom configuration
  python main.py --input examples/sample-design-tokens.json --output ./output/ --config custom-config.json
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to design tokens JSON file from figma-analyzer"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory for generated framework files"
    )

    parser.add_argument(
        "--frameworks", "-f",
        nargs="+",
        default=["tailwind", "css", "javascript"],
        choices=["tailwind", "nativewind", "css", "scss", "javascript"],
        help="Frameworks to generate (default: tailwind css javascript)"
    )

    parser.add_argument(
        "--config", "-c",
        help="Path to configuration JSON file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Token Converter v1.0.0"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Load configuration if provided
        config = {}
        if args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)

        # Initialize converter
        converter = TokenConverter(config)

        # Convert tokens
        converter.convert_tokens(args.input, args.output, args.frameworks)

        print("\n✅ Token conversion completed successfully!")
        print(f"=� Output directory: {args.output}")
        print(f"<� Frameworks generated: {', '.join(args.frameworks)}")
        print(f"=� Tokens processed: {converter.processing_stats['total_tokens']}")

    except CustomValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
