import asyncio
import os
import sys
from datetime import datetime, timezone
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from agent_framework import InMemoryCheckpointStorage
from agent_framework.orchestrations import HandoffAgentUserRequest

from app.workflows.handoff import create_handoff_workflow
from app.services.history import load_history, save_history
from app.services.analytics import get_analytics
from app.services.routing import list_agents_info
from app.services.logger import log_chat, log_routing, log_error
from app.config import CHECKPOINTS_DIR, RuntimeConfig

console = Console()

# Global in-memory storage for persistent CLI session resumption
checkpoint_storage = InMemoryCheckpointStorage()

class CLISessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        # Load existing history/metadata if any
        history_data = load_history(session_id)
        self.metadata = history_data.get("metadata", {
            "active_agent": "Triage",
            "status": "Online",
            "resolved": False,
            "escalated": False
        })
        self.messages = history_data.get("messages", [])
        
        # Load checkpoints and request state from metadata if they exist
        self.checkpoint_id = self.metadata.get("checkpoint_id")
        self.pending_request_id = self.metadata.get("pending_request_id")

    def update_agent(self, agent_name: str):
        self.metadata["active_agent"] = agent_name
        self.save()

    def set_resolved(self, resolved: bool = True):
        self.metadata["resolved"] = resolved
        if resolved:
            self.metadata["status"] = "Resolved"
        self.save()

    def set_escalated(self, escalated: bool = True):
        self.metadata["escalated"] = escalated
        if escalated:
            self.metadata["status"] = "Escalated"
        self.save()

    def add_message(self, role: str, author: str, contents: str):
        self.messages.append({
            "role": role,
            "author": author,
            "contents": [{"type": "text", "text": contents}],
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        })
        self.save()

    def update_checkpoint(self, checkpoint_id: str | None, pending_request_id: str | None):
        self.checkpoint_id = checkpoint_id
        self.pending_request_id = pending_request_id
        self.metadata["checkpoint_id"] = checkpoint_id
        self.metadata["pending_request_id"] = pending_request_id
        self.save()

    def save(self):
        save_history(self.session_id, self.messages, self.metadata)

def draw_header(state: CLISessionState):
    """Draws the header dashboard panel using double borders."""
    agent_display = state.metadata.get("active_agent", "Triage")
    status_display = "Escalated" if state.metadata.get("escalated") else ("Resolved" if state.metadata.get("resolved") else "Active")
    
    # Resolve the active model string
    prov = RuntimeConfig.LLM_PROVIDER.upper()
    mod_attr = f"{prov}_MODEL"
    model_name = getattr(RuntimeConfig, mod_attr, "Unknown")
    model_display = f"{prov} ({model_name})"
    
    text = Text()
    text.append("       🤖 AI Customer Support Center       \n", style="bold cyan")
    text.append(f"Session : {state.session_id}\n", style="green")
    text.append(f"Agent   : {agent_display}\n", style="yellow")
    text.append(f"Model   : {model_display}\n", style="blue")
    text.append(f"Status  : {status_display}", style="magenta")

    panel = Panel(text, box=box.DOUBLE, border_style="bold blue", expand=False)
    console.print(panel)

def print_help():
    """Prints help information."""
    table = Table(title="Support CLI Commands", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    table.add_row("/help", "Show this help table")
    table.add_row("/agents", "List all available support agents and their tools")
    table.add_row("/history", "Display conversation history of this session")
    table.add_row("/session <id>", "Switch to or create a session (e.g. /session customer_002)")
    table.add_row("/provider <p> [m]", "Switch LLM provider (ollama, openai, groq, gemini) and model")
    table.add_row("/summary", "Generate and display ticket details summary (AI analysis)")
    table.add_row("/resolve", "Mark ticket resolved and print closing ticket summary")
    table.add_row("/export", "Export chat history to a Markdown file in history/")
    table.add_row("/escalate", "Escalate the ticket to human support")
    table.add_row("/restart", "Restart conversation and reset session state")
    table.add_row("/status", "Print current system configuration and statistics")
    table.add_row("/exit", "Exit application")
    console.print(table)

def print_agents():
    """Lists agent info."""
    agents = list_agents_info()
    for agent in agents:
        tools_str = ", ".join(agent["tools"]) if agent["tools"] else "None"
        console.print(Panel(
            f"[bold cyan]{agent['name']} ({agent['role']})[/bold cyan]\n"
            f"[white]{agent['description']}[/white]\n"
            f"[yellow]Tools:[/yellow] {tools_str}",
            border_style="green",
            box=box.ROUNDED,
            expand=False
        ))

def print_history(state: CLISessionState):
    """Prints history logs."""
    if not state.messages:
        console.print("[yellow]No message history found for this session.[/yellow]")
        return
        
    console.print(f"\n--- Conversation History for [green]{state.session_id}[/green] ---")
    for msg in state.messages:
        role = msg.get("role")
        author = msg.get("author", role)
        text_parts = []
        for c in msg.get("contents", []):
            if isinstance(c, dict):
                if c.get("type") == "text":
                    text_parts.append(c.get("text", ""))
                elif c.get("type") == "function_call":
                    text_parts.append(f"[Tool Call: {c.get('name')}]")
            else:
                text_parts.append(str(c))
                
        text = "\n".join(text_parts)
        if role == "user":
            console.print(f"[bold green]Customer[/bold green] > {text}")
        else:
            console.print(f"[bold yellow]{author}[/bold yellow] > {text}")

async def handle_cli_workflow(state: CLISessionState, user_input: str):
    """Executes or resumes the workflow with user input, recreates workflow per turn with fallback."""
    # Add user message to history and logger with timestamp
    state.messages.append({
        "role": "user",
        "author": "Customer",
        "contents": [{"type": "text", "text": user_input}],
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    })
    state.save()
    log_chat(state.session_id, "user", "Customer", user_input)
    
    workflow = create_handoff_workflow(checkpoint_storage=checkpoint_storage)

    new_checkpoint_id = None
    new_request_id = None
    
    # Local event handler helper
    active_resp_author = None
    async def process_events(coro):
        nonlocal active_resp_author, new_checkpoint_id, new_request_id
        async for event in coro:
            if event.type == "handoff_sent" and event.data:
                state.update_agent(event.data.target)
                log_routing(state.session_id, event.data.source, event.data.target)
                console.print(f"\n\n[bold magenta][System] Handoff: {event.data.source} -> {event.data.target}[/bold magenta]")
            elif event.type == "request_info":
                new_request_id = event.request_id
            elif event.type == "output" and event.data:
                from agent_framework import AgentResponse, AgentResponseUpdate
                if isinstance(event.data, AgentResponseUpdate):
                    if event.data.text:
                        if not active_resp_author or active_resp_author != event.executor_id:
                            active_resp_author = event.executor_id
                            print(f"\n[{active_resp_author}] > ", end="", flush=True)
                        print(event.data.text, end="", flush=True)
                elif isinstance(event.data, AgentResponse):
                    for msg in event.data.messages:
                        text_parts = []
                        for c in (msg.contents or []):
                            if hasattr(c, "type") and c.type == "text" and c.text:
                                text_parts.append(c.text)
                            elif hasattr(c, "type") and c.type == "function_call":
                                console.print(f"\n[dim yellow][System Tool Call: {c.name}({c.arguments})][/dim yellow]")
                            elif hasattr(c, "type") and c.type == "function_result":
                                console.print(f"[dim green][System Tool Result: {c.result}][/dim green]")
                        
                        final_text = "\n".join(text_parts)
                        if final_text:
                            state.messages.append({
                                "role": "assistant",
                                "author": msg.author_name,
                                "contents": [{"type": "text", "text": final_text}],
                                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                            })
                            state.save()
                            log_chat(state.session_id, "assistant", msg.author_name, final_text)

    # Self-healing checkpoint loading using global memory storage
    resumed = False
    if state.checkpoint_id and state.pending_request_id:
        try:
            # Resume flow
            user_messages = HandoffAgentUserRequest.create_response(user_input)
            run_coro = workflow.run(
                stream=True,
                checkpoint_id=state.checkpoint_id,
                responses={state.pending_request_id: user_messages}
            )
            await process_events(run_coro)
            resumed = True
        except Exception as e:
            log_error(f"In-memory checkpoint resumption failed for CLI session {state.session_id}, falling back to fresh run: {e}")
            state.update_checkpoint(None, None)
            # Recreate workflow to clear broken internal state
            workflow = create_handoff_workflow(checkpoint_storage=checkpoint_storage)
            
    if not resumed:
        try:
            run_coro = workflow.run(message=user_input, stream=True)
            await process_events(run_coro)
        except Exception as e:
            log_error(f"CLI session {state.session_id} workflow error: {str(e)}", exc_info=True)
            console.print(f"\n[bold red]Error running workflow turn: {e}[/bold red]")

    # Save latest checkpoint ID from storage
    checkpoint_ids = await checkpoint_storage.list_checkpoint_ids(workflow_name="customer_support")
    if checkpoint_ids:
        new_checkpoint_id = checkpoint_ids[-1]
    
    # Update local state and history metadata
    state.update_checkpoint(new_checkpoint_id, new_request_id)
    print() # line break after streaming completes

def export_transcript(state: CLISessionState):
    """Exports session logs as a readable markdown file."""
    if not state.messages:
        console.print("[yellow]Nothing to export: session history is empty.[/yellow]")
        return
        
    export_path = os.path.join(os.path.dirname(CHECKPOINTS_DIR), f"{state.session_id}_transcript.md")
    
    try:
        prov = RuntimeConfig.LLM_PROVIDER.upper()
        model_name = getattr(RuntimeConfig, f"{prov}_MODEL", "Unknown")
        
        md = []
        md.append(f"# AI Customer Support Session Transcript - {state.session_id}")
        md.append(f"- **LLM Provider**: {prov}")
        md.append(f"- **LLM Model**: {model_name}")
        md.append(f"- **Final Active Agent**: {state.metadata.get('active_agent', 'Triage')}")
        md.append(f"- **Status**: {'Resolved' if state.metadata.get('resolved') else ('Escalated' if state.metadata.get('escalated') else 'Active')}")
        
        if "summary" in state.metadata:
            s = state.metadata["summary"]
            md.append("\n## Ticket Summary Details")
            md.append(f"- **Issue Summary**: {s.get('issue')}")
            md.append(f"- **Issue Category**: {s.get('category')}")
            md.append(f"- **Case Priority**: {s.get('priority')}")
            md.append(f"- **Turns Logged**: {s.get('turns')}")
            
        md.append("\n---\n")
        
        for msg in state.messages:
            role = msg.get("role", "").upper()
            author = msg.get("author", "Unknown")
            
            text_parts = []
            for c in msg.get("contents", []):
                if c.get("type") == "text":
                    text_parts.append(c.get("text", ""))
                elif c.get("type") == "function_call":
                    text_parts.append(f"*System Tool Call: {c.get('name')}({c.get('arguments')})*")
                elif c.get("type") == "function_result":
                    text_parts.append(f"*System Tool Result: {c.get('result')}*")
                    
            text = "\n".join(text_parts)
            if role == "USER":
                md.append(f"### 👤 Customer\n{text}\n")
            else:
                md.append(f"### 🤖 {author} ({role.title()})\n{text}\n")
                
        with open(export_path, "w") as f:
            f.write("\n".join(md))
            
        console.print(f"[bold green]Success![/bold green] Transcript exported to: [cyan]{export_path}[/cyan]")
    except Exception as e:
        log_error(f"Failed to export transcript for session {state.session_id}: {str(e)}")
        console.print(f"[bold red]Failed to export transcript: {e}[/bold red]")

async def run_cli():
    console.print("[bold cyan]Starting AI Customer Support CLI...[/bold cyan]")
    
    current_session = "customer_001"
    state = CLISessionState(current_session)
    
    os.system("clear" if os.name == "posix" else "cls")
    draw_header(state)
    print_help()
    
    while True:
        try:
            user_input = console.input("\n[bold green]Customer[/bold green] > ").strip()
            if not user_input:
                continue
                
            if user_input.startswith("/"):
                # Handle slash commands
                parts = user_input.split(maxsplit=2)
                cmd = parts[0].lower()
                
                if cmd == "/exit":
                    console.print("[bold red]Exiting Customer Support Center. Goodbye![/bold red]")
                    break
                elif cmd == "/help":
                    print_help()
                elif cmd == "/agents":
                    print_agents()
                elif cmd == "/history":
                    print_history(state)
                elif cmd == "/session":
                    if len(parts) < 2:
                        console.print("[red]Please specify a session ID. Example: /session customer_002[/red]")
                        continue
                    new_session = parts[1].strip()
                    state = CLISessionState(new_session)
                    console.print(f"[green]Switched to session: {new_session}[/green]")
                    draw_header(state)
                elif cmd == "/provider":
                    if len(parts) < 2:
                        prov = RuntimeConfig.LLM_PROVIDER
                        mod_attr = f"{prov.upper()}_MODEL"
                        console.print(f"[yellow]Active Provider: {prov}[/yellow]")
                        console.print(f"[yellow]Active Model   : {getattr(RuntimeConfig, mod_attr, 'Unknown')}[/yellow]")
                        console.print("Available providers: ollama, openai, groq, gemini")
                        continue
                    
                    prov = parts[1].strip().lower()
                    if prov not in ["ollama", "openai", "groq", "gemini"]:
                        console.print("[red]Invalid provider. Choose from: ollama, openai, groq, gemini[/red]")
                        continue
                    
                    RuntimeConfig.LLM_PROVIDER = prov
                    if len(parts) >= 3:
                        model_name = parts[2].strip()
                        setattr(RuntimeConfig, f"{prov.upper()}_MODEL", model_name)
                        
                    console.print(f"[green]Provider switched to {prov.upper()}.[/green]")
                    draw_header(state)
                elif cmd == "/summary":
                    from app.services.summary import generate_ticket_summary
                    console.print("[yellow]Generating dynamic ticket summary using LLM...[/yellow]")
                    summary = await generate_ticket_summary(state.session_id)
                    state.metadata["summary"] = summary
                    state.save()
                    
                    table = Table(title=f"Ticket Summary: {state.session_id}", show_header=True, box=box.ROUNDED, header_style="bold magenta")
                    table.add_column("Field", style="cyan")
                    table.add_column("Value", style="white")
                    table.add_row("Core Issue", summary.get("issue", "N/A"))
                    table.add_row("Category", summary.get("category", "N/A"))
                    table.add_row("Priority", summary.get("priority", "N/A"))
                    table.add_row("Assigned Agent", summary.get("assigned_agent", "N/A"))
                    table.add_row("Resolution", summary.get("resolution", "N/A"))
                    table.add_row("Total Turns", str(summary.get("turns", 0)))
                    console.print(table)
                elif cmd == "/resolve":
                    state.set_resolved(True)
                    from app.services.summary import generate_ticket_summary
                    console.print("[green]Ticket resolved! Generating AI ticket summary...[/green]")
                    summary = await generate_ticket_summary(state.session_id)
                    state.metadata["summary"] = summary
                    state.save()
                    
                    console.print("[bold green]✔ Ticket Successfully Resolved and Closed.[/bold green]")
                    table = Table(title=f"Resolved Ticket Summary: {state.session_id}", show_header=True, box=box.ROUNDED, header_style="bold green")
                    table.add_column("Field", style="cyan")
                    table.add_column("Value", style="white")
                    table.add_row("Core Issue", summary.get("issue", "N/A"))
                    table.add_row("Category", summary.get("category", "N/A"))
                    table.add_row("Priority", summary.get("priority", "N/A"))
                    table.add_row("Assigned Agent", summary.get("assigned_agent", "N/A"))
                    table.add_row("Resolution", summary.get("resolution", "N/A"))
                    table.add_row("Total Turns", str(summary.get("turns", 0)))
                    console.print(table)
                    draw_header(state)
                elif cmd == "/export":
                    export_transcript(state)
                elif cmd == "/escalate":
                    state.set_escalated(True)
                    log_routing(state.session_id, state.metadata.get("active_agent", "Triage"), "Human Specialist")
                    console.print("[bold red]Ticket has been ESCALATED to human support specialist.[/bold red]")
                    draw_header(state)
                elif cmd == "/restart":
                    # Clean checkpoint directory on restart
                    session_checkpoint_dir = os.path.join(CHECKPOINTS_DIR, state.session_id)
                    if os.path.exists(session_checkpoint_dir):
                        for file in os.listdir(session_checkpoint_dir):
                            try:
                                os.remove(os.path.join(session_checkpoint_dir, file))
                            except Exception:
                                pass
                                
                    # Re-initialize state
                    state = CLISessionState(state.session_id)
                    state.metadata = {
                        "active_agent": "Triage",
                        "status": "Online",
                        "resolved": False,
                        "escalated": False,
                        "checkpoint_id": None,
                        "pending_request_id": None
                    }
                    state.messages = []
                    state.checkpoint_id = None
                    state.pending_request_id = None
                    state.save()
                    
                    console.print("[yellow]Session restarted and checkpoints cleared.[/yellow]")
                    draw_header(state)
                elif cmd == "/status":
                    analytics = get_analytics()
                    prov = RuntimeConfig.LLM_PROVIDER.upper()
                    model_name = getattr(RuntimeConfig, f"{prov}_MODEL", "Unknown")
                    
                    console.print(Panel(
                        f"[bold yellow]System Status Details:[/bold yellow]\n"
                        f"Active Session: {state.session_id}\n"
                        f"LLM Provider  : {prov}\n"
                        f"LLM Model     : {model_name}\n"
                        f"Total Sessions: {analytics.get('total_sessions')}\n"
                        f"Resolved Rate : {analytics.get('resolution_rate')}\n"
                        f"Escalated     : {analytics.get('escalated_tickets')}\n"
                        f"Avg Response  : {analytics.get('avg_response_time_str')}\n"
                        f"Avg Duration  : {analytics.get('avg_session_time_str')}",
                        border_style="magenta",
                        box=box.ROUNDED,
                        expand=False
                    ))
                else:
                    console.print(f"[red]Unknown command: {cmd}. Type /help for assistance.[/red]")
            else:
                # Handle standard conversational input
                if state.metadata.get("resolved") or state.metadata.get("escalated"):
                    console.print("[yellow]This ticket is marked resolved or escalated. You can restart using /restart.[/yellow]")
                    continue
                await handle_cli_workflow(state, user_input)
                # Redraw header to update active agent status
                draw_header(state)
        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupt received. Exiting.[/bold red]")
            break
        except Exception as e:
            log_error(f"CLI exception: {str(e)}", exc_info=True)
            console.print(f"[bold red]System Error: {e}[/bold red]")

if __name__ == "__main__":
    asyncio.run(run_cli())
