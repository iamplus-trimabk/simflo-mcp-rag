#!/usr/bin/env python3
"""
Comprehensive CLI utility for validation tasks.

This script provides a unified command-line interface for all validation-related
tasks including data validation, consistency checking, pipeline test generation,
and integration testing.

Usage:
    python scripts/validation-cli.py <command> [options]

Commands:
    validate       - Validate example data against schemas
    consistency    - Check data consistency across pipeline steps
    generate-test  - Generate pipeline test configurations
    all           - Run all validation tasks
    report        - Generate comprehensive validation report

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from generate_pipeline_test import PipelineTestGenerator
from check_data_consistency import DataConsistencyChecker
from validate_example_data import ExampleDataValidator
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class CLICommandResult:
    """Result of a CLI command execution."""
    command: str
    success: bool
    execution_time: float
    output_file: Optional[Path] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


@dataclass
class OverallValidationReport:
    """Overall validation report for all commands."""
    commands_run: List[CLICommandResult]
    total_execution_time: float
    overall_success: bool
    summary: Dict[str, Any]
    timestamp: str


class ValidationCLI:
    """Comprehensive CLI for validation tasks."""

    def __init__(self, examples_dir: Path, output_dir: Path, verbose: bool = False):
        """
        Initialize the validation CLI.

        Args:
            examples_dir: Path to examples directory
            output_dir: Path to output directory
            verbose: Enable verbose output
        """
        self.examples_dir = examples_dir
        self.output_dir = output_dir
        self.verbose = verbose
        self.results = []

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_validate_command(self, format_type: str = 'text',
                             save_output: bool = True) -> CLICommandResult:
        """
        Run the validate example data command.

        Args:
            format_type: Output format ('text' or 'json')
            save_output: Whether to save output to file

        Returns:
            CLICommandResult object
        """
        start_time = time.time()

        try:
            if self.verbose:
                print("Running example data validation...")

            validator = ExampleDataValidator(
                strict_mode=False,
                verbose=self.verbose
            )

            summary = validator.validate_all_files(self.examples_dir)

            # Save output if requested
            output_file = None
            if save_output:
                output_file = self.output_dir / f"validation-results.{format_type}"
                validator.save_report(summary, output_file, format_type)
                if self.verbose:
                    print(f"Validation results saved to: {output_file}")

            # Determine success
            success = summary.invalid_files == 0

            if self.verbose:
                print(
                    f"Validation completed: {summary.valid_files}/{summary.total_files} files valid")

            return CLICommandResult(
                command="validate",
                success=success,
                execution_time=time.time() - start_time,
                output_file=output_file,
                details={
                    'total_files': summary.total_files,
                    'valid_files': summary.valid_files,
                    'invalid_files': summary.invalid_files,
                    'total_errors': summary.total_errors,
                    'total_warnings': summary.total_warnings
                }
            )

        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            if self.verbose:
                print(f"Error: {error_msg}")
                traceback.print_exc()

            return CLICommandResult(
                command="validate",
                success=False,
                execution_time=time.time() - start_time,
                error_message=error_msg
            )

    def run_consistency_command(self, format_type: str = 'text',
                                save_output: bool = True) -> CLICommandResult:
        """
        Run the data consistency check command.

        Args:
            format_type: Output format ('text' or 'json')
            save_output: Whether to save output to file

        Returns:
            CLICommandResult object
        """
        start_time = time.time()

        try:
            if self.verbose:
                print("Running data consistency check...")

            checker = DataConsistencyChecker(
                examples_dir=self.examples_dir,
                verbose=self.verbose
            )

            report = checker.run_all_checks()

            # Save output if requested
            output_file = None
            if save_output:
                output_file = self.output_dir / f"consistency-report.{format_type}"
                checker.save_report(report, output_file, format_type)
                if self.verbose:
                    print(f"Consistency report saved to: {output_file}")

            # Determine success (no errors)
            success = report.error_count == 0

            if self.verbose:
                print(f"Consistency check completed: {report.total_issues} issues found "
                      f"({report.error_count} errors, {report.warning_count} warnings)")

            return CLICommandResult(
                command="consistency",
                success=success,
                execution_time=time.time() - start_time,
                output_file=output_file,
                details={
                    'total_issues': report.total_issues,
                    'error_count': report.error_count,
                    'warning_count': report.warning_count,
                    'info_count': report.info_count,
                    'files_analyzed': report.total_files_analyzed
                }
            )

        except Exception as e:
            error_msg = f"Consistency check failed: {str(e)}"
            if self.verbose:
                print(f"Error: {error_msg}")
                traceback.print_exc()

            return CLICommandResult(
                command="consistency",
                success=False,
                execution_time=time.time() - start_time,
                error_message=error_msg
            )

    def run_generate_test_command(self, save_output: bool = True) -> CLICommandResult:
        """
        Run the pipeline test generation command.

        Args:
            save_output: Whether to save output to file

        Returns:
            CLICommandResult object
        """
        start_time = time.time()

        try:
            if self.verbose:
                print("Generating pipeline test configuration...")

            generator = PipelineTestGenerator(
                examples_dir=self.examples_dir,
                verbose=self.verbose
            )

            config = generator.generate_pipeline_config()

            # Save output if requested
            output_file = None
            if save_output:
                output_file = self.output_dir / "pipeline-test-config.json"
                generator.save_config(config, output_file)

                # Also save step configurations
                steps_dir = self.output_dir / "pipeline-steps"
                for step in config.steps:
                    step_config_path = steps_dir / f"{step.step_name}-config.json"
                    step_config_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(step_config_path, 'w', encoding='utf-8') as f:
                        json.dump(asdict(step), f, indent=2, default=str)

                if self.verbose:
                    print(f"Pipeline configuration saved to: {output_file}")
                    print(f"Step configurations saved to: {steps_dir}")

            if self.verbose:
                print(f"Generated configuration for {len(config.steps)} pipeline steps")

            return CLICommandResult(
                command="generate-test",
                success=True,
                execution_time=time.time() - start_time,
                output_file=output_file,
                details={
                    'pipeline_name': config.pipeline_name,
                    'total_steps': len(config.steps),
                    'enabled_steps': len([s for s in config.steps if s.configuration.get('enabled', True)]),
                    'test_data_sources': len(config.test_data_sources)
                }
            )

        except Exception as e:
            error_msg = f"Pipeline test generation failed: {str(e)}"
            if self.verbose:
                print(f"Error: {error_msg}")
                traceback.print_exc()

            return CLICommandResult(
                command="generate-test",
                success=False,
                execution_time=time.time() - start_time,
                error_message=error_msg
            )

    def run_all_commands(self, format_type: str = 'text') -> OverallValidationReport:
        """
        Run all validation commands.

        Args:
            format_type: Output format for reports ('text' or 'json')

        Returns:
            OverallValidationReport object
        """
        start_time = time.time()

        if self.verbose:
            print("Running all validation commands...")

        commands = [
            ("validate", lambda: self.run_validate_command(format_type)),
            ("consistency", lambda: self.run_consistency_command(format_type)),
            ("generate-test", lambda: self.run_generate_test_command())
        ]

        results = []

        for command_name, command_func in commands:
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"Running: {command_name}")
                print('='*50)

            result = command_func()
            results.append(result)

            status = "✓" if result.success else "✗"
            if self.verbose:
                print(f"{status} {command_name}: {result.execution_time:.2f}s")
                if result.error_message:
                    print(f"  Error: {result.error_message}")

        total_time = time.time() - start_time
        overall_success = all(r.success for r in results)

        # Generate summary
        summary = {
            'commands_run': len(results),
            'successful_commands': sum(1 for r in results if r.success),
            'failed_commands': sum(1 for r in results if not r.success),
            'total_execution_time': total_time,
            'command_details': {
                r.command: {
                    'success': r.success,
                    'execution_time': r.execution_time,
                    'details': r.details or {}
                }
                for r in results
            }
        }

        if self.verbose:
            print(f"\n{'='*50}")
            print("ALL COMMANDS COMPLETED")
            print('='*50)
            print(f"Overall Success: {'✓' if overall_success else '✗'}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Successful: {summary['successful_commands']}/{summary['commands_run']}")

        return OverallValidationReport(
            commands_run=results,
            total_execution_time=total_time,
            overall_success=overall_success,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )

    def generate_comprehensive_report(self, report: OverallValidationReport,
                                      format_type: str = 'text') -> str:
        """
        Generate a comprehensive validation report.

        Args:
            report: OverallValidationReport object
            format_type: Output format ('text' or 'json')

        Returns:
            Formatted report string
        """
        if format_type == 'json':
            return json.dumps(asdict(report), indent=2, default=str)

        # Text format
        output = []
        output.append("=" * 80)
        output.append("COMPREHENSIVE VALIDATION REPORT")
        output.append("=" * 80)
        output.append(f"Generated At: {report.timestamp}")
        output.append(f"Examples Directory: {self.examples_dir}")
        output.append(f"Output Directory: {self.output_dir}")
        output.append("")

        # Overall summary
        output.append("OVERALL SUMMARY:")
        output.append(f"  Commands Run: {report.summary['commands_run']}")
        output.append(f"  Successful: {report.summary['successful_commands']}")
        output.append(f"  Failed: {report.summary['failed_commands']}")
        output.append(f"  Total Time: {report.total_execution_time:.2f}s")
        output.append(f"  Overall Success: {'✓' if report.overall_success else '✗'}")
        output.append("")

        # Command details
        output.append("COMMAND DETAILS:")
        for result in report.commands_run:
            status = "✓" if result.success else "✗"
            output.append(f"  {status} {result.command.upper()}")
            output.append(f"    Execution Time: {result.execution_time:.2f}s")
            output.append(f"    Success: {result.success}")

            if result.details:
                for key, value in result.details.items():
                    output.append(f"    {key.replace('_', ' ').title()}: {value}")

            if result.error_message:
                output.append(f"    Error: {result.error_message}")

            if result.output_file:
                output.append(f"    Output: {result.output_file}")
            output.append("")

        # Recommendations
        output.append("RECOMMENDATIONS:")
        if report.overall_success:
            output.append("  ✓ All validation tasks completed successfully")
            output.append("  ✓ Your example data is ready for pipeline processing")
        else:
            failed_commands = [r.command for r in report.commands_run if not r.success]
            output.append(f"  ✗ Fix issues in failed commands: {', '.join(failed_commands)}")
            output.append("  ✗ Review error messages and update example data")

            if any(r.command == 'validate' and not r.success for r in report.commands_run):
                output.append("  • Fix schema validation errors in example data")

            if any(r.command == 'consistency' and not r.success for r in report.commands_run):
                output.append("  • Resolve data consistency issues")

        output.append("")
        output.append("NEXT STEPS:")
        output.append("  1. Review detailed reports in output directory")
        output.append("  2. Fix any identified issues")
        output.append("  3. Re-run validation to verify fixes")
        output.append("  4. Use generated pipeline configuration for testing")

        return "\n".join(output)

    def save_comprehensive_report(self, report: OverallValidationReport,
                                  format_type: str = 'text') -> Path:
        """
        Save comprehensive report to file.

        Args:
            report: OverallValidationReport object
            format_type: Output format ('text' or 'json')

        Returns:
            Path to saved report file
        """
        content = self.generate_comprehensive_report(report, format_type)
        extension = 'json' if format_type == 'json' else 'txt'
        report_path = self.output_dir / f"comprehensive-validation-report.{extension}"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return report_path


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Comprehensive CLI for validation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate example data
  python scripts/validation-cli.py validate

  # Check data consistency
  python scripts/validation-cli.py consistency --verbose

  # Generate pipeline test configuration
  python scripts/validation-cli.py generate-test --output-dir ./configs

  # Run all validation commands
  python scripts/validation-cli.py all --format json --output-dir ./reports

  # Generate comprehensive report
  python scripts/validation-cli.py report --verbose
        """
    )

    parser.add_argument(
        "command",
        choices=["validate", "consistency", "generate-test", "all", "report"],
        help="Validation command to run"
    )

    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=Path("examples"),
        help="Path to examples directory (default: examples)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("validation-reports"),
        help="Output directory for reports (default: validation-reports)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format for reports (default: text)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save output to files (display only)"
    )

    return parser


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Create CLI instance
        cli = ValidationCLI(
            examples_dir=args.examples_dir,
            output_dir=args.output_dir,
            verbose=args.verbose
        )

        # Validate examples directory exists
        if not args.examples_dir.exists():
            print(f"Error: Examples directory not found: {args.examples_dir}", file=sys.stderr)
            sys.exit(1)

        # Run the requested command
        if args.command == "validate":
            result = cli.run_validate_command(
                format_type=args.format,
                save_output=not args.no_save
            )
            if not result.success:
                sys.exit(1)

        elif args.command == "consistency":
            result = cli.run_consistency_command(
                format_type=args.format,
                save_output=not args.no_save
            )
            if not result.success:
                sys.exit(1)

        elif args.command == "generate-test":
            result = cli.run_generate_test_command(save_output=not args.no_save)
            if not result.success:
                sys.exit(1)

        elif args.command == "all":
            report = cli.run_all_commands(format_type=args.format)

            # Save comprehensive report
            if not args.no_save:
                report_path = cli.save_comprehensive_report(report, args.format)
                if args.verbose:
                    print(f"\nComprehensive report saved to: {report_path}")

            # Exit with error code if any command failed
            if not report.overall_success:
                sys.exit(1)

        elif args.command == "report":
            # Run all commands and generate comprehensive report
            report = cli.run_all_commands(format_type=args.format)

            # Always save the comprehensive report for this command
            report_path = cli.save_comprehensive_report(report, args.format)
            print(cli.generate_comprehensive_report(report, args.format))

            if args.verbose:
                print(f"\nReport saved to: {report_path}")

            # Exit with error code if any command failed
            if not report.overall_success:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
