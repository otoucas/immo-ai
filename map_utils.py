import leafmap.foliumap as leafmap
import folium
from api_dvf import get_last_sale_price

def create_map(df, show_cadastral=False):
    """
    Crée une carte Folium/Leafmap avec :
    - Les données DPE/GES
    - Les prix de vente DVF
    - Option pour afficher les parcelles cadastrales
    """
    m = leafmap.Map(center=[46, 2], zoom=6)
    m.add_basemap("SATELLITE")  # Vue satellite par défaut

    # Ajouter les marqueurs pour chaque bien
    for _, row in df.iterrows():
        if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
            last_sale = get_last_sale_price(
                row.get("code_postal_ban", ""),
                row.get("adresse_ban", "")
            )

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

    # Ajouter les parcelles cadastrales si demandé
    if show_cadastral:
        cadastral_url = "https://wxs.ign.fr/cadastre/geoportail/wms"
        m.add_wms_layer(
            url=cadastral_url,
            layers="CADASTRALPARCELLES",
            name="Parcelles cadastrales",
            format="image/png",
            transparent=True,
            attribution="IGN"
        )

    return m
