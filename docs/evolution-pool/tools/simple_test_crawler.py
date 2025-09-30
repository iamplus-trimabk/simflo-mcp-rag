#!/usr/bin/env python3
"""
Simple test crawler - direct URL testing for proof of concept
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

class SimpleTestCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
        })
        self.data = []

    def crawl_page(self, url):
        """Crawl a single page and extract content"""
        try:
            print(f"Crawling: {url}")
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
            content = content[:2000]  # Limit for testing

            result = {
                'url': url,
                'title': title,
                'content': content,
                'length': len(content),
                'timestamp': datetime.now().isoformat()
            }

            print(f"✓ Success: {title[:80]}...")
            return result

        except Exception as e:
            print(f"✗ Failed: {e}")
            return None

def main():
    """Test with known reliable sources"""
    print("=== Simple Crawler Test ===")

    crawler = SimpleTestCrawler()

    # Test URLs known to have AI/employment content
    test_urls = [
        "https://www.bls.gov/ooh/computer-and-information-technology/home.htm",
        "https://www.weforum.org/reports/future-of-jobs-2023/",
        "https://www.pewresearch.org/topic/science-technology/ai/",
        "https://www.mckinsey.com/featured-insights/mckinsey-technology/whats-next-in-generative-ai",
        "https://www.wired.com/category/artificial-intelligence/"
    ]

    print(f"Testing {len(test_urls)} known sources...")

    for url in test_urls:
        result = crawler.crawl_page(url)
        if result:
            crawler.data.append(result)

        # Delay between requests
        time.sleep(2)

    # Save results
    if crawler.data:
        df = pd.DataFrame(crawler.data)
        filename = f"test_crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nSaved {len(crawler.data)} results to {filename}")

        print("\nResults:")
        for idx, row in df.iterrows():
            print(f"{idx+1}. {row['title'][:60]}...")
            print(f"   URL: {row['url']}")
            print(f"   Content length: {row['length']} chars")
            print()
    else:
        print("No successful crawls")

if __name__ == "__main__":
    main()