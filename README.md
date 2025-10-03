# SimFlo Figma-to-RAG Pipeline

**A comprehensive 9-step pipeline that transforms Figma designs into production-ready applications with automated testing and AI-powered code review.**

## 🎯 Pipeline Overview

This pipeline takes Figma URLs and converts them into:
- Design tokens (Tailwind/NativeWind)
- Component catalog (shadcn/gluestack)
- Page implementations with navigation
- Playwright test suites
- RAG knowledge bases (docs, code, tests)
- AI-powered code review and improvement

## 🏗️ Pipeline Architecture

```
v2/
├── figma-analyzer/          # Step 1: Figma URL → design tokens, components, screens
├── prototype-analyzer/      # Step 2: Prototype flows → interactions & test scenarios
├── token-converter/         # Step 3: Design tokens → Tailwind/NativeWind definitions
├── component-generator/     # Step 4: Component catalog → shadcn/gluestack components
├── page-generator/          # Step 5: Screen specs → page implementations
├── test-generator/          # Step 6: Test scenarios → Playwright test suites
├── test-runner/             # Step 7: Execute E2E tests & provide demo
├── rag-system/              # Step 8: Create doc/code/test RAG knowledge bases
├── ai-assistant/            # Step 9: AI code review & improvement suggestions
├── common/                  # Shared utilities and types
├── tests/                   # Pipeline test suite
└── docs/                    # Pipeline documentation
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Node.js (for component generation and testing)
node --version

# Figma API token
export FIGMA_TOKEN="your_figma_token_here"
```

### Installation

```bash
# Clone repository
git clone <repository-url>
cd simflo-mcp-rag

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for component generation)
npm install

# Make scripts executable
chmod +x v2/*/main.py
```

## 📋 Pipeline Steps

### Step 1: Figma Analyzer
**Input**: Figma URL + Token
**Output**: Design tokens, component catalog, screen specifications

```bash
python3 v2/figma-analyzer/main.py \
  --url "https://www.figma.com/file/your-design" \
  --token $FIGMA_TOKEN \
  --output ./output/
```

**Generates**:
- `design-tokens.json` - Colors, typography, spacing, shadows
- `component-catalog.json` - Component definitions with props
- `screen-specs/` - Individual screen/page specifications

### Step 2: Prototype Analyzer
**Input**: Component catalog + Figma prototype links
**Output**: Interaction flows + test scenarios

```bash
python3 v2/prototype-analyzer/main.py \
  --catalog ./output/component-catalog.json \
  --figma-url "https://www.figma.com/file/your-design" \
  --output ./output/
```

**Generates**:
- `interaction-flows.json` - Click actions, navigation, data flow
- `test-scenarios/` - User journey test cases in Markdown

### Step 3: Token Converter
**Input**: Design tokens
**Output**: Tailwind/NativeWind definitions

```bash
python3 v2/token-converter/main.py \
  --tokens ./output/design-tokens.json \
  --framework tailwind \
  --output ./output/tailwind-config.js
```

**Supports**:
- Tailwind CSS configuration
- NativeWind (React Native) configuration
- Custom design system generation

### Step 4: Component Generator
**Input**: Component catalog + design tokens
**Output**: shadcn/gluestack components

```bash
python3 v2/component-generator/main.py \
  --catalog ./output/component-catalog.json \
  --library shadcn \
  --output ./components/
```

**Generates**:
- React components with TypeScript
- Component stories/documentation
- User stories (2-3 per component)

### Step 5: Page Generator
**Input**: Screen specifications + components
**Output**: Complete page implementations

```bash
python3 v2/page-generator/main.py \
  --screens ./output/screen-specs/ \
  --components ./components/ \
  --output ./pages/
```

**Generates**:
- React pages with routing
- Event handlers and hooks
- User story implementations

### Step 6: Test Generator
**Input**: Test scenarios + pages
**Output**: Playwright test suites

```bash
python3 v2/test-generator/main.py \
  --scenarios ./output/test-scenarios/ \
  --pages ./pages/ \
  --output ./tests/
```

**Generates**:
- Playwright E2E test files
- Test data fixtures
- Test configuration

### Step 7: Test Runner
**Input**: Test suite
**Output**: Test results + demo

```bash
python3 v2/test-runner/main.py \
  --tests ./tests/ \
  --demo ./demo/
```

**Provides**:
- Automated test execution
- Test report generation
- Interactive demo of generated application

### Step 8: RAG System
**Input**: Docs, code, tests
**Output**: RAG knowledge bases

```bash
python3 v2/rag-system/main.py \
  --docs ./output/ \
  --code ./components/ ./pages/ \
  --tests ./tests/ \
  --output ./rag-bases/
```

**Creates**:
- `doc-rag/` - Documentation knowledge base
- `code-rag/` - Code implementation knowledge base
- `test-rag/` - Test scenario knowledge base

### Step 9: AI Assistant
**Input**: RAG bases + code
**Output**: Code review + improvement suggestions

```bash
python3 v2/ai-assistant/main.py \
  --rag-bases ./rag-bases/ \
  --code ./components/ ./pages/ \
  --output ./ai-review/
```

**Provides**:
- Automated code quality analysis
- Improvement recommendations
- Refactoring suggestions

## 🔧 Configuration

### Environment Variables

```bash
# Figma API
FIGMA_TOKEN="your_figma_token"
FIGMA_TEAM_ID="your_team_id"

# Output Configuration
OUTPUT_ROOT="./output"
COMPONENT_ROOT="./components"
PAGE_ROOT="./pages"

# AI Configuration (optional)
OPENAI_API_KEY="your_openai_key"  # For advanced AI features
```

### Pipeline Configuration

Create `pipeline-config.json`:

```json
{
  "figma": {
    "extract_tokens": true,
    "extract_components": true,
    "extract_screens": true
  },
  "components": {
    "library": "shadcn",
    "framework": "react",
    "typescript": true
  },
  "testing": {
    "framework": "playwright",
    "generate_e2e": true,
    "generate_unit": false
  },
  "rag": {
    "chunk_size": 1000,
    "overlap": 200,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
  }
}
```

## 📊 Output Structure

```
output/
├── design-tokens.json          # Design system tokens
├── component-catalog.json      # Component definitions
├── interaction-flows.json      # User interaction flows
├── tailwind-config.js          # Tailwind configuration
├── screen-specs/               # Individual screen specifications
├── test-scenarios/             # User journey test cases
├── components/                 # Generated React components
├── pages/                      # Generated page implementations
├── tests/                      # Playwright test suites
├── rag-bases/                  # RAG knowledge bases
└── ai-review/                  # AI analysis and suggestions
```

## 🧪 Testing

```bash
# Run all pipeline tests
python3 -m pytest v2/tests/ -v

# Run individual component tests
python3 -m pytest v2/tests/test_figma_analyzer.py -v
python3 -m pytest v2/tests/test_component_generator.py -v

# Integration test - full pipeline
python3 v2/tests/test_full_pipeline.py
```

## 🎯 Use Cases

### 1. Rapid Prototyping
- Design in Figma → Generate working application in minutes
- Test user flows before development
- Iterate quickly on designs

### 2. Component Library Generation
- Extract design system from Figma
- Generate consistent component library
- Ensure design-to-code alignment

### 3. Automated Testing
- Generate comprehensive E2E tests
- Test all user journeys from prototypes
- Validate implementation matches design

### 4. Documentation Generation
- Auto-generate documentation from designs
- Create living documentation that stays in sync
- Enable AI-powered code assistance

## 🤝 Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create feature branch** for pipeline improvements
3. **Add tests** for new functionality
4. **Update documentation** in relevant `CLAUDE.md` files
5. **Run full test suite** ensuring no regressions
6. **Submit pull request** with detailed description

### Adding New Pipeline Steps

1. Create directory in `v2/new-step/`
2. Add `__init__.py`, `main.py`, `CLAUDE.md`
3. Implement step with standard input/output interface
4. Add tests in `v2/tests/`
5. Update pipeline documentation

## 📄 License

This project demonstrates automated Figma-to-code generation with comprehensive testing and AI assistance. See LICENSE file for details.

---

**SimFlo Figma-to-RAG Pipeline** - Transform designs into production applications with confidence.