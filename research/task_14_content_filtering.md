# Task 14: Advanced Content Filtering with AI-Driven Personalization

## Intelligent Multi-Dimensional Filtering

### AI-Powered Content Classification System
```python
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    API = "api"
    DOCUMENTATION = "documentation"
    EXAMPLE = "example"
    TEST = "test"
    CONFIGURATION = "configuration"
    DIAGRAM = "diagram"
    ARCHITECTURE = "architecture"

class ComplexityLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

@dataclass
class ContentFeatures:
    content_id: str
    text_features: np.ndarray
    structural_features: np.ndarray
    semantic_features: np.ndarray
    quality_score: float
    relevance_score: float
    freshness_score: float
    popularity_score: float
    user_feedback_score: float
    complexity_level: ComplexityLevel
    content_type: ContentType
    tags: List[str]
    metadata: Dict[str, Any]

class AIContentClassifier:
    def __init__(self):
        self.text_encoder = self._build_text_encoder()
        self.structural_analyzer = StructuralAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.quality_assessor = ContentQualityAssessor()
        self.relevance_predictor = RelevancePredictor()

    def _build_text_encoder(self) -> nn.Module:
        """Build neural network for text encoding."""
        return nn.Sequential(
            nn.Linear(768, 512),  # BERT embeddings
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),  # Final text embedding
            nn.Tanh()
        )

    def extract_comprehensive_features(self, content: Dict[str, Any]) -> ContentFeatures:
        """Extract comprehensive features from content."""

        # Text-based features
        text_features = self._extract_text_features(content)

        # Structural features
        structural_features = self.structural_analyzer.analyze_structure(content)

        # Semantic features
        semantic_features = self.semantic_analyzer.analyze_semantics(content)

        # Quality assessment
        quality_score = self.quality_assessor.assess_quality(content)

        # Relevance prediction
        relevance_score = self.relevance_predictor.predict_relevance(content)

        # Freshness score
        freshness_score = self._calculate_freshness_score(content)

        # Popularity score
        popularity_score = self._calculate_popularity_score(content)

        # User feedback score
        user_feedback_score = self._calculate_user_feedback_score(content)

        # Complexity analysis
        complexity_level = self._determine_complexity_level(content)

        # Content type classification
        content_type = self._classify_content_type(content)

        # Tag extraction
        tags = self._extract_tags(content)

        return ContentFeatures(
            content_id=content.get('content_id', ''),
            text_features=text_features,
            structural_features=structural_features,
            semantic_features=semantic_features,
            quality_score=quality_score,
            relevance_score=relevance_score,
            freshness_score=freshness_score,
            popularity_score=popularity_score,
            user_feedback_score=user_feedback_score,
            complexity_level=complexity_level,
            content_type=content_type,
            tags=tags,
            metadata=content.get('metadata', {})
        )

class StructuralAnalyzer:
    def __init__(self):
        self.code_patterns = {
            'function_def': ['def ', 'function', '=>', '()'],
            'class_def': ['class ', 'interface ', 'type '],
            'module_import': ['import', 'require', 'include'],
            'api_endpoint': ['@app.', 'router.', 'GET ', 'POST '],
            'test_case': ['test_', 'it(', 'describe('],
            'documentation': ['"""', "'''", '/**', '*']
        }

    def analyze_structure(self, content: Dict[str, Any]) -> np.ndarray:
        """Analyze structural features of content."""
        content_text = content.get('content', '')

        features = []

        # Code structure indicators
        for pattern_type, indicators in self.code_patterns.items():
            count = sum(indicator in content_text for indicator in indicators)
            features.append(count / len(content_text.split()))  # Normalize by content length

        # Nesting depth
        max_depth = self._calculate_nesting_depth(content_text)
        features.append(max_depth / 10)  # Normalize

        # Line count
        line_count = len(content_text.split('\n'))
        features.append(min(line_count / 100, 1.0))  # Normalize and cap

        # Code density (code vs comments)
        code_density = self._calculate_code_density(content_text)
        features.append(code_density)

        # Identifier density
        identifier_density = self._calculate_identifier_density(content_text)
        features.append(identifier_density)

        return np.array(features)

    def _calculate_nesting_depth(self, content: str) -> int:
        """Calculate maximum nesting depth."""
        lines = content.split('\n')
        max_depth = 0
        current_depth = 0

        for line in lines:
            stripped = line.strip()
            if any(indicator in stripped for indicator in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:']):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped == '' or stripped.startswith('#') or stripped.startswith('//'):
                pass  # Ignore empty lines and comments
            elif stripped and not any(indicator in stripped for indicator in [' ', '\t']):
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _calculate_code_density(self, content: str) -> float:
        """Calculate ratio of code to comments."""
        lines = content.split('\n')
        code_lines = 0
        comment_lines = 0

        for line in lines:
            stripped = line.strip()
            if stripped and not any(stripped.startswith(prefix) for prefix in ['#', '//', '/*', '*', '/**']):
                code_lines += 1
            elif any(stripped.startswith(prefix) for prefix in ['#', '//', '/*', '*', '/**']):
                comment_lines += 1

        total_lines = code_lines + comment_lines
        return code_lines / total_lines if total_lines > 0 else 0

    def _calculate_identifier_density(self, content: str) -> float:
        """Calculate density of identifiers (variables, functions, classes)."""
        import re

        # Find identifiers
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        words = content.split()

        return len(identifiers) / len(words) if words else 0

class SemanticAnalyzer:
    def __init__(self):
        self.domain_keywords = {
            'database': ['sql', 'query', 'table', 'database', 'index', 'schema'],
            'web': ['http', 'api', 'request', 'response', 'server', 'client'],
            'ml': ['model', 'training', 'prediction', 'algorithm', 'neural', 'deep'],
            'security': ['authentication', 'authorization', 'encryption', 'security', 'token'],
            'performance': ['optimization', 'performance', 'cache', 'memory', 'speed'],
            'testing': ['test', 'assert', 'mock', 'unit', 'integration']
        }

        self.concept_patterns = {
            'async_programming': ['async', 'await', 'promise', 'callback', 'future'],
            'error_handling': ['try', 'catch', 'except', 'error', 'exception'],
            'data_structures': ['list', 'array', 'dictionary', 'map', 'set', 'tree'],
            'design_patterns': ['singleton', 'factory', 'observer', 'strategy', 'adapter']
        }

    def analyze_semantics(self, content: Dict[str, Any]) -> np.ndarray:
        """Analyze semantic features of content."""
        content_text = content.get('content', '').lower()

        features = []

        # Domain relevance scores
        for domain, keywords in self.domain_keywords.items():
            relevance = sum(keyword in content_text for keyword in keywords) / len(keywords)
            features.append(relevance)

        # Concept presence
        for concept, patterns in self.concept_patterns.items():
            presence = sum(pattern in content_text for pattern in patterns) / len(patterns)
            features.append(presence)

        # Technical complexity indicators
        technical_terms = ['algorithm', 'optimization', 'architecture', 'scalability', 'performance']
        tech_complexity = sum(term in content_text for term in technical_terms) / len(technical_terms)
        features.append(tech_complexity)

        # Practicality indicators
        practical_terms = ['example', 'usage', 'implementation', 'code', 'tutorial']
        practicality = sum(term in content_text for term in practical_terms) / len(practical_terms)
        features.append(practicality)

        return np.array(features)

class ContentQualityAssessor:
    def __init__(self):
        self.quality_weights = {
            'completeness': 0.2,
            'clarity': 0.2,
            'correctness': 0.25,
            'documentation': 0.15,
            'examples': 0.1,
            'structure': 0.1
        }

    def assess_quality(self, content: Dict[str, Any]) -> float:
        """Assess content quality using multiple criteria."""
        content_text = content.get('content', '')

        scores = {}

        # Completeness score
        scores['completeness'] = self._assess_completeness(content)

        # Clarity score
        scores['clarity'] = self._assess_clarity(content_text)

        # Correctness indicators (proxy measures)
        scores['correctness'] = self._assess_correctness_indicators(content)

        # Documentation quality
        scores['documentation'] = self._assess_documentation_quality(content_text)

        # Example presence
        scores['examples'] = self._assess_example_quality(content)

        # Structural quality
        scores['structure'] = self._assess_structure_quality(content_text)

        # Calculate weighted score
        total_score = sum(scores[criteria] * weight
                          for criteria, weight in self.quality_weights.items())

        return min(total_score, 1.0)

    def _assess_completeness(self, content: Dict[str, Any]) -> float:
        """Assess content completeness."""
        required_elements = ['content', 'title', 'description']
        present_elements = sum(1 for elem in required_elements if elem in content and content[elem])

        base_score = present_elements / len(required_elements)

        # Bonus for additional metadata
        bonus_elements = ['parameters', 'returns', 'examples', 'see_also']
        bonus = sum(1 for elem in bonus_elements if elem in content and content[elem]) / len(bonus_elements)

        return base_score + (bonus * 0.2)

    def _assess_clarity(self, content_text: str) -> float:
        """Assess content clarity."""
        # Check for clear explanations
        explanation_indicators = ['explains', 'describes', 'shows', 'demonstrates', 'illustrates']
        clarity_score = sum(indicator in content_text for indicator in explanation_indicators) / len(explanation_indicators)

        # Penalize overly complex sentences
        sentences = content_text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        if avg_sentence_length > 30:
            clarity_score *= 0.7
        elif avg_sentence_length > 20:
            clarity_score *= 0.85

        return min(clarity_score, 1.0)

    def _assess_correctness_indicators(self, content: Dict[str, Any]) -> float:
        """Assess indicators of code correctness."""
        content_text = content.get('content', '')

        # Look for error handling
        error_handling = ['try:', 'except', 'catch', 'error handling', 'validation']
        error_score = sum(pattern in content_text for pattern in error_handling) / len(error_handling)

        # Look for testing mentions
        testing = ['test', 'unit test', 'integration', 'verify', 'validate']
        test_score = sum(pattern in content_text for pattern in testing) / len(testing)

        # Look for best practices
        best_practices = ['best practice', 'recommended', 'optimized', 'efficient']
        practice_score = sum(pattern in content_text for pattern in best_practices) / len(best_practices)

        return (error_score + test_score + practice_score) / 3

    def _assess_documentation_quality(self, content_text: str) -> float:
        """Assess documentation quality."""
        doc_patterns = ['"""', "'''", "/**", "# ", "//", "##"]
        doc_score = sum(pattern in content_text for pattern in doc_patterns) / len(doc_patterns)

        # Check for parameter documentation
        param_indicators = ['param', 'parameter', 'arg', 'argument']
        param_score = sum(indicator in content_text.lower() for indicator in param_indicators) / len(param_indicators)

        # Check for return documentation
        return_indicators = ['return', 'returns', 'output']
        return_score = sum(indicator in content_text.lower() for indicator in return_indicators) / len(return_indicators)

        return (doc_score + param_score + return_score) / 3

    def _assess_example_quality(self, content: Dict[str, Any]) -> float:
        """Assess example quality."""
        content_text = content.get('content', '')

        # Look for example indicators
        example_indicators = ['example', 'usage', 'for instance', 'such as', 'e.g.']
        example_score = sum(indicator in content_text.lower() for indicator in example_indicators) / len(example_indicators)

        # Check for code blocks
        code_indicators = ['```', 'def ', 'function', 'class ']
        code_score = sum(indicator in content_text for indicator in code_indicators) / len(code_indicators)

        return (example_score + code_score) / 2

    def _assess_structure_quality(self, content_text: str) -> float:
        """Assess structural quality."""
        lines = content_text.split('\n')

        # Check for logical organization
        section_indicators = ['##', '###', '---', 'section', 'part']
        structure_score = sum(any(indicator in line.lower() for indicator in section_indicators)
                           for line in lines) / len(lines)

        # Check for consistent formatting
        consistent_indentation = self._check_indentation_consistency(lines)

        return (structure_score + consistent_indentation) / 2

    def _check_indentation_consistency(self, lines: List[str]) -> float:
        """Check indentation consistency."""
        indent_counts = []

        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_counts.append(indent)

        if not indent_counts:
            return 1.0

        # Check if indentation follows a pattern
        unique_indents = sorted(set(indent_counts))

        # Award points for consistent indentation levels
        if len(unique_indents) <= 3:
            return 1.0
        elif len(unique_indents) <= 5:
            return 0.7
        else:
            return 0.4

class RelevancePredictor:
    def __init__(self):
        self.tfidf_vectorizer = None
        self.is_trained = False

    def train(self, training_data: List[Dict[str, Any]]):
        """Train the relevance predictor."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        texts = [item['content'] for item in training_data]
        labels = [item['relevance_label'] for item in training_data]

        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = self.tfidf_vectorizer.fit_transform(texts)

        self.classifier = LogisticRegression(random_state=42)
        self.classifier.fit(X, labels)

        self.is_trained = True

    def predict_relevance(self, content: Dict[str, Any]) -> float:
        """Predict content relevance."""
        if not self.is_trained:
            return 0.5  # Default relevance

        text = content.get('content', '')
        if not text:
            return 0.5

        X = self.tfidf_vectorizer.transform([text])
        probability = self.classifier.predict_proba(X)[0]

        # Return probability of being relevant
        relevant_idx = list(self.classifier.classes_).index(1) if 1 in self.classifier.classes_ else 0
        return probability[relevant_idx]
```

## Adaptive Learning Filter

### Reinforcement Learning for Content Filtering
```python
import gymnasium as gym
from gymnasium import spaces
import random

class AdaptiveContentFilteringEnv(gym.Env):
    def __init__(self, user_profile: Dict[str, Any], content_database: List[Dict[str, Any]]):
        super().__init__()

        self.user_profile = user_profile
        self.content_database = content_database
        self.current_step = 0
        self.max_steps = 50

        # Action space: filter configuration
        self.action_space = spaces.Dict({
            'quality_threshold': spaces.Box(0.0, 1.0, shape=(1,)),
            'complexity_preference': spaces.Discrete(4),  # 4 complexity levels
            'content_type_weights': spaces.Box(0.0, 1.0, shape=(10,)),  # 10 content types
            'freshness_weight': spaces.Box(0.0, 1.0, shape=(1,)),
            'popularity_weight': spaces.Box(0.0, 1.0, shape=(1,))
        })

        # Observation space: user feedback and metrics
        self.observation_space = spaces.Dict({
            'user_satisfaction': spaces.Box(0.0, 1.0, shape=(1,)),
            'click_through_rate': spaces.Box(0.0, 1.0, shape=(1,)),
            'session_duration': spaces.Box(0.0, 300.0, shape=(1,)),
            'feedback_score': spaces.Box(0.0, 5.0, shape=(1,)),
            'content_diversity': spaces.Box(0.0, 1.0, shape=(1,))
        })

        self.reset()

    def reset(self, seed=None, options=None):
        """Reset environment for new filtering session."""
        super().reset(seed=seed)
        self.current_step = 0
        self.filtering_history = []
        self.user_feedback = []

        return self._get_observation(), {}

    def step(self, action):
        """Execute filtering action and return results."""
        self.current_step += 1

        # Apply filtering action
        filtered_content = self._apply_filtering_action(action)

        # Simulate user interaction
        user_metrics = self._simulate_user_interaction(filtered_content)

        # Calculate reward
        reward = self._calculate_reward(user_metrics, action)

        # Store interaction for learning
        self.filtering_history.append({
            'action': action,
            'filtered_content': filtered_content,
            'user_metrics': user_metrics
        })

        done = self.current_step >= self.max_steps

        observation = {
            'user_satisfaction': np.array([user_metrics['satisfaction']]),
            'click_through_rate': np.array([user_metrics['ctr']]),
            'session_duration': np.array([user_metrics['session_duration']]),
            'feedback_score': np.array([user_metrics['feedback']]),
            'content_diversity': np.array([user_metrics['diversity']])
        }

        return observation, reward, done, False, {}

    def _apply_filtering_action(self, action: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
        """Apply filtering action to content database."""
        quality_threshold = float(action['quality_threshold'][0])
        complexity_preference = int(action['complexity_preference'][0])
        content_type_weights = action['content_type_weights']
        freshness_weight = float(action['freshness_weight'][0])
        popularity_weight = float(action['popularity_weight'][0])

        filtered = []

        for content in self.content_database:
            score = 0.0

            # Quality filter
            if content.get('quality_score', 0) < quality_threshold:
                continue
            score += content.get('quality_score', 0) * 0.3

            # Complexity filter
            content_complexity = content.get('complexity_level', 2)
            if content_complexity == complexity_preference:
                score += 0.2
            elif abs(content_complexity - complexity_preference) <= 1:
                score += 0.1

            # Content type weighting
            content_type_idx = self._get_content_type_index(content.get('content_type', 'function'))
            if content_type_idx < len(content_type_weights):
                score += content_type_weights[content_type_idx] * 0.2

            # Freshness weighting
            freshness_score = content.get('freshness_score', 0.5)
            score += freshness_score * freshness_weight * 0.1

            # Popularity weighting
            popularity_score = content.get('popularity_score', 0.5)
            score += popularity_score * popularity_weight * 0.1

            # Add score to content
            content['filter_score'] = score
            filtered.append(content)

        # Sort by filter score and return top results
        filtered.sort(key=lambda x: x['filter_score'], reverse=True)
        return filtered[:20]  # Return top 20 results

    def _simulate_user_interaction(self, filtered_content: List[Dict[str, Any]]) -> Dict[str, float]:
        """Simulate user interaction with filtered content."""
        if not filtered_content:
            return {
                'satisfaction': 0.1,
                'ctr': 0.0,
                'session_duration': 10.0,
                'feedback': 1.0,
                'diversity': 0.0
            }

        # Calculate metrics based on content quality and user preferences
        avg_quality = np.mean([c.get('quality_score', 0.5) for c in filtered_content])

        # User satisfaction based on quality and relevance
        satisfaction = min(avg_quality * 1.2, 1.0)

        # Click-through rate based on content appeal
        ctr = min(avg_quality * 0.8, 0.8)

        # Session duration based on engagement
        session_duration = 60 + (satisfaction * 180)  # 1-4 minutes

        # Feedback score
        feedback = 1 + (satisfaction * 4)  # Scale to 1-5

        # Content diversity
        content_types = set(c.get('content_type', 'unknown') for c in filtered_content)
        diversity = len(content_types) / min(len(filtered_content), 10)

        return {
            'satisfaction': satisfaction,
            'ctr': ctr,
            'session_duration': session_duration,
            'feedback': feedback,
            'diversity': min(diversity, 1.0)
        }

    def _calculate_reward(self, user_metrics: Dict[str, float], action: Dict[str, np.ndarray]) -> float:
        """Calculate reward for filtering action."""
        # Weighted combination of user metrics
        reward = (
            0.4 * user_metrics['satisfaction'] +      # User satisfaction
            0.2 * user_metrics['ctr'] +              # Click-through rate
            0.2 * (user_metrics['session_duration'] / 300) +  # Session engagement
            0.1 * (user_metrics['feedback'] / 5) +    # User feedback
            0.1 * user_metrics['diversity']          # Content diversity
        )

        # Bonus for balanced content type distribution
        content_type_variance = np.var(action['content_type_weights'])
        balance_bonus = 0.1 * (1 - content_type_variance)

        return reward + balance_bonus

    def _get_content_type_index(self, content_type: str) -> int:
        """Get index for content type."""
        type_mapping = {
            'function': 0, 'class': 1, 'module': 2, 'api': 3,
            'documentation': 4, 'example': 5, 'test': 6,
            'configuration': 7, 'diagram': 8, 'architecture': 9
        }
        return type_mapping.get(content_type, 0)

    def _get_observation(self) -> Dict[str, np.ndarray]:
        """Get current observation."""
        if not self.filtering_history:
            return {
                'user_satisfaction': np.array([0.5]),
                'click_through_rate': np.array([0.5]),
                'session_duration': np.array([60.0]),
                'feedback_score': np.array([3.0]),
                'content_diversity': np.array([0.5])
            }

        # Return last observation
        last_interaction = self.filtering_history[-1]['user_metrics']
        return {
            'user_satisfaction': np.array([last_interaction['satisfaction']]),
            'click_through_rate': np.array([last_interaction['ctr']]),
            'session_duration': np.array([last_interaction['session_duration']]),
            'feedback_score': np.array([last_interaction['feedback']]),
            'content_diversity': np.array([last_interaction['diversity']])
        }

class ReinforcementLearningFilter:
    def __init__(self, state_dim: int, action_dim: int):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.q_network = self._build_q_network()
        self.target_network = self._build_q_network()
        self.optimizer = torch.optim.Adam(self.q_network.parameters(), lr=0.001)

        # Experience replay buffer
        self.replay_buffer = []
        self.buffer_size = 10000
        self.batch_size = 64

        # Training parameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

        self.update_target_network()

    def _build_q_network(self) -> nn.Module:
        """Build Q-network for action selection."""
        return nn.Sequential(
            nn.Linear(self.state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_dim)
        )

    def select_action(self, state: np.ndarray) -> Dict[str, np.ndarray]:
        """Select action using epsilon-greedy policy."""
        if np.random.random() < self.epsilon:
            # Random exploration
            return {
                'quality_threshold': np.random.uniform(0.3, 0.9, size=(1,)),
                'complexity_preference': np.random.randint(0, 4, size=(1,)),
                'content_type_weights': np.random.uniform(0.1, 1.0, size=(10,)),
                'freshness_weight': np.random.uniform(0.1, 0.9, size=(1,)),
                'popularity_weight': np.random.uniform(0.1, 0.9, size=(1,))
            }
        else:
            # Greedy action selection
            with torch.no_grad():
                q_values = self.q_network(torch.FloatTensor(state))
                action_idx = q_values.argmax().item()
                return self._decode_action(action_idx)

    def store_experience(self, state: np.ndarray, action: Dict[str, np.ndarray],
                        reward: float, next_state: np.ndarray, done: bool):
        """Store experience in replay buffer."""
        experience = {
            'state': state,
            'action': self._encode_action(action),
            'reward': reward,
            'next_state': next_state,
            'done': done
        }

        self.replay_buffer.append(experience)

        # Remove old experiences if buffer is full
        if len(self.replay_buffer) > self.buffer_size:
            self.replay_buffer.pop(0)

    def train(self):
        """Train Q-network using experience replay."""
        if len(self.replay_buffer) < self.batch_size:
            return

        # Sample batch from replay buffer
        batch = np.random.choice(len(self.replay_buffer), self.batch_size, replace=False)

        states = torch.FloatTensor([self.replay_buffer[i]['state'] for i in batch])
        actions = torch.LongTensor([self.replay_buffer[i]['action'] for i in batch])
        rewards = torch.FloatTensor([self.replay_buffer[i]['reward'] for i in batch])
        next_states = torch.FloatTensor([self.replay_buffer[i]['next_state'] for i in batch])
        dones = torch.BoolTensor([self.replay_buffer[i]['done'] for i in batch])

        # Get current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Get next Q-values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)

        # Compute loss
        loss = nn.functional.mse_loss(current_q_values.squeeze(), target_q_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Update target network periodically
        if np.random.random() < 0.01:  # 1% chance each training step
            self.update_target_network()

    def _encode_action(self, action: Dict[str, np.ndarray]) -> int:
        """Encode complex action into single integer."""
        quality_bin = int(float(action['quality_threshold'][0]) * 10)
        complexity = int(action['complexity_preference'][0])
        dominant_type = int(np.argmax(action['content_type_weights']))
        freshness = int(float(action['freshness_weight'][0]) * 10)
        popularity = int(float(action['popularity_weight'][0]) * 10)

        return (quality_bin * 10000 + complexity * 1000 +
                dominant_type * 100 + freshness * 10 + popularity)

    def _decode_action(self, action_idx: int) -> Dict[str, np.ndarray]:
        """Decode integer into complex action."""
        quality_bin = action_idx // 10000
        remainder = action_idx % 10000
        complexity = remainder // 1000
        remainder = remainder % 1000
        dominant_type = remainder // 100
        remainder = remainder % 100
        freshness = remainder // 10
        popularity = remainder % 10

        # Generate action with dominant type emphasized
        content_type_weights = np.ones(10) * 0.1
        content_type_weights[dominant_type] = 0.5
        content_type_weights = content_type_weights / content_type_weights.sum()

        return {
            'quality_threshold': np.array([quality_bin / 10.0]),
            'complexity_preference': np.array([complexity]),
            'content_type_weights': content_type_weights,
            'freshness_weight': np.array([freshness / 10.0]),
            'popularity_weight': np.array([popularity / 10.0])
        }

    def update_target_network(self):
        """Update target network weights."""
        self.target_network.load_state_dict(self.q_network.state_dict())
```

## Context-Aware Collaborative Filtering

### Social Learning and Recommendation System
```python
class CollaborativeContentFilter:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_profiles = {}
        self.content_profiles = {}
        self.interaction_history = []

    def build_matrices(self, interactions: List[Dict[str, Any]]):
        """Build user-item interaction matrices."""
        # Extract unique users and items
        users = list(set(i['user_id'] for i in interactions))
        items = list(set(i['content_id'] for i in interactions))

        # Create user-item matrix
        n_users = len(users)
        n_items = len(items)

        self.user_item_matrix = np.zeros((n_users, n_items))
        self.user_to_idx = {user: idx for idx, user in enumerate(users)}
        self.item_to_idx = {item: idx for idx, item in enumerate(items)}

        # Fill matrix with interaction ratings
        for interaction in interactions:
            user_idx = self.user_to_idx[interaction['user_id']]
            item_idx = self.item_to_idx[interaction['content_id']]
            rating = interaction.get('rating', 1.0)
            self.user_item_matrix[user_idx, item_idx] = rating

        # Calculate similarity matrices
        self.user_similarity_matrix = self._calculate_user_similarity()
        self.item_similarity_matrix = self._calculate_item_similarity()

    def _calculate_user_similarity(self) -> np.ndarray:
        """Calculate user similarity using cosine similarity."""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(self.user_item_matrix)

    def _calculate_item_similarity(self) -> np.ndarray:
        """Calculate item similarity using cosine similarity."""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(self.user_item_matrix.T)

    def get_collaborative_recommendations(self, user_id: str,
                                         user_profile: Dict[str, Any],
                                         top_k: int = 10) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations."""
        if user_id not in self.user_to_idx:
            return []

        user_idx = self.user_to_idx[user_id]

        # Find similar users
        user_similarities = self.user_similarity_matrix[user_idx]
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # Top 10 similar users

        # Get items liked by similar users
        recommendations = {}
        for similar_user_idx in similar_users:
            similar_user_items = self.user_item_matrix[similar_user_idx]

            for item_idx, rating in enumerate(similar_user_items):
                if rating > 0 and self.user_item_matrix[user_idx, item_idx] == 0:
                    if item_idx not in recommendations:
                        recommendations[item_idx] = []
                    recommendations[item_idx].append(rating * user_similarities[similar_user_idx])

        # Calculate weighted scores
        item_scores = {}
        for item_idx, ratings in recommendations.items():
            item_scores[item_idx] = sum(ratings) / len(ratings)

        # Apply content-based filtering refinement
        refined_scores = self._refine_with_content_similarity(
            user_id, user_profile, item_scores
        )

        # Get top recommendations
        top_items = sorted(refined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        recommendations = []
        for item_idx, score in top_items:
            item_id = list(self.item_to_idx.keys())[list(self.item_to_idx.values()).index(item_idx)]
            recommendations.append({
                'content_id': item_id,
                'collaborative_score': score,
                'recommendation_type': 'collaborative'
            })

        return recommendations

    def _refine_with_content_similarity(self, user_id: str,
                                     user_profile: Dict[str, Any],
                                     item_scores: Dict[int, float]) -> Dict[int, float]:
        """Refine collaborative scores with content similarity."""
        if user_id not in self.user_to_idx:
            return item_scores

        user_idx = self.user_to_idx[user_id]

        # Get user's liked items
        user_items = self.user_item_matrix[user_idx]
        liked_items = [i for i, rating in enumerate(user_items) if rating > 0]

        if not liked_items:
            return item_scores

        # Calculate content similarity for each recommended item
        refined_scores = {}
        for item_idx, collab_score in item_scores.items():
            content_similarities = []

            for liked_item_idx in liked_items:
                similarity = self.item_similarity_matrix[item_idx, liked_item_idx]
                content_similarities.append(similarity)

            # Combine collaborative and content scores
            avg_content_similarity = np.mean(content_similarities) if content_similarities else 0
            combined_score = 0.7 * collab_score + 0.3 * avg_content_similarity
            refined_scores[item_idx] = combined_score

        return refined_scores

class HybridFilteringSystem:
    def __init__(self):
        self.content_filter = AIContentClassifier()
        self.collaborative_filter = CollaborativeContentFilter()
        self.rl_filter = None
        self.adaptive_weights = {
            'content_based': 0.4,
            'collaborative': 0.3,
            'context_aware': 0.2,
            'popularity': 0.1
        }

    def initialize(self, content_database: List[Dict[str, Any]],
                  interaction_history: List[Dict[str, Any]]):
        """Initialize the hybrid filtering system."""
        # Extract features from all content
        self.content_features = {}
        for content in content_database:
            features = self.content_filter.extract_comprehensive_features(content)
            self.content_features[content['content_id']] = features

        # Build collaborative filtering matrices
        self.collaborative_filter.build_matrices(interaction_history)

        # Store interaction history
        self.interaction_history = interaction_history

    def get_personalized_recommendations(self, user_id: str,
                                        user_context: Dict[str, Any],
                                        top_k: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations using hybrid approach."""
        recommendations = []

        # Content-based filtering
        content_recs = self._get_content_based_recommendations(user_id, user_context, top_k)
        recommendations.extend(content_recs)

        # Collaborative filtering
        collab_recs = self.collaborative_filter.get_collaborative_recommendations(
            user_id, user_context, top_k
        )
        recommendations.extend(collab_recs)

        # Context-aware filtering
        context_recs = self._get_context_aware_recommendations(user_id, user_context, top_k)
        recommendations.extend(context_recs)

        # Popularity-based filtering
        popularity_recs = self._get_popularity_based_recommendations(user_context, top_k)
        recommendations.extend(popularity_recs)

        # Combine and rank recommendations
        final_recommendations = self._combine_recommendations(
            recommendations, user_context, top_k
        )

        return final_recommendations

    def _get_content_based_recommendations(self, user_id: str,
                                          user_context: Dict[str, Any],
                                          top_k: int) -> List[Dict[str, Any]]:
        """Get content-based recommendations."""
        # Get user's preference vector
        user_interactions = [i for i in self.interaction_history if i['user_id'] == user_id]

        if not user_interactions:
            return []

        # Calculate user preference weights
        preference_weights = self._calculate_preference_weights(user_interactions, user_context)

        # Score all content
        content_scores = []
        for content_id, features in self.content_features.items():
            score = self._calculate_content_score(features, preference_weights, user_context)
            content_scores.append({
                'content_id': content_id,
                'score': score,
                'recommendation_type': 'content_based'
            })

        # Sort and return top recommendations
        content_scores.sort(key=lambda x: x['score'], reverse=True)
        return content_scores[:top_k]

    def _get_context_aware_recommendations(self, user_id: str,
                                         user_context: Dict[str, Any],
                                         top_k: int) -> List[Dict[str, Any]]:
        """Get context-aware recommendations."""
        # Extract context features
        current_time = user_context.get('current_time', '')
        current_project = user_context.get('current_project', '')
        current_task = user_context.get('current_task', '')

        # Score content based on context relevance
        context_scores = []
        for content_id, features in self.content_features.items():
            context_score = self._calculate_context_score(
                features, current_time, current_project, current_task
            )
            context_scores.append({
                'content_id': content_id,
                'score': context_score,
                'recommendation_type': 'context_aware'
            })

        # Sort and return top recommendations
        context_scores.sort(key=lambda x: x['score'], reverse=True)
        return context_scores[:top_k]

    def _get_popularity_based_recommendations(self, user_context: Dict[str, Any],
                                            top_k: int) -> List[Dict[str, Any]]:
        """Get popularity-based recommendations."""
        # Calculate popularity scores
        popularity_scores = []

        for content_id, features in self.content_features.items():
            popularity_score = (
                features.popularity_score * 0.5 +
                features.user_feedback_score * 0.3 +
                features.freshness_score * 0.2
            )
            popularity_scores.append({
                'content_id': content_id,
                'score': popularity_score,
                'recommendation_type': 'popularity_based'
            })

        # Sort and return top recommendations
        popularity_scores.sort(key=lambda x: x['score'], reverse=True)
        return popularity_scores[:top_k]

    def _combine_recommendations(self, recommendations: List[Dict[str, Any]],
                                user_context: Dict[str, Any],
                                top_k: int) -> List[Dict[str, Any]]:
        """Combine recommendations from different sources."""
        # Group by content_id
        content_scores = {}

        for rec in recommendations:
            content_id = rec['content_id']
            if content_id not in content_scores:
                content_scores[content_id] = {
                    'content_id': content_id,
                    'scores': {},
                    'types': []
                }

            # Add score from different source
            rec_type = rec['recommendation_type']
            weight = self.adaptive_weights.get(rec_type, 0.25)
            content_scores[content_id]['scores'][rec_type] = rec['score'] * weight
            content_scores[content_id]['types'].append(rec_type)

        # Calculate final scores
        final_recommendations = []
        for content_id, data in content_scores.items():
            final_score = sum(data['scores'].values())
            if len(data['scores']) > 1:
                # Bonus for multi-source agreement
                final_score *= 1.1

            final_recommendations.append({
                'content_id': content_id,
                'final_score': final_score,
                'source_types': data['types'],
                'individual_scores': data['scores']
            })

        # Sort and return top recommendations
        final_recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        return final_recommendations[:top_k]

    def _calculate_preference_weights(self, user_interactions: List[Dict[str, Any]],
                                    user_context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate user preference weights."""
        weights = {
            'quality_weight': 0.3,
            'complexity_preference': 0.2,
            'content_type_preferences': {},
            'technology_preferences': {}
        }

        # Analyze user's past interactions
        for interaction in user_interactions:
            rating = interaction.get('rating', 1.0)
            content_id = interaction['content_id']

            if content_id in self.content_features:
                features = self.content_features[content_id]

                # Update quality preference
                weights['quality_weight'] += features.quality_score * rating

                # Update complexity preference
                if features.complexity_level:
                    complexity_key = f'complexity_{features.complexity_level.value}'
                    weights[complexity_key] = weights.get(complexity_key, 0) + rating

                # Update content type preferences
                if features.content_type:
                    type_key = f'type_{features.content_type.value}'
                    weights[type_key] = weights.get(type_key, 0) + rating

        # Normalize weights
        total_weight = sum(v for k, v in weights.items() if k != 'content_type_preferences' and k != 'technology_preferences')
        if total_weight > 0:
            for key in weights:
                if key not in ['content_type_preferences', 'technology_preferences']:
                    weights[key] = weights[key] / total_weight

        return weights

    def _calculate_content_score(self, features: ContentFeatures,
                               preference_weights: Dict[str, float],
                               user_context: Dict[str, Any]) -> float:
        """Calculate content score based on features and preferences."""
        score = 0.0

        # Quality component
        score += features.quality_score * preference_weights.get('quality_weight', 0.3)

        # Complexity component
        user_complexity = user_context.get('complexity_level', 2)
        if user_complexity == features.complexity_level.value:
            score += 0.2
        elif abs(user_complexity - features.complexity_level.value) <= 1:
            score += 0.1

        # Content type component
        preferred_types = user_context.get('preferred_content_types', [])
        if features.content_type.value in preferred_types:
            score += 0.2

        # Freshness component
        if user_context.get('prefer_fresh_content', True):
            score += features.freshness_score * 0.1

        # User feedback component
        score += features.user_feedback_score * 0.1

        return min(score, 1.0)

    def _calculate_context_score(self, features: ContentFeatures,
                                current_time: str, current_project: str,
                                current_task: str) -> float:
        """Calculate context relevance score."""
        score = 0.0

        # Time-based relevance
        if current_time:
            # Add time-based scoring logic
            score += features.freshness_score * 0.3

        # Project relevance
        if current_project and features.metadata:
            project_keywords = current_project.lower().split()
            content_text = features.metadata.get('description', '').lower()

            if any(keyword in content_text for keyword in project_keywords):
                score += 0.3

        # Task relevance
        if current_task:
            task_keywords = current_task.lower().split()
            content_text = features.metadata.get('description', '').lower()

            if any(keyword in content_text for keyword in task_keywords):
                score += 0.4

        return min(score, 1.0)

**Use Cases for RAG**: Advanced AI-powered content filtering with multi-dimensional analysis, reinforcement learning for adaptive filtering, collaborative filtering with social learning, hybrid recommendation systems, and context-aware personalized content delivery.