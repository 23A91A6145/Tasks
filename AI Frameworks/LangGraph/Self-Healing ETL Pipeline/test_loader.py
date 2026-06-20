from agents.extractor import ExtractorAgent
from agents.cleaner import CleanerAgent
from agents.transformer import TransformerAgent
from agents.validator import ValidatorAgent
from agents.loader import LoaderAgent


def main():

    extractor = ExtractorAgent()

    cleaner = CleanerAgent()

    transformer = TransformerAgent()

    validator = ValidatorAgent()

    loader = LoaderAgent()

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

    if report["status"] == "PASS":

        result = loader.load(
            transformed
        )

        print("\n")

        print("=" * 50)

        print("DATABASE LOAD REPORT")

        print("=" * 50)

        for key, value in result.items():

            print(
                f"{key}: {value}"
            )

    else:

        print(
            "Validation Failed"
        )


if __name__ == "__main__":
    main()