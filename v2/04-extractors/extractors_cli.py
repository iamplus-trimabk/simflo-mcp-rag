#!/usr/bin/env python3
"""
SimFlo MCP RAG - Extractors CLI

Command-line interface for orchestrating content extraction from various sources.
Provides access to specialized extractors for different component libraries and documentation.
"""

import argparse
import json
import sys
import os
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add the current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Also add the core directory
core_dir = Path(__file__).parent / 'core'
sys.path.insert(0, str(core_dir))

try:
    from simple_extractor_factory import SimpleExtractorFactory
except ImportError as e:
    print(f"Error importing simple extractor factory: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Core extractors dir exists: {(Path(__file__).parent / 'core').exists()}")

    # Try to provide more helpful error info
    extractors_dir = Path(__file__).parent / 'core'
    if extractors_dir.exists():
        files = list(extractors_dir.glob('*.py'))
        print(f"Files in core extractors: {[f.name for f in files]}")

    sys.exit(1)


def format_output(data: Any, format_type: str = "json", success: bool = True) -> str:
    """Format output data in specified format"""
    if format_type == "json":
        output = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        return json.dumps(output, indent=2, default=str)
    elif format_type == "table":
        # Simple table format for human readability
        if isinstance(data, list):
            return "\n".join([str(item) for item in data])
        else:
            return str(data)
    else:
        return str(data)


def handle_list_extractors(args) -> str:
    """List all available extractors"""
    try:
        factory = SimpleExtractorFactory()
        extractors = factory.get_available_extractors()

        data = {
            "total_extractors": len(extractors),
            "extractors": extractors
        }

        return format_output(data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_extractor(args) -> str:
    """Run a specific extractor"""
    try:
        factory = SimpleExtractorFactory()

        # Get available extractors to validate
        available_extractors = factory.get_available_extractors()
        if args.name not in available_extractors:
            return format_output({
                "error": f"Extractor '{args.name}' not found. Available: {list(available_extractors.keys())}"
            }, args.format, success=False)

        # Run extraction using the simple factory
        print(f"Running {args.name} extractor...")
        result = factory.run_extractor(args.name)

        if "error" in result:
            return format_output(result, args.format, success=False)

        data = {
            "extractor": args.name,
            "status": "completed",
            "result": result,
            "message": f"Extractor {args.name} executed successfully"
        }

        return format_output(data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_all_extractors(args) -> str:
    """Run all available extractors"""
    try:
        factory = SimpleExtractorFactory()
        extractors = factory.get_available_extractors()

        results = []

        for extractor_name in extractors.keys():
            try:
                print(f"Running {extractor_name} extractor...")
                result = factory.run_extractor(extractor_name)

                data = {
                    "extractor": extractor_name,
                    "status": "completed" if "error" not in result else "failed",
                    "result": result
                }
                results.append(data)

            except Exception as e:
                results.append({
                    "extractor": extractor_name,
                    "status": "failed",
                    "error": str(e)
                })

        response_data = {
            "total_extractors": len(extractors),
            "results": results,
            "summary": {
                "completed": len([r for r in results if r["status"] == "completed"]),
                "failed": len([r for r in results if r["status"] == "failed"])
            }
        }

        return format_output(response_data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_status(args) -> str:
    """Get extractor system status"""
    try:
        factory = SimpleExtractorFactory()
        extractors = factory.get_available_extractors()

        # Check if extractors directory exists and has modules
        extractors_dir = Path(__file__).parent / "core"
        extractor_modules = list(extractors_dir.glob("*extractor*.py")) if extractors_dir.exists() else []

        data = {
            "extractors_available": len(extractors),
            "extractor_modules_found": len(extractor_modules),
            "extractors_directory": str(extractors_dir),
            "directory_exists": extractors_dir.exists(),
            "extractors": list(extractors.keys()),
            "factory_type": "SimpleExtractorFactory",
            "working_extractors": [name for name, info in extractors.items() if "error" not in info]
        }

        return format_output(data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SimFlo MCP RAG - Extractors CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-extractors --format json
  %(prog)s run-extractor shadcn --format json
  %(prog)s run-all-extractors --format json
  %(prog)s status --format json

For comprehensive usage guide, see:
  v2/extractors/user_guide.md
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List extractors command
    list_parser = subparsers.add_parser('list-extractors', help='List all available extractors')
    list_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Run extractor command
    run_parser = subparsers.add_parser('run-extractor', help='Run a specific extractor')
    run_parser.add_argument('name', help='Extractor name to run')
    run_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Run all extractors command
    run_all_parser = subparsers.add_parser('run-all-extractors', help='Run all available extractors')
    run_all_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Status command
    status_parser = subparsers.add_parser('status', help='Get extractor system status')
    status_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == 'list-extractors':
        print(handle_list_extractors(args))
    elif args.command == 'run-extractor':
        print(handle_run_extractor(args))
    elif args.command == 'run-all-extractors':
        print(handle_run_all_extractors(args))
    elif args.command == 'status':
        print(handle_status(args))
    elif args.command is None:
        parser.print_help()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()