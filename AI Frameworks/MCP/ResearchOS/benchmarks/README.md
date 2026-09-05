# ResearchOS Benchmark Suite: DeepResearchBench

This directory contains evaluation benchmarks inspired by **DeepResearchBench**, **BrowseComp**, and **Ragas** to measure the rigor, factual accuracy, and citation validity of autonomous research agents.

## Evaluation Dataset Structure (`DeepResearchBench.jsonl`)
Each test item specifies:
- `query`: The complex technical or architectural prompt.
- `expected_domains`: Authoritative primary domains that must be discovered (e.g., `arxiv.org`, `crewai.com`, `langchain.com`).
- `minimum_citations`: Floor for verified inline citations in the synthesized report.
- `required_aspects`: Key technical facets that the Critic and Evaluator verify for complete coverage.

## Running Evaluation
You can execute automated evaluation directly via the API:
```bash
curl -X POST http://localhost:8000/api/v1/research/{run_id}/evaluate
```
Returns a multi-metric scorecard:
- **Faithfulness Score**: Cosine grounding between atomic claims and cited passages.
- **Citation Validity Score**: HTTP reachability and passage existence index.
- **Context Precision Score**: Relevance of retrieved source candidates.
- **Hallucination Index**: Quantitative measure of unsupported assertions.
