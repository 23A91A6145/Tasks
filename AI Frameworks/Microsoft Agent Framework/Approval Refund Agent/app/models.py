import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

CUSTOMER_ID_RE = re.compile(r"^CUST-\d+$", re.IGNORECASE)
ORDER_ID_RE = re.compile(r"^ORD-\d+$", re.IGNORECASE)

# Customer and order details
class CustomerInfo(BaseModel):
    customer_id: str
    name: str
    email: str
    risk_level: str  # Low, Medium, High
    purchase_date: str
    product_name: str
    account_status: str  # Active, Suspended, Flagged

class RefundRequest(BaseModel):
    customer_id: str
    order_id: str
    amount: float
    reason: str = "No reason specified"

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not CUSTOMER_ID_RE.match(v):
            raise ValueError(f"Invalid Customer ID format: '{v}' (expected CUST-####)")
        return v

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not ORDER_ID_RE.match(v):
            raise ValueError(f"Invalid Order ID format: '{v}' (expected ORD-####)")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Refund amount must be greater than zero.")
        if v > 1_000_000:
            raise ValueError("Refund amount exceeds the maximum allowed limit ($1,000,000).")
        return round(v, 2)

# Approval Request representing HITL task
class ApprovalRequest(BaseModel):
    id: str
    customer_id: str
    order_id: str
    amount: float
    reason: str
    risk_level: str
    product: str
    purchase_date: str
    status: str = "Pending"  # Pending, Approved, Rejected, Hold, Escalated, Request More Info
    reviewer: Optional[str] = None
    role_required: str = "Reviewer"  # Reviewer, Manager
    notes: Optional[str] = ""
    created_at: str
    handled_at: Optional[str] = None
    timeline: List[Dict[str, str]] = []  # List of {"step": str, "timestamp": str}

VALID_ACTIONS = ("Approve", "Reject", "Hold", "Escalate", "Request More Info")
VALID_ROLES = ("Reviewer", "Manager")

class DecisionInput(BaseModel):
    action: Literal["Approve", "Reject", "Hold", "Escalate", "Request More Info"]
    notes: Optional[str] = Field(default="", max_length=2000)
    reviewer_name: str = Field(min_length=1, max_length=120)
    reviewer_role: Literal["Reviewer", "Manager"] = "Reviewer"

    @field_validator("reviewer_name")
    @classmethod
    def validate_reviewer_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Reviewer name cannot be empty.")
        return v

class AuditLogEntry(BaseModel):
    timestamp: str
    request_id: str
    customer_id: str
    order_id: str
    amount: float
    decision: str
    reason: str
    reviewer: str
    reviewer_role: str
    notes: Optional[str] = ""
    ip_address: str
    session_id: str

class RefundDashboardStats(BaseModel):
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    escalated_count: int = 0
    hold_count: int = 0
    expired_count: int = 0
    avg_processing_time_seconds: float = 0.0
    today_requests_count: int = 0
    today_refund_value: float = 0.0
