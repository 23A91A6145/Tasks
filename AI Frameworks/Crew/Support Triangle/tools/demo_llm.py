import logging
import re
from typing import Any, Dict, List, Optional, Union

from crewai.llm import LLM

logger = logging.getLogger(__name__)

CLASSIFICATION_KEYWORDS = {
    "billing": [
        "charge", "invoice", "payment", "refund", "subscription", "billing",
        "discount", "overcharge", "double", "bill", "paid", "cost", "fee",
    ],
    "technical": [
        "login", "log in", "log into", "password", "error", "bug", "dashboard",
        "loading", "crash", "technical", "broken", "down", "not working",
        "error message", "authentication", "access", "reset", "spinner",
        "invalid credentials",
    ],
    "sales": [
        "plan", "upgrade", "pricing", "compare", "features", "pro",
        "enterprise", "basic", "purchase", "buy", "offer", "promotion",
        "student discount", "difference between",
    ],
}


def _classify_query(query: str) -> str:
    q = query.lower()
    scores = {}
    for cat, keywords in CLASSIFICATION_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(re.escape(kw), q))
        scores[cat] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "escalate"
    return best


BILLING_RESPONSE = """Thank you for reaching out about this billing concern.

I have reviewed your account and see what happened. Here is what I found and how we can resolve this:

**Issue:** After checking our billing system, I can see the charge in question.

**Resolution Steps:**
1. The duplicate charge has been flagged for review
2. A refund has been initiated for the erroneous charge (expected within 3-5 business days)
3. I have also verified your billing profile to prevent this from recurring

**Next time:** You can view your full billing history and manage your payment methods anytime through your account dashboard under Settings > Billing.

If you have any other questions about your bill or account, please do not hesitate to ask."""

TECHNICAL_RESPONSE = """Thank you for contacting technical support. I will help you resolve this issue.

**Diagnosis:** Based on the description, this appears to be a common issue that can be resolved with a few troubleshooting steps.

**Step-by-Step Resolution:**
1. **Clear your browser cache and cookies** — Go to your browser settings and clear cached data for the last 24 hours, then restart the browser
2. **Try a different browser or incognito mode** — This helps isolate whether the issue is browser-specific
3. **Check for updates** — Ensure you are using the latest version of the application
4. **Restart the application** — Close and reopen the application completely

If the issue persists after trying these steps, please let me know and I will escalate this to our engineering team with a detailed report."""

SALES_RESPONSE = """Thank you for your interest! I am happy to help you find the right plan.

**Plan Comparison Overview:**

| Feature | Basic | Pro | Enterprise |
|---------|-------|-----|------------|
| Users | Up to 5 | Up to 50 | Unlimited |
| Support | Email | Priority Chat | 24/7 Phone + Chat |
| Analytics | Basic | Advanced | Custom |
| Integrations | 10 | 50 | Unlimited API |
| Storage | 10 GB | 100 GB | Custom |

**Recommendation:** Based on what you have described, the **Pro** plan would be an excellent fit. It offers the best balance of features and value for most customers, with room to grow as your needs evolve.

Would you like me to help you get started with an upgrade or answer any specific questions about these plans?"""

ESCALATE_RESPONSE = "This request could not be confidently classified and has been escalated to a human support agent."

VALIDATION_APPROVED = "APPROVED: The response is complete, accurate, professional, actionable, and concise. All five quality criteria are met."


class DemoLLM(LLM):
    def __init__(self):
        super().__init__(model="demo/demo")

    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
    ) -> str:
        prompt = self._extract_prompt(messages)
        logger.debug("DemoLLM.call received prompt (%d chars)", len(prompt))

        prompt_lower = prompt.lower()

        if "approv" in prompt_lower and "revise" in prompt_lower:
            return self._handle_validation(prompt)
        if "classify" in prompt_lower or "classification" in prompt_lower:
            return self._handle_routing(prompt)
        if "revise" in prompt_lower or "revision" in prompt_lower:
            return self._handle_revision(prompt)
        return self._handle_specialist(prompt)

    def _extract_prompt(self, messages: Union[str, List[Dict[str, str]]]) -> str:
        if isinstance(messages, str):
            return messages
        parts = []
        for m in messages:
            if isinstance(m, dict) and "content" in m:
                parts.append(str(m["content"]))
        return "\n".join(parts)

    def _extract_query(self, prompt: str) -> str:
        for marker in [
            "Customer request:",
            "Original customer request:",
            "Original customer query:",
            "Customer:",
        ]:
            if marker in prompt:
                idx = prompt.index(marker) + len(marker)
                rest = prompt[idx:].strip()
                end = rest.find("\n")
                if end > 0:
                    return rest[:end].strip()
                return rest
        lines = [l.strip() for l in prompt.split("\n") if l.strip()]
        if lines:
            return lines[-1]
        return prompt[:200]

    def _handle_routing(self, prompt: str) -> str:
        query = self._extract_query(prompt)
        category = _classify_query(query)
        return f"{category}: The customer's query has been classified as {category} based on the content and context of their request."

    def _handle_specialist(self, prompt: str) -> str:
        query = self._extract_query(prompt)
        category = _classify_query(query)
        if category == "billing":
            return BILLING_RESPONSE
        if category == "technical":
            return TECHNICAL_RESPONSE
        if category == "sales":
            return SALES_RESPONSE
        return ESCALATE_RESPONSE

    def _handle_validation(self, prompt: str) -> str:
        return VALIDATION_APPROVED

    def _handle_revision(self, prompt: str) -> str:
        draft = self._extract_previous_response(prompt)
        if draft:
            return draft + "\n\n(I have revised the above response based on the quality feedback provided.)"
        return self._handle_specialist(prompt)

    def _extract_previous_response(self, prompt: str) -> str:
        for marker in ["Your previous response:", "Specialist response:"]:
            if marker in prompt:
                idx = prompt.index(marker) + len(marker)
                rest = prompt[idx:].strip()
                end = rest.find("\n\n")
                if end > 0:
                    return rest[:end].strip()
                return rest
        return ""
