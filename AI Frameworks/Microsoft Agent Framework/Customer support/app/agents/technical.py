from typing import Annotated
from agent_framework import Agent, tool, SlidingWindowStrategy
from app.config import get_chat_client

@tool(approval_mode="never_require")
def check_server_status() -> str:
    """Check the operational status of the main application servers and API endpoints."""
    # Mock system check
    return "All systems operational. API Gateway response latency: 45ms. Database health: 99.9%."

@tool(approval_mode="never_require")
def send_password_reset_email(
    email: Annotated[str, "The customer's email address"]
) -> str:
    """Send a secure password reset link to the customer's email address."""
    if "@" not in email:
        return "Error: Invalid email format."
    return f"Success: A password reset link has been dispatched to {email}. The link expires in 15 minutes."

def get_technical_agent() -> Agent:
    client = get_chat_client()
    compaction = SlidingWindowStrategy(keep_last_groups=6, preserve_system=True)
    return Agent(
        client=client,
        id="technical",
        name="Technical",
        description="Handles all technical, troubleshooting, login, password, and app crash issues.",
        require_per_service_call_history_persistence=True,
        compaction_strategy=compaction,
        instructions=(
            "You are the Technical Support Specialist. You handle app crashes, password resets, logins, and API bugs.\n"
            "Tools:\n"
            "- 'check_server_status': Run server diagnostics.\n"
            "- 'send_password_reset_email': Dispatch reset link.\n"
            "Guidelines:\n"
            "1. CRITICAL: If the customer does not provide the required email address for a password reset, do NOT try to call the tool or write JSON. Ask them for it in plain language first.\n"
            "2. Once you have the email, call 'send_password_reset_email'. Do NOT write raw JSON in your response.\n"
            "3. If the user complains about crashes or latency, call 'check_server_status' immediately.\n"
            "4. Once resolved, or if the user asks a non-technical question, you MUST call the function tool 'handoff_to_Triage' immediately. Do NOT write '(handoff_to_Triage)' or 'handoff_to_Triage' in your message text. You must actually execute the function tool to transfer control."
        ),
        tools=[check_server_status, send_password_reset_email]
    )
