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
  platform: z.enum(['reactjs', 'reactnative', 'auto', 'none']).optional(),
});

const GetComponentDetailsSchema = z.object({
  name: z.string().min(1, "Component name is required"),
  registry: z.string().optional(),
});

const GetComponentInstallationSchema = z.object({
  name: z.string().min(1, "Component name is required"),
  registry: z.string().optional(),
});

const ListComponentsSchema = z.object({
  type: z.enum(['ui', 'block', 'hook']).optional(),
  limit: z.number().min(1).max(100).optional().default(20),
  platform: z.enum(['reactjs', 'reactnative', 'auto', 'none']).optional(),
  registry: z.string().optional(),
});

const SetPlatformContextSchema = z.object({
  platform: z.enum(['reactjs', 'reactnative', 'auto', 'none']),
  session_id: z.string().optional(),
  user_agent: z.string().optional(),
  project_type: z.string().optional(),
});

const GetPlatformContextSchema = z.object({
  session_id: z.string().optional(),
});

const ListRegistriesSchema = z.object({
  platform: z.enum(['reactjs', 'reactnative', 'auto', 'none']).optional(),
});

// API client
class RAGAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async searchComponents(query: string, limit: number = 10, platform?: string) {
    const params: any = { q: query, limit };
    if (platform) params.platform = platform;

    const response = await axios.get(`${this.baseUrl}/api/v2/components/search`, { params });
    return response.data;
  }

  async getComponentDetails(name: string, registry?: string) {
    const params: any = {};
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v2/components/${name}`, { params });
    return response.data;
  }

  async getComponentInstallation(name: string, registry?: string) {
    const params: any = {};
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v2/components/${name}/installation`, { params });
    return response.data;
  }

  async listComponents(type?: string, limit: number = 20, platform?: string, registry?: string) {
    const params: any = { limit };
    if (type) params.type = type;
    if (platform) params.platform = platform;
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v2/components`, { params });
    return response.data;
  }

  async getStats() {
    const response = await axios.get(`${this.baseUrl}/api/v1/stats`);
    return response.data;
  }

  // Context management APIs
  async setPlatformContext(platform: string, sessionId?: string, userAgent?: string, projectType?: string) {
    const response = await axios.post(`${this.baseUrl}/api/v2/context/set`, {
      platform,
      session_id: sessionId,
      user_agent: userAgent,
      project_type: projectType,
    });
    return response.data;
  }

  async getPlatformContext(sessionId?: string) {
    const params: any = {};
    if (sessionId) params.session_id = sessionId;

    const response = await axios.get(`${this.baseUrl}/api/v2/context`, { params });
    return response.data;
  }

  async listRegistries(platform?: string) {
    const params: any = {};
    if (platform) params.platform = platform;

    const response = await axios.get(`${this.baseUrl}/api/v2/registries`, { params });
    return response.data;
  }

  async getContextStats() {
    const response = await axios.get(`${this.baseUrl}/api/v2/context/stats`);
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
        const result = await apiClient.searchComponents(validated.query, validated.limit, validated.platform);

        if (!result.success) {
          throw new Error(result.error || 'Search failed');
        }

        return {
          content: [
            {
              type: 'text',
              text: `Found ${result.data.length} components matching "${validated.query}"${validated.platform ? ` for ${validated.platform}` : ''}:\n\n${result.data.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type || 'component'})\n` +
                `   Registry: ${comp.registry || 'unknown'}\n` +
                `   Platform: ${comp.platform ? (Array.isArray(comp.platform) ? comp.platform.join(', ') : comp.platform) : 'any'}\n` +
                `   Relevance: ${(comp.relevance_score || comp.relevanceScore || 0 * 100).toFixed(1)}%\n` +
                (comp.description ? `   Description: ${comp.description}\n` : '') +
                (comp.installation ? `   Install: \`${comp.installation}\`\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      case 'get_component_details': {
        const validated = GetComponentDetailsSchema.parse(args);
        const result = await apiClient.getComponentDetails(validated.name, validated.registry);

        if (!result.success) {
          throw new Error(result.error || `Failed to get component details for "${validated.name}"`);
        }

        const comp = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**${comp.name}** (${comp.type || 'component'})\n\n` +
                (comp.description ? `**Description:** ${comp.description}\n\n` : '') +
                `**Registry:** ${comp.registry || 'unknown'}\n` +
                `**Platform:** ${comp.platform ? (Array.isArray(comp.platform) ? comp.platform.join(', ') : comp.platform) : 'any'}\n` +
                (comp.installation ? `**Installation:** \`${comp.installation}\`\n` : '') +
                (comp.dependencies && comp.dependencies.length > 0 ?
                  `**Dependencies:** ${comp.dependencies.join(', ')}\n` : '') +
                (comp.files && comp.files.length > 0 ?
                  `**Files:** ${comp.files.length} file(s)\n` : '') +
                (comp.usage_examples && comp.usage_examples.length > 0 ?
                  `**Usage Examples:**\n${comp.usage_examples.map((ex: string, i: number) => `  ${i + 1}. ${ex}`).join('\n')}\n` : ''),
            },
          ],
        };
      }

      case 'get_component_installation': {
        const validated = GetComponentInstallationSchema.parse(args);
        const result = await apiClient.getComponentInstallation(validated.name, validated.registry);

        if (!result.success) {
          throw new Error(result.error || `Failed to get installation info for "${validated.name}"`);
        }

        const install = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Installation for ${validated.name}:**\n\n` +
                `**Registry:** ${install.registry || 'unknown'}\n` +
                (install.command ? `**Command:** \`${install.command}\`\n\n` : '') +
                (install.dependencies && install.dependencies.length > 0 ?
                  `**Dependencies:** ${install.dependencies.join(', ')}\n\n` : '') +
                (install.setup_notes ? `**Setup Notes:** ${install.setup_notes}` : ''),
            },
          ],
        };
      }

      case 'list_components': {
        const validated = ListComponentsSchema.parse(args);
        const result = await apiClient.listComponents(validated.type, validated.limit, validated.platform, validated.registry);

        if (!result.success) {
          throw new Error(result.error || 'Failed to list components');
        }

        return {
          content: [
            {
              type: 'text',
              text: `Available components${validated.type ? ` of type "${validated.type}"` : ''}${validated.platform ? ` for ${validated.platform}` : ''}${validated.registry ? ` from ${validated.registry}` : ''}:\n\n${result.data.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type || 'component'})\n` +
                `   Registry: ${comp.registry || 'unknown'}\n` +
                `   Platform: ${comp.platform ? (Array.isArray(comp.platform) ? comp.platform.join(', ') : comp.platform) : 'any'}\n` +
                (comp.installation ? `   Install: \`${comp.installation}\`\n` : '') +
                (comp.description ? `   Description: ${comp.description}\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      case 'set_platform_context': {
        const validated = SetPlatformContextSchema.parse(args);
        const result = await apiClient.setPlatformContext(
          validated.platform,
          validated.session_id,
          validated.user_agent,
          validated.project_type
        );

        if (!result.success) {
          throw new Error(result.error || 'Failed to set platform context');
        }

        const context = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Platform context set to ${context.platform}**\n\n` +
                `**Session ID:** ${context.session_id}\n` +
                `**Timestamp:** ${new Date(context.timestamp * 1000).toISOString()}\n` +
                (context.user_agent ? `**User Agent:** ${context.user_agent}\n` : '') +
                (context.project_type ? `**Project Type:** ${context.project_type}\n` : '') +
                `**Confidence:** ${(context.confidence * 100).toFixed(1)}%\n\n` +
                `The system will now prioritize components for ${context.platform} in search results.`,
            },
          ],
        };
      }

      case 'get_platform_context': {
        const validated = GetPlatformContextSchema.parse(args);
        const result = await apiClient.getPlatformContext(validated.session_id);

        if (!result.success) {
          throw new Error(result.error || 'Failed to get platform context');
        }

        const context = result.data;
        return {
          content: [
            {
              type: 'text',
              text: context ?
                `**Current Platform Context:** ${context.platform}\n\n` +
                `**Session ID:** ${context.session_id}\n` +
                `**Timestamp:** ${new Date(context.timestamp * 1000).toISOString()}\n` +
                (context.user_agent ? `**User Agent:** ${context.user_agent}\n` : '') +
                (context.project_type ? `**Project Type:** ${context.project_type}\n` : '') +
                `**Confidence:** ${(context.confidence * 100).toFixed(1)}%` :
                'No platform context is currently set. Use set_platform_context to establish context.',
            },
          ],
        };
      }

      case 'list_registries': {
        const validated = ListRegistriesSchema.parse(args);
        const result = await apiClient.listRegistries(validated.platform);

        if (!result.success) {
          throw new Error(result.error || 'Failed to list registries');
        }

        return {
          content: [
            {
              type: 'text',
              text: `Available component registries${validated.platform ? ` for ${validated.platform}` : ''}:\n\n${result.data.map((reg: any, index: number) =>
                `${index + 1}. **${reg.name}**\n` +
                `   Components: ${reg.component_count || 0}\n` +
                `   Platform: ${reg.platform ? (Array.isArray(reg.platform) ? reg.platform.join(', ') : reg.platform) : 'any'}\n` +
                `   Status: ${reg.is_active ? 'Active' : 'Inactive'}\n` +
                `   Last Updated: ${reg.last_updated ? new Date(reg.last_updated * 1000).toISOString() : 'unknown'}\n` +
                (reg.description ? `   Description: ${reg.description}\n` : '')
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