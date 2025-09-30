#!/usr/bin/env python3
"""
Simple Content Analysis using Claude Code
Extract insights from research data by creating analysis prompts for manual Claude Code execution
"""

import pandas as pd
import json
from datetime import datetime

class SimpleContentAnalyzer:
    def __init__(self):
        self.research_data = None

    def load_research_data(self, csv_file):
        """Load the enhanced research data"""
        try:
            self.research_data = pd.read_csv(csv_file)
            print(f"Loaded research data: {len(self.research_data)} sources")
            return True
        except Exception as e:
            print(f"Error loading research data: {e}")
            return False

    def create_analysis_prompts(self):
        """Create analysis prompts for Claude Code execution"""
        if self.research_data is None:
            print("No research data loaded")
            return

        # Focus on high-quality sources
        high_quality = self.research_data[
            self.research_data['relevance_score'] >= 4
        ].sort_values('relevance_score', ascending=False)

        print(f"Creating analysis prompts for {len(high_quality)} high-quality sources...")

        # Create individual analysis prompts
        prompts_file = "claude_analysis_prompts.md"
        with open(prompts_file, 'w', encoding='utf-8') as f:
            f.write("# Claude Code Analysis Prompts\n\n")
            f.write("Run each of these prompts using: `claude -p \"<prompt text>\"`\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for idx, row in high_quality.iterrows():
                f.write(f"## Analysis Prompt {idx+1}: {row['title'][:60]}...\n\n")
                f.write(f"**Source**: {row['title']}\n")
                f.write(f"**Type**: {row['source_type']}\n")
                f.write(f"**Topic**: {row['target_topic']}\n")
                f.write(f"**Relevance Score**: {row['relevance_score']}\n")
                f.write(f"**URL**: {row['url']}\n\n")

                # Create analysis prompt
                prompt = f"""Please analyze this research content about AI employability:

**Source**: {row['title']}
**Type**: {row['source_type']}
**Topic**: {row['target_topic']}

**Content**:
{row['content'][:2000]}...

Please provide:
1. Key findings related to AI employability
2. Important trends or patterns
3. Notable statistics or data points
4. Expert opinions or predictions
5. Actionable insights for simflo-rag development

Focus on the most relevant insights and keep analysis concise."""

                f.write(f"**Command**: `claude -p \"{prompt.replace('\"', '\\\"')}\"`\n\n")
                f.write("---\n\n")

        print(f"Analysis prompts saved to: {prompts_file}")

        # Create comprehensive analysis prompt
        comprehensive_prompt = self.create_comprehensive_analysis_prompt(high_quality)
        comp_file = "comprehensive_analysis_prompt.md"
        with open(comp_file, 'w', encoding='utf-8') as f:
            f.write(comprehensive_prompt)

        print(f"Comprehensive analysis prompt saved to: {comp_file}")

        return prompts_file, comp_file

    def create_comprehensive_analysis_prompt(self, high_quality_sources):
        """Create a comprehensive analysis prompt for all sources"""
        prompt = f"""# Comprehensive AI Employability Research Analysis

Please analyze this comprehensive research data about AI employability from {len(high_quality_sources)} high-quality sources collected on {datetime.now().strftime('%Y-%m-%d')}.

## Research Overview
- **Total Sources Analyzed**: {len(high_quality_sources)}
- **Content Volume**: {high_quality_sources['content_length'].sum()} characters
- **Source Types**: {dict(high_quality_sources['source_type'].value_counts())}
- **Average Relevance**: {high_quality_sources['relevance_score'].mean():.1f}

## High-Quality Sources by Type

"""

        # Group by source type
        by_type = {}
        for idx, row in high_quality_sources.iterrows():
            source_type = row['source_type']
            if source_type not in by_type:
                by_type[source_type] = []
            by_type[source_type].append(row)

        for source_type, sources in by_type.items():
            prompt += f"### {source_type.replace('_', ' ').title()} ({len(sources)} sources)\n\n"
            for row in sources:
                prompt += f"- **{row['title']}** (Score: {row['relevance_score']})\n"
                prompt += f"  Topic: {row['target_topic']}\n"
                prompt += f"  URL: {row['url']}\n\n"

        prompt += """
## Key Content Samples

Here are representative content samples from the highest quality sources:

"""

        # Include top 3 sources with content
        top_sources = high_quality_sources.nlargest(3, 'relevance_score')
        for idx, row in top_sources.iterrows():
            prompt += f"""
### Source {idx+1}: {row['title']} (Score: {row['relevance_score']})
**Type**: {row['source_type']} | **Topic**: {row['target_topic']}

**Content Excerpt**:
{row['content'][:1500]}...

---

"""

        prompt += """
## Analysis Request

Please provide a comprehensive analysis covering:

### 1. Key Themes and Patterns
- What are the most common themes across all sources?
- What patterns emerge about AI employability trends?
- What consensus or disagreements exist among sources?

### 2. Employment Market Insights
- How is AI changing job markets and career paths?
- What skills are becoming most valuable?
- What types of AI-related jobs are growing?

### 3. Industry Impact Analysis
- Which industries are most affected by AI adoption?
- How are different sectors adapting to AI?
- What industry-specific trends are emerging?

### 4. Future Predictions and Trends
- What do experts predict for AI employability in 2025-2030?
- What emerging trends should we watch?
- What long-term impacts are anticipated?

### 5. Actionable Insights for simflo-rag
- What features should simflo-rag prioritize based on these findings?
- What user needs are most critical to address?
- What market opportunities exist for AI employability tools?

### 6. Research Gaps and Opportunities
- What questions remain unanswered?
- What additional research would be valuable?
- What areas need deeper investigation?

Please provide specific, actionable insights that can guide simflo-rag development strategy. Include relevant statistics, quotes, and concrete examples from the sources where applicable.
"""

        return prompt

def main():
    """Main workflow"""
    print("=== Simple Content Analysis ===")
    print("Creating Claude Code analysis prompts\n")

    analyzer = SimpleContentAnalyzer()

    # Load research data
    latest_csv = "enhanced_ai_employability_research_20250930_120921.csv"
    if not analyzer.load_research_data(latest_csv):
        print("Failed to load research data")
        return

    # Create analysis prompts
    prompts_file, comp_file = analyzer.create_analysis_prompts()

    print(f"\n✅ Analysis prompts created!")
    print(f"Individual prompts: {prompts_file}")
    print(f"Comprehensive prompt: {comp_file}")

    print(f"\n📋 Next Steps:")
    print(f"1. Run: `claude -p \"$(cat comprehensive_analysis_prompt.md)\"`")
    print(f"2. Save the analysis results")
    print(f"3. Use insights to build RAG knowledge base")
    print(f"4. Generate final research report")

if __name__ == "__main__":
    main()