#!/usr/bin/env python3
"""
SimFlo MCP RAG - MCP Server CLI

Command-line interface for AI assistants to search and interact with component registries.
Provides all MCP functionality through CLI commands with JSON output.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add the data-pipeline directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "data-pipeline"))

try:
    from registry_manager import get_registry_manager, RegistryInfo
    from context_manager import get_context_manager, PlatformContext
    from vector_store import VectorStore
    from parse_registry import ShadcnComponent
except ImportError as e:
    print(f"Error importing data-pipeline modules: {e}")
    print("Make sure data-pipeline/ directory exists and contains required modules")
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


def handle_search(args) -> str:
    """Search for components using natural language query"""
    try:
        registry_manager = get_registry_manager()
        context_manager = get_context_manager()

        # Get current context for platform-aware search
        current_context = context_manager.get_context()

        # Build platform context if platform specified
        platform_context = None
        if hasattr(args, 'platform') and args.platform:
            from context_manager import PlatformContext
            platform_context = PlatformContext(args.platform)

        results = registry_manager.search_components(
            query=args.query,
            platform_context=platform_context,
            limit=args.limit
        )

        # Format results similar to original MCP server
        components = []
        for result in results:
            component = result.component
            component.update({
                "registry": result.registry,
                "relevance_score": result.relevance_score,
                "platform_relevance": result.platform_relevance
            })
            components.append(component)

        return format_output({
            "query": args.query,
            "platform": getattr(args, 'platform', current_context.platform if current_context else None),
            "total_found": len(components),
            "components": components
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_get_component(args) -> str:
    """Get detailed information about a specific component"""
    try:
        registry_manager = get_registry_manager()

        component = registry_manager.get_component_details(
            component_name=args.name,
            registry_name=args.registry
        )

        if not component:
            return format_output({
                "error": f"Component '{args.name}' not found"
            }, args.format, success=False)

        return format_output(component, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_list_components(args) -> str:
    """List available components by type or registry"""
    try:
        registry_manager = get_registry_manager()

        # Build platform context if platform specified
        platform_context = None
        if hasattr(args, 'platform') and args.platform:
            from context_manager import PlatformContext
            platform_context = PlatformContext(args.platform)

        components = registry_manager.list_components(
            registry_name=args.registry,
            platform_context=platform_context,
            limit=args.limit
        )

        return format_output({
            "type": args.type,
            "registry": args.registry,
            "platform": getattr(args, 'platform', None),
            "total_count": len(components),
            "components": components
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_set_context(args) -> str:
    """Set platform context for intelligent component recommendations"""
    try:
        context_manager = get_context_manager()

        context = context_manager.set_context(
            platform=args.platform,
            session_id=args.session_id,
            user_agent=getattr(args, 'user_agent', None),
            project_type=getattr(args, 'project_type', None)
        )

        return format_output(context, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_get_context(args) -> str:
    """Get current platform context"""
    try:
        context_manager = get_context_manager()

        context = context_manager.get_context(args.session_id)

        if not context:
            return format_output({
                "message": "No platform context is currently set"
            }, args.format)

        return format_output(context, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_list_registries(args) -> str:
    """List available component registries"""
    try:
        registry_manager = get_registry_manager()

        # Build platform context if platform specified
        platform_context = None
        if hasattr(args, 'platform') and args.platform:
            from context_manager import PlatformContext
            platform_context = PlatformContext(args.platform)

        registries = registry_manager.get_available_registries(platform=platform_context)

        return format_output({
            "platform": getattr(args, 'platform', None),
            "total_registries": len(registries),
            "registries": registries
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_extraction(args) -> str:
    """Run extraction pipeline for components - not implemented"""
    return format_output({
        "error": "Extraction functionality not yet implemented in CLI architecture"
    }, args.format, success=False)


def handle_extraction_status(args) -> str:
    """Get extraction pipeline status - not implemented"""
    return format_output({
        "message": "Extraction status functionality not yet implemented in CLI architecture"
    }, args.format)


def handle_list_extraction_registries(args) -> str:
    """List available extraction registries - not implemented"""
    return format_output({
        "message": "Extraction registries functionality not yet implemented in CLI architecture"
    }, args.format)


def handle_clear_extraction_data(args) -> str:
    """Clear extracted data - not implemented"""
    return format_output({
        "error": "Extraction data clearing functionality not yet implemented in CLI architecture"
    }, args.format, success=False)


def handle_search_by_category(args) -> str:
    """Search components within specific categories"""
    try:
        registry_manager = get_registry_manager()

        results = registry_manager.search_components_by_category(
            query=args.query,
            category=args.category,
            platform=getattr(args, 'platform', None),
            limit=args.limit
        )

        return format_output({
            "query": args.query,
            "category": args.category,
            "platform": getattr(args, 'platform', None),
            "total_found": len(results.get('results', [])),
            "results": results.get('results', [])
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_list_registry_sources(args) -> str:
    """List detailed sources for a specific registry - not implemented"""
    return format_output({
        "error": "Registry sources functionality not yet implemented in CLI architecture"
    }, args.format, success=False)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SimFlo MCP RAG - CLI Server for AI Assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search --query "button" --limit 10 --format json
  %(prog)s get-component --name dialog --registry shadcn_db --format json
  %(prog)s set-context --platform reactjs --format json
  %(prog)s run-extraction --registry shadcn --mode test --format json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for components')
    search_parser.add_argument('query', help='Natural language search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results (default: 10)')
    search_parser.add_argument('--platform', choices=['reactjs', 'reactnative', 'auto', 'none'], help='Target platform')
    search_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Get component command
    get_parser = subparsers.add_parser('get-component', help='Get component details')
    get_parser.add_argument('name', help='Component name')
    get_parser.add_argument('--registry', help='Specific registry to search')
    get_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # List components command
    list_parser = subparsers.add_parser('list-components', help='List available components')
    list_parser.add_argument('--type', choices=['ui', 'block', 'hook'], help='Filter by component type')
    list_parser.add_argument('--registry', help='Specific registry to search')
    list_parser.add_argument('--platform', choices=['reactjs', 'reactnative', 'auto', 'none'], help='Filter by platform')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum results (default: 20)')
    list_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Context management commands
    set_context_parser = subparsers.add_parser('set-context', help='Set platform context')
    set_context_parser.add_argument('platform', choices=['reactjs', 'reactnative', 'auto', 'none'], help='Target platform')
    set_context_parser.add_argument('--session-id', help='Optional session identifier')
    set_context_parser.add_argument('--user-agent', help='Optional user agent information')
    set_context_parser.add_argument('--project-type', help='Optional project type information')
    set_context_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    get_context_parser = subparsers.add_parser('get-context', help='Get current platform context')
    get_context_parser.add_argument('--session-id', help='Optional session identifier')
    get_context_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Registry commands
    list_registries_parser = subparsers.add_parser('list-registries', help='List available registries')
    list_registries_parser.add_argument('--platform', choices=['reactjs', 'reactnative', 'auto', 'none'], help='Filter by platform')
    list_registries_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Extraction management commands
    extraction_parser = subparsers.add_parser('run-extraction', help='Run extraction pipeline')
    extraction_parser.add_argument('--registry', help='Specific registry to extract')
    extraction_parser.add_argument('--source', help='Specific source within registry')
    extraction_parser.add_argument('--mode', choices=['test', 'real'], default='test', help='Extraction mode')
    extraction_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    status_parser = subparsers.add_parser('extraction-status', help='Get extraction pipeline status')
    status_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    list_extraction_parser = subparsers.add_parser('list-extraction-registries', help='List extraction registries')
    list_extraction_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    clear_parser = subparsers.add_parser('clear-extraction-data', help='Clear extracted data')
    clear_parser.add_argument('--registry', help='Specific registry to clear')
    clear_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Category search
    category_search_parser = subparsers.add_parser('search-by-category', help='Search by category')
    category_search_parser.add_argument('query', help='Search query')
    category_search_parser.add_argument('category', choices=['components', 'hooks', 'blocks'], help='Component category')
    category_search_parser.add_argument('--platform', choices=['reactjs', 'reactnative', 'auto', 'none'], help='Target platform')
    category_search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    category_search_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Registry sources
    sources_parser = subparsers.add_parser('list-registry-sources', help='List registry sources')
    sources_parser.add_argument('registry', help='Registry name')
    sources_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate handler
    command_handlers = {
        'search': handle_search,
        'get-component': handle_get_component,
        'list-components': handle_list_components,
        'set-context': handle_set_context,
        'get-context': handle_get_context,
        'list-registries': handle_list_registries,
        'run-extraction': handle_run_extraction,
        'extraction-status': handle_extraction_status,
        'list-extraction-registries': handle_list_extraction_registries,
        'clear-extraction-data': handle_clear_extraction_data,
        'search-by-category': handle_search_by_category,
        'list-registry-sources': handle_list_registry_sources,
    }

    handler = command_handlers.get(args.command)
    if handler:
        try:
            result = handler(args)
            print(result)
        except KeyboardInterrupt:
            print(format_output({"error": "Operation cancelled"}, args.format, success=False))
            sys.exit(1)
        except Exception as e:
            print(format_output({"error": f"Command failed: {str(e)}"}, args.format, success=False))
            sys.exit(1)
    else:
        print(format_output({"error": f"Unknown command: {args.command}"}, args.format, success=False))
        sys.exit(1)


if __name__ == "__main__":
    main()