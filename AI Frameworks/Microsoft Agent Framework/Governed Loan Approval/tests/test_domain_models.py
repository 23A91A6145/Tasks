import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from apps.api.models import (
    User, UserRole, CustomerProfile, LoanApplication, 
    LoanApplicationStatus, AuditLog, ApprovalGate, ApprovalStatus,
    decrypt_data
)

def test_user_registration_and_pii_encryption(client: TestClient, session: Session):
    # Register customer
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Alice Smith",
                "ssn": "123-456-7890",
                "monthly_income": 6500.0,
                "credit_score": 780,
                "employment_status": "Employed"
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["role"] == "customer"

    # Verify database entry & PII encryption
    user = session.exec(select(User).where(User.username == "alice")).first()
    assert user is not None
    assert user.customer_profile is not None
    assert user.customer_profile.full_name == "Alice Smith"
    
    # Assert ssn is encrypted in the raw column and decrypted on property access
    assert user.customer_profile.encrypted_ssn != "123-456-7890"
    assert user.customer_profile.ssn == "123-456-7890"

    # Audit log check
    audit = session.exec(select(AuditLog).where(AuditLog.event_type == "AUTHENTICATION")).first()
    assert audit is not None
    assert "alice" in audit.action

def test_loan_auto_approval_gate(client: TestClient, session: Session):
    # 1. Register a customer with high credit score
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Bob Jones",
                "ssn": "000-11-2222",
                "monthly_income": 5000.0,
                "credit_score": 760,
                "employment_status": "Employed"
            }
        }
    )

    # Login Bob
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "bob", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Apply for auto-approvable loan ($500 with credit score 760)
    loan_resp = client.post(
        "/api/v1/api/v1/loans" if False else "/api/v1/loans",
        json={"amount": 500.0, "purpose": "Emergency medical bill", "term_months": 12},
        headers=headers
    )
    assert loan_resp.status_code == 201
    loan_data = loan_resp.json()
    assert loan_data["status"] == "approved"  # Auto-approved!

    # Apply for non-auto-approvable loan ($5000)
    loan_resp_large = client.post(
        "/api/v1/loans",
        json={"amount": 5000.0, "purpose": "Car repair", "term_months": 24},
        headers=headers
    )
    assert loan_resp_large.status_code == 201
    loan_data_large = loan_resp_large.json()
    assert loan_data_large["status"] == "pending_approval"  # Needs review!

    # Check if ApprovalGate created
    gate = session.exec(
        select(ApprovalGate)
        .where(ApprovalGate.entity_id == loan_data_large["id"])
    ).first()
    assert gate is not None
    assert gate.status == "pending"

def test_loan_officer_vs_risk_analyst_policies(client: TestClient, session: Session):
    # 1. Setup users (customer, loan officer, risk analyst)
    # Register customer
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Charlie Miller",
                "ssn": "111-22-3333",
                "monthly_income": 12000.0,
                "credit_score": 720,
                "employment_status": "Employed"
            }
        }
    )
    # Register officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "officer1", "email": "officer@bank.com", "password": "password123", "role": "loan_officer"}
    )
    # Register risk analyst
    client.post(
        "/api/v1/auth/register",
        json={"username": "risk1", "email": "risk@bank.com", "password": "password123", "role": "risk_analyst"}
    )

    # Customer logins and applies for a large loan ($15,000)
    login_cust = client.post("/api/v1/auth/login", data={"username": "charlie", "password": "password123"})
    cust_token = login_cust.json()["access_token"]
    
    loan_resp = client.post(
        "/api/v1/loans",
        json={"amount": 15000.0, "purpose": "Business startup"},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    loan_id = loan_resp.json()["id"]

    # Loan officer attempts to approve loan > $10,000
    login_off = client.post("/api/v1/auth/login", data={"username": "officer1", "password": "password123"})
    off_token = login_off.json()["access_token"]
    
    action_resp = client.post(
        f"/api/v1/loans/{loan_id}/action",
        json={"action": "approved", "comments": "Looks fine to me"},
        headers={"Authorization": f"Bearer {off_token}"}
    )
    # Assert permission denied due to risk policy gate
    assert action_resp.status_code == 403
    assert "require Risk Analyst or Administrator approval" in action_resp.json()["detail"]

    # Risk Analyst approves the loan
    login_risk = client.post("/api/v1/auth/login", data={"username": "risk1", "password": "password123"})
    risk_token = login_risk.json()["access_token"]

    action_resp_ok = client.post(
        f"/api/v1/loans/{loan_id}/action",
        json={"action": "approved", "comments": "Approved high-limit loan based on monthly income"},
        headers={"Authorization": f"Bearer {risk_token}"}
    )
    assert action_resp_ok.status_code == 200
    assert action_resp_ok.json()["status"] == "approved"

    # Check AuditLog policy violations
    violations = session.exec(select(AuditLog).where(AuditLog.event_type == "POLICY_VIOLATION")).all()
    assert len(violations) > 0
    assert "officer1" in violations[0].action

def test_support_tickets_flow(client: TestClient, session: Session):
    # Register customer
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "diana",
            "email": "diana@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Diana Prince",
                "ssn": "999-99-9999",
                "monthly_income": 4000.0,
                "credit_score": 680,
                "employment_status": "Self-Employed"
            }
        }
    )
    # Register officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "officer2", "email": "officer2@bank.com", "password": "password123", "role": "loan_officer"}
    )

    # Diana submits ticket
    login_cust = client.post("/api/v1/auth/login", data={"username": "diana", "password": "password123"})
    cust_token = login_cust.json()["access_token"]
    
    ticket_resp = client.post(
        "/api/v1/tickets",
        json={"title": "Error in registration details", "description": "Need to update my income status"},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert ticket_resp.status_code == 201
    ticket_id = ticket_resp.json()["id"]
    assert ticket_resp.json()["status"] == "open"

    # Officer assigns and processes ticket
    login_off = client.post("/api/v1/auth/login", data={"username": "officer2", "password": "password123"})
    off_token = login_off.json()["access_token"]

    action_resp = client.post(
        f"/api/v1/tickets/{ticket_id}/action",
        json={"status": "resolved"},
        headers={"Authorization": f"Bearer {off_token}"}
    )
    assert action_resp.status_code == 200
    assert action_resp.json()["status"] == "resolved"
    # Auto-assigned to officer2
    user_officer = session.exec(select(User).where(User.username == "officer2")).first()
    assert action_resp.json()["assigned_officer_id"] == user_officer.id

def test_audit_logs_auditor_compliance(client: TestClient, session: Session):
    # Register compliance officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "compliance1", "email": "comp@bank.com", "password": "password123", "role": "compliance_officer"}
    )

    # Login compliance officer
    login_comp = client.post("/api/v1/auth/login", data={"username": "compliance1", "password": "password123"})
    comp_token = login_comp.json()["access_token"]

    # View logs
    resp = client.get("/api/v1/audit", headers={"Authorization": f"Bearer {comp_token}"})
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) > 0
    
    # Assert audit inspection log itself is recorded in database (Auditing the Auditors)
    inspection_log = session.exec(
        select(AuditLog).where(AuditLog.event_type == "AUDIT_INSPECTION")
    ).first()
    assert inspection_log is not None
    assert "compliance1" in inspection_log.action


def test_agent_intent_classification_and_pii_redaction(client: TestClient, session: Session):
    # 1. Register customer
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "agent_user",
            "email": "agent@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Agent User",
                "ssn": "111-22-3333",
                "monthly_income": 8000.0,
                "credit_score": 770,
                "employment_status": "Employed"
            }
        }
    )

    # Login
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "agent_user", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Chat with agent using query containing PII (SSN)
    chat_resp = client.post(
        "/api/v1/agent/chat",
        json={
            "session_id": "test_session_1",
            "query": "Hello, I want to apply for a loan. My SSN is 999-88-7777."
        },
        headers=headers
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert data["session_id"] == "test_session_1"
    assert data["classified_intent"] == "loan_application"
    assert data["active_agent"] == "loan_agent"
    assert data["pii_redacted"] is True
    
    # Assert response contains structured output
    assert "application" in data["reply"].lower() or "loan" in data["reply"].lower()

    # Check database for PII redaction log
    pii_log = session.exec(
        select(AuditLog).where(AuditLog.event_type == "PII_REDACTION")
    ).first()
    assert pii_log is not None
    assert pii_log.user_id is not None
    assert "999-88-7777" in pii_log.input_prompt
    assert "[REDACTED_SSN]" in pii_log.redacted_prompt

    # Check database for handoff log
    handoff_log = session.exec(
        select(AuditLog).where(AuditLog.event_type == "AGENT_HANDOFF")
    ).first()
    assert handoff_log is not None
    assert "loan_agent" in handoff_log.action


def test_agent_session_checkpointing_conversation_turns(client: TestClient, session: Session):
    # 1. Register customer
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "checkpoint_user",
            "email": "checkpoint@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Checkpoint User",
                "ssn": "555-55-5555",
                "monthly_income": 9500.0,
                "credit_score": 790,
                "employment_status": "Employed"
            }
        }
    )

    # Login
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "checkpoint_user", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Turn 1: Draft a loan
    chat_resp_1 = client.post(
        "/api/v1/agent/chat",
        json={
            "session_id": "session_turn_check",
            "query": "I would like to apply for a loan of $12000 for a home renovation."
        },
        headers=headers
    )
    assert chat_resp_1.status_code == 200
    data_1 = chat_resp_1.json()
    assert data_1["classified_intent"] == "loan_application"
    assert "last_loan_id" in data_1["shared_context"]
    loan_id = data_1["shared_context"]["last_loan_id"]

    # Turn 2: Query ticket support (triggers support agent, but preserves context of drafted loan)
    chat_resp_2 = client.post(
        "/api/v1/agent/chat",
        json={
            "session_id": "session_turn_check",
            "query": "Also, can I open a support ticket to check on technical app latency issues?"
        },
        headers=headers
    )
    assert chat_resp_2.status_code == 200
    data_2 = chat_resp_2.json()
    assert data_2["classified_intent"] == "general_support"
    assert data_2["active_agent"] == "support_agent"
    
    # Check that loan context from Turn 1 was restored and persists in the updated context!
    assert "last_loan_id" in data_2["shared_context"]
    assert data_2["shared_context"]["last_loan_id"] == loan_id
    assert "last_ticket_id" in data_2["shared_context"]


def test_governance_policy_evaluations():
    from policies.policy_engine import PolicyEngine
    from apps.api.models import CustomerProfile
    
    # 1. Test low credit score policy violation
    bad_profile = CustomerProfile(user_id=1, full_name="Bad credit", monthly_income=5000.0, credit_score=550, employment_status="Employed", encrypted_ssn="abc")
    result = PolicyEngine.evaluate_loan_policy(bad_profile, amount=2000.0)
    assert result["passed"] is False
    assert result["policy_code"] == "CREDIT_THRESHOLD_VIOLATION"

    # 2. Test Debt-to-Income (DTI) policy violation
    low_income_profile = CustomerProfile(user_id=2, full_name="Low income", monthly_income=1000.0, credit_score=720, employment_status="Employed", encrypted_ssn="abc")
    result_dti = PolicyEngine.evaluate_loan_policy(low_income_profile, amount=30000.0, term_months=12)
    assert result_dti["passed"] is False
    assert result_dti["policy_code"] == "DTI_LIMIT_VIOLATION"

    # 3. Test policy pass
    good_profile = CustomerProfile(user_id=3, full_name="Good risk", monthly_income=6000.0, credit_score=750, employment_status="Employed", encrypted_ssn="abc")
    result_ok = PolicyEngine.evaluate_loan_policy(good_profile, amount=5000.0)
    assert result_ok["passed"] is True
    assert result_ok["policy_code"] == "POLICY_PASSED"


def test_conflict_of_interest_self_dealing_denied(client: TestClient, session: Session):
    # Register a loan officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "officer_self", "email": "self@bank.com", "password": "password123", "role": "loan_officer"}
    )
    # Log in
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "officer_self", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Simulate an approval gate created by the officer themselves
    from apps.api.models import ApprovalGate, ApprovalStatus
    gate = ApprovalGate(
        entity_type="loan",
        entity_id=99,
        requested_by_id=1,  # Assuming user ID 1 is the officer_self
        status=ApprovalStatus.PENDING
    )
    session.add(gate)
    session.commit()
    session.refresh(gate)

    # Re-fetch user ID from DB to make sure we align reviewer and applicant IDs
    from apps.api.models import User
    officer_user = session.exec(select(User).where(User.username == "officer_self")).first()
    gate.requested_by_id = officer_user.id
    session.add(gate)
    session.commit()

    # Officer attempts to approve their own request
    resp = client.post(
        f"/api/v1/approvals/{gate.id}/action",
        json={"action": "approved", "comments": "Self approval"},
        headers=headers
    )
    # Assert self-dealing blocked with 403 Forbidden
    assert resp.status_code == 403
    assert "prohibited from actioning their own applications" in resp.json()["detail"]


def test_approval_gate_hitl_actioning(client: TestClient, session: Session):
    # 1. Register customer & submit loan
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "customer_hitl",
            "email": "hitl@example.com",
            "password": "password123",
            "role": "customer",
            "profile": {
                "full_name": "Customer HITL",
                "ssn": "111-11-1111",
                "monthly_income": 8000.0,
                "credit_score": 700,
                "employment_status": "Employed"
            }
        }
    )
    login_cust = client.post("/api/v1/auth/login", data={"username": "customer_hitl", "password": "password123"})
    cust_token = login_cust.json()["access_token"]

    loan_resp = client.post(
        "/api/v1/loans",
        json={"amount": 5000.0, "purpose": "Home Improvement"},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    loan_id = loan_resp.json()["id"]

    # 2. Register loan officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "officer_hitl", "email": "hitl@bank.com", "password": "password123", "role": "loan_officer"}
    )
    login_off = client.post("/api/v1/auth/login", data={"username": "officer_hitl", "password": "password123"})
    off_token = login_off.json()["access_token"]
    off_headers = {"Authorization": f"Bearer {off_token}"}

    # 3. List pending approvals
    list_resp = client.get("/api/v1/approvals", headers=off_headers)
    assert list_resp.status_code == 200
    gates = list_resp.json()
    assert len(gates) > 0
    gate_id = [g for g in gates if g["entity_id"] == loan_id][0]["id"]

    # 4. Action the gate
    action_resp = client.post(
        f"/api/v1/approvals/{gate_id}/action",
        json={"action": "approved", "comments": "Approve after credit analysis"},
        headers=off_headers
    )
    assert action_resp.status_code == 200
    assert action_resp.json()["status"] == "approved"

    # 5. Verify the loan application has updated to approved in database
    loan_in_db = session.get(LoanApplication, loan_id)
    assert loan_in_db.status == LoanApplicationStatus.APPROVED
    assert loan_in_db.approved_by_id is not None


def test_automated_request_auditing_middleware(client: TestClient, session: Session):
    # Register compliance officer
    client.post(
        "/api/v1/auth/register",
        json={"username": "compliance_audit", "email": "comp_aud@bank.com", "password": "password123", "role": "compliance_officer"}
    )
    login_comp = client.post("/api/v1/auth/login", data={"username": "compliance_audit", "password": "password123"})
    token = login_comp.json()["access_token"]

    # Trigger a request on loans endpoint
    client.get("/api/v1/loans", headers={"Authorization": f"Bearer {token}"})

    # Assert that audit log middleware has committed an API_REQUEST log
    api_logs = session.exec(
        select(AuditLog).where(AuditLog.event_type == "API_REQUEST")
    ).all()
    assert len(api_logs) > 0
    
    # Check that it recorded the method and path
    matching_log = [log for log in api_logs if "GET /api/v1/loans" in log.action]
    assert len(matching_log) > 0


