import pandas as pd

def basic_analysis(path: str):
    df = pd.read_csv(path)

    print("Number of rows:", len(df))
    print("Columns:", list(df.columns))

    if "ville" in df.columns:
        print("\nCount by city:")
        print(df["ville"].value_counts().head(10))

    print("\nDescriptive statistics:")
    print(df.describe(include="all"))

if __name__ == "__main__":
    basic_analysis("Données/processed/universites_paris_osm_clean.csv")
