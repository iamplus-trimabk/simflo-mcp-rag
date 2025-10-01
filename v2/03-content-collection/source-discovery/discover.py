"""
Source Discovery Module

Discovers and validates content sources for the RAG pipeline.
Supports various source types including GitHub repositories, NPM packages, and documentation sites.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

class SourceDiscovery:
    """Discovers content sources from various platforms"""

    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'simflo-rag-content-discovery'
        })

    def discover(self, query: str, source_type: str = "github", limit: int = 20) -> List[Dict[str, Any]]:
        """Discover sources based on query and type"""

        if source_type == "github":
            return self._discover_github_repos(query, limit)
        elif source_type == "npm":
            return self._discover_npm_packages(query, limit)
        elif source_type == "documentation":
            return self._discover_documentation_sites(query, limit)
        elif source_type == "community":
            return self._discover_community_resources(query, limit)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def _discover_github_repos(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Discover GitHub repositories"""
        try:
            # Search GitHub repositories
            search_url = f"{self.github_api_base}/search/repositories"
            params = {
                'q': f"{query} language:javascript language:typescript",
                'sort': 'stars',
                'order': 'desc',
                'per_page': min(limit, 100)  # GitHub API limit
            }

            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()

            sources = []
            for repo in data.get('items', []):
                source = {
                    'id': f"github_{repo['id']}",
                    'type': 'github',
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'url': repo['html_url'],
                    'clone_url': repo['clone_url'],
                    'stars': repo['stargazers_count'],
                    'language': repo['language'],
                    'updated_at': repo['updated_at'],
                    'size': repo['size'],
                    'topics': repo.get('topics', []),
                    'discovered_at': datetime.now().isoformat(),
                    'metadata': {
                        'owner': repo['owner']['login'],
                        'default_branch': repo['default_branch'],
                        'open_issues': repo['open_issues_count'],
                        'forks': repo['forks_count']
                    }
                }
                sources.append(source)

            return sources

        except Exception as e:
            print(f"Error discovering GitHub repositories: {e}")
            return []

    def _discover_npm_packages(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Discover NPM packages (placeholder implementation)"""
        # TODO: Implement NPM registry API integration
        return [{
            'id': 'npm_placeholder',
            'type': 'npm',
            'name': 'placeholder-package',
            'description': 'NPM package discovery not yet implemented',
            'url': 'https://www.npmjs.com',
            'discovered_at': datetime.now().isoformat(),
            'metadata': {
                'note': 'Implementation pending'
            }
        }]

    def _discover_documentation_sites(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Discover documentation sites (placeholder implementation)"""
        # TODO: Implement documentation site discovery
        return [{
            'id': 'docs_placeholder',
            'type': 'documentation',
            'name': 'placeholder-docs',
            'description': 'Documentation site discovery not yet implemented',
            'url': 'https://example.com/docs',
            'discovered_at': datetime.now().isoformat(),
            'metadata': {
                'note': 'Implementation pending'
            }
        }]

    def _discover_community_resources(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Discover community resources (placeholder implementation)"""
        # TODO: Implement community resource discovery
        return [{
            'id': 'community_placeholder',
            'type': 'community',
            'name': 'placeholder-community',
            'description': 'Community resource discovery not yet implemented',
            'url': 'https://example.com/community',
            'discovered_at': datetime.now().isoformat(),
            'metadata': {
                'note': 'Implementation pending'
            }
        }]

    def validate_source(self, source: Dict[str, Any]) -> bool:
        """Validate that a source is accessible and suitable"""
        try:
            if source['type'] == 'github':
                # Check if repository is accessible
                response = self.session.head(source['url'])
                return response.status_code == 200
            else:
                # TODO: Implement validation for other source types
                return True
        except:
            return False

    def filter_sources(self, sources: List[Dict[str, Any]], min_stars: int = 0,
                      languages: List[str] = None, topics: List[str] = None) -> List[Dict[str, Any]]:
        """Filter sources based on criteria"""
        filtered = sources.copy()

        # Filter by stars (for GitHub repos)
        if min_stars > 0:
            filtered = [s for s in filtered if s.get('stars', 0) >= min_stars]

        # Filter by languages
        if languages:
            filtered = [s for s in filtered if s.get('language') in languages]

        # Filter by topics
        if topics:
            filtered = [s for s in filtered if any(topic in s.get('topics', []) for topic in topics)]

        return filtered