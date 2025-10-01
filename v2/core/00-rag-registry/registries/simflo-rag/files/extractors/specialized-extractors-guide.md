# Specialized Extractors Guide

## Purpose
Comprehensive guide to the 11 specialized extractors in SimFlo RAG v2, each designed for specific content types and source formats. This guide covers implementation details, usage patterns, and integration workflows.

## Extractor Classification

### Component Library Extractors

#### 1. shadcn_extractor.py
**Purpose**: Extract shadcn/ui components from registry files using GitHub CLI

**Key Features**:
- **Registry File Parsing**: Parse `apps/www/registry/registry-ui.ts` files
- **Component Metadata**: Extract component descriptions, dependencies, usage patterns
- **Hook Extraction**: Extract custom React hooks from source code
- **Block Components**: Extract pre-built UI sections and layouts
- **Variant Support**: Extract component variants and styling options

**Source Requirements**:
- **Repository**: `shadcn-ui/ui`
- **Registry File**: `apps/www/registry/registry-ui.ts`
- **Component Files**: Individual component `.tsx` files in `apps/www/registry/ui/`
- **Dependencies**: React, Radix UI primitives, Tailwind CSS

**Extraction Process**:
1. **Repository Cloning**: Use GitHub CLI to clone repository
2. **Registry Parsing**: Parse registry file for component definitions
3. **Component Analysis**: Extract individual component files and metadata
4. **Hook Discovery**: Identify custom hooks in source files
5. **Block Identification**: Extract composite UI blocks
6. **Metadata Generation**: Create comprehensive metadata for each component

**Output Structure**:
```json
{
  "metadata": {
    "extractor": "shadcn",
    "source_repository": "shadcn-ui/ui",
    "extraction_timestamp": "2025-09-30T21:37:01.043963",
    "total_components": 25,
    "total_hooks": 8,
    "total_blocks": 5
  },
  "components": [
    {
      "name": "button",
      "display_name": "Button",
      "description": "Accessible button component with multiple variants",
      "category": "ui",
      "dependencies": ["@radix-ui/react-slot", "class-variance-authority"],
      "install_command": "npx shadcn-ui@latest add button",
      "usage_examples": [
        "import { Button } from \"@/components/ui/button\"",
        "<Button>Click me</Button>",
        "<Button variant=\"destructive\">Delete</Button>"
      ],
      "variants": ["default", "destructive", "outline", "secondary", "ghost", "link"],
      "sizes": ["default", "sm", "lg", "icon"],
      "source_file": "apps/www/registry/ui/button.tsx",
      "api_reference": {
        "props": [
          {
            "name": "variant",
            "type": "\"default\" | \"destructive\" | \"outline\" | \"secondary\" | \"ghost\" | \"link\"",
            "default": "\"default\"",
            "description": "The visual style variant of the button"
          },
          {
            "name": "size",
            "type": "\"default\" | \"sm\" | \"lg\" | \"icon\"",
            "default": "\"default\"",
            "description": "The size of the button"
          },
          {
            "name": "asChild",
            "type": "boolean",
            "default": "false",
            "description": "Whether to render as a child element"
          }
        ]
      },
      "accessibility_features": [
        "Keyboard navigation support",
        "Screen reader compatibility",
        "Focus management",
        "ARIA attributes"
      ],
      "styling": {
        "css_framework": "Tailwind CSS",
        "css_variables": true,
        "theming": "CSS custom properties",
        "responsive": true
      }
    }
  ],
  "hooks": [
    {
      "name": "use-toast",
      "display_name": "useToast",
      "description": "Hook to manage toast notifications with dismissible and persistent options",
      "category": "hooks",
      "dependencies": ["react"],
      "usage_examples": [
        "const { toast } = useToast()",
        "toast({ title: \"Success\", description: \"Changes saved\" })",
        "toast({ title: \"Error\", description: \"Something went wrong\", variant: \"destructive\" })"
      ],
      "source_file": "apps/www/registry/ui/use-toast.ts",
      "return_type": {
        "toast": "function",
        "dismiss": "function"
      },
      "parameters": [
        {
          "name": "title",
          "type": "string",
          "required": true,
          "description": "Toast title"
        },
        {
          "name": "description",
          "type": "string",
          "required": false,
          "description": "Toast description"
        },
        {
          "name": "variant",
          "type": "\"default\" | \"destructive\"",
          "default": "\"default\"",
          "description": "Toast variant"
        }
      ]
    }
  ],
  "blocks": [
    {
      "name": "sidebar",
      "display_name": "Sidebar",
      "description": "Responsive sidebar layout with collapsible navigation",
      "category": "blocks",
      "components_used": ["button", "sheet", "scroll-area", "separator"],
      "dependencies": ["@radix-ui/react-sheet"],
      "usage_examples": [
        "import { Sidebar } from \"@/components/ui/sidebar\"",
        "<Sidebar />",
        "<Sidebar collapsible=\"icon\" />"
      ],
      "source_file": "apps/www/registry/ui/sidebar.tsx",
      "responsive": true,
      "accessibility": [
        "Keyboard navigation",
        "Screen reader support",
        "Focus management"
      ],
      "customization": {
        "collapsible": true,
        "variant": ["sidebar", "floating"],
        "width": "adjustable"
      }
    }
  ]
}
```

**Usage Examples**:
```bash
# Extract from main shadcn repository
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/

# Extract from local shadcn fork with custom registry
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type local --source-path ~/projects/shadcn-fork --output-dir extracted/shadcn-local/

# Extract specific version
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --branch v1.0.0 --output-dir extracted/shadcn-v1/
```

#### 2. gluestack_extractor.py
**Purpose**: Extract gluestack components from monorepo structure using GitHub CLI

**Key Features**:
- **Monorepo Navigation**: Navigate complex package structures
- **Cross-Platform Support**: Extract both React and React Native components
- **Theme Integration**: Extract theme and styling information
- **Variant System**: Extract component variants and configurations
- **Platform-Specific Logic**: Handle platform differences in components

**Source Requirements**:
- **Repository**: `gluestack/gluestack-ui-` (various packages)
- **Package Structure**: `packages/gluestack-core/src/`
- **Component Files**: Platform-specific component implementations
- **Dependencies**: React, React Native, CSS-in-JS libraries

**Extraction Process**:
1. **Repository Discovery**: Identify gluestack repositories and packages
2. **Monorepo Navigation**: Navigate complex directory structures
3. **Platform Analysis**: Identify React vs React Native implementations
4. **Component Extraction**: Extract component code and metadata
5. **Theme Processing**: Extract theme configurations and styling
6. **Variant Discovery**: Identify component variants and configurations

**Output Structure**:
```json
{
  "metadata": {
    "extractor": "gluestack",
    "source_repository": "gluestack/gluestack-ui-react",
    "extraction_timestamp": "2025-09-30T21:37:01.043963",
    "total_components": 30,
    "platforms": ["reactjs", "react-native"],
    "theme_system": "gluestack-style"
  },
  "components": [
    {
      "name": "Button",
      "display_name": "Button",
      "description": "Cross-platform button component with extensive theming support",
      "category": "ui",
      "platforms": ["reactjs", "react-native"],
      "dependencies": ["@gluestack-ui/button", "@gluestack-ui/theme"],
      "usage_examples": [
        "import { Button } from \"@gluestack-ui/react\"",
        "<Button>Click me</Button>",
        "<Button variant=\"outline\" size=\"lg\">Large Button</Button>"
      ],
      "variants": {
        "solid": "Filled button with background color",
        "outline": "Button with border only",
        "ghost": "Button with no background or border",
        "link": "Link-styled button"
      },
      "sizes": ["xs", "sm", "md", "lg", "xl"],
      "source_files": {
        "reactjs": "packages/gluestack-core/src/button/Button.tsx",
        "react-native": "packages/gluestack-core/src/button/ButtonNative.tsx"
      },
      "styling": {
        "css_framework": "gluestack-style",
        "themeable": true,
        "custom_properties": true,
        "responsive": true
      },
      "accessibility": {
        "keyboard_navigation": true,
        "screen_reader": true,
        "focus_management": true,
        "aria_attributes": true
      },
      "platform_specific_features": {
        "reactjs": {
          "hover_states": true,
          "focus_ring": true,
          "transitions": true
        },
        "react-native": {
          "pressable": true,
          "ripple_effect": true,
          "native_feedback": true
        }
      }
    }
  ],
  "hooks": [
    {
      "name": "useTheme",
      "display_name": "useTheme",
      "description": "Hook for accessing and managing theme configuration across platforms",
      "category": "hooks",
      "platforms": ["reactjs", "react-native"],
      "dependencies": ["@gluestack-ui/theme"],
      "usage_examples": [
        "import { useTheme } from \"@gluestack-ui/react\"",
        "const theme = useTheme()",
        "const colors = theme.colors",
        "const spacing = theme.spacing"
      ],
      "source_files": {
        "reactjs": "packages/gluestack-core/src/theme/useTheme.ts",
        "react-native": "packages/gluestack-core/src/theme/useThemeNative.ts"
      },
      "return_type": {
        "colors": "object",
        "spacing": "object",
        "typography": "object",
        "breakpoints": "object"
      }
    }
  ]
}
```

### Content Type Extractors

#### 3. component_extractor.py
**Purpose**: Generic component extraction from structured sources

**Key Features**:
- **Framework-Agnostic**: Works with React, Vue, Angular components
- **Pattern Recognition**: Identify component patterns and structures
- **Dependency Analysis**: Extract component dependencies and imports
- **Prop Extraction**: Identify component props and interfaces
- **Usage Pattern Analysis**: Analyze common usage patterns

**Supported Frameworks**:
- React (.jsx, .tsx)
- Vue (.vue)
- Angular (.component.ts, .component.html)
- Svelte (.svelte)
- Custom component formats

**Extraction Process**:
1. **File Discovery**: Scan for component files using patterns
2. **Framework Detection**: Identify component framework
3. **Structure Analysis**: Parse component structure and exports
4. **Dependency Extraction**: Extract import statements and dependencies
5. **Interface Analysis**: Extract prop interfaces and types
6. **Usage Pattern**: Analyze common usage patterns

**Output Structure**:
```json
{
  "components": [
    {
      "name": "CustomCard",
      "framework": "react",
      "file_type": "tsx",
      "description": "Custom card component with title, content, and actions",
      "dependencies": ["react", "./Button", "./Avatar"],
      "props": [
        {
          "name": "title",
          "type": "string",
          "required": true,
          "description": "Card title"
        },
        {
          "name": "children",
          "type": "ReactNode",
          "required": true,
          "description": "Card content"
        }
      ],
      "usage_examples": [
        "<CustomCard title=\"Hello\">Content here</CustomCard>"
      ]
    }
  ]
}
```

#### 4. hooks_extractor.py
**Purpose**: Extract React hooks from source code

**Key Features**:
- **Hook Pattern Recognition**: Identify custom hooks (`use-*` pattern)
- **Dependency Tracking**: Extract hook dependencies and imports
- **Return Type Analysis**: Analyze hook return types and structures
- **Parameter Extraction**: Extract hook parameters and their types
- **Usage Pattern Discovery**: Identify common hook usage patterns

**Hook Categories**:
- **State Management**: useState, useReducer variations
- **Side Effects**: useEffect, custom effect hooks
- **Context**: useContext, context provider hooks
- **Performance**: useMemo, useCallback optimizations
- **DOM**: DOM manipulation and event handling
- **Data Fetching**: API and data fetching hooks

**Extraction Process**:
1. **Hook Discovery**: Scan for `use-*` function patterns
2. **Signature Analysis**: Extract hook parameters and return types
3. **Dependency Parsing**: Analyze imports and dependencies
4. **Documentation Extraction**: Extract JSDoc and comments
5. **Usage Pattern**: Identify common usage scenarios

**Output Structure**:
```json
{
  "hooks": [
    {
      "name": "useLocalStorage",
      "description": "Hook for managing localStorage state with SSR support",
      "dependencies": ["react"],
      "parameters": [
        {
          "name": "key",
          "type": "string",
          "required": true,
          "description": "localStorage key"
        },
        {
          "name": "initialValue",
          "type": "T",
          "required": true,
          "description": "Initial value"
        }
      ],
      "return_type": "[T, (value: T) => void]",
      "usage_examples": [
        "const [name, setName] = useLocalStorage('name', 'John')"
      ]
    }
  ]
}
```

#### 5. documentation_extractor.py
**Purpose**: Extract and process documentation content

**Key Features**:
- **Markdown Parsing**: Extract structured content from markdown files
- **API Documentation**: Parse API reference documentation
- **Code Example Extraction**: Extract code examples and snippets
- **Tutorial Processing**: Process tutorial and guide content
- **Cross-Reference Linking**: Extract internal and external links

**Supported Documentation Types**:
- API Reference Documentation
- User Guides and Tutorials
- README Files
- CHANGELOG Files
- Contributing Guidelines
- Architectural Documentation

**Extraction Process**:
1. **File Discovery**: Scan for documentation files
2. **Content Parsing**: Parse markdown and structured content
3. **Section Extraction**: Extract headings and sections
4. **Code Example Processing**: Extract and validate code snippets
5. **Link Analysis**: Extract internal and external references
6. **Metadata Generation**: Create searchable metadata

**Output Structure**:
```json
{
  "documentation": [
    {
      "title": "Getting Started",
      "file": "README.md",
      "content_type": "guide",
      "sections": [
        {
          "title": "Installation",
          "level": 2,
          "content": "Install the package using npm...",
          "code_examples": [
            {
              "language": "bash",
              "code": "npm install package-name"
            }
          ]
        }
      ],
      "internal_links": ["#usage", "#api-reference"],
      "external_links": ["https://example.com/docs"]
    }
  ]
}
```

### Platform-Specific Extractors

#### 6. react_extractor.py
**Purpose**: React-specific component and pattern extraction

**Key Features**:
- **JSX/TSX Parsing**: Parse React component syntax
- **Props Interface Extraction**: Extract TypeScript prop interfaces
- **Hook Usage Analysis**: Analyze hook usage patterns
- **Component Lifecycle**: Identify lifecycle patterns
- **State Management**: Extract state management patterns

#### 7. react_native_extractor.py
**Purpose**: React Native component extraction

**Key Features**:
- **Native Component Recognition**: Identify React Native specific components
- **Platform-Specific Props**: Extract platform-specific prop handling
- **Styling Extraction**: Extract StyleSheet and styling patterns
- **Native Module Integration**: Identify native module usage

#### 8. vue_extractor.py
**Purpose**: Vue.js component extraction

**Key Features**:
- **Single File Components**: Parse .vue file structure
- **Template Extraction**: Extract template syntax and structure
- **Script Analysis**: Extract script logic and composition API usage
- **Style Extraction**: Extract scoped styles and CSS

#### 9. angular_extractor.py
**Purpose**: Angular component extraction

**Key Features**:
- **Component Decorators**: Parse @Component decorators
- **Template Analysis**: Extract Angular template syntax
- **Service Integration**: Identify service dependencies
- **Module Structure**: Extract NgModule information

### Utility Extractors

#### 10. markdown_extractor.py
**Purpose**: Extract content from markdown files

**Key Features**:
- **Structured Parsing**: Parse markdown into structured content
- **Code Block Extraction**: Extract code blocks with language info
- **Front Matter Processing**: Parse YAML front matter
- **Link and Image Extraction**: Extract all links and images

#### 11. json_extractor.py
**Purpose**: Extract structured data from JSON files

**Key Features**:
- **Schema Validation**: Validate JSON structure
- **Nested Object Parsing**: Handle complex nested structures
- **Array Processing**: Process array data efficiently
- **Type Inference**: Infer data types from structure

## Integration Workflows

### Complete Component Library Extraction

```bash
# Step 1: Extract shadcn components
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/

# Step 2: Extract gluestack components
python3 v2/04-extractors/extractors_cli.py run gluestack --source-type github --repository gluestack/gluestack-ui-react --output-dir extracted/gluestack/

# Step 3: Extract generic components from local sources
python3 v2/04-extractors/extractors_cli.py run component_extractor --source-type local --source-path ./components --output-dir extracted/custom/

# Step 4: Extract documentation
python3 v2/04-extractors/extractors_cli.py run documentation_extractor --source-type local --source-path ./docs --output-dir extracted/docs/

# Step 5: Run all extractors in parallel
python3 v2/04-extractors/extractors_cli.py run-all --parallel --output-dir extracted/all/
```

### Content Pipeline Integration

```bash
# Content Collection → Extraction Pipeline
content_discover --query "react component libraries" --source-type github --limit 10 | \
content_fetch --sources - --output-dir $CONTENT_ROOT/github/ | \
extractors_run-all --parallel --output-dir extracted/libraries/

# Specific Repository Extraction
content_discover --query "shadcn-ui components" --source-type github --limit 1 | \
extractors_run shadcn --source-type local --source-path $CONTENT_ROOT/github/shadcn-ui/ui --output-dir extracted/shadcn/

# Custom Component Extraction
content_discover --query "react dashboard components" --source-type github --limit 5 | \
extractors_run component_extractor --source-type local --source-path $CONTENT_ROOT/github/ --output-dir extracted/dashboard-components/
```

### Development Workflow

```bash
# 1. Set up development environment
export CONTENT_ROOT=$HOME/development/content
gh auth login

# 2. Extract components for development
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository my-org/shadcn-custom --output-dir extracted/dev/

# 3. Extract custom components from local project
python3 v2/04-extractors/extractors_cli.py run component_extractor --source-type local --source-path ./src/components --output-dir extracted/local/

# 4. Extract project documentation
python3 v2/04-extractors/extractors_cli.py run documentation_extractor --source-type local --source-path ./docs --output-dir extracted/docs/

# 5. Combine all extractions
python3 v2/04-extractors/extractors_cli.py run-all --category content-types --output-dir extracted/project/
```

## Configuration and Customization

### Extractor Configuration

Each extractor supports configuration through JSON files:

```json
{
  "shadcn": {
    "registry_file_path": "apps/www/registry/registry-ui.ts",
    "component_file_pattern": "apps/www/registry/ui/*.tsx",
    "hook_file_pattern": "apps/www/registry/ui/*.ts",
    "block_file_pattern": "apps/www/registry/ui/*.tsx",
    "supported_variants": ["default", "destructive", "outline", "secondary", "ghost", "link"],
    "extract_usage_examples": true,
    "extract_api_reference": true,
    "extract_accessibility_features": true
  },
  "gluestack": {
    "component_base_path": "packages/gluestack-core/src",
    "platform_patterns": {
      "reactjs": "*.tsx",
      "react-native": "*.native.tsx"
    },
    "theme_file_path": "packages/gluestack-core/theme/index.ts",
    "extract_platform_specific": true,
    "extract_theme_info": true,
    "extract_variants": true
  }
}
```

### Custom Extractor Development

To create a custom extractor:

1. **Create Extractor Class**:
```python
class CustomExtractor(BaseExtractor):
    def __init__(self, config):
        super().__init__(config)
        self.name = "custom"
        self.supported_sources = ["github", "local"]

    def extract(self, source_config):
        # Implementation here
        pass
```

2. **Register Extractor**:
```python
# In extractors_registry.py
from .custom_extractor import CustomExtractor

AVAILABLE_EXTRACTORS = {
    "custom": CustomExtractor,
    # ... other extractors
}
```

3. **Add Configuration**:
```json
{
  "custom": {
    "file_patterns": ["*.custom"],
    "metadata_fields": ["name", "description", "usage"],
    "dependencies": ["dependency1", "dependency2"]
  }
}
```

## Performance and Optimization

### Parallel Processing

Extractors support parallel processing for faster execution:

```bash
# Run all extractors in parallel
python3 v2/04-extractors/extractors_cli.py run-all --parallel --max-workers 8 --output-dir extracted/parallel/

# Run category in parallel
python3 v2/04-extractors/extractors_cli.py run-all --category component-libraries --parallel --output-dir extracted/components/
```

### Caching and Incremental Updates

Extractors support incremental processing:

```bash
# Enable caching
export EXTRACTOR_CACHE_ENABLED=true
export EXTRACTOR_CACHE_DIR=$HOME/.cache/simflo-rag/extractors

# Run with incremental updates
python3 v2/04-extractors/extractors_cli.py run shadcn --incremental --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/
```

### Resource Management

Monitor and optimize resource usage:

```bash
# Check resource usage
python3 v2/04-extractors/extractors_cli.py status --detailed --format table

# Optimize for memory usage
export EXTRACTOR_MEMORY_LIMIT="2GB"
export EXTRACTOR_BATCH_SIZE=50
```

## Error Handling and Troubleshooting

### Common Issues

1. **Repository Access Issues**:
   ```bash
   # Check GitHub CLI authentication
   gh auth status

   # Authenticate if needed
   gh auth login
   ```

2. **Permission Denied**:
   ```bash
   # Check file permissions
   ls -la $CONTENT_ROOT

   # Fix permissions
   chmod -R 755 $CONTENT_ROOT
   ```

3. **Memory Issues**:
   ```bash
   # Reduce batch size
   export EXTRACTOR_BATCH_SIZE=25

   # Enable memory monitoring
   export EXTRACTOR_MEMORY_MONITORING=true
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Enable debug logging
export EXTRACTOR_DEBUG=true
export EXTRACTOR_LOG_LEVEL=DEBUG

# Run with verbose output
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/ --verbose
```

This comprehensive guide to specialized extractors provides the foundation for extracting structured content from diverse sources, enabling powerful content processing and RAG database population in SimFlo RAG v2.