from agent_framework.orchestrations import HandoffBuilder
from app.agents.triage import get_triage_agent
from app.agents.billing import get_billing_agent
from app.agents.technical import get_technical_agent
from app.agents.general import get_general_agent

def create_handoff_workflow(checkpoint_storage=None):
    """Creates and returns the customer support handoff workflow."""
    triage = get_triage_agent()
    billing = get_billing_agent()
    technical = get_technical_agent()
    general = get_general_agent()

    # Build the conversational handoff workflow
    builder = (
        HandoffBuilder(name="customer_support")
        .participants([triage, billing, technical, general])
        .add_handoff(triage, [billing], description="Route billing, payments, refund status, or subscription queries to the Billing Specialist.")
        .add_handoff(triage, [technical], description="Route login issues, password resets, server diagnostics, app crashes, or bug reports to the Technical Specialist.")
        .add_handoff(triage, [general], description="Route hours of operations, pricing information, office locations, or general queries to the General Support Specialist.")
        .add_handoff(billing, [triage], description="Return control back to the Triage Agent after resolving billing/refund inquiries.")
        .add_handoff(technical, [triage], description="Return control back to the Triage Agent after troubleshooting or diagnostic checks.")
        .add_handoff(general, [triage], description="Return control back to the Triage Agent after answering general info queries.")
        .with_start_agent(triage)
    )

    if checkpoint_storage:
        builder = builder.with_checkpointing(checkpoint_storage)

    return builder.build()
