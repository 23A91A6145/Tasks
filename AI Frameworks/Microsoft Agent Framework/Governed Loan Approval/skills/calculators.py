from typing import Dict, Any, List

class LoanCalculator:
    @staticmethod
    def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
        """
        Calculates monthly payment using standard amortization formula:
        M = P * [r(1+r)^n] / [(1+r)^n - 1]
        """
        if principal <= 0 or annual_rate < 0 or term_months <= 0:
            return 0.0
        
        # Monthly interest rate
        r = (annual_rate / 100) / 12
        if r == 0:
            return principal / term_months
            
        n = term_months
        monthly_payment = principal * (r * (1 + r)**n) / (((1 + r)**n) - 1)
        return round(monthly_payment, 2)

    @staticmethod
    def generate_amortization_schedule(principal: float, annual_rate: float, term_months: int) -> List[Dict[str, Any]]:
        """
        Generates a standard amortization schedule table showing monthly breakdowns.
        """
        schedule = []
        monthly_payment = LoanCalculator.calculate_monthly_payment(principal, annual_rate, term_months)
        
        r = (annual_rate / 100) / 12
        balance = principal
        
        for i in range(1, term_months + 1):
            if r == 0:
                interest_payment = 0.0
                principal_payment = monthly_payment
            else:
                interest_payment = balance * r
                principal_payment = monthly_payment - interest_payment
            
            # Adjust final payment to avoid floating-point drift
            if i == term_months:
                principal_payment = balance
                monthly_payment = interest_payment + principal_payment
                
            balance -= principal_payment
            if balance < 0:
                balance = 0.0
                
            schedule.append({
                "month": i,
                "payment": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "remaining_balance": round(balance, 2)
            })
            
        return schedule
