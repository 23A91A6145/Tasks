"""
Slash Command Dispatcher for Persistent Memory Chat CLI.
Supports Health Audits (/health), Multi-Format Exports (/export txt|md|json|html),
Fact Mutation (/forget, /setfact), Session Cloning (/clone), and Deletion (/delete).
"""

from typing import Dict, Any, Tuple, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.analytics import AnalyticsEngine
from app.health import SystemHealthCheck

class CommandDispatcher:
    """Dispatches and executes CLI slash commands."""

    def __init__(self, console: Console):
        self.console = console

    def handle_command(self, user_input: str, thread_obj, agent_obj) -> Tuple[bool, bool]:
        """
        Handles slash command execution.
        Returns tuple: (is_command, should_exit)
        """
        if not user_input.startswith("/"):
            return False, False

        parts = user_input.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("/exit", "/quit"):
            self.console.print("\n[bold yellow]👋 Exiting Persistent Memory Chat CLI. Goodbye![/bold yellow]\n")
            return True, True

        elif cmd == "/help":
            self._show_help()
        elif cmd in ("/health", "/doctor"):
            self._show_health(agent_obj.config)
        elif cmd == "/history":
            self._show_history(thread_obj, role_filter=arg)
        elif cmd in ("/stats", "/analytics"):
            self._show_analytics(thread_obj)
        elif cmd == "/facts":
            self._show_facts(thread_obj)
        elif cmd == "/forget":
            if arg:
                removed = thread_obj.memory_manager.provider.remove_fact(thread_obj.session_id, arg)
                if removed:
                    self.console.print(f"[bold green]🗑️ Removed fact key '[cyan]{arg}[/cyan]' from memory.[/bold green]")
                else:
                    self.console.print(f"[bold yellow]Fact key '[cyan]{arg}[/cyan]' not found in session memory.[/bold yellow]")
            else:
                self.console.print("[bold red]Please specify a fact key to remove! Example: /forget location[/bold red]")
        elif cmd == "/setfact":
            fact_parts = arg.split(maxsplit=1)
            if len(fact_parts) == 2:
                thread_obj.memory_manager.provider.set_fact(thread_obj.session_id, fact_parts[0], fact_parts[1])
                self.console.print(f"[bold green]🧠 Memory fact updated: [cyan]{fact_parts[0]}[/cyan] = '{fact_parts[1]}'[/bold green]")
            else:
                self.console.print("[bold red]Usage: /setfact <key> <value> (Example: /setfact role Lead Developer)[/bold red]")
        elif cmd == "/search":
            if arg:
                self._search_history(thread_obj, arg)
            else:
                self.console.print("[bold red]Please specify a search query! Example: /search python[/bold red]")
        elif cmd == "/title":
            if arg:
                thread_obj.memory_manager.set_session_title(thread_obj.session_id, arg)
                self.console.print(f"[bold green]🏷️ Session title updated to: [cyan]'{arg}'[/cyan][/bold green]")
            else:
                self.console.print(f"[bold cyan]Current Session Title:[/bold cyan] {thread_obj.title}")
        elif cmd == "/clone":
            if arg:
                cloned = thread_obj.memory_manager.provider.clone_session(thread_obj.session_id, arg)
                if cloned:
                    self.console.print(f"[bold green]📋 Session '[cyan]{thread_obj.session_id}[/cyan]' cloned to '[cyan]{arg}[/cyan]'.[/bold green]")
                    thread_obj.switch_session(arg)
                else:
                    self.console.print(f"[bold red]Failed to clone session. Make sure active session has history.[/bold red]")
            else:
                self.console.print("[bold red]Usage: /clone <new_session_id>[/bold red]")
        elif cmd == "/delete":
            if arg:
                deleted = thread_obj.memory_manager.clear_session(arg)
                if deleted:
                    self.console.print(f"[bold red]🗑️ Deleted session '[cyan]{arg}[/cyan]'.[/bold red]")
                    if arg == thread_obj.session_id:
                        thread_obj.switch_session("session_default")
                else:
                    self.console.print(f"[bold yellow]Session '[cyan]{arg}[/cyan]' does not exist.[/bold yellow]")
            else:
                self.console.print("[bold red]Usage: /delete <session_id>[/bold red]")
        elif cmd == "/compact":
            count = thread_obj.compact()
            self.console.print(f"[bold green]🧹 Storage compacted! Retained {count} clean message records.[/bold green]")
        elif cmd == "/clear":
            thread_obj.clear()
            self.console.print(f"[bold red]🗑️ Memory cleared for session '{thread_obj.session_id}'.[/bold red]")
        elif cmd in ("/session", "/new"):
            if arg:
                thread_obj.switch_session(arg)
                self.console.print(f"[bold green]🔄 Switched to session: [cyan]{arg}[/cyan][/bold green]")
            else:
                self._show_sessions(thread_obj)
        elif cmd == "/model":
            if arg:
                new_prov = arg.lower()
                if new_prov in ("mock", "ollama", "groq", "gemini"):
                    agent_obj.provider = new_prov
                    agent_obj.config.llm_provider = new_prov
                    agent_obj.model_name = agent_obj._resolve_model_name()
                    self.console.print(f"[bold green]🤖 Model provider updated to: [cyan]{agent_obj.model_name}[/cyan][/bold green]")
                else:
                    self.console.print("[bold red]Invalid provider! Options: mock, ollama, groq, gemini[/bold red]")
            else:
                self.console.print(f"[bold cyan]Active LLM Provider:[/bold cyan] {agent_obj.model_name}")
        elif cmd == "/export":
            fmt = arg.lower() if arg.lower() in ("txt", "md", "json", "html") else "txt"
            export_path = thread_obj.memory_manager.export(thread_obj.session_id, export_format=fmt)
            if export_path:
                self.console.print(f"[bold green]📄 Exported session history ({fmt.upper()}) to: [cyan]{export_path}[/cyan][/bold green]")
            else:
                self.console.print("[bold yellow]No history to export.[/bold yellow]")
        else:
            # Suggest matching command
            suggestions = self._suggest_command(cmd)
            self.console.print(f"[bold red]Unknown command '{cmd}'.[/bold red] Did you mean: [cyan]{suggestions}[/cyan]? Type /help for list.")

        return True, False

    def _suggest_command(self, typed_cmd: str) -> str:
        valid_cmds = ["/help", "/health", "/history", "/facts", "/setfact", "/forget", "/search", "/analytics", "/stats", "/title", "/compact", "/clone", "/delete", "/session", "/model", "/export", "/exit"]
        for c in valid_cmds:
            if c.startswith(typed_cmd[:3]):
                return c
        return "/help"

    def _show_help(self) -> None:
        table = Table(title="💡 Complete Slash Commands Suite", header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        table.add_row("/help", "Display available commands")
        table.add_row("/health or /doctor", "Run full system health audit & API connectivity check")
        table.add_row("/history [user|assistant]", "View history timeline (optionally filtered by role)")
        table.add_row("/facts", "View extracted semantic user facts stored in memory")
        table.add_row("/setfact <key> <val>", "Manually add or override a persistent memory fact")
        table.add_row("/forget <key>", "Remove a specific user fact from persistent memory")
        table.add_row("/search <query>", "Search past message history for keyword")
        table.add_row("/stats or /analytics", "View Token Usage Dashboard & System Overview")
        table.add_row("/title [name]", "View or rename active session title")
        table.add_row("/clone <new_id>", "Duplicate active session into a new session thread")
        table.add_row("/delete <id>", "Delete a specific session history")
        table.add_row("/compact", "Compact and optimize JSONL history storage file")
        table.add_row("/session [id]", "List sessions or switch to session ID")
        table.add_row("/model [name]", "Show or set provider (mock, ollama, groq, gemini)")
        table.add_row("/export [txt|md|json|html]", "Export history log to TXT, Markdown, JSON, or HTML")
        table.add_row("/exit", "Exit the CLI application")

        self.console.print(table)

    def _show_health(self, config) -> None:
        health_check = SystemHealthCheck(config)
        audit = health_check.run_health_audit()

        table = Table(title="🩺 System Health Audit", header_style="bold green")
        table.add_column("Diagnostic Check", style="cyan")
        table.add_column("Status / Details", style="bold white")

        table.add_row("Overall Health", f"[bold green]{audit['status']}[/bold green]")
        table.add_row("Free Disk Space", f"{audit['free_disk_gb']} GB")
        table.add_row("Total Active Sessions", str(audit["sessions_count"]))
        table.add_row("Total Saved Messages", str(audit["total_messages"]))
        table.add_row("Chat Log File Size", f"{audit['chat_log_size_kb']} KB")
        table.add_row("Error Log File Size", f"{audit['error_log_size_kb']} KB")
        table.add_row("Active Provider", audit["active_provider"])
        table.add_row("Ollama Server Status", "[bold green]ONLINE[/bold green]" if audit["ollama_online"] else "[bold yellow]OFFLINE (Fallback to Mock active)[/bold yellow]")
        table.add_row("Groq API Key", "[bold green]CONFIGURED[/bold green]" if audit["groq_configured"] else "[dim]NOT SET[/dim]")
        table.add_row("Gemini API Key", "[bold green]CONFIGURED[/bold green]" if audit["gemini_configured"] else "[dim]NOT SET[/dim]")

        self.console.print(table)

    def _show_history(self, thread_obj, role_filter: str = "") -> None:
        messages = thread_obj.memory_manager.provider.load_history(thread_obj.session_id, role_filter=role_filter)
        if not messages:
            self.console.print(f"[bold yellow]No messages in session history matching filter '{role_filter}'.[/bold yellow]")
            return

        filter_label = f" (Filter: {role_filter})" if role_filter else ""
        self.console.print(f"\n[bold cyan]📜 Session History: {thread_obj.title} ({thread_obj.session_id}){filter_label} - {len(messages)} messages:[/bold cyan]\n")
        for idx, m in enumerate(messages, 1):
            role_color = "green" if m["role"] == "user" else "cyan"
            timestamp = m.get("timestamp", "")
            content = m.get("content", "")
            tokens = m.get("tokens", 0)
            self.console.print(f"[dim]{idx}. [{timestamp}] ({tokens} tokens)[/dim] [{role_color}][bold]{m['role'].upper()}:[/bold][/{role_color}] {content}")
        self.console.print()

    def _show_facts(self, thread_obj) -> None:
        facts = thread_obj.get_extracted_facts()
        if not facts:
            self.console.print("[bold yellow]No extracted user facts stored in memory yet. Tell me 'My name is Bob' or 'I am a Developer'![/bold yellow]")
            return

        table = Table(title=f"🧠 Extracted Memory Facts ({thread_obj.session_id})", header_style="bold cyan")
        table.add_column("Attribute", style="magenta")
        table.add_column("Extracted Fact", style="bold green")

        for k, v in facts.items():
            table.add_row(k.replace("_", " ").title(), v)

        self.console.print(table)

    def _search_history(self, thread_obj, query: str) -> None:
        results = thread_obj.memory_manager.search(query)
        if not results:
            self.console.print(f"[bold yellow]No matches found for query: '{query}'[/bold yellow]")
            return

        self.console.print(f"\n[bold cyan]🔍 Found {len(results)} search matches for '{query}':[/bold cyan]\n")
        for idx, r in enumerate(results, 1):
            self.console.print(
                f"[dim]{idx}. [{r['timestamp']}] [Session: {r['session_id']}][/dim] "
                f"[bold cyan]{r['role'].upper()}:[/bold cyan] {r['content']}"
            )
        self.console.print()

    def _show_analytics(self, thread_obj) -> None:
        engine = AnalyticsEngine(thread_obj.memory_manager.provider)
        session_data = engine.get_session_analytics(thread_obj.session_id)
        system_data = engine.get_system_analytics()

        table = Table(title=f"📊 Session Token Analytics ({thread_obj.title})", header_style="bold green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")

        table.add_row("Session ID", session_data["session_id"])
        table.add_row("Session Title", session_data["title"])
        table.add_row("Total Messages", str(session_data["total_messages"]))
        table.add_row("User Messages / Tokens", f"{session_data['user_messages']} msgs ({session_data['user_tokens']} tokens)")
        table.add_row("Assistant Messages / Tokens", f"{session_data['assistant_messages']} msgs ({session_data['assistant_tokens']} tokens)")
        table.add_row("Total Token Consumption", f"{session_data['total_tokens']} tokens")
        table.add_row("Avg Tokens Per Turn", f"{session_data['avg_tokens_per_msg']} tokens/turn")
        table.add_row("Memory Facts Extracted", str(session_data["facts_count"]))
        table.add_row("Disk Storage Footprint", f"{session_data['disk_size_kb']} KB")
        table.add_row("JSONL Storage Path", session_data["file_path"])

        self.console.print(table)

        sys_panel = (
            f"[bold cyan]🌐 System-Wide Memory Overview:[/bold cyan]\n"
            f"• Active Sessions: [bold yellow]{system_data['total_sessions']}[/bold yellow] | "
            f"Total Messages: [bold yellow]{system_data['grand_total_messages']}[/bold yellow] | "
            f"Total Tokens: [bold yellow]{system_data['grand_total_tokens']}[/bold yellow] | "
            f"Total Disk Usage: [bold yellow]{system_data['grand_total_disk_kb']} KB[/bold yellow]"
        )
        self.console.print(Panel(sys_panel, border_style="green"))

    def _show_sessions(self, thread_obj) -> None:
        sessions = thread_obj.memory_manager.list_all_sessions()
        self.console.print("\n[bold cyan]📁 Available Persistent Sessions:[/bold cyan]")
        table = Table(header_style="bold green")
        table.add_column("Status", style="bold yellow")
        table.add_column("Session ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Messages", style="magenta")
        table.add_column("Last Updated", style="dim")

        for s in sessions:
            status = "ACTIVE" if s["id"] == thread_obj.session_id else ""
            table.add_row(
                status,
                s["id"],
                s.get("title", s["id"]),
                str(s.get("message_count", 0)),
                s.get("updated_at", "")
            )

        self.console.print(table)
        self.console.print("[dim]To switch sessions, run: /session <session_id>[/dim]\n")
