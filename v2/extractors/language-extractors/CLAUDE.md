# Language Extractors

## Purpose
Language-specific code analysis tools that understand the nuances and patterns of different programming languages.

## Role in System
The **multilingual code analysis engine** that provides deep understanding of language-specific constructs, patterns, and best practices.

## What This Directory Contains
- **typescript-extractor/**: TypeScript code analysis, type system understanding, and pattern extraction
- **python-extractor/**: Python code analysis, package structure, and dependency analysis
- **javascript-extractor/**: JavaScript analysis, framework patterns, and modern syntax
- **java-extractor/**: Java code analysis, object-oriented patterns, and enterprise patterns
- **go-extractor/**: Go language analysis, concurrency patterns, and package structure
- **rust-extractor/**: Rust code analysis, ownership patterns, and memory safety
- **cpp-extractor/**: C++ analysis, object-oriented patterns, and memory management

## What This Directory Should NOT Contain
- **Framework-specific analysis** - belongs in code-extractors/framework-extractors/
- **UI component extraction** - belongs in code-extractors/react-extractors/
- **AI-powered analysis** - belongs in claude-code-extractor/
- **General code structure** - belongs in code-extractors/general-code-extractors/

## CLI Interface
```bash
# TypeScript analysis
language-extractors/typescript-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/typescript-extractor/extract-types.py --source /path/to/src --output /path/to/output
language-extractors/typescript-extractor/find-patterns.py --file /path/to/file --output /path/to/output

# Python analysis
language-extractors/python-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/python-extractor/extract-modules.py --source /path/to/src --output /path/to/output
language-extractors/python-extractor/find-dependencies.py --file /path/to/file --output /path/to/output

# JavaScript analysis
language-extractors/javascript-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/javascript-extractor/extract-frameworks.py --source /path/to/src --output /path/to/output

# Java analysis
language-extractors/java-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/java-extractor/extract-classes.py --source /path/to/src --output /path/to/output

# Go analysis
language-extractors/go-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/go-extractor/extract-packages.py --source /path/to/src --output /path/to/output

# Rust analysis
language-extractors/rust-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/rust-extractor/extract-traits.py --source /path/to/src --output /path/to/output

# C++ analysis
language-extractors/cpp-extractor/analyze.py --project /path/to/project --output /path/to/output
language-extractors/cpp-extractor/extract-classes.py --source /path/to/src --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, code-extractors/ for general code patterns
- **Provides**: Language-specific insights to claude-code-extractor/ and core/rag-engine/
- **Integrates with**: document-extractors/ for documentation generation
- **Serves**: Multilingual code analysis and understanding systems

## Implementation Guidelines
1. **Language expertise** - deep understanding of each language's idioms and patterns
2. **Parser integration** - use official or well-maintained language parsers
3. **Type system understanding** - for statically typed languages, understand type relationships
4. **Package/module analysis** - understand how code is organized and structured
5. **Best practice detection** - identify language-specific best practices and anti-patterns