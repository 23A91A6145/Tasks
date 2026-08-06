from agent_framework import Agent, tool, SlidingWindowStrategy
from app.config import get_chat_client

@tool(approval_mode="never_require")
def get_pricing_info() -> str:
    """Retrieve details about the current pricing tiers and subscription options."""
    return (
        "Subscription Tiers:\n"
        "1. Free Tier: $0/month (Basic features, 100 queries/month, community support).\n"
        "2. Pro Tier: $15/month (Advanced features, unlimited queries, 24/7 email support).\n"
        "3. Enterprise Tier: Custom pricing (Dedicated account manager, SLA guarantees, SLA support)."
    )

def get_general_agent() -> Agent:
    client = get_chat_client()
    compaction = SlidingWindowStrategy(keep_last_groups=6, preserve_system=True)
    return Agent(
        client=client,
        id="general",
        name="General",
        description="Handles general support queries, pricing inquiries, company info, and operating hours.",
        require_per_service_call_history_persistence=True,
        compaction_strategy=compaction,
        instructions=(
            "You are the General Support Specialist. You handle office hours, pricing, plan tiers, and office location.\n"
            "Tools:\n"
            "- 'get_pricing_info': Retrieve subscription plans.\n"
            "Company Details:\n"
            "- Operating Hours: Monday to Friday, 9:00 AM - 5:00 PM EST.\n"
            "- Office Location: 100 Innovation Way, Boston, MA 02110.\n"
            "- Contact Email: support@example.com.\n"
            "Guidelines:\n"
            "1. Answer company questions. Call 'get_pricing_info' if the customer asks about cost or subscription differences.\n"
            "2. Once resolved, or if the user asks a non-general question, you MUST call the function tool 'handoff_to_Triage' immediately. Do NOT write '(handoff_to_Triage)' or 'handoff_to_Triage' in your message text. You must actually execute the function tool to transfer control."
        ),
        tools=[get_pricing_info]
    )
