import os
import json
import importlib.util
import subprocess
import yaml
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from models.skill import Skill
from providers.base_provider import BaseProvider, logger
from configs.settings import PROVIDERS_CONFIG, PROJECT_ROOT

class FileProvider(BaseProvider):
    """
    Loads skills from the filesystem (JSON, YAML, Markdown, and Python files).
    Compiles dynamic handlers for files containing code or system commands.
    """
    
    def __init__(self, name: str = "file_provider", default_priority: int = 0):
        super().__init__(name, default_priority)
        self.config = PROVIDERS_CONFIG.get("file_provider", {})
        self.directory = PROJECT_ROOT / self.config.get("directory", "skills/file")
        self.allowed_extensions = self.config.get("allowed_extensions", [".yaml", ".json", ".py", ".md"])

    def load_skills(self) -> List[Skill]:
        """Scans the directory and loads skills from supported files."""
        if not self.config.get("enabled", True):
            logger.info("File provider is disabled")
            return []

        if not self.directory.exists():
            logger.warning(f"File provider directory does not exist: {self.directory}")
            return []

        skills = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                if ext not in self.allowed_extensions:
                    continue

                try:
                    loaded_skill = self._load_file(file_path, ext)
                    if loaded_skill:
                        loaded_skill.priority = self.default_priority
                        skills.append(loaded_skill)
                except Exception as e:
                    logger.error(f"Error loading skill from file {file_path}: {e}", exc_info=True)

        return skills

    def _load_file(self, file_path: Path, ext: str) -> Optional[Skill]:
        """Loads a single file and creates a Skill object with an executable handler."""
        if ext == ".py":
            return self._load_python_file(file_path)
        elif ext in (".yaml", ".yml"):
            return self._load_yaml_file(file_path)
        elif ext == ".json":
            return self._load_json_file(file_path)
        elif ext == ".md":
            return self._load_markdown_file(file_path)
        return None

    def _load_python_file(self, file_path: Path) -> Optional[Skill]:
        """Loads metadata and execution handler from a Python script file."""
        module_name = f"dynamic_file_skill_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if not spec or not spec.loader:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 1. Look for SKILL_METADATA dict in module
        metadata = getattr(module, "SKILL_METADATA", {})
        
        # 2. Look for execution function (default to 'execute' or 'run' or function with skill decorator)
        handler = None
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name in ("execute", "run", file_path.stem):
                handler = func
                break
        
        # If no explicit handler, look for first public function
        if not handler:
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_"):
                    handler = func
                    break

        if not handler:
            logger.warning(f"No executable function found in Python skill file {file_path}")
            return None

        # Build name and description from metadata or module info
        skill_name = metadata.get("name") or file_path.stem
        skill_desc = metadata.get("description") or module.__doc__ or f"Python skill loaded from {file_path.name}"
        version = metadata.get("version") or "1.0.0"
        
        # Inferred parameters
        parameters = metadata.get("parameters")
        if not parameters:
            parameters = self._infer_parameters_from_function(handler)

        try:
            source_rel = str(file_path.relative_to(PROJECT_ROOT))
        except ValueError:
            source_rel = str(file_path)

        return Skill(
            name=skill_name,
            description=skill_desc,
            parameters=parameters,
            source_type="file",
            source_path=source_rel,
            version=version,
            handler=handler
        )

    def _load_yaml_file(self, file_path: Path) -> Optional[Skill]:
        """Loads a Skill from a YAML definition."""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        if not data:
            return None
        return self._create_skill_from_dict(data, file_path)

    def _load_json_file(self, file_path: Path) -> Optional[Skill]:
        """Loads a Skill from a JSON definition."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return self._create_skill_from_dict(data, file_path)

    def _load_markdown_file(self, file_path: Path) -> Optional[Skill]:
        """
        Loads a Skill from a Markdown file. 
        Supports YAML frontmatter for metadata, and python code blocks for execution code.
        """
        with open(file_path, "r") as f:
            content = f.read()

        # Parse YAML frontmatter
        metadata = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except Exception as e:
                    logger.error(f"Failed to parse frontmatter in {file_path}: {e}")

        # Extract python code block
        python_code = ""
        import re
        matches = re.findall(r"```python\n(.*?)```", body, re.DOTALL)
        if matches:
            python_code = matches[0]

        if not metadata:
            # Fallback if no frontmatter is found
            metadata = {
                "name": file_path.stem,
                "description": f"Markdown skill loaded from {file_path.name}"
            }

        if python_code:
            metadata["execute_code"] = python_code

        return self._create_skill_from_dict(metadata, file_path)

    def _create_skill_from_dict(self, data: Dict[str, Any], file_path: Path) -> Optional[Skill]:
        """Helper to convert structured dictionary metadata into a Skill object."""
        name = data.get("name") or file_path.stem
        description = data.get("description") or f"Skill loaded from {file_path.name}"
        version = data.get("version", "1.0.0")
        parameters = data.get("parameters", {})
        
        # Ensure parameters are correctly formatted
        if parameters and "properties" not in parameters:
            parameters = {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }

        handler = None
        
        # 1. Compile execute_code block if present
        if "execute_code" in data:
            code_str = data["execute_code"]
            handler = self._compile_python_code(code_str, name)
            
        # 2. Setup shell command if present
        elif "command" in data:
            command_str = data["command"]
            handler = self._create_command_handler(command_str)
            
        # 3. Dynamic python handler import path (e.g. "path.to.module:function")
        elif "python_handler" in data:
            handler_str = data["python_handler"]
            handler = self._import_handler_string(handler_str)

        if not handler:
            # Create a mock default handler if nothing is specified
            logger.warning(f"No execution handler configured for {name} in {file_path}. Creating a dummy handler.")
            handler = lambda **kwargs: f"Mock execution of {name} with args: {kwargs}"

        try:
            source_rel = str(file_path.relative_to(PROJECT_ROOT))
        except ValueError:
            source_rel = str(file_path)

        return Skill(
            name=name,
            description=description,
            parameters=parameters,
            source_type="file",
            source_path=source_rel,
            version=version,
            handler=handler
        )

    def _compile_python_code(self, code_str: str, skill_name: str) -> Callable:
        """Compiles a Python code block and extracts the 'execute' or first public function."""
        local_vars = {}
        # Execute the code block to populate local namespace
        exec(code_str, globals(), local_vars)
        
        # Extract execution function
        for func_name in ("execute", "run", skill_name):
            if func_name in local_vars and callable(local_vars[func_name]):
                return local_vars[func_name]
                
        # Fallback to the first callable in the executed code
        for val in local_vars.values():
            if callable(val):
                return val
                
        raise ValueError(f"No executable function found in code block for skill {skill_name}")

    def _create_command_handler(self, command_str: str) -> Callable:
        """Creates a handler that executes a shell command and substitutes parameters."""
        def command_handler(**kwargs) -> str:
            # Substitute variables inside the command string, e.g. "echo {name}"
            cmd = command_str.format(**kwargs)
            logger.info(f"Executing system command skill: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError(f"Command failed with code {result.returncode}: {result.stderr}")
            return result.stdout.strip()
        return command_handler

    def _import_handler_string(self, handler_str: str) -> Callable:
        """Imports a function from a module path string, e.g., 'os.path:exists'."""
        if ":" not in handler_str:
            raise ValueError(f"Invalid handler import path: {handler_str}. Must be in format 'module:function'")
        module_path, func_name = handler_str.split(":", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)

    def _infer_parameters_from_function(self, func: Callable) -> Dict[str, Any]:
        """Helper to build JSON schema parameters using python function signatures."""
        sig = inspect.signature(func)
        props = {}
        required = []
        for param_name, param in sig.parameters.items():
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
        
        return {
            "type": "object",
            "properties": props,
            "required": required
        }
