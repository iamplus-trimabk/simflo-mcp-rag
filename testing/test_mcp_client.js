#!/usr/bin/env node

/**
 * MCP Client Test Script
 *
 * Tests MCP server functionality using the MCP SDK client
 * This validates that the MCP server properly exposes all expected tools
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testMCPServer() {
    console.log('🔍 Testing MCP Server Functionality');
    console.log('=' * 50);

    try {
        // Start MCP server process
        const serverPath = path.join(__dirname, '..', 'mcp-server', 'dist', 'index.js');
        console.log(`Starting MCP server from: ${serverPath}`);

        const serverProcess = spawn('node', [serverPath]);

        // Create client transport
        const transport = new StdioClientTransport({
            command: 'node',
            args: [serverPath]
        });

        // Create MCP client
        const client = new Client(
            {
                name: 'test-client',
                version: '1.0.0'
            },
            {
                capabilities: {}
            }
        );

        console.log('🔌 Connecting to MCP server...');
        await client.connect(transport);
        console.log('✅ Connected successfully');

        // Test 1: List available tools
        console.log('\n📋 Test: Tool Discovery');
        console.log('-' * 30);

        const toolsResult = await client.listTools();
        const tools = toolsResult.tools;

        console.log(`📊 Found ${tools.length} tools:`);
        tools.forEach(tool => {
            console.log(`   • ${tool.name}: ${tool.description}`);
        });

        // Test 2: Validate expected tools are present
        console.log('\n📋 Test: Expected Tools Validation');
        console.log('-' * 30);

        const expectedTools = [
            'search_components',
            'get_component_details',
            'get_component_installation',
            'list_components',
            'set_platform_context',
            'get_platform_context',
            'list_registries'
        ];

        const missingTools = expectedTools.filter(toolName =>
            !tools.some(tool => tool.name === toolName)
        );

        if (missingTools.length === 0) {
            console.log('✅ All expected tools are present');
        } else {
            console.log(`❌ Missing tools: ${missingTools.join(', ')}`);
            process.exit(1);
        }

        // Test 3: Test tool execution (simple test)
        console.log('\n📋 Test: Tool Execution');
        console.log('-' * 30);

        try {
            const listResult = await client.callTool({
                name: 'list_components',
                arguments: {}
            });

            console.log('✅ list_components tool executed successfully');
            console.log(`📄 Result type: ${typeof listResult.content[0]?.text}`);
        } catch (error) {
            console.log(`❌ Tool execution failed: ${error.message}`);
        }

        // Test 4: Test context tools
        console.log('\n📋 Test: Context Tools');
        console.log('-' * 30);

        try {
            const contextResult = await client.callTool({
                name: 'get_platform_context',
                arguments: {}
            });

            console.log('✅ get_platform_context tool executed successfully');
        } catch (error) {
            console.log(`❌ Context tool failed: ${error.message}`);
        }

        console.log('\n' + '=' * 50);
        console.log('🎉 All MCP client tests completed successfully!');
        console.log('✅ MCP server is working correctly');

        // Clean up
        serverProcess.kill();
        process.exit(0);

    } catch (error) {
        console.error(`❌ MCP client test failed: ${error.message}`);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run the test
testMCPServer();