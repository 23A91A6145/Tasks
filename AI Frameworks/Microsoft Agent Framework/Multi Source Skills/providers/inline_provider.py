import importlib.util
import os
import inspect
from typing import List, Callable, Dict, Any, Optional
from pathlib import Path
from models.skill import Skill
from providers.base_provider import BaseProvider, logger
from configs.settings import PROVIDERS_CONFIG, PROJECT_ROOT

# In-memory storage for programmatically registered inline skills
_REGISTERED_INLINE_SKILLS: List[Skill] = []

def register_inline_skill(name: str, description: str, parameters: Optional[Dict[str, Any]] = None):
    """
    Decorator to register a python function as an inline skill.
    If parameters schema is omitted, it will attempt to infer from function signature.
    """
    def decorator(func: Callable):
        params = parameters or {}
        if not params:
            sig = inspect.signature(func)
            props = {}
            required = []
            for param_name, param in sig.parameters.items():
                if param_name in ("self", "args", "kwargs"):
                    continue
                # Map python types to JSON schema types
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"
                
                props[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            
            params = {
                "type": "object",
                "properties": props,
                "required": required
            }
        else:
            # Wrap standard JSON properties schema if needed
            if "properties" not in params:
                params = {
                    "type": "object",
                    "properties": params,
                    "required": list(params.keys())
                }

        skill = Skill(
            name=name,
            description=description,
            parameters=params,
            source_type="inline",
            source_path=f"inline_function:{func.__name__}",
            priority=0, # Set by Resolver
            handler=func
        )
        
        # Avoid duplicate registrations of the same function name in inline registry
        for idx, existing in enumerate(_REGISTERED_INLINE_SKILLS):
            if existing.name == name:
                _REGISTERED_INLINE_SKILLS[idx] = skill
                break
        else:
            _REGISTERED_INLINE_SKILLS.append(skill)
        
        return func
    return decorator


class InlineProvider(BaseProvider):
    """
    Loads inline skills that have been registered programmatically or 
    loaded dynamically from the configured python module.
    """
    
    def __init__(self, name: str = "inline_provider", default_priority: int = 0):
        super().__init__(name, default_priority)
        self.config = PROVIDERS_CONFIG.get("inline_provider", {})
        self.module_loaded = False

    def load_skills(self) -> List[Skill]:
        """Loads and returns all inline skills."""
        if not self.config.get("enabled", True):
            logger.info("Inline provider is disabled")
            return []

        # Load the dynamic inline file if configured and not yet loaded
        module_rel_path = self.config.get("module_path", "skills/inline/sample_inline.py")
        if module_rel_path and not self.module_loaded:
            module_path = PROJECT_ROOT / module_rel_path
            if module_path.exists():
                try:
                    logger.info(f"Loading inline skills from module {module_path}")
                    # Dynamically import module to trigger decorators
                    spec = importlib.util.spec_from_file_location("dynamic_inline_skills", str(module_path))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self.module_loaded = True
                        logger.info(f"Successfully loaded inline skills from {module_rel_path}")
                except Exception as e:
                    logger.error(f"Error loading inline skills from {module_path}: {e}", exc_info=True)
            else:
                logger.warning(f"Configured inline skills path does not exist: {module_path}")

        # Set the default priority on each loaded inline skill
        for skill in _REGISTERED_INLINE_SKILLS:
            skill.priority = self.default_priority
            
        return _REGISTERED_INLINE_SKILLS
