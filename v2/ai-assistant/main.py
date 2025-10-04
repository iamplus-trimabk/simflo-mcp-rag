# -*- coding: utf-8 -*-
"""
AI Assistant Step - Step 9 of the SimFlo Figma-to-RAG Pipeline.

This module provides AI-powered code review and improvement suggestions
using RAG knowledge bases created by previous pipeline steps.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from ai_analyzer import AIAnalyzer, AIAnalysisConfig
import logging
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the AI assistant."""
    parser = argparse.ArgumentParser(
        description='AI Assistant - Step 9 of the SimFlo Figma-to-RAG Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze pipeline outputs
  python v2/ai-assistant/main.py --rag-bases ./rag-output --code-dirs ./output/components ./output/pages --output ./ai-output

  # Custom analysis configuration
  python v2/ai-assistant/main.py --rag-bases ./rag-output --code-dirs ./output --output ./ai-output --confidence-threshold 0.7

  # Enable specific analysis types
  python v2/ai-assistant/main.py --rag-bases ./rag-output --code-dirs ./output --output ./ai-output --no-security --no-performance

  # Strict mode for higher standards
  python v2/ai-assistant/main.py --rag-bases ./rag-output --code-dirs ./output --output ./ai-output --strict
        """
    )

    # Required arguments
    parser.add_argument(
        '--rag-bases',
        type=Path,
        required=True,
        help='Directory containing RAG knowledge bases'
    )
    parser.add_argument(
        '--code-dirs',
        nargs='+',
        type=Path,
        required=True,
        help='Directories containing code to analyze'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output directory for analysis results'
    )

    # Configuration options
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.5,
        help='Minimum confidence threshold for issues (default: 0.5)'
    )
    parser.add_argument(
        '--max-issues-per-category',
        type=int,
        default=50,
        help='Maximum issues per category (default: 50)'
    )

    # Analysis type controls
    parser.add_argument(
        '--no-code-quality',
        action='store_true',
        help='Disable code quality analysis'
    )
    parser.add_argument(
        '--no-security',
        action='store_true',
        help='Disable security analysis'
    )
    parser.add_argument(
        '--no-performance',
        action='store_true',
        help='Disable performance analysis'
    )
    parser.add_argument(
        '--no-best-practices',
        action='store_true',
        help='Disable best practices analysis'
    )
    parser.add_argument(
        '--no-accessibility',
        action='store_true',
        help='Disable accessibility analysis'
    )

    # Scope controls
    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='Skip test file analysis'
    )
    parser.add_argument(
        '--no-docs',
        action='store_true',
        help='Skip documentation file analysis'
    )

    # Behavior controls
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict analysis mode'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input directories
    if not args.rag_bases.exists():
        logger.warning(f"RAG bases directory not found: {args.rag_bases}")

    for code_dir in args.code_dirs:
        if not code_dir.exists():
            logger.error(f"Code directory not found: {code_dir}")
            sys.exit(1)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Create analysis configuration
    config = AIAnalysisConfig(
        enable_code_quality_analysis=not args.no_code_quality,
        enable_security_analysis=not args.no_security,
        enable_performance_analysis=not args.no_performance,
        enable_best_practices_analysis=not args.no_best_practices,
        enable_accessibility_analysis=not args.no_accessibility,
        strict_mode=args.strict,
        confidence_threshold=args.confidence_threshold,
        max_issues_per_category=args.max_issues_per_category,
        include_rag_context=True,
        generate_improvement_suggestions=True,
        generate_refactoring_plan=True,
        analyze_test_files=not args.no_tests,
        analyze_documentation=not args.no_docs
    )

    try:
        # Create analyzer and run analysis
        analyzer = AIAnalyzer(config)

        result = analyzer.analyze_pipeline_outputs(
            rag_bases_dir=args.rag_bases,
            code_dirs=args.code_dirs,
            output_dir=args.output
        )

        # Print summary
        print("\n✅ AI-Powered Code Analysis Complete")
        print(f"   Processing time: {result.processing_time:.2f}s")

        # Handle summary safely
        if hasattr(result.summary, 'files_analyzed'):
            print(f"   Files analyzed: {result.summary.files_analyzed}")
            print(f"   Total issues found: {result.summary.total_issues}")
        elif isinstance(result.summary, dict):
            print(f"   Files analyzed: {result.summary.get('files_analyzed', 'unknown')}")
            print(f"   Total issues found: {result.summary.get('total_issues', 'unknown')}")
        else:
            print("   Files analyzed: error - summary not available")
            print(f"   Total issues found: {len(result.issues) if result.issues else 0}")

        print(f"   Overall quality score: {result.metrics.overall_score}/100")
        print(f"   Output directory: {args.output}")

        # Print quality metrics
        print("\n📊 Quality Metrics:")
        print(f"   Maintainability: {result.metrics.maintainability_score}/100")
        print(f"   Security: {result.metrics.security_score}/100")
        print(f"   Performance: {result.metrics.performance_score}/100")
        print(f"   Accessibility: {result.metrics.accessibility_score}/100")
        print(f"   Test Coverage: {result.metrics.test_coverage_score}/100")
        print(f"   Documentation: {result.metrics.documentation_score}/100")

        # Print issue breakdown
        print("\n📋 Issue Breakdown:")
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = len([issue for issue in result.issues if issue.severity.value == severity])
            if count > 0:
                print(f"   {severity.title()}: {count} issues")

        # Print top improvements
        if result.improvement_suggestions:
            print("\n💡 Top Improvement Suggestions:")
            for suggestion in result.improvement_suggestions[:3]:
                print(f"   • {suggestion.get('title', 'N/A')}")

        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                logger.error(f"  - {error}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                logger.warning(f"  - {warning}")

        logger.info(f"Analysis results saved to {args.output}")

    except Exception as e:
        logger.error(f"AI assistant failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
