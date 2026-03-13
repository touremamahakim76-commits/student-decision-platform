import requests
import pandas as pd

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def run_overpass(query: str):
    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
    response.raise_for_status()
    return response.json()

def elements_to_df(elements):
    rows = []
    for el in elements:
        tags = el.get("tags", {})
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        rows.append({
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "nom": tags.get("name", ""),
            "adresse": tags.get("addr:full", ""),
            "rue": tags.get("addr:street", ""),
            "code_postal": tags.get("addr:postcode", ""),
            "ville": tags.get("addr:city", ""),
            "lat": lat,
            "lon": lon
        })
    return pd.DataFrame(rows)

query_univ = """
[out:json][timeout:60];
area[name="Paris"]->.a;
(
  node["amenity"="university"](area.a);
  way["amenity"="university"](area.a);
  relation["amenity"="university"](area.a);
);
out center tags;
"""

if __name__ == "__main__":
    data = run_overpass(query_univ)
    df = elements_to_df(data.get("elements", []))
    df = df[df["nom"] != ""].reset_index(drop=True)
    df.to_csv("Données/raw/universites_paris_osm.csv", index=False, encoding="utf-8")
    print("Extraction terminée : universites_paris_osm.csv")
