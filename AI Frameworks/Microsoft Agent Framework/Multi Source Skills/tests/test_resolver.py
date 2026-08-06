import pytest
from models.skill import Skill
from resolver.overlap_detector import detect_overlaps
from resolver.priority import resolve_conflict
from resolver.merge import normalize_name, validate_skill, merge_skills
from configs.settings import DEFAULT_PRIORITIES, SKILL_OVERRIDES

def dummy_handler():
    return "ok"

def test_normalize_name():
    assert normalize_name("Math-Add") == "math_add"
    assert normalize_name("search.skill.google") == "search_skill_google"
    assert normalize_name("  Trim_and_Lower ") == "trim_and_lower"
    assert normalize_name("Special@#$Chars!") == "specialchars"


def test_validate_skill():
    # Valid skill
    valid = Skill(
        name="test_skill",
        description="A valid skill",
        source_type="inline",
        source_path="local",
        handler=dummy_handler
    )
    assert validate_skill(valid) is True
    
    # Missing description
    invalid_desc = Skill(
        name="test_skill",
        description="",
        source_type="inline",
        source_path="local",
        handler=dummy_handler
    )
    assert validate_skill(invalid_desc) is False

    # Missing handler
    invalid_handler = Skill(
        name="test_skill",
        description="Missing handler",
        source_type="inline",
        source_path="local",
        handler=None
    )
    assert validate_skill(invalid_handler) is False


def test_detect_overlaps():
    skills = [
        Skill(name="search", description="S1", source_type="file", source_path="f1", handler=dummy_handler),
        Skill(name="search", description="S2", source_type="inline", source_path="f2", handler=dummy_handler),
        Skill(name="math", description="M1", source_type="class", source_path="f3", handler=dummy_handler)
    ]
    grouped = detect_overlaps(skills)
    assert len(grouped["search"]) == 2
    assert len(grouped["math"]) == 1


def test_resolve_conflict_by_priority():
    # Set default mock priorities
    DEFAULT_PRIORITIES["inline"] = 100
    DEFAULT_PRIORITIES["class"] = 80
    DEFAULT_PRIORITIES["file"] = 50
    
    s_inline = Skill(name="search", description="S1", source_type="inline", source_path="inline_p", handler=dummy_handler)
    s_class = Skill(name="search", description="S2", source_type="class", source_path="class_p", handler=dummy_handler)
    s_file = Skill(name="search", description="S3", source_type="file", source_path="file_p", handler=dummy_handler)
    
    # Resolve
    winner, detail = resolve_conflict("search", [s_file, s_class, s_inline])
    
    assert winner.source_type == "inline"
    assert winner.source_path == "inline_p"
    assert detail.winning_source_type == "inline"
    assert "Highest resolved priority" in detail.resolution_reason


def test_resolve_conflict_by_override():
    # Configure mock override
    SKILL_OVERRIDES["search"] = {
        "preferred_source": "class",
        "reason": "Forced override to class"
    }
    
    s_inline = Skill(name="search", description="S1", source_type="inline", source_path="inline_p", handler=dummy_handler)
    s_class = Skill(name="search", description="S2", source_type="class", source_path="class_p", handler=dummy_handler)
    
    winner, detail = resolve_conflict("search", [s_inline, s_class])
    
    assert winner.source_type == "class"
    assert winner.source_path == "class_p"
    assert "Explicit user override" in detail.resolution_reason
    
    # Clean up global state override
    del SKILL_OVERRIDES["search"]
