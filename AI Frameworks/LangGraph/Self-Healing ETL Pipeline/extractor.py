from pathlib import Path

import pandas as pd
from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB",
    level="INFO"
)


class ExtractorAgent:

    def load_csv(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        return pd.read_csv(path)

    def get_metadata(self, df, file_path):

        path = Path(file_path)

        return {
            "file_name": path.name,
            "file_size_kb": round(
                path.stat().st_size / 1024,
                2
            ),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "missing_values": int(
                df.isnull().sum().sum()
            )
        }

    def extract(self, file_path: str):

        logger.info(
            f"Loading file: {file_path}"
        )

        df = self.load_csv(file_path)

        metadata = self.get_metadata(
            df,
            file_path
        )

        logger.success(
            "Extraction completed"
        )

        return {
            "status": "success",
            "data": df,
            "metadata": metadata
        }