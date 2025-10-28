import streamlit as st
from api_ademe import fetch_dpe_data
from map_utils import create_map
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("🏡 Recherche de biens immobiliers (DPE/GES + Prix de vente + Cadastral)")

# Filtres dans la sidebar
with st.sidebar:
    st.header("🔍 Filtres")
    dpe_filter = st.multiselect(
        "Étiquette DPE",
        options=["A", "B", "C", "D", "E", "F", "G"],
        default=["D"]
    )
    ges_filter = st.multiselect(
        "Étiquette GES",
        options=["A", "B", "C", "D", "E", "F", "G"],
        default=["D"]
    )
    surface_min, surface_max = st.slider(
        "Surface (m²)",
        min_value=0,
        max_value=500,
        value=(210, 217)
    )
    code_postal = st.text_input("Code postal", value="01")

    # Option pour afficher les parcelles cadastrales
    show_cadastral = st.checkbox("Afficher les parcelles cadastrales", value=True)

# Récupérer les données DPE/GES
with st.spinner("Chargement des données DPE/GES..."):
    df = fetch_dpe_data(
        etiquette_dpe=",".join(dpe_filter),
        etiquette_ges=",".join(ges_filter),
        surface_min=surface_min,
        surface_max=surface_max,
        code_postal=code_postal,
    )

# Afficher le tableau des résultats
st.subheader("📊 Résultats")
if df.empty:
    st.warning("Aucun résultat trouvé pour les filtres sélectionnés.")
else:
    st.dataframe(df, use_container_width=True)

    # Afficher la carte
    st.subheader("🗺️ Carte interactive")
    m = create_map(df, show_cadastral=show_cadastral)
    m.to_streamlit(width=700, height=500)

# Pied de page
st.markdown("---")
st.caption("Données : ADEME (DPE/GES) & DVF (Prix de vente) | Cadastral : IGN")
