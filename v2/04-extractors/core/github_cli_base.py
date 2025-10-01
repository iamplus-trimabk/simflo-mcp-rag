"""
GitHub CLI Base Extractor

Base class for extractors that use GitHub CLI for repository operations.
Provides local file access, repository management, and git metadata extraction.
"""

import json
import logging
import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

from .base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent

logger = logging.getLogger(__name__)


class GitHubCLIBaseExtractor(BaseExtractor, ABC):
    """Base class for GitHub CLI-based extractors"""

    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize extractor with source configuration

        Args:
            source_config: Source configuration dictionary
        """
        super().__init__(source_config)
        self.repo_url = source_config.get("url", "")
        self.branch = source_config.get("branch", "main")
        self.registry_file = source_config.get("registry_file", "")
        self.name = source_config.get("name", "unknown")

        self.repo_path: Optional[Path] = None
        self.temp_dir: Optional[str] = None
        self.gh_cli_available = self._check_gh_cli()
        self.repo_info = {}

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

        if self.repo_url.startswith('http'):
            parsed = urlparse(self.repo_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return {'owner': path_parts[0], 'repo': path_parts[1], 'format': 'url'}
        elif self.repo_url.startswith('git@'):
            # SSH format
            path_parts = self.repo_url.split(':')[1].replace('.git', '').split('/')
            if len(path_parts) >= 2:
                return {'owner': path_parts[0], 'repo': path_parts[1], 'format': 'ssh'}
        elif '/' in self.repo_url:
            parts = self.repo_url.split('/')
            if len(parts) >= 2:
                return {'owner': parts[0], 'repo': parts[1].replace('.git', ''), 'format': 'short'}

        raise ValueError(f"Invalid repository identifier: {self.repo_url}")

    def _clone_repository(self) -> Path:
        """Clone repository using GitHub CLI"""
        if not self.gh_cli_available:
            raise RuntimeError("GitHub CLI is not available")

        self.temp_dir = tempfile.mkdtemp(prefix=f'github_extractor_{self.name.replace("/", "_")}_')
        temp_path = Path(self.temp_dir)

        logger.info(f"Cloning {self.repo_url} to {temp_path}")

        try:
            # Use GitHub CLI for authenticated cloning
            repo_info = self._parse_repo_identifier()
            owner, repo = repo_info['owner'], repo_info['repo']

            # Clone specific branch if specified
            clone_cmd = ['gh', 'repo', 'clone', f'{owner}/{repo}', str(temp_path)]
            if self.branch and self.branch != "main":
                clone_cmd.extend(['--branch', self.branch])

            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Repository cloned successfully using GitHub CLI")
            self.repo_path = temp_path
            return temp_path

        except subprocess.CalledProcessError as e:
            logger.error(f"GitHub CLI clone failed: {e}")
            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
            raise RuntimeError(f"Failed to clone repository: {e}")

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
            logger.warning(f"Failed to get repository metadata: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse repository metadata: {e}")
            return {}

    def _read_local_file(self, file_path: str) -> Optional[str]:
        """Read a file from the cloned repository"""
        if not self.repo_path:
            raise RuntimeError("Repository not cloned. Call _clone_repository() first.")

        full_path = self.repo_path / file_path
        if not full_path.exists():
            logger.warning(f"File not found: {full_path}")
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {full_path}: {e}")
            return None

    def _find_files_by_pattern(self, pattern: str, directory: str = "") -> List[Path]:
        """Find files in the cloned repository matching a pattern"""
        if not self.repo_path:
            raise RuntimeError("Repository not cloned. Call _clone_repository() first.")

        search_path = self.repo_path
        if directory:
            search_path = self.repo_path / directory

        if not search_path.exists():
            return []

        return list(search_path.rglob(pattern))

    def _cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.repo_path = None
            logger.info(f"Cleaned up temporary directory for {self.name}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.cleanup()

    async def setup(self):
        """Setup the extractor"""
        logger.info(f"Setting up GitHub CLI extractor for {self.name}")
        self._clone_repository()
        self.repo_info = self._get_repository_metadata()

    def cleanup(self):
        """Cleanup resources"""
        self._cleanup()

    @abstractmethod
    async def extract(self):
        """Extract data from the repository - to be implemented by subclasses"""
        pass