import requests
import pandas as pd
from functools import lru_cache

# URL de l'API DVF (exemple avec l'API officielle ou un service comme https://github.com/etalab/data.gouv.fr-dvf)
DVF_API_URL = "https://api.dvf.etalab.gouv.fr/parcelles"

@lru_cache(maxsize=32)
def fetch_dvf_data(code_postal, adresse=None):
    """
    Récupère les dernières transactions immobilières (DVF) pour un code postal et une adresse donnés.
    Utilise l'API DVF officielle ou un service compatible.
    """
    params = {
        "code_postal": code_postal,
        "limit": 5,  # Limite le nombre de résultats
    }
    if adresse:
        params["adresse"] = adresse

    try:
        response = requests.get(DVF_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data.get("features", []))
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données DVF: {e}")
        return pd.DataFrame()

def get_last_sale_price(code_postal, adresse):
    """
    Récupère le dernier prix de vente pour une adresse donnée.
    """
    df = fetch_dvf_data(code_postal, adresse)
    if not df.empty:
        # Supposons que la réponse contient un champ "valeur_fonciere"
        return df.iloc[0].get("valeur_fonciere", "Non disponible")
    return "Non disponible"
