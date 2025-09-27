#!/usr/bin/env python3
"""
SimFlo MCP RAG - GitHub CLI-based Extractor

Enhanced extractor using GitHub CLI for repository operations.
Provides better repository discovery, metadata, and efficient cloning.
"""

import json
import re
import ast
import subprocess
import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse
import logging
from urllib.parse import urlparse
from datetime import datetime

# Import from base extractor
from github_extractor import GitHubExtractor, ComponentFile, ComponentInfo


class GitHubCLIExtractor(GitHubExtractor):
    """Enhanced extractor using GitHub CLI for better repository operations"""

    def __init__(self, repo_identifier: str, output_dir: Optional[str] = None):
        """
        Initialize extractor with GitHub CLI

        Args:
            repo_identifier: GitHub repo URL or owner/repo format
            output_dir: Output directory for extracted data
        """
        # Normalize to URL format for parent class
        if not repo_identifier.startswith('http'):
            if '/' in repo_identifier and not repo_identifier.startswith('git@'):
                # Convert owner/repo to HTTPS URL
                repo_identifier = f'https://github.com/{repo_identifier}'

        # Initialize parent class
        super().__init__(repo_identifier, output_dir)

        self.repo_identifier = repo_identifier
        self.repo_info = {}
        self.quality_metrics = {}
        self.similar_repositories = []

        # Check if GitHub CLI is available
        if not self._check_gh_cli():
            self.logger.warning("GitHub CLI (gh) is not available, falling back to basic extraction")
            self.gh_cli_available = False
        else:
            self.gh_cli_available = True

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _parse_repo_identifier(self) -> Dict[str, str]:
        """Parse repository identifier to extract owner/repo"""
        # Handle different formats:
        # https://github.com/owner/repo
        # git@github.com:owner/repo.git
        # owner/repo

        if self.repo_identifier.startswith('http'):
            parsed = urlparse(self.repo_identifier)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return {'owner': path_parts[0], 'repo': path_parts[1], 'format': 'url'}
        elif self.repo_identifier.startswith('git@'):
            # SSH format
            path_parts = self.repo_identifier.split(':')[1].replace('.git', '').split('/')
            if len(path_parts) >= 2:
                return {'owner': path_parts[0], 'repo': path_parts[1], 'format': 'ssh'}
        elif '/' in self.repo_identifier:
            parts = self.repo_identifier.split('/')
            if len(parts) >= 2:
                return {'owner': parts[0], 'repo': parts[1].replace('.git', ''), 'format': 'short'}

        raise ValueError(f"Invalid repository identifier: {self.repo_identifier}")

    def _get_repository_metadata(self) -> Dict[str, Any]:
        """Get repository metadata using GitHub CLI"""
        if not self.gh_cli_available:
            return {}

        try:
            repo_info = self._parse_repo_identifier()
            owner, repo = repo_info['owner'], repo_info['repo']

            # Get repository info
            result = subprocess.run(
                ['gh', 'repo', 'view', f'{owner}/{repo}', '--json',
                 'name,description,homepage,language,createdAt,updatedAt,stargazerCount,forkCount,topics,defaultBranch'],
                capture_output=True,
                text=True,
                check=True
            )

            metadata = json.loads(result.stdout)

            # Get repository topics
            topics_result = subprocess.run(
                ['gh', 'repo', 'view', f'{owner}/{repo}', '--json', 'topics'],
                capture_output=True,
                text=True,
                check=True
            )

            topics_data = json.loads(topics_result.stdout)
            metadata['topics'] = topics_data.get('topics', [])

            # Get recent commits for activity level
            commits_result = subprocess.run(
                ['gh', 'api', f'repos/{owner}/{repo}/commits?per_page=5'],
                capture_output=True,
                text=True,
                check=True
            )

            commits_data = json.loads(commits_result.stdout)
            metadata['recent_activity'] = len(commits_data)

            return metadata

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to get repository metadata: {e}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse repository metadata: {e}")
            return {}

    def _find_similar_repositories(self) -> List[Dict[str, Any]]:
        """Find similar repositories using GitHub CLI"""
        if not self.gh_cli_available:
            return []

        try:
            repo_info = self._parse_repo_identifier()
            owner, repo = repo_info['owner'], repo_info['repo']

            # Get repository topics
            result = subprocess.run(
                ['gh', 'repo', 'view', f'{owner}/{repo}', '--json', 'topics'],
                capture_output=True,
                text=True,
                check=True
            )

            topics_data = json.loads(result.stdout)
            topics = topics_data.get('topics', [])

            if topics:
                # Search for repositories with similar topics
                topic_query = ' '.join([f'topic:{topic}' for topic in topics[:3]])  # Use top 3 topics
                search_result = subprocess.run(
                    ['gh', 'repo', 'list', '--limit', '10', '--json', 'name,owner,description,stargazerCount,language',
                     '--search', topic_query],
                    capture_output=True,
                    text=True,
                    check=True
                )

                repos = json.loads(search_result.stdout)
                # Filter out the original repository
                similar_repos = [r for r in repos if not (r['owner']['login'] == owner and r['name'] == repo)]
                return similar_repos[:5]  # Return top 5 similar repos

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to find similar repositories: {e}")

        return []

    def _clone_repository_with_gh(self) -> Path:
        """Clone repository using GitHub CLI"""
        if not self.gh_cli_available:
            # Fall back to parent method
            return self._clone_repository()

        self.temp_dir = tempfile.mkdtemp(prefix=f'github_cli_extractor_{self.repo_identifier.replace("/", "_")}_')
        temp_path = Path(self.temp_dir)

        self.logger.info(f"Cloning {self.repo_identifier} to {temp_path}")

        try:
            # Use GitHub CLI for authenticated cloning
            repo_info = self._parse_repo_identifier()
            owner, repo = repo_info['owner'], repo_info['repo']

            result = subprocess.run(
                ['gh', 'repo', 'clone', f'{owner}/{repo}', str(temp_path)],
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info(f"Repository cloned successfully using GitHub CLI")
            return temp_path

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"GitHub CLI clone failed, falling back to git: {e}")
            # Fall back to parent method
            return self._clone_repository()

    def _analyze_repository_quality(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository quality metrics"""
        quality_metrics = {
            'has_package_json': False,
            'has_readme': False,
            'has_tests': False,
            'has_typescript': False,
            'file_count': 0,
            'test_file_count': 0,
            'typescript_file_count': 0,
            'documentation_score': 0
        }

        try:
            # Count files and check for key files
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    quality_metrics['file_count'] += 1

                    if file_path.name == 'package.json':
                        quality_metrics['has_package_json'] = True
                    elif file_path.name.lower().startswith('readme'):
                        quality_metrics['has_readme'] = True
                    elif file_path.suffix in ['.test.ts', '.test.js', '.spec.ts', '.spec.js']:
                        quality_metrics['test_file_count'] += 1
                        quality_metrics['has_tests'] = True
                    elif file_path.suffix in ['.ts', '.tsx']:
                        quality_metrics['typescript_file_count'] += 1
                        quality_metrics['has_typescript'] = True

            # Calculate documentation score
            if quality_metrics['has_readme']:
                quality_metrics['documentation_score'] += 30
            if quality_metrics['has_package_json']:
                quality_metrics['documentation_score'] += 20
            if quality_metrics['has_tests']:
                quality_metrics['documentation_score'] += 25
            if quality_metrics['has_typescript']:
                quality_metrics['documentation_score'] += 25

        except Exception as e:
            self.logger.warning(f"Error analyzing repository quality: {e}")

        return quality_metrics

    def extract_components(self) -> List[ComponentInfo]:
        """Main method to extract components from repository using GitHub CLI"""
        self.logger.info(f"Starting enhanced extraction from {self.repo_identifier}")

        try:
            # Get repository metadata
            self.repo_info = self._get_repository_metadata()
            self.logger.info(f"Repository metadata: {self.repo_info.get('name', 'Unknown')}")

            # Clone repository using enhanced method
            repo_path = self._clone_repository_with_gh()

            # Analyze repository quality
            self.quality_metrics = self._analyze_repository_quality(repo_path)
            self.logger.info(f"Repository quality score: {self.quality_metrics.get('documentation_score', 0)}")

            # Find similar repositories
            self.similar_repositories = self._find_similar_repositories()
            if self.similar_repositories:
                self.logger.info(f"Found {len(self.similar_repositories)} similar repositories")

            # Continue with parent extraction logic
            # Use parent class methods for the actual component extraction
            package_json = self._find_package_json(repo_path)
            readme_content = self._find_readme(repo_path)

            # Extract basic repository info
            repo_info_dict = {
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
                    peer_dependencies=list(repo_info_dict['peerDependencies'].keys()),
                    dev_dependencies=list(repo_info_dict['devDependencies'].keys()),
                    examples=examples,
                    tags=tags,
                    props_info=props_info,
                    usage_patterns=usage_patterns[:5],  # Limit to 5 patterns
                    source_repository=self.repo_url,
                    repository_metadata=self.repo_info
                )

                self.components.append(component)

            self.logger.info(f"Extracted {len(self.components)} components")
            return self.components

        finally:
            # Clean up temporary directory
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)

    def save_to_json(self, output_path: Optional[str] = None, include_metadata: bool = True) -> str:
        """Save extracted components to JSON file with enhanced metadata"""
        if output_path is None:
            repo_info = self._parse_repo_identifier()
            output_path = self.output_dir / f'{repo_info["repo"]}_components.json'

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        components_data = []
        for component in self.components:
            component_dict = asdict(component)
            # Convert ComponentFile objects to dicts
            component_dict['files'] = [asdict(f) for f in component.files]
            components_data.append(component_dict)

        # Create enhanced output with repository metadata
        output_data = {
            'repository': self.repo_info,
            'extraction_metadata': {
                'extracted_at': datetime.now().isoformat(),
                'extractor_version': 'github-cli-enhanced',
                'total_components': len(self.components),
                'quality_metrics': self.quality_metrics,
                'similar_repositories': self.similar_repositories
            },
            'components': components_data
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Enhanced components data saved to {output_file}")
        return str(output_file)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Enhanced GitHub repository extractor using GitHub CLI')
    parser.add_argument('repo_identifier', help='GitHub repository URL or owner/repo')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--metadata-only', action='store_true', help='Only extract repository metadata')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        extractor = GitHubCLIExtractor(args.repo_identifier, args.output)

        if args.metadata_only:
            # Only extract metadata
            metadata = extractor._get_repository_metadata()
            similar_repos = extractor._find_similar_repositories()

            output_data = {
                'repository': metadata,
                'similar_repositories': similar_repos,
                'extraction_metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'extractor_version': 'github-cli-metadata-only'
                }
            }

            output_path = args.output or f"{extractor._parse_repo_identifier()['repo']}_metadata.json"
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"Repository metadata saved to {output_path}")
        else:
            # Full extraction
            components = extractor.extract_components()
            output_file = extractor.save_to_json(args.output, include_metadata=True)
            print(f"Successfully extracted {len(components)} components to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()