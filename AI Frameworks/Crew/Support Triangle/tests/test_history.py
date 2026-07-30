import pytest

from api.history_store import HistoryStore


@pytest.fixture
def store():
    s = HistoryStore()
    s.clear()
    return s


class TestHistoryStore:
    def test_add_and_count(self, store):
        store.add_entry("q1", "billing", ["T1"], "r", "resp1", True, "OK", 1.0)
        store.add_entry("q2", "technical", ["T2"], "r", "resp2", False, "", 2.5)
        entries = store.get_all()
        assert len(entries) == 2

    def test_add_returns_correct_fields(self, store):
        eid = store.add_entry("test query", "billing", ["Curr", "Data"], "invoice",
                              "response text", True, "APPROVED", 3.45, conversation_id="conv_test")
        entries = store.get_all()
        e = entries[0]
        assert e["query"] == "test query"
        assert e["classification"] == "billing"
        assert e["tools_used"] == ["Curr", "Data"]
        assert e["routing_rationale"] == "invoice"
        assert e["response"] == "response text"
        assert e["validated"] is True
        assert e["validation_report"] == "APPROVED"
        assert e["execution_time"] == 3.45
        assert e["conversation_id"] == "conv_test"
        assert e["feedback"] is None
        assert e["id"] > 0

    def test_get_by_id(self, store):
        eid = store.add_entry("test", "sales", [], "", "resp", False, "", 0.5)
        e = store.get_by_id(eid)
        assert e is not None
        assert e["query"] == "test"

    def test_get_by_id_not_found(self, store):
        assert store.get_by_id(99999) is None

    def test_clear(self, store):
        store.add_entry("q", "billing", [], "", "r", True, "", 1.0)
        assert len(store.get_all()) == 1
        store.clear()
        assert len(store.get_all()) == 0

    def test_limit(self, store):
        for i in range(10):
            store.add_entry(f"q{i}", "billing", [], "", "r", True, "", 1.0)
        assert len(store.get_all(limit=3)) == 3

    def test_empty_store(self, store):
        assert store.get_all() == []

    def test_conversation_id_filter(self, store):
        store.add_entry("q1", "billing", [], "", "r1", True, "", 1.0, conversation_id="a")
        store.add_entry("q2", "technical", [], "", "r2", True, "", 1.0, conversation_id="a")
        store.add_entry("q3", "sales", [], "", "r3", True, "", 1.0, conversation_id="b")
        entries = store.get_all(conversation_id="a")
        assert len(entries) == 2
        assert entries[0]["query"] == "q2"

    def test_search(self, store):
        store.add_entry("refund request", "billing", [], "", "here is your refund", True, "", 1.0)
        store.add_entry("login issue", "technical", [], "", "reset password", True, "", 1.0)
        entries = store.get_all(search="refund")
        assert len(entries) == 1
        assert entries[0]["query"] == "refund request"

    def test_classification_filter(self, store):
        store.add_entry("q1", "billing", [], "", "r", True, "", 1.0)
        store.add_entry("q2", "technical", [], "", "r", True, "", 1.0)
        entries = store.get_all(classification="billing")
        assert len(entries) == 1

    def test_update_feedback(self, store):
        eid = store.add_entry("q", "billing", [], "", "r", True, "", 1.0)
        store.update_feedback(eid, 1)
        e = store.get_by_id(eid)
        assert e["feedback"] == 1

    def test_update_feedback_invalid(self, store):
        eid = store.add_entry("q", "billing", [], "", "r", True, "", 1.0)
        result = store.update_feedback(eid, 0)
        assert result is False

    def test_delete_entry(self, store):
        eid = store.add_entry("q", "billing", [], "", "r", True, "", 1.0)
        assert store.get_by_id(eid) is not None
        store.delete_entry(eid)
        assert store.get_by_id(eid) is None

    def test_get_conversation(self, store):
        store.add_entry("q1", "billing", [], "", "r1", True, "", 1.0, conversation_id="c1")
        store.add_entry("q2", "billing", [], "", "r2", True, "", 1.0, conversation_id="c1")
        entries = store.get_conversation("c1")
        assert len(entries) == 2

    def test_count(self, store):
        store.add_entry("q1", "billing", [], "", "r", True, "", 1.0)
        store.add_entry("q2", "technical", [], "", "r", True, "", 1.0)
        assert store.count() == 2
        assert store.count(classification="billing") == 1
