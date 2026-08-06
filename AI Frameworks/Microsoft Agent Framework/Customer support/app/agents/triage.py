from agent_framework import Agent, SlidingWindowStrategy
from app.config import get_chat_client

def get_triage_agent() -> Agent:
    client = get_chat_client()
    compaction = SlidingWindowStrategy(keep_last_groups=6, preserve_system=True)
    return Agent(
        client=client,
        id="triage",
        name="Triage",
        description="Responsible for identifying the customer's intent and routing them to the correct specialist.",
        require_per_service_call_history_persistence=True,
        compaction_strategy=compaction,
        instructions=(
            "You are the Triage Agent, the primary coordinator of AI Customer Support.\n"
            "Your main role is to understand the customer's query and call the correct handoff tool:\n"
            "- Refunds, billing, invoices, payment queries -> call 'handoff_to_Billing'.\n"
            "- Server issues, crashes, password resets, logins -> call 'handoff_to_Technical'.\n"
            "- Operating hours, pricing plans, business locations -> call 'handoff_to_General'.\n"
            "- If the query is vague, ask clarifying questions first.\n"
            "CRITICAL: You MUST call the actual handoff tool function to route. Do NOT output raw JSON or write the tool name in your response text. You must actually execute the function tool."
        )
    )
