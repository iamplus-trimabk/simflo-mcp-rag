#!/usr/bin/env python3
"""
Enhanced Source Discovery for AI Employability Research
Scaling from 4 to 20+ relevant sources through automated discovery
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from urllib.parse import urljoin, urlparse, parse_qs
import json
from datetime import datetime
from research_pipeline import ResearchPipeline

class EnhancedSourceDiscovery(ResearchPipeline):
    def __init__(self):
        super().__init__()
        self.discovered_sources = []
        self.search_results_cache = {}

    # Expanded source categories with specific search queries
    SOURCE_CATEGORIES = {
        'academic': {
            'queries': [
                'artificial intelligence employment trends research',
                'AI job market academic papers',
                'machine learning workforce impact studies',
                'AI career development academic research',
                'artificial intelligence skills demand studies'
            ],
            'seed_urls': [
                'https://arxiv.org/list/cs.AI/recent',
                'https://scholar.google.com/scholar?q=AI+employment',
                'https://www.pnas.org/search?term=artificial+intelligence+employment',
                'https://www.nature.com/search?q=ai+employment'
            ]
        },
        'industry_reports': {
            'queries': [
                'AI job market report 2024',
                'artificial intelligence workforce trends',
                'AI skills gap industry report',
                'future of work AI report',
                'AI employment statistics industry'
            ],
            'seed_urls': [
                'https://www.weforum.org/reports',
                'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
                'https://www.pwc.com/gx/en/issues/data-and-analytics/ai-projects.html',
                'https://www.gartner.com/en/information-technology/insights'
            ]
        },
        'government_data': {
            'queries': [
                'Bureau of Labor Statistics AI occupations',
                'AI employment government data',
                'artificial intelligence workforce statistics',
                'AI job growth government report',
                'technology employment trends government'
            ],
            'seed_urls': [
                'https://www.bls.gov/ooh/computer-and-information-technology/home.htm',
                'https://www.dol.gov/agencies/eta/ai',
                'https://www.census.gov/topics/economy/science-technology.html',
                'https://www.bls.gov/emp/',
                'https://www.europa.eu/!YD44KQ'
            ]
        },
        'tech_news': {
            'queries': [
                'AI job market tech news',
                'artificial intelligence career development',
                'AI skills demand tech industry',
                'future of work AI technology',
                'AI employment trends technology'
            ],
            'seed_urls': [
                'https://www.wired.com/category/artificial-intelligence/',
                'https://www.techcrunch.com/category/artificial-intelligence/',
                'https://www.computerworld.com/category/artificial-intelligence/',
                'https://www.technologyreview.com/topic/artificial-intelligence/',
                'https://www.theverge.com/artificial-intelligence'
            ]
        },
        'expert_analysis': {
            'queries': [
                'AI employment expert analysis',
                'artificial intelligence career experts',
                'AI workforce development experts',
                'future of AI employment analysis',
                'AI skills expert opinion'
            ],
            'seed_urls': [
                'https://www.brookings.edu/search/?s=artificial+intelligence+employment',
                'https://www.rand.org/topics/artificial-intelligence.html',
                'https://hbr.org/topic/artificial-intelligence',
                'https://www.oreilly.com/radar/topics/artificial-intelligence/',
                'https://ai.stanford.edu/blog/'
            ]
        }
    }

    def discover_sources_via_search(self, category, max_results=5):
        """Discover sources using search-like queries on seed URLs"""
        print(f"Discovering {category} sources...")

        category_info = self.SOURCE_CATEGORIES[category]
        discovered = []

        # Try seed URLs first
        for seed_url in category_info['seed_urls'][:3]:  # Limit to avoid overwhelming
            try:
                sources_from_seed = self.extract_links_from_page(seed_url, category)
                discovered.extend(sources_from_seed)

                # Rate limiting
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Failed to extract from {seed_url}: {e}")

        # Remove duplicates and limit results
        unique_sources = []
        seen_urls = set()

        for source in discovered:
            if source['url'] not in seen_urls and len(unique_sources) < max_results:
                unique_sources.append(source)
                seen_urls.add(source['url'])

        print(f"Discovered {len(unique_sources)} {category} sources")
        return unique_sources

    def extract_links_from_page(self, url, category):
        """Extract relevant links from a page"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links
            all_links = soup.find_all('a', href=True)
            relevant_links = []

            for link in all_links:
                href = link.get('href')
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue

                # Make absolute URL
                if href.startswith('/'):
                    href = urljoin(url, href)

                # Check relevance
                if self.is_relevant_link(href, link.text, category):
                    relevant_links.append({
                        'url': href,
                        'title': link.text.strip(),
                        'category': category,
                        'discovery_method': 'page_extraction',
                        'source_url': url
                    })

            return relevant_links[:10]  # Limit per page

        except Exception as e:
            print(f"Error extracting links from {url}: {e}")
            return []

    def is_relevant_link(self, url, link_text, category):
        """Check if a link is relevant to AI employability"""
        relevance_keywords = {
            'academic': ['ai', 'artificial', 'intelligence', 'research', 'paper', 'study', 'academic'],
            'industry_reports': ['report', 'analysis', 'trends', 'market', 'industry', 'survey'],
            'government_data': ['government', 'data', 'statistics', 'bureau', 'labor', 'employment'],
            'tech_news': ['ai', 'artificial', 'intelligence', 'tech', 'news', 'technology'],
            'expert_analysis': ['expert', 'analysis', 'opinion', 'insight', 'thought', 'leadership']
        }

        url_lower = url.lower()
        text_lower = link_text.lower()

        # Check category-specific keywords
        keywords = relevance_keywords.get(category, [])
        keyword_score = sum(1 for keyword in keywords if keyword in url_lower or keyword in text_lower)

        # General AI employability relevance
        ai_keywords = ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'automation', 'llm']
        employment_keywords = ['job', 'career', 'employment', 'work', 'workforce', 'skill', 'occupation']

        ai_score = sum(1 for keyword in ai_keywords if keyword in url_lower)
        employment_score = sum(1 for keyword in employment_keywords if keyword in url_lower)

        # Minimum thresholds
        return (keyword_score >= 1) and (ai_score >= 1 or employment_score >= 1)

    def expand_known_sources(self):
        """Expand our initial reliable sources with similar content"""
        print("Expanding known reliable sources...")

        expanded_sources = []

        # Additional reliable sources based on our initial success
        additional_sources = [
            {
                'url': 'https://www.technologyreview.com/topic/artificial-intelligence/',
                'topic': 'AI employment framework',
                'type': 'tech_news',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.brookings.edu/search/?s=artificial+intelligence+employment',
                'topic': 'AI employment framework',
                'type': 'expert_analysis',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://hbr.org/topic/artificial-intelligence',
                'topic': 'AI career development',
                'type': 'expert_analysis',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.rand.org/topics/artificial-intelligence.html',
                'topic': 'AI workforce statistics',
                'type': 'expert_analysis',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.pwc.com/gx/en/issues/data-and-analytics/ai-projects.html',
                'topic': 'AI job market research',
                'type': 'industry_reports',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
                'topic': 'AI employment impact',
                'type': 'industry_reports',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://arxiv.org/list/cs.AI/recent',
                'topic': 'AI employment framework',
                'type': 'academic',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://ai.stanford.edu/blog/',
                'topic': 'AI career development',
                'type': 'academic',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.techcrunch.com/category/artificial-intelligence/',
                'topic': 'AI job market research',
                'type': 'tech_news',
                'discovery_method': 'known_reliable'
            },
            {
                'url': 'https://www.theverge.com/artificial-intelligence',
                'topic': 'AI career development',
                'type': 'tech_news',
                'discovery_method': 'known_reliable'
            }
        ]

        return additional_sources

    def run_enhanced_discovery(self):
        """Run enhanced source discovery to scale to 20+ sources"""
        print("=== Enhanced Source Discovery ===")
        print("Scaling from 4 to 20+ relevant sources\n")

        all_discovered_sources = []

        # Step 1: Expand known reliable sources
        print("Step 1: Expanding known reliable sources...")
        known_expanded = self.expand_known_sources()
        all_discovered_sources.extend(known_expanded)
        print(f"Added {len(known_expanded)} known reliable sources")

        # Step 2: Automated discovery by category
        print("\nStep 2: Automated discovery by category...")
        for category in self.SOURCE_CATEGORIES.keys():
            print(f"\nDiscovering {category} sources...")
            discovered = self.discover_sources_via_search(category, max_results=3)
            all_discovered_sources.extend(discovered)

            # Rate limiting between categories
            time.sleep(random.uniform(3, 5))

        # Remove duplicates
        unique_sources = []
        seen_urls = set()

        for source in all_discovered_sources:
            if source['url'] not in seen_urls:
                unique_sources.append(source)
                seen_urls.add(source['url'])

        print(f"\n=== Discovery Summary ===")
        print(f"Total unique sources discovered: {len(unique_sources)}")
        print(f"Source types: {pd.DataFrame(unique_sources)['category'].value_counts().to_dict()}")

        # Save discovered sources
        self.save_discovered_sources(unique_sources)

        return unique_sources

    def save_discovered_sources(self, sources):
        """Save discovered sources for crawling"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as JSON
        json_filename = f"discovered_sources_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=2, ensure_ascii=False)
        print(f"Saved discovered sources: {json_filename}")

        # Save as CSV for easy review
        df = pd.DataFrame(sources)
        csv_filename = f"discovered_sources_{timestamp}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved sources list: {csv_filename}")

    def crawl_discovered_sources(self, sources, max_sources=20):
        """Crawl the discovered sources"""
        print(f"\n=== Crawling Discovered Sources ===")
        print(f"Crawling top {max_sources} discovered sources...\n")

        crawled_results = []

        for i, source in enumerate(sources[:max_sources], 1):
            print(f"[{i}/{max_sources}] Crawling: {source['url']}")

            # Convert to format expected by parent class
            source_info = {
                'url': source['url'],
                'topic': source.get('topic', 'AI employability research'),
                'type': source.get('category', 'general')
            }

            result = self.crawl_url(source_info)
            if result:
                result['discovery_method'] = source.get('discovery_method', 'unknown')
                result['category'] = source.get('category', 'general')
                crawled_results.append(result)

            # Rate limiting
            if i < max_sources:
                delay = random.uniform(2, 4)
                print(f"Waiting {delay:.1f}s...")
                time.sleep(delay)

        return crawled_results

def main():
    """Main execution for enhanced source discovery"""
    print("Starting Enhanced Source Discovery for AI Employability Research")

    discovery = EnhancedSourceDiscovery()

    # Step 1: Discover sources
    discovered_sources = discovery.run_enhanced_discovery()

    # Step 2: Crawl top sources
    if discovered_sources:
        crawled_results = discovery.crawl_discovered_sources(discovered_sources, max_sources=20)

        if crawled_results:
            # Save results
            discovery.results = crawled_results
            discovery.save_results('enhanced_ai_employability_research')

            # Analyze results
            discovery.analyze_results()
        else:
            print("No sources successfully crawled")
    else:
        print("No sources discovered")

if __name__ == "__main__":
    main()