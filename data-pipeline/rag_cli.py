#!/usr/bin/env python3
"""
SimFlo MCP RAG - CLI Interface

Command-line interface for testing the RAG database with various query types.
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path

from vector_store import VectorStore
from parse_registry import ShadcnComponent


class RAGCLI:
    """Command-line interface for RAG database testing"""

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.vector_store = VectorStore(persist_dir)

        # Load components from JSON if vector store is empty but cache is empty
        if self.vector_store.collection.count() > 0 and not self.vector_store.components_cache:
            self._load_components_to_cache()

    def _load_components_to_cache(self):
        """Load components from JSON file into cache"""
        try:
            import json
            with open('components.json', 'r', encoding='utf-8') as f:
                components_data = json.load(f)

            for comp_data in components_data:
                # Convert file dictionaries back to RegistryFile objects
                files_data = comp_data.get('files', [])
                files = []
                for file_data in files_data:
                    from parse_registry import RegistryFile
                    files.append(RegistryFile(**file_data))

                comp_data['files'] = files
                component = ShadcnComponent(**comp_data)
                self.vector_store.components_cache[component.name] = component

            print(f"Loaded {len(self.vector_store.components_cache)} components to cache")
        except Exception as e:
            print(f"Warning: Could not load components to cache: {e}")

    def search_components(self, query: str, limit: int = 10) -> None:
        """Search for components using natural language"""
        print(f"\n🔍 Searching for: '{query}'")
        print("=" * 60)

        results = self.vector_store.search(query, limit)

        if not results:
            print("❌ No components found matching your query.")
            return

        print(f"✅ Found {len(results)} relevant components:\n")

        for i, result in enumerate(results, 1):
            component = result.component
            print(f"{i:2d}. {component.name} ({component.type})")
            print(f"    Relevance: {result.relevance_score:.3f}")

            if component.description:
                print(f"    Description: {component.description}")

            if component.categories:
                print(f"    Categories: {', '.join(component.categories)}")

            print(f"    Install: {component.installCommand}")

            if component.dependencies:
                print(f"    Dependencies: {', '.join(component.dependencies[:3])}")
                if len(component.dependencies) > 3:
                    print(f"                ... and {len(component.dependencies) - 3} more")

            print()

    def get_component_details(self, name: str) -> None:
        """Get detailed information about a specific component"""
        print(f"\n📋 Component Details: {name}")
        print("=" * 60)

        component = self.vector_store.get_component(name)
        if not component:
            print(f"❌ Component '{name}' not found.")
            return

        print(f"Name: {component.name}")
        print(f"Type: {component.type}")

        if component.description:
            print(f"Description: {component.description}")

        if component.categories:
            print(f"Categories: {', '.join(component.categories)}")

        print(f"\n📦 Installation:")
        print(f"  Command: {component.installCommand}")
        print(f"  Location: {component.fileLocation}")

        if component.dependencies:
            print(f"\n🔗 Dependencies ({len(component.dependencies)}):")
            for dep in component.dependencies:
                print(f"  - {dep}")

        if component.registryDependencies:
            print(f"\n🔗 Registry Dependencies ({len(component.registryDependencies)}):")
            for dep in component.registryDependencies:
                print(f"  - {dep}")

        if component.files:
            print(f"\n📁 Files ({len(component.files)}):")
            for file in component.files:
                print(f"  - {file.path} ({file.type})")

    def list_components(self, component_type: Optional[str] = None, limit: int = 20) -> None:
        """List components, optionally filtered by type"""
        print(f"\n📚 Component List")
        print("=" * 60)

        components = self.vector_store.get_all_components(component_type)

        if component_type:
            print(f"Showing {component_type} components ({len(components)} total)")
        else:
            print(f"Showing all components ({len(components)} total)")

        if not components:
            print("❌ No components found.")
            return

        # Limit display
        display_components = components[:limit]

        for i, component in enumerate(display_components, 1):
            print(f"{i:3d}. {component.name:<20} ({component.type})")
            if component.description:
                desc = component.description[:60] + "..." if len(component.description) > 60 else component.description
                print(f"      {desc}")

        if len(components) > limit:
            print(f"\n... and {len(components) - limit} more components not shown.")

    def show_stats(self) -> None:
        """Show database statistics"""
        print("\n📊 Database Statistics")
        print("=" * 60)

        stats = self.vector_store.get_stats()

        print(f"Total Components: {stats['total_components']}")
        print(f"Vector Store Entries: {stats['vector_store_count']}")

        print(f"\nComponents by Type:")
        for comp_type, count in stats['components_by_type'].items():
            print(f"  {comp_type.capitalize():<10}: {count:>3}")

        # Show some sample searches
        print(f"\n💡 Try these sample searches:")
        sample_queries = [
            "modal dialog popup",
            "form input validation",
            "calendar date picker",
            "table data grid",
            "navigation menu sidebar",
            "chart graph data visualization",
            "authentication login",
            "button click action"
        ]
        for query in sample_queries:
            print(f"  • '{query}'")

    def interactive_mode(self) -> None:
        """Start interactive CLI mode"""
        print("\n🎯 SimFlo RAG CLI - Interactive Mode")
        print("=" * 60)
        print("Available commands:")
        print("  search <query>     - Search for components")
        print("  details <name>     - Get component details")
        print("  list [type]        - List components (ui/block/hook)")
        print("  stats              - Show database statistics")
        print("  help               - Show this help")
        print("  quit/exit          - Exit CLI")
        print("=" * 60)

        while True:
            try:
                command = input("\n🔧 rag> ").strip()

                if not command:
                    continue

                if command.lower() in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break

                elif command.lower() == 'help':
                    print("Available commands:")
                    print("  search <query>     - Search for components")
                    print("  details <name>     - Get component details")
                    print("  list [type]        - List components (ui/block/hook)")
                    print("  stats              - Show database statistics")
                    print("  help               - Show this help")
                    print("  quit/exit          - Exit CLI")

                elif command.lower() == 'stats':
                    self.show_stats()

                elif command.startswith('search '):
                    query = command[7:].strip()
                    if query:
                        self.search_components(query, 5)
                    else:
                        print("❌ Please provide a search query.")

                elif command.startswith('details '):
                    name = command[8:].strip()
                    if name:
                        self.get_component_details(name)
                    else:
                        print("❌ Please provide a component name.")

                elif command.startswith('list '):
                    comp_type = command[5:].strip()
                    if comp_type.lower() in ['ui', 'block', 'hook']:
                        self.list_components(comp_type.lower(), 10)
                    elif not comp_type:
                        self.list_components(None, 10)
                    else:
                        print("❌ Invalid component type. Use: ui, block, hook, or leave empty for all.")

                elif command == 'list':
                    self.list_components(None, 10)

                else:
                    print(f"❌ Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="SimFlo RAG CLI - Test the shadcn components RAG database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "modal dialog"               # Search for modal components
  %(prog)s details button                      # Get button component details
  %(prog)s list ui                             # List all UI components
  %(prog)s list                                # List all components
  %(prog)s stats                               # Show database statistics
  %(prog)s interactive                         # Start interactive mode
        """
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=['search', 'details', 'list', 'stats', 'interactive'],
        help="Command to execute"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Search query or component name (for search/details commands)"
    )

    parser.add_argument(
        "--type",
        choices=['ui', 'block', 'hook'],
        help="Component type filter (for list command)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results to show"
    )

    parser.add_argument(
        "--persist-dir",
        default="./chroma_db",
        help="Vector store directory"
    )

    args = parser.parse_args()

    # Initialize CLI
    try:
        cli = RAGCLI(args.persist_dir)

        # Check if vector store is initialized
        if cli.vector_store.collection.count() == 0:
            print("❌ Vector store is empty. Please run the indexing first:")
            print("   python3 vector_store.py --stats")
            return 1

        # Execute command
        if args.command == 'search':
            if not args.query:
                print("❌ Please provide a search query.")
                return 1
            cli.search_components(args.query, args.limit)

        elif args.command == 'details':
            if not args.query:
                print("❌ Please provide a component name.")
                return 1
            cli.get_component_details(args.query)

        elif args.command == 'list':
            comp_type = args.type or None
            cli.list_components(comp_type, args.limit)

        elif args.command == 'stats':
            cli.show_stats()

        elif args.command == 'interactive':
            cli.interactive_mode()

        else:
            # No command provided, show help
            parser.print_help()
            print(f"\n📊 Database Statistics:")
            cli.show_stats()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())