#!/usr/bin/env python3
"""
Bitbucket Extractor for Component Registry

This extractor handles component extraction from Bitbucket repositories,
including support for self-hosted Bitbucket instances and private repositories.
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
class BitbucketRepoInfo:
    """Bitbucket repository information"""
    repo_slug: str
    full_name: str
    main_branch: str
    clone_url: str
    is_private: bool
    updated_on: datetime
    language: str

class BitbucketExtractor(BaseExtractor):
    """Extractor for Bitbucket-based component registries"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.api_url = source_config.get('api_url', 'https://api.bitbucket.org/2.0')
        self.repo_slug = source_config.get('repo_slug')
        self.workspace = source_config.get('workspace')
        self.access_token = source_config.get('access_token')
        self.branch = source_config.get('branch', 'main')
        self.registry_file = source_config.get('registry_file')

        # Extract workspace and repo_slug from URL if not provided
        if not self.workspace and not self.repo_slug and self.source_config.get('url'):
            self._extract_repo_info_from_url(self.source_config['url'])

        if not self.workspace or not self.repo_slug:
            raise ValueError("Bitbucket source requires both workspace and repo_slug, or URL")

        self.session: Optional[aiohttp.ClientSession] = None
        self.repo_info: Optional[BitbucketRepoInfo] = None
        self.logger = logging.getLogger(__name__)

    def _extract_repo_info_from_url(self, url: str):
        """Extract workspace and repo_slug from Bitbucket URL"""
        # Handle both bitbucket.org and self-hosted URLs
        parsed = urlparse(url)

        # Extract path components
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) >= 2:
            self.workspace = path_parts[0]
            self.repo_slug = path_parts[1]

    async def __aenter__(self):
        """Initialize aiohttp session"""
        headers = {'Accept': 'application/json'}
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

    async def _fetch_repository_info(self) -> BitbucketRepoInfo:
        """Fetch repository information from Bitbucket API"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        try:
            async with self.session.get(f"{self.api_url}/repositories/{self.workspace}/{self.repo_slug}") as response:
                if response.status == 200:
                    data = await response.json()

                    self.repo_info = BitbucketRepoInfo(
                        repo_slug=data['slug'],
                        full_name=data['full_name'],
                        main_branch=data['mainbranch']['name'] if data.get('mainbranch') else 'main',
                        clone_url=data['links']['clone'][0]['href'] if data['links']['clone'] else '',
                        is_private=data.get('is_private', False),
                        updated_on=datetime.fromisoformat(data['updated_on'].replace('Z', '+00:00')),
                        language=data.get('language', 'unknown')
                    )

                    self.logger.info(f"Fetched Bitbucket repo info: {self.repo_info.full_name}")
                    return self.repo_info
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch Bitbucket repo info: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"Error fetching Bitbucket repository info: {e}")
            raise

    async def _fetch_file_content(self, file_path: str, ref: Optional[str] = None) -> Optional[str]:
        """Fetch file content from Bitbucket repository"""
        if not self.session or not self.repo_info:
            raise RuntimeError("Session or repository info not initialized")

        ref = ref or self.branch or self.repo_info.main_branch

        try:
            # Bitbucket API v2 doesn't have direct file content endpoint
            # Use src endpoint with proper encoding
            encoded_path = file_path.replace('/', '%2F')
            url = f"{self.api_url}/repositories/{self.workspace}/{self.repo_slug}/src/{ref}/{encoded_path}"

            async with self.session.get(url) as response:
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
        """Fetch directory contents from Bitbucket repository"""
        if not self.session or not self.repo_info:
            raise RuntimeError("Session or repository info not initialized")

        ref = ref or self.branch or self.repo_info.main_branch

        try:
            encoded_path = dir_path.replace('/', '%2F')
            url = f"{self.api_url}/repositories/{self.workspace}/{self.repo_slug}/src/{ref}/{encoded_path}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Bitbucket returns HTML for directories, we need to parse or use different approach
                    # For now, return empty list as directory listing is complex with Bitbucket API
                    return []
                elif response.status == 404:
                    return []
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch directory {dir_path}: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"Error fetching directory {dir_path}: {e}")
            return []

    async def extract(self) -> ExtractionResult:
        """Extract components from Bitbucket repository"""
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

            # Add Bitbucket-specific metadata
            for component in components:
                component.metadata.update({
                    'bitbucket_workspace': self.repo_info.full_name.split('/')[0] if self.repo_info else None,
                    'bitbucket_repo_slug': self.repo_info.repo_slug if self.repo_info else None,
                    'bitbucket_language': self.repo_info.language if self.repo_info else None,
                    'bitbucket_private': self.repo_info.is_private if self.repo_info else None,
                    'bitbucket_updated': self.repo_info.updated_on.isoformat() if self.repo_info else None,
                    'extracted_at': datetime.now().isoformat(),
                    'extractor_type': 'bitbucket'
                })

            self.logger.info(f"Successfully extracted {len(components)} components from Bitbucket repository")

            return ExtractionResult(
                success=True,
                components=components,
                errors=errors,
                warnings=warnings,
                extraction_time=0.0,
                source_info=self.source_config
            )

        except Exception as e:
            error_msg = f"Failed to extract from Bitbucket repository: {str(e)}"
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
        """Parse Bitbucket registry file content"""
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
                item_pattern = r'\{\s*name:\s*[\"\']([^\"\']+)[\"\'][^}]*\}'
                item_matches = re.findall(item_pattern, registry_content)

                for name in item_matches:
                    component = Component(
                        name=name,
                        display_name=self._format_display_name(name),
                        description=f"Component extracted from Bitbucket registry",
                        component_type=ComponentType.COMPONENT,
                        category=ComponentCategory.COMPONENTS,
                        source_url=self._build_file_url(self.registry_file),
                        documentation_url=self._build_file_url(self.registry_file),
                        metadata={
                            'bitbucket_source': True,
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
                item_pattern = r'\{\s*name:\s*[\"\']([^\"\']+)[\"\'][^}]*\}'
                item_matches = re.findall(item_pattern, registry_content)

                for name in item_matches:
                    component = Component(
                        name=name,
                        display_name=self._format_display_name(name),
                        description=f"Component extracted from Bitbucket registry",
                        component_type=ComponentType.COMPONENT,
                        category=ComponentCategory.COMPONENTS,
                        source_url=self._build_file_url(self.registry_file),
                        documentation_url=self._build_file_url(self.registry_file),
                        metadata={
                            'bitbucket_source': True,
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
                            description=item.get('description', f"Component extracted from Bitbucket registry"),
                            component_type=self._determine_component_type(item.get('type', 'component')),
                            category=self._determine_component_category(item.get('category', 'components')),
                            source_url=self._build_file_url(self.registry_file),
                            documentation_url=item.get('documentation_url', self._build_file_url(self.registry_file)),
                            dependencies=item.get('dependencies', []),
                            metadata={
                                'bitbucket_source': True,
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
        """Build URL to view file in Bitbucket"""
        if not self.repo_info:
            return self.source_config.get('url', '')

        ref = self.branch or self.repo_info.main_branch
        return f"https://bitbucket.org/{self.workspace}/{self.repo_slug}/src/{ref}/{file_path}"

    def validate_source(self) -> bool:
        """Validate that the source configuration is valid for this extractor"""
        # Check required fields
        if not self.workspace:
            self.logger.error("Bitbucket source requires workspace")
            return False

        if not self.repo_slug:
            self.logger.error("Bitbucket source requires repo_slug")
            return False

        if not self.registry_file:
            self.logger.error("Bitbucket source requires registry_file")
            return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get list of component types this extractor supports"""
        return ["components", "hooks", "blocks"]

    async def validate_repository(self) -> bool:
        """Validate that the Bitbucket repository is accessible"""
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