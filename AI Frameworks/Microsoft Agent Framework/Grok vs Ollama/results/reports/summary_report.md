# 🏆 AI Provider Swap Benchmarking Scorecard Report

**Generated At:** 2026-08-05 15:49:53

This report outlines the latency, quality, throughput, and cost analysis of executing identical AI Agent personas across Groq, Ollama, and Mock providers using the Microsoft Agent Framework abstraction.

## 🏆 Provider Awards & Rankings

- **🏆 Fastest Response (Avg Latency):** Groq (llama-3.3-70b-versatile) - **4.532s**
- **⚡ Highest Throughput (Avg TPS):** Ollama (llama3.2:3b) - **10.5 tokens/s**
- **🎯 Best Response Quality (Avg Score):** Ollama (llama3.2:3b) - **9.7/10**
- **💰 Lowest Operation Cost (Total Run):** Ollama (llama3.2:3b) - **$0.000000**

## 📊 Provider Benchmark Metrics Table

| Provider | Model | Runs | Latency (Avg/Min/Max) | TTFT (Avg) | Throughput (Avg TPS) | Quality Score (Avg) | RAM Avg/Peak | Success Rate | Total Cost |
|---|---|---|---|---|---|---|---|---|---|
| **Groq** | llama-3.3-70b-versatile | 6 | 4.53s / 4.52s / 4.54s | 0.00s | 0.0 tps | 1.0/10 | 5.32 GB / 5.32 GB | 0.0% | $0.000130 |
| **Ollama** | llama3.2:3b | 6 | 16.60s / 7.52s / 27.90s | 1.24s | 10.5 tps | 9.7/10 | 7.80 GB / 7.86 GB | 100.0% | $0.00 (Local/Free) |

## 🔍 Category-Specific Quality Scores

| Category | Provider | Model | Quality Score | Latency | TPS |
|---|---|---|---|---|---|
| Coding | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.54s | 0.0 |
| Coding | **Ollama** | llama3.2:3b | 10.0/10 | 27.90s | 11.1 |
| General QA | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.54s | 0.0 |
| General QA | **Ollama** | llama3.2:3b | 10.0/10 | 19.63s | 13.2 |
| Reasoning | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.54s | 0.0 |
| Reasoning | **Ollama** | llama3.2:3b | 8.0/10 | 18.23s | 10.6 |
| Summarization | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.53s | 0.0 |
| Summarization | **Ollama** | llama3.2:3b | 10.0/10 | 8.39s | 8.1 |
| Tool Calling | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.53s | 0.0 |
| Tool Calling | **Ollama** | llama3.2:3b | 10.0/10 | 7.52s | 10.0 |
| Translation | **Groq** | llama-3.3-70b-versatile | 1.0/10 | 4.52s | 0.0 |
| Translation | **Ollama** | llama3.2:3b | 10.0/10 | 17.92s | 10.0 |

## 📂 Generated Assets
- Latency Comparison: `results/charts/latency_comparison.png`
- Throughput Comparison: `results/charts/tps_comparison.png`
- Quality Comparison: `results/charts/quality_comparison.png`

---

*Note: Quality evaluation utilizes automated AST-based python parser checks and regex heuristic checks to verify syntax validity, step-by-step reasoning tokens, and structured JSON completeness constraints.*