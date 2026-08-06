import asyncio
from agent_framework import InMemoryCheckpointStorage, AgentResponse, AgentResponseUpdate
from app.workflows.handoff import create_handoff_workflow

def handle_workflow_event(event):
    """Processes and formats workflow events for interactive terminal output."""
    if event.type == "handoff_sent" and event.data:
        print(f"\n\n[System] Handoff: {event.data.source} -> {event.data.target}")
    elif event.type == "request_info":
        print(f"\n\n[System] Workflow paused. Waiting for user input... (Request ID: {event.request_id})")
    elif event.type == "output" and event.data:
        if isinstance(event.data, AgentResponseUpdate):
            if event.data.text:
                print(event.data.text, end="", flush=True)
        elif isinstance(event.data, AgentResponse):
            # Print tool calls/results if any occurred in the background
            for msg in event.data.messages:
                for c in (msg.contents or []):
                    if hasattr(c, "type") and c.type == "function_call":
                        print(f"\n[{msg.author_name}] -> Call Tool: {c.name}({c.arguments})")
                    elif hasattr(c, "type") and c.type == "function_result":
                        print(f"[{msg.author_name}] -> Tool Result: {c.result}")

async def main():
    storage = InMemoryCheckpointStorage()
    workflow = create_handoff_workflow(checkpoint_storage=storage)

    # Step 1: Initial user query
    user_input = "Hi, I need to check the status of my refund."
    print(f"\n[Customer] > {user_input}")
    print("\n--- Running Turn 1 ---")
    
    current_request_id = None
    
    # Run the workflow. It starts with TriageAgent, routes to BillingAgent.
    async for event in workflow.run(
        message=user_input,
        stream=True
    ):
        handle_workflow_event(event)
        if event.type == "request_info":
            current_request_id = event.request_id

    # Fetch the checkpoint ID from storage
    checkpoint_ids = await storage.list_checkpoint_ids(workflow_name="customer_support")
    if checkpoint_ids:
        checkpoint_id = checkpoint_ids[-1]
        print(f"\n[System] Retrieved Checkpoint ID: {checkpoint_id}")
    else:
        print("\n[System] Error: No checkpoint ID generated in Turn 1.")
        return

    # Step 2: Next turn with the transaction ID
    if current_request_id:
        user_input_2 = "My refund ticket ID is TICKET-123"
        print(f"\n[Customer] > {user_input_2}")
        print("\n--- Running Turn 2 ---")
        
        # Build the response payload using the helper
        from agent_framework.orchestrations import HandoffAgentUserRequest
        user_messages = HandoffAgentUserRequest.create_response(user_input_2)
        
        # Recreate workflow to simulate stateless API checkpoint load
        workflow = create_handoff_workflow(checkpoint_storage=storage)
        
        # Resume the workflow by passing responses mapping
        async for event in workflow.run(
            stream=True,
            checkpoint_id=checkpoint_id,
            responses={current_request_id: user_messages}
        ):
            handle_workflow_event(event)

if __name__ == "__main__":
    asyncio.run(main())
