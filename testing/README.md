# SimFlo MCP RAG Testing Framework

A comprehensive testing framework for validating the MCP server functionality, build process, and integration endpoints.

## Quick Start

### Run All Tests
```bash
cd /Users/tbardale/v2/simflo-mcp-rag/testing
python run_all_tests.py mcp_server_tests.json
```

### Run Specific Categories
```bash
# Run only build tests
python run_all_tests.py mcp_server_tests.json --categories build

# Run build and tools_list tests
python run_all_tests.py mcp_server_tests.json --categories build tools_list

# Run all tests and save detailed report
python run_all_tests.py mcp_server_tests.json --output test_report.json
```

### Run Individual Test with Debug Info
```bash
python test_runner.py mcp_server_tests.json json
```

## Test Categories

### 🔍 Code Presence Tests (`01-code_presence_tests.json`)
- **CP-001**: MCP Server source file exists
- **CP-002**: Required MCP tools code present
- **CP-003**: Context tools implementation present
- **CP-004**: API server Python file exists
- **CP-005**: Data pipeline Python files present

### 🧹 Lint Tests (`02-lint_tests.json`)
- **LINT-001**: TypeScript lint success
- **LINT-002**: TypeScript type check
- **LINT-003**: Python syntax check
- **LINT-004**: Testing framework Python lint

### 🏗️ Build Tests (`03-build_tests.json`)
- **BLD-001**: TypeScript compilation success
- **BLD-002**: Distribution directory creation
- **BLD-003**: JavaScript file generation

### 📋 Tools List Tests (`04-tools_list_tests.json`) - **CRITICAL**
- **TL-001**: Exactly 7 tools in tools list 🔥 **Would have caught missing 3 tools issue**
- **TL-002**: Required tool names present
- **TL-003**: Context tools present
- **TL-004**: Platform parameter validation
- **TL-005**: Registry parameter validation

### 🌐 API Tests (`05-api_tests.json`)
- **API-001**: API server health check
- **API-002**: V2 context endpoints available
- **API-003**: Context setting functionality
- **API-004**: Registry listing functionality

### 🔧 MCP Tests (`06-mcp_tests.json`)
- **MCP-001**: MCP server startup
- **MCP-002**: MCP server process check
- **MCP-003**: MCP client tools discovery (using MCP SDK)
- **MCP-004**: MCP client tool execution (using MCP SDK)

### 🔄 End-to-End Tests (`end_to_end`)
- **E2E-001**: Complete build and validation
- **E2E-002**: Tools count verification 🔥 **Critical for detecting missing tools**
- **E2E-003**: Schema validation
- **E2E-004**: Handler implementation check

### 🔗 Integration Tests (`integration`)
- **INT-001**: API server integration
- **INT-002**: Context-aware search
- **INT-003**: Registry management

### ⚡ Performance Tests (`performance`)
- **PERF-001**: Build performance
- **PERF-002**: API response time

### 🔒 Security Tests (`security`)
- **SEC-001**: No hardcoded secrets
- **SEC-002**: Environment variable usage

## Key Features

### 🔍 Comprehensive Validation
- **Exact matching**: String equality validation
- **Pattern matching**: Regex and substring validation
- **Exit code validation**: Process exit status checking
- **Custom validation**: Flexible validation logic
- **JSON validation**: Structured data validation

### 📊 Detailed Reporting
- **Real-time progress**: Live test execution feedback
- **Category analysis**: Pass/fail rates by test category
- **Failure analysis**: Pattern detection and root cause analysis
- **Performance metrics**: Execution time and slowest tests
- **Actionable recommendations**: Specific improvement suggestions

### 🚀 Developer Experience
- **Human-readable output**: Clear status indicators and error messages
- **JSON export**: Machine-readable results for CI/CD integration
- **Flexible execution**: Run specific categories or all tests
- **Debugging support**: Full stdout/stderr capture for failed tests

## How This Prevents Issues Like the Missing 3 Tools Problem

The original issue where 3 MCP tools were missing from the tools list would have been caught by multiple validation layers:

### 🔍 Code Presence Validation
- **CP-002**: Would fail if tools are not defined in source code
- **CP-003**: Would specifically fail if context tools are missing

### 🧹 Lint Validation
- **LINT-001/LINT-002**: Would catch TypeScript errors preventing proper compilation

### 🏗️ Build Validation
- **BLD-001**: Would fail if MCP server cannot compile

### 📋 Tools List Validation
- **TL-001**: Explicitly checks for exactly 7 tools
- **TL-003**: Verifies the 3 context-aware tools specifically
- **Category analysis**: Tools list category would show 60% pass rate (3/5 tests passing)

### 🔧 MCP Client Testing
- **MCP-003**: Would discover only 4 tools instead of 7
- **MCP-004**: Would fail to execute missing tools

This comprehensive validation ensures issues are caught at the earliest possible stage in the development workflow.

## Integration with Development Workflow

### Pre-commit Checks
```bash
# Run critical tests before committing (following logical development sequence)
python run_all_tests.py master_test_config.json --master --categories code_presence lint build tools_list
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Run MCP Server Tests
  run: |
    cd testing
    python run_all_tests.py master_test_config.json --master --output test_results.json
```

### Manual Testing
```bash
# Quick health check
python run_all_tests.py mcp_server_tests.json --categories api

# Full validation before release
python run_all_tests.py mcp_server_tests.json --output release_validation.json
```

## Test Configuration

Tests are defined in JSON format with the following structure:

```json
{
  "test_id": "TEST-001",
  "name": "Human-readable test name",
  "description": "Detailed test description",
  "command": "shell command to execute",
  "expect_exit_code": {"type": "exit_code", "value": 0},
  "expect_stdout": {"type": "contains", "value": "expected string"},
  "expect_stderr": {"type": "none", "value": ""},
  "timeout": 30
}
```

### Validation Types
- **exact**: Exact string match
- **contains**: Substring match
- **regex**: Regular expression match
- **contains_all**: Contains all strings in a list
- **exit_code**: Specific exit code
- **none**: No validation (command should succeed)

## Adding New Tests

1. **Create test configuration**: Add to appropriate JSON file
2. **Update categories**: Add test ID to relevant category in `test_categories`
3. **Test locally**: Verify the test works as expected
4. **Document**: Add description and purpose to README

## Troubleshooting

### Common Issues

**Test fails intermittently**: Increase timeout or add retry logic
**Command not found**: Ensure dependencies are installed and paths are correct
**Permission errors**: Check file permissions and user access rights
**Network timeouts**: Increase timeout values for network-dependent tests

### Debug Mode
Run individual tests with detailed output:
```bash
python test_runner.py mcp_server_tests.json
```

### Custom Validation
For complex validation logic, use the `custom_validation` field with lambda expressions.

## Future Enhancements

- [ ] Parallel test execution
- [ ] Test result history and trending
- [ ] Integration with IDEs
- [ ] Performance benchmarking
- [ ] Cross-platform compatibility testing
- [ ] Load testing capabilities

## Contributing

1. Follow the existing test structure and naming conventions
2. Add descriptive test names and documentation
3. Include tests for both success and failure scenarios
4. Ensure tests are deterministic and repeatable
5. Add tests for new features and bug fixes

This framework ensures comprehensive validation of the MCP server and prevents regressions like the missing 3 tools issue.