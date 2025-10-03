# Task 3: Advanced API Endpoint Detection and Schema Extraction

## Modern Framework Detection

### JavaScript/TypeScript Framework Detection

#### Express.js Advanced Detection
```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

class ExpressRouteDetector {
    constructor() {
        this.routes = [];
        this.middleware = [];
        this.schemas = new Map();
    }

    extractRoutes(code) {
        const ast = parser.parse(code, {
            sourceType: 'module',
            plugins: ['typescript', 'decorators-legacy', 'jsx', 'classProperties']
        });

        traverse(ast, {
            CallExpression: (path) => {
                this.analyzeRouteCall(path);
            },
            VariableDeclarator: (path) => {
                this.analyzeVariableDeclaration(path);
            }
        });

        return this.processRoutes();
    }

    analyzeRouteCall(path) {
        const callee = path.node.callee;

        // Express route detection: app.get(), router.post(), etc.
        if (callee.type === 'MemberExpression' &&
            ['app', 'router', 'api'].includes(callee.object.name)) {

            const method = callee.property.name;
            const args = path.node.arguments;

            if (args.length >= 1 && args[0].type === 'StringLiteral') {
                const routeInfo = {
                    method: method.toUpperCase(),
                    path: args[0].value,
                    type: 'express',
                    line: path.node.loc?.start.line,
                    handlers: this.extractHandlers(args.slice(1)),
                    middleware: this.extractMiddleware(args.slice(1)),
                    parameters: this.extractPathParameters(args[0].value),
                    schema: this.extractRouteSchema(path)
                };

                this.routes.push(routeInfo);
            }
        }

        // Advanced route patterns: route.use(), middleware chains
        if (callee.type === 'MemberExpression' &&
            callee.property.name === 'use') {
            this.analyzeMiddlewareChain(path);
        }
    }

    extractHandlers(handlerArgs) {
        return handlerArgs.map(arg => {
            if (arg.type === 'FunctionExpression' || arg.type === 'ArrowFunctionExpression') {
                return {
                    type: 'inline',
                    params: arg.params.map(p => ({
                        name: p.name || p.left?.name,
                        type: this.inferParameterType(p)
                    })),
                    body: this.extractFunctionBody(arg.body),
                    async: arg.async || false
                };
            } else if (arg.type === 'Identifier') {
                return {
                    type: 'reference',
                    name: arg.name
                };
            }
            return null;
        }).filter(Boolean);
    }

    extractPathParameters(path) {
        const params = [];
        const segments = path.split('/');

        for (const segment of segments) {
            if (segment.startsWith(':')) {
                params.push({
                    name: segment.slice(1),
                    type: 'path',
                    required: true,
                    description: `Path parameter: ${segment.slice(1)}`
                });
            } else if (segment.startsWith('*')) {
                params.push({
                    name: segment.slice(1),
                    type: 'wildcard',
                    required: false,
                    description: `Wildcard parameter: ${segment.slice(1)}`
                });
            }
        }

        return params;
    }

    extractRouteSchema(path) {
        // Extract validation schemas, response definitions
        const schema = {
            request: this.extractRequestSchema(path),
            response: this.extractResponseSchema(path),
            validation: this.extractValidationMiddleware(path)
        };

        return schema;
    }
}
```

#### Fastify Detection
```javascript
class FastifyRouteDetector {
    extractRoutes(code) {
        const ast = parser.parse(code, {
            sourceType: 'module',
            plugins: ['typescript', 'decorators-legacy']
        });

        const routes = [];

        traverse(ast, {
            CallExpression: (path) => {
                const callee = path.node.callee;

                // Fastify pattern: fastify.get(), fastify.route()
                if (callee.type === 'MemberExpression' &&
                    (callee.object.name === 'fastify' ||
                     (callee.object.type === 'MemberExpression' &&
                      callee.object.property.name === 'fastify'))) {

                    const method = callee.property.name;
                    const args = path.node.arguments;

                    if (method === 'route' && args.length >= 1) {
                        // Fastify.route({ method, url, schema, handler })
                        const routeConfig = this.extractRouteConfig(args[0]);
                        routes.push(routeConfig);
                    } else if (['get', 'post', 'put', 'delete', 'patch'].includes(method)) {
                        // Fastify.get(url, options, handler)
                        const routeInfo = {
                            method: method.toUpperCase(),
                            url: args[0]?.value,
                            options: this.extractRouteOptions(args[1]),
                            handler: this.extractHandler(args[args.length - 1])
                        };
                        routes.push(routeInfo);
                    }
                }
            }
        });

        return routes;
    }

    extractRouteConfig(configNode) {
        const config = {};

        if (configNode.type === 'ObjectExpression') {
            for (const prop of configNode.properties) {
                if (prop.key.type === 'Identifier') {
                    config[prop.key.name] = this.extractPropertyValue(prop.value);
                }
            }
        }

        return config;
    }

    extractRouteOptions(optionsNode) {
        const options = { schema: {} };

        if (optionsNode && optionsNode.type === 'ObjectExpression') {
            for (const prop of optionsNode.properties) {
                if (prop.key.type === 'Identifier' && prop.key.name === 'schema') {
                    options.schema = this.extractSchemaDefinition(prop.value);
                }
            }
        }

        return options;
    }

    extractSchemaDefinition(schemaNode) {
        // Extract JSON schema definitions from Fastify routes
        const schema = {};

        if (schemaNode.type === 'ObjectExpression') {
            for (const prop of schemaNode.properties) {
                if (prop.key.type === 'Identifier') {
                    schema[prop.key.name] = this.extractSchemaValue(prop.value);
                }
            }
        }

        return schema;
    }
}
```

### Python Advanced Framework Detection

#### FastAPI with Pydantic Schemas
```python
import ast
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class APIEndpoint:
    method: str
    path: str
    function_name: str
    parameters: List[Dict[str, Any]]
    response_model: Optional[str]
    status_code: Optional[int]
    tags: List[str]
    dependencies: List[str]
    pydantic_schemas: Dict[str, Any]
    description: str

class FastAPIAdvancedDetector:
    def __init__(self):
        self.endpoints = []
        self.schemas = {}
        self.dependencies = {}

    def extract_routes(self, tree: ast.AST, code: str) -> List[APIEndpoint]:
        """Extract FastAPI routes with full schema information."""

        # First pass: extract all Pydantic models
        self.extract_pydantic_schemas(tree)

        # Second pass: extract API endpoints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.decorator_list:
                endpoint = self.analyze_fastapi_function(node, code)
                if endpoint:
                    self.endpoints.append(endpoint)

        return self.endpoints

    def extract_pydantic_schemas(self, tree: ast.AST):
        """Extract Pydantic model definitions for schema generation."""
        for node in ast.walk(tree):
            if (isinstance(node, ast.ClassDef) and
                self.is_pydantic_model(node)):

                schema_info = {
                    'name': node.name,
                    'fields': self.extract_pydantic_fields(node),
                    'config': self.extract_pydantic_config(node),
                    'inheritance': [base.id for base in node.bases if isinstance(base, ast.Name)]
                }

                self.schemas[node.name] = schema_info

    def is_pydantic_model(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from Pydantic BaseModel."""
        for base in node.bases:
            if (isinstance(base, ast.Attribute) and
                base.attr == 'BaseModel'):
                return True
            if (isinstance(base, ast.Name) and
                base.id == 'BaseModel'):
                return True
        return False

    def extract_pydantic_fields(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract field definitions from Pydantic model."""
        fields = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_info = {
                    'name': item.target.id,
                    'type': self.get_type_annotation(item.annotation),
                    'default': self.get_default_value(item),
                    'validators': self.extract_field_validators(item),
                    'description': self.extract_field_description(item)
                }
                fields.append(field_info)

        return fields

    def analyze_fastapi_function(self, node: ast.FunctionDef, code: str) -> Optional[APIEndpoint]:
        """Analyze FastAPI function with comprehensive information extraction."""

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                method = self.get_http_method(decorator)
                if method:
                    path = self.get_route_path(decorator)

                    return APIEndpoint(
                        method=method.upper(),
                        path=path,
                        function_name=node.name,
                        parameters=self.extract_function_parameters(node),
                        response_model=self.extract_response_model(decorator),
                        status_code=self.extract_status_code(decorator),
                        tags=self.extract_tags(decorator),
                        dependencies=self.extract_dependencies(decorator),
                        pydantic_schemas=self.get_related_schemas(node),
                        description=ast.get_docstring(node) or ""
                    )

        return None

    def extract_function_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters with type information."""
        parameters = []

        # Extract regular parameters
        for arg in node.args.args:
            if arg.arg not in ['self', 'cls']:
                param_info = {
                    'name': arg.arg,
                    'type': self.get_type_annotation_string(arg),
                    'source': self.get_parameter_source(arg),
                    'required': not self.has_default_value(arg, node),
                    'default': self.get_default_value_for_param(arg, node),
                    'validation': self.extract_parameter_validation(arg)
                }
                parameters.append(param_info)

        return parameters

    def get_parameter_source(self, arg: ast.arg) -> str:
        """Determine parameter source (Path, Query, Body, etc.)."""
        # This would analyze the default value to determine the source
        # e.g., Query(...), Path(...), Body(...)
        return 'query'  # Simplified for example

    def get_related_schemas(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Get Pydantic schemas related to this function."""
        related_schemas = {}

        # Analyze return type annotation
        if node.returns:
            return_type_str = ast.unparse(node.returns)
            if return_type_str in self.schemas:
                related_schemas['response'] = self.schemas[return_type_str]

        # Analyze parameter types
        for arg in node.args.args:
            if hasattr(arg, 'type_annotation') and arg.type_annotation:
                param_type_str = ast.unparse(arg.type_annotation)
                if param_type_str in self.schemas:
                    if 'request' not in related_schemas:
                        related_schemas['request'] = {}
                    related_schemas['request'][arg.arg] = self.schemas[param_type_str]

        return related_schemas
```

#### GraphQL and gRPC Detection
```python
class GraphQLDetector:
    def extract_resolvers(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract GraphQL resolver functions."""
        resolvers = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                resolver_info = self.analyze_resolver_function(node)
                if resolver_info:
                    resolvers.append(resolver_info)

        return resolvers

    def analyze_resolver_function(self, node: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        """Analyze GraphQL resolver function."""
        # Check for GraphQL resolver patterns
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Name) and
                decorator.id in ['resolver', 'field_resolver']):

                return {
                    'name': node.name,
                    'type': 'graphql_resolver',
                    'parameters': self.extract_resolver_parameters(node),
                    'return_type': self.get_resolver_return_type(node),
                    'description': ast.get_docstring(node),
                    'field_name': self.extract_field_name(decorator, node)
                }

        return None

class gRPCDetector:
    def extract_services(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract gRPC service definitions."""
        services = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                service_info = self.analyze_grpc_service(node)
                if service_info:
                    services.append(service_info)

        return services

    def analyze_grpc_service(self, node: ast.ClassDef) -> Optional[Dict[str, Any]]:
        """Analyze gRPC service class."""
        if not self.is_grpc_service(node):
            return None

        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.analyze_grpc_method(item)
                if method_info:
                    methods.append(method_info)

        return {
            'name': node.name,
            'type': 'grpc_service',
            'methods': methods,
            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'description': ast.get_docstring(node)
        }

    def is_grpc_service(self, node: ast.ClassDef) -> bool:
        """Check if class is a gRPC service."""
        grpc_indicators = ['Servicer', 'Service', 'grpc']

        for base in node.bases:
            if isinstance(base, ast.Name):
                if any(indicator in base.id for indicator in grpc_indicators):
                    return True
            elif isinstance(base, ast.Attribute):
                if any(indicator in base.attr for indicator in grpc_indicators):
                    return True

        return False
```

## Schema and Validation Extraction

### OpenAPI Schema Generation
```python
from typing import Dict, Any
import json

class OpenAPISchemaGenerator:
    def __init__(self):
        self.openapi_spec = {
            "openapi": "3.1.0",
            "info": {"title": "API Documentation", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}}
        }

    def generate_from_endpoints(self, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Generate complete OpenAPI spec from detected endpoints."""

        for endpoint in endpoints:
            self.add_endpoint_to_spec(endpoint)

        return self.openapi_spec

    def add_endpoint_to_spec(self, endpoint: APIEndpoint):
        """Add single endpoint to OpenAPI specification."""
        path = endpoint.path
        method = endpoint.method.lower()

        if path not in self.openapi_spec['paths']:
            self.openapi_spec['paths'][path] = {}

        operation = {
            "summary": f"{endpoint.method} {path}",
            "operationId": f"{method}_{self.sanitize_operation_id(path)}",
            "description": endpoint.description,
            "tags": endpoint.tags,
            "parameters": self.generate_parameters(endpoint.parameters),
            "responses": self.generate_responses(endpoint.response_model, endpoint.status_code)
        }

        # Add request body if needed
        if self.has_request_body(endpoint):
            operation["requestBody"] = self.generate_request_body(endpoint)

        # Add schema definitions
        if endpoint.pydantic_schemas:
            self.add_schema_definitions(endpoint.pydantic_schemas)

        self.openapi_spec['paths'][path][method] = operation

    def generate_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate OpenAPI parameter definitions."""
        openapi_params = []

        for param in parameters:
            openapi_param = {
                "name": param['name'],
                "in": param.get('source', 'query'),
                "required": param['required'],
                "schema": self.generate_schema_from_type(param['type'])
            }

            if param.get('description'):
                openapi_param["description"] = param['description']

            openapi_params.append(openapi_param)

        return openapi_params

    def generate_schema_from_type(self, type_str: str) -> Dict[str, Any]:
        """Generate OpenAPI schema from type string."""
        type_mapping = {
            'str': {'type': 'string'},
            'int': {'type': 'integer'},
            'float': {'type': 'number'},
            'bool': {'type': 'boolean'},
            'list': {'type': 'array'},
            'dict': {'type': 'object'}
        }

        # Handle complex types (List[str], Optional[int], etc.)
        if 'List[' in type_str or 'list[' in type_str:
            inner_type = type_str.split('[')[1].split(']')[0]
            return {
                'type': 'array',
                'items': self.generate_schema_from_type(inner_type)
            }

        if 'Optional[' in type_str:
            inner_type = type_str.split('[')[1].split(']')[0]
            schema = self.generate_schema_from_type(inner_type)
            schema['nullable'] = True
            return schema

        return type_mapping.get(type_str, {'type': 'string'})

    def add_schema_definitions(self, schemas: Dict[str, Any]):
        """Add Pydantic schema definitions to OpenAPI components."""
        for schema_name, schema_info in schemas.items():
            if schema_name not in self.openapi_spec['components']['schemas']:
                self.openapi_spec['components']['schemas'][schema_name] = self.convert_pydantic_to_openapi(schema_info)

    def convert_pydantic_to_openapi(self, pydantic_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Pydantic schema to OpenAPI schema format."""
        properties = {}
        required = []

        for field in pydantic_schema.get('fields', []):
            field_name = field['name']
            properties[field_name] = {
                'type': self.map_python_type_to_openapi(field['type']),
                'description': field.get('description', '')
            }

            if not field.get('default'):
                required.append(field_name)

        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }
```

### Integration Pattern
```python
class ComprehensiveAPIDetector:
    def __init__(self):
        self.detectors = {
            'express': ExpressRouteDetector(),
            'fastify': FastifyRouteDetector(),
            'fastapi': FastAPIAdvancedDetector(),
            'flask': FlaskRouteDetector(),
            'graphql': GraphQLDetector(),
            'grpc': gRPCDetector()
        }
        self.schema_generator = OpenAPISchemaGenerator()

    def detect_all_apis(self, repo_path: str) -> Dict[str, Any]:
        """Comprehensive API detection across all frameworks."""
        results = {
            'endpoints': [],
            'schemas': {},
            'openapi_spec': None,
            'frameworks_detected': [],
            'statistics': {}
        }

        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)

                if file.endswith(('.py', '.js', '.ts')):
                    framework_results = self.analyze_file(file_path)

                    if framework_results['endpoints']:
                        results['endpoints'].extend(framework_results['endpoints'])
                        results['frameworks_detected'].append(framework_results['framework'])

        # Generate OpenAPI specification
        if results['endpoints']:
            results['openapi_spec'] = self.schema_generator.generate_from_endpoints(results['endpoints'])

        # Generate statistics
        results['statistics'] = self.generate_statistics(results)

        return results

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze single file for API definitions."""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        file_ext = os.path.splitext(file_path)[1]

        if file_ext == '.py':
            return self.analyze_python_file(code, file_path)
        elif file_ext in ['.js', '.ts']:
            return self.analyze_javascript_file(code, file_path)

        return {'endpoints': [], 'framework': 'unknown'}

    def generate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive API statistics."""
        endpoints = results['endpoints']

        stats = {
            'total_endpoints': len(endpoints),
            'methods': {},
            'frameworks': {},
            'path_patterns': {},
            'authentication_required': 0,
            'public_endpoints': 0
        }

        for endpoint in endpoints:
            # Count methods
            method = endpoint.get('method', 'UNKNOWN')
            stats['methods'][method] = stats['methods'].get(method, 0) + 1

            # Count frameworks
            framework = endpoint.get('type', 'unknown')
            stats['frameworks'][framework] = stats['frameworks'].get(framework, 0) + 1

            # Analyze path patterns
            path = endpoint.get('path', '')
            if path.startswith('/api'):
                stats['path_patterns']['api_routes'] = stats['path_patterns'].get('api_routes', 0) + 1
            if ':' in path or '{' in path:
                stats['path_patterns']['parameterized'] = stats['path_patterns'].get('parameterized', 0) + 1

        return stats

# Usage example
detector = ComprehensiveAPIDetector()
api_results = detector.detect_all_apis('./repository')
print(f"Detected {api_results['statistics']['total_endpoints']} API endpoints")
```

**Use Cases for RAG**: Complete API discovery across modern frameworks, automatic OpenAPI 3.1 specification generation, comprehensive schema extraction with Pydantic support, GraphQL resolver detection, gRPC service analysis, and intelligent API relationship mapping.