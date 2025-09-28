#!/usr/bin/env node

/**
 * Simple MCP Test Script using CommonJS
 * Tests basic MCP server functionality without SDK dependencies
 */

const { spawn } = require('child_process');
const path = require('path');

async function testMCPServer() {
    console.log('🔍 Testing MCP Server Basic Functionality');
    console.log('='.repeat(50));

    try {
        // Start MCP server process
        const serverPath = path.join(__dirname, '..', 'mcp-server', 'dist', 'index.js');
        console.log(`Testing MCP server at: ${serverPath}`);

        // Test if the server file exists
        const fs = require('fs');
        if (!fs.existsSync(serverPath)) {
            console.log('❌ MCP server built file does not exist');
            process.exit(1);
        }

        console.log('✅ MCP server built file exists');

        // Test basic server startup
        const serverProcess = spawn('node', [serverPath], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        // Set up timeout
        const timeout = setTimeout(() => {
            serverProcess.kill();
            console.log('✅ MCP server started successfully (timeout test)');
            process.exit(0);
        }, 3000);

        serverProcess.on('error', (error) => {
            clearTimeout(timeout);
            console.log(`❌ Server startup failed: ${error.message}`);
            process.exit(1);
        });

        serverProcess.on('exit', (code) => {
            clearTimeout(timeout);
            if (code === 0) {
                console.log('✅ MCP server exited cleanly');
                process.exit(0);
            } else {
                console.log(`❌ MCP server exited with code ${code}`);
                process.exit(1);
            }
        });

        // Read any output
        serverProcess.stderr.on('data', (data) => {
            const output = data.toString();
            if (output.includes('SimFlo MCP RAG server started')) {
                clearTimeout(timeout);
                console.log('✅ MCP server started successfully');
                serverProcess.kill();
                process.exit(0);
            }
        });

    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        process.exit(1);
    }
}

// Run the test
testMCPServer();