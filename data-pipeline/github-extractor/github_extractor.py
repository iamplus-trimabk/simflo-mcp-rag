#!/usr/bin/env python3
"""
SimFlo MCP RAG - GitHub Repository Extractor

Extracts component information from GitHub repositories for RAG database.
Supports any component library with flexible repository structure detection.
"""

import json
import re
import ast
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse
import logging
from urllib.parse import urlparse


@dataclass
class ComponentFile:
    """Represents a component file in the repository"""
    path: str
    content: str
    language: str  # 'typescript', 'javascript', 'jsx', 'tsx'
    component_type: str  # 'component', 'hook', 'util', 'type'
    exports: List[str] = None
    imports: List[str] = None
    props_info: Dict[str, Any] = None
    usage_patterns: List[str] = None

    def __post_init__(self):
        if self.exports is None:
            self.exports = []
        if self.imports is None:
            self.imports = []
        if self.props_info is None:
            self.props_info = {}
        if self.usage_patterns is None:
            self.usage_patterns = []


@dataclass
class ComponentInfo:
    """Represents extracted component information"""
    name: str
    description: Optional[str] = None
    type: str = 'component'  # 'component', 'hook', 'util'
    platform: List[str] = None  # 'reactjs', 'reactnative', 'both'
    files: List[ComponentFile] = None
    dependencies: List[str] = None
    peer_dependencies: List[str] = None
    dev_dependencies: List[str] = None
    examples: List[str] = None
    tags: List[str] = None
    props_info: Dict[str, Any] = None
    usage_patterns: List[str] = None
    source_repository: str = ""
    repository_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.platform is None:
            self.platform = ['reactjs']
        if self.files is None:
            self.files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.peer_dependencies is None:
            self.peer_dependencies = []
        if self.dev_dependencies is None:
            self.dev_dependencies = []
        if self.examples is None:
            self.examples = []
        if self.tags is None:
            self.tags = []
        if self.props_info is None:
            self.props_info = {}
        if self.usage_patterns is None:
            self.usage_patterns = []
        if self.repository_metadata is None:
            self.repository_metadata = {}


class GitHubExtractor:
    """Extracts component information from GitHub repositories"""

    def __init__(self, repo_url: str, output_dir: Optional[str] = None):
        self.repo_url = repo_url
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.temp_dir = None
        self.repo_name = self._extract_repo_name(repo_url)
        self.components: List[ComponentInfo] = []

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _extract_repo_name(self, url: str) -> str:
        """Extract repository name from GitHub URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts[1]
        return 'unknown'

    def _clone_repository(self) -> Path:
        """Clone repository to temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix=f'github_extractor_{self.repo_name}_')
        temp_path = Path(self.temp_dir)

        self.logger.info(f"Cloning {self.repo_url} to {temp_path}")

        try:
            result = subprocess.run(
                ['git', 'clone', self.repo_url, str(temp_path)],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"Repository cloned successfully")
            return temp_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to clone repository: {e}")
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)
            raise

    def _find_package_json(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Find and parse package.json file"""
        package_json_paths = [
            repo_path / 'package.json',
            repo_path / 'src' / 'package.json',
        ]

        for package_path in package_json_paths:
            if package_path.exists():
                try:
                    with open(package_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    self.logger.warning(f"Failed to parse {package_path}: {e}")

        return None

    def _find_readme(self, repo_path: Path) -> Optional[str]:
        """Find and read README file"""
        readme_patterns = ['README.md', 'README.rst', 'README.txt', 'readme.md']

        for pattern in readme_patterns:
            readme_path = repo_path / pattern
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except IOError as e:
                    self.logger.warning(f"Failed to read {readme_path}: {e}")

        return None

    def _scan_component_directories(self, repo_path: Path) -> List[Path]:
        """Scan for component directories using common patterns"""
        component_dirs = []

        # Common component directory patterns
        patterns = [
            'components',
            'src/components',
            'ui',
            'src/ui',
            'lib/components',
            'packages/*/src/components',
        ]

        for pattern in patterns:
            if '*' in pattern:
                # Handle glob patterns
                for path in repo_path.glob(pattern):
                    if path.is_dir():
                        component_dirs.append(path)
            else:
                path = repo_path / pattern
                if path.is_dir():
                    component_dirs.append(path)

        return component_dirs

    def _find_component_files(self, directories: List[Path]) -> List[Path]:
        """Find component files in directories"""
        component_files = []

        # Component file extensions
        extensions = ['.tsx', '.ts', '.jsx', '.js']

        for directory in directories:
            for ext in extensions:
                component_files.extend(directory.glob(f'**/*{ext}'))

        return component_files

    def _analyze_component_file(self, file_path: Path, repo_root: Path) -> ComponentFile:
        """Analyze a single component file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            self.logger.warning(f"Failed to read {file_path}: {e}")
            return ComponentFile(str(file_path), "", "unknown", "unknown")

        # Determine language
        if file_path.suffix == '.tsx':
            language = 'tsx'
        elif file_path.suffix == '.ts':
            language = 'typescript'
        elif file_path.suffix == '.jsx':
            language = 'jsx'
        else:
            language = 'javascript'

        # Determine component type based on filename and content
        component_type = self._determine_component_type(file_path, content)

        # Extract exports and imports
        exports = self._extract_exports(content)
        imports = self._extract_imports(content)

        # Parse component interface and props
        props_info = {}
        if component_type == 'component':
            props_info = self._parse_component_interface(content)

        # Extract usage patterns
        usage_patterns = []
        if exports:
            main_export = exports[0]
            usage_patterns = self._extract_usage_patterns(content, main_export)

        return ComponentFile(
            path=str(file_path.relative_to(repo_root)),
            content=content,
            language=language,
            component_type=component_type,
            exports=exports,
            imports=imports,
            props_info=props_info,
            usage_patterns=usage_patterns
        )

    def _determine_component_type(self, file_path: Path, content: str) -> str:
        """Determine if file contains component, hook, or utility"""
        filename = file_path.name.lower()

        # Check for hooks
        if filename.startswith('use') and '.ts' in filename:
            return 'hook'

        # Check for utilities
        if 'util' in filename or 'helper' in filename:
            return 'util'

        # Check for type definitions
        if filename.endswith('.d.ts') or 'types' in filename:
            return 'type'

        # Default to component
        return 'component'

    def _extract_exports(self, content: str) -> List[str]:
        """Extract export statements from content"""
        exports = []

        # Export statements
        export_patterns = [
            r'export\s+(?:const|let|var|function|class)\s+(\w+)',
            r'export\s+default\s+(?:function|class)?\s*(\w+)?',
            r'export\s+{\s*([^}]+)\s*}',
        ]

        for pattern in export_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1] if len(match) > 1 else ''
                if match:
                    # Split multiple exports in braces
                    for export in [e.strip() for e in match.split(',') if e.strip()]:
                        exports.append(export)

        return list(set(exports))

    def _parse_component_interface(self, content: str) -> Dict[str, Any]:
        """Parse TypeScript interface/props from component"""
        props_info = {
            'props': [],
            'interface_name': None,
            'has_children': False,
            'is_functional': True
        }

        try:
            # Parse AST for better component analysis
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                    # Extract function/class name
                    component_name = node.name

                    # Check if it's a React component (has JSX or returns JSX)
                    if self._is_react_component(node):
                        # Extract props from function parameters or class properties
                        props_info.update(self._extract_component_props(node, content))
                        props_info['component_name'] = component_name

        except SyntaxError:
            # If AST parsing fails, use regex fallback
            props_info.update(self._extract_props_regex(content))

        return props_info

    def _is_react_component(self, node) -> bool:
        """Check if AST node represents a React component"""
        # Check for React component patterns
        if hasattr(node, 'name') and (
            node.name.startswith(('use', 'create')) or  # Skip hooks and creators
            node.name.lower().endswith('component') or
            any(char.isupper() for char in node.name[:1])  # PascalCase
        ):
            return True

        # Check for JSX in function body
        if hasattr(node, 'body'):
            for child in ast.walk(node.body):
                if hasattr(child, '__class__'):
                    # Look for JSX-like patterns (simplified check)
                    if hasattr(child, 'value') and hasattr(child.value, '__class__'):
                        return True

        return False

    def _extract_component_props(self, node, content: str) -> Dict[str, Any]:
        """Extract props from component node"""
        props = []
        interface_name = None

        # Extract from function parameters
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg == 'props':
                    # Look for props interface/type definition
                    interface_name = self._find_props_interface(content, arg.arg)
                elif arg.arg != 'children':
                    props.append({
                        'name': arg.arg,
                        'type': 'any',
                        'required': True,
                        'description': ''
                    })

        # Extract class properties for class components
        elif isinstance(node, ast.ClassDef):
            # Look for prop types or TypeScript interfaces
            interface_name = self._find_props_interface(content, 'props')

        return {
            'props': props,
            'interface_name': interface_name,
            'has_children': self._has_children_prop(content),
            'is_functional': isinstance(node, ast.FunctionDef)
        }

    def _find_props_interface(self, content: str, props_var: str = 'props') -> Optional[str]:
        """Find TypeScript interface for props"""
        # Look for interface definitions
        interface_patterns = [
            fr'interface\s+{props_var.title()}\s*Props\s*{{[^}}]*}}',
            fr'type\s+{props_var.title()}\s*Props\s*=\s*{{[^}}]*}}',
            fr'interface\s+\w*Props\s*{{[^}}]*}}',
            fr'type\s+\w*Props\s*=\s*{{[^}}]*}}',
        ]

        for pattern in interface_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # Extract interface name
                name_match = re.search(r'(?:interface|type)\s+(\w+)', match.group(0))
                if name_match:
                    return name_match.group(1)

        return None

    def _has_children_prop(self, content: str) -> bool:
        """Check if component accepts children"""
        patterns = [
            r'children\s*:',
            r'props\.children',
            r'\{children\}',
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                return True

        return False

    def _extract_props_regex(self, content: str) -> Dict[str, Any]:
        """Fallback regex-based prop extraction"""
        props = []

        # Extract interface definitions
        interface_pattern = r'interface\s+(\w*Props?)\s*{([^}]*)}'
        matches = re.findall(interface_pattern, content, re.DOTALL)

        interface_name = None
        for match in matches:
            interface_name = match[0]
            interface_body = match[1]

            # Extract individual props
            prop_lines = [line.strip() for line in interface_body.split('\n') if line.strip()]
            for line in prop_lines:
                prop_match = re.match(r'(\w+)\s*:\s*([^;]+)', line)
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_type = prop_match.group(2).strip()

                    # Check if optional
                    is_required = '?' not in prop_name
                    if '?' in prop_name:
                        prop_name = prop_name.replace('?', '')

                    props.append({
                        'name': prop_name,
                        'type': prop_type,
                        'required': is_required,
                        'description': ''
                    })

        return {
            'props': props,
            'interface_name': interface_name,
            'has_children': self._has_children_prop(content),
            'is_functional': True
        }

    def _extract_usage_patterns(self, content: str, component_name: str) -> List[str]:
        """Extract common usage patterns from component source"""
        patterns = []

        # Look for common React patterns
        react_patterns = [
            # JSX usage
            rf'<{component_name}[^>]*>.*?</{component_name}>',
            rf'<{component_name}[^>]*/>',
            # Hook usage
            rf'const\s+\w+\s*=\s*{component_name}\s*\(',
            # Function calls
            rf'{component_name}\s*\([^)]*\)',
        ]

        for pattern in react_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            patterns.extend(matches[:2])  # Limit to 2 patterns per type

        return patterns[:5]  # Total limit

    def _extract_component_tags(self, component_name: str, files: List[ComponentFile],
                              package_json: Dict[str, Any]) -> List[str]:
        """Extract relevant tags for the component"""
        tags = []

        # Add platform tags
        for file in files:
            if 'native' in file.path.lower() or 'react-native' in file.imports:
                tags.append('react-native')
            elif 'web' in file.path.lower() or 'react' in file.imports:
                tags.append('react')

        # Add component type tags
        for file in files:
            if file.component_type == 'hook':
                tags.append('hook')
            elif file.component_type == 'component':
                tags.append('ui-component')

        # Add file-based tags
        for file in files:
            filename = Path(file.path).name.lower()
            if 'button' in filename:
                tags.append('button')
            elif 'input' in filename:
                tags.append('input')
            elif 'modal' in filename:
                tags.append('modal')
            elif 'form' in filename:
                tags.append('form')

        # Add package keywords
        if package_json and 'keywords' in package_json:
            tags.extend(package_json['keywords'])

        return list(set(tags))

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from content"""
        imports = []

        # Import statements
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)

        return list(set(imports))

    def _extract_platform_info(self, package_json: Dict[str, Any]) -> List[str]:
        """Extract platform information from package.json"""
        platforms = ['reactjs']  # Default

        # Check for React Native indicators
        if package_json:
            name = package_json.get('name', '').lower()
            keywords = package_json.get('keywords', [])
            dependencies = package_json.get('dependencies', {})

            if ('react-native' in name or
                'react-native' in keywords or
                'react-native' in dependencies):
                platforms = ['reactnative']
            elif any('react' in dep.lower() for dep in dependencies):
                platforms = ['reactjs']
            else:
                platforms = ['both']  # Assume both if unclear

        return platforms

    def _extract_component_description(self, component_name: str, files: List[ComponentFile],
                                     package_json: Dict[str, Any], readme: str) -> str:
        """Extract component description from various sources"""
        description = ""

        # Try to find JSDoc comments in component files
        for file in files:
            if file.component_type == 'component':
                jsdoc_comments = self._extract_jsdoc_comments(file.content)
                if jsdoc_comments:
                    description = jsdoc_comments[0]  # Use first JSDoc comment
                    break

        # Try to extract from README
        if not description and readme:
            description = self._extract_from_readme(component_name, readme)

        # Use package.json description as fallback
        if not description and package_json:
            description = package_json.get('description', '')

        return description

    def _extract_jsdoc_comments(self, content: str) -> List[str]:
        """Extract JSDoc comments from source code"""
        jsdoc_pattern = r'/\*\*[\s\S]*?\*/'
        matches = re.findall(jsdoc_pattern, content)

        descriptions = []
        for match in matches:
            # Clean up JSDoc comment
            lines = match.split('\n')
            clean_lines = []
            for line in lines:
                line = line.strip().replace('* ', '').replace('*', '').replace('/**', '').replace('*/', '')
                if line and not line.startswith('@'):
                    clean_lines.append(line)

            if clean_lines:
                descriptions.append(' '.join(clean_lines))

        return descriptions

    def _extract_from_readme(self, component_name: str, readme: str) -> str:
        """Extract component description from README"""
        # Look for component sections in README
        patterns = [
            rf'##\s*{component_name.title()}[\s\S]*?(?=##|\Z)',
            rf'#{component_name.title()}[\s\S]*?(?=#|\Z)',
            rf'`{component_name}`[\s\S]*?(?=\n\n|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, readme, re.IGNORECASE)
            if match:
                section = match.group(0)
                # Extract first paragraph after heading
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('`'):
                        return line

        return ""

    def _extract_dependencies_from_file(self, file: ComponentFile) -> List[str]:
        """Extract dependencies specific to a component file"""
        dependencies = []

        for import_path in file.imports:
            # Filter out relative imports and built-in modules
            if (not import_path.startswith('./') and
                not import_path.startswith('../') and
                not import_path.startswith('/')):
                dependencies.append(import_path)

        return dependencies

    def _extract_examples(self, component_name: str, files: List[ComponentFile], readme: str) -> List[str]:
        """Extract usage examples for the component"""
        examples = []

        # Extract from README
        readme_examples = self._extract_examples_from_readme(component_name, readme)
        examples.extend(readme_examples)

        # Extract from file comments
        for file in files:
            if file.component_type == 'component':
                file_examples = self._extract_examples_from_file(file.content, component_name)
                examples.extend(file_examples)

        return examples[:3]  # Limit to 3 examples per component

    def _extract_examples_from_readme(self, component_name: str, readme: str) -> List[str]:
        """Extract code examples from README"""
        examples = []

        # Look for code blocks near component mentions
        pattern = rf'```(?:tsx|ts|jsx|js)[\s\S]*?{component_name}[\s\S]*?```'
        matches = re.findall(pattern, readme, re.IGNORECASE)

        for match in matches:
            # Clean up code block
            code = match.replace('```tsx', '').replace('```ts', '').replace('```jsx', '').replace('```js', '').replace('```', '')
            code = code.strip()
            if code:
                examples.append(code)

        return examples

    def _extract_examples_from_file(self, content: str, component_name: str) -> List[str]:
        """Extract examples from file comments"""
        examples = []

        # Look for example blocks in comments
        pattern = r'/\*\*[\s\S]*?@example[\s\S]*?\*/'
        matches = re.findall(pattern, content)

        for match in matches:
            # Extract code after @example
            example_match = re.search(r'@example\s*(.*?)(?=\s*@|\*/)', match, re.DOTALL)
            if example_match:
                example = example_match.group(1).strip()
                if example:
                    examples.append(example)

        return examples

    def extract_components(self) -> List[ComponentInfo]:
        """Main method to extract components from repository"""
        self.logger.info(f"Starting extraction from {self.repo_url}")

        try:
            # Clone repository
            repo_path = self._clone_repository()

            # Find package.json and README
            package_json = self._find_package_json(repo_path)
            readme_content = self._find_readme(repo_path)

            # Extract basic repository info
            repo_info = {
                'name': package_json.get('name', self.repo_name) if package_json else self.repo_name,
                'description': package_json.get('description', '') if package_json else '',
                'version': package_json.get('version', '1.0.0') if package_json else '1.0.0',
                'dependencies': package_json.get('dependencies', {}) if package_json else {},
                'peerDependencies': package_json.get('peerDependencies', {}) if package_json else {},
                'devDependencies': package_json.get('devDependencies', {}) if package_json else {},
            }

            # Scan for component directories
            component_dirs = self._scan_component_directories(repo_path)
            self.logger.info(f"Found component directories: {[str(d) for d in component_dirs]}")

            # Find component files
            component_files = self._find_component_files(component_dirs)
            self.logger.info(f"Found {len(component_files)} component files")

            # Analyze each component file
            analyzed_files = []
            for file_path in component_files:
                analyzed_file = self._analyze_component_file(file_path, repo_path)
                analyzed_files.append(analyzed_file)

            # Group files by component name
            component_groups = self._group_files_by_component(analyzed_files)

            # Create ComponentInfo objects
            platform = self._extract_platform_info(package_json)

            for component_name, files in component_groups.items():
                # Extract enhanced metadata for this component
                description = self._extract_component_description(component_name, files, package_json, readme_content)
                examples = self._extract_examples(component_name, files, readme_content)
                tags = self._extract_component_tags(component_name, files, package_json)

                # Extract specific dependencies for this component
                component_dependencies = set()
                for file in files:
                    file_deps = self._extract_dependencies_from_file(file)
                    component_dependencies.update(file_deps)

                # Aggregate props info from all files
                props_info = {}
                usage_patterns = []
                for file in files:
                    if file.props_info:
                        props_info = file.props_info  # Use main component props
                    usage_patterns.extend(file.usage_patterns)

                component = ComponentInfo(
                    name=component_name,
                    description=description,
                    platform=platform,
                    files=files,
                    dependencies=list(component_dependencies),
                    peer_dependencies=list(repo_info['peerDependencies'].keys()),
                    dev_dependencies=list(repo_info['devDependencies'].keys()),
                    examples=examples,
                    tags=tags,
                    props_info=props_info,
                    usage_patterns=usage_patterns[:5],  # Limit to 5 patterns
                    source_repository=self.repo_url
                )

                self.components.append(component)

            self.logger.info(f"Extracted {len(self.components)} components")
            return self.components

        finally:
            # Clean up temporary directory
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)

    def _group_files_by_component(self, files: List[ComponentFile]) -> Dict[str, List[ComponentFile]]:
        """Group component files by component name"""
        component_groups = {}

        for file in files:
            # Extract component name from file path
            component_name = self._extract_component_name_from_file(file)

            if component_name:
                if component_name not in component_groups:
                    component_groups[component_name] = []
                component_groups[component_name].append(file)

        return component_groups

    def _extract_component_name_from_file(self, file: ComponentFile) -> Optional[str]:
        """Extract component name from file path and exports"""
        # Try to get component name from file path
        filename = Path(file.path).stem

        # Skip test files and utility files
        if filename.endswith('.test') or filename.endswith('.spec') or filename.startswith('index'):
            return None

        # If file has exports, use the main export
        if file.exports:
            main_export = file.exports[0]
            # Clean up export name (remove hooks prefix, etc.)
            if main_export.startswith('use'):
                return main_export  # Keep hook names
            else:
                # Remove component suffixes
                clean_name = re.sub(r'Component$', '', main_export)
                return clean_name.lower()

        # Use filename as fallback
        clean_name = re.sub(r'Component$', '', filename, flags=re.IGNORECASE)
        return clean_name.lower()

    def save_to_json(self, output_path: Optional[str] = None) -> str:
        """Save extracted components to JSON file"""
        if output_path is None:
            output_path = self.output_dir / f'{self.repo_name}_components.json'

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        components_data = []
        for component in self.components:
            component_dict = asdict(component)
            # Convert ComponentFile objects to dicts
            component_dict['files'] = [asdict(f) for f in component.files]
            components_data.append(component_dict)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(components_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Components saved to {output_file}")
        return str(output_file)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Extract components from GitHub repository')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        extractor = GitHubExtractor(args.repo_url, args.output)
        components = extractor.extract_components()

        output_file = extractor.save_to_json(args.output)
        print(f"Successfully extracted {len(components)} components to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()