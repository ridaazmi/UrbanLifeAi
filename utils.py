import streamlit as st
import pandas as pd
import random
import json

# --- Génération de Données Synthétiques (Rabat) ---
@st.cache_data
def generate_rabat_data():
    """
    Génère un DataFrame de données synthétiques pour les quartiers de Rabat.
    """
    random.seed(42) # Pour la reproductibilité
    quartiers = [
        "Agdal", "Hay Riad", "Yacoub El Mansour", "L'Océan", 
        "Médina", "Souissi", "Hassan"
    ]
    
    # Coordonnées approximatives (Latitude, Longitude)
    coords = {
        "Agdal": (34.0043, -6.8506),
        "Hay Riad": (33.9655, -6.8768),
        "Yacoub El Mansour": (33.9950, -6.8800),
        "L'Océan": (34.0250, -6.8550),
        "Médina": (34.0280, -6.8360),
        "Souissi": (33.9750, -6.8200),
        "Hassan": (34.0200, -6.8300)
    }

    data = []
    for q in quartiers:
        # Logique de génération semi-réaliste
        if q in ["Souissi", "Hay Riad"]:
            pop = random.randint(10000, 30000)
            densite = random.randint(1000, 3000)
            chomage = random.uniform(5, 10)
            espaces_verts = random.randint(40000, 80000)
            vetuste = random.randint(0, 3)
            transport = random.randint(4, 8)
        elif q in ["Yacoub El Mansour", "L'Océan", "Médina"]:
            pop = random.randint(50000, 120000)
            densite = random.randint(10000, 25000)
            chomage = random.uniform(12, 22)
            espaces_verts = random.randint(1000, 10000)
            vetuste = random.randint(6, 9)
            transport = random.randint(6, 9)
        else: # Agdal, Hassan
            pop = random.randint(30000, 60000)
            densite = random.randint(5000, 15000)
            chomage = random.uniform(8, 15)
            espaces_verts = random.randint(10000, 30000)
            vetuste = random.randint(3, 6)
            transport = random.randint(8, 10)

        data.append({
            "Nom du quartier": q,
            "Population": pop,
            "Densité (hab/km²)": densite,
            "Taux de chômage (%)": round(chomage, 1),
            "Surface Espaces Verts (m²)": espaces_verts,
            "Indice de Vétusté (0-10)": vetuste,
            "Accessibilité Transports (0-10)": transport,
            "Accessibilité Santé (0-10)": random.randint(2, 9),
            "Accessibilité Education (0-10)": random.randint(3, 10),
            "Sécurité (0-10)": random.randint(4, 9),
            "lat": coords[q][0],
            "lon": coords[q][1]
        })
    
    return pd.DataFrame(data)

# --- Calcul d'Indicateurs ---
def calculate_vulnerability_score(df, w_social, w_infra, w_env, w_sante, w_educ, w_secu):
    """
    Calcule un score de vulnérabilité (0-100) basé sur des poids pondérés.
    Plus le score est élevé, plus le quartier est vulnérable.
    """
    df_calc = df.copy()
    
    # Normalisation des données
    norm_chomage = df_calc["Taux de chômage (%)"] / 25.0
    norm_vetuste = df_calc["Indice de Vétusté (0-10)"] / 10.0
    norm_transport = 1 - (df_calc["Accessibilité Transports (0-10)"] / 10.0)
    norm_verts = 1 - (df_calc["Surface Espaces Verts (m²)"] / 80000.0)
    norm_sante = 1 - (df_calc["Accessibilité Santé (0-10)"] / 10.0)
    norm_educ = 1 - (df_calc["Accessibilité Education (0-10)"] / 10.0)
    norm_secu = 1 - (df_calc["Sécurité (0-10)"] / 10.0)
    
    # Calcul du score brut pondéré
    score_brut = (
        w_social * norm_chomage +
        w_infra * (norm_vetuste + norm_transport) / 2 +
        w_env * norm_verts +
        w_sante * norm_sante +
        w_educ * norm_educ +
        w_secu * norm_secu
    )
    
    # Normalisation finale sur 100
    total_weight = w_social + w_infra + w_env + w_sante + w_educ + w_secu
    if total_weight == 0: total_weight = 1
    
    df_calc["Score Vulnérabilité"] = (score_brut / total_weight) * 100
    df_calc["Score Vulnérabilité"] = df_calc["Score Vulnérabilité"].round(1)
    
    return df_calc

# --- Chargement GeoJSON ---
@st.cache_data
def load_geojson():
    """Charge le fichier GeoJSON du découpage administratif de Rabat."""
    try:
        with open('Data/Rabat.geojson', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement du GeoJSON : {e}")
        return None

# --- Fonction de coloration ---
def get_color_for_score(score):
    """Retourne une couleur en fonction du score de vulnérabilité."""
    if score > 60:
        return "#e74c3c"  # Rouge (priorité haute)
    elif score > 40:
        return "#f39c12"  # Orange (priorité moyenne)
    else:
        return "#27ae60"  # Vert (priorité basse)

# --- Explications des indicateurs ---
INDICATOR_EXPLANATIONS = {
    "Taux de chômage (%)": "Pourcentage de la population active sans emploi. Un taux élevé indique une vulnérabilité sociale.",
    "Indice de Vétusté (0-10)": "État de dégradation du bâti. 0-3: Bâti récent, 4-6: Vétusté modérée, 7-10: Forte dégradation.",
    "Accessibilité Transports (0-10)": "Proximité et qualité des transports en commun. 0-3: Faible desserte, 4-7: Correcte, 8-10: Excellente.",
    "Surface Espaces Verts (m²)": "Surface totale d'espaces verts accessibles dans le quartier.",
    "Accessibilité Santé (0-10)": "Proximité des centres de santé, hôpitaux et pharmacies.",
    "Accessibilité Education (0-10)": "Proximité des écoles, collèges, lycées et universités.",
    "Sécurité (0-10)": "Niveau de sécurité basé sur les statistiques de criminalité. 0-3: Faible, 4-7: Moyenne, 8-10: Très sécurisé."
}

# --- Actions de simulation prédéfinies ---
DEFAULT_ACTIONS = [
    {"name": "Aucune action", "target": None, "type": None, "val": 0},
    {"name": "Rénovation urbaine - Yacoub El Mansour", "target": "Yacoub El Mansour", "type": "vetuste", "val": -3},
    {"name": "Création de parc - L'Océan", "target": "L'Océan", "type": "verts", "val": 15000},
    {"name": "Extension Tramway - Témara", "target": ["Hay Riad", "Souissi"], "type": "transport", "val": {"Hay Riad": 2, "Souissi": 3}},
    {"name": "Construction d'un hôpital - Médina", "target": "Médina", "type": "sante", "val": 4},
    {"name": "Programme de formation professionnelle - Yacoub El Mansour", "target": "Yacoub El Mansour", "type": "chomage", "val": -5},
    {"name": "Installation de caméras de surveillance - Hassan", "target": "Hassan", "type": "secu", "val": 3},
    {"name": "Ouverture d'une école primaire - L'Océan", "target": "L'Océan", "type": "educ", "val": 3},
    {"name": "Réhabilitation des espaces publics - Agdal", "target": "Agdal", "type": "verts", "val": 10000},
    {"name": "Extension du réseau de bus - Souissi", "target": "Souissi", "type": "transport", "val": 2}
]
