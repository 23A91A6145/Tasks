#!/usr/bin/env python3
"""
Persistent-Memory Chat CLI
Powered by Microsoft Agent Framework (AgentThread + FileHistoryProvider)

Entry point script.
"""

import sys
from app.config import load_config
from app.cli import PersistentChatCLI

def main():
    try:
        config = load_config()
        cli_app = PersistentChatCLI(config)
        cli_app.run()
    except Exception as e:
        print(f"Fatal Startup Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
