# Component Architecture Principles and Standards

## Overview

This document defines the core architecture principles, standards, and guidelines for all components in the simflo-rag v2 system. These principles ensure consistency, maintainability, and quality across all components.

## Core Architecture Principles

### 1. CLI-First Communication

**Principle**: All component-to-component communication MUST use CLI interfaces.

**Rationale**:
- No language dependencies between components
- Component crashes don't cascade to other components
- Easy parallelization and distributed execution
- Clear, testable interfaces

**Implementation**:
```python
# Good: CLI interface
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    # Process data
    result = process_data(args.input)

    # Write output
    with open(args.output, 'w') as f:
        json.dump(result, f)

# Bad: Direct function calls between components
def component_a_function():
    # Direct call to component b
    return component_b_function()
```

### 2. Evolutionary Development

**Principle**: Small batches only (2-3 tasks maximum), emergent design, no big-upfront planning.

**Rationale**:
- Reduces complexity and cognitive load
- Allows design to emerge from implementation
- Faster feedback loops
- Adapts to changing requirements

**Implementation**:
- Never plan more than 2-3 tasks ahead
- Let architecture emerge from implementation
- Design for the current need, not hypothetical future needs
- Refactor when patterns emerge

### 3. Single Responsibility

**Principle**: Each component has a single, well-defined responsibility.

**Rationale**:
- Easier to understand and maintain
- Reduced coupling between components
- Better testability
- Clear boundaries and interfaces

**Implementation**:
```python
# Good: Single responsibility
class ContentExtractor:
    def extract_content(self, source):
        pass

class ContentValidator:
    def validate_content(self, content):
        pass

# Bad: Multiple responsibilities
class ContentManager:
    def extract_content(self, source):
        pass

    def validate_content(self, content):
        pass

    def store_content(self, content):
        pass
```

### 4. Dependency Injection

**Principle**: Components should not create their dependencies; dependencies should be injected.

**Rationale**:
- Better testability
- Loose coupling
- Easier to swap implementations
- Clear dependency relationships

**Implementation**:
```python
# Good: Dependency injection
class DataProcessor:
    def __init__(self, storage_engine, validator):
        self.storage_engine = storage_engine
        self.validator = validator

    def process(self, data):
        validated_data = self.validator.validate(data)
        return self.storage_engine.store(validated_data)

# Bad: Creating dependencies
class DataProcessor:
    def __init__(self):
        self.storage_engine = PostgreSQLEngine()
        self.validator = DataValidator()
```

### 5. Error Handling and Resilience

**Principle**: Components must handle errors gracefully and provide meaningful feedback.

**Rationale**:
- Prevents cascading failures
- Better debugging and troubleshooting
- Improved user experience
- System stability

**Implementation**:
```python
# Good: Comprehensive error handling
def process_data(input_path, output_path):
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)

        if not validate_input(data):
            raise ValueError("Invalid input data")

        result = transform_data(data)

        with open(output_path, 'w') as f:
            json.dump(result, f)

        return {"status": "success", "code": 0}

    except FileNotFoundError as e:
        return {"status": "error", "code": 1, "message": f"File not found: {e}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "code": 2, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"status": "error", "code": 3, "message": f"Unexpected error: {e}"}

# Bad: Minimal error handling
def process_data(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)
    result = transform_data(data)
    with open(output_path, 'w') as f:
        json.dump(result, f)
```

## Component Design Standards

### 1. Standard Component Structure

```
component-name/
├── __init__.py          # Component exports
├── main.py             # Main CLI entry point
├── core.py             # Core functionality
├── cli.py              # CLI interface logic
├── config.py           # Configuration handling
├── utils.py            # Utility functions
├── tests/              # Test files
│   ├── test_core.py
│   ├── test_cli.py
│   └── test_utils.py
└── CLAUDE.md           # Component documentation
```

### 2. CLI Interface Standard

**Required Arguments**:
- `--input`: Input file path (JSON)
- `--output`: Output file path (JSON)
- `--config`: Configuration file path (JSON)
- `--verbose`: Verbose output
- `--help`: Help information

**Exit Codes**:
- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Input validation error
- `4`: Processing error
- `5`: System error

### 3. Data Exchange Format

**Standard Request Format**:
```json
{
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "operation": "operation_name",
  "input": {},
  "config": {},
  "metadata": {}
}
```

**Standard Response Format**:
```json
{
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "operation": "operation_name",
  "output": {},
  "status": {
    "code": 0,
    "message": "Success"
  },
  "metadata": {}
}
```

**Error Response Format**:
```json
{
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "operation": "operation_name",
  "error": {
    "code": 1,
    "message": "Error description",
    "details": {}
  },
  "status": {
    "code": 1,
    "message": "Error"
  }
}
```

### 4. Configuration Management

**Principle**: Configuration should be external, environment-specific, and version-controlled.

**Implementation**:
```python
# Good: External configuration
class ComponentConfig:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    @property
    def database_url(self):
        return self.config.get('database_url')

    @property
    def api_key(self):
        return self.config.get('api_key')

# Bad: Hardcoded configuration
class ComponentConfig:
    def __init__(self):
        self.database_url = "postgresql://localhost:5432/db"
        self.api_key = "hardcoded-key"
```

### 5. Logging Standards

**Principle**: Comprehensive logging for debugging, monitoring, and auditing.

**Implementation**:
```python
import logging
import json
from datetime import datetime

class ComponentLogger:
    def __init__(self, component_name):
        self.logger = logging.getLogger(component_name)
        self.component_name = component_name

        # Configure logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_operation(self, operation, input_data, output_data, status):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": self.component_name,
            "operation": operation,
            "input_size": len(str(input_data)),
            "output_size": len(str(output_data)),
            "status": status
        }
        self.logger.info(json.dumps(log_entry))

    def log_error(self, operation, error, details=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": self.component_name,
            "operation": operation,
            "error": str(error),
            "details": details
        }
        self.logger.error(json.dumps(log_entry))
```

## Quality Standards

### 1. Testing Requirements

**Unit Tests**:
- Minimum 80% code coverage
- Test all public methods
- Mock external dependencies
- Test error conditions

**Integration Tests**:
- Test CLI interfaces
- Test data flow between components
- Test with real data samples
- Test error scenarios

**E2E Tests**:
- Test complete workflows
- Test with production-like data
- Test performance and scalability
- Test disaster recovery

### 2. Code Quality Standards

**Python Code Style**:
- Follow PEP 8 guidelines
- Use type hints consistently
- Maximum line length: 88 characters
- Use meaningful variable and function names
- Write comprehensive docstrings

**Security Standards**:
- Validate all inputs
- Sanitize all outputs
- Never hardcode secrets
- Use secure communication protocols
- Implement proper authentication and authorization

### 3. Performance Standards

**Response Time**:
- CLI operations: < 5 seconds for typical operations
- Batch processing: < 60 seconds for standard batches
- Large datasets: Provide progress feedback

**Resource Usage**:
- Memory: Monitor and limit memory usage
- CPU: Optimize for CPU-intensive operations
- Storage: Clean up temporary files
- Network: Minimize network calls

## Documentation Standards

### 1. Component Documentation

Each component must have:
- **CLAUDE.md**: Purpose, boundaries, CLI interfaces
- **README.md**: Usage examples and setup instructions
- **API Documentation**: Generated from code
- **Changelog**: Version history and changes

### 2. Code Documentation

**Docstring Format**:
```python
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data and return transformed results.

    Args:
        data: Input data dictionary containing:
            - source: Data source identifier
            - content: Raw content to process
            - metadata: Additional metadata

    Returns:
        Dictionary containing:
            - processed_content: Transformed content
            - extracted_metadata: Extracted metadata
            - processing_stats: Processing statistics

    Raises:
        ValueError: If input data is invalid
        ProcessingError: If processing fails
    """
```

### 3. CLI Help Documentation

Each CLI command must provide:
- Usage examples
- Argument descriptions
- Configuration options
- Error code explanations
- Version information

## Deployment and Operations

### 1. Packaging Standards

**Requirements**:
- All dependencies in requirements.txt
- Version pinning for production
- Separate dev and production dependencies
- Security scanning of dependencies

**Containerization**:
- Dockerfile for each component
- Multi-stage builds for size optimization
- Security scanning of containers
- Non-root user execution

### 2. Monitoring and Observability

**Metrics**:
- Operation success/failure rates
- Response times and throughput
- Resource usage (CPU, memory, disk)
- Error rates and types

**Logging**:
- Structured JSON logging
- Log aggregation and analysis
- Log rotation and retention
- Sensitive data filtering

### 3. Backup and Recovery

**Data Backup**:
- Automated daily backups
- Off-site backup storage
- Backup encryption
- Backup verification

**Disaster Recovery**:
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Documentation of recovery procedures
- Regular testing of recovery procedures

## Evolution and Maintenance

### 1. Version Management

**Semantic Versioning**:
- MAJOR version for breaking changes
- MINOR version for new features
- PATCH version for bug fixes
- Clear deprecation policy

**Backward Compatibility**:
- Maintain CLI interface compatibility
- Provide migration guides for breaking changes
- Support multiple versions during transition
- Clear communication of changes

### 2. Refactoring Guidelines

**When to Refactor**:
- Code complexity increases
- Performance issues identified
- Security vulnerabilities discovered
- New requirements emerge

**Refactoring Process**:
- Write comprehensive tests first
- Refactor in small increments
- Test after each change
- Update documentation

### 3. Technical Debt Management

**Identification**:
- Regular code reviews
- Static analysis tools
- Performance profiling
- Security scanning

**Prioritization**:
- Security issues first
- Performance bottlenecks
- Maintenance complexity
- User impact

## Compliance and Governance

### 1. Security Compliance

**Data Protection**:
- Encrypt sensitive data at rest
- Encrypt data in transit
- Implement access controls
- Regular security audits

**Privacy Compliance**:
- Data minimization principles
- User consent management
- Data retention policies
- Privacy impact assessments

### 2. Legal and Regulatory

**License Compliance**:
- Track all third-party licenses
- Ensure open-source compliance
- Document license requirements
- Regular license audits

**Data Governance**:
- Data classification policies
- Data lineage tracking
- Quality standards and metrics
- Regulatory compliance checks

## Conclusion

These architecture principles and standards provide the foundation for building a maintainable, scalable, and high-quality simflo-rag system. By following these guidelines, we ensure consistency across all components while enabling evolutionary development and continuous improvement.

All team members should familiarize themselves with these standards and apply them consistently throughout the development process. Regular reviews and updates to these standards will ensure they remain relevant and effective as the system evolves.