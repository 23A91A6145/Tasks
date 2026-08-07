import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# 1. Create a single shared in-memory SQLite engine with StaticPool
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 2. Patch the global engine in apps.api.database BEFORE importing main or route packages
import apps.api.database
apps.api.database.engine = test_engine

from apps.api.main import app

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    # Re-create all tables for clean test isolation on every test run
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        # Bind the session to the context var so get_active_session() retrieves it
        from apps.api.database import db_session_var
        token = db_session_var.set(session)
        try:
            yield session
        finally:
            try:
                db_session_var.reset(token)
            except ValueError:
                pass

@pytest.fixture(name="client")
def client_fixture():
    # No dependency overrides required since the global engine is patched!
    client = TestClient(app)
    yield client
