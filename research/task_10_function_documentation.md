# Task 10: Advanced Function Documentation Generation with Type Analysis

## Enhanced JavaScript/TypeScript Function Analysis

### TypeScript-Aware Function Extraction
```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

class AdvancedFunctionAnalyzer {
    constructor() {
        this.functions = [];
        this.classes = [];
        this.interfaces = [];
        this.typeAliases = [];
    }

    analyzeCode(code) {
        const ast = parser.parse(code, {
            sourceType: 'module',
            plugins: [
                'typescript',
                'decorators-legacy',
                'jsx',
                'classProperties',
                'objectRestSpread',
                'asyncGenerators',
                'functionBind',
                'exportDefaultFrom',
                'exportNamespaceFrom',
                'dynamicImport',
                'nullishCoalescingOperator',
                'optionalChaining'
            ]
        });

        // Extract type definitions first
        this.extractTypeDefinitions(ast);

        // Then extract functions and classes
        this.extractFunctions(ast);
        this.extractClasses(ast);

        return {
            functions: this.functions,
            classes: this.classes,
            interfaces: this.interfaces,
            typeAliases: this.typeAliases
        };
    }

    extractTypeDefinitions(ast) {
        traverse(ast, {
            TSInterfaceDeclaration: (path) => {
                const interfaceDecl = path.node;
                this.interfaces.push({
                    name: interfaceDecl.id.name,
                    type: 'interface',
                    properties: this.extractInterfaceProperties(interfaceDecl),
                    methods: this.extractInterfaceMethods(interfaceDecl),
                    extends: interfaceDecl.extends?.map(ext => ext.id.name) || [],
                    description: this.extractJSDocComment(path),
                    line: interfaceDecl.loc?.start.line
                });
            },

            TSTypeAliasDeclaration: (path) => {
                const typeAlias = path.node;
                this.typeAliases.push({
                    name: typeAlias.id.name,
                    type: 'type_alias',
                    typeDefinition: this.parseTypeAnnotation(typeAlias.typeAnnotation),
                    description: this.extractJSDocComment(path),
                    line: typeAlias.loc?.start.line
                });
            }
        });
    }

    extractFunctions(ast) {
        traverse(ast, {
            FunctionDeclaration: (path) => {
                this.analyzeFunction(path, 'declaration');
            },

            FunctionExpression: (path) => {
                this.analyzeFunction(path, 'expression');
            },

            ArrowFunctionExpression: (path) => {
                this.analyzeArrowFunction(path);
            },

            MethodDefinition: (path) => {
                this.analyzeMethod(path);
            },

            ClassMethod: (path) => {
                this.analyzeClassMethod(path);
            }
        });
    }

    analyzeFunction(path, functionType) {
        const node = path.node;
        const jsdoc = this.extractJSDocComment(path);

        const functionInfo = {
            name: node.id?.name || 'anonymous',
            type: functionType,
            kind: node.kind || 'function',
            async: node.async || false,
            generator: node.generator || false,
            parameters: this.extractParameters(node.params, node),
            returnType: this.extractReturnType(node),
            typeParameters: this.extractTypeParameters(node.typeParameters),
            description: jsdoc?.description || '',
            examples: jsdoc?.examples || [],
            deprecated: jsdoc?.deprecated || false,
            since: jsdoc?.since || '',
            author: jsdoc?.author || '',
            line: node.loc?.start.line,
            decorators: this.extractDecorators(node),
            generics: this.extractGenerics(node)
        };

        // Add complexity metrics
        functionInfo.complexity = this.calculateComplexity(node);
        functionInfo.cyclomaticComplexity = this.calculateCyclomaticComplexity(node);

        this.functions.push(functionInfo);
    }

    extractParameters(params, functionNode) {
        return params.map((param, index) => {
            const paramInfo = {
                name: this.getParameterName(param),
                type: this.extractParameterType(param),
                optional: this.isParameterOptional(param),
                defaultValue: this.extractDefaultValue(param),
                description: this.extractParameterDescription(param, index),
                decorators: this.extractDecorators(param),
                rest: param.type === 'RestElement'
            };

            // Add destructuring information
            if (param.type === 'ObjectPattern' || param.type === 'ArrayPattern') {
                paramInfo.destructuring = this.analyzeDestructuringPattern(param);
            }

            return paramInfo;
        });
    }

    extractParameterType(param) {
        if (param.typeAnnotation) {
            return this.parseTypeAnnotation(param.typeAnnotation.typeAnnotation);
        }
        return 'any';
    }

    parseTypeAnnotation(typeAnnotation) {
        if (!typeAnnotation) return 'unknown';

        switch (typeAnnotation.type) {
            case 'TSStringKeyword':
                return 'string';
            case 'TSNumberKeyword':
                return 'number';
            case 'TSBooleanKeyword':
                return 'boolean';
            case 'TSVoidKeyword':
                return 'void';
            case 'TSAnyKeyword':
                return 'any';
            case 'TSUnknownKeyword':
                return 'unknown';
            case 'TSUnionType':
                return typeAnnotation.types.map(t => this.parseTypeAnnotation(t)).join(' | ');
            case 'TSIntersectionType':
                return typeAnnotation.types.map(t => this.parseTypeAnnotation(t)).join(' & ');
            case 'TSArrayType':
                return `${this.parseTypeAnnotation(typeAnnotation.elementType)}[]`;
            case 'TSArrayType':
                return `Array<${this.parseTypeAnnotation(typeAnnotation.elementType)}>`;
            case 'TSTypeReference':
                if (typeAnnotation.typeName.type === 'Identifier') {
                    return typeAnnotation.typeName.name;
                }
                return this.parseQualifiedType(typeAnnotation.typeName);
            case 'TSFunctionType':
                return this.parseFunctionType(typeAnnotation);
            case 'TSLiteralType':
                return typeAnnotation.literal.value?.toString() || 'unknown';
            default:
                return 'unknown';
        }
    }

    extractJSDocComment(path) {
        const leadingComments = path.node.leadingComments;
        if (!leadingComments || leadingComments.length === 0) {
            return null;
        }

        const lastComment = leadingComments[leadingComments.length - 1];
        if (lastComment.type !== 'CommentBlock' || !lastComment.value.startsWith('*')) {
            return null;
        }

        return this.parseJSDoc(lastComment.value);
    }

    parseJSDoc(jsdocString) {
        const jsdoc = {
            description: '',
            parameters: [],
            returns: '',
            examples: [],
            deprecated: false,
            since: '',
            author: '',
            throws: [],
            see: [],
            todo: []
        };

        // Remove comment markers and split into lines
        const lines = jsdocString
            .replace(/^\/\*\*/, '')
            .replace(/\*\/$/, '')
            .split('\n')
            .map(line => line.replace(/^\s*\*?\s?/, '').trim())
            .filter(line => line.length > 0);

        let currentSection = 'description';
        let currentExample = [];

        for (const line of lines) {
            if (line.startsWith('@param') || line.startsWith('@arg')) {
                currentSection = 'params';
                const paramMatch = line.match(/@(?:param|arg)\s+\{([^}]+)\}\s+(\w+)\s*(.*)/);
                if (paramMatch) {
                    jsdoc.parameters.push({
                        type: paramMatch[1],
                        name: paramMatch[2],
                        description: paramMatch[3].trim()
                    });
                }
            } else if (line.startsWith('@returns') || line.startsWith('@return')) {
                currentSection = 'returns';
                const returnMatch = line.match(/@(?:returns|return)\s+\{([^}]+)\s*(.*)/);
                if (returnMatch) {
                    jsdoc.returns = returnMatch[1];
                }
            } else if (line.startsWith('@example')) {
                currentSection = 'example';
                currentExample = [];
            } else if (line.startsWith('@deprecated')) {
                jsdoc.deprecated = true;
            } else if (line.startsWith('@since')) {
                jsdoc.since = line.replace('@since', '').trim();
            } else if (line.startsWith('@author')) {
                jsdoc.author = line.replace('@author', '').trim();
            } else if (line.startsWith('@throws')) {
                const throwMatch = line.match(/@throws\s+\{([^}]+)\}\s*(.*)/);
                if (throwMatch) {
                    jsdoc.throws.push({
                        type: throwMatch[1],
                        description: throwMatch[2].trim()
                    });
                }
            } else if (line.startsWith('@see')) {
                jsdoc.see.push(line.replace('@see', '').trim());
            } else if (line.startsWith('@todo')) {
                jsdoc.todo.push(line.replace('@todo', '').trim());
            } else if (line.startsWith('@')) {
                currentSection = 'other';
            } else {
                if (currentSection === 'description') {
                    jsdoc.description += (jsdoc.description ? ' ' : '') + line;
                } else if (currentSection === 'example') {
                    currentExample.push(line);
                }
            }
        }

        if (currentExample.length > 0) {
            jsdoc.examples.push(currentExample.join('\n'));
        }

        return jsdoc;
    }

    calculateComplexity(node) {
        let complexity = 1; // Base complexity

        // Count decision points
        const complexityNodes = [
            'IfStatement', 'WhileStatement', 'DoWhileStatement',
            'ForStatement', 'ForInStatement', 'ForOfStatement',
            'SwitchStatement', 'CatchClause', 'ConditionalExpression'
        ];

        traverse({ type: 'Program', body: [node] }, {
            enter: (path) => {
                if (complexityNodes.includes(path.node.type)) {
                    complexity += 1;
                }

                // Add complexity for logical operators
                if (path.node.type === 'LogicalExpression' &&
                    ['&&', '||'].includes(path.node.operator)) {
                    complexity += 1;
                }
            }
        });

        return complexity;
    }
}
```

## Advanced Python Function Analysis

### Comprehensive Python Function Analyzer
```python
import ast
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import inspect

@dataclass
class PythonFunction:
    name: str
    type: str  # function, method, async_function, async_method
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    type_hints: Dict[str, str]
    decorators: List[str]
    docstring: Optional[str]
    description: str
    examples: List[str]
    raises: List[Dict[str, str]]
    line_number: int
    complexity: int
    cyclomatic_complexity: int
    is_abstract: bool
    is_static: bool
    is_class_method: bool
    is_property: bool
    module: str
    imports_used: List[str]

class AdvancedPythonAnalyzer:
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.current_module = None

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive analysis of Python file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        self.current_module = self.extract_module_name(file_path)

        # Extract imports first
        self.extract_imports(tree)

        # Extract classes and their methods
        self.extract_classes(tree)

        # Extract standalone functions
        self.extract_functions(tree)

        # Cross-reference and enhance information
        self.enhance_with_cross_references()

        return {
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'module': self.current_module,
            'statistics': self.generate_statistics()
        }

    def extract_functions(self, tree: ast.AST):
        """Extract function definitions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods (they'll be extracted with classes)
                if not self.is_method(node, tree):
                    function_info = self.analyze_function(node, 'function')
                    if function_info:
                        self.functions.append(function_info)

    def extract_classes(self, tree: ast.AST):
        """Extract class definitions and their methods."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self.analyze_class(node)
                if class_info:
                    self.classes.append(class_info)

    def analyze_function(self, node: ast.FunctionDef, function_type: str) -> Optional[PythonFunction]:
        """Analyze individual function."""
        try:
            # Extract docstring
            docstring = ast.get_docstring(node)
            parsed_docstring = self.parse_docstring(docstring) if docstring else {}

            # Extract parameters with detailed information
            parameters = self.extract_function_parameters(node)

            # Extract return type annotation
            return_type = self.extract_return_type_annotation(node)

            # Extract type hints
            type_hints = self.extract_all_type_hints(node)

            # Extract decorators
            decorators = self.extract_decorators(node)

            # Determine function characteristics
            is_async = isinstance(node, ast.AsyncFunctionDef)
            is_abstract = self.is_abstract_method(node)
            is_static = 'staticmethod' in decorators
            is_class_method = 'classmethod' in decorators
            is_property = 'property' in decorators

            # Calculate complexity metrics
            complexity = self.calculate_function_complexity(node)
            cyclomatic_complexity = self.calculate_cyclomatic_complexity(node)

            # Extract used imports
            imports_used = self.extract_function_imports(node)

            function_info = PythonFunction(
                name=node.name,
                type=f"async_{function_type}" if is_async else function_type,
                parameters=parameters,
                return_type=return_type,
                type_hints=type_hints,
                decorators=decorators,
                docstring=docstring,
                description=parsed_docstring.get('description', ''),
                examples=parsed_docstring.get('examples', []),
                raises=parsed_docstring.get('raises', []),
                line_number=node.lineno,
                complexity=complexity,
                cyclomatic_complexity=cyclomatic_complexity,
                is_abstract=is_abstract,
                is_static=is_static,
                is_class_method=is_class_method,
                is_property=is_property,
                module=self.current_module,
                imports_used=imports_used
            )

            return function_info

        except Exception as e:
            print(f"Error analyzing function {node.name}: {e}")
            return None

    def extract_function_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract detailed parameter information."""
        parameters = []

        # Regular arguments
        for i, arg in enumerate(node.args.args):
            if arg.arg not in ['self', 'cls']:
                param_info = self.analyze_parameter(arg, node, i)
                parameters.append(param_info)

        # Keyword-only arguments
        for i, arg in enumerate(node.args.kwonlyargs):
            param_info = self.analyze_parameter(arg, node, i, kwonly=True)
            parameters.append(param_info)

        # *args
        if node.args.vararg:
            vararg_info = self.analyze_parameter(node.args.vararg, node, -1, vararg=True)
            parameters.append(vararg_info)

        # **kwargs
        if node.args.kwarg:
            kwarg_info = self.analyze_parameter(node.args.kwarg, node, -1, kwarg=True)
            parameters.append(kwarg_info)

        return parameters

    def analyze_parameter(self, arg: ast.arg, node: ast.FunctionDef,
                         index: int, *, kwonly: bool = False,
                         vararg: bool = False, kwarg: bool = False) -> Dict[str, Any]:
        """Analyze individual parameter."""
        param_name = arg.arg

        # Extract type annotation
        param_type = None
        if hasattr(arg, 'type_annotation') and arg.type_annotation:
            param_type = ast.unparse(arg.type_annotation)

        # Extract default value
        default_value = None
        has_default = False

        if not vararg and not kwarg:
            defaults = node.args.defaults
            kw_defaults = node.args.kw_defaults

            if kwonly and kw_defaults:
                # Keyword-only parameter
                kwonly_index = node.args.kwonlyargs.index(arg)
                if kwonly_index < len(kw_defaults) and kw_defaults[kwonly_index] is not None:
                    default_value = ast.unparse(kw_defaults[kwonly_index])
                    has_default = True
            elif not kwonly and defaults:
                # Regular parameter
                default_index = len(node.args.args) - len(defaults)
                param_index = node.args.args.index(arg)
                if param_index >= default_index:
                    default_value = ast.unparse(defaults[param_index - default_index])
                    has_default = True

        # Determine parameter kind
        if vararg:
            param_kind = 'VAR_POSITIONAL'
        elif kwarg:
            param_kind = 'VAR_KEYWORD'
        elif kwonly:
            param_kind = 'KEYWORD_ONLY'
        else:
            param_kind = 'POSITIONAL_OR_KEYWORD'

        return {
            'name': param_name,
            'type': param_type or 'Any',
            'default': default_value,
            'has_default': has_default,
            'required': not has_default and not vararg and not kwarg,
            'kind': param_kind,
            'annotation': param_type,
            'description': self.extract_parameter_description(node, param_name)
        }

    def parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse docstring with support for Google, NumPy, and Sphinx styles."""
        if not docstring:
            return {}

        parsed = {
            'description': '',
            'parameters': [],
            'returns': '',
            'raises': [],
            'examples': [],
            'notes': [],
            'see_also': []
        }

        lines = docstring.split('\n')
        current_section = 'description'
        current_example = []

        for line in lines:
            stripped = line.strip()

            # Google style docstring sections
            if stripped.startswith('Args:') or stripped.startswith('Arguments:'):
                current_section = 'args'
                continue
            elif stripped.startswith('Returns:'):
                current_section = 'returns'
                continue
            elif stripped.startswith('Raises:'):
                current_section = 'raises'
                continue
            elif stripped.startswith('Example:'):
                current_section = 'example'
                continue
            elif stripped.startswith('Note:'):
                current_section = 'notes'
                continue
            elif stripped.startswith('See Also:'):
                current_section = 'see_also'
                continue
            elif stripped and not stripped.startswith(' ') and current_section != 'description':
                # End of section, go back to description
                if stripped not in ['Args:', 'Arguments:', 'Returns:', 'Raises:', 'Example:', 'Note:', 'See Also:']:
                    current_section = 'description'

            if current_section == 'description':
                if stripped:
                    parsed['description'] += (parsed['description'] + ' ' if parsed['description'] else '') + stripped
            elif current_section == 'args':
                param_match = re.match(r'(\w+)\s*\(([^)]+)\):\s*(.*)', stripped)
                if param_match:
                    param_name = param_match.group(1)
                    param_type = param_match.group(2)
                    param_desc = param_match.group(3)
                    parsed['parameters'].append({
                        'name': param_name,
                        'type': param_type,
                        'description': param_desc
                    })
            elif current_section == 'returns':
                if stripped and not stripped.startswith('Returns:'):
                    parsed['returns'] = stripped
            elif current_section == 'raises':
                raise_match = re.match(r'(\w+):\s*(.*)', stripped)
                if raise_match:
                    exception_type = raise_match.group(1)
                    exception_desc = raise_match.group(2)
                    parsed['raises'].append({
                        'type': exception_type,
                        'description': exception_desc
                    })
            elif current_section == 'example':
                if stripped:
                    if stripped == 'Example:':
                        continue
                    current_example.append(stripped)
            elif current_section == 'notes':
                if stripped and not stripped.startswith('Note:'):
                    parsed['notes'].append(stripped)
            elif current_section == 'see_also':
                if stripped and not stripped.startswith('See Also:'):
                    parsed['see_also'].append(stripped)

        if current_example:
            parsed['examples'].append('\n'.join(current_example))

        return parsed

    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.With, ast.AsyncWith, ast.ExceptHandler,
                               ast.Assert, ast.BoolOp)):
                complexity += 1
            elif isinstance(child, ast.ListComp) or isinstance(child, ast.DictComp):
                complexity += 1

        return complexity

    def calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate overall function complexity."""
        complexity = 1

        # Count different types of statements
        complexity_nodes = [
            ast.If, ast.While, ast.For, ast.AsyncFor,
            ast.Try, ast.ExceptHandler, ast.With, ast.AsyncWith,
            ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp
        ]

        for child in ast.walk(node):
            if any(isinstance(child, node_type) for node_type in complexity_nodes):
                complexity += 1

        return complexity

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate analysis statistics."""
        total_functions = len(self.functions)
        total_classes = len(self.classes)
        total_methods = sum(len(cls['methods']) for cls in self.classes)

        function_complexities = [f.complexity for f in self.functions]
        method_complexities = []
        for cls in self.classes:
            method_complexities.extend(m.get('complexity', 0) for m in cls.get('methods', []))

        all_complexities = function_complexities + method_complexities

        return {
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_methods': total_methods,
            'average_complexity': sum(all_complexities) / len(all_complexities) if all_complexities else 0,
            'max_complexity': max(all_complexities) if all_complexities else 0,
            'functions_with_docstrings': sum(1 for f in self.functions if f.docstring),
            'functions_with_type_hints': sum(1 for f in self.functions if f.type_hints),
            'async_functions': sum(1 for f in self.functions if 'async' in f.type),
            'decorators_used': list(set(decorator for f in self.functions for decorator in f.decorators))
        }
```

## Enhanced Documentation Generation

### Multi-Format Documentation Generator
```python
class MultiFormatDocumentationGenerator:
    def __init__(self):
        self.templates = {
            'markdown': self.load_markdown_template(),
            'html': self.load_html_template(),
            'jupyter': self.load_jupyter_template(),
            'sphinx': self.load_sphinx_template()
        }

    def generate_comprehensive_docs(self, analysis_result: Dict[str, Any],
                                   output_dir: str = "./docs") -> Dict[str, str]:
        """Generate documentation in multiple formats."""
        import os
        os.makedirs(output_dir, exist_ok=True)

        generated_files = {}

        # Generate different formats
        formats = ['markdown', 'html', 'jupyter', 'sphinx']

        for format_type in formats:
            content = self.generate_documentation(analysis_result, format_type)
            filename = self.get_filename(format_type, output_dir)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            generated_files[format_type] = filename

        # Generate index page
        index_content = self.generate_index_page(analysis_result, generated_files)
        index_file = os.path.join(output_dir, 'index.html')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        generated_files['index'] = index_file

        return generated_files

    def generate_documentation(self, analysis_result: Dict[str, Any], format_type: str) -> str:
        """Generate documentation in specified format."""
        if format_type == 'markdown':
            return self.generate_markdown_docs(analysis_result)
        elif format_type == 'html':
            return self.generate_html_docs(analysis_result)
        elif format_type == 'jupyter':
            return self.generate_jupyter_notebook(analysis_result)
        elif format_type == 'sphinx':
            return self.generate_sphinx_docs(analysis_result)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_markdown_docs(self, analysis_result: Dict[str, Any]) -> str:
        """Generate comprehensive Markdown documentation."""
        md_content = []

        # Title and overview
        md_content.append(f"# {analysis_result['module']} Documentation\n")

        # Table of contents
        md_content.append(self.generate_markdown_toc(analysis_result))

        # Module overview
        md_content.append(self.generate_module_overview(analysis_result))

        # Function documentation
        if analysis_result['functions']:
            md_content.append("## Functions\n")
            for func in analysis_result['functions']:
                md_content.append(self.generate_function_markdown(func))

        # Class documentation
        if analysis_result['classes']:
            md_content.append("## Classes\n")
            for cls in analysis_result['classes']:
                md_content.append(self.generate_class_markdown(cls))

        # Statistics
        md_content.append(self.generate_statistics_markdown(analysis_result['statistics']))

        return '\n\n'.join(md_content)

    def generate_function_markdown(self, func: PythonFunction) -> str:
        """Generate Markdown documentation for a function."""
        md = []

        # Function header
        md.append(f"### {func.name}")
        if func.is_abstract:
            md.append("`abstract`")
        if func.is_static:
            md.append("`static`")
        if func.is_class_method:
            md.append("`classmethod`")
        if func.is_property:
            md.append("`property`")

        # Signature
        signature = self.generate_function_signature(func)
        md.append(f"```python\n{signature}\n```")

        # Description
        if func.description:
            md.append(f"\n{func.description}")

        # Parameters
        if func.parameters:
            md.append("\n**Parameters:**")
            for param in func.parameters:
                required_marker = "" if param['required'] else " (optional)"
                type_info = f" *{param['type']}*" if param['type'] != 'Any' else ""
                md.append(f"- `{param['name']}`{type_info}{required_marker}: {param.get('description', 'No description')}")

        # Return type
        if func.return_type and func.return_type != 'None':
            md.append(f"\n**Returns:** `{func.return_type}`")

        # Raises
        if func.raises:
            md.append("\n**Raises:**")
            for exc in func.raises:
                md.append(f"- `{exc['type']}`: {exc['description']}")

        # Examples
        if func.examples:
            md.append("\n**Examples:**")
            for example in func.examples:
                md.append(f"```python\n{example}\n```")

        # Complexity metrics
        md.append(f"\n**Complexity:** {func.complexity} (Cyclomatic: {func.cyclomatic_complexity})")

        return '\n'.join(md)

    def generate_function_signature(self, func: PythonFunction) -> str:
        """Generate function signature string."""
        params = []

        for param in func.parameters:
            param_str = param['name']

            if param['type'] != 'Any':
                param_str += f": {param['type']}"

            if param['default']:
                param_str += f" = {param['default']}"

            params.append(param_str)

        signature = f"def {func.name}({', '.join(params)})"

        if func.return_type and func.return_type != 'None':
            signature += f" -> {func.return_type}"

        return signature

    def generate_html_docs(self, analysis_result: Dict[str, Any]) -> str:
        """Generate HTML documentation with modern styling."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_name} Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px;
            background: #f8f9fa; color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; border-radius: 12px; text-align: center; margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }}
        .stat-card {{
            background: white; padding: 20px; border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .section {{
            background: white; margin-bottom: 30px; border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden;
        }}
        .section-header {{
            background: #667eea; color: white; padding: 20px;
            font-size: 1.5em; font-weight: bold;
        }}
        .section-content {{ padding: 30px; }}
        .function-card {{
            border-left: 4px solid #667eea; padding: 20px; margin-bottom: 20px;
            background: #f8f9fa; border-radius: 0 8px 8px 0;
        }}
        .function-name {{ font-size: 1.3em; font-weight: bold; color: #333; margin-bottom: 10px; }}
        .function-signature {{
            background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px;
            font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em;
            margin: 15px 0;
        }}
        .tags {{ margin-top: 10px; }}
        .tag {{
            display: inline-block; background: #667eea; color: white;
            padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;
        }}
        .parameters {{ margin: 15px 0; }}
        .parameter {{ margin: 8px 0; }}
        .param-name {{ font-weight: bold; color: #4a5568; }}
        .param-type {{ color: #718096; font-style: italic; }}
        .complexity {{
            background: #fef5e7; color: #f39c12; padding: 5px 10px;
            border-radius: 4px; font-size: 0.8em; display: inline-block; margin-top: 10px;
        }}
        .toc {{
            background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .toc h3 {{ margin-top: 0; color: #667eea; }}
        .toc ul {{ list-style: none; padding-left: 0; }}
        .toc li {{ margin: 5px 0; }}
        .toc a {{ color: #667eea; text-decoration: none; }}
        .toc a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    {content}
</body>
</html>
        """

        # Generate content sections
        content_parts = []

        # Header
        content_parts.append(f"""
        <div class="header">
            <h1>{analysis_result['module']} Documentation</h1>
            <p>Comprehensive API reference and usage guide</p>
        </div>
        """)

        # Statistics
        content_parts.append(self.generate_html_stats(analysis_result['statistics']))

        # Table of contents
        content_parts.append(self.generate_html_toc(analysis_result))

        # Functions section
        if analysis_result['functions']:
            content_parts.append("""
            <div class="section">
                <div class="section-header">Functions</div>
                <div class="section-content">
            """)

            for func in analysis_result['functions']:
                content_parts.append(self.generate_function_html(func))

            content_parts.append("""
                </div>
            </div>
            """)

        # Classes section
        if analysis_result['classes']:
            content_parts.append("""
            <div class="section">
                <div class="section-header">Classes</div>
                <div class="section-content">
            """)

            for cls in analysis_result['classes']:
                content_parts.append(self.generate_class_html(cls))

            content_parts.append("""
                </div>
            </div>
            """)

        full_content = ''.join(content_parts)
        return html_template.format(module_name=analysis_result['module'], content=full_content)

    def generate_function_html(self, func: PythonFunction) -> str:
        """Generate HTML documentation for a function."""
        html = f'<div class="function-card" id="function-{func.name}">'

        # Function name and tags
        html += f'<div class="function-name">{func.name}</div>'

        tags = []
        if func.is_async:
            tags.append('<span class="tag">async</span>')
        if func.is_abstract:
            tags.append('<span class="tag">abstract</span>')
        if func.is_static:
            tags.append('<span class="tag">static</span>')
        if func.is_class_method:
            tags.append('<span class="tag">classmethod</span>')
        if func.is_property:
            tags.append('<span class="tag">property</span>')

        if tags:
            html += f'<div class="tags">{"".join(tags)}</div>'

        # Function signature
        signature = self.generate_function_signature(func)
        html += f'<div class="function-signature">{signature}</div>'

        # Description
        if func.description:
            html += f'<p>{func.description}</p>'

        # Parameters
        if func.parameters:
            html += '<div class="parameters"><strong>Parameters:</strong>'
            for param in func.parameters:
                required = "required" if param['required'] else "optional"
                html += f'''
                <div class="parameter">
                    <span class="param-name">{param['name']}</span>
                    <span class="param-type">({param['type']}, {required})</span>: {param.get('description', 'No description')}
                </div>
                '''
            html += '</div>'

        # Return type
        if func.return_type and func.return_type != 'None':
            html += f'<p><strong>Returns:</strong> <code>{func.return_type}</code></p>'

        # Raises
        if func.raises:
            html += '<p><strong>Raises:</strong></p><ul>'
            for exc in func.raises:
                html += f'<li><code>{exc["type"]}</code>: {exc["description"]}</li>'
            html += '</ul>'

        # Examples
        if func.examples:
            html += '<p><strong>Examples:</strong></p>'
            for example in func.examples:
                html += f'<pre><code>{example}</code></pre>'

        # Complexity
        html += f'<div class="complexity">Complexity: {func.complexity} (Cyclomatic: {func.cyclomatic_complexity})</div>'

        html += '</div>'
        return html

    def generate_jupyter_notebook(self, analysis_result: Dict[str, Any]) -> str:
        """Generate Jupyter notebook documentation."""
        import json

        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {analysis_result['module']} Documentation\n",
                        f"Interactive documentation for the `{analysis_result['module']}` module.\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Import the module\n",
                        f"import {analysis_result['module']}\n",
                        "import inspect\n",
                        "from pprint import pprint"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        # Add function documentation cells
        for func in analysis_result['functions']:
            # Markdown cell with documentation
            doc_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": self.generate_function_markdown(func)
            }
            notebook["cells"].append(doc_cell)

            # Code cell with example usage
            example_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    f"# Example usage of {func.name}\n",
                    "# help({analysis_result['module']}.{func.name})\n",
                    "# {func.name}()"
                ]
            }
            notebook["cells"].append(example_cell)

        return json.dumps(notebook, indent=2)

    def generate_sphinx_docs(self, analysis_result: Dict[str, Any]) -> str:
        """Generate Sphinx reStructuredText documentation."""
        rst_content = []

        # Module header
        rst_content.append(f".. _{analysis_result['module']}:\n")
        rst_content.append(f"{analysis_result['module']}")
        rst_content.append("=" * len(analysis_result['module']))
        rst_content.append("")

        # Module description
        rst_content.append(f".. automodule:: {analysis_result['module']}")
        rst_content.append("   :members:")
        rst_content.append("   :undoc-members:")
        rst_content.append("   :show-inheritance:")

        # Function documentation
        if analysis_result['functions']:
            rst_content.append("\nFunctions")
            rst_content.append("-" * 9)
            rst_content.append("")

            for func in analysis_result['functions']:
                rst_content.append(f".. autofunction:: {analysis_result['module']}.{func.name}")
                rst_content.append("")

        # Class documentation
        if analysis_result['classes']:
            rst_content.append("\nClasses")
            rst_content.append("-" * 7)
            rst_content.append("")

            for cls in analysis_result['classes']:
                rst_content.append(f".. autoclass:: {analysis_result['module']}.{cls['name']}")
                rst_content.append("   :members:")
                rst_content.append("   :undoc-members:")
                rst_content.append("   :show-inheritance:")
                rst_content.append("")

        return '\n'.join(rst_content)

# Usage example
generator = MultiFormatDocumentationGenerator()
analysis_result = python_analyzer.analyze_file('example.py')
generated_docs = generator.generate_comprehensive_docs(analysis_result)
print(f"Generated documentation: {generated_docs}")
```

**Use Cases for RAG**: Comprehensive function documentation generation with TypeScript support, Python type hints, complexity analysis, multi-format output (Markdown, HTML, Jupyter, Sphinx), interactive documentation, and enhanced code examples for better developer experience.