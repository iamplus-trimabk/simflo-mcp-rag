# Task 16: Advanced AI-Powered Search Ranking with Learning Systems

## Overview

Modern RAG systems require sophisticated ranking algorithms that can adapt to user preferences, learn from feedback, and provide highly relevant results in real-time. This comprehensive approach combines machine learning, A/B testing, multi-armed bandit algorithms, and continuous optimization for intelligent search ranking.

## Advanced Machine Learning Ranking Systems

### Neural Network-Based Relevance Scoring

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

class SearchRankingDataset(Dataset):
    """Dataset for search ranking neural network training."""

    def __init__(self, search_data: List[Dict]):
        self.data = search_data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            'query_embedding': torch.FloatTensor(item['query_embedding']),
            'content_embedding': torch.FloatTensor(item['content_embedding']),
            'text_features': torch.FloatTensor(item['text_features']),
            'metadata_features': torch.FloatTensor(item['metadata_features']),
            'user_features': torch.FloatTensor(item['user_features']),
            'interaction_features': torch.FloatTensor(item['interaction_features']),
            'relevance_score': torch.FloatTensor([item['relevance_score']])
        }

class NeuralRankingModel(nn.Module):
    """Deep neural network for search relevance ranking."""

    def __init__(self, embedding_dim: int = 384, text_feature_dim: int = 50,
                 metadata_feature_dim: int = 30, user_feature_dim: int = 20,
                 interaction_feature_dim: int = 15, hidden_dims: List[int] = [512, 256, 128]):
        super().__init__()

        # Input dimensions
        self.embedding_dim = embedding_dim
        self.text_feature_dim = text_feature_dim
        self.metadata_feature_dim = metadata_feature_dim
        self.user_feature_dim = user_feature_dim
        self.interaction_feature_dim = interaction_feature_dim

        # Feature embedding layers
        self.embedding_processor = nn.Sequential(
            nn.Linear(embedding_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU()
        )

        self.text_processor = nn.Sequential(
            nn.Linear(text_feature_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32)
        )

        self.metadata_processor = nn.Sequential(
            nn.Linear(metadata_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32)
        )

        self.user_processor = nn.Sequential(
            nn.Linear(user_feature_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )

        self.interaction_processor = nn.Sequential(
            nn.Linear(interaction_feature_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )

        # Combined feature dimension
        combined_dim = 128 + 32 + 32 + 16 + 16

        # Deep ranking layers
        layers = []
        prev_dim = combined_dim
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.BatchNorm1d(hidden_dim)
            ])
            prev_dim = hidden_dim

        # Final output layer
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())

        self.ranking_layers = nn.Sequential(*layers)

    def forward(self, batch):
        # Process query and content embeddings
        query_emb = self.embedding_processor(batch['query_embedding'])
        content_emb = self.embedding_processor(batch['content_embedding'])

        # Calculate embedding similarity features
        cos_sim = nn.functional.cosine_similarity(query_emb, content_emb, dim=1)
        euclidean_dist = torch.norm(query_emb - content_emb, dim=1)
        dot_product = torch.sum(query_emb * content_emb, dim=1)

        embedding_features = torch.stack([cos_sim, euclidean_dist, dot_product], dim=1)

        # Process other features
        text_features = self.text_processor(batch['text_features'])
        metadata_features = self.metadata_processor(batch['metadata_features'])
        user_features = self.user_processor(batch['user_features'])
        interaction_features = self.interaction_processor(batch['interaction_features'])

        # Concatenate all features
        combined_features = torch.cat([
            embedding_features,
            text_features,
            metadata_features,
            user_features,
            interaction_features
        ], dim=1)

        # Pass through ranking layers
        relevance_score = self.ranking_layers(combined_features)

        return relevance_score.squeeze()

class AdvancedMLRankingSystem:
    """Advanced machine learning-based ranking system."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = NeuralRankingModel()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-5)
        self.criterion = nn.BCELoss()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Training data storage
        self.training_data = deque(maxlen=10000)  # Store last 10K interactions
        self.validation_data = deque(maxlen=2000)

        # Feature extractors
        self.feature_extractors = self._initialize_feature_extractors()

        # Model versioning
        self.model_version = 1
        self.last_training_time = None
        self.training_metrics = defaultdict(list)

        # Load pre-trained model if available
        if model_path:
            self.load_model(model_path)

    def _initialize_feature_extractors(self):
        """Initialize feature extraction components."""
        return {
            'text_features': TextFeatureExtractor(),
            'metadata_features': MetadataFeatureExtractor(),
            'user_features': UserFeatureExtractor(),
            'interaction_features': InteractionFeatureExtractor()
        }

    def extract_features(self, query_embedding: List[float], chunk: Dict,
                        user_context: Dict, query_text: str) -> Dict[str, List[float]]:
        """Extract comprehensive features for ranking."""

        # Text-based features
        text_features = self.feature_extractors['text_features'].extract(
            query_text, chunk.get('content', ''), chunk.get('language', '')
        )

        # Metadata features
        metadata_features = self.feature_extractors['metadata_features'].extract(chunk)

        # User features
        user_features = self.feature_extractors['user_features'].extract(user_context)

        # Interaction features
        interaction_features = self.feature_extractors['interaction_features'].extract(
            query_text, chunk, user_context
        )

        return {
            'query_embedding': query_embedding,
            'content_embedding': chunk.get('embedding', [0.0] * 384),
            'text_features': text_features,
            'metadata_features': metadata_features,
            'user_features': user_features,
            'interaction_features': interaction_features
        }

    def predict_relevance(self, features: Dict[str, List[float]]) -> float:
        """Predict relevance score using neural network."""
        self.model.eval()

        with torch.no_grad():
            # Convert to tensors
            batch = {
                'query_embedding': torch.FloatTensor([features['query_embedding']]).to(self.device),
                'content_embedding': torch.FloatTensor([features['content_embedding']]).to(self.device),
                'text_features': torch.FloatTensor([features['text_features']]).to(self.device),
                'metadata_features': torch.FloatTensor([features['metadata_features']]).to(self.device),
                'user_features': torch.FloatTensor([features['user_features']]).to(self.device),
                'interaction_features': torch.FloatTensor([features['interaction_features']]).to(self.device)
            }

            # Get prediction
            score = self.model(batch)
            return float(score.cpu().numpy())

    def rank_with_ml_model(self, query_embedding: List[float], query_text: str,
                          chunks: List[Dict], user_context: Dict,
                          top_k: int = 10) -> List[Dict]:
        """Rank search results using machine learning model."""

        scored_chunks = []

        for chunk in chunks:
            try:
                # Extract features
                features = self.extract_features(query_embedding, chunk, user_context, query_text)

                # Predict relevance
                ml_score = self.predict_relevance(features)

                # Combine with traditional scores
                traditional_score = self._calculate_traditional_score(
                    query_embedding, query_text, chunk, user_context
                )

                # Ensemble final score
                final_score = 0.7 * ml_score + 0.3 * traditional_score

                chunk.update({
                    'ml_score': ml_score,
                    'traditional_score': traditional_score,
                    'final_score': final_score,
                    'features': features
                })

                scored_chunks.append(chunk)

            except Exception as e:
                logging.error(f"Error scoring chunk: {e}")
                # Fallback to traditional scoring
                fallback_score = self._calculate_traditional_score(
                    query_embedding, query_text, chunk, user_context
                )
                chunk.update({
                    'ml_score': 0.5,  # Neutral score
                    'traditional_score': fallback_score,
                    'final_score': fallback_score
                })
                scored_chunks.append(chunk)

        # Sort by final score
        scored_chunks.sort(key=lambda x: x['final_score'], reverse=True)

        return scored_chunks[:top_k]

    def record_interaction(self, query_embedding: List[float], query_text: str,
                          chunk: Dict, user_context: Dict, interaction_type: str,
                          rating: Optional[float] = None):
        """Record user interaction for learning."""

        features = self.extract_features(query_embedding, chunk, user_context, query_text)

        # Determine relevance score based on interaction
        if rating is not None:
            relevance_score = rating
        else:
            relevance_score = self._infer_relevance_from_interaction(interaction_type)

        training_item = {
            'query_embedding': features['query_embedding'],
            'content_embedding': features['content_embedding'],
            'text_features': features['text_features'],
            'metadata_features': features['metadata_features'],
            'user_features': features['user_features'],
            'interaction_features': features['interaction_features'],
            'relevance_score': relevance_score,
            'timestamp': datetime.now().isoformat(),
            'interaction_type': interaction_type,
            'query_text': query_text,
            'chunk_id': chunk.get('id', 'unknown')
        }

        self.training_data.append(training_item)

        # Trigger training if enough data collected
        if len(self.training_data) >= 100 and self._should_retrain():
            self._train_model()

    def _infer_relevance_from_interaction(self, interaction_type: str) -> float:
        """Infer relevance score from interaction type."""
        interaction_scores = {
            'click': 0.8,
            'long_view': 0.9,
            'copy_code': 0.95,
            'bookmark': 1.0,
            'share': 1.0,
            'quick_exit': 0.2,
            'no_interaction': 0.1,
            'thumbs_up': 1.0,
            'thumbs_down': 0.0,
            'feedback_positive': 0.9,
            'feedback_negative': 0.1
        }
        return interaction_scores.get(interaction_type, 0.5)

    def _should_retrain(self) -> bool:
        """Determine if model should be retrained."""
        if self.last_training_time is None:
            return True

        time_since_last = datetime.now() - self.last_training_time
        return time_since_last > timedelta(hours=6)  # Retrain every 6 hours

    def _train_model(self):
        """Train the neural ranking model."""
        if len(self.training_data) < 100:
            logging.warning("Insufficient training data")
            return

        try:
            # Prepare dataset
            dataset = SearchRankingDataset(list(self.training_data))
            train_size = int(0.8 * len(dataset))
            val_size = len(dataset) - train_size

            train_dataset, val_dataset = torch.utils.data.random_split(
                dataset, [train_size, val_size]
            )

            train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=32)

            # Training loop
            self.model.train()
            num_epochs = 10
            best_val_loss = float('inf')

            for epoch in range(num_epochs):
                # Training phase
                train_loss = 0.0
                for batch in train_loader:
                    batch = {k: v.to(self.device) for k, v in batch.items()}

                    self.optimizer.zero_grad()
                    predictions = self.model(batch)
                    loss = self.criterion(predictions, batch['relevance_score'].squeeze())
                    loss.backward()
                    self.optimizer.step()

                    train_loss += loss.item()

                # Validation phase
                self.model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for batch in val_loader:
                        batch = {k: v.to(self.device) for k, v in batch.items()}
                        predictions = self.model(batch)
                        loss = self.criterion(predictions, batch['relevance_score'].squeeze())
                        val_loss += loss.item()

                avg_train_loss = train_loss / len(train_loader)
                avg_val_loss = val_loss / len(val_loader)

                self.training_metrics['train_loss'].append(avg_train_loss)
                self.training_metrics['val_loss'].append(avg_val_loss)

                # Save best model
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    self.model_version += 1
                    self._save_checkpoint(f"model_v{self.model_version}.pt")

                logging.info(f"Epoch {epoch+1}/{num_epochs}: "
                           f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

            self.last_training_time = datetime.now()
            logging.info(f"Model training completed. Version: {self.model_version}")

        except Exception as e:
            logging.error(f"Error during model training: {e}")

    def _save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'model_version': self.model_version,
            'training_metrics': dict(self.training_metrics),
            'timestamp': datetime.now().isoformat()
        }
        torch.save(checkpoint, filename)

    def load_model(self, model_path: str):
        """Load pre-trained model."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.model_version = checkpoint.get('model_version', 1)
            self.training_metrics = defaultdict(list, checkpoint.get('training_metrics', {}))
            logging.info(f"Model loaded from {model_path}, version {self.model_version}")
        except Exception as e:
            logging.error(f"Error loading model: {e}")

    def _calculate_traditional_score(self, query_embedding: List[float], query_text: str,
                                   chunk: Dict, user_context: Dict) -> float:
        """Calculate traditional relevance score as fallback."""
        # Vector similarity
        if chunk.get('embedding'):
            vector_sim = self._cosine_similarity(query_embedding, chunk['embedding'])
        else:
            vector_sim = 0.0

        # Text similarity
        text_sim = self._text_similarity(query_text, chunk.get('content', ''))

        # Quality score
        quality_score = self._calculate_quality_score(chunk)

        # Context relevance
        context_score = self._calculate_context_relevance(chunk, user_context)

        # Weighted combination
        traditional_score = (
            vector_sim * 0.5 +
            text_sim * 0.2 +
            quality_score * 0.2 +
            context_score * 0.1
        )

        return traditional_score

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using keyword overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _calculate_quality_score(self, chunk: Dict) -> float:
        """Calculate content quality score."""
        content = chunk.get('content', '')
        quality_score = 0.0

        # Documentation presence
        if any(pattern in content for pattern in ['"""', "'''", "//", "#"]):
            quality_score += 0.3

        # Code structure
        if any(pattern in content for pattern in ['def ', 'class ', 'function']):
            quality_score += 0.2

        # Examples
        if any(pattern in content.lower() for pattern in ['example', 'usage']):
            quality_score += 0.2

        # Length appropriateness
        word_count = len(content.split())
        if 50 <= word_count <= 500:
            quality_score += 0.2
        elif 20 <= word_count <= 1000:
            quality_score += 0.1

        return min(quality_score, 1.0)

    def _calculate_context_relevance(self, chunk: Dict, user_context: Dict) -> float:
        """Calculate context relevance score."""
        if not user_context:
            return 0.0

        score = 0.0

        # Language preference
        preferred_lang = user_context.get('preferred_language')
        if preferred_lang and chunk.get('language') == preferred_lang:
            score += 0.4

        # Framework preference
        preferred_framework = user_context.get('preferred_framework')
        if preferred_framework and chunk.get('framework') == preferred_framework:
            score += 0.3

        # Expertise level
        user_expertise = user_context.get('expertise_level', 'intermediate')
        chunk_complexity = chunk.get('complexity', 1)
        if self._complexity_matches_expertise(chunk_complexity, user_expertise):
            score += 0.3

        return min(score, 1.0)

    def _complexity_matches_expertise(self, complexity: int, expertise: str) -> bool:
        """Check if content complexity matches user expertise."""
        complexity_levels = {
            'beginner': [1, 2],
            'intermediate': [2, 3, 4],
            'expert': [4, 5, 6]
        }
        return complexity in complexity_levels.get(expertise, [2, 3, 4])
```

### Feature Extraction Components

```python
import re
from typing import List, Dict, Any

class TextFeatureExtractor:
    """Extract text-based features for ranking."""

    def extract(self, query_text: str, content: str, language: str) -> List[float]:
        features = []

        # Basic text statistics
        query_words = set(query_text.lower().split())
        content_words = set(content.lower().split())

        # Jaccard similarity
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)
        jaccard_sim = len(intersection) / len(union) if union else 0.0
        features.append(jaccard_sim)

        # Exact phrase match
        exact_match = 1.0 if query_text.lower() in content.lower() else 0.0
        features.append(exact_match)

        # Word overlap ratio
        overlap_ratio = len(intersection) / len(query_words) if query_words else 0.0
        features.append(overlap_ratio)

        # Content length features
        content_length = len(content.split())
        features.append(min(content_length / 500.0, 1.0))  # Normalized length

        # Query length
        query_length = len(query_text.split())
        features.append(min(query_length / 20.0, 1.0))

        # Language match
        language_match = 1.0 if language else 0.5
        features.append(language_match)

        # Code-specific features
        is_code = any(pattern in content for pattern in ['def ', 'class ', 'function', 'import'])
        features.append(1.0 if is_code else 0.0)

        # Documentation presence
        has_docs = any(pattern in content for pattern in ['"""', "'''", '#', '//'])
        features.append(1.0 if has_docs else 0.0)

        # Fill to fixed size
        while len(features) < 50:
            features.append(0.0)

        return features[:50]

class MetadataFeatureExtractor:
    """Extract metadata-based features for ranking."""

    def extract(self, chunk: Dict) -> List[float]:
        features = []

        # Content type (one-hot encoded)
        content_types = ['function', 'class', 'module', 'documentation', 'example', 'test']
        content_type = chunk.get('content_type', 'unknown')
        for ct in content_types:
            features.append(1.0 if ct in content_type.lower() else 0.0)

        # Language (one-hot encoded)
        languages = ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'cpp']
        language = chunk.get('language', '')
        for lang in languages:
            features.append(1.0 if lang in language.lower() else 0.0)

        # Quality score
        quality_score = chunk.get('quality_score', 0.0)
        features.append(quality_score)

        # Complexity score (normalized)
        complexity = chunk.get('complexity', 1)
        features.append(min(complexity / 10.0, 1.0))

        # Popularity score (normalized)
        popularity = chunk.get('popularity_score', 0.0)
        features.append(popularity)

        # Has tests
        features.append(1.0 if chunk.get('has_tests', False) else 0.0)

        # Is documented
        features.append(1.0 if chunk.get('is_documented', False) else 0.0)

        # Token count (normalized)
        token_count = chunk.get('token_count', 0)
        features.append(min(token_count / 1000.0, 1.0))

        # Line count (normalized)
        line_count = chunk.get('line_count', 0)
        features.append(min(line_count / 200.0, 1.0))

        # Fill to fixed size
        while len(features) < 30:
            features.append(0.0)

        return features[:30]

class UserFeatureExtractor:
    """Extract user-based features for ranking."""

    def extract(self, user_context: Dict) -> List[float]:
        features = []

        # User role (one-hot encoded)
        roles = ['developer', 'architect', 'designer', 'manager', 'analyst']
        user_role = user_context.get('role', '')
        for role in roles:
            features.append(1.0 if role in user_role.lower() else 0.0)

        # Expertise level (one-hot encoded)
        expertise_levels = ['beginner', 'intermediate', 'expert', 'master']
        expertise = user_context.get('expertise_level', 'intermediate')
        for level in expertise_levels:
            features.append(1.0 if level in expertise.lower() else 0.0)

        # Activity level
        activity_score = user_context.get('activity_score', 0.5)
        features.append(activity_score)

        # Session duration (normalized)
        session_duration = user_context.get('session_duration', 0)
        features.append(min(session_duration / 3600.0, 1.0))  # Normalize to hours

        # Previous interaction count (normalized)
        interaction_count = user_context.get('interaction_count', 0)
        features.append(min(interaction_count / 1000.0, 1.0))

        # Preferred technology match score
        preferred_tech = user_context.get('preferred_technologies', [])
        tech_match_score = user_context.get('tech_match_score', 0.0)
        features.append(tech_match_score)

        # Fill to fixed size
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

class InteractionFeatureExtractor:
    """Extract interaction-based features for ranking."""

    def extract(self, query_text: str, chunk: Dict, user_context: Dict) -> List[float]:
        features = []

        # Query complexity
        query_complexity = self._calculate_query_complexity(query_text)
        features.append(query_complexity)

        # Content recency score
        recency_score = self._calculate_recency_score(chunk)
        features.append(recency_score)

        # User familiarity with content type
        content_type = chunk.get('content_type', '')
        familiarity = self._calculate_familiarity_score(content_type, user_context)
        features.append(familiarity)

        # Project relevance
        project_relevance = self._calculate_project_relevance(chunk, user_context)
        features.append(project_relevance)

        # Time-of-day relevance
        time_relevance = self._calculate_time_relevance(user_context)
        features.append(time_relevance)

        # Device type relevance
        device_relevance = self._calculate_device_relevance(user_context)
        features.append(device_relevance)

        # Previous success rate with similar content
        success_rate = user_context.get('success_rate', 0.5)
        features.append(success_rate)

        # Learning progress alignment
        learning_alignment = self._calculate_learning_alignment(chunk, user_context)
        features.append(learning_alignment)

        # Fill to fixed size
        while len(features) < 15:
            features.append(0.0)

        return features[:15]

    def _calculate_query_complexity(self, query_text: str) -> float:
        """Calculate query complexity score."""
        # Count technical terms
        technical_terms = ['function', 'class', 'method', 'api', 'algorithm', 'pattern']
        tech_count = sum(1 for term in technical_terms if term in query_text.lower())

        # Length-based complexity
        length_complexity = min(len(query_text.split()) / 10.0, 1.0)

        # Combined complexity
        return (tech_count / len(technical_terms) * 0.6 + length_complexity * 0.4)

    def _calculate_recency_score(self, chunk: Dict) -> float:
        """Calculate content recency score."""
        from datetime import datetime, timedelta

        timestamp = chunk.get('timestamp')
        if not timestamp:
            return 0.5

        try:
            content_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days_old = (datetime.now() - content_date).days

            # More recent content gets higher score
            if days_old <= 7:
                return 1.0
            elif days_old <= 30:
                return 0.8
            elif days_old <= 90:
                return 0.6
            elif days_old <= 365:
                return 0.4
            else:
                return 0.2
        except:
            return 0.5

    def _calculate_familiarity_score(self, content_type: str, user_context: Dict) -> float:
        """Calculate user familiarity with content type."""
        familiarity_history = user_context.get('familiarity_history', {})
        return familiarity_history.get(content_type, 0.5)

    def _calculate_project_relevance(self, chunk: Dict, user_context: Dict) -> float:
        """Calculate project relevance score."""
        current_project = user_context.get('current_project', '').lower()
        file_path = chunk.get('file_path', '').lower()
        content = chunk.get('content', '').lower()

        if current_project:
            if current_project in file_path or current_project in content:
                return 1.0
            elif any(word in file_path or word in content
                    for word in current_project.split('_')):
                return 0.7
            else:
                return 0.3
        return 0.5

    def _calculate_time_relevance(self, user_context: Dict) -> float:
        """Calculate time-of-day relevance."""
        from datetime import datetime

        hour = datetime.now().hour
        work_hours = range(9, 18)  # 9 AM to 6 PM

        if hour in work_hours:
            return 0.8  # Higher relevance during work hours
        elif hour in range(18, 22):
            return 0.6  # Evening
        else:
            return 0.4  # Night/early morning

    def _calculate_device_relevance(self, user_context: Dict) -> float:
        """Calculate device type relevance."""
        device_type = user_context.get('device_type', 'desktop')

        # Different content types may be better suited for different devices
        if device_type == 'mobile':
            return 0.7  # Mobile gets slight penalty for complex code
        elif device_type == 'tablet':
            return 0.9
        else:  # desktop
            return 1.0

    def _calculate_learning_alignment(self, chunk: Dict, user_context: Dict) -> float:
        """Calculate alignment with user's learning progress."""
        user_level = user_context.get('expertise_level', 'intermediate')
        chunk_complexity = chunk.get('complexity', 1)

        complexity_mapping = {
            'beginner': [1, 2],
            'intermediate': [2, 3, 4],
            'expert': [4, 5, 6],
            'master': [5, 6, 7]
        }

        preferred_complexity = complexity_mapping.get(user_level, [2, 3, 4])
        return 1.0 if chunk_complexity in preferred_complexity else 0.5
```

**Use Cases for RAG**: Provide highly accurate, learning-powered search rankings that continuously improve from user interactions, adapt to individual preferences, and deliver personalized results with real-time optimization.

## A/B Testing and Multi-Armed Bandit Optimization

### Advanced A/B Testing Framework

```python
import numpy as np
import random
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json
import logging
from enum import Enum

class ExperimentType(Enum):
    RANKING_ALGORITHM = "ranking_algorithm"
    FEATURE_WEIGHTS = "feature_weights"
    RESULT_DIVERSITY = "result_diversity"
    PERSONALIZATION_LEVEL = "personalization_level"
    RESULT_LAYOUT = "result_layout"

@dataclass
class ExperimentVariant:
    """Represents a single variant in an A/B test."""
    variant_id: str
    name: str
    description: str
    config: Dict[str, Any]
    traffic_allocation: float  # 0.0 to 1.0
    is_control: bool = False

@dataclass
class Experiment:
    """A/B testing experiment configuration."""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    variants: List[ExperimentVariant]
    start_time: datetime
    end_time: Optional[datetime] = None
    sample_size: int = 1000
    confidence_level: float = 0.95
    min_effect_size: float = 0.05

class ABTestManager:
    """Advanced A/B testing manager for search ranking optimization."""

    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant_id}
        self.experiment_metrics: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def create_experiment(self, experiment: Experiment) -> bool:
        """Create a new A/B test experiment."""
        try:
            # Validate experiment configuration
            self._validate_experiment(experiment)

            # Store experiment
            self.experiments[experiment.experiment_id] = experiment

            # Initialize metrics storage
            self.experiment_metrics[experiment.experiment_id] = {
                'total_impressions': defaultdict(int),
                'total_clicks': defaultdict(int),
                'total_conversions': defaultdict(int),
                'total_relevance_scores': defaultdict(list),
                'average_response_times': defaultdict(list),
                'user_satisfaction_scores': defaultdict(list),
                'variant_users': defaultdict(set)
            }

            self.logger.info(f"Created experiment: {experiment.experiment_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating experiment: {e}")
            return False

    def _validate_experiment(self, experiment: Experiment):
        """Validate experiment configuration."""
        if not experiment.variants:
            raise ValueError("Experiment must have at least one variant")

        total_allocation = sum(v.traffic_allocation for v in experiment.variants)
        if abs(total_allocation - 1.0) > 0.001:
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")

        control_variants = [v for v in experiment.variants if v.is_control]
        if len(control_variants) != 1:
            raise ValueError("Experiment must have exactly one control variant")

    def assign_user_to_variant(self, user_id: str, experiment_id: str) -> str:
        """Assign user to experimental variant based on traffic allocation."""
        if experiment_id not in self.experiments:
            return "default"

        experiment = self.experiments[experiment_id]

        # Check if user is already assigned
        if user_id in self.user_assignments.get(experiment_id, {}):
            return self.user_assignments[experiment_id][user_id]

        # Determine variant assignment using deterministic hash
        user_hash = int(hashlib.md5(f"{user_id}_{experiment_id}".encode()).hexdigest()[:8], 16)
        traffic_value = (user_hash % 1000) / 1000.0

        # Find variant based on traffic allocation
        cumulative_allocation = 0.0
        for variant in experiment.variants:
            cumulative_allocation += variant.traffic_allocation
            if traffic_value <= cumulative_allocation:
                assignment = variant.variant_id
                break
        else:
            assignment = experiment.variants[-1].variant_id  # Fallback to last variant

        # Store assignment
        if experiment_id not in self.user_assignments:
            self.user_assignments[experiment_id] = {}
        self.user_assignments[experiment_id][user_id] = assignment

        # Track user in variant metrics
        self.experiment_metrics[experiment_id]['variant_users'][assignment].add(user_id)

        return assignment

    def record_impression(self, user_id: str, experiment_id: str, variant_id: str,
                          result_position: int, response_time_ms: float):
        """Record impression metric for A/B test analysis."""
        if experiment_id not in self.experiment_metrics:
            return

        metrics = self.experiment_metrics[experiment_id]
        metrics['total_impressions'][variant_id] += 1
        metrics['average_response_times'][variant_id].append(response_time_ms)

    def record_click(self, user_id: str, experiment_id: str, variant_id: str,
                     result_position: int, clicked_result_id: str):
        """Record click metric for A/B test analysis."""
        if experiment_id not in self.experiment_metrics:
            return

        metrics = self.experiment_metrics[experiment_id]
        metrics['total_clicks'][variant_id] += 1

    def record_conversion(self, user_id: str, experiment_id: str, variant_id: str,
                         conversion_type: str, value: float = 1.0):
        """Record conversion metric for A/B test analysis."""
        if experiment_id not in self.experiment_metrics:
            return

        metrics = self.experiment_metrics[experiment_id]
        metrics['total_conversions'][variant_id] += value

    def record_relevance_feedback(self, user_id: str, experiment_id: str, variant_id: str,
                                 relevance_score: float):
        """Record relevance feedback for A/B test analysis."""
        if experiment_id not in self.experiment_metrics:
            return

        metrics = self.experiment_metrics[experiment_id]
        metrics['total_relevance_scores'][variant_id].append(relevance_score)

    def record_satisfaction(self, user_id: str, experiment_id: str, variant_id: str,
                          satisfaction_score: float):
        """Record user satisfaction metric for A/B test analysis."""
        if experiment_id not in self.experiment_metrics:
            return

        metrics = self.experiment_metrics[experiment_id]
        metrics['user_satisfaction_scores'][variant_id].append(satisfaction_score)

    def calculate_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Calculate comprehensive A/B test results."""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}

        experiment = self.experiments[experiment_id]
        metrics = self.experiment_metrics[experiment_id]

        results = {
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'total_impressions': sum(metrics['total_impressions'].values()),
            'variants': []
        }

        control_variant = None

        for variant in experiment.variants:
            variant_metrics = {
                'variant_id': variant.variant_id,
                'variant_name': variant.name,
                'is_control': variant.is_control,
                'impressions': metrics['total_impressions'].get(variant.variant_id, 0),
                'clicks': metrics['total_clicks'].get(variant.variant_id, 0),
                'conversions': metrics['total_conversions'].get(variant.variant_id, 0),
                'unique_users': len(metrics['variant_users'].get(variant.variant_id, set())),
                'click_through_rate': 0.0,
                'conversion_rate': 0.0,
                'avg_relevance_score': 0.0,
                'avg_satisfaction_score': 0.0,
                'avg_response_time_ms': 0.0,
                'statistical_significance': None
            }

            # Calculate rates
            if variant_metrics['impressions'] > 0:
                variant_metrics['click_through_rate'] = (
                    variant_metrics['clicks'] / variant_metrics['impressions']
                )
                variant_metrics['conversion_rate'] = (
                    variant_metrics['conversions'] / variant_metrics['impressions']
                )

            # Calculate averages
            relevance_scores = metrics['total_relevance_scores'].get(variant.variant_id, [])
            if relevance_scores:
                variant_metrics['avg_relevance_score'] = sum(relevance_scores) / len(relevance_scores)

            satisfaction_scores = metrics['user_satisfaction_scores'].get(variant.variant_id, [])
            if satisfaction_scores:
                variant_metrics['avg_satisfaction_score'] = sum(satisfaction_scores) / len(satisfaction_scores)

            response_times = metrics['average_response_times'].get(variant.variant_id, [])
            if response_times:
                variant_metrics['avg_response_time_ms'] = sum(response_times) / len(response_times)

            # Identify control variant for comparison
            if variant.is_control:
                control_variant = variant_metrics

            results['variants'].append(variant_metrics)

        # Calculate statistical significance
        if control_variant and len(results['variants']) > 1:
            for variant in results['variants']:
                if not variant['is_control']:
                    variant['statistical_significance'] = self._calculate_statistical_significance(
                        control_variant, variant, experiment.sample_size
                    )

        results['recommendation'] = self._generate_experiment_recommendation(results['variants'])

        return results

    def _calculate_statistical_significance(self, control: Dict, treatment: Dict,
                                           sample_size: int) -> Dict[str, Any]:
        """Calculate statistical significance using chi-square test."""
        try:
            # Simplified chi-square test for conversion rates
            control_conversions = control['conversions']
            control_non_conversions = control['impressions'] - control_conversions

            treatment_conversions = treatment['conversions']
            treatment_non_conversions = treatment['impressions'] - treatment_conversions

            # Build contingency table
            observed = np.array([
                [control_conversions, control_non_conversions],
                [treatment_conversions, treatment_non_conversions]
            ])

            # Calculate chi-square statistic
            row_sums = observed.sum(axis=1)
            col_sums = observed.sum(axis=0)
            total = observed.sum()

            expected = np.outer(row_sums, col_sums) / total

            # Avoid division by zero
            expected[expected == 0] = 1
            chi2_stat = ((observed - expected) ** 2 / expected).sum()

            # Calculate p-value (simplified)
            from scipy.stats import chi2
            p_value = 1 - chi2.cdf(chi2_stat, df=1)

            # Calculate effect size (Cohen's h)
            prop_control = control_conversions / control['impressions'] if control['impressions'] > 0 else 0
            prop_treatment = treatment_conversions / treatment['impressions'] if treatment['impressions'] > 0 else 0

            # Cohen's h for proportions
            h = 2 * np.arcsin(np.sqrt(prop_treatment)) - 2 * np.arcsin(np.sqrt(prop_control))

            return {
                'chi2_statistic': chi2_stat,
                'p_value': p_value,
                'is_significant': p_value < (1 - experiment.confidence_level),
                'effect_size': h,
                'confidence_interval': self._calculate_effect_size_ci(h, len(control['variant_users']), len(treatment['variant_users']))
            }

        except Exception as e:
            self.logger.error(f"Error calculating statistical significance: {e}")
            return {'error': str(e)}

    def _calculate_effect_size_ci(self, h: float, n1: int, n2: int) -> Tuple[float, float]:
        """Calculate confidence interval for effect size."""
        try:
            # Standard error for Cohen's h
            se = np.sqrt((n1 + n2) / (n1 * n2) * h ** 2 / 4 + 1 / n1 + 1 / n2)
            z_score = 1.96  # 95% confidence interval

            ci_lower = h - z_score * se
            ci_upper = h + z_score * se

            return (max(ci_lower, -1.0), min(ci_upper, 1.0))

        except:
            return (0.0, 0.0)

    def _generate_experiment_recommendation(self, variants: List[Dict]) -> str:
        """Generate recommendation based on A/B test results."""
        if len(variants) < 2:
            return "Insufficient data for recommendation"

        # Find best performing variant (excluding control)
        best_variant = None
        best_score = 0.0

        for variant in variants:
            if not variant['is_control'] and variant['statistical_significance']:
                if variant['statistical_significance']['is_significant']:
                    # Use conversion rate as primary metric
                    score = variant['conversion_rate']
                    if score > best_score:
                        best_score = score
                        best_variant = variant

        if best_variant:
            improvement = ((best_score - next(v['conversion_rate'] for v in variants if v['is_control'])) /
                          next(v['conversion_rate'] for v in variants if v['is_control'])) * 100
            return f"Recommend implementing {best_variant['variant_name']} - {improvement:.1f}% improvement with {best_variant['statistical_significance']['p_value']:.3f} p-value"
        else:
            return "No statistically significant improvement detected. Continue running experiment."

### Multi-Armed Bandit Optimization

```python
class MultiArmedBanditOptimizer:
    """Multi-armed bandit algorithm for dynamic ranking optimization."""

    def __init__(self, bandit_type: str = "thompson_sampling"):
        self.bandit_type = bandit_type
        self.arms = {}  # arm_id -> arm_data
        self.total_pulls = 0
        self.logger = logging.getLogger(__name__)

    def add_arm(self, arm_id: str, initial_config: Dict[str, Any]):
        """Add a new arm (ranking variant) to the bandit."""
        self.arms[arm_id] = {
            'arm_id': arm_id,
            'config': initial_config,
            'pulls': 0,
            'rewards': [],
            'alpha': 1.0,  # Beta distribution alpha
            'beta': 1.0,   # Beta distribution beta
            'mean_reward': 0.0,
            'confidence': 0.0,
            'ucb_value': 0.0
        }

    def select_arm(self, user_context: Optional[Dict] = None) -> str:
        """Select arm based on bandit strategy."""
        if self.bandit_type == "epsilon_greedy":
            return self._epsilon_greedy_select()
        elif self.bandit_type == "ucb":
            return self._ucb_select()
        elif self.bandit_type == "thompson_sampling":
            return self._thompson_sampling_select()
        else:
            return self._round_robin_select()

    def _epsilon_greedy_select(self) -> str:
        """Epsilon-greedy arm selection."""
        epsilon = 0.1  # Exploration rate

        if random.random() < epsilon or self.total_pulls == 0:
            # Exploration: random selection
            return random.choice(list(self.arms.keys()))
        else:
            # Exploitation: select best performing arm
            best_arm = max(self.arms.keys(), key=lambda x: self.arms[x]['mean_reward'])
            return best_arm

    def _ucb_select(self) -> str:
        """Upper Confidence Bound arm selection."""
        if self.total_pulls == 0:
            return random.choice(list(self.arms.keys()))

        # Calculate UCB values
        for arm_id, arm_data in self.arms.items():
            if arm_data['pulls'] == 0:
                arm_data['ucb_value'] = float('inf')
            else:
                confidence = np.sqrt(2 * np.log(self.total_pulls) / arm_data['pulls'])
                arm_data['ucb_value'] = arm_data['mean_reward'] + confidence

        return max(self.arms.keys(), key=lambda x: self.arms[x]['ucb_value'])

    def _thompson_sampling_select(self) -> str:
        """Thompson Sampling arm selection."""
        samples = {}

        for arm_id, arm_data in self.arms.items():
            # Sample from Beta distribution
            sample = np.random.beta(arm_data['alpha'], arm_data['beta'])
            samples[arm_id] = sample

        return max(samples, key=samples.get)

    def _round_robin_select(self) -> str:
        """Round-robin arm selection."""
        if not self.arms:
            return "default"

        arm_ids = list(self.arms.keys())
        return arm_ids[self.total_pulls % len(arm_ids)]

    def update_arm(self, arm_id: str, reward: float):
        """Update arm with observed reward."""
        if arm_id not in self.arms:
            self._add_arm_if_not_exists(arm_id)

        arm = self.arms[arm_id]
        arm['pulls'] += 1
        arm['rewards'].append(reward)
        self.total_pulls += 1

        # Update statistics
        if arm['pulls'] > 0:
            arm['mean_reward'] = sum(arm['rewards']) / arm['pulls']

            # Update Beta distribution parameters for Thompson Sampling
            # alpha = 1 + number of successes
            # beta = 1 + number of failures
            successes = sum(1 for r in arm['rewards'] if r > 0.5)
            failures = arm['pulls'] - successes
            arm['alpha'] = 1 + successes
            arm['beta'] = 1 + failures

    def _add_arm_if_not_exists(self, arm_id: str):
        """Add arm if it doesn't exist."""
        if arm_id not in self.arms:
            self.add_arm(arm_id, {})

    def get_arm_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive statistics for all arms."""
        stats = {}

        for arm_id, arm_data in self.arms.items():
            stats[arm_id] = {
                'pulls': arm_data['pulls'],
                'mean_reward': arm_data['mean_reward'],
                'total_reward': sum(arm_data['rewards']),
                'std_reward': np.std(arm_data['rewards']) if arm_data['rewards'] else 0.0,
                'min_reward': min(arm_data['rewards']) if arm_data['rewards'] else 0.0,
                'max_reward': max(arm_data['rewards']) if arm_data['rewards'] else 0.0,
                'confidence_interval': self._calculate_confidence_interval(arm_data),
                'win_rate': sum(1 for r in arm_data['rewards'] if r > 0.5) / len(arm_data['rewards']) if arm_data['rewards'] else 0.0
            }

        return stats

    def _calculate_confidence_interval(self, arm_data: Dict, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for arm performance."""
        if arm_data['pulls'] < 2:
            return (0.0, 1.0)

        mean = arm_data['mean_reward']
        std = np.std(arm_data['rewards']) if len(arm_data['rewards']) > 1 else 0.0
        n = arm_data['pulls']

        # Calculate standard error
        se = std / np.sqrt(n)

        # Calculate margin of error
        from scipy.stats import t
        margin = t.ppf((1 + confidence) / 2, n - 1) * se

        return (mean - margin, mean + margin)

class RealTimeOptimizationEngine:
    """Real-time optimization engine combining A/B testing and bandit algorithms."""

    def __init__(self):
        self.ab_test_manager = ABTestManager()
        self.bandit_optimizer = MultiArmedBanditOptimizer()
        self.optimization_history = []
        self.current_config = {}
        self.performance_metrics = defaultdict(list)

    def initialize_optimization(self, config_variants: List[Dict[str, Any]]):
        """Initialize optimization with configuration variants."""
        for i, variant in enumerate(config_variants):
            variant_id = f"variant_{i}"
            bandit_config = {
                'ranking_weights': variant.get('ranking_weights', {}),
                'diversity_factor': variant.get('diversity_factor', 0.1),
                'personalization_strength': variant.get('personalization_strength', 0.5),
                'freshness_boost': variant.get('freshness_boost', 0.1)
            }
            self.bandit_optimizer.add_arm(variant_id, bandit_config)

        self.current_config = config_variants[0] if config_variants else {}

    def get_optimized_ranking_config(self, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get optimized ranking configuration using bandit algorithm."""
        selected_arm_id = self.bandit_optimizer.select_arm(user_context)
        selected_config = self.bandit_optimizer.arms[selected_arm_id]['config']

        # Blend with current config for smooth transitions
        blend_factor = 0.8  # 80% new config, 20% current
        optimized_config = {}

        for key, value in selected_config.items():
            current_value = self.current_config.get(key, 0.0)
            optimized_config[key] = blend_factor * value + (1 - blend_factor) * current_value

        return optimized_config

    def update_performance(self, config_id: str, user_feedback: Dict[str, float]):
        """Update performance metrics and feed into bandit algorithm."""
        # Calculate composite reward
        reward_components = [
            user_feedback.get('relevance_score', 0.0) * 0.4,
            user_feedback.get('satisfaction_score', 0.0) * 0.3,
            user_feedback.get('engagement_time', 0.0) * 0.2,
            user_feedback.get('conversion_value', 0.0) * 0.1
        ]

        composite_reward = sum(reward_components)

        # Update bandit
        self.bandit_optimizer.update_arm(config_id, composite_reward)

        # Track optimization history
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'config_id': config_id,
            'reward': composite_reward,
            'components': user_feedback,
            'current_best_arm': self.bandit_optimizer.select_arm()
        })

        # Limit history size
        if len(self.optimization_history) > 10000:
            self.optimization_history = self.optimization_history[-5000:]

    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        arm_stats = self.bandit_optimizer.get_arm_statistics()

        report = {
            'total_optimizations': len(self.optimization_history),
            'arm_performance': arm_stats,
            'best_performing_arm': None,
            'optimization_trend': [],
            'recommendations': []
        }

        # Find best performing arm
        if arm_stats:
            best_arm = max(arm_stats.keys(), key=lambda x: arm_stats[x]['mean_reward'])
            report['best_performing_arm'] = best_arm

        # Calculate optimization trend
        if len(self.optimization_history) >= 100:
            recent_rewards = [entry['reward'] for entry in self.optimization_history[-100:]]
            older_rewards = [entry['reward'] for entry in self.optimization_history[-200:-100]]

            if recent_rewards and older_rewards:
                recent_avg = sum(recent_rewards) / len(recent_rewards)
                older_avg = sum(older_rewards) / len(older_rewards)
                improvement = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
                report['optimization_trend'] = [
                    f"Recent performance: {recent_avg:.3f}",
                    f"Previous performance: {older_avg:.3f}",
                    f"Improvement: {improvement:.1f}%"
                ]

        # Generate recommendations
        report['recommendations'] = self._generate_optimization_recommendations(arm_stats)

        return report

    def _generate_optimization_recommendations(self, arm_stats: Dict[str, Dict]) -> List[str]:
        """Generate optimization recommendations based on performance data."""
        recommendations = []

        if not arm_stats:
            return recommendations

        # Find underperforming arms
        best_performance = max(arm_stats.values(), key=lambda x: x['mean_reward'])
        for arm_id, stats in arm_stats.items():
            if stats['mean_reward'] < best_performance['mean_reward'] * 0.8:
                recommendations.append(
                    f"Consider removing or reconfiguring {arm_id} - "
                    f"performance {stats['mean_reward']:.3f} vs best {best_performance['mean_reward']:.3f}"
                )

        # Check for insufficient exploration
        total_pulls = sum(stats['pulls'] for stats in arm_stats.values())
        if total_pulls < 1000:
            recommendations.append("Increase exploration - insufficient data collected")

        # Check for high variance
        high_variance_arms = [
            arm_id for arm_id, stats in arm_stats.items()
            if stats['std_reward'] > 0.3
        ]
        if high_variance_arms:
            recommendations.append(
                f"High variance detected in arms {high_variance_arm_ids} - consider increasing sample size"
            )

        return recommendations
```

**Use Cases for RAG**: Continuous optimization through A/B testing and multi-armed bandit algorithms, real-time performance monitoring, statistical significance analysis, and automated recommendation generation for search ranking improvements.

**Use Cases for RAG**: Provide highly relevant search results, learn from user feedback, personalize search based on role and context, and continuously improve ranking quality.