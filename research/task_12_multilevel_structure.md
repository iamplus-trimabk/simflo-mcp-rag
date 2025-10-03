# Task 12: Advanced Multi-Format Documentation Architecture

## Overview

Modern documentation systems require sophisticated multi-level structuring that supports various content formats, adaptive delivery mechanisms, and intelligent content organization. This comprehensive approach provides hierarchical documentation with cross-format compatibility and intelligent content discovery.

## Advanced Hierarchical Content Organization

### Multi-Dimensional Content Classification

```python
import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime

class ContentComplexity(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(Enum):
    ARCHITECTURE = "architecture"
    API = "api"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    EXAMPLE = "example"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"

class DocumentationLevel(Enum):
    EXECUTIVE = "executive"      # High-level overview for decision makers
    ARCHITECTURAL = "architectural"  # System design and patterns
    TECHNICAL = "technical"      # Implementation details
    IMPLEMENTATION = "implementation"  # Code-level specifics
    OPERATIONAL = "operational"  # Runtime and maintenance

@dataclass
class ContentMetadata:
    """Rich metadata for documentation chunks."""
    content_id: str
    title: str
    content_type: ContentType
    complexity: ContentComplexity
    level: DocumentationLevel
    target_audience: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    estimated_read_time: int  # minutes
    related_topics: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    interactive_elements: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    popularity_score: float = 0.0
    completion_rate: float = 0.0

@dataclass
class DocumentationChunk:
    """Enhanced documentation chunk with multi-level metadata."""
    content: str
    metadata: ContentMetadata
    children: List['DocumentationChunk'] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    semantic_hash: str = field(default="")

    def __post_init__(self):
        if not self.semantic_hash:
            self.semantic_hash = self.calculate_semantic_hash()

    def calculate_semantic_hash(self) -> str:
        """Calculate semantic hash for content deduplication."""
        content = f"{self.metadata.title} {self.content[:500]}"
        return hashlib.md5(content.encode()).hexdigest()

class AdvancedContentOrganizer:
    """Sophisticated content organization with multi-dimensional analysis."""

    def __init__(self):
        self.chunks: Dict[str, DocumentationChunk] = {}
        self.content_graph = nx.DiGraph()
        self.audience_mapping: Dict[str, List[str]] = {}
        self.learning_paths: Dict[str, List[str]] = {}

    def analyze_and_organize(self, raw_chunks: List[Dict[str, Any]]) -> Dict[str, DocumentationChunk]:
        """Analyze raw content and organize into hierarchical structure."""
        # First pass: Create chunks with metadata
        for chunk_data in raw_chunks:
            chunk = self.create_enhanced_chunk(chunk_data)
            self.chunks[chunk.metadata.content_id] = chunk

        # Second pass: Build relationships
        self.build_content_relationships()
        self.calculate_quality_scores()
        self.generate_learning_paths()

        return self.chunks

    def create_enhanced_chunk(self, chunk_data: Dict[str, Any]) -> DocumentationChunk:
        """Create documentation chunk with comprehensive metadata."""
        content = chunk_data.get('content', '')
        content_type = self.classify_content_type(content)
        complexity = self.assess_complexity(content)
        level = self.determine_documentation_level(content, chunk_data)
        target_audience = self.identify_target_audience(content, level, complexity)

        metadata = ContentMetadata(
            content_id=self.generate_content_id(content),
            title=self.extract_title(content, chunk_data),
            content_type=content_type,
            complexity=complexity,
            level=level,
            target_audience=target_audience,
            prerequisites=self.extract_prerequisites(content),
            learning_objectives=self.extract_learning_objectives(content),
            estimated_read_time=self.estimate_read_time(content),
            related_topics=self.extract_related_topics(content),
            code_examples=self.extract_code_examples(content),
            interactive_elements=self.identify_interactive_elements(content)
        )

        return DocumentationChunk(
            content=content,
            metadata=metadata,
            tags=self.extract_tags(content, chunk_data)
        )

    def classify_content_type(self, content: str) -> ContentType:
        """Advanced content type classification using multiple signals."""
        content_lower = content.lower()

        # Architecture indicators
        architecture_signals = [
            'system architecture', 'design pattern', 'component', 'module',
            'microservice', 'scalability', 'high availability', 'deployment',
            'infrastructure', 'integration', 'api gateway'
        ]

        # API indicators
        api_signals = [
            'endpoint', 'request', 'response', 'http', 'rest', 'graphql',
            'api documentation', 'authentication', 'authorization',
            'swagger', 'openapi', 'postman', 'curl'
        ]

        # Tutorial indicators
        tutorial_signals = [
            'step by step', 'how to', 'tutorial', 'getting started',
            'follow along', 'learn', 'example', 'walkthrough',
            'hands on', 'practice', 'exercise'
        ]

        # Reference indicators
        reference_signals = [
            'reference', 'documentation', 'syntax', 'parameters',
            'return value', 'method', 'function', 'class',
            'interface', 'enumeration', 'constant'
        ]

        # Conceptual indicators
        conceptual_signals = [
            'concept', 'theory', 'principle', 'fundamental',
            'overview', 'introduction', 'background', 'history',
            'philosophy', 'rationale', 'motivation'
        ]

        # Procedural indicators
        procedural_signals = [
            'procedure', 'process', 'workflow', 'steps',
            'installation', 'configuration', 'setup',
            'deployment', 'maintenance', 'troubleshooting'
        ]

        # Calculate scores for each type
        signal_scores = {
            ContentType.ARCHITECTURE: self.count_signals(content_lower, architecture_signals),
            ContentType.API: self.count_signals(content_lower, api_signals),
            ContentType.TUTORIAL: self.count_signals(content_lower, tutorial_signals),
            ContentType.REFERENCE: self.count_signals(content_lower, reference_signals),
            ContentType.CONCEPTUAL: self.count_signals(content_lower, conceptual_signals),
            ContentType.PROCEDURAL: self.count_signals(content_lower, procedural_signals)
        }

        # Add code-based classification
        if self.has_code_blocks(content):
            if 'class ' in content or 'interface ' in content:
                signal_scores[ContentType.REFERENCE] += 3
            elif 'function ' in content or 'def ' in content:
                signal_scores[ContentType.TUTORIAL] += 2
                signal_scores[ContentType.REFERENCE] += 1

        # Return the type with highest score
        return max(signal_scores, key=signal_scores.get)

    def count_signals(self, content: str, signals: List[str]) -> int:
        """Count occurrence of signal phrases in content."""
        score = 0
        for signal in signals:
            score += content.count(signal)
            # Weight exact matches higher
            if signal in content:
                score += 2
        return score

    def assess_complexity(self, content: str) -> ContentComplexity:
        """Assess content complexity using multiple factors."""
        complexity_score = 0

        # Technical indicators
        technical_terms = [
            'algorithm', 'optimization', 'performance', 'scalability',
            'asynchronous', 'concurrent', 'distributed', 'encryption',
            'authentication', 'authorization', 'middleware', 'framework'
        ]

        for term in technical_terms:
            complexity_score += content.lower().count(term) * 2

        # Code complexity
        if self.has_code_blocks(content):
            complexity_score += len(self.extract_code_examples(content)) * 3

            # Check for advanced programming concepts
            advanced_concepts = [
                'recursion', 'polymorphism', 'inheritance', 'abstraction',
                'closure', 'decorator', 'generics', 'async/await',
                'promise', 'callback', 'observer', 'factory'
            ]

            for concept in advanced_concepts:
                complexity_score += content.lower().count(concept) * 2

        # Length and structure complexity
        word_count = len(content.split())
        if word_count > 1000:
            complexity_score += 5
        elif word_count > 500:
            complexity_score += 3

        # Mathematical/notation complexity
        math_patterns = [r'\{.*\}', r'\[.*\]', r'\$.*\$', r'\\[a-zA-Z]+\{']
        for pattern in math_patterns:
            if re.search(pattern, content):
                complexity_score += 3

        # Classify based on score
        if complexity_score >= 20:
            return ContentComplexity.EXPERT
        elif complexity_score >= 15:
            return ContentComplexity.ADVANCED
        elif complexity_score >= 8:
            return ContentComplexity.INTERMEDIATE
        else:
            return ContentComplexity.BASIC

    def determine_documentation_level(self, content: str, chunk_data: Dict[str, Any]) -> DocumentationLevel:
        """Determine documentation level based on content characteristics."""
        content_lower = content.lower()

        # Executive level indicators
        executive_signals = [
            'business value', 'roi', 'cost benefit', 'strategic',
            'market', 'competitive', 'executive', 'leadership',
            'vision', 'mission', 'goals', 'objectives', 'kpis'
        ]

        # Architectural level indicators
        architectural_signals = [
            'architecture', 'design', 'pattern', 'system',
            'component', 'integration', 'scalability', 'performance',
            'security', 'infrastructure', 'deployment'
        ]

        # Technical level indicators
        technical_signals = [
            'implementation', 'development', 'programming',
            'code', 'api', 'library', 'framework', 'configuration',
            'build', 'test', 'deploy'
        ]

        # Implementation level indicators
        implementation_signals = [
            'function', 'method', 'class', 'variable',
            'syntax', 'parameter', 'return', 'exception',
            'debug', 'optimize', 'refactor'
        ]

        # Operational level indicators
        operational_signals = [
            'monitoring', 'maintenance', 'support',
            'troubleshooting', 'incident', 'backup',
            'restore', 'scaling', 'performance tuning'
        ]

        # Calculate scores
        level_scores = {
            DocumentationLevel.EXECUTIVE: self.count_signals(content_lower, executive_signals),
            DocumentationLevel.ARCHITECTURAL: self.count_signals(content_lower, architectural_signals),
            DocumentationLevel.TECHNICAL: self.count_signals(content_lower, technical_signals),
            DocumentationLevel.IMPLEMENTATION: self.count_signals(content_lower, implementation_signals),
            DocumentationLevel.OPERATIONAL: self.count_signals(content_lower, operational_signals)
        }

        # Consider file path and context
        file_path = chunk_data.get('file_path', '').lower()
        if 'arch' in file_path or 'design' in file_path:
            level_scores[DocumentationLevel.ARCHITECTURAL] += 3
        elif 'api' in file_path or 'spec' in file_path:
            level_scores[DocumentationLevel.TECHNICAL] += 3
        elif 'guide' in file_path or 'tutorial' in file_path:
            level_scores[DocumentationLevel.IMPLEMENTATION] += 2

        return max(level_scores, key=level_scores.get)

    def identify_target_audience(self, content: str, level: DocumentationLevel, complexity: ContentComplexity) -> List[str]:
        """Identify target audience based on content characteristics."""
        audience_map = {
            DocumentationLevel.EXECUTIVE: ['executives', 'managers', 'decision-makers', 'stakeholders'],
            DocumentationLevel.ARCHITECTURAL: ['architects', 'senior-developers', 'tech-leads', 'system-designers'],
            DocumentationLevel.TECHNICAL: ['developers', 'engineers', 'technical-managers', 'devops'],
            DocumentationLevel.IMPLEMENTATION: ['developers', 'programmers', 'coders', 'software-engineers'],
            DocumentationLevel.OPERATIONAL: ['ops-engineers', 'administrators', 'support-staff', 'devops']
        }

        base_audience = audience_map.get(level, ['general'])

        # Adjust based on complexity
        if complexity == ContentComplexity.BASIC:
            base_audience.extend(['beginners', 'students', 'new-developers'])
        elif complexity == ContentComplexity.EXPERT:
            base_audience.extend(['experts', 'specialists', 'researchers'])

        # Look for specific audience indicators
        content_lower = content.lower()
        if 'beginner' in content_lower or 'intro' in content_lower:
            base_audience.extend(['beginners'])
        elif 'advanced' in content_lower or 'expert' in content_lower:
            base_audience.extend(['advanced-users', 'experts'])

        return list(set(base_audience))  # Remove duplicates

    def build_content_relationships(self) -> None:
        """Build relationships between content chunks."""
        for chunk_id, chunk in self.chunks.items():
            # Build content graph
            self.content_graph.add_node(chunk_id, chunk=chunk)

            # Find related chunks based on content similarity
            for other_id, other_chunk in self.chunks.items():
                if chunk_id != other_id:
                    similarity = self.calculate_content_similarity(chunk, other_chunk)
                    if similarity > 0.3:  # Threshold for relationship
                        self.content_graph.add_edge(chunk_id, other_id, weight=similarity)
                        chunk.cross_references.append(other_id)

            # Build parent-child relationships based on hierarchy
            self.build_hierarchy_relationships(chunk)

    def calculate_content_similarity(self, chunk1: DocumentationChunk, chunk2: DocumentationChunk) -> float:
        """Calculate similarity between two content chunks."""
        # Title similarity
        title_similarity = self.text_similarity(chunk1.metadata.title, chunk2.metadata.title)

        # Content similarity
        content_similarity = self.text_similarity(chunk1.content[:500], chunk2.content[:500])

        # Tag similarity
        tags1 = set(chunk1.tags)
        tags2 = set(chunk2.tags)
        tag_similarity = len(tags1.intersection(tags2)) / max(len(tags1.union(tags2)), 1)

        # Type and level similarity
        type_match = 1.0 if chunk1.metadata.content_type == chunk2.metadata.content_type else 0.0
        level_match = 1.0 if chunk1.metadata.level == chunk2.metadata.level else 0.0

        # Weighted combination
        overall_similarity = (
            title_similarity * 0.3 +
            content_similarity * 0.4 +
            tag_similarity * 0.2 +
            type_match * 0.05 +
            level_match * 0.05
        )

        return overall_similarity

    def text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using word overlap."""
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def build_hierarchy_relationships(self, chunk: DocumentationChunk) -> None:
        """Build parent-child relationships based on content hierarchy."""
        # Find potential parents (more general content)
        potential_parents = [
            other for other in self.chunks.values()
            if (other.metadata.level.value < chunk.metadata.level.value and
                other.metadata.complexity.value <= chunk.metadata.complexity.value and
                self.calculate_content_similarity(chunk, other) > 0.2)
        ]

        # Sort by similarity and add top matches as parents
        potential_parents.sort(key=lambda p: self.calculate_content_similarity(chunk, p), reverse=True)

        for parent in potential_parents[:2]:  # Limit to 2 parents
            chunk.parents.append(parent.metadata.content_id)
            parent.children.append(chunk.metadata.content_id)

    def calculate_quality_scores(self) -> None:
        """Calculate quality scores for all chunks."""
        for chunk in self.chunks.values():
            score = 0.0

            # Content structure quality
            if self.has_code_blocks(chunk.content):
                score += 0.2
            if self.has_headings(chunk.content):
                score += 0.1
            if chunk.metadata.learning_objectives:
                score += 0.15

            # Metadata completeness
            metadata_fields = [
                chunk.metadata.prerequisites,
                chunk.metadata.learning_objectives,
                chunk.metadata.related_topics,
                chunk.metadata.target_audience
            ]
            completeness = sum(1 for field in metadata_fields if field) / len(metadata_fields)
            score += completeness * 0.3

            # Cross-reference quality
            if len(chunk.cross_references) > 0:
                score += min(0.2, len(chunk.cross_references) * 0.05)

            chunk.metadata.quality_score = min(1.0, score)

    def generate_learning_paths(self) -> None:
        """Generate learning paths for different audiences."""
        for audience_type in ['beginners', 'developers', 'architects', 'experts']:
            relevant_chunks = [
                chunk for chunk in self.chunks.values()
                if audience_type in chunk.metadata.target_audience
            ]

            # Sort by complexity and level
            relevant_chunks.sort(key=lambda c: (
                c.metadata.level.value,
                c.metadata.complexity.value
            ))

            # Build learning path using graph traversal
            path = self.build_learning_path(relevant_chunks)
            self.learning_paths[audience_type] = path

    def build_learning_path(self, chunks: List[DocumentationChunk]) -> List[str]:
        """Build optimal learning path through content."""
        if not chunks:
            return []

        # Start with basic content
        path = [chunks[0].metadata.content_id]
        visited = {chunks[0].metadata.content_id}
        current = chunks[0]

        # Greedy path building
        while len(path) < min(len(chunks), 10):  # Limit path length
            best_next = None
            best_score = 0

            for chunk in chunks:
                if chunk.metadata.content_id not in visited:
                    # Score based on prerequisites and similarity
                    score = 0

                    # Check if prerequisites are met
                    prereq_met = all(
                        prereq in visited for prereq in chunk.metadata.prerequisites
                    )
                    if prereq_met:
                        score += 2

                    # Content similarity
                    similarity = self.calculate_content_similarity(current, chunk)
                    score += similarity

                    # Complexity progression
                    if (chunk.metadata.complexity.value >= current.metadata.complexity.value and
                        chunk.metadata.level.value >= current.metadata.level.value):
                        score += 1

                    if score > best_score:
                        best_score = score
                        best_next = chunk

            if best_next:
                path.append(best_next.metadata.content_id)
                visited.add(best_next.metadata.content_id)
                current = best_next
            else:
                break

        return path

    # Helper methods for content analysis
    def has_code_blocks(self, content: str) -> bool:
        """Check if content contains code blocks."""
        return bool(re.search(r'```[^`]+```|`[^`]+`', content))

    def has_headings(self, content: str) -> bool:
        """Check if content has structured headings."""
        return bool(re.search(r'^#+\s+', content, re.MULTILINE))

    def extract_title(self, content: str, chunk_data: Dict[str, Any]) -> str:
        """Extract title from content or metadata."""
        # Try to extract from content
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        # Try filename
        if 'file_path' in chunk_data:
            filename = chunk_data['file_path'].split('/')[-1]
            return filename.replace('_', ' ').replace('-', ' ').title()

        # Fallback to first line or generated title
        lines = content.split('\n')
        first_line = lines[0].strip() if lines else 'Untitled'
        if len(first_line) < 100 and first_line:
            return first_line

        # Generate title from first few words
        words = content.split()[:5]
        return ' '.join(words) + ('...' if len(content.split()) > 5 else '')

    def extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisites from content."""
        prerequisites = []
        content_lower = content.lower()

        # Look for explicit prerequisites
        prereq_patterns = [
            r'prerequisite[s]?:\s*(.+?)(?:\n|$)',
            r'required?:\s*(.+?)(?:\n|$)',
            r'before you begin:\s*(.+?)(?:\n|$)',
            r'you should know:\s*(.+?)(?:\n|$)'
        ]

        for pattern in prereq_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                items = [item.strip() for item in match.split(',')]
                prerequisites.extend([item for item in items if item])

        # Look for technical prerequisites
        tech_patterns = [
            r'knowledge of ([^.]+)',
            r'familiarity with ([^.]+)',
            r'experience with ([^.]+)'
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            prerequisites.extend([match.strip() for match in matches])

        return list(set(prerequisites))[:5]  # Limit to 5 prerequisites

    def extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content."""
        objectives = []
        content_lower = content.lower()

        # Look for explicit objectives
        objective_patterns = [
            r'(?:you will|objectives?|goals?):\s*(.+?)(?:\n\n|\n[A-Z]|\n#|$)',
            r'after this.*?(?:learn|understand|be able to):\s*(.+?)(?:\n\n|\n[A-Z]|\n#|$)',
            r'in this.*?(?:learn|understand|master):\s*(.+?)(?:\n\n|\n[A-Z]|\n#|$)'
        ]

        for pattern in objective_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                # Split by common separators
                items = re.split(r'[,;•]\s*', match)
                objectives.extend([item.strip() for item in items if len(item.strip()) > 5])

        return list(set(objectives))[:5]  # Limit to 5 objectives

    def estimate_read_time(self, content: str) -> int:
        """Estimate reading time in minutes."""
        word_count = len(content.split())
        code_blocks = re.findall(r'```[^`]+```', content)
        code_words = sum(len(block.split()) for block in code_blocks)

        # Adjust for code (slower to read)
        adjusted_word_count = word_count + (code_words * 0.5)
        reading_speed = 200  # words per minute

        return max(1, int(adjusted_word_count / reading_speed))

    def extract_related_topics(self, content: str) -> List[str]:
        """Extract related topics from content."""
        topics = []
        content_lower = content.lower()

        # Look for topic mentions
        topic_patterns = [
            r'(?:related|see also|related topics?):\s*(.+?)(?:\n\n|\n#|$)',
            r'(?:learn more|further reading):\s*(.+?)(?:\n\n|\n#|$)'
        ]

        for pattern in topic_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                items = re.split(r'[,;]\s*', match)
                topics.extend([item.strip() for item in items if item])

        return list(set(topics))[:3]  # Limit to 3 related topics

    def extract_code_examples(self, content: str) -> List[str]:
        """Extract code examples from content."""
        code_blocks = re.findall(r'```(\w+)?\n([^`]+)```', content)
        return [block[1] for block in code_blocks]

    def identify_interactive_elements(self, content: str) -> List[str]:
        """Identify interactive elements in content."""
        interactive = []
        content_lower = content.lower()

        interactive_indicators = [
            'interactive', 'live demo', 'playground', 'sandbox',
            'exercise', 'quiz', 'challenge', 'try it yourself',
            'hands-on', 'practice', 'simulation'
        ]

        for indicator in interactive_indicators:
            if indicator in content_lower:
                interactive.append(indicator)

        return list(set(interactive))

    def extract_tags(self, content: str, chunk_data: Dict[str, Any]) -> List[str]:
        """Extract tags from content and metadata."""
        tags = set()

        # Add content type tags
        content_lower = content.lower()
        if 'api' in content_lower:
            tags.add('api')
        if 'tutorial' in content_lower:
            tags.add('tutorial')
        if 'example' in content_lower:
            tags.add('example')
        if 'reference' in content_lower:
            tags.add('reference')

        # Add language-specific tags
        languages = ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++']
        for lang in languages:
            if lang in content_lower:
                tags.add(lang)

        # Add file path-based tags
        if 'file_path' in chunk_data:
            path_parts = chunk_data['file_path'].lower().split('/')
            for part in path_parts:
                if len(part) > 2:
                    tags.add(part)

        return list(tags)[:10]  # Limit to 10 tags

    def generate_content_id(self, content: str) -> str:
        """Generate unique content ID."""
        return hashlib.sha256(content[:200].encode()).hexdigest()[:16]
```

## Multi-Format Documentation Generation

### Adaptive Content Rendering

```python
import json
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import markdown
import jinja2

class OutputFormat(Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    EPUB = "epub"
    DOCX = "docx"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    JUPYTER = "jupyter"
    SPHINX = "sphinx"
    DITA = "dita"

@dataclass
class RenderingConfig:
    """Configuration for content rendering."""
    format: OutputFormat
    template_path: Optional[str] = None
    style_config: Optional[Dict] = None
    output_options: Dict = None

class MultiFormatRenderer:
    """Advanced multi-format documentation renderer."""

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader({
                'markdown_template': self._get_markdown_template(),
                'html_template': self._get_html_template(),
                'api_template': self._get_api_template(),
                'tutorial_template': self._get_tutorial_template()
            })
        )
        self.formatters = {
            OutputFormat.MARKDOWN: self._render_markdown,
            OutputFormat.HTML: self._render_html,
            OutputFormat.JSON: self._render_json,
            OutputFormat.YAML: self._render_yaml,
            OutputFormat.XML: self._render_xml,
            OutputFormat.JUPYTER: self._render_jupyter,
            OutputFormat.SPHINX: self._render_sphinx,
            OutputFormat.DITA: self._render_dita
        }

    def render_content(self, chunks: Dict[str, DocumentationChunk],
                      config: RenderingConfig) -> str:
        """Render documentation chunks in specified format."""
        if config.format not in self.formatters:
            raise ValueError(f"Unsupported format: {config.format}")

        # Organize content by level and type
        organized_content = self._organize_by_level(chunks)

        # Apply formatting
        formatter = self.formatters[config.format]
        return formatter(organized_content, config)

    def render_all_formats(self, chunks: Dict[str, DocumentationChunk]) -> Dict[str, str]:
        """Render documentation in all supported formats."""
        results = {}

        for format_enum in OutputFormat:
            try:
                config = RenderingConfig(format=format_enum)
                results[format_enum.value] = self.render_content(chunks, config)
            except Exception as e:
                print(f"Error rendering {format_enum.value}: {e}")
                results[format_enum.value] = f"Error: {str(e)}"

        return results

    def _organize_by_level(self, chunks: Dict[str, DocumentationChunk]) -> Dict:
        """Organize chunks by documentation level."""
        organized = {
            'executive': [],
            'architectural': [],
            'technical': [],
            'implementation': [],
            'operational': []
        }

        for chunk in chunks.values():
            level_key = chunk.metadata.level.value
            if level_key in organized:
                organized[level_key].append(chunk)

        # Sort each level by quality score
        for level_chunks in organized.values():
            level_chunks.sort(key=lambda c: c.metadata.quality_score, reverse=True)

        return organized

    def _render_markdown(self, organized_content: Dict, config: RenderingConfig) -> str:
        """Render content as structured Markdown."""
        template = self.jinja_env.get_template('markdown_template')

        # Convert each level to markdown
        rendered_levels = {}
        for level, chunks in organized_content.items():
            rendered_levels[level] = self._render_level_markdown(chunks, level)

        return template.render(
            levels=rendered_levels,
            title="Documentation",
            generated_at=datetime.now().isoformat()
        )

    def _render_level_markdown(self, chunks: List[DocumentationChunk], level: str) -> str:
        """Render a single level as Markdown."""
        if not chunks:
            return ""

        md_content = f"\n\n## {level.title()} Level Documentation\n\n"

        for chunk in chunks:
            md_content += f"### {chunk.metadata.title}\n\n"

            # Add metadata
            if chunk.metadata.target_audience:
                md_content += f"**Audience:** {', '.join(chunk.metadata.target_audience)}\n\n"

            if chunk.metadata.estimated_read_time:
                md_content += f"**Read Time:** {chunk.metadata.estimated_read_time} minutes\n\n"

            if chunk.metadata.prerequisites:
                md_content += f"**Prerequisites:** {', '.join(chunk.metadata.prerequisites)}\n\n"

            # Add content
            md_content += f"{chunk.content}\n\n"

            # Add cross-references
            if chunk.cross_references:
                md_content += "**Related:**\n"
                for ref_id in chunk.cross_references[:3]:
                    if ref_id in self.chunks:
                        ref_chunk = self.chunks[ref_id]
                        md_content += f"- [{ref_chunk.metadata.title}](#{ref_chunk.metadata.title.lower().replace(' ', '-')})\n"
                md_content += "\n"

            md_content += "---\n\n"

        return md_content

    def _render_html(self, organized_content: Dict, config: RenderingConfig) -> str:
        """Render content as responsive HTML."""
        template = self.jinja_env.get_template('html_template')

        # Convert markdown to HTML
        rendered_levels = {}
        for level, chunks in organized_content.items():
            rendered_levels[level] = self._render_level_html(chunks, level)

        # Generate table of contents
        toc = self._generate_html_toc(organized_content)

        return template.render(
            toc=toc,
            levels=rendered_levels,
            title="Documentation",
            generated_at=datetime.now().isoformat(),
            css_styles=self._get_html_styles()
        )

    def _render_level_html(self, chunks: List[DocumentationChunk], level: str) -> str:
        """Render a single level as HTML."""
        if not chunks:
            return ""

        html_parts = [f'<section class="level level-{level}">']
        html_parts.append(f'<h2>{level.title()} Level Documentation</h2>')

        for chunk in chunks:
            html_parts.append(f'<article class="content-chunk" id="{chunk.metadata.content_id}">')
            html_parts.append(f'<h3>{chunk.metadata.title}</h3>')

            # Metadata sidebar
            html_parts.append('<aside class="chunk-metadata">')
            if chunk.metadata.target_audience:
                html_parts.append(f'<div class="audience"><strong>Audience:</strong> {", ".join(chunk.metadata.target_audience)}</div>')

            if chunk.metadata.estimated_read_time:
                html_parts.append(f'<div class="read-time"><strong>Read Time:</strong> {chunk.metadata.estimated_read_time} minutes</div>')

            if chunk.metadata.quality_score:
                html_parts.append(f'<div class="quality"><strong>Quality:</strong> {chunk.metadata.quality_score:.1%}</div>')

            html_parts.append('</aside>')

            # Content
            content_html = markdown.markdown(chunk.content, extensions=['codehilite', 'toc', 'tables'])
            html_parts.append(f'<div class="content">{content_html}</div>')

            html_parts.append('</article>')

        html_parts.append('</section>')
        return ''.join(html_parts)

    def _render_json(self, organized_content: Dict, config: RenderingConfig) -> str:
        """Render content as structured JSON."""
        json_data = {
            'metadata': {
                'title': 'Documentation',
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'total_chunks': sum(len(chunks) for chunks in organized_content.values())
            },
            'levels': {}
        }

        for level, chunks in organized_content.items():
            level_data = {
                'title': f"{level.title()} Level",
                'chunks': []
            }

            for chunk in chunks:
                chunk_data = {
                    'id': chunk.metadata.content_id,
                    'title': chunk.metadata.title,
                    'content_type': chunk.metadata.content_type.value,
                    'complexity': chunk.metadata.complexity.value,
                    'target_audience': chunk.metadata.target_audience,
                    'prerequisites': chunk.metadata.prerequisites,
                    'learning_objectives': chunk.metadata.learning_objectives,
                    'estimated_read_time': chunk.metadata.estimated_read_time,
                    'quality_score': chunk.metadata.quality_score,
                    'content': chunk.content,
                    'tags': chunk.tags,
                    'cross_references': chunk.cross_references
                }
                level_data['chunks'].append(chunk_data)

            json_data['levels'][level] = level_data

        return json.dumps(json_data, indent=2, ensure_ascii=False)

    def _render_jupyter(self, organized_content: Dict, config: RenderingConfig) -> str:
        """Render content as Jupyter notebook."""
        notebook = {
            'cells': [],
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
                'language_info': {
                    'name': 'python',
                    'version': '3.8.0'
                },
                'title': 'Interactive Documentation'
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }

        # Add title cell
        notebook['cells'].append({
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['# Interactive Documentation Notebook', '', f'Generated: {datetime.now().isoformat()}']
        })

        # Add table of contents
        toc_cells = self._generate_jupyter_toc(organized_content)
        notebook['cells'].extend(toc_cells)

        # Add content for each level
        for level, chunks in organized_content.items():
            if not chunks:
                continue

            # Level header
            notebook['cells'].append({
                'cell_type': 'markdown',
                'metadata': {},
                'source': [f'# {level.title()} Level']
            })

            for chunk in chunks:
                # Chunk header
                notebook['cells'].append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [f'## {chunk.metadata.title}']
                })

                # Metadata
                if chunk.metadata.prerequisites or chunk.metadata.learning_objectives:
                    metadata_lines = []
                    if chunk.metadata.prerequisites:
                        metadata_lines.append(f"**Prerequisites:** {', '.join(chunk.metadata.prerequisites)}")
                    if chunk.metadata.learning_objectives:
                        metadata_lines.append(f"**Learning Objectives:**")
                        for obj in chunk.metadata.learning_objectives:
                            metadata_lines.append(f"- {obj}")

                    notebook['cells'].append({
                        'cell_type': 'markdown',
                        'metadata': {},
                        'source': metadata_lines
                    })

                # Content
                notebook['cells'].append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': chunk.content.split('\n')
                })

                # Code examples as executable cells
                for code_example in chunk.metadata.code_examples:
                    notebook['cells'].append({
                        'cell_type': 'code',
                        'execution_count': None,
                        'metadata': {},
                        'outputs': [],
                        'source': code_example.split('\n')
                    })

        return json.dumps(notebook, indent=2)

    def _render_sphinx(self, organized_content: Dict, config: RenderingConfig) -> str:
        """Render content as Sphinx reStructuredText."""
        rst_parts = [
            'Documentation',
            '=============',
            '',
            f'Generated: {datetime.now().isoformat()}',
            ''
        ]

        # Add toctree
        rst_parts.extend([
            '.. toctree::',
            '   :maxdepth: 3',
            '   :caption: Contents:',
            ''
        ])

        for level in organized_content.keys():
            rst_parts.append(f'   {level}')
        rst_parts.append('')

        # Generate sections for each level
        for level, chunks in organized_content.items():
            if not chunks:
                continue

            rst_parts.extend([
                f'{level.title()} Level',
                f'{"=" * (len(level) + 13)}',
                ''
            ])

            for chunk in chunks:
                # Convert title to RST format
                rst_parts.append(chunk.metadata.title)
                rst_parts.append('-' * len(chunk.metadata.title))
                rst_parts.append('')

                # Add metadata
                if chunk.metadata.target_audience:
                    rst_parts.append(f'.. note:: Audience: {", ".join(chunk.metadata.target_audience)}')
                    rst_parts.append('')

                # Convert content (basic conversion)
                content_rst = self._markdown_to_rst(chunk.content)
                rst_parts.append(content_rst)
                rst_parts.append('')

        return '\n'.join(rst_parts)

    def _markdown_to_rst(self, content: str) -> str:
        """Basic markdown to RST conversion."""
        # Convert headers
        lines = content.split('\n')
        rst_lines = []

        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                rst_lines.append('.. code-block:: python')
                rst_lines.append('')
                continue

            # Lists (basic)
            if re.match(r'^\s*[-*+]\s+', line):
                rst_lines.append(re.sub(r'^\s*[-*+]\s+', '- ', line))
                continue

            rst_lines.append(line)

        return '\n'.join(rst_lines)

    # Template methods
    def _get_markdown_template(self) -> str:
        return """
# {{ title }}

Generated: {{ generated_at }}

{% for level_name, level_content in levels.items() %}
{{ level_content }}

{% endfor %}
"""

    def _get_html_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>{{ css_styles }}</style>
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
        <p>Generated: {{ generated_at }}</p>
    </header>

    <nav class="table-of-contents">
        <h2>Table of Contents</h2>
        {{ toc|safe }}
    </nav>

    <main>
        {% for level_name, level_content in levels.items() %}
        {{ level_content|safe }}
        {% endfor %}
    </main>

    <footer>
        <p>Documentation generated with advanced multi-format renderer</p>
    </footer>
</body>
</html>
"""

    def _get_html_styles(self) -> str:
        return """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        header { border-bottom: 2px solid #e1e5e9; padding-bottom: 20px; margin-bottom: 30px; }
        .table-of-contents { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .content-chunk { margin-bottom: 40px; border: 1px solid #e1e5e9; border-radius: 8px; padding: 20px; }
        .chunk-metadata { background: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .chunk-metadata div { margin-bottom: 5px; }
        .content { margin-top: 20px; }
        pre { background: #f6f8fa; padding: 15px; border-radius: 6px; overflow-x: auto; }
        code { background: #f6f8fa; padding: 2px 4px; border-radius: 3px; }
        h1, h2, h3 { color: #24292e; }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        """

    def _generate_html_toc(self, organized_content: Dict) -> str:
        """Generate HTML table of contents."""
        toc_items = []

        for level, chunks in organized_content.items():
            if chunks:
                toc_items.append(f'<h3>{level.title()}</h3>')
                toc_items.append('<ul>')

                for chunk in chunks:
                    toc_items.append(f'<li><a href="#{chunk.metadata.content_id}">{chunk.metadata.title}</a></li>')

                toc_items.append('</ul>')

        return ''.join(toc_items)

    def _generate_jupyter_toc(self, organized_content: Dict) -> List[Dict]:
        """Generate Jupyter notebook table of contents cells."""
        toc_lines = ['## Table of Contents', '']

        for level, chunks in organized_content.items():
            if chunks:
                toc_lines.append(f'### {level.title()}')
                for chunk in chunks:
                    toc_lines.append(f'- [{chunk.metadata.title}](#{chunk.metadata.content_id})')
                toc_lines.append('')

        return [{
            'cell_type': 'markdown',
            'metadata': {},
            'source': toc_lines
        }]
```

**Use Cases for RAG**: Provide sophisticated multi-level documentation with intelligent content organization, adaptive rendering across multiple formats, and personalized learning paths for diverse user audiences with comprehensive metadata and relationship mapping.

### Content Classification
```python
def classify_content_complexity(chunk):
    """Classify content by complexity and audience."""
    content = chunk['content']
    chunk_type = chunk['type']

    # High complexity indicators
    high_complexity_signals = [
        'architecture', 'design pattern', 'scalability',
        'performance', 'security', 'integration'
    ]

    # Medium complexity indicators
    medium_complexity_signals = [
        'class', 'interface', 'api', 'module',
        'configuration', 'deployment'
    ]

    complexity_score = 0
    for signal in high_complexity_signals:
        if signal in content.lower():
            complexity_score += 3

    for signal in medium_complexity_signals:
        if signal in content.lower():
            complexity_score += 2

    # Base score from content type
    if chunk_type == 'class':
        complexity_score += 2
    elif chunk_type == 'function':
        complexity_score += 1

    # Determine level
    if complexity_score >= 6:
        return 'high'
    elif complexity_score >= 3:
        return 'medium'
    else:
        return 'low'
```

## Progressive Documentation Generation

### Executive Summary (High Level)
```python
def generate_executive_summary(repository_info):
    """Generate high-level overview for architects."""
    summary = "# Executive Summary\n\n"

    # System overview
    summary += "## System Overview\n\n"
    summary += f"This repository contains **{repository_info['file_count']}** files "
    summary += f"primarily written in **{repository_info['main_language']}**.\n\n"

    # Key components
    if repository_info.get('modules'):
        summary += "## Key Components\n\n"
        for module in repository_info['modules'][:5]:  # Top 5 modules
            summary += f"- **{module['name']}**: {module.get('description', 'Core module')}\n"
        summary += "\n"

    # Architecture patterns
    if repository_info.get('patterns'):
        summary += "## Architecture Patterns\n\n"
        for pattern in repository_info['patterns']:
            summary += f"- **{pattern}**: Used throughout the codebase\n"
        summary += "\n"

    # Technology stack
    summary += "## Technology Stack\n\n"
    summary += f"- **Primary Language**: {repository_info['main_language']}\n"
    summary += f"- **Frameworks**: {', '.join(repository_info.get('frameworks', []))}\n"
    summary += f"- **Databases**: {', '.join(repository_info.get('databases', []))}\n"

    return summary
```

### Technical Documentation (Detailed Level)
```python
def generate_technical_documentation(organized_content):
    """Generate detailed technical documentation."""
    docs = "# Technical Documentation\n\n"

    # Module documentation
    docs += "## Modules and Components\n\n"
    for chunk in organized_content['detailed']:
        if chunk['type'] == 'class':
            docs += f"### {chunk.get('name', 'Unknown Class')}\n\n"
            docs += f"{chunk.get('description', 'No description available')}\n\n"

            # Add methods if available
            if chunk.get('methods'):
                docs += "**Methods:**\n\n"
                for method in chunk['methods']:
                    docs += f"- `{method}`()\n"
                docs += "\n"

        elif chunk['type'] == 'api':
            docs += f"### {chunk.get('path', 'Unknown Endpoint')}\n\n"
            docs += f"**Method:** {chunk.get('method', 'GET')}\n\n"
            docs += f"{chunk.get('description', 'No description available')}\n\n"

    # API documentation
    api_chunks = [c for c in organized_content['detailed'] if c['type'] == 'api']
    if api_chunks:
        docs += "## API Reference\n\n"
        for api in api_chunks:
            docs += f"### {api['method']} {api['path']}\n\n"
            docs += f"{api.get('description', 'No description')}\n\n"

    return docs
```

### Implementation Guide (Implementation Level)
```python
def generate_implementation_guide(organized_content):
    """Generate hands-on implementation guide."""
    guide = "# Implementation Guide\n\n"

    # Function documentation
    functions = [c for c in organized_content['implementation'] if c['type'] == 'function']
    if functions:
        guide += "## Function Reference\n\n"
        for func in functions[:10]:  # Limit to top 10 functions
            guide += f"### {func.get('name', 'unknown_function')}\n\n"

            # Function signature
            params = func.get('params', [])
            param_list = ', '.join([p['name'] for p in params])
            guide += f"```python\n{func['name']}({param_list})\n```\n\n"

            # Description
            if func.get('description'):
                guide += f"{func['description']}\n\n"

            # Parameters
            if params:
                guide += "**Parameters:**\n\n"
                for param in params:
                    guide += f"- `{param['name']}`: {param.get('type', 'any')}\n"
                guide += "\n"

    # Code examples
    guide += "## Usage Examples\n\n"
    examples = generate_usage_examples(functions)
    for func_name, example in list(examples.items())[:5]:
        guide += f"### {func_name} Example\n\n"
        guide += f"```python\n{example}\n```\n\n"

    return guide
```

## Navigation and Cross-References

### Content Linking
```python
def generate_cross_references(organized_content):
    """Create cross-references between documentation levels."""
    references = {}

    # Link high-level to detailed
    for high_chunk in organized_content['high_level']:
        chunk_name = high_chunk.get('name', '').lower()
        related_detailed = []

        for detailed_chunk in organized_content['detailed']:
            detailed_content = detailed_chunk['content'].lower()
            if chunk_name and chunk_name in detailed_content:
                related_detailed.append({
                    'name': detailed_chunk.get('name', 'Unknown'),
                    'type': detailed_chunk['type'],
                    'file': detailed_chunk.get('file_path', '')
                })

        if related_detailed:
            references[chunk_name] = {
                'high_level': high_chunk,
                'detailed': related_detailed
            }

    return references
```

### Navigation Structure
```python
def generate_navigation_table(organized_content):
    """Generate navigation table for documentation."""
    nav = "# Navigation\n\n"

    # High-level sections
    nav += "## High-Level Overview\n\n"
    for chunk in organized_content['high_level']:
        name = chunk.get('name', 'Overview')
        nav += f"- [{name}](#{name.lower().replace(' ', '-')})\n"

    # Detailed sections
    nav += "\n## Detailed Documentation\n\n"
    for chunk in organized_content['detailed']:
        name = chunk.get('name', 'Details')
        chunk_type = chunk['type'].title()
        nav += f"- [{name}](#{name.lower().replace(' ', '-')}) ({chunk_type})\n"

    # Implementation sections
    nav += "\n## Implementation Details\n\n"
    for chunk in organized_content['implementation'][:20]:  # Limit to 20 items
        name = chunk.get('name', 'Implementation')
        nav += f"- [{name}](#{name.lower().replace(' ', '-')})\n"

    return nav
```

### Integration Pattern
```python
def create_multilevel_documentation(repository_chunks):
    """Create complete multi-level documentation."""
    # Organize content by level
    organized = organize_documentation_by_level(repository_chunks)

    # Generate each level
    repo_info = extract_repository_overview(repository_chunks)
    executive_summary = generate_executive_summary(repo_info)
    technical_docs = generate_technical_documentation(organized)
    implementation_guide = generate_implementation_guide(organized)
    navigation = generate_navigation_table(organized)

    # Combine into complete documentation
    complete_docs = f"{navigation}\n\n---\n\n{executive_summary}\n\n---\n\n"
    complete_docs += f"{technical_docs}\n\n---\n\n{implementation_guide}"

    # Add cross-references
    cross_refs = generate_cross_references(organized)
    if cross_refs:
        complete_docs += "\n\n---\n\n## Related Content\n\n"
        for concept, refs in cross_refs.items():
            complete_docs += f"### {concept.title()}\n\n"
            for ref in refs['detailed']:
                complete_docs += f"- {ref['name']} ({ref['type']})\n"

    return {
        'complete_documentation': complete_docs,
        'executive_summary': executive_summary,
        'technical_docs': technical_docs,
        'implementation_guide': implementation_guide,
        'navigation': navigation,
        'organization': organized
    }
```

**Use Cases for RAG**: Provide structured documentation for different user needs, enable progressive disclosure of information, and create hierarchical knowledge bases for complex repositories.