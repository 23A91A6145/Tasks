import random

class CreditBureauMCP:
    @staticmethod
    def check_outstanding_debt(ssn: str) -> float:
        """
        Simulates an external Model Context Protocol (MCP) tool call to query
        active debt indices for a verified SSN.
        """
        if not ssn:
            return 0.0
        # Seed generator with the SSN value to keep responses stable and reproducible
        random.seed(ssn)
        return round(random.uniform(0.0, 12000.0), 2)

    @staticmethod
    def get_credit_rating_class(credit_score: int) -> str:
        """
        Maps numeric credit scores to credit risk class assessments.
        """
        if credit_score >= 740:
            return "Excellent"
        elif credit_score >= 670:
            return "Good"
        elif credit_score >= 580:
            return "Fair"
        elif credit_score >= 300:
            return "Poor"
        else:
            return "Critical"
