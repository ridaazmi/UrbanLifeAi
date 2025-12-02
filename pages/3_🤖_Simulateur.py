import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_rabat_data, calculate_vulnerability_score, DEFAULT_ACTIONS

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Simulateur - UrbanLifeAI",
    page_icon="🤖",
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

# --- Chargement des Données ---
df = generate_rabat_data()
df_scored = calculate_vulnerability_score(df, w_social, w_infra, w_env, w_sante, w_educ, w_secu)

# --- En-tête ---
st.title("🤖 Simulateur d'Impact (IA Prédictive)")
st.markdown("Simulez l'impact de différentes interventions urbaines et visualisez les résultats avant/après.")
st.markdown("---")

# --- Initialisation des Actions ---
if "actions" not in st.session_state:
    st.session_state.actions = DEFAULT_ACTIONS.copy()

# --- Ajout d'Actions Personnalisées ---
st.subheader("➕ Ajouter une Intervention Personnalisée")
st.info("Créez vos propres scénarios d'intervention pour tester leur impact.")

with st.form("add_action_form"):
    col_form1, col_form2, col_form3, col_form4 = st.columns(4)
    
    with col_form1:
        new_name = st.text_input("Nom de l'intervention", placeholder="Ex: Nouveau parc")
    
    with col_form2:
        new_target = st.selectbox("Quartier cible", df["Nom du quartier"].unique())
    
    with col_form3:
        new_type = st.selectbox("Type d'impact", ["vetuste", "transport", "verts", "sante", "educ", "secu", "chomage"])
    
    with col_form4:
        new_val = st.number_input("Valeur de l'impact", value=0.0, step=0.5)
    
    submitted = st.form_submit_button("Ajouter l'intervention")
    
    if submitted and new_name:
        new_action = {
            "name": new_name,
            "target": new_target,
            "type": new_type,
            "val": new_val
        }
        st.session_state.actions.append(new_action)
        st.success(f"✅ Intervention '{new_name}' ajoutée avec succès!")

# --- Sélection de l'Action ---
st.markdown("---")
st.subheader(" Sélection de l'Intervention à Simuler")

action_names = [a["name"] for a in st.session_state.actions]
selected_action_name = st.selectbox("Choisir une action à simuler :", action_names)

# --- Simulation ---
selected_action = next((a for a in st.session_state.actions if a["name"] == selected_action_name), None)

if selected_action and selected_action["name"] != "Aucune action":
    targets = selected_action["target"]
    if not isinstance(targets, list):
        targets = [targets]
    
    st.markdown("---")
    st.subheader(" Résultats de la Simulation")
    
    for target in targets:
        st.markdown(f"#### 🎯 Impact sur : {target}")
        
        q_data = df_scored[df_scored["Nom du quartier"] == target].iloc[0]
        old_score = q_data["Score Vulnérabilité"]
        
        # Clone values to modify
        vals = {
            "vetuste": q_data["Indice de Vétusté (0-10)"],
            "transport": q_data["Accessibilité Transports (0-10)"],
            "verts": q_data["Surface Espaces Verts (m²)"],
            "sante": q_data["Accessibilité Santé (0-10)"],
            "educ": q_data["Accessibilité Education (0-10)"],
            "secu": q_data["Sécurité (0-10)"],
            "chomage": q_data["Taux de chômage (%)"]
        }
        
        # Apply impact
        act_type = selected_action["type"]
        act_val = selected_action["val"]
        
        if act_type == "transport":
            if isinstance(act_val, dict):
                vals["transport"] = min(10, vals["transport"] + act_val.get(target, 0))
            else:
                vals["transport"] = min(10, vals["transport"] + act_val)
        elif act_type == "vetuste":
            vals["vetuste"] = max(0, vals["vetuste"] + act_val)
        elif act_type == "verts":
            vals["verts"] += act_val
        elif act_type == "chomage":
            vals["chomage"] = max(0, vals["chomage"] + act_val)
        elif act_type in ["sante", "educ", "secu"]:
            vals[act_type] = min(10, vals[act_type] + act_val)
        
        # Recalculate Score
        norm_chomage = vals["chomage"] / 25.0
        norm_vetuste = vals["vetuste"] / 10.0
        norm_transport = 1 - (vals["transport"] / 10.0)
        norm_verts = 1 - (vals["verts"] / 80000.0)
        norm_sante = 1 - (vals["sante"] / 10.0)
        norm_educ = 1 - (vals["educ"] / 10.0)
        norm_secu = 1 - (vals["secu"] / 10.0)
        
        total_weight = w_social + w_infra + w_env + w_sante + w_educ + w_secu
        if total_weight == 0: total_weight = 1
        
        new_score_brut = (
            w_social * norm_chomage +
            w_infra * (norm_vetuste + norm_transport) / 2 +
            w_env * norm_verts +
            w_sante * norm_sante +
            w_educ * norm_educ +
            w_secu * norm_secu
        )
        
        new_score = (new_score_brut / total_weight) * 100
        delta = new_score - old_score
        
        # Visualisation Avant/Après
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            st.metric("Score Avant", f"{old_score:.1f}/100")
            st.metric("Score Après", f"{new_score:.1f}/100", f"{delta:.1f}", delta_color="inverse")
            st.write(f"**Type d'intervention :** {act_type.capitalize()}")
            st.write(f"**Valeur de l'impact :** {act_val}")
            
            # Afficher les changements détaillés
            st.markdown("##### Changements Détaillés")
            if act_type == "chomage":
                st.write(f"Chômage : {q_data['Taux de chômage (%)']}% → {vals['chomage']:.1f}%")
            elif act_type == "vetuste":
                st.write(f"Vétusté : {q_data['Indice de Vétusté (0-10)']} → {vals['vetuste']}")
            elif act_type == "transport":
                st.write(f"Transport : {q_data['Accessibilité Transports (0-10)']} → {vals['transport']}")
            elif act_type == "verts":
                st.write(f"Espaces Verts : {q_data['Surface Espaces Verts (m²)']:,} m² → {vals['verts']:,} m²")
            elif act_type == "sante":
                st.write(f"Santé : {q_data['Accessibilité Santé (0-10)']} → {vals['sante']}")
            elif act_type == "educ":
                st.write(f"Éducation : {q_data['Accessibilité Education (0-10)']} → {vals['educ']}")
            elif act_type == "secu":
                st.write(f"Sécurité : {q_data['Sécurité (0-10)']} → {vals['secu']}")
            
        with col_res2:
            # Graphique de comparaison avant/après
            comparison_df = pd.DataFrame({
                'État': ['Avant', 'Après'],
                'Score de Vulnérabilité': [old_score, new_score]
            })
            
            fig_comparison = px.bar(
                comparison_df,
                x='État',
                y='Score de Vulnérabilité',
                color='Score de Vulnérabilité',
                color_continuous_scale='RdYlGn_r',
                text='Score de Vulnérabilité',
                height=300,
                title=f"Impact de l'intervention sur {target}"
            )
            fig_comparison.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_comparison.update_layout(showlegend=False)
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        st.markdown("---")

elif selected_action and selected_action["name"] == "Aucune action":
    st.info("⏳ En attente de simulation... Sélectionnez une action pour voir les résultats.")

# --- Tableau Récapitulatif des Actions ---
st.markdown("---")
st.subheader(" Liste des Interventions Disponibles")

actions_df = pd.DataFrame([
    {
        "Nom": a["name"],
        "Quartier Cible": a["target"] if a["target"] else "N/A",
        "Type": a["type"] if a["type"] else "N/A",
        "Impact": a["val"]
    }
    for a in st.session_state.actions if a["name"] != "Aucune action"
])

st.dataframe(actions_df, use_container_width=True)

# --- Estimation de Coût (Fictive) ---
st.markdown("---")
st.subheader(" Estimation de Coût et ROI Social")

if selected_action and selected_action["name"] != "Aucune action":
    # Coûts fictifs basés sur le type d'intervention
    cost_estimates = {
        "vetuste": 5000000,  # 5M MAD
        "transport": 10000000,  # 10M MAD
        "verts": 2000000,  # 2M MAD
        "sante": 15000000,  # 15M MAD
        "educ": 8000000,  # 8M MAD
        "secu": 3000000,  # 3M MAD
        "chomage": 4000000  # 4M MAD (formation)
    }
    
    estimated_cost = cost_estimates.get(selected_action["type"], 0)
    
    col_cost1, col_cost2, col_cost3 = st.columns(3)
    
    with col_cost1:
        st.metric("Coût Estimé", f"{estimated_cost:,} MAD")
    
    with col_cost2:
        # ROI social basé sur la réduction du score
        if delta < 0:
            roi_social = abs(delta) * 10  # Fictif
            st.metric("ROI Social", f"{roi_social:.1f}%")
        else:
            st.metric("ROI Social", "N/A")
    
    with col_cost3:
        # Population impactée
        if isinstance(targets, list):
            pop_impactee = sum([df_scored[df_scored["Nom du quartier"] == t]["Population"].values[0] for t in targets])
        else:
            pop_impactee = df_scored[df_scored["Nom du quartier"] == targets]["Population"].values[0]
        st.metric("Population Impactée", f"{pop_impactee:,}")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Center of Urban Systems (CUS) - UM6P | Developed for UrbanLifeAI")

