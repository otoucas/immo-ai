import requests
from functools import lru_cache

@lru_cache(maxsize=32)
def fetch_dpe_data(etiquette_dpe="D", etiquette_ges="D", surface_min=210, surface_max=217, code_postal="01"):
    """Récupère les données DPE/GES et retourne une liste de dictionnaires."""
    base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/full"
    params = {
        "etiquette_dpe_search": etiquette_dpe,
        "etiquette_ges_search": etiquette_ges,
        "surface_habitable_logement_gte": surface_min,
        "surface_habitable_logement_lte": surface_max,
        "code_postal_ban_starts": code_postal,
        "sort": "-surface_habitable_logement",
        "rows": 100,
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("records", [])
    except Exception as e:
        print(f"Erreur lors de la récupération des données DPE: {e}")
        return []
