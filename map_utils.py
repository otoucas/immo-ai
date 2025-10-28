import leafmap.foliumap as leafmap
import folium
import requests
import json
from api_dvf import get_last_sale_price
from streamlit_folium import st_folium
from folium.plugins import Draw

def get_communes_geojson(code_postal):
    """Récupère les limites communales pour un code postal donné (via API Nominatim ou IGN)."""
    # Exemple avec l'API Nominatim (OpenStreetMap)
    url = f"https://nominatim.openstreetmap.org/search?postalcode={code_postal}&country=France&format=geojson"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def create_map(df, show_cadastral=False, show_communes=False, selected_codes_postaux=[]):
    """Crée une carte avec marqueurs, parcelles cadastrales et limites communales."""
    m = leafmap.Map(center=[46, 2], zoom=6)
    m.add_basemap("SATELLITE")

    # Ajouter les marqueurs pour chaque bien
    for _, row in df.iterrows():
        if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
            last_sale = get_last_sale_price(row.get("code_postal_ban", ""), row.get("adresse_ban", ""))
            popup = f"""
            <b>Adresse:</b> {row.get('adresse_ban', 'N/A')} <br>
            <b>DPE:</b> {row.get('etiquette_dpe', 'N/A')} <br>
            <b>GES:</b> {row.get('etiquette_ges', 'N/A')} <br>
            <b>Surface:</b> {row.get('surface_habitable_logement', 'N/A')} m² <br>
            <b>Dernier prix de vente:</b> {last_sale} € <br>
            """
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=popup,
            ).add_to(m)

    # Ajouter les parcelles cadastrales
    if show_cadastral:
        cadastral_url = "https://wxs.ign.fr/cadastre/geoportail/wms"
        m.add_wms_layer(
            url=cadastral_url,
            layers="CADASTRALPARCELLES",
            name="Parcelles cadastrales",
            format="image/png",
            transparent=True,
        )

    # Ajouter les limites communales pour les codes postaux sélectionnés
    if show_communes and selected_codes_postaux:
        for code in selected_codes_postaux:
            geojson = get_communes_geojson(code)
            if geojson:
                folium.GeoJson(
                    geojson,
                    name=f"Limites communales ({code})",
                    style_function=lambda x: {"color": "red", "weight": 2, "fillOpacity": 0},
                ).add_to(m)

    # Ajouter un outil de dessin pour sélectionner des zones (clics)
    Draw(export=True).add_to(m)

    return m
