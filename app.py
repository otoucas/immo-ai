import streamlit as st
from api_ademe import fetch_dpe_data
from map_utils import create_map, extract_postal_codes_from_click
from filter_utils import load_filters, save_filters, delete_filter

# Configuration de la page
st.set_page_config(layout="wide")
st.title("🏡 Recherche immobilière ultra-légère")

# Initialiser les codes postaux et les filtres dans session_state
if "codes_postaux" not in st.session_state:
    st.session_state.codes_postaux = ["01"]
if "dpe_filter" not in st.session_state:
    st.session_state.dpe_filter = []
if "ges_filter" not in st.session_state:
    st.session_state.ges_filter = []

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
        st.session_state.codes_postaux = current_filter.get("codes_postaux", ["01"])
        st.session_state.dpe_filter = current_filter.get("dpe", [])
        st.session_state.ges_filter = current_filter.get("ges", [])
        surface_min = current_filter.get("surface_min", 0)
        surface_max = current_filter.get("surface_max", 500)
    else:
        current_filter = {
            "dpe": [],
            "ges": [],
            "surface_min": 0,
            "surface_max": 500,
            "codes_postaux": st.session_state.codes_postaux,
        }
        surface_min = 0
        surface_max = 500

    # Filtres interactifs (cases à cocher pour DPE/GES)
    st.subheader("Étiquettes DPE")
    dpe_options = ["A", "B", "C", "D", "E", "F", "G"]
    for option in dpe_options:
        if st.checkbox(f"{option}", value=option in st.session_state.dpe_filter, key=f"dpe_{option}"):
            if option not in st.session_state.dpe_filter:
                st.session_state.dpe_filter.append(option)
        else:
            if option in st.session_state.dpe_filter:
                st.session_state.dpe_filter.remove(option)

    st.subheader("Étiquettes GES")
    for option in dpe_options:
        if st.checkbox(f"{option}", value=option in st.session_state.ges_filter, key=f"ges_{option}"):
            if option not in st.session_state.ges_filter:
                st.session_state.ges_filter.append(option)
        else:
            if option in st.session_state.ges_filter:
                st.session_state.ges_filter.remove(option)

    # Champs pour la surface (min et max)
    col1, col2 = st.columns(2)
    with col1:
        surface_min = st.number_input("Surface min (m²)", min_value=0, value=current_filter.get("surface_min", 0))
    with col2:
        surface_max = st.number_input("Surface max (m²)", min_value=0, value=current_filter.get("surface_max", 500))

    # Options d'affichage (parcelles décochées par défaut)
    show_cadastral = st.checkbox("Afficher les parcelles cadastrales", value=False)

    # Sauvegarder ou supprimer un filtre
    new_filter_name = st.text_input("Nom du filtre (pour sauvegarder)")
    if st.button("Sauvegarder le filtre"):
        if new_filter_name:
            saved_filters[new_filter_name] = {
                "dpe": st.session_state.dpe_filter,
                "ges": st.session_state.ges_filter,
                "surface_min": surface_min,
                "surface_max": surface_max,
                "codes_postaux": st.session_state.codes_postaux,
            }
            save_filters(saved_filters)
            st.success(f"Filtre '{new_filter_name}' sauvegardé !")
        else:
            st.error("Veuillez donner un nom au filtre.")

# Affichage des filtres en cours et suppression
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Filtres actifs")
st.sidebar.markdown(f"""
- **DPE:** {', '.join(st.session_state.dpe_filter) if st.session_state.dpe_filter else 'Aucun'}
- **GES:** {', '.join(st.session_state.ges_filter) if st.session_state.ges_filter else 'Aucun'}
- **Surface:** {surface_min} - {surface_max} m²
- **Codes postaux:** {', '.join(st.session_state.codes_postaux)}
""")

# Suppression des filtres depuis la zone d'affichage
if saved_filters:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Supprimer un filtre")
    for filter_name in saved_filters.keys():
        if st.sidebar.button(f"Supprimer {filter_name}", key=f"delete_{filter_name}"):
            if delete_filter(filter_name):
                st.sidebar.success(f"Filtre '{filter_name}' supprimé !")
                st.experimental_rerun()
            else:
                st.sidebar.error("Erreur lors de la suppression.")

# Récupérer les données DPE/GES
with st.spinner("Chargement des données..."):
    records = []
    for code in st.session_state.codes_postaux:
        records.extend(fetch_dpe_data(
            etiquette_dpe=",".join(st.session_state.dpe_filter) if st.session_state.dpe_filter else None,
            etiquette_ges=",".join(st.session_state.ges_filter) if st.session_state.ges_filter else None,
            surface_min=surface_min,
            surface_max=surface_max,
            code_postal=code,
        ))

# Afficher les résultats
st.subheader("📊 Résultats")
if not records:
    st.warning("Aucun résultat trouvé.")
else:
    st.json(records)  # Affiche les données sous forme de JSON

    # Afficher la carte (avec une clé pour forcer le rafraîchissement)
    st.subheader("🗺️ Carte interactive")
    m = create_map(records, show_cadastral=show_cadastral)
    map_data = st_folium(m, width=700, height=500, key=f"map_{len(records)}")

    # Gérer les clics pour ajouter des codes postaux
    if map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        postal_code = extract_postal_codes_from_click(lat, lon)
        if postal_code and postal_code not in st.session_state.codes_postaux:
            st.session_state.codes_postaux = list(st.session_state.codes_postaux) + [postal_code]
            st.experimental_rerun()

# Pied de page
st.markdown("---")
st.caption("Données : ADEME (DPE/GES) | Cadastral : IGN")
