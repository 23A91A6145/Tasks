from pathlib import Path

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class ValidatorAgent:

    REQUIRED_COLUMNS = [
        "Id",
        "SepalLengthCm",
        "SepalWidthCm",
        "PetalLengthCm",
        "PetalWidthCm",
        "Species",
        "TotalLength",
        "TotalWidth",
        "FlowerSize",
        "SpeciesCode"
    ]

    def validate_columns(self, df):

        missing_columns = []

        for column in self.REQUIRED_COLUMNS:

            if column not in df.columns:
                missing_columns.append(column)

        return missing_columns

    def validate_missing_values(self, df):

        return int(
            df.isnull().sum().sum()
        )

    def validate_duplicate_ids(self, df):

        return int(
            df["Id"].duplicated().sum()
        )

    def validate_flower_size(self, df):

        return bool(
            (df["FlowerSize"] > 0).all()
        )

    def validate_species_code(self, df):

        allowed = {0, 1, 2}

        values = set(
            df["SpeciesCode"].unique()
        )

        return values.issubset(
            allowed
        )

    def create_report(
        self,
        report_path,
        report
    ):

        Path(report_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as file:

            for key, value in report.items():

                file.write(
                    f"{key}: {value}\n"
                )

    def validate(self, df):

        logger.info(
            "Validation Started"
        )

        missing_columns = (
            self.validate_columns(df)
        )

        missing_values = (
            self.validate_missing_values(df)
        )

        duplicate_ids = (
            self.validate_duplicate_ids(df)
        )

        flower_size_valid = (
            self.validate_flower_size(df)
        )

        species_valid = (
            self.validate_species_code(df)
        )

        status = (
            len(missing_columns) == 0
            and missing_values == 0
            and duplicate_ids == 0
            and flower_size_valid
            and species_valid
        )

        report = {
            "status":
                "PASS"
                if status
                else "FAIL",

            "missing_columns":
                missing_columns,

            "missing_values":
                missing_values,

            "duplicate_ids":
                duplicate_ids,

            "flower_size_valid":
                flower_size_valid,

            "species_valid":
                species_valid
        }

        self.create_report(
            "data/reports/validation_report.txt",
            report
        )

        logger.success(
            "Validation Completed"
        )

        return report