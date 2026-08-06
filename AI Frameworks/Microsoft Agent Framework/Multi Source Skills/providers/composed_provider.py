import time
import logging
from typing import List, Dict, Tuple, Optional
from models.skill import Skill
from models.registry import RegistrySummary, ConflictDetail
from providers.base_provider import BaseProvider
from providers.file_provider import FileProvider
from providers.inline_provider import InlineProvider
from providers.class_provider import ClassProvider
from resolver.merge import merge_skills
from configs.settings import PROVIDERS_CONFIG

logger = logging.getLogger("ComposedProvider")

class ComposedProvider(BaseProvider):
    """
    A composite provider that aggregates and manages multiple individual sub-providers.
    Coordinates skill loading, normalization, validation, and priority resolution.
    """
    
    def __init__(self, providers: Optional[List[BaseProvider]] = None, name: str = "composed_provider"):
        super().__init__(name=name, default_priority=0)
        
        # If no providers are specified, auto-discover based on providers.yaml configuration
        if providers is None:
            self.providers = []
            self._discover_and_register_providers()
        else:
            self.providers = providers

    def _discover_and_register_providers(self):
        """Initializes and registers sub-providers according to configuration settings."""
        logger.info("Initializing auto-discovered providers...")
        
        # File Provider
        file_cfg = PROVIDERS_CONFIG.get("file_provider", {})
        if file_cfg.get("enabled", True):
            priority = file_cfg.get("priority_offset", 0)
            self.providers.append(FileProvider(default_priority=priority))
            logger.info("Registered FileProvider")

        # Inline Provider
        inline_cfg = PROVIDERS_CONFIG.get("inline_provider", {})
        if inline_cfg.get("enabled", True):
            priority = inline_cfg.get("priority_offset", 0)
            self.providers.append(InlineProvider(default_priority=priority))
            logger.info("Registered InlineProvider")

        # Class Provider
        class_cfg = PROVIDERS_CONFIG.get("class_provider", {})
        if class_cfg.get("enabled", True):
            priority = class_cfg.get("priority_offset", 0)
            self.providers.append(ClassProvider(default_priority=priority))
            logger.info("Registered ClassProvider")

    def load_skills(self) -> List[Skill]:
        """Collects raw, un-resolved skills from all sub-providers."""
        raw_skills = []
        for provider in self.providers:
            try:
                logger.info(f"Loading skills from provider: {provider.name}")
                skills = provider.load_skills()
                raw_skills.extend(skills)
                logger.info(f"Loaded {len(skills)} raw skills from {provider.name}")
            except Exception as e:
                logger.error(f"Error loading skills from provider {provider.name}: {e}", exc_info=True)
        return raw_skills

    def compose_registry(self, overrides: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Skill], RegistrySummary]:
        """
        Executes the entire loading, validation, normalization, and merge pipeline.
        Returns the finalized active skill map and a detailed RegistrySummary report.
        """
        start_time = time.perf_counter()
        
        # 1. Load all raw skills
        raw_skills = self.load_skills()
        
        # 2. Normalize, validate, group, resolve, and merge
        merged_skills, conflicts = merge_skills(raw_skills, overrides)
        
        end_time = time.perf_counter()
        load_duration = end_time - start_time
        
        # 3. Create the registry summary metadata
        summary = RegistrySummary(
            total_loaded_skills=len(raw_skills),
            active_skills=list(merged_skills.keys()),
            conflicts_detected=len(conflicts),
            conflicts=conflicts,
            load_time_seconds=round(load_duration, 5)
        )
        
        logger.info(
            f"Skill composition complete in {summary.load_time_seconds:.4f}s. "
            f"Active skills: {len(merged_skills)}, Conflicts detected: {summary.conflicts_detected}"
        )
        
        return merged_skills, summary
