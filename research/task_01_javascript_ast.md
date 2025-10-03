# Task 1: JavaScript/TypeScript AST Parsing

## Comprehensive Parser Comparison

### 1. @babel/parser (Formerly Babylon)

### Overview
`@babel/parser` is the modern, actively maintained parser used by Babel. It supports JavaScript, TypeScript, JSX, Flow, and experimental features with excellent error recovery and source map support.

### Installation
```bash
npm install @babel/parser
```

### Basic Usage
```javascript
const parser = require('@babel/parser');

const code = `
interface User {
  id: number;
  name: string;
  email: string;
}

class UserService {
  private users: User[] = [];

  async getUserById(id: number): Promise<User | null> {
    return this.users.find(user => user.id === id) || null;
  }

  addUser(user: User): void {
    this.users.push(user);
  }
}

export default UserService;
`;

// Parse with TypeScript support
const ast = parser.parse(code, {
  sourceType: 'module',
  plugins: [
    'typescript',
    'jsx',
    'classProperties',
    'optionalChaining',
    'nullishCoalescingOperator'
  ],
  allowImportExportEverywhere: true,
  allowReturnOutsideFunction: true
});

console.log(JSON.stringify(ast, null, 2));
```

### Advanced Configuration
```javascript
const parseOptions = {
  // Source type
  sourceType: 'module', // 'script' or 'module'

  // Plugins for different syntax features
  plugins: [
    'typescript',           // TypeScript support
    'jsx',                  // JSX support
    'decorators',          // Decorators syntax
    'classProperties',     // Class properties
    'objectRestSpread',    // Object rest/spread
    'dynamicImport',       // Dynamic import
    'optionalChaining',    // Optional chaining
    'nullishCoalescingOperator', // Nullish coalescing
    'classPrivateMethods', // Private class methods
    'classPrivateProperties', // Private class properties
    'bigInt',              // BigInt literals
    'numericSeparator',    // Numeric separators
    'throwExpressions',    // Throw expressions
    'logicalAssignment',   // Logical assignment
    'pipelineOperator',    // Pipeline operator
    'partialApplication',  // Partial application
    'doExpressions',       // Do expressions
    'functionBind',        // Function bind operator
    'functionSent',        // Function.sent
    'exportDefaultFrom',   // Export default from
    'exportNamespaceFrom', // Export namespace from
    'moduleStringNames'    // Module string names
  ],

  // Error recovery options
  allowImportExportEverywhere: false,
  allowReturnOutsideFunction: false,
  allowSuperOutsideMethod: false,
  allowHashBang: true,
  strictMode: null,
  sourceFilename: undefined,
  startLine: 1,
  startColumn: 0,
  ranges: false,
  tokens: false,
  errorRecovery: false
};
```

### 2. TypeScript Compiler API

### Overview
The TypeScript Compiler API provides native TypeScript parsing with full type information and semantic analysis capabilities.

### Installation
```bash
npm install typescript
```

### Basic Usage
```typescript
import * as ts from 'typescript';

const code = `
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async fetch<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await fetch(\`\${this.baseUrl}\${endpoint}\`);
    return response.json();
  }
}
`;

// Create source file
const sourceFile = ts.createSourceFile(
  'temp.ts',
  code,
  ts.ScriptTarget.Latest,
  true
);

// Extract interfaces and classes
function extractTypeScriptStructure(sourceFile: ts.SourceFile) {
  const interfaces: any[] = [];
  const classes: any[] = [];
  const functions: any[] = [];

  function visit(node: ts.Node) {
    if (ts.isInterfaceDeclaration(node)) {
      interfaces.push({
        name: node.name.text,
        typeParameters: node.typeParameters?.map(tp => tp.name.text) || [],
        properties: node.members.filter(ts.isPropertySignature).map(prop => ({
          name: prop.name.getText(),
          type: prop.type?.getText() || 'any',
          optional: prop.questionToken !== undefined
        })),
        methods: node.members.filter(ts.isMethodSignature).map(method => ({
          name: method.name.getText(),
          parameters: method.parameters.map(param => ({
            name: param.name.getText(),
            type: param.type?.getText() || 'any'
          })),
          returnType: method.type?.getText() || 'void'
        }))
      });
    }

    if (ts.isClassDeclaration(node)) {
      const properties = node.members.filter(ts.isPropertyDeclaration).map(prop => ({
        name: prop.name.getText(),
        type: prop.type?.getText() || 'any',
        accessibility: ts.getModifierFlags(prop) & ts.ModifierFlags.Private ? 'private' :
                      ts.getModifierFlags(prop) & ts.ModifierFlags.Protected ? 'protected' : 'public',
        static: ts.getModifierFlags(prop) & ts.ModifierFlags.Static
      }));

      const methods = node.members.filter(ts.isMethodDeclaration).map(method => ({
        name: method.name.getText(),
        parameters: method.parameters.map(param => ({
          name: param.name.getText(),
          type: param.type?.getText() || 'any',
          optional: param.questionToken !== undefined
        })),
        returnType: method.type?.getText() || 'void',
        accessibility: ts.getModifierFlags(method) & ts.ModifierFlags.Private ? 'private' :
                      ts.getModifierFlags(method) & ts.ModifierFlags.Protected ? 'protected' : 'public',
        async: !!ts.getEffectiveModifierFlags(method) & ts.ModifierFlags.Async
      }));

      classes.push({
        name: node.name?.getText() || 'Anonymous',
        extends: node.heritageClauses?.[0]?.types?.[0]?.getText(),
        implements: node.heritageClauses?.filter(hc => hc.token === ts.SyntaxKind.ImplementsKeyword)
          .flatMap(hc => hc.types.map(t => t.getText())),
        properties,
        methods
      });
    }

    if (ts.isFunctionDeclaration(node)) {
      functions.push({
        name: node.name?.getText() || 'Anonymous',
        parameters: node.parameters.map(param => ({
          name: param.name.getText(),
          type: param.type?.getText() || 'any',
          optional: param.questionToken !== undefined
        })),
        returnType: node.type?.getText() || 'void',
        async: !!ts.getEffectiveModifierFlags(node) & ts.ModifierFlags.Async,
        generator: !!ts.getEffectiveModifierFlags(node) & ts.ModifierFlags.Generator
      });
    }

    ts.forEachChild(node, visit);
  }

  visit(sourceFile);

  return { interfaces, classes, functions };
}

const structure = extractTypeScriptStructure(sourceFile);
console.log('TypeScript Structure:', JSON.stringify(structure, null, 2));
```

### 3. Acorn Parser

### Overview
Acorn is a small, fast, JavaScript-based parser that's highly extensible and produces ESTree-compliant ASTs.

### Installation
```bash
npm install acorn acorn-walk
```

### Basic Usage
```javascript
const acorn = require('acorn');
const walk = require('acorn-walk');

const code = `
const utils = {
  formatDate: (date) => date.toISOString(),
  calculateTax: (amount, rate = 0.1) => amount * rate,
  validateEmail: (email) => /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)
};

export default utils;
`;

// Parse with modern JavaScript support
const ast = acorn.parse(code, {
  ecmaVersion: 'latest',
  sourceType: 'module',
  locations: true,
  allowHashBang: true,
  allowReturnOutsideFunction: true,
  allowImportExportEverywhere: true
});

// Walk the AST
const exports = [];
const functions = [];

walk.full(ast, (node) => {
  if (node.type === 'ExportDefaultDeclaration') {
    exports.push({
      type: 'default',
      declaration: node.declaration.type
    });
  }

  if (node.type === 'FunctionExpression' || node.type === 'ArrowFunctionExpression') {
    functions.push({
      type: node.type,
      async: node.async,
      generator: node.generator,
      params: node.params.length
    });
  }
});

console.log('AST:', ast);
console.log('Exports:', exports);
console.log('Functions:', functions);
```

### 4. Esprima (Enhanced)

### Overview
Esprima remains a solid choice for standards-compliant parsing with excellent TypeScript support and error recovery.

### Installation
```bash
npm install esprima
```

### Enhanced Usage
```javascript
const esprima = require('esprima');

const code = `
// Modern JavaScript with TypeScript
type UserId = string | number;

interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  ssl?: boolean;
}

class DatabaseManager {
  #connection: any; // Private field

  constructor(private config: DatabaseConfig) {
    this.#connection = null;
  }

  async connect(): Promise<void> {
    try {
      this.#connection = await this.createConnection();
      console.log('Connected to database');
    } catch (error) {
      console.error('Connection failed:', error);
      throw error;
    }
  }

  private createConnection(): Promise<any> {
    // Implementation
    return Promise.resolve('mock connection');
  }

  async query<T>(sql: string, params: any[] = []): Promise<T[]> {
    if (!this.#connection) {
      throw new Error('Not connected to database');
    }

    // Execute query
    return [];
  }

  async disconnect(): Promise<void> {
    if (this.#connection) {
      this.#connection = null;
      console.log('Disconnected from database');
    }
  }
}

export { DatabaseManager, DatabaseConfig };
export type { UserId };
`;

// Parse with comprehensive options
const parseOptions = {
  jsx: true,
  typescript: true,
  loc: true,
  range: true,
  tokens: true,
  comment: true,
  tolerant: true,
  sourceType: 'module',
  ecmaVersion: 2024,
  allowReturnOutsideFunction: true,
  allowImportExportEverywhere: true
};

const ast = esprima.parseModule(code, parseOptions);

// Enhanced extraction functions
function extractModernJavaScriptStructure(ast) {
  const structure = {
    types: [],
    interfaces: [],
    classes: [],
    functions: [],
    variables: [],
    imports: [],
    exports: [],
    decorators: []
  };

  function traverse(node, parent = null) {
    // Extract type declarations
    if (node.type === 'TSTypeAliasDeclaration') {
      structure.types.push({
        name: node.id.name,
        typeParameters: node.typeParameters?.params.map(p => p.name) || [],
        typeAnnotation: node.typeAnnotation.type
      });
    }

    // Extract interfaces
    if (node.type === 'TSInterfaceDeclaration') {
      structure.interfaces.push({
        name: node.id.name,
        typeParameters: node.typeParameters?.params.map(p => p.name) || [],
        extends: node.extends?.map(ext => ext.expression.name) || [],
        body: node.body.body.map(member => ({
          type: member.type,
          name: member.key?.name || member.key?.value,
          optional: member.optional,
          type: member.typeAnnotation?.typeAnnotation?.typeName?.name || 'any'
        }))
      });
    }

    // Extract classes with modern features
    if (node.type === 'ClassDeclaration') {
      const classInfo = {
        name: node.id.name,
        typeParameters: node.typeParameters?.params.map(p => p.name) || [],
        extends: node.superClass?.name || null,
        implements: node.implements?.map(impl => impl.expression.name) || [],
        decorators: node.decorators?.map(dec => dec.expression.name) || [],
        privateFields: [],
        publicFields: [],
        methods: [],
        staticMethods: [],
        privateMethods: [],
        getterSetters: []
      };

      // Extract class members
      node.body.body.forEach(member => {
        if (member.type === 'PropertyDefinition') {
          const fieldInfo = {
            name: member.key.name,
            type: member.typeAnnotation?.typeAnnotation?.typeName?.name || 'any',
            optional: member.optional,
            readonly: member.readonly,
            static: member.static,
            value: member.value?.value
          };

          if (member.key.name.startsWith('#')) {
            classInfo.privateFields.push(fieldInfo);
          } else {
            classInfo.publicFields.push(fieldInfo);
          }
        }

        if (member.type === 'MethodDefinition') {
          const methodInfo = {
            name: member.key.name,
            parameters: member.value.params.map(p => ({
              name: p.name,
              type: p.typeAnnotation?.typeAnnotation?.typeName?.name || 'any',
              optional: p.optional
            })),
            returnType: member.value.returnType?.typeAnnotation?.typeName?.name || 'void',
            async: member.value.async,
            generator: member.value.generator,
            static: member.static,
            private: member.key.name.startsWith('#'),
            kind: member.kind // 'method', 'get', 'set', 'constructor'
          };

          if (methodInfo.private) {
            classInfo.privateMethods.push(methodInfo);
          } else if (methodInfo.static) {
            classInfo.staticMethods.push(methodInfo);
          } else {
            classInfo.methods.push(methodInfo);
          }
        }
      });

      structure.classes.push(classInfo);
    }

    // Extract modern function declarations
    if (node.type === 'FunctionDeclaration') {
      structure.functions.push({
        name: node.id.name,
        parameters: node.params.map(p => ({
          name: p.name,
          type: p.typeAnnotation?.typeAnnotation?.typeName?.name || 'any',
          optional: p.optional,
          defaultValue: p.value?.value
        })),
        returnType: node.returnType?.typeAnnotation?.typeName?.name || 'void',
        async: node.async,
        generator: node.generator,
        typeParameters: node.typeParameters?.params.map(p => p.name) || []
      });
    }

    // Extract import/export statements
    if (node.type === 'ImportDeclaration') {
      structure.imports.push({
        source: node.source.value,
        specifiers: node.specifiers.map(spec => ({
          type: spec.type,
          name: spec.local.name,
          imported: spec.imported?.name
        }))
      });
    }

    if (node.type === 'ExportNamedDeclaration') {
      structure.exports.push({
        type: 'named',
        declaration: node.declaration?.type,
        specifiers: node.specifiers?.map(spec => ({
          local: spec.local.name,
          exported: spec.exported.name
        })) || [],
        source: node.source?.value
      });
    }

    if (node.type === 'ExportDefaultDeclaration') {
      structure.exports.push({
        type: 'default',
        declaration: node.declaration.type,
        name: node.declaration.name || node.declaration.id?.name
      });
    }

    // Traverse child nodes
    for (const key in node) {
      if (node[key] && typeof node[key] === 'object') {
        traverse(node[key], node);
      }
    }
  }

  traverse(ast);
  return structure;
}

const structure = extractModernJavaScriptStructure(ast);
console.log('Enhanced Structure:', JSON.stringify(structure, null, 2));
```

### AST Transformation and Code Generation

### Transforming AST
```javascript
const { parse } = require('@babel/parser');
const generate = require('@babel/generator').default;
const traverse = require('@babel/traverse').default;
const t = require('@babel/types');

const code = `
function greet(name) {
  return \`Hello, \${name}!\`;
}

const result = greet('World');
`;

// Parse code
const ast = parse(code, {
  sourceType: 'module',
  plugins: ['jsx']
});

// Transform AST
traverse(ast, {
  // Transform function calls
  CallExpression(path) {
    if (path.node.callee.name === 'greet') {
      // Change function call
      path.node.callee.name = 'welcomeUser';
    }
  },

  // Transform function declarations
  FunctionDeclaration(path) {
    if (path.node.id.name === 'greet') {
      // Rename function
      path.node.id.name = 'welcomeUser';

      // Add parameter validation
      const validationBlock = t.blockStatement([
        t.ifStatement(
          t.unaryExpression('!', path.node.params[0]),
          t.blockStatement([
            t.throwStatement(
              t.newExpression(t.identifier('Error'), [
                t.stringLiteral('Name is required')
              ])
            )
          ])
        )
      ]);

      // Insert validation at start of function
      path.get('body').unshiftContainer('body', validationBlock.body[0]);
    }
  }
});

// Generate transformed code
const result = generate(ast, {}, code);
console.log('Transformed Code:', result.code);
```

### Code Quality Metrics

### Complexity Analysis
```javascript
function analyzeCodeComplexity(ast) {
  const metrics = {
    totalLines: 0,
    totalFunctions: 0,
    totalClasses: 0,
    cyclomaticComplexity: 0,
    maintainabilityIndex: 0,
    HalsteadMetrics: {
      operators: 0,
      operands: 0,
      distinctOperators: new Set(),
      distinctOperands: new Set()
    }
  };

  function calculateCyclomaticComplexity(node) {
    let complexity = 1; // Base complexity

    function traverse(node) {
      switch (node.type) {
        case 'IfStatement':
        case 'ConditionalExpression':
        case 'ForStatement':
        case 'ForInStatement':
        case 'ForOfStatement':
        case 'WhileStatement':
        case 'DoWhileStatement':
          complexity++;
          break;
        case 'SwitchStatement':
          complexity += node.cases.length;
          break;
        case 'LogicalExpression':
          if (node.operator === '&&' || node.operator === '||') {
            complexity++;
          }
          break;
      }

      for (const key in node) {
        if (node[key] && typeof node[key] === 'object') {
          traverse(node[key]);
        }
      }
    }

    traverse(node);
    return complexity;
  }

  function extractHalsteadMetrics(node) {
    const operators = ['+', '-', '*', '/', '%', '++', '--', '==', '!=', '===', '!==',
                      '<', '>', '<=', '>=', '&&', '||', '!', '&', '|', '^', '~', '<<',
                      '>>', '>>>', '=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=',
                      '>>>=', '&=', '|=', '^=', '=>'];

    function traverse(node) {
      // Count operators
      if (node.type === 'BinaryExpression' || node.type === 'LogicalExpression') {
        metrics.HalsteadMetrics.operators++;
        metrics.HalsteadMetrics.distinctOperators.add(node.operator);
      }

      // Count operands
      if (node.type === 'Identifier') {
        metrics.HalsteadMetrics.operands++;
        metrics.HalsteadMetrics.distinctOperands.add(node.name);
      }

      if (node.type === 'Literal') {
        metrics.HalsteadMetrics.operands++;
        metrics.HalsteadMetrics.distinctOperands.add(String(node.value));
      }

      for (const key in node) {
        if (node[key] && typeof node[key] === 'object') {
          traverse(node[key]);
        }
      }
    }

    traverse(node);
  }

  // Extract all metrics
  traverse(ast, (node) => {
    if (node.type === 'FunctionDeclaration' || node.type === 'FunctionExpression') {
      metrics.totalFunctions++;
      metrics.cyclomaticComplexity += calculateCyclomaticComplexity(node);
      extractHalsteadMetrics(node);
    }

    if (node.type === 'ClassDeclaration') {
      metrics.totalClasses++;
    }
  });

  // Calculate maintainability index
  const vocabulary = metrics.HalsteadMetrics.distinctOperators.size +
                   metrics.HalsteadMetrics.distinctOperands.size;
  const length = metrics.HalsteadMetrics.operators + metrics.HalsteadMetrics.operands;
  const volume = length * Math.log2(vocabulary) / Math.log2(2);
  const difficulty = (metrics.HalsteadMetrics.distinctOperators.size *
                    metrics.HalsteadMetrics.operators) / (2 * metrics.HalsteadMetrics.distinctOperands.size);
  const effort = difficulty * volume;

  metrics.maintainabilityIndex = Math.max(0, (171 - 5.2 * Math.log(volume) -
                                            0.23 * metrics.cyclomaticComplexity - 16.2 * Math.log(length)) * 100 / 171);

  return metrics;
}
```

### Integration Pattern for RAG Systems

### Comprehensive Analysis Pipeline
```javascript
class JavaScriptAnalyzer {
  constructor() {
    this.parsers = {
      babel: require('@babel/parser'),
      typescript: require('typescript'),
      acorn: require('acorn'),
      esprima: require('esprima')
    };
  }

  async analyzeFile(filePath, options = {}) {
    const fs = require('fs');
    const path = require('path');

    const code = fs.readFileSync(filePath, 'utf8');
    const extension = path.extname(filePath).toLowerCase();

    // Choose parser based on file type
    let parser = 'babel';
    let parseOptions = {
      sourceType: 'module',
      plugins: ['jsx'],
      loc: true,
      ranges: true
    };

    if (extension === '.ts' || extension === '.tsx') {
      parseOptions.plugins.push('typescript');
      if (extension === '.tsx') {
        parseOptions.plugins.push('tsx');
      }
    }

    // Parse code
    let ast;
    try {
      if (parser === 'babel') {
        ast = this.parsers.babel.parse(code, parseOptions);
      } else if (parser === 'typescript') {
        // TypeScript API parsing
      }
    } catch (error) {
      console.error(`Parse error in ${filePath}:`, error.message);
      return null;
    }

    // Extract comprehensive structure
    const structure = this.extractComprehensiveStructure(ast, code);

    // Calculate metrics
    const metrics = this.calculateCodeMetrics(ast, code);

    // Generate documentation chunks
    const chunks = this.generateDocumentationChunks(structure, metrics, filePath);

    return {
      filePath,
      language: extension === '.ts' || extension === '.tsx' ? 'typescript' : 'javascript',
      structure,
      metrics,
      chunks,
      ast
    };
  }

  extractComprehensiveStructure(ast, code) {
    // Extract all relevant information for RAG
    const structure = {
      imports: [],
      exports: [],
      types: [],
      interfaces: [],
      classes: [],
      functions: [],
      variables: [],
      decorators: [],
      comments: this.extractComments(code),
      dependencies: this.extractDependencies(ast),
      complexity: this.calculateComplexity(ast)
    };

    // Implementation of comprehensive extraction
    // ... (similar to previous examples but more thorough)

    return structure;
  }

  generateDocumentationChunks(structure, metrics, filePath) {
    const chunks = [];

    // Generate chunks for different content types
    structure.classes.forEach(cls => {
      chunks.push({
        type: 'class',
        name: cls.name,
        content: this.formatClassDocumentation(cls),
        file_path: filePath,
        language: 'javascript',
        metadata: {
          complexity: cls.complexity,
          methods: cls.methods.length,
          dependencies: cls.dependencies
        },
        user_roles: ['developer', 'architect'],
        expertise_level: 'intermediate'
      });
    });

    structure.functions.forEach(func => {
      chunks.push({
        type: 'function',
        name: func.name,
        content: this.formatFunctionDocumentation(func),
        file_path: filePath,
        language: 'javascript',
        metadata: {
          complexity: func.complexity,
          parameters: func.parameters.length,
          async: func.async
        },
        user_roles: ['developer'],
        expertise_level: func.complexity > 10 ? 'advanced' : 'intermediate'
      });
    });

    return chunks;
  }

  formatClassDocumentation(cls) {
    let doc = `## Class: ${cls.name}\\n\\n`;

    if (cls.typeParameters.length > 0) {
      doc += `**Type Parameters**: ${cls.typeParameters.join(', ')}\\n\\n`;
    }

    if (cls.extends) {
      doc += `**Extends**: ${cls.extends}\\n\\n`;
    }

    if (cls.implements.length > 0) {
      doc += `**Implements**: ${cls.implements.join(', ')}\\n\\n`;
    }

    doc += `### Properties\\n\\n`;
    cls.publicFields.forEach(field => {
      doc += `- \`${field.name}\`: ${field.type}${field.optional ? '?' : ''}\\n`;
    });

    doc += `\\n### Methods\\n\\n`;
    cls.methods.forEach(method => {
      doc += `#### ${method.name}()\\n`;
      doc += `**Parameters**: ${method.parameters.map(p => `${p.name}: ${p.type}`).join(', ')}\\n`;
      doc += `**Returns**: ${method.returnType}\\n`;
      if (method.async) doc += `**Async**: Yes\\n`;
      doc += '\\n';
    });

    return doc;
  }

  formatFunctionDocumentation(func) {
    let doc = `## Function: ${func.name}()\\n\\n`;

    doc += `**Parameters**: ${func.parameters.map(p => `${p.name}: ${p.type}${p.optional ? '?' : ''}`).join(', ')}\\n`;
    doc += `**Returns**: ${func.returnType}\\n`;
    if (func.async) doc += `**Async**: Yes\\n`;
    if (func.generator) doc += `**Generator**: Yes\\n`;

    return doc;
  }
}

// Usage example
const analyzer = new JavaScriptAnalyzer();
const result = await analyzer.analyzeFile('./src/components/UserService.ts');
console.log('Analysis Result:', result);
```

### Error Handling and Recovery

### Robust Parsing with Error Recovery
```javascript
function parseWithErrorRecovery(code, options = {}) {
  const { parse } = require('@babel/parser');

  const parseOptions = {
    sourceType: 'module',
    plugins: ['typescript', 'jsx'],
    errorRecovery: true,
    allowReturnOutsideFunction: true,
    allowImportExportEverywhere: true,
    ...options
  };

  try {
    return parse(code, parseOptions);
  } catch (error) {
    console.warn('Parse error, attempting recovery...');

    // Remove problematic syntax and retry
    let sanitizedCode = code
      .replace(/@[^\\n]+/g, '') // Remove decorators
      .replace(/#[^\\n]+/g, '') // Remove private fields
      .replace(/\\?.[^\\n]+/g, ''); // Remove optional chaining

    try {
      return parse(sanitizedCode, parseOptions);
    } catch (secondError) {
      console.error('Failed to parse even after sanitization');
      return null;
    }
  }
}
```

### Performance Optimization

### Incremental Parsing
```javascript
class IncrementalParser {
  constructor() {
    this.cache = new Map();
    this.fileVersions = new Map();
  }

  parseFile(filePath, code) {
    const currentVersion = this.calculateFileVersion(code);

    // Check if file hasn't changed
    if (this.fileVersions.get(filePath) === currentVersion) {
      return this.cache.get(filePath);
    }

    // Parse the file
    const ast = this.parseCode(code);

    // Cache the result
    this.cache.set(filePath, ast);
    this.fileVersions.set(filePath, currentVersion);

    return ast;
  }

  calculateFileVersion(code) {
    // Simple hash for version tracking
    let hash = 0;
    for (let i = 0; i < code.length; i++) {
      const char = code.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
  }

  parseCode(code) {
    // Implement parsing with caching
  }
}
```

### Use Cases for RAG Systems

1. **Automated Documentation Generation**: Extract function signatures, class definitions, and type information to generate comprehensive documentation
2. **Code Search and Navigation**: Enable semantic search across codebases by understanding structure and relationships
3. **Dependency Analysis**: Map import/export relationships and identify circular dependencies
4. **Code Quality Assessment**: Calculate complexity metrics and identify potential refactoring opportunities
5. **API Documentation**: Automatically generate API documentation from TypeScript interfaces and function signatures
6. **Code Transformation**: Enable automated refactoring and code modernization
7. **Type Safety Analysis**: Analyze type usage and identify potential type safety issues

### Best Practices and Considerations

- **Choose the right parser**: @babel/parser for modern JavaScript/TypeScript, TypeScript Compiler API for native TypeScript analysis
- **Handle errors gracefully**: Implement error recovery for malformed code
- **Use caching**: Cache parsed ASTs for performance in large codebases
- **Extract comprehensive metadata**: Go beyond basic structure to include type information, complexity metrics, and relationships
- **Generate meaningful chunks**: Create documentation chunks that are useful for RAG systems with proper metadata and user role targeting
- **Consider performance**: Use incremental parsing and lazy evaluation for large files

**Best for**: Comprehensive JavaScript/TypeScript code analysis for RAG systems, requiring modern syntax support, type information extraction, and production-ready error handling.