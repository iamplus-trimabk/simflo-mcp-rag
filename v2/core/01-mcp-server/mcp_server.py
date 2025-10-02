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

# Add the rag-builder core directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "02-rag-builder" / "core"))

try:
    from registry_manager import get_registry_manager, RegistryInfo
    from context_manager import get_context_manager, PlatformContext
    from vector_store import VectorStore
    from parse_registry import ShadcnComponent
except ImportError as e:
    print(f"Error importing rag-builder modules: {e}")
    print("Make sure v2/core/02-rag-builder/core/ directory exists and contains required modules")
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

        # Convert RegistryInfo objects to dictionaries for JSON serialization
        registries_data = []
        for reg in registries:
            registries_data.append({
                "name": reg.name,
                "path": reg.path,
                "platforms": reg.platform,
                "description": reg.description,
                "component_count": reg.component_count,
                "last_updated": reg.last_updated,
                "is_active": reg.is_active,
                "registry_type": reg.registry_type
            })

        return format_output({
            "platform": getattr(args, 'platform', None),
            "total_registries": len(registries_data),
            "registries": registries_data
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_run_extraction(args) -> str:
    """Run extraction pipeline for components"""
    try:
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        # Build extraction command
        cmd = [
            "python3",
            str(project_root / "v2/04-extractors/extractors_cli.py")
        ]

        if args.registry:
            cmd.extend(["run-extractor", args.registry])
        else:
            cmd.extend(["run-all-extractors"])

        cmd.extend(["--format", "json"])

        # Run extraction command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        if result.returncode == 0:
            try:
                extraction_data = json.loads(result.stdout)
                return format_output({
                    "extraction_completed": True,
                    "registry": args.registry or "all",
                    "mode": getattr(args, 'mode', 'test'),
                    "extraction_result": extraction_data,
                    "message": f"Successfully ran extraction for {args.registry or 'all registries'}"
                }, args.format)
            except json.JSONDecodeError:
                return format_output({
                    "extraction_completed": True,
                    "registry": args.registry or "all",
                    "mode": getattr(args, 'mode', 'test'),
                    "raw_output": result.stdout,
                    "message": f"Extraction completed for {args.registry or 'all registries'}"
                }, args.format)
        else:
            return format_output({
                "error": f"Extraction failed with exit code {result.returncode}",
                "registry": args.registry or "all",
                "mode": getattr(args, 'mode', 'test'),
                "stderr": result.stderr,
                "stdout": result.stdout
            }, args.format, success=False)

    except Exception as e:
        return format_output({
            "error": f"Failed to run extraction: {str(e)}",
            "registry": getattr(args, 'registry', 'unknown'),
            "mode": getattr(args, 'mode', 'test')
        }, args.format, success=False)


def handle_extraction_status(args) -> str:
    """Get extraction pipeline status"""
    try:
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        # Get extractor status
        extractors_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "status", "--format", "json"
        ]

        extractors_result = subprocess.run(
            extractors_cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        # Get RAG builder status
        rag_builder_cmd = [
            "python3", str(project_root / "v2/core/02-rag-builder/rag_builder_cli.py"),
            "status", "--format", "json"
        ]

        rag_builder_result = subprocess.run(
            rag_builder_cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        # Get registry status
        registry_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "status", "--format", "json"
        ]

        registry_result = subprocess.run(
            registry_cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        status_data = {
            "extraction_system": "operational",
            "components": {}
        }

        # Parse extractors status
        if extractors_result.returncode == 0:
            try:
                extractors_data = json.loads(extractors_result.stdout)
                status_data["components"]["extractors"] = extractors_data.get("data", {})
            except:
                status_data["components"]["extractors"] = {
                    "status": "error",
                    "raw_output": extractors_result.stdout
                }
        else:
            status_data["components"]["extractors"] = {
                "status": "error",
                "error": extractors_result.stderr
            }

        # Parse RAG builder status
        if rag_builder_result.returncode == 0:
            try:
                rag_builder_data = json.loads(rag_builder_result.stdout)
                status_data["components"]["rag_builder"] = rag_builder_data.get("data", {})
            except:
                status_data["components"]["rag_builder"] = {
                    "status": "error",
                    "raw_output": rag_builder_result.stdout
                }
        else:
            status_data["components"]["rag_builder"] = {
                "status": "error",
                "error": rag_builder_result.stderr
            }

        # Parse registry status
        if registry_result.returncode == 0:
            try:
                registry_data = json.loads(registry_result.stdout)
                status_data["components"]["registry"] = registry_data.get("data", {})
            except:
                status_data["components"]["registry"] = {
                    "status": "error",
                    "raw_output": registry_result.stdout
                }
        else:
            status_data["components"]["registry"] = {
                "status": "error",
                "error": registry_result.stderr
            }

        return format_output(status_data, args.format)

    except Exception as e:
        return format_output({
            "error": f"Failed to get extraction status: {str(e)}"
        }, args.format, success=False)


def handle_list_extraction_registries(args) -> str:
    """List available extraction registries"""
    try:
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        # Get available extractors
        extractors_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "list-extractors", "--format", "json"
        ]

        result = subprocess.run(
            extractors_cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        if result.returncode == 0:
            try:
                extractors_data = json.loads(result.stdout)
                extractors_info = extractors_data.get("data", {})

                # Format extraction registry information
                extraction_registries = []
                extractors = extractors_info.get("extractors", {})

                if isinstance(extractors, dict):
                    for name, info in extractors.items():
                        extraction_registries.append({
                            "name": name,
                            "type": info.get("type", "extractor"),
                            "description": info.get("description", ""),
                            "supported_sources": info.get("supported_sources", []),
                            "version": info.get("version", "unknown"),
                            "available": "error" not in info
                        })
                elif isinstance(extractors, list):
                    for extractor in extractors:
                        extraction_registries.append({
                            "name": extractor,
                            "type": "extractor",
                            "description": f"Extractor for {extractor}",
                            "supported_sources": ["github"],
                            "version": "unknown",
                            "available": True
                        })

                return format_output({
                    "extraction_registries": extraction_registries,
                    "total_available": len(extraction_registries),
                    "extraction_system": "operational",
                    "message": f"Found {len(extraction_registries)} available extraction registries"
                }, args.format)

            except json.JSONDecodeError:
                return format_output({
                    "extraction_registries": [],
                    "total_available": 0,
                    "raw_output": result.stdout,
                    "message": "Could not parse extractors list"
                }, args.format)
        else:
            return format_output({
                "error": f"Failed to list extraction registries: {result.stderr}",
                "extraction_registries": [],
                "total_available": 0
            }, args.format, success=False)

    except Exception as e:
        return format_output({
            "error": f"Failed to list extraction registries: {str(e)}",
            "extraction_registries": [],
            "total_available": 0
        }, args.format, success=False)


def handle_clear_extraction_data(args) -> str:
    """Clear extracted data"""
    try:
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        if args.registry:
            # Clear specific registry
            registry_cmd = [
                "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
                "clean-all", "--registry", args.registry, "--format", "json"
            ]

            result = subprocess.run(
                registry_cmd,
                capture_output=True,
                text=True,
                cwd=project_root
            )

            if result.returncode == 0:
                try:
                    clear_data = json.loads(result.stdout)
                    return format_output({
                        "clear_completed": True,
                        "registry": args.registry,
                        "clear_result": clear_data.get("data", {}),
                        "message": f"Successfully cleared data for registry '{args.registry}'"
                    }, args.format)
                except json.JSONDecodeError:
                    return format_output({
                        "clear_completed": True,
                        "registry": args.registry,
                        "raw_output": result.stdout,
                        "message": f"Cleared data for registry '{args.registry}'"
                    }, args.format)
            else:
                return format_output({
                    "error": f"Failed to clear registry '{args.registry}': {result.stderr}",
                    "registry": args.registry
                }, args.format, success=False)
        else:
            # Get list of all registries and clear them
            list_cmd = [
                "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
                "list", "--format", "json"
            ]

            list_result = subprocess.run(
                list_cmd,
                capture_output=True,
                text=True,
                cwd=project_root
            )

            if list_result.returncode == 0:
                try:
                    list_data = json.loads(list_result.stdout)
                    registries = list_data.get("data", {}).get("registries", [])

                    cleared_registries = []
                    failed_registries = []

                    for registry in registries:
                        registry_name = registry.get("name")
                        if registry_name:
                            clear_cmd = [
                                "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
                                "clean-all", "--registry", registry_name, "--format", "json"
                            ]

                            clear_result = subprocess.run(
                                clear_cmd,
                                capture_output=True,
                                text=True,
                                cwd=project_root
                            )

                            if clear_result.returncode == 0:
                                cleared_registries.append(registry_name)
                            else:
                                failed_registries.append({
                                    "registry": registry_name,
                                    "error": clear_result.stderr
                                })

                    return format_output({
                        "clear_completed": True,
                        "target": "all_registries",
                        "cleared_registries": cleared_registries,
                        "failed_registries": failed_registries,
                        "total_cleared": len(cleared_registries),
                        "total_failed": len(failed_registries),
                        "message": f"Cleared data for {len(cleared_registries)} registries"
                    }, args.format)

                except json.JSONDecodeError:
                    return format_output({
                        "error": "Failed to parse registry list",
                        "target": "all_registries"
                    }, args.format, success=False)
            else:
                return format_output({
                    "error": f"Failed to list registries: {list_result.stderr}",
                    "target": "all_registries"
                }, args.format, success=False)

    except Exception as e:
        return format_output({
            "error": f"Failed to clear extraction data: {str(e)}",
            "registry": getattr(args, 'registry', 'all')
        }, args.format, success=False)


def handle_search_by_category(args) -> str:
    """Search components within specific categories"""
    try:
        # For now, use the main search functionality and filter by category
        # This is a simplified implementation that uses the existing search
        registry_manager = get_registry_manager()

        # Build platform context if platform specified
        platform_context = None
        if hasattr(args, 'platform') and args.platform:
            from context_manager import PlatformContext
            platform_context = PlatformContext(args.platform)

        # Use existing search functionality
        search_results = registry_manager.search_components(
            query=args.query,
            platform_context=platform_context,
            limit=args.limit
        )

        # Convert SearchResult objects to dictionaries and filter by category
        all_results = []
        for result in search_results:
            component = result.component
            component.update({
                "registry": result.registry,
                "relevance_score": result.relevance_score,
                "platform_relevance": result.platform_relevance
            })
            all_results.append(component)

        # Filter results by category if specified
        if hasattr(args, 'category') and args.category:
            filtered_results = []

            for result in all_results:
                # Simple category matching based on file paths or tags
                file_path = result.get('file_path', '').lower()
                tags = result.get('tags', [])

                # Check if category matches file path or tags
                if (args.category in file_path or
                    args.category in str(tags).lower()):
                    filtered_results.append(result)

            all_results = filtered_results

        return format_output({
            "query": args.query,
            "category": getattr(args, 'category', 'all'),
            "platform": getattr(args, 'platform', None),
            "total_found": len(all_results),
            "results": all_results,
            "search_type": "category_filtered"
        }, args.format)

    except Exception as e:
        return format_output({"error": str(e)}, args.format, success=False)


def handle_list_registry_sources(args) -> str:
    """List detailed sources for a specific registry"""
    try:
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        # Get detailed registry information
        registry_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "info", "--name", args.registry, "--format", "json"
        ]

        result = subprocess.run(
            registry_cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )

        if result.returncode == 0:
            try:
                registry_data = json.loads(result.stdout)
                registry_info = registry_data.get("data", {})

                # Extract source information
                sources = []
                file_types = registry_info.get("file_types", {})

                for file_type, info in file_types.items():
                    if isinstance(info, dict) and "files" in info:
                        for file_path in info["files"]:
                            if file_path.endswith(('.md', '.json', '.tsx', '.ts')):
                                relative_path = Path(file_path).relative_to(project_root)
                                sources.append({
                                    "name": relative_path.stem,
                                    "type": file_type,
                                    "file_path": str(relative_path),
                                    "full_path": file_path,
                                    "source_type": "extracted_content"
                                })

                # Add registry metadata
                registry_sources = {
                    "registry": {
                        "name": registry_info.get("name"),
                        "path": registry_info.get("path"),
                        "total_source_files": registry_info.get("total_source_files", 0),
                        "total_db_files": registry_info.get("total_db_files", 0),
                        "db_exists": registry_info.get("db_exists", False),
                        "files_exist": registry_info.get("files_exist", False)
                    },
                    "sources": sources,
                    "source_categories": list(file_types.keys()),
                    "total_sources": len(sources),
                    "extraction_status": "complete" if sources else "empty"
                }

                return format_output(registry_sources, args.format)

            except json.JSONDecodeError:
                return format_output({
                    "error": "Failed to parse registry information",
                    "registry": args.registry,
                    "raw_output": result.stdout
                }, args.format, success=False)
        else:
            return format_output({
                "error": f"Registry '{args.registry}' not found or failed to load: {result.stderr}",
                "registry": args.registry
            }, args.format, success=False)

    except Exception as e:
        return format_output({
            "error": f"Failed to list registry sources: {str(e)}",
            "registry": getattr(args, 'registry', 'unknown')
        }, args.format, success=False)


def handle_create_registry_from_source(args) -> str:
    """Create a new registry from source URL with automated workflow"""
    try:
        import subprocess
        from pathlib import Path
        import time

        project_root = Path(__file__).parent.parent.parent.parent
        start_time = time.time()

        # Step 1: Detect repository type and extractor
        print("🔍 Detecting repository type and extractor...", file=sys.stderr)
        detect_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "detect-repository", "--repository-url", args.source, "--format", "json"
        ]

        detect_result = subprocess.run(detect_cmd, capture_output=True, text=True, cwd=project_root)
        if detect_result.returncode != 0:
            return format_output({
                "error": f"Repository detection failed: {detect_result.stderr}",
                "source": args.source,
                "registry_name": args.name
            }, args.format, success=False)

        detect_data = json.loads(detect_result.stdout)
        if not detect_data.get("success"):
            return format_output({
                "error": f"Repository detection failed: {detect_data.get('data', {}).get('error', 'Unknown error')}",
                "source": args.source,
                "registry_name": args.name
            }, args.format, success=False)

        detection_info = detect_data["data"]["detection"]
        recommended_extractor = detection_info.get("recommended_extractor")

        # Step 2: Extract content using universal extractor (creates registry structure automatically)
        print(f"🚀 Extracting content using {recommended_extractor} extractor...", file=sys.stderr)
        extract_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "extract-repository", "--repository-url", args.source, "--format", "json"
        ]

        if hasattr(args, 'extractor') and args.extractor:
            extract_cmd.extend(["--force-extractor", args.extractor])

        extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, cwd=project_root)
        if extract_result.returncode != 0:
            return format_output({
                "error": f"Content extraction failed: {extract_result.stderr}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": recommended_extractor
            }, args.format, success=False)

        extract_data = json.loads(extract_result.stdout)
        if not extract_data.get("success"):
            return format_output({
                "error": f"Content extraction failed: {extract_data.get('data', {}).get('error', 'Unknown error')}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": recommended_extractor
            }, args.format, success=False)

        extraction_result = extract_data["data"]["extraction"]
        elements_extracted = extraction_result.get("elements_found", 0)

        # Step 4: Build registry database
        print("🔨 Building registry database...", file=sys.stderr)
        build_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "rebuild-db", "--registry", args.name, "--format", "json"
        ]

        build_result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=project_root)
        if build_result.returncode != 0:
            return format_output({
                "error": f"Database building failed: {build_result.stderr}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": recommended_extractor
            }, args.format, success=False)

        # Step 5: Verify registry functionality
        print("✅ Verifying registry functionality...", file=sys.stderr)
        verify_cmd = [
            "python3", str(project_root / "v2/core/01-mcp-server/mcp_server.py"),
            "list-registries", "--format", "json"
        ]

        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, cwd=project_root)
        registry_verified = False
        if verify_result.returncode == 0:
            try:
                verify_data = json.loads(verify_result.stdout)
                registries = verify_data.get("data", {}).get("registries", [])
                registry_verified = any(reg.get("name") == args.name for reg in registries)
            except:
                pass

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)

        # Return comprehensive result
        result_data = {
            "registry_created": True,
            "registry_name": args.name,
            "source": args.source,
            "processing_time_seconds": processing_time,
            "steps_completed": [
                "Repository type detection",
                "Content extraction (creates registry automatically)",
                "Database building",
                "Registry verification"
            ],
            "extraction_details": {
                "recommended_extractor": recommended_extractor,
                "used_extractor": getattr(args, 'extractor', recommended_extractor),
                "extraction_type": detection_info.get("extraction_type"),
                "quality": detection_info.get("quality"),
                "confidence": detection_info.get("confidence"),
                "elements_extracted": elements_extracted
            },
            "registry_status": {
                "verified": registry_verified,
                "database_built": True,
                "ready_for_search": registry_verified
            },
            "workflow_summary": {
                "total_steps": 4,
                "steps_successful": 4 if registry_verified else 3,
                "success_rate": "100%" if registry_verified else "75%",
                "source_type": detection_info.get("extraction_type", "unknown")
            }
        }

        if not registry_verified:
            result_data["warning"] = "Registry created but verification failed - manual verification recommended"

        message = f"Successfully created registry '{args.name}' from source '{args.source}' with {elements_extracted} elements extracted"

        return format_output(result_data, args.format)

    except Exception as e:
        return format_output({
            "error": f"Registry creation workflow failed: {str(e)}",
            "source": getattr(args, 'source', 'unknown'),
            "registry_name": getattr(args, 'name', 'unknown')
        }, args.format, success=False)


def handle_add_source_to_registry(args) -> str:
    """Add content from new source to existing registry"""
    try:
        import subprocess
        from pathlib import Path
        import time

        project_root = Path(__file__).parent.parent.parent.parent
        start_time = time.time()

        # Step 1: Verify registry exists
        print(f"🔍 Verifying registry '{args.registry}' exists...", file=sys.stderr)
        verify_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "info", "--name", args.registry, "--format", "json"
        ]

        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, cwd=project_root)
        if verify_result.returncode != 0:
            return format_output({
                "error": f"Registry '{args.registry}' not found or not accessible",
                "source": args.source,
                "registry_name": args.registry
            }, args.format, success=False)

        # Step 2: Detect repository type
        print("🔍 Detecting repository type...", file=sys.stderr)
        detect_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "detect-repository", "--repository-url", args.source, "--format", "json"
        ]

        detect_result = subprocess.run(detect_cmd, capture_output=True, text=True, cwd=project_root)
        if detect_result.returncode != 0:
            return format_output({
                "error": f"Repository detection failed: {detect_result.stderr}",
                "source": args.source,
                "registry_name": args.registry
            }, args.format, success=False)

        detect_data = json.loads(detect_result.stdout)
        if not detect_data.get("success"):
            return format_output({
                "error": f"Repository detection failed: {detect_data.get('data', {}).get('error', 'Unknown error')}",
                "source": args.source,
                "registry_name": args.registry
            }, args.format, success=False)

        detection_info = detect_data["data"]["detection"]
        recommended_extractor = detection_info.get("recommended_extractor")

        # Step 3: Extract content
        print(f"🚀 Extracting content using {recommended_extractor} extractor...", file=sys.stderr)
        extract_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "extract-repository", "--repository-url", args.source, "--format", "json"
        ]

        if hasattr(args, 'extractor') and args.extractor:
            extract_cmd.extend(["--force-extractor", args.extractor])

        extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, cwd=project_root)
        if extract_result.returncode != 0:
            return format_output({
                "error": f"Content extraction failed: {extract_result.stderr}",
                "source": args.source,
                "registry_name": args.registry,
                "extractor": recommended_extractor
            }, args.format, success=False)

        extract_data = json.loads(extract_result.stdout)
        if not extract_data.get("success"):
            return format_output({
                "error": f"Content extraction failed: {extract_data.get('data', {}).get('error', 'Unknown error')}",
                "source": args.source,
                "registry_name": args.registry,
                "extractor": recommended_extractor
            }, args.format, success=False)

        extraction_result = extract_data["data"]["extraction"]
        elements_extracted = extraction_result.get("elements_found", 0)

        # Step 4: Rebuild registry database with new content
        print("🔨 Rebuilding registry database with new content...", file=sys.stderr)
        build_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "rebuild-db", "--registry", args.registry, "--format", "json"
        ]

        build_result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=project_root)
        if build_result.returncode != 0:
            return format_output({
                "error": f"Database rebuild failed: {build_result.stderr}",
                "source": args.source,
                "registry_name": args.registry
            }, args.format, success=False)

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)

        result_data = {
            "source_added": True,
            "registry_name": args.registry,
            "new_source": args.source,
            "processing_time_seconds": processing_time,
            "steps_completed": [
                "Registry verification",
                "Repository type detection",
                "Content extraction",
                "Database rebuild"
            ],
            "extraction_details": {
                "recommended_extractor": recommended_extractor,
                "used_extractor": getattr(args, 'extractor', recommended_extractor),
                "extraction_type": detection_info.get("extraction_type"),
                "elements_extracted": elements_extracted
            },
            "update_summary": {
                "total_steps": 4,
                "steps_successful": 4,
                "success_rate": "100%",
                "new_elements_added": elements_extracted
            }
        }

        message = f"Successfully added source '{args.source}' to registry '{args.registry}' with {elements_extracted} new elements"

        return format_output(result_data, args.format)

    except Exception as e:
        return format_output({
            "error": f"Failed to add source to registry: {str(e)}",
            "source": getattr(args, 'source', 'unknown'),
            "registry_name": getattr(args, 'registry', 'unknown')
        }, args.format, success=False)


def handle_create_and_extract(args) -> str:
    """Create registry and extract with explicit extractor control"""
    try:
        import subprocess
        from pathlib import Path
        import time

        project_root = Path(__file__).parent.parent.parent.parent
        start_time = time.time()

        # Validate extractor
        valid_extractors = ["shadcn", "gluestack", "typescript", "python", "language-documentation", "configuration"]
        if args.extractor not in valid_extractors:
            return format_output({
                "error": f"Invalid extractor '{args.extractor}'. Valid extractors: {', '.join(valid_extractors)}",
                "source": args.source,
                "registry_name": args.name,
                "requested_extractor": args.extractor
            }, args.format, success=False)

        print(f"🎯 Creating registry '{args.name}' with explicit extractor '{args.extractor}'...", file=sys.stderr)

        # Step 1: Extract content with specified extractor (creates registry structure automatically)
        print(f"🚀 Extracting content using '{args.extractor}' extractor...", file=sys.stderr)
        extract_cmd = [
            "python3", str(project_root / "v2/04-extractors/extractors_cli.py"),
            "extract-repository", "--repository-url", args.source, "--force-extractor", args.extractor, "--format", "json"
        ]

        extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, cwd=project_root)
        if extract_result.returncode != 0:
            return format_output({
                "error": f"Content extraction failed: {extract_result.stderr}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": args.extractor
            }, args.format, success=False)

        extract_data = json.loads(extract_result.stdout)
        if not extract_data.get("success"):
            return format_output({
                "error": f"Content extraction failed: {extract_data.get('data', {}).get('error', 'Unknown error')}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": args.extractor
            }, args.format, success=False)

        extraction_result = extract_data["data"]["extraction"]
        elements_extracted = extraction_result.get("elements_found", 0)

        # Step 2: Build registry database
        print("🔨 Building registry database...", file=sys.stderr)
        build_cmd = [
            "python3", str(project_root / "v2/core/00-rag-registry/registry.py"),
            "rebuild-db", "--registry", args.name, "--format", "json"
        ]

        build_result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=project_root)
        if build_result.returncode != 0:
            return format_output({
                "error": f"Database building failed: {build_result.stderr}",
                "source": args.source,
                "registry_name": args.name,
                "extractor": args.extractor
            }, args.format, success=False)

        # Step 3: Verify functionality
        print("✅ Verifying registry functionality...", file=sys.stderr)
        verify_cmd = [
            "python3", str(project_root / "v2/core/01-mcp-server/mcp_server.py"),
            "search", "test", "--limit", "1", "--format", "json"
        ]

        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, cwd=project_root)
        registry_verified = verify_result.returncode == 0

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)

        result_data = {
            "registry_created": True,
            "registry_name": args.name,
            "source": args.source,
            "extractor_used": args.extractor,
            "processing_time_seconds": processing_time,
            "steps_completed": [
                "Content extraction (explicit, creates registry automatically)",
                "Database building",
                "Registry verification"
            ],
            "extraction_summary": {
                "elements_extracted": elements_extracted,
                "extractor_type": "specialized" if args.extractor in ["shadcn", "gluestack"] else "language-based",
                "extraction_quality": "high" if args.extractor in ["shadcn", "gluestack"] else "good"
            },
            "verification_status": {
                "verified": registry_verified,
                "database_built": True,
                "ready_for_search": registry_verified
            }
        }

        return format_output(result_data, args.format)

    except Exception as e:
        return format_output({
            "error": f"Create and extract workflow failed: {str(e)}",
            "source": getattr(args, 'source', 'unknown'),
            "registry_name": getattr(args, 'name', 'unknown'),
            "extractor": getattr(args, 'extractor', 'unknown')
        }, args.format, success=False)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SimFlo MCP RAG - CLI Server for AI Assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "button" --limit 10 --format json
  %(prog)s get-component dialog --registry shadcn_db --format json
  %(prog)s set-context reactjs --format json
  %(prog)s run-extraction shadcn --mode test --format json

For comprehensive usage guide and AI integration patterns, see:
  v2/core/mcp-server/user_guide.md
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

    # Enhanced Registry Creation Commands
    create_registry_parser = subparsers.add_parser('create-registry-from-source', help='Create registry from source URL (automated workflow)')
    create_registry_parser.add_argument('--name', required=True, help='Registry name to create')
    create_registry_parser.add_argument('--source', required=True, help='Source repository URL')
    create_registry_parser.add_argument('--extractor', help='Force specific extractor (overrides auto-detection)')
    create_registry_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    add_source_parser = subparsers.add_parser('add-source-to-registry', help='Add content from new source to existing registry')
    add_source_parser.add_argument('--registry', required=True, help='Existing registry name')
    add_source_parser.add_argument('--source', required=True, help='Source repository URL')
    add_source_parser.add_argument('--extractor', help='Force specific extractor (overrides auto-detection)')
    add_source_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

    create_extract_parser = subparsers.add_parser('create-and-extract', help='Create registry with explicit extractor control')
    create_extract_parser.add_argument('--name', required=True, help='Registry name to create')
    create_extract_parser.add_argument('--source', required=True, help='Source repository URL')
    create_extract_parser.add_argument('--extractor', required=True, choices=['shadcn', 'gluestack', 'typescript', 'python', 'language-documentation', 'configuration'], help='Specific extractor to use')
    create_extract_parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format (default: json)')

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
        # Enhanced Registry Creation Commands
        'create-registry-from-source': handle_create_registry_from_source,
        'add-source-to-registry': handle_add_source_to_registry,
        'create-and-extract': handle_create_and_extract,
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