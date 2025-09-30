# Storage Engines

## Purpose
Various storage engine implementations and adapters for different data storage needs.

## Role in System
The **data persistence abstraction layer** that provides unified access to different storage backends and technologies.

## What This Directory Contains
- **postgresql-engine/**: PostgreSQL storage engine implementation
- **sqlite-engine/**: SQLite storage engine implementation
- **mongodb-engine/**: MongoDB storage engine implementation
- **redis-engine/**: Redis cache and session storage
- **vector-db-engines/**: Vector database engines (ChromaDB, Pinecone, etc.)
- **file-storage/**: File system storage and management
- **cloud-storage/**: Cloud storage adapters (AWS S3, Google Cloud, etc.)

## What This Directory Should NOT Contain
- **Schema definitions** - belongs in database-schemas/
- **Migration logic** - belongs in migration-tools/
- **Backup logic** - belongs in backup-systems/
- **Performance optimization** - belongs in performance-optimizers/

## CLI Interface
```bash
# PostgreSQL engine
storage-engines/postgresql-engine/init.py --config /path/to/config.json --output /path/to/output
storage-engines/postgresql-engine/connect.py --database "dbname" --user "username" --output /path/to/output
storage-engines/postgresql-engine/execute.py --query "SELECT * FROM table" --output /path/to/output

# SQLite engine
storage-engines/sqlite-engine/init.py --database /path/to/database.db --output /path/to/output
storage-engines/sqlite-engine/connect.py --database /path/to/database.db --output /path/to/output
storage-engines/sqlite-engine/execute.py --query "SELECT * FROM table" --output /path/to/output

# MongoDB engine
storage-engines/mongodb-engine/init.py --config /path/to/config.json --output /path/to/output
storage-engines/mongodb-engine/connect.py --database "dbname" --collection "collection" --output /path/to/output
storage-engines/mongodb-engine/query.py --filter '{"field": "value"}' --output /path/to/output

# Redis engine
storage-engines/redis-engine/init.py --config /path/to/config.json --output /path/to/output
storage-engines/redis-engine/connect.py --host "localhost" --port 6379 --output /path/to/output
storage-engines/redis-engine/execute.py --command "SET key value" --output /path/to/output

# Vector database engines
storage-engines/vector-db-engines/init.py --engine chromadb --config /path/to/config.json --output /path/to/output
storage-engines/vector-db-engines/index.py --data /path/to/data.json --output /path/to/output
storage-engines/vector-db-engines/search.py --query "search terms" --top-k 10 --output /path/to/output

# File storage
storage-engines/file-storage/store.py --file /path/to/file --destination /path/to/destination --output /path/to/output
storage-engines/file-storage/retrieve.py --path /path/to/file --output /path/to/output
storage-engines/file-storage/list.py --directory /path/to/directory --output /path/to/output

# Cloud storage
storage-engines/cloud-storage/upload.py --file /path/to/file --bucket "bucket-name" --provider aws --output /path/to/output
storage-engines/cloud-storage/download.py --object "object-key" --bucket "bucket-name" --output /path/to/output
storage-engines/cloud-storage/list.py --bucket "bucket-name" --provider aws --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, database-schemas/ for schema definitions
- **Provides**: Storage capabilities to all system components
- **Integrates with**: monitoring/ for storage performance and health
- **Serves**: All components requiring data persistence and storage

## Implementation Guidelines
1. **Consistent interface** - provide unified API across different storage engines
2. **Connection management** - handle connection pooling, timeouts, and reconnection
3. **Error handling** - implement robust error handling and recovery mechanisms
4. **Performance optimization** - optimize for specific engine characteristics
5. **Configuration management** - support flexible configuration and deployment options