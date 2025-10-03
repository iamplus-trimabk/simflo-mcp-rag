# Task 5: Content-Aware Chunking

## Code Chunking Strategies

### Function-Level Chunking
```python
def chunk_functions(code, language='python'):
    """Chunk code by function boundaries."""
    if language == 'python':
        import ast
        tree = ast.parse(code)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                lines = code.split('\n')
                chunk = '\n'.join(lines[start_line-1:end_line])

                chunks.append({
                    'content': chunk,
                    'type': 'function',
                    'name': node.name,
                    'start_line': start_line,
                    'end_line': end_line
                })

        return chunks
```

### Class-Level Chunking
```python
def chunk_classes(code, language='python'):
    """Chunk code by class boundaries."""
    if language == 'python':
        import ast
        tree = ast.parse(code)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                lines = code.split('\n')
                chunk = '\n'.join(lines[start_line-1:end_line])

                chunks.append({
                    'content': chunk,
                    'type': 'class',
                    'name': node.name,
                    'start_line': start_line,
                    'end_line': end_line
                })

        return chunks
```

## Documentation Chunking

### Markdown Section Chunking
```python
def chunk_markdown(content):
    """Chunk markdown by sections (H1, H2, H3)."""
    import re
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_title = "Introduction"

    for line in lines:
        # Check if line is a header
        header_match = re.match(r'^(#{1,3})\s+(.+)', line)
        if header_match:
            # Save previous chunk
            if current_chunk:
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'type': 'documentation',
                    'title': current_title.strip()
                })
                current_chunk = []

            # Start new chunk
            level = len(header_match.group(1))
            current_title = header_match.group(2)
            current_chunk.append(line)
        else:
            current_chunk.append(line)

    # Add final chunk
    if current_chunk:
        chunks.append({
            'content': '\n'.join(current_chunk),
            'type': 'documentation',
            'title': current_title.strip()
        })

    return chunks
```

### Mixed Content Chunking
```python
def chunk_mixed_content(content, file_extension):
    """Intelligently chunk mixed code and documentation."""
    if file_extension in ['.py', '.js']:
        # Separate code and docstrings
        code_chunks = chunk_functions(content, 'python' if file_extension == '.py' else 'javascript')
        docstring_chunks = extract_docstrings(content)

        # Add metadata for different content types
        for chunk in code_chunks:
            chunk['content_type'] = 'code'
            chunk['user_roles'] = ['developer']

        for chunk in docstring_chunks:
            chunk['content_type'] = 'documentation'
            chunk['user_roles'] = ['developer', 'architect']

        return code_chunks + docstring_chunks

    elif file_extension == '.md':
        return chunk_markdown(content)

    else:
        # Fallback to fixed-size chunking
        return chunk_fixed_size(content)
```

## Chunking for Different User Roles

### Role-Specific Chunking
```python
def chunk_for_roles(content, target_roles):
    """Create chunks optimized for specific user roles."""
    chunks = []

    if 'architect' in target_roles:
        # High-level chunks: classes, modules, imports
        high_level = extract_high_level_structure(content)
        chunks.extend(high_level)

    if 'developer' in target_roles:
        # Detailed chunks: functions, methods
        detailed = extract_functions_and_methods(content)
        chunks.extend(detailed)

    if 'api_user' in target_roles:
        # API-focused chunks: endpoints, interfaces
        api_chunks = extract_api_interfaces(content)
        chunks.extend(api_chunks)

    return chunks
```

### Chunk Metadata Enhancement
```python
def enhance_chunk_metadata(chunks, file_path):
    """Add comprehensive metadata to chunks."""
    for chunk in chunks:
        chunk['file_path'] = file_path
        chunk['timestamp'] = datetime.now().isoformat()
        chunk['abstraction_level'] = determine_abstraction_level(chunk)
        chunk['language'] = detect_language(file_path)

        # Add complexity score
        chunk['complexity'] = calculate_complexity(chunk['content'])

        # Add cross-references
        chunk['references'] = find_references(chunk['content'])

    return chunks
```

### Size Optimization
```python
def optimize_chunk_size(chunks, max_size=512):
    """Ensure chunks don't exceed maximum token limits."""
    optimized = []

    for chunk in chunks:
        if len(chunk['content'].split()) <= max_size:
            optimized.append(chunk)
        else:
            # Split oversized chunks
            sub_chunks = split_large_chunk(chunk, max_size)
            optimized.extend(sub_chunks)

    return optimized
```

**Use Cases for RAG**: Create contextually appropriate chunks that preserve code structure while being optimized for vector search and role-based filtering.