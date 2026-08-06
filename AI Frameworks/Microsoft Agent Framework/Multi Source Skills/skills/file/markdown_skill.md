---
name: markdown_greet
description: "A greet skill written in a Markdown file with embedded Python"
version: "1.0.0"
parameters:
  name:
    type: "string"
    description: "The name of the user to greet"
---

# Markdown Greet Skill
This is a standard markdown document that includes metadata in the YAML frontmatter.
The system compiles and extracts the python code block below at runtime.

```python
def execute(name: str) -> str:
    return f"Hello, {name}! This greeting is dynamically executed from a Markdown file code block."
```
