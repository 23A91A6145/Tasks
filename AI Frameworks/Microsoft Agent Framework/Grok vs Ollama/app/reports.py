import json
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from app.config import Config
from app.utils import get_logger, console

logger = get_logger("reports")

class BenchmarkReportGenerator:
    @staticmethod
    def generate_all(results_list: List[Dict[str, Any]]) -> None:
        """Generates all analytics, tables, rank metrics, charts, and markdown scorecards."""
        if not results_list:
            logger.warning("No results found to generate reports.")
            console.print("[bold red]⚠ No results to generate reports. Run a benchmark first.[/bold red]")
            return

        df = pd.DataFrame(results_list)
        
        # Ensure directories exist
        Config.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Generate Visual Analytics Charts
        BenchmarkReportGenerator.generate_charts(df)
        
        # 2. Generate Markdown & Text Scorecard Reports
        BenchmarkReportGenerator.generate_markdown_report(df)
        
        console.print("[bold green]✔ Summary reports and visual analytics charts generated successfully![/bold green]")
        console.print(f"  📂 Reports: [cyan]{Config.REPORTS_DIR}/summary_report.md[/cyan]")
        console.print(f"  📂 Charts: [cyan]{Config.CHARTS_DIR}/[/cyan]")

    @staticmethod
    def generate_charts(df: pd.DataFrame) -> None:
        """Generates matplotlib chart PNGs for Latency, Quality, and Throughput."""
        # Group by Provider/Model combination
        grouped = df.groupby(["provider", "model"]).agg(
            avg_latency=("latency", "mean"),
            avg_ttft=("ttft", "mean"),
            avg_tps=("tps", "mean"),
            avg_quality=("quality_score", "mean"),
            success_rate=("error", lambda x: (x.isna() | (x == "")).mean() * 100)
        ).reset_index()
        
        labels = [f"{row['provider']}\n({row['model']})" for _, row in grouped.iterrows()]
        x = np.arange(len(labels))
        width = 0.35

        # --- Chart 1: Latency & TTFT Comparison ---
        plt.figure(figsize=(10, 6))
        plt.bar(x - width/2, grouped["avg_latency"], width, label="Avg Total Latency (s)", color="#3f51b5")
        plt.bar(x + width/2, grouped["avg_ttft"], width, label="Avg TTFT (s)", color="#00bcd4")
        plt.ylabel("Seconds")
        plt.title("Latency & Time to First Token (TTFT) Comparison")
        plt.xticks(x, labels)
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(Config.CHARTS_DIR / "latency_comparison.png", dpi=150)
        plt.close()

        # --- Chart 2: Throughput (TPS) Comparison ---
        plt.figure(figsize=(10, 6))
        plt.bar(labels, grouped["avg_tps"], color="#4caf50", width=0.5)
        plt.ylabel("Tokens Per Second (TPS)")
        plt.title("Inference Throughput (Output Tokens / Sec)")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(Config.CHARTS_DIR / "tps_comparison.png", dpi=150)
        plt.close()

        # --- Chart 3: Quality Score Comparison ---
        plt.figure(figsize=(10, 6))
        plt.bar(labels, grouped["avg_quality"], color="#ff9800", width=0.5)
        plt.ylabel("Quality Score (1-10)")
        plt.ylim(0, 10.5)
        plt.title("Response Quality Evaluation (Higher is Better)")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(Config.CHARTS_DIR / "quality_comparison.png", dpi=150)
        plt.close()

        logger.info("Matplotlib charts successfully rendered and saved.")

    @staticmethod
    def generate_markdown_report(df: pd.DataFrame) -> None:
        """Generates a professional Markdown scorecard summary report."""
        # Calculate summary metrics grouped by provider and model
        grouped = df.groupby(["provider", "model"]).agg(
            total_runs=("prompt", "count"),
            avg_latency=("latency", "mean"),
            min_latency=("latency", "min"),
            max_latency=("latency", "max"),
            avg_ttft=("ttft", "mean"),
            avg_tps=("tps", "mean"),
            avg_quality=("quality_score", "mean"),
            success_rate=("error", lambda x: (x.isna() | (x == "")).mean() * 100),
            total_cost=("cost", "sum"),
            avg_ram_gb=("ram_used_gb", "mean"),
            peak_ram_gb=("ram_used_gb", "max"),
            avg_ram_delta_gb=("ram_delta_gb", "mean")
        ).reset_index()

        # Find award rankings
        fastest_row = grouped.loc[grouped["avg_latency"].idxmin()]
        best_tps_row = grouped.loc[grouped["avg_tps"].idxmax()]
        best_quality_row = grouped.loc[grouped["avg_quality"].idxmax()]
        lowest_cost_row = grouped.loc[grouped["total_cost"].idxmin()]

        # Generate markdown content
        md = []
        md.append("# 🏆 AI Provider Swap Benchmarking Scorecard Report\n")
        md.append(f"**Generated At:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append("This report outlines the latency, quality, throughput, and cost analysis of executing identical AI Agent personas across Groq, Ollama, and Mock providers using the Microsoft Agent Framework abstraction.\n")
        
        md.append("## 🏆 Provider Awards & Rankings\n")
        md.append(f"- **🏆 Fastest Response (Avg Latency):** {fastest_row['provider']} ({fastest_row['model']}) - **{fastest_row['avg_latency']:.3f}s**")
        md.append(f"- **⚡ Highest Throughput (Avg TPS):** {best_tps_row['provider']} ({best_tps_row['model']}) - **{best_tps_row['avg_tps']:.1f} tokens/s**")
        md.append(f"- **🎯 Best Response Quality (Avg Score):** {best_quality_row['provider']} ({best_quality_row['model']}) - **{best_quality_row['avg_quality']:.1f}/10**")
        md.append(f"- **💰 Lowest Operation Cost (Total Run):** {lowest_cost_row['provider']} ({lowest_cost_row['model']}) - **${lowest_cost_row['total_cost']:.6f}**\n")

        md.append("## 📊 Provider Benchmark Metrics Table\n")
        md.append("| Provider | Model | Runs | Latency (Avg/Min/Max) | TTFT (Avg) | Throughput (Avg TPS) | Quality Score (Avg) | RAM Avg/Peak | Success Rate | Total Cost |")
        md.append("|---|---|---|---|---|---|---|---|---|---|")
        
        for _, row in grouped.iterrows():
            latency_str = f"{row['avg_latency']:.2f}s / {row['min_latency']:.2f}s / {row['max_latency']:.2f}s"
            success_str = f"{row['success_rate']:.1f}%"
            cost_str = f"${row['total_cost']:.6f}" if row['total_cost'] > 0 else "$0.00 (Local/Free)"
            ram_str = f"{row['avg_ram_gb']:.2f} GB / {row['peak_ram_gb']:.2f} GB" if row['avg_ram_gb'] > 0 else "N/A"
            md.append(
                f"| **{row['provider']}** | {row['model']} | {row['total_runs']} | {latency_str} | "
                f"{row['avg_ttft']:.2f}s | {row['avg_tps']:.1f} tps | {row['avg_quality']:.1f}/10 | {ram_str} | {success_str} | {cost_str} |"
            )
        
        md.append("\n## 🔍 Category-Specific Quality Scores\n")
        md.append("| Category | Provider | Model | Quality Score | Latency | TPS |")
        md.append("|---|---|---|---|---|---|")
        
        cat_group = df.groupby(["category", "provider", "model"]).agg(
            avg_q=("quality_score", "mean"),
            avg_l=("latency", "mean"),
            avg_tps=("tps", "mean")
        ).reset_index()
        
        for _, row in cat_group.iterrows():
            md.append(
                f"| {row['category']} | **{row['provider']}** | {row['model']} | {row['avg_q']:.1f}/10 | {row['avg_l']:.2f}s | {row['avg_tps']:.1f} |"
            )

        md.append("\n## 📂 Generated Assets")
        md.append("- Latency Comparison: `results/charts/latency_comparison.png`")
        md.append("- Throughput Comparison: `results/charts/tps_comparison.png`")
        md.append("- Quality Comparison: `results/charts/quality_comparison.png`")
        
        md.append("\n---")
        md.append("\n*Note: Quality evaluation utilizes automated AST-based python parser checks and regex heuristic checks to verify syntax validity, step-by-step reasoning tokens, and structured JSON completeness constraints.*")

        report_path = Config.REPORTS_DIR / "summary_report.md"
        with open(report_path, "w") as f:
            f.write("\n".join(md))

        logger.info(f"Markdown report scorecard generated and saved to {report_path}.")
