#!/usr/bin/env python3
"""
Content Collection CLI

CLI interface for content discovery and acquisition from various sources.
Provides source discovery and content fetching capabilities that feed into the RAG pipeline.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from source_discovery.discover import SourceDiscovery
    from content_fetching.fetcher import ContentFetcher
except ImportError as e:
    # Fallback for when modules are not yet available
    print(f"Import error: {e}", file=sys.stderr)
    print("Content Collection CLI is not fully available during initial setup", file=sys.stderr)
    SourceDiscovery = None
    ContentFetcher = None

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

def handle_discover_sources(args) -> str:
    """Discover sources for content collection"""
    try:
        if SourceDiscovery is None:
            return format_output({
                "error": "Source discovery module not available",
                "message": "Source discovery is not yet implemented"
            }, success=False)

        discovery = SourceDiscovery()
        sources = discovery.discover(
            query=args.query,
            source_type=args.source_type,
            limit=args.limit
        )

        data = {
            "query": args.query,
            "source_type": args.source_type,
            "total_found": len(sources),
            "sources": sources
        }
        return format_output(data, args.format)

    except Exception as e:
        return format_output({
            "error": str(e),
            "query": args.query
        }, success=False)

def handle_fetch_content(args) -> str:
    """Fetch content from discovered sources"""
    try:
        if ContentFetcher is None:
            return format_output({
                "error": "Content fetcher module not available",
                "message": "Content fetching is not yet implemented"
            }, success=False)

        # Load sources from file or use provided sources
        if args.sources_file:
            with open(args.sources_file, 'r') as f:
                sources = json.load(f)
        else:
            sources = json.loads(args.sources) if args.sources else []

        fetcher = ContentFetcher()
        results = fetcher.fetch_all(
            sources=sources,
            output_dir=args.output_dir,
            parallel=args.parallel
        )

        data = {
            "total_sources": len(sources),
            "successful_fetches": results.get("successful", 0),
            "failed_fetches": results.get("failed", 0),
            "output_directory": args.output_dir,
            "results": results.get("details", [])
        }
        return format_output(data, args.format)

    except Exception as e:
        return format_output({
            "error": str(e),
            "sources_file": args.sources_file
        }, success=False)

def handle_status(args) -> str:
    """Get content collection system status"""
    try:
        data = {
            "component": "03-content-collection",
            "status": "documentation_only",
            "modules": {
                "source_discovery": SourceDiscovery is not None,
                "content_fetching": ContentFetcher is not None
            },
            "capabilities": [
                "Source discovery and validation",
                "Content acquisition and download",
                "Integration with extractors",
                "Pipeline orchestration"
            ],
            "integration_points": [
                "04-extractors: Uses discovered sources",
                "02-rag-builder: Processes extracted content",
                "00-rag-registry: Stores processed content"
            ]
        }
        return format_output(data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, success=False)

def handle_list_source_types(args) -> str:
    """List available source types"""
    try:
        data = {
            "available_source_types": [
                {
                    "type": "github",
                    "description": "GitHub repositories and content",
                    "supported": True,
                    "examples": ["component libraries", "UI frameworks", "documentation"]
                },
                {
                    "type": "npm",
                    "description": "NPM packages and metadata",
                    "supported": False,
                    "examples": ["react components", "utility libraries", "hooks"]
                },
                {
                    "type": "documentation",
                    "description": "Documentation sites and guides",
                    "supported": False,
                    "examples": ["API docs", "user guides", "tutorials"]
                },
                {
                    "type": "community",
                    "description": "Community resources and examples",
                    "supported": False,
                    "examples": ["blog posts", "code examples", "tutorials"]
                }
            ]
        }
        return format_output(data, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, success=False)

def main():
    parser = argparse.ArgumentParser(
        description="Content Collection CLI - Source discovery and content acquisition for simflo-rag",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover React component sources
  python3 content_collection_cli.py discover --query "react components" --source-type github --limit 10

  # Fetch content from discovered sources
  python3 content_collection_cli.py fetch --sources-file sources.json --output-dir raw_content/

  # Get system status
  python3 content_collection_cli.py status

  # List available source types
  python3 content_collection_cli.py list-source-types
        """
    )

    parser.add_argument('--format', choices=['json', 'table'], default='json',
                       help='Output format (default: json)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover content sources')
    discover_parser.add_argument('--query', required=True,
                                help='Search query for discovering sources')
    discover_parser.add_argument('--source-type', choices=['github', 'npm', 'documentation', 'community'],
                                default='github', help='Type of sources to discover')
    discover_parser.add_argument('--limit', type=int, default=20,
                                help='Maximum number of sources to discover (default: 20)')
    discover_parser.add_argument('--output', help='Output file for discovered sources')

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch content from sources')
    fetch_parser.add_argument('--sources-file', help='JSON file containing sources to fetch')
    fetch_parser.add_argument('--sources', help='JSON string containing sources to fetch')
    fetch_parser.add_argument('--output-dir', default='fetched_content',
                              help='Output directory for fetched content (default: fetched_content)')
    fetch_parser.add_argument('--parallel', action='store_true',
                              help='Enable parallel fetching')

    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')

    # List source types command
    list_parser = subparsers.add_parser('list-source-types', help='List available source types')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate handler
    handlers = {
        'discover': handle_discover_sources,
        'fetch': handle_fetch_content,
        'status': handle_status,
        'list-source-types': handle_list_source_types
    }

    handler = handlers.get(args.command)
    if handler:
        result = handler(args)
        print(result)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()