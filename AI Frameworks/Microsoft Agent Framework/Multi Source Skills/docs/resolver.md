# Conflict Resolution Engine

This document details how the resolver resolves conflicts when multiple providers export tools with overlapping names.

---

## Conflict Lifecycle

When a query is processed or registry reloaded, the pipeline performs the following steps:

1. **Discovery**: All registered providers return flat lists of raw `Skill` definitions.
2. **Normalization**: Skill names are normalized using regular expressions to lowercase snake_case (e.g. `Math-Add` and `math_add` represent the same skill).
3. **Validation**: Skills are validated (must contain a name, description, and valid handler).
4. **Overlap Detection**: The registry aggregates skills by name and flags duplicates.
5. **Priority Overrides Check**: If a duplicate matches a key in the `skill_overrides` dictionary inside `configs/priorities.yaml`, that source is instantly selected as the winner.
6. **Default Priority Matching**: If no override exists, the candidate with the highest default source type priority wins.
7. **Resolution Reporting**: A detailed conflict summary report is generated.

---

## Overrides Configuration (`configs/priorities.yaml`)

You can force a specific winner using overrides. For example, if both Class-based and File-based providers register `search_skill`, you can configure the override like this:

```yaml
skill_overrides:
  search_skill:
    preferred_source: "class"
    reason: "Prefer structured class lookup over simple file scan."
```

If this override is active, the class provider's `search_skill` will be selected as active, even if another provider has a higher default priority.
