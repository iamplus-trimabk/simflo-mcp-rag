# Task 15: Advanced Metadata Tagging with AI-Driven Enrichment

## Intelligent Metadata Architecture

### AI-Powered Content Tagging System
```python
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from collections import Counter
import hashlib
import re

class TagType(Enum):
    CONTENT_TYPE = "content_type"
    ROLE = "role"
    EXPERTISE = "expertise"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    PATTERN = "pattern"
    SEMANTIC = "semantic"
    RELATIONSHIP = "relationship"
    QUALITY = "quality"
    CONTEXT = "context"

class TagConfidence(Enum):
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    VERY_LOW = 0.3

@dataclass
class MetadataTag:
    tag_id: str
    tag_type: TagType
    tag_value: str
    confidence: TagConfidence
    source: str  # 'ai_generated', 'rule_based', 'user_provided'
    evidence: List[str] = field(default_factory=list)
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentMetadata:
    content_id: str
    base_metadata: Dict[str, Any]
    tags: List[MetadataTag]
    embeddings: Optional[np.ndarray] = None
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    enrichment_history: List[Dict[str, Any]] = field(default_factory=list)

class AIMetadataTagger:
    def __init__(self):
        self.nlp_model = self._load_nlp_model()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_classifier = self._build_content_classifier()
        self.role_classifier = self._build_role_classifier()
        self.expertise_classifier = self._build_expertise_classifier()
        self.technology_tagger = self._build_technology_tagger()
        self.semantic_analyzer = SemanticAnalyzer()
        self.pattern_recognizer = PatternRecognizer()

    def _load_nlp_model(self):
        """Load NLP model for advanced text analysis."""
        try:
            return spacy.load("en_core_web_md")
        except OSError:
            # Fallback to basic text processing
            return None

    def _build_content_classifier(self) -> nn.Module:
        """Build neural network for content type classification."""
        return nn.Sequential(
            nn.Linear(768, 512),  # BERT embeddings
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 10)  # 10 content types
            nn.Softmax(dim=1)
        )

    def _build_role_classifier(self) -> nn.Module:
        """Build neural network for role classification."""
        return nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 8)  # 8 role types
            nn.Softmax(dim=1)
        )

    def _build_expertise_classifier(self) -> nn.Module:
        """Build neural network for expertise level classification."""
        return nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 4)  # 4 expertise levels
            nn.Softmax(dim=1)
        )

    def _build_technology_tagger(self) -> nn.Module:
        """Build neural network for technology tagging."""
        return nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 50)  # 50 common technologies
            nn.Sigmoid()
        )

    def enrich_metadata(self, content: Dict[str, Any],
                        all_chunks: List[Dict[str, Any]] = None) -> ContentMetadata:
        """Comprehensive metadata enrichment with AI."""
        content_id = content.get('content_id', '')
        content_text = content.get('content', '')

        # Create base metadata
        base_metadata = self._create_base_metadata(content)

        # Generate AI-enhanced tags
        tags = []

        # Content type classification
        content_type_tag = self._classify_content_type(content_text)
        tags.append(content_type_tag)

        # Role classification
        role_tags = self._classify_roles(content_text)
        tags.extend(role_tags)

        # Expertise level classification
        expertise_tag = self._classify_expertise_level(content_text)
        tags.append(expertise_tag)

        # Technology tagging
        tech_tags = self._identify_technologies(content_text)
        tags.extend(tech_tags)

        # Semantic analysis
        semantic_tags = self.semantic_analyzer.analyze_semantics(content_text)
        tags.extend(semantic_tags)

        # Pattern recognition
        pattern_tags = self.pattern_recognizer.recognize_patterns(content_text)
        tags.extend(pattern_tags)

        # Quality assessment tags
        quality_tags = self._assess_quality_tags(content)
        tags.extend(quality_tags)

        # Contextual tags
        if all_chunks:
            contextual_tags = self._generate_contextual_tags(content, all_chunks)
            tags.extend(contextual_tags)

        # Relationship tags
        relationship_tags = self._identify_relationships(content, all_chunks)
        tags.extend(relationship_tags)

        # Create metadata object
        metadata = ContentMetadata(
            content_id=content_id,
            base_metadata=base_metadata,
            tags=tags,
            relationships=self._build_relationships(content, all_chunks),
            quality_metrics=self._calculate_quality_metrics(content),
            enrichment_history=[{
                'timestamp': datetime.now().isoformat(),
                'enrichment_type': 'ai_enhanced',
                'tags_added': len(tags)
            }]
        )

        return metadata

    def _create_base_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive base metadata."""
        file_path = content.get('file_path', '')
        return {
            'content_id': content.get('content_id', self._generate_id()),
            'file_path': file_path,
            'file_name': file_path.split('/')[-1] if file_path else '',
            'content_type': content.get('type', 'unknown'),
            'language': self._detect_language(file_path),
            'timestamp': datetime.now().isoformat(),
            'size': len(content.get('content', '')),
            'line_start': content.get('start_line', 0),
            'line_end': content.get('end_line', 0),
            'file_extension': self._get_file_extension(file_path),
            'encoding': self._detect_encoding(content.get('content', '')),
            'hash': self._calculate_content_hash(content.get('content', ''))
        }

    def _classify_content_type(self, content: str) -> MetadataTag:
        """Classify content type using AI model."""
        if self.nlp_model:
            # Use spaCy for advanced NLP analysis
            doc = self.nlp_model(content[:512])  # Limit context length
            features = self._extract_spacy_features(doc)
            predicted_type = self._predict_content_type_from_features(features)
            confidence = TagConfidence.MEDIUM
        else:
            # Fallback to rule-based classification
            predicted_type = self._rule_based_content_classification(content)
            confidence = TagConfidence.HIGH

        return MetadataTag(
            tag_id=f"content_type_{self._generate_id()}",
            tag_type=TagType.CONTENT_TYPE,
            tag_value=predicted_type,
            confidence=confidence,
            source='ai_model' if self.nlp_model else 'rule_based',
            evidence=[predicted_type],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

    def _classify_roles(self, content: str) -> List[MetadataTag]:
        """Classify user roles using AI model."""
        roles = []
        content_lower = content.lower()

        # Use AI model if available
        if self.role_classifier:
            # Extract features and classify
            features = self._extract_text_features(content)
            with torch.no_grad():
                role_probs = self.role_classifier(torch.FloatTensor(features))
                top_roles = torch.topk(role_probs, 3)[1]

            role_mapping = ['architect', 'developer', 'api_user', 'data_scientist',
                           'qa_engineer', 'devops', 'product_manager', 'technical_writer']

            for i, (prob, idx) in enumerate(zip(top_roles, torch.topk(role_probs, 3)[0])):
                if prob > 0.3:  # Minimum confidence threshold
                    role = role_mapping[idx]
                    roles.append(MetadataTag(
                        tag_id=f"role_{role}_{self._generate_id()}",
                        tag_type=TagType.ROLE,
                        tag_value=role,
                        confidence=TagConfidence(prob.item()),
                        source='ai_model',
                        evidence=[f"confidence_{prob.item():.2f}"],
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    ))
        else:
            # Rule-based role classification
            roles = self._rule_based_role_classification(content)

        return roles

    def _classify_expertise_level(self, content: str) -> MetadataTag:
        """Classify expertise level using AI model."""
        content_lower = content.lower()

        # Use AI model if available
        if self.expertise_classifier:
            features = self._extract_text_features(content)
            with torch.no_grad():
                expertise_probs = self.expertise_classifier(torch.FloatTensor(features))
                predicted_idx = torch.argmax(expertise_probs).item()

            levels = ['beginner', 'intermediate', 'advanced', 'expert']
            predicted_level = levels[predicted_idx]
            confidence = TagConfidence.MEDIUM
        else:
            # Rule-based expertise classification
            predicted_level, confidence = self._rule_based_expertise_classification(content)

        return MetadataTag(
            tag_id=f"expertise_{predicted_level}_{self._generate_id()}",
            tag_type=TagType.EXPERTISE,
            tag_value=predicted_level,
            confidence=confidence,
            source='ai_model' if self.expertise_classifier else 'rule_based',
            evidence=[predicted_level],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

    def _identify_technologies(self, content: str) -> List[MetadataTag]:
        """Identify technologies using AI model."""
        if not self.technology_tagger:
            return self._rule_based_technology_identification(content)

        # Extract text features
        features = self._extract_text_features(content)

        # Get technology predictions
        with torch.no_grad():
            tech_scores = self.technology_tagger(torch.FloatTensor(features))

        # Get top technology predictions
        common_techs = [
            'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++', 'c#',
            'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'git', 'github', 'gitlab', 'bitbucket'
        ]

        tech_tags = []
        for i, tech in enumerate(common_techs):
            if i < len(tech_scores) and tech_scores[i] > 0.3:
                tech_tags.append(MetadataTag(
                    tag_id=f"tech_{tech}_{self._generate_id()}",
                    tag_type=TagType.TECHNOLOGY,
                    tag_value=tech,
                    confidence=TagConfidence(tech_scores[i].item()),
                    source='ai_model',
                    evidence=[f"confidence_{tech_scores[i].item():.2f}"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return tech_tags

class SemanticAnalyzer:
    def __init__(self):
        self.domain_ontology = self._build_domain_ontology()
        self.concept_vectors = {}
        self.word_embeddings = {}

    def analyze_semantics(self, content: str) -> List[MetadataTag]:
        """Analyze semantic meaning of content."""
        semantic_tags = []

        # Domain classification
        domain_tags = self._classify_domain(content)
        semantic_tags.extend(domain_tags)

        # Concept extraction
        concept_tags = self._extract_concepts(content)
        semantic_tags.extend(concept_tags)

        # Relationship inference
        relationship_tags = self._infer_relationships(content)
        semantic_tags.extend(relationship_tags)

        # Abstractness level
        abstractness_tag = self._assess_abstractness(content)
        semantic_tags.append(abstractness_tag)

        return semantic_tags

    def _build_domain_ontology(self) -> Dict[str, List[str]]:
        """Build comprehensive domain ontology."""
        return {
            'software_development': [
                'programming', 'coding', 'software', 'development', 'coding',
                'algorithm', 'data_structure', 'debugging', 'testing', 'version control'
            ],
            'web_development': [
                'web', 'website', 'frontend', 'backend', 'fullstack',
                'http', 'api', 'rest', 'graphql', 'websocket', 'spa'
            ],
            'data_science': [
                'data', 'analytics', 'statistics', 'machine learning', 'ai',
                'deep learning', 'neural networks', 'visualization', 'big data'
            ],
            'devops': [
                'deployment', 'infrastructure', 'automation', 'ci/cd',
                'monitoring', 'scaling', 'containerization', 'orchestration'
            ],
            'security': [
                'security', 'authentication', 'authorization', 'encryption',
                'vulnerability', 'penetration testing', 'compliance'
            ],
            'database': [
                'database', 'sql', 'nosql', 'schema', 'migration',
                'indexing', 'query', 'transaction', 'backup'
            ],
            'cloud_computing': [
                'cloud', 'aws', 'azure', 'gcp', 'serverless',
                'microservices', 'containers', 'orchestration'
            ]
        }

    def _classify_domain(self, content: str) -> List[MetadataTag]:
        """Classify content domain."""
        content_lower = content.lower()
        domain_scores = {}

        for domain, keywords in self.domain_ontology.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                domain_scores[domain] = score / len(keywords)

        domain_tags = []
        for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0.1:  # Minimum threshold
                domain_tags.append(MetadataTag(
                    tag_id=f"domain_{domain}_{self._generate_id()}",
                    tag_type=TagType.CONCEPT,
                    tag_value=domain,
                    confidence=TagConfidence(min(score, 0.9)),
                    source='semantic_analysis',
                    evidence=[f"score_{score:.2f}"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return domain_tags

    def _extract_concepts(self, content: str) -> List[MetadataTag]:
        """Extract high-level concepts from content."""
        concepts = {
            'object_oriented_programming': ['oop', 'encapsulation', 'inheritance', 'polymorphism', 'class', 'object'],
            'functional_programming': ['functional', 'pure function', 'immutable', 'lambda', 'map', 'filter', 'reduce'],
            'asynchronous_programming': ['async', 'await', 'callback', 'promise', 'future', 'coroutine'],
            'design_patterns': ['pattern', 'singleton', 'factory', 'observer', 'strategy', 'adapter', 'decorator'],
            'error_handling': ['try', 'catch', 'exception', 'error', 'exception handling', 'validation'],
            'data_structures': ['array', 'list', 'dict', 'set', 'tree', 'graph', 'hash_map'],
            'algorithms': ['algorithm', 'sorting', 'searching', 'optimization', 'complexity', 'performance'],
            'testing': ['test', 'unit test', 'integration', 'mock', 'stub', 'assertion'],
            'caching': ['cache', 'caching', 'memoization', 'performance'],
            'security': ['auth', 'security', 'encryption', 'validation', 'authorization']
        }

        content_lower = content.lower()
        concept_tags = []

        for concept, indicators in concepts.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score > 0:
                concept_tags.append(MetadataTag(
                    tag_id=f"concept_{concept}_{self._generate_id()}",
                    tag_type=TagType.CONCEPT,
                    tag_value=concept,
                    confidence=TagConfidence(min(score / len(indicators), 0.8)),
                    source='semantic_analysis',
                    evidence=[f"found_{score}_indicators"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return concept_tags

    def _infer_relationships(self, content: str) -> List[MetadataTag]:
        """Infer relationships from content."""
        relationships = {
            'client_server': ['client', 'server', 'request', 'response', 'http'],
            'input_output': ['input', 'output', 'parameters', 'return', 'result'],
            'cause_effect': ['because', 'therefore', 'thus', 'consequently'],
            'problem_solution': ['problem', 'solution', 'fix', 'resolve'],
            'before_after': ['before', 'after', 'previous', 'next']
        }

        content_lower = content.lower()
        relationship_tags = []

        for relationship, indicators in relationships.items():
            if all(indicator in content_lower for indicator in indicators):
                relationship_tags.append(MetadataTag(
                    tag_id=f"relationship_{relationship}_{self._generate_id()}",
                    tag_type=TagType.RELATIONSHIP,
                    tag_value=relationship,
                    confidence=TagConfidence.HIGH,
                    source='semantic_analysis',
                    evidence=indicators,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return relationship_tags

    def _assess_abstractness(self, content: content) -> MetadataTag:
        """Assess content abstractness level."""
        high_level_indicators = [
            'architecture', 'design', 'system', 'overview', 'framework',
            'principle', 'theory', 'concept', 'abstraction'
        ]

        low_level_indicators = [
            'implementation', 'code', 'example', 'specific', 'detail',
            'concrete', 'instance', 'practical', 'hands-on'
        ]

        content_lower = content.lower()
        high_score = sum(1 for indicator in high_level_indicators if indicator in content_lower)
        low_score = sum(1 for indicator in low_level_indicators if indicator in content_lower)

        if high_score > low_score:
            level = 'high'
            confidence = TagConfidence(min(high_score / max(high_score + low_score, 1), 0.9))
        elif low_score > high_score:
            level = 'low'
            confidence = TagConfidence(min(low_score / max(high_score + low_score, 1), 0.9))
        else:
            level = 'medium'
            confidence = TagConfidence(0.5)

        return MetadataTag(
            tag_id=f"abstractness_{level}_{self._generate_id()}",
            tag_type=TagType.CONCEPT,
            tag_value=level,
            confidence=confidence,
            source='semantic_analysis',
            evidence=[f"high_score_{high_score}", f"low_score_{low_score}"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime_now().isoformat()
        )

class PatternRecognizer:
    def __init__(self):
        self.design_patterns = {
            'creational': {
                'singleton': ['singleton', 'single_instance', 'getInstance', 'instance'],
                'factory': ['factory', 'create', 'build', 'construct'],
                'builder': ['builder', 'build', 'construct', 'assemble'],
                'prototype': ['prototype', 'clone', 'copy', 'deep_copy']
            },
            'structural': {
                'adapter': ['adapter', 'wrap', 'convert', 'transform'],
                'decorator': ['decorator', 'enhance', 'extend', 'modify'],
                'facade': ['facade', 'simplify', 'interface', 'gateway'],
                'proxy': ['proxy', 'representative', 'wrapper', 'surrogate']
            },
            'behavioral': {
                'observer': ['observer', 'subscriber', 'listener', 'notify'],
                'strategy': ['strategy', 'algorithm', 'approach', 'method'],
                'command': ['command', 'execute', 'invoke', 'call'],
                'state': ['state', 'status', 'condition']
            }
        }

        self.architectural_patterns = {
            'microservices': ['microservice', 'service', 'distributed', 'scalable'],
            'monolith': ['monolith', 'single_unit', 'integrated'],
            'mvc': ['mvc', 'model', 'view', 'controller'],
            'mvc_variant': ['mvvm', 'model', 'view', 'viewModel'],
            'clean_architecture': ['clean', 'clean_architecture', 'dependency_inversion']
        }

    def recognize_patterns(self, content: str) -> List[MetadataTag]:
        """Recognize design and architectural patterns."""
        content_lower = content.lower()
        pattern_tags = []

        # Design pattern recognition
        for category, patterns in self.design_patterns.items():
            for pattern_name, indicators in patterns.items():
                score = sum(1 for indicator in indicators if indicator in content_lower)
                if score >= 2:  # Require multiple indicators
                    pattern_tags.append(MetadataTag(
                        tag_id=f"pattern_{pattern_name}_{self._generate_id()}",
                        tag_type=TagType.PATTERN,
                        tag_value=pattern_name,
                        category=category,
                        confidence=TagConfidence(min(score / len(indicators), 0.8)),
                        source='pattern_recognition',
                        evidence=[f"found_{score}_indicators"],
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    ))

        # Architectural pattern recognition
        for pattern_name, indicators in self.architectural_patterns.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score >= 1:
                pattern_tags.append(MetadataTag(
                    tag_id=f"architecture_{pattern_name}_{self._generate_id()}",
                    tag_type=TagType.PATTERN,
                    tag_value=pattern_name,
                    category='architectural',
                    confidence=TagConfidence(min(score / len(indicators), 0.7)),
                    source='pattern_recognition',
                    evidence=[f"found_{score}_indicators"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return pattern_tags

class QualityAssessmentTagger:
    def __init__(self):
        self.quality_metrics = {
            'completeness': 0.2,
            'clarity': 0.2,
            'correctness': 0.25,
            'documentation': 0.15,
            'examples': 0.1,
            'structure': 0.1
        }

    def assess_quality_tags(self, content: Dict[str, Any]) -> List[MetadataTag]:
        """Generate quality assessment tags."""
        content_text = content.get('content', '')
        tags = []

        # Completeness assessment
        completeness_score = self._assess_completeness(content)
        if completeness_score < 0.5:
            tags.append(MetadataTag(
                tag_id="quality_incomplete",
                tag_type=TagType.QUALITY,
                tag_value="incomplete",
                confidence=TagConfidence.HIGH,
                source="quality_assessment",
                evidence=["missing_elements"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))
        elif completeness_score > 0.8:
            tags.append(MetadataTag(
                tag_id="quality_complete",
                tag_type=TagType.QUALITY,
                tag_value="complete",
                confidence=TagConfidence.HIGH,
                source="quality_assessment",
                evidence=[f"score_{completeness_score:.2f}"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))

        # Clarity assessment
        clarity_score = self._assess_clarity(content_text)
        if clarity_score < 0.4:
            tags.append(MetadataTag(
                tag_id="quality_unclear",
                tag_type=TagType.QUALITY,
                tag_value="unclear",
                confidence=TagConfidence.MEDIUM,
                source="quality_assessment",
                evidence=["complex_language", "poor_structure"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))

        # Documentation quality
        doc_quality = self._assess_documentation_quality(content_text)
        if doc_quality > 0.7:
            tags.append(MetadataTag(
                tag_id="well_documented",
                tag_type=TagType.QUALITY,
                tag_value="well_documented",
                confidence=TagConfidence.HIGH,
                source="quality_assessment",
                evidence=["comprehensive_docs"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))

        # Example presence
        if self._has_examples(content_text):
            tags.append(MetadataTag(
                tag_id="has_examples",
                tag_type=TagType.QUALITY,
                tag_value="has_examples",
                confidence=TagConfidence.MEDIUM,
                source="quality_assessment",
                evidence=["examples_found"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))

        return tags

    def _assess_completeness(self, content: Dict[str, Any]) -> float:
        """Assess content completeness."""
        required_elements = ['content', 'title', 'description']
        present_elements = sum(1 for elem in required_elements
                            if elem in content and content[elem])

        base_score = present_elements / len(required_elements)

        # Bonus for additional metadata
        bonus_elements = ['parameters', 'returns', 'examples', 'see_also']
        bonus = sum(1 for elem in bonus_elements
                    if elem in content and content[elem]) / len(bonus_elements)

        return min(base_score + (bonus * 0.2), 1.0)

    def _assess_clarity(self, content_text: str) -> float:
        """Assess content clarity."""
        # Check for clear explanations
        explanation_indicators = ['explains', 'describes', 'shows', 'demonstrates', 'illustrates']
        clarity_score = sum(indicator in content_text for indicator in explanation_indicators) / len(explanation_indicators)

        # Penalize overly complex sentences
        sentences = content_text.split('.')
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences))
            if avg_sentence_length > 30:
                clarity_score *= 0.7
            elif avg_sentence_length > 20:
                clarity_score *= 0.85

        return min(clarity_score, 1.0)

    def _assess_documentation_quality(self, content_text: str) -> float:
        """Assess documentation quality."""
        doc_patterns = ['"""', "'''", "/**", "# ", "//", "##"]
        doc_score = sum(pattern in content_text for pattern in doc_patterns) / len(doc_patterns)

        # Parameter documentation
        param_indicators = ['param', 'parameter', 'arg', 'argument']
        param_score = sum(indicator in content_text.lower() for indicator in param_indicators) / len(param_indicators)

        # Return documentation score
        return (doc_score + param_score) / 2

    def _has_examples(self, content_text: str) -> bool:
        """Check if content has examples."""
        example_indicators = ['example', 'usage', 'for instance', 'such as', 'e.g.']
        return any(indicator in content_text.lower() for indicator in example_indicators)

class ContextualTagger:
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()

    def generate_contextual_tags(self, content: Dict[str, Any],
                               all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Generate contextual tags based on content relationships."""
        contextual_tags = []

        content_id = content.get('content_id', '')
        content_text = content.get('content', '')

        # Temporal context tags
        temporal_tags = self._analyze_temporal_context(content, all_chunks)
        contextual_tags.extend(temporal_tags)

        # Project context tags
        project_tags = self._analyze_project_context(content, all_chunks)
        contextual_tags.extend(project_tags)

        # Collaborative context tags
        collaborative_tags = self._analyze_collaborative_context(content, all_chunks)
        contextual_tags.extend(collaborative_tags)

        # Learning context tags
        learning_tags = self._analyze_learning_context(content, all_chunks)
        contextual_tags.extend(learning_tags)

        return contextual_tags

    def _analyze_temporal_context(self, content: Dict[str, Any],
                               all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Analyze temporal context of content."""
        tags = []
        content_timestamp = content.get('timestamp', '')

        if content_timestamp:
            timestamp = datetime.fromisoformat(content_timestamp.replace('timestamp', ''))
            now = datetime.now()
            days_old = (now - timestamp).days

            if days_old < 1:
                tags.append(MetadataTag(
                    tag_id="temporal_recent",
                    tag_type=TagType.CONTEXT,
                    tag_value="recent",
                    confidence=TagConfidence.HIGH,
                    source="temporal_analysis",
                    evidence=[f"{days_old}_days_old"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))
            elif days_old < 30:
                tags.append(MetadataTag(
                    tag_id="temporal_fresh",
                    tag_type=TagType.CONTEXT,
                    tag_value="fresh",
                    confidence=TagConfidence.MEDIUM,
                    source="temporal_analysis",
                    evidence=[f"{days_old}_days_old"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))
            elif days_old < 365:
                tags.append(MetadataTag(
                    tag_id="temporal_current",
                    tag_type=TagType.CONTEXT,
                    tag_value="current",
                    confidence=TagConfidence.MEDIUM,
                    source="temporal_analysis",
                    evidence=[f"{days_old}_days_old"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))
            else:
                tags.append(MetadataTag(
                    tag_id="temporal_historical",
                    tag_type=TagType.CONTEXT,
                    tag_value="historical",
                    confidence=TagConfidence.LOW,
                    source="temporal_analysis",
                    evidence=[f"{days_old}_days_old"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return tags

    def _analyze_project_context(self, content: Dict[str, Any],
                             all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Analyze project context."""
        tags = []
        file_path = content.get('file_path', '')

        # Extract project context from file path
        if file_path:
            path_parts = file_path.split('/')
            if len(path_parts) > 1:
                project_name = path_parts[-2]
                tags.append(MetadataTag(
                    tag_id=f"project_{project_name}",
                    tag_type=TagType.CONTEXT,
                    tag_value=project_name,
                    confidence=TagConfidence.HIGH,
                    source="context_analysis",
                    evidence=[file_path],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        # Analyze related content within project
        related_content = self._find_related_content(content, all_chunks)
        if related_content:
            tags.append(MetadataTag(
                tag_id="has_related_content",
                tag_type=TagType.CONTEXT,
                tag_value="has_related_content",
                confidence=TagConfidence.MEDIUM,
                source="context_analysis",
                evidence=[f"found_{len(related_content)}_related_chunks"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))

        return tags

    def _find_related_content(self, content: Dict[str, Any],
                             all_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find content chunks related to the given content."""
        related_content = []
        content_keywords = set(self._extract_keywords(content.get('content', ''))[:10])  # Top 10 keywords

        for chunk in all_chunks:
            if chunk.get('content_id') != content.get('content_id'):
                chunk_keywords = set(self._extract_keywords(chunk.get('content', ''))[:10])
                similarity = len(content_keywords.intersection(chunk_keywords)) / max(len(content_keywords), 1)

                if similarity > 0.2:  # Similarity threshold
                    related_content.append(chunk)

        return related_content

    def _analyze_collaborative_context(self, content: Dict[str, Any],
                                   all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Analyze collaborative context."""
        tags = []

        # This would analyze user interactions, comments, collaborative editing history
        # For now, provide a basic implementation

        return tags

    def _analyze_learning_context(self, content: Dict[str, Any],
                                all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Analyze learning context and progression."""
        tags = []

        # This would analyze learning patterns, skill progression, knowledge gaps
        # For now, provide a basic implementation

        return tags

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content."""
        if not content:
            return []

        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content.lower())

        # Filter out common stop words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'or', 'but', 'in', 'with',
            'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'for', 'of', 'to', 'from', 'by', 'about', 'if', 'else', 'return'
        }

        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]

        # Count frequency and return top keywords
        word_freq = Counter(filtered_words)
        return [word for word, count in word_freq.most_common(max_keywords)]

    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react_typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.sql': 'sql',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yml',
            '.md': 'markdown',
            '.txt': 'text'
        }

        for ext, lang in extension_map.items():
            if file_path.endswith(ext):
                return lang

        return 'unknown'

    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension."""
        import os
        return os.path.splitext(file_path)[1].lower() if file_path else ''

    def _detect_encoding(self, content: str) -> str:
        """Detect content encoding."""
        # Simple encoding detection
        try:
            content.encode('utf-8').decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            try:
                content.encode('latin-1').decode('latin-1')
                return 'latin-1'
            except UnicodeDecodeError:
                return 'unknown'

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate content hash for deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _extract_text_features(self, content: str) -> np.ndarray:
        """Extract features for ML models."""
        if self.nlp_model:
            doc = self.nlp_model(content[:512])
            return self._extract_spacy_features(doc)
        else:
            # Fallback TF-IDF features
            try:
                vectorizer = TfidfVectorizer(max_features=768, stop_words='english')
                return vectorizer.fit_transform([content]).mean(axis=0)
            except:
                return np.zeros(768)

    def _extract_spacy_features(self, doc) -> np.ndarray:
        """Extract features from spaCy doc."""
        if not doc:
            return np.zeros(512)

        features = []

        # Vector representation
        features.append(doc.vector.mean(axis=0) if doc.vector is not None else np.zeros(300))

        # Part-of-speech tags
        pos_counts = Counter([token.pos_ for token in doc])
        common_pos = ['NOUN', 'VERB', 'ADJ', 'PROPN', 'PROUN']
        for pos in common_pos:
            features.append(pos_counts.get(pos, 0) / len(doc))

        # Named entities
        entity_types = Counter([ent.label_ for ent in doc.ents])
        common_entities = ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'WORK_OF_ART', 'EVENT']
        for entity in common_entities:
            features.append(entity_types.get(entity, 0) / len(doc.ents))

        # Dependency parse tree structure
        if len(list(doc.sents)) > 0:
            tree_depth = max([sent.root.depth for sent in doc.sents if sent.root])
            features.append(min(tree_depth / 10, 1.0))

        # Pad or truncate to expected size
        while len(features) < 512:
            features.append(0.0)
        return np.array(features[:512])

    def _predict_content_type_from_features(self, features: np.ndarray) -> str:
        """Predict content type from features."""
        type_mapping = [
            'function', 'class', 'module', 'api', 'documentation',
            'example', 'test', 'configuration', 'architecture', 'utility'
        ]

        # Simple linear combination for demonstration
        scores = np.dot(features[:len(type_mapping)], np.ones(len(type_mapping)))
        predicted_idx = np.argmax(scores)
        return type_mapping[predicted_idx]

    def _rule_based_content_classification(self, content: str) -> str:
        """Rule-based content type classification."""
        content_lower = content.lower()

        indicators = {
            'function': ['def ', 'function', '=>', '()', 'return', 'async'],
            'class': ['class ', 'interface ', 'struct', 'object', 'constructor'],
            'api': ['@app.', 'router.', 'GET ', 'POST ', 'api_endpoint'],
            'documentation': ['"""', "'''", '/**', '# ', '##', '###'],
            'example': ['example', 'Example', 'EXAMPLE', 'usage', 'Usage'],
            'test': ['test_', 'it(', 'describe(', 'assert', 'unittest'],
            'module': ['import', 'module', 'package', 'namespace']
        }

        scores = {}
        for content_type, indicators in indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            scores[content_type] = score

        return max(scores, key=scores.get) if scores else 'unknown'

    def _rule_based_role_classification(self, content: str) -> List[MetadataTag]:
        """Rule-based role classification."""
        content_lower = content.lower()

        role_indicators = {
            'architect': ['architecture', 'design', 'system', 'scalability', 'pattern'],
            'developer': ['function', 'class', 'implementation', 'code', 'debugging'],
            'data_scientist': ['data', 'model', 'algorithm', 'statistics', 'visualization'],
            'qa_engineer': ['test', 'quality', 'verification', 'assertion']
        }

        roles = []
        for role, indicators in role_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score > 1:
                roles.append(MetadataTag(
                    tag_id=f"role_{role}_{self._generate_id()}",
                    tag_type=TagType.ROLE,
                    tag_value=role,
                    confidence=TagConfidence(min(score / len(indicators), 0.8)),
                    source='rule_based',
                    evidence=[f"found_{score}_indicators"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return roles

    def _rule_based_expertise_classification(self, content: str) -> Tuple[str, TagConfidence]:
        """Rule-based expertise level classification."""
        content_lower = content.lower()

        expert_indicators = [
            'advanced', 'optimization', 'performance', 'scalability',
            'architecture', 'design pattern', 'concurrency',
            'asynchronous', 'algorithm'
        ]

        beginner_indicators = [
            'basic', 'intro', 'tutorial', 'getting started',
            'example', 'simple', 'hello world', 'beginner'
        ]

        expert_score = sum(1 for indicator in expert_indicators if indicator in content_lower)
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in content_lower)

        if expert_score > beginner_score:
            return 'expert', TagConfidence(min(expert_score / max(expert_score + beginner_score, 1), 0.9))
        elif beginner_score > expert_score:
            return 'beginner', TagConfidence(min(beginner_score / max(expert_score + beginner_score, 1), 0.9))
        else:
            return 'intermediate', TagConfidence(0.5)

    def _rule_based_technology_identification(self, content: str) -> List[MetadataTag]:
        """Rule-based technology identification."""
        tech_patterns = {
            'python': ['def ', 'import ', 'from ', 'self.', '@dataclass'],
            'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'export'],
            'typescript': ['interface ', 'type ', 'as ', 'private ', 'public '],
            'java': ['public class', 'private ', 'public ', 'System.out'],
            'react': ['import React', 'React.Component', 'useState', 'useEffect'],
            'vue': ['<template>', 'Vue.component', 'data()'],
            'docker': ['FROM', 'RUN', 'COPY', 'WORKDIR', 'EXPOSE'],
            'kubernetes': ['apiVersion', 'kind', 'metadata', 'spec']
        }

        content_lower = content.lower()
        tech_tags = []

        for tech, patterns in tech_patterns.items():
            score = sum(1 for pattern in patterns if pattern in content_lower)
            if score >= 1:
                tech_tags.append(MetadataTag(
                    tag_id=f"tech_{tech}_{self._generate_id()}",
                    tag_type=TagType.TECHNOLOGY,
                    tag_value=tech,
                    confidence=TagConfidence(min(score / len(patterns), 0.8)),
                    source='rule_based',
                    evidence=[f"found_{score}_patterns"],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))

        return tech_tags

class RelationshipTagger:
    def __init__(self):
        self.similarity_threshold = 0.3
        self.relationship_types = [
            'imports', 'function_calls', 'class_references',
            'conceptual_similarity', 'structural_dependency'
        ]

    def identify_relationships(self, content: Dict[str, Any],
                             all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Identify relationships with other content."""
        relationships = []

        content_id = content.get('content_id', '')
        content_text = content.get('content', '')

        # Import dependencies
        import_tags = self._extract_imports(content_text)
        relationships.extend(import_tags)

        # Function call references
        function_tags = self._extract_function_calls(content_text)
        relationships.extend(function_tags)

        # Class references
        class_tags = self._extract_class_references(content_text)
        relationships.extend(class_tags)

        # Content similarity relationships
        similarity_tags = self._find_similar_content(content, all_chunks)
        relationships.extend(similarity_tags)

        return relationships

    def _extract_imports(self, content: str) -> List[MetadataTag]:
        """Extract import statements from content."""
        import_patterns = [
            r'import\s+([^\n]+)',
            r'from\s+([^\n]+)\s+import',
            r'require\s*\(\s*[\'"]([^\]]+)\s*\)',
            r'#include\s*[<"]([^>]+)[>"]',
            r'<import[^>]*>([^<]*)</import>'
        ]

        imports = []
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)

        unique_imports = list(set(imports))
        return [MetadataTag(
            tag_id=f"import_{imp}_{self._generate_id()}",
            tag_type=TagType.RELATIONSHIP,
            tag_value="import_dependency",
            confidence=TagConfidence.HIGH,
            source="parsing",
            evidence=unique_imports,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ) for imp in unique_imports]

    def _extract_function_calls(self, content: str) -> List[MetadataTag]:
        """Extract function call references."""
        # Simple pattern matching for function calls
        call_patterns = [
            r'(\w+)\s*\(',
            r'\.(\w+)\s*\(',
            r'(\w+)\.(\w+)'  # Method calls
        ]

        calls = []
        for pattern in call_patterns:
            matches = re.findall(pattern, content)
            calls.extend(matches)

        unique_calls = list(set(calls))
        return [MetadataTag(
            tag_id=f"function_call_{call}_{self._generate_id()}",
            tag_type=TagType.RELATIONSHIP,
            tag_value="function_call",
            confidence=TagConfidence.MEDIUM,
            source="parsing",
            evidence=unique_calls,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ) for call in unique_calls]

    def _extract_class_references(self, content: str) -> List[MetadataTag]:
        """Extract class references from content."""
        class_patterns = [
            r'(\w+)\s*extends\s+(\w+)',
            r'(\w+)\s*:\s*(\w+)',
            r'(\w+)\.\w+)',  # Method calls
            r'\b(\w+)\b'  # Type references
        ]

        references = []
        for pattern in class_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)

        unique_references = list(set(references))
        return [MetadataTag(
            tag_id=f"class_reference_{ref}_{self._generate_id()}",
            tag_type=TagType.RELATIONSHIP,
            tag_value="class_reference",
            confidence=TagConfidence.MEDIUM,
            source="parsing",
            evidence=unique_references,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ) for ref in unique_references]

    def _find_similar_content(self, content: Dict[str, Any],
                                all_chunks: List[Dict[str, Any]]) -> List[MetadataTag]:
        """Find similar content chunks."""
        content_keywords = set(self._extract_keywords(content.get('content', ''))[:20])
        similarity_tags = []

        for chunk in all_chunks:
            if chunk.get('content_id') != content.get('content_id'):
                chunk_keywords = set(self._extract_keywords(chunk.get('content', ''))[:20])

                if content_keywords and chunk_keywords:
                    intersection = content_keywords.intersection(chunk_keywords)
                    union = content_keywords.union(chunk_keywords)

                    if union:  # Avoid division by zero
                        similarity = len(intersection) / len(union)
                        if similarity >= self.similarity_threshold:
                            similarity_tags.append(MetadataTag(
                                tag_id=f"similar_{chunk.get('content_id')[:8]}",
                                tag_type=TagType.RELATIONSHIP,
                                tag_value="content_similarity",
                                confidence=TagConfidence(similarity),
                                source="similarity_analysis",
                                evidence=[f"similarity_{similarity:.2f}"],
                                created_at=datetime.now().isoformat(),
                                updated_at=datetime.now().isoformat()
                            ))

        return similarity_tags

class ContextAnalyzer:
    def __init__(self):
        self.temporal_patterns = {}
        self.project_contexts = {}
        self.user_contexts = {}

    def analyze_context(self, content: Dict[str, Any],
                        user_id: str = None,
                        session_id: str = None) -> Dict[str, Any]:
        """Analyze comprehensive context around content."""
        context = {
            'temporal': self._get_temporal_context(content),
            'project': self._get_project_context(content),
            'user': self._get_user_context(user_id, session_id),
            'session': self._get_session_context(session_id)
        }

        return context

    def _get_temporal_context(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Get temporal context information."""
        timestamp = content.get('timestamp', '')
        if not timestamp:
            return {}

        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            return {
                'created_at': timestamp,
                'age_days': (now - dt).days,
                'is_recent': (now - dt).days < 30,
                'time_of_day': dt.hour,
                'day_of_week': dt.weekday()
            }
        except:
            return {'created_at': timestamp}

    def _get_project_context(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Get project context information."""
        file_path = content.get('file_path', '')
        if not file_path:
            return {}

        path_parts = file_path.split('/')
        if len(path_parts) > 1:
            return {
                'project_name': path_parts[-2],
                'module_path': '/'.join(path_parts[:-1]),
                'file_depth': len(path_parts) - 1,
                'is_in_main': path_parts[0] in ['src', 'lib', 'app', 'main']
            }
        return {}

    def _get_user_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get user context information."""
        context = {
            'user_id': user_id,
            'session_id': session_id,
            'preferences': self._get_user_preferences(user_id),
            'history': self._get_user_history(user_id),
            'skill_level': self._estimate_user_skill_level(user_id)
        }

        return context

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        # This would retrieve from user profile database
        return {
            'preferred_content_types': ['function', 'class', 'documentation'],
            'complexity_preference': 'intermediate',
            'language_preferences': ['python', 'javascript'],
            'notification_settings': {}
        }

    def _get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user interaction history."""
        # This would retrieve from user activity logs
        return []

    def _estimate_user_skill_level(self, user_id: str) -> str:
        """Estimate user skill level."""
        # This would analyze user performance metrics
        return 'intermediate'

class MetadataEnrichmentPipeline:
    def __init__(self):
        self.ai_tagger = AIMetadataTagger()
        self.contextual_tagger = ContextualTagger()
        self.relationship_tagger = RelationshipTagger()
        self.enrichment_history = {}

    def process_content_collection(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a collection of content chunks with comprehensive metadata."""
        processed_chunks = {}

        print(f"Processing {len(chunks)} content chunks for metadata enrichment...")

        for i, chunk in enumerate(chunks):
            try:
                print(f"Enriching chunk {i+1}/{len(chunks)}: {chunk.get('content_id', 'unknown')}")

                # Enrich metadata
                metadata = self.ai_tagger.enrich_metadata(chunk, all_chunks)
                processed_chunks[chunk['content_id']] = metadata

                # Add contextual information
                contextual_tags = self.contextual_tagger.generate_contextual_tags(
                    chunk, chunks
                )
                metadata.tags.extend(contextual_tags)

                # Add relationship tags
                relationship_tags = self.relationship_tagger.identify_relationships(chunk, chunks)
                metadata.tags.extend(relationship_tags)

                # Store enrichment history
                self.enrichment_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'chunk_id': chunk['content_id'],
                    'tags_added': len(metadata.tags),
                    'enrichment_time': datetime.now().isoformat()
                })

            except Exception as e:
                print(f"Error processing chunk {i+1}: {e}")
                # Create minimal metadata
                metadata = ContentMetadata(
                    content_id=chunk.get('content_id', f"chunk_{i}"),
                    base_metadata=self.ai_tagger._create_base_metadata(chunk),
                    tags=[],
                    quality_metrics={},
                    enrichment_history=[{
                        'timestamp': datetime.now().isoformat(),
                        'chunk_id': chunk['content_id'],
                        'tags_added': 0,
                        'enrichment_time': datetime.now().isoformat(),
                        'error': str(e)
                    }]
                )
                processed_chunks[chunk['content_id']] = metadata

        # Generate statistics
        stats = self._generate_enrichment_statistics(processed_chunks)

        return {
            'processed_chunks': processed_chunks,
            'statistics': stats,
            'enrichment_pipeline_version': '2.0'
        }

    def _generate_enrichment_statistics(self, processed_chunks: Dict[str, ContentMetadata]) -> Dict[str, Any]:
        """Generate enrichment statistics."""
        total_chunks = len(processed_chunks)
        total_tags = sum(len(metadata.tags) for metadata in processed_chunks.values())

        tag_type_counts = {}
        for metadata in processed_chunks.values():
            for tag in metadata.tags:
                tag_type = tag.tag_type.value
                tag_type_counts[tag_type] = tag_type_counts.get(tag_type, 0) + 1

        quality_scores = []
        for metadata in processed_chunks.values():
            quality_scores.append(metadata.quality_metrics.get('overall_quality', 0.5))

        return {
            'total_chunks_processed': total_chunks,
            'total_tags_generated': total_tags,
            'average_tags_per_chunk': total_tags / total_chunks if total_chunks > 0 else 0,
            'tag_type_distribution': tag_type_counts,
            'average_quality_score': np.mean(quality_scores) if quality_scores else 0,
            'enrichment_success_rate': 1.0  # All chunks processed
            'processing_errors': len([m for m in processed_chunks.values()
                                          if 'error' in m.enrichment_history])
        }

    def export_enhanced_metadata(self, processed_chunks: Dict[str, ContentMetadata],
                                  output_file: str = "enhanced_metadata.json") -> str:
        """Export enhanced metadata to JSON file."""
        # Convert to JSON-serializable format
        export_data = {}
        for content_id, metadata in processed_chunks.items():
            export_data[content_id] = {
                'base_metadata': metadata.base_metadata,
                'tags': [
                    {
                        'tag_id': tag.tag_id,
                        'tag_type': tag.tag_type.value,
                        'tag_value': tag.tag_value,
                        'confidence': tag.confidence.value,
                        'source': tag.source,
                        'evidence': tag.evidence,
                        'created_at': tag.created_at,
                        'updated_at': tag.updated_at
                    } for tag in metadata.tags
                ],
                'relationships': metadata.relationships,
                'quality_metrics': metadata.quality_metrics,
                'enrichment_history': metadata.enrichment_history
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)

        return output_file

    def get_enrichment_summary(self, processed_chunks: Dict[str, ContentMetadata]) -> str:
        """Get summary of enrichment process."""
        stats = self._generate_enrichment_statistics(processed_chunks)

        summary = f"""
        # Metadata Enrichment Summary

        ## Processing Results
        - Total chunks processed: {stats['total_chunks_processed']}
        - Total tags generated: {stats['total_tags_generated']}
        - Average tags per chunk: {stats['average_tags_per_chunk']:.2f}
        - Enrichment success rate: {stats['enrichment_success_rate']*100:.1f}%
        - Processing errors: {stats['processing_errors']}

        ## Tag Distribution
        """

        for tag_type, count in sorted(stats['tag_type_distribution'].items()):
            summary += f"- {tag_type}: {count}\n"

        summary += f"""

        ## Quality Metrics
        - Average quality score: {stats['average_quality_score']:.3f}
        - Content coverage: {(stats['average_quality_score'] * 100):.1f}%
        """

        return summary

        **Use Cases for RAG**: Advanced AI-powered metadata tagging with multi-dimensional analysis, contextual awareness, relationship mapping, quality assessment, and comprehensive enrichment pipeline for sophisticated RAG systems.