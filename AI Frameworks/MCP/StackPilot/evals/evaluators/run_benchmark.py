import sys
import os
import uuid

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.app.agents.graph import build_migration_graph
from backend.app.models.task import RiskLevel

SCENARIOS = [
    {
        "id": "SCENARIO_01_NODE_POSTGRES",
        "name": "Monolithic Express + Postgres to Microservices",
        "goal": "Migrate monolithic Node.js + PostgreSQL to modular services with strict security",
        "constraints": {"budget_yearly_inr": 500000.0, "primary_focus": "security"},
        "expected_strategy": "Strangler Fig Pattern",
        "expected_replans": 1
    },
    {
        "id": "SCENARIO_02_COST_OPTIMIZED",
        "name": "High-Budget Cloud Cost Optimization",
        "goal": "Migrate legacy workload while minimizing annual cloud expenses under ₹2 Lakhs",
        "constraints": {"budget_yearly_inr": 200000.0, "primary_focus": "cost"},
        "expected_strategy": "Strangler Fig Pattern",
        "expected_replans": 0
    },
    {
        "id": "SCENARIO_03_VELOCITY_FAST",
        "name": "Fastest Migration Timeline",
        "goal": "Migrate monolithic application to cloud containers in shortest possible schedule",
        "constraints": {"budget_yearly_inr": 800000.0, "primary_focus": "velocity"},
        "expected_strategy": "Strangler Fig Pattern",
        "expected_replans": 0
    }
]

def evaluate_scenario(scenario):
    graph = build_migration_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = {
        "run_id": f"eval_{scenario['id']}",
        "thread_id": thread_id,
        "project_id": "eval_proj",
        "user_goal": scenario["goal"],
        "constraints": scenario["constraints"],
        "project_context": {"repo_path": "./samples/legacy-monolith"},
        "plan": [],
        "current_task_idx": 0,
        "current_task": None,
        "completed_tasks": [],
        "failed_tasks": [],
        "evidence": [],
        "findings": [],
        "critique": None,
        "replans": 0,
        "risk_level": "LOW",
        "approval_required": False,
        "pending_approval_id": None,
        "approval_decision": None,
        "final_recommendation": None,
        "error_message": None
    }

    # Step 1: Run until interrupt or completion
    list(graph.stream(state, config=config))
    curr = graph.get_state(config).values

    # Step 2: Handle HITL if paused
    if curr.get("approval_required"):
        graph.update_state(config, {"approval_decision": "APPROVED", "approval_required": False})
        list(graph.stream(None, config=config))
        curr = graph.get_state(config).values

    rec = curr.get("final_recommendation", {})
    strategy = rec.get("recommended_strategy", "")
    confidence = rec.get("confidence_score", 0.0)
    replans = curr.get("replans", 0)

    # Score scenario
    plan_validity = 1.0 if len(curr.get("completed_tasks", [])) >= 4 else 0.0
    evidence_grounding = 1.0 if len(curr.get("evidence", [])) >= 4 else 0.0
    strategy_match = 1.0 if scenario["expected_strategy"] in strategy else 0.0
    score = (plan_validity * 0.3) + (evidence_grounding * 0.3) + (strategy_match * 0.4)

    return {
        "scenario_id": scenario["id"],
        "name": scenario["name"],
        "score": score * 100,
        "confidence": confidence * 100,
        "replans": replans,
        "tasks_completed": len(curr.get("completed_tasks", [])),
        "status": "PASSED" if score >= 0.8 else "FAILED"
    }

def main():
    print("=" * 70)
    print(" 🧪 STACKPILOT AGENT BENCHMARK EVALUATION HARNESS")
    print("=" * 70)
    
    results = []
    for sc in SCENARIOS:
        print(f"Running scenario: {sc['name']}...")
        r = evaluate_scenario(sc)
        results.append(r)
        print(f"  -> Score: {r['score']:.1f}% | Confidence: {r['confidence']:.1f}% | Replans: {r['replans']} | Status: {r['status']}")

    avg_score = sum(r["score"] for r in results) / len(results)
    print("-" * 70)
    print(f"BENCHMARK COMPLETED: Mean Quality Score = {avg_score:.1f}% across {len(results)} scenarios")
    print("=" * 70)

if __name__ == "__main__":
    main()
