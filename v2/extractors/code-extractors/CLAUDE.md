# Code Extractors

## Purpose
Specialized extractors for code analysis, component extraction, and codebase intelligence.

## Role in System
The **code intelligence engine** that analyzes codebases, extracts components, and provides structured understanding of code structure and patterns.

## What This Directory Contains
- **react-extractors/**: React-specific component extraction (JSX, hooks, contexts)
- **ui-library-extractors/**: Specialized extractors for UI libraries (Shadcn, Gluestack)
- **general-code-extractors/**: Generic code structure and pattern analysis
- **framework-extractors/**: Framework-specific extraction (Vue, Angular, Svelte)
- **testing-extractors/**: Test code analysis and extraction

## What This Directory Should NOT Contain
- **Language-specific analysis** - belongs in language-extractors/
- **AI-powered analysis** - belongs in claude-code-extractor/
- **Web content extraction** - belongs in web-extractors/
- **Document parsing** - belongs in document-extractors/

## CLI Interface
```bash
# React component extraction
code-extractors/react-extractors/extract.py --source /path/to/src --output /path/to/output --format json
code-extractors/react-extractors/analyze-hooks.py --file /path/to/file --output /path/to/output
code-extractors/react-extractors/find-contexts.py --project /path/to/project

# UI library extraction
code-extractors/ui-library-extractors/extract-shadcn.py --source /path/to/shadcn --output /path/to/output
code-extractors/ui-library-extractors/extract-gluestack.py --source /path/to/gluestack --output /path/to/output

# General code analysis
code-extractors/general-code-extractors/analyze-structure.py --project /path/to/project --output /path/to/output
code-extractors/general-code-extractors/find-patterns.py --source /path/to/code --output /path/to/output

# Framework extraction
code-extractors/framework-extractors/extract-vue.py --source /path/to/vue --output /path/to/output
code-extractors/framework-extractors/extract-angular.py --source /path/to/angular --output /path/to/output

# Test code analysis
code-extractors/testing-extractors/analyze-tests.py --project /path/to/project --output /path/to/output
code-extractors/testing-extractors/extract-test-patterns.py --source /path/to/tests --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, language-extractors/ for language-specific parsing
- **Provides**: Structured code analysis to claude-code-extractor/ and core/rag-engine/
- **Integrates with**: document-extractors/ for documentation generation
- **Serves**: Code intelligence and component discovery systems

## Implementation Guidelines
1. **Framework-specific knowledge** - deep understanding of target frameworks
2. **AST-based analysis** - use abstract syntax trees for accurate code parsing
3. **Component relationship mapping** - understand dependencies and hierarchies
4. **Pattern recognition** - identify common patterns and anti-patterns
5. **Metadata extraction** - extract meaningful metadata from code structure