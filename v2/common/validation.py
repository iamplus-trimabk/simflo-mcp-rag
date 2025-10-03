"""
Schema validation utilities for the SimFlo Figma-to-RAG pipeline.

This module provides validation functions, error handling, and utilities
for working with JSON schemas throughout the pipeline.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Type, Any, Dict, List, Tuple
from pydantic import BaseModel
from datetime import datetime

from .schemas import (
    DesignTokenSet,
    ComponentCatalog,
    ComponentDefinition,
    TestScenario,
    ScreenSet,
    TestSuite,
    RAGKnowledgeBase,
    create_example_design_tokens,
    create_example_component,
    create_example_test_scenario
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomValidationError(Exception):
    """Custom validation error with detailed information."""

    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []
        self.timestamp = datetime.now()

    def __str__(self):
        error_msg = f"Validation Error: {self.message}"
        if self.errors:
            error_msg += f"\nDetails: {'; '.join(self.errors)}"
        return error_msg


class SchemaValidator:
    """Main schema validator class for pipeline data validation."""

    def __init__(self, strict_mode: bool = False):
        """
        Initialize schema validator.

        Args:
            strict_mode: If True, validation fails on warnings.
                         If False, warnings are logged but don't cause failure.
        """
        self.strict_mode = strict_mode
        self.validation_history: List[Dict[str, Any]] = []

    def validate_json_file(
          self, file_path: Path, schema_class: Type[BaseModel]
      ) -> Tuple[bool, BaseModel, List[str]]:
        """
        Validate a JSON file against a schema class.

        Args:
            file_path: Path to JSON file to validate
            schema_class: Pydantic schema class to validate against

        Returns:
            Tuple of (is_valid, validated_object, error_messages)

        Raises:
            FileNotFoundError: If file doesn't exist
            CustomValidationError: If validation fails in strict mode
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate against schema
            validated_object = schema_class(**data)
            errors = []
            warnings = []

            # Custom validations and warnings
            self._perform_custom_validations(validated_object, warnings)

            # Log warnings if any
            if warnings:
                logger.warning(f"Validation warnings for {file_path}: {warnings}")

            # Record validation
            self._record_validation(file_path, schema_class, True, warnings)

            if self.strict_mode and warnings:
                raise CustomValidationError(
                    f"Validation failed with strict mode: {file_path}",
                    warnings
                )

            return True, validated_object, errors

        except CustomValidationError as e:
            errors = self._extract_validation_errors(e)
            self._record_validation(file_path, schema_class, False, errors)

            if self.strict_mode:
                raise CustomValidationError(
                    f"Schema validation failed: {file_path}",
                    errors
                )

            logger.error(f"Validation failed for {file_path}: {errors}")
            return False, None, errors

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {str(e)}"
            self._record_validation(file_path, schema_class, False, [error_msg])

            if self.strict_mode:
                raise CustomValidationError(error_msg)

            logger.error(error_msg)
            return False, None, [error_msg]

    def validate_dict(
          self, data: Dict[str, Any], schema_class: Type[BaseModel]
      ) -> Tuple[bool, BaseModel, List[str]]:
        """
        Validate a dictionary against a schema class.

        Args:
            data: Dictionary to validate
            schema_class: Pydantic schema class to validate against

        Returns:
            Tuple of (is_valid, validated_object, error_messages)
        """
        try:
            validated_object = schema_class(**data)
            warnings = []
            self._perform_custom_validations(validated_object, warnings)

            if warnings:
                logger.warning(f"Validation warnings: {warnings}")

            return True, validated_object, []

        except CustomValidationError as e:
            errors = self._extract_validation_errors(e)
            logger.error(f"Validation failed: {errors}")
            return False, None, errors

    def load_and_validate(self, file_path: Path, schema_class: Type[BaseModel]) -> BaseModel:
        """
        Load JSON file and validate against schema. Raises CustomValidationError on failure.

        Args:
            file_path: Path to JSON file
            schema_class: Pydantic schema class

        Returns:
            Validated schema object

        Raises:
            CustomValidationError: If validation fails
            FileNotFoundError: If file doesn't exist
        """
        is_valid, validated_object, errors = self.validate_json_file(file_path, schema_class)

        if not is_valid:
            raise CustomValidationError(
                f"Failed to load and validate {file_path}",
                errors
            )

        return validated_object

    def validate_batch(
          self, file_paths: List[Path], schema_class: Type[BaseModel]
      ) -> Dict[Path, Tuple[bool, List[str]]]:
        """
        Validate multiple files against the same schema class.

        Args:
            file_paths: List of file paths to validate
            schema_class: Pydantic schema class

        Returns:
            Dictionary mapping file paths to (is_valid, error_messages) tuples
        """
        results = {}

        for file_path in file_paths:
            try:
                is_valid, _, errors = self.validate_json_file(file_path, schema_class)
                results[file_path] = (is_valid, errors)
            except Exception as e:
                results[file_path] = (False, [str(e)])

        return results

    def _perform_custom_validations(self, obj: BaseModel, warnings: List[str]) -> None:
        """Perform custom validations beyond Pydantic's built-in validations."""
        # Design Token Set validations
        if isinstance(obj, DesignTokenSet):
            self._validate_design_token_set(obj, warnings)

        # Component Catalog validations
        elif isinstance(obj, ComponentCatalog):
            self._validate_component_catalog(obj, warnings)

        # Screen Set validations
        elif isinstance(obj, ScreenSet):
            self._validate_screen_set(obj, warnings)

        # Test Suite validations
        elif isinstance(obj, TestSuite):
            self._validate_test_suite(obj, warnings)

        # RAG Knowledge Base validations
        elif isinstance(obj, RAGKnowledgeBase):
            self._validate_rag_knowledge_base(obj, warnings)

    def _validate_design_token_set(self, tokens: DesignTokenSet, warnings: List[str]) -> None:
        """Custom validations for DesignTokenSet."""
        # Check for duplicate token names
        all_names = []
        for color in tokens.colors:
            all_names.append(f"color.{color.name}")
        for typo in tokens.typography:
            all_names.append(f"typography.{typo.name}")
        for spacing in tokens.spacing:
            all_names.append(f"spacing.{spacing.name}")

        duplicates = [name for name in set(all_names) if all_names.count(name) > 1]
        if duplicates:
            warnings.append(f"Duplicate token names found: {duplicates}")

        # Check for missing essential tokens
        if not any("primary" in color.name for color in tokens.colors):
            warnings.append("No primary color tokens defined")

        if not tokens.typography:
            warnings.append("No typography tokens defined")

    def _validate_component_catalog(self, catalog: ComponentCatalog, warnings: List[str]) -> None:
        """Custom validations for ComponentCatalog."""
        # Check for orphaned instances
        component_ids = {comp.id for comp in catalog.components}
        orphaned_instances = [
            instance for instance in catalog.instances
            if instance.component_id not in component_ids
        ]

        if orphaned_instances:
            warnings.append(f"Found {len(orphaned_instances)} orphaned component instances")

        # Check for components without properties
        components_without_props = [
            comp for comp in catalog.components
            if not comp.properties
        ]

        if components_without_props:
            warnings.append(
                f"Found {len(components_without_props)} components without defined properties")

    def _validate_screen_set(self, screen_set: ScreenSet, warnings: List[str]) -> None:
        """Custom validations for ScreenSet."""
        # Check for screens without component instances
        screens_without_components = [
            screen for screen in screen_set.screens
            if not screen.component_instances
        ]

        if screens_without_components:
            warnings.append(
                f"Found {len(screens_without_components)} screens without component instances")

        # Check for invalid navigation references
        screen_ids = {screen.id for screen in screen_set.screens}
        invalid_refs = []

        for screen in screen_set.screens:
            for nav in screen.navigation_flows:
                if nav.from_screen_id not in screen_ids:
                    invalid_refs.append(nav.from_screen_id)
                if nav.to_screen_id not in screen_ids:
                    invalid_refs.append(nav.to_screen_id)

        if invalid_refs:
            warnings.append(
                f"Found navigation references to non-existent screens: {set(invalid_refs)}")

    def _validate_test_suite(self, test_suite: TestSuite, warnings: List[str]) -> None:
        """Custom validations for TestSuite."""
        # Check for scenarios without steps
        scenarios_without_steps = [
            scenario for scenario in test_suite.scenarios
            if not scenario.steps
        ]

        if scenarios_without_steps:
            warnings.append(f"Found {len(scenarios_without_steps)} test scenarios without steps")

        # Check for scenarios without success criteria
        scenarios_without_criteria = [
            scenario for scenario in test_suite.scenarios
            if not scenario.success_criteria
        ]

        if scenarios_without_criteria:
            warnings.append(
                f"Found {len(scenarios_without_criteria)} scenarios without success criteria")

        # Check for steps without actions
        steps_without_actions = 0
        for scenario in test_suite.scenarios:
            for step in scenario.steps:
                if not step.actions:
                    steps_without_actions += 1

        if steps_without_actions > 0:
            warnings.append(f"Found {steps_without_actions} test steps without actions")

    def _validate_rag_knowledge_base(self, kb: RAGKnowledgeBase, warnings: List[str]) -> None:
        """Custom validations for RAGKnowledgeBase."""
        # Check for empty chunks
        empty_chunks = [
            chunk for chunk in kb.chunks
            if not chunk.content.strip()
        ]

        if empty_chunks:
            warnings.append(f"Found {len(empty_chunks)} empty content chunks")

        # Check for chunks without source information
        chunks_without_source = [
            chunk for chunk in kb.chunks
            if not chunk.source_info
        ]

        if chunks_without_source:
            warnings.append(f"Found {len(chunks_without_source)} chunks without source information")

        # Check for chunks without tags
        chunks_without_tags = [
            chunk for chunk in kb.chunks
            if not chunk.tags
        ]

        if chunks_without_tags:
            warnings.append(f"Found {len(chunks_without_tags)} chunks without tags")

    def _extract_validation_errors(self, e: CustomValidationError) -> List[str]:
        """Extract error messages from Pydantic CustomValidationError."""
        errors = []
        for error in e.errors():
            field_path = " -> ".join(str(loc) for loc in error['loc'])
            errors.append(f"{field_path}: {error['msg']}")
        return errors

    def _record_validation(self, file_path: Path, schema_class: Type[BaseModel],
                           is_valid: bool, messages: List[str]) -> None:
        """Record validation result in history."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'file_path': str(file_path),
            'schema_class': schema_class.__name__,
            'is_valid': is_valid,
            'messages': messages
        }
        self.validation_history.append(record)

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation history."""
        if not self.validation_history:
            return {'total_validations': 0}

        total = len(self.validation_history)
        successful = sum(1 for r in self.validation_history if r['is_valid'])
        failed = total - successful

        return {
            'total_validations': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'last_validation': self.validation_history[-1]['timestamp']
        }


class FileValidator:
    """Utility class for file-level validations."""

    @staticmethod
    def validate_json_structure(file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate basic JSON file structure.

        Args:
            file_path: Path to JSON file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return False, errors

        if not file_path.is_file():
            errors.append(f"Path is not a file: {file_path}")
            return False, errors

        if file_path.stat().st_size == 0:
            errors.append(f"File is empty: {file_path}")
            return False, errors

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
            return False, errors
        except UnicodeDecodeError as e:
            errors.append(f"File encoding error: {str(e)}")
            return False, errors

        return True, errors

    @staticmethod
    def validate_file_permissions(file_path: Path, require_read: bool = True,
                                  require_write: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate file permissions.

        Args:
            file_path: Path to file
            require_read: Whether read permission is required
            require_write: Whether write permission is required

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return False, errors

        try:
            if require_read:
                # Try to read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1)  # Read first byte to test readability

            if require_write:
                # Try to write to file (create temporary file in same directory)
                test_file = file_path.parent / f".write_test_{file_path.stem}"
                test_file.touch()
                test_file.unlink()

        except PermissionError as e:
            errors.append(f"Permission error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error checking permissions: {str(e)}")
            return False, errors

        return True, errors

    @staticmethod
    def validate_directory_structure(
          directory: Path, required_subdirs: List[str] = None
      ) -> Tuple[bool, List[str]]:
        """
        Validate directory structure.

        Args:
            directory: Directory path to validate
            required_subdirs: List of required subdirectory names

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not directory.exists():
            errors.append(f"Directory does not exist: {directory}")
            return False, errors

        if not directory.is_dir():
            errors.append(f"Path is not a directory: {directory}")
            return False, errors

        if required_subdirs:
            for subdir in required_subdirs:
                subdir_path = directory / subdir
                if not subdir_path.exists():
                    errors.append(f"Required subdirectory missing: {subdir}")

        return len(errors) == 0, errors


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_validator(strict_mode: bool = False) -> SchemaValidator:
    """
    Create a configured schema validator.

    Args:
        strict_mode: Whether to enable strict validation mode

    Returns:
        Configured SchemaValidator instance
    """
    return SchemaValidator(strict_mode=strict_mode)


def validate_and_load(file_path: Path, schema_class: Type[BaseModel],
                      strict_mode: bool = False) -> BaseModel:
    """
    Convenience function to validate and load a JSON file.

    Args:
        file_path: Path to JSON file
        schema_class: Pydantic schema class
        strict_mode: Whether to enable strict validation

    Returns:
        Validated schema object

    Raises:
        CustomValidationError: If validation fails
    """
    validator = create_validator(strict_mode)
    return validator.load_and_validate(file_path, schema_class)


def validate_example_data() -> Dict[str, Tuple[bool, List[str]]]:
    """
    Validate all example data schemas to ensure they work correctly.

    Returns:
        Dictionary mapping schema names to (is_valid, error_messages) tuples
    """
    validator = create_validator(strict_mode=False)
    results = {}

    try:
        # Test design tokens
        design_tokens = create_example_design_tokens()
        is_valid, validated_obj, errors = validator.validate_dict(
            design_tokens.model_dump(), DesignTokenSet)
        results['design_tokens'] = (is_valid, errors)

        # Test component
        component = create_example_component()
        is_valid, validated_obj, errors = validator.validate_dict(
            component.model_dump(), ComponentDefinition)
        results['component'] = (is_valid, errors)

        # Test scenario
        scenario = create_example_test_scenario()
        is_valid, validated_obj, errors = validator.validate_dict(
            scenario.model_dump(), TestScenario)
        results['test_scenario'] = (is_valid, errors)

    except Exception as e:
        results['error'] = (False, [str(e)])

    return results


def batch_validate_directory(directory: Path, schema_class: Type[BaseModel],
                             pattern: str = "*.json") -> Dict[Path, Tuple[bool, List[str]]]:
    """
    Validate all JSON files in a directory against a schema.

    Args:
        directory: Directory containing JSON files
        schema_class: Pydantic schema class
        pattern: File pattern to match (default: "*.json")

    Returns:
        Dictionary mapping file paths to validation results
    """
    validator = create_validator()
    json_files = list(directory.glob(pattern))
    return validator.validate_batch(json_files, schema_class)


def generate_validation_report(validator: SchemaValidator) -> str:
    """
    Generate a human-readable validation report.

    Args:
        validator: SchemaValidator instance

    Returns:
        Formatted validation report string
    """
    summary = validator.get_validation_summary()

    report = f"""
Validation Report
================
Total Validations: {summary['total_validations']}
Successful: {summary['successful']}
Failed: {summary['failed']}
Success Rate: {summary['success_rate']:.1f}%
Last Validation: {summary['last_validation']}

Recent Validations:
"""

    # Show last 5 validations
    recent_validations = validator.validation_history[-5:]
    for validation in recent_validations:
        status = "✓ PASS" if validation['is_valid'] else "✗ FAIL"
        report += f"  {status} {validation['file_path']} ({validation['schema_class']})\n"

        if validation['messages']:
            for message in validation['messages'][:3]:  # Show first 3 messages
                report += f"    - {message}\n"

    return report


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def main():
    """Command line interface for validation utilities."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Schema validation utilities")
    parser.add_argument("command", choices=["validate", "test", "report"],
                        help="Validation command to run")
    parser.add_argument("--file", type=Path, help="File to validate")
    parser.add_argument("--schema", choices=[
        "DesignTokenSet", "ComponentCatalog", "ScreenSet",
        "TestSuite", "RAGKnowledgeBase"
    ], help="Schema class to validate against")
    parser.add_argument("--strict", action="store_true",
                        help="Enable strict validation mode")
    parser.add_argument("--directory", type=Path,
                        help="Directory to validate (for batch validation)")

    args = parser.parse_args()

    if args.command == "validate":
        if not args.file or not args.schema:
            print("Error: --file and --schema are required for validation")
            sys.exit(1)

        # Map schema names to classes
        schema_map = {
            "DesignTokenSet": DesignTokenSet,
            "ComponentCatalog": ComponentCatalog,
            "ScreenSet": ScreenSet,
            "TestSuite": TestSuite,
            "RAGKnowledgeBase": RAGKnowledgeBase
        }

        schema_class = schema_map.get(args.schema)
        if not schema_class:
            print(f"Error: Unknown schema class: {args.schema}")
            sys.exit(1)

        try:
            validator = create_validator(args.strict)
            is_valid, obj, errors = validator.validate_json_file(args.file, schema_class)

            if is_valid:
                print(f"✓ Validation successful: {args.file}")
                if errors:
                    print(f"Warnings: {'; '.join(errors)}")
            else:
                print(f"✗ Validation failed: {args.file}")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "test":
        print("Testing example data schemas...")
        results = validate_example_data()

        all_passed = True
        for schema_name, (is_valid, errors) in results.items():
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"{status} {schema_name}")

            if not is_valid:
                all_passed = False
                for error in errors:
                    print(f"  - {error}")

        if all_passed:
            print("\n✓ All example schemas validated successfully!")
        else:
            print("\n✗ Some schemas failed validation")
            sys.exit(1)

    elif args.command == "report":
        validator = create_validator()
        print(generate_validation_report(validator))


if __name__ == "__main__":
    main()
