import json
import os
import streamlit as st

# Chemin pour sauvegarder les filtres
FILTERS_FILE = "saved_filters.json"

def load_filters():
    """Charge les filtres sauvegardés depuis un fichier JSON."""
    if os.path.exists(FILTERS_FILE):
        with open(FILTERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_filters(filters):
    """Sauvegarde les filtres dans un fichier JSON."""
    with open(FILTERS_FILE, "w") as f:
        json.dump(filters, f, indent=4)

def delete_filter(filter_name):
    """Supprime un filtre sauvegardé."""
    filters = load_filters()
    if filter_name in filters:
        del filters[filter_name]
        save_filters(filters)
        return True
    return False
