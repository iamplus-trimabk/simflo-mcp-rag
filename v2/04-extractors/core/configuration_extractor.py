"""
Configuration Language-Based Extractor

A fallback extractor for configuration files in any repository.
Extracts package.json, tsconfig.json, requirements.txt, setup.py, and other config files.
"""

import re
import json
import subprocess
import os
import configparser
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class ConfigurationExtractor:
    """Language-based extractor for configuration files"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

        # File patterns to analyze
        self.file_patterns = [
            "**/package.json", "**/package-lock.json",
            "**/tsconfig.json", "**/jsconfig.json",
            "**/requirements.txt", "**/requirements*.txt",
            "**/setup.py", "**/pyproject.toml",
            "**/Pipfile", "**/poetry.lock",
            "**/Cargo.toml", "**/Cargo.lock",
            "**/composer.json", "**/composer.lock",
            "**/Gemfile", "**/Gemfile.lock",
            "**/go.mod", "**/go.sum",
            "**/pom.xml", "**/build.gradle",
            "**/Dockerfile", "**/docker-compose.yml",
            "**/.env.example", "**/.env.sample",
            "**/vite.config.ts", "**/vite.config.js",
            "**/webpack.config.js", "**/rollup.config.js",
            "**/.eslintrc*", "**/.prettierrc*",
            "**/jest.config.js", "**/jest.config.ts"
        ]

        # Configuration file type handlers
        self.parsers = {
            "json": self._parse_json_config,
            "toml": self._parse_toml_config,
            "python": self._parse_python_config,
            "xml": self._parse_xml_config,
            "docker": self._parse_docker_config,
            "yaml": self._parse_yaml_config,
            "text": self._parse_text_config
        }

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract configuration from any repository"""
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

            # Extract configuration from the repository
            configs = self._extract_configurations(repo_name, repo_path)

            # Save configurations to registry files
            saved = self.save_to_registry(configs, repo_name)

            result = {
                "extractor": "configuration",
                "repository": repo_name,
                "repository_url": repo_url,
                "local_path": str(repo_path),
                "timestamp": datetime.now().isoformat(),
                "configurations_found": len(configs),
                "configurations": configs,
                "saved_to_registry": saved,
                "repo_info": repo_info,
                "file_patterns": self.file_patterns,
                "config_types": list(set(config.get("config_type", "unknown") for config in configs))
            }

            return result

        except Exception as e:
            return {
                "extractor": "configuration",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _parse_repo_url(self, url: str) -> Optional[str]:
        """Parse GitHub URL to get repository name"""
        patterns = [
            r'github\.com/([^/]+/[^/]+?)(?:\.git)?/?$',
            r'([^/]+/[^/]+)$',
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
                return {
                    "name": repo_name,
                    "description": f"{repo_name} repository",
                    "stargazerCount": 0,
                    "forkCount": 0,
                    "createdAt": "unknown",
                    "updatedAt": "unknown",
                    "primaryLanguage": {"name": "Configuration"}
                }
        except Exception:
            return None

    def _extract_configurations(self, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract configuration from files"""
        configurations = []

        # Find all configuration files
        files = []
        for pattern in self.file_patterns:
            files.extend(repo_path.glob(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        for file_path in files:
            try:
                # Skip common directories to ignore
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', 'venv', 'env', '.venv', 'site-packages', 'build', 'dist', '__pycache__']):
                    continue

                config = self._extract_from_file(file_path, repo_name, repo_path)
                if config:
                    configurations.append(config)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return configurations

    def _extract_from_file(self, file_path: Path, repo_name: str, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from a single configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        # Skip empty files
        if not content.strip():
            return None

        relative_path = file_path.relative_to(repo_path)
        file_name = file_path.name.lower()
        file_extension = file_path.suffix.lower()

        # Determine parser and config type
        parser, config_type = self._determine_parser(file_name, file_extension)

        # Parse configuration
        try:
            parsed_data = parser(content, file_path)
        except Exception as e:
            print(f"Error parsing {file_path} with {parser.__name__}: {e}")
            # Fallback to text parsing
            parsed_data = self._parse_text_config(content, file_path)

        return self._create_config_element(
            parsed_data, file_path, relative_path, repo_name, config_type
        )

    def _determine_parser(self, file_name: str, file_extension: str) -> tuple:
        """Determine the appropriate parser based on file name and extension"""
        # JSON files
        if file_extension in ['.json'] or 'package.json' in file_name:
            return self._parse_json_config, "json"

        # TOML files
        elif file_extension in ['.toml']:
            return self._parse_toml_config, "toml"

        # Python files
        elif file_name in ['setup.py', 'pipfile'] or file_extension == '.py':
            return self._parse_python_config, "python"

        # XML files
        elif file_extension in ['.xml']:
            return self._parse_xml_config, "xml"

        # YAML files
        elif file_extension in ['.yml', '.yaml'] or 'docker-compose' in file_name:
            return self._parse_yaml_config, "yaml"

        # Docker files
        elif 'dockerfile' in file_name:
            return self._parse_docker_config, "docker"

        # Text files (requirements.txt, etc.)
        elif file_extension in ['.txt', '.env', '.md'] or 'requirements' in file_name:
            return self._parse_text_config, "text"

        # Default to text
        else:
            return self._parse_text_config, "text"

    def _parse_json_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse JSON configuration files"""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {file_path}: {e}")
            return {"error": "Invalid JSON", "raw_content": content[:500]}

    def _parse_toml_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse TOML configuration files"""
        try:
            # Try to import tomli (Python 3.11+ has tomllib)
            try:
                import tomllib
                import io
                return tomllib.load(io.StringIO(content))
            except ImportError:
                try:
                    import toml
                    return toml.loads(content)
                except ImportError:
                    # Fallback: simple TOML parsing
                    return self._simple_toml_parse(content)
        except Exception as e:
            print(f"Error parsing TOML in {file_path}: {e}")
            return {"error": "TOML parsing failed", "raw_content": content[:500]}

    def _simple_toml_parse(self, content: str) -> Dict[str, Any]:
        """Simple TOML parser as fallback"""
        result = {}
        current_section = None

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Section headers
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                if current_section not in result:
                    result[current_section] = {}
                continue

            # Key-value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().strip('"\'')
                value = value.strip().strip('"\'')

                if current_section:
                    result[current_section][key] = value
                else:
                    result[key] = value

        return result

    def _parse_python_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse Python configuration files"""
        try:
            # For setup.py, try to extract setup() arguments
            if 'setup.py' in file_path.name:
                return self._parse_setup_py(content)
            elif 'pipfile' in file_path.name:
                return self._parse_pipfile(content)
            else:
                return {"type": "python-config", "raw_content": content[:1000]}
        except Exception as e:
            print(f"Error parsing Python config in {file_path}: {e}")
            return {"error": "Python config parsing failed", "raw_content": content[:500]}

    def _parse_setup_py(self, content: str) -> Dict[str, Any]:
        """Parse setup.py file"""
        result = {"type": "setup.py"}

        # Extract common setup() arguments
        patterns = {
            "name": r'name\s*=\s*["\']([^"\']+)["\']',
            "version": r'version\s*=\s*["\']([^"\']+)["\']',
            "description": r'description\s*=\s*["\']([^"\']+)["\']',
            "author": r'author\s*=\s*["\']([^"\']+)["\']',
            "packages": r'packages\s*=\s*\[([^\]]+)\]',
            "install_requires": r'install_requires\s*=\s*\[([^\]]+)\]',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                value = match.group(1)
                # Clean up list values
                if key in ["packages", "install_requires"]:
                    value = [item.strip().strip('"\'') for item in value.split(',')]
                result[key] = value

        return result

    def _parse_pipfile(self, content: str) -> Dict[str, Any]:
        """Parse Pipfile"""
        result = {"type": "Pipfile", "packages": {}, "dev-packages": {}}

        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                continue

            if current_section in ['packages', 'dev-packages'] and '=' in line:
                package, version = line.split('=', 1)
                package = package.strip()
                version = version.strip().strip('"\'')
                result[current_section][package] = version

        return result

    def _parse_xml_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse XML configuration files"""
        try:
            root = ET.fromstring(content)
            return {
                "type": "xml",
                "root_tag": root.tag,
                "attributes": root.attrib,
                "text": root.text.strip() if root.text else None,
                "children": [{child.tag: child.text.strip() if child.text else None} for child in root]
            }
        except ET.ParseError as e:
            print(f"Error parsing XML in {file_path}: {e}")
            return {"error": "XML parsing failed", "raw_content": content[:500]}

    def _parse_docker_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse Docker configuration files"""
        result = {"type": "docker", "instructions": []}

        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract Docker instructions
                if any(line.startswith(cmd) for cmd in ['FROM', 'RUN', 'COPY', 'ADD', 'WORKDIR', 'CMD', 'ENTRYPOINT', 'EXPOSE', 'ENV']):
                    result["instructions"].append(line)

        return result

    def _parse_yaml_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse YAML configuration files"""
        result = {"type": "yaml", "raw_content": content[:1000]}

        # Try to import yaml parser
        try:
            import yaml
            try:
                parsed = yaml.safe_load(content)
                result.update(parsed)
                return result
            except Exception as e:
                print(f"YAML parsing failed: {e}")
        except ImportError:
            print("PyYAML not available, using simple parsing")

        # Simple YAML parsing as fallback
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"\'')

        return result

    def _parse_text_config(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse text-based configuration files"""
        result = {"type": "text", "lines": []}

        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                result["lines"].append(line)

        # Try to extract dependencies from requirements.txt style files
        if 'requirements' in file_path.name:
            result["dependencies"] = []
            for line in result["lines"]:
                if line and not line.startswith('#'):
                    # Clean up dependency specifications
                    dep = line.split('#')[0].strip()  # Remove comments
                    if dep:
                        result["dependencies"].append(dep)

        return result

    def _create_config_element(self, parsed_data: Dict[str, Any], file_path: Path,
                              relative_path: Path, repo_name: str, config_type: str) -> Dict[str, Any]:
        """Create a configuration element"""
        file_name = file_path.name

        # Extract key information based on config type
        summary = self._extract_config_summary(parsed_data, file_name, config_type)
        dependencies = self._extract_dependencies(parsed_data, config_type)

        # Determine platform based on config type and content
        platforms = self._determine_platforms(parsed_data, config_type)

        return {
            "name": file_name,
            "type": "configuration",
            "category": "configuration",
            "file_path": str(relative_path),
            "description": summary or f"{config_type.title()} configuration: {file_name}",
            "usage_examples": [str(parsed_data)],
            "dependencies": dependencies,
            "peer_dependencies": [],
            "installation": f"# Configuration file from {repo_name}",
            "metadata": {
                "extractor": "configuration",
                "repository": repo_name,
                "config_type": config_type,
                "file_extension": file_path.suffix.lower(),
                "file_size": len(str(parsed_data)),
                "has_dependencies": len(dependencies) > 0,
                "dependency_count": len(dependencies),
                "platforms": platforms,
                "raw_data_keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else []
            },
            "quality_score": self._calculate_config_quality(parsed_data, dependencies),
            "platform": platforms,
            "registry": repo_name
        }

    def _extract_config_summary(self, parsed_data: Dict[str, Any], file_name: str, config_type: str) -> str:
        """Extract a summary from the configuration data"""
        if "error" in parsed_data:
            return f"Configuration file with parsing errors: {file_name}"

        summaries = {
            "package.json": f"Node.js package configuration: {parsed_data.get('name', 'Unknown')}",
            "tsconfig.json": "TypeScript compiler configuration",
            "requirements.txt": f"Python dependencies ({len(parsed_data.get('dependencies', []))} packages)",
            "setup.py": f"Python package setup: {parsed_data.get('name', 'Unknown')}",
            "pyproject.toml": "Python project configuration",
            "Dockerfile": f"Docker container configuration ({len(parsed_data.get('instructions', []))} instructions)",
            "docker-compose.yml": "Docker Compose configuration"
        }

        return summaries.get(file_name, f"{config_type.title()} configuration file")

    def _extract_dependencies(self, parsed_data: Dict[str, Any], config_type: str) -> List[str]:
        """Extract dependencies from configuration"""
        dependencies = []

        if config_type == "json":
            # package.json dependencies
            for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                if dep_type in parsed_data and isinstance(parsed_data[dep_type], dict):
                    dependencies.extend(parsed_data[dep_type].keys())

        elif config_type == "toml":
            # pyproject.toml dependencies
            if "dependencies" in parsed_data:
                dependencies.extend(parsed_data["dependencies"].keys())

        elif config_type == "python":
            # setup.py or requirements.txt
            if "install_requires" in parsed_data:
                dependencies.extend(parsed_data["install_requires"])
            elif "dependencies" in parsed_data:
                dependencies.extend(parsed_data["dependencies"])

        elif config_type == "text":
            # requirements.txt style
            if "dependencies" in parsed_data:
                dependencies.extend(parsed_data["dependencies"])

        return [dep for dep in dependencies if dep and not dep.startswith('#')]

    def _determine_platforms(self, parsed_data: Dict[str, Any], config_type: str) -> List[str]:
        """Determine relevant platforms based on configuration"""
        platforms = []

        if config_type == "json":
            # Node.js projects
            platforms.extend(["nodejs", "javascript", "web"])

            # Check for React
            if "react" in str(parsed_data).lower():
                platforms.extend(["reactjs", "frontend"])

        elif config_type == "toml":
            # Python projects
            platforms.extend(["python", "backend"])

        elif config_type == "python":
            # Python projects
            platforms.extend(["python", "backend"])

        elif config_type in ["docker", "yaml"]:
            # Containerized projects
            platforms.extend(["docker", "backend"])
            if "node" in str(parsed_data).lower():
                platforms.extend(["nodejs"])
            elif "python" in str(parsed_data).lower():
                platforms.extend(["python"])

        return list(set(platforms)) or ["backend"]

    def _calculate_config_quality(self, parsed_data: Dict[str, Any], dependencies: List[str]) -> float:
        """Calculate quality score for configuration"""
        score = 0.0

        # Data quality (0.4)
        if "error" not in parsed_data:
            score += 0.2
            if isinstance(parsed_data, dict) and len(parsed_data) > 3:
                score += 0.2

        # Dependencies (0.3)
        if dependencies:
            score += min(0.3, len(dependencies) * 0.05)

        # Completeness (0.3)
        if isinstance(parsed_data, dict):
            common_fields = ["name", "version", "description"]
            found_fields = sum(1 for field in common_fields if field in parsed_data)
            score += min(0.3, found_fields * 0.1)

        return min(score, 1.0)

    def save_to_registry(self, configurations: List[Dict[str, Any]], repo_name: str) -> Dict[str, int]:
        """Save configurations to registry files"""
        # Sanitize repository name for file system compatibility
        safe_repo_name = repo_name.replace('/', '-').replace('\\', '-')
        registry_dir = Path(f"v2/core/00-rag-registry/registries/{safe_repo_name}/files")
        saved_counts = {}

        try:
            # Create configuration directory
            config_dir = registry_dir / "configuration"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Group configurations by type
            by_type = {}
            for config in configurations:
                config_type = config.get("config_type", "unknown")
                if config_type not in by_type:
                    by_type[config_type] = []
                by_type[config_type].append(config)

            # Save each configuration type to its own file
            for config_type, type_configs in by_type.items():
                output_file = config_dir / f"{safe_repo_name}-{config_type}-configs.json"

                # Load existing data if file exists
                existing_data = []
                if output_file.exists():
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        existing_data = []

                # Add new configurations
                existing_data.extend(type_configs)

                # Save updated data
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, default=str)

                saved_counts[config_type] = len(type_configs)

            return saved_counts

        except Exception as e:
            print(f"Error saving to registry: {e}")
            return {}

    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about this extractor"""
        return {
            "name": "configuration",
            "type": "language-based",
            "description": "Configuration language-based fallback extractor",
            "supported_patterns": self.file_patterns,
            "config_types": [
                "json", "toml", "python", "xml", "docker", "yaml", "text"
            ],
            "supports_any_repository": True,
            "quality": "good",
            "fallback_for": [
                "Node.js", "Python", "Docker", "Java", "Ruby",
                "Go", "Rust", "General configuration files"
            ],
            "features": [
                "Multi-format parsing", "Dependency extraction",
                "Platform detection", "Quality scoring"
            ]
        }