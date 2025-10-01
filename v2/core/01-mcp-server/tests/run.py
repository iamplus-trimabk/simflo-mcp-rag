#!/usr/bin/env python3
"""
MCP Server Test Runner

Runs all MCP server CLI tests using the centralized test execution engine.
"""

import sys
from pathlib import Path

# Add the v2/tests directory to path for imports
tests_dir = Path(__file__).parent.parent.parent.parent / "tests"
sys.path.insert(0, str(tests_dir))

try:
    from cmd_test_executor import CommandTestExecutor
except ImportError as e:
    print(f"Error importing cmd_test_executor: {e}")
    print("Make sure v2/tests/cmd_test_executor.py exists")
    sys.exit(1)


def run_all_tests(test_dir: Path, verbose: bool = False):
    """Run all tests in the test directory"""
    test_files = list(test_dir.glob("*.json"))

    if not test_files:
        print("❌ No test files found")
        return False

    executor = CommandTestExecutor(verbose=verbose)
    all_passed = True

    for test_file in test_files:
        print(f"\n🚀 Running tests from {test_file.name}")
        results = executor.run_tests_from_file(test_file)

        # Check if all tests passed
        file_passed = all(r.passed for r in results)
        all_passed = all_passed and file_passed

        if not file_passed:
            print(f"❌ Some tests failed in {test_file.name}")
        else:
            print(f"✅ All tests passed in {test_file.name}")

    return all_passed


def main():
    """Main test runner entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP server CLI tests")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for test report (JSON format)"
    )

    args = parser.parse_args()

    test_dir = Path(__file__).parent
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)

    # Run all tests
    all_passed = run_all_tests(test_dir, args.verbose)

    # Generate and save report if output file specified
    if args.output:
        from cmd_test_executor import CommandTestExecutor
        executor = CommandTestExecutor(verbose=args.verbose)
        report = executor.generate_report()

        with open(args.output, 'w') as f:
            import json
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()