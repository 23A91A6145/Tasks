from agents.extractor import ExtractorAgent


def main():

    extractor = ExtractorAgent()

    result = extractor.extract(
        "data/raw/iris.csv"
    )

    print("\n")

    print("=" * 50)
    print("STATUS")
    print("=" * 50)

    print(result["status"])

    print("\n")

    print("=" * 50)
    print("METADATA")
    print("=" * 50)

    for key, value in result["metadata"].items():
        print(f"{key}: {value}")

    print("\n")

    print("=" * 50)
    print("FIRST 5 ROWS")
    print("=" * 50)

    print(result["data"].head())


if __name__ == "__main__":
    main()