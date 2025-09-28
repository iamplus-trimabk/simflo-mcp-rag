#!/usr/bin/env python3
"""
Universal Test Runner for SimFlo MCP RAG

A flexible test runner that can execute commands, capture output, and validate results
against expected outcomes with comprehensive reporting.
"""

import json
import subprocess
import re
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import signal


class ValidationType(Enum):
    """Types of validation for test results"""
    EXACT = "exact"           # Exact string match
    CONTAINS = "contains"     # String contains expected value
    REGEX = "regex"          # Regular expression match
    JSON_EQUALS = "json_equals"  # JSON equality
    JSON_SCHEMA = "json_schema"  # JSON schema validation
    EXIT_CODE = "exit_code"   # Specific exit code
    CONTAINS_ALL = "contains_all"  # Contains all expected strings
    GE = "ge"                # Greater than or equal (for numeric values)
    NONE = "none"           # No validation (command should just succeed)


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    passed: bool
    expected: Any
    actual: Any
    error_message: str = ""


@dataclass
class TestResult:
    """Complete test execution result"""
    test_id: str
    name: str
    description: str
    passed: bool
    execution_time: float
    stdout: str
    stderr: str
    exit_code: int
    validation_results: List[ValidationResult]
    error_message: str = ""


class TestRunner:
    """Universal test execution engine"""

    def __init__(self, timeout: int = 30, working_dir: str = None):
        self.timeout = timeout
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.test_results: List[TestResult] = []

    def run_single_test(self, test_config: Dict[str, Any]) -> TestResult:
        """
        Execute a single test with comprehensive validation

        Args:
            test_config: Test configuration dictionary

        Returns:
            TestResult object with detailed execution information
        """
        start_time = time.time()
        test_id = test_config.get("test_id", "unknown")
        name = test_config.get("name", "Unnamed Test")
        description = test_config.get("description", "")

        try:
            # Execute the command
            result = self._execute_command(test_config)

            # Validate results
            validation_results = self._validate_results(test_config, result)

            # Determine overall test result
            all_passed = all(vr.passed for vr in validation_results)

            test_result = TestResult(
                test_id=test_id,
                name=name,
                description=description,
                passed=all_passed,
                execution_time=time.time() - start_time,
                stdout=result['stdout'],
                stderr=result['stderr'],
                exit_code=result['exit_code'],
                validation_results=validation_results,
                error_message="" if all_passed else self._generate_error_message(validation_results)
            )

        except Exception as e:
            test_result = TestResult(
                test_id=test_id,
                name=name,
                description=description,
                passed=False,
                execution_time=time.time() - start_time,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                validation_results=[],
                error_message=f"Test execution failed: {str(e)}"
            )

        self.test_results.append(test_result)
        return test_result

    def _execute_command(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the test command and capture all output"""
        cmd = test_config["command"]
        cwd = self.working_dir / test_config.get("working_dir", ".") if test_config.get("working_dir") else self.working_dir
        env = test_config.get("env", {})
        stdin_input = test_config.get("stdin", "")
        timeout = test_config.get("timeout", self.timeout)

        # Prepare environment
        process_env = dict(os.environ)
        process_env.update(env)

        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=cwd,
                env=process_env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True
            )

            # Send stdin input if provided
            if stdin_input:
                process.stdin.write(stdin_input)
                process.stdin.flush()
                process.stdin.close()

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code
            }

        except Exception as e:
            raise RuntimeError(f"Command execution failed: {str(e)}")

    def _validate_results(self, test_config: Dict[str, Any], result: Dict[str, Any]) -> List[ValidationResult]:
        """Validate test results against expected outcomes"""
        validations = []

        # Exit code validation
        if "expect_exit_code" in test_config:
            expected_exit_config = test_config["expect_exit_code"]
            actual_exit = result["exit_code"]

            # Handle different exit code validation types
            if expected_exit_config.get("type") == "exit_code":
                expected_exit = expected_exit_config.get("value")
                passed = expected_exit == actual_exit
                error_message = f"Expected exit code {expected_exit}, got {actual_exit}"
            else:
                # Default behavior for backward compatibility
                expected_exit = expected_exit_config
                passed = expected_exit == actual_exit
                error_message = f"Expected exit code {expected_exit}, got {actual_exit}"

            validations.append(ValidationResult(
                passed=passed,
                expected=expected_exit,
                actual=actual_exit,
                error_message=error_message
            ))

        # Stdout validation
        if "expect_stdout" in test_config:
            stdout_validation = self._validate_output(
                test_config["expect_stdout"],
                result["stdout"],
                "stdout"
            )
            validations.append(stdout_validation)

        # Stderr validation
        if "expect_stderr" in test_config:
            stderr_validation = self._validate_output(
                test_config["expect_stderr"],
                result["stderr"],
                "stderr"
            )
            validations.append(stderr_validation)

        # Custom validation function
        if "custom_validation" in test_config:
            custom_config = test_config["custom_validation"]
            if isinstance(custom_config, dict) and custom_config.get("type") == "function":
                # Handle lambda-like validation from JSON
                validation_expr = custom_config.get("implementation", "")
                if validation_expr:
                    try:
                        # Simple evaluation for basic validation expressions
                        # Note: This is simplified for security - in production use proper sandboxing
                        if "lambda result:" in validation_expr:
                            # Extract the lambda body
                            lambda_body = validation_expr.split("lambda result:")[-1].strip()
                            # Create a safe evaluation context
                            passed = eval(lambda_body, {"result": result})
                            validations.append(ValidationResult(
                                passed=passed,
                                expected="custom validation",
                                actual="custom validation result",
                                error_message="Custom validation failed" if not passed else ""
                            ))
                        else:
                            # Direct expression evaluation
                            passed = eval(validation_expr, {"result": result})
                            validations.append(ValidationResult(
                                passed=passed,
                                expected="custom validation",
                                actual="custom validation result",
                                error_message="Custom validation failed" if not passed else ""
                            ))
                    except Exception as e:
                        validations.append(ValidationResult(
                            passed=False,
                            expected="custom validation",
                            actual=f"validation error: {str(e)}",
                            error_message=f"Custom validation execution failed: {str(e)}"
                        ))
            elif callable(custom_config):
                # Direct callable function
                custom_result = custom_config(result)
                if isinstance(custom_result, ValidationResult):
                    validations.append(custom_result)
                elif isinstance(custom_result, bool):
                    validations.append(ValidationResult(
                        passed=custom_result,
                        expected="custom validation",
                        actual="custom validation result",
                        error_message="Custom validation failed" if not custom_result else ""
                    ))

        return validations

    def _validate_output(self, expectation: Dict[str, Any], actual: str, output_type: str) -> ValidationResult:
        """Validate output against expectation using specified validation type"""
        validation_type = ValidationType(expectation.get("type", "exact"))
        expected_value = expectation.get("value", "")

        try:
            if validation_type == ValidationType.EXACT:
                passed = actual.strip() == expected_value.strip()
                error_msg = f"Expected exact match in {output_type}" if not passed else ""

            elif validation_type == ValidationType.CONTAINS:
                passed = expected_value in actual
                error_msg = f"Expected '{expected_value}' not found in {output_type}" if not passed else ""

            elif validation_type == ValidationType.REGEX:
                pattern = re.compile(expected_value, re.MULTILINE | re.DOTALL)
                passed = bool(pattern.search(actual))
                error_msg = f"Regex pattern '{expected_value}' not matched in {output_type}" if not passed else ""

            elif validation_type == ValidationType.CONTAINS_ALL:
                if isinstance(expected_value, list):
                    passed = all(value in actual for value in expected_value)
                    missing = [val for val in expected_value if val not in actual]
                    error_msg = f"Missing values in {output_type}: {missing}" if not passed else ""
                else:
                    passed = expected_value in actual
                    error_msg = f"Expected '{expected_value}' not found in {output_type}" if not passed else ""

            elif validation_type == ValidationType.EXIT_CODE:
                # This is handled separately
                passed = True
                error_msg = ""

            elif validation_type == ValidationType.GE:
                # Greater than or equal validation for numeric values
                try:
                    actual_num = float(actual.strip())
                    expected_num = float(expected_value)
                    passed = actual_num >= expected_num
                    error_msg = f"Expected value >= {expected_num}, got {actual_num} in {output_type}" if not passed else ""
                except (ValueError, TypeError):
                    passed = False
                    error_msg = f"Cannot compare non-numeric values in {output_type}: expected >= {expected_value}, got '{actual}'"

            elif validation_type == ValidationType.NONE:
                passed = True
                error_msg = ""

            else:
                passed = False
                error_msg = f"Unknown validation type: {validation_type}"

            return ValidationResult(
                passed=passed,
                expected=expected_value,
                actual=actual[:500] + "..." if len(actual) > 500 else actual,
                error_message=error_msg
            )

        except Exception as e:
            return ValidationResult(
                passed=False,
                expected=expected_value,
                actual=actual,
                error_message=f"Validation failed with error: {str(e)}"
            )

    def _generate_error_message(self, validation_results: List[ValidationResult]) -> str:
        """Generate detailed error message from validation results"""
        failed_validations = [vr for vr in validation_results if not vr.passed]

        if not failed_validations:
            return ""

        error_lines = []
        for i, vr in enumerate(failed_validations, 1):
            error_lines.append(f"{i}. {vr.error_message}")

        return "Validation failures:\n" + "\n".join(error_lines)

    def run_test_suite(self, test_configs: List[Dict[str, Any]]) -> List[TestResult]:
        """Execute multiple tests and return all results"""
        results = []
        for config in test_configs:
            result = self.run_single_test(config)
            results.append(result)

        return results

    def generate_report(self, output_format: str = "json") -> Union[str, Dict]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for tr in self.test_results if tr.passed)
        failed_tests = total_tests - passed_tests

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": sum(tr.execution_time for tr in self.test_results),
            "test_results": [asdict(tr) for tr in self.test_results]
        }

        if output_format == "json":
            return json.dumps(summary, indent=2)
        elif output_format == "summary":
            return self._generate_summary_report(summary)
        else:
            return summary

    def _generate_summary_report(self, summary: Dict) -> str:
        """Generate human-readable summary report"""
        report_lines = [
            "=== Test Execution Summary ===",
            f"Total Tests: {summary['total_tests']}",
            f"Passed: {summary['passed_tests']}",
            f"Failed: {summary['failed_tests']}",
            f"Pass Rate: {summary['pass_rate']:.1f}%",
            f"Total Execution Time: {summary['execution_time']:.2f}s",
            ""
        ]

        if summary['failed_tests'] > 0:
            report_lines.append("=== Failed Tests ===")
            failed_tests = [tr for tr in self.test_results if not tr.passed]
            for test in failed_tests:
                report_lines.append(f"❌ {test.test_id}: {test.name}")
                if test.error_message:
                    report_lines.append(f"   Error: {test.error_message[:100]}...")
            report_lines.append("")

        return "\n".join(report_lines)


def main():
    """Command line interface for test runner"""
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <test_config_file> [output_format]")
        print("Example: python test_runner.py mcp_server_tests.json json")
        sys.exit(1)

    config_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "summary"

    try:
        with open(config_file, 'r') as f:
            test_configs = json.load(f)

        runner = TestRunner()
        results = runner.run_test_suite(test_configs)
        report = runner.generate_report(output_format)

        print(report)

        # Exit with appropriate code
        failed_tests = sum(1 for r in results if not r.passed)
        sys.exit(1 if failed_tests > 0 else 0)

    except Exception as e:
        print(f"Error running tests: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()