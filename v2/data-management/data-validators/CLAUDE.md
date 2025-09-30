# Data Validators

## Purpose
Data validation and integrity checking tools for ensuring data quality and consistency.

## Role in System
The **data quality assurance engine** that validates data integrity, enforces business rules, and ensures data consistency across the system.

## What This Directory Contains
- **schema-validators/**: Schema validation and structure checking
- **business-rule-validators/**: Business rule validation and enforcement
- **integrity-checkers/**: Data integrity and consistency checking
- **format-validators/**: Data format validation and normalization
- **quality-scanners/**: Data quality assessment and scoring
- **duplicate-detectors/**: Duplicate detection and data deduplication
- **constraint-enforcers/**: Constraint enforcement and data correction

## What This Directory Should NOT Contain
- **Storage engine logic** - belongs in storage-engines/
- **Schema definitions** - belongs in database-schemas/
- **Backup logic** - belongs in backup-systems/
- **Migration logic** - belongs in migration-tools/

## CLI Interface
```bash
# Schema validation
data-validators/schema-validators/validate.py --data /path/to/data.json --schema /path/to/schema.json --output /path/to/output
data-validators/schema-validators/check-structure.py --data /path/to/data --schema /path/to/schema --output /path/to/output
data-validators/schema-validators/test-types.py --data /path/to/data.json --types /path/to/types.json --output /path/to/output

# Business rule validation
data-validators/business-rule-validators/validate.py --data /path/to/data.json --rules /path/to/rules.json --output /path/to/output
data-validators/business-rule-validators/enforce.py --data /path/to/data.json --rules /path/to/rules.json --output /path/to/output
data-validators/business-rule-validators/test.py --data /path/to/data.json --rules /path/to/rules.json --output /path/to/output

# Integrity checking
data-validators/integrity-checkers/check.py --data /path/to/data --constraints /path/to/constraints.json --output /path/to/output
data-validators/integrity-checkers/verify.py --data /path/to/data --relationships /path/to/relationships.json --output /path/to/output
data-validators/integrity-checkers/scan.py --database /path/to/database --output /path/to/output

# Format validation
data-validators/format-validators/validate.py --data /path/to/data --format json --output /path/to/output
data-validators/format-validators/normalize.py --data /path/to/data --format json --output /path/to/output
data-validators/format-validators/convert.py --data /path/to/data --from-format csv --to-format json --output /path/to/output

# Quality scanning
data-validators/quality-scanners/scan.py --data /path/to/data --metrics completeness,accuracy,consistency --output /path/to/output
data-validators/quality-scanners/score.py --data /path/to/data --criteria /path/to/criteria.json --output /path/to/output
data-validators/quality-scanners/report.py --data /path/to/data --output /path/to/output

# Duplicate detection
data-validators/duplicate-detectors/find.py --data /path/to/data --fields "field1,field2" --output /path/to/output
data-validators/duplicate-detectors/merge.py --data /path/to/data --duplicates /path/to/duplicates.json --output /path/to/output
data-validators/duplicate-detectors/remove.py --data /path/to/data --duplicates /path/to/duplicates.json --output /path/to/output

# Constraint enforcement
data-validators/constraint-enforcers/enforce.py --data /path/to/data --constraints /path/to/constraints.json --output /path/to/output
data-validators/constraint-enforcers/correct.py --data /path/to/data --constraints /path/to/constraints.json --output /path/to/output
data-validators/constraint-enforcers/validate.py --data /path/to/data --constraints /path/to/constraints.json --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, database-schemas/ for schema definitions
- **Provides**: Data validation services to storage-engines/ and migration-tools/
- **Integrates with:** monitoring/ for data quality metrics and alerts
- **Serves**: Data quality assurance and validation systems

## Implementation Guidelines
1. **Comprehensive validation** - validate structure, format, business rules, and integrity
2. **Automated detection** - automatically detect data quality issues and anomalies
3. **Corrective actions** - provide mechanisms to correct identified issues
4. **Performance awareness** - optimize validation for large datasets
5. **Reporting** - provide detailed validation reports and quality scores