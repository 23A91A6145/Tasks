import time
from typing import List, Dict, Any, Tuple
from app.providers import BaseProviderClient
from app.utils import get_logger, get_ram_usage

logger = get_logger("agent")

class ChatAgent:
    def __init__(self, client: BaseProviderClient, instructions: str = "You are a helpful, professional AI assistant.") -> None:
        """
        Initializes the ChatAgent with a ChatClient (ProviderClient) and system instructions.
        """
        self.client = client
        self.instructions = instructions
        self.memory: List[Dict[str, str]] = []
        self._reset_memory()

    def _reset_memory(self) -> None:
        """Resets agent conversation context to include the system instruction."""
        self.memory = [{"role": "system", "content": self.instructions}]

    def run(self, prompt: str, stream: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Executes a single prompt through the configured ChatClient.
        Measures exact TTFT, Latency, and Throughput (TPS).
        """
        # Append user prompt to memory
        self.memory.append({"role": "user", "content": prompt})
        
        # Setup logging
        logger.info(f"Agent executing prompt with client '{self.client.__class__.__name__}' (Model: '{self.client.model_id}')")
        
        ram_before = get_ram_usage()
        response_text = ""
        ttft = 0.0
        start_time = time.perf_counter()
        
        input_tokens = 0
        output_tokens = 0
        
        try:
            # We call the provider client with automatic retries for transient errors
            retries = 3
            backoff = 1.5
            raw_response = None
            
            for attempt in range(1, retries + 1):
                try:
                    raw_response = self.client.generate_response(
                        messages=self.memory,
                        stream=stream
                    )
                    break
                except Exception as e:
                    if attempt == retries:
                        raise
                    logger.warning(f"Connection/API error (Attempt {attempt}/{retries}): {e}. Retrying in {backoff * attempt}s...")
                    time.sleep(backoff * attempt)
            
            if stream:
                first_token_received = False
                
                # Check provider client type to parse chunks appropriately
                if self.client.__class__.__name__ == "GroqProviderClient":
                    for chunk in raw_response:
                        if not first_token_received:
                            ttft = time.perf_counter() - start_time
                            first_token_received = True
                            
                        # Groq stream chunks
                        if chunk.choices and len(chunk.choices) > 0:
                            delta_content = chunk.choices[0].delta.content or ""
                            response_text += delta_content
                            
                        # If chunk has usage metadata
                        if hasattr(chunk, "usage") and chunk.usage:
                            input_tokens = chunk.usage.prompt_tokens
                            output_tokens = chunk.usage.completion_tokens
                            
                elif self.client.__class__.__name__ == "OllamaProviderClient":
                    for chunk in raw_response:
                        if not first_token_received:
                            ttft = time.perf_counter() - start_time
                            first_token_received = True
                            
                        delta_content = chunk.get("message", {}).get("content", "")
                        response_text += delta_content
                        
                        # Ollama includes final token counts on last chunk
                        if chunk.get("done", False):
                            input_tokens = chunk.get("prompt_eval_count", 0)
                            output_tokens = chunk.get("eval_count", 0)
                            
                elif self.client.__class__.__name__ == "MockProviderClient":
                    for chunk in raw_response:
                        if not first_token_received:
                            ttft = time.perf_counter() - start_time
                            first_token_received = True
                            
                        delta = chunk["choices"][0]["delta"]
                        if isinstance(delta, dict):
                            delta_content = delta.get("content", "") or ""
                        else:
                            delta_content = getattr(delta, "content", "") or ""
                        response_text += delta_content
                        
                        # Mock completion usage
                        usage = chunk.get("usage") if isinstance(chunk, dict) else getattr(chunk, "usage", None)
                        if usage:
                            if isinstance(usage, dict):
                                input_tokens = usage.get("prompt_tokens", 0)
                                output_tokens = usage.get("completion_tokens", 0)
                            else:
                                input_tokens = getattr(usage, "prompt_tokens", 0)
                                output_tokens = getattr(usage, "completion_tokens", 0)
                else:
                    # Generic streaming parsing fallback
                    for chunk in raw_response:
                        if not first_token_received:
                            ttft = time.perf_counter() - start_time
                            first_token_received = True
                        if isinstance(chunk, dict):
                            delta_content = chunk.get("content", "")
                            response_text += delta_content
                        else:
                            response_text += str(chunk)
            else:
                # Non-streaming call
                end_call_time = time.perf_counter()
                ttft = end_call_time - start_time  # TTFT equals latency in non-streaming
                
                if self.client.__class__.__name__ == "GroqProviderClient":
                    response_text = raw_response.choices[0].message.content or ""
                    if hasattr(raw_response, "usage") and raw_response.usage:
                        input_tokens = raw_response.usage.prompt_tokens
                        output_tokens = raw_response.usage.completion_tokens
                        
                elif self.client.__class__.__name__ == "OllamaProviderClient":
                    response_text = raw_response.get("message", {}).get("content", "")
                    input_tokens = raw_response.get("prompt_eval_count", 0)
                    output_tokens = raw_response.get("eval_count", 0)
                    
                elif self.client.__class__.__name__ == "MockProviderClient":
                    response_text = raw_response["choices"][0]["message"]["content"] or ""
                    input_tokens = raw_response["usage"]["prompt_tokens"]
                    output_tokens = raw_response["usage"]["completion_tokens"]
                else:
                    response_text = str(raw_response)
            
            end_time = time.perf_counter()
            total_latency = end_time - start_time
            
            # Estimator fallback if token counts are zero
            if input_tokens == 0:
                # Average English word is ~1.3 tokens
                input_tokens = int(len(prompt.split()) * 1.3)
            if output_tokens == 0:
                output_tokens = int(len(response_text.split()) * 1.3)
                
            tps = output_tokens / total_latency if total_latency > 0 else 0.0
            
            # Append response to memory for potential multi-turn persistence
            self.memory.append({"role": "assistant", "content": response_text})
            
            ram_after = get_ram_usage()
            ram_delta = max(0.0, round(ram_after - ram_before, 3))
            
            metrics = {
                "latency": total_latency,
                "ttft": ttft,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tps": tps,
                "response_text": response_text,
                "error": None,
                "ram_used_gb": ram_after,
                "ram_delta_gb": ram_delta
            }
            logger.info(f"Agent finished run successfully. Latency: {total_latency:.2f}s, TPS: {tps:.2f}, RAM Used: {ram_after} GB (Delta: {ram_delta} GB)")
            return response_text, metrics
            
        except Exception as e:
            end_time = time.perf_counter()
            total_latency = end_time - start_time
            ram_after = get_ram_usage()
            logger.error(f"Agent failed execution: {e}")
            metrics = {
                "latency": total_latency,
                "ttft": 0.0,
                "input_tokens": int(len(prompt.split()) * 1.3),
                "output_tokens": 0,
                "tps": 0.0,
                "response_text": "",
                "error": str(e),
                "ram_used_gb": ram_after,
                "ram_delta_gb": 0.0
            }
            return "", metrics
