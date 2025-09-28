"""
Documentation Extractor

Extracts structured content from technical documentation websites.
Supports web scraping, content cleaning, and code example extraction.
"""

import logging
import asyncio
import re
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup, Tag
import time

from extractors.base_extractor import BaseExtractor, ExtractionResult, ExtractedComponent

logger = logging.getLogger(__name__)

@dataclass
class DocumentationPage:
    """Represents a single documentation page"""
    url: str
    title: str
    content: str
    code_examples: List[str]
    description: str
    metadata: Dict[str, Any]
    page_type: str  # 'guide', 'api', 'reference', 'tutorial'
    last_updated: datetime

@dataclass
class DocumentationSite:
    """Represents a documentation site configuration"""
    name: str
    base_url: str
    start_urls: List[str]
    allowed_domains: List[str]
    selectors: Dict[str, str]
    rate_limit: float = 1.0  # requests per second
    max_pages: int = 100
    respect_robots_txt: bool = True

class DocumentationExtractor(BaseExtractor):
    """Extractor for technical documentation websites"""

    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)

        # Initialize documentation site configuration
        self.site = self._create_documentation_site()
        self.visited_urls: Set[str] = set()
        self.pending_urls: List[str] = self.site.start_urls.copy()
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None

        # Content extraction patterns
        self.code_patterns = [
            r'<code[^>]*>(.*?)</code>',
            r'<pre[^>]*>(.*?)</pre>',
            r'```(.*?)```',
            r'`(.*?)`'
        ]

        self.metadata_patterns = {
            'title': [r'<title>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>'],
            'description': [r'<meta[^>]*name="description"[^>]*content="([^"]*)"', r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"'],
        }

    def _create_documentation_site(self) -> DocumentationSite:
        """Create documentation site configuration from source config"""
        return DocumentationSite(
            name=self.source_config.get("name", "unknown"),
            base_url=self.source_config.get("base_url", ""),
            start_urls=self.source_config.get("start_urls", []),
            allowed_domains=self.source_config.get("allowed_domains", []),
            selectors=self.source_config.get("selectors", {}),
            rate_limit=self.source_config.get("rate_limit", 1.0),
            max_pages=self.source_config.get("max_pages", 100),
            respect_robots_txt=self.source_config.get("respect_robots_txt", True)
        )

    def validate_source(self) -> bool:
        """Validate that the source configuration is valid for documentation extraction"""
        required_fields = ["name", "base_url", "start_urls", "allowed_domains", "selectors"]

        for field in required_fields:
            if not self.source_config.get(field):
                self.logger.error(f"Documentation source missing required field: {field}")
                return False

        # Validate URL format
        try:
            urlparse(self.site.base_url)
        except Exception as e:
            self.logger.error(f"Invalid base URL: {self.site.base_url}")
            return False

        # Validate selectors
        required_selectors = ["content", "title", "navigation"]
        for selector in required_selectors:
            if selector not in self.site.selectors:
                self.logger.error(f"Missing required selector: {selector}")
                return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get list of content types this extractor supports"""
        return ["documentation", "guides", "api_reference", "tutorials"]

    async def extract(self) -> ExtractionResult:
        """Extract documentation from the website"""
        pages = []
        errors = []

        try:
            # Crawl and extract pages
            while self.pending_urls and len(self.visited_urls) < self.site.max_pages:
                url = self.pending_urls.pop(0)

                if url in self.visited_urls:
                    continue

                # Respect rate limiting
                await self._respect_rate_limit()

                page = await self._extract_page(url)
                if page:
                    pages.append(page)

                    # Extract links for further crawling
                    new_links = await self._extract_links(page)
                    self.pending_urls.extend(new_links)

                self.visited_urls.add(url)

            # Convert pages to ExtractedComponent format
            components = []
            for page in pages:
                component = self._page_to_component(page)
                if component:
                    components.append(component)

            return self.create_extraction_result(
                success=True,
                data=components,
                metadata={
                    "pages_extracted": len(pages),
                    "total_urls_visited": len(self.visited_urls),
                    "site_name": self.site.name,
                    "base_url": self.site.base_url
                }
            )

        except Exception as e:
            self.logger.error(f"Documentation extraction failed: {e}")
            return self.create_extraction_result(
                success=False,
                errors=[f"Extraction error: {str(e)}"]
            )

    async def _respect_rate_limit(self):
        """Respect rate limiting between requests"""
        if self.site.rate_limit > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < 1.0 / self.site.rate_limit:
                await asyncio.sleep(1.0 / self.site.rate_limit - elapsed)
        self.last_request_time = time.time()

    async def _extract_page(self, url: str) -> Optional[DocumentationPage]:
        """Extract content from a single page"""
        try:
            html_content = await self.fetch_content(url)
            if not html_content:
                return None

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = self._extract_title(soup, url)

            # Extract main content
            content = self._extract_content(soup)

            # Extract code examples
            code_examples = self._extract_code_examples(soup)

            # Extract description
            description = self._extract_description(soup)

            # Determine page type
            page_type = self._determine_page_type(url, title, content)

            # Extract metadata
            metadata = self._extract_metadata(soup, url)

            return DocumentationPage(
                url=url,
                title=title,
                content=content,
                code_examples=code_examples,
                description=description,
                metadata=metadata,
                page_type=page_type,
                last_updated=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Failed to extract page {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title"""
        # Try custom selector first
        if 'title' in self.site.selectors:
            title_elem = soup.select_one(self.site.selectors['title'])
            if title_elem:
                return title_elem.get_text().strip()

        # fallback to h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # fallback to title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        # fallback to URL
        return url.split('/')[-1]

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        if 'content' in self.site.selectors:
            content_elem = soup.select_one(self.site.selectors['content'])
            if content_elem:
                # Remove navigation and other non-content elements
                for non_content in content_elem.find_all(['nav', 'aside', 'script', 'style']):
                    non_content.decompose()

                return content_elem.get_text().strip()

        return ""

    def _extract_code_examples(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from the page"""
        examples = []

        # Find code blocks
        code_blocks = soup.find_all(['code', 'pre'])
        for block in code_blocks:
            code = block.get_text().strip()
            if code and len(code) > 10:  # Minimum length threshold
                examples.append(code)

        return examples

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()

        # Try to extract from content
        if 'content' in self.site.selectors:
            content_elem = soup.select_one(self.site.selectors['content'])
            if content_elem:
                # Get first paragraph
                first_p = content_elem.find('p')
                if first_p:
                    text = first_p.get_text().strip()
                    return text[:200] + "..." if len(text) > 200 else text

        return ""

    def _determine_page_type(self, url: str, title: str, content: str) -> str:
        """Determine the type of documentation page"""
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content.lower()

        # Check for API reference
        if any(keyword in url_lower for keyword in ['api', 'reference', 'docs']):
            return 'api'

        # Check for tutorials
        if any(keyword in url_lower for keyword in ['tutorial', 'guide', 'getting-started', 'learn']):
            return 'tutorial'

        # Check for guides
        if any(keyword in title_lower for keyword in ['guide', 'how to', 'tutorial']):
            return 'guide'

        # Default to reference
        return 'reference'

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc,
            'extracted_at': datetime.now().isoformat()
        }

        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content

        # Extract headings structure
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': level,
                    'text': heading.get_text().strip()
                })
        metadata['headings'] = headings

        return metadata

    async def _extract_links(self, page: DocumentationPage) -> List[str]:
        """Extract links from a page for further crawling"""
        links = []

        try:
            soup = BeautifulSoup(page.content, 'html.parser')

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Skip empty, javascript, and anchor links
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue

                # Convert to absolute URL
                absolute_url = urljoin(page.url, href)

                # Check if within allowed domains
                if self._is_allowed_url(absolute_url):
                    links.append(absolute_url)

        except Exception as e:
            self.logger.error(f"Failed to extract links from {page.url}: {e}")

        return links

    def _is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed for crawling"""
        parsed = urlparse(url)

        # Check domain
        if not any(domain in parsed.netloc for domain in self.site.allowed_domains):
            return False

        # Check if already visited
        if url in self.visited_urls or url in self.pending_urls:
            return False

        # Check file extensions (skip non-content files)
        skip_extensions = ['.pdf', '.zip', '.jpg', '.png', '.gif', '.css', '.js']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        return True

    def _page_to_component(self, page: DocumentationPage) -> Optional[Dict[str, Any]]:
        """Convert a documentation page to ExtractedComponent format"""
        try:
            # Create a component name from URL
            component_name = self._url_to_component_name(page.url)

            # Determine component type based on page type
            component_type = {
                'api': 'api_reference',
                'tutorial': 'tutorial',
                'guide': 'guide',
                'reference': 'documentation'
            }.get(page.page_type, 'documentation')

            return {
                "name": component_name,
                "category": "documentation",
                "type": component_type,
                "description": page.description,
                "installation": f"# View documentation at: {page.url}",
                "usage_examples": page.code_examples,
                "dependencies": [],
                "peer_dependencies": [],
                "metadata": {
                    **page.metadata,
                    "page_type": page.page_type,
                    "title": page.title,
                    "content_length": len(page.content),
                    "code_examples_count": len(page.code_examples),
                    "source_site": self.site.name
                },
                "platform": ["web"],
                "registry": "documentation",
                "sources": [self.site.name],
                "priority_source": self.site.name
            }

        except Exception as e:
            self.logger.error(f"Failed to convert page to component: {e}")
            return None

    def _url_to_component_name(self, url: str) -> str:
        """Convert URL to component name"""
        # Remove base URL
        if url.startswith(self.site.base_url):
            path = url[len(self.site.base_url):]
        else:
            path = urlparse(url).path

        # Clean up path
        path = path.strip('/')

        # Replace slashes and dashes with underscores
        name = path.replace('/', '_').replace('-', '_')

        # Remove file extensions
        if '.' in name:
            name = name.split('.')[0]

        # Ensure valid name
        if not name or len(name) == 0:
            name = "documentation_page"

        return name

    def calculate_quality_score(self, component: Dict[str, Any]) -> float:
        """Calculate quality score for documentation component"""
        score = 0.0
        max_score = 1.0

        # Content quality (0.4)
        metadata = component.get("metadata", {})
        content_length = metadata.get("content_length", 0)
        if content_length > 1000:
            score += 0.4
        elif content_length > 500:
            score += 0.3
        elif content_length > 200:
            score += 0.2
        else:
            score += 0.1

        # Code examples (0.3)
        code_count = metadata.get("code_examples_count", 0)
        if code_count > 3:
            score += 0.3
        elif code_count > 1:
            score += 0.2
        elif code_count > 0:
            score += 0.1

        # Description quality (0.2)
        description = component.get("description", "")
        if len(description) > 100:
            score += 0.2
        elif len(description) > 50:
            score += 0.15
        elif len(description) > 20:
            score += 0.1

        # Metadata completeness (0.1)
        if metadata.get("title") and metadata.get("page_type"):
            score += 0.1

        return min(score, max_score)

    def validate_component(self, component: Dict[str, Any]) -> List[str]:
        """Validate a documentation component"""
        errors = []

        # Required fields
        required_fields = ["name", "category", "type", "description"]
        for field in required_fields:
            if not component.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate content
        metadata = component.get("metadata", {})
        content_length = metadata.get("content_length", 0)
        if content_length < 50:
            errors.append("Content too short (< 50 characters)")

        # Validate URL
        url = metadata.get("url")
        if not url or not url.startswith("http"):
            errors.append("Invalid or missing URL")

        return errors