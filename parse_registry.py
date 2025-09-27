#!/usr/bin/env python3
"""
SimFlo MCP RAG - Registry Parser

Parses shadcn registry files and extracts structured component data for RAG database.
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class RegistryFile:
    """Represents a file in the registry"""
    path: str
    type: str
    content: Optional[str] = None
    target: Optional[str] = None


@dataclass
class ShadcnComponent:
    """Represents a shadcn component/block/hook"""
    name: str
    type: str  # 'ui', 'block', 'hook'
    description: Optional[str] = None
    dependencies: List[str] = None
    registryDependencies: List[str] = None
    files: List[RegistryFile] = None
    tailwind: Optional[Dict[str, Any]] = None
    categories: List[str] = None
    meta: Optional[Dict[str, Any]] = None
    cssVars: Optional[Dict[str, Any]] = None
    installCommand: str = ""
    fileLocation: str = ""

    def __post_init__(self):
        """Initialize default values for lists"""
        if self.dependencies is None:
            self.dependencies = []
        if self.registryDependencies is None:
            self.registryDependencies = []
        if self.files is None:
            self.files = []
        if self.categories is None:
            self.categories = []

        # Generate install command and file location based on type
        if not self.installCommand:
            if self.type == 'ui':
                self.installCommand = f"npx shadcn add {self.name}"
                self.fileLocation = f"ui/{self.name}.tsx"
            elif self.type == 'hook':
                self.installCommand = f"npx shadcn add {self.name}"
                self.fileLocation = f"hooks/{self.name}.ts"
            elif self.type == 'block':
                self.installCommand = f"Manual installation - copy block files"
                self.fileLocation = f"blocks/{self.name}/"


class RegistryParser:
    """Parses shadcn registry files"""

    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.components: List[ShadcnComponent] = []
        self.documentation = {}

    def parse_registry_file(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """Parse TypeScript registry file and extract component data"""
        # Extract the array from the export statement - handle different patterns
        patterns = [
            r'export\s+(?:const|let|var)\s+(\w+)\s*:\s*Registry\["items"\]\s*=\s*(\[[\s\S]*?\])\s*$',
            r'export\s+(?:const|let|var)\s+(\w+)\s*:\s*Registry\["items"\]\s*=\s*(\[[\s\S]*?\]);',
            r'export\s+(?:const|let|var)\s+(\w+)\s*=\s*(\[[\s\S]*?\])\s*$',
            r'export\s+(?:const|let|var)\s+(\w+)\s*=\s*(\[[\s\S]*?\]);'
        ]

        array_content = None
        for pattern in patterns:
            try:
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    array_content = match.group(2)
                    break
            except re.error:
                continue

        if not array_content:
            raise ValueError(f"Could not find registry array in {file_type} file")

        # Convert JavaScript object syntax to JSON
        try:
            return self._js_to_json(array_content)
        except Exception as e:
            raise ValueError(f"Failed to parse {file_type} registry: {e}")

    def _js_to_json(self, js_content: str) -> List[Dict[str, Any]]:
        """Convert JavaScript object syntax to JSON and parse"""
        # Step 1: Replace JavaScript values with JSON equivalents
        content = js_content.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        # Step 2: Quote unquoted keys more precisely
        # Only match word characters at the beginning of a line or after whitespace, followed by colon
        content = re.sub(r'^(\s*)(\w+)(\s*):', r'\1"\2"\3:', content, flags=re.MULTILINE)
        content = re.sub(r'(\n\s*)(\w+)(\s*):', r'\1"\2"\3:', content)
        content = re.sub(r'(\{\s*)(\w+)(\s*):', r'\1"\2"\3:', content)

        # Step 3: Handle trailing commas in arrays and objects
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        # Step 4: Fix any remaining nested objects with unquoted keys
        def quote_nested_keys(match):
            before = match.group(1)
            key = match.group(2)
            after = match.group(3)
            return f'{before}"{key}"{after}:'

        content = re.sub(r'(\{\s*)(\w+)(\s*):', quote_nested_keys, content)

        # Step 5: Try to parse as Python literal first
        try:
            return ast.literal_eval(content)
        except (ValueError, SyntaxError) as e:
            # Step 6: Fallback to JSON parsing with additional cleanup
            try:
                # Additional cleaning for JSON compatibility
                content = content.replace("'", '"')  # Single quotes to double quotes

                # Fix registry:ui type fields specifically
                content = re.sub(r'"type":\s*""([^"]+)""', r'"type": "\1"', content)

                # Fix any remaining syntax issues
                content = re.sub(r'}\s*{', '},{', content)  # Fix missing commas between objects

                return json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON parsing failed: {e}")

    def parse_ui_components(self) -> None:
        """Parse UI components from registry-ui.ts"""
        ui_file = self.registry_path / "registry-ui.ts"
        if not ui_file.exists():
            raise FileNotFoundError(f"UI registry file not found: {ui_file}")

        content = ui_file.read_text()
        ui_data = self.parse_registry_file(content, "ui")

        for item in ui_data:
            component = ShadcnComponent(
                name=item['name'],
                type='ui',
                dependencies=item.get('dependencies', []),
                registryDependencies=item.get('registryDependencies', []),
                files=[RegistryFile(**f) for f in item.get('files', [])],
                tailwind=item.get('tailwind'),
                cssVars=item.get('cssVars')
            )
            self.components.append(component)

    def parse_blocks(self) -> None:
        """Parse blocks from registry-blocks.ts"""
        blocks_file = self.registry_path / "registry-blocks.ts"
        if not blocks_file.exists():
            raise FileNotFoundError(f"Blocks registry file not found: {blocks_file}")

        content = blocks_file.read_text()
        blocks_data = self.parse_registry_file(content, "blocks")

        for item in blocks_data:
            component = ShadcnComponent(
                name=item['name'],
                type='block',
                description=item.get('description', ''),
                dependencies=item.get('dependencies', []),
                registryDependencies=item.get('registryDependencies', []),
                files=[RegistryFile(**f) for f in item.get('files', [])],
                categories=item.get('categories', []),
                meta=item.get('meta')
            )
            self.components.append(component)

    def parse_hooks(self) -> None:
        """Parse hooks from registry-hooks.ts"""
        hooks_file = self.registry_path / "registry-hooks.ts"
        if not hooks_file.exists():
            raise FileNotFoundError(f"Hooks registry file not found: {hooks_file}")

        content = hooks_file.read_text()
        hooks_data = self.parse_registry_file(content, "hooks")

        for item in hooks_data:
            component = ShadcnComponent(
                name=item['name'],
                type='hook',
                dependencies=item.get('dependencies', []),
                registryDependencies=item.get('registryDependencies', []),
                files=[RegistryFile(**f) for f in item.get('files', [])]
            )
            self.components.append(component)

    def load_documentation(self) -> None:
        """Load documentation files to enhance descriptions"""
        doc_path = self.registry_path.parent

        # Load components documentation
        components_doc = doc_path / "COMPONENTS_REGISTRY.md"
        if components_doc.exists():
            self.documentation['components'] = components_doc.read_text()

        # Load hooks documentation
        hooks_doc = doc_path / "HOOKS_REGISTRY.md"
        if hooks_doc.exists():
            self.documentation['hooks'] = hooks_doc.read_text()

        # Load blocks documentation
        blocks_doc = doc_path / "BLOCKS_REGISTRY.md"
        if blocks_doc.exists():
            self.documentation['blocks'] = blocks_doc.read_text()

    def enhance_descriptions(self) -> None:
        """Enhance component descriptions with documentation"""
        # This is a simple enhancement - in a real implementation, you might want
        # to do more sophisticated matching and extraction
        for component in self.components:
            if component.type == 'ui' and 'components' in self.documentation:
                # Look for component name in documentation
                component_name_lower = component.name.lower()
                doc_content = self.documentation['components'].lower()

                # Simple enhancement - add description if not present
                if not component.description:
                    if component_name_lower in doc_content:
                        component.description = f"UI component for {component.name.replace('-', ' ')}"
                    else:
                        component.description = f"Shadcn UI component: {component.name}"

            elif component.type == 'hook' and 'hooks' in self.documentation:
                if not component.description:
                    component.description = f"React hook: {component.name}"

            elif component.type == 'block' and 'blocks' in self.documentation:
                if not component.description:
                    component.description = f"Block component: {component.name}"

    def parse_all(self) -> List[ShadcnComponent]:
        """Parse all registry files and return components"""
        print(f"Parsing registry files from: {self.registry_path}")

        # Load documentation first
        self.load_documentation()

        # Parse all component types
        self.parse_ui_components()
        print(f"Parsed {len([c for c in self.components if c.type == 'ui'])} UI components")

        self.parse_blocks()
        print(f"Parsed {len([c for c in self.components if c.type == 'block'])} blocks")

        self.parse_hooks()
        print(f"Parsed {len([c for c in self.components if c.type == 'hook'])} hooks")

        # Enhance with documentation
        self.enhance_descriptions()

        print(f"Total components parsed: {len(self.components)}")
        return self.components

    def to_json(self, output_file: Optional[str] = None) -> str:
        """Export components to JSON"""
        data = [asdict(comp) for comp in self.components]
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if output_file:
            Path(output_file).write_text(json_str, encoding='utf-8')
            print(f"Exported to: {output_file}")

        return json_str

    def print_summary(self) -> None:
        """Print a summary of parsed components"""
        print("\n=== Parsing Summary ===")
        print(f"Total Components: {len(self.components)}")

        by_type = {}
        for comp in self.components:
            by_type[comp.type] = by_type.get(comp.type, 0) + 1

        for comp_type, count in by_type.items():
            print(f"  {comp_type.capitalize()}: {count}")

        print("\nSample components:")
        for comp in self.components[:5]:
            desc = comp.description or "No description"
            print(f"  - {comp.name} ({comp.type}): {desc[:60]}...")

        if len(self.components) > 5:
            print(f"  ... and {len(self.components) - 5} more")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Parse shadcn registry files")
    parser.add_argument(
        "--registry-path",
        default="/Users/tbardale/github/shadcn-ui/apps/v4/registry",
        help="Path to shadcn registry directory"
    )
    parser.add_argument(
        "--output",
        default="components.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, don't save JSON"
    )

    args = parser.parse_args()

    try:
        registry_parser = RegistryParser(args.registry_path)
        components = registry_parser.parse_all()

        registry_parser.print_summary()

        if not args.summary_only:
            json_output = registry_parser.to_json(args.output)
            print(f"\nSuccessfully parsed and saved {len(components)} components")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())