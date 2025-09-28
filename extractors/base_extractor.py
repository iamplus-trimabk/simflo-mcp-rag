"""
Base Extractor Abstract Class

Defines the interface and common functionality for all specialized extractors.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Result of an extraction operation"""
    success: bool
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    extraction_time: float
    source_info: Dict[str, Any]

    def __post_init__(self):
        if not self.data:
            self.data = []
        if not self.errors:
            self.errors = []
        if not self.warnings:
            self.warnings = []
        if not self.metadata:
            self.metadata = {}

@dataclass
class ExtractedComponent:
    """A single extracted component/hook/block"""
    name: str
    category: str
    type: str
    sources: List[str]
    priority_source: str
    description: str
    dependencies: List[str]
    peer_dependencies: List[str]
    installation: str
    usage_examples: List[str]
    metadata: Dict[str, Any]
    quality_score: float
    last_updated: datetime
    platform: List[str]
    registry: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "sources": self.sources,
            "priority_source": self.priority_source,
            "description": self.description,
            "dependencies": self.dependencies,
            "peer_dependencies": self.peer_dependencies,
            "installation": self.installation,
            "usage_examples": self.usage_examples,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "last_updated": self.last_updated.isoformat(),
            "platform": self.platform,
            "registry": self.registry
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedComponent':
        """Create from dictionary"""
        return cls(
            name=data["name"],
            category=data["category"],
            type=data["type"],
            sources=data["sources"],
            priority_source=data["priority_source"],
            description=data["description"],
            dependencies=data.get("dependencies", []),
            peer_dependencies=data.get("peer_dependencies", []),
            installation=data["installation"],
            usage_examples=data.get("usage_examples", []),
            metadata=data.get("metadata", {}),
            quality_score=data.get("quality_score", 0.0),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            platform=data.get("platform", []),
            registry=data["registry"]
        )

class BaseExtractor(ABC):
    """Base class for all specialized extractors"""

    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.source_name = source_config.get("name", "unknown")
        self.source_type = source_config.get("type", "unknown")
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300),
            headers={
                "User-Agent": "SimFlo-MCP-RAG/1.0.0"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def extract(self) -> ExtractionResult:
        """
        Extract components from the source
        Must be implemented by specific extractors
        """
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """
        Validate that the source configuration is valid for this extractor
        Must be implemented by specific extractors
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """
        Get list of component types this extractor supports
        Must be implemented by specific extractors
        """
        pass

    async def fetch_content(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Fetch content from URL with error handling and caching"""
        if url in self.cache:
            self.logger.debug(f"Using cached content for {url}")
            return self.cache[url]

        try:
            if not self.session:
                raise RuntimeError("Extractor not initialized. Use async context manager.")

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    self.cache[url] = content
                    return content
                else:
                    self.logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    async def fetch_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch JSON content from URL"""
        content = await self.fetch_content(url, headers)
        if content:
            try:
                import json
                return json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON from {url}: {e}")
                return None
        return None

    def calculate_quality_score(self, component: Dict[str, Any]) -> float:
        """
        Calculate quality score for a component based on various factors
        Override in subclasses for specialized scoring
        """
        score = 0.0
        max_score = 1.0

        # Description quality (0.3)
        if component.get("description"):
            desc = component["description"]
            if len(desc) > 50:
                score += 0.3
            elif len(desc) > 20:
                score += 0.2
            else:
                score += 0.1

        # Installation command (0.2)
        if component.get("installation"):
            score += 0.2

        # Usage examples (0.2)
        examples = component.get("usage_examples", [])
        if examples:
            score += min(0.2, len(examples) * 0.1)

        # Dependencies (0.1)
        if component.get("dependencies"):
            score += 0.1

        # Metadata completeness (0.2)
        metadata = component.get("metadata", {})
        if metadata:
            completeness = len(metadata) / 10  # Assume 10 fields is complete
            score += min(0.2, completeness * 0.2)

        return min(score, max_score)

    def validate_component(self, component: Dict[str, Any]) -> List[str]:
        """
        Validate a component and return list of validation errors
        Override in subclasses for specialized validation
        """
        errors = []

        # Required fields
        required_fields = ["name", "category", "type", "description", "installation"]
        for field in required_fields:
            if not component.get(field):
                errors.append(f"Missing required field: {field}")

        # Name validation
        name = component.get("name", "")
        if not name or len(name.strip()) == 0:
            errors.append("Invalid component name")
        elif not name.replace("-", "").replace("_", "").isalnum():
            errors.append("Component name contains invalid characters")

        # Installation validation
        installation = component.get("installation", "")
        if not installation or len(installation.strip()) == 0:
            errors.append("Invalid installation command")

        return errors

    def extract_dependencies(self, code: str) -> List[str]:
        """
        Extract dependencies from code
        Basic implementation, override in subclasses for specialized parsing
        """
        dependencies = []

        # Look for import statements
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s+[\'"]([^\'"]+)[\'"]'
        ]

        import re
        for pattern in import_patterns:
            matches = re.findall(pattern, code)
            dependencies.extend(matches)

        # Clean and deduplicate
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]
        return list(set(dependencies))

    def extract_installation_command(self, component: Dict[str, Any]) -> str:
        """
        Generate installation command for component
        Override in subclasses for specialized installation commands
        """
        registry = component.get("registry", "unknown")
        name = component.get("name", "unknown")

        if registry == "shadcn":
            return f"npx shadcn@latest add {name}"
        elif registry == "gluestack":
            return f"npx gluestack-ui@latest add {name}"
        else:
            return f"# Installation command not available for {name}"

    def create_extraction_result(
        self,
        success: bool,
        data: List[Dict[str, Any]] = None,
        errors: List[str] = None,
        warnings: List[str] = None,
        metadata: Dict[str, Any] = None,
        extraction_time: float = 0.0
    ) -> ExtractionResult:
        """Create a standardized extraction result"""
        return ExtractionResult(
            success=success,
            data=data or [],
            metadata=metadata or {},
            errors=errors or [],
            warnings=warnings or [],
            extraction_time=extraction_time,
            source_info=self.source_config.copy()
        )

    def log_extraction_start(self):
        """Log the start of extraction"""
        self.logger.info(f"Starting extraction from {self.source_name} ({self.source_type})")

    def log_extraction_complete(self, result: ExtractionResult):
        """Log the completion of extraction"""
        self.logger.info(
            f"Extraction from {self.source_name} completed: "
            f"success={result.success}, "
            f"components={len(result.data)}, "
            f"errors={len(result.errors)}, "
            f"time={result.extraction_time:.2f}s"
        )

    async def extract_with_validation(self) -> ExtractionResult:
        """
        Extract with automatic validation and quality scoring
        """
        self.log_extraction_start()
        start_time = asyncio.get_event_loop().time()

        try:
            # Validate source configuration
            if not self.validate_source():
                return self.create_extraction_result(
                    success=False,
                    errors=["Invalid source configuration for this extractor"]
                )

            # Perform extraction
            result = await self.extract()

            # Validate and score components
            validated_components = []
            for component in result.data:
                validation_errors = self.validate_component(component)
                if validation_errors:
                    result.warnings.extend([
                        f"Component {component.get('name', 'unknown')}: {error}"
                        for error in validation_errors
                    ])
                    continue

                # Add quality score
                component["quality_score"] = self.calculate_quality_score(component)

                # Add source metadata
                component["sources"] = [self.source_name]
                component["priority_source"] = self.source_name

                validated_components.append(component)

            result.data = validated_components

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            result = self.create_extraction_result(
                success=False,
                errors=[f"Extraction error: {str(e)}"]
            )

        finally:
            result.extraction_time = asyncio.get_event_loop().time() - start_time
            self.log_extraction_complete(result)

        return result

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cached_urls": list(self.cache.keys())
        }

    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        self.logger.info("Extraction cache cleared")