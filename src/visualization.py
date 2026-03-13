import pandas as pd
import matplotlib.pyplot as plt

def plot_city_distribution(path: str, output_path: str):
    df = pd.read_csv(path)

    if "ville" not in df.columns:
        print("Column 'ville' not found.")
        return

    counts = df["ville"].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    counts.plot(kind="bar")
    plt.title("Top 10 cities in dataset")
    plt.xlabel("City")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    plot_city_distribution(
        "Données/processed/universites_paris_osm_clean.csv",
        "visualisation/city_distribution.png"
    )
