from fastapi import HTTPException, status
from apps.api.models import CustomerProfile

class PolicyException(Exception):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code

class PolicyEngine:
    @staticmethod
    def evaluate_loan_policy(profile: CustomerProfile, amount: float, term_months: int = 36) -> dict:
        """
        Enforces banking regulations and risk parameters:
        1. Minimum Credit Score: Credit score must be >= 600.
        2. Debt-to-Income (DTI) Limit: Monthly payment cannot exceed 35% of monthly income.
           Assumes an estimated interest rate of 8% (0.08) APR.
        """
        # 1. Credit Score Threshold
        if profile.credit_score < 600:
            return {
                "passed": False,
                "reason": f"Credit score {profile.credit_score} is below the regulatory minimum threshold of 600.",
                "policy_code": "CREDIT_THRESHOLD_VIOLATION"
            }

        # 2. Debt-to-Income Calculation
        # Simple interest payment estimation: (Principal + Interest) / Term
        annual_rate = 0.08
        total_payment = amount * (1 + (annual_rate * (term_months / 12)))
        estimated_monthly_payment = total_payment / term_months
        
        allowed_max_payment = profile.monthly_income * 0.35
        
        if estimated_monthly_payment > allowed_max_payment:
            return {
                "passed": False,
                "reason": (
                    f"Estimated monthly payment of ${estimated_monthly_payment:.2f} exceeds "
                    f"35% of monthly income (${allowed_max_payment:.2f})."
                ),
                "policy_code": "DTI_LIMIT_VIOLATION"
            }

        return {"passed": True, "reason": "All loan risk policies satisfied.", "policy_code": "POLICY_PASSED"}

    @staticmethod
    def evaluate_review_safety(reviewer_id: int, applicant_id: int) -> None:
        """
        Prevents conflict of interest (Self-Dealing Prevention Policy):
        Internal bank employees cannot review or approve their own loan applications.
        """
        if reviewer_id == applicant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Violation: Reviewers are prohibited from actioning their own applications."
            )
