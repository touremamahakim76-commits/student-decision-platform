

import pandas as pd
from sqlalchemy import create_engine
from math import radians, cos, sin, asin, sqrt

# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================
DATA_PATH = "data/"

MYSQL_USER = "root"
MYSQL_PASSWORD = "Taimer123*"
MYSQL_HOST = "localhost"
MYSQL_DB = "vie_etudiante"


# ============================================================
# OUTIL : DISTANCE HAVERSINE (km)
# ============================================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c


# ============================================================
# 1️⃣ LOGEMENTS – DVF
# ============================================================
def clean_logements():
    print("🔄 Nettoyage logements (DVF)")

    df = pd.read_csv(
        DATA_PATH + "dvf.csv",
        sep=",",
        low_memory=False,
        usecols=[
            "type_local",
            "surface_reelle_bati",
            "valeur_fonciere",
            "latitude",
            "longitude"
        ]
    )

    df = df[df["type_local"] == "Appartement"]

    df = df[
        (df["surface_reelle_bati"] > 0) &
        (df["valeur_fonciere"] > 0) &
        (df["latitude"].notna()) &
        (df["longitude"].notna())
    ]

    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

    df = df[["latitude", "longitude", "prix_m2", "surface_reelle_bati"]]
    df.columns = ["lat", "lon", "prix_m2", "surface"]

    df = df.drop_duplicates(subset=["lat", "lon", "prix_m2"])

    df.to_csv(DATA_PATH + "logements_clean.csv", index=False)
    print("✅ logements_clean.csv généré")


# ============================================================
# 2️⃣ BIBLIOTHÈQUES
# ============================================================
def clean_bibliotheques():
    print("🔄 Nettoyage bibliothèques")

    df = pd.read_csv(DATA_PATH + "repertoire-bibliotheques.csv", sep=";")
    df = df[df["commune"].astype(str).str.lower() == "paris"]
    df = df[["nometablissement", "geo"]].dropna()

    df[["lat", "lon"]] = df["geo"].str.split(",", expand=True)
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    df = df.rename(columns={"nometablissement": "nom"})
    df = df[["nom", "lat", "lon"]].drop_duplicates()

    df.to_csv(DATA_PATH + "bibliotheques_clean.csv", index=False)
    print("✅ bibliotheques_clean.csv généré")


# ============================================================
# 3️⃣ UNIVERSITÉS
# ============================================================
def clean_universites():
    print("🔄 Nettoyage universités")

    df = pd.read_csv(DATA_PATH + "universites.csv", sep=";")
    df = df[["uo_lib", "coordonnees"]].dropna()

    def extract_lat_lon(x):
        if isinstance(x, tuple):
            return x[0], x[1]
        if isinstance(x, str):
            lat, lon = x.strip("()").split(",")
            return float(lat), float(lon)
        return None, None

    df[["lat", "lon"]] = df["coordonnees"].apply(
        lambda x: pd.Series(extract_lat_lon(x))
    )

    df = df.rename(columns={"uo_lib": "nom"})
    df = df[["nom", "lat", "lon"]].dropna().drop_duplicates()

    df.to_csv(DATA_PATH + "universites_clean.csv", index=False)
    print("✅ universites_clean.csv généré")


# ============================================================
# 4️⃣ MYSQL (PYTHON ONLY)
# ============================================================
def load_to_mysql():
    print("🔄 Envoi des données vers MySQL")

    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )

    pd.read_csv(DATA_PATH + "logements_clean.csv").to_sql(
        "logements", engine, if_exists="replace", index=False
    )
    pd.read_csv(DATA_PATH + "bibliotheques_clean.csv").to_sql(
        "bibliotheques", engine, if_exists="replace", index=False
    )
    pd.read_csv(DATA_PATH + "universites_clean.csv").to_sql(
        "universites", engine, if_exists="replace", index=False
    )

    print("✅ Données insérées dans MySQL")


# ============================================================
# 5️⃣ ANALYSE + SCORE QUALITÉ DE VIE
# ============================================================
def analyse_universite(nom_universite):
    print(f"\n📊 Analyse pour : {nom_universite}")

    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )

    logements = pd.read_sql("SELECT * FROM logements", engine)
    biblios = pd.read_sql("SELECT * FROM bibliotheques", engine)
    universites = pd.read_sql("SELECT * FROM universites", engine)

    uni = universites[universites["nom"] == nom_universite].iloc[0]

    logements["dist_uni"] = logements.apply(
        lambda r: haversine(uni.lat, uni.lon, r.lat, r.lon), axis=1
    )

    biblios["dist_uni"] = biblios.apply(
        lambda r: haversine(uni.lat, uni.lon, r.lat, r.lon), axis=1
    )

    dist_biblio = biblios["dist_uni"].min()

    logements["score"] = (
        100
        - (logements["prix_m2"] / 100)
        - (logements["dist_uni"] * 10)
        - (dist_biblio * 5)
    )

    logements = logements.sort_values("score", ascending=False)

    print("\n🏠 Top logements recommandés :")
    print(logements.head(5))


# ============================================================
# 🚀 PIPELINE COMPLET
# ============================================================
if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE PIPELINE GLOBAL\n")

    clean_logements()
    clean_bibliotheques()
    clean_universites()
    load_to_mysql()

    # Exemple d’analyse
    analyse_universite("Sorbonne Université")

    print("\n🎉 PIPELINE COMPLET TERMINÉ AVEC SUCCÈS")
