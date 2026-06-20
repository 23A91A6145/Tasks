from agents.extractor import ExtractorAgent
from agents.cleaner import CleanerAgent
from agents.transformer import TransformerAgent


def main():

    extractor = ExtractorAgent()

    cleaner = CleanerAgent()

    transformer = TransformerAgent()

    extracted = extractor.extract(
        "data/raw/iris.csv"
    )

    cleaned_df = cleaner.clean(
        extracted["data"]
    )

    transformed_df = transformer.transform(
        cleaned_df
    )

    transformer.save_transformed_data(
        transformed_df,
        "data/transformed/iris_transformed.csv"
    )

    print("\n")

    print("=" * 50)
    print("TRANSFORMATION SUMMARY")
    print("=" * 50)

    print(
        f"Rows: {len(transformed_df)}"
    )

    print(
        f"Columns: {len(transformed_df.columns)}"
    )

    print("\nNew Columns Added:")

    print(
        "TotalLength"
    )

    print(
        "TotalWidth"
    )

    print(
        "FlowerSize"
    )

    print(
        "SpeciesCode"
    )

    print("\n")

    print(
        transformed_df.head()
    )


if __name__ == "__main__":
    main()