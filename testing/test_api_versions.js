#!/usr/bin/env node

/**
 * Test both v1 and v2 API endpoints to compare functionality
 */

const { execSync } = require('child_process');

function testEndpoint(url, description) {
    try {
        console.log(`\n🔍 Testing: ${description}`);
        console.log(`URL: ${url}`);

        const result = execSync(`curl -s "${url}"`, { encoding: 'utf8' });
        const data = JSON.parse(result);

        console.log(`✅ SUCCESS: Status ${data.success ? 'OK' : 'FAILED'}`);
        if (data.success) {
            if (data.data && Array.isArray(data.data)) {
                console.log(`   Response: Array with ${data.data.length} items`);
            } else if (data.data && typeof data.data === 'object') {
                if (data.data.results) {
                    console.log(`   Response: Object with ${data.data.results.length} results`);
                } else if (data.data.components) {
                    console.log(`   Response: Object with ${data.data.components.length} components`);
                } else {
                    console.log(`   Response: Object with keys: ${Object.keys(data.data).join(', ')}`);
                }
            } else {
                console.log(`   Response: ${typeof data.data}`);
            }
        } else {
            console.log(`   Error: ${data.error || 'Unknown error'}`);
        }

        return { success: data.success, data: data.data };
    } catch (error) {
        console.log(`❌ FAILED: ${error.message}`);
        return { success: false, error: error.message };
    }
}

console.log('🔍 Comparing v1 and v2 API Endpoints');
console.log('='.repeat(60));

// Test results
const results = {
    v1: {},
    v2: {}
};

// Health checks
results.v1.health = testEndpoint('http://127.0.0.1:8000/health', 'V1 Health Check');
results.v2.health = testEndpoint('http://127.0.0.1:8000/health', 'V2 Health Check');

// Context endpoints
results.v1.context_current = testEndpoint('http://127.0.0.1:8000/api/v1/context/current', 'V1 Get Current Context');
results.v1.context_set = testEndpoint('http://127.0.0.1:8000/api/v1/context/set -X POST -H "Content-Type: application/json" -d \'{"platform":"reactjs"}\'', 'V1 Set Context');
results.v2.context = testEndpoint('http://127.0.0.1:8000/api/v2/context', 'V2 Get Context');
results.v2.context_set = testEndpoint('http://127.0.0.1:8000/api/v2/context/set -X POST -H "Content-Type: application/json" -d \'{"platform":"reactjs"}\'', 'V2 Set Context');

// Registry endpoints
results.v1.registries = testEndpoint('http://127.0.0.1:8000/api/v1/registries?platform=reactjs', 'V1 List Registries');
results.v2.registries = testEndpoint('http://127.0.0.1:8000/api/v2/registries?platform=reactjs', 'V2 List Registries');

// Component search endpoints
results.v1.search = testEndpoint('http://127.0.0.1:8000/api/v1/components/search?q=button&limit=5', 'V1 Search Components');
results.v2.search = testEndpoint('http://127.0.0.1:8000/api/v2/components/search?q=button&limit=5', 'V2 Search Components');

// Component list endpoints
results.v1.list = testEndpoint('http://127.0.0.1:8000/api/v1/components?type=ui&limit=5', 'V1 List Components');
results.v2.list = testEndpoint('http://127.0.0.1:8000/api/v2/components?type=ui&limit=5', 'V2 List Components');

// Component details
results.v1.details = testEndpoint('http://127.0.0.1:8000/api/v1/components/button', 'V1 Get Component Details');
results.v2.details = testEndpoint('http://127.0.0.1:8000/api/v2/components/button', 'V2 Get Component Details');

// Stats
results.v1.stats = testEndpoint('http://127.0.0.1:8000/api/v1/stats', 'V1 Get Stats');
results.v2.context_stats = testEndpoint('http://127.0.0.1:8000/api/v2/context/stats', 'V2 Get Context Stats');

// Summary
console.log('\n' + '='.repeat(60));
console.log('📊 API VERSION COMPARISON SUMMARY');
console.log('='.repeat(60));

const v1Count = Object.values(results.v1).filter(r => r.success).length;
const v2Count = Object.values(results.v2).filter(r => r.success).length;
const v1Total = Object.keys(results.v1).length;
const v2Total = Object.keys(results.v2).length;

console.log(`\n📈 V1 API: ${v1Count}/${v1Total} endpoints working (${((v1Count/v1Total)*100).toFixed(1)}%)`);
console.log(`📈 V2 API: ${v2Count}/${v2Total} endpoints working (${((v2Count/v2Total)*100).toFixed(1)}%)`);

console.log('\n🔧 MCP Server Usage:');
console.log('   Components Search: V2');
console.log('   Component Details: V2');
console.log('   Component Installation: V2');
console.log('   Components List: V2');
console.log('   Context Set: V1');
console.log('   Context Get: V1');
console.log('   Registries: V1');
console.log('   Stats: V1');

console.log('\n💡 Recommendations:');
if (v1Count > v2Count) {
    console.log('   ✅ V1 API appears more stable');
} else if (v2Count > v1Count) {
    console.log('   ✅ V2 API appears more stable');
} else {
    console.log('   ⚖️  Both APIs have similar stability');
}

console.log('   📝 Consider standardizing on one API version for consistency');
console.log('   🔍 Test both versions thoroughly before production use');