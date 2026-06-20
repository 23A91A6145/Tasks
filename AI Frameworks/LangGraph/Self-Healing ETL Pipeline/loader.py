from pathlib import Path

from sqlalchemy import create_engine
from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class LoaderAgent:

    def __init__(self):

        db_path = Path(
            "database/etl.db"
        )

        self.engine = create_engine(
            f"sqlite:///{db_path}"
        )

    def load(self, df):

        logger.info(
            "Database Loading Started"
        )

        df.to_sql(
            name="iris_data",
            con=self.engine,
            if_exists="replace",
            index=False
        )

        logger.success(
            "Database Loading Completed"
        )

        return {
            "status": "success",
            "rows_loaded": len(df),
            "table_name": "iris_data"
        }