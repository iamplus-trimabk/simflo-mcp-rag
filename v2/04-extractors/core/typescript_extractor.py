"""
TypeScript/JavaScript Language-Based Extractor

A fallback extractor for any TypeScript/JavaScript repository.
Extracts components, functions, classes, types, and other code elements.
"""

import re
import json
import subprocess
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class TypescriptExtractor:
    """Language-based extractor for TypeScript/JavaScript repositories"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

        # File patterns to analyze
        self.file_patterns = [
            "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"
        ]

        # Patterns for different code elements
        self.patterns = {
            "component": {
                "tsx_component": r'export\s+(?:const|function)\s+(\w+).*?React\.[FC] Component',
                "function_component": r'export\s+function\s+(\w+)\s*\(',
                "arrow_component": r'export\s+const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                "class_component": r'export\s+class\s+(\w+).*?extends\s+.*Component',
            },
            "function": {
                "function_export": r'export\s+function\s+(\w+)\s*\(',
                "function_default": r'function\s+(\w+)\s*\(',
                "arrow_function": r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                "method": r'(\w+)\s*\([^)]*\)\s*[:{]',
            },
            "class": {
                "class_export": r'export\s+class\s+(\w+)',
                "class_default": r'class\s+(\w+)',
            },
            "type": {
                "type_export": r'export\s+(?:type|interface)\s+(\w+)',
                "type_alias": r'type\s+(\w+)\s*=',
                "interface": r'interface\s+(\w+)',
            },
            "constant": {
                "constant_export": r'export\s+const\s+(\w+)\s*=',
                "constant": r'const\s+(\w+)\s*=',
            }
        }

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract from any TypeScript/JavaScript repository"""
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
                "extractor": "typescript",
                "repository": repo_name,
                "repository_url": repo_url,
                "local_path": str(repo_path),
                "timestamp": datetime.now().isoformat(),
                "elements_found": len(elements),
                "elements": elements,
                "saved_to_registry": saved,
                "repo_info": repo_info,
                "file_patterns": self.file_patterns,
                "languages_detected": ["TypeScript", "JavaScript"]
            }

            return result

        except Exception as e:
            return {
                "extractor": "typescript",
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
                    "primaryLanguage": {"name": "TypeScript"}
                }
        except Exception:
            return None

    def _extract_elements(self, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract code elements from TypeScript/JavaScript files"""
        elements = []

        # Find all TypeScript/JavaScript files
        files = []
        for pattern in self.file_patterns:
            files.extend(repo_path.glob(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        for file_path in files:
            try:
                # Skip node_modules, dist, build, etc.
                if any(skip in str(file_path) for skip in ['node_modules', 'dist', 'build', '.git', 'coverage']):
                    continue

                elements.extend(self._extract_from_file(file_path, repo_name, repo_path))
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return elements

    def _extract_from_file(self, file_path: Path, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract elements from a single file"""
        elements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return elements

        relative_path = file_path.relative_to(repo_path)
        file_type = self._get_file_type(file_path)

        # Extract different types of elements
        for element_type, patterns in self.patterns.items():
            for pattern_name, pattern in patterns.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

                for match in matches:
                    element_name = match.group(1)

                    # Skip if too short or likely false positive
                    if len(element_name) < 2 or element_name in ['React', 'useState', 'useEffect']:
                        continue

                    element = self._create_element(
                        element_name=element_name,
                        element_type=element_type,
                        file_path=relative_path,
                        repo_name=repo_name,
                        match=match,
                        content=content,
                        file_type=file_type
                    )

                    if element:
                        elements.append(element)

        return elements

    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension"""
        suffix = file_path.suffix.lower()
        if suffix == '.tsx':
            return 'react-component'
        elif suffix == '.ts':
            return 'typescript'
        elif suffix == '.jsx':
            return 'react-jsx'
        elif suffix == '.js':
            return 'javascript'
        else:
            return 'unknown'

    def _create_element(self, element_name: str, element_type: str, file_path: Path,
                       repo_name: str, match: re.Match, content: str, file_type: str) -> Optional[Dict[str, Any]]:
        """Create an element dictionary from regex match"""
        try:
            # Extract surrounding context
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(content), match.end() + 500)
            context = content[start_pos:end_pos].strip()

            # Extract JSDoc comment if present
            jsdoc_match = re.search(r'/\*\*[\s\S]*?\*/', content[start_pos:match.start()])
            description = jsdoc_match.group(0) if jsdoc_match else ""
            description = re.sub(r'/\*\*|\*/|\*\s?', '', description).strip()

            # Extract dependencies (import statements)
            imports = re.findall(r'import.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            dependencies = [imp for imp in imports if not imp.startswith('.') and not imp.startswith('@types/')]

            return {
                "name": element_name,
                "type": element_type,
                "category": self._get_category(element_type, file_type),
                "file_path": str(file_path),
                "description": description or f"{element_type.title()}: {element_name}",
                "usage_examples": [context],
                "dependencies": dependencies,
                "peer_dependencies": [],
                "installation": f"# Found in {repo_name}",
                "metadata": {
                    "extractor": "typescript",
                    "repository": repo_name,
                    "file_type": file_type,
                    "line_number": content[:match.start()].count('\n') + 1,
                    "context_length": len(context),
                    "has_jsdoc": bool(jsdoc_match)
                },
                "quality_score": self._calculate_quality_score(description, context, dependencies),
                "platform": ["reactjs", "nodejs", "web"] if "react" in file_type else ["nodejs", "web"],
                "registry": repo_name
            }
        except Exception as e:
            print(f"Error creating element {element_name}: {e}")
            return None

    def _get_category(self, element_type: str, file_type: str) -> str:
        """Determine category from element type and file type"""
        if element_type == "component":
            return "ui-components"
        elif element_type == "function":
            return "utilities"
        elif element_type == "class":
            return "classes"
        elif element_type == "type":
            return "types"
        elif element_type == "constant":
            return "constants"
        else:
            return "miscellaneous"

    def _calculate_quality_score(self, description: str, context: str, dependencies: List[str]) -> float:
        """Calculate quality score for extracted element"""
        score = 0.0

        # Description quality (0.3)
        if description and len(description) > 20:
            score += 0.3
        elif description:
            score += 0.1

        # Context quality (0.3)
        if len(context) > 200:
            score += 0.3
        elif len(context) > 50:
            score += 0.2

        # Dependencies (0.2)
        if dependencies:
            score += min(0.2, len(dependencies) * 0.05)

        # Name quality (0.2)
        # (Already filtered in regex matching)
        score += 0.2

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
            "name": "typescript",
            "type": "language-based",
            "description": "TypeScript/JavaScript language-based fallback extractor",
            "supported_patterns": self.file_patterns,
            "element_types": list(self.patterns.keys()),
            "supports_any_repository": True,
            "quality": "good",
            "fallback_for": ["TypeScript", "JavaScript", "React", "Node.js"]
        }