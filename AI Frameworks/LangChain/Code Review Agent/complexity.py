from radon.complexity import cc_visit
from radon.metrics import mi_visit


def analyze_complexity(code):

    try:

        complexity_results = cc_visit(code)

        functions = []

        total_complexity = 0

        for item in complexity_results:

            functions.append({
                "name": item.name,
                "complexity": item.complexity
            })

            total_complexity += item.complexity

        maintainability = round(
            mi_visit(code, multi=True),
            2
        )

        if total_complexity <= 5:
            risk = "LOW"

        elif total_complexity <= 15:
            risk = "MEDIUM"

        else:
            risk = "HIGH"

        return {
            "functions": functions,
            "total_complexity": total_complexity,
            "maintainability": maintainability,
            "risk_level": risk
        }

    except Exception as e:

        return {
            "error": str(e)
        }