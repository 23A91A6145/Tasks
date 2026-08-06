import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from app.config import LLM_PROVIDER, GROQ_API_KEY, OLLAMA_API_BASE, LLM_MODEL, MAX_AUTO_APPROVE_AMOUNT
from app.utils import logger, MOCK_CUSTOMERS, MOCK_ORDERS, generate_id, log_audit
from app.refund_tool import validate_policy, execute_payment_refund
from app.workflow import WorkflowState
from app.models import ApprovalRequest, AuditLogEntry
from app.approval import save_approval_request, get_all_approval_requests

class ChatAgent:
    """
    AI Refund Agent. Responsible for conversational interactions, policy validation,
    sensitive tool detection, workflow pausing, and checkpoint management.
    """
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Best-effort JSON extraction from an LLM response."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return None
        return None

    def _call_groq(self, message: str) -> Optional[Dict[str, Any]]:
        """Structured extraction using the Groq free tier (urllib, no extra deps)."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        prompt = (
            "Extract refund request fields from the customer message. "
            "Respond with ONLY JSON: {\"customer_id\": \"CUST-####\", \"order_id\": \"ORD-####\", "
            "\"amount\": 0.0, \"reason\": \"...\"}. Use null for missing fields."
            f"\n\nCustomer message: {message}"
        )
        payload = json.dumps({
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode())
        content = body["choices"][0]["message"]["content"]
        parsed = self._extract_json(content)
        if not parsed:
            return None
        return {
            "customer_id": (parsed.get("customer_id") or "").upper(),
            "order_id": (parsed.get("order_id") or "").upper(),
            "amount": parsed.get("amount"),
            "reason": parsed.get("reason") or "No reason specified",
        }

    def _call_ollama(self, message: str) -> Optional[Dict[str, Any]]:
        """Structured extraction using a local Ollama instance (offline LLM)."""
        url = f"{OLLAMA_API_BASE}/api/chat"
        prompt = (
            "Extract refund request fields. Reply with ONLY JSON: "
            "{\"customer_id\": \"CUST-####\", \"order_id\": \"ORD-####\", "
            "\"amount\": 0.0, \"reason\": \"...\"}. Use null for missing fields."
            f"\n\nCustomer message: {message}"
        )
        payload = json.dumps({
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0},
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
        content = body.get("message", {}).get("content", "")
        parsed = self._extract_json(content)
        if not parsed:
            return None
        return {
            "customer_id": (parsed.get("customer_id") or "").upper(),
            "order_id": (parsed.get("order_id") or "").upper(),
            "amount": parsed.get("amount"),
            "reason": parsed.get("reason") or "No reason specified",
        }

    def parse_with_llm(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Structured field extraction using a configured LLM provider (Groq / Ollama).
        Returns a dict of (customer_id, order_id, amount, reason) or None on failure.
        """
        try:
            if LLM_PROVIDER == "groq":
                if not GROQ_API_KEY:
                    logger.warning("LLM_PROVIDER=groq but GROQ_API_KEY is empty; using heuristics.")
                    return None
                return self._call_groq(message)
            if LLM_PROVIDER == "ollama":
                return self._call_ollama(message)
        except Exception as e:
            logger.warning(f"LLM parsing failed ({LLM_PROVIDER}): {e}; falling back to heuristics.")
        return None

    def extract_refund_details(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[str]]:
        """
        Parses the query text using LLM or rule heuristics to find refund parameters.
        Returns (customer_id, order_id, amount, reason).
        """
        # 1. Try LLM first if configured (Groq / Ollama via agent-framework or direct client)
        if LLM_PROVIDER != "mock":
            try:
                llm_result = self.parse_with_llm(message)
                if llm_result and all(
                    k in llm_result for k in ("customer_id", "order_id", "amount", "reason")
                ):
                    logger.info(f"✨ LLM parsing succeeded: {llm_result}")
                    return (
                        llm_result["customer_id"],
                        llm_result["order_id"],
                        llm_result["amount"],
                        llm_result["reason"],
                    )
            except Exception as e:
                logger.warning(f"LLM parsing failed, falling back to heuristics: {e}")

        # 2. Rule-based heuristic extraction (deterministic, offline, 100% free)
        customer_id = None
        order_id = None
        amount = None
        reason = "No reason specified"

        # Regex patterns for identifiers
        cust_match = re.search(r"CUST-\d+", message, re.IGNORECASE)
        ord_match = re.search(r"ORD-\d+", message, re.IGNORECASE)

        if cust_match:
            customer_id = cust_match.group(0).upper()
        if ord_match:
            order_id = ord_match.group(0).upper()

        # Amount extraction: prefer explicit currency markers so numbers inside
        # IDs like "CUST-1045" are never mistaken for the refund amount.
        dollar_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", message)
        if dollar_match:
            amount = float(dollar_match.group(1))
        else:
            usd_match = re.search(
                r"\b(\d+(?:\.\d+)?)\s*(?:dollars|usd)\b", message, re.IGNORECASE
            )
            if usd_match:
                amount = float(usd_match.group(1))
            else:
                # Fall back to the first bare number that is not part of an ID
                for num in re.findall(r"\d+(?:\.\d+)?", message):
                    if cust_match and num in cust_match.group(0):
                        continue
                    if ord_match and num in ord_match.group(0):
                        continue
                    amount = float(num)
                    break

        # Attempt to extract reason (ordered by specificity)
        reason_phrases = [
            "reason is",
            "reason:",
            "because of",
            "because",
            "due to",
            "refund for",
            "refund of",
        ]
        for phrase in reason_phrases:
            idx = message.lower().find(phrase)
            if idx != -1:
                raw = message[idx + len(phrase):].strip(" .?!,;")
                # Cut the phrase at the next identifier or currency token
                cut = re.search(r"\s(CUST-\d+|ORD-\d+|\$\s*\d+)\b", raw, re.IGNORECASE)
                if cut:
                    raw = raw[:cut.start()]
                if raw:
                    reason = raw
                break

        return customer_id, order_id, amount, reason

    def run(self, message: str) -> Dict[str, Any]:
        """
        Processes a chat request. Evaluates policies, handles human-in-the-loop pauses,
        and saves checkpoint state.
        """
        logger.info(f"ChatAgent received message: {message}")
        
        # Extract fields
        customer_id, order_id, amount, reason = self.extract_refund_details(message)
        
        if not customer_id or not order_id or amount is None:
            return {
                "status": "clarification_required",
                "message": "I noticed you want to process a refund, but I need some details. Please provide: Customer ID (e.g., CUST-1045), Order ID (e.g., ORD-5582), and the Refund Amount.",
                "missing_fields": {
                    "customer_id": not customer_id,
                    "order_id": not order_id,
                    "amount": amount is None
                }
            }

        # Check for duplicate transactions (compliance safety block).
        # Only ACTIVE tickets block a resubmission: finalized (Approved/Rejected/
        # Expired) requests have left the queue and a fresh ticket may be opened.
        ACTIVE = ("Pending", "Escalated", "Hold", "Request More Info")
        try:
            existing_requests = get_all_approval_requests()
            for req_id, req_data in existing_requests.items():
                if req_data.get("order_id") == order_id and req_data.get("status") in ACTIVE:
                    logger.warning(f"❌ Security Block: Duplicate refund attempt for order {order_id} (Current status: {req_data.get('status')})")
                    return {
                        "status": "policy_rejected",
                        "message": f"Security Alert: A refund request for Order '{order_id}' already exists with status '{req_data.get('status')}'. Duplicate submissions are blocked by compliance rules.",
                        "details": {
                            "customer_id": customer_id,
                            "order_id": order_id,
                            "amount": amount,
                            "reason": f"Duplicate transaction attempt. Existing ticket: {req_id}"
                        }
                    }
        except Exception as e:
            logger.error(f"Error checking duplicate refunds: {e}")

        # Validate against refund policies
        is_valid, policy_reason, role_required = validate_policy(customer_id, order_id, amount)
        
        if not is_valid:
            logger.warning(f"❌ Policy check failed for Customer={customer_id}, Order={order_id}: {policy_reason}")
            return {
                "status": "policy_rejected",
                "message": f"Refund request rejected by Safety Policy Engine: {policy_reason}",
                "details": {
                    "customer_id": customer_id,
                    "order_id": order_id,
                    "amount": amount,
                    "reason": policy_reason
                }
            }

        # Safety Gate: Tool execute_payment_refund has approval_mode="always_require"
        request_id = generate_id("REF")
        now_str = datetime.now().isoformat()
        
        customer_details = MOCK_CUSTOMERS.get(customer_id, {})
        risk_level = customer_details.get("risk_level", "Low")

        # Check if eligible for automatic approval (low risk, low amount, active account)
        if amount <= MAX_AUTO_APPROVE_AMOUNT and risk_level == "Low" and customer_details.get("account_status", "Active") == "Active":
            logger.info(f"⚡ Auto-Approving refund {request_id} for Customer={customer_id}, Amount=${amount:.2f}")
            
            # Execute payment refund tool immediately
            tool_result = execute_payment_refund(customer_id, order_id, amount, reason)
            
            # Create finalized ApprovalRequest
            approval_req = ApprovalRequest(
                id=request_id,
                customer_id=customer_id,
                order_id=order_id,
                amount=amount,
                reason=reason,
                risk_level=risk_level,
                product=customer_details.get("product_name", "Unknown Product"),
                purchase_date=customer_details.get("purchase_date", ""),
                status="Approved",
                reviewer="System (Auto-Approve)",
                role_required=role_required,
                notes=f"Auto-approved: Amount is <= ${MAX_AUTO_APPROVE_AMOUNT:.2f} and Customer Risk is Low.",
                created_at=now_str,
                handled_at=now_str,
                timeline=[
                    {"step": "Customer Request Received", "timestamp": now_str},
                    {"step": "Safety Policies Verified", "timestamp": now_str},
                    {"step": "Eligibility for Auto-Approval Verified", "timestamp": now_str},
                    {"step": "Refund Executed Automatically", "timestamp": now_str}
                ]
            )
            
            # Save request to database
            save_approval_request(approval_req)
            
            # Write to audit log
            audit_entry = AuditLogEntry(
                timestamp=now_str,
                request_id=request_id,
                customer_id=customer_id,
                order_id=order_id,
                amount=amount,
                decision="Approved (Auto)",
                reason=reason,
                reviewer="System (Auto-Approve)",
                reviewer_role="System",
                notes=approval_req.notes,
                ip_address="127.0.0.1",
                session_id="SESSION-AUTO-APPROVE"
            )
            log_audit(audit_entry.model_dump())
            
            return {
                "status": "auto_approved",
                "message": f"Refund of ${amount:.2f} was automatically approved and processed under standard risk policies. Transaction reference: {tool_result['transaction_id']}",
                "request_id": request_id,
                "approval_req": approval_req
            }

        # Otherwise, fall back to Human-in-the-Loop approval gate
        approval_req = ApprovalRequest(
            id=request_id,
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            reason=reason,
            risk_level=risk_level,
            product=customer_details.get("product_name", "Unknown Product"),
            purchase_date=customer_details.get("purchase_date", ""),
            status="Pending",
            role_required=role_required,
            created_at=now_str,
            timeline=[
                {"step": "Customer Request Received", "timestamp": now_str},
                {"step": "Safety Policies Verified", "timestamp": now_str},
                {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": now_str}
            ]
        )

        # Save checkpoint to pause workflow
        checkpoint_data = {
            "request_id": request_id,
            "tool_call": {
                "name": "execute_payment_refund",
                "args": {
                    "customer_id": customer_id,
                    "order_id": order_id,
                    "amount": amount,
                    "reason": reason
                }
            },
            "approval_req": approval_req.model_dump(),
            "paused_at": now_str
        }
        
        WorkflowState.save_checkpoint(request_id, checkpoint_data)
        
        return {
            "status": "approval_required",
            "message": f"Refund request of ${amount:.2f} created. It requires approval from a {role_required} before it can execute.",
            "request_id": request_id,
            "approval_req": approval_req
        }
