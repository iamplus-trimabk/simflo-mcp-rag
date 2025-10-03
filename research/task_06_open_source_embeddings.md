# Task 6: Advanced Open-Source Embedding Models

## Latest 2024 Embedding Models

### State-of-the-Art Text Embeddings

#### BGE (Beijing Academy of Artificial Intelligence) Models
```python
from sentence_transformers import SentenceTransformer

# BGE-Large - Top tier performance (1024 dimensions)
bge_large = SentenceTransformer('BAAI/bge-large-en-v1.5')
# Superior for semantic search and RAG retrieval
# Performance: Beats OpenAI text-embedding-ada-002 on MTEB

# BGE-Base - Balanced performance/speed (768 dimensions)
bge_base = SentenceTransformer('BAAI/bge-base-en-v1.5')
# Good balance of quality and computational efficiency

# BGE-Small - Fast inference (384 dimensions)
bge_small = SentenceTransformer('BAAI/bge-small-en-v1.5')
# 5x faster than BGE-large, suitable for real-time applications

def embed_with_bge(chunks, model_size='base'):
    """Generate embeddings using BGE models."""
    model_map = {
        'large': 'BAAI/bge-large-en-v1.5',
        'base': 'BAAI/bge-base-en-v1.5',
        'small': 'BAAI/bge-small-en-v1.5'
    }

    model = SentenceTransformer(model_map[model_size])
    texts = [chunk['content'] for chunk in chunks]

    # BGE models benefit from longer sequences
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,  # Important for cosine similarity
        batch_size=32,
        show_progress_bar=True
    )

    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i].tolist()
        chunk['embedding_model'] = model_map[model_size]
        chunk['embedding_dimensions'] = embeddings.shape[1]

    return chunks
```

#### E5 Models (Microsoft Research)
```python
# E5-Large - Excellent for retrieval tasks (1024 dimensions)
e5_large = SentenceTransformer('intfloat/e5-large-v2')
# Optimized for search and retrieval tasks
# Requires "query: " and "passage: " prefixes

def embed_with_e5(chunks, is_query=False):
    """Generate embeddings using E5 models with proper prefixes."""
    model = SentenceTransformer('intfloat/e5-large-v2')

    # Add required prefixes for optimal performance
    prefix = "query: " if is_query else "passage: "
    texts = [prefix + chunk['content'] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32
    )

    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i].tolist()
        chunk['embedding_model'] = 'intfloat/e5-large-v2'
        chunk['embedding_dimensions'] = 1024

    return chunks

# E5-Base - Smaller alternative (768 dimensions)
e5_base = SentenceTransformer('intfloat/e5-base-v2')
```

#### Jina Embeddings V2
```python
# Jina Embeddings V2 Base Code - Multilingual code embeddings (768 dimensions)
jina_code = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')
# Supports 30+ programming languages and English
# 8192 token context length for long code sequences

def embed_code_with_jina(code_chunks):
    """Generate embeddings for code using Jina V2."""
    model = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')

    texts = [chunk['content'] for chunk in code_chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=16,  # Smaller batch for long sequences
        truncation=True  # Handle very long code snippets
    )

    for i, chunk in enumerate(code_chunks):
        chunk['embedding'] = embeddings[i].tolist()
        chunk['embedding_model'] = 'jinaai/jina-embeddings-v2-base-code'
        chunk['embedding_dimensions'] = 768

    return code_chunks

# Jina Embeddings V2 Small - Faster general text embeddings (512 dimensions)
jina_small = SentenceTransformer('jinaai/jina-embeddings-v2-small-en')
```

### Advanced Code Embedding Models

#### CodeT5+ and Code-Specific Models
```python
from transformers import AutoTokenizer, AutoModel
import torch

# SFR-Embedding-Code-400M - Specialized for code semantic search
def embed_with_sfr_code(code_chunks):
    """Generate embeddings using SFR specialized code model."""
    tokenizer = AutoTokenizer.from_pretrained('Salesforce/SFR-Embedding-Code-400M_R')
    model = AutoModel.from_pretrained('Salesforce/SFR-Embedding-Code-400M_R')

    embeddings = []

    for chunk in code_chunks:
        # Prepare input with special tokens for code
        inputs = tokenizer(
            chunk['content'],
            return_tensors='pt',
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
            # Use mean pooling of last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=0)
            embeddings.append(embedding.tolist())

        chunk['embedding'] = embeddings[-1]
        chunk['embedding_model'] = 'Salesforce/SFR-Embedding-Code-400M_R'
        chunk['embedding_dimensions'] = 768

    return code_chunks

# CodeT5+ for code understanding
def embed_with_codet5(code_chunks):
    """Generate embeddings using CodeT5+ model."""
    tokenizer = AutoTokenizer.from_pretrained('Salesforce/codet5p-770m-py')
    model = AutoModel.from_pretrained('Salesforce/codet5p-770m-py')

    for chunk in code_chunks:
        inputs = tokenizer(
            chunk['content'],
            return_tensors='pt',
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state[0, 0].numpy()  # [CLS] token
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            chunk['embedding'] = embedding.tolist()
            chunk['embedding_model'] = 'Salesforce/codet5p-770m-py'
            chunk['embedding_dimensions'] = 768

    return code_chunks
```

## Hybrid Embedding Strategies

### Multi-Model Ensemble Approach
```python
import numpy as np
from typing import List, Dict

class HybridEmbeddingGenerator:
    def __init__(self):
        # Initialize multiple models
        self.text_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.code_model = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')
        self.fallback_model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_ensemble_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings using ensemble of models."""
        for chunk in chunks:
            content_type = chunk.get('type', 'text')
            content = chunk['content']

            if content_type in ['function', 'class', 'method']:
                # Use specialized code model
                code_embedding = self.code_model.encode(content)
                text_embedding = self.text_model.encode(content)

                # Weighted combination (60% code, 40% text)
                combined_embedding = (
                    0.6 * code_embedding / np.linalg.norm(code_embedding) +
                    0.4 * text_embedding / np.linalg.norm(text_embedding)
                )

            elif content_type in ['documentation', 'markdown', 'comment']:
                # Use text model with code awareness
                text_embedding = self.text_model.encode(content)
                code_embedding = self.code_model.encode(content)

                # Weighted combination (30% code, 70% text)
                combined_embedding = (
                    0.3 * code_embedding / np.linalg.norm(code_embedding) +
                    0.7 * text_embedding / np.linalg.norm(text_embedding)
                )

            else:
                # Use fallback model for unknown types
                combined_embedding = self.fallback_model.encode(content)

            # Normalize final embedding
            combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)

            chunk['embedding'] = combined_embedding.tolist()
            chunk['embedding_model'] = 'hybrid_ensemble'
            chunk['embedding_dimensions'] = len(combined_embedding)

        return chunks

    def generate_query_embedding(self, query: str, query_type: str = 'text') -> np.ndarray:
        """Generate embedding for search queries."""
        if query_type == 'code':
            # Prioritize code model for code searches
            code_emb = self.code_model.encode(query)
            text_emb = self.text_model.encode(query)
            combined = 0.7 * code_emb + 0.3 * text_emb
        else:
            # Use text model for general searches
            combined = self.text_model.encode(query)

        return combined / np.linalg.norm(combined)
```

### Context-Aware Embedding Selection
```python
class AdaptiveEmbeddingSelector:
    def __init__(self):
        self.models = {
            'technical_docs': SentenceTransformer('BAAI/bge-large-en-v1.5'),
            'code': SentenceTransformer('jinaai/jina-embeddings-v2-base-code'),
            'api_docs': SentenceTransformer('intfloat/e5-base-v2'),
            'general': SentenceTransformer('all-MiniLM-L6-v2')
        }

    def select_model(self, chunk: Dict) -> str:
        """Select appropriate model based on content characteristics."""
        content = chunk['content'].lower()
        chunk_type = chunk.get('type', 'text')

        # API documentation patterns
        if any(keyword in content for keyword in ['endpoint', 'api', 'response', 'request']):
            return 'api_docs'

        # Heavy code patterns
        if chunk_type in ['function', 'class'] or 'def ' in content or 'class ' in content:
            return 'code'

        # Technical documentation patterns
        if any(keyword in content for keyword in ['architecture', 'system', 'design', 'implementation']):
            return 'technical_docs'

        return 'general'

    def generate_adaptive_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings using adaptive model selection."""
        for chunk in chunks:
            model_type = self.select_model(chunk)
            model = self.models[model_type]

            # Add model-specific preprocessing
            content = self.preprocess_content(chunk['content'], model_type)

            embedding = model.encode(content)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize

            chunk['embedding'] = embedding.tolist()
            chunk['embedding_model'] = model_type
            chunk['embedding_dimensions'] = len(embedding)

        return chunks

    def preprocess_content(self, content: str, model_type: str) -> str:
        """Apply model-specific preprocessing."""
        if model_type == 'api_docs':
            # Add prefixes for API docs
            return f"API documentation: {content}"
        elif model_type == 'code':
            # Preserve code structure
            return content
        else:
            return content
```

## Advanced Caching and Optimization

### Redis-Based Distributed Caching
```python
import redis
import json
import pickle
import hashlib
from typing import Optional, List

class RedisEmbeddingCache:
    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self.redis_client = redis.from_url(redis_url)
        self.local_cache = {}
        self.local_cache_size = 1000

    def _get_content_hash(self, content: str, model_name: str) -> str:
        """Generate hash for content-model combination."""
        combined = f"{model_name}:{content}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_embedding(self, content: str, model_name: str) -> Optional[List[float]]:
        """Get embedding from cache (local + Redis)."""
        content_hash = self._get_content_hash(content, model_name)

        # Check local cache first
        if content_hash in self.local_cache:
            return self.local_cache[content_hash]

        # Check Redis cache
        cached_data = self.redis_client.get(f"embedding:{content_hash}")
        if cached_data:
            embedding = json.loads(cached_data)
            # Store in local cache
            self._update_local_cache(content_hash, embedding)
            return embedding

        return None

    def store_embedding(self, content: str, model_name: str, embedding: List[float]):
        """Store embedding in both local and Redis caches."""
        content_hash = self._get_content_hash(content, model_name)

        # Store in local cache
        self._update_local_cache(content_hash, embedding)

        # Store in Redis with TTL (7 days)
        self.redis_client.setex(
            f"embedding:{content_hash}",
            604800,  # 7 days in seconds
            json.dumps(embedding)
        )

    def _update_local_cache(self, key: str, value: List[float]):
        """Update LRU local cache."""
        if len(self.local_cache) >= self.local_cache_size:
            # Remove oldest item (simple FIFO)
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]

        self.local_cache[key] = value

    def batch_get_embeddings(self, contents: List[str], model_name: str) -> Dict[str, Optional[List[float]]]:
        """Batch get embeddings from cache."""
        results = {}

        for content in contents:
            embedding = self.get_embedding(content, model_name)
            results[content] = embedding

        return results

    def close(self):
        """Cleanup resources."""
        self.redis_client.close()
```

### GPU-Accelerated Batch Processing
```python
import torch
from torch.utils.data import DataLoader
from typing import List, Dict

class GPUEmbeddingProcessor:
    def __init__(self, model_name: str = 'BAAI/bge-large-en-v1.5', device: str = 'auto'):
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        self.model = SentenceTransformer(model_name, device=self.device)
        self.model.eval()

    def process_large_batch(self, chunks: List[Dict], batch_size: int = 128) -> List[Dict]:
        """Process large batches efficiently on GPU."""
        if self.device == 'cpu':
            # Smaller batches for CPU
            batch_size = min(batch_size, 32)

        texts = [chunk['content'] for chunk in chunks]

        # Process in optimal batch sizes
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_chunks = chunks[i:i+batch_size]

            with torch.no_grad():
                embeddings = self.model.encode(
                    batch_texts,
                    normalize_embeddings=True,
                    batch_size=batch_size,
                    device=self.device
                )

            # Update chunks with embeddings
            for j, chunk in enumerate(batch_chunks):
                chunk['embedding'] = embeddings[j].tolist()
                chunk['embedding_model'] = self.model._modules['0'].auto_model.name_or_path
                chunk['embedding_dimensions'] = embeddings.shape[1]
                chunk['processing_device'] = self.device

        return chunks

    def get_processing_stats(self) -> Dict:
        """Get processing statistics."""
        return {
            'device': self.device,
            'model_name': self.model._modules['0'].auto_model.name_or_path,
            'gpu_available': torch.cuda.is_available(),
            'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None
        }
```

### Embedding Quality Assessment
```python
class EmbeddingQualityAssessment:
    def __init__(self):
        self.quality_metrics = {}

    def assess_embedding_quality(self, chunks: List[Dict]) -> Dict:
        """Assess quality of generated embeddings."""
        if not chunks or 'embedding' not in chunks[0]:
            return {'error': 'No embeddings found'}

        embeddings = np.array([chunk['embedding'] for chunk in chunks])

        quality_report = {
            'total_embeddings': len(embeddings),
            'embedding_dimensions': embeddings.shape[1],
            'average_norm': np.mean(np.linalg.norm(embeddings, axis=1)),
            'norm_std': np.std(np.linalg.norm(embeddings, axis=1)),
            'pairwise_similarities': self._compute_pairwise_similarities(embeddings),
            'diversity_score': self._compute_diversity_score(embeddings),
            'recommendations': []
        }

        # Generate recommendations
        if quality_report['norm_std'] > 0.1:
            quality_report['recommendations'].append(
                "High variance in embedding norms - consider better normalization"
            )

        if quality_report['diversity_score'] < 0.3:
            quality_report['recommendations'].append(
                "Low diversity - embeddings may be too similar"
            )

        return quality_report

    def _compute_pairwise_similarities(self, embeddings: np.ndarray) -> Dict:
        """Compute pairwise similarity statistics."""
        from sklearn.metrics.pairwise import cosine_similarity

        # Sample for large matrices to avoid memory issues
        sample_size = min(100, len(embeddings))
        sample_indices = np.random.choice(len(embeddings), sample_size, replace=False)
        sample_embeddings = embeddings[sample_indices]

        similarities = cosine_similarity(sample_embeddings)

        # Remove diagonal (self-similarities)
        mask = ~np.eye(similarities.shape[0], dtype=bool)
        similarities = similarities[mask]

        return {
            'mean': float(np.mean(similarities)),
            'std': float(np.std(similarities)),
            'min': float(np.min(similarities)),
            'max': float(np.max(similarities))
        }

    def _compute_diversity_score(self, embeddings: np.ndarray) -> float:
        """Compute diversity score based on pairwise distances."""
        from sklearn.metrics.pairwise import euclidean_distances

        # Sample for efficiency
        sample_size = min(50, len(embeddings))
        sample_indices = np.random.choice(len(embeddings), sample_size, replace=False)
        sample_embeddings = embeddings[sample_indices]

        distances = euclidean_distances(sample_embeddings)

        # Remove diagonal (self-distances)
        mask = ~np.eye(distances.shape[0], dtype=bool)
        distances = distances[mask]

        # Normalize by maximum possible distance
        max_distance = np.sqrt(2) * np.max(np.linalg.norm(embeddings, axis=1))
        diversity = np.mean(distances) / max_distance

        return float(diversity)
```

## Integration with RAG Pipeline

### Complete Embedding Pipeline
```python
class RAGEmbeddingPipeline:
    def __init__(self, config: Dict):
        self.config = config
        self.cache = RedisEmbeddingCache(config.get('redis_url'))
        self.processor = GPUEmbeddingProcessor(
            config.get('model_name', 'BAAI/bge-large-en-v1.5'),
            config.get('device', 'auto')
        )
        self.quality_assessor = EmbeddingQualityAssessment()

    def process_repository(self, chunks: List[Dict]) -> Dict:
        """Complete embedding processing pipeline."""
        print(f"Processing {len(chunks)} chunks for embeddings...")

        # Check cache first
        uncached_chunks = []
        for chunk in chunks:
            cached_embedding = self.cache.get_embedding(
                chunk['content'],
                chunk.get('preferred_model', self.config.get('default_model'))
            )

            if cached_embedding:
                chunk['embedding'] = cached_embedding
                chunk['from_cache'] = True
            else:
                uncached_chunks.append(chunk)
                chunk['from_cache'] = False

        print(f"Cached embeddings: {len(chunks) - len(uncached_chunks)}")
        print(f"Generating new embeddings: {len(uncached_chunks)}")

        # Process uncached chunks
        if uncached_chunks:
            processed_chunks = self.processor.process_large_batch(uncached_chunks)

            # Store in cache
            for chunk in processed_chunks:
                self.cache.store_embedding(
                    chunk['content'],
                    chunk['embedding_model'],
                    chunk['embedding']
                )

        # Quality assessment
        quality_report = self.quality_assessor.assess_embedding_quality(chunks)

        # Generate processing report
        report = {
            'total_chunks': len(chunks),
            'cached_chunks': len(chunks) - len(uncached_chunks),
            'processed_chunks': len(uncached_chunks),
            'cache_hit_rate': (len(chunks) - len(uncached_chunks)) / len(chunks),
            'quality_assessment': quality_report,
            'processing_stats': self.processor.get_processing_stats(),
            'models_used': list(set(chunk.get('embedding_model', 'unknown') for chunk in chunks))
        }

        self.cache.close()
        return {
            'chunks': chunks,
            'report': report
        }

# Usage example
pipeline_config = {
    'model_name': 'BAAI/bge-large-en-v1.5',
    'redis_url': 'redis://localhost:6379',
    'device': 'auto',
    'default_model': 'BAAI/bge-large-en-v1.5'
}

pipeline = RAGEmbeddingPipeline(pipeline_config)
result = pipeline.process_repository(repository_chunks)
print(f"Processing complete: {result['report']}")
```

**Use Cases for RAG**: State-of-the-art embedding quality with 2024 models, intelligent model selection for different content types, GPU-accelerated processing for large repositories, distributed caching for scalability, and comprehensive quality assessment for reliable embeddings.