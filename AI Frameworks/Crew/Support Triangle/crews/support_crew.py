import logging
import re

from crewai import Crew, Process, Task

from agents.router import RouterAgent
from agents.billing import BillingAgent
from agents.technical import TechnicalAgent
from agents.sales import SalesAgent
from agents.validator import ValidatorAgent

from tasks.routing import RoutingTask
from tasks.billing import BillingTask
from tasks.technical import TechnicalTask
from tasks.sales import SalesTask
from tasks.validation import ValidationTask

from tools.web_search import web_search_tool
from tools.calculator import calculator_tool
from tools.custom_api import currency_tool, weather_tool
from tools.company_data import company_data_tool

from config.settings import MAX_REVISIONS, USE_DEMO_LLM
from tools.demo_llm import (
    _classify_query,
    BILLING_RESPONSE,
    TECHNICAL_RESPONSE,
    SALES_RESPONSE,
    ESCALATE_RESPONSE,
)

logger = logging.getLogger(__name__)

ROUTING_MAP = {
    "billing": {
        "agent_cls": BillingAgent,
        "task_cls": BillingTask,
        "tools": [currency_tool, company_data_tool],
    },
    "technical": {
        "agent_cls": TechnicalAgent,
        "task_cls": TechnicalTask,
        "tools": [web_search_tool, calculator_tool],
    },
    "sales": {
        "agent_cls": SalesAgent,
        "task_cls": SalesTask,
        "tools": [web_search_tool, company_data_tool, weather_tool],
    },
}


def _get_result(result) -> str:
    return result.raw if hasattr(result, "raw") else str(result)


class SupportCrew:
    def __init__(self, query: str, conversation_history: list | None = None):
        self.query = query
        self.conversation_history = conversation_history or []
        self.router_agent = RouterAgent().get()
        self.routing_task = RoutingTask(query).get()
        self._classification = None

    def _build_context(self) -> str:
        if not self.conversation_history:
            return self.query
        parts = []
        for entry in self.conversation_history[-6:]:
            role = "Customer" if entry.get("role") == "user" else "Support Agent"
            parts.append(f"{role}: {entry['content']}")
        parts.append(f"Customer: {self.query}")
        return "\n".join(parts)

    def _run_routing(self) -> str:
        crew = Crew(
            agents=[self.router_agent],
            tasks=[self.routing_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff()
        self._classification = _get_result(result)
        logger.info("Routing result: %s", self._classification[:120])
        return self._classification

    @staticmethod
    def _parse_classification(routing_output: str) -> str:
        text = routing_output.strip().lower()
        words = re.findall(r'\b\w+\b', text)
        for label in ("billing", "technical", "sales", "escalate"):
            if label in words:
                return label
        logger.warning("Could not parse classification from '%s', escalating.", routing_output[:80])
        return "escalate"

    def _run_specialist(self, category: str) -> str:
        if category not in ROUTING_MAP:
            logger.error("Unknown classification '%s', delivering fallback response.", category)
            return "Your request could not be matched to a support specialist. Please try rephrasing your question."
        cfg = ROUTING_MAP[category]
        agent = cfg["agent_cls"](tools=cfg["tools"]).get()
        context = self._build_context()
        task = cfg["task_cls"](context).get()

        logger.info("Specialist: %s with tools %s", agent.role, [t.name for t in agent.tools])

        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
        result = crew.kickoff()
        return _get_result(result)

    def _run_validation(self, query: str, response: str) -> str:
        agent = ValidatorAgent().get()
        task = ValidationTask(query, response).get()

        logger.info("Validator reviewing response (%d chars)...", len(response))

        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
        result = crew.kickoff()
        return _get_result(result)

    @staticmethod
    def _parse_validation(validation_output: str) -> tuple:
        text = validation_output.strip()
        upper = text.upper()
        if upper.startswith("APPROVED"):
            return True, ""
        if upper.startswith("REVISE:"):
            feedback = text[7:].strip()
            return False, feedback or "Please revise the response."
        if upper.startswith("REVISE"):
            feedback = text[6:].strip()
            return False, feedback or "Please revise the response."
        return False, text

    def _run_revision(self, category: str, draft: str, feedback: str) -> str:
        cfg = ROUTING_MAP[category]
        agent = cfg["agent_cls"](tools=cfg["tools"]).get()

        revision_prompt = (
            f"Original customer request: {self.query}\n\n"
            f"Your previous response:\n{draft}\n\n"
            f"Quality review feedback — address each issue:\n{feedback}\n\n"
            f"Please revise your response to fix ALL issues above. "
            f"Use your tools to verify any facts if needed."
        )

        task = Task(
            description=revision_prompt,
            expected_output=cfg["task_cls"](self.query).get().expected_output,
            agent=agent,
        )

        logger.info("Revision requested. Feedback: %s", feedback[:100])
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
        result = crew.kickoff()
        return _get_result(result)

    def _run_demo(self) -> dict:
        logger.info("=== Support Triage Demo Start ===")
        logger.info("Query: %s", self.query[:200])

        category = _classify_query(self.query)
        logger.info("Classification (demo): %s", category)

        routing_rationale = f"{category}: classified via keyword matching"

        if category == "escalate":
            return {
                "query": self.query,
                "classification": "escalate",
                "routing_rationale": routing_rationale,
                "response": ESCALATE_RESPONSE,
                "validated": False,
                "tools_used": [],
            }

        RESPONSE_MAP = {
            "billing": BILLING_RESPONSE,
            "technical": TECHNICAL_RESPONSE,
            "sales": SALES_RESPONSE,
        }

        response_text = RESPONSE_MAP.get(category, ESCALATE_RESPONSE)

        TOOLS_MAP = {
            "billing": ["Currency Converter", "Company Data"],
            "technical": ["Web Search", "Calculator"],
            "sales": ["Web Search", "Company Data", "Weather"],
        }

        logger.info("=== Support Triage Demo End ===")
        return {
            "query": self.query,
            "classification": category,
            "routing_rationale": routing_rationale,
            "response": response_text,
            "validated": True,
            "validation_report": "APPROVED: Demo response meets quality criteria.",
            "tools_used": TOOLS_MAP.get(category, []),
        }

    def run(self) -> dict:
        if USE_DEMO_LLM:
            return self._run_demo()

        logger.info("=== Support Triage Start ===")
        logger.info("Query: %s", self.query[:200])

        routing_output = self._run_routing()
        category = self._parse_classification(routing_output)
        logger.info("Classification: %s", category)

        if category == "escalate":
            return {
                "query": self.query,
                "classification": "escalate",
                "routing_rationale": routing_output,
                "response": "This request could not be confidently classified and has been escalated to a human support agent.",
                "validated": False,
                "tools_used": [],
            }

        cfg = ROUTING_MAP[category]
        tools_used = [t.name for t in cfg["tools"]]

        draft = self._run_specialist(category)

        validation_output = self._run_validation(self.query, draft)
        approved, feedback = self._parse_validation(validation_output)

        if not approved and MAX_REVISIONS > 0:
            logger.info("Validation rejected. Requesting revision...")
            draft = self._run_revision(category, draft, feedback)

            validation_output = self._run_validation(self.query, draft)
            approved, _ = self._parse_validation(validation_output)

            if approved:
                logger.info("Revision accepted.")
            else:
                logger.warning("Revision still has issues. Delivering as-is.")

        logger.info("=== Support Triage End ===")
        return {
            "query": self.query,
            "classification": category,
            "routing_rationale": routing_output,
            "response": draft,
            "validated": approved,
            "validation_report": validation_output,
            "tools_used": tools_used,
        }
