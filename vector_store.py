#!/usr/bin/env python3
"""
SimFlo MCP RAG - Vector Store

Creates and manages vector embeddings for component search using ChromaDB.
"""

import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import argparse

from parse_registry import ShadcnComponent


@dataclass
class SearchResult:
    """Represents a search result from the vector store"""
    component: ShadcnComponent
    relevance_score: float
    matched_fields: List[str]


class VectorStore:
    """Manages vector storage and retrieval for components"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="shadcn_components",
            metadata={"description": "Shadcn components for semantic search"}
        )

        # Cache for components
        self.components_cache: Dict[str, ShadcnComponent] = {}

    def _create_search_text(self, component: ShadcnComponent) -> str:
        """Create searchable text from component data"""
        parts = [
            f"Name: {component.name}",
            f"Type: {component.type}",
        ]

        if component.description:
            parts.append(f"Description: {component.description}")

        if component.categories:
            parts.append(f"Categories: {', '.join(component.categories)}")

        if component.dependencies:
            parts.append(f"Dependencies: {', '.join(component.dependencies)}")

        if component.registryDependencies:
            parts.append(f"Registry Dependencies: {', '.join(component.registryDependencies)}")

        # Add information about files
        file_paths = [f.path for f in component.files if f.path]
        if file_paths:
            parts.append(f"Files: {', '.join(file_paths)}")

        return "\n".join(parts)

    def index_components(self, components: List[ShadcnComponent]) -> None:
        """Index components in the vector store"""
        print(f"Indexing {len(components)} components in vector store...")

        # Clear existing data
        if self.collection.count() > 0:
            print("Clearing existing vector store...")
            self.collection.delete()

        # Prepare data for indexing
        documents = []
        metadatas = []
        ids = []

        for component in components:
            # Create searchable text
            search_text = self._create_search_text(component)

            # Create metadata
            metadata = {
                "name": component.name,
                "type": component.type,
                "dependencies": json.dumps(component.dependencies),
                "registryDependencies": json.dumps(component.registryDependencies),
                "categories": json.dumps(component.categories),
                "installCommand": component.installCommand,
                "fileLocation": component.fileLocation
            }

            if component.description:
                metadata["description"] = component.description

            # Add to batch
            documents.append(search_text)
            metadatas.append(metadata)
            ids.append(component.name)

            # Cache component
            self.components_cache[component.name] = component

        # Add to vector store in batches
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_documents = documents[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            batch_ids = ids[i:end_idx]

            self.collection.add(
                documents=batch_documents,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"  Indexed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

        print(f"Successfully indexed {len(components)} components")
        print(f"Vector store contains {self.collection.count()} entries")

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for components using semantic search"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )

            search_results = []
            for i in range(len(results['ids'][0])):
                component_id = results['ids'][0][i]
                distance = results['distances'][0][i]
                metadata = results['metadatas'][0][i]

                # Convert distance to relevance score (lower distance = higher relevance)
                relevance_score = 1.0 - min(distance, 2.0) / 2.0

                # Get component from cache
                component = self.components_cache.get(component_id)
                if not component:
                    # Reconstruct component from metadata if not in cache
                    component = ShadcnComponent(
                        name=metadata['name'],
                        type=metadata['type'],
                        description=metadata.get('description'),
                        dependencies=json.loads(metadata['dependencies']),
                        registryDependencies=json.loads(metadata['registryDependencies']),
                        categories=json.loads(metadata['categories']),
                        installCommand=metadata['installCommand'],
                        fileLocation=metadata['fileLocation']
                    )

                search_results.append(SearchResult(
                    component=component,
                    relevance_score=relevance_score,
                    matched_fields=['name', 'description', 'type']
                ))

            return search_results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_component(self, name: str) -> Optional[ShadcnComponent]:
        """Get a specific component by name"""
        return self.components_cache.get(name)

    def get_all_components(self, component_type: Optional[str] = None) -> List[ShadcnComponent]:
        """Get all components, optionally filtered by type"""
        components = list(self.components_cache.values())

        if component_type:
            components = [c for c in components if c.type == component_type]

        return components

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        components_by_type = {}
        for component in self.components_cache.values():
            components_by_type[component.type] = components_by_type.get(component.type, 0) + 1

        return {
            "total_components": len(self.components_cache),
            "components_by_type": components_by_type,
            "vector_store_count": self.collection.count()
        }


def main():
    """Main function for vector store operations"""
    parser = argparse.ArgumentParser(description="Manage vector store for shadcn components")
    parser.add_argument(
        "--components-file",
        default="components.json",
        help="Path to components JSON file"
    )
    parser.add_argument(
        "--persist-dir",
        default="./chroma_db",
        help="Directory to persist vector store"
    )
    parser.add_argument(
        "--search",
        help="Search query (if provided, will perform search)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of search results to return"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show vector store statistics"
    )

    args = parser.parse_args()

    # Load components
    try:
        with open(args.components_file, 'r', encoding='utf-8') as f:
            components_data = json.load(f)

        components = []
        for comp_data in components_data:
            # Convert file dictionaries back to RegistryFile objects
            files_data = comp_data.get('files', [])
            files = []
            for file_data in files_data:
                from parse_registry import RegistryFile
                files.append(RegistryFile(**file_data))

            comp_data['files'] = files
            components.append(ShadcnComponent(**comp_data))

        print(f"Loaded {len(components)} components from {args.components_file}")

    except FileNotFoundError:
        print(f"Error: Components file not found: {args.components_file}")
        print("Please run 'python3 parse_registry.py' first to generate components.json")
        return 1

    # Initialize vector store
    vector_store = VectorStore(args.persist_dir)

    # Index components if vector store is empty
    if vector_store.collection.count() == 0:
        print("Vector store is empty, indexing components...")
        vector_store.index_components(components)
    else:
        print(f"Vector store already contains {vector_store.collection.count()} entries")

    # Perform search if requested
    if args.search:
        print(f"\nSearching for: '{args.search}'")
        results = vector_store.search(args.search, args.limit)

        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.component.name} ({result.component.type})")
                print(f"   Relevance: {result.relevance_score:.3f}")
                if result.component.description:
                    print(f"   Description: {result.component.description}")
                print(f"   Install: {result.component.installCommand}")
        else:
            print("No results found")

    # Show statistics if requested
    if args.stats:
        stats = vector_store.get_stats()
        print(f"\nVector Store Statistics:")
        print(f"  Total Components: {stats['total_components']}")
        print(f"  Vector Store Entries: {stats['vector_store_count']}")
        print(f"  Components by Type:")
        for comp_type, count in stats['components_by_type'].items():
            print(f"    {comp_type}: {count}")

    return 0


if __name__ == "__main__":
    exit(main())