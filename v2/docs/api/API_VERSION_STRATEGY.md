# API Version Strategy for SimFlo MCP RAG

## Development Workflow

This document outlines our API version management strategy to ensure we always have a stable, working API while developing new features.

### 🔄 Current State (Phase 1: Stable Foundation)

**V1 API (Current Stable Version)**
- **Status**: ✅ Production ready
- **Endpoints**: `/api/v1/*`
- **Response Format**: Simple direct arrays
  ```json
  {
    "success": true,
    "data": [array_of_items]
  }
  ```
- **Usage**: All MCP server calls use v1 endpoints
- **Testing**: All tests validate v1 functionality

**V2 API (Development Version)**
- **Status**: 🚧 Not yet implemented
- **Endpoints**: `/api/v2/*` (will be created for new features)
- **Response Format**: Enhanced structured format (future)
- **Usage**: Development and testing only
- **Testing**: Separate test suite for v2 validation

### 📋 Migration Workflow

When developing new features:

#### Step 1: Develop V2 Features
```bash
# 1. Create new v2 endpoint in API server
/api/v2/components/search-enhanced
/api/v2/context/ai-powered

# 2. Update MCP server to use v2 for testing
async searchComponentsV2(...) {
  const response = await axios.get(`${this.baseUrl}/api/v2/components/search-enhanced`);
  return response.data; // Handle new response format
}
```

#### Step 2: Test V2 Implementation
```bash
# Test v2 endpoints with comprehensive validation
python3 run_all_tests.py master_test_config.json --categories api_v2

# Validate v2 functionality works as expected
node test_v2_client.mjs
```

#### Step 3: Stabilize and Replace V1
```bash
# Once v2 is stable and tested:

# 1. Replace v1 endpoints with v2 implementation
#    /api/v1/components/search now uses v2 logic internally
#    /api/v2/components/search remains for compatibility

# 2. Update MCP server to use simplified v1 endpoints
#    Remove v2-specific handling
#    Use consistent response format

# 3. Update all tests to use v1 endpoints only
#    Remove v2 test categories
#    Ensure all functionality works with v1
```

#### Step 4: Cleanup
```bash
# Once migration is complete:

# 1. Archive old v1 implementation (if needed)
# 2. Remove v2 endpoints (or keep for future migration)
# 3. Update documentation to reflect current v1 implementation
# 4. Full test suite validation
python3 run_all_tests.py master_test_config.json
```

### 🎯 Key Benefits

1. **Always Stable**: Production always has working v1 API
2. **Safe Development**: New features developed in v2 without risk
3. **Incremental Progress**: Features migrated one by one
4. **Easy Rollback**: If v2 has issues, v1 remains untouched
5. **Clear Testing**: Separate test suites for each version

### 📊 Current Implementation Status

**V1 API (Stable)**
- ✅ `/api/v1/stats` - System statistics
- ✅ `/api/v1/context/set` - Platform context setting
- ✅ `/api/v1/context` - Context retrieval
- ✅ `/api/v1/registries` - Registry listing
- ✅ All endpoints using simple array response format

**V2 API (Ready for Development)**
- 🚧 Available for new feature development
- 🚧 No breaking changes to current v1 implementation

### 🔧 MCP Server Integration

The MCP server currently uses v1 endpoints with simplified response processing:

```typescript
// Simple v1 response handling
const components = result.data || [];  // Direct array access
const registries = result.data || [];  // Direct array access
```

This ensures maximum stability and minimal complexity.

### 📝 Development Guidelines

1. **Never modify v1 endpoints directly** - Always create v2 first
2. **Test v2 thoroughly** before migration
3. **Migrate features incrementally** - one endpoint at a time
4. **Update MCP server after API migration** - maintain compatibility
5. **Run full test suite** after each migration step
6. **Document changes** in this file and API documentation

### 🚀 Next Steps

When ready to develop new features:

1. Create v2 endpoints in the API server
2. Implement enhanced functionality and response formats
3. Create comprehensive v2 test suite
4. Validate v2 functionality works correctly
5. Plan migration strategy for each new feature
6. Execute migration following the workflow above

This strategy ensures we maintain a stable, production-ready system while safely developing and deploying new features.