import streamlit as st
from api_ademe import fetch_dpe_data
from map_utils import create_map
import pandas as pd

st.title("Recherche de biens DPE/GES avec prix de vente")

# Filtres
st.sidebar.header("Filtres")
dpe_filter = st.sidebar.multiselect("Étiquette DPE", options=["A", "B", "C", "D", "E", "F", "G"], default=["D"])
ges_filter = st.sidebar.multiselect("Étiquette GES", options=["A", "B", "C", "D", "E", "F", "G"], default=["D"])
surface_min = st.sidebar.number_input("Surface min (m²)", min_value=0, value=210)
surface_max = st.sidebar.number_input("Surface max (m²)", min_value=0, value=217)
code_postal = st.sidebar.text_input("Code postal", value="01")

# Récupérer les données DPE/GES
df = fetch_dpe_data(
    etiquette_dpe=",".join(dpe_filter),
    etiquette_ges=",".join(ges_filter),
    surface_min=surface_min,
    surface_max=surface_max,
    code_postal=code_postal,
)

# Afficher le tableau
st.dataframe(df, use_container_width=True)

# Afficher la carte
if not df.empty:
    m = create_map(df)
    m.to_streamlit(width=700, height=500)
else:
    st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
