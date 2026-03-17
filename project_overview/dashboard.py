import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from math import radians, cos, sin, asin, sqrt
import folium
from streamlit_folium import st_folium

# ============================================================
# CONFIG MYSQL
# ============================================================
engine = create_engine(
    "mysql+pymysql://root:Taimer123*@localhost/vie_etudiante"
)

# ============================================================
# OUTILS
# ============================================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return 6371*c

def format_distance(km):
    if km < 1:
        return f"{int(km * 1000)} m"
    return f"{km:.1f} km"

def format_number(n):
    return f"{int(n):,}".replace(",", " ")

def format_euro(n):
    return f"{format_number(n)} €"

def clamp(x, min_val=0, max_val=20):
    return max(min_val, min(x, max_val))

# ============================================================
# CONFIG PAGE
# ============================================================
st.set_page_config(page_title="Vie étudiante à Paris", layout="wide")

# ============================================================
# CHARGEMENT DONNÉES PARIS
# ============================================================
@st.cache_data
def load_data():

    logements = pd.read_sql(
        """
        SELECT *
        FROM logements
        WHERE lat BETWEEN 48.80 AND 48.90
          AND lon BETWEEN 2.25 AND 2.42
          AND prix_m2 IS NOT NULL
          AND prix_m2 > 0
        """,
        engine
    )

    biblios = pd.read_sql(
        """
        SELECT *
        FROM bibliotheques
        WHERE lat BETWEEN 48.80 AND 48.90
          AND lon BETWEEN 2.25 AND 2.42
        """,
        engine
    )

    universites = pd.read_sql(
        """
        SELECT *
        FROM universites
        WHERE lat BETWEEN 48.80 AND 48.90
          AND lon BETWEEN 2.25 AND 2.42
        """,
        engine
    )

    return logements, biblios, universites


logements, biblios, universites = load_data()

if logements.empty or biblios.empty or universites.empty:
    st.error("Données insuffisantes pour Paris")
    st.stop()

# ============================================================
# TITRE
# ============================================================
st.title("🎓 Vie étudiante à Paris")
st.caption("Recherche par université – logements et bibliothèques proches")

# ============================================================
# RECHERCHE UNIVERSITÉ
# ============================================================
search_uni = st.text_input("🔎 Rechercher une université")

filtered_unis = universites["nom"].unique()

if search_uni:
    filtered_unis = [
        u for u in filtered_unis
        if search_uni.lower() in u.lower()
    ]

uni_name = st.selectbox(
    "Choisir une université",
    sorted(filtered_unis)
)

uni = universites[universites["nom"] == uni_name].iloc[0]

# ============================================================
# CALCUL DISTANCES
# ============================================================
logements = logements.copy()
biblios = biblios.copy()

logements["distance"] = logements.apply(
    lambda r: haversine(uni.lat, uni.lon, r.lat, r.lon), axis=1
)

biblios["distance"] = biblios.apply(
    lambda r: haversine(uni.lat, uni.lon, r.lat, r.lon), axis=1
)

# ============================================================
# ESTIMATION LOYER
# ============================================================
logements["loyer_estime"] = (logements["prix_m2"] * logements["surface"] * 0.04) / 12

logements = logements[
    (logements["loyer_estime"] > 200) &
    (logements["loyer_estime"] < 3000)
]

# ============================================================
# SCORE QUALITÉ DE VIE
# ============================================================
logements["score"] = logements.apply(
    lambda r: clamp(
        20
        - r["distance"] * 4
        - r["loyer_estime"] / 500,
    ),
    axis=1
)

logements = logements.sort_values("score", ascending=False)

# ============================================================
# BIBLIOTHÈQUES PROCHES
# ============================================================
st.subheader("📚 Bibliothèques les plus proches")

biblios_proches = biblios.sort_values("distance").head(5)

st.dataframe(
    pd.DataFrame({
        "Nom": biblios_proches["nom"],
        "Distance": biblios_proches["distance"].apply(format_distance),
        "Accès": "Gratuit"
    }),
    hide_index=True,
    use_container_width=True
)

# ============================================================
# LOGEMENTS PROCHES
# ============================================================
st.subheader("🏠 Logements proches de l’université")

st.dataframe(
    pd.DataFrame({
        "Surface (m²)": logements["surface"].astype(int),
        "Loyer estimé / mois": logements["loyer_estime"].apply(format_euro),
        "Distance université": logements["distance"].apply(format_distance),
        "Note": logements["score"].apply(lambda x: f"{x:.1f} / 20")
    }).head(20),
    hide_index=True,
    use_container_width=True
)

# ============================================================
# INDICATEURS
# ============================================================
c1, c2, c3 = st.columns(3)

c1.metric(
    "📚 Bibliothèque la plus proche",
    format_distance(biblios_proches.iloc[0]["distance"])
)

c2.metric(
    "🏠 Loyer moyen",
    format_euro(logements["loyer_estime"].mean())
)

c3.metric(
    "⭐ Meilleure note",
    f"{logements['score'].max():.1f} / 20"
)

# ============================================================
# CARTE
# ============================================================
st.subheader("🗺️ Carte des résultats")

m = folium.Map(location=[uni.lat, uni.lon], zoom_start=13)

folium.Marker(
    [uni.lat, uni.lon],
    popup=f"Université : {uni.nom}",
    icon=folium.Icon(color="red", icon="graduation-cap", prefix="fa")
).add_to(m)

for _, b in biblios_proches.iterrows():
    folium.Marker(
        [b.lat, b.lon],
        popup=b.nom,
        icon=folium.Icon(color="blue", icon="book", prefix="fa")
    ).add_to(m)

for _, l in logements.head(30).iterrows():
    folium.CircleMarker(
        [l.lat, l.lon],
        radius=3,
        color="green",
        fill=True,
        popup=f"{format_euro(l.loyer_estime)} / mois"
    ).add_to(m)

st_folium(m, width=1100, height=600)
