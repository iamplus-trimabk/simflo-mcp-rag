#!/usr/bin/env python3
"""
Generate complete pipeline test configuration from example data.

This script creates comprehensive test configurations for the Figma-to-RAG pipeline
by analyzing example data and generating appropriate input/output mappings,
test scenarios, and expected validation results.

Usage:
    python scripts/generate-pipeline-test.py [--examples-dir DIR] [--output-dir DIR] [--verbose]

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from v2.common.validation import create_validator
from v2.common.schemas import (
    DesignTokenSet,
    ComponentCatalog,
    ScreenSet,
    TestSuite,
    PipelineStepType
)
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class PipelineStepConfig:
    """Configuration for a single pipeline step."""
    step_name: str
    step_type: str
    input_files: List[str]
    output_files: List[str]
    configuration: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_schema: str
    dependencies: List[str]


@dataclass
class PipelineTestConfig:
    """Complete pipeline test configuration."""
    pipeline_name: str
    version: str
    description: str
    steps: List[PipelineStepConfig]
    test_data_sources: List[str]
    expected_outputs: Dict[str, Any]
    validation_rules: Dict[str, Any]
    metadata: Dict[str, Any]


class PipelineTestGenerator:
    """Generates comprehensive test configurations for the pipeline."""

    def __init__(self, examples_dir: Path, verbose: bool = False):
        """
        Initialize the test generator.

        Args:
            examples_dir: Path to examples directory
            verbose: Enable verbose output
        """
        self.examples_dir = examples_dir
        self.verbose = verbose
        self.validator = create_validator(strict_mode=False)

        # Pipeline step definitions
        self.pipeline_steps = [
            {
                'name': 'figma-analyzer',
                'type': PipelineStepType.FIGMA_ANALYZER,
                'description': 'Extract design assets from Figma URL',
                'input_schema': None,  # Takes Figma URL, not JSON
                'output_schemas': ['DesignTokenSet', 'ComponentCatalog', 'ScreenSet']
            },
            {
                'name': 'prototype-analyzer',
                'type': PipelineStepType.PROTOTYPE_ANALYZER,
                'description': 'Analyze user interactions and test scenarios',
                'input_schemas': ['ComponentCatalog'],
                'output_schemas': ['TestSuite']
            },
            {
                'name': 'token-converter',
                'type': PipelineStepType.TOKEN_CONVERTER,
                'description': 'Convert design tokens to framework definitions',
                'input_schemas': ['DesignTokenSet'],
                'output_schemas': ['DesignTokenSet']  # Converted tokens
            },
            {
                'name': 'component-generator',
                'type': PipelineStepType.COMPONENT_GENERATOR,
                'description': 'Generate React components from catalog',
                'input_schemas': ['ComponentCatalog', 'DesignTokenSet'],
                'output_schemas': ['ComponentCatalog']  # Generated components
            },
            {
                'name': 'page-generator',
                'type': PipelineStepType.PAGE_GENERATOR,
                'description': 'Create page implementations from screen specs',
                'input_schemas': ['ScreenSet', 'ComponentCatalog'],
                'output_schemas': ['ScreenSet']  # Generated pages
            },
            {
                'name': 'test-generator',
                'type': PipelineStepType.TEST_GENERATOR,
                'description': 'Generate E2E test suites',
                'input_schemas': ['TestSuite', 'ScreenSet'],
                'output_schemas': ['TestSuite']  # Generated tests
            },
            {
                'name': 'test-runner',
                'type': PipelineStepType.TEST_RUNNER,
                'description': 'Execute tests and provide demo',
                'input_schemas': ['TestSuite'],
                'output_schemas': []  # Test results and demo
            },
            {
                'name': 'rag-system',
                'type': PipelineStepType.RAG_SYSTEM,
                'description': 'Create RAG knowledge bases',
                'input_schemas': ['DesignTokenSet', 'ComponentCatalog', 'ScreenSet', 'TestSuite'],
                'output_schemas': ['RAGKnowledgeBase']
            },
            {
                'name': 'ai-assistant',
                'type': PipelineStepType.AI_ASSISTANT,
                'description': 'AI-powered code review',
                'input_schemas': ['RAGKnowledgeBase'],
                'output_schemas': []  # Analysis and suggestions
            }
        ]

    def find_example_files(self) -> Dict[str, Path]:
        """
        Find and categorize example files.

        Returns:
            Dictionary mapping file types to file paths
        """
        files = {}

        # Look for specific file patterns
        patterns = {
            'design_tokens': ['*design-tokens*.json'],
            'component_catalog': ['*component-catalog*.json'],
            'screen_specs': ['*screen*.json'],
            'test_suite': ['*test*.json', '*test-suite*.json'],
            'figma_data': ['*figma*.json']
        }

        for file_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = list(self.examples_dir.glob(pattern))
                if matches:
                    files[file_type] = matches[0]  # Take first match
                    break

        # Look for screen specs in subdirectories
        screen_specs_dir = self.examples_dir / 'screen-specs'
        if screen_specs_dir.exists():
            screen_files = list(screen_specs_dir.glob('*.json'))
            if screen_files:
                files['screen_specs'] = screen_files

        return files

    def validate_example_files(self, files: Dict[str, Path]) -> Dict[str, Tuple[bool, Any, List[str]]]:
        """
        Validate all example files.

        Args:
            files: Dictionary of file paths

        Returns:
            Dictionary mapping file types to validation results
        """
        validation_results = {}

        # Schema mapping
        schema_map = {
            'design_tokens': DesignTokenSet,
            'component_catalog': ComponentCatalog,
            'screen_specs': ScreenSet,  # For multiple screens
            'test_suite': TestSuite
        }

        for file_type, file_path in files.items():
            if isinstance(file_path, list):
                # Handle multiple files (like screen specs)
                for i, path in enumerate(file_path):
                    schema_class = schema_map.get(file_type, ScreenSet)
                    try:
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            path, schema_class
                        )
                        validation_results[f"{file_type}_{i}"] = (is_valid, validated_obj, errors)
                    except Exception as e:
                        validation_results[f"{file_type}_{i}"] = (False, None, [str(e)])
            else:
                schema_class = schema_map.get(file_type)
                if schema_class:
                    try:
                        is_valid, validated_obj, errors = self.validator.validate_json_file(
                            file_path, schema_class
                        )
                        validation_results[file_type] = (is_valid, validated_obj, errors)
                    except Exception as e:
                        validation_results[file_type] = (False, None, [str(e)])

        return validation_results

    def generate_step_config(self, step_def: Dict[str, Any],
                             available_files: Dict[str, Path],
                             validation_results: Dict[str, Tuple[bool, Any, List[str]]]) -> PipelineStepConfig:
        """
        Generate configuration for a single pipeline step.

        Args:
            step_def: Step definition
            available_files: Available example files
            validation_results: Validation results for files

        Returns:
            PipelineStepConfig object
        """
        step_name = step_def['name']
        input_schemas = step_def.get('input_schemas', [])
        output_schemas = step_def.get('output_schemas', [])

        # Determine input files
        input_files = []
        if input_schemas:
            for schema in input_schemas:
                # Find corresponding files
                if schema == 'DesignTokenSet' and 'design_tokens' in available_files:
                    input_files.append(str(available_files['design_tokens']))
                elif schema == 'ComponentCatalog' and 'component_catalog' in available_files:
                    input_files.append(str(available_files['component_catalog']))
                elif schema == 'ScreenSet' and 'screen_specs' in available_files:
                    if isinstance(available_files['screen_specs'], list):
                        input_files.extend([str(f) for f in available_files['screen_specs']])
                    else:
                        input_files.append(str(available_files['screen_specs']))
                elif schema == 'TestSuite' and 'test_suite' in available_files:
                    input_files.append(str(available_files['test_suite']))

        # Special case for figma-analyzer (takes URL, not files)
        if step_name == 'figma-analyzer':
            input_files = []  # Will be configured with Figma URL

        # Determine output files (generate expected paths)
        output_files = []
        output_dir = Path("output")

        if output_schemas:
            for schema in output_schemas:
                if schema == 'DesignTokenSet':
                    output_files.append(str(output_dir / "design-tokens.json"))
                elif schema == 'ComponentCatalog':
                    output_files.append(str(output_dir / "component-catalog.json"))
                elif schema == 'ScreenSet':
                    output_files.append(str(output_dir / "screen-specs.json"))
                elif schema == 'TestSuite':
                    output_files.append(str(output_dir / "test-suite.json"))
                elif schema == 'RAGKnowledgeBase':
                    output_files.append(str(output_dir / "rag-knowledge-base.json"))

        # Generate step-specific configuration
        configuration = self._generate_step_configuration(step_name, input_files)

        # Generate expected results
        expected_results = self._generate_expected_results(step_name, validation_results)

        # Determine dependencies
        dependencies = []
        if step_name != 'figma-analyzer':
            # All steps depend on previous steps
            step_order = [s['name'] for s in self.pipeline_steps]
            current_index = step_order.index(step_name)
            dependencies = step_order[:current_index]

        return PipelineStepConfig(
            step_name=step_name,
            step_type=step_def['type'],
            input_files=input_files,
            output_files=output_files,
            configuration=configuration,
            expected_results=expected_results,
            validation_schema=output_schemas[0] if output_schemas else None,
            dependencies=dependencies
        )

    def _generate_step_configuration(self, step_name: str, input_files: List[str]) -> Dict[str, Any]:
        """Generate step-specific configuration."""
        base_config = {
            'enabled': True,
            'timeout': 300,  # 5 minutes
            'retry_count': 3,
            'log_level': 'INFO'
        }

        step_configs = {
            'figma-analyzer': {
                **base_config,
                'figma_url': 'https://www.figma.com/file/example',
                'extract_tokens': True,
                'extract_components': True,
                'extract_screens': True,
                'output_format': 'json'
            },
            'prototype-analyzer': {
                **base_config,
                'analyze_interactions': True,
                'generate_test_scenarios': True,
                'include_user_flows': True,
                'output_format': 'json'
            },
            'token-converter': {
                **base_config,
                'target_framework': 'tailwind',
                'output_format': 'css',
                'include_variants': True,
                'semantic_tokens': True
            },
            'component-generator': {
                **base_config,
                'target_library': 'shadcn',
                'framework': 'react',
                'typescript': True,
                'include_stories': True,
                'include_tests': True
            },
            'page-generator': {
                **base_config,
                'framework': 'react',
                'router': 'react-router',
                'include_state_management': True,
                'include_error_handling': True
            },
            'test-generator': {
                **base_config,
                'test_framework': 'playwright',
                'generate_e2e_tests': True,
                'include_accessibility_tests': True,
                'include_performance_tests': False
            },
            'test-runner': {
                **base_config,
                'headless': True,
                'generate_report': True,
                'include_screenshots': True,
                'include_video': False
            },
            'rag-system': {
                **base_config,
                'vector_db': 'chromadb',
                'embedding_model': 'all-MiniLM-L6-v2',
                'chunk_size': 1000,
                'chunk_overlap': 200
            },
            'ai-assistant': {
                **base_config,
                'model': 'gpt-4',
                'analyze_code_quality': True,
                'suggest_improvements': True,
                'security_analysis': True
            }
        }

        return step_configs.get(step_name, base_config)

    def _generate_expected_results(self, step_name: str,
                                   validation_results: Dict[str, Tuple[bool, Any, List[str]]]) -> Dict[str, Any]:
        """Generate expected results for a step."""
        base_results = {
            'status': 'success',
            'execution_time': '< 60 seconds',
            'output_valid': True,
            'error_count': 0,
            'warning_count': 0
        }

        # Step-specific expectations
        step_expectations = {
            'figma-analyzer': {
                **base_results,
                'extracted_colors': '> 5',
                'extracted_components': '> 3',
                'extracted_screens': '> 1'
            },
            'component-generator': {
                **base_results,
                'generated_components': '>= component catalog size',
                'typescript_interfaces': True,
                'component_stories': True
            },
            'test-generator': {
                **base_results,
                'generated_test_scenarios': '> 0',
                'e2e_tests': True,
                'accessibility_tests': True
            }
        }

        return step_expectations.get(step_name, base_results)

    def generate_pipeline_config(self) -> PipelineTestConfig:
        """
        Generate complete pipeline test configuration.

        Returns:
            PipelineTestConfig object
        """
        if self.verbose:
            print("Finding example files...")

        files = self.find_example_files()

        if self.verbose:
            print(f"Found {len(files)} example file types")
            for file_type, path in files.items():
                if isinstance(path, list):
                    print(f"  {file_type}: {len(path)} files")
                else:
                    print(f"  {file_type}: {path}")

        if self.verbose:
            print("Validating example files...")

        validation_results = self.validate_example_files(files)

        if self.verbose:
            valid_count = sum(1 for _, (is_valid, _, _) in validation_results.items() if is_valid)
            print(f"Validated {len(validation_results)} file groups, {valid_count} valid")

        # Generate step configurations
        steps = []
        for step_def in self.pipeline_steps:
            if self.verbose:
                print(f"Generating config for {step_def['name']}...")

            step_config = self.generate_step_config(step_def, files, validation_results)
            steps.append(step_config)

        # Generate test data sources
        test_data_sources = [str(path) for path in files.values() if not isinstance(path, list)]
        for path in files.values():
            if isinstance(path, list):
                test_data_sources.extend([str(p) for p in path])

        # Generate expected outputs
        expected_outputs = {
            'pipeline_execution': {
                'total_steps': len(steps),
                'expected_success_rate': 100.0,
                'max_execution_time': 600  # 10 minutes
            },
            'file_outputs': {
                'design_tokens': 'output/design-tokens.json',
                'component_catalog': 'output/component-catalog.json',
                'screen_specs': 'output/screen-specs.json',
                'test_suite': 'output/test-suite.json'
            }
        }

        # Generate validation rules
        validation_rules = {
            'required_steps': [step.step_name for step in steps if step.configuration.get('enabled', True)],
            'file_validation': True,
            'schema_validation': True,
            'consistency_validation': True,
            'performance_validation': True
        }

        return PipelineTestConfig(
            pipeline_name="figma-to-rag-test",
            version="1.0.0",
            description="Comprehensive test configuration for Figma-to-RAG pipeline",
            steps=steps,
            test_data_sources=test_data_sources,
            expected_outputs=expected_outputs,
            validation_rules=validation_rules,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0.0',
                'examples_directory': str(self.examples_dir),
                'total_example_files': len(test_data_sources)
            }
        )

    def save_config(self, config: PipelineTestConfig, output_path: Path) -> None:
        """
        Save pipeline configuration to file.

        Args:
            config: Pipeline test configuration
            output_path: Path to save configuration
        """
        # Convert to dictionary
        config_dict = asdict(config)

        # Save as JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, default=str)

        if self.verbose:
            print(f"Pipeline configuration saved to: {output_path}")

    def generate_summary_report(self, config: PipelineTestConfig) -> str:
        """
        Generate a summary report of the pipeline configuration.

        Args:
            config: Pipeline test configuration

        Returns:
            Formatted summary report
        """
        report = []
        report.append("=" * 70)
        report.append("PIPELINE TEST CONFIGURATION SUMMARY")
        report.append("=" * 70)
        report.append(f"Pipeline Name: {config.pipeline_name}")
        report.append(f"Version: {config.version}")
        report.append(f"Description: {config.description}")
        report.append(f"Generated At: {config.metadata.get('generated_at', 'Unknown')}")
        report.append("")

        # Step summary
        report.append(f"Total Steps: {len(config.steps)}")
        report.append("")

        enabled_steps = [step for step in config.steps if step.configuration.get('enabled', True)]
        report.append(f"Enabled Steps: {len(enabled_steps)}")
        for step in enabled_steps:
            report.append(f"  - {step.step_name} ({step.step_type})")
        report.append("")

        # Data sources
        report.append(f"Test Data Sources: {len(config.test_data_sources)}")
        for source in config.test_data_sources[:5]:  # Show first 5
            report.append(f"  - {source}")
        if len(config.test_data_sources) > 5:
            report.append(f"  ... and {len(config.test_data_sources) - 5} more")
        report.append("")

        # Expected outputs
        report.append("Expected Outputs:")
        for category, outputs in config.expected_outputs.items():
            report.append(f"  {category}:")
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    report.append(f"    {key}: {value}")
            else:
                report.append(f"    {outputs}")
        report.append("")

        # Validation rules
        report.append("Validation Rules:")
        for rule, value in config.validation_rules.items():
            report.append(f"  {rule}: {value}")

        return "\n".join(report)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Generate pipeline test configuration from example data"
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
        default=Path("test-configs"),
        help="Output directory for generated configurations (default: test-configs)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Provide detailed output"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only generate summary report, not full configuration"
    )

    args = parser.parse_args()

    try:
        # Create generator
        generator = PipelineTestGenerator(
            examples_dir=args.examples_dir,
            verbose=args.verbose
        )

        # Generate configuration
        config = generator.generate_pipeline_config()

        # Display summary
        summary = generator.generate_summary_report(config)
        print(summary)

        if not args.summary_only:
            # Save full configuration
            output_path = args.output_dir / "pipeline-test-config.json"
            generator.save_config(config, output_path)

            # Save step-by-step configurations
            steps_dir = args.output_dir / "steps"
            for step in config.steps:
                step_config_path = steps_dir / f"{step.step_name}-config.json"
                step_config_path.parent.mkdir(parents=True, exist_ok=True)

                with open(step_config_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(step), f, indent=2, default=str)

            if args.verbose:
                print(f"\nStep configurations saved to: {steps_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
