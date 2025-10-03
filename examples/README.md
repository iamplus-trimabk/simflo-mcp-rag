# SimFlo Figma-to-RAG Pipeline - Example Dataset

This directory contains a comprehensive example dataset that demonstrates the complete capabilities of the SimFlo Figma-to-RAG Pipeline. The dataset represents a realistic mobile task management application called "TaskFlow" and includes all the necessary data to test every step of the pipeline.

## 📁 File Structure

```
examples/
├── README.md                          # This documentation
├── sample-figma-data.json             # Simulated Figma API response
├── sample-design-tokens.json          # Design system tokens
├── sample-component-catalog.json      # Component definitions and instances
├── sample-screen-specs/               # Screen layout specifications
│   ├── login-screen.json
│   ├── home-screen.json
│   └── task-detail-screen.json
└── sample-test-scenarios/             # User journey test scenarios
    ├── user-login-flow.md
    ├── task-management-flow.md
    └── navigation-flows.md
```

## 🎯 About the Example Application

**TaskFlow** is a mobile task management application with the following features:

- **Authentication**: User login and registration
- **Task Management**: Create, view, edit, delete, and complete tasks
- **Task Organization**: Priority levels, due dates, tags, and assignees
- **Navigation**: Bottom navigation bar with home, tasks, calendar, and profile sections
- **User Interface**: Modern, responsive design with consistent components

The example data represents a typical user journey through the application, from logging in to managing their daily tasks.

## 📋 Data Files Overview

### 1. sample-figma-data.json
**Purpose**: Simulates the complete response from Figma API for a design file
**Size**: 1.2MB (comprehensive design data)
**Contents**:
- Document structure with multiple pages/screens
- Design styles (colors, typography, effects)
- Component definitions with variants and properties
- Component instances with specific configurations
- Prototype flows and navigation relationships
- Figma-specific metadata and node IDs

**Key Features**:
- 12 color styles with variants
- 6 typography styles
- 4 shadow effects
- 5 main components (Button, Input, Task Card, Navigation Bar, Modal)
- 3 screens with complete layouts
- 3 user flow prototypes
- Realistic design tokens and spacing

### 2. sample-design-tokens.json
**Purpose**: Extracted and structured design tokens from the Figma data
**Size**: 45KB (comprehensive design system)
**Contents**:
- **Colors**: 12 color tokens (primary, secondary, feedback, neutral)
- **Typography**: 9 typography tokens (headings, body, captions, buttons)
- **Spacing**: 7 spacing tokens following a consistent scale
- **Shadows**: 4 shadow tokens for elevation and depth
- **Border Radius**: 6 border radius tokens for consistent rounding

**Token Structure**:
- All tokens include proper metadata (description, variants, opacity)
- Tokens follow naming conventions (category-specific-name)
- Includes validation rules and constraints
- Compatible with major design token formats

### 3. sample-component-catalog.json
**Purpose**: Complete catalog of all components extracted from the design
**Size**: 180KB (comprehensive component library)
**Contents**:
- **6 Component Definitions**: Button, Input Field, Task Card, Navigation Bar, Modal, Badge
- **9 Component Instances**: Specific usage examples throughout the app
- **Component Properties**: Detailed property definitions with validation
- **Component Variants**: Multiple states and configurations per component
- **Usage Examples**: Real-world implementation examples
- **Component Relationships**: Parent-child and dependency mappings

**Component Features**:
- Interactive components with multiple states
- Form components with validation
- Display components with data binding
- Navigation components with routing
- Comprehensive prop validation and typing

### 4. sample-screen-specs/ (Directory)
**Purpose**: Individual screen specifications extracted from Figma frames
**Total Size**: 125KB (3 detailed screen specifications)

#### login-screen.json
- Authentication screen with email/password fields
- Form validation and error states
- Navigation to signup and password recovery
- Responsive layout with proper spacing
- Accessibility considerations

#### home-screen.json
- Main dashboard with task list
- Scrollable content with multiple task cards
- Bottom navigation integration
- Header with date and greeting
- Priority badges and task indicators

#### task-detail-screen.json
- Detailed task information view
- Editable form fields with validation
- Date pickers and selection controls
- Action buttons for save/delete
- Rich form controls and user inputs

### 5. sample-test-scenarios/ (Directory)
**Purpose**: Comprehensive test scenarios for E2E testing
**Total Size**: 85KB (3 detailed test scenarios)

#### user-login-flow.md
- Complete authentication journey testing
- Form validation and error handling
- Security considerations and edge cases
- Performance and accessibility requirements
- Multiple test data scenarios (valid/invalid credentials)

#### task-management-flow.md
- Full CRUD operations testing
- Task creation, editing, and deletion
- Form validation and data persistence
- User interaction patterns and workflows
- Error handling and recovery scenarios

#### navigation-flows.md
- Complete navigation system testing
- Bottom navigation and deep linking
- Modal dialogs and overlay navigation
- Back navigation and state management
- Performance and accessibility testing

## 🔄 How Data Flows Through the Pipeline

The example data is designed to flow through all 9 pipeline steps:

1. **Step 1 - figma-analyzer**: Processes `sample-figma-data.json` → extracts design tokens, components, and screens
2. **Step 2 - prototype-analyzer**: Analyzes prototype flows → generates interaction scenarios
3. **Step 3 - token-converter**: Converts `sample-design-tokens.json` → framework-specific configurations
4. **Step 4 - component-generator**: Uses `sample-component-catalog.json` → generates React components
5. **Step 5 - page-generator**: Combines screen specs + components → creates React pages
6. **Step 6 - test-generator**: Uses test scenarios + screen flows → generates Playwright tests
7. **Step 7 - test-runner**: Executes generated tests → provides demo and validation
8. **Step 8 - rag-system**: Creates knowledge bases from all generated content
9. **Step 9 - ai-assistant**: Analyzes all artifacts → provides code review and improvements

## 🎨 Design System Overview

### Color Palette
- **Primary**: Blue (#3B82F6) with light/dark variants
- **Secondary**: Green (#10B981) for success states
- **Feedback**: Red (#EF4444) for errors, Yellow (#F59E0B) for warnings
- **Neutral**: Gray scale (#F3F4F6 to #111827) for text and backgrounds

### Typography
- **Font Family**: Inter (modern, clean sans-serif)
- **Headings**: Bold weights (600-700) with tight line height
- **Body**: Regular weight (400) with comfortable reading line height
- **Consistent scale**: 32px, 24px, 20px, 18px, 16px, 14px, 12px

### Spacing System
- **Scale**: 4px, 8px, 16px, 24px, 32px, 48px, 64px
- **Usage**: Consistent padding, margins, and gaps throughout
- **Ratio**: Each step is approximately 1.5x the previous size

### Component Design
- **Modern aesthetics**: Rounded corners, subtle shadows, clean lines
- **Consistent interactions**: Hover states, loading states, disabled states
- **Accessibility focus**: High contrast, clear focus indicators, semantic HTML

## 🧪 Testing Coverage

The example data provides comprehensive test coverage:

### Functional Testing
- ✅ User authentication flows
- ✅ Task CRUD operations
- ✅ Form validation and error handling
- ✅ Navigation and routing
- ✅ Data persistence and synchronization

### UI Testing
- ✅ Component rendering and state
- ✅ Responsive layouts
- ✅ Interactive elements and gestures
- ✅ Loading states and transitions
- ✅ Error states and recovery

### Integration Testing
- ✅ End-to-end user workflows
- ✅ Cross-screen data flow
- ✅ Component integration
- ✅ API integration (mocked)
- ✅ State management

### Performance Testing
- ✅ Navigation timing
- ✅ Component rendering performance
- ✅ Animation smoothness
- ✅ Memory usage
- ✅ Network request handling

## 🛠️ Usage Examples

### Running the Complete Pipeline
```bash
# Process the example data through all pipeline steps
python3 v2/figma-analyzer/main.py --input examples/sample-figma-data.json --output ./output/
python3 v2/prototype-analyzer/main.py --catalog ./output/component-catalog.json --output ./output/
python3 v2/token-converter/main.py --tokens ./output/design-tokens.json --output ./output/
python3 v2/component-generator/main.py --catalog ./output/component-catalog.json --output ./output/
python3 v2/page-generator/main.py --screens ./output/screen-specs/ --output ./output/
python3 v2/test-generator/main.py --scenarios ./output/test-scenarios/ --output ./output/
python3 v2/test-runner/main.py --tests ./output/tests/ --output ./output/
python3 v2/rag-system/main.py --docs ./output/ --code ./output/components/ --output ./output/
python3 v2/ai-assistant/main.py --rag-bases ./output/rag-bases/ --code ./output/components/ --output ./output/
```

### Validating Data Against Schemas
```bash
# Validate all example data against Pydantic schemas
python3 v2/common/validate-schemas.py \
  --figma examples/sample-figma-data.json \
  --tokens examples/sample-design-tokens.json \
  --components examples/sample-component-catalog.json \
  --screens examples/sample-screen-specs/ \
  --tests examples/sample-test-scenarios/
```

### Individual Component Testing
```bash
# Test specific components from the catalog
python3 v2/component-generator/main.py \
  --catalog examples/sample-component-catalog.json \
  --components button,task_card \
  --output ./components/
```

## 📊 Data Validation

All example data files are designed to be 100% compatible with the Pydantic schemas defined in `v2/common/schemas.py`:

- ✅ **sample-figma-data.json**: Validated against Figma-like response structure
- ✅ **sample-design-tokens.json**: Validates as DesignTokenSet
- ✅ **sample-component-catalog.json**: Validates as ComponentCatalog
- ✅ **sample-screen-specs/*.json**: Each validates as ScreenSpecification
- ✅ **sample-test-scenarios/*.md**: Follows TestScenario markdown format

## 🔧 Customization and Extension

### Adding New Components
1. Add component definition to `sample-component-catalog.json`
2. Create component instances in appropriate screen specs
3. Add test scenarios covering new component usage
4. Update design tokens if new styles are needed

### Adding New Screens
1. Create new JSON file in `sample-screen-specs/`
2. Define component instances and layout
3. Add navigation flows to/from the new screen
4. Create test scenarios for the new screen

### Modifying Design Tokens
1. Update `sample-design-tokens.json` with new tokens
2. Ensure components reference updated token names
3. Verify consistency across all files
4. Update test scenarios if colors/typography changed

## 📈 Performance Characteristics

The example dataset is optimized for realistic testing:

- **File Sizes**: Reasonable sizes for processing (1.2MB total)
- **Component Count**: Manageable number of components (6 main types)
- **Screen Complexity**: Realistic but not overwhelming (3 main screens)
- **Test Coverage**: Comprehensive but focused (3 main scenarios)
- **Processing Time**: Designed to complete pipeline in under 2 minutes

## 🎯 Learning Objectives

This example dataset demonstrates:

1. **Complete Pipeline Flow**: How data flows through all 9 pipeline steps
2. **Real-World Application**: How the pipeline handles a real mobile app design
3. **Design System Integration**: How design tokens, components, and screens work together
4. **Test Generation**: How user flows translate to automated tests
5. **Documentation Generation**: How RAG systems create searchable knowledge bases

## 🤝 Contributing

When extending or modifying the example dataset:

1. **Maintain Schema Compatibility**: Ensure all changes validate against existing schemas
2. **Keep Data Realistic**: Use realistic values that represent actual mobile apps
3. **Update Tests**: Keep test scenarios in sync with data changes
4. **Document Changes**: Update this README when adding new features
5. **Validate Pipeline**: Ensure the complete pipeline still processes the data

## 📞 Support

For questions about the example dataset:

1. Check the schema definitions in `v2/common/schemas.py`
2. Review the pipeline documentation in individual step CLAUDE.md files
3. Run validation scripts to check data integrity
4. Test individual pipeline steps with the example data
5. Check the main project README for general guidance

---

**Note**: This example dataset is designed specifically for testing and demonstrating the SimFlo Figma-to-RAG Pipeline capabilities. It represents a fictional application and should not be used for production purposes.