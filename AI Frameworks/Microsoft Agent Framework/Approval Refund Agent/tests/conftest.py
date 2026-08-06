import os
import glob
import pytest

# Deterministic, offline test environment. Must be set before any app import.
os.environ["LLM_PROVIDER"] = "mock"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["MAX_AUTO_APPROVE_AMOUNT"] = "50"
os.environ["MANAGER_LIMIT"] = "100"
os.environ.setdefault("APPROVAL_SLA_TIMEOUT_SECONDS", "300")

import app.config  # noqa: E402  (ensure settings/env load first)


@pytest.fixture(autouse=True)
def clean_workspace():
    """Wipes the DB file, checkpoints, notification outbox, and logs for clean tests."""
    from app.approval import DB_FILE
    from app.config import CHECKPOINT_DIR, LOG_DIR
    from app.services import NOTIFICATION_OUTBOX

    for path in (DB_FILE, NOTIFICATION_OUTBOX):
        if path.exists():
            path.unlink()

    for f_path in glob.glob(str(CHECKPOINT_DIR / "*.json")):
        try:
            os.unlink(f_path)
        except OSError:
            pass

    for f_path in glob.glob(str(LOG_DIR / "*.log")):
        try:
            os.unlink(f_path)
        except OSError:
            pass

    yield

    for path in (DB_FILE, NOTIFICATION_OUTBOX):
        if path.exists():
            path.unlink()
    for f_path in glob.glob(str(CHECKPOINT_DIR / "*.json")):
        try:
            os.unlink(f_path)
        except OSError:
            pass
