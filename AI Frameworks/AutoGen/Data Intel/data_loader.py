import pandas as pd
from pathlib import Path


def load_sales_data():

    # Project-relative path (portable)
    path = Path("data") / "sales.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find: {path.resolve()}"
        )

    df = pd.read_csv(path)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    print("\nLoaded Columns:")
    print(df.columns.tolist())

    required_columns = [
        "month",
        "revenue",
        "customers"
    ]

    missing = [
        c for c in required_columns
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}\n"
            f"Found columns: {df.columns.tolist()}"
        )

    revenue_growth = round(
        (
            (df["revenue"].iloc[-1]
             - df["revenue"].iloc[0])
            / df["revenue"].iloc[0]
        ) * 100,
        2
    )

    customer_growth = round(
        (
            (df["customers"].iloc[-1]
             - df["customers"].iloc[0])
            / df["customers"].iloc[0]
        ) * 100,
        2
    )

    summary = {
        "rows": len(df),

        "columns": df.columns.tolist(),

        "missing_values":
            df.isnull().sum().to_dict(),

        "duplicates":
            int(df.duplicated().sum()),

        "revenue_growth_percent":
            revenue_growth,

        "customer_growth_percent":
            customer_growth,
    }

    return df, summary