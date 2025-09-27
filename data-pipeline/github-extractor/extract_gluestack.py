#!/usr/bin/env python3
"""
SimFlo MCP RAG - Gluestack Extraction Script

Specifically configured to extract components from the Gluestack UI repository.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import extractors
sys.path.insert(0, str(Path(__file__).parent))

from github_cli_extractor import GitHubCLIExtractor
import json
import logging


def configure_gluestack_extractor():
    """Configure extractor specifically for Gluestack repository"""
    return {
        'repo_url': 'https://github.com/gluestack/gluestack-ui',
        'component_patterns': [
            # Gluestack specific patterns
            'packages/core/components/**/*.tsx',
            'packages/core/components/**/*.ts',
            'example/components/**/*.tsx',
            'example/components/**/*.ts',
        ],
        'platform_detection': {
            'reactnative_indicators': [
                'react-native',
                'native',
                '@gluestack-style/react-native',
                '@gluestack-ui/themed-native',
            ],
            'reactjs_indicators': [
                'react',
                'next',
                '@gluestack-style/react',
                '@gluestack-ui/themed',
            ]
        },
        'component_categories': {
            'ui': ['button', 'input', 'modal', 'alert', 'toast', 'tooltip'],
            'layout': ['box', 'vstack', 'hstack', 'center', 'divider'],
            'navigation': ['actionsheet', 'avatar', 'breadcrumb', 'tabs'],
            'form': ['checkbox', 'radio', 'switch', 'slider', 'select'],
            'feedback': ['alert', 'toast', 'progress', 'skeleton'],
            'data': ['table', 'list', 'card', 'badge'],
        }
    }


def post_process_gluestack_components(components, config):
    """Post-process extracted components with Gluestack-specific logic"""
    processed_components = []

    for component in components:
        # Enhance platform detection for Gluestack
        platform = _detect_gluestack_platform(component, config)

        # Add Gluestack-specific tags
        tags = component.get('tags', [])
        tags.extend(['gluestack', 'ui-library'])

        # Categorize component
        category = _categorize_gluestack_component(component, config)

        # Enhance description with Gluestack context
        description = _enhance_gluestack_description(component)

        processed_component = {
            **component,
            'platform': platform,
            'tags': tags,
            'category': category,
            'library': 'gluestack',
            'enhanced_description': description,
        }

        processed_components.append(processed_component)

    return processed_components


def _detect_gluestack_platform(component, config):
    """Detect platform based on Gluestack-specific indicators"""
    platform = []

    files = component.get('files', [])
    dependencies = component.get('dependencies', [])

    # Check file paths for platform indicators
    for file in files:
        file_path = file.get('path', '').lower()
        if 'native' in file_path:
            platform.append('reactnative')
        elif 'web' in file_path or 'example' in file_path:
            platform.append('reactjs')

    # Check dependencies for platform indicators
    rn_indicators = config['platform_detection']['reactnative_indicators']
    react_indicators = config['platform_detection']['reactjs_indicators']

    has_native = any(indicator in dependencies for indicator in rn_indicators)
    has_react = any(indicator in dependencies for indicator in react_indicators)

    if has_native:
        platform = ['reactnative'] if 'reactnative' not in platform else platform
    elif has_react:
        platform = ['reactjs'] if 'reactjs' not in platform else platform
    elif not platform:
        platform = ['both']  # Default to both if unclear

    return list(set(platform))


def _categorize_gluestack_component(component, config):
    """Categorize component based on Gluestack patterns"""
    component_name = component.get('name', '').lower()
    files = component.get('files', [])

    for category, keywords in config['component_categories'].items():
        for keyword in keywords:
            if keyword in component_name:
                return category

    # Check file paths for category hints
    for file in files:
        file_path = file.get('path', '').lower()
        if 'layout' in file_path:
            return 'layout'
        elif 'form' in file_path:
            return 'form'
        elif 'navigation' in file_path:
            return 'navigation'

    return 'ui'  # Default category


def _enhance_gluestack_description(component):
    """Enhance component description with Gluestack-specific information"""
    base_description = component.get('description', '')
    component_name = component.get('name', '')

    if not base_description:
        base_description = f"Gluestack {component_name} component"

    # Add platform info
    platform = component.get('platform', [])
    if 'reactnative' in platform and 'reactjs' in platform:
        platform_info = " (cross-platform)"
    elif 'reactnative' in platform:
        platform_info = " (React Native)"
    elif 'reactjs' in platform:
        platform_info = " (React)"
    else:
        platform_info = ""

    return f"{base_description}{platform_info}"


def main():
    """Main extraction function"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configure Gluestack extraction
    config = configure_gluestack_extractor()
    output_file = 'rag_databases/gluestack_db/components.json'

    logger.info("Starting Gluestack component extraction...")

    try:
        # Create output directory
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize extractor
        extractor = GitHubCLIExtractor(config['repo_url'])

        # Extract components
        components = extractor.extract_components()

        # Convert to dict format for processing
        components_dict = []
        for component in components:
            component_dict = component.__dict__.copy()
            # Convert ComponentFile objects to dicts
            component_dict['files'] = [
                {
                    'path': f.path,
                    'content': f.content,
                    'language': f.language,
                    'component_type': f.component_type,
                    'exports': f.exports,
                    'imports': f.imports,
                    'props_info': f.props_info,
                    'usage_patterns': f.usage_patterns,
                }
                for f in component.files
            ]
            components_dict.append(component_dict)

        # Post-process with Gluestack-specific logic
        processed_components = post_process_gluestack_components(components_dict, config)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_components, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully extracted {len(processed_components)} Gluestack components")
        logger.info(f"Components saved to {output_file}")

        # Print summary
        print(f"\nGluestack Extraction Summary:")
        print(f"Total components extracted: {len(processed_components)}")

        # Platform breakdown
        platform_counts = {}
        category_counts = {}
        for component in processed_components:
            platform = component.get('platform', ['unknown'])
            for p in platform:
                platform_counts[p] = platform_counts.get(p, 0) + 1

            category = component.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        print(f"Platform distribution: {platform_counts}")
        print(f"Category distribution: {category_counts}")

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()