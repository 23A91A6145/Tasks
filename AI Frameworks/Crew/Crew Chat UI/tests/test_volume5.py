from services.token_counter import TokenCounter
from services.provider_service import get_providers, get_available_providers
from services.validator import InputValidator
from services.mock_responder import get_mock_response
from crew.crew import CrewAssistant


# ─── TokenCounter ───────────────────────────────────────────────

def test_token_counter_estimate_empty():
    assert TokenCounter.estimate("") == 0


def test_token_counter_estimate_text():
    assert TokenCounter.estimate("hello world") == 2
    assert TokenCounter.estimate("a") == 1


def test_token_counter_estimate_messages():
    msgs = [
        {"role": "user", "content": "hello world"},
        {"role": "assistant", "content": "hi there"},
    ]
    stats = TokenCounter.estimate_messages(msgs)
    assert stats["total"] == 4
    assert stats["per_role"]["user"] == 2
    assert stats["per_role"]["assistant"] == 2


def test_token_counter_estimate_cost():
    assert TokenCounter.estimate_cost(100) == "free"


def test_token_counter_format_tokens():
    assert TokenCounter.format_tokens(500) == "500 tokens"
    assert TokenCounter.format_tokens(1500) == "1.5K tokens"


def test_token_counter_summarize():
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "world"},
    ]
    summary = TokenCounter.summarize_token_usage(msgs)
    assert "total" in summary.lower() or "tokens" in summary.lower()


def test_token_counter_estimate_messages_empty():
    stats = TokenCounter.estimate_messages([])
    assert stats["total"] == 0


# ─── Provider Service ───────────────────────────────────────────

def test_get_providers():
    providers = get_providers()
    assert "ollama" in providers
    assert "openai" in providers
    assert "openrouter" in providers


def test_get_available_providers():
    available = get_available_providers()
    assert len(available) >= 2
    names = [p["name"] for p in available]
    assert "ollama" in names
    assert "openai" in names


def test_provider_config_ollama():
    from services.provider_service import ProviderConfig
    cfg = ProviderConfig("ollama", "Ollama", "", "")
    assert cfg.name == "ollama"
    assert cfg.is_configured


def test_provider_config_openai():
    from services.provider_service import ProviderConfig
    cfg = ProviderConfig("openai", "OpenAI", "OPENAI_API_KEY")
    assert cfg.name == "openai"


def test_provider_config_to_dict():
    from services.provider_service import ProviderConfig
    cfg = ProviderConfig("test", "Test", "TEST_KEY")
    d = cfg.to_dict()
    assert d["name"] == "test"
    assert d["display"] == "Test"
    assert "configured" in d


# ─── Validator (Volume 5 additions) ─────────────────────────────

def test_validator_sanitize_preserves_markdown():
    result = InputValidator.sanitize("**bold** and `code`")
    assert "**bold**" in result


def test_validator_sanitize_removes_javascript_protocol():
    result = InputValidator.sanitize("javascript:alert(1)")
    assert "javascript:" not in result


def test_validator_prepare_query_empty():
    result = InputValidator.prepare_query("")
    assert result == ""


def test_validator_prepare_query_valid():
    result = InputValidator.prepare_query("  hello world  ")
    assert result == "hello world"


# ─── Mock Responder ─────────────────────────────────────────────

def test_mock_responder_empty():
    r = get_mock_response("")
    assert len(r) > 0


def test_mock_responder_random():
    r1 = get_mock_response("this is a random query about nothing in particular")
    r2 = get_mock_response("another random query that is different")
    assert len(r1) > 0
    assert len(r2) > 0


def test_mock_responder_analysis():
    r = get_mock_response("Analyze the impact of AI on healthcare")
    assert len(r) > 0


# ─── CrewAssistant Volume 5 ─────────────────────────────────────

def test_crew_assistant_fallback_generates():
    a = CrewAssistant()
    r = a.run("What is CrewAI?")
    assert len(r) > 10
    assert "CrewAI" in r
    assert a.metrics.used_fallback


def test_crew_assistant_metrics_on_fallback():
    a = CrewAssistant()
    a.run("test")
    assert hasattr(a.metrics, 'used_fallback')
    assert hasattr(a.metrics, 'duration')
    assert a.metrics.duration >= 0
