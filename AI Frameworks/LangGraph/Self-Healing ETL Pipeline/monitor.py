from pathlib import Path
import json
from datetime import datetime

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class MonitorAgent:

    def create_execution_report(
        self,
        metrics
    ):

        Path(
            "reports"
        ).mkdir(
            exist_ok=True
        )

        with open(
            "reports/execution_report.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4
            )

        with open(
            "reports/execution_report.txt",
            "w",
            encoding="utf-8"
        ) as file:

            for key, value in metrics.items():

                file.write(
                    f"{key}: {value}\n"
                )

    def save_metrics(
        self,
        metrics
    ):

        with open(
            "reports/metrics.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4
            )

        logger.success(
            "Metrics Saved"
        )

    def build_metrics(
        self,
        df,
        validation_report,
        start_time,
        end_time
    ):

        duration = (
            end_time -
            start_time
        ).total_seconds()

        metrics = {

            "execution_time":
                str(
                    datetime.now()
                ),

            "status":
                validation_report[
                    "status"
                ],

            "rows":
                len(df),

            "columns":
                len(df.columns),

            "duration_seconds":
                round(
                    duration,
                    4
                ),

            "table_name":
                "iris_data",

            "success_rate":
                "100%"
                if validation_report[
                    "status"
                ] == "PASS"
                else "0%"
        }

        return metrics