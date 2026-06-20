import json
from pathlib import Path


class QualityAgent:

    def calculate_score(
        self,
        report
    ):

        score = 100

        score -= report.get(
            "missing_values",
            0
        )

        score -= report.get(
            "duplicate_ids",
            0
        )

        if score < 0:
            score = 0

        return score

    def save_history(
        self,
        metrics,
        score
    ):

        Path(
            "reports"
        ).mkdir(
            exist_ok=True
        )

        history_file = Path(
            "reports/quality_history.json"
        )

        history = []

        if history_file.exists():

            history = json.loads(
                history_file.read_text()
            )

        history.append({

            "execution_time":
            metrics["execution_time"],

            "rows":
            metrics["rows"],

            "quality_score":
            score
        })

        history_file.write_text(

            json.dumps(
                history,
                indent=4
            )
        )

        return history