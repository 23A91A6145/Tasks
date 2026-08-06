# Skill Providers & Extension Guide

This document describes the structure of Skill Providers and explains how to create custom providers.

## Provider Base Structure

All skill providers inherit from `BaseProvider` inside `providers/base_provider.py`:

```python
import abc
from typing import List
from models.skill import Skill

class BaseProvider(abc.ABC):
    def __init__(self, name: str, default_priority: int = 0):
        self.name = name
        self.default_priority = default_priority

    @abc.abstractmethod
    def load_skills(self) -> List[Skill]:
        """Loads and returns all available skills from this provider."""
        pass
```

---

## Implementing a Custom Provider

To add a new skill source (for example, a Remote HTTP Skill Provider or database-backed provider):

1. **Create the Provider Class**: Create a file in `providers/` inheriting from `BaseProvider`.
2. **Implement `load_skills`**: Write logic to fetch skill definitions and return a list of `Skill` objects with execution handlers.
3. **Register in `composed_provider.py`**: Add discovery support or register it directly inside the `ComposedProvider` constructor.

### Example: Remote HTTP Provider

Here is an example of how an HTTP API Skill Provider could look:

```python
import requests
from typing import List
from models.skill import Skill
from providers.base_provider import BaseProvider

class RemoteHttpProvider(BaseProvider):
    def __init__(self, endpoint_url: str, default_priority: int = 40):
        super().__init__("remote_http_provider", default_priority)
        self.endpoint_url = endpoint_url

    def load_skills(self) -> List[Skill]:
        skills = []
        try:
            response = requests.get(f"{self.endpoint_url}/skills")
            if response.status_code == 200:
                skill_definitions = response.json()
                for data in skill_definitions:
                    # Dynamically construct HTTP call execution handler
                    handler = self._create_remote_handler(data["name"])
                    
                    skill = Skill(
                        name=data["name"],
                        description=data["description"],
                        parameters=data["parameters"],
                        source_type="remote_http",
                        source_path=f"{self.endpoint_url}/{data['name']}",
                        handler=handler
                    )
                    skills.append(skill)
        except Exception as e:
            print(f"Error loading remote skills: {e}")
        return skills

    def _create_remote_handler(self, skill_name: str):
        def handler(**kwargs):
            res = requests.post(f"{self.endpoint_url}/execute/{skill_name}", json=kwargs)
            return res.json().get("result")
        return handler
```
This pluggable design makes it easy to integrate remote tools, enterprise plugins, or MCP servers.
