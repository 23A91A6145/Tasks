"""Sample clean and secure application fixture for automated evaluation."""

import os
import subprocess
from pydantic import BaseModel, Field


class UserQuery(BaseModel):
    user_id: int = Field(gt=0, description="Positive user identifier")


def get_user_data(user: UserQuery):
    # Safe parameterized query pattern
    query = "SELECT * FROM users WHERE id = :user_id AND is_active = 1"
    params = {"user_id": user.user_id}
    return query, params


def run_diagnostics(host: str):
    # Safe subprocess execution without shell=True
    subprocess.run(["ping", "-c", "1", host], check=True)


def restore_session(payload: str):
    try:
        import json
        return json.loads(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return None
