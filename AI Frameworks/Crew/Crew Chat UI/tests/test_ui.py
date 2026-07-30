from datetime import datetime

from services.memory import ConversationMemory
from services.history import ChatHistory
from ui.theme import LIGHT, DARK, build_css


# ─── Theme ─────────────────────────────────────────────────────

def test_light_theme_has_all_keys():
    required = {"bg", "text", "primary", "user_bubble_bg", "assistant_bubble"}
    assert required.issubset(LIGHT.keys())


def test_dark_theme_has_all_keys():
    required = {"bg", "text", "primary", "user_bubble_bg", "assistant_bubble"}
    assert required.issubset(DARK.keys())


def test_build_css_returns_string():
    css = build_css(LIGHT)
    assert isinstance(css, str)
    assert len(css) > 100
    assert "<style>" in css
    assert "</style>" in css


def test_build_css_contains_theme_values():
    css = build_css(LIGHT)
    assert LIGHT["bg"] in css
    assert LIGHT["primary"] in css


def test_themes_different():
    assert LIGHT != DARK


def test_build_css_dark():
    css = build_css(DARK)
    assert DARK["bg"] in css


# ─── Memory ────────────────────────────────────────────────────

def test_memory_add_and_count():
    mem = ConversationMemory()
    assert mem.is_empty
    assert mem.count == 0

    mem.add("user", "Hello")
    assert mem.count == 1
    assert not mem.is_empty


def test_memory_get_context():
    mem = ConversationMemory()
    mem.add("user", "What is AI?")
    mem.add("assistant", "AI is...")
    context = mem.get_context(window=2)
    assert "What is AI?" in context
    assert "AI is..." in context


def test_memory_get_last_user_query():
    mem = ConversationMemory()
    mem.add("user", "first")
    mem.add("assistant", "response")
    mem.add("user", "second")
    assert mem.get_last_user_query() == "second"


def test_memory_max_history():
    mem = ConversationMemory(max_history=3)
    for i in range(5):
        mem.add("user", f"msg{i}")
    assert mem.count == 3
    assert "msg0" not in mem.get_context(5)
    assert "msg4" in mem.get_context(5)


def test_memory_clear():
    mem = ConversationMemory()
    mem.add("user", "test")
    mem.clear()
    assert mem.is_empty
    assert mem.count == 0


def test_memory_get_last_user_query_empty():
    mem = ConversationMemory()
    assert mem.get_last_user_query() == ""


# ─── Chat message structure ────────────────────────────────────

def test_message_structure():
    msg = {
        "role": "user",
        "content": "Hello",
        "timestamp": datetime.now().strftime("%I:%M %p"),
    }
    assert msg["role"] in ("user", "assistant")
    assert isinstance(msg["content"], str)
    assert len(msg["timestamp"]) > 0


def test_message_timestamp_format():
    ts = datetime.now().strftime("%I:%M %p")
    assert ":" in ts


# ─── Agent info (for sidebar) ──────────────────────────────────

def test_agent_info_structure():
    agents_info = [
        ("🔍 Research Specialist", "Gathers relevant information"),
        ("📊 Analysis Expert", "Extracts insights"),
        ("✍️ Response Writer", "Synthesizes final response"),
    ]
    assert len(agents_info) == 3
    for role, desc in agents_info:
        assert len(role) > 0
        assert len(desc) > 0


# ─── Provider config ───────────────────────────────────────────

def test_settings_provider_detection():
    from crew.config import Settings
    s = Settings()
    assert hasattr(s, "provider")
    assert s.provider in ("ollama", "openai", "none")


# ─── InputValidator ─────────────────────────────────────────────

def test_validator_sanitize_removes_script_tags():
    from services.validator import InputValidator
    result = InputValidator.sanitize("<script>alert('xss')</script>")
    assert "script" not in result
    assert "alert" not in result


def test_validator_sanitize_removes_event_handlers():
    from services.validator import InputValidator
    result = InputValidator.sanitize('<img onerror="alert(1)">')
    assert "onerror" not in result


def test_validator_sanitize_preserves_normal_text():
    from services.validator import InputValidator
    result = InputValidator.sanitize("Hello, world!")
    assert result == "Hello, world!"


def test_validator_validate_query_empty():
    from services.validator import InputValidator
    valid, msg = InputValidator.validate_query("")
    assert not valid
    assert "empty" in msg.lower()


def test_validator_validate_query_valid():
    from services.validator import InputValidator
    valid, msg = InputValidator.validate_query("What is AI?")
    assert valid
    assert msg == ""


def test_validator_validate_query_too_long():
    from services.validator import InputValidator
    long_text = "x" * (InputValidator.MAX_QUERY_LENGTH + 1)
    valid, msg = InputValidator.validate_query(long_text)
    assert not valid
    assert "exceed" in msg.lower()


def test_validator_prepare_query_sanitizes():
    from services.validator import InputValidator
    result = InputValidator.prepare_query("<script>alert(1)</script>Hello")
    assert "script" not in result
    assert "Hello" in result


# ─── ChatHistory ───────────────────────────────────────────────

def test_history_init(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    assert h.storage.exists()


def test_history_save_and_load(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    msgs = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    h.save("test1", msgs)
    loaded = h.load("test1")
    assert len(loaded) == 2
    assert loaded[0]["role"] == "user"
    assert loaded[1]["content"] == "Hi"


def test_history_load_missing(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    assert h.load("nonexistent") == []


def test_history_list_sessions(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    h.save("s1", [{"role": "user", "content": "a"}])
    h.save("s2", [{"role": "user", "content": "b"}])
    sessions = h.list_sessions()
    assert len(sessions) == 2
    assert sessions[0]["id"] == "s2"


def test_history_delete(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    h.save("test_del", [{"role": "user", "content": "x"}])
    h.delete("test_del")
    assert h.load("test_del") == []


def test_export_markdown(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    msgs = [
        {"role": "user", "content": "Hello", "timestamp": "10:00 AM"},
        {"role": "assistant", "content": "Hi there!", "timestamp": "10:01 AM"},
    ]
    md = h.export_markdown(msgs)
    assert "# Chat Export" in md
    assert "Hello" in md
    assert "Hi there!" in md


def test_export_json(tmp_path):
    h = ChatHistory(storage_dir=str(tmp_path / "sessions"))
    msgs = [{"role": "user", "content": "test"}]
    js = h.export_json(msgs)
    assert "exported_at" in js
    assert "messages" in js
    assert "test" in js


def test_estimate_tokens():
    assert ChatHistory.estimate_tokens("hello world") == 2
    assert ChatHistory.estimate_tokens("a") == 1


def test_compute_stats_empty():
    stats = ChatHistory.compute_stats([])
    assert stats["total"] == 0
    assert stats["user"] == 0
    assert stats["assistant"] == 0


def test_compute_stats_with_messages():
    msgs = [
        {"role": "user", "content": "Hello", "timestamp": "10:00 AM"},
        {"role": "assistant", "content": "Hi there!", "timestamp": "10:01 AM"},
        {"role": "user", "content": "How are you?", "timestamp": "10:02 AM"},
    ]
    stats = ChatHistory.compute_stats(msgs)
    assert stats["total"] == 3
    assert stats["user"] == 2
    assert stats["assistant"] == 1
    assert stats["estimated_tokens"] > 0


# ─── Suggested prompts ─────────────────────────────────────────

def test_suggested_prompts_exist():
    from ui.components import SUGGESTED_PROMPTS
    assert len(SUGGESTED_PROMPTS) >= 3
    for p in SUGGESTED_PROMPTS:
        assert len(p) > 10


# ─── Prompt templates ──────────────────────────────────────────

def test_prompt_templates_exist():
    from ui.components import PROMPT_TEMPLATES
    assert len(PROMPT_TEMPLATES) >= 3
    assert "General Q&A" in PROMPT_TEMPLATES
    assert "Code Review" in PROMPT_TEMPLATES


# ─── Mock Responder ─────────────────────────────────────────────

def test_mock_responder_greeting():
    from services.mock_responder import get_mock_response
    r = get_mock_response("hello")
    assert len(r) > 0
    assert "CrewAI" in r or "assistant" in r.lower()


def test_mock_responder_crewai_query():
    from services.mock_responder import get_mock_response
    r = get_mock_response("What is CrewAI?")
    assert "CrewAI" in r
    assert "framework" in r.lower()


def test_mock_responder_code_query():
    from services.mock_responder import get_mock_response
    r = get_mock_response("Write a Python function")
    assert "python" in r.lower() or "```" in r


# ─── Model Service ──────────────────────────────────────────────

def test_model_service_init():
    from services.model_service import ModelService
    ms = ModelService()
    assert ms.ollama_url == "http://localhost:11434"


# ─── CrewAssistant Fallback ─────────────────────────────────────

def test_crew_assistant_fallback():
    from crew.crew import CrewAssistant
    a = CrewAssistant()
    r = a.run("hello")
    assert len(r) > 0
    assert hasattr(a.metrics, 'used_fallback')
