from crewai.tools import tool

_MOCK_CUSTOMERS = {
    "C1001": {"name": "Alice Johnson", "email": "alice@example.com", "plan": "Pro", "status": "active", "since": "2024-03-15"},
    "C1002": {"name": "Bob Smith", "email": "bob@example.com", "plan": "Basic", "status": "active", "since": "2024-06-01"},
    "C1003": {"name": "Carol Davis", "email": "carol@example.com", "plan": "Enterprise", "status": "past_due", "since": "2023-11-20"},
}

_MOCK_INVOICES = [
    {"id": "INV-1243", "customer": "C1001", "amount": 99.00, "currency": "USD", "status": "paid", "due": "2026-07-15"},
    {"id": "INV-1244", "customer": "C1001", "amount": 99.00, "currency": "USD", "status": "pending", "due": "2026-08-15"},
    {"id": "INV-1245", "customer": "C1003", "amount": 499.00, "currency": "USD", "status": "overdue", "due": "2026-06-30"},
]

_MOCK_ORDERS = [
    {"id": "ORD-901", "customer": "C1001", "product": "Pro Plan - Annual", "amount": 999.00, "status": "completed", "date": "2026-01-10"},
    {"id": "ORD-902", "customer": "C1002", "product": "Basic Plan - Monthly", "amount": 19.00, "status": "active", "date": "2026-07-01"},
    {"id": "ORD-903", "customer": "C1003", "product": "Enterprise - Custom", "amount": 4999.00, "status": "pending", "date": "2026-07-20"},
]

_MOCK_PRODUCTS = {
    "Basic": {"price": 19, "billing": "monthly", "features": ["1 user", "5GB storage", "Email support"]},
    "Pro": {"price": 99, "billing": "monthly", "features": ["5 users", "50GB storage", "Priority support", "API access"]},
    "Enterprise": {"price": 499, "billing": "monthly", "features": ["Unlimited users", "500GB storage", "24/7 support", "API access", "Custom integrations", "SLA"]},
}


@tool("Company Data")
def company_data_tool(query: str) -> str:
    """Looks up company records: customers, invoices, orders, or products.
    Use for account-specific questions about billing history, order status,
    customer details, invoices, pricing, or plan features.
    Include identifiers like customer ID, invoice number, or product name."""
    try:
        q = query.lower()

        if "customer" in q or "account" in q:
            for cid, info in _MOCK_CUSTOMERS.items():
                if cid.lower() in q or info["name"].lower() in q:
                    return (
                        f"Customer: {info['name']} ({cid})\n"
                        f"  Email:  {info['email']}\n"
                        f"  Plan:   {info['plan']}\n"
                        f"  Status: {info['status']}\n"
                        f"  Since:  {info['since']}"
                    )
            customers = "\n".join(
                f"  {cid}: {c['name']} ({c['plan']}, {c['status']})"
                for cid, c in _MOCK_CUSTOMERS.items()
            )
            return f"Customers on file:\n{customers}"

        if "invoice" in q or "inv" in q:
            for inv in _MOCK_INVOICES:
                if inv["id"].lower() in q:
                    return (
                        f"Invoice {inv['id']}\n"
                        f"  Customer: {inv['customer']}\n"
                        f"  Amount:   {inv['currency']} {inv['amount']:.2f}\n"
                        f"  Status:   {inv['status']}\n"
                        f"  Due:      {inv['due']}"
                    )
            invoices = "\n".join(
                f"  {inv['id']}: {inv['customer']} - {inv['currency']} {inv['amount']:.2f} ({inv['status']})"
                for inv in _MOCK_INVOICES
            )
            return f"Invoices on file:\n{invoices}"

        if "order" in q:
            for o in _MOCK_ORDERS:
                if o["id"].lower() in q:
                    return (
                        f"Order {o['id']}\n"
                        f"  Customer: {o['customer']}\n"
                        f"  Product:  {o['product']}\n"
                        f"  Amount:   ${o['amount']:.2f}\n"
                        f"  Status:   {o['status']}\n"
                        f"  Date:     {o['date']}"
                    )
            orders = "\n".join(
                f"  {o['id']}: {o['customer']} - {o['product']} (${o['amount']:.2f}, {o['status']})"
                for o in _MOCK_ORDERS
            )
            return f"Orders on file:\n{orders}"

        if "product" in q or "plan" in q or "pricing" in q or "feature" in q:
            for pname, pinfo in _MOCK_PRODUCTS.items():
                if pname.lower() in q:
                    features = "\n    - ".join([""] + pinfo["features"])
                    return (
                        f"Product: {pname}\n"
                        f"  Price:   ${pinfo['price']}/{pinfo['billing']}\n"
                        f"  Features:{features}"
                    )
            plans = "\n".join(
                f"  {pname}: ${pinfo['price']}/{pinfo['billing']}"
                for pname, pinfo in _MOCK_PRODUCTS.items()
            )
            return f"Available plans:\n{plans}"

        return (
            "Company records available. Try:\n"
            '  - "customer C1001" or "customer Alice"\n'
            '  - "invoice INV-1243"\n'
            '  - "order ORD-901"\n'
            '  - "product Pro" or "pricing plans"'
        )
    except Exception as e:
        return f"Company data lookup failed: {e}"
