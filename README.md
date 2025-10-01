# simflo-rag v2: CLI-First RAG Architecture

**A CLI-first Retrieval-Augmented Generation system that demonstrates how command-line interfaces can provide simplicity, maintainability, and natural composition for RAG systems.**

## 🏗️ Architecture Overview

### Numbered Component System

```
simflo-rag v2/
├── 00-rag-registry/      # ✅ Registry-based database management
├── 01-mcp-server/        # ✅ AI assistant integration (12 commands)
├── 02-rag-builder/       # ✅ Pipeline orchestration
├── 03-content-collection/ # ✅ Source discovery & acquisition
└── 04-extractors/        # ✅ Content extraction (11 extractors)
```

### CLI-First Design Philosophy

- **All component communication via CLI interfaces**
- **JSON standardization across all components**
- **Direct module calls eliminate HTTP overhead**
- **Unix pipeline principles for data flow**
- **Comprehensive JSON-based testing framework**

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python3 --version

# Git required for content fetching
git --version

# Required Python packages
pip install requests
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd simflo-mcp-rag

# Make CLI scripts executable
find v2 -name "*.py" -path "*/cli.py" -exec chmod +x {} \;
find v2 -name "run.py" -exec chmod +x {} \;

# Setup command aliases (one-time setup)
source commands.sh

# Or add to your shell profile for persistence
echo 'source $(pwd)/commands.sh' >> ~/.bashrc
source ~/.bashrc
```

### Basic Usage

#### 1. System Status Check

```bash
# Check all component statuses
rag_registry status
mcp_server list-registries
extractors status

# Or use the quick status command
simflo_status
```

#### 2. Component Search (AI Assistant Integration)

```bash
# Search for React components
mcp_server search "react button" --limit 5

# Get detailed component information
mcp_server get-component button --registry shadcn
```

#### 3. Content Discovery and Acquisition

```bash
# Discover new component libraries
content_collection discover \
  --query "react component library" \
  --source-type github \
  --limit 10

# List available source types
content_collection list-source-types
```

#### 4. Registry Management

```bash
# List all available registries
rag_registry list

# Search across all registries
rag_registry search --query "form input" --limit 5

# Get registry information
rag_registry info --name shadcn
```

#### 5. Content Extraction

```bash
# List available extractors
extractors list-extractors

# Run specific extractor
extractors run-extractor shadcn

# Run all extractors
extractors run-all-extractors
```

## 📚 Documentation

### Core Documentation

- **[CLI-First Architecture Guide](v2/docs/CLI-FIRST_ARCHITECTURE.md)** - Architecture patterns and CLI design
- **[Component Integration Guide](v2/docs/COMPONENT_INTEGRATION.md)** - Integration patterns and examples

## 🧪 Testing

### Run All Tests

```bash
# Test all components
python3 v2/core/00-rag-registry/tests/run.py --verbose
python3 v2/core/01-mcp-server/tests/run.py --verbose
python3 v2/03-content-collection/tests/run.py --verbose
python3 v2/04-extractors/tests/run.py --verbose

# Or use the test executor with aliases
test_executor v2/core/00-rag-registry/tests/cmd_tests.json
test_executor v2/core/01-mcp-server/tests/mcp_tests.json
test_executor v2/03-content-collection/tests/content_collection_tests.json
test_executor v2/04-extractors/tests/extractor_tests.json
```

### Test Results Summary

| Component | Test Cases | Pass Rate | Status |
|-----------|------------|-----------|--------|
| 00-rag-registry | 8 tests | 100% | ✅ Complete |
| 01-mcp-server | 14 tests | 100% | ✅ Complete |
| 03-content-collection | 8 tests | 62.5% | ✅ Functional |
| 04-extractors | 8 tests | 100% | ✅ Complete |

### Individual Test Execution

```bash
# Run specific test file
test_executor v2/core/01-mcp-server/tests/mcp_tests.json

# Run with output file
python3 v2/core/00-rag-registry/tests/run.py --output test_results.json
```

## 📚 Documentation

### Core Documentation

- **[CLI-First Architecture Guide](v2/docs/CLI-FIRST_ARCHITECTURE.md)** - Comprehensive architecture documentation
- **[Component Integration Guide](v2/docs/COMPONENT_INTEGRATION.md)** - Integration patterns and examples
- **[Interactive Presentation](v2/docs/interactive-presentation.html)** - Visual research presentation

### Component Documentation

Each component includes its own `CLAUDE.md` with:
- Component purpose and responsibilities
- CLI command reference
- Integration patterns
- Test coverage information

## 🔧 Component Reference

### 00-rag-registry: Registry Management

**Purpose:** Registry-based RAG database management with CLI commands

**Key Commands:**
```bash
rag_registry list --format json
rag_registry search --query "button" --limit 5
rag_registry info --name shadcn
rag_registry status
```

### 01-mcp-server: AI Assistant Integration

**Purpose:** AI assistant integration via CLI (12 commands)

**Key Commands:**
```bash
mcp_server search "button" --limit 10
mcp_server get-component dialog --registry shadcn
mcp_server set-context reactjs --session-id abc123
mcp_server list-registries
```

### 02-rag-builder: Pipeline Orchestration

**Purpose:** Pipeline orchestration and RAG construction

**Key Commands:**
```bash
rag_builder status
rag_builder list-profiles
rag_builder check
```

### 03-content-collection: Source Discovery

**Purpose:** Source discovery and content acquisition

**Key Commands:**
```bash
content_collection discover --query "react components"
content_collection fetch --sources-file sources.json
content_collection list-source-types
content_collection status
```

### 04-extractors: Content Extraction

**Purpose:** Content extraction from various sources (11 specialized extractors)

**Key Commands:**
```bash
extractors list-extractors
extractors run-extractor shadcn
extractors run-all-extractors
extractors status
```

## 🎯 CLI-First Benefits

### Key Advantages

- **Simplicity**: Direct module calls eliminate HTTP complexity
- **Testability**: 100% test coverage through simple CLI testing
- **Natural Composition**: Unix pipeline principles for data flow
- **Debugging**: Visible command execution and clear error messages
- **Maintainability**: Loose coupling through stable CLI interfaces

### Design Principles

- **JSON Standardization**: Consistent data exchange format
- **Direct Module Calls**: No network overhead between components
- **Unix Philosophy**: Simple, composable tools
- **Comprehensive Testing**: CLI interfaces enable thorough testing

## 🚀 Command Aliases

### CLI Shortcuts

This project includes a centralized command alias system for easier CLI usage. After setting up the aliases:

```bash
# Quick status check
simflo_status

# Component commands
rag_registry list
mcp_server search "button" --limit 5
extractors list-extractors
content_collection discover --query "react"
rag_builder status

# Help
simflo_help
```

### Setup

One-time setup:
```bash
source commands.sh
```

For persistence (recommended):
```bash
echo 'source $(pwd)/commands.sh' >> ~/.bashrc
source ~/.bashrc
```

### Alias Reference

| Alias | Command | Purpose |
|-------|---------|---------|
| `rag_registry` | Registry management | List, search, manage RAG databases |
| `mcp_server` | AI assistant integration | Search components, get details |
| `rag_builder` | Pipeline orchestration | Build and manage RAG pipelines |
| `content_collection` | Content discovery | Find and acquire content sources |
| `extractors` | Content extraction | Run extraction processes |
| `test_executor` | Test execution | Run test suites |
| `simflo_status` | Quick status | Check all components at once |
| `simflo_help` | Command help | Show available commands |

## 🛠️ Development Guidelines

### Adding New Components

1. **Create CLI Interface**
   ```python
   # Component CLI wrapper pattern
   def format_output(data, format_type="json", success=True):
       response = {
           "success": success,
           "timestamp": datetime.now().isoformat(),
           "data": data
       }
       return json.dumps(response, indent=2)
   ```

2. **Implement Standard Commands**
   - `status` - Component health check
   - `list` - List available resources
   - `help` - Command documentation

3. **Add JSON-based Tests**
   ```json
   {
     "test_name": "status_command",
     "command": "python3 component/cli.py status",
     "expected_exit_code": 0,
     "expected_stdout_pattern": ".*success.*true.*"
   }
   ```

4. **Update Documentation**
   - Component CLAUDE.md
   - Integration guide
   - CLI reference

### Integration Patterns

```python
# Standard component communication
import subprocess
import json

def call_component(component_path, command, **kwargs):
    cmd = ['python3', component_path, command]
    for key, value in kwargs.items():
        cmd.extend([f'--{key}', str(value)])
    cmd.extend(['--format', 'json'])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)
```

## 🤝 Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create feature branch** with descriptive name
3. **Implement changes** following CLI-first patterns
4. **Add comprehensive tests** with JSON-based framework
5. **Update documentation** (CLAUDE.md, integration guides)
6. **Run full test suite** ensuring 100% pass rate
7. **Submit pull request** with detailed description

### Code Standards

- **Python 3.8+** compatibility
- **Type hints** for all functions
- **Docstrings** following Google style
- **CLI interfaces** with `--format json|table`
- **JSON output** with standard format
- **Error handling** with meaningful messages

## 📄 License

This project demonstrates CLI-first architecture patterns for RAG systems. See LICENSE file for details.

## 🙏 Acknowledgments

Built to explore CLI-first architectural patterns for RAG (Retrieval-Augmented Generation) systems, focusing on simplicity and maintainability.

---

**simflo-rag v2** demonstrates how CLI-first architecture can provide effective alternatives for RAG system implementation.