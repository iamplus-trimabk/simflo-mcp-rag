# Ultimate Clean v2 Migration - ZERO Root Files

## 🎯 Objective
Achieve absolutely clean root directory with ONLY git/config files. EVERYTHING moves to v2.

## 📋 Complete Zero-Root Migration Tasks

### 1. **Move All Documentation to v2**
- `*.md` files → `v2/docs/`
- `API_VERSION_STRATEGY.md` → `v2/docs/api/`
- `SETUP.md` → `v2/docs/setup/`
- `CLAUDE_CONFIG.md` → `v2/docs/config/`
- `project_summary.md` → `v2/docs/project/`
- `current_context.md` → `v2/docs/context/`

### 2. **Move Extractor Implementation to v2**
- `/extractors/*` → `v2/04-extractors/core/` (actual implementation)
- Update CLI in `v2/04-extractors/` to import from `./core/`
- Delete old `/extractors/` directory completely

### 3. **Migrate RAG Databases to Registry Structure**
- `/rag_databases/shadcn_db/` → `v2/core/00-rag-registry/registries/shadcn/db/`
- `/rag_databases/gluestack_db/` → `v2/core/00-rag-registry/registries/gluestack/db/`
- `/rag_databases/radix_db/` → `v2/core/00-rag-registry/registries/radix/db/`
- `/rag_databases/test_docs/` → `v2/core/00-rag-registry/registries/test_docs/db/`
- `/rag_databases/registry_config.*` → `v2/core/00-rag-registry/config/`
- Delete `/rag_databases/` completely

### 4. **Move All Support Directories to v2**
- `/scripts/` → `v2/scripts/`
- `/utils/` → `v2/utils/`
- `/services/` → `v2/services/`
- `/models/` → `v2/models/`
- `/configs/` → `v2/configs/`
- `/user_guide/` → `v2/docs/user_guide/`

### 5. **Delete All Obsolete Components**
- Remove entire `/mcp-server/` (TypeScript version)
- Remove broken `extract.py` (references deleted data-pipeline)
- Remove `__init__.py` (not needed)
- Remove `chroma_db/`, `test_output/`, `__pycache__/`, `.pytest_cache/`
- Remove `.benchmarks/`, `.bmad-core/` (if not needed)

### 6. **Move Essential Status Files to v2**
- `current_mvp.txt` → `v2/config/current_mvp.txt`
- Update any references to new location

### 7. **Update All Import Paths**
- Fix extractors CLI to import from `./core/` instead of root `/extractors/`
- Fix any remaining references to old directory structure
- Update v2 components to work with new registry/database locations

## ✅ Ultimate End State

### 🎯 **Root Directory (ZERO Files)**
```
simflo-mcp-rag/
├── .git/
├── .claude/
└── v2/                    # LITERALLY EVERYTHING
```

### 🏗️ **Complete v2 Structure**
```
v2/
├── 00-rag-registry/
│   ├── registries/
│   │   ├── shadcn/db/     # Moved from rag_databases/
│   │   ├── gluestack/db/  # Moved from rag_databases/
│   │   └── radix/db/      # Moved from rag_databases/
│   └── config/            # Moved from rag_databases/
├── 01-mcp-server/
├── 02-rag-builder/
├── 03-content-collection/
├── 04-extractors/
│   ├── core/              # Moved from root extractors/
│   └── extractors_cli.py
├── docs/                  # All documentation
├── scripts/               # Moved from root/
├── utils/                 # Moved from root/
├── services/              # Moved from root/
├── models/                # Moved from root/
├── configs/               # Moved from root/
└── config/
    └── current_mvp.txt    # Moved from root/
```

## 🔥 Critical Success Metrics
- **Zero files** in root directory (except .git/.claude)
- All functionality preserved and working
- No broken import paths anywhere
- Complete self-contained v2 architecture
- Registry-based database structure functional

## ⏱️ **Time Estimate: 2-3 hours**
- File moves and reorganization: 90-120 minutes
- Import path updates: 60-90 minutes
- Testing and verification: 30-45 minutes
- Final cleanup and commit: 15-30 minutes