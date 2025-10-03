# RAG System Step - Step 8 of the SimFlo Figma-to-RAG Pipeline

## <¯ Purpose

The RAG System step creates comprehensive knowledge bases from all previous pipeline outputs, enabling AI-powered search and retrieval across documentation, code, tests, and configurations. This step transforms structured pipeline artifacts into searchable vector representations for intelligent content discovery and analysis.

### Key Features
- **Multi-Modal Content Processing**: Handles JSON, Markdown, code, and text files
- **Intelligent Text Chunking**: Content-aware segmentation with overlap
- **Mock Embedding Generation**: Creates consistent vector representations
- **Knowledge Base Organization**: Separates content by type (docs, code, tests, config)
- **Semantic Search**: Enables intelligent content retrieval
- **Metadata Enrichment**: Tracks source information and content relationships

## =Ë Input/Output

### Input
The RAG System processes outputs from all previous pipeline steps:

1. **Documentation Outputs** (Steps 1-3)
   - `design-tokens.json` - Design system specifications
   - `component-catalog.json` - Component definitions
   - `interaction-flows.json` - User interaction mappings
   - `screen-specs/` - Screen layout specifications
   - Token conversion outputs (CSS, JS, config files)

2. **Code Outputs** (Steps 4-5)
   - `components/` - Generated React components
   - `pages/` - Generated page implementations
   - `hooks/` - Custom React hooks
   - `contexts/` - State management contexts
   - Component stories and documentation

3. **Test Outputs** (Steps 6-7)
   - `tests/` - Playwright test files
   - `test-results/` - Test execution reports
   - `demo/` - Interactive demo applications
   - Test scenarios and configurations

### Output
The RAG System creates structured knowledge bases:

1. **Documentation Knowledge Base** (`doc-rag/`)
   - Processed documentation chunks
   - Design token information
   - Component specifications
   - User interaction flows

2. **Code Knowledge Base** (`code-rag/`)
   - Component implementations
   - Page structures
   - Custom hooks and utilities
   - Code patterns and examples

3. **Test Knowledge Base** (`test-rag/`)
   - Test scenarios and cases
   - Test execution results
   - Demo applications
   - Testing patterns

4. **Configuration Knowledge Base** (`config-rag/`)
   - Pipeline configurations
   - Build settings
   - Framework configurations
   - System settings

5. **Main Configuration** (`rag-config.json`)
   - System metadata
   - Processing statistics
   - Knowledge base summaries
   - Configuration settings

## <× Architecture

### Core Components

#### `RAGSystem`
Main orchestrator that coordinates the entire RAG processing pipeline.

**Key Methods:**
- `process_pipeline_outputs(input_dirs, output_dir)` - Main processing entry point
- `_collect_files(input_dirs)` - Collect all processable files
- `_save_rag_configuration(output_dir, knowledge_bases, statistics)` - Save system configuration

#### `ContentProcessor`
Handles extraction and parsing of different file types.

**Supported File Types:**
- **JSON**: Structured data extraction with path tracking
- **Markdown**: Section-based parsing with header hierarchy
- **Code**: Function/class extraction with language-specific patterns
- **Text**: Paragraph-based segmentation

**Key Methods:**
- `process_file(file_path)` - Process individual files
- `_extract_json_content(content, file_path)` - Extract JSON data
- `_extract_markdown_content(content, file_path)` - Parse Markdown sections
- `_extract_code_content(content, file_type, file_path)` - Parse code structures

#### `TextChunker`
Intelligently segments content into optimal chunks for vector storage.

**Chunking Strategies:**
- **Structured Content**: No splitting for JSON values and code blocks
- **Text Content**: Sentence-based splitting with overlap
- **Size Optimization**: Respects min/max chunk size constraints

**Key Methods:**
- `chunk_content(content_sections, file_path)` - Main chunking logic
- `_split_text(text)` - Split text with overlap
- `_create_chunk(content, chunk_type, file_path, ...)` - Create ContentChunk objects

#### `EmbeddingGenerator`
Creates vector representations of text chunks.

**Features:**
- **Mock Embeddings**: Consistent pseudo-random vectors based on content
- **Normalization**: L2 normalized vectors for similarity comparison
- **Fallback Support**: Works with or without NumPy
- **Deterministic**: Same content always produces same embedding

**Key Methods:**
- `generate_embeddings(chunks)` - Generate embeddings for all chunks
- `_generate_mock_embedding(text)` - Create mock embedding vector

#### `VectorStore`
Mock vector database for storing and searching embeddings.

**Features:**
- **Index Management**: Automatic index building and maintenance
- **Search Functionality**: Content-based search with scoring
- **Filtering**: Support for content type and tag filtering
- **Statistics**: Detailed store analytics

**Key Methods:**
- `add_chunks(chunks)` - Add chunks to store
- `build_index()` - Build search index
- `search(query, content_type, tags, limit)` - Search for similar content
- `get_statistics()` - Get store statistics

#### `RAGKnowledgeBaseManager`
Manages multiple knowledge bases and their operations.

**Knowledge Base Types:**
- **doc-rag**: Documentation and design content
- **code-rag**: Code implementations and patterns
- **test-rag**: Test scenarios and results
- **config-rag**: Configuration and settings

**Key Methods:**
- `create_knowledge_base(name, chunks)` - Create new knowledge base
- `save_knowledge_base(name, output_dir)` - Persist knowledge base
- `search_knowledge_base(name, query, ...)` - Search within knowledge base
- `list_knowledge_bases()` - List all available knowledge bases

### Data Models

#### `RAGProcessingConfig`
Configuration for RAG processing parameters.

```python
@dataclass
class RAGProcessingConfig:
    chunk_size: int = 1000          # Target chunk size in tokens
    chunk_overlap: int = 200        # Overlap between chunks
    min_chunk_size: int = 100       # Minimum chunk size
    max_chunk_size: int = 2000      # Maximum chunk size
    embedding_dim: int = 384        # Embedding dimension
    similarity_threshold: float = 0.7  # Similarity threshold
    max_search_results: int = 10    # Maximum search results
    include_metadata: bool = True    # Include rich metadata
    strict_validation: bool = False  # Strict validation mode
    generate_mock_embeddings: bool = True  # Generate mock embeddings
```

#### `ContentChunk`
Represents a chunk of content for the RAG knowledge base.

**Key Fields:**
- `id`: Unique chunk identifier
- `content_type`: Type of content (documentation, code, test, etc.)
- `content`: Actual text content
- `metadata`: Content-specific metadata
- `source_info`: Source file and location information
- `embedding_vector`: Vector representation
- `tags`: Content tags for categorization
- `language`: Content language (if applicable)
- `quality_score`: Content quality assessment

## =' Processing Pipeline

### Phase 1: File Collection and Discovery
1. **Directory Scanning**: Recursively scan input directories
2. **File Type Filtering**: Identify supported file types
3. **Path Validation**: Verify file accessibility
4. **Metadata Collection**: Gather file information

### Phase 2: Content Extraction
1. **File Type Detection**: Determine appropriate processing strategy
2. **Content Parsing**: Extract structured content based on file type
3. **Metadata Generation**: Create rich metadata for each section
4. **Content Validation**: Ensure content quality and completeness

### Phase 3: Text Chunking
1. **Content Analysis**: Determine optimal chunking strategy
2. **Size Optimization**: Apply min/max size constraints
3. **Overlap Management**: Create context-preserving overlaps
4. **Chunk Generation**: Create ContentChunk objects

### Phase 4: Embedding Generation
1. **Vector Creation**: Generate embedding vectors for each chunk
2. **Normalization**: Apply L2 normalization
3. **Quality Assurance**: Validate embedding dimensions
4. **Storage Preparation**: Prepare for vector storage

### Phase 5: Knowledge Base Creation
1. **Content Categorization**: Group chunks by content type
2. **Knowledge Base Initialization**: Create separate knowledge bases
3. **Vector Indexing**: Build search indexes
4. **Category Generation**: Create content categories

### Phase 6: Persistence and Export
1. **Knowledge Base Serialization**: Save knowledge bases to files
2. **Configuration Export**: Export system configuration
3. **Statistics Generation**: Create processing statistics
4. **Validation**: Verify output completeness

## =Ê Content Processing Details

### JSON File Processing
**Strategy**: Recursive extraction with path tracking

**Extraction Rules**:
- Primitive values (string, number, boolean) become individual chunks
- Object structure is preserved in metadata
- JSON path information is tracked
- Data type information is included

**Example**:
```json
{
  "component": {
    "name": "Button",
    "props": {
      "variant": "primary"
    }
  }
}
```

**Generated Chunks**:
- Content: "Button", Path: "root.component.name", Type: string
- Content: "primary", Path: "root.component.props.variant", Type: string

### Markdown File Processing
**Strategy**: Section-based parsing with header hierarchy

**Extraction Rules**:
- Split by headers (H1-H6)
- Preserve header hierarchy in metadata
- Maintain content context
- Generate section-aware tags

**Example**:
```markdown
# Component Documentation
## Button Component
This is a button component...
```

**Generated Chunks**:
- Content: "# Component Documentation\n## Button Component\nThis is a button component..."
- Metadata: header_level=1, header_text="Component Documentation"

### Code File Processing
**Strategy**: Function/class extraction with language-specific patterns

**Supported Languages**:
- **JavaScript/TypeScript**: Functions, classes, interfaces, types
- **Python**: Functions, classes, methods
- **CSS/SCSS**: Selectors, rules, mixins
- **HTML**: Elements, attributes, structure

**Extraction Rules**:
- Identify function/class boundaries
- Extract complete code blocks
- Track line numbers and locations
- Generate language-specific tags

**Example**:
```typescript
function Button(props: ButtonProps) {
  return <button {...props} />;
}
```

**Generated Chunk**:
- Content: Complete function definition
- Metadata: function_name="Button", language="typescript", start_line=1, end_line=3

## = Search and Retrieval

### Search Algorithm
The RAG system implements a multi-layered search approach:

1. **Content Filtering**: Filter by content type and tags
2. **Text Matching**: Exact and partial text matches
3. **Word Matching**: Token-based similarity scoring
4. **Tag Matching**: Tag relevance scoring
5. **Metadata Matching**: Title and section relevance
6. **Result Ranking**: Combined scoring algorithm

### Search Scoring
**Score Components**:
- **Exact Content Match**: 10 points
- **Word Match**: 2 points per matching word
- **Tag Match**: 3 points per matching tag
- **Title Match**: 5 points for title/section matches

### Search Features
- **Content Type Filtering**: Search within specific content types
- **Tag Filtering**: Filter by content tags
- **Result Limiting**: Control maximum number of results
- **Relevance Ranking**: Results sorted by relevance score

## =à Configuration Options

### Chunking Configuration
```python
chunk_size: 1000          # Target chunk size in tokens
chunk_overlap: 200        # Overlap between chunks
min_chunk_size: 100       # Minimum chunk size
max_chunk_size: 2000      # Maximum chunk size
```

### Embedding Configuration
```python
embedding_dim: 384        # Embedding vector dimension
generate_mock_embeddings: True  # Use mock embeddings
```

### Search Configuration
```python
similarity_threshold: 0.7  # Minimum similarity threshold
max_search_results: 10    # Maximum search results
```

### Validation Configuration
```python
strict_validation: False  # Enable strict validation
include_metadata: True    # Include rich metadata
```

## =È Performance Considerations

### Memory Usage
- **Chunk Processing**: Linear with content size
- **Embedding Storage**: O(n * embedding_dim) where n is number of chunks
- **Index Building**: One-time cost proportional to chunk count
- **Search Memory**: O(1) for query processing

### Processing Time
- **File Processing**: Depends on file size and complexity
- **Chunking**: O(total_content_size)
- **Embedding Generation**: O(num_chunks * embedding_dim)
- **Index Building**: O(num_chunks * log(num_chunks))
- **Search**: O(log(num_chunks)) with proper indexing

### Optimization Strategies
1. **Lazy Loading**: Load content on demand
2. **Batch Processing**: Process multiple files simultaneously
3. **Memory Management**: Release unused content from memory
4. **Index Optimization**: Use efficient data structures
5. **Caching**: Cache frequently accessed chunks

## >ê Testing and Validation

### Unit Testing
```bash
# Test individual components
python -m pytest v2/tests/test_rag_system.py

# Test with coverage
python -m pytest v2/tests/test_rag_system.py --cov=v2/rag-system
```

### Integration Testing
```bash
# Test with sample pipeline outputs
python v2/rag-system/main.py --input ./test-output --output ./test-rag

# Validate generated knowledge bases
python v2/common/validation.py validate --file ./test-rag/rag-config.json --schema RAGKnowledgeBase
```

### Performance Testing
```bash
# Test with large datasets
python v2/rag-system/main.py --input ./large-dataset --output ./perf-test --verbose

# Measure processing time and memory usage
time python v2/rag-system/main.py --input ./test-data --output ./perf-test
```

## =' Usage Examples

### Basic Usage
```bash
# Process pipeline outputs
python v2/rag-system/main.py --input ./output --output ./rag-output

# Process multiple input directories
python v2/rag-system/main.py --input ./output ./examples --output ./rag-output
```

### Advanced Configuration
```bash
# Custom chunking parameters
python v2/rag-system/main.py \
  --input ./output \
  --output ./rag-output \
  --chunk-size 500 \
  --overlap 100 \
  --embedding-dim 768

# Strict validation mode
python v2/rag-system/main.py \
  --input ./output \
  --output ./rag-output \
  --strict \
  --verbose
```

### Programmatic Usage
```python
from pathlib import Path
from v2.rag_system.main import RAGSystem, RAGProcessingConfig

# Create configuration
config = RAGProcessingConfig(
    chunk_size=500,
    chunk_overlap=100,
    embedding_dim=768
)

# Create RAG system
rag_system = RAGSystem(config)

# Process pipeline outputs
result = rag_system.process_pipeline_outputs(
    input_dirs=[Path("./output")],
    output_dir=Path("./rag-output")
)

# Access knowledge bases
doc_kb = rag_system.kb_manager.get_knowledge_base('doc-rag')
code_kb = rag_system.kb_manager.get_knowledge_base('code-rag')

# Search within knowledge bases
results = rag_system.kb_manager.search_knowledge_base(
    'doc-rag',
    'React component',
    limit=5
)
```

## = Troubleshooting

### Common Issues

#### File Not Found
```
FileNotFoundError: Input directory not found: ./output
```
**Solution**: Verify input directory paths and ensure they exist

#### Unsupported File Types
```
Warning: Unsupported file type: .xyz
```
**Solution**: Check supported file types or add new file type handlers

#### Memory Issues
```
MemoryError: Unable to allocate memory for embeddings
```
**Solution**: Reduce chunk size or process files in smaller batches

#### JSON Parsing Errors
```
JSONDecodeError: Invalid JSON format
```
**Solution**: Validate JSON syntax and encoding

#### Empty Knowledge Bases
```
Warning: No chunks found for knowledge base
```
**Solution**: Check input files and processing configuration

### Debug Mode
```bash
# Enable verbose logging
python v2/rag-system/main.py --input ./output --output ./rag-output --verbose

# Check processing statistics
cat ./rag-output/rag-config.json | jq '.statistics'
```

### Validation
```bash
# Validate output files
python v2/common/validation.py validate --file ./rag-output/rag-config.json --schema RAGKnowledgeBase

# Check knowledge base integrity
python v2/rag-system/main.py --input ./rag-output --output ./validation-test --strict
```

## =. Future Enhancements

### Planned Features
1. **Real Embedding Models**: Integration with sentence-transformers, OpenAI embeddings
2. **Advanced Vector Databases**: ChromaDB, Pinecone, Weaviate integration
3. **Semantic Search**: True vector similarity search
4. **Content Ranking**: Advanced relevance ranking algorithms
5. **Query Understanding**: Natural language query processing
6. **Content Updates**: Incremental knowledge base updates
7. **Multi-Modal Support**: Image and video content processing
8. **API Interface**: RESTful API for knowledge base access

### Extension Points
1. **Custom Content Processors**: Plugin system for new file types
2. **Custom Chunking Strategies**: Configurable chunking algorithms
3. **Custom Embedding Models**: Support for different embedding models
4. **Custom Search Filters**: Advanced filtering and faceting
5. **Custom Metadata Schemas**: Extensible metadata models

### Performance Improvements
1. **Parallel Processing**: Multi-threaded content processing
2. **Streaming Processing**: Process large files without loading entirely into memory
3. **Caching Layers**: Cache embeddings and search results
4. **Index Optimization**: Advanced indexing strategies
5. **Compression**: Compress stored embeddings and content

## =Ú API Reference

### RAGSystem Class
```python
class RAGSystem:
    def __init__(self, config: RAGProcessingConfig)
    def process_pipeline_outputs(self, input_dirs: List[Path], output_dir: Path) -> RAGProcessingResult
```

### RAGKnowledgeBaseManager Class
```python
class RAGKnowledgeBaseManager:
    def create_knowledge_base(self, name: str, chunks: List[ContentChunk]) -> RAGKnowledgeBase
    def save_knowledge_base(self, name: str, output_dir: Path)
    def search_knowledge_base(self, name: str, query: str, **kwargs) -> List[ContentChunk]
    def list_knowledge_bases(self) -> List[str]
    def get_knowledge_base(self, name: str) -> Optional[RAGKnowledgeBase]
```

### ContentProcessor Class
```python
class ContentProcessor:
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]
```

### TextChunker Class
```python
class TextChunker:
    def chunk_content(self, content_sections: List[Dict[str, Any]], file_path: Path) -> List[ContentChunk]
    def count_tokens(self, text: str) -> int
```

### VectorStore Class
```python
class VectorStore:
    def add_chunks(self, chunks: List[ContentChunk])
    def build_index(self)
    def search(self, query: str, content_type: Optional[str] = None, tags: Optional[List[str]] = None, limit: int = None) -> List[ContentChunk]
    def get_statistics(self) -> Dict[str, Any]
```

## <Æ Success Criteria

### Functional Requirements
-  Process all pipeline output files
-  Create separate knowledge bases by content type
-  Generate consistent embeddings
-  Enable content search and retrieval
-  Maintain metadata and source information
-  Validate all outputs against schemas

### Quality Requirements
-  Comprehensive error handling and logging
-  Performance optimization for large datasets
-  Configurable processing parameters
-  Detailed statistics and reporting
-  CLI interface with full argument parsing
-  Complete documentation and examples

### Integration Requirements
-  Compatible with all pipeline step outputs
-  Follow established pipeline patterns
-  Use existing validation utilities
-  Maintain schema compliance
-  Support incremental processing

---

**Step 8 of 9** - RAG System creates intelligent knowledge bases from all pipeline artifacts, enabling AI-powered content discovery and analysis across the entire project.