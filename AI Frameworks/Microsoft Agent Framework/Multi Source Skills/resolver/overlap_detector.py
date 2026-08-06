from typing import List, Dict
from models.skill import Skill

def detect_overlaps(skills: List[Skill]) -> Dict[str, List[Skill]]:
    """
    Groups skills by name. 
    Any key in the returned dictionary with more than one element indicates an overlap/conflict.
    """
    grouped: Dict[str, List[Skill]] = {}
    for skill in skills:
        grouped.setdefault(skill.name, []).append(skill)
    return grouped
