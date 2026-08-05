# 🔬 Benchmarking Methodology

## Overview
This document defines the scientific evaluation methodology used by the **Groq vs Ollama Provider Swap System**.

---

## 1. Evaluation Dimensions

### 1.1 Latency & Speed Metrics
- **Time to First Token (TTFT):** Measures responsiveness of the API / model backend.
- **End-to-End Latency (s):** Total elapsed time from prompt request dispatch to final token receipt.
- **Tokens Per Second (TPS):** Throughput calculation ($\text{TPS} = \frac{\text{Output Tokens}}{\text{Elapsed Time}}$).

### 1.2 Quality & Accuracy Metrics
- **Instruction Following:** Did the model follow constraints (e.g. JSON output format, word limits, code block structure)?
- **Completeness Score (1-10):** Evaluates if the generated response answered all parts of complex multi-step prompts.
- **Error Rate (%):** Percentage of queries resulting in timeouts, network failures, or malformed outputs.

### 1.3 Cost & Efficiency
- **Cloud API Cost:** Calculated based on Groq pricing tiers ($0 on free tier).
- **Local Compute Overhead:** RAM/VRAM footprint and thermal stability during Ollama runs.

---

## 2. Benchmark Categories & Prompt Datasets

| Category | Description | Key Focus |
|---|---|---|
| **General QA** | Knowledge retrieval & succinct explanations | Accuracy & concise delivery |
| **Coding** | Python algorithm design & refactoring | Syntax validity & logic correctness |
| **Reasoning & Logic** | Multi-step mathematical & logical puzzles | Step-by-step thinking |
| **Summarization** | Compressing long context passages | Key point retention |
| **Tool Calling** | Structured JSON function calling | Schema adherence |
| **Translation** | Multi-language translation tasks | Nuance & fidelity |

---

## 3. Experimental Controls
To ensure unbiased comparisons:
1. **Identical System Prompts:** Both backends receive the exact same system instructions (`ChatAgent.system_instruction`).
2. **Fixed Parameters:**
   - `temperature = 0.2` (Deterministic evaluation).
   - `max_tokens = 1024`.
3. **Warm-Up Runs:** Initial 1 dummy request sent to Ollama to eliminate cold-start model loading latency skew from measurements.
4. **Repeated Samples:** Each prompt is evaluated across multiple runs to calculate statistical mean and standard deviation for latency.
