# Task 11: Advanced Automated Diagram Generation

## Overview

Automated diagram generation transforms static code analysis into visual representations that enhance understanding of complex systems. This comprehensive approach supports multiple diagram types, interactive visualizations, and intelligent layout algorithms for modern software documentation.

## Advanced Call Graph Generation

### Enhanced Python Call Graph Analysis

```python
import ast
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import re

@dataclass
class FunctionInfo:
    name: str
    line: int
    complexity: int
    calls: List[str]
    called_by: List[str]
    params: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: List[str]

class AdvancedCallGraphAnalyzer:
    """Enhanced call graph analyzer with comprehensive function relationships."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.functions: Dict[str, FunctionInfo] = {}
        self.modules: Set[str] = set()
        self.classes: Dict[str, List[str]] = defaultdict(list)

    def analyze_file(self, file_path: str) -> Tuple[nx.DiGraph, Dict[str, FunctionInfo]]:
        """Analyze a single Python file for call relationships."""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)
        return self.analyze_tree(tree, code, file_path)

    def analyze_tree(self, tree: ast.AST, code: str, file_path: str = "") -> Tuple[nx.DiGraph, Dict[str, FunctionInfo]]:
        """Comprehensive AST analysis for function relationships."""
        # Extract all function definitions first
        self._extract_function_definitions(tree, code)

        # Extract function calls and build relationships
        self._extract_function_calls(tree)

        # Analyze complexity metrics
        self._calculate_complexity_metrics(tree)

        # Build class hierarchies
        self._extract_class_relationships(tree)

        return self.graph, self.functions

    def _extract_function_definitions(self, tree: ast.AST, code: str):
        """Extract function definitions with metadata."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                params = [arg.arg for arg in node.args.args]
                decorators = [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]

                # Extract docstring
                docstring = ast.get_docstring(node)

                # Extract return type annotation
                return_type = None
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        return_type = node.returns.id
                    elif hasattr(node.returns, 'id'):
                        return_type = node.returns.id

                self.functions[func_name] = FunctionInfo(
                    name=func_name,
                    line=node.lineno,
                    complexity=1,  # Will be calculated later
                    calls=[],
                    called_by=[],
                    params=params,
                    return_type=return_type,
                    docstring=docstring,
                    decorators=decorators
                )

                self.graph.add_node(func_name,
                                  type='function',
                                  line=node.lineno,
                                  params=params,
                                  complexity=1)

    def _extract_function_calls(self, tree: ast.AST):
        """Extract function calls and build call relationships."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                caller = node.name

                # Find all calls within this function
                calls = self._find_calls_in_function(node)

                for call in calls:
                    if call in self.functions:
                        self.functions[caller].calls.append(call)
                        self.functions[call].called_by.append(caller)
                        self.graph.add_edge(caller, call)

    def _find_calls_in_function(self, func_node: ast.FunctionDef) -> List[str]:
        """Find all function calls within a function."""
        calls = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                call_name = self._extract_call_name(node)
                if call_name:
                    calls.append(call_name)

        return calls

    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            # Handle method calls and module functions
            return self._extract_attribute_chain(call_node.func)
        return None

    def _extract_attribute_chain(self, node: ast.Attribute) -> str:
        """Extract full attribute chain (e.g., module.function)."""
        chain = []
        current = node

        while isinstance(current, ast.Attribute):
            chain.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            chain.append(current.id)

        return '.'.join(reversed(chain))

    def _calculate_complexity_metrics(self, tree: ast.AST):
        """Calculate cyclomatic complexity for all functions."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_function_complexity(node)
                self.functions[node.name].complexity = complexity
                self.graph.nodes[node.name]['complexity'] = complexity

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _extract_class_relationships(self, tree: ast.AST):
        """Extract class hierarchies and method relationships."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name

                # Find methods in this class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = f"{class_name}.{item.name}"
                        self.classes[class_name].append(method_name)

                        # Update function info to include class context
                        if item.name in self.functions:
                            self.functions[item.name].name = method_name
                            self.graph.nodes[item.name]['class'] = class_name

def generate_advanced_mermaid_diagram(graph: nx.DiGraph, functions: Dict[str, FunctionInfo],
                                     title: str = "Advanced Call Flow",
                                     layout: str = "TD") -> str:
    """Generate enhanced Mermaid diagram with rich metadata."""
    mermaid = f"graph {layout}\n    title[{title}]\n"

    # Group functions by complexity for visual clustering
    high_complexity = [f for f, info in functions.items() if info.complexity > 5]
    medium_complexity = [f for f, info in functions.items() if 2 <= info.complexity <= 5]
    low_complexity = [f for f, info in functions.items() if info.complexity < 2]

    # Create subgraphs for complexity groups
    if high_complexity:
        mermaid += "    subgraph High Complexity Functions\n"
        for func in high_complexity:
            info = functions[func]
            safe_name = func.replace('(', '_').replace(')', '_').replace('.', '_')
            mermaid += f"        {safe_name}[{func}<br/><small>C: {info.complexity}</small>]\n"
        mermaid += "    end\n"

    if medium_complexity:
        mermaid += "    subgraph Medium Complexity Functions\n"
        for func in medium_complexity:
            info = functions[func]
            safe_name = func.replace('(', '_').replace(')', '_').replace('.', '_')
            mermaid += f"        {safe_name}[{func}<br/><small>C: {info.complexity}</small>]\n"
        mermaid += "    end\n"

    # Add edges with relationship information
    for edge in graph.edges():
        source, target = edge
        safe_source = source.replace('(', '_').replace(')', '_').replace('.', '_')
        safe_target = target.replace('(', '_').replace(')', '_').replace('.', '_')

        # Count call frequency if available
        call_count = functions[source].calls.count(target)
        label = f" ({call_count}x)" if call_count > 1 else ""

        mermaid += f"    {safe_source} -->{label} {safe_target}\n"

    return mermaid
```

### Advanced JavaScript/TypeScript Call Graph Analysis

```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const graphviz = require('graphviz');

class JavaScriptCallGraphAnalyzer {
    constructor() {
        this.graph = new Map();
        this.functions = new Map();
        this.classes = new Map();
        this.modules = new Set();
        this.imports = new Map();
    }

    analyzeCode(code, options = {}) {
        const defaultOptions = {
            sourceType: 'module',
            plugins: [
                'typescript',
                'jsx',
                'classProperties',
                'optionalChaining',
                'nullishCoalescingOperator',
                'decorators-legacy',
                'objectRestSpread',
                'asyncGenerators',
                'functionBind',
                'exportDefaultFrom',
                'exportNamespaceFrom',
                'dynamicImport',
                'classPrivateProperties'
            ]
        };

        const ast = parser.parse(code, { ...defaultOptions, ...options });
        return this.analyzeAST(ast, code);
    }

    analyzeAST(ast, code) {
        // Clear previous analysis
        this.graph.clear();
        this.functions.clear();
        this.classes.clear();
        this.modules.clear();

        // Extract imports and dependencies
        this.extractImports(ast);

        // Extract function and class definitions
        this.extractFunctionDefinitions(ast);
        this.extractClassDefinitions(ast);

        // Build call relationships
        this.buildCallRelationships(ast);

        // Calculate complexity metrics
        this.calculateComplexity(ast);

        return {
            graph: this.graph,
            functions: this.functions,
            classes: this.classes,
            imports: this.imports,
            modules: this.modules
        };
    }

    extractImports(ast) {
        traverse(ast, {
            ImportDeclaration(path) {
                const source = path.node.source.value;
                const specifiers = path.node.specifiers.map(spec => ({
                    imported: spec.imported?.name || 'default',
                    local: spec.local.name
                }));

                this.imports.set(source, specifiers);
                if (!source.startsWith('.')) {
                    this.modules.add(source);
                }
            },

            CallExpression(path) {
                if (path.node.callee.type === 'Import') {
                    // Handle dynamic imports
                    const source = path.node.arguments[0]?.value;
                    if (source && typeof source === 'string') {
                        this.modules.add(source);
                    }
                }
            }
        });
    }

    extractFunctionDefinitions(ast) {
        traverse(ast, {
            FunctionDeclaration: (path) => {
                const node = path.node;
                const funcName = node.id?.name || 'anonymous';

                this.functions.set(funcName, {
                    name: funcName,
                    type: 'function',
                    line: node.loc?.start.line || 0,
                    params: node.params.map(p => this.extractParameterName(p)),
                    isAsync: node.async,
                    isGenerator: node.generator,
                    calls: new Set(),
                    calledBy: new Set(),
                    complexity: 1,
                    decorators: [],
                    docstring: this.extractJSDoc(path.parentPath)
                });

                this.graph.set(funcName, new Set());
            },

            ArrowFunctionExpression: (path) => {
                const parent = path.parent;
                let funcName = 'arrow_function';

                if (parent.type === 'VariableDeclarator' && parent.id.name) {
                    funcName = parent.id.name;
                } else if (parent.type === 'AssignmentExpression' && parent.left.name) {
                    funcName = parent.left.name;
                } else if (parent.type === 'Property' && parent.key.name) {
                    funcName = `${this.getCurrentClassName(path.parentPath)}.${parent.key.name}`;
                }

                this.functions.set(funcName, {
                    name: funcName,
                    type: 'arrow',
                    line: path.node.loc?.start.line || 0,
                    params: path.node.params.map(p => this.extractParameterName(p)),
                    isAsync: path.node.async,
                    calls: new Set(),
                    calledBy: new Set(),
                    complexity: 1,
                    decorators: []
                });

                this.graph.set(funcName, new Set());
            },

            MethodDefinition: (path) => {
                const node = path.node;
                const methodName = node.key.name;
                const className = this.getCurrentClassName(path.parentPath);
                const fullName = `${className}.${methodName}`;

                this.functions.set(fullName, {
                    name: fullName,
                    type: 'method',
                    line: node.loc?.start.line || 0,
                    params: node.value.params.map(p => this.extractParameterName(p)),
                    isAsync: node.value.async,
                    isGenerator: node.value.generator,
                    calls: new Set(),
                    calledBy: new Set(),
                    complexity: 1,
                    decorators: node.decorators?.map(d => d.expression?.name || 'decorator') || [],
                    isStatic: node.static,
                    docstring: this.extractJSDoc(path)
                });

                this.graph.set(fullName, new Set());
            }
        });
    }

    extractClassDefinitions(ast) {
        traverse(ast, {
            ClassDeclaration: (path) => {
                const node = path.node;
                const className = node.id?.name || 'AnonymousClass';

                const superClass = node.superClass?.name || null;
                const methods = [];
                const properties = [];

                path.get('body.body').forEach(memberPath => {
                    const member = memberPath.node;
                    if (member.type === 'MethodDefinition') {
                        methods.push({
                            name: member.key.name,
                            kind: member.kind,
                            static: member.static,
                            async: member.value.async,
                            generator: member.value.generator
                        });
                    } else if (member.type === 'ClassProperty') {
                        properties.push({
                            name: member.key.name,
                            static: member.static,
                            type: this.extractTypeAnnotation(member)
                        });
                    }
                });

                this.classes.set(className, {
                    name: className,
                    superClass,
                    methods,
                    properties,
                    decorators: node.decorators?.map(d => d.expression?.name || 'decorator') || [],
                    line: node.loc?.start.line || 0
                });
            }
        });
    }

    buildCallRelationships(ast) {
        traverse(ast, {
            FunctionDeclaration: (path) => {
                const caller = path.node.id?.name;
                if (caller) {
                    this.findCallsInFunction(path, caller);
                }
            },

            ArrowFunctionExpression: (path) => {
                const funcName = this.getFunctionName(path);
                if (funcName) {
                    this.findCallsInFunction(path, funcName);
                }
            },

            MethodDefinition: (path) => {
                const methodName = path.node.key.name;
                const className = this.getCurrentClassName(path.parentPath);
                const fullName = `${className}.${methodName}`;
                this.findCallsInFunction(path.get('value'), fullName);
            }
        });
    }

    findCallsInFunction(path, caller) {
        traverse(path.node, {
            CallExpression: (callPath) => {
                const callee = callPath.node.callee;
                let calledFunction = null;

                if (callee.type === 'Identifier') {
                    calledFunction = callee.name;
                } else if (callee.type === 'MemberExpression') {
                    calledFunction = this.extractMemberExpression(callee);
                }

                if (calledFunction && this.functions.has(calledFunction)) {
                    this.functions.get(caller).calls.add(calledFunction);
                    this.functions.get(calledFunction).calledBy.add(caller);
                    this.graph.get(caller)?.add(calledFunction);
                }
            }
        });
    }

    calculateComplexity(ast) {
        this.functions.forEach((funcInfo, funcName) => {
            // Find the function node and calculate cyclomatic complexity
            traverse(ast, {
                FunctionDeclaration: (path) => {
                    if (path.node.id?.name === funcName) {
                        funcInfo.complexity = this.calculateFunctionComplexity(path.node);
                    }
                },

                ArrowFunctionExpression: (path) => {
                    const name = this.getFunctionName(path);
                    if (name === funcName) {
                        funcInfo.complexity = this.calculateFunctionComplexity(path.node);
                    }
                },

                MethodDefinition: (path) => {
                    const methodName = path.node.key.name;
                    const className = this.getCurrentClassName(path.parentPath);
                    const fullName = `${className}.${methodName}`;
                    if (fullName === funcName) {
                        funcInfo.complexity = this.calculateFunctionComplexity(path.node.value);
                    }
                }
            });
        });
    }

    calculateFunctionComplexity(node) {
        let complexity = 1; // Base complexity

        traverse(node, {
            IfStatement: () => complexity++,
            ConditionalExpression: () => complexity++,
            LogicalExpression: (path) => {
                if (path.node.operator === '&&') complexity++;
            },
            SwitchCase: () => complexity++,
            ForStatement: () => complexity++,
            ForInStatement: () => complexity++,
            ForOfStatement: () => complexity++,
            WhileStatement: () => complexity++,
            DoWhileStatement: () => complexity++,
            CatchClause: () => complexity++,
            YieldExpression: () => complexity++,
            AwaitExpression: () => complexity++
        });

        return complexity;
    }

    // Helper methods
    extractParameterName(param) {
        if (param.type === 'Identifier') {
            return param.name;
        } else if (param.type === 'AssignmentPattern') {
            return this.extractParameterName(param.left);
        } else if (param.type === 'RestElement') {
            return `...${param.argument.name}`;
        }
        return 'unknown';
    }

    extractMemberExpression(node) {
        const parts = [];
        let current = node;

        while (current.type === 'MemberExpression') {
            if (current.property.type === 'Identifier') {
                parts.unshift(current.property.name);
            }
            current = current.object;
        }

        if (current.type === 'Identifier') {
            parts.unshift(current.name);
        }

        return parts.join('.');
    }

    getCurrentClassName(path) {
        while (path && !path.isClassBody()) {
            path = path.parentPath;
        }
        return path?.parentPath?.node.id?.name || 'UnknownClass';
    }

    getFunctionName(path) {
        const parent = path.parent;
        if (parent.type === 'VariableDeclarator' && parent.id.name) {
            return parent.id.name;
        } else if (parent.type === 'AssignmentExpression' && parent.left.name) {
            return parent.left.name;
        } else if (parent.type === 'Property' && parent.key.name) {
            const className = this.getCurrentClassName(path.parentPath.parentPath);
            return `${className}.${parent.key.name}`;
        }
        return null;
    }

    extractJSDoc(path) {
        const leadingComments = path.node.leadingComments;
        if (leadingComments) {
            const jsDocComment = leadingComments.find(comment =>
                comment.type === 'CommentBlock' && comment.value.startsWith('*')
            );
            return jsDocComment ? jsDocComment.value : null;
        }
        return null;
    }

    extractTypeAnnotation(node) {
        return node.typeAnnotation?.typeAnnotation?.typeName?.name || 'any';
    }
}

function generateAdvancedMermaidDiagram(analyzer, title = "JavaScript Call Flow") {
    let mermaid = `graph TD\n    title[${title}]\n`;

    // Group functions by complexity
    const functions = Array.from(analyzer.functions.entries());
    const highComplexity = functions.filter(([_, info]) => info.complexity > 10);
    const mediumComplexity = functions.filter(([_, info]) => info.complexity >= 3 && info.complexity <= 10);
    const lowComplexity = functions.filter(([_, info]) => info.complexity < 3);

    // Create complexity-based subgraphs
    if (highComplexity.length > 0) {
        mermaid += "    subgraph High Complexity Functions\n";
        highComplexity.forEach(([name, info]) => {
            const safeName = name.replace(/[^a-zA-Z0-9]/g, '_');
            mermaid += `        ${safeName}["${name}<br/><small>C: ${info.complexity}</small>"]\n`;
        });
        mermaid += "    end\n";
    }

    if (mediumComplexity.length > 0) {
        mermaid += "    subgraph Medium Complexity Functions\n";
        mediumComplexity.forEach(([name, info]) => {
            const safeName = name.replace(/[^a-zA-Z0-9]/g, '_');
            mermaid += `        ${safeName}["${name}<br/><small>C: ${info.complexity}</small>"]\n`;
        });
        mermaid += "    end\n";
    }

    // Add low complexity functions without grouping
    lowComplexity.forEach(([name, info]) => {
        const safeName = name.replace(/[^a-zA-Z0-9]/g, '_');
        mermaid += `    ${safeName}["${name}<br/><small>C: ${info.complexity}</small>"]\n`;
    });

    // Add call relationships
    analyzer.graph.forEach((targets, caller) => {
        const safeCaller = caller.replace(/[^a-zA-Z0-9]/g, '_');
        targets.forEach(callee => {
            const safeCallee = callee.replace(/[^a-zA-Z0-9]/g, '_');
            const callCount = analyzer.functions.get(caller)?.calls.size || 1;
            const label = callCount > 1 ? ` (${callCount} calls)` : '';
            mermaid += `    ${safeCaller} -->${label} ${safeCallee}\n`;
        });
    });

    // Add class groupings if any
    if (analyzer.classes.size > 0) {
        mermaid += "\n    subgraph Classes\n";
        analyzer.classes.forEach((classInfo, className) => {
            const safeName = className.replace(/[^a-zA-Z0-9]/g, '_');
            mermaid += `        class_${safeName}["${className}<br/><small>Class</small>"]\n`;
        });
        mermaid += "    end\n";
    }

    return mermaid;
}
```

## Advanced API Workflow Diagrams

### Comprehensive API Flow Analysis

```python
import yaml
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class APIEndpoint:
    path: str
    method: HTTPMethod
    operation_id: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Dict] = None
    request_body: Optional[Dict] = None
    responses: Dict[int, Dict] = None
    tags: List[str] = None
    security: List[Dict] = None
    rate_limit: Optional[str] = None

@dataclass
class APIWorkflow:
    name: str
    description: str
    endpoints: List[APIEndpoint]
    sequence: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]] = None
    error_handling: List[Dict[str, Any]] = None

class APIWorkflowAnalyzer:
    """Advanced API workflow analyzer with OpenAPI/Swagger support."""

    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self.workflows: List[APIWorkflow] = []
        self.resource_groups: Dict[str, List[APIEndpoint]] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def load_openapi_spec(self, spec_path: str) -> None:
        """Load OpenAPI specification from file."""
        with open(spec_path, 'r', encoding='utf-8') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)

        self.parse_openapi_spec(spec)

    def parse_openapi_spec(self, spec: Dict) -> None:
        """Parse OpenAPI specification and extract workflows."""
        paths = spec.get('paths', {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.upper() in [m.value for m in HTTPMethod]:
                    endpoint = self._create_endpoint(path, method, operation)
                    self.endpoints.append(endpoint)

        self._group_endpoints_by_resource()
        self._extract_dependencies()
        self._identify_workflows()

    def _create_endpoint(self, path: str, method: str, operation: Dict) -> APIEndpoint:
        """Create API endpoint from OpenAPI operation."""
        return APIEndpoint(
            path=path,
            method=HTTPMethod(method.upper()),
            operation_id=operation.get('operationId'),
            description=operation.get('description'),
            parameters=operation.get('parameters', []),
            request_body=operation.get('requestBody'),
            responses=operation.get('responses', {}),
            tags=operation.get('tags', []),
            security=operation.get('security', []),
            rate_limit=operation.get('x-rate-limit')
        )

    def _group_endpoints_by_resource(self) -> None:
        """Group endpoints by resource type."""
        self.resource_groups.clear()

        for endpoint in self.endpoints:
            resource = self._extract_resource_name(endpoint.path)
            if resource not in self.resource_groups:
                self.resource_groups[resource] = []
            self.resource_groups[resource].append(endpoint)

    def _extract_resource_name(self, path: str) -> str:
        """Extract resource name from API path."""
        # Remove leading/trailing slashes and split
        segments = [s for s in path.split('/') if s]

        if not segments:
            return 'root'

        # Extract main resource (first segment after version if present)
        if segments[0].startswith('v') and segments[0][1:].isdigit():
            return segments[1] if len(segments) > 1 else 'root'

        return segments[0]

    def _extract_dependencies(self) -> None:
        """Extract dependencies between endpoints based on path patterns and responses."""
        self.dependencies.clear()

        for endpoint in self.endpoints:
            dependencies = set()

            # Analyze path parameters
            path_params = [p['name'] for p in endpoint.parameters if p.get('in') == 'path']

            # Look for endpoints that create resources used by this endpoint
            for other_endpoint in self.endpoints:
                if other_endpoint != endpoint:
                    if self._has_dependency(other_endpoint, endpoint, path_params):
                        dependencies.add(other_endpoint.path)

            self.dependencies[endpoint.path] = dependencies

    def _has_dependency(self, source: APIEndpoint, target: APIEndpoint, path_params: List[str]) -> bool:
        """Check if source endpoint creates resources used by target endpoint."""
        # Check if source is POST (create) and target uses the same resource
        if source.method == HTTPMethod.POST:
            source_resource = self._extract_resource_name(source.path)
            target_resource = self._extract_resource_name(target.path)

            if source_resource == target_resource:
                return True

        # Check response schemas for references
        if source.responses and target.parameters:
            source_responses = list(source.responses.values())
            if source_responses and 'schema' in source_responses[0]:
                source_schema = source_responses[0]['schema']
                for param in target.parameters:
                    if '$ref' in param.get('schema', {}):
                        ref = param['schema']['$ref']
                        if self._schema_references_match(source_schema, ref):
                            return True

        return False

    def _schema_references_match(self, schema: Dict, ref: str) -> bool:
        """Check if schema matches a reference."""
        # Simple implementation - in practice, this would be more sophisticated
        if '$ref' in schema:
            return schema['$ref'] == ref
        return False

    def _identify_workflows(self) -> None:
        """Identify common API workflows based on REST patterns."""
        self.workflows.clear()

        # CRUD workflow
        for resource, endpoints in self.resource_groups.items():
            crud_workflow = self._create_crud_workflow(resource, endpoints)
            if crud_workflow:
                self.workflows.append(crud_workflow)

        # Authentication workflows
        auth_workflow = self._create_auth_workflow()
        if auth_workflow:
            self.workflows.append(auth_workflow)

        # Search and filtering workflows
        search_workflow = self._create_search_workflow()
        if search_workflow:
            self.workflows.append(search_workflow)

    def _create_crud_workflow(self, resource: str, endpoints: List[APIEndpoint]) -> Optional[APIWorkflow]:
        """Create CRUD workflow for a resource."""
        operations = {ep.method: ep for ep in endpoints}

        if HTTPMethod.GET not in operations:
            return None

        sequence = [
            {'step': 1, 'operation': 'read', 'method': 'GET', 'endpoint': operations[HTTPMethod.GET].path}
        ]

        if HTTPMethod.POST in operations:
            sequence.append({
                'step': 2,
                'operation': 'create',
                'method': 'POST',
                'endpoint': operations[HTTPMethod.POST].path
            })

        if HTTPMethod.PUT in operations or HTTPMethod.PATCH in operations:
            put_or_patch = operations.get(HTTPMethod.PUT, operations.get(HTTPMethod.PATCH))
            sequence.append({
                'step': 3,
                'operation': 'update',
                'method': put_or_patch.method.value,
                'endpoint': put_or_patch.path
            })

        if HTTPMethod.DELETE in operations:
            sequence.append({
                'step': 4,
                'operation': 'delete',
                'method': 'DELETE',
                'endpoint': operations[HTTPMethod.DELETE].path
            })

        return APIWorkflow(
            name=f"{resource.title()} CRUD",
            description=f"Complete CRUD operations for {resource} resource",
            endpoints=endpoints,
            sequence=sequence,
            error_handling=[
                {'step': '*', 'error': '404', 'handling': 'Resource not found'},
                {'step': '*', 'error': '400', 'handling': 'Validation error'},
                {'step': '*', 'error': '401', 'handling': 'Authentication required'},
                {'step': '*', 'error': '403', 'handling': 'Insufficient permissions'}
            ]
        )

    def _create_auth_workflow(self) -> Optional[APIWorkflow]:
        """Create authentication workflow."""
        auth_endpoints = [ep for ep in self.endpoints if 'auth' in ep.tags or 'login' in ep.path.lower()]

        if not auth_endpoints:
            return None

        sequence = []
        for i, endpoint in enumerate(auth_endpoints[:3], 1):  # Limit to first 3 auth endpoints
            sequence.append({
                'step': i,
                'operation': 'authenticate',
                'method': endpoint.method.value,
                'endpoint': endpoint.path
            })

        return APIWorkflow(
            name="Authentication",
            description="User authentication and authorization flow",
            endpoints=auth_endpoints,
            sequence=sequence,
            conditions=[
                {'condition': 'valid_credentials', 'outcome': 'access_token'},
                {'condition': 'invalid_credentials', 'outcome': '401 Unauthorized'}
            ]
        )

    def _create_search_workflow(self) -> Optional[APIWorkflow]:
        """Create search and filtering workflow."""
        search_endpoints = [ep for ep in self.endpoints if 'search' in ep.path.lower() or 'filter' in ep.path.lower()]

        if not search_endpoints:
            return None

        sequence = []
        for i, endpoint in enumerate(search_endpoints[:3], 1):
            sequence.append({
                'step': i,
                'operation': 'search',
                'method': endpoint.method.value,
                'endpoint': endpoint.path
            })

        return APIWorkflow(
            name="Search & Filter",
            description="Search and filtering operations",
            endpoints=search_endpoints,
            sequence=sequence
        )

def generate_comprehensive_mermaid_workflow(workflow: APIWorkflow, style: str = "TD") -> str:
    """Generate comprehensive Mermaid workflow diagram."""
    mermaid = f"graph {style}\n    title[{workflow.name}]\n"

    # Add description
    if workflow.description:
        mermaid += f"\n    subgraph Description\n        desc[{workflow.description}]\n    end\n"

    # Group endpoints by resource
    resource_groups = {}
    for endpoint in workflow.endpoints:
        resource = endpoint.path.split('/')[1] if '/' in endpoint.path else 'root'
        if resource not in resource_groups:
            resource_groups[resource] = []
        resource_groups[resource].append(endpoint)

    # Create resource subgraphs
    for resource, endpoints in resource_groups.items():
        safe_resource = resource.replace('-', '_').replace('.', '_')
        mermaid += f"\n    subgraph {resource.title()}\n"

        for endpoint in endpoints:
            safe_path = endpoint.path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
            node_label = f"{endpoint.method.value} {endpoint.path}"
            if endpoint.operation_id:
                node_label += f"<br/><small>{endpoint.operation_id}</small>"

            mermaid += f"        {safe_path}[{node_label}]\n"

        mermaid += "    end\n"

    # Add sequence flow
    for i, step in enumerate(workflow.sequence):
        current_node = step['endpoint'].replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')

        if i < len(workflow.sequence) - 1:
            next_step = workflow.sequence[i + 1]
            next_node = next_step['endpoint'].replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
            mermaid += f"    {current_node} -->|{step['operation']}| {next_node}\n"

    # Add error handling if present
    if workflow.error_handling:
        mermaid += "\n    subgraph Error Handling\n"
        for error in workflow.error_handling[:3]:  # Limit to 3 error handlers
            safe_name = f"error_{error['error'].replace(' ', '_')}"
            mermaid += f"        {safe_name}{{Error {error['error']}<br/><small>{error['handling']}</small>}}\n"
        mermaid += "    end\n"

        # Connect to error handling
        for endpoint in workflow.endpoints:
            safe_path = endpoint.path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
            mermaid += f"    {safe_path} -.->|Error| error_400\n"
            mermaid += f"    {safe_path} -.->|Error| error_401\n"

    return mermaid

def generate_sequence_diagram(workflow: APIWorkflow) -> str:
    """Generate sequence diagram for API workflow."""
    mermaid = f"sequenceDiagram\n    title {workflow.name}\n"

    # Add actors
    mermaid += "    participant User\n"
    mermaid += "    participant API_Gateway\n"

    # Add unique services
    services = set()
    for endpoint in workflow.endpoints:
        service = endpoint.path.split('/')[1] if '/' in endpoint.path else 'Service'
        services.add(service)

    for service in sorted(services):
        safe_service = service.replace('-', '_')
        mermaid += f"    participant {safe_service}\n"

    # Add sequence
    for step in workflow.sequence:
        method = step['method']
        endpoint = step['endpoint']
        operation = step['operation']

        service = endpoint.split('/')[1] if '/' in endpoint else 'Service'
        safe_service = service.replace('-', '_')

        mermaid += f"\n    User->>API_Gateway: {method} {endpoint}\n"
        mermaid += f"    API_Gateway->>{safe_service}: {operation.title()} Request\n"
        mermaid += f"    {safe_service}-->>API_Gateway: {operation.title()} Response\n"
        mermaid += f"    API_Gateway-->>User: {operation.title()} Result\n"

    return mermaid
```

## Modern Diagram Formats and Interactive Visualizations

### Multi-Format Diagram Generation

```python
from typing import Dict, List, Any, Optional, Union
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import base64
import io

@dataclass
class DiagramFormat:
    name: str
    extension: str
    mime_type: str
    generator: callable

class MultiFormatDiagramGenerator:
    """Generate diagrams in multiple modern formats."""

    def __init__(self):
        self.formats = {
            'mermaid': DiagramFormat('Mermaid', '.mmd', 'text/plain', self.generate_mermaid),
            'plantuml': DiagramFormat('PlantUML', '.puml', 'text/plain', self.generate_plantuml),
            'graphviz': DiagramFormat('Graphviz DOT', '.dot', 'text/plain', self.generate_graphviz),
            'd2': DiagramFormat('D2 Lang', '.d2', 'text/plain', self.generate_d2),
            'drawio': DiagramFormat('Draw.io', '.drawio', 'application/xml', self.generate_drawio),
            'excalidraw': DiagramFormat('Excalidraw', '.excalidraw', 'application/json', self.generate_excalidraw),
            'svg': DiagramFormat('SVG', '.svg', 'image/svg+xml', self.generate_svg),
            'png': DiagramFormat('PNG', '.png', 'image/png', self.generate_png)
        }

    def generate_diagram(self, graph_data: Dict, format_name: str, **kwargs) -> str:
        """Generate diagram in specified format."""
        if format_name not in self.formats:
            raise ValueError(f"Unsupported format: {format_name}")

        format_spec = self.formats[format_name]
        return format_spec.generator(graph_data, **kwargs)

    def generate_all_formats(self, graph_data: Dict) -> Dict[str, str]:
        """Generate diagrams in all supported formats."""
        return {
            format_name: self.generate_diagram(graph_data, format_name)
            for format_name in self.formats.keys()
        }

    def generate_mermaid(self, graph_data: Dict, **kwargs) -> str:
        """Generate Mermaid diagram."""
        graph_type = graph_data.get('type', 'flowchart')
        title = graph_data.get('title', 'Diagram')
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        if graph_type == 'flowchart':
            direction = kwargs.get('direction', 'TD')
            mermaid = f"graph {direction}\n    title[{title}]\n"

            # Add nodes
            for node in nodes:
                node_id = node['id'].replace('-', '_').replace(' ', '_')
                node_label = node.get('label', node['id'])
                node_type = node.get('shape', '[')
                closing_type = ']' if node_type == '[' else ')'
                mermaid += f"    {node_id}{node_type}{node_label}{closing_type}\n"

            # Add edges
            for edge in edges:
                source = edge['from'].replace('-', '_').replace(' ', '_')
                target = edge['to'].replace('-', '_').replace(' ', '_')
                label = edge.get('label', '')
                if label:
                    mermaid += f"    {source} -->|{label}| {target}\n"
                else:
                    mermaid += f"    {source} --> {target}\n"

        elif graph_type == 'sequence':
            mermaid = f"sequenceDiagram\n    title {title}\n"
            participants = graph_data.get('participants', [])
            messages = graph_data.get('messages', [])

            for participant in participants:
                safe_name = participant.replace('-', '_')
                mermaid += f"    participant {safe_name}\n"

            for message in messages:
                from_part = message['from'].replace('-', '_')
                to_part = message['to'].replace('-', '_')
                msg_text = message.get('text', '')
                arrow_type = '->>' if message.get('async', False) else '->'
                mermaid += f"    {from_part}{arrow_type}{to_part}: {msg_text}\n"

        return mermaid

    def generate_plantuml(self, graph_data: Dict, **kwargs) -> str:
        """Generate PlantUML diagram."""
        graph_type = graph_data.get('type', 'class')
        title = graph_data.get('title', 'Diagram')

        plantuml = f"@startuml\n    title {title}\n"

        if graph_type == 'class':
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])

            for node in nodes:
                node_name = node['id']
                node_label = node.get('label', node['id'])
                node_attributes = node.get('attributes', [])
                node_methods = node.get('methods', [])

                plantuml += f"class {node_name} {{\n"
                if node_attributes:
                    for attr in node_attributes:
                        plantuml += f"  +{attr}\n"
                if node_methods:
                    for method in node_methods:
                        plantuml += f"  +{method}()\n"
                plantuml += "}\n"

            for edge in edges:
                from_node = edge['from']
                to_node = edge['to']
                relation = edge.get('relation', '-->')
                label = edge.get('label', '')
                if label:
                    plantuml += f"{from_node} {relation} {to_node} : {label}\n"
                else:
                    plantuml += f"{from_node} {relation} {to_node}\n"

        elif graph_type == 'sequence':
            participants = graph_data.get('participants', [])
            messages = graph_data.get('messages', [])

            for participant in participants:
                plantuml += f"participant {participant}\n"

            for message in messages:
                from_part = message['from']
                to_part = message['to']
                msg_text = message.get('text', '')
                plantuml += f"{from_part} -> {to_part}: {msg_text}\n"

        plantuml += "@enduml"
        return plantuml

    def generate_graphviz(self, graph_data: Dict, **kwargs) -> str:
        """Generate Graphviz DOT diagram."""
        graph_type = graph_data.get('type', 'digraph')
        title = graph_data.get('title', 'Diagram')
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        dot = f'{graph_type} "{title}" {{\n'
        dot += '    rankdir=TB;\n'
        dot += '    node [shape=box, style=rounded];\n'
        dot += '    edge [fontsize=10];\n\n'

        # Add nodes
        for node in nodes:
            node_id = node['id']
            node_label = node.get('label', node['id'])
            node_shape = node.get('shape', 'box')
            dot += f'    "{node_id}" [label="{node_label}", shape={node_shape}];\n'

        # Add edges
        for edge in edges:
            from_node = edge['from']
            to_node = edge['to']
            label = edge.get('label', '')
            if label:
                dot += f'    "{from_node}" -> "{to_node}" [label="{label}"];\n'
            else:
                dot += f'    "{from_node}" -> "{to_node}";\n'

        dot += '}'
        return dot

    def generate_d2(self, graph_data: Dict, **kwargs) -> str:
        """Generate D2 diagram."""
        title = graph_data.get('title', 'Diagram')
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        d2 = f"# {title}\n\n"

        # Add nodes with styles
        for node in nodes:
            node_id = node['id']
            node_label = node.get('label', node['id'])
            node_style = node.get('style', {})

            d2 += f'{node_id}: "{node_label}"'
            if node_style:
                d2 += ' {\n'
                for key, value in node_style.items():
                    d2 += f'  {key}: {value}\n'
                d2 += '}\n'
            else:
                d2 += '\n'

        # Add connections
        for edge in edges:
            from_node = edge['from']
            to_node = edge['to']
            label = edge.get('label', '')
            edge_style = edge.get('style', {})

            if label:
                d2 += f'{from_node} -> {to_node}: "{label}"'
            else:
                d2 += f'{from_node} -> {to_node}'

            if edge_style:
                d2 += ' {\n'
                for key, value in edge_style.items():
                    d2 += f'  {key}: {value}\n'
                d2 += '}\n'
            else:
                d2 += '\n'

        return d2

    def generate_excalidraw(self, graph_data: Dict, **kwargs) -> str:
        """Generate Excalidraw diagram (JSON format)."""
        elements = []
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        # Generate random but deterministic positions
        import hashlib

        def get_position(node_id):
            hash_val = int(hashlib.md5(node_id.encode()).hexdigest()[:8], 16)
            x = (hash_val % 800) + 100
            y = ((hash_val // 800) % 600) + 100
            return x, y

        # Add nodes as rectangles
        for node in nodes:
            node_id = node['id']
            node_label = node.get('label', node['id'])
            x, y = get_position(node_id)

            element = {
                "type": "rectangle",
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "id": node_id,
                "fillStyle": "hachure",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "x": x,
                "y": y,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "#f5f5f5",
                "width": 120,
                "height": 60,
                "seed": 1,
                "groupIds": [],
                "frameId": None,
                "roundness": {
                    "type": 3
                },
                "boundElements": [],
                "updated": 1,
                "link": None,
                "locked": False
            }
            elements.append(element)

            # Add text element
            text_element = {
                "type": "text",
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "id": f"text_{node_id}",
                "fillStyle": "hachure",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "x": x + 60,
                "y": y + 30,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "width": 100,
                "height": 40,
                "seed": 1,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "boundElements": [],
                "updated": 1,
                "link": None,
                "locked": False,
                "fontSize": 14,
                "fontFamily": 1,
                "text": node_label,
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": node_id,
                "originalText": node_label,
                "lineHeight": 1.25,
                "baseline": 30
            }
            elements.append(text_element)

        # Add edges as arrows
        for edge in edges:
            from_node = edge['from']
            to_node = edge['to']
            from_x, from_y = get_position(from_node)
            to_x, to_y = get_position(to_node)

            edge_element = {
                "type": "arrow",
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "id": f"edge_{from_node}_{to_node}",
                "fillStyle": "hachure",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "x": from_x + 120,
                "y": from_y + 30,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "width": abs(to_x - from_x),
                "height": abs(to_y - from_y),
                "seed": 1,
                "groupIds": [],
                "frameId": None,
                "roundness": {
                    "type": 2
                },
                "boundElements": [],
                "updated": 1,
                "link": None,
                "locked": False,
                "startBinding": {
                    "elementId": from_node,
                    "focus": 0,
                    "gap": 1
                },
                "endBinding": {
                    "elementId": to_node,
                    "focus": 0,
                    "gap": 1
                },
                "lastCommittedPoint": None,
                "startArrowhead": None,
                "endArrowhead": "arrow",
                "points": [
                    [from_x + 120, from_y + 30],
                    [to_x, to_y + 30]
                ]
            }
            elements.append(edge_element)

        excalidraw_data = {
            "type": "excalidraw",
            "version": 2,
            "source": 1,
            "elements": elements,
            "appState": {
                "gridSize": 20,
                "viewBackgroundColor": "#ffffff"
            }
        }

        return json.dumps(excalidraw_data, indent=2)

    def generate_svg(self, graph_data: Dict, **kwargs) -> str:
        """Generate SVG diagram."""
        title = graph_data.get('title', 'Diagram')
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        # Calculate dimensions
        width = max(800, len(nodes) * 200)
        height = max(600, len(nodes) * 100)

        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .node-box {{ fill: #f0f4f8; stroke: #2d3748; stroke-width: 2; rx: 8; }}
            .node-text {{ fill: #1a202c; font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }}
            .edge-line {{ stroke: #4a5568; stroke-width: 2; fill: none; }}
            .edge-arrow {{ fill: #4a5568; }}
            .title-text {{ fill: #1a202c; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
        </style>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" class="edge-arrow"/>
        </marker>
    </defs>

    <text x="{width//2}" y="30" class="title-text">{title}</text>
'''

        # Position nodes
        positions = {}
        for i, node in enumerate(nodes):
            x = (i % 4) * 200 + 100
            y = (i // 4) * 150 + 80
            positions[node['id']] = (x, y)

        # Draw edges
        for edge in edges:
            from_pos = positions.get(edge['from'], (0, 0))
            to_pos = positions.get(edge['to'], (0, 0))

            svg += f'    <line x1="{from_pos[0] + 60}" y1="{from_pos[1] + 30}" x2="{to_pos[0]}" y2="{to_pos[1] + 30}" class="edge-line" marker-end="url(#arrowhead)"/>\n'

        # Draw nodes
        for node in nodes:
            node_id = node['id']
            node_label = node.get('label', node['id'])
            x, y = positions.get(node_id, (0, 0))

            svg += f'    <rect x="{x}" y="{y}" width="120" height="60" class="node-box"/>\n'
            svg += f'    <text x="{x + 60}" y="{y + 35}" class="node-text">{node_label}</text>\n'

        svg += '</svg>'
        return svg

    def generate_png(self, graph_data: Dict, **kwargs) -> str:
        """Generate PNG diagram (base64 encoded)."""
        # This would typically use a library like PIL or cairosvg
        # For now, return a placeholder
        return "PNG generation requires external library dependencies"
```
```

### Database Interaction Flow
```python
def generate_database_flow(code_snippets):
    """Generate database interaction workflow."""
    operations = []

    for snippet in code_snippets:
        content = snippet['content']
        if 'SELECT' in content.upper():
            operations.append(('Read', 'Database'))
        elif 'INSERT' in content.upper():
            operations.append(('Create', 'Database'))
        elif 'UPDATE' in content.upper():
            operations.append(('Update', 'Database'))
        elif 'DELETE' in content.upper():
            operations.append(('Delete', 'Database'))

    mermaid = "graph LR\n    title[Database Operations]\n"

    for i, (operation, target) in enumerate(operations):
        if i == 0:
            mermaid += f"    App -->|{operation}| {target}\n"
        else:
            mermaid += f"    {target} -->|{operation}| {target}_{i}\n"

    return mermaid
```

## Component Architecture Diagrams

### Module Dependency Graph
```python
def generate_module_dependency_graph(file_paths):
    """Generate module dependency visualization."""
    graph = nx.DiGraph()

    # Add nodes for each file
    for file_path in file_paths:
        module_name = file_path.replace('.py', '').replace('/', '.')
        graph.add_node(module_name)

    # Analyze imports to add edges
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            code = f.read()

        tree = ast.parse(code)
        imports = extract_imports(tree)

        current_module = file_path.replace('.py', '').replace('/', '.')

        for imported_module in imports:
            # Only add edges for local modules
            if not imported_module.startswith(('os', 'sys', 'json', 'datetime')):
                graph.add_edge(current_module, imported_module)

    # Generate Mermaid diagram
    mermaid = "graph TD\n    title[Module Dependencies]\n"

    for node in graph.nodes():
        safe_name = node.replace('.', '_')
        mermaid += f"    {safe_name}[{node}]\n"

    for edge in graph.edges():
        source, target = edge
        safe_source = source.replace('.', '_')
        safe_target = target.replace('.', '_')
        mermaid += f"    {safe_source} --> {safe_target}\n"

    return mermaid
```

### System Architecture Diagram
```python
def generate_system_architecture(components_info):
    """Generate high-level system architecture diagram."""
    mermaid = "graph TB\n    title[System Architecture]\n"

    # Define component types
    component_types = {
        'frontend': 'Web Browser',
        'api': 'API Gateway',
        'service': 'Microservice',
        'database': 'Database',
        'cache': 'Cache'
    }

    for component in components_info:
        comp_type = component.get('type', 'service')
        comp_name = component['name']
        display_name = component_types.get(comp_type, comp_name)

        safe_name = comp_name.replace(' ', '_')
        mermaid += f"    {safe_name}[{display_name}]\n"

    # Add connections
    connections = component.get('connections', [])
    for connection in connections:
        source = connection['from'].replace(' ', '_')
        target = connection['to'].replace(' ', '_')
        protocol = connection.get('protocol', 'HTTP')
        mermaid += f"    {source} -->|{protocol}| {target}\n"

    return mermaid
```

## Diagram Integration
```python
def generate_repository_diagrams(repo_path):
    """Generate all diagram types for a repository."""
    diagrams = {}

    # Process Python files for call graphs
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()

                tree = ast.parse(code)
                call_graph, functions = generate_call_graph(tree, code)

                if len(call_graph.nodes()) > 1:
                    diagram_name = file.replace('.py', '_call_graph')
                    diagrams[diagram_name] = generate_mermaid_diagram(
                        call_graph, f"Call Graph - {file}"
                    )

    # Generate module dependency graph
    python_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    if len(python_files) > 1:
        diagrams['module_dependencies'] = generate_module_dependency_graph(python_files)

    return diagrams
```

## Interactive Diagram Features

### Real-time Collaboration and Updates

```python
import asyncio
import websockets
import json
from datetime import datetime
from typing import Set, Dict, Any

class InteractiveDiagramServer:
    """WebSocket server for real-time diagram collaboration."""

    def __init__(self):
        self.clients: Set = set()
        self.diagram_states: Dict[str, Dict] = {}
        self.collaboration_sessions: Dict[str, Dict] = {}

    async def register_client(self, websocket, session_id: str, user_id: str):
        """Register a new client for collaboration."""
        self.clients.add(websocket)

        if session_id not in self.collaboration_sessions:
            self.collaboration_sessions[session_id] = {
                'users': set(),
                'diagram_data': {},
                'history': [],
                'last_updated': datetime.now()
            }

        self.collaboration_sessions[session_id]['users'].add(user_id)

        # Send current diagram state
        if session_id in self.diagram_states:
            await websocket.send(json.dumps({
                'type': 'state_update',
                'data': self.diagram_states[session_id]
            }))

    async def handle_diagram_update(self, websocket, session_id: str, update_data: Dict):
        """Handle real-time diagram updates."""
        if session_id not in self.diagram_states:
            self.diagram_states[session_id] = {
                'nodes': [],
                'edges': [],
                'metadata': {'created': datetime.now()}
            }

        # Apply update
        self.diagram_states[session_id].update(update_data)
        self.diagram_states[session_id]['metadata']['last_updated'] = datetime.now()

        # Record in collaboration history
        self.collaboration_sessions[session_id]['history'].append({
            'timestamp': datetime.now(),
            'update': update_data,
            'user': update_data.get('user_id')
        })

        # Broadcast to all clients in session
        message = json.dumps({
            'type': 'diagram_update',
            'session': session_id,
            'data': update_data
        })

        await asyncio.gather(
            *[client.send(message) for client in self.clients if client != websocket]
        )

class DiagramAnalytics:
    """Analytics for diagram usage and interactions."""

    def __init__(self):
        self.usage_stats = {}
        self.interaction_patterns = {}
        self.popular_templates = {}

    def track_diagram_creation(self, diagram_type: str, user_context: Dict):
        """Track diagram creation patterns."""
        key = f"{diagram_type}_{user_context.get('role', 'unknown')}"
        self.usage_stats[key] = self.usage_stats.get(key, 0) + 1

    def track_interaction(self, action: str, element_type: str, duration: float):
        """Track user interactions with diagrams."""
        pattern_key = f"{action}_{element_type}"
        if pattern_key not in self.interaction_patterns:
            self.interaction_patterns[pattern_key] = []

        self.interaction_patterns[pattern_key].append({
            'duration': duration,
            'timestamp': datetime.now()
        })

    def get_insights(self) -> Dict[str, Any]:
        """Generate usage insights."""
        most_used_diagrams = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        avg_interaction_times = {}
        for pattern, interactions in self.interaction_patterns.items():
            if interactions:
                avg_time = sum(i['duration'] for i in interactions) / len(interactions)
                avg_interaction_times[pattern] = avg_time

        return {
            'most_used_diagrams': most_used_diagrams,
            'average_interaction_times': avg_interaction_times,
            'total_diagrams_created': sum(self.usage_stats.values()),
            'popular_patterns': list(most_used_diagrams)[:5]
        }
```

### AI-Powered Diagram Enhancement

```python
import openai
from typing import List, Dict, Any
import re

class AIDiagramAssistant:
    """AI-powered diagram enhancement and suggestions."""

    def __init__(self, api_key: str):
        openai.api_key = api_key

    async def suggest_layout_improvements(self, diagram_data: Dict) -> List[str]:
        """Suggest improvements for diagram layout."""
        prompt = f"""
        Analyze this diagram structure and suggest layout improvements:

        Nodes: {len(diagram_data.get('nodes', []))}
        Edges: {len(diagram_data.get('edges', []))}
        Type: {diagram_data.get('type', 'unknown')}

        Provide 3-5 specific suggestions for improving:
        1. Visual clarity
        2. Information hierarchy
        3. User navigation
        4. Accessibility
        5. Interactive features
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert UX designer and information architect."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return self.parse_suggestions(response.choices[0].message.content)

    async def generate_diagram_description(self, diagram_data: Dict) -> str:
        """Generate comprehensive diagram description."""
        node_types = set(node.get('type', 'unknown') for node in diagram_data.get('nodes', []))
        edge_count = len(diagram_data.get('edges', []))
        diagram_type = diagram_data.get('type', 'flowchart')

        prompt = f"""
        Generate a comprehensive description for this {diagram_type} diagram:

        - Contains {len(diagram_data.get('nodes', []))} nodes of types: {', '.join(node_types)}
        - Has {edge_count} connections/relationships
        - Purpose: {diagram_data.get('title', 'Untitled')}

        Create a clear, accessible description that explains:
        1. What the diagram represents
        2. Key components and their roles
        3. Main relationships and flows
        4. Important patterns or insights
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert technical communicator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )

        return response.choices[0].message.content

    async def suggest_related_diagrams(self, diagram_data: Dict, context: Dict) -> List[Dict]:
        """Suggest related diagrams that might be useful."""
        current_type = diagram_data.get('type')
        current_context = context.get('project', 'general')

        prompt = f"""
        Based on this {current_type} diagram in a {current_context} context, suggest 3 related diagrams
        that would provide additional value:

        Current diagram elements:
        - Nodes: {[node.get('label', node['id']) for node in diagram_data.get('nodes', [])[:5]]}
        - Main purpose: {diagram_data.get('title', 'Untitled')}

        Suggest diagrams with:
        1. Different but related perspectives
        2. Deeper or broader views
        3. Complementary information

        For each suggestion, provide:
        - Diagram type
        - Title/purpose
        - Key elements to include
        - How it relates to the current diagram
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert system architect and information designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.5
        )

        return self.parse_related_suggestions(response.choices[0].message.content)

    def parse_suggestions(self, ai_response: str) -> List[str]:
        """Parse AI response into actionable suggestions."""
        # Extract numbered or bulleted suggestions
        suggestions = []
        lines = ai_response.split('\n')

        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('•'):
                # Clean up the suggestion
                clean_suggestion = re.sub(r'^\d+\.?\s*[-•]?\s*', '', line).strip()
                if clean_suggestion:
                    suggestions.append(clean_suggestion)

        return suggestions[:5]  # Return top 5 suggestions

    def parse_related_suggestions(self, ai_response: str) -> List[Dict]:
        """Parse AI response into structured diagram suggestions."""
        suggestions = []
        sections = ai_response.split('\n\n')

        for section in sections:
            if any(keyword in section.lower() for keyword in ['diagram', 'chart', 'graph']):
                suggestion = {
                    'type': 'suggested_diagram',
                    'description': section.strip(),
                    'confidence': 0.8
                }
                suggestions.append(suggestion)

        return suggestions[:3]  # Return top 3 suggestions
```

**Use Cases for RAG**: Provide highly interactive, real-time collaborative diagram generation with AI-powered enhancements, multiple format support, and intelligent layout suggestions for complex system visualization and documentation.