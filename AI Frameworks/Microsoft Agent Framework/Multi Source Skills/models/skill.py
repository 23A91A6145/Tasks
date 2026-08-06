from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, Callable

class Skill(BaseModel):
    name: str = Field(..., description="Unique identifier name of the skill (normalized to snake_case or kebab-case)")
    description: str = Field(..., description="Human-readable description of what the skill does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for the inputs of the skill")
    source_type: str = Field(..., description="Source classification: 'file', 'inline', or 'class'")
    source_path: str = Field(..., description="Reference path or module/class name where this skill originated")
    version: str = Field("1.0.0", description="Version string of the skill")
    priority: int = Field(0, description="Priority level of this skill for conflict resolution")
    
    # The actual executable handler is excluded from serialization
    handler: Optional[Callable] = Field(None, exclude=True, description="The callable Python function that executes the skill")

    model_config = ConfigDict(arbitrary_types_allowed=True)
        
    def execute(self, *args, **kwargs) -> Any:
        """Executes the skill with the provided arguments."""
        if not self.handler:
            raise ValueError(f"Skill '{self.name}' does not have an execution handler attached.")
        return self.handler(*args, **kwargs)
