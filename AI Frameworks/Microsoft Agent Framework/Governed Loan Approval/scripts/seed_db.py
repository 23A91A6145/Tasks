import sys
from pathlib import Path

# Add project root to python path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine
from apps.api.config import settings
from apps.api.database import engine
from apps.api.auth_utils import get_password_hash
from apps.api.models import (
    User, UserRole, CustomerProfile, LoanApplication, 
    LoanApplicationStatus, SupportTicket, SupportTicketStatus, 
    AuditLog, ApprovalGate, ApprovalStatus
)

def seed():
    print("Initializing database tables...")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        print("Creating users...")
        
        # Admins & Employees
        admin = User(
            username="admin",
            email="admin@bank.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        officer = User(
            username="officer_bob",
            email="bob@bank.com",
            hashed_password=get_password_hash("officer123"),
            role=UserRole.LOAN_OFFICER
        )
        analyst = User(
            username="analyst_clara",
            email="clara@bank.com",
            hashed_password=get_password_hash("analyst123"),
            role=UserRole.RISK_ANALYST
        )
        compliance = User(
            username="compliance_dan",
            email="dan@bank.com",
            hashed_password=get_password_hash("compliance123"),
            role=UserRole.COMPLIANCE_OFFICER
        )
        
        # Customers
        cust_john = User(
            username="john_doe",
            email="john@example.com",
            hashed_password=get_password_hash("john123"),
            role=UserRole.CUSTOMER
        )
        cust_mary = User(
            username="mary_smith",
            email="mary@example.com",
            hashed_password=get_password_hash("mary123"),
            role=UserRole.CUSTOMER
        )

        session.add_all([admin, officer, analyst, compliance, cust_john, cust_mary])
        session.commit()
        session.refresh(cust_john)
        session.refresh(cust_mary)

        print("Creating customer profiles (with encrypted PII)...")
        profile_john = CustomerProfile(
            user_id=cust_john.id,
            full_name="John Doe",
            monthly_income=7200.00,
            credit_score=765,
            employment_status="Employed"
        )
        profile_john.ssn = "123-45-6789"  # Triggers property encryption

        profile_mary = CustomerProfile(
            user_id=cust_mary.id,
            full_name="Mary Smith",
            monthly_income=4500.00,
            credit_score=610,
            employment_status="Self-Employed"
        )
        profile_mary.ssn = "987-65-4321"  # Triggers property encryption

        session.add_all([profile_john, profile_mary])
        session.commit()

        print("Creating sample loan applications...")
        # John applies for standard auto-approvable loan (system auto-approved)
        loan_john_auto = LoanApplication(
            customer_id=cust_john.id,
            amount=800.00,
            purpose= "Computer replacement",
            term_months=12,
            credit_score_snapshot=765,
            status=LoanApplicationStatus.APPROVED,
            denied_reason="System auto-approved: Low risk and high credit score."
        )
        
        # John applies for larger loan (pending approval)
        loan_john_large = LoanApplication(
            customer_id=cust_john.id,
            amount=15000.00,
            purpose="Home Improvement renovation",
            term_months=48,
            credit_score_snapshot=765,
            status=LoanApplicationStatus.PENDING_APPROVAL
        )

        # Mary applies for a loan (pending approval)
        loan_mary = LoanApplication(
            customer_id=cust_mary.id,
            amount=5000.00,
            purpose="Debt consolidation",
            term_months=36,
            credit_score_snapshot=610,
            status=LoanApplicationStatus.PENDING_APPROVAL
        )

        session.add_all([loan_john_auto, loan_john_large, loan_mary])
        session.commit()
        session.refresh(loan_john_large)
        session.refresh(loan_mary)

        print("Creating approval gates for pending loans...")
        gate_john = ApprovalGate(
            entity_type="loan",
            entity_id=loan_john_large.id,
            requested_by_id=cust_john.id,
            status=ApprovalStatus.PENDING
        )
        gate_mary = ApprovalGate(
            entity_type="loan",
            entity_id=loan_mary.id,
            requested_by_id=cust_mary.id,
            status=ApprovalStatus.PENDING
        )
        session.add_all([gate_john, gate_mary])

        print("Creating support tickets...")
        ticket_1 = SupportTicket(
            customer_id=cust_mary.id,
            title="Unable to submit application",
            description="I get an error saying 'Ineligible credit threshold' but I want to apply anyway.",
            status=SupportTicketStatus.OPEN
        )
        ticket_2 = SupportTicket(
            customer_id=cust_john.id,
            title="Interest rate inquiry",
            description="What are the latest interest rates for a 36-month term?",
            status=SupportTicketStatus.RESOLVED,
            assigned_officer_id=officer.id,
            updated_at=datetime.utcnow() - timedelta(hours=2)
        )
        session.add_all([ticket_1, ticket_2])

        print("Creating audit logs...")
        logs = [
            AuditLog(
                event_type="AUTHENTICATION",
                user_id=cust_john.id,
                action="Registered new user 'john_doe' with role 'customer'"
            ),
            AuditLog(
                event_type="LOAN_SUBMISSION",
                user_id=cust_john.id,
                action=f"Submitted loan application #{loan_john_auto.id} for $800.00. System automatically approved application."
            ),
            AuditLog(
                event_type="LOAN_SUBMISSION",
                user_id=cust_john.id,
                action=f"Submitted loan application #{loan_john_large.id} for $15,000.00."
            ),
            AuditLog(
                event_type="TICKET_CREATION",
                user_id=cust_mary.id,
                action="Opened support ticket: 'Unable to submit application'"
            ),
            AuditLog(
                event_type="TICKET_DECISION",
                user_id=officer.id,
                action=f"Updated ticket #{ticket_2.id} status to 'resolved' and assigned to user id '{officer.id}'."
            )
        ]
        session.add_all(logs)
        session.commit()
        
        print("\nDatabase seeded successfully!")
        print("---------------------------------")
        print("Sample Credentials:")
        print("  - Customer: username='john_doe', password='john123'")
        print("  - Customer: username='mary_smith', password='mary123'")
        print("  - Loan Officer: username='officer_bob', password='officer123'")
        print("  - Risk Analyst: username='analyst_clara', password='analyst123'")
        print("  - Compliance Officer: username='compliance_dan', password='compliance123'")
        print("  - Administrator: username='admin', password='admin123'")
        print("---------------------------------")

if __name__ == "__main__":
    seed()
