# Designing & Implementing Skills

This guide details how to implement skills across the three supported formats: **File System**, **Inline Memory**, and **Class Modules**.

---

## 1. File-Based Skills (`skills/file/`)

The file provider supports loading skills from multiple formats, making it easy to integrate static definitions, scripts, or external libraries.

### A. YAML Format (`.yaml` / `.yml`)
Ideal for declaring python scripts inline alongside metadata.

```yaml
name: "yaml_math_multiply"
description: "Multiplies two numbers together."
version: "1.0.0"
parameters:
  x:
    type: "number"
    description: "Multiplier"
  y:
    type: "number"
    description: "Multiplicand"
execute_code: |
  def execute(x, y):
      return x * y
```

### B. JSON Format (`.json`)
Ideal for shell command integrations.

```json
{
  "name": "host_ip",
  "description": "Prints local host ip address",
  "version": "1.0.0",
  "parameters": {},
  "command": "hostname -I"
}
```

### C. Markdown Format (`.md`)
Allows writing self-documenting skills. The parser reads YAML frontmatter and extracts the first ` ```python ` code block.

```markdown
---
name: greet_md
description: "Greets the user"
version: "1.0.0"
parameters:
  username:
    type: "string"
---

# Greet Skill in Markdown
This is a python skill block:

```python
def execute(username):
    return f"Hello, {username}!"
```

### D. Python Format (`.py`)
Standard python scripts with a `SKILL_METADATA` global dictionary and an `execute` function.

```python
SKILL_METADATA = {
    "name": "square_root",
    "description": "Computes square root.",
    "parameters": {
        "val": {"type": "number"}
    }
}

def execute(val):
    import math
    return math.sqrt(val)
```

---

## 2. Inline Skills (`skills/inline/`)

Inline skills are registered directly using the `@register_inline_skill` decorator.

```python
from providers.inline_provider import register_inline_skill

@register_inline_skill(
    name="uppercase_text",
    description="Converts input to uppercase",
    parameters={
        "text": {"type": "string", "description": "Text to transform"}
    }
)
def uppercase(text: str) -> str:
    return text.upper()
```

If the `parameters` dictionary is omitted, the provider will automatically inspect the function signature to generate a JSON Schema.

---

## 3. Class-Based Skills (`skills/classes/`)

Class-based skills group related tools. Individual methods are exposed as skills by decorating them with `@skill_method`.

```python
from providers.class_provider import skill_method

class DatabaseTools:
    def __init__(self):
        self.db = "mock_db_connection"
        
    @skill_method(
        name="db_query",
        description="Query the mock database"
    )
    def query(self, sql_query: str) -> str:
        return f"Executing '{sql_query}' on database."
```
When class provider loads a module, it automatically instantiates any class defined in it using the default constructor and extracts the decorated skill methods.
