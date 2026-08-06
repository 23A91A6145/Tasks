import re
import logging
from typing import List, Dict, Tuple, Any, Optional
from models.skill import Skill
from models.registry import ConflictDetail, RegistrySummary
from resolver.overlap_detector import detect_overlaps
from resolver.priority import resolve_conflict

logger = logging.getLogger("SkillsResolver")

def normalize_name(name: str) -> str:
    """Normalizes a skill name to lowercase snake_case."""
    # Replace spaces, hyphens, and dots with underscores, remove non-alphanumeric chars
    s = name.strip().lower()
    s = re.sub(r'[\s\-\.]+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s

def validate_skill(skill: Skill) -> bool:
    """
    Validates a Skill's metadata. 
    Returns True if valid, False otherwise.
    """
    if not skill.name:
        logger.warning(f"Skill validation failed: Missing name. Source: {skill.source_type}")
        return False
        
    if not skill.description:
        logger.warning(f"Skill validation failed: Missing description for skill '{skill.name}'")
        return False

    if skill.handler is None:
        logger.warning(f"Skill validation failed: Handler function is missing for skill '{skill.name}'")
        return False

    return True

def merge_skills(
    raw_skills: List[Skill], 
    overrides: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Skill], List[ConflictDetail]]:
    """
    Processes, normalizes, validates, and merges raw skills from multiple sources.
    Resolves name collisions using priority rules.
    Returns:
        Tuple: (merged_skills_dict, list_of_conflicts)
    """
    normalized_skills: List[Skill] = []
    
    # 1. Normalize and Validate
    for skill in raw_skills:
        # Clone to avoid mutating original values in dynamic code source lists
        skill_copy = skill.model_copy()
        
        # Normalize the name
        original_name = skill_copy.name
        skill_copy.name = normalize_name(skill_copy.name)
        
        if skill_copy.name != original_name:
            logger.info(f"Normalized skill name '{original_name}' -> '{skill_copy.name}'")
            
        if validate_skill(skill_copy):
            normalized_skills.append(skill_copy)
        else:
            logger.warning(f"Discarding invalid skill: {original_name} from {skill_copy.source_path}")

    # 2. Detect Overlaps
    grouped_skills = detect_overlaps(normalized_skills)
    
    merged_registry: Dict[str, Skill] = {}
    conflicts: List[ConflictDetail] = []

    # 3. Resolve and Merge
    for skill_name, candidates in grouped_skills.items():
        if len(candidates) > 1:
            logger.warning(f"Conflict detected for skill '{skill_name}': {len(candidates)} sources found.")
            winner, conflict_detail = resolve_conflict(skill_name, candidates, overrides)
            merged_registry[skill_name] = winner
            conflicts.append(conflict_detail)
            logger.info(f"Resolved conflict for '{skill_name}': Winner is '{winner.source_type}' ({winner.source_path}) due to {conflict_detail.resolution_reason}")
        else:
            merged_registry[skill_name] = candidates[0]

    return merged_registry, conflicts
