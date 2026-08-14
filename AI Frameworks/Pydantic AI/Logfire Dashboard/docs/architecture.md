# AgentEval Lab — Complete System Architecture (Volumes 1–5)

## End-to-End Enterprise AI Evaluation Architecture

```mermaid
graph TD
    subgraph Developer & CI Interface
        Dev([Developer / Engineer]) --> WebUI[Web UI Interactive Dashboard - Port 8000]
        Dev --> CLI[CLI Runner / Matrix / Slicing Engine]
        PR[GitHub Actions CI/CD] --> CIGate[CI Quality Gate Runner]
    end

    subgraph FastAPI Service Layer
        WebUI --> API[FastAPI REST API Service]
        API --> Routes[Endpoints: /datasets, /evals, /experiments, /compare, /feedback]
    end

    subgraph Agent & OpenTelemetry Tracing
        CLI --> Harness[Multi-Rubric Evaluation Harness]
        Routes --> Harness
        CIGate --> Harness
        Harness --> Agent[Pydantic AI Customer Support Agent]
        Agent --> Tools[Support Tools: Orders, Customers, Refunds, FAQs]
        Agent --> OTEL[Logfire & OpenTelemetry Span Hierarchy]
    end

    subgraph Multi-Rubric & Behavioral Evaluators
        Harness --> Det[Deterministic Keyword & Latency Checks]
        Harness --> Beh[Behavioral & Argument Accuracy Validator]
        Harness --> Judge[Multi-Rubric LLM-as-a-Judge]
        Harness --> Cost[Cost & Token Efficiency Optimizer]
    end

    subgraph Regression & Production Feedback
        Harness --> RegEngine[Multi-Dimensional Regression Engine]
        RegEngine --> Reports[(JSON, Markdown & Trace Reports)]
        Prod[Live Production Telemetry] --> Ingestion[Production Feedback Loop]
        Ingestion --> GoldenDB[(Golden Test Datasets)]
        GoldenDB --> Harness
    end
```

---

## 5-Volume Engineering Framework Summary

| Volume | Focus Domain | Key Capabilities |
| :--- | :--- | :--- |
| **Volume 1** | Evaluation Foundations | Local test harness, Pydantic AI Support Agent, deterministic evaluators, initial quality gate CLI. |
| **Volume 2** | Evaluation Intelligence | 28 curated cases, multi-rubric LLM judge (Accuracy, Relevance, Policy, Tone), hybrid scoring, metadata slicing. |
| **Volume 3** | Observability & Dashboard | Logfire OpenTelemetry span trees, terminal dashboard, ASCII quality trends, side-by-side comparison, trace debugger. |
| **Volume 4** | Regression Engine & QA | 5-dimensional regression detection (zero-tolerance safety), automated CI/CD PR gate, behavioral evaluators, incident ingestion. |
| **Volume 5** | Expert Production Platform | FastAPI REST service, Interactive Web UI SPA, Model $\times$ Prompt Matrix Runner, token & cost optimizer. |
