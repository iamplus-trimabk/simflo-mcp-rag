#!/usr/bin/env python3
"""
SimFlo MCP RAG - API Server

HTTP API server for RAG database queries that the TypeScript MCP server can use.
"""

import json
import uvicorn
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

        # Load components cache if needed
        if self.vector_store.collection.count() > 0 and not self.vector_store.components_cache:
            self._load_components_to_cache()

        self._setup_routes()

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
            """Health check endpoint"""
            return {
                "status": "healthy",
                "components_count": len(self.vector_store.components_cache),
                "vector_store_count": self.vector_store.collection.count()
            }

        @self.app.get("/api/v1/components/search", response_model=APIResponse)
        async def search_components(
            q: str = Query(..., description="Search query"),
            limit: int = Query(10, description="Maximum number of results")
        ):
            """Search for components using natural language"""
            try:
                results = self.vector_store.search(q, limit)

                search_results = []
                for result in results:
                    search_results.append(SearchResultResponse(
                        name=result.component.name,
                        type=result.component.type,
                        description=result.component.description,
                        relevanceScore=result.relevance_score,
                        installCommand=result.component.installCommand
                    ))

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