# app/agent.py

import os
import time
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from app.config import LLM_MODEL, OLLAMA_BASE_URL
from app.models import TicketResult, TicketCategory, TicketPriority, SuggestedAgent
from app.prompts import SYSTEM_INSTRUCTION

# Helper to initialize model
def get_model(model_str: str):
    if model_str.startswith("ollama:"):
        # Slice off 'ollama:' prefix to get local model name
        model_name = model_str[7:]
        # Ensure base URL is configured in environment for Pydantic AI Ollama provider
        os.environ["OLLAMA_BASE_URL"] = OLLAMA_BASE_URL
        return OllamaModel(model_name=model_name)
    else:
        # Pass directly (e.g. "groq:...", "google:...")
        return model_str

# Initialize Agents
from app.config import FALLBACK_MODEL
from pydantic_ai.settings import ModelSettings

try:
    primary_model = get_model(LLM_MODEL)
    primary_agent = Agent(
        model=primary_model,
        output_type=TicketResult,
        system_prompt=SYSTEM_INSTRUCTION,
        retries=3, # Pydantic AI will automatically retry if output fails validation
        model_settings=ModelSettings(timeout=15.0)
    )
except Exception as e:
    print(f"Error initializing primary agent model: {e}")
    primary_agent = None

try:
    fallback_model = get_model(FALLBACK_MODEL)
    fallback_agent = Agent(
        model=fallback_model,
        output_type=TicketResult,
        system_prompt=SYSTEM_INSTRUCTION,
        retries=3,
        model_settings=ModelSettings(timeout=15.0)
    )
except Exception as e:
    print(f"Error initializing fallback agent model: {e}")
    fallback_agent = None

# Backward compatibility alias for tests overriding agent
agent = primary_agent

def fallback_classify(message: str) -> TicketResult:
    """A fallback rule-based classifier if LLM fails or is unavailable."""
    msg_lower = message.lower()
    
    # 1. Check for security indicators
    if any(word in msg_lower for word in ["hack", "compromise", "unauthorized", "security", "breach", "leak"]):
        return TicketResult(
            category=TicketCategory.SECURITY,
            priority=TicketPriority.CRITICAL,
            suggested_agent=SuggestedAgent.SECURITY,
            confidence=0.5,
            summary="Potential security breach or unauthorized access request.",
            reasoning="Rule-based fallback: Detected security-related keywords in ticket.",
            requires_human_review=True
        )
        
    # 2. Check for billing/refund indicators
    if any(word in msg_lower for word in ["charge", "billing", "invoice", "refund", "payment", "card", "receipt"]):
        category = TicketCategory.BILLING
        suggested_agent = SuggestedAgent.BILLING
        if "refund" in msg_lower:
            category = TicketCategory.REFUND
        elif any(w in msg_lower for w in ["subscribe", "plan", "upgrade", "cancel"]):
            category = TicketCategory.SUBSCRIPTION
            
        return TicketResult(
            category=category,
            priority=TicketPriority.MEDIUM,
            suggested_agent=suggested_agent,
            confidence=0.5,
            summary="Billing, refund or subscription related request.",
            reasoning="Rule-based fallback: Detected financial or transactional keywords.",
            requires_human_review=False
        )

    # 3. Check for technical issues
    if any(word in msg_lower for word in ["error", "500", "fail", "bug", "broken", "export", "crash", "slow"]):
        return TicketResult(
            category=TicketCategory.TECHNICAL,
            priority=TicketPriority.HIGH,
            suggested_agent=SuggestedAgent.TECHNICAL,
            confidence=0.5,
            summary="Technical error or system malfunction reported.",
            reasoning="Rule-based fallback: Detected system failure or bug keywords.",
            requires_human_review=False
        )
        
    # 4. Default other
    return TicketResult(
        category=TicketCategory.OTHER,
        priority=TicketPriority.LOW,
        suggested_agent=SuggestedAgent.HUMAN,
        confidence=0.3,
        summary="Support inquiry requiring categorization.",
        reasoning="Rule-based fallback: No clear keywords matched, routing to general human support.",
        requires_human_review=True
    )

def classify_ticket_content(message: str) -> tuple[TicketResult, int]:
    """
    Runs the Pydantic AI agent to classify the support ticket.
    Failover logic: Primary LLM -> Fallback LLM -> Fallback Rule Heuristics.
    Returns a tuple of (TicketResult, processing_time_ms).
    """
    start_time = time.perf_counter()
    
    # 1. Attempt Primary Agent
    if primary_agent is not None:
        try:
            run_res = primary_agent.run_sync(message)
            result = run_res.output
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return result, duration_ms
        except Exception as e1:
            print(f"Primary agent ({LLM_MODEL}) failed: {e1}. Trying fallback agent...")
            
    # 2. Attempt Fallback Agent
    if fallback_agent is not None:
        try:
            run_res = fallback_agent.run_sync(message)
            result = run_res.output
            # Append notice to reasoning
            result.reasoning += f" (Note: Classified by fallback model {FALLBACK_MODEL} after primary failed: {str(e1)})"
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return result, duration_ms
        except Exception as e2:
            print(f"Fallback agent ({FALLBACK_MODEL}) also failed: {e2}. Falling back to rule heuristics...")
            error_details = f"Primary error: {str(e1)}. Fallback error: {str(e2)}"
    else:
        error_details = f"Primary error: {str(e1)}. Fallback agent was not initialized."

    # 3. Fallback to deterministic rules
    result = fallback_classify(message)
    result.reasoning += f" (Note: All LLM models failed. Details: {error_details})"
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    return result, duration_ms
