#!/usr/bin/env python3
"""
SimFlo MCP RAG - Data Pipeline Orchestrator

Central orchestration system for managing component extraction workflows.
Supports multiple extractors, post-processing, and quality control.
"""

import json
import sys
import os
import re
import argparse
import logging
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess


class PipelineOrchestrator:
    """Main orchestrator for data extraction pipelines"""

    def __init__(self, config_path: str = None):
        """Initialize orchestrator with configuration"""
        self.config_path = config_path or "config/pipeline_config.json"
        self.config = self._load_config()
        self.setup_logging()

        # Create output directories
        self.base_output_dir = Path(self.config["pipeline"]["default_output_dir"])
        self.temp_dir = Path(self.config["pipeline"]["temp_dir"])
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        try:
            config_file = Path(self.config_path)
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid configuration file: {e}")

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config["orchestration"]["log_level"]
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are met"""
        prerequisites = {
            "python": True,  # We're running, so Python is available
            "git": self._check_command("git", ["--version"]),
            "gh_cli": self._check_command("gh", ["--version"]),
        }

        # Check if required extractors exist
        extractor_dir = Path(__file__).parent / "github-extractor"
        prerequisites["github_cli_extractor"] = (extractor_dir / "github_cli_extractor.py").exists()
        prerequisites["github_basic_extractor"] = (extractor_dir / "github_extractor.py").exists()

        return prerequisites

    def _check_command(self, command: str, args: List[str]) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run([command] + args, capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List available extraction profiles"""
        profiles = []
        for name, profile in self.config["extractor_profiles"].items():
            profiles.append({
                "name": name,
                "display_name": profile["name"],
                "description": profile.get("description", ""),
                "repository": profile["repository"],
                "extractor": profile["extractor"],
                "output_path": profile["output_path"]
            })
        return profiles

    def validate_profile(self, profile_name: str) -> Dict[str, Any]:
        """Validate a specific profile"""
        if profile_name not in self.config["extractor_profiles"]:
            return {"valid": False, "errors": [f"Profile '{profile_name}' not found"]}

        profile = self.config["extractor_profiles"][profile_name]
        errors = []

        # Check extractor exists
        extractor_name = profile["extractor"]
        if extractor_name not in self.config["extractors"]:
            errors.append(f"Extractor '{extractor_name}' not found")

        # Check if GitHub CLI is required and available
        extractor_config = self.config["extractors"].get(extractor_name, {})
        if extractor_config.get("requires_gh_cli", False):
            if not self._check_command("gh", ["--version"]):
                errors.append("GitHub CLI (gh) is required but not installed")

        # Validate repository format
        repo_identifier = profile["repository"]
        if not self._validate_repo_identifier(repo_identifier):
            errors.append(f"Invalid repository identifier: {repo_identifier}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "profile": profile
        }

    def _validate_repo_identifier(self, repo_identifier: str) -> bool:
        """Validate repository identifier format"""
        # Accept various formats: owner/repo, https://github.com/owner/repo, git@github.com:owner/repo.git
        patterns = [
            r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$',  # owner/repo
            r'^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+',  # HTTPS URL
            r'^git@github\.com:[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git$',  # SSH URL
        ]

        return any(re.match(pattern, repo_identifier) for pattern in patterns)

    def run_extraction(self, profile_name: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run extraction for a specific profile"""
        validation = self.validate_profile(profile_name)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
                "profile": profile_name
            }

        profile = validation["profile"]
        self.logger.info(f"Starting extraction for profile: {profile_name}")

        try:
            # Build extraction command
            extractor_dir = Path(__file__).parent / "github-extractor"
            extractor_config = self.config["extractors"][profile["extractor"]]
            extractor_script = extractor_dir / extractor_config["executable"]

            if not extractor_script.exists():
                raise FileNotFoundError(f"Extractor script not found: {extractor_script}")

            # Prepare command arguments
            cmd = [
                "python3", str(extractor_script),
                profile["repository"]
            ]

            # Add output path
            output_path = Path(profile["output_path"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cmd.extend(["--output", str(output_path)])

            # Add verbose flag if requested
            if options and options.get("verbose"):
                cmd.append("--verbose")

            # Add metadata-only flag if requested
            if options and options.get("metadata_only"):
                cmd.append("--metadata-only")

            # Run extraction
            self.logger.info(f"Running extraction command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["orchestration"]["timeout"]
            )

            if result.returncode == 0:
                # Process successful extraction
                extraction_result = {
                    "success": True,
                    "profile": profile_name,
                    "output_path": str(output_path),
                    "command_output": result.stdout,
                    "extracted_at": datetime.now().isoformat()
                }

                # Run post-processing if configured
                if profile.get("post_processor"):
                    post_process_result = self._run_post_processing(
                        profile_name, output_path, profile["post_processor"]
                    )
                    extraction_result["post_processing"] = post_process_result

                return extraction_result
            else:
                return {
                    "success": False,
                    "profile": profile_name,
                    "errors": [f"Extraction failed with return code {result.returncode}"],
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "profile": profile_name,
                "errors": ["Extraction timed out"]
            }
        except Exception as e:
            return {
                "success": False,
                "profile": profile_name,
                "errors": [str(e)]
            }

    def _run_post_processing(self, profile_name: str, output_path: Path, processor_name: str) -> Dict[str, Any]:
        """Run post-processing on extracted components"""
        self.logger.info(f"Running post-processing: {processor_name}")

        try:
            if processor_name not in self.config["post_processors"]:
                return {"success": False, "error": f"Post processor '{processor_name}' not found"}

            processor_config = self.config["post_processors"][processor_name]

            # For now, implement basic post-processing
            # In a more advanced version, this could be a separate script
            with open(output_path, 'r') as f:
                data = json.load(f)

            # Apply post-processing logic
            processed_data = self._apply_post_processing(data, processor_config, profile_name)

            # Save processed data
            with open(output_path, 'w') as f:
                json.dump(processed_data, f, indent=2)

            return {
                "success": True,
                "processor": processor_name,
                "changes_applied": "basic_enhancement"
            }

        except Exception as e:
            return {
                "success": False,
                "processor": processor_name,
                "error": str(e)
            }

    def _apply_post_processing(self, data: Dict, processor_config: Dict, profile_name: str) -> Dict:
        """Apply post-processing logic to extracted data"""
        # Basic enhancement - can be extended with more sophisticated processing
        if "components" in data:
            for component in data["components"]:
                # Add profile-specific tags
                if "tags" not in component:
                    component["tags"] = []
                component["tags"].extend([profile_name, "processed"])

                # Add processing metadata
                component["processed_at"] = datetime.now().isoformat()
                component["processor"] = processor_config["name"]

        return data

    def run_multiple_extractions(self, profile_names: List[str], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run multiple extractions concurrently"""
        self.logger.info(f"Starting multiple extractions for profiles: {profile_names}")

        max_concurrent = self.config["orchestration"]["max_concurrent_extractions"]
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all extraction tasks
            future_to_profile = {
                executor.submit(self.run_extraction, profile, options): profile
                for profile in profile_names
            }

            # Collect results
            for future in concurrent.futures.as_completed(future_to_profile):
                profile = future_to_profile[future]
                try:
                    result = future.result()
                    results[profile] = result
                    self.logger.info(f"Completed extraction for {profile}: {'✅' if result['success'] else '❌'}")
                except Exception as e:
                    results[profile] = {
                        "success": False,
                        "profile": profile,
                        "errors": [str(e)]
                    }

        return results

    def discovery_mode(self, keywords: List[str], limit: int = 10) -> Dict[str, Any]:
        """Discover repositories using GitHub CLI"""
        self.logger.info(f"Starting discovery mode with keywords: {keywords}")

        try:
            # Build search query
            search_query = " ".join([f"topic:{keyword}" for keyword in keywords])
            search_query += " language:typescript stars:>100"  # Focus on popular TypeScript repos

            # Search for repositories
            cmd = [
                "gh", "repo", "list",
                "--limit", str(limit),
                "--json", "name,owner,description,language,stargazerCount,topics,updatedAt",
                "--search", search_query,
                "--order", "desc",
                "--sort", "stars"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            repositories = json.loads(result.stdout)

            return {
                "success": True,
                "query": search_query,
                "repositories": repositories,
                "count": len(repositories)
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"GitHub CLI search failed: {e.stderr}"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse search results: {e}"
            }

    def generate_report(self) -> Dict[str, Any]:
        """Generate pipeline status report"""
        prerequisites = self.check_prerequisites()
        profiles = self.list_profiles()

        # Check output directories
        output_status = {}
        for profile in profiles:
            output_path = Path(profile["output_path"])
            output_status[profile["name"]] = {
                "exists": output_path.exists(),
                "size": output_path.stat().st_size if output_path.exists() else 0,
                "modified": output_path.stat().st_mtime if output_path.exists() else None
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "prerequisites": prerequisites,
            "profiles": profiles,
            "output_status": output_status,
            "configuration": {
                "max_concurrent": self.config["orchestration"]["max_concurrent_extractions"],
                "timeout": self.config["orchestration"]["timeout"]
            }
        }


def main():
    """Command line interface for the orchestrator"""
    parser = argparse.ArgumentParser(description='SimFlo MCP RAG Data Pipeline Orchestrator')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List profiles command
    list_parser = subparsers.add_parser('list-profiles', help='List available extraction profiles')

    # Validate profile command
    validate_parser = subparsers.add_parser('validate', help='Validate extraction profile')
    validate_parser.add_argument('profile', help='Profile name to validate')

    # Run extraction command
    run_parser = subparsers.add_parser('run', help='Run extraction for a profile')
    run_parser.add_argument('profile', help='Profile name to run')
    run_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    run_parser.add_argument('--metadata-only', action='store_true', help='Only extract metadata')

    # Run multiple extractions
    multi_parser = subparsers.add_parser('run-multiple', help='Run multiple extractions')
    multi_parser.add_argument('profiles', nargs='+', help='Profile names to run')
    multi_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # Discovery mode
    discovery_parser = subparsers.add_parser('discover', help='Discover repositories')
    discovery_parser.add_argument('keywords', nargs='+', help='Search keywords')
    discovery_parser.add_argument('--limit', type=int, default=10, help='Number of results')

    # Status report
    status_parser = subparsers.add_parser('status', help='Generate pipeline status report')

    # Check prerequisites
    check_parser = subparsers.add_parser('check', help='Check pipeline prerequisites')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        orchestrator = PipelineOrchestrator()

        if args.command == 'list-profiles':
            profiles = orchestrator.list_profiles()
            print(f"Available Extraction Profiles ({len(profiles)}):")
            for profile in profiles:
                print(f"  • {profile['name']}: {profile['display_name']}")
                print(f"    Repository: {profile['repository']}")
                print(f"    Extractor: {profile['extractor']}")
                print(f"    Output: {profile['output_path']}")
                print()

        elif args.command == 'validate':
            validation = orchestrator.validate_profile(args.profile)
            if validation['valid']:
                print(f"✅ Profile '{args.profile}' is valid")
            else:
                print(f"❌ Profile '{args.profile}' has issues:")
                for error in validation['errors']:
                    print(f"  • {error}")

        elif args.command == 'run':
            options = {
                'verbose': args.verbose,
                'metadata_only': args.metadata_only
            }
            result = orchestrator.run_extraction(args.profile, options)

            if result['success']:
                print(f"✅ Extraction completed for '{args.profile}'")
                print(f"Output: {result['output_path']}")
            else:
                print(f"❌ Extraction failed for '{args.profile}'")
                for error in result.get('errors', []):
                    print(f"  • {error}")

        elif args.command == 'run-multiple':
            options = {'verbose': args.verbose}
            results = orchestrator.run_multiple_extractions(args.profiles, options)

            print(f"Multiple Extraction Results:")
            for profile, result in results.items():
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {profile}: {result.get('output_path', 'Failed')}")

        elif args.command == 'discover':
            result = orchestrator.discovery_mode(args.keywords, args.limit)

            if result['success']:
                print(f"Found {result['count']} repositories for keywords: {args.keywords}")
                for repo in result['repositories']:
                    stars = repo.get('stargazerCount', 0)
                    language = repo.get('language', 'Unknown')
                    print(f"  • {repo['owner']['login']}/{repo['name']} ({language}, ⭐ {stars})")
                    if repo.get('description'):
                        print(f"    {repo['description']}")
            else:
                print(f"❌ Discovery failed: {result.get('error')}")

        elif args.command == 'status':
            report = orchestrator.generate_report()
            print("Pipeline Status Report:")
            print(f"Generated: {report['timestamp']}")
            print(f"Max concurrent extractions: {report['configuration']['max_concurrent']}")
            print(f"Timeout: {report['configuration']['timeout']} seconds")
            print()

            print("Prerequisites:")
            for prereq, status in report['prerequisites'].items():
                print(f"  {'✅' if status else '❌'} {prereq}")
            print()

            print("Output Status:")
            for profile, status in report['output_status'].items():
                if status['exists']:
                    size_kb = status['size'] / 1024
                    print(f"  ✅ {profile}: {size_kb:.1f} KB")
                else:
                    print(f"  ❌ {profile}: Not found")

        elif args.command == 'check':
            prerequisites = orchestrator.check_prerequisites()
            print("Pipeline Prerequisites Check:")
            all_good = True
            for prereq, status in prerequisites.items():
                icon = "✅" if status else "❌"
                print(f"  {icon} {prereq}")
                if not status:
                    all_good = False

            if all_good:
                print("\n🎉 All prerequisites are satisfied!")
            else:
                print("\n❌ Some prerequisites are missing. Please install required dependencies.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()