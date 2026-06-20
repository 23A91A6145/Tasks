from pathlib import Path
from datetime import datetime
import json
import pandas as pd

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class ReporterAgent:

    def generate_report(
        self,
        validation_report,
        rows_processed,
        rows_loaded
    ):

        timestamp = datetime.now()

        report = {
            "timestamp":
                str(timestamp),

            "rows_processed":
                rows_processed,

            "rows_loaded":
                rows_loaded,

            "validation_status":
                validation_report["status"],

            "missing_values":
                validation_report[
                    "missing_values"
                ],

            "duplicate_ids":
                validation_report[
                    "duplicate_ids"
                ]
        }

        Path(
            "data/reports"
        ).mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            "data/reports/pipeline_metrics.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        with open(
            "data/reports/pipeline_report.txt",
            "w",
            encoding="utf-8"
        ) as file:

            for key, value in report.items():

                file.write(
                    f"{key}: {value}\n"
                )

        history = pd.DataFrame(
            [report]
        )

        history_file = (
            "data/reports/execution_history.csv"
        )

        if Path(history_file).exists():

            old = pd.read_csv(
                history_file
            )

            history = pd.concat(
                [old, history],
                ignore_index=True
            )

        history.to_csv(
            history_file,
            index=False
        )

        logger.success(
            "Report Generated"
        )

        return report