import requests
from functools import lru_cache

@lru_cache(maxsize=32)
def fetch_dpe_data(etiquette_dpe=None, etiquette_ges=None, surface_min=0, surface_max=500, code_postal="01"):
    """Récupère les données DPE/GES et retourne une liste de dictionnaires."""
    base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/full"
    params = {
        "surface_habitable_logement_gte": surface_min,
        "surface_habitable_logement_lte": surface_max,
        "code_postal_ban_starts": code_postal,
        "sort": "-surface_habitable_logement",
        "rows": 100,
    }

    # Ajouter les filtres DPE/GES uniquement s'ils sont sélectionnés
    if etiquette_dpe:
        params["etiquette_dpe_search"] = etiquette_dpe
    if etiquette_ges:
        params["etiquette_ges_search"] = etiquette_ges

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("records", [])
    except Exception as e:
        print(f"Erreur lors de la récupération des données DPE: {e}")
        return []
