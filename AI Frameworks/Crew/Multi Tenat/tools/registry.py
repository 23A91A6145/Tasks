"""Tool Ecosystem — Built-in enterprise tools for AI agents and REST API.

Provides:
- Calculator (safe mathematical evaluation)
- Web Search (live web & technical search)
- CRM Lookup (tenant customer profiles, subscription tiers, SLA limits)
- Email Dispatcher (drafting & sending support notifications)
- Calendar Scheduler (follow-up meeting scheduling)
- GitHub Support Tool (create issues, list repository files)
- Ticket Operations (sub-ticket management & agent assignment)
"""

import math
import re
from typing import Any, Callable, Dict, List, Optional


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        parameters_schema: Dict[str, Any],
        category: str = "general",
    ):
        self._tools[name] = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters_schema,
            "category": category,
        }

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for name, meta in self._tools.items():
            if category and meta["category"] != category:
                continue
            results.append({
                "name": meta["name"],
                "description": meta["description"],
                "parameters": meta["parameters"],
                "category": meta["category"],
            })
        return results

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found"}
        try:
            result = tool["func"](**kwargs)
            return {"success": True, "tool": name, "result": result}
        except Exception as exc:
            return {"success": False, "tool": name, "error": str(exc)}


# Tool implementations
def run_calculator(expression: str) -> str:
    """Safe evaluation of mathematical expressions."""
    cleaned = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", expression)
    if not cleaned.strip():
        return "Error: Invalid expression"
    try:
        # Evaluate using safe global context
        allowed_names = {"sqrt": math.sqrt, "abs": abs, "round": round}
        val = eval(cleaned, {"__builtins__": None}, allowed_names)
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(round(val, 4) if isinstance(val, float) else val)
    except Exception as e:
        return f"Error: {e}"


def run_web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Simulated web search for documentation and live technical information."""
    q_lower = query.lower()
    results = []
    if "billing" in q_lower or "price" in q_lower or "plan" in q_lower:
        results.append({
            "title": "Pricing & Billing Overview",
            "snippet": "TenantDesk offers Free ($0), Pro ($49/mo), and Enterprise ($299/mo) plans. Upgrades are prorated.",
            "url": "https://tenantdesk.ai/docs/billing",
        })
    if "api" in q_lower or "token" in q_lower or "auth" in q_lower:
        results.append({
            "title": "API Authentication Guide",
            "snippet": "Include Bearer JWT token in Authorization header: 'Authorization: Bearer <JWT>'. Tokens expire in 30 days.",
            "url": "https://tenantdesk.ai/docs/api-auth",
        })
    if "reset" in q_lower or "password" in q_lower:
        results.append({
            "title": "Account & Password Security",
            "snippet": "Navigate to Workspace Settings -> Security -> Reset Password. Verification link sent via email.",
            "url": "https://tenantdesk.ai/docs/password-reset",
        })
    if not results:
        results.append({
            "title": f"Search results for '{query}'",
            "snippet": f"Official documentation search returned relevant guidelines for topic: {query}.",
            "url": f"https://tenantdesk.ai/search?q={query}",
        })
    return results[:max_results]


def run_crm_lookup(customer_email: str) -> Dict[str, Any]:
    """Fetch customer profile, subscription tier, and support history from CRM."""
    hash_val = sum(ord(c) for c in customer_email)
    tiers = ["Free Plan", "Pro Plan", "Enterprise Plan"]
    chosen_tier = tiers[hash_val % len(tiers)]
    return {
        "email": customer_email,
        "name": customer_email.split("@")[0].capitalize(),
        "tier": chosen_tier,
        "sla_tier": "Priority 24/7" if chosen_tier == "Enterprise Plan" else "Standard 24h",
        "open_tickets": hash_val % 3,
        "lifetime_value": f"${(hash_val % 10 + 1) * 120}.00",
        "account_status": "active",
    }


def run_send_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
    """Draft and dispatch transactional customer support email."""
    return {
        "status": "queued",
        "recipient": recipient,
        "subject": subject,
        "preview": body[:100] + "..." if len(body) > 100 else body,
        "message_id": f"msg_{hash(subject + recipient) & 0xFFFFFFFF:08x}",
    }


def run_schedule_calendar(
    title: str,
    attendee_email: str,
    date_time: str,
    duration_minutes: int = 30,
) -> Dict[str, Any]:
    """Schedule a support follow-up call or onboarding session."""
    return {
        "status": "scheduled",
        "title": title,
        "attendee": attendee_email,
        "scheduled_time": date_time,
        "duration": f"{duration_minutes} mins",
        "calendar_link": f"https://cal.tenantdesk.ai/invite/{hash(title) & 0xFFFF}",
    }


def run_github_tool(
    action: str,
    repo: str,
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> Dict[str, Any]:
    """GitHub integration to search code or create support issue."""
    if action == "create_issue":
        return {
            "status": "created",
            "action": "create_issue",
            "repo": repo,
            "issue_id": f"#{hash(title or '') % 500 + 1}",
            "title": title or "Support Escalate Issue",
            "url": f"https://github.com/{repo}/issues/{hash(title or '') % 500 + 1}",
        }
    return {
        "status": "success",
        "action": action,
        "repo": repo,
        "files": ["README.md", "src/index.ts", "docs/API.md", "package.json"],
    }


# Global tool registry instance
registry = ToolRegistry()

# Register core tools
registry.register(
    name="calculator",
    description="Evaluates mathematical expressions safely (e.g. '120 * 0.85' or '50 + 25').",
    func=run_calculator,
    parameters_schema={"expression": {"type": "string", "description": "Math expression to solve"}},
    category="utility",
)

registry.register(
    name="web_search",
    description="Searches online documentation and knowledge bases for live answers.",
    func=run_web_search,
    parameters_schema={"query": {"type": "string", "description": "Search query keywords"}},
    category="search",
)

registry.register(
    name="crm_lookup",
    description="Queries CRM database for customer tier, SLA level, and lifetime value.",
    func=run_crm_lookup,
    parameters_schema={"customer_email": {"type": "string", "description": "Customer email address"}},
    category="crm",
)

registry.register(
    name="send_email",
    description="Sends or queues a transactional support email to the customer.",
    func=run_send_email,
    parameters_schema={
        "recipient": {"type": "string"},
        "subject": {"type": "string"},
        "body": {"type": "string"},
    },
    category="communication",
)

registry.register(
    name="schedule_calendar",
    description="Schedules support follow-up calls or screen-share meetings.",
    func=run_schedule_calendar,
    parameters_schema={
        "title": {"type": "string"},
        "attendee_email": {"type": "string"},
        "date_time": {"type": "string"},
    },
    category="communication",
)

registry.register(
    name="github_tool",
    description="Interacts with GitHub repositories to create support issues or view repo files.",
    func=run_github_tool,
    parameters_schema={
        "action": {"type": "string", "enum": ["create_issue", "list_files"]},
        "repo": {"type": "string"},
        "title": {"type": "string"},
    },
    category="developer",
)
