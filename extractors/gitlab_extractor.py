#!/usr/bin/env python3
"""
GitLab Extractor for Component Registry

This extractor handles component extraction from GitLab repositories,
including support for self-hosted GitLab instances and private repositories.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import aiohttp
from datetime import datetime

from .base_extractor import BaseExtractor, ExtractionResult
from models import Component, ComponentCategory, ComponentType

@dataclass
class GitLabRepoInfo:
    """GitLab repository information"""
    project_id: int
    project_path: str
    default_branch: str
    http_url_to_repo: str
    visibility: str
    last_activity_at: datetime

class GitLabExtractor(BaseExtractor):
    """Extractor for GitLab-based component registries"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.api_url = source_config.get('api_url', 'https://gitlab.com/api/v4')
        self.project_path = source_config.get('project_path')
        self.repo_slug = source_config.get('repo_slug')  # Alternative to project_path
        self.access_token = source_config.get('access_token')
        self.branch = source_config.get('branch', 'main')
        self.registry_file = source_config.get('registry_file')

        # Extract project info from URL if not provided
        if not self.project_path and self.source_config.get('url'):
            self.project_path = self._extract_project_path_from_url(self.source_config['url'])

        if not self.project_path and not self.repo_slug:
            raise ValueError("GitLab source requires either project_path, repo_slug, or URL")

        self.session: Optional[aiohttp.ClientSession] = None
        self.repo_info: Optional[GitLabRepoInfo] = None
        self.logger = logging.getLogger(__name__)

    def _extract_project_path_from_url(self, url: str) -> Optional[str]:
        """Extract GitLab project path from URL"""
        # Handle both gitlab.com and self-hosted URLs
        parsed = urlparse(url)

        # Remove .git suffix and extract path
        path = parsed.path
        if path.endswith('.git'):
            path = path[:-4]

        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]

        return path if path else None

    async def __aenter__(self):
        """Initialize aiohttp session"""
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        self.session = aiohttp.ClientSession(headers=headers)

        # Get repository information
        await self._fetch_repository_info()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up aiohttp session"""
        if self.session:
            await self.session.close()

    async def _fetch_repository_info(self) -> GitLabRepoInfo:
        """Fetch repository information from GitLab API"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        # Try project_path first, then repo_slug
        project_identifier = self.project_path or self.repo_slug

        # URL encode the project path for API calls
        encoded_project = project_identifier.replace('/', '%2F')

        try:
            async with self.session.get(f"{self.api_url}/projects/{encoded_project}") as response:
                if response.status == 200:
                    data = await response.json()

                    self.repo_info = GitLabRepoInfo(
                        project_id=data['id'],
                        project_path=data['path_with_namespace'],
                        default_branch=data['default_branch'],
                        http_url_to_repo=data['http_url_to_repo'],
                        visibility=data['visibility'],
                        last_activity_at=datetime.fromisoformat(data['last_activity_at'].replace('Z', '+00:00'))
                    )

                    self.logger.info(f"Fetched GitLab repo info: {self.repo_info.project_path}")
                    return self.repo_info
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch GitLab repo info: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"Error fetching GitLab repository info: {e}")
            raise

    async def _fetch_file_content(self, file_path: str, ref: Optional[str] = None) -> Optional[str]:
        """Fetch file content from GitLab repository"""
        if not self.session or not self.repo_info:
            raise RuntimeError("Session or repository info not initialized")

        ref = ref or self.branch or self.repo_info.default_branch
        encoded_project = self.repo_info.project_path.replace('/', '%2F')
        encoded_file_path = file_path.replace('/', '%2F')

        try:
            async with self.session.get(
                f"{self.api_url}/projects/{encoded_project}/repository/files/{encoded_file_path}/raw",
                params={'ref': ref}
            ) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 404:
                    self.logger.warning(f"File not found: {file_path}")
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch file {file_path}: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"Error fetching file {file_path}: {e}")
            return None

    async def _fetch_directory_contents(self, dir_path: str, ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch directory contents from GitLab repository"""
        if not self.session or not self.repo_info:
            raise RuntimeError("Session or repository info not initialized")

        ref = ref or self.branch or self.repo_info.default_branch
        encoded_project = self.repo_info.project_path.replace('/', '%2F')
        encoded_dir_path = dir_path.replace('/', '%2F')

        try:
            async with self.session.get(
                f"{self.api_url}/projects/{encoded_project}/repository/tree",
                params={'path': encoded_dir_path, 'ref': ref}
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return []
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch directory {dir_path}: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"Error fetching directory {dir_path}: {e}")
            return []

    async def extract(self) -> ExtractionResult:
        """Extract components from GitLab repository"""
        components = []
        warnings = []
        errors = []

        try:
            if not self.registry_file:
                errors.append("Registry file not specified")
                return ExtractionResult(
                    success=False,
                    components=[],
                    errors=errors,
                    warnings=warnings,
                    extraction_time=0.0,
                    source_info=self.source_config
                )

            # Fetch registry file content
            registry_content = await self._fetch_file_content(self.registry_file)
            if not registry_content:
                errors.append(f"Registry file not found: {self.registry_file}")
                return ExtractionResult(
                    success=False,
                    components=[],
                    errors=errors,
                    warnings=warnings,
                    extraction_time=0.0,
                    source_info=self.source_config
                )

            # Parse registry file (similar to GitHub extractor)
            parsed_components = await self._parse_registry_file(registry_content, self.registry_file)
            components.extend(parsed_components)

            # Add GitLab-specific metadata
            for component in components:
                component.metadata.update({
                    'gitlab_project_id': self.repo_info.project_id if self.repo_info else None,
                    'gitlab_project_path': self.repo_info.project_path if self.repo_info else None,
                    'gitlab_visibility': self.repo_info.visibility if self.repo_info else None,
                    'gitlab_last_activity': self.repo_info.last_activity_at.isoformat() if self.repo_info else None,
                    'extracted_at': datetime.now().isoformat(),
                    'extractor_type': 'gitlab'
                })

            self.logger.info(f"Successfully extracted {len(components)} components from GitLab repository")

            return ExtractionResult(
                success=True,
                components=components,
                errors=errors,
                warnings=warnings,
                extraction_time=0.0,
                source_info=self.source_config
            )

        except Exception as e:
            error_msg = f"Failed to extract from GitLab repository: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)

            return ExtractionResult(
                success=False,
                components=[],
                errors=errors,
                warnings=warnings,
                extraction_time=0.0,
                source_info=self.source_config
            )

    async def _parse_registry_file(self, content: str, file_path: str) -> List[Component]:
        """Parse GitLab registry file content"""
        components = []

        try:
            # Try to detect file type and parse accordingly
            if file_path.endswith('.ts') or file_path.endswith('.tsx'):
                components.extend(await self._parse_typescript_registry(content))
            elif file_path.endswith('.js') or file_path.endswith('.jsx'):
                components.extend(await self._parse_javascript_registry(content))
            elif file_path.endswith('.json'):
                components.extend(await self._parse_json_registry(content))
            else:
                # Try to auto-detect format
                if 'export' in content and ('interface' in content or 'type' in content):
                    components.extend(await self._parse_typescript_registry(content))
                elif content.strip().startswith('{'):
                    components.extend(await self._parse_json_registry(content))
                else:
                    components.extend(await self._parse_javascript_registry(content))

        except Exception as e:
            self.logger.error(f"Error parsing registry file {file_path}: {e}")

        return components

    async def _parse_typescript_registry(self, content: str) -> List[Component]:
        """Parse TypeScript registry file"""
        components = []

        # Look for registry array/object patterns
        patterns = [
            r'export\s+(?:const|let|var)\s+(\w+)\s*[:=]\s*\[([\s\S]*?)\];',
            r'export\s+default\s*\[([\s\S]*?)\];',
            r'export\s+\{\s*registry\s*[:=]\s*\[([\s\S]*?)\]\s*\}'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                registry_content = match[1] if len(match) > 1 else match[0]

                # Extract individual component definitions
                item_pattern = r'\{\s*name:\s*["\']([^"\']+)["\'][^}]*\}'
                item_matches = re.findall(item_pattern, registry_content)

                for name in item_matches:
                    component = Component(
                        name=name,
                        display_name=self._format_display_name(name),
                        description=f"Component extracted from GitLab registry",
                        component_type=ComponentType.COMPONENT,
                        category=ComponentCategory.COMPONENTS,
                        source_url=self._build_file_url(self.registry_file),
                        documentation_url=self._build_file_url(self.registry_file),
                        metadata={
                            'gitlab_source': True,
                            'registry_file': self.registry_file,
                            'parsing_method': 'typescript'
                        }
                    )
                    components.append(component)

        return components

    async def _parse_javascript_registry(self, content: str) -> List[Component]:
        """Parse JavaScript registry file"""
        components = []

        # Similar to TypeScript but without type annotations
        patterns = [
            r'(?:const|let|var)\s+(\w+)\s*=\s*\[([\s\S]*?)\];',
            r'module\.exports\s*=\s*\[([\s\S]*?)\];'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                registry_content = match[1] if len(match) > 1 else match[0]

                # Extract component names
                item_pattern = r'\{\s*name:\s*["\']([^"\']+)["\'][^}]*\}'
                item_matches = re.findall(item_pattern, registry_content)

                for name in item_matches:
                    component = Component(
                        name=name,
                        display_name=self._format_display_name(name),
                        description=f"Component extracted from GitLab registry",
                        component_type=ComponentType.COMPONENT,
                        category=ComponentCategory.COMPONENTS,
                        source_url=self._build_file_url(self.registry_file),
                        documentation_url=self._build_file_url(self.registry_file),
                        metadata={
                            'gitlab_source': True,
                            'registry_file': self.registry_file,
                            'parsing_method': 'javascript'
                        }
                    )
                    components.append(component)

        return components

    async def _parse_json_registry(self, content: str) -> List[Component]:
        """Parse JSON registry file"""
        components = []

        try:
            data = json.loads(content)

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'name' in item:
                        component = Component(
                            name=item['name'],
                            display_name=item.get('display_name', self._format_display_name(item['name'])),
                            description=item.get('description', f"Component extracted from GitLab registry"),
                            component_type=self._determine_component_type(item.get('type', 'component')),
                            category=self._determine_component_category(item.get('category', 'components')),
                            source_url=self._build_file_url(self.registry_file),
                            documentation_url=item.get('documentation_url', self._build_file_url(self.registry_file)),
                            dependencies=item.get('dependencies', []),
                            metadata={
                                'gitlab_source': True,
                                'registry_file': self.registry_file,
                                'parsing_method': 'json',
                                'raw_data': item
                            }
                        )
                        components.append(component)

        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON registry: {e}")

        return components

    def _format_display_name(self, name: str) -> str:
        """Format component name for display"""
        # Convert kebab-case to Title Case
        return ' '.join(word.capitalize() for word in name.replace('-', ' ').split())

    def _determine_component_type(self, type_str: str) -> ComponentType:
        """Determine component type from string"""
        type_mapping = {
            'component': ComponentType.COMPONENT,
            'hook': ComponentType.HOOK,
            'block': ComponentType.BLOCK,
            'utility': ComponentType.UTILITY,
            'layout': ComponentType.LAYOUT
        }
        return type_mapping.get(type_str.lower(), ComponentType.COMPONENT)

    def _determine_component_category(self, category_str: str) -> ComponentCategory:
        """Determine component category from string"""
        category_mapping = {
            'components': ComponentCategory.COMPONENTS,
            'hooks': ComponentCategory.HOOKS,
            'blocks': ComponentCategory.BLOCKS,
            'utilities': ComponentCategory.COMPONENTS,
            'layouts': ComponentCategory.COMPONENTS
        }
        return category_mapping.get(category_str.lower(), ComponentCategory.COMPONENTS)

    def _build_file_url(self, file_path: str) -> str:
        """Build URL to view file in GitLab"""
        if not self.repo_info:
            return self.source_config.get('url', '')

        ref = self.branch or self.repo_info.default_branch
        return f"{self.repo_info.http_url_to_repo}/-/blob/{ref}/{file_path}"

    def validate_source(self) -> bool:
        """Validate that the source configuration is valid for this extractor"""
        # Check required fields
        if not self.project_path and not self.repo_slug:
            self.logger.error("GitLab source requires project_path or repo_slug")
            return False

        if not self.registry_file:
            self.logger.error("GitLab source requires registry_file")
            return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get list of component types this extractor supports"""
        return ["components", "hooks", "blocks"]

    async def validate_repository(self) -> bool:
        """Validate that the GitLab repository is accessible"""
        try:
            if not self.session:
                await self.__aenter__()

            if self.repo_info:
                return True

            await self._fetch_repository_info()
            return True

        except Exception as e:
            self.logger.error(f"Repository validation failed: {e}")
            return False