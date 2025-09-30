# Web Extractors

## Purpose
Web content extraction and analysis tools for processing online documentation, APIs, and web-based resources.

## Role in System
The **web intelligence engine** that discovers, extracts, and analyzes web-based content and documentation sources.

## What This Directory Contains
- **crawlers/**: Web crawling and spidering tools for systematic content discovery
- **scrapers/**: Targeted content scraping from specific websites and platforms
- **api-extractors/**: API documentation extraction and analysis
- **documentation-extractors/**: Web documentation processing and structuring
- **rss-feed-extractors/**: RSS and feed processing for dynamic content
- **search-engine-extractors/**: Search result extraction and analysis

## What This Directory Should NOT Contain
- **Local file processing** - belongs in document-extractors/
- **Code analysis** - belongs in code-extractors/
- **AI-powered analysis** - belongs in claude-code-extractor/
- **Database operations** - belongs in data-management/

## CLI Interface
```bash
# Web crawling
web-extractors/crawlers/crawl.py --url https://example.com --depth 3 --output /path/to/output
web-extractors/crawlers/spider.py --start-url https://example.com --max-pages 100 --output /path/to/output
web-extractors/crawlers/sitemap.py --url https://example.com/sitemap.xml --output /path/to/output

# Content scraping
web-extractors/scrapers/scrape.py --url https://example.com --selector ".content" --output /path/to/output
web-extractors/scrapers/extract-tables.py --url https://example.com --output /path/to/output
web-extractors/scrapers/extract-forms.py --url https://example.com --output /path/to/output

# API extraction
web-extractors/api-extractors/extract-swagger.py --url https://api.example.com/swagger.json --output /path/to/output
web-extractors/api-extractors/extract-openapi.py --url https://api.example.com/openapi.yaml --output /path/to/output
web-extractors/api-extractors/extract-rest-docs.py --url https://docs.example.com/api --output /path/to/output

# Documentation extraction
web-extractors/documentation-extractors/extract-md.py --url https://docs.example.com --output /path/to/output
web-extractors/documentation-extractors/extract-wiki.py --url https://wiki.example.com --output /path/to/output
web-extractors/documentation-extractors/extract-readme.py --url https://github.com/user/repo --output /path/to/output

# RSS feed processing
web-extractors/rss-feed-extractors/extract.py --url https://example.com/feed.xml --output /path/to/output
web-extractors/rss-feed-extractors/aggregate.py --feeds /path/to/feeds.txt --output /path/to/output

# Search engine extraction
web-extractors/search-engine-extractors/extract-results.py --query "search terms" --engine google --output /path/to/output
web-extractors/search-engine-extractors/extract-urls.py --query "search terms" --max-results 50 --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, content-collection/ for source discovery
- **Provides**: Structured web content to core/rag-engine/ and document-extractors/
- **Integrates with**: monitoring/ for crawl health and performance
- **Serves**: Web-based content discovery and processing systems

## Implementation Guidelines
1. **Respectful crawling** - follow robots.txt, rate limiting, and ethical crawling practices
2. **Robust parsing** - handle malformed HTML, dynamic content, and various markup formats
3. **Content quality** - focus on high-quality, relevant content extraction
4. **Metadata extraction** - extract meaningful metadata from web sources
5. **Error handling** - handle network issues, rate limits, and content changes gracefully