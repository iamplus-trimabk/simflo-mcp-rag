#!/usr/bin/env python3
"""
Build Service for Automated Registry Updates

This script runs as a persistent service that monitors and executes
scheduled registry builds with comprehensive monitoring and health checks.
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_build_pipeline import AutomatedBuildPipeline, BuildStatus
from utils.logger import setup_logging

class BuildService:
    """Persistent service for automated registry builds"""

    def __init__(
        self,
        config_dir: str = "rag_databases/registry_config",
        output_dir: str = "rag_databases/extracted_data",
        history_dir: str = "rag_databases/build_history",
        check_interval: int = 60  # Check every minute
    ):
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.history_dir = history_dir
        self.check_interval = check_interval
        self.running = False
        self.pipeline: Optional[AutomatedBuildPipeline] = None
        self.logger = logging.getLogger(__name__)

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def start(self):
        """Start the build service"""
        self.logger.info("🚀 Starting Build Service")
        self.running = True

        # Initialize pipeline
        self.pipeline = AutomatedBuildPipeline(
            config_dir=self.config_dir,
            output_dir=self.output_dir,
            build_history_dir=self.history_dir
        )

        self.logger.info("✅ Build pipeline initialized")

        # Main service loop
        while self.running:
            try:
                await self._service_loop()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Service loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

        self.logger.info("🛑 Build service stopped")

    async def _service_loop(self):
        """Main service loop for checking and running builds"""
        current_time = datetime.now()

        # Check for scheduled builds
        scheduled_results = await self.pipeline.run_scheduled_builds()
        if scheduled_results:
            self.logger.info(f"📅 Executed {len(scheduled_results)} scheduled builds")

        # Log service status
        if current_time.minute % 5 == 0:  # Every 5 minutes
            await self._log_service_status()

    async def _log_service_status(self):
        """Log current service status"""
        if not self.pipeline:
            return

        running_builds = self.pipeline.get_running_builds()
        queued_builds = self.pipeline.get_build_queue()

        self.logger.info(f"📊 Service Status - Running: {len(running_builds)}, Queued: {len(queued_builds)}")

        # Log running builds
        for registry_name in running_builds:
            self.logger.info(f"🔨 Building: {registry_name}")

        # Log queued builds
        for registry_name in queued_builds:
            next_run = self.pipeline.get_next_run_time(registry_name)
            if next_run:
                wait_time = (next_run - datetime.now()).total_seconds()
                self.logger.info(f"⏳ Queued: {registry_name} (in {wait_time:.0f}s)")

    async def run_manual_build(self, registry_name: str, source_filter: Optional[str] = None) -> bool:
        """Run a manual build for a specific registry"""
        if not self.pipeline:
            self.logger.error("Pipeline not initialized")
            return False

        try:
            result = await self.pipeline.run_build(registry_name, source_filter)
            self.logger.info(f"✅ Manual build completed: {result.status.value}")
            return result.status == BuildStatus.SUCCESS
        except Exception as e:
            self.logger.error(f"❌ Manual build failed: {e}")
            return False

    async def get_service_health(self) -> Dict:
        """Get service health status"""
        if not self.pipeline:
            return {"status": "uninitialized", "message": "Pipeline not initialized"}

        running_builds = self.pipeline.get_running_builds()
        queued_builds = self.pipeline.get_build_queue()

        # Calculate some basic metrics
        total_registries = len(self.pipeline.build_configs)
        enabled_registries = len([c for c in self.pipeline.build_configs.values() if c.enabled])

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "running_builds": len(running_builds),
            "queued_builds": len(queued_builds),
            "total_registries": total_registries,
            "enabled_registries": enabled_registries,
            "uptime": "N/A"  # Could track actual uptime
        }

    def stop(self):
        """Stop the build service"""
        self.logger.info("Stopping build service...")
        self.running = False

async def main():
    """Main entry point for the build service"""
    import argparse

    parser = argparse.ArgumentParser(description="Build Service for Automated Registry Updates")
    parser.add_argument("--config", "-c", default="rag_databases/registry_config", help="Configuration directory")
    parser.add_argument("--output", "-o", default="rag_databases/extracted_data", help="Output directory")
    parser.add_argument("--history-dir", default="rag_databases/build_history", help="Build history directory")
    parser.add_argument("--interval", "-i", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--oneshot", action="store_true", help="Run once and exit")
    parser.add_argument("--build", "-b", help="Run manual build for specific registry")
    parser.add_argument("--source", "-s", help="Source filter for manual build")
    parser.add_argument("--health", action="store_true", help="Show service health")
    parser.add_argument("--status", action="store_true", help="Show detailed status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon service")

    args = parser.parse_args()

    # Setup logging
    setup_logging(level="INFO")
    logger = logging.getLogger(__name__)

    # Create service
    service = BuildService(
        config_dir=args.config,
        output_dir=args.output,
        history_dir=args.history_dir,
        check_interval=args.interval
    )

    try:
        if args.health:
            # Show health status
            health = await service.get_service_health()
            print(json.dumps(health, indent=2))
            return

        elif args.status:
            # Show detailed status
            pipeline = AutomatedBuildPipeline(args.config, args.output, args.history_dir)

            print("📊 Build Service Status")
            print("=" * 40)

            configs = pipeline.build_configs
            print(f"📋 Total registries: {len(configs)}")
            print(f"✅ Enabled registries: {len([c for c in configs.values() if c.enabled])}")

            running = pipeline.get_running_builds()
            print(f"🔨 Running builds: {len(running)}")
            for registry in running:
                print(f"  - {registry}")

            queue = pipeline.get_build_queue()
            print(f"⏳ Queued builds: {len(queue)}")
            for registry in queue:
                next_run = pipeline.get_next_run_time(registry)
                if next_run:
                    wait_time = (next_run - datetime.now()).total_seconds()
                    print(f"  - {registry} (in {wait_time:.0f}s)")

            # Show recent builds
            for registry_name in configs.keys():
                history = pipeline.get_build_history_summary(registry_name)
                if history.last_build:
                    print(f"📈 {registry_name}: {history.last_build.status.value} at {history.last_build.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        elif args.build:
            # Run manual build
            logger.info(f"🔨 Starting manual build for {args.build}")
            success = await service.run_manual_build(args.build, args.source)
            sys.exit(0 if success else 1)

        elif args.oneshot:
            # Run once and exit
            logger.info("🔄 Running one-time build check")
            await service.start()
            service.stop()

        else:
            # Run as service
            logger.info("🚀 Starting build service")
            if args.daemon:
                logger.info("🔒 Running in daemon mode")

            await service.start()

    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())