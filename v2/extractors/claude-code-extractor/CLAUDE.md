# Claude Code Extractor

## Purpose
AI-powered code analysis and summarization using Claude Code for intelligent code understanding and documentation generation.

## Role in System
The **intelligent code analysis engine** that leverages AI to provide deep insights, summarization, and understanding of codebases beyond traditional static analysis.

## What This Directory Contains
- **code-analysis/**: AI-powered code analysis and pattern recognition
- **summarization/**: Automatic code summarization and documentation generation
- **evolution-tracking/**: Code evolution analysis and change impact assessment
- **insights-generation/**: Deep code insights and best practice recommendations
- **documentation-generation/**: Automatic documentation creation from code analysis

## What This Directory Should NOT Contain
- **Traditional static analysis** - belongs in code-extractors/ or language-extractors/
- **Language-specific parsing** - belongs in language-extractors/
- **Framework extraction** - belongs in code-extractors/
- **Manual documentation** - belongs in documentation/

## CLI Interface
```bash
# AI-powered code analysis
claude-code-extractor/code-analysis/analyze.py --source /path/to/code --output /path/to/output --depth deep
claude-code-extractor/code-analysis/find-patterns.py --project /path/to/project --output /path/to/output
claude-code-extractor/code-analysis/assess-quality.py --file /path/to/file --output /path/to/output

# Code summarization
claude-code-extractor/summarization/summarize.py --input /path/to/code --output /path/to/output --format markdown
claude-code-extractor/summarization/generate-docs.py --project /path/to/project --output /path/to/output
claude-code-extractor/summarization/create-overview.py --source /path/to/src --output /path/to/output

# Evolution tracking
claude-code-extractor/evolution-tracking/analyze-changes.py --repo /path/to/repo --output /path/to/output
claude-code-extractor/evolution-tracking/assess-impact.py --file /path/to/file --output /path/to/output
claude-code-extractor/evolution-tracking/track-patterns.py --project /path/to/project --output /path/to/output

# Insights generation
claude-code-extractor/insights-generation/generate-insights.py --source /path/to/code --output /path/to/output
claude-code-extractor/insights-generation/recommend-best-practices.py --project /path/to/project --output /path/to/output
claude-code-extractor/insights-generation/identify-issues.py --file /path/to/file --output /path/to/output

# Documentation generation
claude-code-extractor/documentation-generation/create-api-docs.py --project /path/to/project --output /path/to/output
claude-code-extractor/documentation-generation/generate-guides.py --source /path/to/src --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, code-extractors/ and language-extractors/ for base analysis
- **Provides**: AI-powered insights to core/rag-engine/ and documentation/
- **Integrates with**: evolution-pool/ for research integration
- **Serves**: Intelligent code understanding and documentation systems

## Implementation Guidelines
1. **Claude Code integration** - leverage Claude Code capabilities for analysis
2. **Context-aware analysis** - understand project context and goals
3. **Quality-focused** - focus on code quality, maintainability, and best practices
4. **Evolution-aware** - understand how code evolves and changes over time
5. **Actionable insights** - provide practical, actionable recommendations and insights