import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"

# Default fallback values
DEFAULT_PRIORITIES = {
    "inline": 100,
    "class": 80,
    "file": 50
}

SKILL_OVERRIDES = {}

PROVIDERS_CONFIG = {
    "file_provider": {
        "enabled": True,
        "directory": "skills/file",
        "allowed_extensions": [".yaml", ".json", ".py", ".md"]
    },
    "inline_provider": {
        "enabled": True,
        "module_path": "skills/inline/sample_inline.py"
    },
    "class_provider": {
        "enabled": True,
        "modules": ["skills.classes.sample_class"]
    }
}

# Load priorities.yaml
priorities_path = CONFIG_DIR / "priorities.yaml"
if priorities_path.exists():
    try:
        with open(priorities_path, "r") as f:
            data = yaml.safe_load(f) or {}
            DEFAULT_PRIORITIES = data.get("default_priorities", DEFAULT_PRIORITIES)
            SKILL_OVERRIDES = data.get("skill_overrides", SKILL_OVERRIDES)
    except Exception as e:
        print(f"Warning: Failed to load priorities.yaml: {e}")

# Load providers.yaml
providers_path = CONFIG_DIR / "providers.yaml"
if providers_path.exists():
    try:
        with open(providers_path, "r") as f:
            data = yaml.safe_load(f) or {}
            PROVIDERS_CONFIG = data.get("providers", PROVIDERS_CONFIG)
    except Exception as e:
        print(f"Warning: Failed to load providers.yaml: {e}")

# Log directory setup
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "skills_provider.log"
