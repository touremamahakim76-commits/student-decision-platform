import pandas as pd

def clean_dataset(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    # supprimer les lignes vides
    df = df.dropna(subset=["nom", "lat", "lon"])

    # enlever les doublons
    df = df.drop_duplicates()

    # normaliser quelques colonnes texte
    for col in ["nom", "ville", "adresse", "rue"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Dataset cleaned and saved to: {output_path}")

if __name__ == "__main__":
    clean_dataset(
        "Données/raw/universites_paris_osm.csv",
        "Données/processed/universites_paris_osm_clean.csv"
    )
