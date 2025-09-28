#!/usr/bin/env python3
"""
SimFlo MCP RAG - API Server

HTTP API server for RAG database queries that the TypeScript MCP server can use.
"""

import json
import uvicorn
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path

from vector_store import VectorStore
from parse_registry import ShadcnComponent
from context_manager import get_context_manager, PlatformContext
from registry_manager import get_registry_manager


# Pydantic models for request/response
class ComponentResponse(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    dependencies: List[str]
    registryDependencies: List[str]
    categories: List[str]
    installCommand: str
    fileLocation: str


class SearchResultResponse(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    relevanceScore: float
    installCommand: str
    registry: Optional[str] = None
    platform: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    registryDependencies: Optional[List[str]] = None


class InstallationInfoResponse(BaseModel):
    command: str
    dependencies: List[str]
    registryDependencies: List[str]
    setupNotes: str


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class ContextRequest(BaseModel):
    platform: str
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    project_type: Optional[str] = None


class ContextResponse(BaseModel):
    platform: str
    session_id: str
    timestamp: float
    registries: List[str]


class RegistryResponse(BaseModel):
    name: str
    description: str
    component_count: int
    platforms: List[str]
    is_active: bool


class RAGAPIServer:
    """HTTP API server for RAG database queries"""

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.app = FastAPI(
            title="SimFlo RAG API",
            description="API for querying multi-platform components RAG database",
            version="2.0.0"
        )
        self.vector_store = VectorStore(str(self.persist_dir))
        self.context_manager = get_context_manager()
        self.registry_manager = get_registry_manager()
        self.logger = logging.getLogger(__name__)

        # Load components cache if needed
        if self.vector_store.collection.count() > 0 and not self.vector_store.components_cache:
            self._load_components_to_cache()

        self._setup_routes()
        self._setup_exception_handlers()

    def _load_components_to_cache(self):
        """Load components from JSON file into cache"""
        try:
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

    def _generate_setup_notes(self, component: ShadcnComponent) -> str:
        """Generate setup notes for a component"""
        notes = []

        if component.dependencies:
            # Check for specific dependency patterns
            if any(dep.startswith('@radix-ui/') for dep in component.dependencies):
                notes.append("Uses Radix UI primitives for accessibility")

            if any('day-picker' in dep.lower() for dep in component.dependencies):
                notes.append("Requires date-fns for date utilities")

            if any('react-hook-form' in dep for dep in component.dependencies):
                notes.append("Integrates with React Hook Form for form validation")

            if any('zod' in dep for dep in component.dependencies):
                notes.append("Uses Zod for schema validation")

        if component.registryDependencies:
            notes.append(f"Requires additional shadcn components: {', '.join(component.registryDependencies)}")

        return '. '.join(notes) if notes else "No special setup requirements"

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/health")
        async def health_check():
            """Enhanced health check endpoint with system status"""
            try:
                # Check registry manager status
                registry_status = {}
                for name, registry in self.registry_manager.registries.items():
                    try:
                        collection = self.registry_manager.collections.get(name)
                        count = collection.count() if collection else 0
                        registry_status[name] = {
                            "status": "healthy" if count > 0 else "empty",
                            "component_count": count,
                            "platforms": registry.platforms if hasattr(registry, 'platforms') else []
                        }
                    except Exception as e:
                        registry_status[name] = {
                            "status": "error",
                            "error": str(e)
                        }

                # Overall system health
                total_components = sum(status.get("component_count", 0) for status in registry_status.values())
                healthy_registries = sum(1 for status in registry_status.values() if status.get("status") == "healthy")

                return {
                    "status": "healthy" if healthy_registries > 0 else "degraded",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "2.0.0",
                    "registries": registry_status,
                    "summary": {
                        "total_registries": len(registry_status),
                        "healthy_registries": healthy_registries,
                        "total_components": total_components,
                        "cache_size": len(self.vector_store.components_cache)
                    }
                }
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

        @self.app.get("/api/v1/components/search", response_model=APIResponse)
        async def search_components(
            q: str = Query(..., description="Search query"),
            limit: int = Query(10, description="Maximum number of results"),
            registry: Optional[str] = Query(None, description="Specific registry to search"),
            platform: Optional[str] = Query(None, description="Platform filter (reactjs, reactnative)")
        ):
            """Search for components using natural language with registry and platform filtering"""
            try:
                search_results = []

                # Determine which registries to search
                target_registries = []
                if registry:
                    # Search specific registry
                    if registry in self.registry_manager.collections:
                        target_registries = [(registry, self.registry_manager.collections[registry])]
                    else:
                        return APIResponse(
                            success=False,
                            data=[],
                            error=f"Registry '{registry}' not found"
                        )
                else:
                    # Search all available registries
                    target_registries = list(self.registry_manager.collections.items())

                # Search each registry and combine results
                for registry_name, collection in target_registries:
                    try:
                        # Perform vector search
                        results = collection.query(
                            query_texts=[q],
                            n_results=min(limit, 20)  # Get more results for better ranking
                        )

                        if results and results.get('ids') and results['ids'][0]:
                            for i, component_id in enumerate(results['ids'][0]):
                                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                                distance = results['distances'][0][i] if results.get('distances') else 1.0

                                # Get platform information
                                component_platform = metadata.get('platform', '')
                                if isinstance(component_platform, str):
                                    component_platform = [component_platform]

                                # Apply platform filter if specified
                                if platform and platform not in component_platform:
                                    continue

                                # Convert distance to relevance score (lower distance = higher relevance)
                                relevance_score = max(0.0, 1.0 - distance)

                                # Parse additional metadata
                                categories = metadata.get('categories', '').split(',') if metadata.get('categories') else []
                                dependencies = metadata.get('dependencies', '').split(',') if metadata.get('dependencies') else []
                                registry_deps = metadata.get('registry_dependencies', '').split(',') if metadata.get('registry_dependencies') else []

                                search_results.append(SearchResultResponse(
                                    name=metadata.get('name', 'Unknown'),
                                    type=metadata.get('type', 'ui'),
                                    description=metadata.get('description', ''),
                                    relevanceScore=relevance_score,
                                    installCommand=metadata.get('install_command', ''),
                                    registry=metadata.get('registry', registry_name),
                                    platform=component_platform,
                                    categories=categories,
                                    dependencies=dependencies,
                                    registryDependencies=registry_deps
                                ))

                    except Exception as e:
                        self.logger.warning(f"Search failed for registry {registry_name}: {e}")
                        continue

                # Sort by relevance score and limit results
                search_results.sort(key=lambda x: x.relevanceScore, reverse=True)
                search_results = search_results[:limit]

                return APIResponse(
                    success=True,
                    data=search_results
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Search failed: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v1/components/{name}", response_model=APIResponse)
        async def get_component_details(name: str):
            """Get detailed information about a specific component"""
            try:
                component = self.vector_store.get_component(name)
                if not component:
                    return JSONResponse(
                        status_code=404,
                        content=APIResponse(
                            success=False,
                            error=f"Component '{name}' not found"
                        ).dict()
                    )

                component_data = ComponentResponse(
                    name=component.name,
                    type=component.type,
                    description=component.description,
                    dependencies=component.dependencies,
                    registryDependencies=component.registryDependencies,
                    categories=component.categories,
                    installCommand=component.installCommand,
                    fileLocation=component.fileLocation
                )

                return APIResponse(
                    success=True,
                    data=component_data.dict()
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get component details: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v1/components", response_model=APIResponse)
        async def list_components(
            type: Optional[str] = Query(None, description="Filter by component type (ui/block/hook)"),
            limit: int = Query(50, description="Maximum number of results")
        ):
            """List components, optionally filtered by type"""
            try:
                components = self.vector_store.get_all_components(type)

                if limit:
                    components = components[:limit]

                component_list = []
                for component in components:
                    component_list.append(ComponentResponse(
                        name=component.name,
                        type=component.type,
                        description=component.description,
                        dependencies=component.dependencies,
                        registryDependencies=component.registryDependencies,
                        categories=component.categories,
                        installCommand=component.installCommand,
                        fileLocation=component.fileLocation
                    ))

                return APIResponse(
                    success=True,
                    data=component_list
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list components: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v1/components/{name}/installation", response_model=APIResponse)
        async def get_installation_info(name: str):
            """Get installation information for a component"""
            try:
                component = self.vector_store.get_component(name)
                if not component:
                    return JSONResponse(
                        status_code=404,
                        content=APIResponse(
                            success=False,
                            error=f"Component '{name}' not found"
                        ).dict()
                    )

                install_info = InstallationInfoResponse(
                    command=component.installCommand,
                    dependencies=component.dependencies,
                    registryDependencies=component.registryDependencies,
                    setupNotes=self._generate_setup_notes(component)
                )

                return APIResponse(
                    success=True,
                    data=install_info.dict()
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get installation info: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v1/stats", response_model=APIResponse)
        async def get_stats():
            """Get database statistics"""
            try:
                stats = self.vector_store.get_stats()
                return APIResponse(
                    success=True,
                    data=stats
                )
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get stats: {str(e)}"
                    ).dict()
                )

        # Context Management Endpoints
        @self.app.post("/api/v1/context/set", response_model=APIResponse)
        async def set_context(request: ContextRequest):
            """Set platform context"""
            try:
                context = self.context_manager.set_context(
                    platform=request.platform,
                    session_id=request.session_id,
                    user_agent=request.user_agent,
                    project_type=request.project_type
                )

                registries = self.context_manager.get_registries_for_context(context.platform)

                return APIResponse(
                    success=True,
                    data=ContextResponse(
                        platform=context.platform.value,
                        session_id=context.session_id,
                        timestamp=context.timestamp,
                        registries=registries
                    ).dict()
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to set context: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v1/context/current", response_model=APIResponse)
        async def get_current_context(session_id: Optional[str] = None):
            """Get current platform context"""
            try:
                context = self.context_manager.get_context(session_id)
                if not context:
                    return APIResponse(
                        success=False,
                        error="No context set"
                    )

                registries = self.context_manager.get_registries_for_context(context.platform)

                return APIResponse(
                    success=True,
                    data=ContextResponse(
                        platform=context.platform.value,
                        session_id=context.session_id,
                        timestamp=context.timestamp,
                        registries=registries
                    ).dict()
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get context: {str(e)}"
                    ).dict()
                )

        @self.app.delete("/api/v1/context/clear", response_model=APIResponse)
        async def clear_context(session_id: Optional[str] = None):
            """Clear platform context"""
            try:
                success = self.context_manager.clear_context(session_id)
                return APIResponse(
                    success=success,
                    data={"message": "Context cleared successfully" if success else "No context to clear"}
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to clear context: {str(e)}"
                    ).dict()
                )

        # Registry Management Endpoints
        @self.app.get("/api/v1/registries", response_model=APIResponse)
        async def list_registries(platform: Optional[str] = None):
            """List available registries"""
            try:
                platform_context = None
                if platform:
                    try:
                        platform_context = PlatformContext(platform)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid platform: {platform}"
                            ).dict()
                        )

                registries = self.registry_manager.get_available_registries(platform_context)
                registry_responses = [
                    RegistryResponse(
                        name=reg.name,
                        description=reg.description,
                        component_count=reg.component_count,
                        platforms=reg.platform,
                        is_active=reg.is_active
                    )
                    for reg in registries
                ]

                return APIResponse(
                    success=True,
                    data=registry_responses
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list registries: {str(e)}"
                    ).dict()
                )

        # Enhanced Context-Aware Search Endpoints
        @self.app.get("/api/v2/components/search", response_model=APIResponse)
        async def search_components_v2(
            q: str = Query(..., description="Search query"),
            platform: Optional[str] = Query(None, description="Platform context (reactjs, reactnative)"),
            session_id: Optional[str] = Query(None, description="Session ID"),
            limit: int = Query(10, description="Maximum number of results")
        ):
            """Context-aware component search"""
            try:
                # Use provided platform or current context
                platform_context = None
                if platform:
                    try:
                        platform_context = PlatformContext(platform)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid platform: {platform}"
                            ).dict()
                        )
                else:
                    platform_context = self.context_manager.get_current_platform()

                # Search using registry manager
                results = self.registry_manager.search_components(
                    query=q,
                    platform_context=platform_context,
                    limit=limit
                )

                # Format results
                search_results = []
                for result in results:
                    component_data = result.component
                    search_results.append({
                        "name": component_data.get("name"),
                        "type": component_data.get("type", "component"),
                        "description": component_data.get("description"),
                        "registry": result.registry,
                        "relevance_score": result.relevance_score,
                        "context_match": result.context_match,
                        "platform_relevance": result.platform_relevance,
                        "dependencies": component_data.get("dependencies", []),
                        "install_command": component_data.get("installCommand", "")
                    })

                return APIResponse(
                    success=True,
                    data={
                        "results": search_results,
                        "context": {
                            "platform": platform_context.value if platform_context else "none",
                            "registries_searched": self.registry_manager.get_registries_for_context(platform_context)
                        }
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Search failed: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/components/{name}", response_model=APIResponse)
        async def get_component_details_v2(
            name: str,
            registry: Optional[str] = Query(None, description="Specific registry to search")
        ):
            """Get detailed component information with registry awareness"""
            try:
                component = self.registry_manager.get_component_details(name, registry)

                if not component:
                    return JSONResponse(
                        status_code=404,
                        content=APIResponse(
                            success=False,
                            error=f"Component '{name}' not found"
                        ).dict()
                    )

                return APIResponse(
                    success=True,
                    data=component
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get component details: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/components", response_model=APIResponse)
        async def list_components_v2(
            registry: Optional[str] = Query(None, description="Specific registry"),
            platform: Optional[str] = Query(None, description="Platform context"),
            limit: int = Query(50, description="Maximum number of results")
        ):
            """List components with context awareness"""
            try:
                platform_context = None
                if platform:
                    try:
                        platform_context = PlatformContext(platform)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid platform: {platform}"
                            ).dict()
                        )

                components = self.registry_manager.list_components(
                    registry_name=registry,
                    platform_context=platform_context,
                    limit=limit
                )

                return APIResponse(
                    success=True,
                    data={
                        "components": components,
                        "total_count": len(components)
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list components: {str(e)}"
                    ).dict()
                )

        # Context Management Endpoints
        @self.app.post("/api/v2/context/set", response_model=APIResponse)
        async def set_platform_context(
            platform: str = Form(...),
            session_id: Optional[str] = Form(None),
            user_agent: Optional[str] = Form(None),
            project_type: Optional[str] = Form(None)
        ):
            """Set the current platform context"""
            try:
                from context_manager import PlatformContext

                # Convert string to enum
                try:
                    platform_enum = PlatformContext(platform)
                except ValueError:
                    return JSONResponse(
                        status_code=400,
                        content=APIResponse(
                            success=False,
                            error=f"Invalid platform: {platform}. Must be one of: [reactjs, reactnative, auto, none]"
                        ).dict()
                    )

                context_info = self.context_manager.set_context(
                    platform_enum,
                    session_id,
                    user_agent,
                    project_type
                )

                return APIResponse(
                    success=True,
                    data={
                        "platform": context_info.platform.value,
                        "session_id": context_info.session_id,
                        "timestamp": context_info.timestamp,
                        "user_agent": context_info.user_agent,
                        "project_type": context_info.project_type,
                        "confidence": context_info.confidence
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to set platform context: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/context", response_model=APIResponse)
        async def get_platform_context(
            session_id: Optional[str] = Query(None, description="Session identifier")
        ):
            """Get the current platform context"""
            try:
                context_info = self.context_manager.get_context(session_id)

                if not context_info:
                    return APIResponse(
                        success=True,
                        data=None,
                        message="No platform context is currently set"
                    )

                return APIResponse(
                    success=True,
                    data={
                        "platform": context_info.platform.value,
                        "session_id": context_info.session_id,
                        "timestamp": context_info.timestamp,
                        "user_agent": context_info.user_agent,
                        "project_type": context_info.project_type,
                        "confidence": context_info.confidence
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get platform context: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/registries", response_model=APIResponse)
        async def list_registries_v2(
            platform: Optional[str] = Query(None, description="Platform filter for registries")
        ):
            """List available component registries with platform awareness"""
            try:
                from context_manager import PlatformContext

                platform_context = None
                if platform:
                    try:
                        platform_context = PlatformContext(platform)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid platform: {platform}"
                            ).dict()
                        )

                registries = self.registry_manager.get_available_registries(platform_context)

                return APIResponse(
                    success=True,
                    data=[
                        {
                            "name": reg.name,
                            "path": reg.path,
                            "platform": reg.platform,
                            "description": reg.description,
                            "component_count": reg.component_count,
                            "last_updated": reg.last_updated,
                            "is_active": reg.is_active
                        }
                        for reg in registries
                    ]
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list registries: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/context/stats", response_model=APIResponse)
        async def get_context_stats():
            """Get context usage statistics"""
            try:
                stats = self.context_manager.get_context_stats()
                return APIResponse(
                    success=True,
                    data=stats
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get context stats: {str(e)}"
                    ).dict()
                )

        # Specialized Extraction Pipeline Endpoints
        @self.app.get("/api/v2/extraction/registries", response_model=APIResponse)
        async def list_extraction_registries():
            """List available registries for extraction"""
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from services.registry_config_manager import RegistryConfigManager
                manager = RegistryConfigManager("rag_databases/registry_config")
                registries = manager.list_registries()

                registry_details = []
                for registry_name in registries:
                    try:
                        config = manager.load_registry_config(registry_name)
                        if config:
                            registry_details.append({
                                "name": registry_name,
                                "display_name": config.display_name,
                                "description": config.description,
                                "platforms": config.platforms,
                                "categories": list(config.categories.keys()),
                                "status": config.status.value,
                                "component_count": sum(
                                    len(category.sources) for category in config.categories.values()
                                )
                            })
                    except Exception as e:
                        registry_details.append({
                            "name": registry_name,
                            "error": str(e)
                        })

                return APIResponse(
                    success=True,
                    data={
                        "registries": registry_details,
                        "total_count": len(registries)
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list extraction registries: {str(e)}"
                    ).dict()
                )

        @self.app.post("/api/v2/extraction/run", response_model=APIResponse)
        async def run_extraction(
            registry: Optional[str] = Form(None, description="Specific registry to extract"),
            source: Optional[str] = Form(None, description="Specific source to extract"),
            mode: str = Form("test", description="Extraction mode (test/real)")
        ):
            """Run extraction pipeline"""
            try:
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from scripts.run_extraction import run_test_mode, run_real_mode

                if mode == "test":
                    success = await run_test_mode()
                elif mode == "real":
                    success = await run_real_mode(registry, source)
                else:
                    return JSONResponse(
                        status_code=400,
                        content=APIResponse(
                            success=False,
                            error=f"Invalid mode: {mode}. Must be 'test' or 'real'"
                        ).dict()
                    )

                return APIResponse(
                    success=success,
                    data={
                        "mode": mode,
                        "registry": registry,
                        "source": source,
                        "message": "Extraction completed successfully" if success else "Extraction failed"
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Extraction failed: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/extraction/status", response_model=APIResponse)
        async def get_extraction_status():
            """Get extraction pipeline status and statistics"""
            try:
                from pathlib import Path
                import json

                output_dir = Path("rag_databases/extracted_data")
                status = {
                    "output_directory_exists": output_dir.exists(),
                    "extracted_files": [],
                    "total_components": 0,
                    "last_extraction": None
                }

                if output_dir.exists():
                    extracted_files = list(output_dir.glob("*_extracted.json"))
                    merged_files = list(output_dir.glob("*_merged.json"))

                    status["extracted_files"] = [f.stem for f in extracted_files]
                    status["merged_files"] = [f.stem for f in merged_files]

                    # Calculate total components
                    for extracted_file in extracted_files:
                        try:
                            with open(extracted_file, 'r') as f:
                                data = json.load(f)
                                status["total_components"] += data.get("total_components", 0)

                                # Track last extraction time
                                extraction_time = data.get("extraction_timestamp")
                                if extraction_time and (not status["last_extraction"] or extraction_time > status["last_extraction"]):
                                    status["last_extraction"] = extraction_time
                        except Exception:
                            pass

                return APIResponse(
                    success=True,
                    data=status
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to get extraction status: {str(e)}"
                    ).dict()
                )

        @self.app.get("/api/v2/components/search/category", response_model=APIResponse)
        async def search_components_by_category(
            q: str = Query(..., description="Search query"),
            category: str = Query(..., description="Component category (components/hooks/blocks)"),
            platform: Optional[str] = Query(None, description="Platform context"),
            limit: int = Query(10, description="Maximum number of results"),
            quality_threshold: float = Query(0.0, description="Minimum quality score threshold"),
            strategy: str = Query("weighted", description="Search strategy (exact/semantic/cross/weighted)")
        ):
            """Enhanced category-aware component search"""
            try:
                from context_manager import PlatformContext

                # Validate platform context
                platform_context = None
                if platform:
                    try:
                        platform_context = PlatformContext(platform)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid platform: {platform}"
                            ).dict()
                        )

                # Use enhanced category search service
                try:
                    from services.category_search_service import get_category_search_service, SearchStrategy
                    search_service = get_category_search_service()

                    # Parse strategy
                    try:
                        search_strategy = SearchStrategy(strategy)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=APIResponse(
                                success=False,
                                error=f"Invalid search strategy: {strategy}. Use: exact, semantic, cross, weighted"
                            ).dict()
                        )

                    # Create search query
                    search_query = search_service.create_search_query(
                        query=q,
                        categories=[category],
                        platforms=[platform] if platform else None,
                        quality_threshold=quality_threshold,
                        strategy=search_strategy
                    )

                    # Perform enhanced search
                    enhanced_results = await search_service.search_components(search_query, limit)

                    # Convert to response format
                    results = [result.to_dict() for result in enhanced_results]

                    # Get category suggestions
                    category_suggestions = search_service.suggest_categories(q)

                    return APIResponse(
                        success=True,
                        data={
                            "results": results,
                            "category": category,
                            "total_found": len(results),
                            "query_analysis": {
                                "strategy": strategy,
                                "quality_threshold": quality_threshold,
                                "category_suggestions": category_suggestions,
                                "applied_filters": {
                                    "categories": [category],
                                    "platform": platform,
                                    "quality_threshold": quality_threshold
                                }
                            },
                            "context": {
                                "platform": platform_context.value if platform_context else "none",
                                "registries_searched": self.registry_manager.get_registries_for_context(platform_context) if self.registry_manager else []
                            }
                        }
                    )

                except ImportError:
                    # Fallback to legacy search if enhanced service not available
                    self.logger.warning("Enhanced search service not available, using legacy search")
                    return await self._legacy_category_search(q, category, platform_context, limit)

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Category search failed: {str(e)}"
                    ).dict()
                )

        async def _legacy_category_search(self, q: str, category: str, platform_context, limit: int):
            """Legacy category search fallback"""
            # Use registry manager with category filter
            results = self.registry_manager.search_components(
                query=q,
                platform_context=platform_context,
                limit=limit
            )

            # Filter by category and enhance results
            category_results = []
            for result in results:
                component_data = result.component

                # Check if component matches category
                component_categories = component_data.get("categories", [])
                component_type = component_data.get("type", "")

                category_match = (
                    category in component_categories or
                    category in component_type.lower() or
                    (category == "hooks" and "hook" in component_type.lower()) or
                    (category == "blocks" and "block" in component_type.lower())
                )

                if category_match:
                    enhanced_result = {
                        "name": component_data.get("name"),
                        "type": component_data.get("type", "component"),
                        "description": component_data.get("description"),
                        "registry": result.registry,
                        "relevance_score": result.relevance_score,
                        "context_match": result.context_match,
                        "platform_relevance": result.platform_relevance,
                        "category_match": category,
                        "categories": component_categories,
                        "dependencies": component_data.get("dependencies", []),
                        "install_command": component_data.get("installCommand", "")
                    }
                    category_results.append(enhanced_result)

            return APIResponse(
                success=True,
                data={
                    "results": category_results,
                    "category": category,
                    "total_found": len(category_results),
                    "context": {
                        "platform": platform_context.value if platform_context else "none",
                        "registries_searched": self.registry_manager.get_registries_for_context(platform_context)
                    },
                    "legacy_mode": True
                }
            )

        @self.app.get("/api/v2/extraction/sources", response_model=APIResponse)
        async def list_registry_sources(
            registry: str = Query(..., description="Registry name")
        ):
            """List sources for a specific registry"""
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from services.registry_config_manager import RegistryConfigManager

                manager = RegistryConfigManager("rag_databases/registry_config")
                config = manager.load_registry_config(registry)

                if not config:
                    return JSONResponse(
                        status_code=404,
                        content=APIResponse(
                            success=False,
                            error=f"Registry '{registry}' not found"
                        ).dict()
                    )

                sources_info = {}
                for category_name, category_config in config.categories.items():
                    sources_info[category_name] = [
                        {
                            "name": source.name,
                            "type": source.type.value,
                            "url": getattr(source, 'url', ''),
                            "enabled": category_config.enabled,
                            "priority": getattr(source, 'priority', 1),
                            "extractor": getattr(source, 'extractor', 'auto')
                        }
                        for source in category_config.sources
                    ]

                return APIResponse(
                    success=True,
                    data={
                        "registry": registry,
                        "categories": sources_info,
                        "total_sources": sum(len(sources) for sources in sources_info.values())
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to list registry sources: {str(e)}"
                    ).dict()
                )

        @self.app.delete("/api/v2/extraction/clear", response_model=APIResponse)
        async def clear_extraction_data(
            registry: Optional[str] = Query(None, description="Specific registry to clear")
        ):
            """Clear extracted data files"""
            try:
                from pathlib import Path
                import os

                output_dir = Path("rag_databases/extracted_data")
                if not output_dir.exists():
                    return APIResponse(
                        success=True,
                        data={"message": "No extraction data to clear"}
                    )

                cleared_files = []
                if registry:
                    # Clear specific registry
                    patterns = [f"{registry}_extracted.json", f"{registry}_merged.json"]
                    for pattern in patterns:
                        file_path = output_dir / pattern
                        if file_path.exists():
                            file_path.unlink()
                            cleared_files.append(file_path.name)
                else:
                    # Clear all extraction data
                    for file_path in output_dir.glob("*"):
                        if file_path.is_file():
                            file_path.unlink()
                            cleared_files.append(file_path.name)

                return APIResponse(
                    success=True,
                    data={
                        "cleared_files": cleared_files,
                        "registry": registry,
                        "message": f"Cleared {len(cleared_files)} files"
                    }
                )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=APIResponse(
                        success=False,
                        error=f"Failed to clear extraction data: {str(e)}"
                    ).dict()
                )

    def _setup_exception_handlers(self):
        """Setup global exception handlers"""

        @self.app.exception_handler(ValueError)
        async def value_error_exception_handler(request, exc: ValueError):
            """Handle validation errors"""
            self.logger.warning(f"Validation error: {exc}")
            return JSONResponse(
                status_code=400,
                content=APIResponse(
                    success=False,
                    error=f"Validation error: {str(exc)}"
                ).dict()
            )

        @self.app.exception_handler(KeyError)
        async def key_error_exception_handler(request, exc: KeyError):
            """Handle missing key errors"""
            self.logger.warning(f"Key error: {exc}")
            return JSONResponse(
                status_code=404,
                content=APIResponse(
                    success=False,
                    error=f"Resource not found: {str(exc)}"
                ).dict()
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc: Exception):
            """Handle all other exceptions"""
            self.logger.error(f"Unexpected error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=APIResponse(
                    success=False,
                    error="Internal server error. Please try again later."
                ).dict()
            )

    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the API server"""
        print(f"🚀 Starting SimFlo RAG API server on {host}:{port}")
        print(f"📊 Components loaded: {len(self.vector_store.components_cache)}")
        print(f"💾 Vector store entries: {self.vector_store.collection.count()}")

        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main function to run the API server"""
    import argparse

    parser = argparse.ArgumentParser(description="SimFlo RAG API Server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    parser.add_argument(
        "--persist-dir",
        default="./chroma_db",
        help="Vector store directory"
    )

    args = parser.parse_args()

    # Check if vector store exists
    persist_dir = Path(args.persist_dir)
    if not persist_dir.exists():
        print("❌ Vector store not found. Please run indexing first:")
        print("   python3 vector_store.py --stats")
        return 1

    # Start server
    server = RAGAPIServer(args.persist_dir)
    server.run(args.host, args.port)


if __name__ == "__main__":
    exit(main())