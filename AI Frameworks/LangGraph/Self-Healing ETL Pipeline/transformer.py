from pathlib import Path

import pandas as pd

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class TransformerAgent:

    def create_total_length(self, df):

        df["TotalLength"] = (
            df["SepalLengthCm"]
            + df["PetalLengthCm"]
        )

        return df

    def create_total_width(self, df):

        df["TotalWidth"] = (
            df["SepalWidthCm"]
            + df["PetalWidthCm"]
        )

        return df

    def create_flower_size(self, df):

        df["FlowerSize"] = (
            df["TotalLength"]
            + df["TotalWidth"]
        )

        return df

    def encode_species(self, df):

        mapping = {
            "Iris-setosa": 0,
            "Iris-versicolor": 1,
            "Iris-virginica": 2
        }

        df["SpeciesCode"] = (
            df["Species"]
            .map(mapping)
        )

        return df

    def save_transformed_data(
        self,
        df,
        output_path
    ):

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df.to_csv(
            output_path,
            index=False
        )

        logger.success(
            f"Saved: {output_path}"
        )

    def transform(self, df):

        logger.info(
            "Transformation Started"
        )

        df = self.create_total_length(df)

        df = self.create_total_width(df)

        df = self.create_flower_size(df)

        df = self.encode_species(df)

        logger.success(
            "Transformation Completed"
        )

        return df