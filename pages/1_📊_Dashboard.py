import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_rabat_data, calculate_vulnerability_score, INDICATOR_EXPLANATIONS

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Dashboard Analytique - UrbanLifeAI",
    page_icon="📊",
    layout="wide"
)

# --- CSS Personnalisé ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

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
st.sidebar.title("📚 Guide des Indicateurs")
with st.sidebar.expander("ℹ️ Comprendre les métriques"):
    for indicator, explanation in INDICATOR_EXPLANATIONS.items():
        st.markdown(f"**{indicator}** : {explanation}")

# --- Chargement des Données ---
df = generate_rabat_data()
df_scored = calculate_vulnerability_score(df, w_social, w_infra, w_env, w_sante, w_educ, w_secu)

# --- En-tête ---
st.title("📊 Tableau de Bord Analytique")
st.markdown("Vue d'ensemble des quartiers de Rabat avec analyses détaillées et visualisations interactives.")
st.markdown("---")

# --- KPIs Principaux ---
col1, col2, col3 = st.columns(3)

score_moyen = df_scored["Score Vulnérabilité"].mean()
pop_totale = df_scored["Population"].sum()
quartier_prioritaire = df_scored.loc[df_scored["Score Vulnérabilité"].idxmax(), "Nom du quartier"]

with col1:
    st.metric("Score Moyen de Vulnérabilité", f"{score_moyen:.1f}/100")

with col2:
    st.metric("Population Totale", f"{pop_totale:,}")

with col3:
    st.metric("Quartier le Plus Vulnérable", quartier_prioritaire)

# --- Tableau des Quartiers Prioritaires ---
st.markdown("---")
st.subheader("🎯 Quartiers Prioritaires (Top 5)")

top_5 = df_scored.nlargest(5, "Score Vulnérabilité")[["Nom du quartier", "Score Vulnérabilité", "Population", "Taux de chômage (%)", "Indice de Vétusté (0-10)"]]
top_5 = top_5.reset_index(drop=True)
top_5.index = top_5.index + 1

st.dataframe(top_5, use_container_width=True)

# --- Visualisations ---
st.markdown("---")
st.subheader("📊 Tableau de Bord Analytique")

# 1. Scores de Vulnérabilité par Quartier
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.markdown("##### Scores de Vulnérabilité par Quartier")
    df_sorted = df_scored.sort_values("Score Vulnérabilité", ascending=False)
    fig_bar = px.bar(
        df_sorted,
        x="Nom du quartier",
        y="Score Vulnérabilité",
        color="Score Vulnérabilité",
        color_continuous_scale="RdYlGn_r",
        text="Score Vulnérabilité",
        height=400
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Score de Vulnérabilité")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_viz2:
    st.markdown("##### Distribution de la Population")
    fig_pie = px.pie(
        df_scored,
        values="Population",
        names="Nom du quartier",
        hole=0.4,
        height=400
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# 2. Comparaison Multi-Indicateurs
st.markdown("##### Comparaison Multi-Indicateurs")
df_indicators = df_scored[["Nom du quartier", "Accessibilité Transports (0-10)", "Accessibilité Santé (0-10)", "Accessibilité Education (0-10)", "Sécurité (0-10)"]]
df_melted = df_indicators.melt(id_vars="Nom du quartier", var_name="Indicateur", value_name="Score")

fig_grouped = px.bar(
    df_melted,
    x="Nom du quartier",
    y="Score",
    color="Indicateur",
    barmode="group",
    height=400
)
fig_grouped.update_layout(xaxis_title="", yaxis_title="Score (0-10)")
st.plotly_chart(fig_grouped, use_container_width=True)

# 3. Matrice de Corrélation
st.markdown("##### Matrice de Corrélation des Indicateurs")
corr_cols = ["Taux de chômage (%)", "Indice de Vétusté (0-10)", "Accessibilité Transports (0-10)", 
             "Accessibilité Santé (0-10)", "Accessibilité Education (0-10)", "Sécurité (0-10)", "Score Vulnérabilité"]
corr_matrix = df_scored[corr_cols].corr()

fig_heatmap = px.imshow(
    corr_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    aspect="auto",
    height=500
)
fig_heatmap.update_layout(
    xaxis_title="",
    yaxis_title="",
    xaxis={'side': 'bottom'}
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# --- Fiche Détaillée par Quartier ---
st.markdown("---")
st.subheader("🏘️ Fiche Détaillée par Quartier")
selected_quartier = st.selectbox("Sélectionnez un quartier pour voir les détails :", df_scored["Nom du quartier"].unique())

if selected_quartier:
    q_data = df_scored[df_scored["Nom du quartier"] == selected_quartier].iloc[0]
    
    col_d1, col_d2 = st.columns([1, 1])
    
    with col_d1:
        st.markdown("##### Informations Générales")
        st.write(f"**Population :** {q_data['Population']:,} habitants")
        st.write(f"**Densité :** {q_data['Densité (hab/km²)']:,} hab/km²")
        st.write(f"**Espaces Verts :** {q_data['Surface Espaces Verts (m²)']:,} m²")
        st.metric("Score de Vulnérabilité Global", f"{q_data['Score Vulnérabilité']:.1f}/100")
        
        # Indicateurs avec tooltips
        st.markdown("##### Indicateurs Détaillés")
        
        col_ind1, col_ind2 = st.columns([3, 1])
        with col_ind1:
            st.write("**Taux de chômage**")
        with col_ind2:
            st.write(f"{q_data['Taux de chômage (%)']}%")
        st.caption("ℹ️ Pourcentage de la population active sans emploi")
        
        col_ind1, col_ind2 = st.columns([3, 1])
        with col_ind1:
            st.write("**Indice de Vétusté**")
        with col_ind2:
            st.write(f"{q_data['Indice de Vétusté (0-10)']}/10")
        st.caption("ℹ️ État de dégradation du bâti (0=neuf, 10=très dégradé)")
        
    with col_d2:
        st.markdown("##### Profil du Quartier")
        # Radar chart
        categories = ['Transport', 'Santé', 'Éducation', 'Sécurité']
        values = [
            q_data["Accessibilité Transports (0-10)"],
            q_data["Accessibilité Santé (0-10)"],
            q_data["Accessibilité Education (0-10)"],
            q_data["Sécurité (0-10)"]
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=selected_quartier,
            line_color='#3498db',
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False,
            height=350
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Légende du radar
        st.caption("ℹ️ **Transport** : Proximité et qualité des transports en commun")
        st.caption("ℹ️ **Santé** : Accessibilité aux centres de santé et hôpitaux")
        st.caption("ℹ️ **Éducation** : Proximité des établissements scolaires")
        st.caption("ℹ️ **Sécurité** : Niveau de sécurité du quartier")

# --- Export de Données ---
st.markdown("---")
st.subheader("📥 Export des Données")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("##### Télécharger les données complètes")
    csv = df_scored.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Télécharger CSV",
        data=csv,
        file_name=f"urbanlife_rabat_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

with col_exp2:
    st.markdown("##### Informations sur l'export")
    st.write(f"**Nombre de quartiers :** {len(df_scored)}")
    st.write(f"**Colonnes incluses :** {len(df_scored.columns)}")
    st.caption("Le fichier CSV contient toutes les données affichées dans le tableau de bord.")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Center of Urban Systems (CUS) - UM6P | Developed for UrbanLifeAI")
