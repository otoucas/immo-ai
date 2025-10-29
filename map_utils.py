import folium
import requests
from streamlit_folium import st_folium
from folium.plugins import Draw

def reverse_geocode(lat, lon):
    """Récupère le code postal depuis des coordonnées (lat, lon) via Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
    try:
        response = requests.get(url, headers={"User-Agent": "immo-ai/1.0"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("postcode")
    except Exception as e:
        print(f"Erreur lors du reverse geocoding: {e}")
    return None

def create_map(records, show_cadastral=False):
    """Crée une carte avec folium (sans pandas)."""
    m = folium.Map(location=[46, 2], zoom_start=6, tiles="OpenStreetMap")

    # Ajouter les marqueurs pour chaque bien
    for record in records:
        fields = record.get("fields", {})
        if "latitude" in fields and "longitude" in fields:
            popup = f"""
            <b>Adresse:</b> {fields.get('adresse_ban', 'N/A')} <br>
            <b>DPE:</b> {fields.get('etiquette_dpe', 'N/A')} <br>
            <b>GES:</b> {fields.get('etiquette_ges', 'N/A')} <br>
            <b>Surface:</b> {fields.get('surface_habitable_logement', 'N/A')} m² <br>
            """
            folium.Marker(
                location=[fields["latitude"], fields["longitude"]],
                popup=popup,
            ).add_to(m)

    # Ajouter les parcelles cadastrales (WMS IGN)
    if show_cadastral:
        cadastral_url = "https://wxs.ign.fr/cadastre/geoportail/wms"
        folium.WmsTileLayer(
            url=cadastral_url,
            layers="CADASTRALPARCELLES",
            name="Parcelles cadastrales",
            fmt="image/png",
            transparent=True,
        ).add_to(m)

    # Ajouter un outil de dessin pour sélectionner des zones
    Draw(
        export=True,
        position="topleft",
        draw_options={
            "polyline": False,
            "polygon": True,
            "rectangle": True,
            "circle": False,
            "marker": False,
        },
    ).add_to(m)

    return m

def extract_postal_codes_from_click(lat, lon):
    """Extrait le code postal depuis un clic sur la carte."""
    return reverse_geocode(lat, lon)
