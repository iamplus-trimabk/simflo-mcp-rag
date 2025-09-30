# Simple Research Tools

## Evolutionary Approach: Good Enough > Perfect

### Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the crawler:**
```bash
python automated_research_crawler.py
```

### What This Does

- **Automated Source Discovery**: No manual URL lists needed
- **Search-Based Collection**: Uses DuckDuckGo to find relevant sources
- **Smart Filtering**: Focuses on AI employability content
- **Multi-Format Output**: CSV + JSON for analysis
- **Source Classification**: Academic, news, blog, official sources

### Key Features

✅ **No Manual Work**: Automatically generates search queries from topics
✅ **Smart Relevance Scoring**: Ranks content by AI employment relevance
✅ **Rate Limiting**: Respects servers with random delays
✅ **Error Handling**: Graceful failure recovery
✅ **Progress Tracking**: Real-time feedback on crawling progress

### Output Files

- `ai_employability_research_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `ai_employability_research_YYYYMMDD_HHMMSS.json` - Detailed data
- Console summary with top relevant results

### Next Evolution Steps

Once we have data, we can:
1. **Analyze patterns**: Look for common themes across sources
2. **Improve filtering**: Better relevance algorithms
3. **Add sources**: More specialized search engines
4. **Build RAG**: Vector database for knowledge retrieval

---

*Philosophy: Start with simple working solution, evolve based on real data and needs*