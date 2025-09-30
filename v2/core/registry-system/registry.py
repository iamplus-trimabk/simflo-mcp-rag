#!/usr/bin/env python3
"""
SimFlo MCP RAG - Registry System CLI

Command-line interface for the registry system that manages multiple RAG databases
with context-aware routing and search capabilities.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the data-pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "data-pipeline"))

try:
    from registry_manager import get_registry_manager, RegistryInfo
except ImportError as e:
    print(f"Error importing registry_manager: {e}")
    print("Make sure data-pipeline/registry_manager.py exists")
    sys.exit(1)


def format_output(data: Any, format_type: str = "json") -> str:
    """Format output data in specified format"""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    elif format_type == "table":
        if isinstance(data, list):
            headers = []
            rows = []
            for item in data:
                if isinstance(item, dict) and not headers:
                    headers = list(item.keys())
                if isinstance(item, dict):
                    rows.append([str(item.get(h, "")) for h in headers])
                else:
                    rows.append([str(item)])

            if headers:
                output = " | ".join(headers) + "\n"
                output += "-" * len(" | ".join(headers)) + "\n"
                for row in rows:
                    output += " | ".join(row) + "\n"
                return output
            else:
                return "\n".join([str(item) for item in data])
        else:
            return str(data)
    else:
        return str(data)


def cmd_list(args):
    """List all available registries"""
    try:
        registry_manager = get_registry_manager()
        stats = registry_manager.get_registry_stats()

        # Extract registries from stats
        registries = []
        if "registries" in stats:
            for name, registry_info in stats["registries"].items():
                registry_info["name"] = name
                registries.append(registry_info)

        print(format_output(registries, args.format))
        return {"status": "success", "count": len(registries)}

    except Exception as e:
        error_output = {"status": "error", "message": str(e)}
        print(format_output(error_output, args.format))
        return error_output


def cmd_info(args):
    """Get information about a specific registry"""
    try:
        registry_manager = get_registry_manager()
        stats = registry_manager.get_registry_stats()

        if "registries" in stats and args.name in stats["registries"]:
            registry_info = stats["registries"][args.name]
            registry_info["name"] = args.name
            print(format_output(registry_info, args.format))
            return {"status": "success", "registry": registry_info}
        else:
            error_output = {"status": "error", "message": f"Registry '{args.name}' not found"}
            print(format_output(error_output, args.format))
            return error_output

    except Exception as e:
        error_output = {"status": "error", "message": str(e)}
        print(format_output(error_output, args.format))
        return error_output


def cmd_search(args):
    """Search across all registries"""
    try:
        registry_manager = get_registry_manager()

        # Search components
        results = registry_manager.search_components(
            query=args.query,
            limit=args.limit
        )

        # Convert SearchResult objects to dicts for JSON output
        output_results = []
        for result in results:
            if hasattr(result, '__dict__'):
                output_results.append(vars(result))
            else:
                output_results.append(result)

        output_data = {
            "query": args.query,
            "total_results": len(output_results),
            "results": output_results
        }

        print(format_output(output_data, args.format))
        return {"status": "success", "results": output_data}

    except Exception as e:
        error_output = {"status": "error", "message": str(e)}
        print(format_output(error_output, args.format))
        return error_output


def cmd_status(args):
    """Get registry system status"""
    try:
        registry_manager = get_registry_manager()
        stats = registry_manager.get_registry_stats()

        status_info = {
            "total_registries": stats.get("total_registries", 0),
            "active_registries": stats.get("active_registries", 0),
            "total_components": stats.get("total_components", 0),
            "system_health": "healthy"
        }

        print(format_output(status_info, args.format))
        return {"status": "success", "system_status": status_info}

    except Exception as e:
        error_output = {"status": "error", "message": str(e)}
        print(format_output(error_output, args.format))
        return error_output


def main():
    """Main CLI entry point"""
    # Create parent parser for common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)"
    )
    parent_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser = argparse.ArgumentParser(
        description="SimFlo MCP RAG Registry System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all registries
  %(prog)s list --format table           # List in table format
  %(prog)s info --name shadcn            # Get registry info
  %(prog)s search --query "button"       # Search all registries
  %(prog)s status                        # Get system status
        """,
        parents=[parent_parser]
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands", metavar="COMMAND")

    # List command
    list_parser = subparsers.add_parser("list", help="List all registries", parents=[parent_parser])
    list_parser.set_defaults(func=cmd_list)

    # Info command
    info_parser = subparsers.add_parser("info", help="Get registry information", parents=[parent_parser])
    info_parser.add_argument("--name", required=True, help="Registry name")
    info_parser.set_defaults(func=cmd_info)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search registries", parents=[parent_parser])
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Result limit (default: 10)")
    search_parser.add_argument("--include-metadata", action="store_true", help="Include metadata in results")
    search_parser.set_defaults(func=cmd_search)

    # Status command
    status_parser = subparsers.add_parser("status", help="Get system status", parents=[parent_parser])
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.verbose:
        print(f"Executing command: {args.command}", file=sys.stderr)

    result = args.func(args)

    if args.verbose:
        print(f"Command completed with status: {result.get('status', 'unknown')}", file=sys.stderr)


if __name__ == "__main__":
    main()