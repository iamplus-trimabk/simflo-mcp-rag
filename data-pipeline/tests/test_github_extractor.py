#!/usr/bin/env python3
"""
Simple test script for GitHub extractor
"""

import sys
import os
from pathlib import Path
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from github_extractor import GitHubExtractor

def test_basic_functionality():
    """Test basic extractor functionality"""
    print("Testing GitHub extractor basic functionality...")

    # Test with a simple repository first
    test_repo = "https://github.com/radix-ui/primitives"  # Simple, well-structured repo

    try:
        extractor = GitHubExtractor(test_repo, output_dir="test_output")
        print(f"✅ Extractor initialized successfully")

        # Test repository name extraction
        repo_name = extractor._extract_repo_name(test_repo)
        print(f"✅ Repo name extraction: {repo_name}")

        # Test platform detection
        test_package = {
            "name": "test-react-native-lib",
            "dependencies": {"react-native": "*"},
            "keywords": ["react-native", "ui"]
        }
        platform = extractor._extract_platform_info(test_package)
        print(f"✅ Platform detection: {platform}")

        print("✅ All basic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_file_analysis():
    """Test file analysis functionality"""
    print("\nTesting file analysis...")

    try:
        # Create test component content
        test_content = '''
import React from 'react';
import { View, Text } from 'react-native';

/**
 * Button component for mobile apps
 * @example
 * <Button title="Click me" onPress={() => {}} />
 */
interface ButtonProps {
  title: string;
  onPress?: () => void;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({ title, onPress, variant = 'primary' }) => {
  return (
    <View>
      <Text>{title}</Text>
    </View>
  );
};

export default Button;
'''

        extractor = GitHubExtractor("https://github.com/test/repo")

        # Test exports extraction
        exports = extractor._extract_exports(test_content)
        print(f"✅ Exports found: {exports}")

        # Test imports extraction
        imports = extractor._extract_imports(test_content)
        print(f"✅ Imports found: {imports}")

        # Test JSDoc extraction
        jsdoc = extractor._extract_jsdoc_comments(test_content)
        print(f"✅ JSDoc comments found: {len(jsdoc)}")

        # Test interface parsing
        interface_name = extractor._find_props_interface(test_content)
        print(f"✅ Interface found: {interface_name}")

        print("✅ File analysis tests passed!")
        return True

    except Exception as e:
        print(f"❌ File analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting GitHub extractor tests...\n")

    tests_passed = 0
    total_tests = 2

    if test_basic_functionality():
        tests_passed += 1

    if test_file_analysis():
        tests_passed += 1

    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! GitHub extractor is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)