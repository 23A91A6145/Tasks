"""Agent runtime dependencies and in-memory database store for deterministic evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from pydantic import BaseModel


class CustomerRecord(BaseModel):
    """Customer database record."""
    customer_id: str
    name: str
    email: str
    tier: str  # "Standard", "Premium", "VIP"
    status: str  # "Active", "Suspended"


class OrderRecord(BaseModel):
    """Order database record."""
    order_id: str
    customer_id: str
    status: str  # "Processing", "Shipped", "Delivered", "Cancelled", "Refunded"
    item_name: str
    amount: float
    tracking_number: str | None = None
    eligible_for_refund: bool = True
    days_since_delivery: int = 5


@dataclass
class SupportDependencies:
    """Dependency injection container for the customer support agent."""

    customers: dict[str, CustomerRecord] = field(default_factory=lambda: {
        "CUST-101": CustomerRecord(
            customer_id="CUST-101",
            name="Alice Johnson",
            email="alice@example.com",
            tier="VIP",
            status="Active",
        ),
        "CUST-102": CustomerRecord(
            customer_id="CUST-102",
            name="Bob Smith",
            email="bob@example.com",
            tier="Standard",
            status="Active",
        ),
        "CUST-103": CustomerRecord(
            customer_id="CUST-103",
            name="Charlie Brown",
            email="charlie@example.com",
            tier="Standard",
            status="Suspended",
        ),
        "CUST-104": CustomerRecord(
            customer_id="CUST-104",
            name="Diana Prince",
            email="diana@example.com",
            tier="VIP",
            status="Active",
        ),
        "CUST-105": CustomerRecord(
            customer_id="CUST-105",
            name="Evan Wright",
            email="evan@example.com",
            tier="Standard",
            status="Active",
        ),
    })

    orders: dict[str, OrderRecord] = field(default_factory=lambda: {
        "A100": OrderRecord(
            order_id="A100",
            customer_id="CUST-101",
            status="Shipped",
            item_name="Noise-Cancelling Headphones",
            amount=199.99,
            tracking_number="TRK-98765",
            eligible_for_refund=True,
            days_since_delivery=0,
        ),
        "B200": OrderRecord(
            order_id="B200",
            customer_id="CUST-102",
            status="Delivered",
            item_name="Mechanical Keyboard",
            amount=129.50,
            tracking_number="TRK-11223",
            eligible_for_refund=True,
            days_since_delivery=12,
        ),
        "C300": OrderRecord(
            order_id="C300",
            customer_id="CUST-102",
            status="Delivered",
            item_name="Smart Watch",
            amount=299.00,
            tracking_number="TRK-44556",
            eligible_for_refund=False,
            days_since_delivery=45,  # Exceeds 30-day return policy
        ),
        "D400": OrderRecord(
            order_id="D400",
            customer_id="CUST-103",
            status="Cancelled",
            item_name="USB-C Hub",
            amount=45.00,
            tracking_number=None,
            eligible_for_refund=False,
            days_since_delivery=0,
        ),
        "E500": OrderRecord(
            order_id="E500",
            customer_id="CUST-104",
            status="Processing",
            item_name="Ultra-Wide Gaming Monitor",
            amount=499.00,
            tracking_number=None,
            eligible_for_refund=True,
            days_since_delivery=0,
        ),
        "F600": OrderRecord(
            order_id="F600",
            customer_id="CUST-105",
            status="Delivered",
            item_name="Wireless Earbuds",
            amount=59.00,
            tracking_number="TRK-77889",
            eligible_for_refund=True,
            days_since_delivery=28,  # Near boundary: 28 days <= 30 days
        ),
        "G700": OrderRecord(
            order_id="G700",
            customer_id="CUST-105",
            status="Delivered",
            item_name="Ergonomic Desk Chair",
            amount=349.00,
            tracking_number="TRK-33445",
            eligible_for_refund=False,
            days_since_delivery=32,  # Near boundary: 32 days > 30 days
        ),
        "H800": OrderRecord(
            order_id="H800",
            customer_id="CUST-104",
            status="Delivered",
            item_name="Aluminum Laptop Stand",
            amount=39.99,
            tracking_number="TRK-99001",
            eligible_for_refund=True,
            days_since_delivery=5,
        ),
    })

    refund_window_days: int = 30
    tool_call_history: list[dict[str, Any]] = field(default_factory=list)


def create_default_dependencies() -> SupportDependencies:
    """Create a fresh instance of support dependencies."""
    return SupportDependencies()
