#!/usr/bin/env python3
"""
Automated Build Pipeline for Registry Updates

This script provides automated scheduling and execution of registry extraction
pipelines with monitoring, error handling, and notification capabilities.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

import aiohttp
import aiofiles
from croniter import croniter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.real_extraction_pipeline import RealExtractionPipeline
from services.registry_config_manager import RegistryConfigManager
from models import Component, ComponentCategory, ComponentType
from utils.logger import setup_logging

class BuildStatus(Enum):
    """Build status values"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationType(Enum):
    """Notification types"""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    CONSOLE = "console"

@dataclass
class BuildConfig:
    """Configuration for automated builds"""
    registry_name: str
    schedule: str  # Cron expression
    enabled: bool = True
    source_filter: Optional[str] = None
    notification_types: List[NotificationType] = None
    notification_targets: List[str] = None
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout_minutes: int = 30
    quality_threshold: float = 0.7

    def __post_init__(self):
        if self.notification_types is None:
            self.notification_types = [NotificationType.CONSOLE]
        if self.notification_targets is None:
            self.notification_targets = []

@dataclass
class BuildResult:
    """Result of a build execution"""
    build_id: str
    registry_name: str
    status: BuildStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    components_extracted: int = 0
    sources_processed: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BuildHistory:
    """History of build executions"""
    builds: List[BuildResult]
    total_builds: int
    success_rate: float
    average_duration: float
    last_build: Optional[BuildResult] = None

class NotificationService:
    """Service for sending build notifications"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def send_notification(
        self,
        notification_type: NotificationType,
        target: str,
        message: str,
        build_result: BuildResult
    ) -> bool:
        """Send notification based on type"""
        try:
            if notification_type == NotificationType.WEBHOOK:
                return await self._send_webhook(target, message, build_result)
            elif notification_type == NotificationType.SLACK:
                return await self._send_slack(target, message, build_result)
            elif notification_type == NotificationType.EMAIL:
                return await self._send_email(target, message, build_result)
            elif notification_type == NotificationType.CONSOLE:
                return self._send_console(message, build_result)
        except Exception as e:
            self.logger.error(f"Failed to send {notification_type.value} notification: {e}")
            return False

        return False

    async def _send_webhook(
        self,
        url: str,
        message: str,
        build_result: BuildResult
    ) -> bool:
        """Send webhook notification"""
        if not self.session:
            return False

        # Convert BuildStatus enum to string for JSON serialization
        build_result_dict = asdict(build_result)
        build_result_dict['status'] = build_result.status.value

        payload = {
            "message": message,
            "build_result": build_result_dict,
            "timestamp": datetime.now().isoformat()
        }

        try:
            async with self.session.post(url, json=payload, timeout=30) as response:
                return response.status < 400
        except Exception as e:
            self.logger.error(f"Webhook failed: {e}")
            return False

    async def _send_slack(
        self,
        webhook_url: str,
        message: str,
        build_result: BuildResult
    ) -> bool:
        """Send Slack notification"""
        if not self.session:
            return False

        # Determine color based on status
        color = {
            BuildStatus.SUCCESS: "good",
            BuildStatus.FAILED: "danger",
            BuildStatus.RUNNING: "warning",
            BuildStatus.PENDING: "#cccccc"
        }.get(build_result.status, "#cccccc")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"Registry Build: {build_result.registry_name}",
                    "text": message,
                    "fields": [
                        {"title": "Status", "value": build_result.status.value, "short": True},
                        {"title": "Duration", "value": f"{build_result.duration_seconds:.1f}s", "short": True},
                        {"title": "Components", "value": str(build_result.components_extracted), "short": True},
                        {"title": "Sources", "value": str(build_result.sources_processed), "short": True}
                    ],
                    "footer": "SimFlo RAG Build Pipeline",
                    "ts": int(build_result.start_time.timestamp())
                }
            ]
        }

        try:
            async with self.session.post(webhook_url, json=payload, timeout=30) as response:
                return response.status < 400
        except Exception as e:
            self.logger.error(f"Slack notification failed: {e}")
            return False

    async def _send_email(
        self,
        email_address: str,
        message: str,
        build_result: BuildResult
    ) -> bool:
        """Send email notification (placeholder implementation)"""
        self.logger.info(f"Email notification to {email_address}: {message}")
        # In a real implementation, integrate with email service
        return True

    def _send_console(self, message: str, build_result: BuildResult) -> bool:
        """Send console notification"""
        timestamp = build_result.start_time.strftime("%Y-%m-%d %H:%M:%S")
        status_color = {
            BuildStatus.SUCCESS: "\033[92m",  # Green
            BuildStatus.FAILED: "\033[91m",   # Red
            BuildStatus.RUNNING: "\033[93m",  # Yellow
            BuildStatus.PENDING: "\033[90m"   # Gray
        }.get(build_result.status, "\033[0m")

        reset_color = "\033[0m"

        print(f"\n{status_color}[{timestamp}] {message}{reset_color}")
        print(f"  Registry: {build_result.registry_name}")
        print(f"  Status: {build_result.status.value}")
        print(f"  Duration: {build_result.duration_seconds:.1f}s")
        print(f"  Components: {build_result.components_extracted}")
        print(f"  Sources: {build_result.sources_processed}")

        if build_result.errors:
            print(f"  Errors: {len(build_result.errors)}")
            for error in build_result.errors[:3]:  # Show first 3 errors
                print(f"    - {error}")

        return True

class AutomatedBuildPipeline:
    """Automated build pipeline for registry updates"""

    def __init__(
        self,
        config_dir: str = "rag_databases/registry_config",
        output_dir: str = "rag_databases/extracted_data",
        build_history_dir: str = "rag_databases/build_history"
    ):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.build_history_dir = Path(build_history_dir)
        self.registry_manager = RegistryConfigManager(str(config_dir))
        self.build_configs: Dict[str, BuildConfig] = {}
        self.build_history: Dict[str, List[BuildResult]] = {}
        self.running_builds: Dict[str, asyncio.Task] = {}

        # Setup logging
        setup_logging(level="INFO")
        self.logger = logging.getLogger(__name__)

        # Create directories
        self.build_history_dir.mkdir(parents=True, exist_ok=True)

        # Load build configurations
        self._load_build_configs()
        self._load_build_history()

    def _load_build_configs(self):
        """Load build configurations from registry configs"""
        registries = self.registry_manager.get_all_registries()

        for registry in registries:
            # Use the build configuration from the registry config
            build_cfg = registry.build_configuration

            build_config = BuildConfig(
                registry_name=registry.registry_name,
                schedule=build_cfg.schedule,
                enabled=build_cfg.build_enabled,
                notification_types=[
                    NotificationType(nt) for nt in
                    build_cfg.notification_types
                ],
                notification_targets=build_cfg.notification_targets,
                retry_on_failure=build_cfg.retry_on_failure,
                max_retries=build_cfg.max_retries,
                timeout_minutes=build_cfg.timeout_minutes,
                quality_threshold=build_cfg.quality_threshold
            )

            self.build_configs[registry.registry_name] = build_config
            self.logger.info(f"Loaded build config for registry: {registry.registry_name}")

    def _load_build_history(self):
        """Load build history from files"""
        for history_file in self.build_history_dir.glob("*.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

                registry_name = history_file.stem
                self.build_history[registry_name] = [
                    BuildResult(
                        build_id=result["build_id"],
                        registry_name=result["registry_name"],
                        status=BuildStatus(result["status"]),
                        start_time=datetime.fromisoformat(result["start_time"]),
                        end_time=datetime.fromisoformat(result["end_time"]) if result["end_time"] else None,
                        duration_seconds=result["duration_seconds"],
                        components_extracted=result["components_extracted"],
                        sources_processed=result["sources_processed"],
                        errors=result["errors"],
                        warnings=result["warnings"],
                        metadata=result["metadata"]
                    )
                    for result in history_data.get("builds", [])
                ]

                self.logger.info(f"Loaded build history for {registry_name}: {len(self.build_history[registry_name])} builds")

            except Exception as e:
                self.logger.error(f"Failed to load build history from {history_file}: {e}")

    def _save_build_history(self, registry_name: str):
        """Save build history to file"""
        if registry_name not in self.build_history:
            return

        history_file = self.build_history_dir / f"{registry_name}.json"
        history_data = {
            "registry_name": registry_name,
            "builds": [asdict(build) for build in self.build_history[registry_name]]
        }

        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save build history for {registry_name}: {e}")

    def get_next_run_time(self, registry_name: str) -> Optional[datetime]:
        """Get next scheduled run time for a registry"""
        if registry_name not in self.build_configs:
            return None

        config = self.build_configs[registry_name]
        if not config.enabled:
            return None

        try:
            cron = croniter(config.schedule, datetime.now())
            return cron.get_next(datetime)
        except Exception as e:
            self.logger.error(f"Invalid cron expression for {registry_name}: {config.schedule}")
            return None

    def get_build_history_summary(self, registry_name: str) -> BuildHistory:
        """Get build history summary for a registry"""
        if registry_name not in self.build_history:
            return BuildHistory(builds=[], total_builds=0, success_rate=0.0, average_duration=0.0)

        builds = self.build_history[registry_name]
        if not builds:
            return BuildHistory(builds=[], total_builds=0, success_rate=0.0, average_duration=0.0)

        successful_builds = [b for b in builds if b.status == BuildStatus.SUCCESS]
        total_builds = len(builds)
        success_rate = len(successful_builds) / total_builds if total_builds > 0 else 0.0
        average_duration = sum(b.duration_seconds for b in builds) / total_builds if total_builds > 0 else 0.0

        return BuildHistory(
            builds=builds[-50:],  # Return last 50 builds
            total_builds=total_builds,
            success_rate=success_rate,
            average_duration=average_duration,
            last_build=builds[-1] if builds else None
        )

    async def run_build(
        self,
        registry_name: str,
        source_filter: Optional[str] = None,
        timeout_minutes: Optional[int] = None
    ) -> BuildResult:
        """Run a build for a specific registry"""
        if registry_name in self.running_builds:
            raise ValueError(f"Build already running for registry: {registry_name}")

        config = self.build_configs.get(registry_name)
        if not config or not config.enabled:
            raise ValueError(f"No enabled build configuration for registry: {registry_name}")

        # Create build result
        build_id = f"{registry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        build_result = BuildResult(
            build_id=build_id,
            registry_name=registry_name,
            status=BuildStatus.RUNNING,
            start_time=datetime.now()
        )

        # Add to history
        if registry_name not in self.build_history:
            self.build_history[registry_name] = []
        self.build_history[registry_name].append(build_result)

        # Start build task
        task = asyncio.create_task(
            self._execute_build(
                build_result,
                config,
                source_filter or config.source_filter,
                timeout_minutes or config.timeout_minutes
            )
        )
        self.running_builds[registry_name] = task

        try:
            await task
        except asyncio.CancelledError:
            build_result.status = BuildStatus.CANCELLED
            build_result.end_time = datetime.now()
            build_result.duration_seconds = (build_result.end_time - build_result.start_time).total_seconds()
            build_result.errors.append("Build cancelled by user")

        finally:
            self.running_builds.pop(registry_name, None)
            self._save_build_history(registry_name)

        return build_result

    async def _execute_build(
        self,
        build_result: BuildResult,
        config: BuildConfig,
        source_filter: Optional[str],
        timeout_minutes: int
    ) -> None:
        """Execute the actual build process"""
        async with NotificationService(self.logger) as notifier:
            try:
                # Send start notification
                await notifier.send_notification(
                    NotificationType.CONSOLE,
                    "",
                    f"🚀 Starting build for {build_result.registry_name}",
                    build_result
                )

                # Send notifications to configured targets
                for notification_type, target in zip(config.notification_types, config.notification_targets):
                    await notifier.send_notification(
                        notification_type,
                        target,
                        f"🚀 Starting build for {build_result.registry_name}",
                        build_result
                    )

                # Create extraction pipeline
                pipeline = RealExtractionPipeline(
                    config_dir=str(self.config_dir),
                    output_dir=str(self.output_dir)
                )

                # Run extraction with timeout
                try:
                    extraction_result = await asyncio.wait_for(
                        pipeline.run_full_pipeline(
                            registry_name=config.registry_name,
                            source_name=source_filter
                        ),
                        timeout=timeout_minutes * 60
                    )

                    # Process results
                    build_result.end_time = datetime.now()
                    build_result.duration_seconds = (build_result.end_time - build_result.start_time).total_seconds()

                    if "error" in extraction_result.get("results", {}).get(config.registry_name, {}):
                        build_result.status = BuildStatus.FAILED
                        build_result.errors.append(extraction_result["results"][config.registry_name]["error"])
                    else:
                        build_result.status = BuildStatus.SUCCESS
                        build_result.components_extracted = extraction_result.get("pipeline_run", {}).get("total_components", 0)
                        build_result.sources_processed = len(extraction_result.get("results", {}).get(config.registry_name, {}).get("categories_extracted", {}))
                        build_result.metadata = extraction_result

                    # Check quality threshold
                    if config.quality_threshold > 0:
                        quality_score = self._calculate_quality_score(build_result)
                        if quality_score < config.quality_threshold:
                            build_result.status = BuildStatus.FAILED
                            build_result.errors.append(f"Quality score {quality_score:.2f} below threshold {config.quality_threshold}")

                except asyncio.TimeoutError:
                    build_result.status = BuildStatus.FAILED
                    build_result.end_time = datetime.now()
                    build_result.duration_seconds = (build_result.end_time - build_result.start_time).total_seconds()
                    build_result.errors.append(f"Build timed out after {timeout_minutes} minutes")

                except Exception as e:
                    build_result.status = BuildStatus.FAILED
                    build_result.end_time = datetime.now()
                    build_result.duration_seconds = (build_result.end_time - build_result.start_time).total_seconds()
                    build_result.errors.append(f"Build failed: {str(e)}")

                # Retry logic
                if build_result.status == BuildStatus.FAILED and config.retry_on_failure:
                    retry_count = 0
                    while retry_count < config.max_retries:
                        retry_count += 1
                        self.logger.info(f"Retrying build for {config.registry_name} (attempt {retry_count}/{config.max_retries})")

                        # Wait before retry
                        await asyncio.sleep(min(60 * retry_count, 300))  # Exponential backoff, max 5 minutes

                        try:
                            extraction_result = await asyncio.wait_for(
                                pipeline.run_full_pipeline(
                                    registry_name=config.registry_name,
                                    source_name=source_filter
                                ),
                                timeout=timeout_minutes * 60
                            )

                            # Update build result
                            if "error" not in extraction_result.get("results", {}).get(config.registry_name, {}):
                                build_result.status = BuildStatus.SUCCESS
                                build_result.components_extracted = extraction_result.get("pipeline_run", {}).get("total_components", 0)
                                build_result.sources_processed = len(extraction_result.get("results", {}).get(config.registry_name, {}).get("categories_extracted", {}))
                                build_result.metadata = extraction_result
                                build_result.errors.clear()
                                break

                        except Exception as retry_e:
                            self.logger.error(f"Retry {retry_count} failed: {retry_e}")
                            build_result.errors.append(f"Retry {retry_count} failed: {str(retry_e)}")

                # Send completion notification
                status_emoji = "✅" if build_result.status == BuildStatus.SUCCESS else "❌"
                await notifier.send_notification(
                    NotificationType.CONSOLE,
                    "",
                    f"{status_emoji} Build {build_result.status.value} for {build_result.registry_name}",
                    build_result
                )

                # Send notifications to configured targets
                for notification_type, target in zip(config.notification_types, config.notification_targets):
                    await notifier.send_notification(
                        notification_type,
                        target,
                        f"{status_emoji} Build {build_result.status.value} for {build_result.registry_name}",
                        build_result
                    )

            except Exception as e:
                self.logger.error(f"Build execution failed: {e}")
                build_result.status = BuildStatus.FAILED
                build_result.end_time = datetime.now()
                build_result.duration_seconds = (build_result.end_time - build_result.start_time).total_seconds()
                build_result.errors.append(f"Execution error: {str(e)}")

    def _calculate_quality_score(self, build_result: BuildResult) -> float:
        """Calculate quality score for a build result"""
        if build_result.status != BuildStatus.SUCCESS:
            return 0.0

        # Simple quality scoring based on components extracted and errors
        base_score = 1.0

        # Deduct for warnings
        warning_penalty = min(len(build_result.warnings) * 0.05, 0.3)

        # Bonus for component count
        component_bonus = min(build_result.components_extracted * 0.01, 0.2)

        # Calculate final score
        quality_score = base_score - warning_penalty + component_bonus
        return max(0.0, min(1.0, quality_score))

    async def run_scheduled_builds(self) -> List[BuildResult]:
        """Run all builds that are scheduled to run now"""
        current_time = datetime.now()
        results = []

        for registry_name, config in self.build_configs.items():
            if not config.enabled:
                continue

            next_run = self.get_next_run_time(registry_name)
            if not next_run:
                continue

            # Check if build should run now (within 1 minute window)
            if abs((next_run - current_time).total_seconds()) <= 60:
                try:
                    result = await self.run_build(registry_name)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to run scheduled build for {registry_name}: {e}")

        return results

    async def cancel_build(self, registry_name: str) -> bool:
        """Cancel a running build"""
        if registry_name not in self.running_builds:
            return False

        task = self.running_builds[registry_name]
        if not task.cancelled():
            task.cancel()
            return True

        return False

    def get_running_builds(self) -> List[str]:
        """Get list of registries with running builds"""
        return list(self.running_builds.keys())

    def get_build_queue(self) -> List[str]:
        """Get list of registries with pending builds"""
        current_time = datetime.now()
        queue = []

        for registry_name, config in self.build_configs.items():
            if not config.enabled:
                continue

            next_run = self.get_next_run_time(registry_name)
            if not next_run:
                continue

            # Check if build is scheduled within the next hour
            if 0 < (next_run - current_time).total_seconds() <= 3600:
                queue.append(registry_name)

        return queue

    def cleanup_old_builds(self, days_to_keep: int = 30):
        """Clean up old build history"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        for registry_name, builds in self.build_history.items():
            # Keep only builds newer than cutoff date
            self.build_history[registry_name] = [
                build for build in builds
                if build.start_time > cutoff_date
            ]

            # Save cleaned history
            self._save_build_history(registry_name)

            self.logger.info(f"Cleaned up old builds for {registry_name}, kept {len(self.build_history[registry_name])} builds")

async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Build Pipeline for Registry Updates")
    parser.add_argument("--registry", "-r", help="Specific registry to build")
    parser.add_argument("--source", "-s", help="Specific source to process")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in minutes")
    parser.add_argument("--schedule", action="store_true", help="Run scheduled builds")
    parser.add_argument("--status", action="store_true", help="Show build status")
    parser.add_argument("--history", help="Show build history for registry")
    parser.add_argument("--cancel", help="Cancel running build for registry")
    parser.add_argument("--cleanup", type=int, help="Clean up builds older than N days")

    args = parser.parse_args()

    pipeline = AutomatedBuildPipeline()

    try:
        if args.registry:
            # Run specific build
            result = await pipeline.run_build(args.registry, args.source, args.timeout)
            print(f"Build completed: {result.status.value}")

        elif args.schedule:
            # Run scheduled builds
            results = await pipeline.run_scheduled_builds()
            print(f"Ran {len(results)} scheduled builds")

        elif args.status:
            # Show status
            running = pipeline.get_running_builds()
            queue = pipeline.get_build_queue()

            print(f"Running builds: {len(running)}")
            for registry in running:
                print(f"  - {registry}")

            print(f"Queued builds: {len(queue)}")
            for registry in queue:
                next_run = pipeline.get_next_run_time(registry)
                print(f"  - {registry} (next: {next_run})")

        elif args.history:
            # Show build history
            summary = pipeline.get_build_history_summary(args.history)
            print(f"Build history for {args.history}:")
            print(f"  Total builds: {summary.total_builds}")
            print(f"  Success rate: {summary.success_rate:.1%}")
            print(f"  Average duration: {summary.average_duration:.1f}s")

            if summary.last_build:
                print(f"  Last build: {summary.last_build.status.value} at {summary.last_build.start_time}")

        elif args.cancel:
            # Cancel build
            success = await pipeline.cancel_build(args.cancel)
            print(f"Build cancelled: {success}")

        elif args.cleanup:
            # Clean up old builds
            pipeline.cleanup_old_builds(args.cleanup)
            print(f"Cleaned up builds older than {args.cleanup} days")

        else:
            # Interactive mode
            print("Automated Build Pipeline")
            print("=" * 40)

            while True:
                print("\nOptions:")
                print("1. Run build for registry")
                print("2. Run scheduled builds")
                print("3. Show status")
                print("4. Show build history")
                print("5. Cancel build")
                print("6. Exit")

                choice = input("\nEnter choice (1-6): ").strip()

                if choice == "1":
                    registry = input("Enter registry name: ").strip()
                    source = input("Enter source filter (optional): ").strip() or None
                    timeout = int(input("Enter timeout in minutes (default 30): ").strip() or "30")

                    result = await pipeline.run_build(registry, source, timeout)
                    print(f"Build completed: {result.status.value}")

                elif choice == "2":
                    results = await pipeline.run_scheduled_builds()
                    print(f"Ran {len(results)} scheduled builds")

                elif choice == "3":
                    running = pipeline.get_running_builds()
                    queue = pipeline.get_build_queue()

                    print(f"Running builds: {len(running)}")
                    for registry in running:
                        print(f"  - {registry}")

                    print(f"Queued builds: {len(queue)}")
                    for registry in queue:
                        next_run = pipeline.get_next_run_time(registry)
                        print(f"  - {registry} (next: {next_run})")

                elif choice == "4":
                    registry = input("Enter registry name: ").strip()
                    summary = pipeline.get_build_history_summary(registry)
                    print(f"Build history for {registry}:")
                    print(f"  Total builds: {summary.total_builds}")
                    print(f"  Success rate: {summary.success_rate:.1%}")
                    print(f"  Average duration: {summary.average_duration:.1f}s")

                    if summary.last_build:
                        print(f"  Last build: {summary.last_build.status.value} at {summary.last_build.start_time}")

                elif choice == "5":
                    registry = input("Enter registry name: ").strip()
                    success = await pipeline.cancel_build(registry)
                    print(f"Build cancelled: {success}")

                elif choice == "6":
                    break

                else:
                    print("Invalid choice. Please try again.")

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())