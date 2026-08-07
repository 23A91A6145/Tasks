from sqlmodel import Session, select
from apps.api.database import get_active_session
from apps.api.models import User, CustomerProfile, LoanApplication, LoanApplicationStatus, ApprovalGate, ApprovalStatus, AuditLog
from agents.llm_client import LLMClient
from skills.calculators import LoanCalculator
from mcp.credit_bureau import CreditBureauMCP
from policies.policy_engine import PolicyEngine

class LoanAgent:
    def __init__(self):
        self.llm = LLMClient()

    def process(self, query: str, user_id: int, session: Session) -> dict:
        # Load user profile to check eligibility
        user = session.get(User, user_id)
        if not user:
            return {"response_content": "Error: User account not found."}
            
        profile = session.exec(select(CustomerProfile).where(CustomerProfile.user_id == user_id)).first()
        if not profile:
            return {
                "response_content": "To apply for or inquire about a loan, please set up a customer financial profile first."
            }

        # If user query is a loan application request, try to parse amount & purpose
        if "apply" in query.lower() or "borrow" in query.lower() or "application" in query.lower():
            # Extract amount from prompt (simple numeric parser, fallback to $5000 default)
            amount = 5000.0
            for word in query.replace("$", "").replace(",", "").split():
                try:
                    val = float(word)
                    if val > 100.0:  # Sensible minimum for loan amount
                        amount = val
                        break
                except ValueError:
                    continue
            
            # Check for purpose
            purpose = "Personal Loan"
            if "car" in query.lower() or "vehicle" in query.lower():
                purpose = "Auto Finance"
            elif "home" in query.lower() or "house" in query.lower() or "renovation" in query.lower():
                purpose = "Home Improvement"
            elif "medical" in query.lower() or "bill" in query.lower():
                purpose = "Medical Expenses"
            elif "study" in query.lower() or "college" in query.lower() or "education" in query.lower():
                purpose = "Education Funding"

            # --- Volume 4: MCP Tool Integration (External Debt Check) ---
            # Call simulated external bureau MCP endpoint
            bureau_debt = CreditBureauMCP.check_outstanding_debt(profile.ssn)
            rating_class = CreditBureauMCP.get_credit_rating_class(profile.credit_score)
            
            # Log the MCP tool call to the audit log
            mcp_audit = AuditLog(
                event_type="MCP_TOOL_CALL",
                user_id=user_id,
                action=(
                    f"External Credit Bureau Tool Call successful. SSN verified. "
                    f"Reported active debt: ${bureau_debt:,.2f}. Rating: '{rating_class}'."
                )
            )
            session.add(mcp_audit)
            session.commit()

            # --- Volume 4: Skill Integration (Monthly Payment Calculation) ---
            interest_rate = 8.0  # 8% APR standard
            term_months = 36
            monthly_payment = LoanCalculator.calculate_monthly_payment(amount, interest_rate, term_months)

            # --- Volume 3: Governance Policy Check ---
            policy_check = PolicyEngine.evaluate_loan_policy(profile, amount, term_months)
            
            # Setup Loan Application in DB
            loan = LoanApplication(
                customer_id=user_id,
                amount=amount,
                purpose=purpose,
                term_months=term_months,
                credit_score_snapshot=profile.credit_score,
                status=LoanApplicationStatus.PENDING_APPROVAL
            )
            
            if not policy_check["passed"]:
                # Auto Denied due to regulatory policy check failure
                loan.status = LoanApplicationStatus.DENIED
                loan.denied_reason = f"Policy violation ({policy_check['policy_code']}): {policy_check['reason']}"
                session.add(loan)
                session.commit()
                session.refresh(loan)
                
                # Log policy violation
                policy_audit = AuditLog(
                    event_type="POLICY_VIOLATION",
                    user_id=user_id,
                    action=f"Loan Application #{loan.id} failed policy checks: {policy_check['policy_code']}"
                )
                session.add(policy_audit)
                session.commit()

                resp_str = (
                    f"I processed your loan application #{loan.id} for ${loan.amount:,.2f} ({loan.purpose}).\n\n"
                    f"⚠️ **Application Denied** due to a policy check failure: {policy_check['reason']}\n"
                    f"Credit Bureau Assessment: {rating_class} (reported active debt: ${bureau_debt:,.2f})."
                )
                return {
                    "response_content": resp_str,
                    "shared_context": {"last_loan_id": loan.id, "loan_status": loan.status.value}
                }
            
            # Apply auto-approval logic
            is_auto_approved = False
            if loan.amount <= 1000.0 and profile.credit_score >= 750:
                is_auto_approved = True
                loan.status = LoanApplicationStatus.APPROVED
                loan.denied_reason = "System auto-approved: Low risk parameters met."

            session.add(loan)
            session.commit()
            session.refresh(loan)

            # Add ApprovalGate if review is needed
            if not is_auto_approved:
                gate = ApprovalGate(
                    entity_type="loan",
                    entity_id=loan.id,
                    requested_by_id=user_id,
                    status=ApprovalStatus.PENDING
                )
                session.add(gate)
                
            # Audit log submission
            audit_action = f"Agent drafted loan application #{loan.id} for ${loan.amount:.2f} (Purpose: {loan.purpose})."
            if is_auto_approved:
                audit_action += " Automatically approved by the system."
            
            audit = AuditLog(
                event_type="LOAN_SUBMISSION",
                user_id=user_id,
                action=audit_action
            )
            session.add(audit)
            session.commit()

            # Generate detailed agent response
            if is_auto_approved:
                resp_str = (
                    f"Congratulations! Your loan application #{loan.id} for ${loan.amount:,.2f} has been **automatically approved** "
                    f"based on your excellent credit score of {profile.credit_score}.\n\n"
                    f"📊 **Amortization Details:**\n"
                    f"  - Term: 36 Months\n"
                    f"  - Estimated Interest Rate: 8.0% APR\n"
                    f"  - Monthly Payment: **${monthly_payment:,.2f}**\n"
                    f"  - External Debt Index: ${bureau_debt:,.2f}\n"
                    f"  - Credit Bureau Rating: {rating_class}"
                )
            else:
                resp_str = (
                    f"Thank you. I have submitted your loan application #{loan.id} for ${loan.amount:,.2f} ({loan.purpose}) for review.\n\n"
                    f"📊 **Amortization Details:**\n"
                    f"  - Term: 36 Months\n"
                    f"  - Estimated Interest Rate: 8.0% APR\n"
                    f"  - Monthly Payment: **${monthly_payment:,.2f}**\n"
                    f"  - External Debt Index: ${bureau_debt:,.2f}\n"
                    f"  - Credit Bureau Rating: {rating_class}\n\n"
                    f"A Loan Officer will review the application shortly."
                )
            
            return {
                "response_content": resp_str,
                "shared_context": {"last_loan_id": loan.id, "loan_status": loan.status.value}
            }
        
        # If it's a general loan inquiry, generate an informative LLM response
        system_instruction = (
            "You are the Loan Specialist Agent of a Governed Banking Platform.\n"
            f"The current customer is {profile.full_name}. Their credit score is {profile.credit_score}.\n"
            "Help them understand loan criteria: personal loans up to $10,000 only require standard officer approval. "
            "Loans above $10,000 trigger a risk analyst review gate. Interest rates range from 4.5% to 12.0%."
        )
        response = self.llm.generate(system_instruction, query)
        
        return {
            "response_content": response,
            "shared_context": {"credit_score": profile.credit_score}
        }
