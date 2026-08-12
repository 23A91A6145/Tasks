# app/eval.py

import json
import time
import os
from pydantic_ai.models.test import TestModel
from app.agent import agent, classify_ticket_content, fallback_classify
from app.models import TicketResult, TicketCategory, TicketPriority, SuggestedAgent

def run_evaluation(mode: str = "fallback"):
    """
    Runs classification evaluation against the benchmark dataset in data/sample_tickets.json.
    Supports modes:
    - 'fallback': runs the local heuristic rule classifier (fast, CPU friendly)
    - 'test': runs the agent mocked with TestModel
    - 'llm': runs the actual configured LLM models (requires local Ollama or API keys)
    """
    print(f"Starting Structured Ticket Classifier benchmark evaluation in '{mode}' mode...")
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_tickets.json")
    with open(data_path, "r") as f:
        tickets = json.load(f)
        
    total = len(tickets)
    correct_category = 0
    correct_priority = 0
    correct_agent = 0
    total_confidence = 0.0
    total_latency_ms = 0
    human_reviews = 0
    failures = 0
    
    results_log = []
    
    # Setup override if mock mode
    override_context = None
    if mode == "test":
        override_context = agent.override(model=TestModel())
        override_context.__enter__()
        
    try:
        for idx, item in enumerate(tickets):
            msg = item["message"]
            expected_cat = item["expected_category"]
            expected_pri = item["expected_priority"]
            expected_agt = item["expected_agent"]
            
            start = time.perf_counter()
            
            # Execute classification based on selected mode
            if mode == "fallback":
                result = fallback_classify(msg)
                latency_ms = int((time.perf_counter() - start) * 1000)
            else:
                # 'test' and 'llm' run the actual function (which will be overridden in test mode)
                try:
                    result, latency_ms = classify_ticket_content(msg)
                except Exception as e:
                    print(f"Classification failed on ticket {idx+1}: {e}")
                    failures += 1
                    continue
                    
            total_latency_ms += latency_ms
            total_confidence += result.confidence
            if result.requires_human_review:
                human_reviews += 1
                
            # Check correctness
            cat_match = result.category.value == expected_cat
            pri_match = result.priority.value == expected_pri
            agt_match = result.suggested_agent.value == expected_agt
            
            if cat_match: correct_category += 1
            if pri_match: correct_priority += 1
            if agt_match: correct_agent += 1
            
            results_log.append({
                "id": item["id"],
                "message": msg[:60] + "...",
                "expected": f"{expected_cat}/{expected_pri}/{expected_agt}",
                "predicted": f"{result.category.value}/{result.priority.value}/{result.suggested_agent.value}",
                "confidence": result.confidence,
                "latency_ms": latency_ms,
                "human_review": "YES" if result.requires_human_review else "NO"
            })
    finally:
        if override_context:
            override_context.__exit__(None, None, None)
            
    # Calculate statistics
    valid_runs = total - failures
    if valid_runs == 0:
        print("Error: No valid runs completed.")
        return
        
    cat_acc = round(correct_category / valid_runs, 4)
    pri_acc = round(correct_priority / valid_runs, 4)
    agt_acc = round(correct_agent / valid_runs, 4)
    avg_conf = round(total_confidence / valid_runs, 4)
    avg_latency = round(total_latency_ms / valid_runs, 2)
    human_review_rate = round(human_reviews / valid_runs, 4)
    
    # Generate markdown report
    report = []
    report.append("# Structured Ticket Classifier — Evaluation Report")
    report.append(f"\n* **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"* **Execution Mode**: `{mode}`")
    report.append(f"* **Total Test cases**: {total}")
    report.append(f"* **Successful runs**: {valid_runs}")
    report.append(f"* **Failures**: {failures}")
    report.append("\n## Aggregate Metrics")
    report.append("| Metric | Value | Details |")
    report.append("| :--- | :--- | :--- |")
    report.append(f"| **Category Accuracy** | {cat_acc*100:.1f}% | {correct_category}/{valid_runs} matching labels |")
    report.append(f"| **Priority Accuracy** | {pri_acc*100:.1f}% | {correct_priority}/{valid_runs} matching labels |")
    report.append(f"| **Routing Agent Accuracy** | {agt_acc*100:.1f}% | {correct_agent}/{valid_runs} matching channels |")
    report.append(f"| **Average Confidence** | {avg_conf*100:.1f}% | Calculated model probability score |")
    report.append(f"| **Human Review Rate** | {human_review_rate*100:.1f}% | Cases flagged for manual oversight |")
    report.append(f"| **Average Latency** | {avg_latency} ms | Average classification time |")
    
    report.append("\n## Detailed Execution Logs")
    report.append("| ID | Support Message Snippet | Expected (Cat/Pri/Agt) | Predicted (Cat/Pri/Agt) | Conf. | Latency | Review |")
    report.append("| :-: | :--- | :--- | :--- | :-: | :-: | :-: |")
    for r in results_log:
        report.append(f"| {r['id']} | {r['message']} | {r['expected']} | {r['predicted']} | {r['confidence']*100:.0f}% | {r['latency_ms']}ms | {r['human_review']} |")
        
    markdown_report = "\n".join(report)
    
    # Write to local file
    report_path = os.path.join(os.path.dirname(__file__), "..", "evaluation_results.md")
    with open(report_path, "w") as f:
        f.write(markdown_report)
        
    print(f"\nEvaluation complete! Report written to: {os.path.abspath(report_path)}")
    print(f"Summary: Category Acc={cat_acc*100:.1f}%, Priority Acc={pri_acc*100:.1f}%, Avg Latency={avg_latency}ms")
    
if __name__ == "__main__":
    import sys
    mode = "fallback"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    run_evaluation(mode)
