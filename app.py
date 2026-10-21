import streamlit as st
import json
import os

# Configuration de la page (Doit être la toute première commande Streamlit)
st.set_page_config(page_title="L5A - Hôte de Table", layout="wide")

# --- STYLE GRAPHIQUE PERSONNALISÉ (Thème Sombre L5A) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #f1c40f !important;
        font-family: 'Georgia', serif;
    }
    .streamlit-expanderHeader {
        background-color: #1e1e1e !important;
        border: 1px solid #333333 !important;
        border-radius: 5px;
        color: #ffffff !important;
    }
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
    }
    .stForm {
        background-color: #1e1e1e !important;
        border: 1px solid #d4af37 !important;
        border-radius: 8px;
        padding: 20px;
    }
    .stButton>button {
        background-color: #8b0000 !important;
        color: white !important;
        border-radius: 5px !important;
        border: 1px solid #ff4500 !important;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ff0000 !important;
        box-shadow: 0 0 10px #ff0000;
    }
    [data-testid="stSidebar"] {
        background-color: #181818 !important;
        border-right: 1px solid #2b2b2b;
    }
    </style>
""", unsafe_allow_html=True)

# Configuration des dossiers système
DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

ACTIONS_FILE = "notifications_mj.json"

# --- FONCTIONS DE SAUVEGARDE ET CHARGEMENT ---
def sauver_fiche(nom_joueur, data):
    filename = os.path.join(DB_DIR, f"{nom_joueur.lower().strip().replace(' ', '_')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def charger_fiche(nom_joueur):
    filename = os.path.join(DB_DIR, f"{nom_joueur.lower().strip().replace(' ', '_')}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def notifier_mj(nom_joueur, nom_perso, tech):
    actions = []
    if os.path.exists(ACTIONS_FILE):
        try:
            with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
                actions = json.load(f)
        except: 
            actions = []
    nouvel_id = len(actions) + 1
    actions.append({"id": nouvel_id, "joueur": nom_joueur, "perso": nom_perso, "technique": tech, "statut": "En attente"})
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=4, ensure_ascii=False)

# --- STRUCTURE DES PAGES ---
st.title("⛩️ L'Empire d'Émeraude - Gestionnaire de Table L5A")

# Choix du rôle dans la barre latérale
role = st.sidebar.radio("🔑 Sécurisation de l'Accès :", ["Visiteur", "Joueur (Accès Secret)", "Maître du Jeu (Hôte)"])

# ==============================================================================
# SECTEUR JOUEUR
# ==============================================================================
if role == "Joueur (Accès Secret)":
    st.header("👤 Votre Parchemin de Personnage")
    nom_identifiant = st.text_input("Entrez votre prénom (Identifiant de session) :").strip()
    
    if nom_identifiant:
        fiche_chargee = charger_fiche(nom_identifiant)
        if fiche_chargee:
            st.success(f"🏯 Données rechargées pour {nom_identifiant}.")
            data = fiche_chargee
        else:
            st.info("🆕 Création d'une nouvelle fiche personnalisée pour la table.")
            data = {
                "perso": "", "rang_ecole": 1, "posture_active": "Air",
                "air": 1, "terre": 1, "feu": 1, "eau": 1, "vide": 1, "points_vide": 1,
                "end_act": 4, "sf_act": 4,
                "comp_artisanales": 0, "comp_martiales": 0, "comp_savantes": 0, "comp_sociales": 0, "comp_professionnelles": 0,
                "res_physique": "0", "res_surnaturelle": "0", "prop_armure": "",
                "arme_nom": "", "arme_degats": "0", "arme_danger": "0", "arme_portee": "1", "arme_prop": "",
                "kata": "", "kiho": "", "invoc": "", "rituels": "", "shuji": "", "maho": "", "ninjutsu": "", "inversions": ""
            }
            
        with st.form("form_personnage_integral"):
            st.subheader("📝 Informations Principales")
            col_id1, col_id2, col_id3 = st.columns(3)
            nom_perso = col_id1.text_input("Nom du Personnage :", value=data.get("perso", ""))
            rang_ecole = col_id2.number_input("Rang d'École (1 à 6) :", 1, 6, value=data.get("rang_ecole", 1))
            posture_active = col_id3.selectbox("Posture Active de Combat :", ["Air", "Terre", "Feu", "Eau", "Vide"], index=["Air", "Terre", "Feu", "Eau", "Vide"].index(data.get("posture_active", "Air")))
            
            st.subheader("🌀 Les Cinq Anneaux (Rang de 1 à 5)")
            c1, c2, c3, c4, c5 = st.columns(5)
            air = c1.slider("Air 💨", 1, 5, value=data.get("air", 1))
            terre = c2.slider("Terre 🏔️", 1, 5, value=data.get("terre", 1))
            feu = c3.slider("Feu 🔥", 1, 5, value=data.get("feu", 1))
            eau = c4.slider("Eau 💧", 1, 5, value=data.get("eau", 1))
            vide = c5.slider("Vide 🌌", 1, 5, value=data.get("vide", 1))
            points_vide = st.number_input("Points de Vide Actuels", 0, vide, value=data.get("points_vide", 1))

            # --- CALCULS AUTOMATIQUES SELON VOS ÉQUATIONS ---
            end_max = (terre + feu) * 2
            sf_max = (terre + eau) * 2
            attention = air + feu
            vigilance = (air + eau) / 2
            
            st.subheader("📊 Statistiques Secondaires Automatiques")
            cs1, cs2, cs3, cs4 = st.columns(4)
            cs1.metric("🏋️ Endurance Maximum", f"{end_max} PV")
            cs2.metric("🧠 Sang-froid Maximum", f"{sf_max}")
            cs3.metric("🎓 Attention", f"{attention}")
            cs4.metric("👁️ Vigilance", f"{vigilance}", help="Nombre de réussites nécessaires pour qu'une créature touche le joueur.")
            
            st.markdown("##### Ajustement de votre Vitalité Actuelle")
            c_vit1, c_vit2 = st.columns(2)
            end_act = c_vit1.number_input("Endurance Actuelle :", 0, end_max, value=min(data.get("end_act", end_max), end_max))
            sf_act = c_vit2.number_input("Sang-froid Actuel :", 0, sf_max, value=min(data.get("sf_act", sf_max), sf_max))

            st.subheader("🎭 Catégories de Compétences (Rang de 0 à 5)")
            cc1, cc2, cc3, cc4, cc5 = st.columns(5)
            comp_artisanales = cc1.number_input("Artisanales 🎨", 0, 5, value=data.get("comp_artisanales", 0))
            comp_martiales = cc2.number_input("Martiales ⚔️", 0, 5, value=data.get("comp_martiales", 0))
            comp_savantes = cc3.number_input("Savantes 📜", 0, 5, value=data.get("comp_savantes", 0))
            comp_sociales = cc4.number_input("Sociales 🗣️", 0, 5, value=data.get("comp_sociales", 0))
            comp_professionnelles = cc5.number_input("Professionnelles 🛠️", 0, 5, value=data.get("comp_professionnelles", 0))

            st.subheader("🛡️ Armure & Résistances")
            cr1, cr2, cr3 = st.columns(3)
            res_physique = cr1.text_input("Résistance Physique :", value=data.get("res_physique", "0"))
            res_surnaturelle = cr2.text_input("Résistance Surnaturelle :", value=data.get("res_surnaturelle", "0"))
            prop_armure = cr3.text_input("Propriétés de l'Armure :", value=data.get("prop_armure", ""))

            st.subheader("🗡️ Profil de l'Arme Équipée")
            ca1, ca2, ca3, ca4, ca5 = st.columns(5)
            arme_nom = ca1.text_input("Nom de l'Arme :", value=data.get("arme_nom", ""))
            arme_degats = ca2.text_input("Dégâts :", value=data.get("arme_degats", "0"))
            arme_danger = ca3.text_input("Dangerosité :", value=data.get("arme_danger", "0"))
            arme_portee = ca4.text_input("Portée :", value=data.get("arme_portee", "1"))
            arme_prop = ca5.text_input("Propriétés de l'Arme :", value=data.get("arme_prop", ""))

            st.subheader("📜 Grimoire des Techniques Apprises (Rang 1 à 5)")
            ct1, ct2, ct3, ct4 = st.columns(4)
            kata = ct1.text_area("Kata", value=data.get("kata", ""))
            kiho = ct2.text_area("Kího", value=data.get("kiho", ""))
            invoc = ct3.text_area("Invocations", value=data.get("invoc", ""))
            rituels = ct4.text_area("Rituels", value=data.get("rituels", ""))
            
            ct5, ct6, ct7, ct8 = st.columns(4)
            shuji = ct5.text_area("Shuji", value=data.get("shuji", ""))
            maho = ct6.text_area("Maho", value=data.get("maho", ""))
            ninjutsu = ct7.text_area("Ninjutsu", value=data.get("ninjutsu", ""))
            inversions = ct8.text_area("Inversions", value=data.get("inversions", ""))

            if st.form_submit_button("💾 Sauvegarder et Synchroniser ma Fiche"):
                maj_data = {
                    "perso": nom_perso, "rang_ecole": rang_ecole, "posture_active": posture_active,
                    "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "points_vide": points_vide,
                    "end_act": end_act, "sf_act": sf_act,
                    "comp_artisanales": comp_artisanales, "comp_martiales": comp_martiales, "comp_savantes": comp_savantes,
                    "comp_sociales": comp_sociales, "comp_professionnelles": comp_professionnelles,
                    "res_physique": res_physique, "res_surnaturelle": res_surnaturelle, "prop_armure": prop_armure,
                    "arme_nom": arme_nom, "arme_degats": arme_degats, "arme_danger": arme_danger, "arme_portee": arme_portee, "arme_prop": arme_prop,
