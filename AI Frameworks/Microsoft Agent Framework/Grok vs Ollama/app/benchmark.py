import csv
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

from app.config import Config
from app.utils import get_logger, console
from app.providers import BaseProviderClient, GroqProviderClient, OllamaProviderClient, MockProviderClient
from app.agent import ChatAgent
from app.evaluator import ResponseEvaluator
from app.metrics import BenchmarkMetric

logger = get_logger("benchmark")

class BenchmarkController:
    def __init__(self, runs_per_prompt: int = 1, timeout: int = 60) -> None:
        self.runs_per_prompt = runs_per_prompt
        self.timeout = timeout
        self.results: List[Dict[str, Any]] = []

    def get_default_prompts(self) -> List[Dict[str, str]]:
        """Generates a default suite of professional benchmarking prompts across 6 core categories."""
        return [
            {
                "category": "General QA",
                "prompt": "Explain the concept of quantum computing superposition in simple terms for a high school student."
            },
            {
                "category": "Coding",
                "prompt": "Write a Python function called 'is_prime' that checks if a number is prime and returns a boolean. Include comments."
            },
            {
                "category": "Reasoning",
                "prompt": "If a shirt is wet and dries in 1 hour in the sun, how long does it take for 5 shirts to dry in the sun? Explain your logic step-by-step."
            },
            {
                "category": "Summarization",
                "prompt": "Summarize the following passage in less than 3 sentences: 'The Model Context Protocol (MCP) is an open-standard protocol designed to establish secure, uniform communication between AI clients and local or remote data sources. By formalizing tool capabilities, data routing, and session handshakes, it eliminates developer-side custom integrations, allowing agents to query databases, file systems, and API nodes out of the box. Key advantages include client-agnostic reuse and deep security sandboxing.'"
            },
            {
                "category": "Tool Calling",
                "prompt": "Generate a JSON payload representation of a tool call named 'get_weather' targeting location 'Tokyo, Japan' with unit 'celsius'."
            },
            {
                "category": "Translation",
                "prompt": "Translate the following statement into formal French: 'AI provider abstraction layers prevent developer lock-in and enable seamless client swapping.'"
            }
        ]

    def load_datasets(self) -> List[Dict[str, str]]:
        """
        Loads prompts from datasets/prompts.csv or datasets/benchmark_cases.json.
        Falls back to generating defaults if files are empty or missing, saving them for future runs.
        """
        prompts_file = Config.DATASETS_DIR / "prompts.csv"
        json_file = Config.DATASETS_DIR / "benchmark_cases.json"
        
        # 1. Try to load from CSV
        if prompts_file.exists() and prompts_file.stat().st_size > 0:
            try:
                df = pd.read_csv(prompts_file)
                if not df.empty and "prompt" in df.columns and "category" in df.columns:
                    logger.info(f"Loaded {len(df)} prompts from CSV: {prompts_file}")
                    return df.to_dict(orient="records")
            except Exception as e:
                logger.error(f"Error reading prompts CSV: {e}")

        # 2. Try to load from JSON
        if json_file.exists() and json_file.stat().st_size > 0:
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0 and "prompt" in data[0]:
                        logger.info(f"Loaded {len(data)} prompts from JSON: {json_file}")
                        return data
            except Exception as e:
                logger.error(f"Error reading prompts JSON: {e}")

        # 3. Fallback to default prompts
        defaults = self.get_default_prompts()
        logger.info("No prompts dataset found or files are empty. Generating default suite.")
        
        # Save defaults to CSV & JSON
        try:
            Config.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
            # Save CSV
            df = pd.DataFrame(defaults)
            df.to_csv(prompts_file, index=False)
            # Save JSON
            with open(json_file, "w") as f:
                json.dump(defaults, f, indent=2)
            logger.info("Saved default prompt suite to datasets directory.")
        except Exception as e:
            logger.error(f"Failed to save default prompt files: {e}")
            
        return defaults

    def run_benchmark(self, providers: List[BaseProviderClient], prompts: List[Dict[str, str]], stream: bool = True) -> List[Dict[str, Any]]:
        """
        Runs the benchmark suite sequentially across active providers.
        Implements warmup runs and handles failures gracefully.
        """
        self.results = []
        
        console.print(Panel.fit(
            "[bold green]Starting AI Provider Benchmark Execution Engine[/bold green]\n"
            f"Prompts: {len(prompts)} | Runs per prompt: {self.runs_per_prompt} | Streaming: {stream}",
            title="⚡ Engine Config"
        ))

        for provider in providers:
            # 1. Check health
            console.print(f"\n[bold blue]Checking connection to provider '{provider.__class__.__name__}' (Model: {provider.model_id})...[/bold blue]")
            if not provider.check_health():
                console.print(f"[bold red]❌ Provider '{provider.__class__.__name__}' is offline or model is missing. Skipping.[/bold red]")
                logger.warning(f"Skipped provider {provider.__class__.__name__} due to health check failure.")
                continue
            console.print(f"[bold green]✔ Connected to '{provider.__class__.__name__}'![/bold green]")
            
            # 2. Warm-Up Run
            console.print(f"[dim]Initiating warm-up run for model '{provider.model_id}' to eliminate cold-start loading skews...[/dim]")
            agent = ChatAgent(client=provider)
            try:
                # 1 token warm up run
                agent.run("Hello", stream=False)
                logger.info(f"Warm-up run completed successfully for {provider.model_id}.")
            except Exception as e:
                logger.warning(f"Warm-up run failed for {provider.model_id}: {e}")

            # 3. Benchmark Execution Loop
            total_tasks = len(prompts) * self.runs_per_prompt
            
            # Concurrency Control: Run Ollama sequentially to avoid high RAM CPU swap, run others concurrently
            is_local_cpu = "ollama" in provider.__class__.__name__.lower()
            max_workers = 1 if is_local_cpu else min(4, total_tasks)
            
            results_lock = threading.Lock()
            task_idx = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task_id = progress.add_task(
                    description=f"Benchmarking {provider.__class__.__name__.replace('ProviderClient', '')} ({provider.model_id})",
                    total=total_tasks
                )

                def execute_single_prompt(item, run_num):
                    nonlocal task_idx
                    category = item.get("category", "General")
                    prompt = item.get("prompt", "")
                    
                    # Track task index (safe thread-increment not strictly required for CLI presentation, but nice to show)
                    with results_lock:
                        task_idx += 1
                        current_idx = task_idx
                        
                    progress.update(task_id, description=f"[{current_idx}/{total_tasks}] Category: {category} (Run {run_num}/{self.runs_per_prompt})")
                    logger.info(f"Running Benchmark task: Provider={provider.__class__.__name__}, Category={category}, Run={run_num}/{self.runs_per_prompt}")
                    
                    # Re-instantiate agent for clean memory/context on each run
                    agent = ChatAgent(client=provider)
                    
                    try:
                        # Run prompt and get metrics
                        response_text, metrics = agent.run(prompt, stream=stream)
                        
                        # Quality Evaluation
                        quality_score = ResponseEvaluator.evaluate(
                            prompt=prompt,
                            category=category,
                            response_text=response_text,
                            error=metrics.get("error")
                        )
                        
                        # Cost Estimation
                        cost = 0.0
                        if "groq" in provider.__class__.__name__.lower():
                            cost = (metrics["input_tokens"] / 1_000_000) * 0.59 + (metrics["output_tokens"] / 1_000_000) * 0.79
                        
                        # Standardize metric dictionary
                        metric_record = BenchmarkMetric(
                            prompt=prompt,
                            category=category,
                            provider=provider.__class__.__name__.replace("ProviderClient", ""),
                            model=provider.model_id,
                            latency=metrics["latency"],
                            ttft=metrics["ttft"],
                            input_tokens=metrics["input_tokens"],
                            output_tokens=metrics["output_tokens"],
                            tps=metrics["tps"],
                            quality_score=quality_score,
                            response_text=response_text,
                            error=metrics["error"],
                            cost=cost,
                            ram_used_gb=metrics.get("ram_used_gb", 0.0),
                            ram_delta_gb=metrics.get("ram_delta_gb", 0.0)
                        )
                        
                        with results_lock:
                            self.results.append(metric_record.model_dump())
                            
                    except Exception as e:
                        logger.error(f"Benchmark run crashed: {e}")
                        metric_record = BenchmarkMetric(
                            prompt=prompt,
                            category=category,
                            provider=provider.__class__.__name__.replace("ProviderClient", ""),
                            model=provider.model_id,
                            latency=0.0,
                            ttft=0.0,
                            input_tokens=0,
                            output_tokens=0,
                            tps=0.0,
                            quality_score=1.0,
                            response_text="",
                            error=str(e),
                            cost=0.0,
                            ram_used_gb=0.0,
                            ram_delta_gb=0.0
                        )
                        with results_lock:
                            self.results.append(metric_record.model_dump())
                    
                    progress.update(task_id, advance=1)

                if max_workers == 1:
                    # Sequential execution (CPU-safe for Ollama)
                    for item in prompts:
                        for run_num in range(1, self.runs_per_prompt + 1):
                            execute_single_prompt(item, run_num)
                            # Add a tiny cooldown to let CPU rest and prevent thermal throttling
                            if is_local_cpu:
                                time.sleep(1.0)
                else:
                    # Concurrent execution (Fast cloud API processing)
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = [
                            executor.submit(execute_single_prompt, item, run_num)
                            for item in prompts
                            for run_num in range(1, self.runs_per_prompt + 1)
                        ]
                        # Wait for all to finish
                        for f in as_completed(futures):
                            pass

        # Save metrics
        self.save_results()
        return self.results

    def save_results(self) -> None:
        """Persists the benchmark outputs to results/benchmark.csv and results/benchmark.json."""
        if not self.results:
            logger.warning("No benchmark results to save.")
            return

        Config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        csv_file = Config.RESULTS_DIR / "benchmark.csv"
        json_file = Config.RESULTS_DIR / "benchmark.json"

        try:
            # Save to JSON
            with open(json_file, "w") as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Successfully saved benchmark JSON results to {json_file}")
            
            # Save to CSV using pandas DataFrame
            df = pd.DataFrame(self.results)
            # Remove response_text from CSV to keep file sizes clean and readable
            df_csv = df.drop(columns=["response_text"], errors="ignore")
            df_csv.to_csv(csv_file, index=False)
            logger.info(f"Successfully saved benchmark CSV results to {csv_file}")
            
        except Exception as e:
            logger.error(f"Error saving benchmark result files: {e}")
            console.print(f"[bold red]❌ Failed to save results to disk: {e}[/bold red]")
