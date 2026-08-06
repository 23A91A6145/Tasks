import abc
import logging
from typing import List
from models.skill import Skill
from models.provider import ProviderMetadata
from configs.settings import DEFAULT_PRIORITIES

# Configure structured logging helper if needed, or standard logger
logger = logging.getLogger("SkillsProvider")

class BaseProvider(abc.ABC):
    """
    Abstract base class for all skill providers.
    Each provider represents a source of capabilities (e.g. filesystem, classes, inline).
    """
    
    def __init__(self, name: str, default_priority: int = 0):
        self.name = name
        self.default_priority = default_priority or DEFAULT_PRIORITIES.get(self.name.replace("_provider", ""), 0)
        self.metadata = ProviderMetadata(
            name=self.name,
            priority=self.default_priority,
            description=f"Skill provider loading from {self.name}",
            enabled=True
        )

    @abc.abstractmethod
    def load_skills(self) -> List[Skill]:
        """Loads and returns all available skills from this provider."""
        pass
