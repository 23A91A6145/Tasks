import importlib
import inspect
import logging
from typing import List, Any, Dict, Optional, Callable
from models.skill import Skill
from providers.base_provider import BaseProvider, logger
from configs.settings import PROVIDERS_CONFIG

# Storage for programmatically registered class instances
_REGISTERED_CLASS_INSTANCES: List[Any] = []

def skill_method(name: Optional[str] = None, description: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
    """
    Decorator to mark a class method as an executable skill.
    """
    def decorator(func: Callable):
        func._is_skill = True
        func._skill_name = name
        func._skill_description = description
        func._skill_parameters = parameters
        return func
    return decorator

def register_class_instance(instance: Any):
    """Programmatically register a class instance to the class provider."""
    if instance not in _REGISTERED_CLASS_INSTANCES:
        _REGISTERED_CLASS_INSTANCES.append(instance)


class ClassProvider(BaseProvider):
    """
    Loads skills from Python classes.
    It inspects class instances and registers methods decorated with @skill_method.
    """
    
    def __init__(self, name: str = "class_provider", default_priority: int = 0):
        super().__init__(name, default_priority)
        self.config = PROVIDERS_CONFIG.get("class_provider", {})
        self.loaded_modules = set()

    def _extract_skills_from_instance(self, instance: Any) -> List[Skill]:
        """Inspects an instance and extracts methods decorated with @skill_method."""
        skills = []
        class_name = instance.__class__.__name__
        
        for attr_name in dir(instance):
            # Skip private attributes
            if attr_name.startswith("_"):
                continue
            
            try:
                method = getattr(instance, attr_name)
            except AttributeError:
                continue
                
            if not inspect.ismethod(method) and not inspect.isfunction(method):
                continue
                
            # Check if method is decorated with @skill_method
            if getattr(method, "_is_skill", False):
                skill_name = getattr(method, "_skill_name", None) or attr_name
                skill_desc = getattr(method, "_skill_description", None) or method.__doc__ or f"Class method {attr_name} on {class_name}"
                raw_params = getattr(method, "_skill_parameters", None)
                
                # Infer parameters from method signature if not specified
                if not raw_params:
                    sig = inspect.signature(method)
                    props = {}
                    required = []
                    for param_name, param in sig.parameters.items():
                        # Skip self and other positional-only arguments that shouldn't be exposed
                        if param_name in ("self", "args", "kwargs"):
                            continue
                        
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
                    
                    raw_params = {
                        "type": "object",
                        "properties": props,
                        "required": required
                    }
                else:
                    if "properties" not in raw_params:
                        raw_params = {
                            "type": "object",
                            "properties": raw_params,
                            "required": list(raw_params.keys())
                        }
                
                # Build skill object
                skill = Skill(
                    name=skill_name,
                    description=skill_desc,
                    parameters=raw_params,
                    source_type="class",
                    source_path=f"class:{class_name}.{attr_name}",
                    priority=self.default_priority,
                    handler=method
                )
                skills.append(skill)
                
        return skills

    def load_skills(self) -> List[Skill]:
        """Loads and returns all skills from registered and configured classes."""
        if not self.config.get("enabled", True):
            logger.info("Class provider is disabled")
            return []

        skills = []
        
        # 1. Load from configured modules
        configured_modules = self.config.get("modules", ["skills.classes.sample_class"])
        for module_name in configured_modules:
            if module_name not in self.loaded_modules:
                try:
                    logger.info(f"Importing class skills module: {module_name}")
                    module = importlib.import_module(module_name)
                    self.loaded_modules.add(module_name)
                    
                    # Instantiate any classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Ensure class belongs to the imported module (not standard library or imports)
                        if obj.__module__ == module_name:
                            try:
                                # Try instantiating with default constructor
                                logger.info(f"Instantiating class {name} for skill discovery")
                                instance = obj()
                                register_class_instance(instance)
                            except Exception as instantiation_err:
                                logger.warning(
                                    f"Could not automatically instantiate {name} in {module_name}: {instantiation_err}. "
                                    f"Please register instances programmatically instead."
                                )
                except Exception as e:
                    logger.error(f"Error loading module {module_name} in ClassProvider: {e}", exc_info=True)

        # 2. Extract skills from all registered instances
        for instance in _REGISTERED_CLASS_INSTANCES:
            skills.extend(self._extract_skills_from_instance(instance))
            
        return skills
