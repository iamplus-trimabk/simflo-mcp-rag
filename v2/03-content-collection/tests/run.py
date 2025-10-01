#!/usr/bin/env python3
"""
Content Collection Test Runner

Runs comprehensive test suite for the Content Collection CLI.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tests.cmd_test_executor import TestExecutor
except ImportError:
    # Fallback implementation
    class TestExecutor:
        def __init__(self):
            self.results = []

        def run_test_file(self, test_file: str, verbose: bool = False) -> Dict[str, Any]:
            """Run tests from a JSON test file"""
            with open(test_file, 'r') as f:
                test_data = json.load(f)

            results = {
                "test_file": test_file,
                "total_tests": len(test_data["tests"]),
                "passed": 0,
                "failed": 0,
                "start_time": datetime.now().isoformat(),
                "tests": []
            }

            for test in test_data["tests"]:
                test_result = self._run_single_test(test, verbose)
                results["tests"].append(test_result)
                if test_result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1

            results["end_time"] = datetime.now().isoformat()
            results["success_rate"] = (results["passed"] / results["total_tests"]) * 100

            return results

        def _run_single_test(self, test: Dict[str, Any], verbose: bool) -> Dict[str, Any]:
            """Run a single test case"""
            import re
            import shlex

            try:
                # Parse and execute command
                cmd = shlex.split(test["command"])
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                # Check exit code
                exit_code_match = result.returncode == test["expected_exit_code"]

                # Check stdout pattern
                stdout_match = True
                if "expected_stdout_pattern" in test:
                    stdout_match = bool(re.search(
                        test["expected_stdout_pattern"],
                        result.stdout,
                        re.DOTALL
                    ))

                # Check stderr
                stderr_match = True
                if "expected_stderr" in test:
                    stderr_match = test["expected_stderr"] in result.stderr
                elif "expected_stderr_pattern" in test:
                    stderr_match = bool(re.search(
                        test["expected_stderr_pattern"],
                        result.stderr,
                        re.DOTALL
                    ))

                passed = exit_code_match and stdout_match and stderr_match

                return {
                    "test_name": test["test_name"],
                    "description": test["description"],
                    "passed": passed,
                    "command": test["command"],
                    "expected_exit_code": test["expected_exit_code"],
                    "actual_exit_code": result.returncode,
                    "stdout": result.stdout[:500] if verbose else "",
                    "stderr": result.stderr[:500] if verbose else "",
                    "execution_time": 0  # Placeholder
                }

            except subprocess.TimeoutExpired:
                return {
                    "test_name": test["test_name"],
                    "description": test["description"],
                    "passed": False,
                    "error": "Test timed out",
                    "command": test["command"]
                }
            except Exception as e:
                return {
                    "test_name": test["test_name"],
                    "description": test["description"],
                    "passed": False,
                    "error": str(e),
                    "command": test["command"]
                }

def run_tests(verbose: bool = False) -> Dict[str, Any]:
    """Run all Content Collection tests"""
    test_executor = TestExecutor()

    # Find test files
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("*_tests.json"))

    if not test_files:
        return {
            "error": "No test files found",
            "test_directory": str(test_dir)
        }

    all_results = {
        "component": "03-content-collection",
        "test_files_run": len(test_files),
        "total_tests": 0,
        "total_passed": 0,
        "total_failed": 0,
        "overall_success_rate": 0,
        "start_time": datetime.now().isoformat(),
        "file_results": []
    }

    for test_file in test_files:
        try:
            file_result = test_executor.run_test_file(str(test_file), verbose)
            all_results["file_results"].append(file_result)
            all_results["total_tests"] += file_result["total_tests"]
            all_results["total_passed"] += file_result["passed"]
            all_results["total_failed"] += file_result["failed"]
        except Exception as e:
            all_results["file_results"].append({
                "test_file": str(test_file),
                "error": str(e),
                "total_tests": 0,
                "passed": 0,
                "failed": 0
            })

    all_results["end_time"] = datetime.now().isoformat()
    if all_results["total_tests"] > 0:
        all_results["overall_success_rate"] = (all_results["total_passed"] / all_results["total_tests"]) * 100

    return all_results

def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Content Collection tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Output file for results (JSON)")
    args = parser.parse_args()

    print("🧪 Running Content Collection Test Suite...")
    print("=" * 50)

    results = run_tests(args.verbose)

    # Display summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Test Files: {results['test_files_run']}")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['total_passed']}")
    print(f"   Failed: {results['total_failed']}")
    print(f"   Success Rate: {results['overall_success_rate']:.1f}%")

    if results['overall_success_rate'] == 100:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        if args.verbose:
            for file_result in results['file_results']:
                if file_result.get('failed', 0) > 0:
                    print(f"\nFailed tests in {file_result.get('test_file', 'unknown')}:")
                    for test in file_result.get('tests', []):
                        if not test.get('passed', True):
                            print(f"  ❌ {test.get('test_name', 'unknown')}: {test.get('description', 'unknown')}")

    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if results['overall_success_rate'] == 100 else 1)

if __name__ == '__main__':
    main()