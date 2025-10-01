"""
Content Fetcher Module

Fetches content from discovered sources and prepares it for the extraction pipeline.
Supports Git cloning, web scraping, and file downloads.
"""

import os
import json
import subprocess
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

class ContentFetcher:
    """Fetches content from various source types"""

    def __init__(self, output_dir: str = "fetched_content"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()

    def fetch_all(self, sources: List[Dict[str, Any]], parallel: bool = False) -> Dict[str, Any]:
        """Fetch content from multiple sources"""
        results = {
            "successful": 0,
            "failed": 0,
            "details": []
        }

        for source in sources:
            try:
                result = self.fetch_single(source)
                if result['success']:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "source_id": source.get('id', 'unknown'),
                    "success": False,
                    "error": str(e),
                    "source_type": source.get('type', 'unknown')
                })

        return results

    def fetch_single(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch content from a single source"""
        source_type = source.get('type')
        source_id = source.get('id')

        try:
            if source_type == 'github':
                return self._fetch_github_repo(source)
            elif source_type == 'npm':
                return self._fetch_npm_package(source)
            elif source_type == 'documentation':
                return self._fetch_documentation(source)
            elif source_type == 'community':
                return self._fetch_community_resource(source)
            else:
                return {
                    "source_id": source_id,
                    "success": False,
                    "error": f"Unsupported source type: {source_type}",
                    "source_type": source_type
                }

        except Exception as e:
            return {
                "source_id": source_id,
                "success": False,
                "error": str(e),
                "source_type": source_type
            }

    def _fetch_github_repo(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch content from GitHub repository using git clone"""
        source_id = source.get('id')
        clone_url = source.get('clone_url')
        repo_name = source.get('full_name', 'unknown').replace('/', '_')

        # Create subdirectory for this repo
        repo_dir = self.output_dir / "github" / repo_name
        repo_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Check if already cloned
            if (repo_dir / ".git").exists():
                # Pull latest changes
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode != 0:
                    return {
                        "source_id": source_id,
                        "success": False,
                        "error": f"Git pull failed: {result.stderr}",
                        "source_type": "github"
                    }
            else:
                # Clone repository
                result = subprocess.run(
                    ["git", "clone", clone_url, str(repo_dir)],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes timeout
                )
                if result.returncode != 0:
                    return {
                        "source_id": source_id,
                        "success": False,
                        "error": f"Git clone failed: {result.stderr}",
                        "source_type": "github"
                    }

            # Create metadata file
            metadata = {
                "source": source,
                "fetched_at": datetime.now().isoformat(),
                "local_path": str(repo_dir),
                "fetch_method": "git_clone",
                "size_bytes": self._get_directory_size(repo_dir)
            }

            metadata_file = repo_dir / "fetch_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            return {
                "source_id": source_id,
                "success": True,
                "local_path": str(repo_dir),
                "fetch_method": "git_clone",
                "source_type": "github",
                "metadata": metadata
            }

        except subprocess.TimeoutExpired:
            return {
                "source_id": source_id,
                "success": False,
                "error": "Git operation timed out",
                "source_type": "github"
            }
        except Exception as e:
            return {
                "source_id": source_id,
                "success": False,
                "error": str(e),
                "source_type": "github"
            }

    def _fetch_npm_package(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch NPM package information (placeholder)"""
        source_id = source.get('id')

        # TODO: Implement NPM package fetching
        return {
            "source_id": source_id,
            "success": False,
            "error": "NPM package fetching not yet implemented",
            "source_type": "npm"
        }

    def _fetch_documentation(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch documentation content (placeholder)"""
        source_id = source.get('id')
        url = source.get('url')

        try:
            # Basic web scraping
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Create subdirectory for documentation
            doc_dir = self.output_dir / "documentation" / source_id
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Save main page
            main_file = doc_dir / "index.html"
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            metadata = {
                "source": source,
                "fetched_at": datetime.now().isoformat(),
                "local_path": str(doc_dir),
                "fetch_method": "web_scraping",
                "files": ["index.html"]
            }

            metadata_file = doc_dir / "fetch_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            return {
                "source_id": source_id,
                "success": True,
                "local_path": str(doc_dir),
                "fetch_method": "web_scraping",
                "source_type": "documentation",
                "metadata": metadata
            }

        except Exception as e:
            return {
                "source_id": source_id,
                "success": False,
                "error": str(e),
                "source_type": "documentation"
            }

    def _fetch_community_resource(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch community resource content (placeholder)"""
        source_id = source.get('id')

        # TODO: Implement community resource fetching
        return {
            "source_id": source_id,
            "success": False,
            "error": "Community resource fetching not yet implemented",
            "source_type": "community"
        }

    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size

    def get_fetch_summary(self) -> Dict[str, Any]:
        """Get summary of fetched content"""
        summary = {
            "output_directory": str(self.output_dir),
            "total_sources": 0,
            "by_type": {},
            "total_size_bytes": 0,
            "last_updated": None
        }

        try:
            for source_type_dir in self.output_dir.iterdir():
                if source_type_dir.is_dir():
                    type_name = source_type_dir.name
                    type_count = len([d for d in source_type_dir.iterdir() if d.is_dir()])
                    summary["by_type"][type_name] = type_count
                    summary["total_sources"] += type_count

            # Calculate total size
            summary["total_size_bytes"] = self._get_directory_size(self.output_dir)

            # Get last update time
            summary["last_updated"] = datetime.now().isoformat()

        except Exception as e:
            summary["error"] = str(e)

        return summary