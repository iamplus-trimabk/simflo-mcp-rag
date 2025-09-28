#!/usr/bin/env python3
"""
Test script for the automated build pipeline
"""

import asyncio
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_build_pipeline import AutomatedBuildPipeline, BuildStatus, BuildConfig
from services.registry_config_manager import RegistryConfigManager, RegistryConfig, BuildConfig as RegistryBuildConfig
from models import Component, ComponentCategory, ComponentType

async def test_build_pipeline():
    """Test the automated build pipeline"""
    print("🚀 Testing Automated Build Pipeline")
    print("=" * 50)

    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_dir = temp_path / "config"
        output_dir = temp_path / "output"
        history_dir = temp_path / "history"

        # Create directories
        config_dir.mkdir()
        output_dir.mkdir()
        history_dir.mkdir()

        # Create a test registry configuration
        test_registry = {
            "registry_name": "test_registry",
            "display_name": "Test Registry",
            "description": "Test registry for automated build pipeline",
            "platforms": ["web"],
            "database_path": "test.db",
            "status": "active",
            "categories": {
                "components": {
                    "enabled": True,
                    "sources": [],
                    "metadata": {}
                }
            },
            "search_configuration": {
                "cross_category_search": True,
                "default_category": "components",
                "category_weights": {"components": 0.6, "hooks": 0.3, "blocks": 0.1},
                "source_boosting": {"official": 1.2, "community": 0.8, "third_party": 0.6}
            },
            "build_configuration": {
                "build_enabled": True,
                "schedule": "0 2 * * *",
                "notification_types": ["console"],
                "notification_targets": [],
                "retry_on_failure": True,
                "max_retries": 2,
                "timeout_minutes": 5,
                "quality_threshold": 0.7,
                "parallel_builds": False,
                "cleanup_days": 30,
                "health_check_interval": 300,
                "auto_deploy": True
            },
            "metadata": {
                "test": True
            }
        }

        # Save test registry configuration
        registry_file = config_dir / "test_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(test_registry, f, indent=2)

        # Create automated build pipeline
        pipeline = AutomatedBuildPipeline(
            config_dir=str(config_dir),
            output_dir=str(output_dir),
            build_history_dir=str(history_dir)
        )

        print("✅ Build pipeline initialized")

        # Test 1: Check build configuration loading
        print("\n📋 Test 1: Build Configuration Loading")
        configs = pipeline.build_configs
        assert "test_registry" in configs, "Test registry not found in build configs"
        assert configs["test_registry"].enabled == True, "Build should be enabled"
        assert configs["test_registry"].schedule == "0 2 * * *", "Schedule not loaded correctly"
        print(f"Debug: max_retries = {configs['test_registry'].max_retries}")
        assert configs["test_registry"].max_retries == 2, "Max retries not loaded correctly"
        print("✅ Build configuration loaded successfully")

        # Test 2: Check next run time calculation
        print("\n📋 Test 2: Next Run Time Calculation")
        next_run = pipeline.get_next_run_time("test_registry")
        assert next_run is not None, "Next run time should be calculated"
        assert next_run > datetime.now(), "Next run time should be in the future"
        print(f"✅ Next run time calculated: {next_run}")

        # Test 3: Test build queue
        print("\n📋 Test 3: Build Queue")
        queue = pipeline.get_build_queue()
        assert isinstance(queue, list), "Queue should be a list"
        print(f"✅ Build queue contains {len(queue)} registries")

        # Test 4: Test running builds tracking
        print("\n📋 Test 4: Running Builds Tracking")
        running = pipeline.get_running_builds()
        assert isinstance(running, list), "Running builds should be a list"
        assert len(running) == 0, "No builds should be running initially"
        print("✅ Running builds tracking works correctly")

        # Test 5: Test build history
        print("\n📋 Test 5: Build History")
        history = pipeline.get_build_history_summary("test_registry")
        assert history.total_builds == 0, "Initial build history should be empty"
        assert history.success_rate == 0.0, "Initial success rate should be 0"
        print("✅ Build history works correctly")

        # Test 6: Test build queue management
        print("\n📋 Test 6: Build Queue Management")
        queue = pipeline.get_build_queue()
        assert isinstance(queue, list), "Queue should be a list"
        print(f"✅ Build queue contains {len(queue)} registries")

        # Test 7: Test build cleanup
        print("\n📋 Test 7: Build Cleanup")
        pipeline.cleanup_old_builds(days_to_keep=0)
        print("✅ Build cleanup completed")

        print("\n🎉 All tests passed!")

async def test_notification_service():
    """Test the notification service"""
    print("\n🚀 Testing Notification Service")
    print("=" * 40)

    # Import here to avoid import issues if not available
    try:
        from scripts.automated_build_pipeline import NotificationService, NotificationType, BuildResult
        import logging

        # Set up logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Create a test build result
        build_result = BuildResult(
            build_id="test_build",
            registry_name="test_registry",
            status=BuildStatus.SUCCESS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=30.5,
            components_extracted=10,
            sources_processed=2,
            errors=[],
            warnings=["Test warning"],
            metadata={"test": True}
        )

        async with NotificationService(logger) as notifier:
            # Test console notification
            result = await notifier.send_notification(
                NotificationType.CONSOLE,
                "",
                "Test notification",
                build_result
            )
            assert result == True, "Console notification should succeed"
            print("✅ Console notification works")

            # Test webhook notification (will fail due to invalid URL, but should handle gracefully)
            result = await notifier.send_notification(
                NotificationType.WEBHOOK,
                "https://invalid-url.com/test",
                "Test webhook",
                build_result
            )
            print(f"✅ Webhook notification handled gracefully: {result}")

        print("✅ Notification service tests passed")

    except ImportError as e:
        print(f"⚠️  Notification service test skipped due to missing dependencies: {e}")

async def main():
    """Main test function"""
    try:
        await test_build_pipeline()
        await test_notification_service()
        print("\n🎉 All automated build pipeline tests completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)