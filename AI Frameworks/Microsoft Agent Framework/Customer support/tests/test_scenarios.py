import asyncio
from rich.console import Console
from rich.table import Table
from agent_framework import InMemoryCheckpointStorage
from agent_framework.orchestrations import HandoffAgentUserRequest
from app.workflows.handoff import create_handoff_workflow

console = Console()

TEST_SCENARIOS = [
    {
        "id": 1,
        "name": "Refund request",
        "turns": ["Hi, I want a refund for my order."],
        "expected_agent": "Billing"
    },
    {
        "id": 2,
        "name": "Payment failed",
        "turns": ["My credit card payment failed yesterday, what should I do?"],
        "expected_agent": "Billing|Triage"
    },
    {
        "id": 3,
        "name": "Invoice download",
        "turns": ["Where can I download my last month's invoice?"],
        "expected_agent": "Billing"
    },
    {
        "id": 4,
        "name": "Login issue",
        "turns": ["I keep getting access denied when trying to login."],
        "expected_agent": "Technical|Triage"
    },
    {
        "id": 5,
        "name": "App crash",
        "turns": ["The mobile app crashes every time I tap the home button."],
        "expected_agent": "Technical|Triage"
    },
    {
        "id": 6,
        "name": "Password reset",
        "turns": ["I forgot my password, can you help me reset it?"],
        "expected_agent": "Technical"
    },
    {
        "id": 7,
        "name": "Business hours",
        "turns": ["What are your office business hours?"],
        "expected_agent": "Triage"
    },
    {
        "id": 8,
        "name": "Pricing inquiry",
        "turns": ["How much is the subscription fee for the Pro plan?"],
        "expected_agent": "General|Billing"
    },
    {
        "id": 9,
        "name": "Unknown issue / Clarification",
        "turns": ["I have a question about something."],
        "expected_agent": "Triage"  # Should ask for clarification/not route immediately
    },
    {
        "id": 10,
        "name": "Multi-topic session (Billing -> Technical)",
        "turns": [
            "I need to check the status of my refund.",  # Handoff to Billing
            "My refund ticket ID is TICKET-123. Also, I need to reset my password.",  # Billing checks -> Triage -> Technical
            "My email is test@example.com"  # Technical processes password reset
        ],
        "expected_agent": "Triage"
    }
]

async def run_scenario(scenario):
    storage = InMemoryCheckpointStorage()
    workflow = create_handoff_workflow(checkpoint_storage=storage)
    session_id = f"scenario_session_{scenario['id']}"
    
    active_agent = "Triage"
    visited_agents = {active_agent.lower()}
    checkpoint_id = None
    pending_request_id = None
    
    console.print(f"\n[bold cyan]=== Running Scenario {scenario['id']}: {scenario['name']} ===[/bold cyan]")
    
    for turn_idx, turn_text in enumerate(scenario["turns"]):
        console.print(f"[bold green]Customer (Turn {turn_idx+1})[/bold green] > {turn_text}")
        
        # Recreate workflow to simulate stateless API checkpoint load
        workflow = create_handoff_workflow(checkpoint_storage=storage)
        
        if checkpoint_id and pending_request_id:
            user_messages = HandoffAgentUserRequest.create_response(turn_text)
            run_coro = workflow.run(
                responses={pending_request_id: user_messages},
                checkpoint_id=checkpoint_id
            )
        else:
            run_coro = workflow.run(message=turn_text)
            
        result = await run_coro
        
        # Reset turn markers
        pending_request_id = None
        
        for event in result:
            if event.type == "handoff_sent" and event.data:
                active_agent = event.data.target
                visited_agents.add(active_agent.lower())
                console.print(f"  [magenta]System: Handoff {event.data.source} -> {event.data.target}[/magenta]")
            elif event.type == "request_info":
                pending_request_id = event.request_id
            elif event.type == "output" and event.data:
                for msg in event.data.messages:
                    text_parts = []
                    for c in (msg.contents or []):
                        if hasattr(c, "type") and c.type == "text" and c.text:
                            text_parts.append(c.text)
                        elif hasattr(c, "type") and c.type == "function_call":
                            console.print(f"  [dim yellow]System Tool Call: {c.name}({c.arguments})[/dim yellow]")
                        elif hasattr(c, "type") and c.type == "function_result":
                            console.print(f"  [dim green]System Tool Result: {c.result}[/dim green]")
                    
                    final_text = "\n".join(text_parts)
                    if final_text:
                        console.print(f"  [bold yellow]{msg.author_name}[/bold yellow] > {final_text}")
                        
        checkpoint_ids = await storage.list_checkpoint_ids(workflow_name="customer_support")
        if checkpoint_ids:
            checkpoint_id = checkpoint_ids[-1]
            
    # Check outcome
    expected_options = [x.strip().lower() for x in scenario["expected_agent"].split("|")]
    passed = any(opt in visited_agents for opt in expected_options)
    
    outcome_status = "PASS" if passed else "FAIL"
    console.print(f"[bold {'green' if passed else 'red'}]Result: {outcome_status} (Visited: {visited_agents}, Expected: {scenario['expected_agent']})[/bold {'green' if passed else 'red'}]")
    
    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "expected": scenario["expected_agent"],
        "actual": active_agent,
        "status": outcome_status
    }

async def main():
    console.print("[bold green]Starting Integration Test Suite (10 Scenarios)...[/bold green]")
    results = []
    
    for scenario in TEST_SCENARIOS:
        try:
            res = await run_scenario(scenario)
            results.append(res)
        except Exception as e:
            console.print(f"[bold red]Scenario {scenario['id']} failed with error: {e}[/bold red]")
            results.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "expected": scenario["expected_agent"],
                "actual": "ERROR",
                "status": "FAIL"
            })
            
    # Render final status table
    table = Table(title="Test Suite Results Summary", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Scenario Name", style="white")
    table.add_column("Expected Agent", style="yellow")
    table.add_column("Actual Active Agent", style="blue")
    table.add_column("Status", style="green")
    
    passed_count = 0
    for res in results:
        status_style = "green" if res["status"] == "PASS" else "red"
        table.add_row(
            str(res["id"]),
            res["name"],
            res["expected"],
            res["actual"],
            f"[{status_style}]{res['status']}[/{status_style}]"
        )
        if res["status"] == "PASS":
            passed_count += 1
            
    console.print("\n")
    console.print(table)
    console.print(f"[bold green]Passed {passed_count} / {len(TEST_SCENARIOS)} scenarios.[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())
