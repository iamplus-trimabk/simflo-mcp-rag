# SimFlo MCP RAG - Data Pipeline

Universal component extraction and processing pipeline for the SimFlo MCP RAG system.

## Overview

This data pipeline provides a structured approach to extracting component information from various sources, with special focus on GitHub repositories. The pipeline supports multiple extraction methods, post-processing, and quality control.

## Directory Structure

```
data-pipeline/
├── github-extractor/          # GitHub-based extraction methods
│   ├── github_extractor.py     # Basic GitHub extractor (git-based)
│   ├── github_cli_extractor.py # Enhanced GitHub CLI extractor
│   └── extract_gluestack.py    # Gluestack-specific extraction script
├── config/
│   └── pipeline_config.json    # Pipeline configuration
├── tests/
│   └── test_github_extractor.py # Test suite
├── orchestrator.py             # Main pipeline orchestrator
└── README.md                   # This file
```

## Prerequisites

### Required Tools
- **Python 3.8+** - Core runtime
- **Git** - Version control operations
- **GitHub CLI (gh)** - Enhanced GitHub operations (recommended)

### Optional but Recommended
- **GitHub CLI Authentication** - For higher rate limits and private repositories
- **jq** - JSON processing for command-line operations

### Installing GitHub CLI
```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate with GitHub
gh auth login
```

## Quick Start

### 1. Check Prerequisites
```bash
cd data-pipeline
python3 orchestrator.py check
```

### 2. List Available Profiles
```bash
python3 orchestrator.py list-profiles
```

### 3. Run Extraction
```bash
# Extract Gluestack components
python3 orchestrator.py run gluestack --verbose

# Extract multiple libraries
python3 orchestrator.py run-multiple gluestack shadcn --verbose
```

### 4. Check Pipeline Status
```bash
python3 orchestrator.py status
```

## Available Commands

### Orchestrator Commands

| Command | Description | Example |
|---------|-------------|---------|
| `check` | Verify all prerequisites | `python3 orchestrator.py check` |
| `list-profiles` | Show available extraction profiles | `python3 orchestrator.py list-profiles` |
| `validate` | Validate a specific profile | `python3 orchestrator.py validate gluestack` |
| `run` | Run extraction for a profile | `python3 orchestrator.py run gluestack --verbose` |
| `run-multiple` | Run multiple extractions | `python3 orchestrator.py run-multiple gluestack shadcn` |
| `discover` | Discover new repositories | `python3 orchestrator.py discover react components --limit 5` |
| `status` | Generate pipeline status report | `python3 orchestrator.py status` |

### Direct Extractor Usage

#### GitHub CLI Extractor (Enhanced)
```bash
# Extract with full metadata
python3 github-extractor/github_cli_extractor.py gluestack/gluestack-ui --output gluestack_components.json

# Extract metadata only
python3 github-extractor/github_cli_extractor.py radix-ui/primitives --metadata-only

# Use HTTPS URL
python3 github-extractor/github_cli_extractor.py https://github.com/radix-ui/primitives --verbose
```

#### Basic GitHub Extractor
```bash
# Basic extraction (git-based)
python3 github-extractor/github_extractor.py https://github.com/shadcn-ui/ui --output shadcn_components.json
```

## Configuration

### Pipeline Configuration (`config/pipeline_config.json`)

The pipeline is configured through a comprehensive JSON file that defines:

- **Extractors**: Available extraction methods and their capabilities
- **Profiles**: Pre-configured extraction targets
- **Post-processors**: Component enhancement logic
- **Quality Metrics**: Scoring systems for repository and component quality
- **Orchestration**: Concurrency, timeouts, and retry logic

### Adding New Extraction Profiles

1. **Define the Profile** in `config/pipeline_config.json`:
```json
{
  "extractor_profiles": {
    "my_library": {
      "name": "My Component Library",
      "extractor": "github_cli",
      "repository": "myorg/my-library",
      "output_path": "../rag_databases/my_library_db/components.json",
      "post_processor": "generic_post_processor",
      "platform_detection": "enhanced",
      "quality_threshold": 0.7
    }
  }
}
```

2. **Validate the Profile**:
```bash
python3 orchestrator.py validate my_library
```

3. **Run Extraction**:
```bash
python3 orchestrator.py run my_library
```

### Creating Custom Post-processors

Post-processors are defined in the configuration and can include:

- **Platform Detection**: Map imports to React/React Native platforms
- **Categorization**: Group components by type (UI, layout, forms, etc.)
- **Tag Enhancement**: Add library-specific tags
- **Metadata Enhancement**: Improve descriptions and examples

Example post-processor configuration:
```json
{
  "post_processors": {
    "my_library_post_processor": {
      "name": "My Library Post Processor",
      "platform_mapping": {
        "reactjs_indicators": ["react", "next", "typescript"],
        "reactnative_indicators": ["react-native", "expo"]
      },
      "categories": {
        "ui": ["button", "input", "modal"],
        "layout": ["container", "grid", "stack"]
      }
    }
  }
}
```

## Extraction Methods

### GitHub CLI Extractor (Recommended)

**Advantages:**
- Authenticated access (higher rate limits)
- Repository metadata extraction
- Similar repository discovery
- Quality analysis
- Enhanced error handling

**Requirements:**
- GitHub CLI installed
- Authentication recommended

**Capabilities:**
- Repository stars, contributors, activity analysis
- Topic-based similar repository discovery
- File structure analysis
- Documentation quality scoring

### Basic GitHub Extractor

**Advantages:**
- No additional dependencies beyond git
- Simple and reliable
- Fast for basic extraction

**Limitations:**
- No repository metadata
- No authenticated access
- Basic extraction only

## Output Format

Extracted components are saved in JSON format with enhanced metadata:

```json
{
  "repository": {
    "name": "gluestack-ui",
    "description": "Universal React component library",
    "stargazerCount": 4200,
    "language": "TypeScript",
    "topics": ["react", "react-native", "components"]
  },
  "extraction_metadata": {
    "extracted_at": "2024-01-01T12:00:00Z",
    "extractor_version": "github-cli-enhanced",
    "total_components": 13,
    "quality_metrics": {
      "documentation_score": 85,
      "file_count": 156,
      "typescript_file_count": 89
    }
  },
  "components": [
    {
      "name": "button",
      "description": "Universal button component",
      "platform": ["reactjs", "reactnative"],
      "files": [...],
      "dependencies": [...],
      "props_info": {...},
      "usage_patterns": [...],
      "tags": ["ui-component", "gluestack", "button"]
    }
  ]
}
```

## Quality Metrics

The pipeline evaluates both repository and component quality:

### Repository Quality
- **Documentation Score**: Based on README, package.json, tests, TypeScript usage
- **Activity Level**: Recent commits and contributions
- **Community Health**: Star count, contributor count

### Component Quality
- **Description Quality**: Presence and completeness of descriptions
- **Type Safety**: TypeScript interface definitions
- **Examples**: Usage examples and documentation
- **Props Documentation**: Complete prop type definitions

## Discovery Mode

Find new component libraries using GitHub's search:

```bash
# Discover React component libraries
python3 orchestrator.py discover react components --limit 10

# Find React Native libraries
python3 orchestrator.py discover react-native ui --limit 5

# Search by specific topics
python3 orchestrator.py discover design-system tailwind --limit 8
```

## Testing

Run the test suite:
```bash
python3 tests/test_github_extractor.py
```

## Troubleshooting

### Common Issues

**GitHub CLI Not Found**
```bash
# Install GitHub CLI
brew install gh  # macOS
# Or follow installation instructions for your OS

# Authenticate
gh auth login
```

**Authentication Issues**
```bash
# Check authentication status
gh auth status

# Re-authenticate
gh auth logout
gh auth login
```

**Rate Limiting**
```bash
# Check rate limits
gh api rate_limit

# Use authenticated access for higher limits
gh auth login
```

**Repository Access Issues**
```bash
# Test repository access
gh repo view owner/repo

# Check if repository exists and is accessible
gh api repos/owner/repo
```

### Debug Mode

Run extractions with verbose logging:
```bash
python3 orchestrator.py run gluestack --verbose
```

### Performance Issues

- **Timeout**: Increase timeout in configuration
- **Concurrent Extractions**: Reduce `max_concurrent_extractions` in configuration
- **Memory Issues**: Run extractions sequentially instead of in parallel

## Integration with RAG System

Extracted components are automatically integrated with the SimFlo MCP RAG system:

1. **Output Location**: Components are saved to `rag_databases/{library}_db/`
2. **Registry Configuration**: Update `rag_databases/registry_config.json` with new libraries
3. **Vector Store**: Components are automatically processed into vector databases
4. **MCP Integration**: Components become available through MCP tools

## Contributing

### Adding New Extractors

1. Create extractor script in `github-extractor/`
2. Add extractor configuration to `config/pipeline_config.json`
3. Create extraction profiles for new libraries
4. Add tests to `tests/`
5. Update documentation

### Code Standards

- Follow Python 3.8+ syntax
- Type hints for all functions
- Comprehensive error handling
- Logging for all operations
- Configuration-driven design

## License

This pipeline is part of the SimFlo MCP RAG project. See the main project license for details.