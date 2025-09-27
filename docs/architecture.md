# Minimal Shadcn Components MCP RAG Architecture Document

## Introduction

This document outlines the overall project architecture for the Minimal Shadcn Components MCP RAG service, including backend systems, shared services, and core components. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:**
This is a headless MCP service with no user interface. All user interaction happens through AI assistants using the MCP protocol. The architecture focuses solely on the backend service components and data processing pipeline.

## Starter Template or Existing Project

This is a greenfield project with no existing codebase or starter template. The architecture will be built from scratch following Node.js/TypeScript best practices for minimal, efficient services.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Protocol  │    │  MCP RAG Service  │
│   (Claude etc.) │◄──►│    Connection   │◄──►│    (Node.js)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              │                         │                         │
                              ▼                         ▼                         ▼
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │ Registry Parser │    │  Vector Store   │    │   MCP Tools     │
                    │   Component     │    │   (ChromaDB)    │    │   Interface     │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │                         │
                              └─────────────────────────┼─────────────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Shadcn Registry │
                                              │   Files (Local) │
                                              └─────────────────┘
```

### Core Components

1. **MCP Server**: Protocol handling and tool execution
2. **Registry Parser**: Extracts and processes shadcn registry data
3. **Vector Store**: Semantic search capabilities using ChromaDB
4. **Tool Interface**: Implements the 4 core MCP tools
5. **Configuration Manager**: Handles settings and file paths

## Technology Stack

### Backend Technologies
- **Runtime**: Node.js 18+ with TypeScript 5+
- **MCP Protocol**: `@modelcontextprotocol/sdk` (official SDK)
- **Vector Database**: ChromaDB with JavaScript client
- **File Processing**: Built-in Node.js `fs` and `path` modules
- **Type Checking**: TypeScript compiler
- **Package Management**: npm

### Development Tools
- **Build Tool**: `tsc` (TypeScript compiler) or `esbuild`
- **Linting**: ESLint with TypeScript support
- **Format**: Prettier (optional)
- **Execution**: Node.js directly

### Dependencies (Minimal Set)
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "chromadb": "^1.0.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

## Data Architecture

### Data Sources
- **Primary**: `/Users/tbardale/github/shadcn-ui/apps/v4/registry/` files
- **Secondary**: Registry documentation files in parent directory
- **Format**: TypeScript registry files with structured component data

### Data Flow
```
Registry Files → Parser → JSON Index → Vector Embeddings → Vector Store
     ↓
MCP Tool Request → Vector Search → Result Retrieval → AI Assistant
```

### Data Models

#### Component Interface
```typescript
interface ShadcnComponent {
  name: string;
  type: 'ui' | 'hook' | 'block';
  description: string;
  dependencies: string[];
  registryDependencies: string[];
  files: RegistryFile[];
  tailwind?: TailwindConfig;
  category?: string;
  whenToUse?: string[];
  whenNotToUse?: string[];
  codeExample?: string;
  installCommand: string;
  fileLocation: string;
}

interface RegistryFile {
  path: string;
  type: string;
  content?: string;
}
```

#### Search Result Interface
```typescript
interface SearchResult {
  component: ShadcnComponent;
  relevanceScore: number;
  matchedFields: string[];
}
```

## System Architecture

### Component Design

#### 1. MCP Server Component
```typescript
class McpShadcnServer {
  private mcpServer: MCPServer;
  private vectorStore: VectorStore;
  private registry: RegistryManager;

  constructor(config: ServerConfig) {
    this.mcpServer = new MCPServer(config);
    this.vectorStore = new ChromaVectorStore(config.chromaConfig);
    this.registry = new RegistryManager(config.registryPath);
  }

  async start(): Promise<void> {
    await this.registry.initialize();
    await this.vectorStore.initialize();
    this.registerTools();
    await this.mcpServer.start();
  }

  private registerTools(): void {
    this.mcpServer.registerTool('find_shadcn_component', this.findComponent.bind(this));
    this.mcpServer.registerTool('get_shadcn_component_details', this.getComponentDetails.bind(this));
    this.mcpServer.registerTool('list_shadcn_components', this.listComponents.bind(this));
    this.mcpServer.registerTool('get_component_installation', this.getInstallationInfo.bind(this));
  }
}
```

#### 2. Registry Parser Component
```typescript
class RegistryManager {
  private components: Map<string, ShadcnComponent> = new Map();
  private indexPath: string;

  constructor(private registryPath: string) {
    this.indexPath = path.join(registryPath, '../');
  }

  async initialize(): Promise<void> {
    await this.parseUiComponents();
    await this.parseBlocks();
    await this.parseHooks();
    await this.enrichWithDocumentation();
  }

  private async parseUiComponents(): Promise<void> {
    const uiPath = path.join(this.registryPath, 'registry-ui.ts');
    const content = await fs.readFile(uiPath, 'utf-8');
    const uiComponents = this.parseRegistryFile(content);

    uiComponents.forEach(component => {
      this.components.set(component.name, {
        ...component,
        type: 'ui',
        installCommand: `npx shadcn add ${component.name}`,
        fileLocation: `ui/${component.name}.tsx`
      });
    });
  }

  private parseRegistryFile(content: string): RegistryItem[] {
    // Extract TypeScript array from registry file
    const match = content.match(/export\s+(?:const|let|var)\s+\w+:\s*Registry\["items"\]\s*=\s*(\[.*?\]);/s);
    if (!match) throw new Error('Invalid registry file format');

    try {
      return eval(`(${match[1]})`);
    } catch (error) {
      throw new Error(`Failed to parse registry: ${error}`);
    }
  }
}
```

#### 3. Vector Store Component
```typescript
class ChromaVectorStore implements VectorStore {
  private client: ChromaClient;
  private collection: Collection;

  constructor(config: ChromaConfig) {
    this.client = new ChromaClient({
      path: config.path || 'http://localhost:8000'
    });
  }

  async initialize(): Promise<void> {
    this.collection = await this.client.getOrCreateCollection({
      name: 'shadcn-components',
      metadata: { description: 'Shadcn components for semantic search' }
    });
  }

  async indexComponents(components: ShadcnComponent[]): Promise<void> {
    const documents = components.map(comp => ({
      id: comp.name,
      text: this.createSearchText(comp),
      metadata: {
        name: comp.name,
        type: comp.type,
        category: comp.category,
        dependencies: JSON.stringify(comp.dependencies),
        registryDependencies: JSON.stringify(comp.registryDependencies)
      }
    }));

    await this.collection.add({
      documents: documents.map(d => d.text),
      ids: documents.map(d => d.id),
      metadatas: documents.map(d => d.metadata)
    });
  }

  async search(query: string, limit: number = 10): Promise<SearchResult[]> {
    const results = await this.collection.query({
      queryTexts: [query],
      nResults: limit
    });

    return results.ids[0].map((id, index) => ({
      component: this.components.get(id)!,
      relevanceScore: results.distances[0][index],
      matchedFields: ['description', 'name']
    }));
  }

  private createSearchText(component: ShadcnComponent): string {
    return `
${component.name}: ${component.description}
Type: ${component.type}
Category: ${component.category || 'general'}
Dependencies: ${component.dependencies.join(', ')}
When to use: ${component.whenToUse?.join(', ') || 'general purpose'}
Code example: ${component.codeExample || 'none provided'}
    `.trim();
  }
}
```

#### 4. MCP Tools Implementation
```typescript
class McpTools {
  constructor(
    private registry: RegistryManager,
    private vectorStore: VectorStore
  ) {}

  async findComponent(query: string): Promise<ToolResponse> {
    const results = await this.vectorStore.search(query, 5);

    return {
      success: true,
      data: results.map(result => ({
        name: result.component.name,
        type: result.component.type,
        description: result.component.description,
        relevanceScore: result.relevanceScore,
        installCommand: result.component.installCommand
      }))
    };
  }

  async getComponentDetails(name: string): Promise<ToolResponse> {
    const component = this.registry.getComponent(name);
    if (!component) {
      return {
        success: false,
        error: `Component '${name}' not found`
      };
    }

    return {
      success: true,
      data: {
        name: component.name,
        type: component.type,
        description: component.description,
        dependencies: component.dependencies,
        registryDependencies: component.registryDependencies,
        files: component.files,
        whenToUse: component.whenToUse,
        whenNotToUse: component.whenNotToUse,
        codeExample: component.codeExample,
        installCommand: component.installCommand,
        fileLocation: component.fileLocation
      }
    };
  }

  async listComponents(category?: string): Promise<ToolResponse> {
    const components = this.registry.getComponents(category);

    return {
      success: true,
      data: components.map(comp => ({
        name: comp.name,
        type: comp.type,
        category: comp.category,
        description: comp.description,
        installCommand: comp.installCommand
      }))
    };
  }

  async getInstallationInfo(name: string): Promise<ToolResponse> {
    const component = this.registry.getComponent(name);
    if (!component) {
      return {
        success: false,
        error: `Component '${name}' not found`
      };
    }

    return {
      success: true,
      data: {
        command: component.installCommand,
        dependencies: component.dependencies,
        registryDependencies: component.registryDependencies,
        setupNotes: this.generateSetupNotes(component)
      }
    };
  }

  private generateSetupNotes(component: ShadcnComponent): string {
    const notes = [];

    if (component.dependencies.some(dep => dep.includes('day-picker'))) {
      notes.push('Requires date-fns for date utilities');
    }

    if (component.dependencies.some(dep => dep.includes('radix'))) {
      notes.push('Uses Radix UI primitives for accessibility');
    }

    if (component.registryDependencies.length > 0) {
      notes.push(`Requires additional shadcn components: ${component.registryDependencies.join(', ')}`);
    }

    return notes.join('. ') || 'No special setup requirements';
  }
}
```

## Configuration Architecture

### Configuration Structure
```typescript
interface ServerConfig {
  server: {
    port: number;
    host: string;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
  registry: {
    path: string;
    watchForChanges: boolean;
  };
  chroma: {
    path?: string;
    collectionName: string;
    embeddingModel: string;
  };
  search: {
    defaultLimit: number;
    maxResults: number;
    minRelevanceScore: number;
  };
}
```

### Configuration File (config.json)
```json
{
  "server": {
    "port": 3000,
    "host": "localhost",
    "logLevel": "info"
  },
  "registry": {
    "path": "/Users/tbardale/github/shadcn-ui/apps/v4/registry",
    "watchForChanges": false
  },
  "chroma": {
    "collectionName": "shadcn-components",
    "embeddingModel": "default"
  },
  "search": {
    "defaultLimit": 5,
    "maxResults": 20,
    "minRelevanceScore": 0.1
  }
}
```

## Performance Architecture

### Memory Optimization
- **Lazy Loading**: Components loaded on demand
- **Stream Processing**: Registry files processed in chunks
- **Memory Pooling**: Reuse objects and buffers
- **Cache Strategy**: LRU cache for frequent searches

### Response Time Optimization
- **Pre-indexing**: All components indexed at startup
- **Connection Pooling**: Reuse database connections
- **Parallel Processing**: Multiple components processed simultaneously
- **Result Caching**: Cache common query results

### Startup Time Optimization
- **Incremental Indexing**: Only index new/changed components
- **Configuration Validation**: Early validation fail-fast
- **Dependency Injection**: Fast component initialization
- **Background Processing**: Non-blocking startup operations

## Error Handling Architecture

### Error Types
```typescript
enum ErrorType {
  REGISTRY_PARSE_ERROR = 'REGISTRY_PARSE_ERROR',
  VECTOR_STORE_ERROR = 'VECTOR_STORE_ERROR',
  MCP_PROTOCOL_ERROR = 'MCP_PROTOCOL_ERROR',
  CONFIGURATION_ERROR = 'CONFIGURATION_ERROR',
  COMPONENT_NOT_FOUND = 'COMPONENT_NOT_FOUND'
}

interface ServiceError {
  type: ErrorType;
  message: string;
  details?: any;
  timestamp: Date;
}
```

### Error Handling Strategy
- **Graceful Degradation**: Fallback to text search if vector search fails
- **Retry Logic**: Automatic retry for transient failures
- **Circuit Breaker**: Prevent cascade failures
- **Error Boundaries**: Isolate component failures

## Security Architecture

### Security Considerations
- **Local Only**: No external network access
- **File System Access**: Limited to registry directory
- **No Authentication**: Single-user personal tool
- **Input Validation**: Validate all MCP tool inputs
- **Path Sanitization**: Prevent directory traversal attacks

### Security Measures
- **File Access Control**: Restrict to configured registry path
- **Input Sanitization**: Clean all user inputs
- **Error Message Filtering**: No sensitive information in errors
- **Resource Limits**: Prevent memory exhaustion attacks

## Development Workflow

### Project Structure
```
shadcn-mcp-rag/
├── src/
│   ├── components/
│   │   ├── mcp-server.ts
│   │   ├── registry-manager.ts
│   │   ├── vector-store.ts
│   │   └── mcp-tools.ts
│   ├── types/
│   │   ├── component.ts
│   │   ├── config.ts
│   │   └── errors.ts
│   ├── utils/
│   │   ├── parser.ts
│   │   ├── search.ts
│   │   └── validation.ts
│   ├── config.ts
│   └── index.ts
├── config.json
├── package.json
├── tsconfig.json
└── README.md
```

### Build Process
1. **TypeScript Compilation**: Compile to JavaScript
2. **Dependency Bundling**: Optional for distribution
3. **Configuration Validation**: Verify config on startup
4. **Registry Indexing**: Process registry files

### Development Commands
```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "shadcn-rag": "node dist/index.js",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  }
}
```

## Monitoring and Observability

### Logging Strategy
- **Structured Logging**: JSON format for machine readability
- **Log Levels**: Debug, Info, Warn, Error
- **Request Tracing**: Correlation IDs for MCP requests
- **Performance Metrics**: Response times and memory usage

### Health Checks
- **Server Status**: MCP server availability
- **Registry Access**: File system readability
- **Vector Store**: ChromaDB connectivity
- **Memory Usage**: Current and peak memory consumption

## Deployment Architecture

### Local Deployment
- **Process Management**: Node.js process directly
- **Configuration**: Local config file
- **Data Storage**: Local ChromaDB instance
- **Registry Access**: Local file system

### Startup Sequence
1. Load configuration
2. Initialize logging
3. Connect to vector store
4. Parse registry files
5. Index components
6. Start MCP server
7. Accept connections

## Scaling Considerations

### Vertical Scaling
- **Memory**: Increase available RAM for larger registries
- **CPU**: Faster processors for quicker indexing
- **Storage**: SSD for faster file access

### Horizontal Scaling
- **Not Required**: Single-user personal tool
- **Future Consideration**: Multiple users could use separate instances

## Future Extensibility

### Plugin Architecture
- **Registry Parsers**: Support for different registry formats
- **Vector Stores**: Alternative vector databases
- **Embedding Models**: Multiple embedding options
- **MCP Tools**: Additional tools and capabilities

### Integration Points
- **Additional Registries**: Support for other component libraries
- **AI Assistants**: Multiple AI assistant platforms
- **Documentation Sources**: Additional documentation formats
- **Build Systems**: Integration with build tools

## Risk Assessment

### Technical Risks
- **Registry Format Changes**: shadcn registry structure may change
- **MCP Protocol Evolution**: Protocol may require updates
- **ChromaDB Compatibility**: Version compatibility issues
- **Performance**: May not scale to very large registries

### Mitigation Strategies
- **Flexible Parsing**: Adaptable registry parsing logic
- **Protocol Abstraction**: Layer to handle protocol changes
- **Version Pinning**: Lock dependency versions
- **Performance Testing**: Regular performance monitoring

## Success Criteria Verification

### Performance Metrics
- **Startup Time**: < 10 seconds (measured with time command)
- **Response Time**: < 1 second (measured with tool execution timing)
- **Memory Usage**: < 100MB (measured with process.memoryUsage())
- **Indexing Time**: < 30 seconds (measured during startup)

### Functional Metrics
- **Components Indexed**: 47 UI + 54 blocks + 1 hook = 102 total
- **Tools Available**: 4 MCP tools functional
- **Search Accuracy**: Relevant results for test queries
- **Installation Commands**: Valid commands from registry data

### Integration Metrics
- **MCP Connection**: Successful connection to AI assistant
- **Tool Execution**: All tools execute without errors
- **Response Format**: Proper JSON responses for all tools
- **Error Handling**: Graceful error handling for edge cases

This architecture provides a solid foundation for building the minimal shadcn MCP RAG service while maintaining simplicity and meeting all requirements for personal use.