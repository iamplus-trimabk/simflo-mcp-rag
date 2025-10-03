# Task 7: Comprehensive Vector Database Analysis and Optimization

## Overview

Modern RAG systems require sophisticated vector database solutions that can handle large-scale embeddings, provide high-performance search, and offer flexible deployment options. This comprehensive analysis covers multiple vector database alternatives with detailed performance comparisons, optimization strategies, and production-ready configurations.

## Advanced Vector Database Ecosystem

### Database Comparison Matrix

| Database | Best For | Scale | Performance | Features | Deployment |
|----------|-----------|-------|-------------|----------|------------|
| **Weaviate** | Enterprise RAG | Large | High | GraphQL, Multi-modal | Cloud/Hybrid |
| **Milvus** | High-Performance | Very Large | Very High | Distributed, Zilliz Cloud | Self-hosted |
| **ChromaDB** | Development | Small-Medium | Medium | Simple, In-memory | Local/Cloud |
| **Qdrant** | Production | Medium-Large | High | Rust-based, Quantization | Cloud/Edge |
| **Pinecone** | Serverless | Large | High | Managed, Auto-scaling | SaaS |
| **Vald** | Distributed | Very Large | High | NGT, Edge Computing | Kubernetes |
| **Elasticsearch** | Enterprise Search | Large | Medium | Full-text + Vector | Hybrid |
| **pgvector** | PostgreSQL Apps | Medium | Medium | SQL + Vector | Self-hosted |

## Weaviate: Enterprise-Grade Vector Database

### Advanced Docker Configuration
```yaml
# docker-compose.weaviate.yml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:1.24.4
    restart: on-failure:0
    ports:
      - "8080:8080"
      - "8081:8081"  # GraphQL Playground
      - "6060:6060"  # Prometheus metrics
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: "/var/lib/weaviate"
      DEFAULT_VECTORIZER_MODULE: "none"
      ENABLE_MODULES: "text2vec-openai,generative-openai,qna-openai"
      CLUSTER_HOSTNAME: "node1"
      AUTOSCHEMA_ENABLED: 'false'
      # Performance optimizations
      LIMIT_BATCH_SIZE: 1000
      ASYNC_INDEXING: 'true'
      SHARDS_COUNT: 1
      REPLICATION_FACTOR: 1
      # Resource limits
      GOGC: 100
      GOMEMLIMIT: 4GiB
    volumes:
      - ./weaviate_data:/var/lib/weaviate
      - ./weaviate_config:/weaviate_config
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

volumes:
  weaviate_data:
  weaviate_config:
  redis_data:
```

### Production-Ready Schema Design
```python
import weaviate
from weaviate.util import generate_uuid5
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class AdvancedWeaviateManager:
    """Enterprise-grade Weaviate management with advanced features."""

    def __init__(self, url: str = "http://localhost:8080"):
        self.client = weaviate.Client(url)
        self.schema_config = self._get_comprehensive_schema()

    def _get_comprehensive_schema(self) -> Dict:
        """Define comprehensive schema for RAG system."""
        return {
            "classes": [
                {
                    "class": "CodeRepository",
                    "description": "Repository metadata and overview",
                    "properties": [
                        {"name": "name", "dataType": ["string"]},
                        {"name": "description", "dataType": ["text"]},
                        {"name": "url", "dataType": ["string"]},
                        {"name": "language", "dataType": ["string"]},
                        {"name": "framework", "dataType": ["string"]},
                        {"name": "license", "dataType": ["string"]},
                        {"name": "last_updated", "dataType": ["date"]},
                        {"name": "stars", "dataType": ["int"]},
                        {"name": "forks", "dataType": ["int"]},
                        {"name": "contributors", "dataType": ["int"]},
                        {"name": "topics", "dataType": ["text[]"]},
                        {"name": "repository_size", "dataType": ["int"]},
                        {"name": "is_active", "dataType": ["boolean"]},
                        {"name": "metadata", "dataType": ["object"]}
                    ],
                    "vectorizer": "none",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada-002",
                            "type": "text"
                        }
                    }
                },
                {
                    "class": "CodeChunk",
                    "description": "Individual code chunks with rich metadata",
                    "properties": [
                        {"name": "content", "dataType": ["text"]},
                        {"name": "file_path", "dataType": ["string"]},
                        {"name": "content_type", "dataType": ["string"]},
                        {"name": "language", "dataType": ["string"]},
                        {"name": "framework", "dataType": ["string"]},
                        {"name": "function_name", "dataType": ["string"]},
                        {"name": "class_name", "dataType": ["string"]},
                        {"name": "start_line", "dataType": ["int"]},
                        {"name": "end_line", "dataType": ["int"]},
                        {"name": "complexity", "dataType": ["int"]},
                        {"name": "token_count", "dataType": ["int"]},
                        {"name": "is_test", "dataType": ["boolean"]},
                        {"name": "is_documented", "dataType": ["boolean"]},
                        {"name": "dependencies", "dataType": ["string[]"]},
                        {"name": "imports", "dataType": ["string[]"]},
                        {"name": "user_roles", "dataType": ["string[]"]},
                        {"name": "tags", "dataType": ["string[]"]},
                        {"name": "commit_hash", "dataType": ["string"]},
                        {"name": "author", "dataType": ["string"]},
                        {"name": "created_at", "dataType": ["date"]},
                        {"name": "updated_at", "dataType": ["date"]},
                        {"name": "embedding_model", "dataType": ["string"]},
                        {"name": "chunk_version", "dataType": ["int"]},
                        {"name": "repository", "dataType": ["CodeRepository"]},
                        {"name": "related_chunks", "dataType": ["CodeChunk"]},
                        {"name": "parent_chunk", "dataType": ["CodeChunk"]},
                        {"name": "quality_score", "dataType": ["number"]},
                        {"name": "popularity_score", "dataType": ["number"]},
                        {"name": "metadata", "dataType": ["object"]}
                    ],
                    "vectorizer": "none",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada-002",
                            "type": "text"
                        },
                        "qna-openai": {
                            "model": "gpt-3.5-turbo"
                        }
                    },
                    "invertedIndexConfig": {
                        "bm25": {
                            "k1": 1.2,
                            "b": 0.75
                        },
                        "cleanupIntervalSeconds": 60,
                        "stopwords": {
                            "preset": "en",
                            "additions": ["def", "class", "function", "import", "from"]
                        }
                    }
                },
                {
                    "class": "Documentation",
                    "description": "Documentation and comments",
                    "properties": [
                        {"name": "content", "dataType": ["text"]},
                        {"name": "doc_type", "dataType": ["string"]},
                        {"name": "format", "dataType": ["string"]},
                        {"name": "language", "dataType": ["string"]},
                        {"name": "file_path", "dataType": ["string"]},
                        {"name": "section", "dataType": ["string"]},
                        {"name": "level", "dataType": ["string"]},
                        {"name": "target_audience", "dataType": ["string[]"]},
                        {"name": "prerequisites", "dataType": ["string[]"]},
                        {"name": "learning_objectives", "dataType": ["string[]"]},
                        {"name": "related_chunks", "dataType": ["CodeChunk"]},
                        {"name": "repository", "dataType": ["CodeRepository"]},
                        {"name": "created_at", "dataType": ["date"]},
                        {"name": "updated_at", "dataType": ["date"]},
                        {"name": "quality_score", "dataType": ["number"]}
                    ],
                    "vectorizer": "none"
                },
                {
                    "class": "SearchQuery",
                    "description": "Search query logs for analytics",
                    "properties": [
                        {"name": "query_text", "dataType": ["text"]},
                        {"name": "query_embedding", "dataType": ["number[]"]},
                        {"name": "user_id", "dataType": ["string"]},
                        {"name": "user_role", "dataType": ["string"]},
                        {"name": "context", "dataType": ["text"]},
                        {"name": "filters", "dataType": ["object"]},
                        {"name": "results_count", "dataType": ["int"]},
                        {"name": "response_time_ms", "dataType": ["int"]},
                        {"name": "clicked_results", "dataType": ["string[]"]},
                        {"name": "satisfaction_score", "dataType": ["number"]},
                        {"name": "timestamp", "dataType": ["date"]},
                        {"name": "session_id", "dataType": ["string"]},
                        {"name": "embedding_model", "dataType": ["string"]}
                    ],
                    "vectorizer": "none"
                }
            ]
        }

    def setup_schema(self) -> bool:
        """Setup comprehensive schema with error handling."""
        try:
            # Check existing schema
            existing_classes = [c['class'] for c in self.client.schema.get()['classes']]

            for class_config in self.schema_config['classes']:
                class_name = class_config['class']
                if class_name not in existing_classes:
                    self.client.schema.create_class(class_config)
                    print(f"Created class: {class_name}")
                else:
                    print(f"Class {class_name} already exists")

            return True
        except Exception as e:
            print(f"Error setting up schema: {e}")
            return False

    def batch_insert_chunks(self, chunks: List[Dict], batch_size: int = 100) -> Dict[str, int]:
        """Efficient batch insertion with progress tracking."""
        results = {"success": 0, "failed": 0}

        with self.client.batch as batch:
            batch.batch_size = batch_size
            batch.dynamic = True

            for i, chunk in enumerate(chunks):
                try:
                    # Prepare data object
                    data_object = self._prepare_chunk_data(chunk)

                    # Generate deterministic UUID
                    uuid = generate_uuid5(chunk['content'])

                    # Add to batch
                    batch.add_data_object(
                        data_object=data_object,
                        class_name="CodeChunk",
                        uuid=uuid
                    )

                    results["success"] += 1

                    if i % 100 == 0:
                        print(f"Processed {i}/{len(chunks)} chunks")

                except Exception as e:
                    print(f"Error inserting chunk {i}: {e}")
                    results["failed"] += 1

        return results

    def _prepare_chunk_data(self, chunk: Dict) -> Dict:
        """Prepare chunk data for Weaviate insertion."""
        return {
            "content": chunk.get('content', ''),
            "file_path": chunk.get('file_path', ''),
            "content_type": chunk.get('type', 'unknown'),
            "language": chunk.get('language', ''),
            "framework": chunk.get('framework', ''),
            "function_name": chunk.get('name', ''),
            "class_name": chunk.get('class_name', ''),
            "start_line": chunk.get('start_line', 0),
            "end_line": chunk.get('end_line', 0),
            "complexity": chunk.get('complexity', 1),
            "token_count": chunk.get('token_count', 0),
            "is_test": chunk.get('is_test', False),
            "is_documented": chunk.get('is_documented', False),
            "dependencies": chunk.get('dependencies', []),
            "imports": chunk.get('imports', []),
            "user_roles": chunk.get('user_roles', []),
            "tags": chunk.get('tags', []),
            "commit_hash": chunk.get('commit_hash', ''),
            "author": chunk.get('author', ''),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "embedding_model": chunk.get('embedding_model', 'unknown'),
            "chunk_version": chunk.get('chunk_version', 1),
            "quality_score": chunk.get('quality_score', 0.0),
            "popularity_score": chunk.get('popularity_score', 0.0),
            "metadata": chunk.get('metadata', {})
        }
```

### Advanced Search Capabilities
```python
class AdvancedWeaviateSearch:
    """Advanced search with hybrid queries and filtering."""

    def __init__(self, client: weaviate.Client):
        self.client = client

    def hybrid_search(self, query_text: str, query_embedding: List[float],
                     filters: Optional[Dict] = None, limit: int = 10,
                     alpha: float = 0.75) -> List[Dict]:
        """Hybrid search combining keyword and semantic search."""

        search_query = (
            self.client.query
            .get("CodeChunk", [
                "content", "file_path", "function_name", "class_name",
                "language", "framework", "start_line", "end_line",
                "complexity", "user_roles", "tags", "quality_score",
                "is_documented", "metadata"
            ])
            .with_hybrid(
                query=query_text,
                vector=query_embedding,
                alpha=alpha,  # Weight for semantic vs keyword search
                query_params={
                    "searches": [
                        {
                            "nearVector": {
                                "vector": query_embedding,
                                "certainty": 0.7
                            }
                        },
                        {
                            "bm25": {
                                "query": query_text,
                                "properties": ["content", "function_name", "class_name"]
                            }
                        }
                    ]
                }
            )
        )

        # Add filters if provided
        if filters:
            search_query = search_query.with_where(self._build_where_clause(filters))

        # Execute search
        result = search_query.with_limit(limit).do()

        return result["data"]["Get"]["CodeChunk"]

    def semantic_search_with_reranking(self, query_embedding: List[float],
                                     filters: Optional[Dict] = None,
                                     limit: int = 20, rerank_top_k: int = 5) -> List[Dict]:
        """Semantic search with relevance reranking."""

        # Initial broader search
        initial_results = self._base_vector_search(
            query_embedding, filters, limit
        )

        # Rerank based on multiple factors
        reranked_results = self._rerank_results(
            initial_results, query_embedding, rerank_top_k
        )

        return reranked_results

    def _base_vector_search(self, query_embedding: List[float],
                           filters: Optional[Dict] = None,
                           limit: int = 20) -> List[Dict]:
        """Base vector search implementation."""

        search_query = (
            self.client.query
            .get("CodeChunk", [
                "content", "file_path", "function_name", "class_name",
                "language", "quality_score", "user_roles", "metadata"
            ])
            .with_near_vector({
                "vector": query_embedding,
                "certainty": 0.6  # Lower threshold for broader search
            })
        )

        if filters:
            search_query = search_query.with_where(self._build_where_clause(filters))

        result = search_query.with_limit(limit).do()
        return result["data"]["Get"]["CodeChunk"]

    def _rerank_results(self, results: List[Dict], query_embedding: List[float],
                       top_k: int) -> List[Dict]:
        """Rerank results based on multiple relevance factors."""

        scored_results = []

        for result in results:
            score = self._calculate_relevance_score(result, query_embedding)
            result['_relevance_score'] = score
            scored_results.append(result)

        # Sort by relevance score
        scored_results.sort(key=lambda x: x['_relevance_score'], reverse=True)

        return scored_results[:top_k]

    def _calculate_relevance_score(self, result: Dict, query_embedding: List[float]) -> float:
        """Calculate comprehensive relevance score."""

        base_score = result.get('_additional', {}).get('certainty', 0.0)

        # Quality boost
        quality_boost = result.get('quality_score', 0.0) * 0.2

        # Documentation boost
        doc_boost = 0.1 if result.get('is_documented', False) else 0.0

        # Popularity boost
        popularity_boost = result.get('popularity_score', 0.0) * 0.1

        # Recency boost (if available)
        recency_boost = 0.0
        if 'updated_at' in result:
            # Simple recency calculation
            recency_boost = 0.05  # Placeholder for actual recency logic

        total_score = base_score + quality_boost + doc_boost + popularity_boost + recency_boost

        return min(1.0, total_score)

    def _build_where_clause(self, filters: Dict) -> Dict:
        """Build Weaviate where clause from filters."""
        conditions = []

        for key, value in filters.items():
            if key == "language" and value:
                conditions.append({
                    "path": ["language"],
                    "operator": "Equal",
                    "valueString": value
                })
            elif key == "user_roles" and value:
                conditions.append({
                    "path": ["user_roles"],
                    "operator": "ContainsAny",
                    "valueStringList": [value] if isinstance(value, str) else value
                })
            elif key == "framework" and value:
                conditions.append({
                    "path": ["framework"],
                    "operator": "Equal",
                    "valueString": value
                })
            elif key == "is_test" and value is not None:
                conditions.append({
                    "path": ["is_test"],
                    "operator": "Equal",
                    "valueBoolean": value
                })
            elif key == "quality_score_min" and value:
                conditions.append({
                    "path": ["quality_score"],
                    "operator": "GreaterThanEqual",
                    "valueNumber": value
                })

        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"operator": "And", "operands": conditions}
        else:
            return {}

    def search_analytics(self, query_text: str, query_embedding: List[float],
                        user_id: str, user_role: str, context: str = "",
                        filters: Optional[Dict] = None) -> List[Dict]:
        """Perform search with analytics logging."""

        start_time = time.time()

        # Perform search
        results = self.hybrid_search(query_text, query_embedding, filters)

        # Log search query for analytics
        self._log_search_query(
            query_text, query_embedding, user_id, user_role,
            context, filters, results, time.time() - start_time
        )

        return results

    def _log_search_query(self, query_text: str, query_embedding: List[float],
                         user_id: str, user_role: str, context: str,
                         filters: Optional[Dict], results: List[Dict],
                         response_time: float):
        """Log search query for analytics."""

        try:
            query_data = {
                "query_text": query_text,
                "query_embedding": query_embedding,
                "user_id": user_id,
                "user_role": user_role,
                "context": context,
                "filters": filters or {},
                "results_count": len(results),
                "response_time_ms": int(response_time * 1000),
                "timestamp": datetime.now().isoformat(),
                "embedding_model": "ada-002"  # or get from config
            }

            # Use batch insert for performance
            with self.client.batch as batch:
                batch.batch_size = 1
                batch.add_data_object(
                    data_object=query_data,
                    class_name="SearchQuery",
                    uuid=generate_uuid5(f"{query_text}_{user_id}_{datetime.now().isoformat()}")
                )

        except Exception as e:
            print(f"Error logging search query: {e}")
```

## Milvus: High-Performance Distributed Vector Database

### Advanced Milvus Configuration
```yaml
# docker-compose.milvus.yml
version: '3.5'

services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      ETCD_AUTO_COMPACTION_MODE: revision
      ETCD_AUTO_COMPACTION_RETENTION: 1000
      ETCD_QUOTA_BACKEND_BYTES: 4294967296
      ETCD_SNAPSHOT_COUNT: 50000
    volumes:
      - ./etcd_data:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    healthcheck:
      test: ["CMD", "etcdctl", "endpoint", "health"]
      interval: 30s
      timeout: 20s
      retries: 3

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "9001:9001"
      - "9000:9000"
    volumes:
      - ./minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  milvus:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "standalone"]
    security_opt:
      - seccomp:unconfined
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ./milvus_data:/var/lib/milvus
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      start_period: 90s
      timeout: 20s
      retries: 3
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"

  # Optional: Attu for Milvus management
  attu:
    container_name: milvus-attu
    image: zilliz/attu:v2.3.3
    environment:
      MILVUS_URL: milvus:19530
    ports:
      - "3000:3000"
    depends_on:
      - "milvus"

volumes:
  etcd_data:
  minio_data:
  milvus_data:
```

### Advanced Milvus Client with Optimization
```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from pymilvus import MilvusClient
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import time
import logging

class AdvancedMilvusManager:
    """High-performance Milvus management with optimization."""

    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.client = None
        self.collections = {}
        self.connect()

    def connect(self):
        """Establish connection with retry logic."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                connections.connect("default", host=self.host, port=self.port)
                self.client = MilvusClient(host=self.host, port=self.port)
                print(f"Connected to Milvus at {self.host}:{self.port}")
                return True
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def create_optimized_collection(self, collection_name: str,
                                  embedding_dim: int = 384,
                                  metric_type: str = "COSINE") -> Collection:
        """Create optimized collection with advanced indexing."""

        # Define schema with comprehensive fields
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="framework", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="function_name", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="class_name", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="start_line", dtype=DataType.INT32),
            FieldSchema(name="end_line", dtype=DataType.INT32),
            FieldSchema(name="complexity", dtype=DataType.INT32),
            FieldSchema(name="token_count", dtype=DataType.INT32),
            FieldSchema(name="is_test", dtype=DataType.BOOL),
            FieldSchema(name="is_documented", dtype=DataType.BOOL),
            FieldSchema(name="user_roles", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="quality_score", dtype=DataType.FLOAT),
            FieldSchema(name="popularity_score", dtype=DataType.FLOAT),
            FieldSchema(name="created_at", dtype=DataType.INT64),  # Unix timestamp
            FieldSchema(name="repository_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim)
        ]

        schema = CollectionSchema(fields, f"Optimized RAG collection: {collection_name}")

        # Create collection
        collection = Collection(collection_name, schema)

        # Create optimized index based on data size
        index_params = self._get_optimized_index_params(metric_type, embedding_dim)
        collection.create_index("embedding", index_params)

        # Create index for scalar fields
        scalar_indexes = [
            {"field_name": "content_type", "index_type": "INVERTED"},
            {"field_name": "language", "index_type": "INVERTED"},
            {"field_name": "framework", "index_type": "INVERTED"},
            {"field_name": "user_roles", "index_type": "INVERTED"},
            {"field_name": "quality_score", "index_type": "STL_SORT"}
        ]

        for index_config in scalar_indexes:
            try:
                collection.create_index(
                    field_name=index_config["field_name"],
                    index_params={"index_type": index_config["index_type"]}
                )
            except Exception as e:
                print(f"Index creation for {index_config['field_name']} failed: {e}")

        self.collections[collection_name] = collection
        return collection

    def _get_optimized_index_params(self, metric_type: str, embedding_dim: int) -> Dict:
        """Get optimized index parameters based on dataset characteristics."""

        # For small to medium datasets (< 1M vectors)
        if embedding_dim <= 512:
            return {
                "metric_type": metric_type,
                "index_type": "IVF_FLAT",
                "params": {"nlist": min(1024, embedding_dim * 2)}
            }

        # For larger datasets, use more sophisticated indexing
        return {
            "metric_type": metric_type,
            "index_type": "IVF_PQ",
            "params": {
                "nlist": min(4096, embedding_dim * 4),
                "m": 16,  # PQ parameter
                "nbits": 8  # Bits per vector component
            }
        }

    def optimized_batch_insert(self, collection_name: str, chunks: List[Dict],
                             batch_size: int = 1000) -> Dict[str, int]:
        """High-performance batch insertion with optimization."""

        if collection_name not in self.collections:
            collection = Collection(collection_name)
            self.collections[collection_name] = collection
        else:
            collection = self.collections[collection_name]

        results = {"success": 0, "failed": 0, "total_time": 0}

        start_time = time.time()

        # Pre-allocate data arrays for better performance
        total_chunks = len(chunks)

        for batch_start in range(0, total_chunks, batch_size):
            batch_end = min(batch_start + batch_size, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]

            try:
                # Prepare batch data
                batch_data = self._prepare_batch_data(batch_chunks)

                # Insert batch
                insert_result = collection.insert(batch_data)
                results["success"] += len(batch_chunks)

                print(f"Inserted batch {batch_start//batch_size + 1}: "
                      f"{len(batch_chunks)} chunks")

            except Exception as e:
                print(f"Batch insert failed: {e}")
                results["failed"] += len(batch_chunks)

        # Flush to ensure data persistence
        try:
            collection.flush()
            print("Data flushed to disk")
        except Exception as e:
            print(f"Flush failed: {e}")

        results["total_time"] = time.time() - start_time
        print(f"Total insertion time: {results['total_time']:.2f}s")
        print(f"Average speed: {results['success']/results['total_time']:.2f} chunks/sec")

        return results

    def _prepare_batch_data(self, chunks: List[Dict]) -> List[List]:
        """Prepare batch data for optimal insertion performance."""

        # Pre-allocate lists
        data = [[] for _ in range(20)]  # Match the number of fields

        for chunk in chunks:
            data[0].append(chunk.get('content', ''))
            data[1].append(chunk.get('file_path', ''))
            data[2].append(chunk.get('type', 'unknown'))
            data[3].append(chunk.get('language', ''))
            data[4].append(chunk.get('framework', ''))
            data[5].append(chunk.get('name', ''))
            data[6].append(chunk.get('class_name', ''))
            data[7].append(chunk.get('start_line', 0))
            data[8].append(chunk.get('end_line', 0))
            data[9].append(chunk.get('complexity', 1))
            data[10].append(chunk.get('token_count', 0))
            data[11].append(chunk.get('is_test', False))
            data[12].append(chunk.get('is_documented', False))
            data[13].append(','.join(chunk.get('user_roles', [])))
            data[14].append(','.join(chunk.get('tags', [])))
            data[15].append(chunk.get('quality_score', 0.0))
            data[16].append(chunk.get('popularity_score', 0.0))
            data[17].append(int(time.time()))
            data[18].append(chunk.get('repository_id', ''))
            data[19].append(chunk.get('embedding', []))

        return data

    def advanced_search(self, collection_name: str, query_embedding: List[float],
                       filters: Optional[Dict] = None, limit: int = 10,
                       search_params: Optional[Dict] = None) -> List[Dict]:
        """Advanced search with filtering and optimization."""

        if collection_name not in self.collections:
            collection = Collection(collection_name)
            self.collections[collection_name] = collection
        else:
            collection = self.collections[collection_name]

        # Load collection for search
        collection.load()

        # Default search parameters
        default_search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10, "ef": 64}
        }

        if search_params:
            default_search_params.update(search_params)

        # Build filter expression
        expr = self._build_filter_expression(filters)

        try:
            # Perform search
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=default_search_params,
                limit=limit,
                expr=expr,
                output_fields=[
                    "content", "file_path", "content_type", "language",
                    "framework", "function_name", "class_name", "start_line",
                    "end_line", "complexity", "user_roles", "tags",
                    "quality_score", "popularity_score"
                ]
            )

            # Format results
            formatted_results = []
            for hit in results[0]:
                result_dict = {
                    "id": hit.id,
                    "distance": hit.distance,
                    "score": 1 - hit.distance,  # Convert distance to similarity
                    **hit.entity
                }
                formatted_results.append(result_dict)

            return formatted_results

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def _build_filter_expression(self, filters: Optional[Dict]) -> str:
        """Build Milvus filter expression."""
        if not filters:
            return ""

        conditions = []

        for key, value in filters.items():
            if key == "language" and value:
                conditions.append(f'language == "{value}"')
            elif key == "content_type" and value:
                conditions.append(f'content_type == "{value}"')
            elif key == "framework" and value:
                conditions.append(f'framework == "{value}"')
            elif key == "user_roles" and value:
                if isinstance(value, list):
                    role_conditions = [f'user_roles like "%{role}%"' for role in value]
                    conditions.append(f"({' or '.join(role_conditions)})")
                else:
                    conditions.append(f'user_roles like "%{value}%"')
            elif key == "is_test" and value is not None:
                conditions.append(f'is_test == {str(value).lower()}')
            elif key == "is_documented" and value is not None:
                conditions.append(f'is_documented == {str(value).lower()}')
            elif key == "quality_score_min" and value:
                conditions.append(f'quality_score >= {value}')
            elif key == "complexity_max" and value:
                conditions.append(f'complexity <= {value}')
            elif key == "created_after" and value:
                timestamp = int(value.timestamp())
                conditions.append(f'created_at >= {timestamp}')

        return " and ".join(conditions)

    def performance_optimization_tips(self, collection_name: str) -> Dict[str, Any]:
        """Provide performance optimization recommendations."""

        collection = self.collections.get(collection_name, Collection(collection_name))

        try:
            # Get collection statistics
            stats = collection.describe()
            num_entities = collection.num_entities

            recommendations = {
                "total_vectors": num_entities,
                "recommendations": []
            }

            # Index recommendations
            if num_entities < 10000:
                recommendations["recommendations"].append(
                    "For small datasets (< 10K), consider using FLAT index for exact search"
                )
            elif num_entities < 100000:
                recommendations["recommendations"].append(
                    "For medium datasets (10K-100K), IVF_FLAT provides good balance"
                )
            else:
                recommendations["recommendations"].append(
                    "For large datasets (> 100K), use IVF_PQ or HNSW for better performance"
                )

            # Search parameter recommendations
            if num_entities > 100000:
                recommendations["search_params"] = {
                    "nprobe": min(100, num_entities // 1000),
                    "ef": 64
                }
            else:
                recommendations["search_params"] = {
                    "nprobe": 10,
                    "ef": 32
                }

            # Memory optimization
            recommendations["recommendations"].append(
                "Consider using scalar quantization to reduce memory usage"
            )

            return recommendations

        except Exception as e:
            print(f"Error getting performance tips: {e}")
            return {"error": str(e)}

    def monitor_performance(self, collection_name: str) -> Dict[str, Any]:
        """Monitor collection performance metrics."""

        try:
            # Basic metrics
            collection = self.collections.get(collection_name, Collection(collection_name))

            metrics = {
                "num_entities": collection.num_entities,
                "index_progress": utility.get_index_build_progress(collection_name),
                "load_state": utility.load_state(collection_name)
            }

            return metrics

        except Exception as e:
            print(f"Error monitoring performance: {e}")
            return {"error": str(e)}
```

## Qdrant: Production-Ready Vector Database

### Qdrant Docker Configuration
```yaml
# docker-compose.qdrant.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: qdrant
    ports:
      - "6333:6333"  # HTTP API
      - "6334:6334"  # gRPC API
    volumes:
      - ./qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333
      QDRANT__SERVICE__GRPC_PORT: 6334
      QDRANT__SERVICE__MAX_REQUEST_SIZE_MB: 32
      QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS: 4
      QDRANT__STORAGE__PERFORMANCE__SEARCH_TIMEOUT_SEC: 30
      # Memory settings
      QDRANT__STORAGE__PERFORMANCE__MAX_SEGMENT_SIZE_KB: 2000
      QDRANT__STORAGE__PERFORMANCE__MAX_SEGMENT_SIZE_BATCH: 10000
      # Optimization settings
      QDRANT__STORAGE__OPTIMIZERS__DELETED_THRESHOLD: 0.2
      QDRANT__STORAGE__OPTIMIZERS__VACUUM_THRESHOLD: 0.2
      QDRANT__STORAGE__OPTIMIZERS__INDEXING_THRESHOLD: 0
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
        reservations:
          memory: 1G
          cpus: '0.5'

  # Optional: Qdrant Web UI
  qdrant-web-ui:
    image: fedirz/qdrant-web-ui:latest
    ports:
      - "8000:8000"
    environment:
      QDRANT_URL: http://qdrant:6333
    depends_on:
      - qdrant

volumes:
  qdrant_data:
```

### Advanced Qdrant Client
```python
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from typing import Dict, List, Any, Optional, Union
import numpy as np
import json
from datetime import datetime

class AdvancedQdrantManager:
    """Production-ready Qdrant management with advanced features."""

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_configs = {}

    def create_optimized_collection(self, collection_name: str,
                                 vector_size: int = 384,
                                 distance: Distance = Distance.COSINE) -> bool:
        """Create optimized collection with quantization support."""

        try:
            # Check if collection exists
            if self.client.collection_exists(collection_name):
                print(f"Collection {collection_name} already exists")
                return True

            # Create collection with optimized configuration
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                    # Enable quantization for memory efficiency
                    on_disk=True,
                    # Quantization config
                    quantization_config=models.ScalarQuantization(
                        scalar=models.ScalarQuantizationConfig(
                            type=models.ScalarType.INT8,
                            quantile=0.99,
                            always_ram=False
                        )
                    )
                ),
                # Optimizers configuration
                optimizers_config=models.OptimizersConfigDiff(
                    default_segment_number=2,
                    max_segment_size=20000,
                    memmap_threshold=50000,
                    indexing_threshold=20000,
                    flush_interval_sec=5,
                    max_optimization_threads=1
                ),
                # Performance tuning
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100,
                    full_scan_threshold=10000,
                    max_indexing_threads=4,
                    on_disk=True
                ),
                # WAL configuration
                wal_config=models.WalConfigDiff(
                    wal_capacity_mb=32,
                    wal_segments_ahead=2
                )
            )

            print(f"Created optimized collection: {collection_name}")
            return True

        except Exception as e:
            print(f"Error creating collection {collection_name}: {e}")
            return False

    def create_payload_schema(self, collection_name: str):
        """Define payload schema for structured queries."""

        payload_schema = {
            "content": "text",
            "file_path": "keyword",
            "content_type": "keyword",
            "language": "keyword",
            "framework": "keyword",
            "function_name": "text",
            "class_name": "text",
            "start_line": "integer",
            "end_line": "integer",
            "complexity": "integer",
            "token_count": "integer",
            "is_test": "bool",
            "is_documented": "bool",
            "user_roles": "keyword",
            "tags": "keyword",
            "quality_score": "float",
            "popularity_score": "float",
            "created_at": "integer",
            "repository_id": "keyword",
            "metadata": "json"
        }

        try:
            self.client.update_collection(
                collection_name=collection_name,
                optimizer_config=models.OptimizersConfigDiff(
                    default_segment_number=2,
                    max_segment_size=20000,
                    memmap_threshold=50000,
                    indexing_threshold=20000
                ),
                # Set up payload index for better filtering performance
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100,
                    full_scan_threshold=10000,
                    max_indexing_threads=4
                )
            )
            print(f"Payload schema configured for {collection_name}")
        except Exception as e:
            print(f"Error configuring payload schema: {e}")

    def optimized_batch_upsert(self, collection_name: str, chunks: List[Dict],
                               batch_size: int = 500) -> Dict[str, Any]:
        """High-performance batch upsert with progress tracking."""

        results = {
            "success": 0,
            "failed": 0,
            "batches": 0,
            "start_time": datetime.now()
        }

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            try:
                # Prepare points
                points = []
                for j, chunk in enumerate(batch):
                    point_id = f"{chunk.get('file_path', 'unknown')}_{i + j}"

                    point = models.PointStruct(
                        id=point_id,
                        vector=chunk.get('embedding', []),
                        payload=self._prepare_payload(chunk)
                    )
                    points.append(point)

                # Upsert batch
                upsert_result = self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                    wait=True
                )

                results["success"] += len(points)
                results["batches"] += 1

                print(f"Batch {results['batches']}: Upserted {len(points)} points")

            except Exception as e:
                print(f"Batch upsert failed: {e}")
                results["failed"] += len(batch)

        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        results["throughput"] = results["success"] / results["duration"] if results["duration"] > 0 else 0

        print(f"Upsert completed: {results['success']} points in {results['duration']:.2f}s")
        print(f"Throughput: {results['throughput']:.2f} points/sec")

        return results

    def _prepare_payload(self, chunk: Dict) -> Dict[str, Any]:
        """Prepare payload with structured data."""

        return {
            "content": chunk.get('content', ''),
            "file_path": chunk.get('file_path', ''),
            "content_type": chunk.get('type', 'unknown'),
            "language": chunk.get('language', ''),
            "framework": chunk.get('framework', ''),
            "function_name": chunk.get('name', ''),
            "class_name": chunk.get('class_name', ''),
            "start_line": chunk.get('start_line', 0),
            "end_line": chunk.get('end_line', 0),
            "complexity": chunk.get('complexity', 1),
            "token_count": chunk.get('token_count', 0),
            "is_test": chunk.get('is_test', False),
            "is_documented": chunk.get('is_documented', False),
            "user_roles": chunk.get('user_roles', []),
            "tags": chunk.get('tags', []),
            "quality_score": chunk.get('quality_score', 0.0),
            "popularity_score": chunk.get('popularity_score', 0.0),
            "created_at": int(datetime.now().timestamp()),
            "repository_id": chunk.get('repository_id', ''),
            "metadata": chunk.get('metadata', {})
        }

    def advanced_search(self, collection_name: str, query_vector: List[float],
                       filters: Optional[Dict] = None, limit: int = 10,
                       score_threshold: float = 0.5,
                       search_params: Optional[models.SearchParams] = None,
                       using_vector: str = "vector") -> List[Dict]:
        """Advanced search with comprehensive filtering."""

        # Build filter
        query_filter = self._build_qdrant_filter(filters) if filters else None

        # Default search parameters for performance
        default_search_params = models.SearchParams(
            hnsw_ef=64,
            exact=False,
            quantization=models.QuantizationSearchParams(
                ignore=False,
                rescore=True
            )
        )

        if search_params:
            default_search_params = search_params

        try:
            # Perform search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                search_params=default_search_params,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            formatted_results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                formatted_results.append(result)

            return formatted_results

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def _build_qdrant_filter(self, filters: Dict) -> Filter:
        """Build Qdrant filter from dictionary."""

        conditions = []

        for key, value in filters.items():
            if key == "language" and value:
                conditions.append(FieldCondition(key="language", match=MatchValue(value=value)))
            elif key == "content_type" and value:
                conditions.append(FieldCondition(key="content_type", match=MatchValue(value=value)))
            elif key == "framework" and value:
                conditions.append(FieldCondition(key="framework", match=MatchValue(value=value)))
            elif key == "user_roles" and value:
                if isinstance(value, list):
                    for role in value:
                        conditions.append(FieldCondition(key="user_roles", match=MatchValue(value=role)))
                else:
                    conditions.append(FieldCondition(key="user_roles", match=MatchValue(value=value)))
            elif key == "is_test" and value is not None:
                conditions.append(FieldCondition(key="is_test", match=MatchValue(value=bool(value))))
            elif key == "is_documented" and value is not None:
                conditions.append(FieldCondition(key="is_documented", match=MatchValue(value=bool(value))))
            elif key == "quality_score_min" and value:
                conditions.append(FieldCondition(key="quality_score", range=models.Range(gte=value))))
            elif key == "complexity_max" and value:
                conditions.append(FieldCondition(key="complexity", range=models.Range(lte=value)))

        if not conditions:
            return None

        # Combine conditions with AND
        if len(conditions) == 1:
            return Filter(must=conditions)
        else:
            return Filter(must=conditions)

    def hybrid_search(self, collection_name: str, query_text: str,
                     query_vector: List[float], filters: Optional[Dict] = None,
                     limit: int = 10) -> List[Dict]:
        """Hybrid search combining semantic and keyword search."""

        # For now, implement as semantic search with text matching boost
        semantic_results = self.advanced_search(collection_name, query_vector, filters, limit * 2)

        # Boost results that contain query text
        for result in semantic_results:
            content = result["payload"].get("content", "").lower()
            query_lower = query_text.lower()

            # Text matching boost
            text_match_score = 0.0
            if query_lower in content:
                text_match_score = 0.2
                # Additional boost for exact matches
                words = query_lower.split()
                for word in words:
                    if word in content:
                        text_match_score += 0.05

            result["boosted_score"] = result["score"] + text_match_score

        # Sort by boosted score and return top results
        semantic_results.sort(key=lambda x: x["boosted_score"], reverse=True)
        return semantic_results[:limit]

    def search_with_recommendations(self, collection_name: str, query_vector: List[float],
                                   positive_ids: Optional[List[str]] = None,
                                   negative_ids: Optional[List[str]] = None,
                                   limit: int = 10) -> List[Dict]:
        """Search with recommendation feedback."""

        try:
            # Use context search for recommendations
            search_result = self.client.recommend(
                collection_name=collection_name,
                positive=positive_ids or [],
                negative=negative_ids or [],
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )

            # Format results
            formatted_results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                formatted_results.append(result)

            return formatted_results

        except Exception as e:
            print(f"Recommendation search failed: {e}")
            return []

    def collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get comprehensive collection information."""

        try:
            info = self.client.get_collection(collection_name)

            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "segments_count": info.segments_count,
                "disk_data_size": info.points_data_size,
                "ram_data_size": info.points_ram_data_size,
                "index_data_size": info.index_data_size,
                "vector_index_name": info.config.params.vectors.name,
                "distance": info.config.params.vectors.distance,
                "quantization": info.config.quantization_config.dict() if info.config.quantization_config else None,
                "optimizer": info.config.optimizer_config.dict() if info.config.optimizer_config else None
            }

        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {"error": str(e)}

    def performance_monitoring(self, collection_name: str) -> Dict[str, Any]:
        """Monitor collection performance and health."""

        try:
            info = self.collection_info(collection_name)

            performance_metrics = {
                "collection_info": info,
                "health_status": "healthy",
                "recommendations": []
            }

            # Memory usage analysis
            if info.get("disk_data_size", 0) > 0:
                ram_usage_ratio = info.get("ram_data_size", 0) / info.get("disk_data_size", 1)
                if ram_usage_ratio > 0.5:
                    performance_metrics["recommendations"].append(
                        "Consider enabling more aggressive disk-based storage to reduce RAM usage"
                    )

            # Index optimization recommendations
            if info.get("vectors_count", 0) > 100000:
                performance_metrics["recommendations"].append(
                    "Large collection detected - ensure HNSW parameters are optimized for your use case"
                )

            return performance_metrics

        except Exception as e:
            return {"error": str(e), "health_status": "unhealthy"}
```

**Use Cases for RAG**: Enterprise-grade vector storage with advanced filtering, high-performance search, distributed scaling, quantization for memory efficiency, and comprehensive monitoring capabilities for production RAG deployments.

## ChromaDB: Developer-Friendly Vector Database

### Advanced ChromaDB Configuration
```python
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import time
from typing import Dict, List, Any, Optional
import uuid

class AdvancedChromaDBManager:
    """Advanced ChromaDB management with optimization."""

    def __init__(self, persist_directory: Optional[str] = None,
                 host: str = "localhost", port: int = 8000):
        """Initialize ChromaDB with persistence or server mode."""

        if persist_directory:
            # Local persistent mode
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    allow_reset=False,
                    anonymized_telemetry=False,
                    # Performance settings
                    max_batch_size=1000,
                    # Memory settings
                    memory_limit=4 * 1024 * 1024 * 1024,  # 4GB
                    # Thread settings
                    max_threads=4
                )
            )
            print(f"ChromaDB persistent client created at {persist_directory}")
        else:
            # Server mode
            self.client = chromadb.HttpClient(
                host=f"{host}:{port}",
                settings=Settings(
                    allow_reset=False,
                    anonymized_telemetry=False,
                    # Connection settings
                    max_batch_size=1000,
                    # Performance settings
                    max_request_retries=3,
                    request_timeout=30
                )
            )
            print(f"ChromaDB HTTP client connected to {host}:{port}")

        self.collections = {}

    def create_optimized_collection(self, collection_name: str,
                                   embedding_function=None,
                                   distance_function: str = "cosine") -> Any:
        """Create optimized collection with advanced configuration."""

        try:
            # Use default embedding if none provided
            if embedding_function is None:
                embedding_function = embedding_functions.DefaultEmbeddingFunction()

            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={
                    "hnsw:space": distance_function,
                    "hnsw:construction_ef": 200,
                    "hnsw:search_ef": 50,
                    "hnsw:M": 16,
                    # Performance optimizations
                    "hnsw:num_threads": 4,
                    # Memory optimization
                    "hnsw:ef_construction": 200,
                    "hnsw:M": 16
                }
            )

            self.collections[collection_name] = collection
            print(f"Created/loaded collection: {collection_name}")
            return collection

        except Exception as e:
            print(f"Error creating collection {collection_name}: {e}")
            raise

    def advanced_batch_add(self, collection_name: str, chunks: List[Dict],
                          batch_size: int = 100) -> Dict[str, Any]:
        """Advanced batch insertion with error handling and progress tracking."""

        if collection_name not in self.collections:
            collection = self.create_optimized_collection(collection_name)
        else:
            collection = self.collections[collection_name]

        results = {
            "success": 0,
            "failed": 0,
            "batches": 0,
            "start_time": time.time(),
            "errors": []
        }

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            try:
                # Prepare batch data
                ids = []
                embeddings = []
                metadatas = []
                documents = []

                for j, chunk in enumerate(batch):
                    # Generate unique ID
                    chunk_id = f"{chunk.get('file_path', 'unknown')}_{i + j}_{uuid.uuid4().hex[:8]}"
                    ids.append(chunk_id)

                    # Extract embedding
                    embedding = chunk.get('embedding')
                    if embedding is None:
                        raise ValueError(f"Missing embedding for chunk {j}")
                    embeddings.append(embedding)

                    # Prepare metadata
                    metadata = {
                        "file_path": chunk.get('file_path', ''),
                        "content_type": chunk.get('type', 'unknown'),
                        "language": chunk.get('language', ''),
                        "framework": chunk.get('framework', ''),
                        "function_name": chunk.get('name', ''),
                        "class_name": chunk.get('class_name', ''),
                        "start_line": chunk.get('start_line', 0),
                        "end_line": chunk.get('end_line', 0),
                        "complexity": chunk.get('complexity', 1),
                        "token_count": chunk.get('token_count', 0),
                        "is_test": chunk.get('is_test', False),
                        "is_documented": chunk.get('is_documented', False),
                        "user_roles": chunk.get('user_roles', []),
                        "tags": chunk.get('tags', []),
                        "quality_score": chunk.get('quality_score', 0.0),
                        "popularity_score": chunk.get('popularity_score', 0.0),
                        "repository_id": chunk.get('repository_id', ''),
                        "created_at": int(time.time())
                    }
                    metadatas.append(metadata)

                    # Prepare document (content)
                    document = chunk.get('content', '')
                    documents.append(document)

                # Add batch to collection
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )

                results["success"] += len(batch)
                results["batches"] += 1

                print(f"Batch {results['batches']}: Added {len(batch)} documents")

            except Exception as e:
                error_msg = f"Batch {results['batches'] + 1} failed: {e}"
                print(error_msg)
                results["errors"].append(error_msg)
                results["failed"] += len(batch)

        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        results["throughput"] = results["success"] / results["duration"] if results["duration"] > 0 else 0

        print(f"Insertion completed: {results['success']} documents in {results['duration']:.2f}s")
        print(f"Throughput: {results['throughput']:.2f} docs/sec")

        return results

    def advanced_query(self, collection_name: str, query_embeddings: List[List[float]],
                      where_filters: Optional[Dict] = None,
                      n_results: int = 10,
                      include_metadata: bool = True,
                      include_documents: bool = True,
                      include_distances: bool = True) -> Dict[str, Any]:
        """Advanced query with comprehensive filtering and result formatting."""

        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} not found")

        collection = self.collections[collection_name]

        try:
            # Build where clause for filtering
            where_clause = self._build_chroma_where_clause(where_filters) if where_filters else None

            # Perform query
            start_time = time.time()
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where_clause,
                include=["metadatas", "documents", "distances"] if all([include_metadata, include_documents, include_distances]) else []
            )
            query_time = time.time() - start_time

            # Format results
            formatted_results = []
            for i, query_result in enumerate(results['ids'][0]):
                result = {
                    "id": query_result,
                    "query_index": i
                }

                if include_metadata and results.get('metadatas'):
                    result["metadata"] = results['metadatas'][0][i]

                if include_documents and results.get('documents'):
                    result["document"] = results['documents'][0][i]

                if include_distances and results.get('distances'):
                    # Convert distance to similarity for cosine distance
                    distance = results['distances'][0][i]
                    result["distance"] = distance
                    result["similarity"] = 1 - distance if where_clause and "hnsw:space" in str(where_clause) else distance

                formatted_results.append(result)

            return {
                "results": formatted_results,
                "query_time": query_time,
                "num_results": len(formatted_results)
            }

        except Exception as e:
            print(f"Query failed: {e}")
            return {"error": str(e), "results": []}

    def _build_chroma_where_clause(self, filters: Dict) -> Dict:
        """Build ChromaDB where clause from filter dictionary."""

        where_conditions = []

        for key, value in filters.items():
            if key == "language" and value:
                where_conditions.append({"language": {"$eq": value}})
            elif key == "content_type" and value:
                where_conditions.append({"content_type": {"$eq": value}})
            elif key == "framework" and value:
                where_conditions.append({"framework": {"$eq": value}})
            elif key == "user_roles" and value:
                if isinstance(value, list):
                    where_conditions.append({"user_roles": {"$in": value}})
                else:
                    where_conditions.append({"user_roles": {"$contains": value}})
            elif key == "is_test" and value is not None:
                where_conditions.append({"is_test": {"$eq": bool(value)}})
            elif key == "is_documented" and value is not None:
                where_conditions.append({"is_documented": {"$eq": bool(value)}})
            elif key == "quality_score_min" and value:
                where_conditions.append({"quality_score": {"$gte": float(value)}})
            elif key == "complexity_max" and value:
                where_conditions.append({"complexity": {"$lte": int(value)}})
            elif key == "start_line_min" and value:
                where_conditions.append({"start_line": {"$gte": int(value)}})
            elif key == "end_line_max" and value:
                where_conditions.append({"end_line": {"$lte": int(value)}})

        if not where_conditions:
            return {}
        elif len(where_conditions) == 1:
            return where_conditions[0]
        else:
            return {"$and": where_conditions}

    def similarity_search_with_scores(self, collection_name: str, query_text: str,
                                      query_embedding: List[float],
                                      filters: Optional[Dict] = None,
                                      top_k: int = 10) -> List[Dict]:
        """Search with text matching boost and comprehensive scoring."""

        # Get initial results
        initial_results = self.advanced_query(
            collection_name=collection_name,
            query_embeddings=[query_embedding],
            where_filters=filters,
            n_results=top_k * 2,  # Get more for reranking
            include_metadata=True,
            include_documents=True,
            include_distances=True
        )

        if "error" in initial_results:
            return []

        # Score reranking
        scored_results = []
        query_words = set(query_text.lower().split())

        for result in initial_results["results"]:
            content = result.get("document", "").lower()
            metadata = result.get("metadata", {})

            # Base similarity score
            base_score = result.get("similarity", result.get("distance", 0))

            # Text matching boost
            text_match_score = 0.0
            content_words = set(content.split())
            word_overlap = len(query_words.intersection(content_words))
            if word_overlap > 0:
                text_match_score = 0.1 * (word_overlap / len(query_words))

            # Exact phrase match bonus
            if query_text.lower() in content:
                text_match_score += 0.2

            # Quality score boost
            quality_boost = metadata.get("quality_score", 0.0) * 0.1

            # Documentation boost
            doc_boost = 0.05 if metadata.get("is_documented", False) else 0.0

            # Framework matching boost
            framework_boost = 0.0
            if filters and "framework" in filters:
                if metadata.get("framework") == filters["framework"]:
                    framework_boost = 0.1

            # Combined score
            combined_score = base_score + text_match_score + quality_boost + doc_boost + framework_boost

            scored_results.append({
                "id": result["id"],
                "score": combined_score,
                "base_score": base_score,
                "text_match_score": text_match_score,
                "quality_boost": quality_boost,
                "document": result.get("document", ""),
                "metadata": metadata
            })

        # Sort by combined score
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        return scored_results[:top_k]

    def collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get comprehensive collection statistics."""

        if collection_name not in self.collections:
            return {"error": f"Collection {collection_name} not found"}

        collection = self.collections[collection_name]

        try:
            # Basic count
            count = collection.count()

            # Sample a few items to analyze content
            sample_results = collection.get(limit=100, include=["metadatas"])

            # Analyze metadata
            languages = {}
            content_types = {}
            frameworks = {}
            quality_scores = []

            for metadata in sample_results.get('metadatas', []):
                lang = metadata.get('language', 'unknown')
                content_type = metadata.get('content_type', 'unknown')
                framework = metadata.get('framework', 'unknown')
                quality_score = metadata.get('quality_score', 0)

                languages[lang] = languages.get(lang, 0) + 1
                content_types[content_type] = content_types.get(content_type, 0) + 1
                frameworks[framework] = frameworks.get(framework, 0) + 1
                quality_scores.append(quality_score)

            stats = {
                "collection_name": collection_name,
                "total_documents": count,
                "sample_size": len(sample_results.get('metadatas', [])),
                "languages": languages,
                "content_types": content_types,
                "frameworks": frameworks,
                "quality_stats": {
                    "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                    "min_quality": min(quality_scores) if quality_scores else 0,
                    "max_quality": max(quality_scores) if quality_scores else 0
                }
            }

            return stats

        except Exception as e:
            return {"error": str(e)}

    def optimize_collection(self, collection_name: str) -> Dict[str, Any]:
        """Provide optimization recommendations for the collection."""

        stats = self.collection_stats(collection_name)

        if "error" in stats:
            return stats

        recommendations = []

        # Collection size recommendations
        if stats["total_documents"] < 1000:
            recommendations.append("Small collection - consider batching for better performance")
        elif stats["total_documents"] > 100000:
            recommendations.append("Large collection - consider using persistent server mode")
            recommendations.append("Consider implementing result caching for frequent queries")

        # Quality analysis
        avg_quality = stats["quality_stats"]["avg_quality"]
        if avg_quality < 0.5:
            recommendations.append("Low average quality scores detected - consider data quality improvements")
        elif avg_quality > 0.8:
            recommendations.append("High quality scores - consider reducing search filters for better diversity")

        # Content type diversity
        content_type_diversity = len(stats["content_types"])
        if content_type_diversity == 1:
            recommendations.append("Low content type diversity - consider adding more varied content")

        return {
            "stats": stats,
            "recommendations": recommendations,
            "optimization_applied": False
        }
```

## Performance Benchmarks and Optimization

### Database Performance Comparison
```python
import time
import psutil
import numpy as np
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd

class VectorDatabaseBenchmarker:
    """Comprehensive performance benchmarking for vector databases."""

    def __init__(self):
        self.results = {}

    def benchmark_databases(self, test_data: List[Dict],
                          test_queries: List[List[float]],
                          database_managers: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive benchmarks across multiple databases."""

        benchmark_results = {}

        for db_name, manager in database_managers.items():
            print(f"\n=== Benchmarking {db_name} ===")

            try:
                # Insert performance
                insert_results = self._benchmark_insertion(manager, test_data, db_name)

                # Search performance
                search_results = self._benchmark_search(manager, test_queries, db_name)

                # Memory usage
                memory_results = self._benchmark_memory_usage(manager, db_name)

                # Combine results
                benchmark_results[db_name] = {
                    "insert": insert_results,
                    "search": search_results,
                    "memory": memory_results,
                    "overall_score": self._calculate_overall_score(
                        insert_results, search_results, memory_results
                    )
                }

            except Exception as e:
                print(f"Error benchmarking {db_name}: {e}")
                benchmark_results[db_name] = {"error": str(e)}

        self.results = benchmark_results
        return benchmark_results

    def _benchmark_insertion(self, manager, test_data: List[Dict], db_name: str) -> Dict[str, Any]:
        """Benchmark insertion performance."""

        collection_name = f"benchmark_{db_name}_{int(time.time())}"

        try:
            # Create collection
            if hasattr(manager, 'create_optimized_collection'):
                manager.create_optimized_collection(collection_name)
            elif hasattr(manager, 'create_collection'):
                manager.create_collection(collection_name)
            else:
                raise AttributeError("Manager does not have collection creation method")

            # Benchmark insertion
            batch_sizes = [100, 500, 1000]
            results = {}

            for batch_size in batch_sizes:
                if len(test_data) < batch_size:
                    continue

                # Measure system resources before
                cpu_before = psutil.cpu_percent()
                memory_before = psutil.virtual_memory().used

                # Perform insertion
                start_time = time.time()

                if hasattr(manager, 'optimized_batch_insert'):
                    insert_result = manager.optimized_batch_insert(
                        collection_name, test_data[:batch_size], batch_size
                    )
                elif hasattr(manager, 'batch_insert'):
                    insert_result = manager.batch_insert(
                        collection_name, test_data[:batch_size]
                    )
                else:
                    # Fallback to individual insertion
                    insert_result = {"success": 0}
                    for i, chunk in enumerate(test_data[:batch_size]):
                        try:
                            if hasattr(manager, 'insert_chunks'):
                                manager.insert_chunks([chunk])
                                insert_result["success"] += 1
                        except:
                            pass

                end_time = time.time()

                # Measure system resources after
                cpu_after = psutil.cpu_percent()
                memory_after = psutil.virtual_memory().used

                duration = end_time - start_time
                throughput = insert_result.get("success", 0) / duration if duration > 0 else 0

                results[f"batch_size_{batch_size}"] = {
                    "duration": duration,
                    "throughput": throughput,
                    "success_count": insert_result.get("success", 0),
                    "cpu_usage": cpu_after - cpu_before,
                    "memory_usage_mb": (memory_after - memory_before) / (1024 * 1024)
                }

                print(f"  Insertion (batch_size={batch_size}): {throughput:.2f} items/sec")

            return results

        except Exception as e:
            return {"error": str(e)}

    def _benchmark_search(self, manager, test_queries: List[List[float]], db_name: str) -> Dict[str, Any]:
        """Benchmark search performance."""

        collection_name = f"benchmark_{db_name}_{int(time.time())}"

        try:
            # Prepare test data for search (assuming collection exists from insertion benchmark)
            query_count = len(test_queries)
            results = {
                "single_query": [],
                "batch_query": {},
                "filtering": {}
            }

            # Single query performance
            for i, query in enumerate(test_queries[:10]):  # Test first 10 queries
                start_time = time.time()

                if hasattr(manager, 'advanced_search'):
                    search_result = manager.advanced_search(
                        collection_name, query, limit=10
                    )
                elif hasattr(manager, 'search'):
                    search_result = manager.search(query, limit=10)
                else:
                    search_result = []

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms

                results["single_query"].append({
                    "query_index": i,
                    "response_time_ms": response_time,
                    "result_count": len(search_result) if isinstance(search_result, list) else 0
                })

            # Batch query performance
            batch_sizes = [5, 10, 20]
            for batch_size in batch_sizes:
                if query_count < batch_size:
                    continue

                start_time = time.time()
                batch_results = []

                for query in test_queries[:batch_size]:
                    if hasattr(manager, 'advanced_search'):
                        result = manager.advanced_search(collection_name, query, limit=5)
                    elif hasattr(manager, 'search'):
                        result = manager.search(query, limit=5)
                    else:
                        result = []
                    batch_results.append(result)

                end_time = time.time()
                total_time = (end_time - start_time) * 1000
                avg_time = total_time / batch_size

                results["batch_query"][f"batch_size_{batch_size}"] = {
                    "total_time_ms": total_time,
                    "avg_response_time_ms": avg_time,
                    "queries_per_second": 1000 / avg_time if avg_time > 0 else 0
                }

            # Filtering performance
            filters = [
                {"language": "python"},
                {"content_type": "function"},
                {"quality_score_min": 0.5},
                {"language": "python", "content_type": "class"}
            ]

            for filter_config in filters:
                start_time = time.time()

                if hasattr(manager, 'advanced_search'):
                    filtered_results = manager.advanced_search(
                        collection_name, test_queries[0], filters=filter_config, limit=10
                    )
                else:
                    filtered_results = []

                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                filter_key = "_".join([f"{k}_{v}" for k, v in filter_config.items()])
                results["filtering"][filter_key] = {
                    "response_time_ms": response_time,
                    "result_count": len(filtered_results) if isinstance(filtered_results, list) else 0
                }

            return results

        except Exception as e:
            return {"error": str(e)}

    def _benchmark_memory_usage(self, manager, db_name: str) -> Dict[str, Any]:
        """Benchmark memory usage patterns."""

        try:
            # Get initial memory state
            initial_memory = psutil.virtual_memory().used

            # Simulate memory stress test
            memory_results = {
                "initial_memory_mb": initial_memory / (1024 * 1024),
                "peak_memory_mb": initial_memory / (1024 * 1024),
                "memory_growth_mb": 0
            }

            # Monitor memory during operations
            peak_memory = initial_memory
            samples = []

            for _ in range(10):  # 10 memory samples
                current_memory = psutil.virtual_memory().used
                samples.append(current_memory)
                peak_memory = max(peak_memory, current_memory)
                time.sleep(0.1)  # Small delay

            memory_results.update({
                "peak_memory_mb": peak_memory / (1024 * 1024),
                "memory_growth_mb": (peak_memory - initial_memory) / (1024 * 1024),
                "avg_memory_mb": sum(samples) / len(samples) / (1024 * 1024)
            })

            return memory_results

        except Exception as e:
            return {"error": str(e)}

    def _calculate_overall_score(self, insert_results: Dict,
                                 search_results: Dict,
                                 memory_results: Dict) -> float:
        """Calculate overall performance score."""

        if "error" in insert_results or "error" in search_results:
            return 0.0

        # Insertion score (40% weight)
        insert_score = 0.0
        if "batch_size_1000" in insert_results:
            throughput = insert_results["batch_size_1000"]["throughput"]
            insert_score = min(1.0, throughput / 1000)  # Normalize to 1000 items/sec

        # Search score (40% weight)
        search_score = 0.0
        if "single_query" in search_results:
            avg_response_time = sum(r["response_time_ms"] for r in search_results["single_query"]) / len(search_results["single_query"])
            # Lower response time is better (target: < 10ms)
            search_score = max(0.0, 1.0 - (avg_response_time - 10) / 90)

        # Memory score (20% weight)
        memory_score = 1.0
        if "memory_growth_mb" in memory_results:
            # Lower memory growth is better (target: < 100MB)
            memory_growth = memory_results["memory_growth_mb"]
            memory_score = max(0.0, 1.0 - memory_growth / 100)

        overall_score = (insert_score * 0.4) + (search_score * 0.4) + (memory_score * 0.2)
        return overall_score

    def generate_benchmark_report(self, output_file: str = "vector_db_benchmark_report.html") -> str:
        """Generate comprehensive benchmark report."""

        if not self.results:
            return "No benchmark results available"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vector Database Performance Report</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .database-section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                .chart-container { width: 100%; height: 400px; margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .score-good { color: green; font-weight: bold; }
                .score-medium { color: orange; font-weight: bold; }
                .score-poor { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Vector Database Performance Benchmark Report</h1>
            <p>Generated on: {timestamp}</p>

            <div class="database-section">
                <h2>Overall Performance Scores</h2>
                <div class="chart-container">
                    <canvas id="overallScoreChart"></canvas>
                </div>
            </div>

            {database_sections}

            <script>
                // Overall Score Chart
                const overallCtx = document.getElementById('overallScoreChart').getContext('2d');
                new Chart(overallCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {db_names},
                        datasets: [{{
                            label: 'Overall Score',
                            data: {scores},
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 1
                            }}
                        }}
                    }}
                }});

                {chart_scripts}
            </script>
        </body>
        </html>
        """

        # Prepare data
        db_names = list(self.results.keys())
        scores = []
        database_sections = ""
        chart_scripts = ""

        for db_name, results in self.results.items():
            if "error" not in results:
                scores.append(results["overall_score"])
                database_sections += f"""
                <div class="database-section">
                    <h3>{db_name}</h3>
                    <p><strong>Overall Score: {results["overall_score"]:.2f}</strong></p>
                    <h4>Performance Metrics</h4>
                    <table>
                        <tr><th>Metric</th><th>Value</th></tr>
                """

                # Add detailed metrics
                if "insert" in results and "batch_size_1000" in results["insert"]:
                    insert_perf = results["insert"]["batch_size_1000"]
                    database_sections += f"""
                        <tr>
                            <td>Insert Throughput (1000 batch)</td>
                            <td>{insert_perf['throughput']:.2f} items/sec</td>
                        </tr>
                    """

                if "search" in results and "single_query" in results["search"]:
                    search_perf = results["search"]["single_query"]
                    avg_time = sum(r["response_time_ms"] for r in search_perf) / len(search_perf)
                    database_sections += f"""
                        <tr>
                            <td>Avg Search Response Time</td>
                            <td>{avg_time:.2f} ms</td>
                        </tr>
                    """

                database_sections += "</table></div>"

        # Generate HTML
        html_content = html_template.format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            db_names=db_names,
            scores=scores,
            database_sections=database_sections,
            chart_scripts=chart_scripts
        )

        # Write to file
        with open(output_file, 'w') as f:
            f.write(html_content)

        return f"Benchmark report saved to {output_file}"

**Use Cases for RAG**: Comprehensive vector database comparison and optimization with performance benchmarking, memory usage analysis, and automated recommendations for production RAG deployments.

**Use Cases for RAG**: Store and search code embeddings with role-based filtering, support semantic similarity search across repositories, and enable efficient retrieval of relevant code snippets.