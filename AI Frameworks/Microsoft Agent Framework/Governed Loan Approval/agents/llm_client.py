import os
import httpx
from typing import List, Dict, Any, Optional
from apps.api.config import settings

class LLMClient:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.ollama_host = settings.OLLAMA_HOST
        
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        # Scenario 1: Gemini API
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_prompt
                )
                response = model.generate_content(
                    user_prompt,
                    generation_config={"temperature": temperature}
                )
                return response.text.strip()
            except Exception as e:
                # Log error and fallback
                print(f"[LLM LOG] Gemini failed, falling back: {e}")
        
        # Scenario 2: Ollama Local (Free / Offline)
        try:
            # Check if ollama is reachable via HTTP request
            resp = httpx.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3",  # default model
                    "prompt": f"System: {system_prompt}\nUser: {user_prompt}",
                    "stream": False,
                    "options": {"temperature": temperature}
                },
                timeout=5.0
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception:
            pass  # Ollama not running or timeout, fallback to mock

        # Scenario 3: Rule-based Smart Mock fallback (Guarantees zero-risk execution on laptop)
        return self._smart_mock_response(system_prompt, user_prompt)

    def _smart_mock_response(self, system_instruction: str, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        # 1. Mocking Intent Classifier Agent
        if "classify" in system_instruction.lower():
            if "apply" in prompt_lower or "loan application" in prompt_lower or "borrow" in prompt_lower:
                return "INTENT: loan_application\nAGENT: loan_agent"
            elif "loan" in prompt_lower or "interest" in prompt_lower or "rate" in prompt_lower or "mortgage" in prompt_lower:
                return "INTENT: loan_inquiry\nAGENT: loan_agent"
            elif "support" in prompt_lower or "error" in prompt_lower or "bug" in prompt_lower or "ticket" in prompt_lower:
                return "INTENT: general_support\nAGENT: support_agent"
            else:
                return "INTENT: general_support\nAGENT: support_agent"

        # 2. Mocking Loan Agent
        if "loan" in system_instruction.lower():
            if "apply" in prompt_lower:
                # Extract amount if present
                amount = "5000"
                for word in prompt.replace("$", "").split():
                    if word.isdigit():
                        amount = word
                        break
                return f"LOAN_APPLICATION: amount={amount}, purpose=requested loan. Processing application details."
            return "Based on our current regulations, we offer competitive personal and home loan interest rates starting from 5.4% APR for 12 to 60-month terms. Please apply formally so we can evaluate your credit score."

        # 3. Mocking Support Agent
        if "support" in system_instruction.lower():
            return "Thank you for reaching out to customer support. I have checked your account status, and we are working to resolve any technical issues you may be facing. Let me know if you need to open a formal ticket."

        # 4. Fallback Generic
        return "I am the automated Governed Agent. How may I assist you with your loan or support query today?"
