import argparse
import sys
from rich.panel import Panel
from rich.table import Table
from app.config import Config
from app.utils import console, get_logger
from app.providers import GroqProviderClient, OllamaProviderClient, MockProviderClient
from app.benchmark import BenchmarkController
from app.reports import BenchmarkReportGenerator

logger = get_logger("main")

def print_welcome_banner():
    banner_text = (
        "[bold cyan]⚡ Microsoft Agent Framework • Provider Swap Benchmarking System ⚡[/bold cyan]\n"
        "[dim]Zero-bias latency, throughput, quality, and cost evaluation across backends[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", expand=False))

def handle_health_check(groq_model, ollama_model):
    console.print("\n[bold yellow]🔍 Running Provider Diagnostics & Health Checks...[/bold yellow]")
    
    mock_client = MockProviderClient()
    groq_client = GroqProviderClient(model_id=groq_model)
    ollama_client = OllamaProviderClient(model_id=ollama_model)
    
    table = Table(title="Provider Health Summary")
    table.add_column("Provider", style="cyan")
    table.add_column("Model ID", style="magenta")
    table.add_column("Connection Status", style="green")
    table.add_column("Diagnostics / Action Required", style="yellow")
    
    # Check Mock
    mock_ok = mock_client.check_health()
    table.add_row(
        "Mock (Local Sim)", 
        mock_client.model_id, 
        "[green]✔ Healthy[/green]" if mock_ok else "[red]❌ Error[/red]", 
        "Offline test client. Always available."
    )
    
    # Check Groq
    groq_ok = groq_client.check_health()
    groq_diag = "API key active. Connected." if groq_ok else "Check GROQ_API_KEY in your .env file or register at https://console.groq.com."
    table.add_row(
        "Groq (Cloud)", 
        groq_client.model_id, 
        "[green]✔ Healthy[/green]" if groq_ok else "[red]❌ Offline / Bad Credentials[/red]", 
        groq_diag
    )
    
    # Check Ollama
    ollama_ok = ollama_client.check_health()
    ollama_diag = "Daemon active. Model verified." if ollama_ok else (
        "1. Verify Ollama is running (`ollama serve`)\n"
        f"2. Pull the model locally (`ollama pull {ollama_model}`)\n"
        f"3. Verify host matches: {Config.OLLAMA_HOST}"
    )
    table.add_row(
        "Ollama (Local)", 
        ollama_client.model_id, 
        "[green]✔ Healthy[/green]" if ollama_ok else "[red]❌ Connection Refused / Pull Required[/red]", 
        ollama_diag
    )
    
    console.print(table)
    
    all_healthy = groq_ok and ollama_ok
    if not all_healthy:
        console.print("\n[bold red]⚠️ Some providers are not fully healthy.[/bold red] You can still run the benchmark in mock mode or skip the offline provider.")
    return groq_ok, ollama_ok

def display_results_summary(results):
    if not results:
        return
        
    table = Table(title="🏆 Benchmark Performance Rankings Summary")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Avg Latency (s)", style="green")
    table.add_column("Avg TTFT (s)", style="blue")
    table.add_column("Avg TPS", style="yellow")
    table.add_column("Quality Score", style="cyan")
    table.add_column("Cost", style="magenta")
    table.add_column("Status", style="green")
    
    # Aggregate data manually for a nice summary terminal representation
    summary = {}
    for r in results:
        key = (r["provider"], r["model"])
        if key not in summary:
            summary[key] = {
                "latencies": [], "ttfts": [], "tps_vals": [], "qualities": [], "errors": 0, "cost": 0.0
            }
        if r["error"]:
            summary[key]["errors"] += 1
        else:
            summary[key]["latencies"].append(r["latency"])
            summary[key]["ttfts"].append(r["ttft"])
            summary[key]["tps_vals"].append(r["tps"])
            summary[key]["qualities"].append(r["quality_score"])
            summary[key]["cost"] += r["cost"]

    for (provider, model), stats in summary.items():
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0.0
        avg_ttft = sum(stats["ttfts"]) / len(stats["ttfts"]) if stats["ttfts"] else 0.0
        avg_tps = sum(stats["tps_vals"]) / len(stats["tps_vals"]) if stats["tps_vals"] else 0.0
        avg_q = sum(stats["qualities"]) / len(stats["qualities"]) if stats["qualities"] else 1.0
        
        status_str = f"[green]Success[/green]" if stats["errors"] == 0 else f"[red]{stats['errors']} Failed[/red]"
        cost_str = f"${stats['cost']:.6f}" if stats["cost"] > 0 else "$0.00"
        
        table.add_row(
            provider,
            model,
            f"{avg_lat:.2f}s",
            f"{avg_ttft:.2f}s",
            f"{avg_tps:.1f} tps",
            f"{avg_q:.1f}/10",
            cost_str,
            status_str
        )
        
    console.print(table)

def main():
    print_welcome_banner()
    
    parser = argparse.ArgumentParser(description="Microsoft Agent Framework Provider Swap Benchmark Suite")
    parser.add_argument("--mode", type=str, choices=["full", "dry-run", "mock"], default="full",
                        help="Execution mode: full (Groq + Ollama), dry-run (first 2 prompts), mock (local simulated clients)")
    parser.add_argument("--runs", type=int, default=1, help="Number of benchmark iterations per prompt")
    parser.add_argument("--check-providers", action="store_true", help="Run diagnostic health checks on providers and exit")
    parser.add_argument("--model-groq", type=str, default=Config.GROQ_DEFAULT_MODEL, help="Override Groq model ID")
    parser.add_argument("--model-ollama", type=str, default=Config.OLLAMA_DEFAULT_MODEL, help="Override Ollama model ID")
    parser.add_argument("--prompts-limit", type=int, default=0, help="Limit number of prompts from the dataset to benchmark")
    parser.add_argument("--no-stream", action="store_true", help="Disable response streaming (measures TTFT as full latency)")
    
    args = parser.parse_args()
    
    # 1. Diagnostic health checks mode
    if args.check_providers:
        handle_health_check(args.model_groq, args.model_ollama)
        sys.exit(0)
        
    # 2. Check health automatically for full run
    groq_ok, ollama_ok = False, False
    if args.mode == "full":
        groq_ok, ollama_ok = handle_health_check(args.model_groq, args.model_ollama)
        if not groq_ok and not ollama_ok:
            console.print("\n[bold yellow]⚠️ Warning: Both Groq and Ollama are offline. Automatically switching to 'mock' mode for local simulation.[/bold yellow]")
            args.mode = "mock"
        elif not groq_ok or not ollama_ok:
            offline_provider = "Ollama" if not ollama_ok else "Groq"
            console.print(f"\n[bold yellow]⚠️ Warning: {offline_provider} is offline. Automatically falling back to active providers (unattended mode).[/bold yellow]")

    # 3. Setup Provider Client instances based on mode
    providers = []
    if args.mode == "mock":
        providers = [MockProviderClient(model_id="mock-lpu-1b"), MockProviderClient(model_id="mock-server-8b")]
    elif args.mode == "dry-run":
        providers = [MockProviderClient(model_id="mock-dry-run-model")]
    else:
        if groq_ok:
            providers.append(GroqProviderClient(model_id=args.model_groq))
        if ollama_ok:
            providers.append(OllamaProviderClient(model_id=args.model_ollama))
            
    if not providers:
        console.print("[bold red]❌ No healthy provider clients available to execute benchmarks. Aborting.[/bold red]")
        sys.exit(1)

    # 4. Load datasets
    controller = BenchmarkController(runs_per_prompt=args.runs)
    prompts = controller.load_datasets()
    
    # Apply dry-run limits or custom prompt limit
    if args.mode == "dry-run":
        console.print("[yellow]Dry-run mode activated: Benchmarking top 2 prompts with Mock Client[/yellow]")
        prompts = prompts[:2]
    elif args.prompts_limit > 0:
        prompts = prompts[:args.prompts_limit]

    # 5. Execute benchmark runs
    stream = not args.no_stream
    results = controller.run_benchmark(providers, prompts, stream=stream)
    
    # 6. Display CLI Summary & Scorecards
    display_results_summary(results)
    
    # 7. Generate markdown summary reports and charts
    BenchmarkReportGenerator.generate_all(results)

if __name__ == "__main__":
    main()
