import leafmap.foliumap as leafmap
import folium
import requests
from api_dvf import get_last_sale_price
from streamlit_folium import st_folium
from folium.plugins import Draw

def get_communes_geojson(code_postal):
    """Récupère les limites communales pour un code postal donné (via Nominatim)."""
    url = f"https://nominatim.openstreetmap.org/search?postalcode={code_postal}&country=France&format=geojson&polygon_geojson=1"
    response = requests.get(url, headers={"User-Agent": "immo-ai/1.0"})
    if response.status_code == 200:
        return response.json()
    return None

def reverse_geocode(lat, lon):
    """Récupère le code postal à partir de coordonnées (lat, lon) via Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
    response = requests.get(url, headers={"User-Agent": "immo-ai/1.0"})
    if response.status_code == 200:
        data = response.json()
        return data.get("address", {}).get("postcode")
    return None

def create_map(df, show_cadastral=False, show_communes=False, selected_codes_postaux=[]):
    """Crée une carte avec marqueurs, parcelles cadastrales, et limites communales."""
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

    # Ajouter les limites communales
    if show_communes and selected_codes_postaux:
        for code in selected_codes_postaux:
            geojson = get_communes_geojson(code)
            if geojson:
                folium.GeoJson(
                    geojson,
                    name=f"Limites communales ({code})",
                    style_function=lambda x: {"color": "red", "weight": 2, "fillOpacity": 0},
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

def extract_postal_codes_from_geojson(geojson):
    """Extrait les codes postaux depuis un GeoJSON (zone dessinée)."""
    if geojson["geometry"]["type"] == "Polygon":
        coords = geojson["geometry"]["coordinates"][0]
        centroid_lat = sum([c[1] for c in coords]) / len(coords)
        centroid_lon = sum([c[0] for c in coords]) / len(coords)
        return reverse_geocode(centroid_lat, centroid_lon)
    return None
