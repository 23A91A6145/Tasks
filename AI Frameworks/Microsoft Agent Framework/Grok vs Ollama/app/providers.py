import time
import json
import random
from typing import List, Dict, Any, Generator, Tuple
import httpx
from groq import Groq
from app.config import Config
from app.utils import get_logger, console

logger = get_logger("providers")

class BaseProviderClient:
    def __init__(self, model_id: str):
        self.model_id = model_id

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Any:
        """
        Generate a response from the provider.
        If stream=True, returns a generator of chunks.
        """
        raise NotImplementedError("Subclasses must implement generate_response")

    def check_health(self) -> bool:
        """Verify provider connection and model availability."""
        raise NotImplementedError("Subclasses must implement check_health")


class GroqProviderClient(BaseProviderClient):
    def __init__(self, model_id: str = None, api_key: str = None):
        model = model_id or Config.GROQ_DEFAULT_MODEL
        super().__init__(model)
        self.api_key = api_key or Config.GROQ_API_KEY
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Any:
        if not self.client:
            raise ValueError("Groq API key is not set. Please configure GROQ_API_KEY in your .env file.")
        
        try:
            # We request token usage in stream using stream_options if supported
            stream_options = {"include_usage": True} if stream else None
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                stream_options=stream_options
            )
            return response
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise

    def check_health(self) -> bool:
        if not self.api_key:
            logger.warning("Groq API Key is missing in configuration.")
            return False
        try:
            if not self.client:
                self.client = Groq(api_key=self.api_key)
            # Fast ping completion
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "ping"}],
                model=self.model_id,
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.warning(f"Groq health check failed for model '{self.model_id}': {e}")
            return False


class OllamaProviderClient(BaseProviderClient):
    def __init__(self, model_id: str = None, host: str = None):
        model = model_id or Config.OLLAMA_DEFAULT_MODEL
        super().__init__(model)
        self.host = host or Config.OLLAMA_HOST
        if not self.host.startswith("http"):
            self.host = f"http://{self.host}"
        
        # Using a timeout configuration that matches the global benchmark timeout
        self.client = httpx.Client(base_url=self.host, timeout=httpx.Timeout(float(Config.BENCHMARK_TIMEOUT)))

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Any:
        payload = {
            "model": self.model_id,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }
        
        try:
            if stream:
                def stream_generator():
                    with self.client.stream("POST", "/api/chat", json=payload) as r:
                        r.raise_for_status()
                        for line in r.iter_lines():
                            if line:
                                yield json.loads(line)
                return stream_generator()
            else:
                response = self.client.post("/api/chat", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def check_health(self) -> bool:
        try:
            # Check connection to Ollama daemon
            response = self.client.get("/")
            if response.status_code != 200:
                logger.warning(f"Ollama health check failed: daemon returned status {response.status_code}")
                return False
                
            # Verify if the requested model is pulled
            tags_resp = self.client.get("/api/tags")
            if tags_resp.status_code == 200:
                models = tags_resp.json().get("models", [])
                pulled_models = [m["name"] for m in models]
                
                # Check for exact name match
                if self.model_id in pulled_models:
                    return True
                
                # Auto-switch to similar model if available
                short_model = self.model_id.split(":")[0]
                for pm in pulled_models:
                    if pm.startswith(short_model + ":") or pm == short_model:
                        console.print(f"[yellow]⚠️ Ollama model '{self.model_id}' is not pulled, but similar model '{pm}' is available. Auto-switching model to '{pm}' for benchmarking.[/yellow]")
                        self.model_id = pm
                        return True
                        
                console.print(f"[red]❌ Ollama model '{self.model_id}' is not pulled. Available: {pulled_models}[/red]")
                logger.warning(f"Ollama model '{self.model_id}' is not pulled. Available: {pulled_models}")
                return False
            else:
                logger.warning(f"Ollama /api/tags returned status {tags_resp.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Ollama health check connection refused: {e}")
            return False


class MockProviderClient(BaseProviderClient):
    def __init__(self, model_id: str = "mock-lpu-1b"):
        super().__init__(model_id)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Any:
        prompt = messages[-1]["content"] if messages else ""
        lower_prompt = prompt.lower()
        
        # Predefined mock replies based on category indicators
        if "code" in lower_prompt or "python" in lower_prompt or "def " in lower_prompt:
            reply = (
                "```python\n"
                "def calculate_stats(numbers):\n"
                "    \"\"\"Calculate basic statistical metrics for a list of numbers.\"\"\"\n"
                "    if not numbers:\n"
                "        return {\"mean\": 0, \"median\": 0, \"variance\": 0}\n"
                "    n = len(numbers)\n"
                "    mean = sum(numbers) / n\n"
                "    sorted_nums = sorted(numbers)\n"
                "    median = sorted_nums[n // 2] if n % 2 != 0 else (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2\n"
                "    variance = sum((x - mean) ** 2 for x in numbers) / n\n"
                "    return {\"mean\": mean, \"median\": median, \"variance\": variance}\n"
                "```"
            )
        elif "puzzle" in lower_prompt or "logic" in lower_prompt or "reason" in lower_prompt:
            reply = (
                "Step-by-Step Analytical Reasoning:\n"
                "1. Identify the entities: Three boxes (Red, Green, Blue) containing different items (Gold, Silver, Bronze).\n"
                "2. Analyze statements: The Red box does not have Silver. The Gold is in the Blue box.\n"
                "3. Deducing placement:\n"
                "   - Blue Box = Gold (given).\n"
                "   - Red Box = Cannot be Silver, and cannot be Gold (already in Blue). Therefore, Red Box = Bronze.\n"
                "   - Green Box = Remaining metal, which is Silver.\n"
                "4. Conclusion: Red contains Bronze, Green contains Silver, and Blue contains Gold."
            )
        elif "summarize" in lower_prompt or "summary" in lower_prompt:
            reply = (
                "Executive Summary:\n"
                "- Decoupled AI architecture ensures model and provider independence.\n"
                "- Cloud APIs (like Groq) provide ultra-low latency LPU hardware acceleration.\n"
                "- Local backends (like Ollama) run locally, offering 100% cost-savings and data privacy.\n"
                "- Swapping backends via a clean ChatClient abstraction facilitates zero-bias statistical profiling."
            )
        elif "translate" in lower_prompt:
            reply = (
                "French Translation:\n"
                "Le Microsoft Agent Framework facilite l'interopérabilité des modèles. "
                "En changeant uniquement le client de chat, le même agent s'exécute de manière identique "
                "sur Groq et Ollama."
            )
        elif "tool" in lower_prompt or "get_weather" in lower_prompt:
            reply = (
                "{\n"
                "  \"tool_call\": \"get_weather\",\n"
                "  \"arguments\": {\n"
                "    \"location\": \"Paris, France\",\n"
                "    \"unit\": \"celsius\"\n"
                "  }\n"
                "}"
            )
        else:
            reply = (
                f"This is a simulated response from MockProviderClient for model '{self.model_id}'. "
                f"The framework has successfully verified the prompt structure and simulated inference. "
                f"Your configurations: temperature={temperature}, max_tokens={max_tokens}."
            )

        sim_latency = random.uniform(0.15, 0.45)
        
        if stream:
            def mock_stream():
                # Split content into smaller chunks to simulate token stream
                chunks = [reply[i:i+8] for i in range(0, len(reply), 8)]
                time.sleep(sim_latency * 0.4)  # Simulate TTFT
                for idx, chunk in enumerate(chunks):
                    time.sleep(0.01)  # Simulate token generation throughput
                    yield {
                        "choices": [{
                            "delta": {
                                "content": chunk
                            }
                        }],
                        "usage": {
                            "prompt_tokens": len(prompt.split()) + 5,
                            "completion_tokens": len(reply.split()) + 5
                        } if idx == len(chunks) - 1 else None
                    }
            return mock_stream()
        else:
            time.sleep(sim_latency)
            return {
                "choices": [{
                    "message": {
                        "content": reply
                    }
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()) + 5,
                    "completion_tokens": len(reply.split()) + 5
                }
            }

    def check_health(self) -> bool:
        return True
