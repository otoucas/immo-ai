import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import leafmap.foliumap as leafmap
import requests
import json
from datetime import datetime, timedelta

# Mise en cache des données pour éviter de refaire des requêtes à chaque rafraîchissement
@st.cache_data(ttl=3600)  # Cache valide 1 heure
def fetch_dpe_data(etiquette_dpe="D", etiquette_ges="D", surface_min=210, surface_max=217, code_postal="01"):
    base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/full"
    params = {
        "etiquette_dpe_search": etiquette_dpe,
        "etiquette_ges_search": etiquette_ges,
        "surface_habitable_logement_gte": surface_min,
        "surface_habitable_logement_lte": surface_max,
        "code_postal_ban_starts": code_postal,
        "sort": "-surface_habitable_logement",
        "rows": 1000,  # Limite le nombre de résultats pour éviter les temps de chargement trop longs
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])
        df = pd.DataFrame([r["fields"] for r in records])
        return df
    else:
        st.error(f"Erreur lors de la récupération des données: {response.status_code}")
        return pd.DataFrame()

# Interface Streamlit
st.title("Recherche de biens DPE/GES")

# Filtres
st.sidebar.header("Filtres")
dpe_filter = st.sidebar.multiselect("Étiquette DPE", options=["A", "B", "C", "D", "E", "F", "G"], default=["D"])
ges_filter = st.sidebar.multiselect("Étiquette GES", options=["A", "B", "C", "D", "E", "F", "G"], default=["D"])
surface_min = st.sidebar.number_input("Surface min (m²)", min_value=0, value=210)
surface_max = st.sidebar.number_input("Surface max (m²)", min_value=0, value=217)
code_postal = st.sidebar.text_input("Code postal", value="01")

# Récupérer les données
df = fetch_dpe_data(
    etiquette_dpe=",".join(dpe_filter),
    etiquette_ges=",".join(ges_filter),
    surface_min=surface_min,
    surface_max=surface_max,
    code_postal=code_postal,
)

# Afficher le tableau
st.dataframe(df, use_container_width=True)

# Carte
st.header("Carte")
m = leafmap.Map(center=[46, 2], zoom=6)
m.add_basemap("SATELLITE")

# Ajouter les points sur la carte
for _, row in df.iterrows():
    if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
        popup = f"""
        <b>Adresse:</b> {row.get('adresse_ban', 'N/A')} <br>
        <b>DPE:</b> {row.get('etiquette_dpe', 'N/A')} <br>
        <b>GES:</b> {row.get('etiquette_ges', 'N/A')} <br>
        <b>Surface:</b> {row.get('surface_habitable_logement', 'N/A')} m² <br>
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup,
        ).add_to(m)

# Afficher la carte
st_folium(m, width=700, height=500)

# Ajouter une couche cadastrale
st.sidebar.checkbox("Afficher les parcelles cadastrales", key="cadastral")
if st.session_state.cadastral:
    cadastral_url = "https://wxs.ign.fr/cadastre/geoportail/wms?"
    m.add_wms_layer(
        url=cadastral_url,
        layers="CADASTRALPARCELLES",
        name="Parcelles cadastrales",
        format="image/png",
        transparent=True,
    )
