"""
Language-Based Documentation Extractor

A fallback extractor for documentation files in any repository.
Extracts content from markdown, MDX, and other documentation formats.
"""

import re
import json
import subprocess
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class LanguageDocumentationExtractor:
    """Language-based extractor for documentation files"""

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        self.source_config = source_config or {}
        self.content_root = os.getenv('CONTENT_ROOT', '/Users/tbardale/v2/simflo-mcp-rag/content')
        self.github_dir = Path(self.content_root) / "github"

        # File patterns to analyze
        self.file_patterns = [
            "**/*.md", "**/*.mdx", "**/*.txt", "**/*.rst"
        ]

        # Documentation patterns to identify different types
        self.doc_patterns = {
            "title": r'^#+\s+(.+)$',
            "heading": r'^#{2,6}\s+(.+)$',
            "code_block": r'```[\w]*\n([\s\S]+?)\n```',
            "api_reference": r'^#+\s+API\s+Reference|^#+\s+(Class|Function|Method)\s*[:\n]',
            "installation": r'^#+\s*(?:Installation|Getting Started|Setup)',
            "usage_example": r'^#+\s*(?:Usage|Examples|How to use)',
            "contributing": r'^#+\s*(?:Contributing|Development)',
            "changelog": r'^#+\s*(?:Changelog|Changes|Release notes)',
            "todo": r'^#+\s*(?:TODO|Roadmap)',
        }

        # Content quality indicators
        self.quality_indicators = {
            "has_headings": r'^#{1,6}\s+',
            "has_code_examples": r'```[\w]*\n',
            "has_links": r'\[([^\]]+)\]\([^)]+\)',
            "has_lists": r'^\s*[-*+]\s+|^\s*\d+\.\s+',
            "has_tables": r'\|.*\|',
            "has_images": r'!\[([^\]]*)\]\([^)]+\)',
        }

    def extract(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract documentation from any repository"""
        try:
            if not repo_url:
                return {"error": "Repository URL required for language-based extraction"}

            # Parse repository URL
            repo_name = self._parse_repo_url(repo_url)
            if not repo_name:
                return {"error": f"Invalid repository URL: {repo_url}"}

            # Ensure GitHub directory exists
            self.github_dir.mkdir(parents=True, exist_ok=True)

            # Download repository using GitHub CLI if not present locally
            repo_path = self.github_dir / repo_name
            if not repo_path.exists():
                print(f"Downloading {repo_name} using GitHub CLI...")
                clone_cmd = ["gh", "repo", "clone", repo_name, str(repo_path)]
                result = subprocess.run(clone_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return {"error": f"Failed to clone repository: {result.stderr}"}
            else:
                print(f"Using local repository at {repo_path}")

            # Get repository information
            repo_info = self._get_repo_info(repo_name, repo_path)
            if not repo_info:
                return {"error": f"Repository {repo_name} not found"}

            # Extract documentation from the repository
            documents = self._extract_documents(repo_name, repo_path)

            # Save documents to registry files
            saved = self.save_to_registry(documents, repo_name)

            result = {
                "extractor": "language-documentation",
                "repository": repo_name,
                "repository_url": repo_url,
                "local_path": str(repo_path),
                "timestamp": datetime.now().isoformat(),
                "documents_found": len(documents),
                "documents": documents,
                "saved_to_registry": saved,
                "repo_info": repo_info,
                "file_patterns": self.file_patterns,
                "document_types": list(set(doc.get("doc_type", "unknown") for doc in documents))
            }

            return result

        except Exception as e:
            return {
                "extractor": "language-documentation",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _parse_repo_url(self, url: str) -> Optional[str]:
        """Parse GitHub URL to get repository name"""
        patterns = [
            r'github\.com/([^/]+/[^/]+?)(?:\.git)?/?$',
            r'([^/]+/[^/]+)$',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).strip('/')

        return None

    def _get_repo_info(self, repo_name: str, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Get repository information using GitHub CLI"""
        try:
            cmd = ["gh", "repo", "view", repo_name, "--json", "name,description,stargazerCount,forkCount,createdAt,updatedAt,owner,languages,primaryLanguage"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    "name": repo_name,
                    "description": f"{repo_name} repository",
                    "stargazerCount": 0,
                    "forkCount": 0,
                    "createdAt": "unknown",
                    "updatedAt": "unknown",
                    "primaryLanguage": {"name": "Documentation"}
                }
        except Exception:
            return None

    def _extract_documents(self, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract documentation from files"""
        documents = []

        # Find all documentation files
        files = []
        for pattern in self.file_patterns:
            files.extend(repo_path.glob(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        for file_path in files:
            try:
                # Skip common directories to ignore
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', 'venv', 'env', '.venv', 'site-packages', 'build', 'dist', '__pycache__']):
                    continue

                documents.extend(self._extract_from_file(file_path, repo_name, repo_path))
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return documents

    def _extract_from_file(self, file_path: Path, repo_name: str, repo_path: Path) -> List[Dict[str, Any]]:
        """Extract content from a single documentation file"""
        documents = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return documents

        # Skip very short files or likely auto-generated files
        if len(content.strip()) < 100:
            return documents

        relative_path = file_path.relative_to(repo_path)
        file_extension = file_path.suffix.lower()

        # Determine document type and structure
        doc_structure = self._analyze_document_structure(content)
        doc_type = self._determine_document_type(relative_path, doc_structure)

        # Split content into logical sections if it's a long document
        if len(content) > 5000:  # For long documents, split into sections
            sections = self._split_into_sections(content, relative_path)
            for i, section in enumerate(sections):
                document = self._create_document_element(
                    section["content"], section["title"], section["section_id"],
                    relative_path, repo_name, doc_type, doc_structure, file_extension
                )
                if document:
                    documents.append(document)
        else:
            # For shorter documents, treat as one document
            title = doc_structure.get("main_title", file_path.stem)
            document = self._create_document_element(
                content, title, file_path.stem,
                relative_path, repo_name, doc_type, doc_structure, file_extension
            )
            if document:
                documents.append(document)

        return documents

    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure and metadata"""
        structure = {
            "main_title": None,
            "headings": [],
            "code_blocks": [],
            "has_api_reference": False,
            "has_installation": False,
            "has_usage_examples": False,
            "word_count": len(content.split()),
            "line_count": len(content.split('\n')),
            "quality_score": 0.0
        }

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Extract main title (first # heading)
            if not structure["main_title"] and line.startswith('# '):
                structure["main_title"] = line[2:].strip()

            # Extract all headings
            if line.startswith('#'):
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if heading_match:
                    structure["headings"].append({
                        "level": len(heading_match.group(1)),
                        "title": heading_match.group(2).strip(),
                        "line": line_num
                    })

        # Check for special content types
        structure["has_api_reference"] = bool(re.search(self.doc_patterns["api_reference"], content, re.MULTILINE | re.IGNORECASE))
        structure["has_installation"] = bool(re.search(self.doc_patterns["installation"], content, re.MULTILINE | re.IGNORECASE))
        structure["has_usage_examples"] = bool(re.search(self.doc_patterns["usage_example"], content, re.MULTILINE | re.IGNORECASE))

        # Count code blocks
        structure["code_blocks"] = re.findall(self.doc_patterns["code_block"], content)

        # Calculate quality score
        structure["quality_score"] = self._calculate_document_quality(content, structure)

        return structure

    def _determine_document_type(self, file_path: Path, structure: Dict[str, Any]) -> str:
        """Determine document type based on file path and content"""
        path_str = str(file_path).lower()

        # Check path-based clues
        if any(keyword in path_str for keyword in ['readme', 'getting-started', 'intro']):
            return "introduction"
        elif any(keyword in path_str for keyword in ['api', 'reference', 'docs']):
            return "api-reference"
        elif any(keyword in path_str for keyword in ['install', 'setup', 'getting-started']):
            return "installation"
        elif any(keyword in path_str for keyword in ['example', 'usage', 'how-to']):
            return "usage-example"
        elif any(keyword in path_str for keyword in ['contributing', 'development', 'dev']):
            return "contributing"
        elif any(keyword in path_str for keyword in ['changelog', 'changes', 'release']):
            return "changelog"
        elif any(keyword in path_str for keyword in ['todo', 'roadmap', 'plan']):
            return "roadmap"
        elif any(keyword in path_str for keyword in ['guide', 'tutorial']):
            return "tutorial"

        # Check content-based clues
        if structure.get("has_api_reference"):
            return "api-reference"
        elif structure.get("has_installation"):
            return "installation"
        elif structure.get("has_usage_examples"):
            return "usage-example"
        elif structure.get("main_title") and "readme" in path_str:
            return "introduction"

        return "general"

    def _split_into_sections(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Split long documents into logical sections"""
        sections = []

        # Split by major headings (## or ###)
        heading_pattern = r'^(#{2,3})\s+(.+)$'
        current_section = {"content": "", "title": "", "section_id": "intro"}
        lines = content.split('\n')

        for line in lines:
            heading_match = re.match(heading_pattern, line)

            if heading_match:
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section.copy())

                # Start new section
                heading_level = len(heading_match.group(1))
                heading_title = heading_match.group(2).strip()
                section_id = re.sub(r'[^a-zA-Z0-9]+', '-', heading_title.lower()).strip('-')

                current_section = {
                    "content": line + '\n',  # Include the heading
                    "title": heading_title,
                    "section_id": section_id
                }
            else:
                current_section["content"] += line + '\n'

        # Add the last section
        if current_section["content"].strip():
            sections.append(current_section)

        # If no major headings found, treat entire content as one section
        if not sections:
            sections.append({
                "content": content,
                "title": file_path.stem,
                "section_id": file_path.stem
            })

        return sections

    def _create_document_element(self, content: str, title: str, doc_id: str, file_path: Path,
                                repo_name: str, doc_type: str, structure: Dict[str, Any], file_extension: str) -> Optional[Dict[str, Any]]:
        """Create a document element"""
        try:
            # Extract key information
            summary = self._extract_summary(content)
            key_points = self._extract_key_points(content)
            code_examples = structure.get("code_blocks", [])

            # Extract links
            links = re.findall(r'\[([^\]]+)\]\([^)]+\)', content)

            # Determine target platforms based on content
            platforms = self._determine_platforms(content, doc_type)

            return {
                "name": doc_id,
                "type": "documentation",
                "category": "documentation",
                "file_path": str(file_path),
                "description": summary or f"{doc_type.title()}: {title}",
                "usage_examples": [content],
                "dependencies": [],
                "peer_dependencies": [],
                "installation": f"# Found in {repo_name} documentation",
                "metadata": {
                    "extractor": "language-documentation",
                    "repository": repo_name,
                    "title": title,
                    "doc_type": doc_type,
                    "file_extension": file_extension,
                    "word_count": len(content.split()),
                    "line_count": len(content.split('\n')),
                    "headings_count": len(structure.get("headings", [])),
                    "code_examples_count": len(code_examples),
                    "has_api_reference": structure.get("has_api_reference", False),
                    "has_installation": structure.get("has_installation", False),
                    "has_usage_examples": structure.get("has_usage_examples", False),
                    "key_points": key_points,
                    "links_count": len(links),
                    "quality_score": structure.get("quality_score", 0.0)
                },
                "quality_score": structure.get("quality_score", 0.0),
                "platform": platforms,
                "registry": repo_name
            }
        except Exception as e:
            print(f"Error creating document element {doc_id}: {e}")
            return None

    def _extract_summary(self, content: str) -> str:
        """Extract a summary from the content"""
        lines = content.split('\n')

        # Try to find the first paragraph after the main title
        summary_start = -1
        for i, line in enumerate(lines):
            if line.startswith('# '):
                # Look for the first non-empty paragraph after the title
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        summary_start = j
                        break
                break

        if summary_start >= 0:
            # Collect consecutive non-empty lines as summary
            summary_lines = []
            for line in lines[summary_start:]:
                if line.strip():
                    if line.startswith('#'):
                        break  # Stop at next heading
                    summary_lines.append(line.strip())
                elif summary_lines:  # Stop after first paragraph break
                    break

            summary = ' '.join(summary_lines)
            return summary[:300] + '...' if len(summary) > 300 else summary

        # Fallback: return first 200 characters
        return content[:200].strip() + '...' if len(content) > 200 else content.strip()

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        key_points = []

        # Look for bullet points and numbered lists
        list_pattern = r'^\s*[-*+]\s+(.+)$|^\s*\d+\.\s+(.+)$'
        lines = content.split('\n')

        for line in lines:
            match = re.match(list_pattern, line)
            if match:
                point = match.group(1) or match.group(2)
                if point and len(point.strip()) > 10:  # Skip very short points
                    key_points.append(point.strip())

        # Limit to top 10 key points
        return key_points[:10]

    def _determine_platforms(self, content: str, doc_type: str) -> List[str]:
        """Determine relevant platforms based on content and document type"""
        platforms = ["web"]  # Default platform

        content_lower = content.lower()

        # Check for platform-specific keywords
        if any(keyword in content_lower for keyword in ['react', 'javascript', 'typescript', 'frontend']):
            platforms.extend(["reactjs", "javascript"])

        if any(keyword in content_lower for keyword in ['react native', 'mobile', 'ios', 'android']):
            platforms.extend(["reactnative", "mobile"])

        if any(keyword in content_lower for keyword in ['python', 'backend', 'api', 'server']):
            platforms.extend(["python", "backend"])

        if any(keyword in content_lower for keyword in ['node', 'npm', 'nodejs']):
            platforms.extend(["nodejs"])

        # Add doc_type specific platforms
        if doc_type in ["installation", "usage-example"]:
            if "react" in platforms:
                platforms.append("reactjs")
            if "python" in platforms:
                platforms.append("python")

        return list(set(platforms))

    def _calculate_document_quality(self, content: str, structure: Dict[str, Any]) -> float:
        """Calculate quality score for documentation"""
        score = 0.0

        # Content length (0.2)
        word_count = structure.get("word_count", 0)
        if word_count > 1000:
            score += 0.2
        elif word_count > 300:
            score += 0.1

        # Structure quality (0.3)
        if structure.get("main_title"):
            score += 0.1
        if len(structure.get("headings", [])) > 3:
            score += 0.1
        if len(structure.get("headings", [])) > 10:
            score += 0.1

        # Content richness (0.3)
        if structure.get("code_blocks"):
            score += 0.1
        if re.search(self.quality_indicators["has_links"], content):
            score += 0.1
        if re.search(self.quality_indicators["has_lists"], content):
            score += 0.1

        # Document type bonuses (0.2)
        if structure.get("has_api_reference"):
            score += 0.1
        if structure.get("has_usage_examples"):
            score += 0.1

        return min(score, 1.0)

    def save_to_registry(self, documents: List[Dict[str, Any]], repo_name: str) -> Dict[str, int]:
        """Save documents to registry files"""
        # Sanitize repository name for file system compatibility
        safe_repo_name = repo_name.replace('/', '-').replace('\\', '-')
        registry_dir = Path(f"v2/core/00-rag-registry/registries/{safe_repo_name}/files")
        saved_counts = {}

        try:
            # Create documentation directory
            doc_dir = registry_dir / "documentation"
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Group documents by type
            by_type = {}
            for document in documents:
                doc_type = document.get("doc_type", "general")
                if doc_type not in by_type:
                    by_type[doc_type] = []
                by_type[doc_type].append(document)

            # Save each document type to its own file
            for doc_type, type_documents in by_type.items():
                output_file = doc_dir / f"{safe_repo_name}-{doc_type}.json"

                # Load existing data if file exists
                existing_data = []
                if output_file.exists():
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        existing_data = []

                # Add new documents
                existing_data.extend(type_documents)

                # Save updated data
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, default=str)

                saved_counts[doc_type] = len(type_documents)

            return saved_counts

        except Exception as e:
            print(f"Error saving to registry: {e}")
            return {}

    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about this extractor"""
        return {
            "name": "language-documentation",
            "type": "language-based",
            "description": "Language-based documentation fallback extractor",
            "supported_patterns": self.file_patterns,
            "document_types": [
                "introduction", "api-reference", "installation",
                "usage-example", "contributing", "changelog",
                "roadmap", "tutorial", "general"
            ],
            "supports_any_repository": True,
            "quality": "good",
            "fallback_for": ["Documentation", "README", "Guides", "Tutorials", "API Docs"],
            "features": [
                "Document structure analysis", "Quality scoring",
                "Section splitting", "Content type detection"
            ]
        }