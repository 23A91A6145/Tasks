from typing import Annotated
from agent_framework import Agent, tool, SlidingWindowStrategy
from app.config import get_chat_client

@tool(approval_mode="never_require")
def get_refund_status(
    ticket_id: Annotated[str, "The unique ID of the support ticket or transaction ID"]
) -> str:
    """Retrieve the status of a refund request."""
    # Mock database lookup
    if ticket_id.endswith("123"):
        return f"Refund for ticket {ticket_id} was successfully processed on 2026-08-01 for $49.99."
    elif ticket_id.endswith("999"):
        return f"Refund for ticket {ticket_id} is currently PENDING bank approval. Expected completion in 3 business days."
    else:
        return f"Refund for ticket {ticket_id} not found. Please verify the ticket ID."

@tool(approval_mode="never_require")
def process_virtual_refund(
    ticket_id: Annotated[str, "The unique ID of the support ticket or transaction ID"],
    amount: Annotated[float, "The refund amount in USD"]
) -> str:
    """Process a virtual refund for a transaction."""
    if amount <= 0:
        return "Error: Refund amount must be greater than 0."
    return f"Success: A virtual refund of ${amount:.2f} has been processed for ticket {ticket_id}. It will appear on the customer's statement in 5-10 business days."

def get_billing_agent() -> Agent:
    client = get_chat_client()
    compaction = SlidingWindowStrategy(keep_last_groups=6, preserve_system=True)
    return Agent(
        client=client,
        id="billing",
        name="Billing",
        description="Handles all billing, payment, invoice, and refund issues.",
        require_per_service_call_history_persistence=True,
        compaction_strategy=compaction,
        instructions=(
            "You are the Billing Support Specialist. You resolve transaction, invoice, and refund queries.\n"
            "Tools:\n"
            "- 'get_refund_status': Check status of an existing refund.\n"
            "- 'process_virtual_refund': Trigger a new refund.\n"
            "Guidelines:\n"
            "1. CRITICAL: If the customer does not provide the required ticket ID or transaction ID, do NOT try to call the tool or write JSON. Ask the customer for it in plain language first.\n"
            "2. Once you have the ID, invoke the appropriate tool. Do NOT write raw JSON in your chat response.\n"
            "3. Once resolved, or if the user asks a non-billing question, you MUST call the function tool 'handoff_to_Triage' immediately. Do NOT write '(handoff_to_Triage)' or 'handoff_to_Triage' in your message text. You must actually execute the function tool to transfer control."
        ),
        tools=[get_refund_status, process_virtual_refund]
    )
