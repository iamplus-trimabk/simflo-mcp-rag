#!/usr/bin/env python3
"""
Simple Automated Research Crawler for AI Employability Research
Following evolutionary philosophy: good enough > perfect
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class AutomatedResearchCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
        })
        self.data = []
        self.visited_urls = set()

    def generate_search_queries(self, topics):
        """Generate search queries from research topics"""
        base_queries = [
            "AI employability trends 2024",
            "AI job market research",
            "AI workforce statistics",
            "future of work with AI",
            "AI career development",
            "AI skills demand",
            "AI employment impact",
            "AI job opportunities",
            "AI career success patterns",
            "AI professional growth"
        ]

        # Add topic-specific variations
        for topic in topics:
            base_queries.extend([
                f"{topic} research",
                f"{topic} statistics",
                f"{topic} trends 2024",
                f"{topic} case studies",
                f"{topic} analysis"
            ])

        return list(set(base_queries))

    def get_search_results(self, query, num_results=10):
        """Get search results using DuckDuckGo HTML scraping"""
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract result links from DuckDuckGo results
            links = []
            results = soup.find_all('a', class_='result__a')

            for result in results[:num_results]:
                href = result.get('href')
                if href and href.startswith('http') and len(links) < num_results:
                    # Clean DuckDuckGo redirect URLs
                    if 'uddg=' in href:
                        # Extract actual URL from DuckDuckGo redirect
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        if 'uddg' in parsed:
                            href = parsed['uddg'][0]

                    links.append(href)

            return links[:num_results]

        except Exception as e:
            print(f"Error getting search results for '{query}': {e}")
            return []

    def crawl_page(self, url):
        """Crawl a single page and extract content"""
        if url in self.visited_urls:
            return None

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic content
            title = soup.find('title')
            title = title.text.strip() if title else 'No title'

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            content = soup.get_text(separator=' ', strip=True)

            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()

            result = {
                'url': url,
                'title': title,
                'content': content[:3000],  # Limit content length
                'content_length': len(content),
                'crawled_at': datetime.now().isoformat(),
                'source_type': self.classify_source(url),
                'relevance_score': 0  # Will be calculated later
            }

            self.visited_urls.add(url)
            return result

        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None

    def classify_source(self, url):
        """Classify source type based on URL"""
        domain = urlparse(url).netloc.lower()

        if any(academic in domain for academic in ['arxiv', 'scholar', 'edu', 'ac']):
            return 'academic'
        elif any(news in domain for news in ['bbc', 'cnn', 'reuters', 'bloomberg', 'techcrunch']):
            return 'news'
        elif any(gov in domain for gov in ['gov', 'org']):
            return 'official'
        elif any(blog in domain for blog in ['medium', 'substack', 'blog']):
            return 'blog'
        else:
            return 'general'

    def is_relevant_content(self, result, topics):
        """Basic relevance checking for AI employability content"""
        content_lower = result['content'].lower()
        title_lower = result['title'].lower()

        # Check for AI/ML related keywords
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'automation', 'robot', 'llm', 'gpt']
        employment_keywords = ['job', 'career', 'employment', 'work', 'workforce', 'profession', 'skill', 'hiring']

        has_ai_content = any(keyword in content_lower for keyword in ai_keywords)
        has_employment_content = any(keyword in content_lower for keyword in employment_keywords)

        # Check topic relevance
        topic_relevance = any(topic.lower() in content_lower for topic in topics)

        # Calculate basic relevance score
        score = 0
        if has_ai_content:
            score += 3
        if has_employment_content:
            score += 3
        if topic_relevance:
            score += 2

        result['relevance_score'] = score
        return score >= 3  # Minimum relevance threshold

    def automated_research(self, topics, max_urls_per_query=5, max_queries=10):
        """Automated research: generate queries, search, and crawl"""
        queries = self.generate_search_queries(topics)

        # Limit queries to avoid rate limiting
        queries = queries[:max_queries]

        print(f"Generated {len(queries)} search queries (limited to avoid rate limiting)")
        print(f"Topics: {topics}")

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Searching: {query}")

            # Longer delay between searches to avoid rate limiting
            if i > 1:
                delay = random.uniform(3, 7)
                print(f"Rate limiting delay: waiting {delay:.1f}s...")
                time.sleep(delay)

            search_results = self.get_search_results(query, max_urls_per_query)
            print(f"Found {len(search_results)} URLs")

            for j, url in enumerate(search_results, 1):
                print(f"  [{j}/{len(search_results)}] Crawling: {url}")

                result = self.crawl_page(url)
                if result and self.is_relevant_content(result, topics):
                    self.data.append(result)
                    print(f"    ✓ Relevant: {result['title']} (Score: {result['relevance_score']})")
                else:
                    print(f"    ✗ Skipped: {'Not relevant' if result else 'Failed to crawl'}")

                # Random delay to avoid overwhelming servers
                if j < len(search_results):
                    delay = random.uniform(2, 5)
                    print(f"    Waiting {delay:.1f}s...")
                    time.sleep(delay)

        return pd.DataFrame(self.data)

    def save_results(self, filename='research_data.csv'):
        """Save results to CSV and JSON"""
        if not self.data:
            print("No data to save")
            return pd.DataFrame()

        df = pd.DataFrame(self.data)

        # Save to CSV
        csv_filename = filename.replace('.csv', '.csv')
        df.to_csv(csv_filename, index=False)
        print(f"Saved {len(df)} results to {csv_filename}")

        # Save to JSON for more detailed analysis
        json_filename = filename.replace('.csv', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Saved detailed results to {json_filename}")

        # Print summary statistics
        print(f"\nResearch Summary:")
        print(f"Total URLs processed: {len(self.visited_urls)}")
        print(f"Relevant results: {len(self.data)}")
        print(f"Source types: {df['source_type'].value_counts().to_dict()}")
        print(f"Average relevance score: {df['relevance_score'].mean():.2f}")

        return df

def main():
    """Main execution function"""
    print("=== AI Employability Research Crawler ===")
    print("Following evolutionary philosophy: Start simple, improve iteratively")

    # Initialize crawler
    crawler = AutomatedResearchCrawler()

    # Define research topics based on our ongoing discussion
    research_topics = [
        "AI employment framework",
        "Human development parallels",
        "Success pattern framework",
        "Goal cascading system",
        "Role specialization guide"
    ]

    # Execute automated research
    print(f"\nStarting automated research on topics: {research_topics}")
    results_df = crawler.automated_research(research_topics, max_urls_per_query=3, max_queries=5)

    # Save results
    if not results_df.empty:
        output_file = f"ai_employability_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        crawler.save_results(output_file)

        # Show top results by relevance
        print(f"\nTop 10 most relevant results:")
        top_results = results_df.nlargest(10, 'relevance_score')
        for idx, row in top_results.iterrows():
            print(f"  {row['relevance_score']}/8 - {row['title']}")
            print(f"    {row['url']}")
            print(f"    Type: {row['source_type']}")
            print()
    else:
        print("No relevant results found. Consider:")
        print("1. Adjusting search queries")
        print("2. Expanding topic scope")
        print("3. Checking network connectivity")

if __name__ == "__main__":
    main()