# Testing Framework Usage Examples

## Quick Start Examples

### 1. Run All Tests (Basic)
```bash
cd /Users/tbardale/v2/simflo-mcp-rag/testing
python run_all_tests.py mcp_server_tests.json
```

### 2. Run with Detailed Report
```bash
python run_all_tests.py mcp_server_tests.json --output detailed_report.json
```

### 3. Run Specific Categories
```bash
# Only build tests
python run_all_tests.py mcp_server_tests.json --categories build

# Build and tools validation (most critical)
python run_all_tests.py mcp_server_tests.json --categories build tools_list

# API and integration tests
python run_all_tests.py mcp_server_tests.json --categories api integration
```

### 4. Quick Health Check
```bash
# Before committing changes
python run_all_tests.py mcp_server_tests.json --categories build tools_list api
```

## Development Workflow Integration

### Pre-commit Hook (add to .git/hooks/pre-commit)
```bash
#!/bin/bash
echo "Running pre-commit tests..."
cd testing
python run_all_tests.py mcp_server_tests.json --categories build tools_list

if [ $? -ne 0 ]; then
    echo "❌ Pre-commit tests failed. Please fix issues before committing."
    exit 1
fi

echo "✅ Pre-commit tests passed."
exit 0
```

### GitHub Actions Workflow (.github/workflows/test.yml)
```yaml
name: MCP Server Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        npm ci
        pip install -r requirements.txt  # if you have any

    - name: Run comprehensive tests
      run: |
        cd testing
        python run_all_tests.py mcp_server_tests.json --output test_results.json

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: testing/test_results.json
```

## CI/CD Integration Examples

### 1. Basic Pipeline Check
```bash
# In your CI pipeline
echo "Running MCP server validation..."
cd testing

# Critical tests only (fast execution)
python run_all_tests.py mcp_server_tests.json --categories build tools_list

if [ $? -eq 0 ]; then
    echo "✅ Critical tests passed"
else
    echo "❌ Critical tests failed"
    exit 1
fi
```

### 2. Release Validation
```bash
# Before releasing a new version
echo "Running full validation suite..."
cd testing

# Complete test suite with detailed reporting
python run_all_tests.py mcp_server_tests.json --output release_validation.json

# Check pass rate
python -c "
import json
with open('release_validation.json') as f:
    data = json.load(f)

pass_rate = data['statistics']['pass_rate']
if pass_rate < 100:
    print(f'❌ Release validation failed: {pass_rate:.1f}% pass rate')
    exit(1)
else:
    print(f'✅ Release validation passed: {pass_rate:.1f}% pass rate')
"
```

## Debugging Failed Tests

### 1. Run Individual Tests
```bash
# Get detailed output for a specific test
python test_runner.py mcp_server_tests.json
```

### 2. Manual Command Testing
```bash
# If a test fails, run the command manually to see what's wrong
# Example: Test TS-001 (TypeScript compilation)
cd /Users/tbardale/v2/simflo-mcp-rag/mcp-server
npm run build

# Example: Test TL-002 (tool names check)
grep -c "name: '\\(search_components\\|get_component_details\\|get_component_installation\\|list_components\\|set_platform_context\\|get_platform_context\\|list_registries\\)'" dist/index.js
```

### 3. Check Test Configuration
```bash
# Validate test configuration
python -c "
import json
with open('mcp_server_tests.json') as f:
    config = json.load(f)

print(f'Total tests: {len(config[\"tests\"])}')
print(f'Categories: {list(config[\"test_categories\"].keys())}')

# Check for common issues
for test in config['tests']:
    if 'command' not in test:
        print(f'❌ Missing command in test: {test.get(\"test_id\", \"unknown\")}')
"
```

## Creating Custom Test Suites

### 1. Create New Test Configuration
```json
{
  "test_suite": {
    "name": "Custom Test Suite",
    "description": "Focused tests for specific functionality"
  },
  "tests": [
    {
      "test_id": "CUSTOM-001",
      "name": "Verify specific functionality",
      "description": "Test custom feature",
      "command": "your-test-command-here",
      "expect_exit_code": {"type": "exit_code", "value": 0}
    }
  ]
}
```

### 2. Add Validation Types
```python
# In test_runner.py, add to ValidationType enum
class ValidationType(Enum):
    # ... existing types ...
    CUSTOM_REGEX = "custom_regex"  # Your custom validation
```

### 3. Run Custom Suite
```bash
python run_all_tests.py my_custom_tests.json
```

## Performance Monitoring

### 1. Benchmark Test Execution
```bash
# Run tests multiple times to check performance
for i in {1..5}; do
    echo "Run $i:"
    python run_all_tests.py mcp_server_tests.json --categories build tools_list | grep "Execution Time"
done
```

### 2. Generate Performance Report
```bash
# Run full suite and analyze performance
python run_all_tests.py mcp_server_tests.json --output perf_report.json

# Extract performance data
python -c "
import json
with open('perf_report.json') as f:
    data = json.load(f)

perf = data['performance_analysis']
print(f'Slowest tests:')
for test in perf['slowest_tests']:
    print(f'  {test[\"test_id\"]}: {test[\"execution_time\"]:.2f}s')
print(f'Average execution time: {perf[\"average_execution_time\"]:.2f}s')
"
```

## Troubleshooting Common Issues

### 1. Command Not Found Errors
```bash
# Check if the command exists in the test environment
which node
which npm
which curl

# Verify working directory
pwd
ls -la
```

### 2. Permission Issues
```bash
# Make sure test files are executable
chmod +x testing/*.py

# Check file permissions
ls -la testing/
```

### 3. Timeout Issues
```bash
# Increase timeout for specific tests
# Edit the JSON test configuration:
{
  "timeout": 60  # Increase from default 30 seconds
}
```

### 4. Environment Issues
```bash
# Set environment variables for tests
export API_BASE_URL=http://localhost:8000
export LOG_LEVEL=debug

# Or specify in test configuration:
{
  "env": {
    "API_BASE_URL": "http://localhost:8000",
    "LOG_LEVEL": "debug"
  }
}
```

## Best Practices

### 1. Test Organization
- Group related tests into categories
- Use descriptive test IDs and names
- Include clear descriptions for each test
- Keep tests focused and independent

### 2. Validation Strategy
- Use appropriate validation types for each test
- Include both positive and negative test cases
- Validate both success and failure scenarios
- Add custom validation for complex scenarios

### 3. Performance Considerations
- Set reasonable timeouts for each test
- Avoid expensive operations in frequently run tests
- Use category filtering for development workflows
- Monitor execution times and optimize slow tests

### 4. Maintenance
- Regularly review and update test configurations
- Remove obsolete tests
- Add tests for new features and bug fixes
- Keep documentation up to date

This comprehensive testing framework ensures robust validation of your MCP server and prevents issues like the missing 3 tools problem from reaching production.