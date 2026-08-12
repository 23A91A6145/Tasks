# main.py

import argparse
import sys
import uvicorn
import json

from app.agent import classify_ticket_content
from app.database import init_db, save_classification, get_metrics
from app.config import LLM_MODEL

def run_server(host: str, port: int, reload: bool):
    """Starts the FastAPI web server hosting the dashboard and API."""
    print(f"Starting Structured Ticket Classifier server on http://{host}:{port}")
    print(f"Configured LLM Model: {LLM_MODEL}")
    init_db()
    uvicorn.run("app.api:app", host=host, port=port, reload=reload)

def classify_cli(message: str):
    """Classifies a support ticket directly from the command line."""
    if not message.strip():
        print("Error: Ticket message cannot be empty.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Classifying support ticket message using model: {LLM_MODEL}...\n")
    try:
        result, duration_ms = classify_ticket_content(message)
        
        # Save to database
        init_db()
        ticket_id = save_classification(message, result, LLM_MODEL, duration_ms)
        
        # Format the output beautifully
        output_data = {
            "database_id": ticket_id,
            "category": result.category.value,
            "priority": result.priority.value,
            "suggested_agent": result.suggested_agent.value,
            "confidence": result.confidence,
            "summary": result.summary,
            "requires_human_review": result.requires_human_review,
            "reasoning": result.reasoning,
            "processing_time_ms": duration_ms,
            "model_used": LLM_MODEL
        }
        
        print(json.dumps(output_data, indent=2))
        
    except Exception as e:
        print(f"Classification failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def show_metrics():
    """Displays triage metrics from the database."""
    init_db()
    metrics = get_metrics()
    print("Structured Ticket Classifier - Triage Analytics:\n")
    print(json.dumps(metrics, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="Structured Ticket Classifier - Type-Safe Support Triage System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the FastAPI dashboard web server")
    server_parser.add_argument("--host", default="127.0.0.1", help="Host address to bind the server to")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    server_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload of code changes")
    
    # Classify command
    classify_parser = subparsers.add_parser("classify", help="Classify a ticket message from the terminal")
    classify_parser.add_argument("message", type=str, help="The raw support ticket text message")
    
    # Metrics command
    subparsers.add_parser("metrics", help="Show triage metrics from the database")
    
    # Init DB command
    subparsers.add_parser("init-db", help="Initialize the SQLite database schema")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run benchmark evaluation over sample tickets")
    eval_parser.add_argument("--mode", default="fallback", choices=["fallback", "test", "llm"], help="Benchmark execution mode (default: fallback)")

    args = parser.parse_args()

    # If no command is specified, default to running the server
    if args.command is None:
        run_server("127.0.0.1", 8000, reload=True)
    elif args.command == "server":
        run_server(args.host, args.port, not args.no_reload)
    elif args.command == "classify":
        classify_cli(args.message)
    elif args.command == "metrics":
        show_metrics()
    elif args.command == "init-db":
        print("Initializing database...")
        init_db()
        print("Database initialized successfully.")
    elif args.command == "evaluate":
        from app.eval import run_evaluation
        run_evaluation(args.mode)

if __name__ == "__main__":
    main()
