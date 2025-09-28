#!/usr/bin/env python3
"""
Main Test Runner for SimFlo MCP RAG

Runs comprehensive test suites and generates detailed reports with
failure analysis and recommendations.
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from test_runner import TestRunner, TestResult, ValidationResult

class ComprehensiveTestRunner:
    """Enhanced test runner with comprehensive reporting and analysis"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_runner = TestRunner(working_dir=str(self.project_root))
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None

    def run_master_config(self, master_config_file: str, categories: List[str] = None) -> Dict[str, Any]:
        """Run test suites from master configuration in logical order"""
        self.start_time = datetime.now()
        print(f"🚀 Running Master Test Configuration")
        print(f"📁 Master Config: {master_config_file}")

        with open(master_config_file, 'r') as f:
            master_config = json.load(f)

        test_suite_info = master_config.get('test_suite', {})
        execution_order = test_suite_info.get('execution_order', [])
        test_suites = master_config.get('test_suites', {})

        all_results = []

        for category in execution_order:
            if categories and category not in categories:
                print(f"⏭️  Skipping category: {category}")
                continue

            if category not in test_suites:
                print(f"⚠️  Warning: No test suite found for category: {category}")
                continue

            suite_file = test_suites[category]
            print(f"\n🔍 Running {category.upper()} tests from: {suite_file}")

            suite_results = self.run_test_suite(suite_file)
            # Extract detailed results from the report and convert back to TestResult objects
            suite_test_results = [self._dict_to_result(r) for r in suite_results.get('detailed_results', [])]
            all_results.extend(suite_test_results)

        self.end_time = datetime.now()
        execution_time = (self.end_time - self.start_time).total_seconds()

        # Generate comprehensive report
        return self._generate_comprehensive_report(all_results, {})

    def run_test_suite(self, test_config_file: str, categories: List[str] = None) -> Dict[str, Any]:
        """Run a complete test suite with detailed reporting"""
        self.start_time = datetime.now()

        print(f"🚀 Starting comprehensive test run...")
        print(f"📁 Project Root: {self.project_root}")
        print(f"📋 Test Config: {test_config_file}")
        print("=" * 60)

        # Load test configuration
        try:
            with open(test_config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load test configuration: {e}")
            return {"error": str(e)}

        # Filter tests by category if specified
        tests = config.get("tests", [])
        test_categories = config.get("test_categories", {})

        if categories:
            filtered_tests = []
            for category in categories:
                if category in test_categories:
                    category_tests = [test for test in tests if test["test_id"] in test_categories[category]]
                    filtered_tests.extend(category_tests)
            tests = filtered_tests
            print(f"🎯 Running tests from categories: {', '.join(categories)}")
        else:
            print(f"📊 Running all {len(tests)} tests")

        # Run all tests
        print("\n🔬 Executing tests...")
        print("-" * 60)

        results = []
        for i, test_config in enumerate(tests, 1):
            test_id = test_config.get("test_id", "unknown")
            test_name = test_config.get("name", "Unnamed Test")

            print(f"[{i:2d}/{len(tests)}] {test_id}: {test_name}")

            result = self.test_runner.run_single_test(test_config)
            results.append(result)

            # Print immediate result
            status = "✅ PASS" if result.passed else "❌ FAIL"
            time_str = f"({result.execution_time:.2f}s)"
            print(f"      {status} {time_str}")

            if not result.passed and result.error_message:
                # Print truncated error message
                error_lines = result.error_message.split('\n')[:2]
                for line in error_lines:
                    print(f"      {line}")

        self.end_time = datetime.now()
        self.results = results

        # Generate comprehensive report
        report = self._generate_comprehensive_report(results, config)

        return report

    def _generate_comprehensive_report(self, results: List[TestResult], config: Dict) -> Dict[str, Any]:
        """Generate detailed test report with analysis"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        execution_time = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        # Basic statistics
        stats = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": execution_time,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }

        # Category-based analysis
        test_categories = config.get("test_categories", {})
        category_stats = {}
        for category, test_ids in test_categories.items():
            category_results = [r for r in results if r.test_id in test_ids]
            category_passed = sum(1 for r in category_results if r.passed)
            category_stats[category] = {
                "total": len(category_results),
                "passed": category_passed,
                "failed": len(category_results) - category_passed,
                "pass_rate": (category_passed / len(category_results) * 100) if category_results else 0
            }

        # Failure analysis
        failed_results = [r for r in results if not r.passed]
        failure_analysis = self._analyze_failures(failed_results)

        # Performance analysis
        slow_tests = sorted(results, key=lambda x: x.execution_time, reverse=True)[:5]
        performance_analysis = {
            "slowest_tests": [
                {
                    "test_id": t.test_id,
                    "name": t.name,
                    "execution_time": t.execution_time
                } for t in slow_tests
            ],
            "average_execution_time": sum(r.execution_time for r in results) / len(results) if results else 0
        }

        # Recommendations
        recommendations = self._generate_recommendations(stats, category_stats, failure_analysis)

        return {
            "metadata": {
                "test_suite": config.get("test_suite", {}),
                "generated_at": datetime.now().isoformat(),
                "runner_version": "1.0.0"
            },
            "statistics": stats,
            "category_analysis": category_stats,
            "failure_analysis": failure_analysis,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "detailed_results": [self._result_to_dict(r) for r in results]
        }

    def _result_to_dict(self, result: TestResult) -> Dict[str, Any]:
        """Convert TestResult to dictionary for JSON serialization"""
        return {
            "test_id": result.test_id,
            "name": result.name,
            "description": result.description,
            "passed": result.passed,
            "execution_time": result.execution_time,
            "exit_code": result.exit_code,
            "error_message": result.error_message,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "validation_results": [
                {
                    "passed": vr.passed,
                    "expected": str(vr.expected),
                    "actual": str(vr.actual),
                    "error_message": vr.error_message
                } for vr in result.validation_results
            ]
        }

    def _dict_to_result(self, result_dict: Dict[str, Any]) -> TestResult:
        """Convert dictionary back to TestResult object"""
        validation_results = []
        for vr_dict in result_dict.get("validation_results", []):
            validation_results.append(ValidationResult(
                passed=vr_dict.get("passed", False),
                expected=vr_dict.get("expected", ""),
                actual=vr_dict.get("actual", ""),
                error_message=vr_dict.get("error_message", "")
            ))

        return TestResult(
            test_id=result_dict.get("test_id", "unknown"),
            name=result_dict.get("name", "Unknown Test"),
            description=result_dict.get("description", ""),
            passed=result_dict.get("passed", False),
            execution_time=result_dict.get("execution_time", 0.0),
            exit_code=result_dict.get("exit_code", 0),
            error_message=result_dict.get("error_message", ""),
            stdout=result_dict.get("stdout", ""),
            stderr=result_dict.get("stderr", ""),
            validation_results=validation_results
        )

    def _analyze_failures(self, failed_results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test failures and identify patterns"""
        if not failed_results:
            return {"total_failures": 0, "failure_patterns": []}

        # Categorize failures by error type
        error_patterns = {}
        for result in failed_results:
            error_type = self._categorize_error(result)
            if error_type not in error_patterns:
                error_patterns[error_type] = []
            error_patterns[error_type].append(result.test_id)

        # Identify critical failures
        critical_failures = [
            r.test_id for r in failed_results
            if any("CRITICAL" in r.name.upper() or "exactly" in r.error_message.lower() for r in [r])
        ]

        return {
            "total_failures": len(failed_results),
            "failure_patterns": [
                {
                    "error_type": error_type,
                    "count": len(test_ids),
                    "affected_tests": test_ids
                }
                for error_type, test_ids in error_patterns.items()
            ],
            "critical_failures": critical_failures,
            "failed_test_ids": [r.test_id for r in failed_results]
        }

    def _categorize_error(self, result: TestResult) -> str:
        """Categorize test failure by error type"""
        error_msg = result.error_message.lower()
        stderr = result.stderr.lower()

        if "timeout" in error_msg or "timeout" in stderr:
            return "timeout"
        elif "command not found" in stderr:
            return "command_not_found"
        elif "permission" in error_msg or "permission" in stderr:
            return "permission"
        elif "exit code" in error_msg:
            return "exit_code_mismatch"
        elif "validation" in error_msg:
            return "validation_failure"
        elif "connection" in error_msg or "refused" in stderr:
            return "connection"
        else:
            return "unknown"

    def _generate_recommendations(self, stats: Dict, category_stats: Dict,
                                failure_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Overall pass rate recommendations
        if stats["pass_rate"] < 50:
            recommendations.append("🚨 CRITICAL: Low overall pass rate. Immediate attention required.")
        elif stats["pass_rate"] < 80:
            recommendations.append("⚠️  WARNING: Pass rate below acceptable threshold. Review failures.")

        # Category-specific recommendations
        for category, cat_stats in category_stats.items():
            if cat_stats["pass_rate"] < 100:
                if category == "build":
                    recommendations.append("🔧 Fix build issues before proceeding with other tests.")
                elif category == "tools_list":
                    recommendations.append("📋 Tools list issues detected. This may indicate missing MCP functionality.")
                elif category == "api":
                    recommendations.append("🌐 API endpoints failing. Check API server configuration.")
                elif category == "security":
                    recommendations.append("🔒 Security issues detected. Review for hardcoded secrets.")

        # Critical failure recommendations
        if failure_analysis.get("critical_failures"):
            recommendations.append(f"🚨 Critical failures detected: {', '.join(failure_analysis['critical_failures'])}")

        # Performance recommendations
        if stats["execution_time"] > 60:
            recommendations.append("⏱️  Test execution time is high. Consider optimizing test performance.")

        # Success recommendations
        if stats["pass_rate"] == 100:
            recommendations.append("🎉 All tests passed! System is functioning correctly.")

        return recommendations

    def print_summary_report(self, report: Dict[str, Any]):
        """Print human-readable summary report"""
        stats = report["statistics"]
        recommendations = report["recommendations"]

        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Passed: {stats['passed_tests']}")
        print(f"Failed: {stats['failed_tests']}")
        print(f"Pass Rate: {stats['pass_rate']:.1f}%")
        print(f"Execution Time: {stats['execution_time']:.2f}s")
        print(f"Duration: {stats['start_time'][:19]} - {stats['end_time'][:19]}")

        # Category breakdown
        if report["category_analysis"]:
            print("\n📂 CATEGORY BREAKDOWN")
            print("-" * 40)
            for category, cat_stats in report["category_analysis"].items():
                status = "✅" if cat_stats["pass_rate"] == 100 else "❌"
                print(f"{status} {category}: {cat_stats['passed']}/{cat_stats['total']} ({cat_stats['pass_rate']:.1f}%)")

        # Failed tests
        if stats["failed_tests"] > 0:
            print("\n❌ FAILED TESTS")
            print("-" * 40)
            failed_results = [r for r in self.results if not r.passed]
            for result in failed_results:
                print(f"  {result.test_id}: {result.name}")
                if result.error_message:
                    print(f"    Error: {result.error_message[:100]}...")

        # Recommendations
        if recommendations:
            print("\n💡 RECOMMENDATIONS")
            print("-" * 40)
            for rec in recommendations:
                print(f"  {rec}")

        print("\n" + "=" * 60)

    def save_report(self, report: Dict[str, Any], filename: str):
        """Save detailed report to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Run comprehensive test suite for SimFlo MCP RAG")
    parser.add_argument("config", help="Test configuration JSON file or master config")
    parser.add_argument("--categories", nargs="+", help="Specific test categories to run")
    parser.add_argument("--output", "-o", help="Output file for detailed JSON report")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--format", choices=["summary", "json"], default="summary",
                       help="Output format")
    parser.add_argument("--master", action="store_true",
                       help="Run as master configuration (multiple test suites)")

    args = parser.parse_args()

    # Initialize test runner
    runner = ComprehensiveTestRunner(args.project_root)

    # Run tests
    if args.master:
        report = runner.run_master_config(args.config, args.categories)
    else:
        report = runner.run_test_suite(args.config, args.categories)

    if "error" in report:
        print(f"❌ Test execution failed: {report['error']}")
        sys.exit(1)

    # Print summary
    runner.print_summary_report(report)

    # Save detailed report if requested
    if args.output:
        runner.save_report(report, args.output)

    # Exit with appropriate code
    failed_tests = report["statistics"]["failed_tests"]
    sys.exit(1 if failed_tests > 0 else 0)


if __name__ == "__main__":
    main()