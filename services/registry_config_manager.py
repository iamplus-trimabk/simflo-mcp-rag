"""
Registry Configuration Manager

Manages loading, validation, and access to registry configurations
in the new modular format.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SourceType(Enum):
    """Supported source types for registry extraction"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    NPM = "npm"
    API = "api"
    LOCAL = "local"

class CategoryType(Enum):
    """Supported component categories"""
    COMPONENTS = "components"
    HOOKS = "hooks"
    BLOCKS = "blocks"

class RegistryStatus(Enum):
    """Registry status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

@dataclass
class SourceConfig:
    """Configuration for a single data source"""
    name: str
    type: SourceType
    url: Optional[str] = None
    branch: Optional[str] = None
    registry_file: Optional[str] = None
    package: Optional[str] = None
    extractor: str = "default"
    priority: int = 1
    update_frequency: str = "weekly"
    enabled: bool = True
    # GitLab/Bitbucket specific fields
    project_path: Optional[str] = None  # GitLab project path (e.g., "group/project")
    repo_slug: Optional[str] = None  # Bitbucket repo slug (e.g., "team/repo")
    access_token: Optional[str] = None  # Access token for private repositories
    api_url: Optional[str] = None  # Custom API URL for self-hosted instances
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CategoryConfig:
    """Configuration for a component category"""
    enabled: bool
    sources: List[SourceConfig]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SearchConfig:
    """Search configuration for a registry"""
    cross_category_search: bool = True
    default_category: str = "components"
    category_weights: Dict[str, float] = None
    source_boosting: Dict[str, float] = None

    def __post_init__(self):
        if self.category_weights is None:
            self.category_weights = {
                "components": 0.6,
                "hooks": 0.3,
                "blocks": 0.1
            }
        if self.source_boosting is None:
            self.source_boosting = {
                "official": 1.2,
                "community": 0.8,
                "third_party": 0.6
            }

@dataclass
class BuildConfig:
    """Build configuration for automated registry updates"""
    build_enabled: bool = True
    schedule: str = "0 2 * * *"  # Daily at 2 AM
    notification_types: List[str] = None
    notification_targets: List[str] = None
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout_minutes: int = 30
    quality_threshold: float = 0.7
    parallel_builds: bool = False
    cleanup_days: int = 30
    health_check_interval: int = 300
    auto_deploy: bool = True

    def __post_init__(self):
        if self.notification_types is None:
            self.notification_types = ["console"]
        if self.notification_targets is None:
            self.notification_targets = []

@dataclass
class RegistryConfig:
    """Complete registry configuration"""
    registry_name: str
    display_name: str
    description: str
    platforms: List[str]
    database_path: str
    status: RegistryStatus
    categories: Dict[str, CategoryConfig]
    search_configuration: SearchConfig
    build_configuration: BuildConfig = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.build_configuration is None:
            self.build_configuration = BuildConfig()
        if self.metadata is None:
            self.metadata = {}

class RegistryConfigManager:
    """Manages registry configurations in the new modular format"""

    def __init__(self, config_dir: str = "rag_databases/registry_config"):
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, RegistryConfig] = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all registry configurations from the config directory"""
        if not self.config_dir.exists():
            logger.warning(f"Config directory {self.config_dir} does not exist")
            return

        for config_file in self.config_dir.glob("*.json"):
            try:
                config = self.load_registry_config(config_file.stem)
                if config:
                    self._configs[config.registry_name] = config
                    logger.info(f"Loaded registry config: {config.registry_name}")
            except Exception as e:
                logger.error(f"Failed to load config from {config_file}: {e}")

    def load_registry_config(self, registry_name: str) -> Optional[RegistryConfig]:
        """Load a specific registry configuration"""
        config_file = self.config_dir / f"{registry_name}.json"

        if not config_file.exists():
            logger.error(f"Registry config file not found: {config_file}")
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self._parse_registry_config(data)
        except Exception as e:
            logger.error(f"Failed to parse registry config {registry_name}: {e}")
            return None

    def _parse_registry_config(self, data: Dict[str, Any]) -> RegistryConfig:
        """Parse raw JSON data into RegistryConfig object"""

        # Parse categories
        categories = {}
        for category_name, category_data in data.get('categories', {}).items():
            sources = []
            for source_data in category_data.get('sources', []):
                source = SourceConfig(
                    name=source_data['name'],
                    type=SourceType(source_data['type']),
                    url=source_data.get('url'),
                    branch=source_data.get('branch'),
                    registry_file=source_data.get('registry_file'),
                    package=source_data.get('package'),
                    extractor=source_data.get('extractor', 'default'),
                    priority=source_data.get('priority', 1),
                    update_frequency=source_data.get('update_frequency', 'weekly'),
                    enabled=source_data.get('enabled', True),
                    project_path=source_data.get('project_path'),
                    repo_slug=source_data.get('repo_slug'),
                    access_token=source_data.get('access_token'),
                    api_url=source_data.get('api_url'),
                    metadata=source_data.get('metadata', {})
                )
                sources.append(source)

            category = CategoryConfig(
                enabled=category_data.get('enabled', True),
                sources=sources,
                metadata=category_data.get('metadata', {})
            )
            categories[category_name] = category

        # Parse search configuration
        search_data = data.get('search_configuration', {})
        search_config = SearchConfig(
            cross_category_search=search_data.get('cross_category_search', True),
            default_category=search_data.get('default_category', 'components'),
            category_weights=search_data.get('category_weights'),
            source_boosting=search_data.get('source_boosting')
        )

        # Parse build configuration
        build_data = data.get('build_configuration', {})
        build_config = BuildConfig(
            build_enabled=build_data.get('build_enabled', True),
            schedule=build_data.get('schedule', '0 2 * * *'),
            notification_types=build_data.get('notification_types'),
            notification_targets=build_data.get('notification_targets'),
            retry_on_failure=build_data.get('retry_on_failure', True),
            max_retries=build_data.get('max_retries', 3),
            timeout_minutes=build_data.get('timeout_minutes', 30),
            quality_threshold=build_data.get('quality_threshold', 0.7),
            parallel_builds=build_data.get('parallel_builds', False),
            cleanup_days=build_data.get('cleanup_days', 30),
            health_check_interval=build_data.get('health_check_interval', 300),
            auto_deploy=build_data.get('auto_deploy', True)
        )

        return RegistryConfig(
            registry_name=data['registry_name'],
            display_name=data['display_name'],
            description=data['description'],
            platforms=data['platforms'],
            database_path=data['database_path'],
            status=RegistryStatus(data.get('status', 'active')),
            categories=categories,
            search_configuration=search_config,
            build_configuration=build_config,
            metadata=data.get('metadata', {})
        )

    def get_registry_config(self, registry_name: str) -> Optional[RegistryConfig]:
        """Get a specific registry configuration"""
        return self._configs.get(registry_name)

    def get_all_registries(self) -> List[RegistryConfig]:
        """Get all registry configurations"""
        return list(self._configs.values())

    def get_active_registries(self) -> List[RegistryConfig]:
        """Get only active registry configurations"""
        return [config for config in self._configs.values()
                if config.status == RegistryStatus.ACTIVE]

    def get_registries_for_platform(self, platform: str) -> List[RegistryConfig]:
        """Get registries that support a specific platform"""
        return [config for config in self._configs.values()
                if platform in config.platforms and config.status == RegistryStatus.ACTIVE]

    def get_active_sources(self, registry_name: str, category: str) -> List[SourceConfig]:
        """Get all active sources for a specific registry and category"""
        config = self.get_registry_config(registry_name)
        if not config:
            return []

        category_config = config.categories.get(category)
        if not category_config or not category_config.enabled:
            return []

        return [source for source in category_config.sources if source.enabled]

    def get_source_by_name(self, registry_name: str, category: str, source_name: str) -> Optional[SourceConfig]:
        """Get a specific source configuration"""
        sources = self.get_active_sources(registry_name, category)
        for source in sources:
            if source.name == source_name:
                return source
        return None

    def validate_config(self, config: RegistryConfig) -> bool:
        """Validate a registry configuration"""
        try:
            # Required fields
            if not config.registry_name:
                logger.error("Registry name is required")
                return False

            if not config.display_name:
                logger.error("Display name is required")
                return False

            if not config.platforms:
                logger.error("At least one platform is required")
                return False

            if not config.database_path:
                logger.error("Database path is required")
                return False

            # Validate categories
            for category_name, category_config in config.categories.items():
                if not category_config.enabled:
                    continue

                if not category_config.sources:
                    logger.error(f"Category {category_name} has no sources")
                    return False

                # Validate sources
                for source in category_config.sources:
                    if not self._validate_source(source):
                        return False

            # Validate search configuration
            if not config.search_configuration.default_category:
                logger.error("Default category is required")
                return False

            # Validate category weights sum to 1.0
            weights = config.search_configuration.category_weights
            if abs(sum(weights.values()) - 1.0) > 0.01:
                logger.error("Category weights must sum to 1.0")
                return False

            logger.info(f"Registry config {config.registry_name} is valid")
            return True

        except Exception as e:
            logger.error(f"Error validating config {config.registry_name}: {e}")
            return False

    def _validate_source(self, source: SourceConfig) -> bool:
        """Validate a source configuration"""
        if not source.name:
            logger.error("Source name is required")
            return False

        if not source.type:
            logger.error("Source type is required")
            return False

        # Type-specific validation
        if source.type == SourceType.GITHUB:
            if not source.url:
                logger.error(f"GitHub source {source.name} requires URL")
                return False
            if not source.branch:
                logger.error(f"GitHub source {source.name} requires branch")
                return False
            if not source.registry_file:
                logger.error(f"GitHub source {source.name} requires registry_file")
                return False

        elif source.type == SourceType.NPM:
            if not source.package:
                logger.error(f"NPM source {source.name} requires package")
                return False

        elif source.type == SourceType.GITLAB:
            if not source.url and not source.project_path:
                logger.error(f"GitLab source {source.name} requires URL or project_path")
                return False
            if not source.branch:
                logger.error(f"GitLab source {source.name} requires branch")
                return False
            if not source.registry_file:
                logger.error(f"GitLab source {source.name} requires registry_file")
                return False

        elif source.type == SourceType.BITBUCKET:
            if not source.url and not source.repo_slug:
                logger.error(f"Bitbucket source {source.name} requires URL or repo_slug")
                return False
            if not source.branch:
                logger.error(f"Bitbucket source {source.name} requires branch")
                return False
            if not source.registry_file:
                logger.error(f"Bitbucket source {source.name} requires registry_file")
                return False

        elif source.type == SourceType.LOCAL:
            if not source.registry_file:
                logger.error(f"Local source {source.name} requires registry_file")
                return False

        return True

    def save_registry_config(self, config: RegistryConfig):
        """Save a registry configuration to file"""
        if not self.validate_config(config):
            raise ValueError("Invalid registry configuration")

        config_file = self.config_dir / f"{config.registry_name}.json"

        data = {
            "registry_name": config.registry_name,
            "display_name": config.display_name,
            "description": config.description,
            "platforms": config.platforms,
            "database_path": config.database_path,
            "status": config.status.value,
            "categories": {},
            "search_configuration": {
                "cross_category_search": config.search_configuration.cross_category_search,
                "default_category": config.search_configuration.default_category,
                "category_weights": config.search_configuration.category_weights,
                "source_boosting": config.search_configuration.source_boosting
            },
            "build_configuration": {
                "build_enabled": config.build_configuration.build_enabled,
                "schedule": config.build_configuration.schedule,
                "notification_types": config.build_configuration.notification_types,
                "notification_targets": config.build_configuration.notification_targets,
                "retry_on_failure": config.build_configuration.retry_on_failure,
                "max_retries": config.build_configuration.max_retries,
                "timeout_minutes": config.build_configuration.timeout_minutes,
                "quality_threshold": config.build_configuration.quality_threshold,
                "parallel_builds": config.build_configuration.parallel_builds,
                "cleanup_days": config.build_configuration.cleanup_days,
                "health_check_interval": config.build_configuration.health_check_interval,
                "auto_deploy": config.build_configuration.auto_deploy
            },
            "metadata": config.metadata
        }

        # Add categories
        for category_name, category_config in config.categories.items():
            data["categories"][category_name] = {
                "enabled": category_config.enabled,
                "sources": [
                    {
                        "name": source.name,
                        "type": source.type.value,
                        "url": source.url,
                        "branch": source.branch,
                        "registry_file": source.registry_file,
                        "package": source.package,
                        "extractor": source.extractor,
                        "priority": source.priority,
                        "update_frequency": source.update_frequency,
                        "enabled": source.enabled,
                        "project_path": source.project_path,
                        "repo_slug": source.repo_slug,
                        "access_token": source.access_token,
                        "api_url": source.api_url,
                        "metadata": source.metadata
                    }
                    for source in category_config.sources
                ],
                "metadata": category_config.metadata
            }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Update internal cache
            self._configs[config.registry_name] = config
            logger.info(f"Saved registry config: {config.registry_name}")

        except Exception as e:
            logger.error(f"Failed to save registry config {config.registry_name}: {e}")
            raise

    def create_registry_config(
        self,
        registry_name: str,
        display_name: str,
        description: str,
        platforms: List[str],
        database_path: str
    ) -> RegistryConfig:
        """Create a new registry configuration with defaults"""
        config = RegistryConfig(
            registry_name=registry_name,
            display_name=display_name,
            description=description,
            platforms=platforms,
            database_path=database_path,
            status=RegistryStatus.ACTIVE,
            categories={
                "components": CategoryConfig(enabled=True, sources=[]),
                "hooks": CategoryConfig(enabled=True, sources=[]),
                "blocks": CategoryConfig(enabled=True, sources=[])
            },
            search_configuration=SearchConfig(),
            metadata={}
        )

        return config

    def add_source_to_category(
        self,
        registry_name: str,
        category: str,
        source: SourceConfig
    ) -> bool:
        """Add a source to a registry category"""
        config = self.get_registry_config(registry_name)
        if not config:
            logger.error(f"Registry {registry_name} not found")
            return False

        if category not in config.categories:
            logger.error(f"Category {category} not found in registry {registry_name}")
            return False

        # Check if source already exists
        existing_sources = [s.name for s in config.categories[category].sources]
        if source.name in existing_sources:
            logger.error(f"Source {source.name} already exists in {registry_name}/{category}")
            return False

        config.categories[category].sources.append(source)

        # Save updated config
        try:
            self.save_registry_config(config)
            logger.info(f"Added source {source.name} to {registry_name}/{category}")
            return True
        except Exception as e:
            logger.error(f"Failed to add source: {e}")
            return False

    def remove_source_from_category(
        self,
        registry_name: str,
        category: str,
        source_name: str
    ) -> bool:
        """Remove a source from a registry category"""
        config = self.get_registry_config(registry_name)
        if not config:
            logger.error(f"Registry {registry_name} not found")
            return False

        if category not in config.categories:
            logger.error(f"Category {category} not found in registry {registry_name}")
            return False

        # Find and remove source
        sources = config.categories[category].sources
        for i, source in enumerate(sources):
            if source.name == source_name:
                sources.pop(i)

                # Save updated config
                try:
                    self.save_registry_config(config)
                    logger.info(f"Removed source {source_name} from {registry_name}/{category}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to remove source: {e}")
                    return False

        logger.error(f"Source {source_name} not found in {registry_name}/{category}")
        return False

    def reload_config(self, registry_name: str) -> bool:
        """Reload a specific registry configuration"""
        try:
            config = self.load_registry_config(registry_name)
            if config:
                self._configs[registry_name] = config
                logger.info(f"Reloaded registry config: {registry_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to reload config {registry_name}: {e}")
            return False

    def reload_all_configs(self):
        """Reload all registry configurations"""
        self._configs.clear()
        self._load_all_configs()
        logger.info("Reloaded all registry configurations")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded configurations"""
        stats = {
            "total_registries": len(self._configs),
            "active_registries": len(self.get_active_registries()),
            "platforms": {},
            "categories": {"components": 0, "hooks": 0, "blocks": 0},
            "sources": {"total": 0, "by_type": {}}
        }

        for config in self._configs.values():
            # Platform statistics
            for platform in config.platforms:
                stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1

            # Category statistics
            for category_name, category_config in config.categories.items():
                if category_config.enabled:
                    stats["categories"][category_name] += 1
                    stats["sources"]["total"] += len(category_config.sources)

                    # Source type statistics
                    for source in category_config.sources:
                        source_type = source.type.value
                        stats["sources"]["by_type"][source_type] = \
                            stats["sources"]["by_type"].get(source_type, 0) + 1

        return stats

    def list_registries(self) -> List[str]:
        """List all available registry names"""
        return list(self._configs.keys())