"""Sample vulnerable application fixture for automated evaluation."""

import os
import pickle
import subprocess

# Vulnerability: Hardcoded API Secret
API_KEY = "sk-live-98742398472398472394872"


def get_user_data(user_id: str):
    # Vulnerability: SQL Injection via f-string
    query = f"SELECT * FROM users WHERE id = '{user_id}' AND is_active = 1"
    print(f"Executing query: {query}")
    return query


def run_diagnostics(cmd: str):
    # Vulnerability: Command Injection via shell=True
    subprocess.run(f"ping -c 1 {cmd}", shell=True)


def restore_session(payload: bytes):
    try:
        # Vulnerability: Insecure Deserialization with Pickle
        return pickle.loads(payload)
    except:
        # Code smell: Bare except
        return None
