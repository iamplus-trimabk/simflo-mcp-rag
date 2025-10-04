# -*- coding: utf-8 -*-
"""
AI Assistant Core Analysis Classes - Step 9 of the SimFlo Figma-to-RAG Pipeline.

This module provides AI-powered code analysis capabilities including code quality
assessment, security vulnerability detection, performance analysis, and best
practices validation using RAG knowledge bases.

Author: SimFlo Pipeline Team
Version: 1.0.0
"""

from common.schemas import RAGKnowledgeBase, ContentChunk
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of AI analysis available."""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    ACCESSIBILITY = "accessibility"
    MAINTAINABILITY = "maintainability"


class SeverityLevel(str, Enum):
    """Severity levels for issues found during analysis."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories of issues that can be found during analysis."""
    CODE_STYLE = "code_style"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ERROR_HANDLING = "error_handling"
    DEPENDENCIES = "dependencies"


@dataclass
class AnalysisIssue:
    """Represents an issue found during code analysis."""
    id: str
    type: AnalysisType
    category: IssueCategory
    severity: SeverityLevel
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    rag_context: Optional[List[str]] = None
    confidence_score: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class QualityMetrics:
    """Code quality metrics."""
    overall_score: float  # 0-100
    maintainability_score: float  # 0-100
    security_score: float  # 0-100
    performance_score: float  # 0-100
    accessibility_score: float  # 0-100
    test_coverage_score: float  # 0-100
    documentation_score: float  # 0-100
    complexity_score: float  # 0-100 (lower is better)
    technical_debt_score: float  # 0-100 (lower is better)


@dataclass
class AIAnalysisConfig:
    """Configuration for AI analysis."""
    enable_code_quality_analysis: bool = True
    enable_security_analysis: bool = True
    enable_performance_analysis: bool = True
    enable_best_practices_analysis: bool = True
    enable_accessibility_analysis: bool = True
    strict_mode: bool = False
    confidence_threshold: float = 0.5
    max_issues_per_category: int = 50
    include_rag_context: bool = True
    generate_improvement_suggestions: bool = True
    generate_refactoring_plan: bool = True
    analyze_test_files: bool = True
    analyze_documentation: bool = True


@dataclass
class AIAnalysisResult:
    """Result of AI analysis."""
    issues: List[AnalysisIssue]
    metrics: QualityMetrics
    improvement_suggestions: List[str]
    refactoring_recommendations: List[str]
    security_report: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    rag_insights: Dict[str, Any]
    processing_time: float
    files_analyzed: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGContextProvider:
    """Provides context from RAG knowledge bases for AI analysis."""

    def __init__(self, knowledge_bases: Dict[str, RAGKnowledgeBase]):
        self.knowledge_bases = knowledge_bases
        self.cache = {}

    def get_relevant_context(self, query: str, content_type: str = None,
                             limit: int = 5) -> List[ContentChunk]:
        """
        Get relevant context from RAG knowledge bases.

        Args:
            query: Search query for context
            content_type: Filter by content type
            limit: Maximum number of results

        Returns:
            List of relevant content chunks
        """
        cache_key = f"{query}_{content_type}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        context_chunks = []

        # Search in appropriate knowledge bases
        kb_types = ['code-rag', 'doc-rag', 'test-rag']
        if content_type == 'security':
            kb_types.extend(['code-rag', 'doc-rag'])
        elif content_type == 'performance':
            kb_types.extend(['code-rag'])
        elif content_type == 'accessibility':
            kb_types.extend(['doc-rag', 'code-rag'])

        for kb_name in kb_types:
            if kb_name in self.knowledge_bases:
                kb = self.knowledge_bases[kb_name]
                results = kb.search_chunks(query)
                context_chunks.extend(results[:limit // len(kb_types)])

        # Sort by relevance and limit results
        context_chunks = sorted(context_chunks,
                                key=lambda x: len(x.content),
                                reverse=True)[:limit]

        self.cache[cache_key] = context_chunks
        return context_chunks

    def get_best_practices_context(self, topic: str) -> List[str]:
        """Get best practices context for a given topic."""
        context_chunks = self.get_relevant_context(f"best practices {topic}", 'documentation')
        return [chunk.content for chunk in context_chunks]

    def get_security_patterns(self) -> List[str]:
        """Get security patterns and guidelines."""
        context_chunks = self.get_relevant_context("security patterns", 'documentation')
        return [chunk.content for chunk in context_chunks]

    def get_performance_patterns(self) -> List[str]:
        """Get performance optimization patterns."""
        context_chunks = self.get_relevant_context("performance optimization", 'documentation')
        return [chunk.content for chunk in context_chunks]


class CodeQualityAnalyzer:
    """Analyzes code quality metrics and issues."""

    def __init__(self, config: AIAnalysisConfig, rag_provider: RAGContextProvider):
        self.config = config
        self.rag_provider = rag_provider

    def analyze_file(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze a single file for code quality issues."""
        issues = []

        # Analyze based on file type
        if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            issues.extend(self._analyze_javascript_typescript(file_path, content))
        elif file_path.suffix == '.py':
            issues.extend(self._analyze_python(file_path, content))
        elif file_path.suffix in ['.css', '.scss']:
            issues.extend(self._analyze_css(file_path, content))
        elif file_path.suffix == '.json':
            issues.extend(self._analyze_json(file_path, content))

        return issues

    def _analyze_javascript_typescript(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JavaScript/TypeScript code quality."""
        issues = []
        lines = content.split('\n')

        # Check for common issues
        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # Console.log statements (should be removed in production)
            if 'console.log' in line and '//' not in line.split('console.log')[0]:
                issues.append(AnalysisIssue(
                    id=f"console_log_{i}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.CODE_STYLE,
                    severity=SeverityLevel.LOW,
                    title="Console.log statement found",
                    description="Console.log statements should be removed from production code",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Remove console.log or replace with proper logging",
                    code_snippet=line.strip(),
                    confidence_score=0.9
                ))

            # TODO comments
            if 'TODO' in line_stripped or 'FIXME' in line_stripped:
                issues.append(AnalysisIssue(
                    id=f"todo_comment_{i}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.DOCUMENTATION,
                    severity=SeverityLevel.INFO,
                    title="TODO comment found",
                    description="TODO comments indicate incomplete work",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Address TODO items or create proper issue tracking",
                    code_snippet=line.strip(),
                    confidence_score=0.8
                ))

            # Long lines
            if len(line) > 120:
                issues.append(AnalysisIssue(
                    id=f"long_line_{i}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.CODE_STYLE,
                    severity=SeverityLevel.LOW,
                    title="Line too long",
                    description=f"Line is {len(line)} characters (should be < 120)",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Break long lines into multiple lines",
                    code_snippet=line.strip(),
                    confidence_score=0.7
                ))

        # Function complexity analysis
        issues.extend(self._analyze_function_complexity(file_path, content))

        # Import/export analysis
        issues.extend(self._analyze_imports_exports(file_path, content))

        return issues

    def _analyze_function_complexity(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze function complexity."""
        issues = []

        # Find function definitions
        function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function)|(\w+)\s*\([^)]*\)\s*:)\s*[{]'
        matches = re.finditer(function_pattern, content, re.MULTILINE)

        for match in matches:
            func_name = match.group(1) or match.group(2) or match.group(3)
            if not func_name:
                continue

            # Extract function body
            start_pos = match.start()
            body_start = content.find('{', start_pos)
            if body_start == -1:
                continue

            # Simple complexity check
            func_content = content[body_start:]
            if self._calculate_complexity(func_content) > 10:
                issues.append(AnalysisIssue(
                    id=f"complex_function_{func_name}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.ARCHITECTURE,
                    severity=SeverityLevel.MEDIUM,
                    title=f"Complex function: {func_name}",
                    description="Function has high complexity, consider refactoring",
                    file_path=str(file_path),
                    line_number=content[:start_pos].count('\n') + 1,
                    suggestion="Break function into smaller, more focused functions",
                    confidence_score=0.8
                ))

        return issues

    def _calculate_complexity(self, code: str) -> int:
        """Calculate simple cyclomatic complexity."""
        complexity = 1  # Base complexity

        # Count complexity-increasing statements
        patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bswitch\b', r'\bcase\b', r'\btry\b', r'\bcatch\b', r'\?\s*:',
            r'\&\&', r'\|\|'
        ]

        for pattern in patterns:
            complexity += len(re.findall(pattern, code))

        return complexity

    def _analyze_imports_exports(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze import/export statements."""
        issues = []

        # Check for unused imports (simplified)
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)

        for import_path in imports:
            # Simple heuristic: check if import path is used
            import_name = Path(import_path).stem
            if import_name not in content:
                issues.append(AnalysisIssue(
                    id=f"unused_import_{import_name}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.CODE_STYLE,
                    severity=SeverityLevel.LOW,
                    title=f"Potentially unused import: {import_name}",
                    description="Import may not be used in the file",
                    file_path=str(file_path),
                    suggestion="Remove unused imports",
                    confidence_score=0.6
                ))

        return issues

    def _analyze_python(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze Python code quality."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # Print statements (should use logging)
            if line_stripped.startswith('print(') and 'print(' in line and '#' not in line.split('print(')[0]:
                issues.append(AnalysisIssue(
                    id=f"print_statement_{i}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.CODE_STYLE,
                    severity=SeverityLevel.MEDIUM,
                    title="Print statement found",
                    description="Use logging instead of print statements",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Replace print() with proper logging",
                    code_snippet=line.strip(),
                    confidence_score=0.9
                ))

            # TODO/FIXME comments
            if any(prefix in line_stripped for prefix in ['# TODO', '# FIXME', '# HACK']):
                issues.append(AnalysisIssue(
                    id=f"todo_comment_{i}",
                    type=AnalysisType.CODE_QUALITY,
                    category=IssueCategory.DOCUMENTATION,
                    severity=SeverityLevel.INFO,
                    title="TODO/FIXME comment found",
                    description="Comment indicates incomplete work or temporary solution",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Address TODO items or create proper issue tracking",
                    code_snippet=line.strip(),
                    confidence_score=0.8
                ))

        return issues

    def _analyze_css(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze CSS code quality."""
        issues = []

        # Check for !important usage
        important_pattern = r'!\s*important'
        matches = list(re.finditer(important_pattern, content, re.IGNORECASE))

        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(AnalysisIssue(
                id=f"important_{line_num}",
                type=AnalysisType.CODE_QUALITY,
                category=IssueCategory.CODE_STYLE,
                severity=SeverityLevel.MEDIUM,
                title="!important usage",
                description="Avoid using !important, use more specific selectors instead",
                file_path=str(file_path),
                line_number=line_num,
                suggestion="Use CSS specificity or refactor selector hierarchy",
                confidence_score=0.8
            ))

        return issues

    def _analyze_json(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JSON file quality."""
        issues = []

        try:
            data = json.loads(content)

            # Check for empty objects/arrays that might indicate incomplete data
            def check_empty(obj, path="root"):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}"
                        if isinstance(value, (dict, list)) and len(value) == 0:
                            issues.append(AnalysisIssue(
                                id=f"empty_{current_path}",
                                type=AnalysisType.CODE_QUALITY,
                                category=IssueCategory.DATA_QUALITY,
                                severity=SeverityLevel.LOW,
                                title=f"Empty {key if isinstance(value, dict) else 'array'}",
                                description=f"Empty {type(value).__name__} found at {current_path}",
                                file_path=str(file_path),
                                suggestion="Remove empty structures or populate with data",
                                confidence_score=0.6
                            ))
                        elif isinstance(value, (dict, list)):
                            check_empty(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)) and len(item) == 0:
                            issues.append(AnalysisIssue(
                                id=f"empty_{path}[{i}]",
                                type=AnalysisType.CODE_QUALITY,
                                category=IssueCategory.DATA_QUALITY,
                                severity=SeverityLevel.LOW,
                                title="Empty array item",
                                description=f"Empty item found at {path}[{i}]",
                                file_path=str(file_path),
                                suggestion="Remove empty items or populate with data",
                                confidence_score=0.6
                            ))
                        elif isinstance(item, (dict, list)):
                            check_empty(item, f"{path}[{i}]")

            check_empty(data)

        except json.JSONDecodeError:
            # This would be caught by schema validation earlier
            pass

        return issues


class SecurityAnalyzer:
    """Analyzes code for security vulnerabilities."""

    def __init__(self, config: AIAnalysisConfig, rag_provider: RAGContextProvider):
        self.config = config
        self.rag_provider = rag_provider

    def analyze_file(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze a single file for security issues."""
        issues = []

        # Get security context from RAG
        # security_patterns = self.rag_provider.get_security_patterns()

        # Analyze based on file type
        if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            issues.extend(self._analyze_javascript_security(file_path, content))
        elif file_path.suffix in ['.py']:
            issues.extend(self._analyze_python_security(file_path, content))
        elif file_path.suffix == '.json':
            issues.extend(self._analyze_json_security(file_path, content))

        return issues

    def _analyze_javascript_security(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JavaScript/TypeScript security issues."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # eval() usage
            if 'eval(' in line and '//' not in line.split('eval(')[0]:
                issues.append(AnalysisIssue(
                    id=f"eval_usage_{i}",
                    type=AnalysisType.SECURITY,
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="eval() usage detected",
                    description="eval() can execute arbitrary code and is a major security risk",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Replace eval() with safer alternatives",
                    code_snippet=line.strip(),
                    rag_context=[],
                    confidence_score=0.95
                ))

            # innerHTML usage
            if 'innerHTML' in line and '//' not in line.split('innerHTML')[0]:
                issues.append(AnalysisIssue(
                    id=f"innerhtml_{i}",
                    type=AnalysisType.SECURITY,
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.HIGH,
                    title="innerHTML usage detected",
                    description="innerHTML can lead to XSS vulnerabilities if not properly sanitized",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Use textContent or sanitize HTML before assignment",
                    code_snippet=line.strip(),
                    rag_context=[],
                    confidence_score=0.9
                ))

            # Hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]

            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(AnalysisIssue(
                        id=f"hardcoded_secret_{i}",
                        type=AnalysisType.SECURITY,
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Hardcoded secret detected",
                        description="Hardcoded secrets, passwords, or API keys found",
                        file_path=str(file_path),
                        line_number=i,
                        suggestion="Use environment variables or secure configuration",
                        code_snippet=line.strip(),
                        rag_context=[],
                        confidence_score=0.95
                    ))
                    break

        return issues

    def _analyze_python_security(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze Python security issues."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # exec() usage
            if line_stripped.startswith('exec('):
                issues.append(AnalysisIssue(
                    id=f"exec_usage_{i}",
                    type=AnalysisType.SECURITY,
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="exec() usage detected",
                    description="exec() can execute arbitrary code and is a major security risk",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Avoid exec() or use safe evaluation alternatives",
                    code_snippet=line.strip(),
                    confidence_score=0.95
                ))

            # eval() usage
            if line_stripped.startswith('eval('):
                issues.append(AnalysisIssue(
                    id=f"eval_usage_{i}",
                    type=AnalysisType.SECURITY,
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="eval() usage detected",
                    description="eval() can execute arbitrary code and is a major security risk",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Avoid eval() or use safe evaluation alternatives",
                    code_snippet=line.strip(),
                    confidence_score=0.95
                ))

        return issues

    def _analyze_json_security(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JSON configuration for security issues."""
        issues = []

        try:
            data = json.loads(content)

            # Check for exposed API keys or secrets in configuration
            def check_secrets(obj, path="root"):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}"
                        if isinstance(value, str) and self._is_potential_secret(key, value):
                            issues.append(AnalysisIssue(
                                id=f"secret_in_config_{current_path}",
                                type=AnalysisType.SECURITY,
                                category=IssueCategory.SECURITY,
                                severity=SeverityLevel.HIGH,
                                title=f"Potential secret in configuration: {key}",
                                description="Configuration may contain sensitive information",
                                file_path=str(file_path),
                                suggestion="Move secrets to environment variables",
                                confidence_score=0.8
                            ))
                        elif isinstance(value, (dict, list)):
                            check_secrets(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            check_secrets(item, f"{path}[{i}]")

            check_secrets(data)

        except json.JSONDecodeError:
            pass

        return issues

    def _is_potential_secret(self, key: str, value: str) -> bool:
        """Check if a key-value pair might be a secret."""
        secret_indicators = ['key', 'secret', 'token', 'password', 'auth']
        key_lower = key.lower()

        # Check key name
        if any(indicator in key_lower for indicator in secret_indicators):
            # Check if value looks like a secret (long, alphanumeric, etc.)
            if len(value) > 10 and not value.islower():
                return True

        return False


class PerformanceAnalyzer:
    """Analyzes code for performance issues."""

    def __init__(self, config: AIAnalysisConfig, rag_provider: RAGContextProvider):
        self.config = config
        self.rag_provider = rag_provider

    def analyze_file(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze a single file for performance issues."""
        issues = []

        # Get performance patterns from RAG
        # performance_patterns = self.rag_provider.get_performance_patterns()  # Unused variable removed

        # Analyze based on file type
        if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            issues.extend(self._analyze_javascript_performance(file_path, content))
        elif file_path.suffix == '.py':
            issues.extend(self._analyze_python_performance(file_path, content))

        return issues

    def _analyze_javascript_performance(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JavaScript/TypeScript performance issues."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # React re-renders issues
            if 'useState' in line and 'useEffect' in line:
                # Check for potential re-render issues
                if re.search(r'useEffect\([^,]+,\s*\[\s*\]', line):
                    issues.append(AnalysisIssue(
                        id=f"empty_deps_{i}",
                        type=AnalysisType.PERFORMANCE,
                        category=IssueCategory.PERFORMANCE,
                        severity=SeverityLevel.MEDIUM,
                        title="Empty dependency array in useEffect",
                        description="Empty dependency array may cause stale closures or unnecessary re-renders",
                        file_path=str(file_path),
                        line_number=i,
                        suggestion="Include all dependencies used in the effect",
                        code_snippet=line.strip(),
                        confidence_score=0.7
                    ))

            # Console.log in loops
            if 'console.log' in line and any(keyword in line for keyword in ['for(', 'while(', 'map(', 'forEach(']):
                issues.append(AnalysisIssue(
                    id=f"console_in_loop_{i}",
                    type=AnalysisType.PERFORMANCE,
                    category=IssueCategory.PERFORMANCE,
                    severity=SeverityLevel.LOW,
                    title="console.log in loop",
                    description="Console statements in loops can impact performance",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Remove or move console statements outside loops",
                    code_snippet=line.strip(),
                    confidence_score=0.8
                ))

            # Inefficient DOM queries
            if 'document.getElementById' in line or 'document.querySelector' in line:
                issues.append(AnalysisIssue(
                    id=f"dom_query_{i}",
                    type=AnalysisType.PERFORMANCE,
                    category=IssueCategory.PERFORMANCE,
                    severity=SeverityLevel.MEDIUM,
                    title="Direct DOM query detected",
                    description="Direct DOM queries can be slow, consider caching references",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Cache DOM references or use React refs",
                    code_snippet=line.strip(),
                    confidence_score=0.6
                ))

        return issues

    def _analyze_python_performance(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze Python performance issues."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # Inefficient list operations
            if 'list(' in line and 'range(' in line:
                issues.append(AnalysisIssue(
                    id=f"list_range_{i}",
                    type=AnalysisType.PERFORMANCE,
                    category=IssueCategory.PERFORMANCE,
                    severity=SeverityLevel.LOW,
                    title="Inefficient range conversion",
                    description="Converting range to list unnecessarily uses memory",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Use range directly in loops or iterators",
                    code_snippet=line.strip(),
                    confidence_score=0.6
                ))

            # Global variable lookups in loops
            if re.search(r'for\s+\w+\s+in\s+\w+\s*:', line):
                # This is a simplified check
                issues.append(AnalysisIssue(
                    id=f"loop_scope_{i}",
                    type=AnalysisType.PERFORMANCE,
                    category=IssueCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    title="Loop variable scope",
                    description="Ensure loop variables don't shadow global names",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Use local variable names in loops",
                    code_snippet=line.strip(),
                    confidence_score=0.5
                ))

        return issues


class BestPracticesAnalyzer:
    """Analyzes code for adherence to best practices."""

    def __init__(self, config: AIAnalysisConfig, rag_provider: RAGContextProvider):
        self.config = config
        self.rag_provider = rag_provider

    def analyze_file(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze a single file for best practices violations."""
        issues = []

        # Get best practices context from RAG
        # best_practices = self.rag_provider.get_best_practices_context("coding")  # Unused variable removed

        # Analyze based on file type
        if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            issues.extend(self._analyze_javascript_best_practices(file_path, content))
        elif file_path.suffix == '.py':
            issues.extend(self._analyze_python_best_practices(file_path, content))

        return issues

    def _analyze_javascript_best_practices(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze JavaScript/TypeScript best practices."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # Var usage (prefer const/let)
            if line_stripped.startswith('var '):
                issues.append(AnalysisIssue(
                    id=f"var_usage_{i}",
                    type=AnalysisType.BEST_PRACTICES,
                    category=IssueCategory.CODE_STYLE,
                    severity=SeverityLevel.MEDIUM,
                    title="var usage detected",
                    description="Prefer const or let over var for better scoping",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Replace var with const or let",
                    code_snippet=line.strip(),
                    confidence_score=0.9
                ))

            # Magic numbers
            if re.search(r'\b\d{2,}\b', line) and not re.search(r'//|#', line.split(re.search(r'\b\d{2,}\b', line).group(0))[0]):
                number_match = re.search(r'\b\d{2,}\b', line)
                if number_match:
                    issues.append(AnalysisIssue(
                        id=f"magic_number_{i}",
                        type=AnalysisType.BEST_PRACTICES,
                        category=IssueCategory.CODE_STYLE,
                        severity=SeverityLevel.LOW,
                        title="Magic number detected",
                        description="Consider extracting magic numbers to named constants",
                        file_path=str(file_path),
                        line_number=i,
                        suggestion="Define constants for magic numbers",
                        code_snippet=line.strip(),
                        confidence_score=0.7
                    ))

        return issues

    def _analyze_python_best_practices(self, file_path: Path, content: str) -> List[AnalysisIssue]:
        """Analyze Python best practices."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # line_stripped = line.strip()  # Unused variable removed

            # Long parameter lists
            if re.search(r'def\s+\w+\([^)]{50,}\)', line):
                issues.append(AnalysisIssue(
                    id=f"many_params_{i}",
                    type=AnalysisType.BEST_PRACTICES,
                    category=IssueCategory.ARCHITECTURE,
                    severity=SeverityLevel.MEDIUM,
                    title="Too many parameters",
                    description="Function has too many parameters, consider using a dataclass or dict",
                    file_path=str(file_path),
                    line_number=i,
                    suggestion="Group related parameters into objects or use **kwargs",
                    code_snippet=line.strip(),
                    confidence_score=0.8
                ))

        return issues


@dataclass
class AIAnalysisResult:
    """Result of AI-powered code analysis."""
    success: bool
    processing_time: float
    issues: List[AnalysisIssue]
    metrics: QualityMetrics
    improvement_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AIAnalyzer:
    """Main AI analyzer class that coordinates all analysis operations."""

    def __init__(self, config: AIAnalysisConfig):
        self.config = config
        self.rag_context_provider: Optional[RAGContextProvider] = None
        self.code_quality_analyzer = None
        self.security_analyzer = None
        self.performance_analyzer = None
        self.best_practices_analyzer = None

        logger.info(f"AI Analyzer initialized with config: {config}")

    def analyze_pipeline_outputs(self, rag_bases_dir: Path, code_dirs: List[Path], output_dir: Path) -> AIAnalysisResult:
        """Main analysis entry point."""
        import time
        start_time = time.time()
        logger.info(f"Starting AI analysis of {len(code_dirs)} code directories")

        try:
            # Initialize knowledge bases if RAG is enabled
            if self.config.include_rag_context:
                try:
                    self.rag_context_provider = self._load_knowledge_bases(rag_bases_dir)
                    logger.info(f"Loaded RAG knowledge bases from {rag_bases_dir}")
                except Exception as e:
                    logger.warning(f"Failed to load RAG knowledge bases: {e}")
                    self.rag_context_provider = RAGContextProvider({})  # Empty provider fallback

            # Initialize analyzers with RAG context
            self.code_quality_analyzer = CodeQualityAnalyzer(self.config, self.rag_context_provider)
            self.security_analyzer = SecurityAnalyzer(self.config, self.rag_context_provider)
            self.performance_analyzer = PerformanceAnalyzer(self.config, self.rag_context_provider)
            self.best_practices_analyzer = BestPracticesAnalyzer(self.config, self.rag_context_provider)

            # Collect files for analysis
            files_to_analyze = self._collect_files(code_dirs)
            logger.info(f"Found {len(files_to_analyze)} files to analyze")

            # Analyze all files
            all_issues = []
            for file_path in files_to_analyze:
                try:
                    issues = self._analyze_file(file_path)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")

            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(all_issues, files_to_analyze)

            # Generate improvement suggestions
            improvement_suggestions = []
            if self.config.generate_improvement_suggestions:
                improvement_suggestions = self._generate_improvement_suggestions(all_issues)

            # Create summary
            summary = {
                "files_analyzed": len(files_to_analyze),
                "total_issues": len(all_issues),
                "processing_time": time.time() - start_time,
                "rag_enabled": self.config.include_rag_context,
                "analysis_types_enabled": [
                    name for name, enabled in [
                        ("code_quality", self.config.enable_code_quality_analysis),
                        ("security", self.config.enable_security_analysis),
                        ("performance", self.config.enable_performance_analysis),
                        ("best_practices", self.config.enable_best_practices_analysis),
                        ("accessibility", self.config.enable_accessibility_analysis)
                    ] if enabled
                ]
            }

            # Generate reports
            self._generate_reports(all_issues, metrics, improvement_suggestions, output_dir)

            processing_time = time.time() - start_time
            logger.info(f"AI analysis completed in {processing_time:.2f}s")

            return AIAnalysisResult(
                success=True,
                processing_time=processing_time,
                issues=all_issues,
                metrics=metrics,
                improvement_suggestions=improvement_suggestions,
                summary=summary
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"AI analysis failed: {e}")
            return AIAnalysisResult(
                success=False,
                processing_time=processing_time,
                issues=[],
                metrics=QualityMetrics(
                    overall_score=0,
                    maintainability_score=0,
                    security_score=0,
                    performance_score=0,
                    accessibility_score=0,
                    test_coverage_score=0,
                    documentation_score=0,
                    complexity_score=100,
                    technical_debt_score=100
                ),
                summary={"error": str(e)},
                errors=[str(e)]
            )

    def _load_knowledge_bases(self, rag_bases_dir: Path) -> RAGContextProvider:
        """Load RAG knowledge bases."""
        logger.info(f"Loading RAG knowledge bases from {rag_bases_dir}")

        # Simulate loading RAG knowledge bases
        # In a real implementation, this would load actual vector databases
        knowledge_bases = {}

        # Look for standard RAG base directories
        for base_name in ["doc-rag", "code-rag", "test-rag", "config-rag"]:
            base_path = rag_bases_dir / f"{base_name}-rag"
            if base_path.exists():
                # Create a mock RAGKnowledgeBase for testing
                mock_kb = RAGKnowledgeBase(
                    project_name=f"Mock {base_name}",
                    version="1.0.0",
                    chunks=[
                        ContentChunk(
                            id=f"mock_chunk_{base_name}_1",
                            content_type="documentation",
                            content=f"This is mock content for {base_name} knowledge base",
                            metadata={"source": base_name},
                            source_info={"path": str(base_path)},
                            tags=[base_name, "mock"]
                        )
                    ],
                    metadata={"mock": True, "path": str(base_path)},
                    configuration={"mock": True}
                )
                knowledge_bases[base_name] = mock_kb
                logger.info(f"Loaded {base_name} from {base_path}")

        return RAGContextProvider(knowledge_bases)

    def _collect_files(self, code_dirs: List[Path]) -> List[Path]:
        """Collect all files to analyze."""
        files = []
        supported_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".scss", ".json", ".md"}

        for code_dir in code_dirs:
            if not code_dir.exists():
                logger.warning(f"Code directory not found: {code_dir}")
                continue

            for file_path in code_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in supported_extensions:
                    # Skip node_modules and other common exclusions
                    if "node_modules" in str(file_path) or ".git" in str(file_path):
                        continue

                    # Skip test files if configured
                    if not self.config.analyze_test_files and ("test" in str(file_path) or "spec" in str(file_path)):
                        continue

                    # Skip documentation files if configured
                    if not self.config.analyze_documentation and file_path.suffix in {".md", ".txt"}:
                        continue

                    files.append(file_path)

        return files

    def _analyze_file(self, file_path: Path) -> List[AnalysisIssue]:
        """Analyze a single file and return issues found."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

        issues = []

        # Code quality analysis
        if self.config.enable_code_quality_analysis:
            issues.extend(self.code_quality_analyzer.analyze_file(file_path, content))

        # Security analysis
        if self.config.enable_security_analysis:
            issues.extend(self.security_analyzer.analyze_file(file_path, content))

        # Performance analysis
        if self.config.enable_performance_analysis:
            issues.extend(self.performance_analyzer.analyze_file(file_path, content))

        # Best practices analysis
        if self.config.enable_best_practices_analysis:
            issues.extend(self.best_practices_analyzer.analyze_file(file_path, content))

        # Filter issues by confidence threshold
        issues = [issue for issue in issues if issue.confidence_score >= self.config.confidence_threshold]

        # Limit issues per category
        category_counts = {}
        filtered_issues = []

        for issue in issues:
            category = issue.category.value
            if category_counts.get(category, 0) < self.config.max_issues_per_category:
                filtered_issues.append(issue)
                category_counts[category] = category_counts.get(category, 0) + 1

        return filtered_issues

    def _calculate_quality_metrics(self, issues: List[AnalysisIssue], files_analyzed: List[Path]) -> QualityMetrics:
        """Calculate quality metrics based on issues found."""
        if not files_analyzed:
            return QualityMetrics(0, 0, 0, 0, 0, 0, 0, 100, 100)

        # Count issues by severity
        severity_weights = {
            SeverityLevel.CRITICAL: 20,
            SeverityLevel.HIGH: 10,
            SeverityLevel.MEDIUM: 5,
            SeverityLevel.LOW: 2,
            SeverityLevel.INFO: 1
        }

        # Calculate base scores
        base_score = 100.0
        penalty = sum(severity_weights.get(issue.severity, 1) for issue in issues)

        # Apply penalty based on number of files
        penalty_per_file = penalty / len(files_analyzed)
        overall_score = max(0, base_score - penalty_per_file)

        # Calculate individual scores
        security_issues = [i for i in issues if i.type == AnalysisType.SECURITY]
        performance_issues = [i for i in issues if i.type == AnalysisType.PERFORMANCE]
        code_quality_issues = [i for i in issues if i.type == AnalysisType.CODE_QUALITY]

        security_score = max(0, 100 - sum(severity_weights.get(i.severity, 1) for i in security_issues))
        performance_score = max(0, 100 - sum(severity_weights.get(i.severity, 1) for i in performance_issues))
        maintainability_score = max(0, 100 - sum(severity_weights.get(i.severity, 1) for i in code_quality_issues))

        # Estimate other scores based on available data
        accessibility_score = overall_score * 0.9  # Slightly lower due to specialized analysis
        test_coverage_score = overall_score * 0.8  # Estimated based on code quality
        documentation_score = overall_score * 0.95  # Often higher quality

        # Complexity and technical debt scores
        complexity_score = min(100, len(issues) * 2)  # More issues = higher complexity
        technical_debt_score = min(100, penalty * 1.5)  # Penalty indicates technical debt

        return QualityMetrics(
            overall_score=round(overall_score, 1),
            maintainability_score=round(maintainability_score, 1),
            security_score=round(security_score, 1),
            performance_score=round(performance_score, 1),
            accessibility_score=round(accessibility_score, 1),
            test_coverage_score=round(test_coverage_score, 1),
            documentation_score=round(documentation_score, 1),
            complexity_score=round(complexity_score, 1),
            technical_debt_score=round(technical_debt_score, 1)
        )

    def _generate_improvement_suggestions(self, issues: List[AnalysisIssue]) -> List[Dict[str, Any]]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        # Group issues by type and severity
        critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        high_issues = [i for i in issues if i.severity == SeverityLevel.HIGH]

        # Generate high-priority suggestions
        if critical_issues:
            suggestions.append({
                "priority": "critical",
                "title": "Address Critical Issues",
                "description": f"Found {len(critical_issues)} critical issues that need immediate attention",
                "affected_files": list(set(issue.file_path for issue in critical_issues)),
                "estimated_effort": "high",
                "impact": "prevents production deployment"
            })

        if high_issues:
            suggestions.append({
                "priority": "high",
                "title": "Resolve High-Severity Issues",
                "description": f"Found {len(high_issues)} high-severity issues affecting quality and security",
                "affected_files": list(set(issue.file_path for issue in high_issues)),
                "estimated_effort": "medium",
                "impact": "improves code quality and security"
            })

        # Generate category-specific suggestions
        security_issues = [i for i in issues if i.type == AnalysisType.SECURITY]
        if security_issues:
            suggestions.append({
                "priority": "high",
                "title": "Security Hardening",
                "description": "Implement security best practices and fix vulnerabilities",
                "affected_files": list(set(issue.file_path for issue in security_issues)),
                "suggestions": [
                    "Use parameterized queries instead of string concatenation",
                    "Implement proper input validation and sanitization",
                    "Use HTTPS and secure communication protocols",
                    "Store sensitive data in environment variables",
                    "Implement proper authentication and authorization"
                ],
                "estimated_effort": "medium",
                "impact": "reduces security risks"
            })

        performance_issues = [i for i in issues if i.type == AnalysisType.PERFORMANCE]
        if performance_issues:
            suggestions.append({
                "priority": "medium",
                "title": "Performance Optimization",
                "description": "Optimize code for better performance and user experience",
                "affected_files": list(set(issue.file_path for issue in performance_issues)),
                "suggestions": [
                    "Implement memoization for expensive computations",
                    "Optimize database queries and add indexing",
                    "Use lazy loading for large datasets",
                    "Minimize DOM manipulations",
                    "Implement proper caching strategies"
                ],
                "estimated_effort": "medium",
                "impact": "improves application performance"
            })

        return suggestions

    def _generate_reports(self, issues: List[AnalysisIssue], metrics: QualityMetrics,
                         improvement_suggestions: List[Dict[str, Any]], output_dir: Path):
        """Generate all analysis reports."""
        ai_review_dir = output_dir / "ai-review"
        ai_review_dir.mkdir(parents=True, exist_ok=True)

        # Generate analysis.json
        analysis_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_issues": len(issues),
            "issues_by_severity": {
                severity.value: len([i for i in issues if i.severity == severity])
                for severity in SeverityLevel
            },
            "issues_by_type": {
                analysis_type.value: len([i for i in issues if i.type == analysis_type])
                for analysis_type in AnalysisType
            },
            "issues_by_category": {
                category.value: len([i for i in issues if i.category == category])
                for category in IssueCategory
            },
            "quality_metrics": {
                "overall_score": metrics.overall_score,
                "maintainability_score": metrics.maintainability_score,
                "security_score": metrics.security_score,
                "performance_score": metrics.performance_score,
                "accessibility_score": metrics.accessibility_score,
                "test_coverage_score": metrics.test_coverage_score,
                "documentation_score": metrics.documentation_score,
                "complexity_score": metrics.complexity_score,
                "technical_debt_score": metrics.technical_debt_score
            },
            "detailed_issues": [
                {
                    "id": issue.id,
                    "type": issue.type.value,
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "suggestion": issue.suggestion,
                    "code_snippet": issue.code_snippet,
                    "confidence_score": issue.confidence_score,
                    "tags": issue.tags
                }
                for issue in issues
            ]
        }

        with open(ai_review_dir / "analysis.json", 'w') as f:
            json.dump(analysis_report, f, indent=2)

        # Generate improvements.md
        improvements_md = self._generate_improvements_md(improvement_suggestions, metrics)
        with open(ai_review_dir / "improvements.md", 'w') as f:
            f.write(improvements_md)

        # Generate security-report.json
        security_issues = [i for i in issues if i.type == AnalysisType.SECURITY]
        security_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_security_issues": len(security_issues),
            "security_score": metrics.security_score,
            "risk_level": self._calculate_risk_level(metrics.security_score),
            "vulnerabilities": [
                {
                    "id": issue.id,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "remediation": issue.suggestion,
                    "cvss_score": self._calculate_cvss_score(issue.severity),
                    "confidence_score": issue.confidence_score
                }
                for issue in security_issues
            ],
            "recommendations": [
                "Implement secure coding practices",
                "Regular security audits and penetration testing",
                "Use automated security scanning tools",
                "Keep dependencies up to date",
                "Implement proper authentication and authorization"
            ]
        }

        with open(ai_review_dir / "security-report.json", 'w') as f:
            json.dump(security_report, f, indent=2)

        # Generate refactoring-plan.md
        refactoring_plan = self._generate_refactoring_plan(issues, metrics)
        with open(ai_review_dir / "refactoring-plan.md", 'w') as f:
            f.write(refactoring_plan)

        # Generate performance-report.json
        performance_issues = [i for i in issues if i.type == AnalysisType.PERFORMANCE]
        performance_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_performance_issues": len(performance_issues),
            "performance_score": metrics.performance_score,
            "performance_grade": self._calculate_performance_grade(metrics.performance_score),
            "issues": [
                {
                    "id": issue.id,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "optimization": issue.suggestion,
                    "estimated_impact": self._estimate_performance_impact(issue.severity),
                    "confidence_score": issue.confidence_score
                }
                for issue in performance_issues
            ],
            "optimization_opportunities": [
                "Implement React.memo for expensive components",
                "Use useMemo and useCallback hooks",
                "Optimize database queries with proper indexing",
                "Implement code splitting and lazy loading",
                "Use efficient data structures and algorithms"
            ]
        }

        with open(ai_review_dir / "performance-report.json", 'w') as f:
            json.dump(performance_report, f, indent=2)

        logger.info(f"Generated analysis reports in {ai_review_dir}")

    def _generate_improvements_md(self, improvement_suggestions: List[Dict[str, Any]], metrics: QualityMetrics) -> str:
        """Generate improvements markdown report."""
        md_content = f"""# AI-Powered Code Improvement Suggestions

## Quality Overview
- **Overall Score**: {metrics.overall_score}/100
- **Security Score**: {metrics.security_score}/100
- **Performance Score**: {metrics.performance_score}/100
- **Maintainability Score**: {metrics.maintainability_score}/100

## Priority Improvements

"""

        for suggestion in improvement_suggestions:
            priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(suggestion.get("priority", "medium"), "⚪")
            md_content += f"### {priority_emoji} {suggestion['title']}\n\n"
            md_content += f"**Description**: {suggestion['description']}\n\n"
            md_content += f"**Estimated Effort**: {suggestion.get('estimated_effort', 'unknown')}\n"
            md_content += f"**Impact**: {suggestion.get('impact', 'general improvement')}\n\n"

            if "suggestions" in suggestion:
                md_content += "**Specific Suggestions**:\n"
                for s in suggestion["suggestions"]:
                    md_content += f"- {s}\n"
                md_content += "\n"

            if "affected_files" in suggestion:
                md_content += "**Affected Files**:\n"
                for file_path in suggestion["affected_files"][:5]:  # Limit to 5 files
                    md_content += f"- `{file_path}`\n"
                if len(suggestion["affected_files"]) > 5:
                    md_content += f"- ... and {len(suggestion['affected_files']) - 5} more files\n"
                md_content += "\n"

        md_content += """
## Next Steps

1. **Critical Issues**: Address immediately as they block deployment
2. **High Priority**: Schedule for next sprint
3. **Medium Priority**: Include in upcoming maintenance
4. **Low Priority**: Consider during refactoring efforts

## Automated Fixes

Some issues can be automatically fixed using:
```bash
# ESLint auto-fix
npm run lint -- --fix

# Prettier formatting
npm run format

# Type checking
npm run type-check
```

## Monitoring

Track improvements over time by running this analysis regularly and monitoring:
- Overall quality score trends
- Reduction in critical/high severity issues
- Security and performance score improvements

---
*Generated by SimFlo AI Assistant*
"""
        return md_content

    def _generate_refactoring_plan(self, issues: List[AnalysisIssue], metrics: QualityMetrics) -> str:
        """Generate refactoring plan markdown."""
        # Group issues by file for refactoring recommendations
        files_with_issues = {}
        for issue in issues:
            if issue.file_path not in files_with_issues:
                files_with_issues[issue.file_path] = []
            files_with_issues[issue.file_path].append(issue)

        # Sort files by issue count
        sorted_files = sorted(files_with_issues.items(), key=lambda x: len(x[1]), reverse=True)

        md_content = f"""# Refactoring Plan

## Overview
Based on the analysis of {len(issues)} issues across {len(files_with_issues)} files, here's a prioritized refactoring plan.

## Quality Metrics Summary
- **Overall Score**: {metrics.overall_score}/100
- **Complexity Score**: {metrics.complexity_score}/100 (lower is better)
- **Technical Debt Score**: {metrics.technical_debt_score}/100 (lower is better)

## Priority Refactoring Targets

### High Priority (5+ issues)
"""

        for file_path, file_issues in sorted_files:
            if len(file_issues) >= 5:
                critical_count = len([i for i in file_issues if i.severity == SeverityLevel.CRITICAL])
                high_count = len([i for i in file_issues if i.severity == SeverityLevel.HIGH])

                md_content += f"""
#### `{file_path}`
- **Total Issues**: {len(file_issues)}
- **Critical**: {critical_count}, **High**: {high_count}
- **Refactoring Priority**: High

**Recommended Actions**:
"""

                # Suggest actions based on issue types
                issue_types = set(issue.type.value for issue in file_issues)
                if "security" in issue_types:
                    md_content += "- Review and fix security vulnerabilities\n"
                if "performance" in issue_types:
                    md_content += "- Optimize performance bottlenecks\n"
                if "code_quality" in issue_types:
                    md_content += "- Improve code quality and maintainability\n"

                md_content += "- Consider breaking down complex components\n"
                md_content += "- Add proper error handling and validation\n\n"

        md_content += """
### Medium Priority (2-4 issues)

"""

        for file_path, file_issues in sorted_files:
            if 2 <= len(file_issues) < 5:
                md_content += f"#### `{file_path}`\n"
                md_content += f"- **Issues**: {len(file_issues)} - Review and refactor\n\n"

        md_content += """
## Refactoring Strategy

### Phase 1: Critical Fixes (Week 1-2)
1. Address all critical security vulnerabilities
2. Fix blocking performance issues
3. Resolve critical code quality problems

### Phase 2: Structural Improvements (Week 3-4)
1. Refactor complex components
2. Improve code organization
3. Enhance error handling

### Phase 3: Optimization (Week 5-6)
1. Performance optimization
2. Code style consistency
3. Documentation improvements

## Success Metrics

- **Quality Score**: Increase from {metrics.overall_score} to 85+
- **Security Score**: Increase from {metrics.security_score} to 90+
- **Performance Score**: Increase from {metrics.performance_score} to 85+
- **Technical Debt**: Reduce from {metrics.technical_debt_score} to 20-

## Implementation Guidelines

1. **Test Coverage**: Maintain or increase test coverage during refactoring
2. **Incremental Changes**: Make small, verifiable changes
3. **Code Review**: All refactoring should be reviewed
4. **Performance Testing**: Verify no performance regression
5. **Documentation**: Update documentation alongside code changes

## Tools and Resources

- **Code Quality**: ESLint, Prettier, TypeScript
- **Testing**: Jest, React Testing Library, Playwright
- **Performance**: Lighthouse, WebPageTest
- **Security**: OWASP ZAP, npm audit

---
*Generated by SimFlo AI Assistant*
"""
        return md_content

    def _calculate_risk_level(self, security_score: float) -> str:
        """Calculate risk level based on security score."""
        if security_score >= 90:
            return "low"
        elif security_score >= 70:
            return "medium"
        elif security_score >= 50:
            return "high"
        else:
            return "critical"

    def _calculate_cvss_score(self, severity: SeverityLevel) -> float:
        """Calculate CVSS score based on severity."""
        cvss_scores = {
            SeverityLevel.CRITICAL: 9.0,
            SeverityLevel.HIGH: 7.5,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 0.0
        }
        return cvss_scores.get(severity, 0.0)

    def _calculate_performance_grade(self, performance_score: float) -> str:
        """Calculate performance grade."""
        if performance_score >= 90:
            return "A"
        elif performance_score >= 80:
            return "B"
        elif performance_score >= 70:
            return "C"
        elif performance_score >= 60:
            return "D"
        else:
            return "F"

    def _estimate_performance_impact(self, severity: SeverityLevel) -> str:
        """Estimate performance impact."""
        impact_map = {
            SeverityLevel.CRITICAL: "severe (50ms+ delay)",
            SeverityLevel.HIGH: "significant (20-50ms delay)",
            SeverityLevel.MEDIUM: "moderate (5-20ms delay)",
            SeverityLevel.LOW: "minimal (<5ms delay)",
            SeverityLevel.INFO: "negligible"
        }
        return impact_map.get(severity, "unknown")
