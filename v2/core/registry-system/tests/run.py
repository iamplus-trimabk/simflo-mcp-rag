#!/usr/bin/env python3
"""
Registry System Test Runner

Runs all tests for the registry system CLI using the command test executor.
Provides comprehensive test reporting and easy integration with CI/CD pipelines.
"""

import sys
import json
from pathlib import Path
from typing import List, Optional

# Add the tests directory to the path to import cmd_test_executor
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tests"))

try:
    from cmd_test_executor import CommandTestExecutor
except ImportError as e:
    print(f"❌ Failed to import cmd_test_executor: {e}")
    print("Make sure v2/tests/cmd_test_executor.py exists")
    sys.exit(1)


def run_all_tests(test_dir: Path, verbose: bool = False,
                 output_file: Optional[str] = None) -> bool:
    """Run all tests in the registry system test directory"""

    print("🚀 Registry System Test Runner")
    print("=" * 50)

    # Initialize executor
    executor = CommandTestExecutor(verbose=verbose)

    # Find all test JSON files
    test_files = list(test_dir.glob("*.json"))
    if not test_files:
        print("❌ No test files found in {test_dir}")
        return False

    print(f"📁 Found {len(test_files)} test file(s)")

    # Run all tests
    all_passed = True
    total_tests = 0
    total_passed = 0

    for test_file in test_files:
        print(f"\n📄 Running tests from: {test_file.name}")
        print("-" * 40)

        results = executor.run_tests_from_file(test_file)

        if not results:
            print(f"⚠️  No tests executed from {test_file.name}")
            continue

        tests_passed = sum(1 for r in results if r.passed)
        tests_failed = len(results) - tests_passed

        total_tests += len(results)
        total_passed += tests_passed

        if tests_failed > 0:
            all_passed = False
            print(f"❌ {test_file.name}: {tests_passed}/{len(results)} tests passed")
        else:
            print(f"✅ {test_file.name}: All {len(results)} tests passed")

    # Print final summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")

    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"Success rate: {success_rate:.1f}%")

    if all_passed:
        print("\n🎉 All tests passed! Registry system CLI is working correctly.")
    else:
        print(f"\n❌ {total_tests - total_passed} test(s) failed.")

        # Show failed test details
        print("\n❌ Failed tests:")
        for result in executor.results:
            if not result.passed:
                print(f"   - {result.test_name}: {result.error_message}")

    # Generate and save report
    report = executor.generate_report()

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {output_file}")

    return all_passed


def run_specific_test(test_file: str, verbose: bool = False,
                     output_file: Optional[str] = None) -> bool:
    """Run tests from a specific test file"""

    test_path = Path(test_file)
    if not test_path.exists():
        print(f"❌ Test file not found: {test_file}")
        return False

    print(f"🚀 Running tests from: {test_file}")
    print("=" * 50)

    executor = CommandTestExecutor(verbose=verbose)
    results = executor.run_tests_from_file(test_path)

    if not results:
        print("⚠️  No tests executed")
        return False

    executor.print_summary()

    # Generate and save report
    report = executor.generate_report()

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {output_file}")

    return all(result.passed for result in results)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run registry system CLI tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run all tests
  %(prog)s --verbose                 # Run all tests with verbose output
  %(prog)s --file cmd_tests.json     # Run specific test file
  %(prog)s --output report.json       # Save report to file
  %(prog)s --verbose --output report.json  # Verbose output with report
        """
    )

    parser.add_argument(
        "--file", "-f",
        help="Specific test file to run (default: run all tests)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file for test report (JSON format)"
    )

    parser.add_argument(
        "--working-dir", "-w",
        help="Working directory for command execution"
    )

    args = parser.parse_args()

    # Determine the test directory
    test_dir = Path(__file__).parent

    try:
        if args.file:
            # Run specific test file
            success = run_specific_test(
                args.file,
                verbose=args.verbose,
                output_file=args.output
            )
        else:
            # Run all tests
            success = run_all_tests(
                test_dir,
                verbose=args.verbose,
                output_file=args.output
            )

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()