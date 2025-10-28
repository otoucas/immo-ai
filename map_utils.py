import leafmap.foliumap as leafmap
import folium
from api_dvf import get_last_sale_price

def create_map(df):
    """
    Crée une carte Folium/Leafmap avec les données DPE/GES et les prix de vente DVF.
    """
    m = leafmap.Map(center=[46, 2], zoom=6)
    m.add_basemap("SATELLITE")  # Vue satellite par défaut

    for _, row in df.iterrows():
        if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
            # Récupérer le dernier prix de vente via l'API DVF
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

    # Ajouter les parcelles cadastrales (WMS IGN)
    cadastral_url = "https://wxs.ign.fr/cadastre/geoportail/wms"
    m.add_wms_layer(
        url=cadastral_url,
        layers="CADASTRALPARCELLES",
        name="Parcelles cadastrales",
        format="image/png",
        transparent=True,
    )

    return m
