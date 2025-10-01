# Registry Design: Multi-Source Configuration System

## Overview

This document outlines the design for restructuring the registry configuration system to support multiple sources per registry with granular category management (components, hooks, blocks).

## Current vs Target Structure

### Current Structure
```
rag_databases/
├── registry_config.json          # Monolithic configuration
├── shadcn_db/components.json      # Single source per registry
├── gluestack_db/components.json
└── radix_db/components.json
```

### Target Structure (SimFlo RAG v2 Implementation)
```
rag_databases/
├── registry_config/               # Modular configuration
│   ├── shadcn.json              # Per-registry config
│   ├── gluestack.json
│   ├── radix.json
│   └── mui.json
├── shadcn_db/
│   ├── components.json           # Category-specific data
│   ├── hooks.json
│   └── blocks.json
├── gluestack_db/
└── radix_db/
```

### SimFlo RAG v2 Actual Implementation
```
v2/core/00-rag-registry/registries/
├── shadcn/
│   ├── chroma_db/               # Vector database (standardized path)
│   └── files/                   # Source files organized by type
│       └── components/          # Component definitions and examples
├── gluestack/
│   ├── chroma_db/
│   └── files/
│       └── components/
└── simflo-rag/                  # NEW: Self-documenting registry
    ├── chroma_db/
    └── files/
        ├── architecture/        # System architecture documentation
        ├── rag-registry/        # Registry system documentation
        ├── mcp-server/          # AI assistant integration docs
        ├── commands/            # CLI command references
        └── user-guides/         # Usage guides and patterns
```

## Registry Configuration Schema

### Base Structure
```json
{
  "registry_name": "shadcn",
  "display_name": "Shadcn UI",
  "description": "Modern React component library with hooks and blocks",
  "platforms": ["reactjs"],
  "database_path": "rag_databases/shadcn_db",
  "status": "active",
  "categories": {
    "components": { /* category configuration */ },
    "hooks": { /* category configuration */ },
    "blocks": { /* category configuration */ }
  },
  "search_configuration": { /* search settings */ },
  "metadata": { /* registry metadata */ }
}
```

### Category Configuration
```json
{
  "components": {
    "enabled": true,
    "sources": [
      {
        "name": "shadcn_ui_main",
        "type": "github",
        "url": "https://github.com/shadcn-ui/ui",
        "branch": "main",
        "registry_file": "apps/www/registry/registry-ui.ts",
        "extractor": "shadcn",
        "priority": 1,
        "update_frequency": "weekly"
      }
    ]
  }
}
```

## DatabaseManager Implementation (v2 Achievement)

### Centralized Database Management
SimFlo RAG v2 implements a centralized `DatabaseManager` class that solves the database duplication problem:

**Key Features**:
- **Single Source of Truth**: All database operations go through DatabaseManager
- **Standardized Paths**: `{registry}/chroma_db/` format eliminates confusion
- **Singleton Pattern**: Global instance for consistent database access
- **Cleanup Operations**: Automatic cleanup of duplicate database files

**Database Path Resolution**:
```python
def get_registry_db_path(self, registry_name: str) -> Path:
    """Get the standardized database path for a registry"""
    return self.registries_base_path / registry_name / self.db_path_suffix
```

**Database Creation Process**:
```python
def create_database(self, registry_name: str, source_files: List[Path], collection_name: str = "components") -> Dict[str, Any]:
    """Create a simple ChromaDB database for a registry from source files"""
    # Standardized database directory creation
    # Document processing and metadata generation
    # Vector database population
    # Marker file creation for tracking
```

## Source Types

### GitHub Sources
- **Type**: `github`
- **Use Case**: Repositories with structured registry files
- **Examples**: shadcn/ui, gluestack-ui, radix-ui
- **Extractor Types**: `shadcn`, `gluestack`, `radix`

### NPM Sources
- **Type**: `npm`
- **Use Case**: Packages with hook exports and utilities
- **Examples**: `@hookform/resolvers`, `react-query`
- **Extractor Types**: `npm_hooks`, `npm_utilities`

### API Sources
- **Type**: `api`
- **Use Case**: REST APIs with component data
- **Examples**: Component library APIs, marketplace APIs
- **Extractor Types**: `api_json`, `api_graphql`

### Local Sources
- **Type**: `local`
- **Use Case**: Local development and custom components
- **Examples**: Internal component libraries
- **Extractor Types**: `local_files`, `local_registry`

## Extractor Specialization

### Why Specialized Extractors Are Needed

#### 1. shadcn_hooks_extractor.py (⚠️ V4 Implementation Required)
**Purpose**: Specialized extraction of React hooks from shadcn/ui registry

**Why needed:**
- **Hook Pattern Recognition**: Hooks follow specific patterns (`use-*`, function-based)
- **Dependency Tracking**: Hooks have unique dependencies (react, react-hook-form)
- **TypeScript Interfaces**: Strong typing with generics and complex return types
- **Custom Hook Logic**: Often combines multiple hooks or custom logic
- **Usage Patterns**: Different from components - no JSX, pure function composition

**Unique Requirements:**
- Extract hook-specific metadata (dependencies, return types)
- Handle hook composition and chaining
- Parse JSDoc for hook documentation
- Track peer dependencies specific to hooks

#### 2. shadcn_blocks_extractor.py (⚠️ V4 Implementation Required)
**Purpose**: Specialized extraction of UI blocks from shadcn/ui

**Why needed:**
- **Block Structure**: Pre-built UI sections combining multiple components
- **Layout Logic**: Grid systems, responsive design patterns
- **Multiple Components**: Single block = multiple component instances
- **Configuration-Driven**: Blocks often have configuration options
- **Template-based**: May use templating engines or slot patterns

**Unique Requirements:**
- Parse block composition and component relationships
- Handle layout and responsive design metadata
- Extract configuration options and variants
- Track component dependencies within blocks

#### 3. gluestack_extractor.py (⚠️ V4 Implementation Required)
**Purpose**: Specialized extraction from gluestack's monorepo structure

**Why needed:**
- **Monorepo Structure**: Components in packages/gluestack-core/src/
- **Cross-Platform**: React + React Native components
- **Complex File Discovery**: Advanced file pattern matching
- **Platform-Specific Code**: Conditional exports and platform logic

**Unique Requirements:**
- Navigate complex monorepo directory structures
- Handle platform-specific component variations
- Extract cross-platform compatibility information
- Parse advanced dependency relationships

#### 4. npm_hooks_extractor.py
**Purpose**: Extract hooks from npm packages without registry files

**Why needed:**
- **Package.json Analysis**: Extract hook exports from package main/exports
- **Type Definition Parsing**: Read .d.ts files for hook signatures
- **Dependency Resolution**: Resolve transitive dependencies
- **Version Management**: Handle multiple versions and compatibility
- **Documentation Extraction**: Parse README and JSDoc from npm packages

**Unique Requirements:**
- Handle various package structures (ESM, CommonJS, TypeScript)
- Extract from bundled packages and source maps
- Parse npm registry metadata and documentation
- Handle private packages and scoped packages

## Multi-Source Merging Strategy

### Priority-Based Resolution
```python
def merge_sources(components, sources):
    """
    Merge components from multiple sources using priority-based resolution
    Higher priority sources override lower priority ones
    """
    source_priority = {source['name']: source['priority'] for source in sources}

    # Group by component name
    component_groups = group_by_name(components)

    merged_components = []
    for name, variants in component_groups.items():
        # Select highest priority variant
        selected = max(variants, key=lambda c: source_priority[c['source']])
        selected['sources'] = [v['source'] for v in variants]
        merged_components.append(selected)

    return merged_components
```

### Conflict Resolution Rules
1. **Name Conflicts**: Higher priority source wins
2. **Type Conflicts**: Same component type required for merging
3. **Platform Conflicts**: Union of supported platforms
4. **Dependency Conflicts**: Merge with version resolution
5. **Metadata Conflicts**: Higher priority source metadata takes precedence

## Search and Discovery

### Category-Aware Search
```json
{
  "search_configuration": {
    "cross_category_search": true,
    "default_category": "components",
    "category_weights": {
      "components": 0.6,
      "hooks": 0.3,
      "blocks": 0.1
    },
    "source_boosting": {
      "official": 1.2,
      "community": 0.8,
      "third_party": 0.6
    }
  }
}
```

### Relevance Scoring
- **Category Match**: Exact category match gets highest weight
- **Source Priority**: Higher priority sources get boost
- **Quality Metrics**: Test coverage, documentation score
- **Usage Frequency**: Based on download/installation stats
- **Recency**: Recently updated components get slight boost

## API Integration

### New Endpoints
```
GET /api/v1/registries/{registry}/categories
GET /api/v1/registries/{registry}/{category}/components
GET /api/v1/registries/{registry}/{category}/search
GET /api/v1/registries/{registry}/sources
POST /api/v1/registries/{registry}/build
```

### Enhanced Response Format
```json
{
  "components": [
    {
      "name": "use-form",
      "category": "hooks",
      "sources": ["shadcn_hooks_main", "react_hook_form"],
      "priority_source": "shadcn_hooks_main",
      "quality_score": 0.95,
      "last_updated": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Management and Operations

### Build Pipeline
1. **Configuration Loading**: Load registry configs from `registry_config/`
2. **Source Processing**: Process each source with appropriate extractor
3. **Category Merging**: Merge components from multiple sources per category
4. **Quality Validation**: Run quality checks and validation
5. **Database Update**: Update category-specific JSON files
6. **Index Update**: Update search indexes and vector stores

### Monitoring and Maintenance
- **Source Health**: Monitor source availability and update frequency
- **Quality Metrics**: Track component quality over time
- **Performance Metrics**: Monitor search and build performance
- **Error Tracking**: Log and alert on extraction failures

## SimFlo RAG v2 Implementation Status

### ✅ Achieved
- **Centralized DatabaseManager**: Single source of truth for database operations
- **Standardized Database Paths**: Eliminated 86+ duplicate files
- **Registry CLI Commands**: Complete CLI interface for registry management
- **Vector Database Integration**: ChromaDB with standardized structure
- **Self-Documenting Registry**: simflo-rag registry for system documentation

### 🔄 In Progress
- **Multi-Source Configuration**: Framework ready for implementation
- **Specialized Extractors**: Complex extractors marked for v4.0+
- **Category-Based Organization**: Infrastructure in place

### ⏳ Future (v4.0+)
- **Complex Extractor Implementation**: Full specialized extractors
- **Advanced Search Features**: Category-aware search with weighting
- **Multi-Source Merging**: Priority-based content merging
- **Enhanced API Integration**: RESTful endpoints for registry management

## Migration Strategy

### Phase 1: Infrastructure ✅ (Complete)
- ✅ Create DatabaseManager
- ✅ Develop CLI interface
- ✅ Set up standardized directory structure

### Phase 2: Data Migration ✅ (Complete)
- ✅ Eliminate database duplication
- ✅ Implement centralized database management
- ✅ Create standardized database paths

### Phase 3: Feature Rollout 🔄 (In Progress)
- ✅ Enable basic registry operations
- 🔄 Deploy enhanced search capabilities
- ⏳ Add management CLI tools

### Phase 4: Optimization ⏳ (Planned v4.0+)
- ⏳ Performance tuning
- ⏳ Quality improvements
- ⏳ Additional source types

## Benefits

### Enhanced Hook Coverage
- **Current**: Basic hooks through simple extractors
- **Target v4.0+**: 20+ comprehensive hooks with full metadata

### Multi-Source Flexibility
- **Granular Control**: Enable/disable specific sources
- **Independent Updates**: Update categories without affecting others
- **Source Diversity**: Mix official, community, and third-party sources

### Improved Search Experience
- **Category Precision**: Search within specific component types
- **Source Transparency**: Know which source provided each component
- **Quality Relevance**: Higher quality sources get preference

This design provides a scalable, flexible foundation for comprehensive component and hook discovery while maintaining backward compatibility and enabling future expansion. SimFlo RAG v2 has successfully implemented the core infrastructure and is ready for advanced feature implementation in v4.0+.