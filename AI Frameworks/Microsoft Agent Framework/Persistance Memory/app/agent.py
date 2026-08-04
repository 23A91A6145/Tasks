"""
ChatAgent implementation managing LLM providers (Mock Local Engine, Ollama, Groq, Gemini).
Features Volume 4 Fallback Circuit Breaker & Latency Tracking.
"""

import time
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Tuple
from app.config import AppConfig

class ChatAgent:
    """
    ChatAgent manages interaction with LLMs.
    Features a Fallback Circuit Breaker to ensure 100% availability even if APIs fail.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.provider = config.llm_provider
        self.model_name = self._resolve_model_name()
        self.last_latency_ms: float = 0.0
        self.fallback_active: bool = False

    def _resolve_model_name(self) -> str:
        if self.provider == "ollama":
            return f"Ollama ({self.config.ollama_model})"
        elif self.provider == "groq":
            return "Groq (llama-3.3-70b-versatile)"
        elif self.provider == "gemini":
            return "Gemini (gemini-1.5-flash)"
        else:
            return "Mock AI Engine (Offline Free)"

    def generate_response_with_latency(self, user_input: str, context_messages: List[Dict[str, str]]) -> Tuple[str, float]:
        """
        Generates response and returns tuple: (response_text, latency_ms).
        Includes Fallback Circuit Breaker.
        """
        start_time = time.perf_counter()
        self.fallback_active = False

        try:
            if self.provider == "ollama":
                resp = self._call_ollama(context_messages)
            elif self.provider == "groq":
                resp = self._call_groq(context_messages)
            elif self.provider == "gemini":
                resp = self._call_gemini(context_messages)
            else:
                resp = self._call_mock_engine(user_input, context_messages)
        except Exception as err:
            # Fallback Circuit Breaker Triggered!
            self.fallback_active = True
            fallback_reason = str(err)
            mock_resp = self._call_mock_engine(user_input, context_messages)
            resp = (
                f"⚡ **[Fallback Circuit Breaker Active]**\n"
                f"*(Primary provider '{self.provider}' unavailable: {fallback_reason}. Automatically routing to Local Mock Engine.)*\n\n"
                f"{mock_resp}"
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        self.last_latency_ms = elapsed_ms
        return resp, elapsed_ms

    def generate_response(self, user_input: str, context_messages: List[Dict[str, str]]) -> str:
        """Standard wrapper returning response text."""
        resp, _ = self.generate_response_with_latency(user_input, context_messages)
        return resp

    def _call_mock_engine(self, user_input: str, context_messages: List[Dict[str, str]]) -> str:
        """Volume 4 local offline smart AI engine with persistent memory recall."""
        input_lower = user_input.lower().strip()

        # Parse system facts
        system_facts = {}
        for m in context_messages:
            if m["role"] == "system" and "[Persistent User Facts Memory]:" in m["content"]:
                facts_section = m["content"].split("[Persistent User Facts Memory]:", 1)[1]
                if "[Persistent Memory Summary" in facts_section:
                    facts_section = facts_section.split("[Persistent Memory Summary", 1)[0]
                for line in facts_section.strip().splitlines():
                    if line.startswith("- "):
                        parts = line[2:].split(":", 1)
                        if len(parts) == 2:
                            system_facts[parts[0].strip().lower()] = parts[1].strip()

        # Recall queries
        if any(w in input_lower for w in ["who am i", "my name", "what is my name", "do you remember me", "what do you know about me", "my role", "my tech stack"]):
            recalled_list = []
            if system_facts:
                for k, v in system_facts.items():
                    recalled_list.append(f"**{k.capitalize()}**: {v}")

            if not recalled_list:
                for msg in context_messages:
                    if msg["role"] == "user":
                        text = msg["content"]
                        if re.search(r"\bmy name is\b", text, re.IGNORECASE):
                            name = text.split("is", 1)[1].strip()
                            recalled_list.append(f"**Name**: {name}")
                        elif re.search(r"\bi am (?:a|an)\b", text, re.IGNORECASE):
                            role = text.split("am", 1)[1].strip()
                            recalled_list.append(f"**Role**: {role}")

            if recalled_list:
                return "🧠 **Persistent Memory Recall (Volume 4)**:\n" + "\n".join(f"- {item}" for item in recalled_list)
            else:
                return (
                    "I remember our persistent session thread, but I haven't recorded specific facts yet!\n"
                    "Tell me something like: *'My name is Alice'*, *'I am a Python Developer'*, or *'I live in Seattle'*, "
                    "and I will automatically index and recall it across script restarts!"
                )

        # Greetings
        if any(w in input_lower for w in ["hello", "hi", "hey", "greetings"]):
            user_turns = [m for m in context_messages if m["role"] == "user"]
            if len(user_turns) > 1:
                return f"Welcome back! This session has {len(user_turns)} past user turns loaded in persistent memory. How can I help you today?"
            return "Hello! I am your Volume 4 Persistent-Memory AI Assistant. I automatically index facts and recall our conversation history across restarts!"

        # Features
        if "what can you do" in input_lower or "features" in input_lower:
            return (
                "Here are my Volume 4 Production Persistent Memory capabilities:\n"
                "1. **Semantic Fact Extraction**: Automatically detects names, roles, and tech stack.\n"
                "2. **Sliding Window Summarizer**: Compresses long conversations into memory summaries.\n"
                "3. **Fallback Circuit Breaker**: Auto-routes to offline engine if remote LLM API fails.\n"
                "4. **Multi-Format History Exporter**: Export history to TXT, MD, or JSON using `/export`.\n"
                "5. **Analytics Dashboard**: Run `/analytics` or `/stats` for token metrics.\n"
                "6. **Multi-Model Support**: Hot-swap providers using `/model [mock|ollama|groq|gemini]`."
            )

        # General response
        past_turn_count = len([m for m in context_messages if m["role"] != "system"])
        return (
            f"I have received your message: '{user_input}'.\n\n"
            f"ℹ️ *(Volume 4 Thread Context: {past_turn_count} messages retained in FileHistoryProvider)*"
        )

    def _call_ollama(self, context_messages: List[Dict[str, str]]) -> str:
        """Sends request to local Ollama server."""
        url = f"{self.config.ollama_base_url}/api/chat"
        payload = {
            "model": self.config.ollama_model,
            "messages": context_messages,
            "stream": False
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "No content returned.")

    def _call_groq(self, context_messages: List[Dict[str, str]]) -> str:
        """Sends request to Groq API."""
        if not self.config.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing in .env file.")
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": context_messages
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.groq_api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    def _call_gemini(self, context_messages: List[Dict[str, str]]) -> str:
        """Sends request to Gemini REST API."""
        if not self.config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing in .env file.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.config.gemini_api_key}"
        contents = []
        for m in context_messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {"contents": contents}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
