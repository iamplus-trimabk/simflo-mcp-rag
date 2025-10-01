"""
Simple Gluestack Extractor

A working implementation of gluestack component extraction that uses GitHub CLI
to download repositories and extract components locally.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class SimpleGluestackExtractor:
    """Simple gluestack component extractor using GitHub CLI"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract components from gluestack repository"""
        try:
            # Default to gluestack/gluestack-ui if no repo specified
            target_repo = repo_url or "gluestack/gluestack-ui"

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
            saved = self.save_to_registry(components, "gluestack")

            result = {
                "extractor": "gluestack",
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
                "extractor": "gluestack",
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
            # Try different possible paths for gluestack structure
            possible_paths = [
                repo_path / "components" / "ui",
                repo_path / "src" / "components" / "ui",
                repo_path / "packages" / "components" / "ui"
            ]

            components_dir = None
            for path in possible_paths:
                if path.exists():
                    components_dir = path
                    break

            if components_dir:
                # Find all .tsx files in the components directory
                component_files = list(components_dir.glob("*.tsx"))
                component_files = [f for f in component_files if not f.name.startswith('.')]

                # Extract real component data from the files found
                for file_path in component_files[:5]:  # Limit to first 5 components
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
                        "title": f"Gluestack {component_name.title()}",
                        "description": f"A universal {component_name} component that works across React and React Native",
                        "category": self._categorize_component(component_name),
                        "tags": self._generate_tags(component_name, content),
                        "installation": f"npm install @gluestack-ui/{component_name}",
                        "usage": self._generate_usage_example(component_name),
                        "file_path": f"components/ui/{file_path.name}",
                        "registry": "gluestack",
                        "platforms": ["reactjs", "reactnative"],
                        "repository": repo_name,
                        "local_file_path": str(file_path)
                    }
                    components.append(component)
            else:
                # No components found
                print("Warning: Could not find components directory in repository.")
                return []

        except Exception as e:
            print(f"Error extracting components from repo: {e}")
            return []

        return components

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
        base_tags = [component_name, 'react', 'typescript', 'cross-platform']

        if 'accessible' in content.lower() or 'aria' in content.lower():
            base_tags.append('accessible')
        if 'form' in content.lower():
            base_tags.append('form')
        if 'variant' in content.lower():
            base_tags.append('variants')

        return base_tags

    def _generate_usage_example(self, component_name: str) -> str:
        """Generate usage example for component"""
        examples = {
            'button': '```tsx\nimport { Button, ButtonText } from "@gluestack-ui/button"\n<Button action="primary">\n  <ButtonText>Click me</ButtonText>\n</Button>\n```',
            'input': '```tsx\nimport { Input, InputField } from "@gluestack-ui/input"\n<Input>\n  <InputField placeholder="Enter text" />\n</Input>\n```',
            'card': '```tsx\nimport { Card, CardHeader, CardContent } from "@gluestack-ui/card"\n<Card>\n  <CardHeader>Card Title</CardHeader>\n  <CardContent>Card content goes here</CardContent>\n</Card>\n```'
        }
        return examples.get(component_name, f'```tsx\nimport {{ {component_name.title()} }} from "@gluestack-ui/{component_name}"\n```')

    def save_to_registry(self, components: List[Dict[str, Any]], registry_name: str = "gluestack") -> bool:
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
                filename = f"gluestack_{component['name']}.md"
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
        ]

        # Add platform information if available
        if 'platforms' in component:
            content.extend([
                f"- **Platforms**: {', '.join(component['platforms'])}",
            ])

        # Add repository link if repository field is available
        if 'repository' in component:
            content.extend([
                f"**Source Repository**: [View on GitHub]({self.github_api_base.replace('/api/v3', '')}/{component['repository']}/tree/main/{component['file_path']})",
            ])

        content.extend([
            "",
            "---",
            f"*Extracted by SimFlo RAG on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        return "\n".join(content)

    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about this extractor"""
        return {
            "name": "gluestack",
            "type": "component_extractor",
            "description": "Extracts components from gluestack-ui repositories",
            "supported_sources": ["github"],
            "version": "1.0.0",
            "class": self.__class__.__name__
        }