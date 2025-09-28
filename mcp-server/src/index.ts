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

// Extraction Management Schemas
const ListExtractionRegistriesSchema = z.object({});

const RunExtractionSchema = z.object({
  registry: z.string().optional(),
  source: z.string().optional(),
  mode: z.enum(['test', 'real']).default('test'),
});

const GetExtractionStatusSchema = z.object({});

const SearchComponentsByCategorySchema = z.object({
  query: z.string().min(1, "Search query is required"),
  category: z.enum(['components', 'hooks', 'blocks']),
  platform: z.enum(['reactjs', 'reactnative', 'auto', 'none']).optional(),
  limit: z.number().min(1).max(50).optional().default(10),
});

const ListRegistrySourcesSchema = z.object({
  registry: z.string().min(1, "Registry name is required"),
});

const ClearExtractionDataSchema = z.object({
  registry: z.string().optional(),
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

    const response = await axios.get(`${this.baseUrl}/api/v1/components/search`, { params });
    return response.data;
  }

  async getComponentDetails(name: string, registry?: string) {
    const params: any = {};
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v1/components/${name}`, { params });
    return response.data;
  }

  async getComponentInstallation(name: string, registry?: string) {
    const params: any = {};
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v1/components/${name}/installation`, { params });
    return response.data;
  }

  async listComponents(type?: string, limit: number = 20, platform?: string, registry?: string) {
    const params: any = { limit };
    if (type) params.type = type;
    if (platform) params.platform = platform;
    if (registry) params.registry = registry;

    const response = await axios.get(`${this.baseUrl}/api/v1/components`, { params });
    return response.data;
  }

  async getStats() {
    const response = await axios.get(`${this.baseUrl}/api/v1/stats`);
    return response.data;
  }

  // Context management APIs
  async setPlatformContext(platform: string, sessionId?: string, userAgent?: string, projectType?: string) {
    const data: any = { platform };
    if (sessionId) data.session_id = sessionId;
    if (userAgent) data.user_agent = userAgent;
    if (projectType) data.project_type = projectType;

    const response = await axios.post(`${this.baseUrl}/api/v1/context/set`, data);
    return response.data;
  }

  async getPlatformContext(sessionId?: string) {
    const params: any = {};
    if (sessionId) params.session_id = sessionId;

    const response = await axios.get(`${this.baseUrl}/api/v1/context/current`, { params });
    return response.data;
  }

  async listRegistries(platform?: string) {
    const params: any = {};
    if (platform) params.platform = platform;

    const response = await axios.get(`${this.baseUrl}/api/v1/registries`, { params });
    return response.data;
  }

  async getContextStats() {
    const response = await axios.get(`${this.baseUrl}/api/v1/context/stats`);
    return response.data;
  }

  // Extraction Management APIs
  async listExtractionRegistries() {
    const response = await axios.get(`${this.baseUrl}/api/v2/extraction/registries`);
    return response.data;
  }

  async runExtraction(registry?: string, source?: string, mode: string = 'test') {
    const formData = new FormData();
    if (registry) formData.append('registry', registry);
    if (source) formData.append('source', source);
    formData.append('mode', mode);

    const response = await axios.post(`${this.baseUrl}/api/v2/extraction/run`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getExtractionStatus() {
    const response = await axios.get(`${this.baseUrl}/api/v2/extraction/status`);
    return response.data;
  }

  async searchComponentsByCategory(query: string, category: string, platform?: string, limit: number = 10) {
    const params: any = { q: query, category, limit };
    if (platform) params.platform = platform;

    const response = await axios.get(`${this.baseUrl}/api/v2/components/search/category`, { params });
    return response.data;
  }

  async listRegistrySources(registry: string) {
    const params: any = { registry };

    const response = await axios.get(`${this.baseUrl}/api/v2/extraction/sources`, { params });
    return response.data;
  }

  async clearExtractionData(registry?: string) {
    const params: any = {};
    if (registry) params.registry = registry;

    const response = await axios.delete(`${this.baseUrl}/api/v2/extraction/clear`, { params });
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
        description: 'Search for components using natural language with platform context awareness',
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
            platform: {
              type: 'string',
              enum: ['reactjs', 'reactnative', 'auto', 'none'],
              description: 'Target platform for component recommendations',
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'get_component_details',
        description: 'Get detailed information about a specific component',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Component name (e.g., "button", "dialog", "input")',
            },
            registry: {
              type: 'string',
              description: 'Specific registry to search (e.g., "shadcn_db", "gluestack_db")',
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
            registry: {
              type: 'string',
              description: 'Specific registry to search (e.g., "shadcn_db", "gluestack_db")',
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'list_components',
        description: 'List available components by type or category with platform filtering',
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
            platform: {
              type: 'string',
              enum: ['reactjs', 'reactnative', 'auto', 'none'],
              description: 'Filter by platform support',
            },
            registry: {
              type: 'string',
              description: 'Specific registry to search (e.g., "shadcn_db", "gluestack_db")',
            },
          },
        },
      },
      {
        name: 'set_platform_context',
        description: 'Set the platform context for intelligent component recommendations',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              enum: ['reactjs', 'reactnative', 'auto', 'none'],
              description: 'Target platform for component recommendations',
            },
            session_id: {
              type: 'string',
              description: 'Optional session identifier for context tracking',
            },
            user_agent: {
              type: 'string',
              description: 'Optional user agent information',
            },
            project_type: {
              type: 'string',
              description: 'Optional project type information',
            },
          },
          required: ['platform'],
        },
      },
      {
        name: 'get_platform_context',
        description: 'Get the current platform context and session information',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'Optional session identifier',
            },
          },
        },
      },
      {
        name: 'list_registries',
        description: 'List available component registries with platform filtering',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              enum: ['reactjs', 'reactnative', 'auto', 'none'],
              description: 'Filter registries by platform support',
            },
          },
        },
      },
      {
        name: 'list_extraction_registries',
        description: 'List available registries for specialized extraction with detailed source information',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'run_extraction',
        description: 'Run the specialized extraction pipeline for components, hooks, and blocks',
        inputSchema: {
          type: 'object',
          properties: {
            registry: {
              type: 'string',
              description: 'Specific registry to extract (e.g., "shadcn", "gluestack")',
            },
            source: {
              type: 'string',
              description: 'Specific source to extract within the registry',
            },
            mode: {
              type: 'string',
              enum: ['test', 'real'],
              default: 'test',
              description: 'Extraction mode: test (mock data) or real (live extraction)',
            },
          },
        },
      },
      {
        name: 'get_extraction_status',
        description: 'Get extraction pipeline status, statistics, and available data',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'search_components_by_category',
        description: 'Search for components within specific categories (components, hooks, blocks)',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Natural language search query (e.g., "form validation", "modal dialog")',
            },
            category: {
              type: 'string',
              enum: ['components', 'hooks', 'blocks'],
              description: 'Component category to search within',
            },
            platform: {
              type: 'string',
              enum: ['reactjs', 'reactnative', 'auto', 'none'],
              description: 'Target platform for component recommendations',
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results to return (1-50)',
              default: 10,
            },
          },
          required: ['query', 'category'],
        },
      },
      {
        name: 'list_registry_sources',
        description: 'List detailed sources for a specific registry including extractor types',
        inputSchema: {
          type: 'object',
          properties: {
            registry: {
              type: 'string',
              description: 'Registry name (e.g., "shadcn", "gluestack")',
            },
          },
          required: ['registry'],
        },
      },
      {
        name: 'clear_extraction_data',
        description: 'Clear extracted data files from the extraction pipeline',
        inputSchema: {
          type: 'object',
          properties: {
            registry: {
              type: 'string',
              description: 'Specific registry to clear (optional - clears all if not specified)',
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

        // Handle v2 API response format which has data.components structure
        const components = result.data?.components || result.data?.results || result.data || [];

        return {
          content: [
            {
              type: 'text',
              text: `Found ${components.length} components matching "${validated.query}"${validated.platform ? ` for ${validated.platform}` : ''}:\n\n${components.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type || 'component'})\n` +
                `   Registry: ${comp.registry || 'unknown'}\n` +
                `   Platform: ${comp.platform ? (Array.isArray(comp.platform) ? comp.platform.join(', ') : comp.platform) : 'any'}\n` +
                `   Relevance: ${((comp.relevance_score || comp.relevanceScore || 0) * 100).toFixed(1)}%\n` +
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
                (comp.dependencies && Array.isArray(comp.dependencies) && comp.dependencies.length > 0 ?
                  `**Dependencies:** ${comp.dependencies.join(', ')}\n` : '') +
                (comp.files && Array.isArray(comp.files) && comp.files.length > 0 ?
                  `**Files:** ${comp.files.length} file(s)\n` : '') +
                (comp.usage_examples && Array.isArray(comp.usage_examples) && comp.usage_examples.length > 0 ?
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

        // Handle v2 API response format which has data.components structure
        const components = result.data?.components || result.data?.results || result.data || [];

        return {
          content: [
            {
              type: 'text',
              text: `Available components${validated.type ? ` of type "${validated.type}"` : ''}${validated.platform ? ` for ${validated.platform}` : ''}${validated.registry ? ` from ${validated.registry}` : ''}:\n\n${components.map((comp: any, index: number) =>
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

        const registries = result.data || [];

        return {
          content: [
            {
              type: 'text',
              text: `Available component registries${validated.platform ? ` for ${validated.platform}` : ''}:\n\n${registries.map((reg: any, index: number) =>
                `${index + 1}. **${reg.name}**\n` +
                `   Components: ${reg.component_count || reg.components || 0}\n` +
                `   Platform: ${reg.platform ? (Array.isArray(reg.platform) ? reg.platform.join(', ') : reg.platform) : 'any'}\n` +
                `   Status: ${reg.is_active ? 'Active' : 'Inactive'}\n` +
                `   Last Updated: ${reg.last_updated ? new Date(reg.last_updated * 1000).toISOString() : 'unknown'}\n` +
                (reg.description ? `   Description: ${reg.description}\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      case 'list_extraction_registries': {
        const validated = ListExtractionRegistriesSchema.parse(args);
        const result = await apiClient.listExtractionRegistries();

        if (!result.success) {
          throw new Error(result.error || 'Failed to list extraction registries');
        }

        const registries = result.data?.registries || [];
        return {
          content: [
            {
              type: 'text',
              text: `Available extraction registries (${result.data?.total_count || 0} total):\n\n${registries.map((reg: any, index: number) =>
                `${index + 1}. **${reg.name}** (${reg.display_name})\n` +
                `   Description: ${reg.description}\n` +
                `   Platforms: ${reg.platforms?.join(', ') || 'any'}\n` +
                `   Categories: ${reg.categories?.join(', ') || 'none'}\n` +
                `   Status: ${reg.status}\n` +
                `   Sources: ${reg.component_count || 0}\n` +
                (reg.error ? `   Error: ${reg.error}\n` : '')
              ).join('\n')}`,
            },
          ],
        };
      }

      case 'run_extraction': {
        const validated = RunExtractionSchema.parse(args);
        const result = await apiClient.runExtraction(validated.registry, validated.source, validated.mode);

        if (!result.success) {
          throw new Error(result.error || 'Extraction failed');
        }

        const extraction = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Extraction completed**\n\n` +
                `**Mode:** ${extraction.mode}\n` +
                `**Registry:** ${extraction.registry || 'all registries'}\n` +
                `**Source:** ${extraction.source || 'all sources'}\n` +
                `**Status:** ${extraction.success ? 'Success' : 'Failed'}\n` +
                `**Message:** ${extraction.message}`,
            },
          ],
        };
      }

      case 'get_extraction_status': {
        const validated = GetExtractionStatusSchema.parse(args);
        const result = await apiClient.getExtractionStatus();

        if (!result.success) {
          throw new Error(result.error || 'Failed to get extraction status');
        }

        const status = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Extraction Pipeline Status**\n\n` +
                `**Output Directory:** ${status.output_directory_exists ? 'Exists' : 'Not found'}\n` +
                `**Total Components:** ${status.total_components}\n` +
                `**Last Extraction:** ${status.last_extraction || 'Never'}\n\n` +
                `**Extracted Files:** ${status.extracted_files?.length || 0}\n` +
                (status.extracted_files?.length > 0 ? `   ${status.extracted_files.join(', ')}\n` : '') +
                `**Merged Files:** ${status.merged_files?.length || 0}\n` +
                (status.merged_files?.length > 0 ? `   ${status.merged_files.join(', ')}\n` : ''),
            },
          ],
        };
      }

      case 'search_components_by_category': {
        const validated = SearchComponentsByCategorySchema.parse(args);
        const result = await apiClient.searchComponentsByCategory(
          validated.query,
          validated.category,
          validated.platform,
          validated.limit
        );

        if (!result.success) {
          throw new Error(result.error || 'Category search failed');
        }

        const search = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `Found ${search.total_found || 0} ${validated.category} matching "${validated.query}"${validated.platform ? ` for ${validated.platform}` : ''}:\n\n${search.results?.map((comp: any, index: number) =>
                `${index + 1}. **${comp.name}** (${comp.type})\n` +
                `   Registry: ${comp.registry}\n` +
                `   Category: ${comp.category_match}\n` +
                `   Relevance: ${((comp.relevance_score || 0) * 100).toFixed(1)}%\n` +
                `   Dependencies: ${comp.dependencies?.join(', ') || 'none'}\n` +
                (comp.description ? `   Description: ${comp.description}\n` : '') +
                `   Install: \`${comp.install_command}\``
              ).join('\n') || 'No results found'}`,
            },
          ],
        };
      }

      case 'list_registry_sources': {
        const validated = ListRegistrySourcesSchema.parse(args);
        const result = await apiClient.listRegistrySources(validated.registry);

        if (!result.success) {
          throw new Error(result.error || `Failed to list sources for registry "${validated.registry}"`);
        }

        const sources = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Sources for ${validated.registry}**\n\n` +
                `**Total Sources:** ${sources.total_sources || 0}\n\n` +
                Object.entries(sources.categories || {}).map(([category, categorySources]: [string, any[]]) =>
                  `**${category}** (${categorySources.length} sources):\n` +
                  categorySources.map((source, index) =>
                    `   ${index + 1}. **${source.name}** (${source.type})\n` +
                    `      URL: ${source.url}\n` +
                    `      Enabled: ${source.enabled}\n` +
                    `      Priority: ${source.priority}\n` +
                    `      Extractor: ${source.extractor}\n`
                  ).join('\n')
                ).join('\n'),
            },
          ],
        };
      }

      case 'clear_extraction_data': {
        const validated = ClearExtractionDataSchema.parse(args);
        const result = await apiClient.clearExtractionData(validated.registry);

        if (!result.success) {
          throw new Error(result.error || 'Failed to clear extraction data');
        }

        const clear = result.data;
        return {
          content: [
            {
              type: 'text',
              text: `**Extraction data cleared**\n\n` +
                `**Registry:** ${clear.registry || 'all registries'}\n` +
                `**Cleared Files:** ${clear.cleared_files?.length || 0}\n` +
                (clear.cleared_files?.length > 0 ? `   ${clear.cleared_files.join(', ')}\n` : '') +
                `**Message:** ${clear.message}`,
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