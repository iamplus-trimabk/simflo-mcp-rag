#!/usr/bin/env python3
"""
SimFlo MCP RAG - Registry System CLI

Command-line interface for the registry system that manages multiple RAG databases
with registry-based organization. Each registry (shadcn, gluestack, etc.) has its
own folder with db/ and files/ subdirectories.
"""

import argparse
import json
import sys
import shutil
import glob
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the rag-builder core directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "02-rag-builder" / "core"))

try:
    from database_manager import get_database_manager
except ImportError as e:
    print(f"Error importing DatabaseManager: {e}")
    print("Make sure v2/core/02-rag-builder/core/ directory exists and contains database_manager.py")
    sys.exit(1)


class RegistryManager:
    """Manages multiple RAG registries with registry-based organization"""

    def __init__(self, registries_dir: Path = None):
        """Initialize registry manager"""
        if registries_dir is None:
            registries_dir = Path(__file__).parent / "registries"

        self.registries_dir = Path(registries_dir)
        self.registries_dir.mkdir(parents=True, exist_ok=True)

        # Initialize centralized database manager
        self.database_manager = get_database_manager(str(self.registries_dir))

        # Initialize logger
        import logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def _log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def _log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def list_registries(self) -> List[Dict[str, Any]]:
        """List all available registries"""
        registries = []

        for registry_dir in self.registries_dir.iterdir():
            if registry_dir.is_dir() and registry_dir.name != '__pycache__':
                # Use standardized database path: {registry}/chroma_db/
                db_dir = registry_dir / "chroma_db"
                files_dir = registry_dir / "files"

                # Count ChromaDB files including sqlite database and collection files
                db_files = []
                if db_dir.exists():
                    db_files.extend(list(db_dir.glob("*.db")))
                    db_files.extend(list(db_dir.glob("*.sqlite3")))
                    db_files.extend(list(db_dir.glob("*.marker")))
                    # Count all ChromaDB collection directory files
                    db_files.extend(list(db_dir.rglob("*")))

                registry_info = {
                    "name": registry_dir.name,
                    "path": str(registry_dir),
                    "db_exists": db_dir.exists(),
                    "files_exist": files_dir.exists(),
                    "db_files": db_files,
                    "source_files": list(files_dir.rglob("*")) if files_dir.exists() else [],
                    "total_db_files": len(db_files),
                    "total_source_files": len(list(files_dir.rglob("*"))) if files_dir.exists() else 0
                }
                registries.append(registry_info)

        return registries

    def get_registry_info(self, registry_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific registry"""
        registry_dir = self.registries_dir / registry_name

        if not registry_dir.exists():
            return None

        db_dir = registry_dir / "db"
        files_dir = registry_dir / "files"

        # Get file organization by type
        file_types = {}
        if files_dir.exists():
            for item in files_dir.iterdir():
                if item.is_dir():
                    file_types[item.name] = {
                        "path": str(item),
                        "files": list(item.rglob("*")),
                        "count": len(list(item.rglob("*")))
                    }
                elif item.is_file():
                    # Handle root-level files
                    ext = item.suffix[1:] if item.suffix else 'unknown'
                    if ext not in file_types:
                        file_types[ext] = {"files": [], "count": 0}
                    file_types[ext]["files"].append(item)
                    file_types[ext]["count"] += 1

        # Get database information
        db_info = {}
        if db_dir.exists():
            for db_file in db_dir.glob("*.db"):
                if db_file.exists():
                    stat = db_file.stat()
                    db_info[db_file.stem] = {
                        "path": str(db_file),
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }

        return {
            "name": registry_name,
            "path": str(registry_dir),
            "db_directory": str(db_dir),
            "files_directory": str(files_dir),
            "db_exists": db_dir.exists(),
            "files_exist": files_dir.exists(),
            "file_types": file_types,
            "databases": db_info,
            "total_db_files": len(db_info),
            "total_source_files": sum(ft.get("count", 0) for ft in file_types.values())
        }

    def clean_registry_db(self, registry_name: str) -> Dict[str, Any]:
        """Clean database files for a specific registry"""
        registry_dir = self.registries_dir / registry_name

        if not registry_dir.exists():
            return {"success": False, "error": f"Registry '{registry_name}' not found"}

        db_dir = registry_dir / "db"

        if db_dir.exists():
            # Remove all database files
            removed_files = []
            for db_file in db_dir.glob("*.db"):
                db_file.unlink()
                removed_files.append(str(db_file))

            return {
                "success": True,
                "registry": registry_name,
                "removed_files": removed_files,
                "message": f"Cleaned {len(removed_files)} database files from {registry_name}"
            }
        else:
            return {
                "success": True,
                "registry": registry_name,
                "removed_files": [],
                "message": f"No database directory found for {registry_name}"
            }

    def clean_registry_all(self, registry_name: str) -> Dict[str, Any]:
        """Clean both database and source files for a specific registry"""
        registry_dir = self.registries_dir / registry_name

        if not registry_dir.exists():
            return {"success": False, "error": f"Registry '{registry_name}' not found"}

        removed_files = []

        # Clean database files
        db_dir = registry_dir / "db"
        if db_dir.exists():
            for db_file in db_dir.glob("*.db"):
                db_file.unlink()
                removed_files.append(str(db_file))

        # Clean source files
        files_dir = registry_dir / "files"
        if files_dir.exists():
            for file_path in files_dir.rglob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    removed_files.append(str(file_path))

            # Remove empty directories
            for dir_path in sorted(files_dir.rglob("*"), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()

        return {
            "success": True,
            "registry": registry_name,
            "removed_files": removed_files,
            "message": f"Cleaned {len(removed_files)} files from {registry_name}"
        }

    def rebuild_registry_db(self, registry_name: str) -> Dict[str, Any]:
        """Rebuild database for a registry using centralized DatabaseManager"""
        try:
            self._log_info(f"Rebuilding database for {registry_name} using DatabaseManager")

            # Use centralized DatabaseManager
            result = self.database_manager.rebuild_database(registry_name, "components")

            # Add timestamp for consistency with CLI responses
            if result["success"]:
                result["timestamp"] = datetime.now().isoformat()
                self._log_info(f"Database rebuilt successfully: {result.get('message', 'No message')}")
            else:
                self._log_error(f"Database rebuild failed: {result.get('error', 'Unknown error')}")
                result["timestamp"] = datetime.now().isoformat()

            return result

        except Exception as e:
            error_msg = f"Failed to rebuild database for {registry_name}: {e}"
            self._log_error(error_msg)
            return {
                "success": False,
                "error": str(e),
                "registry": registry_name,
                "timestamp": datetime.now().isoformat()
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        registries = self.list_registries()

        total_db_files = sum(r["total_db_files"] for r in registries)
        total_source_files = sum(r["total_source_files"] for r in registries)
        active_registries = len([r for r in registries if r["db_exists"] and r["files_exist"]])

        return {
            "total_registries": len(registries),
            "active_registries": active_registries,
            "total_db_files": total_db_files,
            "total_source_files": total_source_files,
            "registries_directory": str(self.registries_dir),
            "last_updated": datetime.now().isoformat()
        }


def format_output(data: Any, format_type: str = "json", success: bool = True) -> str:
    """Format output data in specified format"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    if format_type == "json":
        return json.dumps(response, indent=2, default=str)
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


def cmd_list(args) -> str:
    """List all available registries"""
    try:
        manager = RegistryManager()
        registries = manager.list_registries()

        data = {
            "total_registries": len(registries),
            "registries": registries
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_info(args) -> str:
    """Get information about a specific registry"""
    try:
        manager = RegistryManager()
        registry_info = manager.get_registry_info(args.name)

        if registry_info is None:
            return format_output({"error": f"Registry '{args.name}' not found"}, args.format, success=False)

        return format_output(registry_info, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_search(args) -> str:
    """Search across all registries (placeholder implementation)"""
    try:
        manager = RegistryManager()
        registries = manager.list_registries()

        # For now, just return registries that match the query
        matching_registries = []
        query_lower = args.query.lower()

        for registry in registries:
            if query_lower in registry["name"].lower():
                matching_registries.append(registry)

        data = {
            "query": args.query,
            "total_results": len(matching_registries),
            "results": matching_registries
        }
        return format_output(data, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_status(args) -> str:
    """Get registry system status"""
    try:
        manager = RegistryManager()
        status = manager.get_system_status()
        return format_output(status, args.format)
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_clean_db(args) -> str:
    """Clean database files for a specific registry"""
    try:
        manager = RegistryManager()
        result = manager.clean_registry_db(args.registry)
        return format_output(result, args.format, result["success"])
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_clean_all(args) -> str:
    """Clean both database and source files for a specific registry"""
    try:
        manager = RegistryManager()
        result = manager.clean_registry_all(args.registry)
        return format_output(result, args.format, result["success"])
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def cmd_rebuild_db(args) -> str:
    """Rebuild database from source files for a specific registry"""
    try:
        manager = RegistryManager()
        result = manager.rebuild_registry_db(args.registry)
        return format_output(result, args.format, result["success"])
    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RAG Registry System CLI - Manage registry-based RAG databases",
        prog='registry'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create parent parser for common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--format', choices=['json', 'table'], default='json',
                             help='Output format (default: json)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all registries', parents=[parent_parser])
    list_parser.set_defaults(func=cmd_list)

    # Info command
    info_parser = subparsers.add_parser('info', help='Get registry information', parents=[parent_parser])
    info_parser.add_argument('--name', required=True, help='Registry name')
    info_parser.set_defaults(func=cmd_info)

    # Search command
    search_parser = subparsers.add_parser('search', help='Search registries', parents=[parent_parser])
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Result limit (default: 10)')
    search_parser.set_defaults(func=cmd_search)

    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status', parents=[parent_parser])
    status_parser.set_defaults(func=cmd_status)

    # Registry management commands
    clean_db_parser = subparsers.add_parser('clean-db', help='Clean database files for a registry', parents=[parent_parser])
    clean_db_parser.add_argument('--registry', required=True, help='Registry name')
    clean_db_parser.set_defaults(func=cmd_clean_db)

    clean_all_parser = subparsers.add_parser('clean-all', help='Clean all files for a registry', parents=[parent_parser])
    clean_all_parser.add_argument('--registry', required=True, help='Registry name')
    clean_all_parser.set_defaults(func=cmd_clean_all)

    rebuild_parser = subparsers.add_parser('rebuild-db', help='Rebuild database from source files', parents=[parent_parser])
    rebuild_parser.add_argument('--registry', required=True, help='Registry name')
    rebuild_parser.set_defaults(func=cmd_rebuild_db)

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


if __name__ == "__main__":
    sys.exit(main())