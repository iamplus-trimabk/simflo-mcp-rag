# Task 4: Automated Documentation Generation

## JavaScript JSDoc Generation

### Basic JSDoc from Function Analysis
```javascript
function generateJSDoc(functionInfo) {
    const { name, params, returnType, description } = functionInfo;

    let jsdoc = '/**\n';

    if (description) {
        jsdoc += ` * ${description}\n`;
    }

    // Add parameter documentation
    params.forEach(param => {
        const type = param.type || 'any';
        const desc = param.description || '';
        jsdoc += ` * @param {${type}} ${param.name} ${desc}\n`;
    });

    // Add return type
    if (returnType && returnType !== 'void') {
        jsdoc += ` * @returns {${returnType}} Return description\n`;
    }

    jsdoc += ' */';

    return jsdoc;
}

// Usage with AST extraction
function extractFunctionDocumentation(ast) {
    const functions = [];

    function traverse(node) {
        if (node.type === 'FunctionDeclaration') {
            const func = {
                name: node.id.name,
                params: node.params.map(param => ({
                    name: param.name,
                    type: 'any'  // Could be enhanced with TypeScript analysis
                })),
                returnType: 'any',
                description: `Function ${node.id.name}`
            };

            functions.push({
                ...func,
                jsdoc: generateJSDoc(func)
            });
        }
    }

    traverse(ast);
    return functions;
}
```

## Python Docstring Generation

### Basic Docstring from AST
```python
def generate_docstring(function_info):
    """Generate docstring from function analysis."""
    name = function_info['name']
    params = function_info['args']
    return_type = function_info.get('return_type', 'unknown')

    docstring = f'"""\n{name}('

    # Add parameters
    if params:
        param_list = ', '.join([f"{p}: type" for p in params])
        docstring += param_list

    docstring += f') -> {return_type}\n\n'

    # Add parameter descriptions
    for param in params:
        docstring += f"Args:\n    {param}: Description of {param}\n"

    docstring += f"\nReturns:\n    Description of return value\n\"\"\""

    return docstring

def extract_function_documentation(tree):
    """Extract function information and generate docstrings."""
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'return_type': 'unknown',  # Could be enhanced with type hints
                'existing_docstring': ast.get_docstring(node)
            }

            if not func_info['existing_docstring']:
                func_info['generated_docstring'] = generate_docstring(func_info)

            functions.append(func_info)

    return functions
```

## Markdown Documentation Generation

### Function Reference Generation
```python
def generate_function_markdown(functions, class_name=None):
    """Generate Markdown documentation for functions."""
    md = ""

    if class_name:
        md += f"## {class_name}\n\n"

    for func in functions:
        md += f"### {func['name']}\n\n"

        if func.get('existing_docstring'):
            md += f"{func['existing_docstring']}\n\n"
        elif func.get('generated_docstring'):
            md += f"{func['generated_docstring']}\n\n"

        # Add function signature
        params = ', '.join(func['args'])
        md += f"```python\n{func['name']}({params})\n```\n\n"

        md += "---\n\n"

    return md
```

### API Documentation Generation
```python
def generate_api_documentation(routes):
    """Generate API documentation from detected routes."""
    md = "# API Documentation\n\n"

    # Group by path
    paths = {}
    for route in routes:
        path = route['path']
        if path not in paths:
            paths[path] = []
        paths[path].append(route)

    # Generate documentation for each path
    for path, path_routes in paths.items():
        md += f"## {path}\n\n"

        for route in path_routes:
            method = route['method']
            md += f"### {method} {path}\n\n"
            md += f"Handler: `{route['function']}`\n\n"
            md += "**Description:**\n"
            md += "TODO: Add description\n\n"
            md += "**Parameters:**\n"
            md += "TODO: Document parameters\n\n"
            md += "**Response:**\n"
            md += "TODO: Document response format\n\n"
            md += "---\n\n"

    return md
```

### Integration Pattern
```python
def generate_repository_documentation(repo_path):
    """Generate complete documentation for a repository."""
    documentation = "# Repository Documentation\n\n"

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()

                tree = ast.parse(code)
                functions = extract_function_documentation(tree)

                if functions:
                    documentation += f"## {file}\n\n"
                    documentation += generate_function_markdown(functions)

    return documentation
```

**Use Cases for RAG**: Generate comprehensive code documentation for training, create API references, and provide context for code understanding.