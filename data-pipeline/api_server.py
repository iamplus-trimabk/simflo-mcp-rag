#!/usr/bin/env python3
"""
SimFlo MCP RAG - API Server

HTTP API server for RAG database queries that the TypeScript MCP server can use.
"""

import json
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path

from vector_store import VectorStore
from parse_registry import ShadcnComponent


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


class RAGAPIServer:
    """HTTP API server for RAG database queries"""

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.app = FastAPI(
            title="SimFlo RAG API",
            description="API for querying shadcn components RAG database",
            version="1.0.0"
        )
        self.vector_store = VectorStore(str(self.persist_dir))

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