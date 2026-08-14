"""Customer support tools with schema validation and execution tracking."""

from __future__ import annotations

from typing import Any
from pydantic_ai import RunContext
from app.dependencies import SupportDependencies, CustomerRecord, OrderRecord


async def lookup_order(
    ctx: RunContext[SupportDependencies],
    order_id: str,
) -> dict[str, Any]:
    """Look up order information by order ID.

    Args:
        ctx: Run context containing support dependencies.
        order_id: The unique identifier of the order (e.g. A100, B200, E500).

    Returns:
        A dictionary containing order status, items, tracking info, or an error message.
    """
    clean_id = order_id.strip().upper()
    ctx.deps.tool_call_history.append({"tool": "lookup_order", "args": {"order_id": clean_id}})

    order = ctx.deps.orders.get(clean_id)
    if not order:
        return {
            "found": False,
            "order_id": clean_id,
            "message": f"Order {clean_id} was not found in our system. Please verify your order ID.",
        }

    return {
        "found": True,
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "item_name": order.item_name,
        "amount": order.amount,
        "tracking_number": order.tracking_number,
        "days_since_delivery": order.days_since_delivery,
    }


async def lookup_customer(
    ctx: RunContext[SupportDependencies],
    customer_id: str,
) -> dict[str, Any]:
    """Look up customer account details by customer ID.

    Args:
        ctx: Run context containing support dependencies.
        customer_id: The unique identifier of the customer (e.g. CUST-101).

    Returns:
        A dictionary containing customer tier, status, and name, or an error message.
    """
    clean_id = customer_id.strip().upper()
    ctx.deps.tool_call_history.append({"tool": "lookup_customer", "args": {"customer_id": clean_id}})

    customer = ctx.deps.customers.get(clean_id)
    if not customer:
        return {
            "found": False,
            "customer_id": clean_id,
            "message": f"Customer {clean_id} does not exist in our records.",
        }

    return {
        "found": True,
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "tier": customer.tier,
        "status": customer.status,
    }


async def check_refund_policy(
    ctx: RunContext[SupportDependencies],
    order_id: str,
) -> dict[str, Any]:
    """Check whether an order is eligible for a return/refund based on store policy.

    Args:
        ctx: Run context containing support dependencies.
        order_id: The unique order identifier.

    Returns:
        A dictionary indicating refund eligibility and explanation.
    """
    clean_id = order_id.strip().upper()
    ctx.deps.tool_call_history.append({"tool": "check_refund_policy", "args": {"order_id": clean_id}})

    order = ctx.deps.orders.get(clean_id)
    if not order:
        return {
            "eligible": False,
            "reason": f"Order {clean_id} does not exist.",
        }

    if order.status == "Cancelled":
        return {
            "eligible": False,
            "reason": "This order was already cancelled. Any pre-authorized charges have been released.",
        }

    if order.days_since_delivery > ctx.deps.refund_window_days:
        return {
            "eligible": False,
            "reason": f"Order {clean_id} was delivered {order.days_since_delivery} days ago, exceeding the {ctx.deps.refund_window_days}-day return window.",
        }

    return {
        "eligible": True,
        "reason": f"Order {clean_id} is within the {ctx.deps.refund_window_days}-day return window and eligible for a full refund.",
        "amount": order.amount,
    }


async def get_faq_answer(
    ctx: RunContext[SupportDependencies],
    topic: str,
) -> dict[str, Any]:
    """Retrieve standard support guidelines and FAQ information.

    Args:
        ctx: Run context containing support dependencies.
        topic: Topic query (e.g. shipping, warranty, returns, payment, discount).

    Returns:
        A dictionary with relevant policy text.
    """
    clean_topic = topic.strip().lower()
    ctx.deps.tool_call_history.append({"tool": "get_faq_answer", "args": {"topic": clean_topic}})

    faqs = {
        "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days. Tracking numbers are emailed upon dispatch.",
        "returns": "Items may be returned within 30 days of delivery in original condition for a full refund.",
        "warranty": "All hardware items include a 1-year limited manufacturer warranty covering defects.",
        "hours": "Customer support is available Monday through Friday, 9am to 6pm EST.",
        "payment": "We accept major credit cards (Visa, MasterCard, Amex), PayPal, and Apple Pay.",
        "international": "International shipping is available to over 50 countries and takes 7-14 business days.",
        "discount": "VIP tier members receive a 10% discount on all purchases automatically applied at checkout.",
    }

    for key, text in faqs.items():
        if key in clean_topic:
            return {"found": True, "topic": key, "answer": text}

    return {
        "found": False,
        "topic": clean_topic,
        "answer": "No specific FAQ found. For general assistance, our return window is 30 days and shipping is 3-5 business days.",
    }
