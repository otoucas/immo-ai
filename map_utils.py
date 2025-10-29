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

def create_map(df, show_cadastral=False):
    """Crée une carte avec folium (ultra-léger)."""
    m = folium.Map(location=[46, 2], zoom_start=6, tiles="OpenStreetMap")

    # Ajouter les marqueurs pour chaque bien
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
