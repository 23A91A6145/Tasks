import logging
from typing import Optional, Dict, Any
from models.skill import Skill
from models.registry import RegistrySummary
from providers.composed_provider import ComposedProvider
from agents.registry import SkillRegistry
from agents.db_manager import DatabaseManager
from configs.settings import SKILL_OVERRIDES

logger = logging.getLogger("SkillManager")

class SkillManager:
    """
    Manager orchestration class that handles the lifecycle of skill providers.
    It compiles, reloads, and caches the active SkillRegistry instance.
    """
    
    def __init__(self, composed_provider: Optional[ComposedProvider] = None):
        self._provider = composed_provider or ComposedProvider()
        self.db = DatabaseManager()
        self._registry: Optional[SkillRegistry] = None
        # Eagerly load registry on startup
        self.reload()

    def reload(self) -> SkillRegistry:
        """
        Forces a reload of all providers, rebuilds registry, detects conflicts,
        and refreshes cache.
        """
        logger.info("Triggering a complete reload of the skill providers...")
        
        # Keep track of execution history if registry already exists
        old_history = []
        if self._registry:
            old_history = self._registry.execution_history
            
        # Get priority overrides from DB and merge with static settings overrides
        db_overrides = self.db.get_overrides()
        merged_overrides = {}
        merged_overrides.update(SKILL_OVERRIDES)
        merged_overrides.update(db_overrides)
        
        # Get fresh compositions with overrides
        merged_skills, summary = self._provider.compose_registry(merged_overrides)
        
        # Instantiate fresh registry with db manager
        self._registry = SkillRegistry(skills=merged_skills, summary=summary, db_manager=self.db)
        self._registry.execution_history = old_history
        
        logger.info("Skill registry cache refreshed successfully.")
        return self._registry

    def get_registry(self) -> SkillRegistry:
        """Returns the current cached active SkillRegistry."""
        if not self._registry:
            self.reload()
        return self._registry
