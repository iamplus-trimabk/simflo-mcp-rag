# System Integration & Functionality Tasks

## 🎯 Objective
Make simflo-rag v2 a fully functional RAG system with working component integration, reliable tests, and actual search capabilities.

## 📋 Current System Issues Identified

### System Status Assessment
- ✅ CLI commands work individually
- ✅ Sample component data exists
- ✅ Configuration files created
- ❌ Components don't integrate properly (MCP server finds 0 registries)
- ❌ Search returns empty results despite having data
- ❌ Test suite failing (50% pass rate)
- ❌ Vector database functionality missing

---

## Task 1: Fix Core Component Integration Issues

### Problem
CLI commands work individually but don't connect properly:
- MCP server finds 0 registries (should find 5)
- Search returns empty results despite sample data existing
- Path resolution issues between components

### Root Causes Identified
- MCP server looking for wrong registry paths
- Registry search not actually indexing sample files
- Broken component-to-component communication

### Implementation Steps
1. **Fix MCP Server Path Resolution**
   - Update registry manager to use correct paths (`v2/core/00-rag-registry/registries`)
   - Ensure MCP server can detect all 5 registries (shadcn, gluestack, community, radix, test_docs)

2. **Fix Registry Search Functionality**
   - Make registry search actually search through sample markdown files
   - Implement basic text search on component files
   - Return results from shadcn button/dialog and gluestack button

3. **Verify End-to-End Integration**
   - Test: MCP server `list-registries` → should return 5 registries
   - Test: MCP server `search "button"` → should return button components
   - Test: Registry system `search "button"` → should return results

### Success Criteria
- MCP server lists all 5 registries
- Search returns actual component results from sample data
- Component communication works via CLI calls

---

## Task 2: Fix Broken Test Suite

### Problem
Registry tests failing (50% pass rate) due to outdated expectations

### Specific Test Failures Found
1. **info_command**: Expects registry "shadcn_db" but actual is "shadcn"
2. **search_command**: Expects failure but search now succeeds (empty results)
3. **help_command**: Expects old help text format
4. **table_format**: Expects different output structure

### Implementation Steps
1. **Update Test Expectations**
   - Fix registry names in tests (remove "_db" suffix)
   - Update search tests to expect successful empty results
   - Fix help command text expectations
   - Update table format output expectations

2. **Add Missing Test Cases**
   - Test actual search with sample data
   - Test MCP server integration
   - Test RAG builder functionality
   - Test extractor CLI commands

3. **Improve Test Coverage**
   - Add tests for new configuration files
   - Add tests for command aliases
   - Add integration tests between components

### Success Criteria
- All registry tests pass (100% pass rate)
- Tests validate actual working functionality
- Comprehensive coverage of core features

---

## Task 3: Implement Functional Search/Vector Database

### Problem
Sample data exists but search returns empty results - no actual indexing or search functionality

### Missing Functionality
- Vector store implementation (ChromaDB integration)
- Text processing and embedding functionality
- Actual indexing of sample component files

### Implementation Steps
1. **Basic Text Search Implementation**
   - Implement simple keyword search in markdown files
   - Extract component information from sample files
   - Return structured search results

2. **Vector Database Integration**
   - Set up ChromaDB for vector storage
   - Create embeddings from sample component text
   - Index sample components (button, dialog) for search

3. **Search Enhancement**
   - Implement relevance scoring
   - Support multiple search queries
   - Return structured component information

### Success Criteria
- Search returns actual component results
- Vector database contains indexed sample data
- Search relevance and ranking works properly

---

## 🔥 Critical Success Metrics
- **Functional Integration**: All components communicate properly
- **Working Search**: Search returns real component results
- **Reliable Tests**: 100% test pass rate
- **End-to-End Functionality**: AI assistants can discover components

## ⏱️ **Time Estimate: 3-4 hours**
- Task 1 (Integration): 60-90 minutes
- Task 2 (Tests): 60-90 minutes
- Task 3 (Search): 90-120 minutes
- Final verification: 30 minutes