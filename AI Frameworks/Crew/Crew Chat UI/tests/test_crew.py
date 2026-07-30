from crew.crew import CrewAssistant, CrewMetrics
from crew.agents import create_researcher, create_analyst, create_writer, reset_agents, get_all_agents
from crew.tasks import create_research_task, create_analysis_task, create_writing_task, get_all_tasks
from crew.config import settings
from services.logger import logger


# ─── Settings ───────────────────────────────────────────────────

def test_settings_load():
    assert hasattr(settings, "OPENAI_MODEL_NAME")
    assert hasattr(settings, "OLLAMA_MODEL_NAME")
    assert settings.APP_NAME == "Crew Assistant"
    assert settings.APP_VERSION == "5.0.0"


def test_settings_provider_is_detected():
    assert settings.provider in ("ollama", "openai", "none")


def test_settings_active_model_exists():
    assert len(settings.active_model) > 0


def test_settings_repr():
    r = repr(settings)
    assert "provider=" in r
    assert "model=" in r


def test_settings_is_ready_property():
    assert hasattr(settings, "is_ready")
    assert isinstance(settings.is_ready, bool)


def test_settings_missing_keys_property():
    keys = settings.missing_keys
    assert isinstance(keys, list)
    if settings.provider == "none":
        assert len(keys) > 0
    else:
        assert len(keys) == 0


# ─── Logger ─────────────────────────────────────────────────────

def test_logger_basic():
    assert logger.name == "crew"
    assert logger.level > 0


def test_logger_writes_to_file(tmp_path):
    import logging
    test_log = tmp_path / "test.log"
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(str(test_log))
    handler.setFormatter(logging.Formatter("%(message)s"))
    test_logger.addHandler(handler)
    test_logger.info("hello")
    handler.flush()
    assert test_log.read_text().strip() == "hello"


# ─── Agents ─────────────────────────────────────────────────────

def test_researcher_agent():
    reset_agents()
    agent = create_researcher()
    assert agent.role == "Research Specialist"
    assert "information" in agent.goal.lower()


def test_analyst_agent():
    reset_agents()
    agent = create_analyst()
    assert agent.role == "Analysis Expert"
    assert "analy" in agent.goal.lower()


def test_writer_agent():
    reset_agents()
    agent = create_writer()
    assert agent.role == "Response Writer"
    assert "synthesize" in agent.goal.lower()


def test_agents_are_singletons():
    reset_agents()
    a1 = create_researcher()
    a2 = create_researcher()
    assert a1 is a2


def test_get_all_agents_returns_three():
    reset_agents()
    agents = get_all_agents()
    assert len(agents) == 3
    assert agents[0].role == "Research Specialist"
    assert agents[1].role == "Analysis Expert"
    assert agents[2].role == "Response Writer"


def test_reset_agents_clears_cache():
    reset_agents()
    a1 = create_researcher()
    reset_agents()
    a2 = create_researcher()
    assert a1 is not a2


# ─── Tasks ──────────────────────────────────────────────────────

def test_research_task():
    task = create_research_task("What is CrewAI?")
    assert "CrewAI" in task.description
    assert task.agent.role == "Research Specialist"
    assert "summary" in task.expected_output.lower()


def test_analysis_task():
    task = create_analysis_task("What is CrewAI?")
    assert "CrewAI" in task.description
    assert task.agent.role == "Analysis Expert"
    assert "insights" in task.expected_output.lower()


def test_writing_task():
    task = create_writing_task("What is CrewAI?")
    assert "CrewAI" in task.description
    assert task.agent.role == "Response Writer"
    assert "markdown" in task.expected_output.lower()


def test_get_all_tasks_returns_three():
    tasks = get_all_tasks("test query")
    assert len(tasks) == 3
    assert "research" in tasks[0].description.lower()
    assert "analy" in tasks[1].description.lower()
    assert "write" in tasks[2].description.lower()


def test_tasks_reuse_same_agent_instances():
    t1 = create_research_task("q")
    t2 = create_research_task("q")
    assert t1.agent is t2.agent


# ─── CrewAssistant ──────────────────────────────────────────────

def test_crew_assistant_creation():
    assistant = CrewAssistant()
    assert assistant.crew is None
    assert assistant.metrics.duration == 0.0


def test_crew_assistant_empty_query():
    assistant = CrewAssistant()
    result = assistant.run("")
    assert "valid query" in result

    result = assistant.run("   ")
    assert "valid query" in result


def test_crew_assistant_builds_crew_for_valid_query():
    assistant = CrewAssistant()
    assistant._build_crew("test")
    assert assistant.crew is not None
    assert len(assistant.crew.tasks) == 3


def test_crew_assistant_metrics_on_empty():
    assistant = CrewAssistant()
    assistant.run("")
    assert assistant.metrics.error is None


def test_crew_assistant_has_descriptive_repr():
    assistant = CrewAssistant()
    assert hasattr(assistant, "metrics")


# ─── CrewMetrics ────────────────────────────────────────────────

def test_metrics_defaults():
    m = CrewMetrics()
    assert m.duration == 0.0
    assert m.tasks_completed == 0
    assert m.error is None


def test_metrics_with_error():
    m = CrewMetrics(error="test error")
    assert m.error == "test error"
