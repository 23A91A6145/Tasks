# 🏛 Architecture Specification: Provider Swap Benchmarking System

## Overview
The **Microsoft Agent Framework Provider Swap Benchmarking System** is designed to evaluate multiple LLM inference providers while holding the agent definition, prompt instructions, and tool capabilities strictly constant.

---

## 1. Core Architectural Principles

### 1.1 Provider Abstraction Layer
The core principle of this architecture is **Backend Decoupling**. The agent operational logic never depends directly on a vendor SDK (such as `groq` or `ollama` client directly inside agent handlers). Instead:
- `BaseProviderClient` defines an interface `generate_response(messages, temperature, max_tokens)`.
- `GroqProviderClient` wraps Groq API or OpenAI-compatible Groq endpoints.
- `OllamaProviderClient` wraps local Ollama REST endpoints (`http://localhost:11434`).
- `MockProviderClient` provides zero-network testing for offline laptop verification.

### 1.2 ChatAgent Abstraction
The `ChatAgent` class encapsulates:
- System persona & role instructions.
- Conversation context memory.
- Execution loop and response extraction.

By passing a swapped `ChatClient` instance to `ChatAgent(client=provider_client)`, the identical agent persona runs across backends cleanly.

---

## 2. Component Diagram

```
                     +---------------------------+
                     |    main.py (CLI / UI)     |
                     +-------------+-------------+
                                   |
                                   v
                     +---------------------------+
                     |    BenchmarkController    |
                     +-------------+-------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+------------------------+                          +------------------------+
|   GroqProviderClient   |                          |  OllamaProviderClient  |
+-----------+------------+                          +-----------+------------+
            |                                                   |
            +-------------------------+-------------------------+
                                      |
                                      v
                           +--------------------+
                           |     ChatAgent      |
                           +---------+----------+
                                     |
                                     v
                           +--------------------+
                           |  MetricsCollector  |
                           +---------+----------+
                                     |
                                     v
                           +--------------------+
                           | Evaluator & Report |
                           +--------------------+
```

---

## 3. Data Flow & Telemetry Collection
For every prompt execution:
1. **Timestamp Init:** High-resolution start time (`time.perf_counter()`).
2. **First Token Time (TTFT):** Measures time until the initial response chunk arrives (if streaming).
3. **Total Latency:** End-to-end elapsed time in seconds.
4. **Token Metrics:**
   - Input Prompt Tokens.
   - Output Response Tokens.
   - Tokens Per Second (TPS = Output Tokens / Latency).
5. **Quality Scoring:** Rule-based and semantic criteria checking output formatting, response completeness, and accuracy.
6. **Persistence:** Written to `results/benchmark.csv` and `results/benchmark.json`.

---

## 4. Laptop-Optimized Execution Rules
- **Memory Efficiency:** Avoid heavy concurrent parallel threads when querying local Ollama models on consumer laptops. Ollama is throttled to sequential or controlled worker pools (max 1-2 concurrent tasks) to avoid CPU/GPU thermal throttling or RAM overflow.
- **Graceful Fallbacks:** If Ollama service is not active locally, the system detects connection refusers immediately and reports clear diagnostic steps without crashing.
- **Zero-Cost Operation:** Groq free tier API + Ollama local execution ensure zero monetary cost for running full benchmarks.
