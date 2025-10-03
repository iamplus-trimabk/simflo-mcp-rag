# Task 9: Advanced API Documentation Generation with OpenAPI 3.1

## Modern OpenAPI 3.1 Specification Generation

### Comprehensive OpenAPI 3.1 Generator
```python
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class AdvancedOpenAPIGenerator:
    def __init__(self):
        self.spec = {
            "openapi": "3.1.0",
            "info": {
                "title": "Auto-Generated API Documentation",
                "version": "1.0.0",
                "description": "Comprehensive API documentation generated from source code analysis",
                "contact": {
                    "name": "API Team",
                    "email": "api@example.com"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [],
            "paths": {},
            "components": {
                "schemas": {},
                "responses": {},
                "parameters": {},
                "examples": {},
                "securitySchemes": {}
            },
            "tags": [],
            "security": []
        }

    def generate_from_analysis(self, api_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.1 spec from comprehensive API analysis."""

        # Set up servers
        self.setup_servers(api_analysis.get('servers', []))

        # Process all endpoints
        for endpoint in api_analysis.get('endpoints', []):
            self.add_endpoint(endpoint)

        # Add schema definitions
        if 'schemas' in api_analysis:
            self.add_schemas(api_analysis['schemas'])

        # Add security schemes
        if 'security' in api_analysis:
            self.add_security_schemes(api_analysis['security'])

        # Add tags
        self.generate_tags(api_analysis.get('endpoints', []))

        return self.spec

    def setup_servers(self, servers: List[Dict[str, str]]):
        """Configure API servers."""
        default_servers = [
            {
                "url": "http://localhost:3000",
                "description": "Development server"
            },
            {
                "url": "https://api.example.com",
                "description": "Production server"
            }
        ]

        self.spec["servers"] = servers or default_servers

    def add_endpoint(self, endpoint: Dict[str, Any]):
        """Add single endpoint with comprehensive details."""
        path = endpoint['path']
        method = endpoint['method'].lower()

        if path not in self.spec['paths']:
            self.spec['paths'][path] = {}

        operation = self.create_operation(endpoint)
        self.spec['paths'][path][method] = operation

    def create_operation(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive OpenAPI operation object."""
        operation = {
            "summary": endpoint.get('summary', f"{endpoint['method']} {endpoint['path']}"),
            "description": endpoint.get('description', ''),
            "operationId": self.generate_operation_id(endpoint),
            "tags": endpoint.get('tags', []),
            "parameters": self.generate_parameters(endpoint.get('parameters', [])),
            "responses": self.generate_responses(endpoint),
            "deprecated": endpoint.get('deprecated', False)
        }

        # Add request body if applicable
        if self.has_request_body(endpoint):
            operation["requestBody"] = self.generate_request_body(endpoint)

        # Add security requirements
        if endpoint.get('security'):
            operation["security"] = endpoint['security']

        # Add examples
        if endpoint.get('examples'):
            operation["examples"] = endpoint['examples']

        return operation

    def generate_operation_id(self, endpoint: Dict[str, Any]) -> str:
        """Generate unique operation ID."""
        method = endpoint['method'].lower()
        path = endpoint['path'].replace('/', '_').replace(':', '').replace('{', '').replace('}', '')
        function_name = endpoint.get('function_name', '')

        if function_name:
            return f"{method}_{function_name}"
        return f"{method}_{path}"

    def generate_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate OpenAPI parameter definitions."""
        openapi_params = []

        for param in parameters:
            openapi_param = {
                "name": param['name'],
                "in": param.get('in', 'query'),
                "description": param.get('description', ''),
                "required": param.get('required', False),
                "schema": self.generate_schema(param.get('type', 'string'), param)
            }

            # Add examples
            if 'example' in param:
                openapi_param["example"] = param['example']

            # Add validation
            if 'validation' in param:
                openapi_param["schema"].update(param['validation'])

            openapi_params.append(openapi_param)

        return openapi_params

    def generate_schema(self, type_str: str, param: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate OpenAPI schema from type information."""
        param = param or {}

        # Basic type mapping
        type_mapping = {
            'str': {'type': 'string'},
            'int': {'type': 'integer'},
            'float': {'type': 'number'},
            'bool': {'type': 'boolean'},
            'list': {'type': 'array'},
            'dict': {'type': 'object'},
            'datetime': {'type': 'string', 'format': 'date-time'},
            'date': {'type': 'string', 'format': 'date'},
            'email': {'type': 'string', 'format': 'email'},
            'url': {'type': 'string', 'format': 'uri'},
            'uuid': {'type': 'string', 'format': 'uuid'}
        }

        # Handle complex types
        if type_str.startswith('List[') or type_str.startswith('list['):
            inner_type = type_str.split('[')[1].split(']')[0]
            return {
                'type': 'array',
                'items': self.generate_schema(inner_type)
            }

        if type_str.startswith('Optional['):
            inner_type = type_str.split('[')[1].split(']')[0]
            schema = self.generate_schema(inner_type)
            schema['nullable'] = True
            return schema

        if type_str.startswith('Dict[') or type_str.startswith('dict['):
            return {
                'type': 'object',
                'additionalProperties': True
            }

        # Check for reference types
        if type_str.isupper() or '.' in type_str:  # Likely a model reference
            return {'$ref': f'#/components/schemas/{type_str}'}

        # Return basic type mapping
        return type_mapping.get(type_str.lower(), {'type': 'string'})

    def generate_responses(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response definitions."""
        responses = {
            "200": {
                "description": "Successful response",
                "content": self.generate_response_content(endpoint)
            }
        }

        # Add error responses
        error_responses = endpoint.get('error_responses', {})
        for status_code, error_info in error_responses.items():
            responses[str(status_code)] = {
                "description": error_info.get('description', f'Error {status_code}'),
                "content": {
                    "application/json": {
                        "schema": error_info.get('schema', {'$ref': '#/components/schemas/Error'})
                    }
                }
            }

        return responses

    def generate_response_content(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response content based on return type."""
        return_type = endpoint.get('return_type', 'object')

        content = {
            "application/json": {
                "schema": self.generate_schema(return_type)
            }
        }

        # Add examples
        if 'response_example' in endpoint:
            content["application/json"]["example"] = endpoint['response_example']

        return content
```

### Advanced Schema Extraction and Enhancement
```python
class SchemaEnhancer:
    def __init__(self):
        self.enhanced_schemas = {}
        self.relationships = {}

    def enhance_pydantic_schemas(self, pydantic_schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance Pydantic schemas with additional OpenAPI features."""
        enhanced = {}

        for schema_name, schema_info in pydantic_schemas.items():
            enhanced_schema = {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }

            # Process fields
            for field in schema_info.get('fields', []):
                field_schema = self.enhance_field(field)
                enhanced_schema["properties"][field['name']] = field_schema

                if not field.get('default') and field.get('required', True):
                    enhanced_schema["required"].append(field['name'])

            # Add validation
            if 'config' in schema_info:
                enhanced_schema.update(self.extract_config_validation(schema_info['config']))

            # Add examples
            if 'examples' in schema_info:
                enhanced_schema["example"] = schema_info['examples']

            enhanced[schema_name] = enhanced_schema

        return enhanced

    def enhance_field(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance individual field with comprehensive validation."""
        field_schema = self.generate_field_schema(field.get('type', 'str'))

        # Add constraints
        constraints = {}
        if 'min_length' in field:
            constraints['minLength'] = field['min_length']
        if 'max_length' in field:
            constraints['maxLength'] = field['max_length']
        if 'min_value' in field:
            constraints['minimum'] = field['min_value']
        if 'max_value' in field:
            constraints['maximum'] = field['max_value']
        if 'pattern' in field:
            constraints['pattern'] = field['pattern']

        field_schema.update(constraints)

        # Add description
        if field.get('description'):
            field_schema['description'] = field['description']

        # Add default value
        if field.get('default'):
            field_schema['default'] = field['default']

        # Add examples
        if field.get('example'):
            field_schema['example'] = field['example']

        return field_schema

    def extract_config_validation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract validation rules from Pydantic config."""
        validation = {}

        if config.get('str_strip_whitespace'):
            validation['string'] = validation.get('string', {})
            validation['string']['trim'] = True

        if config.get('validate_assignment'):
            validation['additionalProperties'] = False

        return validation

    def generate_field_schema(self, field_type: str) -> Dict[str, Any]:
        """Generate schema for individual field type."""
        type_mapping = {
            'str': {'type': 'string'},
            'int': {'type': 'integer'},
            'float': {'type': 'number'},
            'bool': {'type': 'boolean'},
            'datetime': {'type': 'string', 'format': 'date-time'},
            'email': {'type': 'string', 'format': 'email'},
            'url': {'type': 'string', 'format': 'uri'},
            'uuid': {'type': 'string', 'format': 'uuid'}
        }

        # Handle complex field types
        if field_type.startswith('List['):
            inner_type = field_type.split('[')[1].split(']')[0]
            return {
                'type': 'array',
                'items': self.generate_field_schema(inner_type)
            }

        if field_type.startswith('Optional['):
            inner_type = field_type.split('[')[1].split(']')[0]
            schema = self.generate_field_schema(inner_type)
            schema['nullable'] = True
            return schema

        # Check for model references
        if field_type[0].isupper() or '.' in field_type:
            return {'$ref': f'#/components/schemas/{field_type}'}

        return type_mapping.get(field_type.lower(), {'type': 'string'})
```

## Interactive Documentation Generation

### Swagger UI Integration
```python
class SwaggerUIGenerator:
    def __init__(self):
        self.swagger_config = {
            "dom_id": "#swagger-ui",
            "deepLinking": True,
            "presets": [
                "SwaggerUIBundle.presets.apis",
                "SwaggerUIStandalonePreset"
            ],
            "plugins": [
                "SwaggerUIBundle.plugins.DownloadUrl"
            ],
            "layout": "StandaloneLayout",
            "validatorUrl": None,
            "tryItOutEnabled": True,
            "requestInterceptor": "(request) => { console.log('Request:', request); return request; }",
            "responseInterceptor": "(response) => { console.log('Response:', response); return response; }"
        }

    def generate_swagger_html(self, openapi_spec: Dict[str, Any], output_file: str = "swagger.html"):
        """Generate Swagger UI HTML page."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
        .swagger-ui .topbar { display: none; }
        .custom-header {
            background: #4a90e2;
            color: white;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="custom-header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui-standalone-preset.js"></script>
    <script>
        const spec = {openapi_spec_json};
        const ui = SwaggerUIBundle({swagger_config_json});
    </script>
</body>
</html>
        """

        # Prepare config JSON
        config_json = json.dumps(self.swagger_config, indent=2)
        spec_json = json.dumps(openapi_spec, indent=2)

        # Replace placeholders
        html_content = html_template.format(
            title=openapi_spec['info']['title'],
            description=openapi_spec['info']['description'],
            openapi_spec_json=spec_json,
            swagger_config_json=config_json
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

    def generate_redoc_html(self, openapi_spec: Dict[str, Any], output_file: str = "redoc.html"):
        """Generate ReDoc HTML page."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; }
        .custom-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .custom-header h1 { margin: 0; font-size: 2.5em; }
        .custom-header p { margin: 10px 0 0 0; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="custom-header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    <redoc spec-url="{spec_url}"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>
        """

        html_content = html_template.format(
            title=openapi_spec['info']['title'],
            description=openapi_spec['info']['description'],
            spec_url=json.dumps(openapi_spec)
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file
```

### Advanced Markdown Documentation
```python
class AdvancedMarkdownGenerator:
    def __init__(self):
        self.template = """
# {title}

{description}

## Table of Contents

{toc}

---

{content}

---

## Generated Information

- **Generated on**: {generated_date}
- **Total Endpoints**: {total_endpoints}
- **API Version**: {api_version}
- **OpenAPI Version**: {openapi_version}
        """

    def generate_comprehensive_docs(self, openapi_spec: Dict[str, Any]) -> str:
        """Generate comprehensive markdown documentation."""

        # Generate table of contents
        toc = self.generate_toc(openapi_spec)

        # Generate content
        content = self.generate_content(openapi_spec)

        # Fill template
        markdown = self.template.format(
            title=openapi_spec['info']['title'],
            description=openapi_spec['info']['description'],
            toc=toc,
            content=content,
            generated_date=datetime.now().isoformat(),
            total_endpoints=len(self.get_all_operations(openapi_spec)),
            api_version=openapi_spec['info']['version'],
            openapi_version=openapi_spec['openapi']
        )

        return markdown

    def generate_toc(self, spec: Dict[str, Any]) -> str:
        """Generate table of contents."""
        toc = []
        toc.append("### Overview")
        toc.append("- [API Information](#api-information)")
        toc.append("- [Servers](#servers)")
        toc.append("- [Authentication](#authentication)")

        toc.append("\n### Endpoints")

        # Group by tags
        tag_groups = self.group_endpoints_by_tag(spec)
        for tag, endpoints in tag_groups.items():
            tag_anchor = tag.lower().replace(' ', '-')
            toc.append(f"- [{tag}](#{tag_anchor})")

            for endpoint in endpoints:
                path = endpoint['path']
                method = endpoint['method']
                endpoint_anchor = f"{method.lower()}-{path.replace('/', '-').replace(':', '')}"
                toc.append(f"  - {method.upper()} {path}")

        return '\n'.join(toc)

    def generate_content(self, spec: Dict[str, Any]) -> str:
        """Generate main documentation content."""
        content_parts = []

        # API Information
        content_parts.append(self.generate_api_info(spec))

        # Servers
        content_parts.append(self.generate_servers_section(spec))

        # Authentication
        content_parts.append(self.generate_auth_section(spec))

        # Schemas
        content_parts.append(self.generate_schemas_section(spec))

        # Endpoints
        content_parts.append(self.generate_endpoints_section(spec))

        return '\n\n---\n\n'.join(content_parts)

    def generate_api_info(self, spec: Dict[str, Any]) -> str:
        """Generate API information section."""
        info = spec['info']
        content = [
            "## API Information",
            f"**Title**: {info['title']}",
            f"**Version**: {info['version']}",
            f"**Description**: {info['description']}"
        ]

        if 'contact' in info:
            contact = info['contact']
            content.extend([
                f"**Contact**: {contact.get('name', '')} ({contact.get('email', '')})"
            ])

        if 'license' in info:
            license_info = info['license']
            content.extend([
                f"**License**: {license_info.get('name', '')} - {license_info.get('url', '')}"
            ])

        return '\n\n'.join(content)

    def generate_endpoints_section(self, spec: Dict[str, Any]) -> str:
        """Generate detailed endpoints documentation."""
        content = ["## API Endpoints"]

        # Group by tags
        tag_groups = self.group_endpoints_by_tag(spec)

        for tag, endpoints in tag_groups.items():
            content.append(f"\n### {tag}")

            for endpoint in endpoints:
                path = endpoint['path']
                method = endpoint['method']
                operation = endpoint['operation']

                content.append(f"\n#### {method.upper()} {path}")

                # Summary and description
                if operation.get('summary'):
                    content.append(f"**Summary**: {operation['summary']}")

                if operation.get('description'):
                    content.append(f"**Description**: {operation['description']}")

                # Parameters
                if operation.get('parameters'):
                    content.append("\n**Parameters**:")
                    for param in operation['parameters']:
                        required = " (required)" if param.get('required') else " (optional)"
                        content.append(f"- `{param['name']}` ({param['in']}){required}: {param.get('description', '')}")

                # Request body
                if operation.get('requestBody'):
                    content.append("\n**Request Body**:")
                    body = operation['requestBody']
                    content_content = body.get('content', {}).get('application/json', {})
                    if 'schema' in content_content:
                        content.append(f"- Schema: {json.dumps(content_content['schema'], indent=2)}")

                # Responses
                if operation.get('responses'):
                    content.append("\n**Responses**:")
                    for status, response in operation['responses'].items():
                        content.append(f"- **{status}**: {response.get('description', '')}")

                # Examples
                if operation.get('examples'):
                    content.append("\n**Examples**:")
                    for example_name, example in operation['examples'].items():
                        content.append(f"- {example_name}: {json.dumps(example, indent=2)}")

        return '\n'.join(content)

    def group_endpoints_by_tag(self, spec: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Group endpoints by tags."""
        tag_groups = {}

        for path, path_item in spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    tags = operation.get('tags', ['default'])

                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation': operation,
                        'tags': tags
                    }

                    for tag in tags:
                        if tag not in tag_groups:
                            tag_groups[tag] = []
                        tag_groups[tag].append(endpoint)

        return tag_groups

    def get_all_operations(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all operations from the spec."""
        operations = []

        for path, path_item in spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    operations.append({'path': path, 'method': method.upper()})

        return operations
```

### Complete Documentation Pipeline
```python
class CompleteDocumentationPipeline:
    def __init__(self):
        self.openapi_generator = AdvancedOpenAPIGenerator()
        self.schema_enhancer = SchemaEnhancer()
        self.swagger_generator = SwaggerUIGenerator()
        self.markdown_generator = AdvancedMarkdownGenerator()

    def generate_complete_documentation(self, api_analysis: Dict[str, Any], output_dir: str = "./docs"):
        """Generate complete API documentation suite."""
        import os

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Generate OpenAPI specification
        openapi_spec = self.openapi_generator.generate_from_analysis(api_analysis)

        # Step 2: Enhance schemas
        if 'schemas' in api_analysis:
            enhanced_schemas = self.schema_enhancer.enhance_pydantic_schemas(api_analysis['schemas'])
            openapi_spec['components']['schemas'].update(enhanced_schemas)

        # Step 3: Generate Swagger UI
        swagger_file = self.swagger_generator.generate_swagger_html(
            openapi_spec,
            os.path.join(output_dir, "swagger.html")
        )

        # Step 4: Generate ReDoc
        redoc_file = self.swagger_generator.generate_redoc_html(
            openapi_spec,
            os.path.join(output_dir, "redoc.html")
        )

        # Step 5: Generate Markdown documentation
        markdown_content = self.markdown_generator.generate_comprehensive_docs(openapi_spec)
        markdown_file = os.path.join(output_dir, "api-documentation.md")
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Step 6: Export OpenAPI JSON
        openapi_file = os.path.join(output_dir, "openapi.json")
        with open(openapi_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2)

        # Step 7: Generate index page
        index_file = self.generate_index_page(output_dir, openapi_spec)

        return {
            'openapi_spec': openapi_spec,
            'files': {
                'swagger': swagger_file,
                'redoc': redoc_file,
                'markdown': markdown_file,
                'openapi_json': openapi_file,
                'index': index_file
            },
            'statistics': self.generate_documentation_stats(openapi_spec)
        }

    def generate_index_page(self, output_dir: str, openapi_spec: Dict[str, Any]) -> str:
        """Generate index page with links to all documentation."""
        index_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - API Documentation</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
        .docs-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .doc-card {{ background: white; border-radius: 8px; padding: 24px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .doc-card:hover {{ transform: translateY(-2px); }}
        .doc-card h3 {{ margin-top: 0; color: #333; }}
        .doc-card p {{ color: #666; margin-bottom: 20px; }}
        .btn {{ display: inline-block; background: #4a90e2; color: white;
                padding: 10px 20px; text-decoration: none; border-radius: 4px;
                transition: background 0.2s; }}
        .btn:hover {{ background: #357abd; }}
        .stats {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{description}</p>
        <p><strong>Version:</strong> {version} | <strong>Generated:</strong> {generated_date}</p>
    </div>

    <div class="stats">
        <h3>API Statistics</h3>
        <p><strong>Total Endpoints:</strong> {total_endpoints}</p>
        <p><strong>Tags:</strong> {total_tags}</p>
        <p><strong>Schemas:</strong> {total_schemas}</p>
    </div>

    <div class="docs-grid">
        <div class="doc-card">
            <h3>📘 Swagger UI</h3>
            <p>Interactive API documentation with try-it-out functionality. Perfect for developers who want to test the API directly.</p>
            <a href="swagger.html" class="btn">Open Swagger UI</a>
        </div>

        <div class="doc-card">
            <h3>📚 ReDoc</h3>
            <p>Beautiful, three-panel API documentation optimized for reading and reference. Great for comprehensive API exploration.</p>
            <a href="redoc.html" class="btn">Open ReDoc</a>
        </div>

        <div class="doc-card">
            <h3>📝 Markdown</h3>
            <p>Human-readable documentation format perfect for version control, GitHub wikis, and integration with documentation systems.</p>
            <a href="api-documentation.md" class="btn">View Markdown</a>
        </div>

        <div class="doc-card">
            <h3>🔧 OpenAPI Spec</h3>
            <p>Raw OpenAPI 3.1 specification in JSON format. Use this for programmatic access and integration with API tools.</p>
            <a href="openapi.json" class="btn">Download Spec</a>
        </div>
    </div>
</body>
</html>
        """

        # Calculate statistics
        stats = self.generate_documentation_stats(openapi_spec)

        html_content = index_template.format(
            title=openapi_spec['info']['title'],
            description=openapi_spec['info']['description'],
            version=openapi_spec['info']['version'],
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_endpoints=stats['total_endpoints'],
            total_tags=stats['total_tags'],
            total_schemas=stats['total_schemas']
        )

        index_file = os.path.join(output_dir, 'index.html')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return index_file

    def generate_documentation_stats(self, openapi_spec: Dict[str, Any]) -> Dict[str, int]:
        """Generate documentation statistics."""
        stats = {
            'total_endpoints': 0,
            'total_tags': len(self.markdown_generator.group_endpoints_by_tag(openapi_spec)),
            'total_schemas': len(openapi_spec.get('components', {}).get('schemas', {}))
        }

        for path, path_item in openapi_spec.get('paths', {}).items():
            for method in path_item:
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    stats['total_endpoints'] += 1

        return stats

# Usage example
pipeline = CompleteDocumentationPipeline()
results = pipeline.generate_complete_documentation(api_analysis_results)
print(f"Documentation generated: {results['files']}")
print(f"Statistics: {results['statistics']}")
```

**Use Cases for RAG**: Generate comprehensive API documentation suites with OpenAPI 3.1, interactive Swagger UI and ReDoc interfaces, detailed markdown documentation, schema enhancement with validation rules, and complete documentation pipelines for modern APIs.