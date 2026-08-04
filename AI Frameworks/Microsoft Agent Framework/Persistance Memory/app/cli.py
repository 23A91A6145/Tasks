"""
Rich CLI Terminal Interface for Persistent Memory Chat Assistant (Volume 3 Professional UI).
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live

from app.config import AppConfig
from app.agent import ChatAgent
from app.thread import AgentThread
from app.memory import PersistentMemoryManager
from app.commands import CommandDispatcher
from app.utils import setup_logger

class PersistentChatCLI:
    """Main CLI Application UI Controller."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.console = Console()
        self.logger = setup_logger(config.logs_dir)
        self.memory_manager = PersistentMemoryManager(config.history_dir)
        self.thread = AgentThread(
            session_id=config.default_session_id,
            memory_manager=self.memory_manager,
            max_context=config.max_context_messages
        )
        self.agent = ChatAgent(config)
        self.dispatcher = CommandDispatcher(self.console)

    def print_banner(self) -> None:
        """Renders Volume 3 professional status banner matching specifications."""
        stats = self.memory_manager.get_stats(self.thread.session_id)
        msg_count = stats["total_messages"]
        fact_count = len(stats.get("facts", {}))
        title = stats.get("title", self.thread.session_id)
        
        banner_table = Table.grid(padding=(0, 1))
        banner_table.add_column(style="bold yellow", justify="left", no_wrap=True)
        banner_table.add_column(style="bold white", justify="left")

        banner_table.add_row("Model    :", self.agent.model_name)
        banner_table.add_row("Memory   :", "FileHistoryProvider (Persistent JSONL + Indexing)")
        banner_table.add_row("Session  :", f"{title} [{self.thread.session_id}] ({msg_count} past messages loaded)")
        banner_table.add_row("Facts    :", f"{fact_count} active user facts in persistent memory")
        banner_table.add_row("Status   :", "Connected & Active")

        panel = Panel(
            banner_table,
            border_style="cyan",
            expand=False,
            title="[bold green]🤖 Persistent AI Assistant[/bold green]",
            subtitle="[dim]Microsoft Agent Framework Pattern • Volume 3[/dim]"
        )
        self.console.print(panel)
        self.console.print("[dim]Type your message, or type [cyan]/help[/cyan] for slash commands. Press Ctrl+C or /exit to quit.[/dim]\n")

    def run(self) -> None:
        """Runs interactive CLI chat loop."""
        self.console.clear()
        self.print_banner()

        # Log app start
        self.logger.info(f"CLI Started with session={self.thread.session_id}, provider={self.agent.provider}")

        while True:
            try:
                user_input = self.console.input("[bold green]You > [/bold green]").strip()
                
                if not user_input:
                    continue

                # Handle slash commands
                is_cmd, should_exit = self.dispatcher.handle_command(user_input, self.thread, self.agent)
                if is_cmd:
                    if should_exit:
                        break
                    continue

                # Save user message to persistent thread (triggers fact extraction automatically)
                self.thread.add_user_message(user_input)
                self.logger.info(f"User [{self.thread.session_id}]: {user_input}")

                # Generate AI response with context window & measure latency
                context = self.thread.get_context()

                if self.config.enable_spinner:
                    with self.console.status("[bold cyan]Thinking & Recalling Persistent Memory...[/bold cyan]", spinner="dots"):
                        response_text, latency_ms = self.agent.generate_response_with_latency(user_input, context)
                else:
                    response_text, latency_ms = self.agent.generate_response_with_latency(user_input, context)

                # Save assistant response to persistent thread
                self.thread.add_assistant_message(response_text, model=self.agent.model_name)
                self.logger.info(f"Assistant [{self.thread.session_id}] ({latency_ms}ms): {response_text[:50]}...")

                # Render response in formatted panel with latency badge
                self.console.print(f"\n[bold cyan]Assistant >[/bold cyan] [dim]({latency_ms} ms)[/dim]")
                md_response = Markdown(response_text)
                self.console.print(Panel(md_response, border_style="cyan", padding=(0, 1)))
                self.console.print()

            except KeyboardInterrupt:
                self.console.print("\n\n[bold yellow]Keyboard Interrupt received. Exiting persistent CLI...[/bold yellow]\n")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                self.console.print(f"\n[bold red]⚠️ An error occurred: {str(e)}[/bold red]\n")
