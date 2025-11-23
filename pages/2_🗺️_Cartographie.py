import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import generate_rabat_data, calculate_vulnerability_score, load_geojson, get_color_for_score

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Cartographie - UrbanLifeAI",
    page_icon="🗺️",
    layout="wide"
)

# --- Sidebar : Logos et Paramètres ---
col_logo1, col_logo2 = st.sidebar.columns(2)
with col_logo1:
    st.image("images/LOGO_CUS.png", width=80)
with col_logo2:
    st.image("images/UM6P Primary Lockup - Web.png", width=80)
st.sidebar.title("⚙️ Paramètres du Modèle")

w_social = st.sidebar.slider("Poids Social (Chômage)", 0.0, 5.0, 3.0)
w_infra = st.sidebar.slider("Poids Infrastructure (Vétusté + Transport)", 0.0, 5.0, 2.5)
w_env = st.sidebar.slider("Poids Environnemental (Espaces Verts)", 0.0, 5.0, 1.5)
w_sante = st.sidebar.slider("Poids Santé", 0.0, 5.0, 2.0)
w_educ = st.sidebar.slider("Poids Éducation", 0.0, 5.0, 2.0)
w_secu = st.sidebar.slider("Poids Sécurité", 0.0, 5.0, 1.5)

st.sidebar.markdown("---")
st.sidebar.title("🎨 Légende des Couleurs")
st.sidebar.markdown("""
- 🔴 **Rouge** : Priorité Haute (Score > 60)
- 🟠 **Orange** : Priorité Moyenne (Score 40-60)
- 🟢 **Vert** : Priorité Basse (Score < 40)
""")

# --- Chargement des Données ---
df = generate_rabat_data()
df_scored = calculate_vulnerability_score(df, w_social, w_infra, w_env, w_sante, w_educ, w_secu)
geojson_data = load_geojson()

# --- En-tête ---
st.title("🗺️ Cartographie des Vulnérabilités")
st.markdown("Visualisation géographique avec découpage administratif et coloration par niveau de priorité.")
st.markdown("---")

# --- Sélecteur d'Indicateur ---
col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
    indicator = st.selectbox(
        "Sélectionnez l'indicateur à visualiser :",
        ["Score Vulnérabilité", "Taux de chômage (%)", "Indice de Vétusté (0-10)", 
         "Accessibilité Transports (0-10)", "Accessibilité Santé (0-10)", 
         "Accessibilité Education (0-10)", "Sécurité (0-10)"]
    )

with col_sel2:
    st.info(f"**Indicateur actuel** : {indicator}")

# --- Création de la Carte ---
if geojson_data:
    # Créer un dictionnaire de mapping
    score_dict = df_scored.set_index('Nom du quartier')[indicator].to_dict()
    
    # Créer la carte centrée sur Rabat
    m = folium.Map(location=[34.00, -6.85], zoom_start=12, tiles="CartoDB positron")
    
    # Fonction de style pour coloration
    def style_function(feature):
        commune = feature['properties']['commune']
        # Mapping des noms de communes du GeoJSON aux noms de quartiers
        commune_mapping = {
            "Agdal Riad": "Agdal",
            "Hassan": "Hassan",
            "El Youssoufia": "Médina",
            "Témara": "L'Océan",
            "Harhoura": "Souissi",
            "Sidi Yahya Zaer": "Hay Riad",
            "Ain El Aouda": "Yacoub El Mansour"
        }
        
        quartier = commune_mapping.get(commune, commune)
        score = score_dict.get(quartier, 0)
        
        # Coloration basée sur le score
        if indicator == "Score Vulnérabilité":
            color = get_color_for_score(score)
        else:
            # Pour les autres indicateurs, adapter la logique
            if "Accessibilité" in indicator or "Sécurité" in indicator:
                # Plus c'est élevé, mieux c'est (vert)
                if score > 7: color = "#27ae60"
                elif score > 4: color = "#f39c12"
                else: color = "#e74c3c"
            else:
                # Plus c'est élevé, pire c'est (rouge)
                if score > 15 or score > 7: color = "#e74c3c"
                elif score > 10 or score > 4: color = "#f39c12"
                else: color = "#27ae60"
        
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.6
        }
    
    # Fonction de highlight au survol
    def highlight_function(feature):
        return {
            'fillColor': '#ffff00',
            'color': 'black',
            'weight': 3,
            'fillOpacity': 0.8
        }
    
    # Ajouter le GeoJSON à la carte
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['commune', 'province_1'],
            aliases=['Commune:', 'Province:'],
            style="background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
        popup=folium.GeoJsonPopup(
            fields=['commune', 'province_1', 'region'],
            aliases=['Commune:', 'Province:', 'Région:'],
            style="background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        )
    ).add_to(m)
    
    # Ajouter des marqueurs pour les quartiers avec données
    for _, row in df_scored.iterrows():
        score = row[indicator]
        color = get_color_for_score(row["Score Vulnérabilité"])
        
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin-bottom: 10px;">{row['Nom du quartier']}</h4>
            <p><b>{indicator}:</b> {score}</p>
            <p><b>Population:</b> {row['Population']:,}</p>
            <p><b>Score Vulnérabilité:</b> {row['Score Vulnérabilité']:.1f}/100</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=250),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Afficher la carte
    st_folium(m, width="100%", height=600)
    
    # --- Statistiques de la Carte ---
    st.markdown("---")
    st.subheader("📊 Statistiques de l'Indicateur Sélectionné")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Valeur Moyenne", f"{df_scored[indicator].mean():.1f}")
    
    with col_stat2:
        st.metric("Valeur Minimale", f"{df_scored[indicator].min():.1f}")
    
    with col_stat3:
        st.metric("Valeur Maximale", f"{df_scored[indicator].max():.1f}")
    
    with col_stat4:
        quartier_max = df_scored.loc[df_scored[indicator].idxmax(), "Nom du quartier"]
        st.metric("Quartier Max", quartier_max)
    
    # --- Tableau Récapitulatif ---
    st.markdown("---")
    st.subheader("📋 Tableau Récapitulatif par Quartier")
    
    # Éviter la duplication de colonnes
    if indicator == "Score Vulnérabilité":
        display_cols = ["Nom du quartier", indicator, "Population"]
    else:
        display_cols = ["Nom du quartier", indicator, "Population", "Score Vulnérabilité"]
    df_display = df_scored[display_cols].sort_values(indicator, ascending=False)
    
    st.dataframe(df_display, use_container_width=True)

else:
    st.error("❌ Impossible de charger le fichier GeoJSON. Vérifiez que le fichier `Data/Rabat.geojson` existe.")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Center of Urban Systems (CUS) - UM6P | Developed for UrbanLifeAI")
