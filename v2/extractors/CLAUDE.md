# Extractors Ecosystem

## Purpose
Contains the complete ecosystem for content extraction and analysis from various sources and formats.

## Role in System
The **content discovery and analysis engine** of simflo-rag, providing specialized extraction capabilities for different content types and sources.

## What This Directory Contains
- **code-extractors/**: Specialized extractors for code analysis and component extraction
- **language-extractors/**: Language-specific code analysis tools
- **claude-code-extractor/**: AI-powered code analysis and summarization
- **web-extractors/**: Web content extraction and analysis
- **document-extractors/**: Document processing and text extraction
- **media-extractors/**: Audio, video, and image content extraction

## What This Directory Should NOT Contain
- **RAG processing logic** - belongs in core/rag-engine/
- **Content collection** - belongs in content-collection/
- **Storage operations** - belongs in data-management/
- **User interfaces** - belongs in presentation-layer/
- **Testing infrastructure** - belongs in testing/

## CLI Interface
```bash
# Code extraction operations
extractors/code-extractors/extract.py --source /path/to/code --output /path/to/output --format json
extractors/code-extractors/analyze.py --file /path/to/file --type components
extractors/code-extractors/summarize.py --input /path/to/input --output /path/to/output

# Language-specific extraction
extractors/language-extractors/extract.py --language typescript --source /path/to/src
extractors/language-extractors/analyze.py --language python --project /path/to/project

# Claude Code extraction
extractors/claude-code-extractor/analyze.py --source /path/to/code --depth deep
extractors/claude-code-extractor/summarize.py --input /path/to/input --output /path/to/output

# Web extraction
extractors/web-extractors/crawl.py --url https://example.com --depth 3
extractors/web-extractors/extract.py --source /path/to/html --output /path/to/output

# Document extraction
extractors/document-extractors/parse.py --file /path/to/document.pdf --output /path/to/output
extractors/document-extractors/extract.py --source /path/to/docs --format markdown

# Media extraction
extractors/media-extractors/transcribe.py --file /path/to/audio.mp3 --output /path/to/output
extractors/media-extractors/analyze.py --file /path/to/image.jpg --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, core/rag-engine/ for processing
- **Provides**: Structured content and metadata to core/rag-engine/
- **Integrates with**: content-collection/ for source discovery
- **Serves**: All components requiring content analysis

## Implementation Guidelines
1. **Specialized extractors** - each extractor type has specific domain knowledge
2. **Consistent output format** - standardized JSON/CSV/Markdown outputs
3. **Error handling** - graceful handling of malformed or inaccessible content
4. **Performance optimization** - efficient processing of large content sets
5. **Extensibility** - easy to add new extractor types