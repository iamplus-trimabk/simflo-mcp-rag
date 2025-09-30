#!/usr/bin/env python3
"""
Command Test Executor

A comprehensive test execution engine for running CLI commands with JSON-based test definitions.
Supports stdin input, output validation, timeout control, and detailed test reporting.
"""

import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_name: str
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    error_message: Optional[str] = None
    expected_pattern_matched: bool = False


class TestDefinition:
    """Represents a single test definition"""

    def __init__(self, test_data: Dict[str, Any]):
        self.test_name = test_data.get("test_name", "Unnamed Test")
        self.description = test_data.get("description", "")
        self.command = test_data.get("command", "")
        self.stdin = test_data.get("stdin")
        self.expected_exit_code = test_data.get("expected_exit_code", 0)
        self.expected_stdout_pattern = test_data.get("expected_stdout_pattern")
        self.expected_stderr = test_data.get("expected_stderr", "")
        self.expected_stderr_pattern = test_data.get("expected_stderr_pattern")
        self.timeout = test_data.get("timeout", 10)
        self.setup_commands = test_data.get("setup_commands", [])
        self.teardown_commands = test_data.get("teardown_commands", [])

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate the test definition"""
        if not self.test_name:
            return False, "Test name is required"
        if not self.command:
            return False, "Command is required"
        if self.timeout <= 0:
            return False, "Timeout must be positive"
        return True, None


class CommandTestExecutor:
    """Main test execution engine"""

    def __init__(self, working_dir: Optional[str] = None, verbose: bool = False):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.verbose = verbose
        self.results: List[TestResult] = []

    def _execute_command(self, command: str, stdin_input: Optional[str] = None,
                        timeout: int = 10) -> Tuple[int, str, str, float]:
        """Execute a single command and return exit code, stdout, stderr, and execution time"""
        start_time = time.time()

        try:
            # Set up the process
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE if stdin_input else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_dir,
                env=os.environ.copy()
            )

            # Send stdin input if provided
            stdin_bytes = stdin_input.encode('utf-8') if stdin_input else None

            try:
                stdout, stderr = process.communicate(input=stdin_bytes, timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                stderr += f"\nTest timeout after {timeout} seconds"

        except Exception as e:
            return -1, "", f"Command execution failed: {str(e)}", 0

        execution_time = time.time() - start_time
        return exit_code, stdout, stderr, execution_time

    def _run_setup_commands(self, setup_commands: List[str]) -> bool:
        """Run setup commands before the main test"""
        for cmd in setup_commands:
            if self.verbose:
                print(f"  Setup: {cmd}")
            exit_code, _, stderr, _ = self._execute_command(cmd, timeout=5)
            if exit_code != 0:
                print(f"Setup command failed: {cmd}")
                print(f"Error: {stderr}")
                return False
        return True

    def _run_teardown_commands(self, teardown_commands: List[str]) -> bool:
        """Run teardown commands after the main test"""
        for cmd in teardown_commands:
            if self.verbose:
                print(f"  Teardown: {cmd}")
            exit_code, _, stderr, _ = self._execute_command(cmd, timeout=5)
            if exit_code != 0:
                print(f"Teardown command failed: {cmd}")
                print(f"Error: {stderr}")
                return False
        return True

    def _validate_output(self, stdout: str, stderr: str, exit_code: int,
                        test_def: TestDefinition) -> Tuple[bool, Optional[str]]:
        """Validate command output against expectations"""
        # Check exit code
        if exit_code != test_def.expected_exit_code:
            return False, f"Expected exit code {test_def.expected_exit_code}, got {exit_code}"

        # Check stdout pattern
        if test_def.expected_stdout_pattern:
            pattern = re.compile(test_def.expected_stdout_pattern, re.DOTALL)
            if not pattern.search(stdout):
                return False, f"Stdout does not match expected pattern: {test_def.expected_stdout_pattern}"

        # Check exact stderr match
        if test_def.expected_stderr is not None:
            if stderr.strip() != test_def.expected_stderr.strip():
                return False, f"Expected stderr: '{test_def.expected_stderr}', got: '{stderr.strip()}'"

        # Check stderr pattern
        if test_def.expected_stderr_pattern:
            pattern = re.compile(test_def.expected_stderr_pattern, re.DOTALL)
            if not pattern.search(stderr):
                return False, f"Stderr does not match expected pattern: {test_def.expected_stderr_pattern}"

        return True, None

    def execute_test(self, test_def: TestDefinition) -> TestResult:
        """Execute a single test"""
        if self.verbose:
            print(f"\n🧪 Running test: {test_def.test_name}")
            print(f"📝 Description: {test_def.description}")
            print(f"⚡ Command: {test_def.command}")

        # Run setup commands
        if test_def.setup_commands and not self._run_setup_commands(test_def.setup_commands):
            return TestResult(
                test_name=test_def.test_name,
                passed=False,
                exit_code=-1,
                stdout="",
                stderr="Setup commands failed",
                execution_time=0,
                error_message="Setup commands failed"
            )

        # Execute the main command
        exit_code, stdout, stderr, execution_time = self._execute_command(
            test_def.command,
            test_def.stdin,
            test_def.timeout
        )

        # Validate output
        validation_passed, error_message = self._validate_output(
            stdout, stderr, exit_code, test_def
        )

        # Run teardown commands
        if test_def.teardown_commands:
            self._run_teardown_commands(test_def.teardown_commands)

        result = TestResult(
            test_name=test_def.test_name,
            passed=validation_passed,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            error_message=error_message,
            expected_pattern_matched=bool(validation_passed)
        )

        if self.verbose:
            if result.passed:
                print(f"✅ Test passed in {execution_time:.2f}s")
            else:
                print(f"❌ Test failed: {error_message}")
                if stdout.strip():
                    print(f"📤 Stdout:\n{stdout}")
                if stderr.strip():
                    print(f"📥 Stderr:\n{stderr}")

        return result

    def load_tests_from_file(self, test_file: Path) -> List[TestDefinition]:
        """Load test definitions from a JSON file"""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)

            tests = []
            if isinstance(test_data, list):
                test_list = test_data
            elif isinstance(test_data, dict) and "tests" in test_data:
                test_list = test_data["tests"]
            else:
                raise ValueError("Invalid test file format. Expected list or object with 'tests' key.")

            for test_item in test_list:
                test_def = TestDefinition(test_item)
                is_valid, error = test_def.validate()
                if not is_valid:
                    print(f"⚠️  Invalid test definition '{test_def.test_name}': {error}")
                    continue
                tests.append(test_def)

            return tests

        except Exception as e:
            print(f"❌ Failed to load test file {test_file}: {e}")
            return []

    def run_tests_from_file(self, test_file: Union[str, Path]) -> List[TestResult]:
        """Run all tests from a JSON file"""
        test_file = Path(test_file)
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return []

        tests = self.load_tests_from_file(test_file)
        if not tests:
            print(f"⚠️  No valid tests found in {test_file}")
            return []

        print(f"🚀 Running {len(tests)} tests from {test_file}")

        file_results = []
        for test_def in tests:
            result = self.execute_test(test_def)
            file_results.append(result)
            self.results.append(result)

        return file_results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        total_time = sum(r.execution_time for r in self.results)

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time": total_time,
                "timestamp": datetime.now().isoformat()
            },
            "results": []
        }

        for result in self.results:
            result_data = {
                "test_name": result.test_name,
                "passed": result.passed,
                "exit_code": result.exit_code,
                "execution_time": result.execution_time,
                "error_message": result.error_message
            }

            if self.verbose or not result.passed:
                result_data["stdout"] = result.stdout
                result_data["stderr"] = result.stderr

            report["results"].append(result_data)

        return report

    def print_summary(self):
        """Print a summary of test results"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        total_time = sum(r.execution_time for r in self.results)

        print(f"\n📊 Test Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   📈 Success rate: 0%")
        print(f"   ⏱️  Total time: {total_time:.2f}s")

        if failed_tests > 0:
            print(f"\n❌ Failed tests:")
            for result in self.results:
                if not result.passed:
                    print(f"   - {result.test_name}: {result.error_message}")


def main():
    """Main entry point for the test executor"""
    import argparse

    parser = argparse.ArgumentParser(description="Execute CLI command tests from JSON definitions")
    parser.add_argument("test_file", help="JSON file containing test definitions")
    parser.add_argument("--working-dir", help="Working directory for command execution")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", "-o", help="Output file for test report (JSON format)")

    args = parser.parse_args()

    executor = CommandTestExecutor(
        working_dir=args.working_dir,
        verbose=args.verbose
    )

    # Run tests
    results = executor.run_tests_from_file(args.test_file)

    # Print summary
    executor.print_summary()

    # Generate report
    report = executor.generate_report()

    # Save report if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()