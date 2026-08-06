import pytest
from pathlib import Path
from models.skill import Skill
from providers.inline_provider import InlineProvider, register_inline_skill, _REGISTERED_INLINE_SKILLS
from providers.class_provider import ClassProvider, skill_method, register_class_instance
from providers.file_provider import FileProvider
from configs.settings import DEFAULT_PRIORITIES

def test_inline_provider():
    # Define a temporary inline skill
    @register_inline_skill(
        name="test_temp_inline",
        description="A temp inline skill for test",
        parameters={"val": {"type": "string"}}
    )
    def temp_func(val: str):
        return f"result: {val}"
        
    provider = InlineProvider()
    skills = provider.load_skills()
    
    # Assertions
    names = [s.name for s in skills]
    assert "test_temp_inline" in names
    
    target_skill = next(s for s in skills if s.name == "test_temp_inline")
    assert target_skill.source_type == "inline"
    assert target_skill.execute(val="hello") == "result: hello"


def test_class_provider():
    class TestClassSkills:
        @skill_method(
            name="test_class_method",
            description="Test class method skill"
        )
        def run_me(self, word: str) -> int:
            return len(word)
            
    # Register instance
    register_class_instance(TestClassSkills())
    
    provider = ClassProvider()
    skills = provider.load_skills()
    
    names = [s.name for s in skills]
    assert "test_class_method" in names
    
    target_skill = next(s for s in skills if s.name == "test_class_method")
    assert target_skill.source_type == "class"
    assert target_skill.execute(word="antigravity") == 11


def test_file_provider_yaml_and_json(tmp_path):
    # Setup temporary skills directory in tmp_path
    file_prov = FileProvider()
    # Override directory to use tmp_path
    file_prov.directory = tmp_path
    file_prov.config = {"enabled": True}
    
    # 1. Write YAML skill
    yaml_content = """
name: "temp_yaml_skill"
description: "A temp yaml skill"
version: "1.0.0"
parameters:
  num:
    type: "integer"
execute_code: |
  def execute(num):
      return num * 10
"""
    yaml_file = tmp_path / "skill1.yaml"
    yaml_file.write_text(yaml_content)

    # 2. Write JSON skill
    json_content = """
{
  "name": "temp_json_skill",
  "description": "A temp json skill",
  "command": "echo {text}"
}
"""
    json_file = tmp_path / "skill2.json"
    json_file.write_text(json_content)

    # Load skills
    skills = file_prov.load_skills()
    names = [s.name for s in skills]
    
    assert "temp_yaml_skill" in names
    assert "temp_json_skill" in names
    
    s_yaml = next(s for s in skills if s.name == "temp_yaml_skill")
    assert s_yaml.execute(num=5) == 50
    
    s_json = next(s for s in skills if s.name == "temp_json_skill")
    assert s_json.execute(text="antigravity") == "antigravity"
