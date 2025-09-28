#!/usr/bin/env python3
"""
Simple test script to debug ChromaDB collection creation issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data-pipeline'))

import chromadb
from chromadb.config import Settings
from pathlib import Path

def test_collection_creation():
    """Test basic ChromaDB collection creation"""

    # Test shadcn
    print("Testing shadcn ChromaDB...")
    chroma_path = Path("./rag_databases/shadcn_db/chroma_db")
    chroma_path.mkdir(exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )

    print(f"Client created for path: {chroma_path}")

    # List existing collections
    try:
        collections = client.list_collections()
        print(f"Existing collections: {[col.name for col in collections]}")
    except Exception as e:
        print(f"Error listing collections: {e}")

    # Try to create collection
    collection_name = "components_shadcn"
    print(f"Attempting to create collection: {collection_name}")

    try:
        # First try to delete if it exists
        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted existing collection: {collection_name}")
        except (ValueError, chromadb.errors.NotFoundError):
            print(f"Collection {collection_name} doesn't exist, will create new")

        # Now create it
        collection = client.create_collection(name=collection_name)
        print(f"Successfully created collection: {collection_name}")
        print(f"Collection count: {collection.count()}")

        # Test adding a document
        collection.add(
            documents=["test document"],
            metadatas=[{"name": "test", "type": "ui"}],
            ids=["test_1"]
        )
        print(f"Added test document, count: {collection.count()}")

        # Test search
        results = collection.query(query_texts=["test"], n_results=1)
        print(f"Search results: {results}")

        return True

    except Exception as e:
        print(f"Error creating collection {collection_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_collection_creation()