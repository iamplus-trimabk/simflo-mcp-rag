# Figma Analyzer Step - Step 1 of the SimFlo Figma-to-RAG Pipeline

## <¯ Purpose

The Figma Analyzer step processes Figma-like data structures to extract design tokens, component definitions, and screen specifications. This is the first step in the pipeline that transforms raw design data into structured artifacts for downstream processing.

## =Ë Input/Output

### Input
- **Primary Input**: Figma JSON file (simulated Figma API response)
- **Format**: JSON file with Figma-like structure
- **Example**: `examples/sample-figma-data.json`

### Output
1. **Design Tokens** (`design-tokens.json`)
   - Color tokens with semantic categorization
   - Typography tokens with font properties
   - Spacing tokens with scale values
   - Shadow/effect tokens
   - Border radius tokens

2. **Component Catalog** (`component-catalog.json`)
   - Component definitions with properties
   - Component variants and states
   - Component instances and usage
   - Component relationships

3. **Screen Specifications** (`screen-specs/`)
   - Individual screen JSON files
   - Layout grids and responsive breakpoints
   - Component instances on screens
   - Navigation relationships

4. **Analysis Metadata** (`analysis-metadata.json`)
   - Processing statistics
   - Error and warning messages
   - File metadata and timestamps

## <× Architecture

### Core Classes

#### `FigmaAnalyzer`
Main orchestrator class that coordinates the analysis process.

**Key Methods:**
- `analyze_figma_file(input_path, output_dir)` - Main entry point
- `_save_results(result, output_dir)` - Save analysis results
- `_validate_outputs(output_dir)` - Validate generated files

#### `FigmaDataParser`
Handles parsing of Figma data structures and extraction of artifacts.

**Key Methods:**
- `parse_figma_data(figma_data)` - Parse complete Figma structure
- `_extract_design_tokens(figma_data)` - Extract design tokens
- `_extract_component_catalog(figma_data)` - Extract component definitions
- `_extract_screen_set(figma_data, component_catalog)` - Extract screen specifications

#### `FigmaAnalysisResult`
Data class containing all analysis results and metadata.

**Fields:**
- `design_tokens: DesignTokenSet`
- `component_catalog: ComponentCatalog`
- `screen_set: ScreenSet`
- `metadata: Dict[str, Any]`
- `processing_time: float`
- `errors: List[str]`
- `warnings: List[str]`

## <¨ Design Token Extraction

### Color Tokens
Extracted from Figma color styles with automatic categorization:
- **Primary**: Brand colors (primary blue, etc.)
- **Secondary**: Secondary brand colors
- **Semantic**: Success, error, warning colors
- **Neutral**: Gray scale and base colors

### Typography Tokens
Extracted from Figma text styles:
- **Font Family**: Inter, system fonts, etc.
- **Font Size**: Pixel values from style definitions
- **Font Weight**: 100-900 scale values
- **Line Height**: Unitless or percentage values
- **Letter Spacing**: Pixel values for spacing

### Spacing Tokens
Generated from common design scales:
- **Scale**: 4px, 8px, 16px, 24px, 32px, 48px, 64px
- **Categories**: Margin, padding, gap
- **Units**: Pixels (px) with consistent scale

### Shadow Tokens
Extracted from Figma effect styles:
- **Drop Shadows**: Box shadows for elevation
- **Color Conversion**: RGB to hex conversion
- **Properties**: Offset, blur, spread, opacity

## >é Component Analysis

### Component Types
Automatically categorized based on naming patterns:
- **Interactive**: Buttons, inputs, controls
- **Form**: Input fields, forms, validation
- **Layout**: Cards, containers, panels
- **Navigation**: Menus, tabs, navigation bars
- **Display**: Icons, avatars, images

### Component Properties
Extracted based on component type and structure:

#### Button Components
- `variant`: primary, secondary, outline
- `size`: sm, md, lg
- `text`: Button label content
- `disabled`: Boolean state

#### Input Components
- `placeholder`: Placeholder text
- `value`: Current input value
- `type`: text, email, password, search

#### Card Components
- `title`: Card title text
- `description`: Card description
- `priority`: low, medium, high

### Component Variants
Support for component sets with multiple states:
- **Default**: Normal state
- **Hover**: Mouse hover state
- **Pressed**: Active/pressed state
- **Disabled**: Disabled state

## =ñ Screen Specification

### Screen Types
Automatically detected based on dimensions:
- **Mobile App**: Width d 450px
- **Web Page**: 450px < Width < 1200px
- **Desktop App**: Width e 1200px

### Layout Grid
Standard responsive grid system:
- **Columns**: 12-column grid
- **Gutter**: 16px spacing between columns
- **Margin**: 24px outer margins
- **Max Width**: 1200px container limit

### Responsive Breakpoints
Standard device breakpoints:
- **Mobile**: d 767px
- **Tablet**: 768px - 1023px
- **Desktop**: e 1024px

### Component Instances
Mapped from Figma instances with:
- **Position**: X, Y coordinates
- **Size**: Width, height dimensions
- **Properties**: Component-specific values
- **Hierarchy**: Parent-child relationships

## =' Usage

### Command Line Interface

```bash
# Basic usage
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./output/

# With strict validation
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./output/ --strict

# With verbose logging
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./output/ --verbose

# Combined options
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./output/ --strict --verbose
```

### Programmatic Usage

```python
from pathlib import Path
from v2.figma_analyzer.main import FigmaAnalyzer

# Create analyzer
analyzer = FigmaAnalyzer(strict_validation=False)

# Analyze Figma file
result = analyzer.analyze_figma_file(
    input_path=Path("examples/sample-figma-data.json"),
    output_dir=Path("./output/")
)

# Access results
design_tokens = result.design_tokens
component_catalog = result.component_catalog
screen_set = result.screen_set
```

## ™ Configuration

### Validation Modes
- **Standard Mode**: Warnings are logged but don't cause failure
- **Strict Mode**: Warnings cause validation failure (use `--strict`)

### Logging Levels
- **Default**: INFO level logging
- **Verbose**: DEBUG level logging (use `--verbose`)

## >ê Testing

### Unit Tests
```bash
# Run all tests
python -m pytest v2/tests/test_figma_analyzer.py

# Run with coverage
python -m pytest v2/tests/test_figma_analyzer.py --cov=v2/figma-analyzer
```

### Integration Tests
```bash
# Test with sample data
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./test-output/

# Validate outputs
python v2/common/validation.py validate --file ./test-output/design-tokens.json --schema DesignTokenSet
```

## =¨ Error Handling

### Common Errors

#### File Not Found
```
FileNotFoundError: Input file not found: path/to/file.json
```
**Solution**: Ensure input file path is correct and file exists

#### Validation Errors
```
CustomValidationError: Schema validation failed: design-tokens.json
```
**Solution**: Check input data format and structure

#### JSON Decode Errors
```
json.JSONDecodeError: Invalid JSON format
```
**Solution**: Validate JSON syntax and encoding

### Warnings

#### Missing Components
Component instances without matching definitions are logged as warnings but don't cause failure.

#### Unrecognized Styles
Unknown style types are logged as warnings and skipped during processing.

#### Empty Collections
Empty design token categories or component lists generate warnings.

## =Ê Performance

### Processing Time
Typical processing times for different file sizes:
- **Small** (< 1MB): < 1 second
- **Medium** (1-5MB): 1-3 seconds
- **Large** (> 5MB): 3+ seconds

### Memory Usage
Memory scales with file complexity:
- **Design Tokens**: Minimal memory impact
- **Components**: Moderate memory usage
- **Screens**: Highest memory usage

## = Debugging

### Enable Debug Logging
```bash
python v2/figma-analyzer/main.py input.json output/ --verbose
```

### Check Output Validation
```bash
python v2/common/validation.py validate --file output/design-tokens.json --schema DesignTokenSet
```

### Inspect Generated Files
```bash
# View design tokens
cat output/design-tokens.json | jq '.colors[] | .name, .value'

# View components
cat output/component-catalog.json | jq '.components[] | .name, .category'

# View screens
ls output/screen-specs/
```

## = Integration with Pipeline

### Input Requirements
- Expects Figma-like JSON structure
- Requires valid JSON format
- UTF-8 encoding required

### Output Format
- All outputs conform to pipeline schemas
- JSON format with consistent structure
- Metadata for traceability

### Dependencies
- `common.schemas`: Schema definitions
- `common.validation`: Validation utilities
- `pydantic`: Data validation
- Standard library: json, pathlib, logging, argparse

## =È Future Enhancements

### Planned Features
- **Real Figma API Integration**: Connect to actual Figma API
- **Advanced Token Detection**: Smarter categorization algorithms
- **Component Relationship Mapping**: Enhanced dependency analysis
- **Custom Property Extraction**: User-defined property patterns
- **Performance Optimization**: Faster processing for large files

### Extension Points
- **Custom Token Extractors**: Plugin system for new token types
- **Component Property Mappers**: Configurable property extraction
- **Screen Type Detectors**: Custom screen classification rules
- **Validation Rules**: Custom validation logic

---

**Step 1 of 9** - Figma Analyzer transforms raw design data into structured pipeline artifacts.