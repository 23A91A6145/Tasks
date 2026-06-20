import pandas as pd

from agents.recovery import RecoveryAgent
from agents.validator import ValidatorAgent


def main():

    recovery = RecoveryAgent()

    validator = ValidatorAgent()

    bad_data = pd.DataFrame({

        "Id": [1, 1, 2],

        "SepalLengthCm":
            [5.1, -4.5, None],

        "SepalWidthCm":
            [3.5, 3.0, 3.2],

        "PetalLengthCm":
            [1.4, 1.4, 1.3],

        "PetalWidthCm":
            [0.2, 0.2, 0.2],

        "Species":
            [
                "Iris-setosa",
                "Iris-setosa",
                "Iris-setosa"
            ],

        "TotalLength":
            [6.5, -5.9, None],

        "TotalWidth":
            [3.7, 3.2, 3.4],

        "FlowerSize":
            [10.2, -2.7, None],

        "SpeciesCode":
            [0, 9, 0]
    })

    print("\n")
    print("=" * 50)
    print("BEFORE RECOVERY")
    print("=" * 50)

    print(bad_data)

    fixed_df = recovery.recover(
        bad_data
    )

    print("\n")
    print("=" * 50)
    print("AFTER RECOVERY")
    print("=" * 50)

    print(fixed_df)

    report = validator.validate(
        fixed_df
    )

    print("\n")
    print("=" * 50)
    print("VALIDATION AFTER RECOVERY")
    print("=" * 50)

    print(report)


if __name__ == "__main__":
    main()