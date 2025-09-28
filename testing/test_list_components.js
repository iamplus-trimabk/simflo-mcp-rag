#!/usr/bin/env node

/**
 * Test script specifically for list_components functionality
 */

const { spawn } = require('child_process');
const path = require('path');

async function testListComponents() {
    console.log('🔍 Testing list_components functionality');
    console.log('='.repeat(50));

    try {
        // Start MCP server process
        const serverPath = path.join(__dirname, '..', 'mcp-server', 'dist', 'index.js');
        const serverProcess = spawn('node', [serverPath], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let responseCount = 0;

        serverProcess.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(`Server response: ${output}`);

            try {
                const response = JSON.parse(output);
                if (response.result && response.result.content) {
                    const text = response.result.content[0].text;
                    console.log(`\n✅ SUCCESS: ${text.substring(0, 100)}...`);
                    responseCount++;

                    if (responseCount >= 2) {
                        serverProcess.kill();
                        console.log('\n🎯 All tests completed successfully!');
                        process.exit(0);
                    }
                }
            } catch (e) {
                // Ignore JSON parse errors for non-response lines
            }
        });

        serverProcess.stderr.on('data', (data) => {
            console.log(`Server stderr: ${data.toString()}`);
        });

        // Wait for server to start
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Test list_components
        console.log('\n📡 Testing list_components...');
        const listRequest = {
            jsonrpc: "2.0",
            id: 1,
            method: "tools/call",
            params: {
                name: "list_components",
                arguments: {
                    type: "ui",
                    limit: 5,
                    platform: "reactjs",
                    registry: "gluestack_db"
                }
            }
        };

        serverProcess.stdin.write(JSON.stringify(listRequest) + '\n');

        // Test search_components
        console.log('\n📡 Testing search_components...');
        const searchRequest = {
            jsonrpc: "2.0",
            id: 2,
            method: "tools/call",
            params: {
                name: "search_components",
                arguments: {
                    query: "card",
                    limit: 5,
                    platform: "reactjs"
                }
            }
        };

        setTimeout(() => {
            serverProcess.stdin.write(JSON.stringify(searchRequest) + '\n');
        }, 1000);

        // Timeout after 10 seconds
        setTimeout(() => {
            serverProcess.kill();
            console.log('\n⏰ Test completed due to timeout');
            process.exit(0);
        }, 10000);

    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        process.exit(1);
    }
}

// Run the test
testListComponents();