from sqlmodel import select
from apps.api.database import get_active_session
from apps.api.models import User, SupportTicket, SupportTicketStatus, AuditLog
from agents.llm_client import LLMClient

class SupportAgent:
    def __init__(self):
        self.llm = LLMClient()

    def process(self, query: str, user_id: int, session: Session) -> dict:
        user = session.get(User, user_id)
        if not user:
            return {"response_content": "Error: User account not found."}

        query_lower = query.lower()
        
        # If user asks to create or open a ticket
        if "ticket" in query_lower or "report a bug" in query_lower or "technical issue" in query_lower:
            # Extract title and description
            title = "Technical support request"
            description = query
            
            # Check if they specified a ticket title/description
            if len(query.split()) > 4:
                title = " ".join(query.split()[:5]) + "..."
            
            ticket = SupportTicket(
                customer_id=user_id,
                title=title,
                description=description,
                status=SupportTicketStatus.OPEN
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            
            # Audit log
            audit = AuditLog(
                event_type="TICKET_CREATION",
                user_id=user_id,
                action=f"Agent automatically opened support ticket #{ticket.id}: '{ticket.title}'"
            )
            session.add(audit)
            session.commit()
            
            return {
                "response_content": (
                    f"I have opened support ticket #{ticket.id} for you: **'{ticket.title}'**.\n"
                    f"Our engineering support team has been notified and will address your request shortly."
                ),
                "shared_context": {"last_ticket_id": ticket.id, "ticket_status": ticket.status.value}
            }

        # General LLM answer to user technical question
        system_instruction = (
            "You are the Customer Support Specialist Agent of a Governed Banking Platform.\n"
            "Help customers resolve general questions about using the dashboard, reset passwords, "
            "or explain how to open a support ticket."
        )
        response = self.llm.generate(system_instruction, query)
        
        return {
            "response_content": response,
            "shared_context": {"queries_handled": 1}
        }
