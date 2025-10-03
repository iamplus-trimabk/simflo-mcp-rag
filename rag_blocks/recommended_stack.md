# Recommended Technology Stack

## Complete RAG System Stack
**Category**: Technology Selection, Architecture
**User Roles**: Architect, Developer, DevOps Engineer
**Abstraction Level**: High-Level, Detailed

### Overview
This technology stack provides a comprehensive, production-ready foundation for building repository analysis and RAG systems with role-based access control.

### Core Stack Components

#### Backend Services
- **Node.js 18+**: Primary runtime for API services
- **Python 3.9+**: Machine learning and data processing
- **Express.js**: REST API framework
- **FastAPI**: High-performance Python APIs
- **TypeScript**: Type-safe development

#### Database and Storage
- **PostgreSQL**: Primary metadata storage
- **Weaviate/Milvus**: Open-source vector database for embeddings
- **Redis**: Caching and session management
- **MinIO/Local Storage**: Object storage for files

#### Machine Learning and AI
- **LlamaIndex**: RAG orchestration framework
- **LangChain**: Document processing and chaining
- **sentence-transformers**: Text embeddings
- **CodeBERT**: Code-specific embeddings
- **OpenAI API**: Advanced language models

#### DevOps and Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **GitHub Actions**: CI/CD pipelines
- **Terraform**: Infrastructure as code
- **Prometheus/Grafana**: Monitoring

---

## Repository Analysis Stack

### Sourcegraph Integration
**Purpose**: Large-scale code analysis and search

**Configuration**:
```yaml
sourcegraph_config:
  endpoint: "https://sourcegraph.example.com"
  access_token: "${SOURCEGRAPH_TOKEN}"
  batch_size: 100
  rate_limit: 1000  # requests per hour
  timeout: 30  # seconds
```

**API Usage**:
```python
import requests

class SourcegraphClient:
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.headers = {"Authorization": f"token {token}"}

    def search_repositories(self, query):
        url = f"{self.endpoint}/.api/search"
        params = {"q": query}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_file_content(self, repo, path, commit="main"):
        url = f"{self.endpoint}/.api/repos/{repo}/-/blob/{path}"
        params = {"commit": commit}
        response = requests.get(url, headers=self.headers, params=params)
        return response.text
```

### SonarQube Integration
**Purpose**: Code quality and security analysis

**Configuration**:
```python
SONARQUBE_CONFIG = {
    "url": "https://sonarqube.example.com",
    "token": "${SONARQUBE_TOKEN}",
    "project_key_pattern": "rag-analysis-{repo_name}",
    "quality_gate": "RAG-Analysis-Quality"
}

class SonarQubeAnalyzer:
    def analyze_project(self, repo_path, project_key):
        # Trigger SonarQube analysis
        sonar_scanner_cmd = [
            "sonar-scanner",
            f"-Dsonar.projectKey={project_key}",
            f"-Dsonar.sources={repo_path}",
            "-Dsonar.host.url=https://sonarqube.example.com",
            f"-Dsonar.login={SONARQUBE_CONFIG['token']}"
        ]

        result = subprocess.run(sonar_scanner_cmd, capture_output=True, text=True)
        return result.returncode == 0
```

### AST Parsers by Language

#### JavaScript/TypeScript
```python
import esprima
import typescript

class JavaScriptAnalyzer:
    def parse_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        if file_path.endswith('.ts'):
            return typescript.parse(content)
        else:
            return esprima.parseScript(content)

    def extract_functions(self, ast):
        functions = []
        for node in ast.body:
            if node.type == 'FunctionDeclaration':
                functions.append({
                    'name': node.id.name,
                    'params': [p.name for p in node.params],
                    'source': esprima.generate(node)
                })
        return functions
```

#### Python
```python
import ast

class PythonAnalyzer:
    def parse_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return ast.parse(content)

    def extract_classes_and_functions(self, tree):
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    'name': node.name,
                    'methods': [m.name for m in methods],
                    'line_number': node.lineno
                })
            elif isinstance(node, ast.FunctionDef) and not hasattr(node, 'parent_class'):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'line_number': node.lineno
                })

        return classes, functions
```

---

## RAG Infrastructure Stack

### LlamaIndex Configuration
**Purpose**: RAG orchestration and management

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores import PineconeVectorStore
import pinecone

class RAGManager:
    def __init__(self, pinecone_api_key, index_name):
        pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")

        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            dimension=1536,  # OpenAI ada-002 dimension
            metric="cosine"
        )

        self.indices = {}  # Cache for different content types

    def create_content_index(self, content_type, documents):
        """Create separate index for different content types"""
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=self.vector_store,
            namespace=content_type
        )
        self.indices[content_type] = index
        return index

    def query_with_role_filtering(self, query, user_role, abstraction_level):
        """Query with role and level filtering"""
        filters = {
            "user_role": user_role,
            "abstraction_level": abstraction_level
        }

        # Use the most appropriate index
        index = self.select_best_index(query)

        return index.query(
            query,
            filters=filters,
            top_k=10
        )
```

### Vector Database Setup

#### Weaviate Configuration (Open Source)
```python
import weaviate
from weaviate.client import Client

class WeaviateManager:
    def __init__(self, url="http://localhost:8080"):
        self.client = weaviate.Client(url)

    def create_rag_schema(self):
        """Create schema for RAG content"""
        schema = {
            "classes": [
                {
                    "class": "CodeContent",
                    "description": "Code repository content",
                    "properties": [
                        {"name": "text", "dataType": ["text"]},
                        {"name": "content_type", "dataType": ["string"]},
                        {"name": "user_role", "dataType": ["string"]},
                        {"name": "abstraction_level", "dataType": ["string"]},
                        {"name": "repository", "dataType": ["string"]},
                        {"name": "file_path", "dataType": ["string"]},
                        {"name": "language", "dataType": ["string"]},
                        {"name": "timestamp", "dataType": ["date"]}
                    ],
                    "vectorizer": "none"  # Use custom embeddings
                }
            ]
        }
        self.client.schema.create(schema)

    def upsert_with_metadata(self, content_objects):
        """Upsert content with metadata"""
        with self.client.batch as batch:
            for obj in content_objects:
                batch.add_data_object(
                    data_object=obj,
                    class_name="CodeContent",
                    vector=obj.get("vector")  # Custom embedding
                )
        return True
```

#### Milvus Configuration (Open Source)
```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

class MilvusManager:
    def __init__(self, host="localhost", port="19530"):
        connections.connect(host=host, port=port)

    def create_rag_collection(self, collection_name="rag_content"):
        """Create collection for RAG content"""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="user_role", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="abstraction_level", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="repository", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
        ]

        schema = CollectionSchema(fields, "RAG content collection")
        collection = Collection(collection_name, schema)

        # Create index for embeddings
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index("embedding", index_params)
        return collection
```

### Embedding Models

#### Multi-Model Strategy
```python
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModel

class EmbeddingManager:
    def __init__(self):
        # Text embeddings for documentation
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Code-specific embeddings
        self.code_model = AutoModel.from_pretrained('microsoft/codebert-base')
        self.code_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')

        # OpenAI embeddings for high-quality results
        self.openai_client = None  # Initialize with API key

    def embed_text(self, text, model_type='text'):
        """Generate embeddings based on content type"""
        if model_type == 'text':
            return self.text_model.encode(text)
        elif model_type == 'code':
            return self._embed_code(text)
        elif model_type == 'openai':
            return self._embed_with_openai(text)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def _embed_code(self, code):
        """Generate embeddings for code using CodeBERT"""
        inputs = self.code_tokenizer(code, return_tensors='pt',
                                   truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.code_model(**inputs)
            # Use [CLS] token embedding
            return outputs.last_hidden_state[0, 0].numpy()

    def _embed_with_openai(self, text):
        """Generate embeddings using OpenAI API"""
        import openai
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
```

---

## API and Service Architecture

### FastAPI Service Structure
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Repository RAG API", version="1.0.0")
security = HTTPBearer()

class SearchRequest(BaseModel):
    query: str
    user_role: str
    abstraction_level: Optional[str] = "detailed"
    repository_ids: Optional[List[str]] = None
    limit: int = 10

class SearchResult(BaseModel):
    content: str
    score: float
    metadata: dict
    source: str

# Dependency injection
def get_rag_manager():
    return RAGManager(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        index_name=os.getenv("PINECONE_INDEX")
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify JWT token and extract user info
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return UserRole.from_payload(payload)

@app.post("/search", response_model=List[SearchResult])
async def search_repository(
    request: SearchRequest,
    current_user: UserRole = Depends(get_current_user),
    rag_manager: RAGManager = Depends(get_rag_manager)
):
    """Search repository knowledge base with role-based filtering"""
    try:
        results = rag_manager.query_with_role_filtering(
            query=request.query,
            user_role=request.user_role,
            abstraction_level=request.abstraction_level
        )

        return [
            SearchResult(
                content=result.text,
                score=result.score,
                metadata=result.metadata,
                source=result.metadata.get('repository', 'unknown')
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Background Task Processing

#### Celery Configuration
```python
from celery import Celery
from celery.result import AsyncResult

celery_app = Celery(
    'rag_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task(bind=True)
def process_repository_task(self, repository_url: str, user_role: str):
    """Background task for repository processing"""
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Cloning repository'})

        # Process repository
        processor = RepositoryProcessor()
        result = processor.process_repository(repository_url, user_role)

        return {'status': 'SUCCESS', 'result': result}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

# API endpoint to start background processing
@app.post("/repositories/process")
async def start_repository_processing(
    repository_url: str,
    user_role: str,
    current_user: UserRole = Depends(get_current_user)
):
    task = process_repository_task.delay(repository_url, user_role)
    return {'task_id': task.id, 'status': 'PROCESSING'}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None
    }
```

---

## Deployment and Infrastructure

### Docker Configuration

#### Multi-stage Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM node:18-alpine AS production

# Install Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy built artifacts
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /usr/local/lib/python3.*/site-packages ./python-packages
COPY . .

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app/python-packages

EXPOSE 3000

CMD ["npm", "start"]
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api-server
  labels:
    app: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: rag-api
        image: rag-system:latest
        ports:
        - containerPort: 3000
        env:
        - name: PINECONE_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: pinecone-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Monitoring and Observability

### Prometheus Metrics Configuration
```python
from prometheus_client import Counter, Histogram, Gauge, make_wsgi_app
from werkzeug.wsgi import DispatcherMiddleware

# Define metrics
REQUEST_COUNT = Counter(
    'rag_requests_total',
    'Total RAG API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'rag_request_duration_seconds',
    'RAG API request duration',
    ['method', 'endpoint']
)

ACTIVE_REPOSITORIES = Gauge(
    'rag_active_repositories_total',
    'Number of active repositories'
)

EMBEDDING_CACHE_SIZE = Gauge(
    'rag_embedding_cache_size',
    'Embedding cache size in items'
)

# Middleware to track metrics
class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start_time = time.time()

        def custom_start_response(status, headers, exc_info=None):
            REQUEST_COUNT.labels(
                method=environ['REQUEST_METHOD'],
                endpoint=environ['PATH_INFO'],
                status=status.split()[0]
            ).inc()

            REQUEST_DURATION.labels(
                method=environ['REQUEST_METHOD'],
                endpoint=environ['PATH_INFO']
            ).observe(time.time() - start_time)

            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)

# Apply middleware
app = PrometheusMiddleware(app)
```

### Health Checks
```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/ready")
async def readiness_check():
    """Readiness check - verifies all dependencies"""
    checks = {
        "database": await check_database_connection(),
        "vector_db": await check_vector_db_connection(),
        "redis": await check_redis_connection(),
        "external_apis": await check_external_apis()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow()
    }, status_code

async def check_database_connection():
    try:
        # Test database connection
        await database.execute("SELECT 1")
        return True
    except:
        return False

async def check_vector_db_connection():
    try:
        # Test Pinecone connection
        pinecone.describe_index(os.getenv("PINECONE_INDEX"))
        return True
    except:
        return False
```

This comprehensive technology stack provides a production-ready foundation for building sophisticated repository analysis and RAG systems with proper scaling, monitoring, and security considerations.