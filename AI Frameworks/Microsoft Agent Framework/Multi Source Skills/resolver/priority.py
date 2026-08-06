from typing import List, Tuple, Dict, Any, Optional
from models.skill import Skill
from models.registry import ConflictDetail
from configs.settings import DEFAULT_PRIORITIES, SKILL_OVERRIDES

def resolve_conflict(
    skill_name: str, 
    candidates: List[Skill], 
    overrides: Optional[Dict[str, Any]] = None
) -> Tuple[Skill, ConflictDetail]:
    """
    Resolves a name collision between multiple skill candidates.
    Returns the winning Skill and a detailed ConflictDetail record.
    """
    # Build candidate details for reporting
    sources_info = []
    for c in candidates:
        # Resolve priority using configuration defaults if not already customized
        base_priority = DEFAULT_PRIORITIES.get(c.source_type, 0)
        c.priority = base_priority
        sources_info.append({
            "source_type": c.source_type,
            "source_path": c.source_path,
            "priority": c.priority,
            "version": c.version
        })

    # Check for manual overrides (custom runtime overrides take precedence over static settings overrides)
    active_overrides = overrides if overrides is not None else SKILL_OVERRIDES
    override = active_overrides.get(skill_name)
    winner = None
    reason = ""

    if override:
        preferred_source = override.get("preferred_source")
        reason_msg = override.get("reason", "Manual configuration override")
        # Search for candidate matching the preferred source
        for c in candidates:
            if c.source_type == preferred_source:
                winner = c
                reason = f"Explicit user override: {reason_msg} (Preferred source: {preferred_source})"
                break
        
        if not winner:
            reason = f"Manual override specified preferred source '{preferred_source}', but it was not available. Falling back to priority."

    # If no override or override source wasn't found, determine based on highest priority value
    if not winner:
        # Sort by priority desc, then fallback alphabetically by source_type (inline > class > file)
        order = {"inline": 3, "class": 2, "file": 1}
        
        def sort_key(s: Skill):
            return (s.priority, order.get(s.source_type, 0))

        sorted_candidates = sorted(candidates, key=sort_key, reverse=True)
        winner = sorted_candidates[0]
        reason = f"Highest resolved priority (Priority: {winner.priority}, Source: '{winner.source_type}')"

    # Build conflict detail
    detail = ConflictDetail(
        skill_name=skill_name,
        sources=sources_info,
        winning_source_type=winner.source_type,
        winning_source_path=winner.source_path,
        winning_priority=winner.priority,
        resolution_reason=reason
    )

    return winner, detail
