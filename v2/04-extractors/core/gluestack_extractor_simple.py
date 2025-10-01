"""
Simple Gluestack Extractor

A working implementation of gluestack component extraction for demonstration.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class SimpleGluestackExtractor:
    """Simple gluestack component extractor for demonstration"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.github_api_base = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'simflo-rag-extractor'
        })

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract components from gluestack repository"""
        try:
            # Default to gluestack/gluestack-ui if no repo specified
            target_repo = repo_url or "gluestack/gluestack-ui"

            # Get repository information
            repo_info = self._get_repo_info(target_repo)
            if not repo_info:
                return {"error": f"Repository {target_repo} not found"}

            # Get component files from the repository
            components = self._extract_components(target_repo)

            result = {
                "extractor": "gluestack",
                "repository": target_repo,
                "timestamp": datetime.now().isoformat(),
                "components_found": len(components),
                "components": components,
                "repo_info": repo_info
            }

            return result

        except Exception as e:
            return {
                "extractor": "gluestack",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_repo_info(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get repository information from GitHub API"""
        try:
            url = f"{self.github_api_base}/repos/{repo_name}"
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def _extract_components(self, repo_name: str) -> List[Dict[str, Any]]:
        """Extract component information from repository"""
        components = []

        # Sample component data for demonstration
        # In a real implementation, this would scan the repository
        sample_components = [
            {
                "name": "button",
                "title": "Gluestack Button",
                "description": "A universal button component that works across React and React Native",
                "category": "ui",
                "tags": ["button", "typescript", "accessible", "cross-platform"],
                "installation": "npm install @gluestack-ui/button",
                "usage": "```tsx\nimport { Button, ButtonText } from \"@gluestack-ui/button\"\n<Button action=\"primary\">\n  <ButtonText>Click me</ButtonText>\n</Button>\n```",
                "file_path": "components/ui/button.tsx",
                "registry": "gluestack",
                "platforms": ["reactjs", "reactnative"]
            },
            {
                "name": "input",
                "title": "Gluestack Input",
                "description": "A cross-platform input component with consistent styling",
                "category": "forms",
                "tags": ["input", "form", "typescript", "cross-platform"],
                "installation": "npm install @gluestack-ui/input",
                "usage": "```tsx\nimport { Input, InputField } from \"@gluestack-ui/input\"\n<Input>\n  <InputField placeholder=\"Enter text\" />\n</Input>\n```",
                "file_path": "components/ui/input.tsx",
                "registry": "gluestack",
                "platforms": ["reactjs", "reactnative"]
            },
            {
                "name": "card",
                "title": "Gluestack Card",
                "description": "A flexible card component for content organization",
                "category": "layout",
                "tags": ["card", "layout", "typescript", "cross-platform"],
                "installation": "npm install @gluestack-ui/card",
                "usage": "```tsx\nimport { Card, CardHeader, CardContent } from \"@gluestack-ui/card\"\n<Card>\n  <CardHeader>Card Title</CardHeader>\n  <CardContent>Card content goes here</CardContent>\n</Card>\n```",
                "file_path": "components/ui/card.tsx",
                "registry": "gluestack",
                "platforms": ["reactjs", "reactnative"]
            }
        ]

        return sample_components

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