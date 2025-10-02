"""
Python Language-Based Extractor

A fallback extractor for any Python repository.
Extracts classes, functions, modules, and other Python code elements.
"""

import re
import json
import subprocess
import os
import ast
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class PythonExtractor:
    """Language-based extractor for Python repositories"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

        # File patterns to analyze
        self.file_patterns = [
            "**/*.py"
        ]

        # Python AST node types to extract
        self.ast_node_types = {
            ast.FunctionDef: "function",
            ast.AsyncFunctionDef: "async_function",
            ast.ClassDef: "class",
            ast.Module: "module",
            ast.Assign: "variable",
            ast.AnnAssign: "annotated_variable"
        }

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract from any Python repository"""
        try:
            if not repo_url:
                return {"error": "Repository URL required for language-based extraction"}

            # Parse repository URL
            repo_name = self._parse_repo_url(repo_url)
            if not repo_name:
                return {"error": f"Invalid repository URL: {repo_url}"}

            # Ensure GitHub directory exists
            self.github_dir.mkdir(parents=True, exist_ok=True)

            # Download repository using GitHub CLI if not present locally
            repo_path = self.github_dir / repo_name
            if not repo_path.exists():
                print(f"Downloading {repo_name} using GitHub CLI...")
                clone_cmd = ["gh", "repo", "clone", repo_name, str(repo_path)]
                result = subprocess.run(clone_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return {"error": f"Failed to clone repository: {result.stderr}"}
            else:
                print(f"Using local repository at {repo_path}")

            # Get repository information
            repo_info = self._get_repo_info(repo_name, repo_path)
            if not repo_info:
                return {"error": f"Repository {repo_name} not found"}

            # Extract code elements from the repository
            elements = self._extract_elements(repo_name, repo_path)

            # Save elements to registry files
            saved = self.save_to_registry(elements, repo_name)

            result = {
                "extractor": "python",
                "repository": repo_name,
                "repository_url": repo_url,
                "local_path": str(repo_path),
                "timestamp": datetime.now().isoformat(),
                "elements_found": len(elements),
                "elements": elements,
                "saved_to_registry": saved,
                "repo_info": repo_info,
                "file_patterns": self.file_patterns,
                "languages_detected": ["Python"]
            }

            return result

        except Exception as e:
            return {
                "extractor": "python",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _parse_repo_url(self, url: str) -> Optional[str]:
        """Parse GitHub URL to get repository name"""
        # Handle various GitHub URL formats
        patterns = [
            r'github\.com/([^/]+/[^/]+?)(?:\.git)?/?$',  # https://github.com/owner/repo
            r'([^/]+/[^/]+)$',  # owner/repo
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).strip('/')

        return None

    def _get_repo_info(self, repo_name: str, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Get repository information using GitHub CLI"""
        try:
            cmd = ["gh", "repo", "view", repo_name, "--json", "name,description,stargazerCount,forkCount,createdAt,updatedAt,owner,languages,primaryLanguage"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Fallback to basic info
                return {
                    "name": repo_name,
                    "description": f"{repo_name} repository",
                    "stargazerCount": 0,
                    "forkCount": 0,
                    "createdAt": "unknown",
                    "updatedAt": "unknown",
                    "primaryLanguage": {"name": "Python"}
                }
        except Exception:
            return None

    def _extract_elements(self, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract code elements from Python files"""
        elements = []

        # Find all Python files
        files = []
        for pattern in self.file_patterns:
            files.extend(repo_path.glob(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        for file_path in files:
            try:
                # Skip common directories to ignore
                if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'venv', 'env', '.venv', 'site-packages', 'build', 'dist']):
                    continue

                elements.extend(self._extract_from_file(file_path, repo_name, repo_path))
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return elements

    def _extract_from_file(self, file_path: Path, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract elements from a single Python file using AST"""
        elements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return elements

        try:
            # Parse the AST
            tree = ast.parse(content)
            relative_path = file_path.relative_to(repo_path)

            # Extract elements using AST visitor
            elements.extend(self._extract_from_ast(tree, relative_path, repo_name, content))

        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            # Fallback to regex extraction for files with syntax errors
            elements.extend(self._extract_with_regex(content, relative_path, repo_name))
        except Exception as e:
            print(f"Error parsing AST for {file_path}: {e}")
            # Fallback to regex extraction
            elements.extend(self._extract_with_regex(content, relative_path, repo_name))

        return elements

    def _extract_from_ast(self, tree: ast.AST, file_path: Path, repo_name: str, content: str) -> List[Dict[str, Any]]:
        """Extract elements using Python AST"""
        elements = []

        class ElementVisitor(ast.NodeVisitor):
            def __init__(self, file_path, repo_name, content):
                self.file_path = file_path
                self.repo_name = repo_name
                self.content = content
                self.elements = []

            def visit_FunctionDef(self, node):
                self.elements.append(self._create_function_element(node, "function"))
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.elements.append(self._create_function_element(node, "async_function"))
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.elements.append(self._create_class_element(node))
                self.generic_visit(node)

            def _create_function_element(self, node, element_type):
                # Extract docstring
                docstring = ast.get_docstring(node) or ""

                # Extract function signature
                args = [arg.arg for arg in node.args.args]
                signature = f"def {node.name}({', '.join(args)})"

                # Get decorators
                decorators = [ast.unparse(decorator) for decorator in node.decorator_list]

                return self._create_base_element(
                    name=node.name,
                    element_type=element_type,
                    line_number=node.lineno,
                    description=docstring,
                    metadata={
                        "signature": signature,
                        "args": args,
                        "decorators": decorators,
                        "returns": ast.unparse(node.returns) if node.returns else None
                    }
                )

            def _create_class_element(self, node):
                # Extract docstring
                docstring = ast.get_docstring(node) or ""

                # Get base classes
                bases = [ast.unparse(base) for base in node.bases]

                # Get decorators
                decorators = [ast.unparse(decorator) for decorator in node.decorator_list]

                # Extract methods
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_docstring = ast.get_docstring(item) or ""
                        methods.append({
                            "name": item.name,
                            "type": "async_function" if isinstance(item, ast.AsyncFunctionDef) else "function",
                            "description": method_docstring,
                            "line": item.lineno
                        })

                return self._create_base_element(
                    name=node.name,
                    element_type="class",
                    line_number=node.lineno,
                    description=docstring,
                    metadata={
                        "bases": bases,
                        "decorators": decorators,
                        "methods": methods,
                        "method_count": len(methods)
                    }
                )

            def _create_base_element(self, name, element_type, line_number, description, metadata=None):
                lines = self.content.split('\n')
                start_line = max(0, line_number - 1)
                end_line = min(len(lines), line_number + 20)
                context = '\n'.join(lines[start_line:end_line])

                # Extract imports from the entire file
                imports = self._extract_imports()

                return {
                    "name": name,
                    "type": element_type,
                    "category": self._get_category(element_type),
                    "file_path": str(self.file_path),
                    "description": description or f"{element_type.title()}: {name}",
                    "usage_examples": [context],
                    "dependencies": imports,
                    "peer_dependencies": [],
                    "installation": f"# Found in {self.repo_name}",
                    "metadata": {
                        "extractor": "python",
                        "repository": self.repo_name,
                        "line_number": line_number,
                        "context_length": len(context),
                        "has_docstring": bool(description),
                        **(metadata or {})
                    },
                    "quality_score": self._calculate_quality_score(description, context, imports),
                    "platform": ["python", "backend"],
                    "registry": self.repo_name
                }

            def _extract_imports(self):
                """Extract import statements from the content"""
                imports = []
                for match in re.finditer(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', self.content, re.MULTILINE):
                    module = match.group(1)
                    names = match.group(2)
                    if module:
                        imports.append(module)
                    else:
                        for name in names.split(','):
                            imports.append(name.strip().split('.')[0])
                return [imp for imp in imports if imp and not imp.startswith('.')]

            def _get_category(self, element_type):
                if element_type in ["function", "async_function"]:
                    return "functions"
                elif element_type == "class":
                    return "classes"
                else:
                    return "miscellaneous"

            def _calculate_quality_score(self, description, context, dependencies):
                score = 0.0
                if description and len(description) > 20:
                    score += 0.4
                elif description:
                    score += 0.2
                if len(context) > 100:
                    score += 0.3
                if dependencies:
                    score += min(0.3, len(dependencies) * 0.1)
                return min(score, 1.0)

        visitor = ElementVisitor(file_path, repo_name, content)
        visitor.visit(tree)
        return visitor.elements

    def _extract_with_regex(self, content: str, file_path: Path, repo_name: str) -> List[Dict[str, Any]]:
        """Fallback extraction using regex patterns"""
        elements = []

        # Function patterns
        function_patterns = [
            r'def\s+(\w+)\s*\([^)]*\):',
            r'async\s+def\s+(\w+)\s*\([^)]*\):'
        ]

        # Class patterns
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'

        # Extract functions
        for pattern in function_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                function_name = match.group(1)
                if len(function_name) < 2 or function_name.startswith('_'):
                    continue

                elements.append(self._create_regex_element(
                    function_name, "function", match, content, file_path, repo_name
                ))

        # Extract classes
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            if len(class_name) < 2:
                continue

            elements.append(self._create_regex_element(
                class_name, "class", match, content, file_path, repo_name
            ))

        return elements

    def _create_regex_element(self, name: str, element_type: str, match: re.Match,
                             content: str, file_path: Path, repo_name: str) -> Dict[str, Any]:
        """Create element from regex match"""
        line_number = content[:match.start()].count('\n') + 1
        lines = content.split('\n')
        start_line = max(0, line_number - 1)
        end_line = min(len(lines), line_number + 15)
        context = '\n'.join(lines[start_line:end_line])

        return {
            "name": name,
            "type": element_type,
            "category": "functions" if element_type == "function" else "classes",
            "file_path": str(file_path),
            "description": f"{element_type.title()}: {name}",
            "usage_examples": [context],
            "dependencies": [],
            "peer_dependencies": [],
            "installation": f"# Found in {repo_name}",
            "metadata": {
                "extractor": "python",
                "repository": repo_name,
                "line_number": line_number,
                "context_length": len(context),
                "extraction_method": "regex"
            },
            "quality_score": 0.5,  # Lower score for regex extraction
            "platform": ["python", "backend"],
            "registry": repo_name
        }

    def _calculate_quality_score(self, description: str, context: str, dependencies: List[str]) -> float:
        """Calculate quality score for extracted element"""
        score = 0.0

        # Description quality (0.4)
        if description and len(description) > 20:
            score += 0.4
        elif description:
            score += 0.2

        # Context quality (0.3)
        if len(context) > 150:
            score += 0.3
        elif len(context) > 50:
            score += 0.2

        # Dependencies (0.3)
        if dependencies:
            score += min(0.3, len(dependencies) * 0.1)

        return min(score, 1.0)

    def save_to_registry(self, elements: List[Dict[str, Any]], repo_name: str) -> Dict[str, int]:
        """Save extracted elements to registry files"""
        # Sanitize repository name for file system compatibility
        safe_repo_name = repo_name.replace('/', '-').replace('\\', '-')
        registry_dir = Path(f"v2/core/00-rag-registry/registries/{safe_repo_name}/files")
        saved_counts = {}

        try:
            # Organize elements by category
            by_category = {}
            for element in elements:
                category = element.get("category", "miscellaneous")
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(element)

            # Save each category to its own file
            for category, category_elements in by_category.items():
                category_dir = registry_dir / category
                category_dir.mkdir(parents=True, exist_ok=True)

                output_file = category_dir / f"{safe_repo_name}-{category}.json"

                # Load existing data if file exists
                existing_data = []
                if output_file.exists():
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        existing_data = []

                # Add new elements
                existing_data.extend(category_elements)

                # Save updated data
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, default=str)

                saved_counts[category] = len(category_elements)

            return saved_counts

        except Exception as e:
            print(f"Error saving to registry: {e}")
            return {}

    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about this extractor"""
        return {
            "name": "python",
            "type": "language-based",
            "description": "Python language-based fallback extractor",
            "supported_patterns": self.file_patterns,
            "element_types": ["function", "async_function", "class"],
            "supports_any_repository": True,
            "quality": "good",
            "fallback_for": ["Python", "Django", "Flask", "FastAPI", "Data Science"],
            "extraction_methods": ["AST parsing", "regex fallback"]
        }