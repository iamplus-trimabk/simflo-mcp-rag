# SimFlo MCP RAG - React JS User Guide

This guide provides step-by-step instructions for setting up and using the SimFlo MCP RAG system with React JS applications.

## Quick Start

### 1. Start the Server

First, navigate to your SimFlo MCP RAG project directory and start the services:

```bash
# Navigate to project directory
cd /Users/tbardale/v2/simflo-mcp-rag

# Start the Python API server (runs in background)
cd data-pipeline
python3 api_server.py --host 127.0.0.1 --port 8000 &
cd ..

# Verify the server is running
curl -s http://127.0.0.1:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T04:00:00.000Z",
  "database": "connected",
  "vector_store": "ready"
}
```

### 2. Add to Claude Desktop

**Manual MCP Configuration:**

1. Open Claude Desktop app
2. Go to Settings → Developer → Edit MCP Servers
3. Add the following configuration to your MCP settings:

```json
{
  "mcpServers": {
    "simflo-rag": {
      "command": "node",
      "args": ["/Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js"],
      "env": {
        "API_BASE_URL": "http://127.0.0.1:8000",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

4. Save the configuration and restart Claude Desktop

**Add to Cursor:**

1. Open Cursor
2. Go to Settings → Extensions → MCP
3. Add the same configuration as above
4. Restart Cursor

### 3. Verify MCP Connection

**List Available Tools:**

Ask Claude: "List all available MCP tools"

Expected response:
```
Available MCP Tools:
1. search_components - Search for components using natural language
2. get_component_details - Get detailed information about a specific component
3. get_component_installation - Get installation instructions and dependencies
4. list_components - List components by type or category
```

**Set Context:**

Tell Claude: "I'm working on a React JS project using Tailwind CSS. I need help finding and implementing UI components."

### 4. Test Component Documentation Retrieval

**Test Input Component:**

**Prompt:** "Using the MCP tools, search for input components and show me exactly what the MCP system returns for form input components."

**Expected MCP Response Structure:**
```json
{
  "components": [
    {
      "name": "input",
      "description": "Form input component with various input types and validation",
      "platform": ["reactjs"],
      "files": [
        {
          "path": "components/ui/input.tsx",
          "content": "import React, { useState } from 'react';\nimport { cn } from '@/lib/utils';\n\ninterface InputProps {\n  type?: 'text' | 'email' | 'password' | 'number';\n  placeholder?: string;\n  value?: string;\n  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;\n  className?: string;\n  error?: boolean;\n}\n\nexport const Input: React.FC<InputProps> = ({\n  type = 'text',\n  placeholder,\n  value,\n  onChange,\n  className,\n  error = false\n}) => {\n  return (\n    <input\n      type={type}\n      placeholder={placeholder}\n      value={value}\n      onChange={onChange}\n      className={cn(\n        'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',\n        error && 'border-red-500 focus-visible:ring-red-500',\n        className\n      )}\n    />\n  );\n};",
          "language": "tsx",
          "component_type": "component",
          "props_info": {
            "props": [
              {
                "name": "type",
                "type": "string",
                "default": "'text'",
                "description": "Input type (text, email, password, number)"
              },
              {
                "name": "placeholder",
                "type": "string",
                "description": "Placeholder text"
              },
              {
                "name": "value",
                "type": "string",
                "description": "Input value"
              },
              {
                "name": "onChange",
                "type": "function",
                "description": "Change handler function"
              },
              {
                "name": "className",
                "type": "string",
                "description": "Additional CSS classes"
              },
              {
                "name": "error",
                "type": "boolean",
                "default": "false",
                "description": "Error state styling"
              }
            ],
            "interface_name": "InputProps",
            "has_children": false,
            "is_functional": true
          }
        }
      ],
      "dependencies": ["@/lib/utils"],
      "installation": "npm install @/lib/utils",
      "usage_examples": [
        "<Input type=\"email\" placeholder=\"Enter your email\" />",
        "<Input type=\"password\" placeholder=\"Enter password\" error={true} />"
      ]
    }
  ]
}
```

**Test Form Component:**

**Prompt:** "Search for form components using MCP and show me the exact response structure for form validation components."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "form",
      "description": "Form component with validation and submission handling",
      "platform": ["reactjs"],
      "features": ["validation", "submission", "error handling"],
      "props_info": {
        "props": [
          {
            "name": "onSubmit",
            "type": "function",
            "required": true,
            "description": "Form submission handler"
          },
          {
            "name": "validation",
            "type": "object",
            "description": "Validation rules object"
          }
        ]
      },
      "usage_examples": [
        "<Form onSubmit={handleSubmit} validation={validationRules}>",
        "  <Input name=\"email\" type=\"email\" required />",
        "  <Button type=\"submit\">Submit</Button>",
        "</Form>"
      ]
    }
  ]
}
```

**Test Table Component:**

**Prompt:** "Find table components for React JS and show me the exact MCP response for data table components."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "table",
      "description": "Responsive data table component with sorting and filtering",
      "platform": ["reactjs"],
      "features": ["responsive", "sorting", "filtering", "pagination"],
      "props_info": {
        "props": [
          {
            "name": "data",
            "type": "array",
            "required": true,
            "description": "Table data array"
          },
          {
            "name": "columns",
            "type": "array",
            "required": true,
            "description": "Column definitions"
          },
          {
            "name": "sortable",
            "type": "boolean",
            "default": "false",
            "description": "Enable column sorting"
          }
        ]
      },
      "usage_examples": [
        "<Table data={tableData} columns={columns} sortable={true} />"
      ]
    }
  ]
}
```

**Test Navigation Bar Component:**

**Prompt:** "Search for navigation bar components using MCP and show me the exact response structure."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "navbar",
      "description": "Responsive navigation bar with mobile menu support",
      "platform": ["reactjs"],
      "features": ["responsive", "mobile menu", "dropdown"],
      "props_info": {
        "props": [
          {
            "name": "items",
            "type": "array",
            "required": true,
            "description": "Navigation items array"
          },
          {
            "name": "logo",
            "type": "string",
            "description": "Logo URL or component"
          },
          {
            "name": "variant",
            "type": "string",
            "default": "'default'",
            "description": "Visual variant (default, transparent, solid)"
          }
        ]
      },
      "usage_examples": [
        "<Navbar items={navItems} logo=\"/logo.png\" variant=\"solid\" />"
      ]
    }
  ]
}
```

**Test Date Picker Component:**

**Prompt:** "Find date picker components using MCP tools and show me the exact response for date selection components."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "datepicker",
      "description": "Date picker component with range selection and validation",
      "platform": ["reactjs"],
      "features": ["range selection", "validation", "localization"],
      "props_info": {
        "props": [
          {
            "name": "value",
            "type": "Date",
            "description": "Selected date value"
          },
          {
            "name": "onChange",
            "type": "function",
            "required": true,
            "description": "Date change handler"
          },
          {
            "name": "minDate",
            "type": "Date",
            "description": "Minimum selectable date"
          },
          {
            "name": "maxDate",
            "type": "Date",
            "description": "Maximum selectable date"
          }
        ]
      },
      "dependencies": ["date-fns"],
      "installation": "npm install date-fns",
      "usage_examples": [
        "<DatePicker value={selectedDate} onChange={setDate} minDate={new Date()} />"
      ]
    }
  ]
}
```

## Daily Usage

### Starting the System

1. **Start API Server:**
```bash
cd /Users/tbardale/v2/simflo-mcp-rag/data-pipeline
python3 api_server.py --host 127.0.0.1 --port 8000
```

2. **Verify MCP Connection:**
   - Open Claude/Cursor
   - Ask: "List available MCP tools"

### Common Workflows

**Search for Components:**
- "Find me button components for React JS"
- "Search for modal dialog components"
- "Show me form validation components"

**Get Component Details:**
- "Tell me about the input component"
- "What dependencies does the date picker need?"
- "Show me the table component props"

**Installation Help:**
- "How do I install the navbar component?"
- "What are the dependencies for the form component?"

## Troubleshooting

### Server Issues

**Server Won't Start:**
```bash
# Check port 8000 is available
lsof -i :8000

# Kill any existing processes
kill -9 <PID>

# Restart server
python3 api_server.py --host 127.0.0.1 --port 8000
```

**MCP Connection Issues:**
1. Verify server is running: `curl http://127.0.0.1:8000/health`
2. Check MCP configuration paths are correct
3. Restart Claude/Cursor after configuration changes

### Component Issues

**Empty Results:**
```bash
# Check vector store
python3 rag_cli.py stats

# Re-index if needed
python3 vector_store.py --stats
```

**Incorrect Components:**
- Verify context: "I'm working on React JS project"
- Be specific: "React JS form components" not just "form components"

## Advanced Usage

### Custom Searches

**By Platform:**
- "React JS table components"
- "React JS navigation components"

**By Feature:**
- "Components with validation"
- "Responsive table components"

**By Library:**
- "Gluestack UI button components"
- "Shadcn form components"

### Batch Operations

**List All Components:**
- "List all available React JS components"
- "Show me form components only"

**Compare Components:**
- "Compare input and textarea components"
- "Show differences between modal and dialog components"

## Performance Tips

1. **Keep Server Running:** Start server once per development session
2. **Use Specific Queries:** Be specific about platform and features
3. **Cache Responses:** Component details don't change frequently
4. **Batch Requests:** Ask for multiple components at once

## Integration Examples

### React + TypeScript Project

```typescript
import { useState } from 'react';
import { Input, Button, Form } from './components';

// Ask MCP: "Show me form component implementation"
// Use the returned code structure
const MyForm = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Form submission logic
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Button type="submit">Submit</Button>
    </Form>
  );
};
```

This guide provides everything needed to effectively use the SimFlo MCP RAG system with React JS projects. The MCP tools will provide exact component implementations, dependencies, and usage examples based on your specific project requirements.