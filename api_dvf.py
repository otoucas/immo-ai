import requests
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=32)
def fetch_dvf_data(code_postal, adresse=None):
    """
    Récupère les dernières transactions immobilières (DVF) pour un code postal et une adresse donnés.
    """
    base_url = f"https://app.dvf.etalab.gouv.fr/data/full.csv"
    try:
        # Télécharger le fichier CSV complet (attention : gros fichier, ~1.5 Go)
        # Pour une utilisation en production, il faudrait utiliser une API ou un extrait local.
        # Ici, on simule avec un exemple simplifié (à remplacer par une vraie requête API si disponible).
        # En pratique, il faudrait filtrer localement ou utiliser un service comme :
        # https://github.com/etalab/data.gouv.fr-dvf
        df = pd.read_csv(base_url, sep=";", low_memory=False)

        # Filtrer par code postal et adresse (si fournie)
        if adresse:
            df = df[
                (df["Code postal"].astype(str).str.startswith(code_postal)) &
                (df["Adresse"].str.contains(adresse, case=False, na=False))
            ]
        else:
            df = df[df["Code postal"].astype(str).str.startswith(code_postal)]

        # Retourner les 5 dernières transactions
        return df.sort_values("Date mutation", ascending=False).head(5)

    except Exception as e:
        print(f"Erreur lors de la récupération des données DVF: {e}")
        return pd.DataFrame()

def get_last_sale_price(code_postal, adresse):
    """
    Récupère le dernier prix de vente pour une adresse donnée.
    """
    df = fetch_dvf_data(code_postal, adresse)
    if not df.empty:
        return df.iloc[0]["Valeur foncière"]
    return None
