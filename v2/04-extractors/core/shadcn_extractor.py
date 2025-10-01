"""
Simple Shadcn Extractor

A working implementation of shadcn component extraction that uses GitHub CLI
to download repositories and extract components locally.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class SimpleShadcnExtractor:
    """Simple shadcn component extractor using GitHub CLI"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract components from shadcn repository"""
        try:
            # Default to the official shadcn-ui repository if no repo specified
            target_repo = repo_url or "shadcn-ui/ui"

            # Ensure GitHub directory exists
            self.github_dir.mkdir(parents=True, exist_ok=True)

            # Download repository using GitHub CLI if not present locally
            repo_path = self.github_dir / target_repo
            if not repo_path.exists():
                print(f"Downloading {target_repo} using GitHub CLI...")
                clone_cmd = ["gh", "repo", "clone", target_repo, str(repo_path)]
                result = subprocess.run(clone_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return {"error": f"Failed to clone repository: {result.stderr}"}
            else:
                print(f"Using local repository at {repo_path}")

            # Get repository information
            repo_info = self._get_repo_info(target_repo, repo_path)
            if not repo_info:
                return {"error": f"Repository {target_repo} not found"}

            # Get component files from the local repository
            components = self._extract_components(target_repo, repo_path)

            # Save components to registry files
            saved = self.save_to_registry(components, "shadcn")

            result = {
                "extractor": "shadcn",
                "repository": target_repo,
                "local_path": str(repo_path),
                "timestamp": datetime.now().isoformat(),
                "components_found": len(components),
                "components": components,
                "saved_to_registry": saved,
                "repo_info": repo_info
            }

            return result

        except Exception as e:
            return {
                "extractor": "shadcn",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_repo_info(self, repo_name: str, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Get repository information from local repository or GitHub CLI"""
        try:
            # Try to get repository info using GitHub CLI
            cmd = ["gh", "repo", "view", repo_name, "--json", "name,description,stargazerCount,forkCount,createdAt,updatedAt,owner"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Fallback to basic info from local repo
                return {
                    "name": repo_name,
                    "description": f"{repo_name} repository",
                    "stargazerCount": 0,
                    "forkCount": 0,
                    "createdAt": "unknown",
                    "updatedAt": "unknown"
                }
        except Exception:
            return None

    def _extract_components(self, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract component information from local repository"""
        components = []

        try:
            # Look for component files in the local repository
            # Try different possible paths for component structure
            possible_paths = [
                repo_path / "components" / "ui",
                repo_path / "apps" / "www" / "components" / "ui",
                repo_path / "app" / "components" / "ui",
                repo_path / "src" / "components" / "ui"
            ]

            components_dir = None
            for path in possible_paths:
                if path.exists():
                    components_dir = path
                    break

            if not components_dir:
                # If no standard components directory, look for any .tsx files that might be components
                print(f"Standard component directories not found, searching for .tsx files...")
                # Create a fake components directory for searching
                components_dir = repo_path

            if components_dir.exists():
                # Find all .tsx files in the components directory
                if components_dir == repo_path:
                    # Search recursively if we're using the repo root
                    component_files = list(repo_path.rglob("*.tsx"))
                else:
                    # Search only in the specific directory
                    component_files = list(components_dir.glob("*.tsx"))

                component_files = [f for f in component_files if not f.name.startswith('.') and not f.name.startswith('test')]
                component_files = [f for f in component_files if 'node_modules' not in str(f) and 'test' not in str(f).lower()]

                # Extract real component data from the files found
                for file_path in component_files[:10]:  # Limit to first 10 components
                    component_name = file_path.stem.replace('index.', '')

                    # Read file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception:
                        content = ""

                    # Create component entry
                    component = {
                        "name": component_name,
                        "title": f"{component_name.title()} Component",
                        "description": f"A {component_name} component from shadcn-ui",
                        "category": self._categorize_component(component_name),
                        "tags": self._generate_tags(component_name, content),
                        "installation": self._get_installation_command(component_name),
                        "usage": self._generate_usage_example(component_name),
                        "file_path": f"components/ui/{file_path.name}",
                        "registry": "shadcn",
                        "repository": repo_name,
                        "local_file_path": str(file_path)
                    }
                    components.append(component)
            else:
                # Fallback to essential components if directory not found
                components = self._get_essential_components(repo_name)

        except Exception as e:
            print(f"Error extracting components from repo: {e}")
            # Fallback to essential components
            components = self._get_essential_components(repo_name)

        return components

    def _get_essential_components(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get essential components as fallback - no sample data"""
        # Return empty list when local repository is not accessible
        # This ensures we only work with real repositories
        print("Warning: Could not access local repository. No components extracted.")
        return []

    def _categorize_component(self, component_name: str) -> str:
        """Categorize component based on its name"""
        if component_name in ['input', 'textarea', 'select', 'checkbox', 'radio']:
            return 'forms'
        elif component_name in ['button', 'card', 'dialog', 'sheet', 'dropdown']:
            return 'ui'
        elif component_name in ['table', 'list', 'grid', 'flex']:
            return 'layout'
        else:
            return 'ui'

    def _generate_tags(self, component_name: str, content: str) -> List[str]:
        """Generate tags for component"""
        base_tags = [component_name, 'react', 'typescript']

        if 'accessible' in content.lower() or 'aria' in content.lower():
            base_tags.append('accessible')
        if 'form' in content.lower():
            base_tags.append('form')
        if 'variant' in content.lower():
            base_tags.append('variants')

        return base_tags

    def _get_installation_command(self, component_name: str) -> str:
        """Get installation command for component"""
        install_commands = {
            'button': 'npm install @radix-ui/react-slot',
            'dialog': 'npm install @radix-ui/react-dialog',
            'dropdown': 'npm install @radix-ui/react-dropdown-menu',
            'select': 'npm install @radix-ui/react-select',
            'checkbox': 'npm install @radix-ui/react-checkbox',
            'radio': 'npm install @radix-ui/react-radio-group'
        }
        return install_commands.get(component_name, 'No additional dependencies')

    def _generate_usage_example(self, component_name: str) -> str:
        """Generate usage example for component"""
        examples = {
            'button': '```tsx\nimport { Button } from "@/components/ui/button"\n<Button variant="default">Click me</Button>\n```',
            'card': '```tsx\nimport { Card, CardHeader, CardContent } from "@/components/ui/card"\n<Card><CardHeader>Title</CardHeader><CardContent>Content</CardContent></Card>\n```',
            'input': '```tsx\nimport { Input } from "@/components/ui/input"\n<Input type="text" placeholder="Enter text" />\n```'
        }
        return examples.get(component_name, f'```tsx\nimport {{ {component_name.title()} }} from "@/components/ui/{component_name}"\n```')

    def save_to_registry(self, components: List[Dict[str, Any]], registry_name: str = "shadcn") -> bool:
        """Save extracted components to registry files"""
        try:
            from pathlib import Path
            import os

            # Get the registry files directory
            registry_dir = Path(__file__).parent.parent.parent / "core" / "00-rag-registry" / "registries" / registry_name / "files" / "components"
            registry_dir.mkdir(parents=True, exist_ok=True)

            saved_files = []

            for component in components:
                # Create markdown file for each component
                filename = f"shadcn_{component['name']}.md"
                filepath = registry_dir / filename

                # Generate markdown content
                markdown_content = self._generate_component_markdown(component)

                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)

                saved_files.append(str(filepath))

            print(f"Saved {len(components)} components to {registry_dir}")
            return True

        except Exception as e:
            print(f"Error saving to registry: {e}")
            return False

    def _generate_component_markdown(self, component: Dict[str, Any]) -> str:
        """Generate markdown content for a component"""
        content = [
            f"# {component['title']}",
            "",
            component['description'],
            "",
            "## Installation",
            "",
            f"```bash",
            component['installation'],
            "```",
            "",
            "## Usage",
            "",
            component['usage'],
            "",
            "## Component Details",
            "",
            f"- **Name**: {component['name']}",
            f"- **Category**: {component['category']}",
            f"- **Tags**: {', '.join(component['tags'])}",
            f"- **File Path**: {component['file_path']}",
            f"- **Registry**: {component['registry']}",
            "",
            f"**Source Repository**: [View on GitHub](https://github.com/{component['repository']}/tree/main/{component['file_path']})",
            "",
            "---",
            f"*Extracted by SimFlo RAG on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ]

        return "\n".join(content)

    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about this extractor"""
        return {
            "name": "shadcn",
            "type": "component_extractor",
            "description": "Extracts components from shadcn-ui repositories",
            "supported_sources": ["github"],
            "version": "1.0.0",
            "class": self.__class__.__name__
        }