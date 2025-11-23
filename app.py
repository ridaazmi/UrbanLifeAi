import streamlit as st
from utils import generate_rabat_data, calculate_vulnerability_score

# --- Configuration de la Page ---
st.set_page_config(
    page_title="UrbanLifeAI - Rabat",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personnalisé ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #3498db;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar : Logos et Paramètres ---
col_logo1, col_logo2 = st.sidebar.columns(2)
with col_logo1:
    st.image("LOGO_CUS.png", width=80)
with col_logo2:
    st.image("UM6P Primary Lockup - Web.png", width=80)

st.sidebar.title("⚙️ Paramètres du Modèle")

w_social = st.sidebar.slider("Poids Social (Chômage)", 0.0, 5.0, 3.0)
w_infra = st.sidebar.slider("Poids Infrastructure (Vétusté + Transport)", 0.0, 5.0, 2.5)
w_env = st.sidebar.slider("Poids Environnemental (Espaces Verts)", 0.0, 5.0, 1.5)
w_sante = st.sidebar.slider("Poids Santé", 0.0, 5.0, 2.0)
w_educ = st.sidebar.slider("Poids Éducation", 0.0, 5.0, 2.0)
w_secu = st.sidebar.slider("Poids Sécurité", 0.0, 5.0, 1.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Ajustez les poids pour prioriser certains critères dans le calcul du score de vulnérabilité.")

# --- Chargement des Données ---
df = generate_rabat_data()
df_scored = calculate_vulnerability_score(df, w_social, w_infra, w_env, w_sante, w_educ, w_secu)

# --- En-tête Principal ---
st.markdown('<div class="main-header">🏙️ UrbanLifeAI - Tableau de Bord Rabat</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plateforme d\'Analyse et de Simulation pour la Planification Urbaine</div>', unsafe_allow_html=True)

# --- Message de Bienvenue ---
st.markdown("---")
st.markdown("""
### 👋 Bienvenue sur UrbanLifeAI

Cette application est un outil d'aide à la décision pour la planification urbaine de la ville de Rabat. 
Elle permet d'analyser la vulnérabilité des quartiers selon plusieurs indicateurs socio-économiques et 
de simuler l'impact de différentes interventions.

**Développé par le Center of Urban Systems (CUS) - UM6P**
""")

# --- Navigation vers les Pages ---
st.markdown("---")
st.markdown("### 📍 Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">📊 Dashboard Analytique</div>
        <p>Vue d'ensemble des quartiers avec graphiques interactifs, tableau des priorités, et analyses détaillées.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">🗺️ Cartographie</div>
        <p>Visualisation géographique avec découpage administratif et coloration par niveau de priorité.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">🤖 Simulateur</div>
        <p>Simulation de l'impact de différentes interventions urbaines avec visualisation avant/après.</p>
    </div>
    """, unsafe_allow_html=True)

# --- KPIs Rapides ---
st.markdown("---")
st.markdown("### 📈 Vue d'Ensemble Rapide")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

score_moyen = df_scored["Score Vulnérabilité"].mean()
pop_totale = df_scored["Population"].sum()
quartier_prioritaire = df_scored.loc[df_scored["Score Vulnérabilité"].idxmax(), "Nom du quartier"]

with col_kpi1:
    st.metric("Score Moyen de Vulnérabilité", f"{score_moyen:.1f}/100")

with col_kpi2:
    st.metric("Population Totale", f"{pop_totale:,}")

with col_kpi3:
    st.metric("Quartier le Plus Vulnérable", quartier_prioritaire)

# --- Instructions ---
st.markdown("---")
st.markdown("""
### 📖 Instructions d'Utilisation

1. **Ajustez les paramètres** dans la barre latérale pour personnaliser le modèle de vulnérabilité
2. **Naviguez** entre les pages en utilisant le menu de gauche
3. **Explorez** les données, cartes et simulations pour prendre des décisions éclairées

**Note** : Les données présentées sont synthétiques et à but démonstratif uniquement.
""")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Center of Urban Systems (CUS) - UM6P | Developed for UrbanLifeAI")

