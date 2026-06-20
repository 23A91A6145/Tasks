from agents.extractor import ExtractorAgent
from agents.cleaner import CleanerAgent
from agents.transformer import TransformerAgent
from agents.validator import ValidatorAgent


def main():

    extractor = ExtractorAgent()

    cleaner = CleanerAgent()

    transformer = TransformerAgent()

    validator = ValidatorAgent()

    extracted = extractor.extract(
        "data/raw/iris.csv"
    )

    cleaned = cleaner.clean(
        extracted["data"]
    )

    transformed = transformer.transform(
        cleaned
    )

    report = validator.validate(
        transformed
    )

    print("\n")

    print("=" * 50)
    print("VALIDATION REPORT")
    print("=" * 50)

    for key, value in report.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()