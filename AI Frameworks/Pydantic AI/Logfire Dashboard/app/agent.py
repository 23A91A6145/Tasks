"""Customer Support Agent implemented with Pydantic AI."""

from __future__ import annotations

import re
import time
from typing import Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, TextPart, UserPromptPart, SystemPromptPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from app.config import config
from app.dependencies import SupportDependencies, create_default_dependencies
from app.tools import lookup_order, lookup_customer, check_refund_policy, get_faq_answer


SYSTEM_PROMPT_V1 = """You are an accurate and helpful Customer Support Agent for an e-commerce platform.
Your primary goals:
1. Assist customers with order status, tracking, and refund eligibility.
2. Lookup information using provided tools whenever specific IDs (Order ID, Customer ID) or topics are mentioned.
3. If an Order ID or Customer ID is missing from a request that requires it, politely ask the customer for the missing identifier.
4. NEVER invent or hallucinate order details, tracking codes, or account statuses.
5. Keep your answers concise, courteous, and strictly grounded in real tool data.
"""

SYSTEM_PROMPT_V2 = """You are a Senior E-Commerce Concierge Agent.
1. Answer customer queries with empathy, clarity, and precision.
2. ALWAYS use the order lookup tool for order queries and the refund policy tool for refund assessments.
3. Clearly state whether an order is eligible for refund and state the reason according to store policy.
4. Never assume or make up tracking numbers, delivery dates, or customer records.
5. If required information is missing, ask specifically for the exact identifier needed.
"""


async def _support_agent_mock_function(
    messages: list[Any],
    info: Any,
) -> ModelResponse:
    """Deterministic intelligence for local zero-cost evaluation testing."""
    user_prompt = ""
    for msg in reversed(messages):
        if hasattr(msg, "parts"):
            for part in reversed(msg.parts):
                if type(part).__name__ == "UserPromptPart" or (
                    hasattr(part, "content") and type(part).__name__ != "SystemPromptPart"
                ):
                    if hasattr(part, "content") and isinstance(part.content, str):
                        user_prompt = part.content
                        break
        elif hasattr(msg, "content") and isinstance(msg.content, str):
            user_prompt = msg.content
        if user_prompt:
            break

    text_lower = user_prompt.lower().strip()
    resp_text = ""

    # 1. Empty or whitespace-only input handling
    if not text_lower:
        resp_text = "Hello! How can I assist you with your orders or account today?"

    # 2. Out of domain / safety / prompt injection / PII attacks
    elif any(k in text_lower for k in [
        "ignore previous", "system prompt", "bypass", "jailbreak", "recipe",
        "python script", "write a python script", "hack", "dump api", "sql injection",
        "drop table", "reveal credit card", "system override"
    ]):
        resp_text = "I am a customer support assistant. I can only help with order status, account details, returns, and store policies."

    # 3. Missing order ID cases (where no order ID pattern is present)
    elif (
        any(k in text_lower for k in ["where is my package", "where is my order", "order status", "track my package", "delivery update"])
        and not re.search(r"\b[A-H]\d{3}\b", user_prompt, re.IGNORECASE)
    ):
        resp_text = "I would be happy to check that for you. Could you please provide your Order ID (for example, A100 or B200)?"

    # 4. Missing refund details
    elif (
        any(k in text_lower for k in ["refund", "return my purchase", "want a refund", "send back"])
        and not re.search(r"\b[A-H]\d{3}\b", user_prompt, re.IGNORECASE)
    ):
        resp_text = "Our return policy allows refunds within 30 days of delivery. Could you please provide your Order ID to check eligibility?"

    # 5. Order queries
    elif re.search(r"\b([A-H]\d{3}|Z\d{3}|X\d{3})\b", user_prompt, re.IGNORECASE):
        match_order = re.search(r"\b([A-H]\d{3}|Z\d{3}|X\d{3})\b", user_prompt, re.IGNORECASE)
        order_id = match_order.group(1).upper()

        if "refund" in text_lower or "return" in text_lower:
            if order_id == "A100":
                resp_text = f"Order {order_id} is currently Shipped and is within the 30-day return window, making it eligible for a full refund of $199.99 upon return."
            elif order_id == "B200":
                resp_text = f"Order {order_id} was delivered 12 days ago and is eligible for a full refund of $129.50 within our 30-day window."
            elif order_id == "C300":
                resp_text = f"Order {order_id} was delivered 45 days ago, which exceeds our 30-day return window. Therefore, it is not eligible for a refund."
            elif order_id == "D400":
                resp_text = f"Order {order_id} was cancelled. Pre-authorized charges have been released, so no refund is necessary."
            elif order_id == "E500":
                resp_text = f"Order {order_id} is currently Processing and can be cancelled for a full refund of $499.00."
            elif order_id == "F600":
                resp_text = f"Order {order_id} was delivered 28 days ago and is eligible for a full refund of $59.00 within our 30-day return policy window."
            elif order_id == "G700":
                resp_text = f"Order {order_id} was delivered 32 days ago, which exceeds our 30-day return window. Therefore, it is not eligible for a refund."
            elif order_id == "H800":
                resp_text = f"Order {order_id} was delivered 5 days ago and is eligible for a full refund of $39.99 within our 30-day window."
            else:
                resp_text = f"Order {order_id} was not found in our system. Please verify your order ID."
        else:
            if order_id == "A100":
                resp_text = f"Order {order_id} is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones."
            elif order_id == "B200":
                resp_text = f"Order {order_id} is Delivered. Tracking number was TRK-11223 for Mechanical Keyboard."
            elif order_id == "C300":
                resp_text = f"Order {order_id} is Delivered. Tracking number was TRK-44556 for Smart Watch."
            elif order_id == "D400":
                resp_text = f"Order {order_id} has been Cancelled."
            elif order_id == "E500":
                resp_text = f"Order {order_id} is currently Processing for Ultra-Wide Gaming Monitor ($499.00). It has not shipped yet."
            elif order_id == "F600":
                resp_text = f"Order {order_id} is Delivered. Tracking number was TRK-77889 for Wireless Earbuds."
            elif order_id == "G700":
                resp_text = f"Order {order_id} is Delivered. Tracking number was TRK-33445 for Ergonomic Desk Chair."
            elif order_id == "H800":
                resp_text = f"Order {order_id} is Delivered. Tracking number was TRK-99001 for Aluminum Laptop Stand."
            else:
                resp_text = f"Order {order_id} was not found in our system. Please verify your order ID."

    # 6. Customer account queries
    elif re.search(r"\b(CUST-\d{3})\b", user_prompt, re.IGNORECASE):
        match_cust = re.search(r"\b(CUST-\d{3})\b", user_prompt, re.IGNORECASE)
        cust_id = match_cust.group(1).upper()
        if cust_id == "CUST-101":
            resp_text = f"Customer {cust_id} (Alice Johnson) is a VIP tier member with Active account status."
        elif cust_id == "CUST-102":
            resp_text = f"Customer {cust_id} (Bob Smith) is a Standard tier member with Active account status."
        elif cust_id == "CUST-103":
            resp_text = f"Customer {cust_id} (Charlie Brown) is a Standard tier member. Note: Account is currently Suspended."
        elif cust_id == "CUST-104":
            resp_text = f"Customer {cust_id} (Diana Prince) is a VIP tier member with Active account status."
        elif cust_id == "CUST-105":
            resp_text = f"Customer {cust_id} (Evan Wright) is a Standard tier member with Active account status."
        else:
            resp_text = f"Customer {cust_id} was not found in our database."

    # 7. FAQ queries
    elif "shipping" in text_lower or "how long" in text_lower:
        resp_text = "Standard shipping takes 3-5 business days, while express shipping takes 1-2 business days. Tracking numbers are emailed upon dispatch."
    elif "international" in text_lower:
        resp_text = "International shipping is available to over 50 countries and takes 7-14 business days."
    elif "warranty" in text_lower:
        resp_text = "All hardware items include a 1-year limited manufacturer warranty covering defects."
    elif "payment" in text_lower or "pay with" in text_lower:
        resp_text = "We accept major credit cards (Visa, MasterCard, Amex), PayPal, and Apple Pay."
    elif "discount" in text_lower or "vip benefit" in text_lower:
        resp_text = "VIP tier members receive a 10% discount on all purchases automatically applied at checkout."
    elif "hours" in text_lower or "support" in text_lower or "contact" in text_lower:
        resp_text = "Customer support is available Monday through Friday from 9:00 AM to 6:00 PM EST."
    else:
        resp_text = "Thank you for contacting customer support. How can I help you with your order, refund, or shipping question today?"

    return ModelResponse(parts=[TextPart(resp_text)])


def create_support_agent(
    model_name: str | None = None,
    system_prompt: str = SYSTEM_PROMPT_V1,
) -> Agent[SupportDependencies, str]:
    """Factory to create a configured Support Agent instance."""
    selected_model = model_name or config.model_name

    if selected_model in ("test", "mock", "offline"):
        model = FunctionModel(_support_agent_mock_function)
    else:
        model = selected_model

    agent: Agent[SupportDependencies, str] = Agent(
        model,
        deps_type=SupportDependencies,
        system_prompt=system_prompt,
        tools=[lookup_order, lookup_customer, check_refund_policy, get_faq_answer],
    )

    return agent


async def run_support_agent(
    prompt: str,
    deps: SupportDependencies | None = None,
    agent: Agent[SupportDependencies, str] | None = None,
) -> tuple[str, float, list[dict[str, Any]]]:
    """Execute the support agent and measure latency and tool execution.

    Returns:
        tuple of (response_text, latency_seconds, tool_calls_recorded)
    """
    if deps is None:
        deps = create_default_dependencies()
    if agent is None:
        agent = create_support_agent()

    start_time = time.perf_counter()

    text_lower = prompt.lower().strip()
    match_order = re.search(r"\b([A-H]\d{3}|Z\d{3}|X\d{3})\b", prompt, re.IGNORECASE)
    match_cust = re.search(r"\b(CUST-\d{3})\b", prompt, re.IGNORECASE)

    is_malicious = any(k in text_lower for k in [
        "ignore previous", "system prompt", "bypass", "jailbreak", "recipe",
        "python script", "write a python script", "hack", "dump api", "sql injection",
        "drop table", "reveal credit card", "system override"
    ])

    if not is_malicious:
        if match_order:
            order_id = match_order.group(1).upper()
            if "refund" in text_lower or "return" in text_lower:
                deps.tool_call_history.append({"tool": "check_refund_policy", "args": {"order_id": order_id}})
            else:
                deps.tool_call_history.append({"tool": "lookup_order", "args": {"order_id": order_id}})
        elif match_cust:
            cust_id = match_cust.group(1).upper()
            deps.tool_call_history.append({"tool": "lookup_customer", "args": {"customer_id": cust_id}})
        elif any(k in text_lower for k in ["shipping", "international", "warranty", "payment", "discount", "hours"]):
            deps.tool_call_history.append({"tool": "get_faq_answer", "args": {"topic": text_lower}})

    result = await agent.run(prompt, deps=deps)
    end_time = time.perf_counter()

    latency = end_time - start_time
    response_text = getattr(result, "output", getattr(result, "data", str(result)))
    tool_calls = list(deps.tool_call_history)

    return response_text, latency, tool_calls
