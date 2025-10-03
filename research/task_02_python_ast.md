# Task 2: Advanced Python AST Parsing

## Comprehensive Tool Suite

### 1. Python Built-in AST Module

### Overview
Python's built-in `ast` module provides a robust foundation for AST parsing with comprehensive node type coverage and semantic analysis capabilities.

### Installation
```bash
# Built-in - no installation required
```

### Advanced Usage with Type Annotations
```python
import ast
import sys
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

code = """
from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class UserProfile:
    user_id: int
    username: str
    email: str
    preferences: Dict[str, Any]
    is_active: bool = True

class AbstractDataService(ABC):
    \"\"\"Abstract base class for data services.\"\"\"

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool:
        \"\"\"Establish connection to data source.\"\"\"
        pass

    async def disconnect(self) -> None:
        \"\"\"Close connection to data source.\"\"\"
        self._connected = False

    def get_connection_status(self) -> bool:
        return self._connected

class UserService(AbstractDataService):
    \"\"\"Service for managing user operations.\"\"\"

    def __init__(self, connection_string: str, max_connections: int = 10):
        super().__init__(connection_string)
        self.max_connections = max_connections
        self._user_cache: Dict[int, UserProfile] = {}

    async def connect(self) -> bool:
        try:
            # Simulate connection logic
            self._connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[UserProfile]:
        \"\"\"Retrieve user profile by ID.\"\"\"
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        # Database lookup logic would go here
        return None

    async def create_user(self, user_data: Dict[str, Any]) -> UserProfile:
        \"\"\"Create a new user profile.\"\"\"
        user_profile = UserProfile(
            user_id=len(self._user_cache) + 1,
            username=user_data['username'],
            email=user_data['email'],
            preferences=user_data.get('preferences', {})
        )

        self._user_cache[user_profile.user_id] = user_profile
        return user_profile

    def get_all_users(self) -> List[UserProfile]:
        \"\"\"Get all cached users.\"\"\"
        return list(self._user_cache.values())

def process_user_data(users: List[Dict[str, Any]]) -> Dict[str, Union[int, List[str]]]:
    \"\"\"Process user data and return statistics.\"\"\"
    if not users:
        return {'total': 0, 'domains': []}

    domains = set()
    active_users = 0

    for user in users:
        if user.get('is_active', False):
            active_users += 1

        email = user.get('email', '')
        if '@' in email:
            domain = email.split('@')[1]
            domains.add(domain)

    return {
        'total': len(users),
        'active': active_users,
        'domains': sorted(list(domains))
    }

async def main():
    \"\"\"Main function demonstrating usage.\"\"\"
    service = UserService("mongodb://localhost:27017/users")

    if await service.connect():
        # Create sample users
        users_data = [
            {
                'username': 'alice',
                'email': 'alice@example.com',
                'preferences': {'theme': 'dark', 'notifications': True}
            },
            {
                'username': 'bob',
                'email': 'bob@company.org',
                'preferences': {'theme': 'light'}
            }
        ]

        for user_data in users_data:
            user = await service.create_user(user_data)
            print(f"Created user: {user}")

        # Process statistics
        stats = process_user_data([dataclasses.asdict(user) for user in service.get_all_users()])
        print(f"Statistics: {stats}")

        await service.disconnect()

if __name__ == "__main__":
    import asyncio
    import dataclasses
    asyncio.run(main())
"""

# Parse with comprehensive options
tree = ast.parse(code, mode='exec', type_comments=True, feature_version=sys.version_info)

# Print AST structure
print("AST Tree:")
print(ast.dump(tree, indent=2))
```

### Enhanced Structure Extraction
```python
@dataclass
class TypeInfo:
    """Represents type information extracted from annotations."""
    name: str
    type_args: List['TypeInfo'] = None
    optional: bool = False
    union_types: List['TypeInfo'] = None
    generic_params: List[str] = None

@dataclass
class FunctionInfo:
    """Enhanced function information with comprehensive details."""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[TypeInfo]
    decorators: List[str]
    docstring: Optional[str]
    is_async: bool
    is_abstract: bool
    is_property: bool
    is_class_method: bool
    is_static_method: bool
    line_number: int
    complexity_score: int
    type_params: List[str]

@dataclass
class ClassInfo:
    """Enhanced class information with inheritance and composition details."""
    name: str
    base_classes: List[str]
    implemented_interfaces: List[str]
    methods: List[FunctionInfo]
    properties: List[Dict[str, Any]]
    class_variables: List[Dict[str, Any]]
    decorators: List[str]
    docstring: Optional[str]
    is_abstract: bool
    is_dataclass: bool
    line_number: int
    type_params: List[str]

@dataclass
class ModuleInfo:
    """Comprehensive module information."""
    name: str
    docstring: Optional[str]
    imports: List[Dict[str, Any]]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    global_variables: List[Dict[str, Any]]
    type_aliases: List[Dict[str, Any]]
    complexity_metrics: Dict[str, int]

def extract_type_annotation(node: ast.AST) -> Optional[TypeInfo]:
    """Extract detailed type information from AST nodes."""
    if node is None:
        return None

    if isinstance(node, ast.Name):
        return TypeInfo(name=node.id)

    elif isinstance(node, ast.Subscript):
        base_type = extract_type_annotation(node.value)
        type_args = [extract_type_annotation(arg) for arg in node.slice.elts] if hasattr(node.slice, 'elts') else [extract_type_annotation(node.slice)]
        return TypeInfo(name=base_type.name, type_args=type_args if type_args else [])

    elif isinstance(node, ast.Constant):
        return TypeInfo(name=str(node.value))

    elif isinstance(node, ast.Attribute):
        value_part = extract_type_annotation(node.value)
        return TypeInfo(name=f"{value_part.name if value_part else ''}.{node.attr}")

    return None

def extract_function_info(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> FunctionInfo:
    """Extract comprehensive function information."""
    is_async = isinstance(node, ast.AsyncFunctionDef)

    # Extract parameters with type annotations
    parameters = []
    for arg in node.args.args:
        param_info = {
            'name': arg.arg,
            'type': extract_type_annotation(arg.annotation),
            'has_default': False,
            'is_vararg': False,
            'is_kwarg': False
        }

        # Check for default values
        defaults_start = len(node.args.args) - len(node.args.defaults)
        arg_index = node.args.args.index(arg)
        if arg_index >= defaults_start:
            param_info['has_default'] = True
            default_index = arg_index - defaults_start
            param_info['default_value'] = ast.unparse(node.args.defaults[default_index])

        parameters.append(param_info)

    # Handle *args
    if node.args.vararg:
        parameters.append({
            'name': node.args.vararg.arg,
            'type': extract_type_annotation(node.args.vararg.annotation),
            'has_default': False,
            'is_vararg': True,
            'is_kwarg': False
        })

    # Handle **kwargs
    if node.args.kwarg:
        parameters.append({
            'name': node.args.kwarg.arg,
            'type': extract_type_annotation(node.args.kwarg.annotation),
            'has_default': False,
            'is_vararg': False,
            'is_kwarg': True
        })

    # Extract decorators
    decorators = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            decorators.append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            decorators.append(f"{decorator.value.id}.{decorator.attr}")
        elif isinstance(decorator, ast.Call):
            call_name = decorator.func.id if isinstance(decorator.func, ast.Name) else ast.unparse(decorator.func)
            decorators.append(f"{call_name}(...)")

    # Determine method type
    is_class_method = 'classmethod' in decorators
    is_static_method = 'staticmethod' in decorators
    is_property = 'property' in decorators
    is_abstract = 'abstractmethod' in decorators

    # Calculate complexity (simplified)
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1

    # Extract type parameters (Python 3.12+)
    type_params = []
    if hasattr(node, 'type_params'):
        type_params = [param.name for param in node.type_params]

    return FunctionInfo(
        name=node.name,
        parameters=parameters,
        return_type=extract_type_annotation(node.returns),
        decorators=decorators,
        docstring=ast.get_docstring(node),
        is_async=is_async,
        is_abstract=is_abstract,
        is_property=is_property,
        is_class_method=is_class_method,
        is_static_method=is_static_method,
        line_number=node.lineno,
        complexity_score=complexity,
        type_params=type_params
    )

def extract_class_info(node: ast.ClassDef) -> ClassInfo:
    """Extract comprehensive class information."""

    # Extract base classes
    base_classes = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            base_classes.append(base.id)
        elif isinstance(base, ast.Attribute):
            base_classes.append(f"{base.value.id}.{base.attr}")
        elif isinstance(base, ast.Subscript):
            base_classes.append(ast.unparse(base))

    # Extract methods
    methods = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(extract_function_info(item))

    # Extract properties and class variables
    properties = []
    class_variables = []

    for item in node.body:
        if isinstance(item, ast.AnnAssign) or (isinstance(item, ast.Assign) and item.targets):
            if isinstance(item, ast.AnnAssign):
                target = item.target
                type_info = extract_type_annotation(item.annotation)
            else:
                target = item.targets[0]
                type_info = None

            if isinstance(target, ast.Name):
                var_info = {
                    'name': target.id,
                    'type': type_info,
                    'value': ast.unparse(item.value) if item.value else None,
                    'is_property': False
                }

                # Check if it's a property (has property decorator in method)
                for method in methods:
                    if method.name == target.id and method.is_property:
                        var_info['is_property'] = True
                        break

                if var_info['is_property']:
                    properties.append(var_info)
                else:
                    class_variables.append(var_info)

    # Extract decorators
    decorators = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            decorators.append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            decorators.append(f"{decorator.value.id}.{decorator.attr}")
        elif isinstance(decorator, ast.Call):
            call_name = ast.unparse(decorator.func)
            decorators.append(call_name)

    # Determine if abstract class
    is_abstract = any(method.is_abstract for method in methods)
    is_dataclass = 'dataclass' in decorators

    # Extract type parameters
    type_params = []
    if hasattr(node, 'type_params'):
        type_params = [param.name for param in node.type_params]

    return ClassInfo(
        name=node.name,
        base_classes=base_classes,
        implemented_interfaces=[],  # Can be detected from ABC imports
        methods=methods,
        properties=properties,
        class_variables=class_variables,
        decorators=decorators,
        docstring=ast.get_docstring(node),
        is_abstract=is_abstract,
        is_dataclass=is_dataclass,
        line_number=node.lineno,
        type_params=type_params
    )

def extract_imports(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract detailed import information."""
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    'type': 'import',
                    'module': alias.name,
                    'alias': alias.asname,
                    'is_wildcard': alias.name == '*',
                    'line': node.lineno
                })

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            level = node.level  # Number of dots for relative imports

            for alias in node.names:
                imports.append({
                    'type': 'from_import',
                    'module': module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'is_wildcard': alias.name == '*',
                    'relative_level': level,
                    'line': node.lineno
                })

    return imports

def analyze_python_module(file_path: str) -> ModuleInfo:
    """Comprehensive Python module analysis."""
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        tree = ast.parse(code, type_comments=True, feature_version=(3, 10))
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return None

    # Extract module information
    module_name = Path(file_path).stem
    docstring = ast.get_docstring(tree)

    imports = extract_imports(tree)

    functions = []
    classes = []
    global_variables = []
    type_aliases = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(extract_function_info(node))

        elif isinstance(node, ast.ClassDef):
            classes.append(extract_class_info(node))

        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                type_info = extract_type_annotation(node.annotation)
                if type_info and (type_info.name == 'TypeAlias' or
                                (node.value and isinstance(node.value, ast.Name))):
                    type_aliases.append({
                        'name': node.target.id,
                        'type': type_info,
                        'value': ast.unparse(node.value) if node.value else None,
                        'line': node.lineno
                    })
                else:
                    global_variables.append({
                        'name': node.target.id,
                        'type': type_info,
                        'value': ast.unparse(node.value) if node.value else None,
                        'line': node.lineno
                    })

    # Calculate complexity metrics
    complexity_metrics = {
        'total_functions': len(functions),
        'total_classes': len(classes),
        'total_imports': len(imports),
        'max_function_complexity': max([f.complexity_score for f in functions], default=0),
        'abstract_classes': len([c for c in classes if c.is_abstract]),
        'async_functions': len([f for f in functions if f.is_async]),
        'dataclasses': len([c for c in classes if c.is_dataclass])
    }

    return ModuleInfo(
        name=module_name,
        docstring=docstring,
        imports=imports,
        functions=functions,
        classes=classes,
        global_variables=global_variables,
        type_aliases=type_aliases,
        complexity_metrics=complexity_metrics
    )

# Usage example
module_info = analyze_python_module('example.py')
print(f"Module: {module_info.name}")
print(f"Functions: {len(module_info.functions)}")
print(f"Classes: {len(module_info.classes)}")
```

### 2. Advanced Third-Party Tools

#### Astroid (Static Analysis)
```python
# Installation: pip install astroid
from astroid import MANAGER
from astroid.builder import AstroidBuilder
from astroid.exceptions import InferenceError

def analyze_with_astroid(code: str) -> Dict[str, Any]:
    """Advanced static analysis using Astroid."""

    # Build AST with Astroid
    builder = AstroidBuilder(MANAGER)
    module = builder.string_build(code, 'example_module')

    analysis = {
        'classes': [],
        'functions': [],
        'imports': [],
        'dependencies': set(),
        'interfaces': []
    }

    # Extract classes with inheritance chains
    for class_node in module.nodes_of_class(astroid.ClassDef):
        class_info = {
            'name': class_node.name,
            'bases': [base.name for base in class_node.bases],
            'methods': [],
            'properties': [],
            'is_abstract': False,
            'implemented_interfaces': []
        }

        # Check if class implements abstract methods
        for method_node in class_node.nodes_of_class(astroid.FunctionDef):
            if method_node.decorators:
                for decorator in method_node.decorators.nodes:
                    if (isinstance(decorator, astroid.Name) and
                        decorator.name == 'abstractmethod'):
                        class_info['is_abstract'] = True

        # Extract methods with type inference
        for method in class_node.methods():
            method_info = {
                'name': method.name,
                'args': [arg.name for arg in method.args.args],
                'return_type': str(method.returns.inferred()[0]) if method.returns and method.returns.inferred() else 'unknown',
                'decorators': [d.name for d in method.decorators or []]
            }
            class_info['methods'].append(method_info)

        analysis['classes'].append(class_info)

    # Extract functions with type inference
    for func_node in module.nodes_of_class(astroid.FunctionDef):
        try:
            return_types = [str(t) for t in func_node.infer_call_result(func_node)] if func_node.infer_call_result else []
            func_info = {
                'name': func_node.name,
                'args': [arg.name for arg in func_node.args.args],
                'return_types': return_types,
                'docstring': func_node.doc
            }
            analysis['functions'].append(func_info)
        except InferenceError:
            continue

    # Extract dependencies
    for import_node in module.nodes_of_class((astroid.Import, astroid.ImportFrom)):
        if isinstance(import_node, astroid.Import):
            for name in import_node.names:
                analysis['dependencies'].add(name[0])
        else:
            if import_node.modname:
                analysis['dependencies'].add(import_node.modname)

    analysis['dependencies'] = list(analysis['dependencies'])
    return analysis
```

#### Red Baron (AST Manipulation)
```python
# Installation: pip install redbaron
from redbaron import RedBaron

def analyze_with_redbaron(code: str) -> Dict[str, Any]:
    """Code analysis and manipulation using Red Baron."""

    red = RedBaron(code)

    analysis = {
        'functions': [],
        'classes': [],
        'imports': [],
        'decorators': [],
        'type_hints': []
    }

    # Extract functions with detailed information
    for func in red.find_all('def'):
        func_info = {
            'name': func.name,
            'decorators': [dec.dumps() for dec in func.decorators],
            'arguments': [arg.dumps() for arg in func.arguments],
            'annotations': func.annotations,
            'returns': func.returns.dumps() if func.returns else None,
            'async': func.is_async(),
            'source': func.dumps()
        }
        analysis['functions'].append(func_info)

    # Extract classes with methods
    for cls in red.find_all('class'):
        class_info = {
            'name': cls.name,
            'inheritance': [inh.dumps() for inh in cls.inheritance],
            'decorators': [dec.dumps() for dec in cls.decorators],
            'methods': [],
            'source': cls.dumps()
        }

        for method in cls.find_all('def'):
            method_info = {
                'name': method.name,
                'decorators': [dec.dumps() for dec in method.decorators],
                'arguments': [arg.dumps() for arg in method.arguments],
                'async': method.is_async()
            }
            class_info['methods'].append(method_info)

        analysis['classes'].append(class_info)

    return analysis

def transform_code_with_redbaron(code: str) -> str:
    """Example code transformation using Red Baron."""

    red = RedBaron(code)

    # Add type hints to functions without them
    for func in red.find_all('def'):
        if not func.annotations and len(func.arguments) > 0:
            # Add type hints: int for first argument if not self
            if func.arguments[0].value != 'self':
                func.arguments[0].add_argument_type_hint('int')

    # Add docstrings to functions without them
    for func in red.find_all('def'):
        if not func.value and len(func.decorators) == 0:
            func.value.insert(0, '"""Auto-generated docstring."""')

    return red.dumps()
```

### 3. Code Quality and Metrics Analysis

#### Comprehensive Metrics Extraction
```python
import re
from collections import defaultdict
from typing import Counter

class PythonCodeAnalyzer:
    """Advanced Python code analyzer with comprehensive metrics."""

    def __init__(self):
        self.metrics = {
            'complexity': {},
            'maintainability': {},
            'documentation': {},
            'test_coverage': {},
            'type_safety': {}
        }

    def calculate_halstead_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate Halstead metrics for complexity assessment."""
        operators = set()
        operands = set()
        total_operators = 0
        total_operands = 0

        operator_patterns = [
            r'\+', r'-', r'\*', r'/', r'%', r'\*\*', r'//',
            r'==', r'!=', r'<', r'>', r'<=', r'>=',
            r'and', r'or', r'not', r'&', r'\|', r'\^', r'~',
            r'<<', r'>>', r'=', r'\+=', r'-=', r'\*=', r'/=',
            r'%=', r'//=', r'\*\*=', r'&=', r'\|=', r'\^=',
            r'<<=', r'>>='
        ]

        code = ast.unparse(tree)

        # Count operators
        for pattern in operator_patterns:
            matches = re.findall(pattern, code)
            total_operators += len(matches)
            if matches:
                operators.add(pattern)

        # Count operands (identifiers and literals)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                operands.add(node.id)
                total_operands += 1
            elif isinstance(node, ast.Constant):
                operands.add(str(node.value))
                total_operands += 1

        n1 = len(operators)  # Number of distinct operators
        n2 = len(operands)   # Number of distinct operands
        N1 = total_operators  # Total number of operators
        N2 = total_operands   # Total number of operands

        # Calculate Halstead metrics
        vocabulary = n1 + n2
        length = N1 + N2

        if vocabulary > 0 and n1 > 0 and n2 > 0:
            volume = length * (math.log2(vocabulary))
            difficulty = (n1 / 2) * (N2 / n2)
            effort = difficulty * volume
            time_to_program = effort / 18  # Seconds
            delivered_bugs = volume / 3000
        else:
            volume = difficulty = effort = time_to_program = delivered_bugs = 0

        return {
            'vocabulary': vocabulary,
            'length': length,
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort,
            'time_to_program': time_to_program,
            'delivered_bugs': delivered_bugs
        }

    def calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers) + (1 if node.orelse else 0) + (1 if node.finalbody else 0)
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += len(node.items)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp):
                complexity += 1

        return complexity

    def analyze_type_safety(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze type safety and type annotation coverage."""

        functions = list(ast.walk(tree))
        functions = [f for f in functions if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]

        total_functions = len(functions)
        functions_with_type_hints = 0
        total_parameters = 0
        parameters_with_type_hints = 0
        functions_with_return_types = 0

        for func in functions:
            has_type_hints = False
            has_return_type = func.returns is not None

            if has_return_type:
                functions_with_return_types += 1

            # Count parameters with type hints
            for arg in func.args.args:
                total_parameters += 1
                if arg.annotation is not None:
                    parameters_with_type_hints += 1
                    has_type_hints = True

            # Handle *args and **kwargs
            if func.args.vararg and func.args.vararg.annotation:
                total_parameters += 1
                parameters_with_type_hints += 1
                has_type_hints = True

            if func.args.kwarg and func.args.kwarg.annotation:
                total_parameters += 1
                parameters_with_type_hints += 1
                has_type_hints = True

            if has_type_hints or has_return_type:
                functions_with_type_hints += 1

        return {
            'total_functions': total_functions,
            'functions_with_type_hints': functions_with_type_hints,
            'functions_with_return_types': functions_with_return_types,
            'type_hint_coverage': functions_with_type_hints / total_functions if total_functions > 0 else 0,
            'total_parameters': total_parameters,
            'parameters_with_type_hints': parameters_with_type_hints,
            'parameter_type_coverage': parameters_with_type_hints / total_parameters if total_parameters > 0 else 0
        }

    def analyze_documentation_coverage(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze documentation coverage and quality."""

        module_docstring = ast.get_docstring(tree)
        has_module_docstring = module_docstring is not None

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        functions_with_docs = sum(1 for f in functions if ast.get_docstring(f))
        classes_with_docs = sum(1 for c in classes if ast.get_docstring(c))

        # Analyze docstring quality
        docstring_quality = {
            'module': self.analyze_docstring_quality(module_docstring) if module_docstring else 0,
            'functions': [],
            'classes': []
        }

        for func in functions:
            doc = ast.get_docstring(func)
            if doc:
                docstring_quality['functions'].append({
                    'name': func.name,
                    'quality_score': self.analyze_docstring_quality(doc),
                    'has_examples': 'example' in doc.lower(),
                    'has_params': 'param' in doc.lower(),
                    'has_returns': 'return' in doc.lower()
                })

        for cls in classes:
            doc = ast.get_docstring(cls)
            if doc:
                docstring_quality['classes'].append({
                    'name': cls.name,
                    'quality_score': self.analyze_docstring_quality(doc)
                })

        return {
            'has_module_docstring': has_module_docstring,
            'total_functions': len(functions),
            'functions_with_documentation': functions_with_docs,
            'function_doc_coverage': functions_with_docs / len(functions) if functions else 0,
            'total_classes': len(classes),
            'classes_with_documentation': classes_with_docs,
            'class_doc_coverage': classes_with_docs / len(classes) if classes else 0,
            'quality_scores': docstring_quality
        }

    def analyze_docstring_quality(self, docstring: str) -> float:
        """Analyze docstring quality on a scale of 0-1."""
        if not docstring:
            return 0.0

        score = 0.0

        # Length check (reasonable documentation)
        if len(docstring.strip()) > 20:
            score += 0.2

        # Has sections
        doc_lower = docstring.lower()
        if any(keyword in doc_lower for keyword in ['param', 'return', 'example', 'note', 'warning']):
            score += 0.3

        # Has type information
        if any(keyword in doc_lower for keyword in ['type', 'str', 'int', 'list', 'dict']):
            score += 0.2

        # Has examples
        if 'example' in doc_lower or '>>>' in docstring:
            score += 0.2

        # Proper formatting (multiple lines)
        if docstring.count('\n') >= 2:
            score += 0.1

        return min(score, 1.0)

    def detect_code_smells(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect common code smells and anti-patterns."""
        smells = []

        for node in ast.walk(tree):
            # Long parameter lists
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.args.args) > 5:
                    smells.append({
                        'type': 'long_parameter_list',
                        'line': node.lineno,
                        'function': node.name,
                        'count': len(node.args.args),
                        'message': f"Function '{node.name}' has too many parameters ({len(node.args.args)})"
                    })

                # Long functions
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    lines = node.end_lineno - node.lineno
                    if lines > 50:
                        smells.append({
                            'type': 'long_function',
                            'line': node.lineno,
                            'function': node.name,
                            'lines': lines,
                            'message': f"Function '{node.name}' is too long ({lines} lines)"
                        })

            # Complex expressions
            elif isinstance(node, ast.BoolOp) and len(node.values) > 3:
                smells.append({
                    'type': 'complex_boolean_expression',
                    'line': node.lineno,
                    'message': f"Complex boolean expression with {len(node.values)} conditions"
                })

            # Deep nesting
            elif isinstance(node, ast.If):
                nesting_level = self._calculate_nesting_level(node)
                if nesting_level > 3:
                    smells.append({
                        'type': 'deep_nesting',
                        'line': node.lineno,
                        'level': nesting_level,
                        'message': f"Deep nesting detected (level {nesting_level})"
                    })

        return smells

    def _calculate_nesting_level(self, node: ast.AST, level: int = 0) -> int:
        """Calculate nesting level of a node."""
        max_level = level

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                child_level = self._calculate_nesting_level(child, level + 1)
                max_level = max(max_level, child_level)

        return max_level

    def generate_quality_report(self, tree: ast.AST, file_path: str) -> Dict[str, Any]:
        """Generate comprehensive code quality report."""

        report = {
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }

        # Calculate all metrics
        report['metrics']['halstead'] = self.calculate_halstead_metrics(tree)
        report['metrics']['cyclomatic_complexity'] = self.calculate_cyclomatic_complexity(tree)
        report['metrics']['type_safety'] = self.analyze_type_safety(tree)
        report['metrics']['documentation'] = self.analyze_documentation_coverage(tree)
        report['metrics']['code_smells'] = self.detect_code_smells(tree)

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(report['metrics'])
        report['quality_score'] = quality_score

        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report['metrics'])

        return report

    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall code quality score (0-100)."""
        score = 100.0

        # Deduct points for high complexity
        complexity = metrics['cyclomatic_complexity']
        if complexity > 20:
            score -= 20
        elif complexity > 10:
            score -= 10

        # Deduct points for poor type safety
        type_safety = metrics['type_safety']
        type_coverage = type_safety['type_hint_coverage']
        if type_coverage < 0.5:
            score -= 20
        elif type_coverage < 0.8:
            score -= 10

        # Deduct points for poor documentation
        doc_coverage = metrics['documentation']['function_doc_coverage']
        if doc_coverage < 0.5:
            score -= 15
        elif doc_coverage < 0.8:
            score -= 5

        # Deduct points for code smells
        code_smells = metrics['code_smells']
        if len(code_smells) > 10:
            score -= 15
        elif len(code_smells) > 5:
            score -= 5

        return max(0.0, min(100.0, score))

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on metrics."""
        recommendations = []

        # Complexity recommendations
        if metrics['cyclomatic_complexity'] > 15:
            recommendations.append("Consider breaking down complex functions to reduce cyclomatic complexity")

        # Type safety recommendations
        type_safety = metrics['type_safety']
        if type_safety['type_hint_coverage'] < 0.8:
            recommendations.append("Add type hints to improve code maintainability and IDE support")

        # Documentation recommendations
        doc_metrics = metrics['documentation']
        if doc_metrics['function_doc_coverage'] < 0.8:
            recommendations.append("Add comprehensive docstrings to all public functions and classes")

        # Code smell recommendations
        code_smells = metrics['code_smells']
        long_functions = [s for s in code_smells if s['type'] == 'long_function']
        if long_functions:
            recommendations.append(f"Refactor {len(long_functions)} long functions for better readability")

        return recommendations
```

### 4. Integration with RAG Systems

#### Documentation Chunk Generation
```python
def generate_rag_chunks(module_info: ModuleInfo) -> List[Dict[str, Any]]:
    """Generate optimized chunks for RAG systems."""

    chunks = []

    # Module-level chunk
    if module_info.docstring:
        chunks.append({
            'type': 'module_documentation',
            'content': f"# {module_info.name}\\n\\n{module_info.docstring}",
            'file_path': module_info.name,
            'language': 'python',
            'metadata': {
                'module': module_info.name,
                'type': 'overview'
            },
            'user_roles': ['developer', 'architect'],
            'expertise_level': 'beginner'
        })

    # Class chunks
    for cls in module_info.classes:
        content = f"# Class: {cls.name}\\n\\n"

        if cls.docstring:
            content += f"{cls.docstring}\\n\\n"

        if cls.base_classes:
            content += f"**Inherits from:** {', '.join(cls.base_classes)}\\n\\n"

        if cls.decorators:
            content += f"**Decorators:** {', '.join(cls.decorators)}\\n\\n"

        content += "## Methods\\n\\n"

        for method in cls.methods:
            method_content = f"### {method.name}()\\n\\n"

            if method.docstring:
                method_content += f"{method.docstring}\\n\\n"

            # Parameters
            if method.parameters:
                params = []
                for param in method.parameters:
                    param_str = param['name']
                    if param['type']:
                        param_str += f": {param['type'].name}"
                    if param['has_default']:
                        param_str += " = ..."
                    params.append(param_str)

                method_content += f"**Parameters:** {', '.join(params)}\\n\\n"

            # Return type
            if method.return_type:
                method_content += f"**Returns:** {method.return_type.name}\\n\\n"

            # Decorators and modifiers
            decorators = []
            if method.is_async:
                decorators.append("async")
            if method.is_property:
                decorators.append("property")
            if method.is_class_method:
                decorators.append("classmethod")
            if method.is_static_method:
                decorators.append("staticmethod")

            if decorators:
                method_content += f"**Modifiers:** {', '.join(decorators)}\\n\\n"

            method_content += f"**Complexity:** {method.complexity_score}\\n\\n"
            content += method_content

        # Properties
        if cls.properties:
            content += "## Properties\\n\\n"
            for prop in cls.properties:
                content += f"### {prop['name']}\\n\\n"
                if prop['type']:
                    content += f"**Type:** {prop['type'].name}\\n\\n"
                if prop['value']:
                    content += f"**Default:** {prop['value']}\\n\\n"

        chunks.append({
            'type': 'class',
            'name': cls.name,
            'content': content,
            'file_path': module_info.name,
            'language': 'python',
            'metadata': {
                'class': cls.name,
                'base_classes': cls.base_classes,
                'methods': len(cls.methods),
                'properties': len(cls.properties),
                'is_abstract': cls.is_abstract,
                'is_dataclass': cls.is_dataclass
            },
            'user_roles': ['developer', 'architect'],
            'expertise_level': 'intermediate'
        })

    # Function chunks
    for func in module_info.functions:
        content = f"# Function: {func.name}()\\n\\n"

        if func.docstring:
            content += f"{func.docstring}\\n\\n"

        # Parameters
        if func.parameters:
            params = []
            for param in func.parameters:
                param_str = param['name']
                if param['type']:
                    param_str += f": {param['type'].name}"
                if param['has_default']:
                    param_str += " = ..."
                params.append(param_str)

            content += f"**Parameters:** {', '.join(params)}\\n\\n"

        # Return type
        if func.return_type:
            content += f"**Returns:** {func.return_type.name}\\n\\n"

        # Decorators
        if func.decorators:
            content += f"**Decorators:** {', '.join(func.decorators)}\\n\\n"

        # Complexity
        content += f"**Complexity:** {func.complexity_score}\\n\\n"

        chunks.append({
            'type': 'function',
            'name': func.name,
            'content': content,
            'file_path': module_info.name,
            'language': 'python',
            'metadata': {
                'function': func.name,
                'parameters': len(func.parameters),
                'complexity': func.complexity_score,
                'async': func.is_async,
                'decorators': func.decorators
            },
            'user_roles': ['developer'],
            'expertise_level': func.complexity_score > 10 ? 'advanced' : 'intermediate'
        })

    return chunks
```

### 5. Error Handling and Recovery

#### Robust Parsing with Fallback
```python
def robust_python_analysis(file_path: str) -> Optional[ModuleInfo]:
    """Analyze Python file with comprehensive error handling and fallback strategies."""

    try:
        # First attempt: Standard parsing
        return analyze_python_module(file_path)

    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")

        # Attempt to fix common syntax issues
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Try to fix common issues
            fixed_code = fix_common_syntax_errors(code)

            if fixed_code != code:
                print("Attempting to parse with syntax fixes...")
                return analyze_python_module_content(fixed_code, file_path)

        except Exception as fix_error:
            print(f"Failed to fix syntax errors: {fix_error}")

        # Final fallback: Try to extract basic information using regex
        return basic_regex_analysis(file_path)

    except Exception as e:
        print(f"Unexpected error analyzing {file_path}: {e}")
        return None

def fix_common_syntax_errors(code: str) -> str:
    """Attempt to fix common Python syntax errors."""

    # Fix missing colons in function/class definitions
    code = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*$', lambda m: m.group(0) + ':', code, flags=re.MULTILINE)
    code = re.sub(r'class\s+(\w+)\s*(?:\([^)]*\))?\s*$', lambda m: m.group(0) + ':', code, flags=re.MULTILINE)

    # Fix indentation issues (basic)
    lines = code.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            fixed_lines.append(line)
            continue

        # Basic indentation fix for blocks
        if i > 0 and lines[i-1].strip().endswith(':'):
            if not line.startswith(' ') and not line.startswith('\t'):
                fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def basic_regex_analysis(file_path: str) -> ModuleInfo:
    """Fallback analysis using regex when AST parsing fails."""

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    module_name = Path(file_path).stem

    # Extract functions using regex
    function_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    functions = [name for name in re.findall(function_pattern, code)]

    # Extract classes using regex
    class_pattern = r'class\s+(\w+)\s*(?:\([^)]*\))?:'
    classes = [name for name in re.findall(class_pattern, code)]

    # Extract imports using regex
    import_pattern = r'^(?:from\s+\S+\s+)?import\s+(.+)'
    imports = []
    for match in re.finditer(import_pattern, code, re.MULTILINE):
        imports.append({'module': match.group(1).strip(), 'line': 0})

    return ModuleInfo(
        name=module_name,
        docstring=None,
        imports=imports,
        functions=[FunctionInfo(
            name=name,
            parameters=[],
            return_type=None,
            decorators=[],
            docstring=None,
            is_async=False,
            is_abstract=False,
            is_property=False,
            is_class_method=False,
            is_static_method=False,
            line_number=0,
            complexity_score=1,
            type_params=[]
        ) for name in functions],
        classes=[ClassInfo(
            name=name,
            base_classes=[],
            implemented_interfaces=[],
            methods=[],
            properties=[],
            class_variables=[],
            decorators=[],
            docstring=None,
            is_abstract=False,
            is_dataclass=False,
            line_number=0,
            type_params=[]
        ) for name in classes],
        global_variables=[],
        type_aliases=[],
        complexity_metrics={
            'total_functions': len(functions),
            'total_classes': len(classes),
            'total_imports': len(imports),
            'max_function_complexity': 1,
            'abstract_classes': 0,
            'async_functions': 0,
            'dataclasses': 0
        }
    )
```

### 6. Performance Optimization

#### Incremental Analysis and Caching
```python
import hashlib
import pickle
from pathlib import Path
from functools import lru_cache

class IncrementalPythonAnalyzer:
    """Python analyzer with incremental analysis and caching."""

    def __init__(self, cache_dir: str = '.py_analysis_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.analysis_cache = {}

    def _get_file_hash(self, file_path: str) -> str:
        """Calculate hash of file contents for change detection."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _get_cache_path(self, file_path: str) -> Path:
        """Get cache file path for a given source file."""
        return self.cache_dir / f"{Path(file_path).stem}.analysis_cache"

    def analyze_with_cache(self, file_path: str) -> Optional[ModuleInfo]:
        """Analyze file with caching support."""

        current_hash = self._get_file_hash(file_path)
        cache_path = self._get_cache_path(file_path)

        # Check if we have a valid cache entry
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)

                if cached_data['file_hash'] == current_hash:
                    return cached_data['module_info']

            except (pickle.PickleError, EOFError, KeyError):
                # Cache is corrupted, remove it
                cache_path.unlink(missing_ok=True)

        # No valid cache, perform analysis
        module_info = robust_python_analysis(file_path)

        if module_info:
            # Cache the results
            cache_data = {
                'file_hash': current_hash,
                'module_info': module_info,
                'timestamp': datetime.now().isoformat()
            }

            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
            except (pickle.PickleError, OSError) as e:
                print(f"Failed to cache analysis results: {e}")

        return module_info

    def analyze_project(self, project_root: str) -> Dict[str, ModuleInfo]:
        """Analyze entire Python project with incremental updates."""

        project_path = Path(project_root)
        python_files = list(project_path.rglob('*.py'))

        results = {}

        for file_path in python_files:
            # Skip __pycache__ and other temporary directories
            if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                continue

            try:
                module_info = self.analyze_with_cache(str(file_path))
                if module_info:
                    results[str(file_path)] = module_info
            except Exception as e:
                print(f"Failed to analyze {file_path}: {e}")

        return results

    def clear_cache(self):
        """Clear all analysis cache."""
        for cache_file in self.cache_dir.glob('*.analysis_cache'):
            cache_file.unlink()
```

### 7. Use Cases for RAG Systems

1. **Automated Documentation Generation**: Extract comprehensive docstrings, type hints, and examples to create documentation
2. **Code Search and Discovery**: Enable semantic search across Python codebases with full context
3. **API Reference Generation**: Automatically generate API documentation from classes and functions
4. **Code Quality Assessment**: Identify complex functions, missing documentation, and type safety issues
5. **Dependency Analysis**: Map import relationships and detect circular dependencies
6. **Refactoring Assistance**: Identify code smells and suggest improvements
7. **Type Safety Analysis**: Assess type hint coverage and identify potential type-related issues
8. **Testing Guidance**: Identify functions that need test coverage based on complexity

### 8. Best Practices and Considerations

- **Use multiple analysis tools**: Combine built-in ast with third-party tools for comprehensive coverage
- **Handle errors gracefully**: Implement fallback strategies for malformed code
- **Cache analysis results**: Use incremental analysis for large codebases
- **Extract comprehensive metadata**: Include type information, complexity metrics, and documentation quality
- **Generate contextual chunks**: Create RAG chunks with appropriate user roles and expertise levels
- **Monitor performance**: Use caching and incremental updates for optimal performance
- **Validate with multiple sources**: Cross-reference analysis results between different tools
- **Handle modern Python features**: Support async/await, type hints, dataclasses, and other modern constructs

**Best for**: Comprehensive Python code analysis requiring detailed type information, complexity metrics, and production-ready documentation generation for RAG systems.