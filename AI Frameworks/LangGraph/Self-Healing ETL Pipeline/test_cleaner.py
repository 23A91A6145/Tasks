from agents.extractor import ExtractorAgent

from agents.cleaner import CleanerAgent


def main():

    extractor = ExtractorAgent()

    cleaner = CleanerAgent()

    extracted = extractor.extract(
        "data/raw/iris.csv"
    )

    df = extracted["data"]

    cleaned_df = cleaner.clean(df)

    cleaner.save_cleaned_data(
        cleaned_df,
        "data/cleaned/iris_cleaned.csv"
    )

    print("\n")

    print("=" * 50)

    print("CLEANING SUMMARY")

    print("=" * 50)

    print(
        f"Rows: {len(cleaned_df)}"
    )

    print(
        f"Columns: {len(cleaned_df.columns)}"
    )

    print(
        f"Missing Values: "
        f"{cleaned_df.isnull().sum().sum()}"
    )

    print("\n")

    print(
        cleaned_df.head()
    )


if __name__ == "__main__":
    main()