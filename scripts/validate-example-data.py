#!/usr/bin/env python3
"""
Validate all example data files against their respective schemas.

This script validates all JSON files in the examples/ directory against
the appropriate Pydantic schemas, providing detailed feedback on validation
results and performance metrics.

Usage:
    python scripts/validate-example-data.py [--verbose] [--strict] [--format FORMAT]

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from v2.common.validation import create_validator
from v2.common.schemas import (
    DesignTokenSet,
    ComponentCatalog,
    ScreenSpecification,
    TestSuite,
    RAGKnowledgeBase
)
import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Type
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ValidationResult:
    """Result of validating a single file."""
    file_path: Path
    is_valid: bool
    schema_class: str
    errors: List[str]
    warnings: List[str]
    validation_time: float
    file_size: int


@dataclass
class ValidationSummary:
    """Summary of all validation results."""
    total_files: int
    valid_files: int
    invalid_files: int
    total_errors: int
    total_warnings: int
    total_time: float
    results: List[ValidationResult]


class ExampleDataValidator:
    """Validates all example data files in the examples directory."""

    def __init__(self, strict_mode: bool = False, verbose: bool = False):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, validation fails on warnings
            verbose: If True, provide detailed output
        """
        self.strict_mode = strict_mode
        self.verbose = verbose
        self.validator = create_validator(strict_mode)

        # Mapping of file patterns to schema classes
        self.schema_mappings = [
            {
                'patterns': ['*design-tokens*.json', 'design-tokens.json'],
                'schema_class': DesignTokenSet,
                'description': 'Design Tokens'
            },
            {
                'patterns': ['*component-catalog*.json', 'component-catalog.json'],
                'schema_class': ComponentCatalog,
                'description': 'Component Catalog'
            },
            {
                'patterns': ['*screen-specs*.json', '*screen*.json'],
                'schema_class': ScreenSpecification,
                'description': 'Screen Specification'
            },
            {
                'patterns': ['*test-suite*.json', '*test*.json'],
                'schema_class': TestSuite,
                'description': 'Test Suite'
            },
            {
                'patterns': ['*rag*.json', '*knowledge-base*.json'],
                'schema_class': RAGKnowledgeBase,
                'description': 'RAG Knowledge Base'
            }
        ]

    def find_example_files(self, examples_dir: Path) -> List[Path]:
        """
        Find all JSON files in the examples directory.

        Args:
            examples_dir: Path to examples directory

        Returns:
            List of JSON file paths
        """
        if not examples_dir.exists():
            raise FileNotFoundError(f"Examples directory not found: {examples_dir}")

        json_files = []
        for pattern in ['**/*.json', '*.json']:
            json_files.extend(examples_dir.glob(pattern))

        # Remove duplicates and sort
        json_files = sorted(set(json_files))
        return json_files

    def determine_schema_class(self, file_path: Path) -> Type:
        """
        Determine the appropriate schema class for a file based on its name.

        Args:
            file_path: Path to the file

        Returns:
            Schema class to validate against

        Raises:
            ValueError: If no appropriate schema class found
        """
        file_name = file_path.name.lower()

        for mapping in self.schema_mappings:
            for pattern in mapping['patterns']:
                if pattern.startswith('*') and pattern.endswith('*'):
                    # Contains pattern
                    if pattern[1:-1] in file_name:
                        return mapping['schema_class']
                elif pattern.startswith('*'):
                    # Ends with pattern
                    if file_name.endswith(pattern[1:]):
                        return mapping['schema_class']
                elif pattern.endswith('*'):
                    # Starts with pattern
                    if file_name.startswith(pattern[:-1]):
                        return mapping['schema_class']
                else:
                    # Exact match
                    if file_name == pattern.lower():
                        return mapping['schema_class']

        # If no specific pattern matches, try to determine from directory structure
        if 'screen' in file_name:
            return ScreenSpecification
        elif 'component' in file_name:
            return ComponentCatalog
        elif 'design-token' in file_name or 'token' in file_name:
            return DesignTokenSet
        elif 'test' in file_name:
            return TestSuite
        elif 'rag' in file_name or 'knowledge' in file_name:
            return RAGKnowledgeBase

        # Default to trying all schemas (will be handled in validation)
        return None

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate a single file against its appropriate schema.

        Args:
            file_path: Path to file to validate

        Returns:
            ValidationResult object
        """
        start_time = time.time()
        file_size = file_path.stat().st_size if file_path.exists() else 0

        try:
            # Determine schema class
            schema_class = self.determine_schema_class(file_path)

            if schema_class is None:
                # Try all schemas until one works
                for mapping in self.schema_mappings:
                    try:
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            file_path, mapping['schema_class']
                        )
                        if is_valid:
                            schema_class = mapping['schema_class']
                            break
                    except:
                        continue
                else:
                    # No schema matched
                    return ValidationResult(
                        file_path=file_path,
                        is_valid=False,
                        schema_class="Unknown",
                        errors=["Could not determine appropriate schema class"],
                        warnings=[],
                        validation_time=time.time() - start_time,
                        file_size=file_size
                    )

            # Validate against the determined schema
            is_valid, validated_obj, errors = self.validator.validate_json_file(
                file_path, schema_class
            )

            # Get any warnings from the validator
            warnings = []
            if hasattr(validated_obj, '__dict__'):
                # Extract warnings from custom validations
                last_validation = self.validator.validation_history[-1] if self.validator.validation_history else None
                if last_validation and last_validation.get('messages'):
                    warnings = [msg for msg in last_validation['messages']
                                if 'warning' in msg.lower()]

            return ValidationResult(
                file_path=file_path,
                is_valid=is_valid,
                schema_class=schema_class.__name__,
                errors=errors,
                warnings=warnings,
                validation_time=time.time() - start_time,
                file_size=file_size
            )

        except Exception as e:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                schema_class="Error",
                errors=[str(e)],
                warnings=[],
                validation_time=time.time() - start_time,
                file_size=file_size
            )

    def validate_all_files(self, examples_dir: Path) -> ValidationSummary:
        """
        Validate all files in the examples directory.

        Args:
            examples_dir: Path to examples directory

        Returns:
            ValidationSummary object
        """
        files = self.find_example_files(examples_dir)
        results = []
        total_start_time = time.time()

        if self.verbose:
            print(f"Found {len(files)} JSON files to validate")

        for i, file_path in enumerate(files, 1):
            if self.verbose:
                print(f"Validating {i}/{len(files)}: {file_path.name}")

            result = self.validate_file(file_path)
            results.append(result)

        total_time = time.time() - total_start_time

        # Calculate summary
        total_files = len(results)
        valid_files = sum(1 for r in results if r.is_valid)
        invalid_files = total_files - valid_files
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return ValidationSummary(
            total_files=total_files,
            valid_files=valid_files,
            invalid_files=invalid_files,
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_time=total_time,
            results=results
        )

    def format_results_text(self, summary: ValidationSummary) -> str:
        """
        Format validation results as text.

        Args:
            summary: ValidationSummary object

        Returns:
            Formatted text string
        """
        output = []
        output.append("=" * 70)
        output.append("EXAMPLE DATA VALIDATION REPORT")
        output.append("=" * 70)
        output.append(f"Total Files: {summary.total_files}")
        output.append(f"Valid Files: {summary.valid_files}")
        output.append(f"Invalid Files: {summary.invalid_files}")
        output.append(f"Total Errors: {summary.total_errors}")
        output.append(f"Total Warnings: {summary.total_warnings}")
        output.append(f"Validation Time: {summary.total_time:.2f}s")
        output.append(f"Success Rate: {(summary.valid_files / summary.total_files * 100):.1f}%")
        output.append("")

        # Group results by status
        valid_results = [r for r in summary.results if r.is_valid]
        invalid_results = [r for r in summary.results if not r.is_valid]

        if valid_results:
            output.append("✓ VALID FILES:")
            for result in valid_results:
                output.append(f"  ✓ {result.file_path.name} ({result.schema_class}) "
                              f"- {result.validation_time:.3f}s")
                if result.warnings and self.verbose:
                    for warning in result.warnings:
                        output.append(f"    ⚠ {warning}")
            output.append("")

        if invalid_results:
            output.append("✗ INVALID FILES:")
            for result in invalid_results:
                output.append(f"  ✗ {result.file_path.name} ({result.schema_class}) "
                              f"- {result.validation_time:.3f}s")
                for error in result.errors:
                    output.append(f"    ✗ {error}")
                if result.warnings and self.verbose:
                    for warning in result.warnings:
                        output.append(f"    ⚠ {warning}")
            output.append("")

        # Performance summary
        if self.verbose:
            output.append("PERFORMANCE SUMMARY:")
            sorted_results = sorted(summary.results, key=lambda r: r.validation_time, reverse=True)
            for result in sorted_results[:5]:  # Top 5 slowest
                size_kb = result.file_size / 1024
                output.append(f"  {result.file_path.name}: "
                              f"{result.validation_time:.3f}s, {size_kb:.1f}KB")

        return "\n".join(output)

    def format_results_json(self, summary: ValidationSummary) -> str:
        """
        Format validation results as JSON.

        Args:
            summary: ValidationSummary object

        Returns:
            JSON string
        """
        results_data = []
        for result in summary.results:
            results_data.append({
                'file_path': str(result.file_path),
                'is_valid': result.is_valid,
                'schema_class': result.schema_class,
                'errors': result.errors,
                'warnings': result.warnings,
                'validation_time': result.validation_time,
                'file_size': result.file_size
            })

        summary_data = {
            'summary': {
                'total_files': summary.total_files,
                'valid_files': summary.valid_files,
                'invalid_files': summary.invalid_files,
                'total_errors': summary.total_errors,
                'total_warnings': summary.total_warnings,
                'total_time': summary.total_time,
                'success_rate': (summary.valid_files / summary.total_files * 100) if summary.total_files > 0 else 0
            },
            'results': results_data
        }

        return json.dumps(summary_data, indent=2)

    def save_report(self, summary: ValidationSummary, output_path: Path, format_type: str) -> None:
        """
        Save validation report to file.

        Args:
            summary: ValidationSummary object
            output_path: Path to save report
            format_type: Output format ('text' or 'json')
        """
        if format_type == 'json':
            content = self.format_results_json(summary)
        else:
            content = self.format_results_text(summary)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Validate all example data files against their schemas"
    )
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=Path("examples"),
        help="Path to examples directory (default: examples)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Provide detailed output"
    )
    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Enable strict validation mode (fail on warnings)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Save report to file"
    )

    args = parser.parse_args()

    try:
        # Create validator
        validator = ExampleDataValidator(
            strict_mode=args.strict,
            verbose=args.verbose
        )

        # Validate all files
        summary = validator.validate_all_files(args.examples_dir)

        # Output results
        if args.format == "json":
            output = validator.format_results_json(summary)
        else:
            output = validator.format_results_text(summary)

        print(output)

        # Save to file if requested
        if args.output:
            validator.save_report(summary, args.output, args.format)
            if args.verbose:
                print(f"\nReport saved to: {args.output}")

        # Exit with error code if any files failed validation
        if summary.invalid_files > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
