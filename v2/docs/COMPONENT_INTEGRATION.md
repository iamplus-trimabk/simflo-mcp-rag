# Component Integration Guide

## Overview

This document provides a comprehensive guide to integrating and using the simflo-rag v2 components. It covers component communication patterns, data flows, and practical usage examples.

## Component Architecture

### System Overview

simflo-rag v2 consists of 5 numbered components that work together to provide a complete RAG (Retrieval-Augmented Generation) system:

```
┌─────────────────────────────────────────────────────────────┐
│                    simflo-rag v2 System                    │
├─────────────────────────────────────────────────────────────┤
│  03-content-collection  │  04-extractors  │  02-rag-builder  │
│  Source Discovery       │  Content        │  Pipeline        │
│  & Acquisition          │  Extraction      │  Orchestration   │
├─────────────────────────────────────────────────────────────┤
│           00-rag-registry (Registry-based Storage)          │
├─────────────────────────────────────────────────────────────┤
│           01-mcp-server (AI Assistant Integration)          │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Key Commands | Integration Points |
|-----------|---------|--------------|-------------------|
| **00-rag-registry** | Registry-based database management | `list`, `info`, `search`, `status`, `clean-db`, `rebuild-db` | All components store/retrieve data |
| **01-mcp-server** | AI assistant integration | `search`, `get-component`, `list-components`, `set-context` | Provides AI access to all registries |
| **02-rag-builder** | Pipeline orchestration | `status`, `list-profiles`, `check` | Coordinates extraction and building |
| **03-content-collection** | Source discovery & acquisition | `discover`, `fetch`, `list-source-types`, `status` | Provides sources to extractors |
| **04-extractors** | Content extraction | `list-extractors`, `run-extractor`, `run-all-extractors`, `status` | Extracts content from collected sources |

## Data Flow Patterns

### Complete Content Pipeline

```bash
# 1. Discover sources
python3 v2/03-content-collection/content_collection_cli.py discover \
  --query "react component library" \
  --source-type github \
  --limit 10 \
  --format json > sources.json

# 2. Fetch content
python3 v2/03-content-collection/content_collection_cli.py fetch \
  --sources-file sources.json \
  --output-dir raw_content/ \
  --format json

# 3. Extract content
python3 v2/04-extractors/extractors_cli.py run-all-extractors \
  --format json

# 4. Build RAG databases
python3 v2/core/02-rag-builder/rag_builder_cli.py build \
  --profile default \
  --format json

# 5. Search via AI assistant
python3 v2/core/01-mcp-server/mcp_server.py search \
  "react button component" \
  --limit 5 \
  --format json
```

### Integration Scenarios

#### Scenario 1: Adding New Component Library

```bash
# 1. Discover new library
python3 v2/03-content-collection/content_collection_cli.py discover \
  --query "ui component library typescript" \
  --source-type github \
  --limit 5

# 2. Fetch and extract
python3 v2/03-content-collection/content_collection_cli.py fetch \
  --sources-file discovered_sources.json

python3 v2/04-extractors/extractors_cli.py run-extractor new_library

# 3. Update registry
python3 v2/core/00-rag-registry/registry.py rebuild-db \
  --registry new_library

# 4. Test integration
python3 v2/core/01-mcp-server/mcp_server.py search \
  "component from new library" \
  --registry new_library
```

#### Scenario 2: AI Assistant Integration

```bash
# Set context for AI assistant
python3 v2/core/01-mcp-server/mcp_server.py set-context \
  reactjs \
  --session-id user-session-123

# AI searches for components
python3 v2/core/01-mcp-server/mcp_server.py search \
  "form validation modal" \
  --limit 10 \
  --platform reactjs

# AI gets component details
python3 v2/core/01-mcp-server/mcp_server.py get-component \
  button \
  --registry shadcn \
  --format json
```

#### Scenario 3: Registry Management

```bash
# List all available registries
python3 v2/core/00-rag-registry/registry.py list

# Get registry information
python3 v2/core/00-rag-registry/registry.py info \
  --name shadcn

# Search across all registries
python3 v2/core/00-rag-registry/registry.py search \
  --query "form input" \
  --limit 10

# Clean and rebuild registry
python3 v2/core/00-rag-registry/registry.py clean-db \
  --registry shadcn

python3 v2/core/00-rag-registry/registry.py rebuild-db \
  --registry shadcn
```

## Component Communication

### CLI Integration Pattern

Components communicate through standardized CLI calls:

```python
import subprocess
import json

def call_component(component_path, command, **kwargs):
    """Generic component communication function"""
    cmd = ['python3', component_path, command]

    # Add arguments
    for key, value in kwargs.items():
        if value is not None:
            cmd.extend([f'--{key.replace("_", "-")}', str(value)])

    # Ensure JSON output
    cmd.extend(['--format', 'json'])

    # Execute command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "success": False,
                "error": result.stderr,
                "command": " ".join(cmd)
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "command": " ".join(cmd)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": " ".join(cmd)
        }
```

### Usage Examples

#### Content Collection to Extractors

```python
# Discover sources
sources = call_component(
    'v2/03-content-collection/content_collection_cli.py',
    'discover',
    query='react components',
    source_type='github',
    limit=5
)

if sources['success']:
    # Fetch content
    fetch_result = call_component(
        'v2/03-content-collection/content_collection_cli.py',
        'fetch',
        sources_file='discovered_sources.json',
        output_dir='raw_content'
    )

    if fetch_result['success']:
        # Run extractors
        extraction_result = call_component(
            'v2/04-extractors/extractors_cli.py',
            'run-all-extractors'
        )
```

#### Registry to MCP Server

```python
# Get available registries
registries = call_component(
    'v2/core/00-rag-registry/registry.py',
    'list'
)

if registries['success']:
    for registry in registries['data']['registries']:
        # Search in each registry
        search_result = call_component(
            'v2/core/01-mcp-server/mcp_server.py',
            'search',
            query='button component',
            registry=registry['name'],
            limit=5
        )
```

## Configuration Management

### Registry Configuration

Each registry has its own configuration:

```json
{
  "registry_config": {
    "shadcn": {
      "name": "shadcn",
      "display_name": "Shadcn UI",
      "description": "Modern React component library",
      "base_path": "v2/core/00-rag-registry/registries/shadcn",
      "extractors": ["shadcn", "shadcn_components", "shadcn_hooks"],
      "enabled": true
    },
    "gluestack": {
      "name": "gluestack",
      "display_name": "Gluestack UI",
      "description": "Universal component library",
      "base_path": "v2/core/00-rag-registry/registries/gluestack",
      "extractors": ["gluestack"],
      "enabled": true
    }
  }
}
```

### Component Configuration

Components can be configured through JSON files:

```json
{
  "content_collection": {
    "default_source_type": "github",
    "max_results": 50,
    "fetch_timeout": 600,
    "output_directory": "fetched_content"
  },
  "extractors": {
    "parallel_execution": false,
    "default_extractors": ["shadcn", "documentation"],
    "output_format": "json"
  },
  "rag_builder": {
    "vector_db_config": {
      "embedding_model": "all-MiniLM-L6-v2",
      "chunk_size": 1000,
      "chunk_overlap": 200
    }
  }
}
```

## Error Handling

### Standard Error Response Format

All components return errors in consistent format:

```json
{
  "success": false,
  "timestamp": "2025-10-01T15:00:00.000Z",
  "data": {
    "error": "Description of error",
    "error_code": "ERROR_TYPE",
    "context": {
      "command": "specific command that failed",
      "parameters": {...}
    }
  }
}
```

### Error Handling Patterns

#### 1. Graceful Degradation

```python
def search_with_fallback(query, registries=None):
    """Search with fallback to other registries"""
    if registries:
        for registry in registries:
            result = call_component(
                'v2/core/01-mcp-server/mcp_server.py',
                'search',
                query=query,
                registry=registry
            )
            if result['success'] and result['data'].get('results'):
                return result

    # Fallback to all registries
    return call_component(
        'v2/core/01-mcp-server/mcp_server.py',
        'search',
        query=query
    )
```

#### 2. Retry Logic

```python
def call_with_retry(component_path, command, max_retries=3, **kwargs):
    """Call component with retry logic"""
    for attempt in range(max_retries):
        result = call_component(component_path, command, **kwargs)

        if result['success']:
            return result
        elif attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    return result
```

#### 3. Validation

```python
def validate_component_response(response, required_fields=None):
    """Validate component response structure"""
    if not isinstance(response, dict):
        return False

    if 'success' not in response:
        return False

    if response['success'] and 'data' not in response:
        return False

    if required_fields:
        for field in required_fields:
            if field not in response.get('data', {}):
                return False

    return True
```

## Performance Optimization

### Parallel Execution

```python
import concurrent.futures

def parallel_search(query, registries):
    """Search multiple registries in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                call_component,
                'v2/core/01-mcp-server/mcp_server.py',
                'search',
                query=query,
                registry=registry
            ): registry for registry in registries
        }

        results = {}
        for future in concurrent.futures.as_completed(futures):
            registry = futures[future]
            try:
                results[registry] = future.result()
            except Exception as e:
                results[registry] = {"success": False, "error": str(e)}

    return results
```

### Caching

```python
import functools
import hashlib

def cache_key(func_name, **kwargs):
    """Generate cache key for function calls"""
    key_data = f"{func_name}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

@functools.lru_cache(maxsize=128)
def cached_search(query, registry=None):
    """Cached search function"""
    return call_component(
        'v2/core/01-mcp-server/mcp_server.py',
        'search',
        query=query,
        registry=registry
    )
```

## Monitoring and Observability

### Component Status Monitoring

```python
def get_system_status():
    """Get status of all components"""
    components = {
        'registry': 'v2/core/00-rag-registry/registry.py',
        'mcp_server': 'v2/core/01-mcp-server/mcp_server.py',
        'rag_builder': 'v2/core/02-rag-builder/rag_builder_cli.py',
        'content_collection': 'v2/03-content-collection/content_collection_cli.py',
        'extractors': 'v2/04-extractors/extractors_cli.py'
    }

    status = {}
    for name, path in components.items():
        result = call_component(path, 'status')
        status[name] = result

    return {
        "timestamp": datetime.now().isoformat(),
        "components": status,
        "overall_health": all(
            comp.get('success', False)
            for comp in status.values()
        )
    }
```

### Performance Metrics

```python
import time

def measure_component_performance(component_path, command, **kwargs):
    """Measure component performance"""
    start_time = time.time()

    result = call_component(component_path, command, **kwargs)

    end_time = time.time()

    return {
        "result": result,
        "performance": {
            "execution_time": end_time - start_time,
            "timestamp": datetime.now().isoformat(),
            "component": component_path,
            "command": command
        }
    }
```

## Best Practices

### 1. Error Handling
- Always check the `success` field in responses
- Implement fallback mechanisms
- Use meaningful error messages
- Log errors for debugging

### 2. Performance
- Use parallel execution where possible
- Implement caching for expensive operations
- Monitor component performance
- Optimize CLI argument processing

### 3. Security
- Validate all inputs
- Use absolute paths
- Implement proper error handling
- Avoid exposing sensitive information

### 4. Maintenance
- Keep component interfaces stable
- Use semantic versioning
- Document all changes
- Test thoroughly before deployment

### 5. Integration
- Use standard JSON format
- Implement consistent error handling
- Provide comprehensive logging
- Support both JSON and table outputs

## Troubleshooting

### Common Issues

1. **Component Not Found**
   ```bash
   # Check if component exists and is executable
   ls -la v2/component-path/
   python3 v2/component-path/cli.py --help
   ```

2. **Import Errors**
   ```bash
   # Check Python path and dependencies
   python3 -c "import sys; print(sys.path)"
   cd v2 && python3 component-path/cli.py --help
   ```

3. **Permission Issues**
   ```bash
   # Make CLI scripts executable
   chmod +x v2/*/cli.py
   chmod +x v2/*/tests/run.py
   ```

4. **Test Failures**
   ```bash
   # Run tests with verbose output
   python3 v2/component-path/tests/run.py --verbose

   # Check individual test
   python3 v2/tests/cmd_test_executor.py v2/component-path/tests/tests.json
   ```

### Debug Commands

```bash
# Check all component statuses
for component in registry mcp_server rag_builder content_collection extractors; do
    echo "=== $component ==="
    python3 v2/*$component*/cli.py status --format table
    echo
done

# Test basic functionality
python3 v2/core/01-mcp-server/mcp_server.py search "test" --limit 1
python3 v2/core/00-rag-registry/registry.py list
python3 v2/04-extractors/extractors_cli.py list-extractors
```

This integration guide provides comprehensive information for using and integrating simflo-rag v2 components effectively.