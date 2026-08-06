import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler
from app.config import AUDIT_LOG_PATH, APPROVAL_LOG_PATH, ERROR_LOG_PATH

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler(APPROVAL_LOG_PATH)
    ]
)

logger = logging.getLogger("RefundAgent")

def log_audit(entry: dict):
    """Log secure transactions to the audit file."""
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to audit log: {e}")

def log_error(message: str, exc_info=None):
    """Log system and security errors."""
    try:
        error_logger = logging.getLogger("RefundAgentError")
        if not error_logger.handlers:
            error_logger.addHandler(logging.FileHandler(ERROR_LOG_PATH))
        error_logger.error(message, exc_info=exc_info)
    except Exception as e:
        logger.error(f"Failed to write to error log: {e}")

def generate_id(prefix: str = "REQ") -> str:
    """Generate a unique UUID with prefix."""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

# Mock database of customers and orders for validation and policy checks
MOCK_CUSTOMERS = {
    "CUST-1045": {
        "customer_id": "CUST-1045",
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne.com",
        "risk_level": "Low",
        "purchase_date": "2026-07-28",
        "product_name": "T-800 CPU Repair Kit",
        "account_status": "Active"
    },
    "CUST-2092": {
        "customer_id": "CUST-2092",
        "name": "John Connor",
        "email": "john.connor@resistance.net",
        "risk_level": "Medium",
        "purchase_date": "2026-08-01",
        "product_name": "Tactical Radio Comm",
        "account_status": "Active"
    },
    "CUST-9912": {
        "customer_id": "CUST-9912",
        "name": "T-1000 Liquid Metal",
        "email": "mimicry@skynet.gov",
        "risk_level": "High",
        "purchase_date": "2026-08-05",
        "product_name": "Sub-zero Nitrogen Container",
        "account_status": "Flagged"
    },
    "CUST-5511": {
        "customer_id": "CUST-5511",
        "name": "Miles Dyson",
        "email": "miles.dyson@cyberdyne.com",
        "risk_level": "Low",
        "purchase_date": "2026-08-03",
        "product_name": "Neural Net Processor Schematic",
        "account_status": "Active"
    }
}

MOCK_ORDERS = {
    "ORD-5582": {
        "order_id": "ORD-5582",
        "customer_id": "CUST-1045",
        "amount": 125.00,
        "product": "T-800 CPU Repair Kit",
        "purchase_date": "2026-07-28"
    },
    "ORD-8812": {
        "order_id": "ORD-8812",
        "customer_id": "CUST-2092",
        "amount": 450.00,
        "product": "Tactical Radio Comm",
        "purchase_date": "2026-08-01"
    },
    "ORD-0001": {
        "order_id": "ORD-0001",
        "customer_id": "CUST-9912",
        "amount": 1500.00,
        "product": "Sub-zero Nitrogen Container",
        "purchase_date": "2026-08-05"
    },
    "ORD-3321": {
        "order_id": "ORD-3321",
        "customer_id": "CUST-5511",
        "amount": 89.99,
        "product": "Neural Net Processor Schematic",
        "purchase_date": "2026-08-03"
    }
}
