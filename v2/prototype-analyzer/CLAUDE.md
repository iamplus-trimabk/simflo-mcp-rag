# Prototype Analyzer Step - Step 2 of the SimFlo Figma-to-RAG Pipeline

## <¯ Purpose

The Prototype Analyzer step analyzes component catalogs and screen specifications to generate interaction flows, user journeys, and comprehensive test scenarios. This step transforms static design artifacts into dynamic interaction patterns that can be used for automated testing and user experience validation.

## =å Input/Output

### Input
- **Primary Input**: Component catalog JSON file from figma-analyzer
- **Secondary Input**: Screen set JSON file from figma-analyzer
- **Format**: JSON files conforming to ComponentCatalog and ScreenSet schemas
- **Example**: `./output/component-catalog.json`, `./output/screen-set.json`

### Output
1. **Interaction Flows** (`interaction-flows.json`)
   - User interaction flows between screens
   - Component interaction patterns
   - Navigation relationships
   - User journey classifications

2. **Test Scenarios** (`test-scenarios.json` + `test-scenarios/*.md`)
   - Comprehensive E2E test scenarios
   - Individual markdown test files
   - Test data requirements
   - Success criteria and validation steps

3. **Navigation Graph** (`navigation-graph.json`)
   - Complete navigation map
   - User journey groupings
   - Screen relationship visualization

4. **Component Interactions** (`component-interactions.json`)
   - Component-specific interaction patterns
   - Interaction types and expected outcomes
   - Component relationship mappings

5. **Analysis Metadata** (`prototype-analysis-metadata.json`)
   - Processing statistics and summary
   - Error and warning messages
   - File metadata and timestamps

## <× Architecture

### Core Classes

#### `PrototypeAnalyzer`
Main orchestrator class that coordinates the analysis process.

**Key Methods:**
- `analyze_prototype(component_catalog_path, screen_set_path, output_dir)` - Main entry point
- `_load_component_catalog(path)` - Load and validate component catalog
- `_load_screen_set(path)` - Load and validate screen set
- `_save_results(result, output_dir)` - Save analysis results to files

#### `InteractionFlowAnalyzer`
Analyzes component interactions and generates flow maps.

**Key Methods:**
- `generate_interaction_flows()` - Create all interaction flows
- `_build_navigation_graph()` - Build navigation relationships
- `_analyze_component_interactions()` - Analyze component patterns
- `_create_authentication_flow()` - Generate login/logout flows
- `_create_task_management_flows()` - Generate task-related flows

#### `TestScenarioGenerator`
Generates comprehensive test scenarios from interaction flows.

**Key Methods:**
- `generate_test_scenarios()` - Create all test scenarios
- `_create_primary_scenario(flow)` - Create success path scenarios
- `_create_error_scenarios(flow)` - Create error handling scenarios
- `_create_edge_case_scenarios(flow)` - Create edge case scenarios
- `_create_cross_functional_scenarios()` - Create multi-flow scenarios

#### `InteractionFlow`
Data class representing a user interaction flow.

**Fields:**
- `id: str` - Unique flow identifier
- `name: str` - Human-readable flow name
- `description: str` - Detailed flow description
- `start_screen: str` - Starting screen ID
- `end_screen: str` - Ending screen ID
- `interactions: List[Dict]` - Step-by-step interactions
- `user_journey_type: UserJourneyType` - Journey classification
- `components_involved: List[str]` - Component IDs in flow
- `estimated_duration: int` - Estimated duration in seconds

## = Interaction Flow Generation

### User Journey Types

#### Authentication Flows
- **Login Flow**: Email input ’ Password input ’ Login button ’ Home screen
- **Signup Flow**: Registration form ’ Account creation ’ Home screen
- **Logout Flow**: Logout action ’ Login screen

#### Task Management Flows
- **View Tasks**: Home screen ’ Task list ’ Task details
- **Create Task**: Add task screen ’ Form input ’ Save ’ Home screen
- **Edit Task**: Task details ’ Edit form ’ Save ’ Updated view
- **Delete Task**: Task details ’ Delete confirmation ’ Removal

#### Navigation Flows
- **Bottom Navigation**: Tab switching between main sections
- **Drill-down Navigation**: List ’ Detail ’ Related items
- **Breadcrumbs Navigation**: Hierarchical path traversal

#### Data Entry Flows
- **Form Submission**: Input fields ’ Validation ’ Submit ’ Confirmation
- **Search/Filter**: Search input ’ Results ’ Refinement ’ Selection
- **Multi-step Forms**: Step progression with validation and navigation

### Component Interaction Analysis

#### Interactive Components
- **Buttons**: Click actions with variants and states
- **Links/Tabs**: Navigation triggers with active states
- **Toggles/Switches**: State changes with immediate feedback

#### Form Components
- **Input Fields**: Text entry with validation and formatting
- **Select/Dropdowns**: Option selection with search capabilities
- **Checkboxes/Radio**: Multiple/Single selection with grouping
- **Textareas**: Multi-line text with character limits

#### Layout Components
- **Cards**: Tappable containers with content preview
- **Lists**: Scrollable collections with item actions
- **Grids**: Responsive layouts with item interactions

#### Navigation Components
- **Navigation Bars**: Tab-based navigation with active states
- **Menus**: Hierarchical navigation with sub-menus
- **Breadcrumbs**: Path navigation with parent links

## >ê Test Scenario Generation

### Scenario Types

#### Primary Success Path Scenarios
- **Happy Path**: Expected user journey with all interactions succeeding
- **Critical Path**: Essential business workflows
- **User Goals**: Task completion from user perspective

#### Error Handling Scenarios
- **Invalid Input**: Form validation with error messages
- **Authentication Failures**: Invalid credentials, expired sessions
- **Network Errors**: Connection issues, timeout handling
- **Missing Data**: Empty states, unavailable resources

#### Edge Case Scenarios
- **Performance**: Load time testing, memory usage
- **Accessibility**: Keyboard navigation, screen reader compatibility
- **Mobile**: Touch interactions, gesture support, responsive design
- **Browser Compatibility**: Cross-browser functionality

#### Cross-Functional Scenarios
- **End-to-End Journeys**: Complete user workflows across multiple screens
- **Data Persistence**: State management across navigation
- **Integration**: Multiple component interactions
- **User Experience**: Flow usability and consistency

### Test Scenario Structure

#### Test Steps
Each test scenario contains structured steps with:
- **Actions**: Specific user interactions (click, type, navigate)
- **Validations**: Expected outcomes and assertions
- **Preconditions**: Required state before step execution
- **Postconditions**: Expected state after step completion

#### Test Data
Scenarios include comprehensive test data:
- **User Credentials**: Authentication test data (marked as sensitive)
- **Sample Content**: Realistic data for form inputs and interactions
- **Edge Cases**: Boundary values and special characters
- **Error Data**: Invalid inputs for validation testing

#### Success Criteria
Each scenario defines clear success criteria:
- **Functional Requirements**: All interactions complete successfully
- **Navigation**: Correct screen transitions and flow completion
- **Data Integrity**: Data is properly saved and retrieved
- **User Experience**: No errors, appropriate feedback, responsive behavior

## =ñ Navigation Graph Analysis

### Graph Construction
The navigation graph represents all possible user paths:
- **Nodes**: Screens/pages in the application
- **Edges**: Navigation relationships and user actions
- **Weights**: Interaction complexity and importance
- **Paths**: Complete user journeys from entry to completion

### Logical Flow Detection
The system identifies logical navigation patterns:
- **Authentication Flow**: Login ’ Main Application
- **Task Flow**: List ’ Detail ’ Edit/Action ’ Back
- **Onboarding Flow**: Welcome ’ Setup ’ Main Application
- **Error Recovery**: Error ’ Resolution ’ Resume Flow

### Flow Analysis Metrics
- **Connectivity**: Screen accessibility and reachability
- **Depth**: Maximum navigation steps from entry point
- **Breadth**: Number of available paths from each screen
- **Critical Paths**: Essential flows for core functionality

## =' Usage

### Command Line Interface

```bash
# Basic usage
python v2/prototype-analyzer/main.py \
  --catalog ./output/component-catalog.json \
  --screens ./output/screen-set.json \
  --output ./output/

# With strict validation
python v2/prototype-analyzer/main.py \
  -c component-catalog.json \
  -s screen-set.json \
  -o ./output/ \
  --strict

# With verbose logging
python v2/prototype-analyzer/main.py \
  --catalog ./output/component-catalog.json \
  --screens ./output/screen-set.json \
  --output ./output/ \
  --verbose

# Combined options
python v2/prototype-analyzer/main.py \
  -c ./output/component-catalog.json \
  -s ./output/screen-set.json \
  -o ./analysis-output/ \
  --strict \
  --verbose
```

### Programmatic Usage

```python
from pathlib import Path
from v2.prototype_analyzer.main import PrototypeAnalyzer

# Create analyzer
analyzer = PrototypeAnalyzer(strict_validation=True)

# Analyze prototype
result = analyzer.analyze_prototype(
    component_catalog_path="./output/component-catalog.json",
    screen_set_path="./output/screen-set.json",
    output_dir="./analysis-output/"
)

# Access results
flows = result.interaction_flows
scenarios = result.test_scenarios
navigation_graph = result.navigation_graph
user_journeys = result.user_journeys
```

## ™ Configuration

### Validation Modes
- **Standard Mode**: Warnings are logged but don't cause failure
- **Strict Mode**: Warnings cause validation failure (use `--strict`)

### Logging Levels
- **Default**: INFO level logging
- **Verbose**: DEBUG level logging (use `--verbose`)

### Output Configuration
- **JSON Files**: Structured data for programmatic consumption
- **Markdown Files**: Human-readable test documentation
- **Metadata**: Processing statistics and analysis summary

## >ê Testing and Validation

### Input Validation
The analyzer validates inputs against pipeline schemas:
- **Component Catalog**: Component definitions, instances, and relationships
- **Screen Set**: Screen specifications, navigation flows, and component instances
- **Cross-References**: Consistency between components and screen usage

### Output Validation
Generated outputs are validated against schemas:
- **Test Scenarios**: Complete scenario structure and required fields
- **Interaction Flows**: Proper flow definition and component references
- **Navigation Graph**: Valid screen references and relationship consistency

### Integration Testing
```bash
# Test with figma-analyzer outputs
python v2/figma-analyzer/main.py examples/sample-figma-data.json ./test-output/
python v2/prototype-analyzer/main.py \
  --catalog ./test-output/component-catalog.json \
  --screens ./test-output/screen-set.json \
  --output ./test-output/

# Validate generated outputs
python v2/common/validation.py validate \
  --file ./test-output/interaction-flows.json \
  --schema InteractionFlows
```

## = Error Handling

### Common Errors

#### File Not Found
```
FileNotFoundError: Component catalog file not found: path/to/component-catalog.json
```
**Solution**: Ensure file paths are correct and files exist from figma-analyzer output

#### Schema Validation Errors
```
ValueError: Component catalog validation failed: [...]
```
**Solution**: Check input file format and ensure it conforms to ComponentCatalog schema

#### Missing Components
```
Component instances without definitions: ['component_button_primary']
```
**Solution**: Ensure all component instances have corresponding definitions

#### Navigation Issues
```
Navigation to unknown screen: missing_screen
```
**Solution**: Verify all navigation references correspond to defined screens

### Warnings

#### Missing Navigation Flows
When screens exist but have no navigation relationships defined, the system:
- Logs warnings about missing flows
- Attempts to create logical navigation based on common patterns
- Generates minimal test scenarios based on available data

#### Empty Component Categories
If component categories have no instances:
- Logs warnings about potentially unused components
- Continues analysis with available components
- Notes limitations in generated test coverage

#### Ambiguous Relationships
When component relationships are unclear:
- Logs warnings about relationship ambiguity
- Makes reasonable assumptions about interaction patterns
- Documents assumptions in analysis metadata

## =Ê Performance Characteristics

### Processing Time
Typical processing times for different project sizes:
- **Small** (d 10 screens, d 20 components): < 2 seconds
- **Medium** (11-50 screens, 21-100 components): 2-10 seconds
- **Large** (51+ screens, 100+ components): 10+ seconds

### Memory Usage
Memory consumption scales with:
- **Component Catalog**: Component definitions and instances
- **Screen Set**: Screen specifications and navigation flows
- **Generated Scenarios**: Number and complexity of test scenarios
- **Navigation Graph**: Screen relationship complexity

### Output Size
Generated output files typically:
- **Interaction Flows**: 10-50 KB depending on project complexity
- **Test Scenarios JSON**: 50-500 KB with comprehensive test data
- **Test Scenarios Markdown**: 100-1000 KB of human-readable documentation
- **Navigation Graph**: 5-20 KB of relationship data

## =' Integration with Pipeline

### Input Requirements
- **Component Catalog**: Valid JSON from figma-analyzer step
- **Screen Set**: Complete screen specifications with navigation data
- **Schema Compliance**: Inputs must validate against pipeline schemas
- **Cross-Reference Integrity**: Components and screens must reference correctly

### Output Format
- **Schema Compliance**: All outputs conform to pipeline schemas
- **Consistent Structure**: Standardized JSON and markdown formats
- **Metadata**: Complete traceability and processing information
- **Error Reporting**: Detailed error and warning documentation

### Dependencies
- **common.schemas**: Schema definitions for validation
- **common.validation**: Validation utilities
- **figma-analyzer outputs**: Required input data
- **Standard library**: json, pathlib, logging, argparse, datetime

### Downstream Usage
Generated outputs are designed for:
- **test-generator**: E2E test creation from scenarios
- **rag-system**: Documentation and knowledge base creation
- **ai-assistant**: Code review and improvement suggestions
- **Quality Assurance**: Test planning and execution

## =€ Best Practices

### Input Preparation
1. **Complete Figma Analysis**: Ensure figma-analyzer completes successfully
2. **Component Coverage**: Verify all UI components are properly defined
3. **Navigation Completeness**: Include all screen relationships and flows
4. **Validation**: Run input validation before prototype analysis

### Analysis Optimization
1. **Clear Component Naming**: Use descriptive names for better interaction detection
2. **Consistent Patterns**: Follow consistent design patterns for flow generation
3. **Navigation Mapping**: Explicitly define navigation relationships
4. **Component Categorization**: Properly categorize components for interaction analysis

### Output Utilization
1. **Test Scenario Review**: Review generated scenarios for completeness
2. **Flow Validation**: Verify interaction flows match expected user behavior
3. **Integration Testing**: Use outputs in downstream pipeline steps
4. **Documentation**: Leverage markdown files for test planning

## =È Future Enhancements

### Planned Features
- **Machine Learning**: Intelligent flow pattern recognition
- **A/B Testing Support**: Generate test scenarios for multiple design variants
- **Accessibility Integration**: Enhanced accessibility testing scenarios
- **Performance Testing**: Load testing scenario generation
- **Internationalization**: Multi-language test scenario support

### Extension Points
- **Custom Flow Generators**: Plugin system for domain-specific flows
- **Test Scenario Templates**: Customizable scenario patterns
- **Integration Adapters**: Connect to external test management systems
- **Analysis Rules**: Custom flow analysis and validation rules

---

**Step 2 of 9** - Prototype Analyzer transforms static design artifacts into comprehensive interaction flows and test scenarios for automated testing and user experience validation.