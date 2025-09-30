# Migration Tools

## Purpose
Data migration and transformation tools for moving data between systems and evolving data structures.

## Role in System
The **data transformation engine** that enables safe data migration, transformation, and evolution between different system versions and storage engines.

## What This Directory Contains
- **schema-migrations/**: Database schema migration tools
- **data-transformers/**: Data transformation and mapping tools
- **export-import-tools/**: Data export and import utilities
- **version-upgraders/**: System version upgrade tools
- **data-mappers/**: Field and record mapping tools
- **validation-tools/**: Migration validation and verification
- **rollback-tools/**: Migration rollback and recovery tools

## What This Directory Should NOT Contain
- **Storage engine logic** - belongs in storage-engines/
- **Schema definitions** - belongs in database-schemas/
- **Backup logic** - belongs in backup-systems/
- **Data validation** - belongs in data-validators/

## CLI Interface
```bash
# Schema migrations
migration-tools/schema-migrations/migrate.py --from-version 1.0 --to-version 2.0 --output /path/to/output
migration-tools/schema-migrations/apply.py --migration /path/to/migration.sql --database /path/to/database --output /path/to/output
migration-tools/schema-migrations/rollback.py --migration /path/to/migration.sql --database /path/to/database --output /path/to/output

# Data transformers
migration-tools/data-transformers/transform.py --source /path/to/source --rules /path/to/rules.json --output /path/to/output
migration-tools/data-transformers/map.py --data /path/to/data --mapping /path/to/mapping.json --output /path/to/output
migration-tools/data-transformers/clean.py --data /path/to/data --rules /path/to/rules.txt --output /path/to/output

# Export/import tools
migration-tools/export-import-tools/export.py --source /path/to/source --format json --output /path/to/output
migration-tools/export-import-tools/import.py --source /path/to/source.json --target /path/to/target --output /path/to/output
migration-tools/export-import-tools/batch.py --sources /path/to/sources.txt --format json --output /path/to/output

# Version upgraders
migration-tools/version-upgraders/upgrade.py --from-version 1.0 --to-version 2.0 --data /path/to/data --output /path/to/output
migration-tools/version-upgraders/prepare.py --version 2.0 --output /path/to/output
migration-tools/version-upgraders/verify.py --version 2.0 --data /path/to/data --output /path/to/output

# Data mappers
migration-tools/data-mappers/map-fields.py --source /path/to/source --mapping /path/to/mapping.json --output /path/to/output
migration-tools/data-mappers/merge.py --source1 /path/to/source1 --source2 /path/to/source2 --output /path/to/output
migration-tools/data-mappers/split.py --source /path/to/source --rules /path/to/rules.json --output /path/to/output

# Validation tools
migration-tools/validation-tools/validate.py --before /path/to/before --after /path/to/after --rules /path/to/rules.json --output /path/to/output
migration-tools/validation-tools/compare.py --source /path/to/source --target /path/to/target --output /path/to/output
migration-tools/validation-tools/test.py --migration /path/to/migration --test-data /path/to/test-data --output /path/to/output

# Rollback tools
migration-tools/rollback-tools/rollback.py --migration /path/to/migration --database /path/to/database --output /path/to/output
migration-tools/rollback-tools/prepare.py --migration /path/to/migration --output /path/to/output
migration-tools/rollback-tools/verify.py --rollback /path/to/rollback --expected /path/to/expected --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, database-schemas/ for schema definitions
- **Provides**: Migration capabilities to all system components
- **Integrates with:** backup-systems/ for backup and recovery during migration
- **Serves**: System evolution and data transformation needs

## Implementation Guidelines
1. **Safety first** - always backup before migration and support rollback
2. **Incremental migration** - support step-by-step migration with validation
3. **Data integrity** - ensure data integrity and consistency throughout migration
4. **Performance awareness** - optimize for large datasets and minimal downtime
5. **Comprehensive validation** - validate migration results and verify data integrity