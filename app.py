import streamlit as st
from api_ademe import fetch_dpe_data
from map_utils import create_map, get_communes_geojson
from filter_utils import load_filters, save_filters, delete_filter
import pandas as pd
import json

# Configuration de la page
st.set_page_config(layout="wide")
st.title("🏡 Recherche immobilière avancée (DPE/GES + Prix + Cadastral + Communes)")

# Charger les filtres sauvegardés
saved_filters = load_filters()

# Sidebar pour les filtres
with st.sidebar:
    st.header("🔍 Filtres")

    # Sélection des filtres sauvegardés
    filter_name = st.selectbox(
        "Charger un filtre sauvegardé",
        options=["Nouveau filtre"] + list(saved_filters.keys()),
    )

    if filter_name != "Nouveau filtre":
        current_filter = saved_filters[filter_name]
    else:
        current_filter = {
            "dpe": ["D"],
            "ges": ["D"],
            "surface": [210, 217],
            "codes_postaux": ["01"],
        }

    # Filtres interactifs
    dpe_filter = st.multiselect(
        "Étiquette DPE",
        options=["A", "B", "C", "D", "E", "F", "G"],
        default=current_filter.get("dpe", ["D"]),
    )
    ges_filter = st.multiselect(
        "Étiquette GES",
        options=["A", "B", "C", "D", "E", "F", "G"],
        default=current_filter.get("ges", ["D"]),
    )
    surface_range = st.slider(
        "Surface (m²)",
        min_value=0,
        max_value=500,
        value=current_filter.get("surface", [210, 217]),
    )
    codes_postaux = st.tags_input(
        "Codes postaux",
        value=current_filter.get("codes_postaux", ["01"]),
    )

    # Options d'affichage
    show_cadastral = st.checkbox("Afficher les parcelles cadastrales", value=True)
    show_communes = st.checkbox("Afficher les limites communales", value=True)

    # Sauvegarder ou supprimer un filtre
    new_filter_name = st.text_input("Nom du filtre (pour sauvegarder)")
    if st.button("Sauvegarder le filtre"):
        if new_filter_name:
            saved_filters[new_filter_name] = {
                "dpe": dpe_filter,
                "ges": ges_filter,
                "surface": list(surface_range),
                "codes_postaux": codes_postaux,
            }
            save_filters(saved_filters)
            st.success(f"Filtre '{new_filter_name}' sauvegardé !")
        else:
            st.error("Veuillez donner un nom au filtre.")

    if filter_name != "Nouveau filtre" and st.button("Supprimer le filtre"):
        if delete_filter(filter_name):
            st.success(f"Filtre '{filter_name}' supprimé !")
            st.experimental_rerun()
        else:
            st.error("Erreur lors de la suppression.")

# Affichage des filtres en cours
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Filtres actifs")
st.sidebar.markdown(f"""
- **DPE:** {', '.join(dpe_filter)}
- **GES:** {', '.join(ges_filter)}
- **Surface:** {surface_range[0]} - {surface_range[1]} m²
- **Codes postaux:** {', '.join(codes_postaux)}
""")

# Récupérer les données DPE/GES
with st.spinner("Chargement des données..."):
    df = pd.DataFrame()
    for code in codes_postaux:
        df_code = fetch_dpe_data(
            etiquette_dpe=",".join(dpe_filter),
            etiquette_ges=",".join(ges_filter),
            surface_min=surface_range[0],
            surface_max=surface_range[1],
            code_postal=code,
        )
        df = pd.concat([df, df_code], ignore_index=True)

# Afficher les résultats
st.subheader("📊 Résultats")
if df.empty:
    st.warning("Aucun résultat trouvé.")
else:
    st.dataframe(df, use_container_width=True)

    # Afficher la carte
    st.subheader("🗺️ Carte interactive")
    m = create_map(
        df,
        show_cadastral=show_cadastral,
        show_communes=show_communes,
        selected_codes_postaux=codes_postaux,
    )

    # Afficher la carte avec Streamlit
    map_data = st_folium(m, width=700, height=500)

    # Gérer les clics sur la carte pour ajouter des codes postaux
    if map_data.get("last_active_drawing"):
        st.write("Zone sélectionnée :", map_data["last_active_drawing"])
        # Ici, tu peux ajouter une logique pour extraire le code postal de la zone cliquée
        # et l'ajouter à la liste `codes_postaux`.

# Pied de page
st.markdown("---")
st.caption("Données : ADEME (DPE/GES), DVF (Prix), IGN (Cadastral/Communes)")
