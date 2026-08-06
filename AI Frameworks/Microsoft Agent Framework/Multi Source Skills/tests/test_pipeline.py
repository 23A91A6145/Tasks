import pytest
from agents.manager import SkillManager
from agents.assistant import AssistantAgent

def test_skill_manager_and_registry():
    # Test manager reload and caching
    manager = SkillManager()
    registry = manager.get_registry()
    
    assert registry is not None
    # We should have the default skills loaded: math_add, translate, search_skill, etc.
    active_skills = [s.name for s in registry.list_skills()]
    assert "math_add" in active_skills
    assert "translate" in active_skills
    assert "search_skill" in active_skills
    assert "system_info" in active_skills
    assert "math_factorial" in active_skills
    assert "markdown_greet" in active_skills
    assert "math_subtract" in active_skills
    assert "send_email" in active_skills

    # Test type-safe parameter validation
    # math_add requires parameters 'a' (number) and 'b' (number)
    # 1. Missing parameter 'b'
    with pytest.raises(ValueError) as exc:
        registry.execute("math_add", a=10)
    assert "Missing required parameter: 'b'" in str(exc.value)

    # 2. Wrong parameter type
    with pytest.raises(ValueError) as exc:
        registry.execute("math_add", a="ten", b=20)
    assert "Parameter 'a' must be a number" in str(exc.value)

    # 3. Successful execution
    res = registry.execute("math_add", a=15, b=25)
    assert res == 40.0
    
    # 4. Check history log
    assert len(registry.execution_history) == 1
    assert registry.execution_history[0]["skill_name"] == "math_add"
    assert registry.execution_history[0]["status"] == "success"


def test_assistant_agent_loop():
    manager = SkillManager()
    agent = AssistantAgent(manager)
    
    # Test prompt mapping to math_add
    res = agent.execute_query("Please sum 34 and 66")
    assert res["success"] is True
    assert res["action"] == "math_add"
    assert res["arguments"] == {"a": 34.0, "b": 66.0}
    assert float(res["observation"]) == 100.0
    assert "100" in res["answer"]

    # Test prompt mapping to math_factorial
    res = agent.execute_query("Calculate factorial of 5")
    assert res["success"] is True
    assert res["action"] == "math_factorial"
    assert res["arguments"] == {"n": 5}
    assert int(res["observation"]) == 120
    assert "120" in res["answer"]
    
    # Test fallback query
    res = agent.execute_query("Sing me a song")
    assert res["success"] is False
    assert res["action"] == "none"
