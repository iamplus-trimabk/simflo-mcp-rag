#!/usr/bin/env python3
"""
Check data consistency across pipeline steps.

This script analyzes relationships between different data files to ensure
consistency, identify orphaned references, validate component usage across screens,
and check navigation flow references.

Usage:
    python scripts/check-data-consistency.py [--examples-dir DIR] [--verbose] [--format FORMAT]

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from v2.common.validation import create_validator
from v2.common.schemas import (
    DesignTokenSet,
    ComponentCatalog,
    ScreenSet,
    ScreenSpecification,
    TestSuite
)
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import Counter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found during analysis."""
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    affected_files: List[str]
    details: Dict[str, Any]
    suggestion: Optional[str] = None


@dataclass
class ConsistencyReport:
    """Complete consistency check report."""
    total_files_analyzed: int
    total_issues: int
    error_count: int
    warning_count: int
    info_count: int
    issues: List[ConsistencyIssue]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class DataConsistencyChecker:
    """Checks data consistency across pipeline steps."""

    def __init__(self, examples_dir: Path, verbose: bool = False):
        """
        Initialize the consistency checker.

        Args:
            examples_dir: Path to examples directory
            verbose: Enable verbose output
        """
        self.examples_dir = examples_dir
        self.verbose = verbose
        self.validator = create_validator(strict_mode=False)
        self.issues = []

        # Loaded data
        self.design_tokens = None
        self.component_catalog = None
        self.screen_specs = None
        self.test_suite = None

    def find_and_load_data(self) -> Dict[str, Any]:
        """
        Find and load all example data files.

        Returns:
            Dictionary mapping data types to loaded objects
        """
        data = {}
        files_found = {}

        # Find files
        patterns = {
            'design_tokens': ['*design-tokens*.json'],
            'component_catalog': ['*component-catalog*.json'],
            'screen_specs': ['*screen*.json'],
            'test_suite': ['*test*.json', '*test-suite*.json']
        }

        for data_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = list(self.examples_dir.glob(pattern))
                if matches:
                    files_found[data_type] = matches[0]
                    break

        # Look for screen specs in subdirectories
        screen_specs_dir = self.examples_dir / 'screen-specs'
        if screen_specs_dir.exists() and 'screen_specs' not in files_found:
            screen_files = list(screen_specs_dir.glob('*.json'))
            if screen_files:
                files_found['screen_specs'] = screen_files

        if self.verbose:
            print(f"Found {len(files_found)} data file types")

        # Load and validate files
        schema_map = {
            'design_tokens': DesignTokenSet,
            'component_catalog': ComponentCatalog,
            'test_suite': TestSuite
        }

        for data_type, file_path in files_found.items():
            try:
                if isinstance(file_path, list):
                    # Handle multiple screen spec files
                    screens = []
                    for path in file_path:
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            path, ScreenSpecification
                        )
                        if is_valid:
                            screens.append(validated_obj)
                        else:
                            self.add_issue('validation_error', 'error',
                                           f"Invalid screen specification: {path.name}",
                                           [str(path)], {'errors': errors})

                    # Create a ScreenSet from individual screens
                    if screens:
                        self.screen_specs = ScreenSet(
                            screens=screens,
                            entry_point=screens[0].id if screens else None
                        )
                        data['screen_specs'] = self.screen_specs

                else:
                    schema_class = schema_map.get(data_type)
                    if schema_class:
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            file_path, schema_class
                        )
                        if is_valid:
                            data[data_type] = validated_obj
                            # Set instance variables
                            if data_type == 'design_tokens':
                                self.design_tokens = validated_obj
                            elif data_type == 'component_catalog':
                                self.component_catalog = validated_obj
                            elif data_type == 'test_suite':
                                self.test_suite = validated_obj
                        else:
                            self.add_issue('validation_error', 'error',
                                           f"Invalid {data_type}: {file_path.name}",
                                           [str(file_path)], {'errors': errors})
                    else:
                        # Try to load as screen specification
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            file_path, ScreenSpecification
                        )
                        if is_valid:
                            self.screen_specs = ScreenSet(screens=[validated_obj])
                            data['screen_specs'] = self.screen_specs
                        else:
                            self.add_issue('validation_error', 'error',
                                           f"Unknown file type: {file_path.name}",
                                           [str(file_path)], {'errors': errors})

                if self.verbose:
                    print(f"✓ Loaded {data_type}: {file_path}")

            except Exception as e:
                self.add_issue('load_error', 'error',
                               f"Failed to load {data_type}: {str(e)}",
                               [str(file_path) if not isinstance(
                                   file_path, list) else str(file_path[0])],
                               {'exception': str(e)})

        return data

    def add_issue(self, issue_type: str, severity: str, description: str,
                  affected_files: List[str], details: Dict[str, Any] = None,
                  suggestion: str = None) -> None:
        """Add a consistency issue to the report."""
        issue = ConsistencyIssue(
            issue_type=issue_type,
            severity=severity,
            description=description,
            affected_files=affected_files,
            details=details or {},
            suggestion=suggestion
        )
        self.issues.append(issue)

    def check_component_consistency(self) -> None:
        """Check component-related consistency."""
        if not self.component_catalog:
            return

        # Check for orphaned component instances
        component_ids = {comp.id for comp in self.component_catalog.components}
        orphaned_instances = []

        for instance in self.component_catalog.instances:
            if instance.component_id not in component_ids:
                orphaned_instances.append(instance)

        if orphaned_instances:
            self.add_issue(
                'orphaned_component_instances',
                'warning',
                f"Found {len(orphaned_instances)} component instances with missing component definitions",
                ['component-catalog.json'],
                {
                    'orphaned_instances': [
                        {
                            'instance_id': inst.id,
                            'instance_name': inst.name,
                            'missing_component_id': inst.component_id
                        }
                        for inst in orphaned_instances
                    ]
                },
                "Remove orphaned instances or create missing component definitions"
            )

        # Check for components without properties
        components_without_properties = [
            comp for comp in self.component_catalog.components
            if not comp.properties
        ]

        if components_without_properties:
            self.add_issue(
                'components_without_properties',
                'warning',
                f"Found {len(components_without_properties)} components without defined properties",
                ['component-catalog.json'],
                {
                    'components': [
                        {
                            'component_id': comp.id,
                            'component_name': comp.name
                        }
                        for comp in components_without_properties
                    ]
                },
                "Define properties for these components to make them configurable"
            )

        # Check for duplicate component IDs
        component_id_counts = Counter(comp.id for comp in self.component_catalog.components)
        duplicate_ids = {comp_id for comp_id, count in component_id_counts.items() if count > 1}

        if duplicate_ids:
            self.add_issue(
                'duplicate_component_ids',
                'error',
                f"Found duplicate component IDs: {', '.join(duplicate_ids)}",
                ['component-catalog.json'],
                {
                    'duplicate_ids': list(duplicate_ids),
                    'counts': {comp_id: component_id_counts[comp_id] for comp_id in duplicate_ids}
                },
                "Ensure all component IDs are unique"
            )

    def check_design_token_consistency(self) -> None:
        """Check design token consistency."""
        if not self.design_tokens:
            return

        # Check for duplicate token names across categories
        all_token_names = []
        for category in ['colors', 'typography', 'spacing', 'shadows', 'border_radius']:
            tokens = getattr(self.design_tokens, category, [])
            for token in tokens:
                all_token_names.append(f"{category}.{token.name}")

        name_counts = Counter(all_token_names)
        duplicate_names = [name for name, count in name_counts.items() if count > 1]

        if duplicate_names:
            self.add_issue(
                'duplicate_token_names',
                'error',
                f"Found duplicate token names: {', '.join(duplicate_names)}",
                ['design-tokens.json'],
                {
                    'duplicate_names': duplicate_names,
                    'counts': {name: name_counts[name] for name in duplicate_names}
                },
                "Ensure all token names are unique across categories"
            )

        # Check for essential tokens
        primary_colors = [color for color in self.design_tokens.colors if 'primary' in color.name]
        if not primary_colors:
            self.add_issue(
                'missing_primary_colors',
                'warning',
                "No primary color tokens defined",
                ['design-tokens.json'],
                {
                    'available_color_categories': list(set(color.category for color in self.design_tokens.colors))
                },
                "Define primary color tokens for consistent branding"
            )

        # Check for typography scale consistency
        if len(self.design_tokens.typography) > 1:
            font_sizes = [typo.font_size for typo in self.design_tokens.typography]
            if len(set(font_sizes)) != len(font_sizes):
                self.add_issue(
                    'inconsistent_typography_scale',
                    'warning',
                    "Typography scale has duplicate font sizes",
                    ['design-tokens.json'],
                    {
                        'font_sizes': font_sizes,
                        'duplicates': [size for size, count in Counter(font_sizes).items() if count > 1]
                    },
                    "Ensure typography scale has consistent progression"
                )

    def check_screen_consistency(self) -> None:
        """Check screen specification consistency."""
        if not self.screen_specs:
            return

        screen_ids = {screen.id for screen in self.screen_specs.screens}

        # Check for duplicate screen IDs
        screen_id_counts = Counter(screen.id for screen in self.screen_specs.screens)
        duplicate_ids = {screen_id for screen_id, count in screen_id_counts.items() if count > 1}

        if duplicate_ids:
            self.add_issue(
                'duplicate_screen_ids',
                'error',
                f"Found duplicate screen IDs: {', '.join(duplicate_ids)}",
                ['screen-specs.json'],
                {
                    'duplicate_ids': list(duplicate_ids),
                    'counts': {screen_id: screen_id_counts[screen_id] for screen_id in duplicate_ids}
                },
                "Ensure all screen IDs are unique"
            )

        # Check navigation flow consistency
        invalid_navigation_refs = []
        for screen in self.screen_specs.screens:
            for nav_flow in screen.navigation_flows:
                if nav_flow.from_screen_id not in screen_ids:
                    invalid_navigation_refs.append({
                        'screen': screen.id,
                        'reference': nav_flow.from_screen_id,
                        'type': 'from_screen'
                    })
                if nav_flow.to_screen_id not in screen_ids:
                    invalid_navigation_refs.append({
                        'screen': screen.id,
                        'reference': nav_flow.to_screen_id,
                        'type': 'to_screen'
                    })

        if invalid_navigation_refs:
            self.add_issue(
                'invalid_navigation_references',
                'error',
                f"Found {len(invalid_navigation_refs)} invalid navigation references",
                ['screen-specs.json'],
                {
                    'invalid_references': invalid_navigation_refs
                },
                "Fix navigation references to point to existing screens"
            )

        # Check for screens without component instances
        screens_without_components = [
            screen for screen in self.screen_specs.screens
            if not screen.component_instances
        ]

        if screens_without_components:
            self.add_issue(
                'screens_without_components',
                'warning',
                f"Found {len(screens_without_components)} screens without component instances",
                ['screen-specs.json'],
                {
                    'screens': [
                        {
                            'screen_id': screen.id,
                            'screen_name': screen.name
                        }
                        for screen in screens_without_components
                    ]
                },
                "Add component instances to these screens or verify they are intentional placeholders"
            )

    def check_cross_reference_consistency(self) -> None:
        """Check consistency across different data types."""
        if not all([self.component_catalog, self.screen_specs]):
            return

        # Check component usage in screens
        component_ids = {comp.id for comp in self.component_catalog.components}
        used_component_ids = set()

        for screen in self.screen_specs.screens:
            for instance in screen.component_instances:
                used_component_ids.add(instance.component_id)

        # Find unused components
        unused_components = component_ids - used_component_ids

        if unused_components:
            self.add_issue(
                'unused_components',
                'info',
                f"Found {len(unused_components)} components not used in any screen",
                ['component-catalog.json', 'screen-specs.json'],
                {
                    'unused_component_ids': list(unused_components),
                    'total_components': len(component_ids),
                    'used_components': len(used_component_ids)
                },
                "Consider removing unused components or add them to screens"
            )

        # Find components used in screens but not defined
        missing_components = used_component_ids - component_ids

        if missing_components:
            self.add_issue(
                'missing_component_definitions',
                'error',
                f"Found {len(missing_components)} components used in screens but not defined",
                ['component-catalog.json', 'screen-specs.json'],
                {
                    'missing_component_ids': list(missing_components)
                },
                "Create missing component definitions or fix component references in screens"
            )

    def check_test_consistency(self) -> None:
        """Check test scenario consistency."""
        if not self.test_suite:
            return

        # Check for test scenarios without steps
        scenarios_without_steps = [
            scenario for scenario in self.test_suite.scenarios
            if not scenario.steps
        ]

        if scenarios_without_steps:
            self.add_issue(
                'scenarios_without_steps',
                'warning',
                f"Found {len(scenarios_without_steps)} test scenarios without steps",
                ['test-suite.json'],
                {
                    'scenarios': [
                        {
                            'scenario_id': scenario.id,
                            'scenario_name': scenario.name
                        }
                        for scenario in scenarios_without_steps
                    ]
                },
                "Add test steps to these scenarios or remove empty scenarios"
            )

        # Check for scenarios without success criteria
        scenarios_without_criteria = [
            scenario for scenario in self.test_suite.scenarios
            if not scenario.success_criteria
        ]

        if scenarios_without_criteria:
            self.add_issue(
                'scenarios_without_success_criteria',
                'warning',
                f"Found {len(scenarios_without_criteria)} scenarios without success criteria",
                ['test-suite.json'],
                {
                    'scenarios': [
                        {
                            'scenario_id': scenario.id,
                            'scenario_name': scenario.name
                        }
                        for scenario in scenarios_without_criteria
                    ]
                },
                "Define success criteria for these scenarios"
            )

        # Check for duplicate scenario IDs
        scenario_id_counts = Counter(scenario.id for scenario in self.test_suite.scenarios)
        duplicate_ids = {scenario_id for scenario_id,
                         count in scenario_id_counts.items() if count > 1}

        if duplicate_ids:
            self.add_issue(
                'duplicate_scenario_ids',
                'error',
                f"Found duplicate test scenario IDs: {', '.join(duplicate_ids)}",
                ['test-suite.json'],
                {
                    'duplicate_ids': list(duplicate_ids),
                    'counts': {scenario_id: scenario_id_counts[scenario_id] for scenario_id in duplicate_ids}
                },
                "Ensure all test scenario IDs are unique"
            )

    def check_test_screen_alignment(self) -> None:
        """Check alignment between test scenarios and screen specifications."""
        if not all([self.test_suite, self.screen_specs]):
            return

        screen_ids = {screen.id for screen in self.screen_specs.screens}
        referenced_screen_ids = set()

        # Extract screen references from test scenarios
        for scenario in self.test_suite.scenarios:
            for step in scenario.steps:
                for action in step.actions + step.validations:
                    if 'screen' in action.target.get('selector', '').lower():
                        # This is a simplified check - in practice, you'd parse
                        # the selector more carefully to extract screen references
                        referenced_screen_ids.add(action.target.get('selector', ''))

        # Note: This is a simplified implementation
        # A more thorough implementation would parse action targets more carefully
        if self.verbose:
            print(
                f"Screen-test alignment check: {len(screen_ids)} screens, {len(referenced_screen_ids)} references")

    def run_all_checks(self) -> ConsistencyReport:
        """
        Run all consistency checks.

        Returns:
            ConsistencyReport object
        """
        if self.verbose:
            print("Loading and validating data files...")

        # Load all data
        self.find_and_load_data()

        if self.verbose:
            print("Running consistency checks...")

        # Run individual checks
        self.check_component_consistency()
        self.check_design_token_consistency()
        self.check_screen_consistency()
        self.check_cross_reference_consistency()
        self.check_test_consistency()
        self.check_test_screen_alignment()

        # Count issues by severity
        error_count = sum(1 for issue in self.issues if issue.severity == 'error')
        warning_count = sum(1 for issue in self.issues if issue.severity == 'warning')
        info_count = sum(1 for issue in self.issues if issue.severity == 'info')

        # Generate summary
        summary = {
            'issue_types': Counter(issue.issue_type for issue in self.issues),
            'severity_breakdown': {
                'errors': error_count,
                'warnings': warning_count,
                'info': info_count
            },
            'data_status': {
                'design_tokens_loaded': self.design_tokens is not None,
                'component_catalog_loaded': self.component_catalog is not None,
                'screen_specs_loaded': self.screen_specs is not None,
                'test_suite_loaded': self.test_suite is not None
            }
        }

        return ConsistencyReport(
            total_files_analyzed=len([d for d in [self.design_tokens, self.component_catalog,
                                                  self.screen_specs, self.test_suite] if d]),
            total_issues=len(self.issues),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            issues=self.issues,
            summary=summary,
            metadata={
                'examples_directory': str(self.examples_dir),
                'checker_version': '1.0.0',
                'timestamp': str(Path(__file__).stat().st_mtime)
            }
        )

    def format_report_text(self, report: ConsistencyReport) -> str:
        """
        Format consistency report as text.

        Args:
            report: ConsistencyReport object

        Returns:
            Formatted text string
        """
        output = []
        output.append("=" * 70)
        output.append("DATA CONSISTENCY CHECK REPORT")
        output.append("=" * 70)
        output.append(f"Total Files Analyzed: {report.total_files_analyzed}")
        output.append(f"Total Issues: {report.total_issues}")
        output.append(f"Errors: {report.error_count}")
        output.append(f"Warnings: {report.warning_count}")
        output.append(f"Info: {report.info_count}")
        output.append("")

        # Data status
        output.append("DATA STATUS:")
        for data_type, loaded in report.summary['data_status'].items():
            status = "✓" if loaded else "✗"
            output.append(f"  {status} {data_type.replace('_', ' ').title()}")
        output.append("")

        # Group issues by severity
        issues_by_severity = {
            'error': [issue for issue in report.issues if issue.severity == 'error'],
            'warning': [issue for issue in report.issues if issue.severity == 'warning'],
            'info': [issue for issue in report.issues if issue.severity == 'info']
        }

        for severity, severity_issues in issues_by_severity.items():
            if severity_issues:
                output.append(f"{severity.upper()} ISSUES:")
                for issue in severity_issues:
                    icon = "✗" if severity == 'error' else "⚠" if severity == 'warning' else "ℹ"
                    output.append(f"  {icon} {issue.description}")
                    if self.verbose:
                        output.append(f"    Type: {issue.issue_type}")
                        output.append(f"    Files: {', '.join(issue.affected_files)}")
                        if issue.suggestion:
                            output.append(f"    Suggestion: {issue.suggestion}")
                output.append("")

        # Issue type summary
        if report.summary['issue_types']:
            output.append("ISSUE TYPE SUMMARY:")
            for issue_type, count in report.summary['issue_types'].items():
                output.append(f"  {issue_type}: {count}")
            output.append("")

        # Overall assessment
        if report.error_count == 0:
            if report.warning_count == 0:
                output.append("✓ No consistency issues found!")
            else:
                output.append(f"⚠ No errors, but {report.warning_count} warnings found")
        else:
            output.append(f"✗ {report.error_count} critical issues need to be resolved")

        return "\n".join(output)

    def format_report_json(self, report: ConsistencyReport) -> str:
        """
        Format consistency report as JSON.

        Args:
            report: ConsistencyReport object

        Returns:
            JSON string
        """
        # Convert issues to dictionaries
        issues_data = []
        for issue in report.issues:
            issues_data.append({
                'issue_type': issue.issue_type,
                'severity': issue.severity,
                'description': issue.description,
                'affected_files': issue.affected_files,
                'details': issue.details,
                'suggestion': issue.suggestion
            })

        report_data = {
            'summary': {
                'total_files_analyzed': report.total_files_analyzed,
                'total_issues': report.total_issues,
                'error_count': report.error_count,
                'warning_count': report.warning_count,
                'info_count': report.info_count
            },
            'issues': issues_data,
            'metadata': report.metadata
        }

        return json.dumps(report_data, indent=2, default=str)

    def save_report(self, report: ConsistencyReport, output_path: Path, format_type: str) -> None:
        """
        Save consistency report to file.

        Args:
            report: ConsistencyReport object
            output_path: Path to save report
            format_type: Output format ('text' or 'json')
        """
        if format_type == 'json':
            content = self.format_report_json(report)
        else:
            content = self.format_report_text(report)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Check data consistency across pipeline steps"
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
        # Create checker
        checker = DataConsistencyChecker(
            examples_dir=args.examples_dir,
            verbose=args.verbose
        )

        # Run checks
        report = checker.run_all_checks()

        # Output results
        if args.format == "json":
            output = checker.format_report_json(report)
        else:
            output = checker.format_report_text(report)

        print(output)

        # Save to file if requested
        if args.output:
            checker.save_report(report, args.output, args.format)
            if args.verbose:
                print(f"\nReport saved to: {args.output}")

        # Exit with error code if any errors found
        if report.error_count > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
