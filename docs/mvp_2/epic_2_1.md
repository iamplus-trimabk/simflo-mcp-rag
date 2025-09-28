# Epic 2.1: Specialized Extractors Implementation

## Overview

**Epic ID**: EPIC-2.1
**Priority**: High
**Status**: Planning
**Target MVP**: MVP 2
**Estimated Duration**: 3-4 weeks

## Problem Statement

Currently, the SimFlo MCP RAG system has limited hook coverage (only 1 hook: use-mobile) despite shadcn/ui offering 20+ comprehensive hooks. The existing monolithic extraction approach cannot handle the diverse nature of components, hooks, and blocks from multiple sources. We need specialized extractors to properly process different content types with their unique patterns, dependencies, and metadata requirements.

## Business Impact

### Current Limitations
- **Poor Hook Coverage**: Only 1 out of 20+ shadcn hooks available
- **Generic Extraction**: One-size-fits-all approach misses specialized metadata
- **Single Source Limitation**: Each registry limited to one source per category
- **Quality Issues**: No specialized validation for different content types

### Expected Improvements
- **20x Hook Coverage**: From 1 to 20+ comprehensive hooks with full metadata
- **Multi-Source Flexibility**: Enable/disable specific sources independently
- **Quality Enhancement**: Specialized validation and security scanning
- **Developer Experience**: Rich metadata, usage examples, and dependency tracking

## Technical Architecture

### Core Components

#### 1. Registry Configuration Manager
```python
# Location: services/registry_config_manager.py
class RegistryConfigManager:
    def load_registry_config(self, registry_name: str) -> dict
    def validate_config(self, config: dict) -> bool
    def get_active_sources(self, registry_name: str, category: str) -> list
```

#### 2. Extractor Factory
```python
# Location: extractors/extractor_factory.py
class ExtractorFactory:
    def create_extractor(self, source_type: str, extractor_type: str) -> BaseExtractor
    def get_available_extractors(self) -> dict
    def validate_extractor_compatibility(self, source: dict) -> bool
```

#### 3. Specialized Extractors

##### Shadcn Hooks Extractor
```python
# Location: extractors/shadcn_hooks_extractor.py
class ShadcnHooksExtractor(BaseExtractor):
    def extract_hooks(self, source: dict) -> list
    def parse_hook_dependencies(self, hook_code: str) -> dict
    def extract_hook_metadata(self, hook_file: str) -> dict
    def validate_hook_structure(self, hook: dict) -> bool
```

##### Shadcn Blocks Extractor
```python
# Location: extractors/shadcn_blocks_extractor.py
class ShadcnBlocksExtractor(BaseExtractor):
    def extract_blocks(self, source: dict) -> list
    def parse_block_composition(self, block_code: str) -> dict
    def extract_layout_metadata(self, block: dict) -> dict
    def validate_responsive_design(self, block: dict) -> bool
```

##### NPM Hooks Extractor
```python
# Location: extractors/npm_hooks_extractor.py
class NPMHooksExtractor(BaseExtractor):
    def extract_package_hooks(self, package_name: str) -> list
    def parse_type_definitions(self, types_file: str) -> dict
    def resolve_dependencies(self, package: dict) -> dict
    def extract_npm_metadata(self, package_name: str) -> dict
```

##### Community Extractor
```python
# Location: extractors/community_extractor.py
class CommunityExtractor(BaseExtractor):
    def extract_community_components(self, source: dict) -> list
    def perform_security_scan(self, component: dict) -> dict
    def assess_code_quality(self, component: dict) -> float
    def validate_license_compliance(self, component: dict) -> bool
```

#### 4. Multi-Source Merger
```python
# Location: services/multi_source_merger.py
class MultiSourceMerger:
    def merge_sources(self, components: list, sources: list) -> list
    def resolve_conflicts(self, conflicts: list) -> list
    def calculate_quality_scores(self, components: list) -> list
    def apply_source_boosting(self, components: list) -> list
```

## Implementation Plan

### Phase 1: Infrastructure Foundation (Week 1-2)

#### 1.1 Registry Configuration System
- [ ] Create `rag_databases/registry_config/` directory structure
- [ ] Implement `RegistryConfigManager` class
- [ ] Convert existing `registry_config.json` to modular format
- [ ] Create individual registry configs (shadcn.json, gluestack.json, etc.)
- [ ] Add configuration validation and schema checking

#### 1.2 Extractor Base Architecture
- [ ] Define `BaseExtractor` abstract class
- [ ] Implement `ExtractorFactory` for dynamic extractor creation
- [ ] Create extractor interface contracts
- [ ] Set up error handling and logging framework
- [ ] Implement extractor registration system

#### 1.3 Data Model Updates
- [ ] Update component schema to support multi-source metadata
- [ ] Add quality score and source tracking fields
- [ ] Implement conflict resolution data structures
- [ ] Create category-specific data models (hooks, blocks, components)

### Phase 2: Specialized Extractors (Week 2-3)

#### 2.1 Shadcn Hooks Extractor
- [ ] Implement hook pattern recognition (`use-*` prefix detection)
- [ ] Create dependency parser for React and external libraries
- [ ] Add TypeScript interface extraction for generic types
- [ ] Implement custom hook logic analysis
- [ ] Add JSDoc parsing for documentation extraction

#### 2.2 Shadcn Blocks Extractor
- [ ] Implement block composition analysis (multiple components)
- [ ] Create layout logic parser for responsive design
- [ ] Add configuration options extraction
- [ ] Implement template-based content processing
- [ ] Add component dependency tracking within blocks

#### 2.3 NPM Hooks Extractor
- [ ] Implement package.json analysis for hook exports
- [ ] Create .d.ts file parser for type definitions
- [ ] Add dependency resolution for transitive dependencies
- [ ] Implement version management and compatibility checking
- [ ] Add npm registry metadata extraction

#### 2.4 Community Extractor
- [ ] Implement code quality analysis algorithms
- [ ] Create security scanning patterns
- [ ] Add license validation and attribution tracking
- [ ] Implement standardization formatting
- [ ] Add review workflow integration

### Phase 3: Multi-Source Integration (Week 3-4)

#### 3.1 Multi-Source Merger
- [ ] Implement priority-based conflict resolution
- [ ] Create quality scoring algorithms
- [ ] Add source boosting for search relevance
- [ ] Implement platform conflict resolution
- [ ] Add dependency version merging logic

#### 3.2 Search System Enhancement
- [ ] Update search to support category-aware queries
- [ ] Implement source transparency in results
- [ ] Add quality-based result ranking
- [ ] Create category-weighted search scoring
- [ ] Implement cross-category search functionality

#### 3.3 API Updates
- [ ] Add new endpoints for multi-source registries
- [ ] Update existing endpoints to support new data model
- [ ] Implement source management endpoints
- [ ] Add quality and source filtering options
- [ ] Create registry build endpoint

#### 3.4 MCP Server Updates
- [ ] Update MCP tools to support new search capabilities
- [ ] Add source filtering to component search
- [ ] Implement category-specific search tools
- [ ] Add registry management tools
- [ ] Update installation guides with new metadata

## Technical Specifications

### Registry Configuration Schema
```json
{
  "registry_name": "shadcn",
  "display_name": "Shadcn UI",
  "description": "Modern React component library",
  "platforms": ["reactjs"],
  "database_path": "rag_databases/shadcn_db",
  "status": "active",
  "categories": {
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
    },
    "hooks": {
      "enabled": true,
      "sources": [
        {
          "name": "shadcn_hooks_main",
          "type": "github",
          "url": "https://github.com/shadcn-ui/ui",
          "branch": "main",
          "registry_file": "apps/www/registry/registry-hooks.ts",
          "extractor": "shadcn_hooks",
          "priority": 1,
          "update_frequency": "weekly"
        },
        {
          "name": "react_hook_form",
          "type": "npm",
          "package": "@hookform/resolvers",
          "extractor": "npm_hooks",
          "priority": 2,
          "update_frequency": "monthly"
        }
      ]
    },
    "blocks": {
      "enabled": true,
      "sources": [
        {
          "name": "shadcn_blocks_main",
          "type": "github",
          "url": "https://github.com/shadcn-ui/ui",
          "branch": "main",
          "registry_file": "apps/www/registry/registry-blocks.ts",
          "extractor": "shadcn_blocks",
          "priority": 1,
          "update_frequency": "weekly"
        }
      ]
    }
  },
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
  },
  "metadata": {
    "version": "1.0.0",
    "maintainer": "shadcn",
    "license": "MIT",
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

### Enhanced Component Schema
```json
{
  "name": "use-form",
  "category": "hooks",
  "type": "hook",
  "sources": ["shadcn_hooks_main", "react_hook_form"],
  "priority_source": "shadcn_hooks_main",
  "quality_score": 0.95,
  "description": "Form management hook with validation",
  "dependencies": ["react", "react-hook-form"],
  "peer_dependencies": ["@hookform/resolvers"],
  "installation": "npx shadcn@latest add use-form",
  "usage_examples": [
    "const { control, handleSubmit } = useForm({\n  resolver: zodResolver(schema)\n})"
  ],
  "metadata": {
    "hook_signature": "useForm<T>(options?: UseFormProps<T>): UseFormReturn<T>",
    "return_types": {
      "control": "Control<T>",
      "handleSubmit": "SubmitHandler<T>",
      "formState": "FormState<T>"
    },
    "generics": ["T extends FieldValues"],
    "last_updated": "2024-01-01T00:00:00Z"
  },
  "platform": ["reactjs"],
  "registry": "shadcn",
  "source_metadata": {
    "shadcn_hooks_main": {
      "extracted_at": "2024-01-01T00:00:00Z",
      "version": "latest",
      "commit": "abc123"
    },
    "react_hook_form": {
      "extracted_at": "2024-01-01T00:00:00Z",
      "version": "7.0.0",
      "package_version": "7.0.0"
    }
  }
}
```

## Quality Requirements

### Code Quality Standards
- [ ] **Test Coverage**: 90%+ coverage for all extractors
- [ ] **Type Safety**: 100% TypeScript coverage, no `any` types
- [ ] **Error Handling**: Comprehensive error handling and logging
- [ ] **Performance**: Extraction must complete within 5 minutes per source
- [ ] **Memory Usage**: Must handle large registries without memory leaks

### Data Quality Standards
- [ ] **Metadata Completeness**: 95%+ components must have complete metadata
- [ **Dependency Accuracy**: 100% accurate dependency tracking
- [ ] **Installation Commands**: 100% working installation commands
- [ ] **Usage Examples**: 80%+ components must have working examples
- [ ] **Quality Scores**: Must be calculated and updated automatically

### Security Standards
- [ ] **Input Validation**: All external inputs must be validated
- [ ] **Security Scanning**: Community content must be security scanned
- [ ] **License Compliance**: All components must have valid licenses
- [ ] **Sandbox Isolation**: Extractors must run in isolated environments
- [ ] **Access Control**: Limited access to external APIs and resources

## Success Criteria

### Functional Requirements
- [ ] Extract 20+ shadcn hooks with complete metadata
- [ ] Support 4+ source types (GitHub, NPM, API, Local)
- [ ] Enable multi-source configuration per registry
- [ ] Implement priority-based conflict resolution
- [ ] Provide category-aware search capabilities

### Performance Requirements
- [ ] Search response time < 500ms for 1000+ components
- [ ] Extraction time < 5 minutes per source
- [ ] Memory usage < 512MB for large registries
- [ ] Support 100+ concurrent search requests
- [ ] Database queries < 100ms for complex searches

### User Experience Requirements
- [ ] Rich component metadata with dependencies and examples
- [ ] Source transparency in search results
- [ ] Quality-based result ranking
- [ ] Category-specific search tools
- [ ] Working installation commands

## Dependencies

### Internal Dependencies
- [ ] MCP Server (✅ Complete)
- [ ] API Server (✅ Complete)
- [ ] Registry Configuration System (🚧 In Progress)
- [ ] Search Engine (🚧 Needs Enhancement)

### External Dependencies
- [ ] shadcn/ui GitHub Repository
- [ ] npm Registry API
- [ ] React Hook Form Package
- [ ] TypeScript Compiler API
- [ ] Security scanning libraries

## Risks and Mitigation

### Technical Risks
- **Risk**: Complex hook pattern recognition may miss edge cases
  **Mitigation**: Implement comprehensive test suite with known hook patterns
- **Risk**: Multi-source merging may create conflicts
  **Mitigation**: Implement robust conflict resolution and manual override
- **Risk**: Performance issues with large registries
  **Mitigation**: Implement pagination and caching strategies

### Project Risks
- **Risk**: Scope creep with additional extractor types
  **Mitigation**: Stick to core 4 extractors, plan additional for future sprints
- **Risk**: Integration complexity with existing system
  **Mitigation**: Maintain backward compatibility during transition
- **Risk**: Quality assurance challenges
  **Mitigation**: Implement automated testing and validation pipeline

## Testing Strategy

### Unit Testing
- [ ] Test each extractor in isolation
- [ ] Mock external API responses
- [ ] Validate output schemas and formats
- [ ] Test error handling scenarios

### Integration Testing
- [ ] Test multi-source merging pipeline
- [ ] Validate search functionality with new data
- [ ] Test MCP server integration
- [ ] Validate configuration management

### End-to-End Testing
- [ ] Complete extraction workflow testing
- [ ] Real-world registry extraction testing
- [ ] Performance and load testing
- [ ] User acceptance testing with AI assistants

## Rollout Plan

### Phase 1: Infrastructure (Week 1-2)
- Deploy registry configuration system
- Implement base extractor architecture
- Update data models and schemas

### Phase 2: Extractor Development (Week 2-3)
- Deploy specialized extractors one by one
- Test each extractor with real data
- Validate output quality and completeness

### Phase 3: Integration (Week 3-4)
- Deploy multi-source merger
- Update search and API endpoints
- Test complete workflow with real registries

### Phase 4: Optimization (Week 4)
- Performance tuning and optimization
- Bug fixes and stability improvements
- Documentation and deployment guides

## Metrics and Monitoring

### Key Performance Indicators
- **Hook Coverage**: Track number of hooks extracted (Target: 20+)
- **Source Diversity**: Monitor active sources per registry (Target: 2-3 per category)
- **Quality Scores**: Average component quality (Target: 0.8+)
- **Search Performance**: Response time metrics (Target: <500ms)
- **Error Rates**: Extraction and search error rates (Target: <1%)

### Monitoring Dashboard
- Real-time extraction status
- Source health monitoring
- Quality score trends
- Search performance metrics
- Error and exception tracking

## Future Enhancements

### Near Future (Next Quarter)
- [ ] Additional source types (GitLab, Bitbucket)
- [ ] More specialized extractors (Vue, Svelte components)
- [ ] Advanced quality assessment algorithms
- [ ] Automated extraction scheduling

### Long Term (Next Year)
- [ ] Machine learning for component recommendation
- [ ] Automated dependency conflict resolution
- [ ] Cross-registry component compatibility
- [ ] Community contribution platform

## Conclusion

This epic will transform the SimFlo MCP RAG system from a basic component search tool into a comprehensive, multi-source registry management system. By implementing specialized extractors, we'll dramatically improve hook coverage, enable flexible source management, and provide rich metadata for better developer experience.

The phased approach ensures incremental delivery while maintaining system stability throughout the transformation. Quality obsession remains central to the implementation, with comprehensive testing and validation at each phase.

## Related Documents

- [Registry Design Document](../rag_databases/registry_design.md)
- [MVP 2 Plan](./mvp_2_plan.md)
- [Technical Architecture](../docs/architecture/technical_architecture.md)
- [API Documentation](../docs/api/api_documentation.md)

---
*Last Updated: 2024-01-01*
*Status: Planning*