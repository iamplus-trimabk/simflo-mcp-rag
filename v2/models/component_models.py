"""
Enhanced Component Data Models

Supports multi-source metadata and advanced component features.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class ComponentCategory(Enum):
    """Component categories"""
    COMPONENTS = "components"
    HOOKS = "hooks"
    BLOCKS = "blocks"

class ComponentType(Enum):
    """Component types"""
    UI = "ui"
    HOOK = "hook"
    BLOCK = "block"
    UTILITY = "utility"

class SourceType(Enum):
    """Source types"""
    GITHUB = "github"
    NPM = "npm"
    API = "api"
    LOCAL = "local"

class QualityTier(Enum):
    """Quality tiers"""
    EXCELLENT = "excellent"  # 0.9 - 1.0
    GOOD = "good"          # 0.7 - 0.9
    FAIR = "fair"          # 0.5 - 0.7
    POOR = "poor"          # 0.3 - 0.5
    VERY_POOR = "very_poor"  # 0.0 - 0.3

@dataclass
class SourceMetadata:
    """Metadata for a specific source"""
    source_name: str
    extracted_at: datetime
    version: Optional[str] = None
    commit: Optional[str] = None
    package_version: Optional[str] = None
    url: Optional[str] = None
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "source_name": self.source_name,
            "extracted_at": self.extracted_at.isoformat(),
            "version": self.version,
            "commit": self.commit,
            "package_version": self.package_version,
            "url": self.url,
            "extraction_metadata": self.extraction_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SourceMetadata':
        """Create from dictionary"""
        return cls(
            source_name=data["source_name"],
            extracted_at=datetime.fromisoformat(data["extracted_at"]),
            version=data.get("version"),
            commit=data.get("commit"),
            package_version=data.get("package_version"),
            url=data.get("url"),
            extraction_metadata=data.get("extraction_metadata", {})
        )

@dataclass
class HookSignature:
    """Type signature information for hooks"""
    signature: str
    generics: List[str] = field(default_factory=list)
    return_types: Dict[str, str] = field(default_factory=dict)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    type_parameters: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class BlockComposition:
    """Composition information for blocks"""
    components: List[str] = field(default_factory=list)
    layout_type: Optional[str] = None
    responsive_behavior: Dict[str, Any] = field(default_factory=dict)
    configuration_options: List[Dict[str, Any]] = field(default_factory=list)
    template_data: Optional[str] = None

@dataclass
class UsageExample:
    """Structured usage example"""
    title: Optional[str] = None
    description: Optional[str] = None
    code: str = ""
    language: str = "typescript"
    dependencies: List[str] = field(default_factory=list)
    context: Optional[str] = None
    difficulty: str = "intermediate"  # beginner, intermediate, advanced

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "code": self.code,
            "language": self.language,
            "dependencies": self.dependencies,
            "context": self.context,
            "difficulty": self.difficulty
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageExample':
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            code=data.get("code", ""),
            language=data.get("language", "typescript"),
            dependencies=data.get("dependencies", []),
            context=data.get("context"),
            difficulty=data.get("difficulty", "intermediate")
        )

@dataclass
class ComponentMetadata:
    """Enhanced component metadata"""
    author: Optional[str] = None
    license: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    demo_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    category_specific: Dict[str, Any] = field(default_factory=dict)
    test_coverage: Optional[float] = None
    bundle_size: Optional[str] = None
    accessibility_features: List[str] = field(default_factory=list)
    browser_support: List[str] = field(default_factory=list)
    framework_version: Optional[str] = None
    peer_dependencies: List[str] = field(default_factory=list)

@dataclass
class Component:
    """Enhanced component model with multi-source support"""
    # Core identification
    name: str
    category: ComponentCategory
    type: ComponentType
    registry: str
    priority_source: str

    # Source information
    sources: List[str] = field(default_factory=list)
    source_metadata: Dict[str, SourceMetadata] = field(default_factory=dict)

    # Basic information
    display_name: Optional[str] = None
    description: str = ""
    summary: Optional[str] = None

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    peer_dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)

    # Installation and usage
    installation: str = ""
    import_statement: Optional[str] = None
    usage_examples: List[UsageExample] = field(default_factory=list)

    # Platform support
    platform: List[str] = field(default_factory=list)
    framework: str = "react"
    framework_version: Optional[str] = None

    # Quality and scoring
    quality_score: float = 0.0
    quality_tier: QualityTier = QualityTier.FAIR
    relevance_score: Optional[float] = None
    download_count: Optional[int] = None
    star_count: Optional[int] = None

    # Version and status
    version: Optional[str] = None
    status: str = "active"  # active, deprecated, beta, experimental
    last_updated: datetime = field(default_factory=datetime.now)
    created_at: Optional[datetime] = None

    # Enhanced metadata
    metadata: ComponentMetadata = field(default_factory=ComponentMetadata)
    category_specific_data: Dict[str, Any] = field(default_factory=dict)

    # Search optimization
    search_vector: Optional[List[float]] = None
    search_keywords: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing"""
        if not self.display_name:
            self.display_name = self.name.replace("-", " ").replace("_", " ").title()

        if not self.summary and self.description:
            # Generate summary from first sentence of description
            sentences = self.description.split(".")
            if sentences:
                self.summary = sentences[0].strip()

        # Update quality tier based on score
        self.quality_tier = self._calculate_quality_tier()

        # Ensure priority_source is in sources list
        if self.priority_source not in self.sources:
            self.sources.append(self.priority_source)

    def _calculate_quality_tier(self) -> QualityTier:
        """Calculate quality tier based on quality score"""
        if self.quality_score >= 0.9:
            return QualityTier.EXCELLENT
        elif self.quality_score >= 0.7:
            return QualityTier.GOOD
        elif self.quality_score >= 0.5:
            return QualityTier.FAIR
        elif self.quality_score >= 0.3:
            return QualityTier.POOR
        else:
            return QualityTier.VERY_POOR

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "category": self.category.value,
            "type": self.type.value,
            "registry": self.registry,
            "sources": self.sources,
            "priority_source": self.priority_source,
            "source_metadata": {
                name: meta.to_dict() for name, meta in self.source_metadata.items()
            },
            "display_name": self.display_name,
            "description": self.description,
            "summary": self.summary,
            "dependencies": self.dependencies,
            "peer_dependencies": self.peer_dependencies,
            "dev_dependencies": self.dev_dependencies,
            "installation": self.installation,
            "import_statement": self.import_statement,
            "usage_examples": [example.to_dict() for example in self.usage_examples],
            "platform": self.platform,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "quality_score": self.quality_score,
            "quality_tier": self.quality_tier.value,
            "relevance_score": self.relevance_score,
            "download_count": self.download_count,
            "star_count": self.star_count,
            "version": self.version,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": {
                "author": self.metadata.author,
                "license": self.metadata.license,
                "repository_url": self.metadata.repository_url,
                "documentation_url": self.metadata.documentation_url,
                "demo_url": self.metadata.demo_url,
                "tags": self.metadata.tags,
                "keywords": self.metadata.keywords,
                "category_specific": self.metadata.category_specific,
                "test_coverage": self.metadata.test_coverage,
                "bundle_size": self.metadata.bundle_size,
                "accessibility_features": self.metadata.accessibility_features,
                "browser_support": self.metadata.browser_support,
                "framework_version": self.metadata.framework_version,
                "peer_dependencies": self.metadata.peer_dependencies
            },
            "category_specific_data": self.category_specific_data,
            "search_vector": self.search_vector,
            "search_keywords": self.search_keywords
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create from dictionary"""
        # Handle legacy format for backward compatibility
        if "category" in data and isinstance(data["category"], str):
            category = ComponentCategory(data["category"])
        else:
            category = ComponentCategory.COMPONENTS

        if "type" in data and isinstance(data["type"], str):
            component_type = ComponentType(data["type"])
        else:
            component_type = ComponentType.UI

        # Create component metadata
        metadata_data = data.get("metadata", {})
        metadata = ComponentMetadata(
            author=metadata_data.get("author"),
            license=metadata_data.get("license"),
            repository_url=metadata_data.get("repository_url"),
            documentation_url=metadata_data.get("documentation_url"),
            demo_url=metadata_data.get("demo_url"),
            tags=metadata_data.get("tags", []),
            keywords=metadata_data.get("keywords", []),
            category_specific=metadata_data.get("category_specific", {}),
            test_coverage=metadata_data.get("test_coverage"),
            bundle_size=metadata_data.get("bundle_size"),
            accessibility_features=metadata_data.get("accessibility_features", []),
            browser_support=metadata_data.get("browser_support", []),
            framework_version=metadata_data.get("framework_version"),
            peer_dependencies=metadata_data.get("peer_dependencies", [])
        )

        # Create usage examples
        usage_examples = []
        for example_data in data.get("usage_examples", []):
            usage_examples.append(UsageExample.from_dict(example_data))

        # Create source metadata
        source_metadata = {}
        for source_name, meta_data in data.get("source_metadata", {}).items():
            source_metadata[source_name] = SourceMetadata.from_dict(meta_data)

        return cls(
            name=data["name"],
            category=category,
            type=component_type,
            registry=data["registry"],
            sources=data.get("sources", []),
            priority_source=data.get("priority_source", data.get("sources", ["default"])[0]),
            source_metadata=source_metadata,
            display_name=data.get("display_name"),
            description=data.get("description", ""),
            summary=data.get("summary"),
            dependencies=data.get("dependencies", []),
            peer_dependencies=data.get("peer_dependencies", []),
            dev_dependencies=data.get("dev_dependencies", []),
            installation=data.get("installation", ""),
            import_statement=data.get("import_statement"),
            usage_examples=usage_examples,
            platform=data.get("platform", []),
            framework=data.get("framework", "react"),
            framework_version=data.get("framework_version"),
            quality_score=data.get("quality_score", 0.0),
            relevance_score=data.get("relevance_score"),
            download_count=data.get("download_count"),
            star_count=data.get("star_count"),
            version=data.get("version"),
            status=data.get("status", "active"),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            metadata=metadata,
            category_specific_data=data.get("category_specific_data", {}),
            search_vector=data.get("search_vector"),
            search_keywords=data.get("search_keywords", [])
        )

    def to_legacy_format(self) -> Dict[str, Any]:
        """Convert to legacy format for backward compatibility"""
        return {
            "name": self.name,
            "category": self.category.value,
            "type": self.type.value,
            "registry": self.registry,
            "description": self.description,
            "dependencies": self.dependencies,
            "installation": self.installation,
            "platform": self.platform,
            "usage_examples": [example.code for example in self.usage_examples],
            "files": [],
            "relevance_score": self.relevance_score or self.quality_score
        }

    def get_hook_signature(self) -> Optional[HookSignature]:
        """Get hook signature if this is a hook"""
        if self.type != ComponentType.HOOK:
            return None

        return self.category_specific_data.get("hook_signature")

    def get_block_composition(self) -> Optional[BlockComposition]:
        """Get block composition if this is a block"""
        if self.type != ComponentType.BLOCK:
            return None

        return self.category_specific_data.get("block_composition")

    def add_source_metadata(self, source_name: str, metadata: SourceMetadata):
        """Add source metadata"""
        self.source_metadata[source_name] = metadata
        if source_name not in self.sources:
            self.sources.append(source_name)

    def update_quality_score(self, new_score: float):
        """Update quality score and recalculate tier"""
        self.quality_score = max(0.0, min(1.0, new_score))
        self.quality_tier = self._calculate_quality_tier()

    def is_compatible_with_platform(self, platform: str) -> bool:
        """Check if component is compatible with given platform"""
        if not self.platform:
            return True  # Assume compatible if no platform specified

        platform_lower = platform.lower()
        return any(
            p.lower() == platform_lower or p.lower() == "any"
            for p in self.platform
        )

    def get_primary_dependencies(self) -> List[str]:
        """Get primary dependencies (excluding peer/dev dependencies)"""
        return self.dependencies

    def get_all_dependencies(self) -> List[str]:
        """Get all dependencies including peer and dev dependencies"""
        all_deps = self.dependencies.copy()
        all_deps.extend(self.peer_dependencies)
        all_deps.extend(self.dev_dependencies)
        return list(set(all_deps))

    def generate_search_keywords(self) -> List[str]:
        """Generate search keywords from component data"""
        keywords = []

        # Add name variations
        keywords.append(self.name.lower())
        keywords.append(self.display_name.lower())

        # Add category and type
        keywords.append(self.category.value)
        keywords.append(self.type.value)

        # Add keywords from metadata
        keywords.extend([tag.lower() for tag in self.metadata.tags])
        keywords.extend([keyword.lower() for keyword in self.metadata.keywords])

        # Add registry
        keywords.append(self.registry.lower())

        # Add framework
        keywords.append(self.framework.lower())

        # Generate from description
        if self.description:
            # Simple keyword extraction from description
            desc_words = self.description.lower().split()
            keywords.extend([word.strip(".,!?()[]{}") for word in desc_words if len(word) > 3])

        # Deduplicate and filter
        keywords = list(set(keywords))
        keywords = [kw for kw in keywords if kw.isalnum() or "-" in kw or "_" in kw]

        return keywords[:20]  # Limit to top 20 keywords

    def validate(self) -> List[str]:
        """Validate component and return list of validation errors"""
        errors = []

        # Required fields
        if not self.name:
            errors.append("Component name is required")

        if not self.registry:
            errors.append("Registry is required")

        if not self.description:
            errors.append("Description is required")

        if not self.installation:
            errors.append("Installation command is required")

        if not self.sources:
            errors.append("At least one source is required")

        if not self.priority_source:
            errors.append("Priority source is required")

        # Name validation
        if self.name and not self.name.replace("-", "").replace("_", "").isalnum():
            errors.append("Component name contains invalid characters")

        # Source validation
        if self.priority_source not in self.sources:
            errors.append("Priority source must be in sources list")

        # Platform validation
        if self.platform and not isinstance(self.platform, list):
            errors.append("Platform must be a list")

        # Quality score validation
        if not (0.0 <= self.quality_score <= 1.0):
            errors.append("Quality score must be between 0.0 and 1.0")

        return errors

    def __str__(self) -> str:
        return f"{self.name} ({self.category.value}/{self.type.value})"

    def __repr__(self) -> str:
        return f"Component(name='{self.name}', category='{self.category.value}', type='{self.type.value}')"