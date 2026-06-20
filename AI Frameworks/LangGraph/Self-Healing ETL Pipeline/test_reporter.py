from agents.extractor import ExtractorAgent
from agents.cleaner import CleanerAgent
from agents.transformer import TransformerAgent
from agents.validator import ValidatorAgent
from agents.loader import LoaderAgent
from agents.reporter import ReporterAgent


def main():

    extractor = ExtractorAgent()

    cleaner = CleanerAgent()

    transformer = TransformerAgent()

    validator = ValidatorAgent()

    loader = LoaderAgent()

    reporter = ReporterAgent()

    extracted = extractor.extract(
        "data/raw/iris.csv"
    )

    cleaned = cleaner.clean(
        extracted["data"]
    )

    transformed = transformer.transform(
        cleaned
    )

    validation = validator.validate(
        transformed
    )

    load_result = loader.load(
        transformed
    )

    report = reporter.generate_report(
        validation,
        rows_processed=len(
            transformed
        ),
        rows_loaded=load_result[
            "rows_loaded"
        ]
    )

    print("\n")

    print("=" * 60)

    print(
        "PIPELINE REPORT"
    )

    print("=" * 60)

    for key, value in report.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()