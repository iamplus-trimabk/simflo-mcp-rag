#!/usr/bin/env python3
"""
Extractors CLI Test Runner

Runs the test suite for the extractors CLI.
"""

import sys
import subprocess
import json
from pathlib import Path

def run_test(test_config):
    """Run a single test case"""
    command = test_config["command"]
    expected_exit_code = test_config.get("expected_exit_code", 0)
    expected_stdout_pattern = test_config.get("expected_stdout_pattern", ".*")
    expected_stderr = test_config.get("expected_stderr", "")
    expected_stderr_pattern = test_config.get("expected_stderr_pattern", ".*")

    print(f"  Running: {test_config['test_name']}")
    print(f"    Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check exit code
        if result.returncode != expected_exit_code:
            print(f"    ❌ Failed: Exit code {result.returncode}, expected {expected_exit_code}")
            if result.stderr:
                print(f"    Stderr: {result.stderr.strip()}")
            return False

        # Check stdout pattern
        import re
        if not re.search(expected_stdout_pattern, result.stdout, re.DOTALL):
            print(f"    ❌ Failed: Stdout doesn't match pattern")
            print(f"    Expected pattern: {expected_stdout_pattern}")
            print(f"    Actual stdout: {result.stdout[:200]}...")
            return False

        # Check stderr pattern if specified
        if expected_stderr_pattern and not re.search(expected_stderr_pattern, result.stderr, re.DOTALL):
            print(f"    ❌ Failed: Stderr doesn't match pattern")
            print(f"    Expected pattern: {expected_stderr_pattern}")
            print(f"    Actual stderr: {result.stderr}")
            return False

        print(f"    ✅ Passed")
        return True

    except subprocess.TimeoutExpired:
        print(f"    ❌ Failed: Command timed out")
        return False
    except Exception as e:
        print(f"    ❌ Failed: Exception occurred: {e}")
        return False

def main():
    """Main test runner"""
    test_file = Path(__file__).parent / "extractor_tests.json"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)

    with open(test_file, 'r') as f:
        test_config = json.load(f)

    print(f"Running Extractors CLI Test Suite")
    print(f"Description: {test_config['description']}")
    print(f"Total tests: {len(test_config['tests'])}")
    print()

    passed = 0
    total = len(test_config['tests'])

    for test in test_config['tests']:
        if run_test(test):
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()