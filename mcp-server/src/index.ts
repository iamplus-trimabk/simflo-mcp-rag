#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import axios from 'axios';

// Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://127.0.0.1:8000';

// Schema definitions
const SearchComponentsSchema = z.object({
  query: z.string().min(1, "Search query is required"),
  limit: z.number().min(1).max(50).optional().default(10),
});

const GetComponentDetailsSchema = z.object({
  name: z.string().min(1, "Component name is required"),
});

const GetComponentInstallationSchema = z.object({
  name: z.string().min(1, "Component name is required"),
});

const ListComponentsSchema = z.object({
  type: z.enum(['ui', 'block', 'hook']).optional(),
  limit: z.number().min(1).max(100).optional().default(20),
});

// API client
class RAGAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async searchComponents(query: string, limit: number = 10) {
    const response = await axios.get(`${this.baseUrl}/api/v1/components/search`, {
      params: { q: query, limit },
    });
    return response.data;
  }

  async getComponentDetails(name: string) {
    const response = await axios.get(`${this.baseUrl}/api/v1/components/${name}`);
    return response.data;
  }

  async getComponentInstallation(name: string) {
    const response = await axios.get(`${this.baseUrl}/api/v1/components/${name}/installation`);
    return response.data;
  }

  async listComponents(type?: string, limit: number = 20) {
    const params: any = { limit };
    if (type) params.type = type;

    const response = await axios.get(`${this.baseUrl}/api/v1/components`, {
      params,
    });
    return response.data;
  }

  async getStats() {
    const response = await axios.get(`${this.baseUrl}/api/v1/stats`);
    return response.data;
  }
}

// Create server instance
const server = new Server(
  {
    name: 'simflo-mcp-rag-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize API client
const apiClient = new RAGAPIClient(API_BASE_URL);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'search_components',
        description: 'Search for shadcn components using natural language queries',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Natural language search query (e.g., "modal dialog", "form input validation")',
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results to return (1-50)',
              default: 10,
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'get_component_details',
        description: 'Get detailed information about a specific shadcn component',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Component name (e.g., "button", "dialog", "input")',
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'get_component_installation',
        description: 'Get installation information and setup notes for a component',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Component name (e.g., "button", "dialog", "input")',
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'list_components',
        description: 'List available shadcn components, optionally filtered by type',
        inputSchema: {
          type: 'object',
          properties: {
            type: {
              type: 'string',
              enum: ['ui', 'block', 'hook'],
              description: 'Filter components by type',
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results to return (1-100)',
              default: 20,
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'search_components': {
        const validated = SearchComponentsSchema.parse(args);
        const result = await apiClient.searchComponents(validated.query, validated.limit);

        if (!result.success) {
          throw new Error(result.error || 'Search failed');
        }

        return {
          content: [
            {
              type: 'text',
              text: `Found ${result.data.length} components matching "${validated.query}":\n\n${result.data.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type})\n` +
                `   Relevance: ${(comp.relevanceScore * 100).toFixed(1)}%\n` +
                `   Install: \`${comp.installCommand}\`\n` +
                (comp.description ? `   Description: ${comp.description}\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      case 'get_component_details': {
        const validated = GetComponentDetailsSchema.parse(args);
        const result = await apiClient.getComponentDetails(validated.name);

        if (!result.success) {
          throw new Error(result.error || `Failed to get component details for "${validated.name}"`);
        }

        const comp = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**${comp.name}** (${comp.type})\n\n` +
                (comp.description ? `**Description:** ${comp.description}\n\n` : '') +
                `**Installation:** \`${comp.installCommand}\`\n` +
                `**Location:** ${comp.fileLocation}\n\n` +
                (comp.dependencies && comp.dependencies.length > 0 ?
                  `**Dependencies:** ${comp.dependencies.join(', ')}\n` : '') +
                (comp.registryDependencies && comp.registryDependencies.length > 0 ?
                  `**Registry Dependencies:** ${comp.registryDependencies.join(', ')}\n` : '') +
                (comp.categories && comp.categories.length > 0 ?
                  `**Categories:** ${comp.categories.join(', ')}\n` : ''),
            },
          ],
        };
      }

      case 'get_component_installation': {
        const validated = GetComponentInstallationSchema.parse(args);
        const result = await apiClient.getComponentInstallation(validated.name);

        if (!result.success) {
          throw new Error(result.error || `Failed to get installation info for "${validated.name}"`);
        }

        const install = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Installation for ${validated.name}:**\n\n` +
                `**Command:** \`${install.command}\`\n\n` +
                (install.dependencies && install.dependencies.length > 0 ?
                  `**Dependencies:** ${install.dependencies.join(', ')}\n\n` : '') +
                (install.registryDependencies && install.registryDependencies.length > 0 ?
                  `**Registry Dependencies:** ${install.registryDependencies.join(', ')}\n\n` : '') +
                `**Setup Notes:** ${install.setupNotes}`,
            },
          ],
        };
      }

      case 'list_components': {
        const validated = ListComponentsSchema.parse(args);
        const result = await apiClient.listComponents(validated.type, validated.limit);

        if (!result.success) {
          throw new Error(result.error || 'Failed to list components');
        }

        return {
          content: [
            {
              type: 'text',
              text: `Available components${validated.type ? ` of type "${validated.type}"` : ''}:\n\n${result.data.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type})\n` +
                `   Install: \`${comp.installCommand}\`\n` +
                (comp.description ? `   Description: ${comp.description}\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(`Invalid arguments: ${error.errors.map(e => e.message).join(', ')}`);
    }

    if (axios.isAxiosError(error)) {
      throw new Error(`API request failed: ${error.response?.data?.error || error.message}`);
    }

    throw error;
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('SimFlo MCP RAG server started');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});