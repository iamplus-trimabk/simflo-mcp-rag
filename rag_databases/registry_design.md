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

### Target Structure
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

#### 1. shadcn_hooks_extractor.py
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

#### 2. shadcn_blocks_extractor.py
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

#### 3. npm_hooks_extractor.py
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

#### 4. community_extractor.py
**Purpose**: Process community-contributed components and hooks

**Why needed:**
- **Quality Assessment**: Community submissions vary in quality
- **Security Scanning**: Need to detect potentially malicious code
- **Standardization**: Different coding styles and patterns
- **Metadata Validation**: Ensure required metadata is present
- **Licensing**: Check license compatibility and attribution

**Unique Requirements:**
- Code quality analysis and security scanning
- Automated testing and validation
- Standardization formatting
- Review workflow integration
- Attribution and license management

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

## Migration Strategy

### Phase 1: Infrastructure
- Create configuration manager
- Develop specialized extractors
- Set up new directory structure

### Phase 2: Data Migration
- Convert existing registry configs
- Migrate component data to category structure
- Test backward compatibility

### Phase 3: Feature Rollout
- Enable multi-source extraction
- Deploy enhanced search capabilities
- Add management CLI tools

### Phase 4: Optimization
- Performance tuning
- Quality improvements
- Additional source types

## Benefits

### Enhanced Hook Coverage
- **Current**: Limited to basic hooks
- **Target**: 20+ comprehensive hooks with full metadata

### Multi-Source Flexibility
- **Granular Control**: Enable/disable specific sources
- **Independent Updates**: Update categories without affecting others
- **Source Diversity**: Mix official, community, and third-party sources

### Improved Search Experience
- **Category Precision**: Search within specific component types
- **Source Transparency**: Know which source provided each component
- **Quality Relevance**: Higher quality sources get preference

This design provides a scalable, flexible foundation for comprehensive component and hook discovery while maintaining backward compatibility and enabling future expansion.