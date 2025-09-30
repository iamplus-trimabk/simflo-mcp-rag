#!/usr/bin/env python3
"""
Content Analysis & Summarization using Claude Code
Extract AI-powered insights from enhanced research data
"""

import pandas as pd
import json
import subprocess
import os
from datetime import datetime
import re

class ContentAnalyzer:
    def __init__(self):
        self.research_data = None
        self.analysis_results = []

    def load_research_data(self, csv_file):
        """Load the enhanced research data"""
        try:
            self.research_data = pd.read_csv(csv_file)
            print(f"Loaded research data: {len(self.research_data)} sources")
            print(f"Total content: {self.research_data['content_length'].sum()} characters")
            return True
        except Exception as e:
            print(f"Error loading research data: {e}")
            return False

    def create_analysis_prompt(self, content_chunk, source_info, focus_area):
        """Create Claude Code analysis prompt for content chunk"""

        prompt = f"""
Please analyze this research content about AI employability and provide key insights:

**Source Context:**
- Title: {source_info['title']}
- Type: {source_info['source_type']}
- Topic: {source_info['target_topic']}
- Relevance Score: {source_info['relevance_score']}

**Content to Analyze:**
{content_chunk}

**Analysis Focus: {focus_area}**

Please provide:
1. Key findings related to AI employability
2. Important trends or patterns
3. Notable statistics or data points
4. Expert opinions or predictions
5. Actionable insights for simflo-rag development

Keep the analysis concise and focused on the most relevant insights.
"""

        return prompt

    def analyze_with_claude_code(self, prompt, output_file):
        """Use Claude Code to analyze content"""
        try:
            # Use Claude Code with --print option to get analysis
            cmd = [
                "claude",
                "-p",  # Print response and exit
                "--output-format", "json",
                prompt
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Parse JSON response and save to output file
                try:
                    response_data = json.loads(result.stdout)
                    analysis_text = response_data.get('content', result.stdout)

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(analysis_text)

                    return output_file
                except json.JSONDecodeError:
                    # Fallback: save raw output
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    return output_file
            else:
                print(f"Claude Code analysis failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"Error using Claude Code: {e}")
            return None

    def chunk_content(self, content, max_length=3000):
        """Split content into manageable chunks for analysis"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def analyze_high_quality_sources(self):
        """Focus analysis on high-relevance sources"""
        if self.research_data is None:
            print("No research data loaded")
            return

        # Filter for high-quality sources
        high_quality = self.research_data[
            self.research_data['relevance_score'] >= 4
        ].sort_values('relevance_score', ascending=False)

        print(f"Analyzing {len(high_quality)} high-quality sources...")

        analysis_dir = "content_analysis_results"
        os.makedirs(analysis_dir, exist_ok=True)

        all_insights = []

        for idx, row in high_quality.iterrows():
            print(f"Analyzing source {idx+1}/{len(high_quality)}: {row['title'][:50]}...")

            # Chunk content if too long
            content = row['content']
            if len(content) > 3000:
                content = content[:3000] + "...[truncated]"

            # Create analysis prompt
            prompt = self.create_analysis_prompt(
                content,
                row.to_dict(),
                "AI Employability Insights"
            )

            # Generate analysis using Claude Code
            output_file = f"{analysis_dir}/analysis_{idx+1:02d}_{row['source_type']}_{row['relevance_score']}.md"

            analysis_result = self.analyze_with_claude_code(prompt, output_file)

            if analysis_result and os.path.exists(analysis_result):
                # Read the analysis result
                try:
                    with open(analysis_result, 'r', encoding='utf-8') as f:
                        analysis_text = f.read()

                    # Store analysis result
                    analysis_entry = {
                        'source_index': idx,
                        'title': row['title'],
                        'url': row['url'],
                        'source_type': row['source_type'],
                        'target_topic': row['target_topic'],
                        'relevance_score': row['relevance_score'],
                        'analysis_file': analysis_result,
                        'analysis_text': analysis_text,
                        'analyzed_at': datetime.now().isoformat()
                    }

                    all_insights.append(analysis_entry)
                    print(f"✓ Analysis saved: {output_file}")

                except Exception as e:
                    print(f"Error reading analysis result: {e}")
            else:
                print(f"✗ Analysis failed for source {idx+1}")

        # Save consolidated analysis
        self.save_analysis_summary(all_insights)
        return all_insights

    def save_analysis_summary(self, insights):
        """Save consolidated analysis summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as JSON
        json_file = f"content_analysis_summary_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)

        # Create markdown summary
        md_file = f"content_analysis_summary_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# AI Employability Research - Content Analysis Summary\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Sources Analyzed: {len(insights)}\n\n")

            f.write("## Key Insights by Source Type\n\n")

            # Group by source type
            by_type = {}
            for insight in insights:
                source_type = insight['source_type']
                if source_type not in by_type:
                    by_type[source_type] = []
                by_type[source_type].append(insight)

            for source_type, type_insights in by_type.items():
                f.write(f"### {source_type.replace('_', ' ').title()} ({len(type_insights)} sources)\n\n")

                for insight in type_insights:
                    f.write(f"#### {insight['title'][:80]}... (Score: {insight['relevance_score']})\n")
                    f.write(f"- **Topic**: {insight['target_topic']}\n")
                    f.write(f"- **URL**: {insight['url']}\n")
                    f.write(f"- **Analysis**: [View detailed analysis]({insight['analysis_file']})\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. **Extract Key Themes**: Identify common patterns across sources\n")
            f.write("2. **Create Actionable Insights**: Convert findings into development guidance\n")
            f.write("3. **Build RAG Knowledge Base**: Structure analysis for searchable access\n")
            f.write("4. **Generate Final Report**: Synthesize all findings\n")

        print(f"Analysis summary saved:")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")

        return json_file, md_file

def main():
    """Main content analysis workflow"""
    print("=== AI Employability Content Analysis ===")
    print("Using Claude Code for intelligent content analysis\n")

    analyzer = ContentAnalyzer()

    # Load research data
    latest_csv = "enhanced_ai_employability_research_20250930_120921.csv"
    if not analyzer.load_research_data(latest_csv):
        print("Failed to load research data")
        return

    # Analyze high-quality sources
    insights = analyzer.analyze_high_quality_sources()

    if insights:
        print(f"\n✅ Content analysis completed!")
        print(f"Analyzed {len(insights)} high-quality sources")
        print(f"Individual analysis files saved in 'content_analysis_results/' directory")

        print("\n🔄 Ready for next evolution steps:")
        print("   1. Review analysis results")
        print("   2. Extract key themes and patterns")
        print("   3. Build RAG knowledge base")
        print("   4. Generate comprehensive research report")
    else:
        print("❌ Content analysis failed")

if __name__ == "__main__":
    main()