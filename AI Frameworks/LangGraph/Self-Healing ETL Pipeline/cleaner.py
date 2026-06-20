from pathlib import Path
import pandas as pd
from loguru import logger

logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)

class CleanerAgent:

    def remove_duplicates(self, df):

        before = len(df)

        df = df.drop_duplicates()

        after = len(df)

        logger.info(
            f"Duplicates Removed: {before-after}"
        )

        return df

    def handle_missing_values(self, df):

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for col in numeric_columns:

            median_value = df[col].median()

            df[col] = df[col].fillna(
                median_value
            )

        logger.info(
            "Missing values handled"
        )

        return df

    def clean_text_columns(self, df):

        text_columns = df.select_dtypes(
            include=["object"]
        ).columns

        for col in text_columns:

            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
            )

        logger.info(
            "Text cleaned"
        )

        return df

    def clean(self, df):

        logger.info(
            "Cleaning Started"
        )

        df = self.remove_duplicates(df)

        df = self.handle_missing_values(df)

        df = self.clean_text_columns(df)

        logger.success(
            "Cleaning Completed"
        )

        return df