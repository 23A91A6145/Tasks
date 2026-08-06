import re
from typing import Dict, Any, Tuple
from app.utils import logger, MOCK_CUSTOMERS, MOCK_ORDERS
from app.config import MAX_AUTO_APPROVE_AMOUNT, MANAGER_LIMIT

# ---------------------------------------------------------------------------
# Microsoft Agent Framework integration point
#
# When the official `agent-framework` package is installed we register our
# sensitive tool with its real `@tool(approval_mode="always_require")`
# decorator, which attaches the Human-in-the-Loop approval requirement to the
# tool metadata exactly as the MAF runtime consumes it. When the package is
# absent (fully offline), a lightweight equivalent decorator is used so the
# project still runs with zero external dependencies.
# ---------------------------------------------------------------------------
try:
    from agent_framework import tool as _maf_tool  # real MAF package (optional)

    FRAMEWORK_AVAILABLE = True

    def ai_function(approval_mode: str = "never_require"):
        """
        Register a tool via the real Microsoft Agent Framework `@tool` decorator.
        `approval_mode="always_require"` marks the tool SAFETY-CRITICAL so the
        MAF runtime pauses the workflow for explicit human authorization.
        """
        def decorator(func):
            return _maf_tool(
                func,
                description=(func.__doc__ or "").strip(),
                approval_mode=approval_mode,
            )
        return decorator

except ImportError:  # pragma: no cover - offline fallback
    FRAMEWORK_AVAILABLE = False

    def ai_function(approval_mode: str = "never_require"):
        """
        Offline equivalent of the MAF `@tool(approval_mode=...)` decorator.
        Keeps the same callable semantics and metadata surface so the rest of
        the application is framework-agnostic.
        """
        def decorator(func):
            func.is_ai_function = True
            func.approval_mode = approval_mode
            func.description = (func.__doc__ or "").strip()
            return func
        return decorator


# ---------------------------------------------------------------------------
# Input validation layer (Phase 4.3 - Security)
# ---------------------------------------------------------------------------
def validate_refund_input(customer_id: str, order_id: str, amount: float) -> Tuple[bool, str]:
    """Performs structural input validation on a proposed refund request."""
    if not customer_id or not str(customer_id).strip():
        return False, "Customer ID is missing."
    if not re.match(r"^CUST-\d+$", str(customer_id).strip(), re.IGNORECASE):
        return False, f"Malformed Customer ID '{customer_id}'. Expected format CUST-####."
    if not order_id or not str(order_id).strip():
        return False, "Order ID is missing."
    if not re.match(r"^ORD-\d+$", str(order_id).strip(), re.IGNORECASE):
        return False, f"Malformed Order ID '{order_id}'. Expected format ORD-####."
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, f"Refund amount '{amount}' is not a valid number."
    if amount <= 0:
        return False, "Refund amount must be greater than zero."
    if amount > 1_000_000:
        return False, "Refund amount exceeds the $1,000,000 safety ceiling."
    return True, "Input fields valid."


# Policy Validation Logic
def validate_policy(customer_id: str, order_id: str, amount: float) -> Tuple[bool, str, str]:
    """
    Validates a refund request against corporate safety policy.
    Returns (is_valid, reason, role_required).
    """
    # 0. Structural sanity check (malformed input never reaches the policy engine)
    fields_ok, fields_reason = validate_refund_input(customer_id, order_id, amount)
    if not fields_ok:
        return False, fields_reason, "Reviewer"

    # 1. Customer Verification
    if customer_id not in MOCK_CUSTOMERS:
        return False, f"Customer ID '{customer_id}' not found in records.", "Reviewer"

    customer = MOCK_CUSTOMERS[customer_id]
    if customer["account_status"] == "Suspended":
        return False, "Customer account is suspended due to compliance issues.", "Manager"

    # 2. Order Verification
    if order_id not in MOCK_ORDERS:
        return False, f"Order ID '{order_id}' not found.", "Reviewer"

    order = MOCK_ORDERS[order_id]
    if order["customer_id"] != customer_id:
        return False, f"Order '{order_id}' does not belong to Customer '{customer_id}'.", "Reviewer"

    # 3. Amount Validation
    if amount <= 0:
        return False, "Refund amount must be greater than zero.", "Reviewer"
    if amount > order["amount"]:
        return False, f"Refund amount ${amount:.2f} exceeds original order amount ${order['amount']:.2f}.", "Reviewer"

    # 4. Role Requirement based on Risk and Amount
    role_required = "Reviewer"
    if amount >= MANAGER_LIMIT or customer["risk_level"] == "High":
        role_required = "Manager"

    return True, "Policies verified successfully.", role_required


def is_eligible_for_auto_approval(customer_id: str, amount: float) -> Tuple[bool, str]:
    """
    Returns whether a request may bypass the human gate.
    Only Low-risk, Active accounts below the micro-refund threshold qualify.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, {})
    if amount > MAX_AUTO_APPROVE_AMOUNT:
        return False, f"Amount ${amount:.2f} exceeds the auto-approval ceiling of ${MAX_AUTO_APPROVE_AMOUNT:.2f}."
    if customer.get("risk_level") != "Low":
        return False, f"Customer risk level '{customer.get('risk_level')}' requires human review."
    if customer.get("account_status") != "Active":
        return False, "Customer account is not in an Active state."
    return True, "Eligible for auto-approval under standard risk policies."


@ai_function(approval_mode="always_require")
def execute_payment_refund(customer_id: str, order_id: str, amount: float, reason: str) -> Dict[str, Any]:
    """
    Sensitive financial tool that executes the refund against the payment gateway.
    This operation carries high financial and compliance risk and requires
    explicit human approval before it can ever be invoked by the agent.
    """
    logger.info(f"💰 Executing refund to gateway: Order={order_id}, Amount=${amount:.2f}")

    # Safety invariant: never execute without a validated, approved context
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Refund amount is invalid; refusing to contact gateway.")

    # Simulate payment processor transaction
    transaction_id = f"TXN-{order_id.split('-')[-1]}-{str(abs(int(amount * 100)))[:4]}-REFUND"

    return {
        "status": "success",
        "message": f"Refund of ${amount:.2f} successfully credited to customer bank card.",
        "transaction_id": transaction_id,
        "details": {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "reason": reason
        }
    }
