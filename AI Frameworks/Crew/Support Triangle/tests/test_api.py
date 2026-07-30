import pytest
from fastapi.testclient import TestClient

from api import fastapi_app

client = TestClient(fastapi_app.app)


@pytest.fixture(autouse=True)
def clear_history():
    fastapi_app.store.clear()


class TestHealth:
    def test_health_endpoint(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.1.0"


class TestChat:
    def test_chat_empty_query(self):
        resp = client.post("/chat", json={"query": ""})
        assert resp.status_code == 422

    def test_chat_missing_field(self):
        resp = client.post("/chat", json={})
        assert resp.status_code == 422

    def test_chat_too_long(self):
        resp = client.post("/chat", json={"query": "x" * 2001})
        assert resp.status_code == 422


class TestHistory:
    def test_history_paginated(self):
        resp = client.get("/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "entries" in data
        assert "total" in data
        assert data["entries"] == []

    def test_history_with_limit(self):
        resp = client.get("/history?limit=5")
        assert resp.status_code == 200

    def test_history_entry_not_found(self):
        resp = client.get("/history/99999")
        assert resp.status_code == 404

    def test_history_invalid_limit(self):
        resp = client.get("/history?limit=-1")
        assert resp.status_code == 422

    def test_history_classification_filter(self):
        resp = client.get("/history?classification=billing")
        assert resp.status_code == 200

    def test_history_search(self):
        resp = client.get("/history?search=test")
        assert resp.status_code == 200


class TestStats:
    def test_stats_empty(self):
        resp = client.get("/stats")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestExport:
    def test_export_json(self):
        resp = client.get("/export?format=json")
        assert resp.status_code == 200

    def test_export_csv(self):
        resp = client.get("/export?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]


class TestFeedback:
    def test_feedback_not_found(self):
        resp = client.post("/history/99999/feedback", json={"feedback": 1})
        assert resp.status_code == 404

    def test_feedback_invalid_value(self):
        resp = client.post("/history/1/feedback", json={"feedback": 99})
        assert resp.status_code == 422


class TestDelete:
    def test_delete_not_found(self):
        resp = client.delete("/history/99999")
        assert resp.status_code == 404
