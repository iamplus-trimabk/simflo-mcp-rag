#!/usr/bin/env python3
"""
RAG Builder CLI

CLI interface for building and managing RAG (Retrieval-Augmented Generation) pipelines.
Provides orchestration of content extraction, processing, and vector database construction.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from orchestrator import PipelineOrchestrator
except ImportError as e:
    # Fallback for when modules are not yet available
    print(f"Import error: {e}", file=sys.stderr)
    print("RAG Builder CLI is not fully available during migration", file=sys.stderr)
    PipelineOrchestrator = None

def format_output(data: Dict[str, Any], format_type: str = "json", success: bool = True) -> str:
    """Output formatter"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    if format_type == "json":
        return json.dumps(response, indent=2)
    else:
        return str(data)


def handle_check_prerequisites(args) -> str:
    """Check if all prerequisites are met"""
    try:
        orchestrator = PipelineOrchestrator()
        prerequisites = orchestrator.check_prerequisites()

        data = {
            "prerequisites": prerequisites,
            "all_satisfied": all(prerequisites.values()),
            "message": "All prerequisites are satisfied!" if all(prerequisites.values()) else "Some prerequisites are missing"
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_list_profiles(args) -> str:
    """List available extraction profiles"""
    try:
        orchestrator = PipelineOrchestrator()
        profiles = orchestrator.list_profiles()

        data = {
            "total_profiles": len(profiles),
            "profiles": profiles
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_validate_profile(args) -> str:
    """Validate a specific profile"""
    try:
        orchestrator = PipelineOrchestrator()
        validation = orchestrator.validate_profile(args.profile)

        data = {
            "profile": args.profile,
            "validation": validation
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_extraction(args) -> str:
    """Run extraction for a specific profile"""
    try:
        orchestrator = PipelineOrchestrator()
        options = {
            'verbose': args.verbose,
            'metadata_only': args.metadata_only
        }
        result = orchestrator.run_extraction(args.profile, options)

        data = {
            "extraction": result
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_multiple_extractions(args) -> str:
    """Run multiple extractions concurrently"""
    try:
        orchestrator = PipelineOrchestrator()
        options = {
            'verbose': args.verbose
        }
        results = orchestrator.run_multiple_extractions(args.profiles, options)

        data = {
            "requested_profiles": args.profiles,
            "results": results,
            "summary": {
                "total": len(args.profiles),
                "completed": sum(1 for r in results.values() if r.get('success')),
                "failed": sum(1 for r in results.values() if not r.get('success'))
            }
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_discover_repositories(args) -> str:
    """Discover repositories using GitHub CLI"""
    try:
        orchestrator = PipelineOrchestrator()
        result = orchestrator.discovery_mode(args.keywords, args.limit)

        data = {
            "discovery": result
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_status(args) -> str:
    """Generate pipeline status report"""
    try:
        orchestrator = PipelineOrchestrator()
        report = orchestrator.generate_report()

        data = {
            "status_report": report
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='RAG Builder CLI - Build and manage RAG pipelines',
        prog='rag_builder_cli'
    )

    # Create parent parser for common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--format', choices=['json', 'table'], default='json',
                             help='Output format (default: json)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # System check command
    check_parser = subparsers.add_parser('check', help='Check pipeline prerequisites', parents=[parent_parser])
    check_parser.set_defaults(func=handle_check_prerequisites)

    # Profile management commands
    list_parser = subparsers.add_parser('list-profiles', help='List available extraction profiles', parents=[parent_parser])
    list_parser.set_defaults(func=handle_list_profiles)

    validate_parser = subparsers.add_parser('validate', help='Validate extraction profile', parents=[parent_parser])
    validate_parser.add_argument('profile', help='Profile name to validate')
    validate_parser.set_defaults(func=handle_validate_profile)

    # Extraction commands
    run_parser = subparsers.add_parser('run', help='Run extraction for a profile', parents=[parent_parser])
    run_parser.add_argument('profile', help='Profile name to run')
    run_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    run_parser.add_argument('--metadata-only', action='store_true', help='Only extract metadata')
    run_parser.set_defaults(func=handle_run_extraction)

    multi_parser = subparsers.add_parser('run-multiple', help='Run multiple extractions', parents=[parent_parser])
    multi_parser.add_argument('profiles', nargs='+', help='Profile names to run')
    multi_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    multi_parser.set_defaults(func=handle_run_multiple_extractions)

    # Discovery command
    discovery_parser = subparsers.add_parser('discover', help='Discover repositories', parents=[parent_parser])
    discovery_parser.add_argument('keywords', nargs='+', help='Search keywords')
    discovery_parser.add_argument('--limit', type=int, default=10, help='Number of results (default: 10)')
    discovery_parser.set_defaults(func=handle_discover_repositories)

    # Status command
    status_parser = subparsers.add_parser('status', help='Generate pipeline status report', parents=[parent_parser])
    status_parser.set_defaults(func=handle_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        result = args.func(args)
        print(result)
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        error_msg = f"Error: {e}"
        print(format_output({"error": error_msg}, args.format, success=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())