from pathlib import Path

import pandas as pd

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class RecoveryAgent:

    def fix_missing_values(self, df):

        numeric_cols = df.select_dtypes(
            include=["number"]
        ).columns

        for col in numeric_cols:

            median = df[col].median()

            df[col] = df[col].fillna(
                median
            )

        return df

    def fix_negative_values(self, df):

        numeric_cols = [
            "SepalLengthCm",
            "SepalWidthCm",
            "PetalLengthCm",
            "PetalWidthCm",
            "TotalLength",
            "TotalWidth",
            "FlowerSize"
        ]

        for col in numeric_cols:

            if col in df.columns:

                df[col] = df[col].abs()

        return df

    def remove_duplicate_ids(self, df):

        if "Id" in df.columns:

            df = df.drop_duplicates(
                subset=["Id"]
            )

        return df

    def fix_species_code(self, df):

        if "SpeciesCode" in df.columns:

            df["SpeciesCode"] = (
                df["SpeciesCode"]
                .clip(0, 2)
            )

        return df

    def save_failed_records(
        self,
        df
    ):

        Path(
            "data/failed"
        ).mkdir(
            parents=True,
            exist_ok=True
        )

        df.to_csv(
            "data/failed/failed_records.csv",
            index=False
        )

    def create_report(
        self,
        report_text
    ):

        with open(
            "data/failed/recovery_report.txt",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                report_text
            )

    def recover(self, df):

        logger.info(
            "Recovery Started"
        )

        self.save_failed_records(
            df
        )

        df = self.fix_missing_values(
            df
        )

        df = self.fix_negative_values(
            df
        )

        df = self.remove_duplicate_ids(
            df
        )

        df = self.fix_species_code(
            df
        )

        report = """
Recovery Completed

Fixes Applied:

1. Missing Values Fixed

2. Negative Values Fixed

3. Duplicate IDs Removed

4. Species Codes Corrected
"""

        self.create_report(
            report
        )

        logger.success(
            "Recovery Completed"
        )

        return df