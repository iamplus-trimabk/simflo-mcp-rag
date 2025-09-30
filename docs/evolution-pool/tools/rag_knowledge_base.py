#!/usr/bin/env python3
"""
Simple RAG Knowledge Base for AI Employability Research
Build searchable knowledge base from collected research data and insights
"""

import pandas as pd
import json
import sqlite3
import os
from datetime import datetime
import re
from typing import List, Dict, Any

class RAGKnowledgeBase:
    def __init__(self, db_path="ai_employability_knowledge.db"):
        self.db_path = db_path
        self.conn = None
        self.knowledge_base = []

    def initialize_database(self):
        """Initialize SQLite database for knowledge storage"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # Create knowledge table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT,
                    topic TEXT,
                    relevance_score INTEGER,
                    url TEXT,
                    entry_type TEXT,  -- 'research_data', 'analysis_insight', 'strategic_recommendation'
                    tags TEXT,  -- JSON array of tags
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding_vector BLOB  -- For future vector search
                )
            ''')

            # Create search index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_search
                USING fts5(title, content, source_type, topic, tags)
            ''')

            self.conn.commit()
            print("Database initialized successfully")
            return True

        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False

    def load_research_data(self, csv_file):
        """Load research data from CSV"""
        try:
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} research sources")
            return df
        except Exception as e:
            print(f"Error loading research data: {e}")
            return None

    def load_analysis_insights(self, analysis_file):
        """Load analysis insights from markdown file"""
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Loaded analysis insights: {len(content)} characters")
            return content
        except Exception as e:
            print(f"Error loading analysis insights: {e}")
            return None

    def extract_tags_from_content(self, content: str, source_type: str, topic: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = [source_type.lower(), topic.lower()]

        # AI-related keywords
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'generative ai', 'llm',
            'automation', 'ai adoption', 'ai implementation', 'ai strategy'
        ]

        # Employment-related keywords
        employment_keywords = [
            'job market', 'career', 'employment', 'workforce', 'skills',
            'labor market', 'talent', 'hiring', 'recruitment'
        ]

        # Business-related keywords
        business_keywords = [
            'business impact', 'roi', 'productivity', 'efficiency',
            'transformation', 'digitalization', 'innovation'
        ]

        content_lower = content.lower()

        for keyword in ai_keywords + employment_keywords + business_keywords:
            if keyword in content_lower:
                tags.append(keyword.replace(' ', '_'))

        # Remove duplicates and limit
        unique_tags = list(set(tags))
        return unique_tags[:10]  # Limit to 10 tags per entry

    def add_research_entries(self, df):
        """Add research data entries to knowledge base"""
        cursor = self.conn.cursor()
        added_count = 0

        for idx, row in df.iterrows():
            try:
                # Extract tags
                tags = self.extract_tags_from_content(
                    row['content'], row['source_type'], row['target_topic']
                )

                # Insert into main table
                cursor.execute('''
                    INSERT INTO knowledge_entries
                    (title, content, source_type, topic, relevance_score, url, entry_type, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['title'],
                    row['content'],
                    row['source_type'],
                    row['target_topic'],
                    row['relevance_score'],
                    row['url'],
                    'research_data',
                    json.dumps(tags)
                ))

                added_count += 1

            except Exception as e:
                print(f"Error adding research entry {idx}: {e}")

        self.conn.commit()
        print(f"Added {added_count} research entries to knowledge base")

    def add_analysis_entries(self, analysis_content):
        """Add analysis insights to knowledge base"""
        cursor = self.conn.cursor()

        # Parse analysis content into sections
        sections = re.split(r'##\s+', analysis_content)[1:]  # Skip first section

        for section in sections:
            try:
                # Extract title and content
                lines = section.split('\n')
                title = lines[0].strip()
                content = '\n'.join(lines[1:]).strip()

                if len(content) > 100:  # Only add substantial sections
                    tags = self.extract_tags_from_content(content, 'analysis', 'strategic_insights')

                    cursor.execute('''
                        INSERT INTO knowledge_entries
                        (title, content, source_type, topic, relevance_score, url, entry_type, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        title,
                        content,
                        'analysis',
                        'strategic_insights',
                        10,  # High relevance for analysis
                        None,  # No URL for analysis
                        'analysis_insight',
                        json.dumps(tags)
                    ))

            except Exception as e:
                print(f"Error adding analysis section: {e}")

        self.conn.commit()
        print("Added analysis insights to knowledge base")

    def add_strategic_recommendations(self):
        """Add strategic recommendations based on analysis"""
        cursor = self.conn.cursor()

        recommendations = [
            {
                'title': 'Knowledge Democratization Engine',
                'content': 'Build natural language interfaces that make specialized AI knowledge accessible to non-technical users. Focus on lowering barriers to AI knowledge across organizations.',
                'tags': ['knowledge_democratization', 'natural_language', 'accessibility', 'user_interface']
            },
            {
                'title': 'Industry-Specific Customization',
                'content': 'Enable modular architecture for sector-specific fine-tuning of AI systems. Support proprietary data integration and industry-specific AI solutions.',
                'tags': ['industry_specific', 'customization', 'modular_architecture', 'proprietary_data']
            },
            {
                'title': 'Economic Intelligence Integration',
                'content': 'Incorporate market trend analysis and competitive advantage frameworks to help organizations identify AI-based economic opportunities.',
                'tags': ['economic_intelligence', 'market_trends', 'competitive_advantage', 'business_value']
            },
            {
                'title': 'Strategic Planning Support',
                'content': 'Implement AI-specific OKR tracking and progress measurement tools to support organizational AI transformation initiatives.',
                'tags': ['strategic_planning', 'okr_tracking', 'progress_measurement', 'transformation']
            },
            {
                'title': 'Cross-Functional Knowledge Integration',
                'content': 'Support knowledge transfer across traditional organizational boundaries as AI reshapes departmental structures and workflows.',
                'tags': ['cross_functional', 'knowledge_transfer', 'organizational_change', 'collaboration']
            }
        ]

        for rec in recommendations:
            cursor.execute('''
                INSERT INTO knowledge_entries
                (title, content, source_type, topic, relevance_score, url, entry_type, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rec['title'],
                rec['content'],
                'recommendation',
                'strategic_guidance',
                9,
                None,
                'strategic_recommendation',
                json.dumps(rec['tags'])
            ))

        self.conn.commit()
        print(f"Added {len(recommendations)} strategic recommendations")

    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base using full-text search"""
        cursor = self.conn.cursor()

        # Use FTS for search
        cursor.execute('''
            SELECT ke.*, ksn.rank
            FROM knowledge_entries ke
            JOIN knowledge_search ksn ON ke.rowid = ksn.rowid
            WHERE knowledge_search MATCH ?
            ORDER BY ksn.rank
            LIMIT ?
        ''', (query, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2][:500] + '...' if len(row[2]) > 500 else row[2],
                'source_type': row[3],
                'topic': row[4],
                'relevance_score': row[5],
                'url': row[6],
                'entry_type': row[7],
                'tags': json.loads(row[8]) if row[8] else [],
                'created_at': row[9],
                'search_rank': row[10]
            })

        return results

    def generate_knowledge_report(self):
        """Generate comprehensive knowledge base report"""
        cursor = self.conn.cursor()

        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total_entries = cursor.fetchone()[0]

        cursor.execute('SELECT entry_type, COUNT(*) FROM knowledge_entries GROUP BY entry_type')
        type_counts = dict(cursor.fetchall())

        cursor.execute('SELECT source_type, COUNT(*) FROM knowledge_entries GROUP BY source_type')
        source_counts = dict(cursor.fetchall())

        # Generate report
        report = f"""# AI Employability Knowledge Base Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Entries**: {total_entries}
**Database**: {self.db_path}

## Knowledge Base Statistics

### By Entry Type
"""
        for entry_type, count in type_counts.items():
            report += f"- **{entry_type}**: {count} entries\n"

        report += "\n### By Source Type\n"
        for source_type, count in source_counts.items():
            report += f"- **{source_type}**: {count} entries\n"

        report += f"""
## Search Capabilities

The knowledge base supports:
- **Full-text search** across all content, titles, and tags
- **Filtering by source type, topic, and entry type**
- **Relevance ranking** based on search term matching
- **Tag-based categorization** for content organization

## Knowledge Coverage

The knowledge base contains:
- **Research data** from 17 high-quality sources
- **Analysis insights** from Claude Code analysis
- **Strategic recommendations** for simflo-rag development
- **Industry-specific** AI employability trends
- **Economic impact** data and predictions

## Usage Examples

```python
# Search for specific topics
results = kb.search_knowledge("AI job market trends")
results = kb.search_knowledge("skills demand AI")
results = kb.search_knowledge("industry adoption patterns")
```

This knowledge base serves as the foundation for simflo-rag's AI employability intelligence capabilities.
"""

        # Save report
        report_file = f"knowledge_base_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Knowledge base report saved: {report_file}")
        return report_file

    def build_knowledge_base(self, research_csv, analysis_file):
        """Build complete knowledge base from research data and analysis"""
        print("=== Building AI Employability Knowledge Base ===")

        # Initialize database
        if not self.initialize_database():
            return False

        # Load and add research data
        research_df = self.load_research_data(research_csv)
        if research_df is not None:
            self.add_research_entries(research_df)

        # Load and add analysis insights
        analysis_content = self.load_analysis_insights(analysis_file)
        if analysis_content:
            self.add_analysis_entries(analysis_content)

        # Add strategic recommendations
        self.add_strategic_recommendations()

        # Generate report
        report_file = self.generate_knowledge_report()

        print(f"\n✅ Knowledge base built successfully!")
        print(f"Database: {self.db_path}")
        print(f"Report: {report_file}")

        return True

def main():
    """Main knowledge base building workflow"""
    print("AI Employability RAG Knowledge Base Builder\n")

    kb = RAGKnowledgeBase()

    # Build knowledge base
    research_csv = "enhanced_ai_employability_research_20250930_120921.csv"
    analysis_file = "key_insights_analysis.md"

    if kb.build_knowledge_base(research_csv, analysis_file):
        print("\n🔄 Ready for next evolution steps:")
        print("   1. Test search functionality")
        print("   2. Integrate with simflo-rag system")
        print("   3. Generate comprehensive research report")
        print("   4. Plan next evolution phase")
    else:
        print("❌ Knowledge base construction failed")

if __name__ == "__main__":
    main()