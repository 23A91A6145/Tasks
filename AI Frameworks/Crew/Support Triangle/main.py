import logging
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import LLM_PROVIDER, LLM_MODEL, LOG_DIR, LOG_LEVEL
from crews.support_crew import SupportCrew

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "support_triage.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DEMO_QUERIES = [
    ("I was charged twice for my subscription this month. Can you help?", "Billing"),
    ("I can't log into my account. It says 'invalid credentials'.", "Technical"),
    ("What are the differences between your Pro and Enterprise plans?", "Sales"),
    ("How do I reset my password? I keep getting an error.", "Technical"),
    ("Do you offer student discounts on the basic plan?", "Billing"),
    ("My invoice #1243 shows the wrong amount. Please fix it.", "Billing"),
    ("The dashboard widget keeps showing a loading spinner and never loads.", "Technical"),
    ("I want to upgrade from Basic to Pro. What happens to my existing data?", "Sales"),
    ("Can I speak to a human? This is urgent.", "escalate"),
]


def check_ollama():
    if LLM_PROVIDER != "ollama":
        return True
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        if LLM_MODEL not in result.stdout:
            logger.warning(
                "Model '%s' not found in Ollama. "
                "Run: ollama pull %s", LLM_MODEL, LLM_MODEL
            )
            return False
        return True
    except FileNotFoundError:
        logger.warning("Ollama not found. Install: curl -fsSL https://ollama.com/install.sh | sh")
        return False
    except subprocess.TimeoutExpired:
        logger.warning("Ollama did not respond within 10s.")
        return False


def print_result(result: dict) -> None:
    print("\n" + "=" * 60)
    print(f" Classification: {result.get('classification', 'unknown').upper()}")
    tools = result.get("tools_used", [])
    if tools:
        print(f" Tools: {', '.join(tools)}")
    print(f" Validated: {'YES' if result.get('validated') else 'NO'}")
    if result.get("validation_report") and "APPROVED" not in result.get("validation_report", ""):
        print(f" Report: {result['validation_report'][:80]}...")
    print("-" * 60)
    print(result.get("response", "No response generated."))
    print("=" * 60)


def run_single(query: str) -> dict:
    logger.info("Starting support triage for: %s", query[:200])
    crew = SupportCrew(query)
    return crew.run()


def run_demo() -> list:
    print("\n  SUPPORT TRIAGE DEMO — Volumes I-V")
    print(f" Provider: {LLM_PROVIDER}")
    print(f" Running {len(DEMO_QUERIES)} sample queries...\n")
    results = []
    for i, (query, expected) in enumerate(DEMO_QUERIES, 1):
        print(f"\n--- Query {i}/{len(DEMO_QUERIES)} ---")
        print(f" [{expected}] {query[:80]}...")
        try:
            result = run_single(query)
            results.append(result)
            actual = result.get("classification", "?")
            status = "OK" if actual == expected.lower() else "MISCLASSIFY"
            print(f"  [{status}] → {actual}")
        except Exception as e:
            logger.error("Query %d failed: %s", i, e)
            print(f"  [FAILED] {e}")
    print("\n Demo complete.")
    return results


def main():
    if "--demo" in sys.argv:
        os.environ["USE_DEMO_LLM"] = "true"

    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} \"<query>\"")
        print(f"       python {os.path.basename(__file__)} --demo")
        sys.exit(1)

    if not check_ollama():
        print("\nWarning: Ollama may not be available. Attempting anyway...\n")

    if "--demo" in sys.argv:
        run_demo()
    else:
        query = " ".join(a for a in sys.argv[1:] if a != "--demo")
        if not query:
            print("Error: empty query. Provide a question or use --demo.")
            sys.exit(1)
        result = run_single(query)
        print_result(result)


if __name__ == "__main__":
    main()
