#!/usr/bin/env python3
"""
SimFlo MCP RAG - Context Management System

Manages platform context awareness for intelligent component search and routing.
"""

import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time


class PlatformContext(Enum):
    """Supported platform contexts"""
    REACT_NATIVE = "reactnative"
    REACT_JS = "reactjs"
    AUTO = "auto"  # Future: intelligent detection
    NONE = "none"  # No specific context


@dataclass
class ContextInfo:
    """Information about current context state"""
    platform: PlatformContext
    timestamp: float
    session_id: str
    user_agent: Optional[str] = None
    project_type: Optional[str] = None
    confidence: float = 1.0


@dataclass
class RegistryMapping:
    """Mapping between platform contexts and appropriate registries"""
    platform: PlatformContext
    primary_registries: List[str]
    fallback_registries: List[str]
    priority: int  # Higher number = higher priority


class ContextManager:
    """Manages platform context and registry routing"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize context manager"""
        self.config_path = config_path or "config/context_config.json"
        self.current_context: Optional[ContextInfo] = None
        self.context_history: List[ContextInfo] = []
        self.registry_mappings: List[RegistryMapping] = []
        self.session_counter = 0
        self.lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.setup_default_mappings()
        self.load_config()

    def setup_default_mappings(self):
        """Setup default platform-to-registry mappings"""
        self.registry_mappings = [
            RegistryMapping(
                platform=PlatformContext.REACT_NATIVE,
                primary_registries=["gluestack_db"],
                fallback_registries=["shadcn_db", "radix_db"],
                priority=10
            ),
            RegistryMapping(
                platform=PlatformContext.REACT_JS,
                primary_registries=["shadcn_db"],
                fallback_registries=["gluestack_db", "radix_db"],
                priority=10
            ),
            RegistryMapping(
                platform=PlatformContext.AUTO,
                primary_registries=["gluestack_db", "shadcn_db", "radix_db"],
                fallback_registries=[],
                priority=5
            ),
            RegistryMapping(
                platform=PlatformContext.NONE,
                primary_registries=["gluestack_db", "shadcn_db", "radix_db"],
                fallback_registries=[],
                priority=1
            )
        ]

    def load_config(self):
        """Load context configuration from file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Override default mappings if provided
                    if "registry_mappings" in config:
                        self.registry_mappings = [
                            RegistryMapping(**mapping)
                            for mapping in config["registry_mappings"]
                        ]
                    self.logger.info("Context configuration loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load context config: {e}")

    def set_context(
        self,
        platform: Union[PlatformContext, str],
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        project_type: Optional[str] = None,
        confidence: float = 1.0
    ) -> ContextInfo:
        """Set the current platform context"""
        with self.lock:
            # Convert string to enum if needed
            if isinstance(platform, str):
                try:
                    platform = PlatformContext(platform)
                except ValueError:
                    raise ValueError(f"Invalid platform context: {platform}")

            # Generate session ID if not provided
            if not session_id:
                self.session_counter += 1
                session_id = f"session_{self.session_counter}_{int(time.time())}"

            # Create new context info
            context_info = ContextInfo(
                platform=platform,
                timestamp=time.time(),
                session_id=session_id,
                user_agent=user_agent,
                project_type=project_type,
                confidence=confidence
            )

            # Update current context and history
            if self.current_context:
                self.context_history.append(self.current_context)

            self.current_context = context_info

            # Keep history manageable (last 50 contexts)
            if len(self.context_history) > 50:
                self.context_history = self.context_history[-50:]

            self.logger.info(f"Context set to {platform.value} for session {session_id}")
            return context_info

    def get_context(self, session_id: Optional[str] = None) -> Optional[ContextInfo]:
        """Get current context or context for specific session"""
        with self.lock:
            if session_id:
                # Find context for specific session
                for context in reversed(self.context_history + [self.current_context]):
                    if context and context.session_id == session_id:
                        return context
                return None

            return self.current_context

    def get_current_platform(self) -> PlatformContext:
        """Get current platform context"""
        context = self.get_context()
        return context.platform if context else PlatformContext.NONE

    def get_registries_for_context(
        self,
        platform: Optional[PlatformContext] = None,
        include_fallback: bool = True
    ) -> List[str]:
        """Get appropriate registries for given platform context"""
        if platform is None:
            platform = self.get_current_platform()

        # Find mapping for this platform
        mapping = None
        for m in self.registry_mappings:
            if m.platform == platform:
                mapping = m
                break

        if not mapping:
            # Default to all registries
            return ["gluestack_db", "shadcn_db", "radix_db"]

        # Return registries based on priority
        registries = mapping.primary_registries.copy()
        if include_fallback:
            registries.extend(mapping.fallback_registries)

        return registries

    def get_registry_priority(self, registry: str, platform: Optional[PlatformContext] = None) -> int:
        """Get priority of registry for given platform"""
        if platform is None:
            platform = self.get_current_platform()

        for mapping in self.registry_mappings:
            if mapping.platform == platform:
                if registry in mapping.primary_registries:
                    return mapping.priority * 2
                elif registry in mapping.fallback_registries:
                    return mapping.priority

        return 0  # Default priority

    def clear_context(self, session_id: Optional[str] = None) -> bool:
        """Clear context (current or specific session)"""
        with self.lock:
            if session_id:
                # Clear specific session context from history
                self.context_history = [
                    ctx for ctx in self.context_history
                    if ctx.session_id != session_id
                ]
                return True
            else:
                # Clear current context
                self.current_context = None
                return True

    def get_context_stats(self) -> Dict[str, Any]:
        """Get context usage statistics"""
        with self.lock:
            platform_counts = {}
            for context in self.context_history + ([self.current_context] if self.current_context else []):
                if context:
                    platform = context.platform.value
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1

            # Get current platform directly to avoid deadlock
            current_platform = self.current_context.platform.value if self.current_context else PlatformContext.NONE.value

            return {
                "total_sessions": self.session_counter,
                "current_platform": current_platform,
                "platform_distribution": platform_counts,
                "history_size": len(self.context_history),
                "registry_mappings": [
                    {
                        "platform": mapping.platform.value,
                        "primary": mapping.primary_registries,
                        "fallback": mapping.fallback_registries,
                        "priority": mapping.priority
                    }
                    for mapping in self.registry_mappings
                ]
            }

    def detect_context_from_keywords(self, text: str) -> PlatformContext:
        """Simple keyword-based context detection"""
        text_lower = text.lower()

        # React Native keywords
        native_keywords = [
            "react native", "mobile", "ios", "android", "expo",
            "touchable", "view", "text", "image", "stylesheet",
            "nativewind", "gluestack mobile", "mobile app"
        ]

        # React JS keywords
        web_keywords = [
            "react js", "web", "browser", "nextjs", "next.js",
            "vite", "webpack", "tailwind", "shadcn", "web app",
            "dom", "html", "css", "javascript", "typescript"
        ]

        native_score = sum(1 for keyword in native_keywords if keyword in text_lower)
        web_score = sum(1 for keyword in web_keywords if keyword in text_lower)

        if native_score > web_score:
            return PlatformContext.REACT_NATIVE
        elif web_score > native_score:
            return PlatformContext.REACT_JS
        else:
            return PlatformContext.AUTO

    def suggest_context_switch(self, query: str) -> Optional[PlatformContext]:
        """Suggest context switch based on query content"""
        detected = self.detect_context_from_keywords(query)
        current = self.get_current_platform()

        if detected != current and detected != PlatformContext.AUTO:
            return detected

        return None

    def export_context(self, format: str = "json") -> str:
        """Export current context configuration"""
        data = {
            "current_context": asdict(self.current_context) if self.current_context else None,
            "registry_mappings": [
                {
                    "platform": mapping.platform.value,
                    "primary_registries": mapping.primary_registries,
                    "fallback_registries": mapping.fallback_registries,
                    "priority": mapping.priority
                }
                for mapping in self.registry_mappings
            ],
            "stats": self.get_context_stats()
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global context manager instance
_context_manager = None

def get_context_manager() -> ContextManager:
    """Get global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager

def set_platform_context(
    platform: Union[PlatformContext, str],
    session_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    project_type: Optional[str] = None
) -> ContextInfo:
    """Convenience function to set platform context"""
    return get_context_manager().set_context(platform, session_id, user_agent, project_type)

def get_current_context() -> Optional[ContextInfo]:
    """Convenience function to get current context"""
    return get_context_manager().get_context()

def get_platform_registries(platform: Optional[PlatformContext] = None) -> List[str]:
    """Convenience function to get registries for platform"""
    return get_context_manager().get_registries_for_context(platform)


if __name__ == "__main__":
    # Test the context manager
    manager = ContextManager()

    # Test setting context
    context = manager.set_context(PlatformContext.REACT_NATIVE, session_id="test_session")
    print(f"Set context: {context.platform.value}")

    # Test getting registries
    registries = manager.get_registries_for_context(PlatformContext.REACT_NATIVE)
    print(f"React Native registries: {registries}")

    # Test context detection
    detected = manager.detect_context_from_keywords("I'm building a mobile app with React Native")
    print(f"Detected context: {detected.value}")

    # Test export
    print("Context configuration:")
    print(manager.export_context())