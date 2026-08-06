import logging
import time
from typing import Dict, Any, List, Optional
from models.skill import Skill
from models.registry import RegistrySummary

logger = logging.getLogger("SkillRegistry")

class SkillRegistry:
    """
    Registry container holding all active, conflict-free skills.
    Coordinates parameter validation and executes skills via their handlers.
    """
    
    def __init__(self, skills: Dict[str, Skill], summary: RegistrySummary, db_manager: Optional[Any] = None):
        self._skills = skills
        self.summary = summary
        self.db = db_manager
        self.execution_history = []  # Log execution traces

    def get_skill(self, name: str) -> Optional[Skill]:
        """Retrieves a skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> List[Skill]:
        """Returns list of all active skills."""
        return list(self._skills.values())

    def validate_inputs(self, skill: Skill, arguments: Dict[str, Any]) -> List[str]:
        """
        Validates arguments against the skill's parameter JSON Schema.
        Returns a list of error message strings, if any.
        """
        errors = []
        schema = skill.parameters or {}
        
        # Extract properties and required fields
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Check required fields
        for field in required:
            if field not in arguments:
                errors.append(f"Missing required parameter: '{field}'")

        # Type validation
        for param_name, param_val in arguments.items():
            if param_name not in properties:
                # Allow extra arguments or log warning
                continue
                
            prop_def = properties[param_name]
            expected_type = prop_def.get("type")
            
            if expected_type == "string" and not isinstance(param_val, str):
                errors.append(f"Parameter '{param_name}' must be a string, got {type(param_val).__name__}")
            elif expected_type == "integer" and not isinstance(param_val, int):
                errors.append(f"Parameter '{param_name}' must be an integer, got {type(param_val).__name__}")
            elif expected_type == "number" and not isinstance(param_val, (int, float)):
                errors.append(f"Parameter '{param_name}' must be a number, got {type(param_val).__name__}")
            elif expected_type == "boolean" and not isinstance(param_val, bool):
                errors.append(f"Parameter '{param_name}' must be a boolean, got {type(param_val).__name__}")
            elif expected_type == "object" and not isinstance(param_val, dict):
                errors.append(f"Parameter '{param_name}' must be an object (dict), got {type(param_val).__name__}")
            elif expected_type == "array" and not isinstance(param_val, list):
                errors.append(f"Parameter '{param_name}' must be an array (list), got {type(param_val).__name__}")

        return errors

    def execute(self, _skill_name: str, /, **kwargs) -> Any:
        """
        Looks up, validates inputs, and executes the specified skill.
        Traces execution, writes logs to SQLite database, and returns outcome.
        """
        skill = self.get_skill(_skill_name)
        if not skill:
            raise KeyError(f"Skill '{_skill_name}' is not registered.")

        # Validate arguments
        validation_errors = self.validate_inputs(skill, kwargs)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Validation failed for skill '{_skill_name}': {error_msg}")
            raise ValueError(f"Invalid inputs: {error_msg}")

        logger.info(f"Executing skill '{_skill_name}' (Source: {skill.source_type} [{skill.source_path}]) with arguments {kwargs}")
        
        start_time = time.perf_counter()
        try:
            # Execute skill
            result = skill.execute(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Record execution trace
            trace = {
                "skill_name": _skill_name,
                "source_type": skill.source_type,
                "source_path": skill.source_path,
                "arguments": kwargs,
                "result": str(result),
                "status": "success",
                "error": None,
                "duration_ms": duration_ms
            }
            self.execution_history.append(trace)
            
            if self.db:
                self.db.log_execution(
                    skill_name=_skill_name,
                    source_type=skill.source_type,
                    source_path=skill.source_path,
                    arguments=kwargs,
                    result=str(result),
                    status="success",
                    error=None,
                    duration_ms=duration_ms
                )
                
            logger.info(f"Successfully executed skill '{_skill_name}' in {duration_ms:.2f}ms. Result: {result}")
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Error executing skill '{_skill_name}' in {duration_ms:.2f}ms: {e}", exc_info=True)
            
            trace = {
                "skill_name": _skill_name,
                "source_type": skill.source_type,
                "source_path": skill.source_path,
                "arguments": kwargs,
                "result": None,
                "status": "failed",
                "error": str(e),
                "duration_ms": duration_ms
            }
            self.execution_history.append(trace)
            
            if self.db:
                self.db.log_execution(
                    skill_name=_skill_name,
                    source_type=skill.source_type,
                    source_path=skill.source_path,
                    arguments=kwargs,
                    result=None,
                    status="failed",
                    error=str(e),
                    duration_ms=duration_ms
                )
                
            raise RuntimeError(f"Skill execution failed: {e}") from e
