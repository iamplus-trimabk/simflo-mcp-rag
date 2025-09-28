#!/usr/bin/env node

/**
 * Enhanced MCP Client Test Tool
 * Tests MCP server functionality with actual API calls
 */

const { spawn } = require('child_process');
const path = require('path');

async function testMCPClient() {
    console.log('🔍 Testing MCP Server with API Calls');
    console.log('='.repeat(50));

    try {
        // Start MCP server process
        const serverPath = path.join(__dirname, '..', 'mcp-server', 'dist', 'index.js');
        console.log(`Testing MCP server at: ${serverPath}`);

        const serverProcess = spawn('node', [serverPath], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let serverOutput = '';
        let serverError = '';

        serverProcess.stderr.on('data', (data) => {
            const output = data.toString();
            serverError += output;
            console.log(`Server stderr: ${output}`);
        });

        serverProcess.stdout.on('data', (data) => {
            const output = data.toString();
            serverOutput += output;
            console.log(`Server stdout: ${output}`);
        });

        // Wait for server to start
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Test API endpoints directly
        console.log('\n📡 Testing API Endpoints...');

        // Test 1: Set context
        console.log('\n1. Testing set_platform_context...');
        const contextRequest = {
            jsonrpc: "2.0",
            id: 1,
            method: "tools/call",
            params: {
                name: "set_platform_context",
                arguments: {
                    platform: "reactjs",
                    session_id: "test-session-123"
                }
            }
        };

        serverProcess.stdin.write(JSON.stringify(contextRequest) + '\n');

        // Test 2: Get context
        console.log('\n2. Testing get_platform_context...');
        const getContextRequest = {
            jsonrpc: "2.0",
            id: 2,
            method: "tools/call",
            params: {
                name: "get_platform_context",
                arguments: {
                    session_id: "test-session-123"
                }
            }
        };

        serverProcess.stdin.write(JSON.stringify(getContextRequest) + '\n');

        // Test 3: List tools
        console.log('\n3. Testing tools list...');
        const listToolsRequest = {
            jsonrpc: "2.0",
            id: 3,
            method: "tools/list",
            params: {}
        };

        serverProcess.stdin.write(JSON.stringify(listToolsRequest) + '\n');

        // Wait for responses
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Test 4: Search components
        console.log('\n4. Testing search_components...');
        const searchRequest = {
            jsonrpc: "2.0",
            id: 4,
            method: "tools/call",
            params: {
                name: "search_components",
                arguments: {
                    query: "button",
                    limit: 5
                }
            }
        };

        serverProcess.stdin.write(JSON.stringify(searchRequest) + '\n');

        // Wait for final responses
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log('\n✅ MCP Client Test Summary:');
        console.log(`- Server started: ${serverOutput.includes('SimFlo MCP RAG server started')}`);
        console.log(`- Server errors: ${serverError || 'None'}`);

        // Clean up
        serverProcess.kill();

        console.log('\n🎯 Test completed. Check server output above for detailed results.');

    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        process.exit(1);
    }
}

// Run the test
testMCPClient();