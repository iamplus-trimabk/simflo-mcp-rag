"""
Common schemas for the SimFlo Figma-to-RAG pipeline.

This module defines all the data contracts between pipeline steps using Pydantic models.
Each schema includes validation rules, examples, and JSON serialization capabilities.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Literal, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path
import json


class BaseSchema(BaseModel):
    """Base schema with common fields for all pipeline data models."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0.0", description="Schema version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    def to_json_file(self, file_path: Path) -> None:
        """Save schema to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.dict(), f, indent=2, default=str)

    @classmethod
    def from_json_file(cls, file_path: Path) -> "BaseSchema":
        """Load schema from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls(**data)


# =============================================================================
# DESIGN TOKEN SCHEMAS
# =============================================================================

class ColorToken(BaseSchema):
    """
    Represents a color design token extracted from Figma.

    Example:
    {
        "name": "primary-500",
        "value": "#3B82F6",
        "type": "color",
        "category": "primary",
        "description": "Primary brand color",
        "variants": {
            "light": "#60A5FA",
            "dark": "#2563EB"
        }
    }
    """
    name: str = Field(..., description="Token name (e.g., 'primary-500')")
    value: str = Field(...,
                       pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', description="Hex color value")
    type: Literal["color"] = Field(default="color", description="Token type")
    category: Literal["primary", "secondary", "semantic", "neutral",
                      "feedback"] = Field(..., description="Color category")
    description: Optional[str] = Field(None, description="Token description")
    variants: Dict[str, str] = Field(
        default_factory=dict, description="Color variants (light/dark, states)")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Opacity value")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Token name cannot be empty')
        return v.strip().lower().replace(' ', '-')


class TypographyToken(BaseSchema):
    """
    Represents a typography design token.

    Example:
    {
        "name": "heading-1",
        "font_family": "Inter",
        "font_size": 32,
        "font_weight": 700,
        "line_height": 1.2,
        "letter_spacing": 0,
        "category": "heading"
    }
    """
    name: str = Field(..., description="Token name")
    font_family: str = Field(..., description="Font family name")
    font_size: Union[int, float] = Field(..., gt=0, description="Font size in pixels")
    font_weight: Literal[100, 200, 300, 400, 500, 600, 700,
                         800, 900] = Field(..., description="Font weight")
    line_height: Union[float, str] = Field(..., description="Line height (unitless or percentage)")
    letter_spacing: Union[int, float] = Field(default=0, description="Letter spacing in pixels")
    category: Literal["heading", "body", "caption", "label",
                      "custom"] = Field(..., description="Typography category")
    text_transform: Optional[Literal["none", "uppercase", "lowercase",
                                     "capitalize"]] = Field("none", description="Text transform")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Token name cannot be empty')
        return v.strip().lower().replace(' ', '-')


class SpacingToken(BaseSchema):
    """
    Represents a spacing design token.

    Example:
    {
        "name": "spacing-lg",
        "value": 24,
        "unit": "px",
        "category": "margin",
        "scale_position": 4
    }
    """
    name: str = Field(..., description="Token name")
    value: Union[int, float] = Field(..., ge=0, description="Spacing value")
    unit: Literal["px", "rem", "em", "%"] = Field(default="px", description="Unit type")
    category: Literal["margin", "padding", "gap",
                      "custom"] = Field(..., description="Spacing category")
    scale_position: Optional[int] = Field(None, description="Position in spacing scale")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Token name cannot be empty')
        return v.strip().lower().replace(' ', '-')


class ShadowToken(BaseSchema):
    """
    Represents a shadow/effect design token.

    Example:
    {
        "name": "shadow-md",
        "offset_x": 0,
        "offset_y": 4,
        "blur": 6,
        "spread": 0,
        "color": "#000000",
        "opacity": 0.1,
        "type": "drop-shadow"
    }
    """
    name: str = Field(..., description="Token name")
    offset_x: Union[int, float] = Field(default=0, description="Horizontal offset")
    offset_y: Union[int, float] = Field(default=0, description="Vertical offset")
    blur: Union[int, float] = Field(default=0, ge=0, description="Blur radius")
    spread: Union[int, float] = Field(default=0, description="Spread radius")
    color: str = Field(...,
                       pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', description="Shadow color")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Shadow opacity")
    type: Literal["drop-shadow", "inner-shadow",
                  "text-shadow"] = Field(default="drop-shadow", description="Shadow type")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Token name cannot be empty')
        return v.strip().lower().replace(' ', '-')


class BorderRadiusToken(BaseSchema):
    """
    Represents a border radius design token.

    Example:
    {
        "name": "radius-md",
        "value": 8,
        "unit": "px",
        "corners": "all"
    }
    """
    name: str = Field(..., description="Token name")
    value: Union[int, float] = Field(..., ge=0, description="Border radius value")
    unit: Literal["px", "rem", "em", "%"] = Field(default="px", description="Unit type")
    corners: Literal["all", "top-left", "top-right", "bottom-left",
                     "bottom-right"] = Field(default="all", description="Which corners to apply")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Token name cannot be empty')
        return v.strip().lower().replace(' ', '-')


class DesignTokenSet(BaseSchema):
    """
    Collection of all design tokens for a design system.

    Example:
    {
        "colors": [...],
        "typography": [...],
        "spacing": [...],
        "shadows": [...],
        "border_radius": [...]
    }
    """
    colors: List[ColorToken] = Field(default_factory=list, description="Color tokens")
    typography: List[TypographyToken] = Field(default_factory=list, description="Typography tokens")
    spacing: List[SpacingToken] = Field(default_factory=list, description="Spacing tokens")
    shadows: List[ShadowToken] = Field(default_factory=list, description="Shadow/effect tokens")
    border_radius: List[BorderRadiusToken] = Field(
        default_factory=list, description="Border radius tokens")

    def get_token_by_name(self, token_type: str, name: str) -> Optional[BaseModel]:
        """Get a token by type and name."""
        token_map = {
            "color": self.colors,
            "typography": self.typography,
            "spacing": self.spacing,
            "shadow": self.shadows,
            "border_radius": self.border_radius
        }

        tokens = token_map.get(token_type, [])
        for token in tokens:
            if token.name == name:
                return token
        return None


# =============================================================================
# COMPONENT CATALOG SCHEMAS
# =============================================================================

class ComponentProperty(BaseSchema):
    """
    Represents a component property definition.

    Example:
    {
        "name": "variant",
        "type": "string",
        "default_value": "primary",
        "required": true,
        "description": "Button variant style",
        "allowed_values": ["primary", "secondary", "outline"]
    }
    """
    name: str = Field(..., description="Property name")
    type: Literal["string", "number", "boolean", "array",
                  "object", "enum"] = Field(..., description="Property type")
    default_value: Any = Field(None, description="Default property value")
    required: bool = Field(default=False, description="Whether property is required")
    description: Optional[str] = Field(None, description="Property description")
    allowed_values: Optional[List[Any]] = Field(None, description="Allowed values for enum type")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class ComponentVariant(BaseSchema):
    """
    Represents a component variant definition.

    Example:
    {
        "name": "primary",
        "properties": {
            "variant": "primary",
            "size": "md"
        },
        "description": "Primary button variant"
    }
    """
    name: str = Field(..., description="Variant name")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Variant property values")
    description: Optional[str] = Field(None, description="Variant description")
    preview_url: Optional[str] = Field(None, description="Preview image URL")


class ComponentInstance(BaseSchema):
    """
    Represents an instance of a component in a design.

    Example:
    {
        "id": "instance_123",
        "component_id": "button",
        "name": "Submit Button",
        "properties": {
            "text": "Submit",
            "variant": "primary",
            "size": "md"
        },
        "position": {"x": 100, "y": 200},
        "size": {"width": 120, "height": 40}
    }
    """
    id: str = Field(..., description="Unique instance ID")
    component_id: str = Field(..., description="ID of the component this instance uses")
    name: str = Field(..., description="Instance name")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Instance property values")
    position: Dict[str, Union[int, float]] = Field(
        default_factory=dict, description="Position coordinates")
    size: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Width and height")
    children: List[str] = Field(default_factory=list, description="Child instance IDs")
    parent_id: Optional[str] = Field(None, description="Parent instance ID")


class ComponentDefinition(BaseSchema):
    """
    Represents a component definition extracted from Figma.

    Example:
    {
        "id": "button",
        "name": "Button",
        "type": "component",
        "category": "interactive",
        "description": "Interactive button component",
        "properties": [...],
        "variants": [...],
        "children_component_ids": [],
        "usage_examples": [...]
    }
    """
    id: str = Field(..., description="Unique component ID")
    name: str = Field(..., description="Component name")
    type: Literal["component", "frame", "group",
                  "instance"] = Field(..., description="Component type")
    category: Literal["interactive", "layout", "display", "form", "navigation",
                      "feedback"] = Field(..., description="Component category")
    description: Optional[str] = Field(None, description="Component description")
    properties: List[ComponentProperty] = Field(
        default_factory=list, description="Component properties")
    variants: List[ComponentVariant] = Field(default_factory=list, description="Component variants")
    children_component_ids: List[str] = Field(
        default_factory=list, description="Child component IDs")
    usage_examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    figma_node_id: Optional[str] = Field(None, description="Figma node ID")
    figma_file_key: Optional[str] = Field(None, description="Figma file key")


class ComponentCatalog(BaseSchema):
    """
    Complete catalog of all components extracted from a Figma file.

    Example:
    {
        "components": [...],
        "instances": [...],
        "relationships": {...}
    }
    """
    components: List[ComponentDefinition] = Field(
        default_factory=list, description="Component definitions")
    instances: List[ComponentInstance] = Field(
        default_factory=list, description="Component instances")
    relationships: Dict[str, List[str]] = Field(
        default_factory=dict, description="Component relationships")

    def get_component_by_id(self, component_id: str) -> Optional[ComponentDefinition]:
        """Get component definition by ID."""
        for component in self.components:
            if component.id == component_id:
                return component
        return None

    def get_instances_by_component_id(self, component_id: str) -> List[ComponentInstance]:
        """Get all instances of a component."""
        return [instance for instance in self.instances if instance.component_id == component_id]


# =============================================================================
# SCREEN SPECIFICATION SCHEMAS
# =============================================================================

class LayoutGrid(BaseSchema):
    """
    Represents layout grid specifications.

    Example:
    {
        "type": "columns",
        "columns": 12,
        "gutter_width": 16,
        "margin": 24,
        "max_width": 1200
    }
    """
    type: Literal["columns", "flex", "absolute"] = Field(..., description="Grid type")
    columns: Optional[int] = Field(None, description="Number of columns")
    gutter_width: Optional[Union[int, float]] = Field(None, description="Space between columns")
    margin: Optional[Union[int, float]] = Field(None, description="Grid margin")
    max_width: Optional[Union[int, float]] = Field(None, description="Maximum container width")


class ResponsiveBreakpoint(BaseSchema):
    """
    Represents a responsive breakpoint.

    Example:
    {
        "name": "tablet",
        "min_width": 768,
        "max_width": 1023,
        "description": "Tablet devices"
    }
    """
    name: str = Field(..., description="Breakpoint name")
    min_width: Optional[Union[int, float]] = Field(None, description="Minimum width in pixels")
    max_width: Optional[Union[int, float]] = Field(None, description="Maximum width in pixels")
    description: Optional[str] = Field(None, description="Breakpoint description")


class NavigationRelationship(BaseSchema):
    """
    Represents navigation relationships between screens.

    Example:
    {
        "from_screen_id": "home",
        "to_screen_id": "profile",
        "trigger": "click",
        "trigger_element_id": "profile_button",
        "animation_type": "slide_right"
    }
    """
    from_screen_id: str = Field(..., description="Source screen ID")
    to_screen_id: str = Field(..., description="Target screen ID")
    trigger: Literal["click", "tap", "swipe", "auto",
                     "form_submit"] = Field(..., description="Navigation trigger")
    trigger_element_id: Optional[str] = Field(None, description="Element that triggers navigation")
    animation_type: Optional[str] = Field(None, description="Transition animation type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Navigation parameters")


class ScreenSpecification(BaseSchema):
    """
    Represents a screen/page specification extracted from Figma.

    Example:
    {
        "id": "home_screen",
        "name": "Home Screen",
        "type": "mobile_app",
        "layout_grid": {...},
        "breakpoints": [...],
        "component_instances": [...],
        "navigation_flows": [...],
        "figma_frame_id": "frame_123"
    }
    """
    id: str = Field(..., description="Unique screen ID")
    name: str = Field(..., description="Screen name")
    type: Literal["mobile_app", "web_page", "desktop_app",
                  "modal", "overlay"] = Field(..., description="Screen type")
    layout_grid: Optional[LayoutGrid] = Field(None, description="Layout grid specification")
    breakpoints: List[ResponsiveBreakpoint] = Field(
        default_factory=list, description="Responsive breakpoints")
    component_instances: List[ComponentInstance] = Field(
        default_factory=list, description="Component instances on screen")
    navigation_flows: List[NavigationRelationship] = Field(
        default_factory=list, description="Navigation relationships")
    figma_frame_id: Optional[str] = Field(None, description="Figma frame ID")
    figma_file_key: Optional[str] = Field(None, description="Figma file key")
    background_color: Optional[str] = Field(None, description="Background color")
    status_bar_style: Optional[Literal["default", "hidden", "light", "dark"]] = Field(
        None, description="Status bar style")


class ScreenSet(BaseSchema):
    """
    Collection of all screen specifications for a project.

    Example:
    {
        "screens": [...],
        "navigation_graph": {...},
        "entry_point": "home_screen"
    }
    """
    screens: List[ScreenSpecification] = Field(
        default_factory=list, description="All screen specifications")
    navigation_graph: Dict[str, List[str]] = Field(
        default_factory=dict, description="Navigation graph")
    entry_point: Optional[str] = Field(None, description="Entry point screen ID")

    def get_screen_by_id(self, screen_id: str) -> Optional[ScreenSpecification]:
        """Get screen specification by ID."""
        for screen in self.screens:
            if screen.id == screen_id:
                return screen
        return None


# =============================================================================
# TEST SCENARIO SCHEMAS
# =============================================================================

class TestAction(BaseSchema):
    """
    Represents a single test action.

    Example:
    {
        "action_type": "click",
        "target": {"type": "element", "selector": "#submit-button"},
        "parameters": {"timeout": 5000},
        "description": "Click the submit button"
    }
    """
    action_type: Literal["click", "tap", "type", "select", "navigate",
                         "wait", "assert", "scroll"] = Field(..., description="Action type")
    target: Dict[str, str] = Field(..., description="Action target (element, screen, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    description: str = Field(..., description="Action description")
    expected_result: Optional[str] = Field(None, description="Expected result of action")
    timeout: Optional[int] = Field(None, description="Action timeout in milliseconds")


class TestStep(BaseSchema):
    """
    Represents a test step with actions and validations.

    Example:
    {
        "step_number": 1,
        "description": "Navigate to login page and enter credentials",
        "actions": [...],
        "validations": [...],
        "preconditions": [...]
    }
    """
    step_number: int = Field(..., ge=1, description="Step number")
    description: str = Field(..., description="Step description")
    actions: List[TestAction] = Field(default_factory=list, description="Test actions")
    validations: List[TestAction] = Field(default_factory=list, description="Validation actions")
    preconditions: List[str] = Field(
        default_factory=list, description="Preconditions for this step")
    postconditions: List[str] = Field(
        default_factory=list, description="Postconditions after this step")


class TestDataRequirement(BaseSchema):
    """
    Represents test data requirements.

    Example:
    {
        "type": "user_credentials",
        "description": "Valid user login credentials",
        "data": {"username": "test@example.com", "password": "password123"},
        "sensitive": true
    }
    """
    type: str = Field(..., description="Data type")
    description: str = Field(..., description="Data description")
    data: Dict[str, Any] = Field(default_factory=dict, description="Test data")
    sensitive: bool = Field(default=False, description="Whether data is sensitive")
    source: Optional[str] = Field(None, description="Data source (file, API, etc.)")


class TestScenario(BaseSchema):
    """
    Represents a complete test scenario for user interaction flows.

    Example:
    {
        "id": "user_login_flow",
        "name": "User Login Flow",
        "description": "Test complete user login journey",
        "category": "authentication",
        "priority": "high",
        "steps": [...],
        "test_data": [...],
        "success_criteria": [...]
    }
    """
    id: str = Field(..., description="Unique scenario ID")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    category: Literal["authentication", "navigation", "form_interaction", "data_display",
                      "error_handling", "custom"] = Field(..., description="Test category")
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium", description="Test priority")
    tags: List[str] = Field(default_factory=list, description="Test tags")
    steps: List[TestStep] = Field(default_factory=list, description="Test steps")
    test_data: List[TestDataRequirement] = Field(
        default_factory=list, description="Test data requirements")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    dependencies: List[str] = Field(default_factory=list, description="Test dependencies")

    @field_validator('steps')
    @classmethod
    def validate_steps_order(cls, v):
        if len(v) == 0:
            raise ValueError('Test scenario must have at least one step')

        step_numbers = [step.step_number for step in v]
        if step_numbers != sorted(step_numbers):
            raise ValueError('Step numbers must be in sequential order')

        if step_numbers != list(range(1, len(v) + 1)):
            raise ValueError('Step numbers must start at 1 and be sequential')

        return v


class TestSuite(BaseSchema):
    """
    Collection of test scenarios for a project.

    Example:
    {
        "name": "E2E Test Suite",
        "description": "End-to-end test scenarios",
        "scenarios": [...],
        "configuration": {...}
    }
    """
    name: str = Field(..., description="Test suite name")
    description: str = Field(..., description="Test suite description")
    scenarios: List[TestScenario] = Field(default_factory=list, description="Test scenarios")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Test configuration")
    tags: List[str] = Field(default_factory=list, description="Suite tags")

    def get_scenarios_by_category(self, category: str) -> List[TestScenario]:
        """Get scenarios by category."""
        return [scenario for scenario in self.scenarios if scenario.category == category]

    def get_scenarios_by_priority(self, priority: str) -> List[TestScenario]:
        """Get scenarios by priority."""
        return [scenario for scenario in self.scenarios if scenario.priority == priority]


# =============================================================================
# RAG CONTENT SCHEMAS
# =============================================================================

class ContentChunk(BaseSchema):
    """
    Represents a chunk of content for the RAG knowledge base.

    Example:
    {
        "id": "chunk_123",
        "content_type": "documentation",
        "content": "This is a documentation chunk about React components...",
        "metadata": {...},
        "source_info": {...},
        "embedding_vector": [...],
        "tags": ["react", "components", "documentation"]
    }
    """
    id: str = Field(..., description="Unique chunk ID")
    content_type: Literal["documentation", "code", "test", "configuration",
                          "comment", "example"] = Field(..., description="Content type")
    content: str = Field(..., description="Content text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    source_info: Dict[str, Any] = Field(default_factory=dict, description="Source information")
    embedding_vector: Optional[List[float]] = Field(
        None, description="Embedding vector (placeholder for now)")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    language: Optional[str] = Field(None, description="Content language")
    quality_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Content quality score")

    @field_validator('content')
    @classmethod
    def validate_content_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Content cannot be empty')
        return v.strip()


class SourceInformation(BaseSchema):
    """
    Represents source information for RAG content.

    Example:
    {
        "file_path": "/src/components/Button.tsx",
        "file_type": "typescript",
        "line_numbers": [1, 50],
        "function_name": "Button",
        "class_name": null,
        "repository": "simflo-components",
        "commit_hash": "abc123",
        "last_modified": "2024-01-15T10:30:00Z"
    }
    """
    file_path: str = Field(..., description="Source file path")
    file_type: Optional[str] = Field(None, description="File type/extension")
    line_numbers: Optional[Tuple[int, int]] = Field(None, description="Line number range")
    function_name: Optional[str] = Field(None, description="Function name")
    class_name: Optional[str] = Field(None, description="Class name")
    repository: Optional[str] = Field(None, description="Repository name")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    last_modified: Optional[datetime] = Field(None, description="Last modification timestamp")
    author: Optional[str] = Field(None, description="Content author")


class ContentCategory(BaseSchema):
    """
    Represents a content category for organization.

    Example:
    {
        "name": "react_components",
        "description": "React component implementations",
        "parent_category": null,
        "subcategories": ["buttons", "forms", "layout"],
        "metadata": {"framework": "react"}
    }
    """
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    parent_category: Optional[str] = Field(None, description="Parent category name")
    subcategories: List[str] = Field(default_factory=list, description="Subcategory names")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Category metadata")


class RAGKnowledgeBase(BaseSchema):
    """
    Complete RAG knowledge base for a project.

    Example:
    {
        "project_name": "SimFlo Components",
        "version": "1.0.0",
        "chunks": [...],
        "categories": [...],
        "metadata": {...},
        "configuration": {...}
    }
    """
    project_name: str = Field(..., description="Project name")
    version: str = Field(..., description="Knowledge base version")
    chunks: List[ContentChunk] = Field(default_factory=list, description="Content chunks")
    categories: List[ContentCategory] = Field(
        default_factory=list, description="Content categories")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Knowledge base metadata")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="RAG configuration")

    def get_chunks_by_type(self, content_type: str) -> List[ContentChunk]:
        """Get chunks by content type."""
        return [chunk for chunk in self.chunks if chunk.content_type == content_type]

    def get_chunks_by_tag(self, tag: str) -> List[ContentChunk]:
        """Get chunks by tag."""
        return [chunk for chunk in self.chunks if tag in chunk.tags]

    def search_chunks(self, query: str) -> List[ContentChunk]:
        """Simple text search in chunks (placeholder for vector search)."""
        query_lower = query.lower()
        results = []

        for chunk in self.chunks:
            if (query_lower in chunk.content.lower()
                    or any(query_lower in tag.lower() for tag in chunk.tags)):
                results.append(chunk)

        return results


# =============================================================================
# PIPELINE EXECUTION SCHEMAS
# =============================================================================

class PipelineStepResult(BaseSchema):
    """
    Represents the result of a pipeline step execution.

    Example:
    {
        "step_name": "figma-analyzer",
        "status": "success",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T10:02:30Z",
        "input_files": [...],
        "output_files": [...],
        "errors": [],
        "warnings": [],
        "metadata": {...}
    }
    """
    step_name: str = Field(..., description="Pipeline step name")
    status: Literal["success", "error", "warning",
                    "skipped"] = Field(..., description="Execution status")
    start_time: datetime = Field(default_factory=datetime.now, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    input_files: List[str] = Field(default_factory=list, description="Input file paths")
    output_files: List[str] = Field(default_factory=list, description="Output file paths")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")

    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class PipelineExecutionReport(BaseSchema):
    """
    Complete pipeline execution report.

    Example:
    {
        "pipeline_name": "figma-to-rag",
        "version": "1.0.0",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T10:15:00Z",
        "steps": [...],
        "summary": {...}
    }
    """
    pipeline_name: str = Field(..., description="Pipeline name")
    version: str = Field(..., description="Pipeline version")
    start_time: datetime = Field(default_factory=datetime.now, description="Pipeline start time")
    end_time: Optional[datetime] = Field(None, description="Pipeline end time")
    steps: List[PipelineStepResult] = Field(default_factory=list, description="Step results")
    configuration: Dict[str, Any] = Field(
        default_factory=dict, description="Pipeline configuration")

    @property
    def total_duration(self) -> Optional[float]:
        """Get total pipeline duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def successful_steps(self) -> List[PipelineStepResult]:
        """Get successful step results."""
        return [step for step in self.steps if step.status == "success"]

    @property
    def failed_steps(self) -> List[PipelineStepResult]:
        """Get failed step results."""
        return [step for step in self.steps if step.status == "error"]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if not self.steps:
            return 0.0
        return len(self.successful_steps) / len(self.steps) * 100


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class PipelineStepType(str, Enum):
    """Pipeline step types."""
    FIGMA_ANALYZER = "figma-analyzer"
    PROTOTYPE_ANALYZER = "prototype-analyzer"
    TOKEN_CONVERTER = "token-converter"
    COMPONENT_GENERATOR = "component-generator"
    PAGE_GENERATOR = "page-generator"
    TEST_GENERATOR = "test-generator"
    TEST_RUNNER = "test-runner"
    RAG_SYSTEM = "rag-system"
    AI_ASSISTANT = "ai-assistant"


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"


class FrameworkType(str, Enum):
    """Supported frameworks."""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    FLUTTER = "flutter"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_example_design_tokens() -> DesignTokenSet:
    """Create example design tokens for testing."""
    return DesignTokenSet(
        colors=[
            ColorToken(
                name="primary-500",
                value="#3B82F6",
                category="primary",
                description="Primary brand color",
                variants={"light": "#60A5FA", "dark": "#2563EB"}
            ),
            ColorToken(
                name="gray-500",
                value="#6B7280",
                category="neutral",
                description="Neutral gray color"
            )
        ],
        typography=[
            TypographyToken(
                name="heading-1",
                font_family="Inter",
                font_size=32,
                font_weight=700,
                line_height=1.2,
                category="heading"
            )
        ],
        spacing=[
            SpacingToken(
                name="spacing-md",
                value=16,
                unit="px",
                category="margin",
                scale_position=3
            )
        ]
    )


def create_example_component() -> ComponentDefinition:
    """Create example component definition for testing."""
    return ComponentDefinition(
        id="button",
        name="Button",
        type="component",
        category="interactive",
        description="Interactive button component",
        properties=[
            ComponentProperty(
                name="variant",
                type="string",
                default_value="primary",
                required=True,
                description="Button variant style",
                allowed_values=["primary", "secondary", "outline"]
            ),
            ComponentProperty(
                name="size",
                type="string",
                default_value="md",
                required=True,
                description="Button size",
                allowed_values=["sm", "md", "lg"]
            ),
            ComponentProperty(
                name="disabled",
                type="boolean",
                default_value=False,
                required=False,
                description="Disable the button"
            )
        ],
        variants=[
            ComponentVariant(
                name="primary",
                properties={"variant": "primary", "size": "md"},
                description="Primary button variant"
            ),
            ComponentVariant(
                name="secondary",
                properties={"variant": "secondary", "size": "md"},
                description="Secondary button variant"
            )
        ]
    )


def create_example_test_scenario() -> TestScenario:
    """Create example test scenario for testing."""
    return TestScenario(
        id="button_click_test",
        name="Button Click Test",
        description="Test button click functionality",
        category="form_interaction",
        priority="high",
        steps=[
            TestStep(
                step_number=1,
                description="Navigate to page with button",
                actions=[
                    TestAction(
                        action_type="navigate",
                        target={"type": "url", "selector": "/test-page"},
                        description="Navigate to test page"
                    )
                ]
            ),
            TestStep(
                step_number=2,
                description="Click the primary button",
                actions=[
                    TestAction(
                        action_type="click",
                        target={"type": "element", "selector": "#primary-button"},
                        description="Click primary button",
                        timeout=5000
                    )
                ],
                validations=[
                    TestAction(
                        action_type="assert",
                        target={"type": "element", "selector": ".success-message"},
                        description="Verify success message appears"
                    )
                ]
            )
        ],
        success_criteria=[
            "Button is clickable",
            "Success message appears after click",
            "No JavaScript errors occur"
        ]
    )
