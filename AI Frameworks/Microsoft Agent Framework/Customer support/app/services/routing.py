def list_agents_info() -> list[dict]:
    """Returns details about the available specialist agents and their routing roles."""
    return [
        {
            "id": "triage",
            "name": "Triage Agent",
            "role": "Coordinator",
            "description": "Welcomes users, analyzes query intent, and delegates tasks to specialists.",
            "tools": []
        },
        {
            "id": "billing",
            "name": "Billing Agent",
            "role": "Billing & Refund Specialist",
            "description": "Handles transaction checks, invoices, and virtual refund processing.",
            "tools": ["get_refund_status", "process_virtual_refund"]
        },
        {
            "id": "technical",
            "name": "Technical Agent",
            "role": "Diagnostics & Account Specialist",
            "description": "Troubleshoots crashes, server checks, and triggers password resets.",
            "tools": ["check_server_status", "send_password_reset_email"]
        },
        {
            "id": "general",
            "name": "General Agent",
            "role": "Information Specialist",
            "description": "Answers questions about operating hours, office location, and pricing plans.",
            "tools": ["get_pricing_info"]
        }
    ]
