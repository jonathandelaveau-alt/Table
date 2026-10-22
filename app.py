import json
import os
import time
import streamlit as st

# =====================================================================
# 📂 1. CONFIGURATION DU DOSSIER DE STOCKAGE & DESIGN SOMBRE
# =====================================================================
DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR): 
    os.makedirs(DB_DIR)
ACTIONS_FILE = "notifications_mj.json"

st.set_page_config(page_title="L5A - Table Tactique Évoluée", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    h1, h2, h3, h4 { color: #f1c40f !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #8b0000 !important; color: white !important; font-weight: bold; border: 1px solid #ff4500 !important; }
    [data-testid="stSidebar"] { background-color: #181818 !important; border-right: 1px solid #2b2b2b; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 📜 2. IMPORTATION LOGIQUE DES BASES DE DONNÉES DÉPORTÉES
# =====================================================================
from equipements import CATALOGUE_ARMURES, CATALOGUE_ARMES_AVANCE, CATALOGUE_DIVERS
from techniques import CATALOGUE_COMPLET, DESCRIPTIONS_LORE
from etats_blessures import CATALOGUE_ETATS_BLESSURES
from ecoles import CATALOGUE_ECOLES

# Récupération automatique pour les listes
CATALOGUE_KATAS = CATALOGUE_COMPLET.get("Katas", {})
CATALOGUE_KIHOS = CATALOGUE_COMPLET.get("Kihos", {})
CATALOGUE_INVOCATIONS = CATALOGUE_COMPLET.get("Invocations", {})
CATALOGUE_RITUELS = CATALOGUE_COMPLET.get("Rituels", {})
CATALOGUE_SHUJIS = CATALOGUE_COMPLET.get("Shujis", {})
CATALOGUE_INVERSIONS = CATALOGUE_COMPLET.get("Inversions", {})

DATA_CLANS = {
    "Crabe": ["Hida", "Hiruma", "Kaiu", "Kuni", "Yasuki"],
    "Grue": ["Doji", "Kakita", "Asahina", "Daidoji"],
    "Dragon": ["Mirumoto", "Agasha", "Togashi", "Kitsuki"],
    "Lion": ["Akodo", "Matsu", "Ikoma", "Kitsu"],
    "Phénix": ["Isawa", "Shiba", "Asako", "Agasha"],
    "Scorpion": ["Bayushi", "Shosuro", "Yogo", "Soshi"],
    "Licorne": ["Shinjo", "Utaku", "Ide", "Iuchi"],
    "Mante / Mineur": ["Yoritomo", "Kitsune", "Kasuga"]
}
ROLES_LISTE = ["Bushi", "Courtisan", "Shugenja", "Moine", "Artisan", "Shinobi"]
# =====================================================================
# ⚙️ 3. FONCTIONS UNIQUES DE CHARGEMENT ET SAUVEGARDE SECURISEES
# =====================================================================
def charger_fiche(nom_id):
    """Charge la fiche depuis le dossier et applique la structure par défaut sur les clés manquantes."""
    if not nom_id:
        return {}
        
    nom_fichier = f"{nom_id.lower().strip()}.json"
    path_complet = os.path.join(DB_DIR, nom_fichier)
    
    structure_defaut = {
        "perso": "", "clan": "Clan de la Grue", "famille": "Kakita", "genre": "Homme", "espece": "Humain", "ecole": "",
        "rang_ecole": 1, "profil": ["Bushi"], "posture": "Air",
        "anneau_air": 2, "anneau_terre": 2, "anneau_feu": 2, "anneau_eau": 2, "anneau_vide": 2,
        "score_b_air": 0, "score_b_terre": 0, "score_b_feu": 0, "score_b_eau": 0, "score_b_vide": 0,
        "hon": 50, "glo": 50, "sta": 50,
        "comp_artisanat": 0, "comp_composition": 0, "comp_design": 0, "comp_esthetique": 0, "comp_forgeron": 0,
        "comp_armes_de_poing": 0, "comp_armes_de_jet": 0, "comp_arts_martiaux_(corps_à_corps)": 0,
        "comp_arts_martiaux_(distance)": 0, "comp_arts_martiaux_(mains_nues)": 0, "comp_meditation": 0,
        "comp_commerce": 0, "comp_culture": 0, "comp_theologie": 0, "comp_medecine": 0, "comp_sentiment": 0, "comp_tactique": 0,
        "comp_commandement": 0, "comp_courtoisie": 0, "comp_jeux": 0, "comp_ruse": 0, "comp_performance": 0,
        "comp_chasse": 0, "comp_navigation": 0, "comp_survie": 0, "comp_travail_manuel": 0,
        "inventaire_sac": [
            {"id_obj": 1, "nom": "Katana d'école", "modele_racine": "Katana", "type_cat": "Arme", "details": "Modèle standard d'école.", "main_equipee": "Main Droite", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": "Acérée, Cérémoniale"},
            {"id_obj": 2, "nom": "Wakizashi de base", "modele_racine": "Wakizashi", "type_cat": "Arme", "details": "Lame courte de protection.", "main_equipee": "Aucune", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": "Acérée, Cérémoniale"},
            {"id_obj": 3, "nom": "Armure de Tenue de Cérémonie", "modele_racine": "Armure de Tenue de Cérémonie", "type_cat": "Armure", "details": "Modèle standard.", "equipe": True, "bonus_res_p": 0, "bonus_res_s": 0, "proprietes": "Cérémonielle, Magnifique"}
        ], 
        "mes_katas": [], "mes_kihos": [], "mes_invocs": [], "mes_rituels": [], "mes_shujis": [], 
        "mes_mahos": [], "mes_ninjutsus": [], "mes_inversions": [], "mes_etats": [],
        "xp_accumulee": 0, "xp_depensee_rang": 0, "xp_depensee_libre": 0, "titres_obtenus": [],
        "endurance_actuelle": 10, "sang_froid_actuel": 10, "points_vide_actuels": 2,
        "sh_anneaux": True, "sh_vitalite": True, "sh_social": True, "sh_equipement": True, "sh_grimoire": True
    }
    
    if os.path.exists(path_complet):
        try:
            with open(path_complet, "r", encoding="utf-8") as f_json:
                donnees_chargees = json.load(f_json)
                for cle, valeur in donnees_chargees.items():
                    structure_defaut[cle] = valeur
                return structure_defaut
        except Exception:
            return structure_defaut
    return structure_defaut

def sauver_fiche(nom_id, dictionnaire_fiche):
    """Fige immédiatement l'intégralité du dictionnaire dans le dossier DB_DIR."""
    if not nom_id:
        return
    nom_fichier = f"{nom_id.lower().strip()}.json"
    path_complet = os.path.join(DB_DIR, nom_fichier)
    with open(path_complet, "w", encoding="utf-8") as f_json:
        json.dump(dictionnaire_fiche, f_json, ensure_ascii=False, indent=4)

# =====================================================================
# ⛩️ 4. CONFIGURATION DE LA BARRE LATÉRALE GLOBALE
# =====================================================================
role = st.sidebar.selectbox(
    "👤 Choisissez votre rôle :", 
    ["Accueil", "Joueur (Ma Fiche)", "Maître du Jeu (Hôte)"], 
    key="sb_role_global"
)

# --- BOUTON DE RECHARGEMENT GLOBAL ET SYNCHRONISATION ---
if st.sidebar.button("🔄 Actualiser les données en direct", key="btn_global_sync_refresh"):
    if "fiche_active" in st.session_state:
        del st.session_state["fiche_active"]
    st.toast("🛸 Synchronisation avec la dernière sauvegarde réussie !", icon="⚡")
    st.rerun()
# =====================================================================
# ⛩️ 5. ESPACE LOGIQUE DU JOUEUR (MA FICHE NARRATIVE)
# =====================================================================
if role == "Joueur (Ma Fiche)":
    nom_id = st.sidebar.text_input("⛩️ Saisissez votre prénom :", key="input_prenom_joueur").strip()
    
    if nom_id:
        # Chargement persistant en mémoire tampon de Session State
        if "fiche_active" not in st.session_state or st.session_state.get("joueur_courant") != nom_id:
            st.session_state["fiche_active"] = charger_fiche(nom_id)
            st.session_state["joueur_courant"] = nom_id
            
        f = st.session_state["fiche_active"]
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📌 Navigation")
        onglet_actif = st.sidebar.radio(
            "Choisir la zone à afficher :",
            [
                "📜 Ma Feuille de Personnage", 
                "🔨 Laboratoire de Forge & Recyclage",
                "🎲 Calculateur de Dés Tactique",
                "🏛️ Grand Catalogue des Techniques", 
                "🛒 Marché d'Émeraude",
                "💎 Progression & Expérience",
                "🩸 S'infliger un État / Blessure"
            ],
            key="radio_navigation_globale"
        )

        # =====================================================================
        # 📜 ONGLET 1 : MA FEUILLE DE PERSONNAGE (BLOC ÉTAT-CIVIL & ÉCOLES)
        # =====================================================================
        if onglet_actif == "📜 Ma Feuille de Personnage":
            st.header(f"👤 Votre Feuille Dynamique — {nom_id}")
            
            st.subheader("📝 État-Civil Tactique")
            col_civ1, col_civ2, col_civ3 = st.columns(3)
            
            f["perso"] = col_civ1.text_input("Nom du Personnage :", value=f.get("perso", ""))
            
            clan_actuel = col_civ2.selectbox(
                "Sélectionnez votre Clan :", 
                list(DATA_CLANS.keys()), 
                index=list(DATA_CLANS.keys()).index(f.get("clan", "Grue")) if f.get("clan") in DATA_CLANS else 1
            )
            f["clan"] = clan_actuel
            
            liste_familles_filtrees = DATA_CLANS[clan_actuel]
            famille_actuelle = col_civ3.selectbox(
                "Sélectionnez votre Famille :", 
                liste_familles_filtrees, 
                index=liste_familles_filtrees.index(f.get("famille")) if f.get("famille") in liste_familles_filtrees else 0
            )
            f["famille"] = famille_actuelle
            
            col_civ4, col_civ5, col_civ6 = st.columns(3)
            f["genre"] = col_civ4.selectbox("Genre :", ["Homme", "Femme", "Autre"], index=0 if f.get("genre") == "Homme" else 1 if f.get("genre") == "Femme" else 2, key="sb_mini_genre")
            f["espece"] = col_civ5.text_input("Espèce :", value=f.get("espece", "Humain"), key="ti_mini_espece")
            f["rang_ecole"] = col_civ6.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
            f["profil"] = st.multiselect("Sélectionnez votre ou vos Rôles :", ROLES_LISTE, default=f.get("profil", ["Bushi"]))

            # --- SÉLECTION D'ÉCOLE DÉPORTÉE ---
            db_ecoles_source = CATALOGUE_ECOLES if 'CATALOGUE_ECOLES' in globals() else {}
            ecoles_triees = sorted(db_ecoles_source.items(), key=lambda x: (x[1].get("clan", ""), x[0]))
            
            liste_choix_ecoles = ["-- Choisir une École Impériale --"]
            for nom_ecole, data_ecole in ecoles_triees:
                clan_nom = data_ecole.get("clan", "Sans Clan")
                liste_choix_ecoles.append(f"[{clan_nom}] {nom_ecole}")
                
            ecole_actuelle = f.get("ecole", "")
            idx_defaut_ecole = 0
            if ecole_actuelle:
                for idx, option in enumerate(liste_choix_ecoles):
                    if ecole_actuelle in option:
                        idx_defaut_ecole = idx
                        break
                        
            sel_ecole_brute = st.selectbox("🏫 Sélectionner votre École d'Origine :", liste_choix_ecoles, index=idx_defaut_ecole, key="sb_selection_ecole_triee")
            
            if sel_ecole_brute != "-- Choisir une École Impériale --":
                vrai_nom_ecole = sel_ecole_brute.split("] ")[1]
                f["ecole"] = vrai_nom_ecole
                infos_ecole = db_ecoles_source[vrai_nom_ecole]
                tech_autorisees = ", ".join(infos_ecole.get("techniques_autorisees", []))
                
                st.markdown(
                    f"ℹ️ **Informations de l'école :**\n"
                    f"• **Rôle / Profil :** *{infos_ecole.get('role')}*\n"
                    f"• **Enseignements autorisés :** `{tech_autorisees}`\n"
                    f"• **Notes de l'école :** _{infos_ecole.get('notes', 'Aucune note particulière.')}_"
                )
            else:
                st.caption("⚠️ Aucune école sélectionnée pour le moment.")
            # =====================================================================
            # ☯️ 6. LES CINQ ANNEAUX ET REPERES CRITIQUES
            # =====================================================================
            st.markdown("---")
            st.subheader("🌀 Les Cinq Anneaux Élémentaires")
            
            col_an1, col_an2, col_an3, col_an4, col_an5 = st.columns(5)
            with col_an1: 
                f["anneau_air"] = col_an1.slider("Air 💨", 1, 6, value=int(f.get("anneau_air", 2)), key="sl_an_air")
                f["score_b_air"] = col_an1.selectbox("B. Crit. Air :", list(range(0, 17)), index=int(f.get("score_b_air", 0)), key="sb_b_air")
            with col_an2: 
                f["anneau_terre"] = col_an2.slider("Terre 🏔️", 1, 6, value=int(f.get("anneau_terre", 2)), key="sl_an_terre")
                f["score_b_terre"] = col_an2.selectbox("B. Crit. Terre :", list(range(0, 17)), index=int(f.get("score_b_terre", 0)), key="sb_b_terre")
            with col_an3: 
                f["anneau_feu"] = col_an3.slider("Feu 🔥", 1, 6, value=int(f.get("anneau_feu", 2)), key="sl_an_feu")
                f["score_b_feu"] = col_an3.selectbox("B. Crit. Feu :", list(range(0, 17)), index=int(f.get("score_b_feu", 0)), key="sb_b_feu")
            with col_an4: 
                f["anneau_eau"] = col_an4.slider("Eau 💧", 1, 6, value=int(f.get("anneau_eau", 2)), key="sl_an_eau")
                f["score_b_eau"] = col_an4.selectbox("B. Crit. Eau :", list(range(0, 17)), index=int(f.get("score_b_eau", 0)), key="sb_b_eau")
            with col_an5: 
                f["anneau_vide"] = col_an5.slider("Vide 🌌", 1, 6, value=int(f.get("anneau_vide", 2)), key="sl_an_vide")
                f["score_b_vide"] = col_an5.selectbox("B. Crit. Vide :", list(range(0, 17)), index=int(f.get("score_b_vide", 0)), key="sb_b_vide")

            # --- EXTRACTEUR POUR LES CALCULS MATHEMATIQUES ---
            val_air = int(f["anneau_air"])
            val_terre = int(f["anneau_terre"])
            val_feu = int(f["anneau_feu"])
            val_eau = int(f["anneau_eau"])
            val_vide = int(f["anneau_vide"])

            # =====================================================================
            # 🧮 7. CALCULATEUR DE STATISTIQUES SECONDAIRES & JAUGES EN DIRECT
            # =====================================================================
            endurance_max = (val_terre + val_feu) * 2
            sang_froid_max = (val_terre + val_eau) * 2
            attention_max = val_air + val_feu
            vigilance_max = (val_air + val_eau) / 2
            points_vide_max = val_vide

            st.markdown("---")
            st.subheader("📊 Vitalité & Défenses Sacrées (Calcul Automatique)")

            # Sécurité anti-débordement si un anneau baisse
            if int(f.get("endurance_actuelle", endurance_max)) > endurance_max:
                f["endurance_actuelle"] = endurance_max
            if int(f.get("sang_froid_actuel", sang_froid_max)) > sang_froid_max:
                f["sang_froid_actuel"] = sang_froid_max
            if int(f.get("points_vide_actuels", points_vide_max)) > points_vide_max:
                f["points_vide_actuels"] = points_vide_max

            col_vit1, col_vit2 = st.columns(2)
            with col_vit1:
                st.markdown(f"❤️ **Endurance Maximale (PV) :** `{endurance_max}`")
                f["endurance_actuelle"] = st.number_input(
                    "Endurance Actuelle :", 
                    min_value=0, max_value=endurance_max, 
                    value=int(f.get("endurance_actuelle", endurance_max)),
                    key="num_endurance_live_v6"
                )
                st.progress(f["endurance_actuelle"] / endurance_max if endurance_max > 0 else 0)
                st.markdown(f"🎯 **Attention (Focus Initiative) :** `{attention_max}`")
                
            with col_vit2:
                st.markdown(f"🧠 **Sang-Froid Maximal (Stress) :** `{sang_froid_max}`")
                f["sang_froid_actuel"] = st.number_input(
                    "Sang-Froid Actuel :", 
                    min_value=0, max_value=sang_froid_max, 
                    value=int(f.get("sang_froid_actuel", sang_froid_max)),
                    key="num_sangfroid_live_v6"
                )
                st.progress(f["sang_froid_actuel"] / sang_froid_max if sang_froid_max > 0 else 0)
                st.markdown(f"👁️ **Vigilance Passive :** `{vigilance_max}`")

            st.markdown("---")
            st.markdown(f"🌌 **Points de Vide Disponibles :** Max théorique `{points_vide_max}`")
            f["points_vide_actuels"] = st.slider(
                "Ajuster vos Points de Vide restants :",
                min_value=0, max_value=points_vide_max,
                value=int(f.get("points_vide_actuels", points_vide_max)),
                key="slider_points_vide_live"
            )
            # =====================================================================
            # ⚔️ 8. POSTURE DE COMBAT ACTIVE
            # =====================================================================
            st.markdown("---")
            st.subheader("⚔️ Posture de Combat Temporaire")
            
            val_air_posture = 2 if f["rang_ecole"] >= 4 else 1
            liste_postures = ["Air", "Terre", "Feu", "Eau", "Vide"]
            
            posture_sauvegardee = f.get("posture", "Air")
            idx_posture = liste_postures.index(posture_sauvegardee) if posture_sauvegardee in liste_postures else 0
            
            posture = st.selectbox("Sélectionner votre Posture Active :", liste_postures, index=idx_posture, key="sb_posture_combat_active_v6")
            f["posture"] = posture

            dict_postures = {
                "Air": f"💨 **Posture de l'Air :** Le niveau de difficulty/ND des tests des adversaires pour vous cibler augmente de {val_air_posture}.",
                "Terre": "🏔️ **Posture de la Terre :** Les adversaires ne peuvent pas dépenser d'aubaines pour vous infliger de coups critiques ou d'états.",
                "Feu": "🔥 **Posture du Feu :** +1 succès BONUS par aubaine gardée lors d'un test d'action offensive.",
                "Eau": "💧 **Posture de l'Eau :** Vous pouvez effectuer une action supplémentaire à votre tour (qui ne soit pas du même type).",
                "Vide": "🌌 **Posture du Vide :** Vous ne gagnez aucun point de stress/conflit lié aux effets néfastes."
            }
            st.info(dict_postures.get(posture, "Aucune posture active"))

            # =====================================================================
            # ⚖️ 9. CARACTÉRISTIQUES SOCIALES (0 À 100)
            # =====================================================================
            st.markdown("---")
            st.subheader("⚖️ Caractéristiques Sociales")
            cs1, cs2, cs3 = st.columns(3)
            f["hon"] = cs1.slider("Honneur", 0, 100, value=f.get("hon", 50), key="sl_social_hon")
            f["glo"] = cs2.slider("Gloire", 0, 100, value=f.get("glo", 50), key="sl_social_glo")
            f["sta"] = cs3.slider("Statut", 0, 100, value=f.get("sta", 50), key="sl_social_sta")

            # =====================================================================
            # 🎭 10. GRILLE DES 25 COMPÉTENCES OFFICIELLES
            # =====================================================================
            st.markdown("---")
            st.subheader("🎭 Grille des 25 Compétences Officielles")
            
            with st.expander("🎨 1. Compétences Artisanales"):
                cart1, cart2, cart3, cart4, cart5 = st.columns(5)
                f["comp_artisanat"] = cart1.slider("Artisanat", 0, 6, value=f.get("comp_artisanat", 0), key="sl_c_art")
                f["comp_composition"] = cart2.slider("Composition", 0, 6, value=f.get("comp_composition", 0), key="sl_c_comp")
                f["comp_design"] = cart3.slider("Design", 0, 6, value=f.get("comp_design", 0), key="sl_c_des")
                f["comp_esthetique"] = cart4.slider("Esthétique", 0, 6, value=f.get("comp_esthetique", 0), key="sl_c_est")
                f["comp_forgeron"] = cart5.slider("Forgeron 🔨", 0, 6, value=f.get("comp_forgeron", 0), key="sl_c_forg")
                
            with st.expander("⚔️ 2. Compétences Martiales"):
                cm1, cm2, cm3, cm4, cm5 = st.columns(5)
                f["comp_armes_de_poing"] = cm1.slider("Armes de poing", 0, 6, value=f.get("comp_armes_de_poing", 0), key="sl_c_poing")
                f["comp_armes_de_jet"] = cm2.slider("Armes de jet", 0, 6, value=f.get("comp_armes_de_jet", 0), key="sl_c_jet")
                f["comp_arts_martiaux_(corps_à_corps)"] = cm3.slider("C-à-C (Sabre...)", 0, 6, value=f.get("comp_arts_martiaux_(corps_à_corps)", 0), key="sl_c_cac")
                f["comp_arts_martiaux_(distance)"] = cm4.slider("Distance (Arc...)", 0, 6, value=f.get("comp_arts_martiaux_(distance)", 0), key="sl_c_dist")
                f["comp_arts_martiaux_(mains_nues)"] = cm5.slider("Mains nues", 0, 6, value=f.get("comp_arts_martiaux_(mains_nues)", 0), key="sl_c_mains")
                
            with st.expander("📜 3. Compétences Savantes"):
                csav1, csav2, csav3, csav4, csav5, csav6 = st.columns(6)
                f["comp_culture"] = csav1.slider("Culture", 0, 6, value=f.get("comp_culture", 0), key="sl_c_cult")
                f["comp_medecine"] = csav2.slider("Médecine", 0, 6, value=f.get("comp_medecine", 0), key="sl_c_med")
                f["comp_meditation"] = csav3.slider("Méditation", 0, 6, value=f.get("comp_meditation", 0), key="sl_c_medit")
                f["comp_sentiment"] = csav4.slider("Sentiment", 0, 6, value=f.get("comp_sentiment", 0), key="sl_c_sent")
                f["comp_tactique"] = csav5.slider("Tactique", 0, 6, value=f.get("comp_tactique", 0), key="sl_c_tact")
                f["comp_theologie"] = csav6.slider("Théologie", 0, 6, value=f.get("comp_theologie", 0), key="sl_c_theo")
                
            with st.expander("🗣️ 4. Compétences Sociales"):
                csoc1, csoc2, csoc3, csoc4, csoc5 = st.columns(5)
                f["comp_commandement"] = csoc1.slider("Commandement", 0, 6, value=f.get("comp_commandement", 0), key="sl_c_cmd")
                f["comp_courtoisie"] = csoc2.slider("Courtoisie", 0, 6, value=f.get("comp_courtoisie", 0), key="sl_c_court")
                f["comp_jeux"] = csoc3.slider("Jeux", 0, 6, value=f.get("comp_jeux", 0), key="sl_c_jeux")
                f["comp_performance"] = csoc4.slider("Performance", 0, 6, value=f.get("comp_performance", 0), key="sl_c_perf")
                f["comp_ruse"] = csoc5.slider("Ruse", 0, 6, value=f.get("comp_ruse", 0), key="sl_c_ruse")
                
            with st.expander("🛠️ 5. Compétences Professionnelles"):
                cprof1, cprof2, cprof3, cprof4 = st.columns(4)
                f["comp_commerce"] = cprof1.slider("Commerce", 0, 6, value=f.get("comp_commerce", 0), key="sl_c_comm")
                f["comp_chasse"] = cprof2.slider("Chasse / Survie", 0, 6, value=f.get("comp_chasse", 0), key="sl_c_chas")
                f["comp_navigation"] = cprof3.slider("Navigation", 0, 6, value=f.get("comp_navigation", 0), key="sl_c_nav")
                f["comp_travail_manuel"] = cprof4.slider("Travail manuel", 0, 6, value=f.get("comp_travail_manuel", 0), key="sl_c_man")
            # =====================================================================
            # 🛡️ 11. ARSENAL & EQUIPEMENTS ACTIVEVENT PORTÉS
            # =====================================================================
            st.markdown("---")
            st.subheader("🛡️ Arsenal & Équipement Tactique Porté")
            
            # Initialisation sécurisée des métriques globales
            if "w_md_2mains" not in st.session_state: st.session_state["w_md_2mains"] = False
            if "w_mg_2mains" not in st.session_state: st.session_state["w_mg_2mains"] = False

            liste_toutes_armes = ["Aucune"] + [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme"]

            # Récupération des armes enregistrées pour le chargement visuel
            arme_md_sauvee = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Droite"), None)
            nom_actuel_md = arme_md_sauvee["nom"] if arme_md_sauvee else "Aucune"

            arme_mg_sauvee = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Gauche"), None)
            nom_actuel_mg = arme_mg_sauvee["nom"] if arme_mg_sauvee else "Aucune"

            col_arsenal_droite1, col_arsenal_droite2 = st.columns(2)

            with col_arsenal_droite1:
                # --- GESTION MAIN DROITE ---
                md_est_grisee = st.session_state["w_mg_2mains"] and nom_actuel_mg != "Aucune"
                
                if md_est_grisee:
                    st.selectbox("✋ Arme en Main Droite :", [f"Grise ({nom_actuel_md} au fourreau ⚔️)"], disabled=True, key="sel_w_md_disabled_v6")
                    sel_md = nom_actuel_md
                    st.session_state["w_md_2mains"] = False
                else:
                    idx_md = liste_toutes_armes.index(nom_actuel_md) if nom_actuel_md in liste_toutes_armes else 0
                    sel_md = st.selectbox("✋ Arme en Main Droite :", liste_toutes_armes, index=idx_md, key="sel_w_md_live_v6")
                    
                    if sel_md != "Aucune":
                        obj_md_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_md), None)
                        stats_md_temp = CATALOGUE_ARMES_AVANCE.get(obj_md_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if obj_md_temp else {}
                        
                        if stats_md_temp.get("prise_autorisee") == "2 mains":
                            st.session_state["w_md_2mains"] = True
                            st.caption("ℹ️ Cette arme requiert vos deux mains.")
                        else:
                            st.session_state["w_md_2mains"] = st.checkbox("👐 Tenir à 2 mains (Main Droite)", value=st.session_state["w_md_2mains"], key="chk_2m_md_v6")
                            if st.session_state["w_md_2mains"]:
                                st.session_state["w_mg_2mains"] = False
                    else:
                        st.session_state["w_md_2mains"] = False

            with col_arsenal_droite2:
                # --- GESTION MAIN GAUCHE ---
                mg_est_grisee = st.session_state["w_md_2mains"] and sel_md != "Aucune"
                
                if mg_est_grisee:
                    st.selectbox("🛡️ Équipement en Main Gauche :", [f"Grise ({nom_actuel_mg} au fourreau ⚔️)"], disabled=True, key="sel_w_mg_disabled_v6")
                    sel_mg = nom_actuel_mg
                    st.session_state["w_mg_2mains"] = False
                else:
                    idx_mg = liste_toutes_armes.index(nom_actuel_mg) if nom_actuel_mg in liste_toutes_armes else 0
                    sel_mg = st.selectbox("🛡️ Équipement en Main Gauche :", liste_toutes_armes, index=idx_mg, key="sel_w_mg_live_v6")
                    
                    if sel_mg != "Aucune":
                        obj_mg_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_mg), None)
                        stats_mg_temp = CATALOGUE_ARMES_AVANCE.get(obj_mg_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if obj_mg_temp else {}
                        
                        if stats_mg_temp.get("prise_autorisee") == "2 mains":
                            st.session_state["w_md_2mains"] = True
                            st.caption("ℹ️ Cette arme requiert vos deux mains.")
                        else:
                            st.session_state["w_mg_2mains"] = st.checkbox("👐 Tenir à 2 mains (Main Gauche)", value=st.session_state["w_mg_2mains"], key="chk_2m_mg_v6")
                            if st.session_state["w_mg_2mains"]:
                                st.session_state["w_md_2mains"] = False
                    else:
                        st.session_state["w_mg_2mains"] = False

            # --- SYNCHRONISATION EN DIRECT DES ÉTATS DANS LA BASE DE DONNÉES ---
            for w in f["inventaire_sac"]:
                if w["type_cat"] == "Arme":
                    if w["nom"] == sel_md and not md_est_grisee:
                        w["main_equipee"] = "Main Droite"
                        w["prise_main"] = "2 mains" if st.session_state["w_md_2mains"] else "1 main"
                    elif w["nom"] == sel_mg and not mg_est_grisee:
                        w["main_equipee"] = "Main Gauche"
                        w["prise_main"] = "2 mains" if st.session_state["w_mg_2mains"] else "1 main"
                    else:
                        w["main_equipee"] = "Aucune"
            # --- 12. COMPILATION DES CARACTÉRISTIQUES D'ARMES EN DIRECT ---
            arme_md_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] == sel_md), None)
            arme_mg_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] == sel_mg), None)

            st.markdown("##### 📊 Statistiques de Combat Courantes")
            
            # Calcul et affichage Main Droite
            if sel_md != "Aucune" and arme_md_finale:
                if md_est_grisee:
                    st.caption("✋ **Main Droite :** 😴 *Arme rangée au fourreau (Inutilisable actuellement)*")
                else:
                    w_base_md = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1"})
                    bonus_2m_md = 1 if st.session_state["w_md_2mains"] else 0
                    degats_totaux_md = w_base_md["degats"] + arme_md_finale.get("bonus_degats", 0) + bonus_2m_md
                    danger_total_md = w_base_md["danger"] + arme_md_finale.get("bonus_danger", 0)
                    st.write(f"✋ **Main Droite ({sel_md}) :** Dégâts : `{degats_totaux_md}` | Danger : `{danger_total_md}` | Compétence : `{w_base_md.get('competence', 'Mêlée')}` | Portée : `{w_base_md.get('portee', '1')}`")
            else:
                st.caption("✋ **Main Droite :** Vide")

            # Calcul et affichage Main Gauche
            if sel_mg != "Aucune" and arme_mg_finale:
                if mg_est_grisee:
                    st.caption("🛡️ **Main Gauche :** 😴 *Arme rangée au fourreau (Inutilisable actuellement)*")
                else:
                    w_base_mg = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1"})
                    bonus_2m_mg = 1 if st.session_state["w_mg_2mains"] else 0
                    degats_totaux_mg = w_base_mg["degats"] + arme_mg_finale.get("bonus_degats", 0) + bonus_2m_mg
                    danger_total_mg = w_base_mg["danger"] + arme_mg_finale.get("bonus_danger", 0)
                    st.write(f"🛡️ **Main Gauche ({sel_mg}) :** Dégâts : `{degats_totaux_mg}` | Danger : `{danger_total_mg}` | Compétence : `{w_base_mg.get('competence', 'Mêlée')}` | Portée : `{w_base_mg.get('portee', '1')}`")
            else:
                st.caption("🛡️ **Main Gauche :** Vide")

            # --- 13. GESTION DE L'ARMURE PORTÉE ---
            st.markdown("---")
            st.markdown("##### 👘 Armure Équipée")
            
            armure_active_obj = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Armure" and obj.get("equipe", False)), None)
            liste_armures_sac = ["Aucune"] + [a["nom"] for a in f["inventaire_sac"] if a["type_cat"] == "Armure"]
            nom_a_actuelle = armure_active_obj["nom"] if armure_active_obj else "Aucune"
            
            sel_armure = st.selectbox("👘 Sélectionner l'Armure Active :", liste_armures_sac, index=liste_armures_sac.index(nom_a_actuelle) if nom_a_actuelle in liste_armures_sac else 0, key="sel_a_active_live_v6")
            
            # Synchronisation de l'armure portée dans le sac
            for a in f["inventaire_sac"]:
                if a["type_cat"] == "Armure":
                    a["equipe"] = (a["nom"] == sel_armure)
            
            armure_portee_obj = next((a for a in f["inventaire_sac"] if a["type_cat"] == "Armure" and a["equipe"]), None)
            if armure_portee_obj:
                a_base_stats = CATALOGUE_ARMURES.get(armure_portee_obj.get("modele_racine", "Armure de Cuir Bouilli"), {"res_p": 1, "res_s": 0})
                res_p = a_base_stats["res_p"] + armure_portee_obj.get("bonus_res_p", 0)
                res_s = a_base_stats["res_s"] + armure_portee_obj.get("bonus_res_s", 0)
                st.info(f"🔰 **Résistance Physique actuelle :** `{res_p}` | **Résistance Surnaturelle :** `{res_s}`")
            else:
                st.caption("❌ Aucune armure portée. Votre samouraï combat en vêtements simples.")
            # =====================================================================
            # 🎒 14. INVENTAIRE INTERACTIF DU SAC À DOS
            # =====================================================================
            st.markdown("---")
            st.subheader("🎒 Inventaire Interactif du Sac à Dos")
            
            if "inventaire_sac" not in f or not f["inventaire_sac"]:
                st.info("Votre sac à dos est totalement vide.")
            else:
                obj_analyse = None
                for item in f["inventaire_sac"]:
                    col_item_nom, col_item_eq, col_item_oeil, col_item_croix = st.columns([2, 1, 0.5, 0.5])
                    
                    statut_port = "📦 [Sac]"
                    if item.get("type_cat") == "Arme":
                        if item.get("main_equipee") in ["Main Droite", "Main Gauche"]:
                            statut_port = f"🎯 [{item['main_equipee']}]"
                    elif item.get("type_cat") == "Armure" and item.get("equipe"):
                        statut_port = "🎯 [Portée]"
                        
                    col_item_nom.write(f"**{statut_port} {item['nom']}**")
                    col_item_eq.write(f"*{item.get('type_cat', 'Divers')}*")

                    if col_item_oeil.button("👁️", key=f"oeil_obj_{item['id_obj']}"):
                        f["objet_regarde_id"] = item["id_obj"]
                    
                    if col_item_croix.button("❌", key=f"del_obj_{item['id_obj']}"):
                        f["inventaire_sac"].remove(item)
                        if f.get("objet_regarde_id") == item["id_obj"]:
                            f["objet_regarde_id"] = None
                        sauver_fiche(nom_id, f)
                        st.rerun()
                
                # --- FENÊTRE DE DIAGNOSTIC DES OBJETS REGARDÉS ---
                if f.get("objet_regarde_id"):
                    obj_analyse = next((obj for obj in f["inventaire_sac"] if obj["id_obj"] == f["objet_regarde_id"]), None)
                    
                if obj_analyse:
                    st.markdown("---")
                    with st.chat_message("assistant", avatar="🔍"):
                        st.markdown(f"#### 🔍 Analyse de l'objet : **{obj_analyse['nom']}**")
                        
                        if obj_analyse.get("type_cat") == "Arme":
                            w_racine = obj_analyse.get("modele_racine", "Katana")
                            w_base = CATALOGUE_ARMES_AVANCE.get(w_racine, {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1", "proprietes": "Aucune"})
                            
                            degats_calcul_visu = w_base["degats"] + obj_analyse.get("bonus_degats", 0)
                            danger_calcul_visu = w_base["danger"] + obj_analyse.get("bonus_danger", 0)
                            
                            st.markdown(
                                f"• **Catégorie :** Armes (Type : Sabre / Matériel)\n"
                                f"• **Modèle Racine :** `{w_racine}`\n"
                                f"• **Compétence requise :** *{w_base.get('competence')}*\n"
                                f"• **Portée tactique :** `{w_base.get('portee')}`\n"
                                f"• **Dégâts globaux :** `{degats_calcul_visu}` *(Base {w_base['degats']} + Forge {obj_analyse.get('bonus_degats', 0)})*\n"
                                f"• **Dangerosité :** `{danger_calcul_visu}` *(Base {w_base['danger']} + Forge {obj_analyse.get('bonus_danger', 0)})*\n"
                                f"• **Méthode de Forge appliquée :** *{obj_analyse.get('methode_forge', 'Aucune')}*\n"
                                f"• **Propriétés de l'arme :** _{obj_analyse.get('proprietes_custom', w_base.get('proprietes'))}_\n"
                                f"• **Effets magiques / spéciaux :** _{obj_analyse.get('effet_custom', 'Aucun effet magique actif.')}_"
                            )
                        else:
                            st.markdown(
                                f"• **Catégorie :** {obj_analyse.get('type_cat', 'Divers')}\n"
                                f"• **Propriétés enregistrées :** {obj_analyse.get('proprietes', 'Aucune')}\n"
                                f"• **Détails :** {obj_analyse.get('details', 'Aucun.')}"
                            )
                        
                        if st.button("❌ Fermer l'analyse", key="btn_close_analyse_obj_sac"):
                            f["objet_regarde_id"] = None
                            st.rerun()

            # --- 15. AFFICHAGE DES ÉTATS SUBIS SUR LA FEUILLE ---
            st.markdown("---")
            st.subheader("🩸 États & Blessures Actifs")
            if f.get("mes_etats"):
                for affliction in f["mes_etats"]:
                    st.write(f"• **{affliction}**")
            else:
                st.info("✨ Aucun état handicapant ou blessure majeure sur votre feuille.")

            # --- 16. LE BOUTON ROUGE SACRÉ DE SAUVEGARDE ET SYNCHRONISATION ---
            st.markdown("---")
            if st.button("🧧 ENREGISTRER EN PARCHEMIN (Sauvegarde et Actualisation)", key="btn_sauve_parchemin_v6", use_container_width=True):
                st.session_state["fiche_active"] = f
                sauver_fiche(nom_id, f)
                st.toast("📜 Le Parchemin Ancestral a été scellé et enregistré sur le serveur !", icon="🔥")
                st.rerun()
        # =====================================================================
        # 📖 MON GRIMOIRE PERSONNEL (TECHNIQUES MAÎTRISÉES ENRICHIES)
        # =====================================================================
        st.markdown("---")
        st.subheader("📖 Mon Grimoire de Techniques Personnelles")
        
        cles_techniques = {
            "Katas 📚": "mes_katas", "Kihos 🧘": "mes_kihos", "Invocations 🌪️": "mes_invocs",
            "Rituels 📜": "mes_rituels", "Shujis 🎭": "mes_shujis", "Mahos 🩸": "mes_mahos",
            "Ninjutsus 🥷": "mes_ninjutsus", "Inversions ☯️": "mes_inversions"
        }

        db_descriptions = DESCRIPTIONS_LORE if 'DESCRIPTIONS_LORE' in globals() else {}
        tech_possedee_trouvee = False
        
        for label_cat, cle_fiche in cles_techniques.items():
            if cle_fiche not in f: f[cle_fiche] = []
            
            if f[cle_fiche]:
                tech_possedee_trouvee = True
                st.markdown(f"**🔹 {label_cat} :**")
                for t_nom in f[cle_fiche]:
                    col_t_nom, col_t_oeil, col_t_del = st.columns([3, 0.5, 0.5])
                    col_t_nom.write(f"• {t_nom}")
                    
                    if col_t_oeil.button("👁️", key=f"look_my_t_{cle_fiche}_{t_nom.replace(' ', '_')}"):
                        st.session_state["tech_grimoire_inspectee"] = t_nom
                        
                    if col_t_del.button("❌", key=f"forget_t_{cle_fiche}_{t_nom.replace(' ', '_')}"):
                        f[cle_fiche].remove(t_nom)
                        if st.session_state.get("tech_grimoire_inspectee") == t_nom:
                            st.session_state["tech_grimoire_inspectee"] = None
                        sauver_fiche(nom_id, f)
                        st.error(f"🔮 Technique {t_nom} oubliée.")
                        st.rerun()
                        
        if not tech_possedee_trouvee:
            st.info("Votre grimoire personnel est vide. Utilisez le catalogue pour apprendre des techniques.")

        # 🎪 BULLE D'INFORMATION INTERACTIVE (Œil du Grimoire)
        if st.session_state.get("tech_grimoire_inspectee"):
            t_active = st.session_state["tech_grimoire_inspectee"]
            texte_lore_officiel = db_descriptions.get(t_active, "📜 *Aucune description rédigée dans DESCRIPTIONS_LORE pour cette technique.*")
            
            st.markdown("---")
            with st.chat_message("assistant", avatar="🔮"):
                st.markdown(f"##### Parchemin de Technique : **{t_active}**")
                st.text(texte_lore_officiel)
                if st.button("❌ Fermer la bulle de lecture", key="btn_close_bubble_tech"):
                    st.session_state["tech_grimoire_inspectee"] = None
                    st.rerun()

        # =====================================================================
        # 💎 INTERCEPTION DE L'ONGLET : PROGRESSION & EXPÉRIENCE
        # =====================================================================
        if onglet_actif == "💎 Progression & Expérience":
            st.title("💎 Gestion et Allocation de l'Expérience")
            st.info("Suivez l'évolution de vos points d'apprentissage accumulés et dépensés au cours de vos chroniques.")
            
            if "xp_accumulee" not in f: f["xp_accumulee"] = 0
            if "xp_depensee_rang" not in f: f["xp_depensee_rang"] = 0
            if "xp_depensee_libre" not in f: f["xp_depensee_libre"] = 0
            
            f["xp_accumulee"] = st.slider("1. Points d'Expérience (XP) Accumulés au total :", min_value=0, max_value=100, value=f["xp_accumulee"], key="sl_xp_acc")
            f["xp_depensee_rang"] = st.slider("2. XP dépensés dans le Rang d'École actuel :", min_value=0, max_value=100, value=f["xp_depensee_rang"], key="sl_xp_rng")
            f["xp_depensee_libre"] = st.slider("3. Expérience dépensée librement (Avantages/Compétences annexes) :", min_value=0, max_value=100, value=f["xp_depensee_libre"], key="sl_xp_lib")
            
            xp_restante = f["xp_accumulee"] - (f["xp_depensee_rang"] + f["xp_depensee_libre"])
            
            st.markdown("### 📊 Bilan du Parchemin d'Apprentissage")
            if xp_restante < 0:
                st.error(f"⚠️ Alerte : Vos d'épenses dépassent votre XP accumulée ! (Déficit de {xp_restante} XP)")
            else:
                st.success(f"🔮 Il vous reste **{xp_restante} XP libres** à allouer pour vos prochaines augmentations de caractéristiques.")
        # =====================================================================
        # 🎲 INTERCEPTION DE L'ONGLET : CALCULATEUR DE DÉS TACTIQUE
        # =====================================================================
        if onglet_actif == "🎲 Calculateur de Dés Tactique":
            st.title("🎲 Calculateur de Dés Tactique")
            st.caption("Préparez vos lancers de dés L5R en sélectionnant votre approche narrative.")
            
            type_action = st.radio("Sélectionner la complexité de l'action :", ["Action Simple / Standard", "Action Spéciale / Narrative"], key="rad_type_action")
            
            if type_action == "Action Spéciale / Narrative":
                st.text_input("📝 Écrivez l'action spécifique que votre personnage tente de réaliser :", placeholder="Ex: Infiltrer le dojo de nuit...", key="ti_action_speciale")
                st.info("ℹ️ Exposez votre approche narrative au Maître du Jeu pour valider les modificateurs.")
            else:
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    anneau_choisi = st.selectbox("☯️ 1. Choisir l'Anneau (D6) :", ["Air", "Terre", "Feu", "Eau", "Vide"], key="sb_action_anneau")
                    score_anneau = f.get(f"anneau_{anneau_choisi.lower()}", 2)
                    
                with col_act2:
                    dict_toutes_competences = {
                        "Artisanales 🎨": ["Artisanat", "Composition", "Design", "Esthétique", "Forgeron"],
                        "Martiales ⚔️": ["Armes de poing", "Armes de jet", "Arts martiaux (Corps à corps)", "Arts martiaux (Distance)", "Arts martiaux (Mains nues)", "Méditation"],
                        "Savantes 📜": ["Commerce", "Culture", "Théologie", "Médecine", "Sentiment", "Tactique"],
                        "Sociales 🎭": ["Commandement", "Courtoisie", "Jeux", "Ruse", "Performance"],
                        "Professionnelles ⚒️": ["Commerce (Pro)", "Chasse", "Navigation", "Survie", "Travail manuel"]
                    }
                    
                    liste_deroulante_comp = ["Aucune (0 dé)"]
                    for categorie, liste_sous_comps in dict_toutes_competences.items():
                        for comp in liste_sous_comps:
                            liste_deroulante_comp.append(f"{comp} ({categorie.split()[0]})")
                    
                    comp_choisie_brute = st.selectbox("📚 2. Choisir la Compétence Spécifique (D12) :", liste_deroulante_comp, key="sb_action_comp_advanced")
                    
                    score_comp = 0
                    nom_competence_propre = "Aucune"
                    
                    if comp_choisie_brute != "Aucune (0 dé)":
                        nom_competence_propre = comp_choisie_brute.split(" (")[0]
                        cle_dictionnaire_comp = f"comp_{nom_competence_propre.lower().replace(' ', '_').replace('-', '_').replace('à', 'à')}"
                        score_comp = f.get(cle_dictionnaire_comp, 0)
                        
                with col_act3:
                    liste_armes_sac_sim = ["Aucune"] + [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme"]
                    arme_choisie_sim = st.selectbox("⚔️ 3. Arme en main (Facultatif) :", liste_armes_sac_sim, key="sb_action_arme")
                    
                    txt_arme_bonus = ""
                    if arme_choisie_sim != "Aucune":
                        obj_w_sim = next((w for w in f["inventaire_sac"] if w["nom"] == arme_choisie_sim), None)
                        if obj_w_sim:
                            w_racine = obj_w_sim.get("modele_racine", "Katana")
                            data_racine = CATALOGUE_ARMES_AVANCE.get(w_racine, {})
                            txt_arme_bonus = f"\n• **Propriétés de l'arme :** *{data_racine.get('proprietes', 'Aucune')}* (Portée: {data_racine.get('portee', '1')})"

                st.markdown("##### 📊 Composition de votre Réserve de Dés :")
                st.success(
                    f"🔥 **Sous l'approche de l'Anneau de {anneau_choisi} :**\n"
                    f"• Vous lancez **{score_anneau} Dés d'Anneau (D6)**\n"
                    f"• Vous ajoutez **{score_comp} Dés de Compétence (D12)** *(via votre maîtrise en : {nom_competence_propre})*\n"
                    f"👉 **Total théorique à lancer :** `{score_anneau} D6` + `{score_comp} D12`"
                    f"{txt_arme_bonus}"
                )
                
        # =====================================================================
        # 🎖️ INTERCEPTION DE L'ONGLET : TITRES HONORIFIQUES
        # =====================================================================
        if onglet_actif == "🎖️ Titres Honorifiques":
            st.title("🎖️ Titres Impériaux & Distinctions")
            st.caption("Consultez et revendiquez les titres de gloire décernés à votre samouraï.")
            
            if "titres_obtenus" not in f: f["titres_obtenus"] = []
            
            catalogue_titres_l5r = {
                "Magistrat d'Émeraude (Adjoint)": "Accorde une autorité légale sur les terres impériales. +5 en Gloire.",
                "Héros du Mur des Bâtisseurs": "Reconnaissance de bravoure face à l'Outremonde. +1 en Endurance Maximale.",
                "Chamberlain Intérimaire du Clan": "Accorde un accès privilégié aux requêtes logistiques de votre maison de Clan."
            }
            
            st.markdown("### 📜 Vos Titres Actuels")
            if f["titres_obtenus"]:
                for t_nom in f["titres_obtenus"]:
                    with st.expander(f"🏅 {t_nom}"):
                        st.write(catalogue_titres_l5r.get(t_nom, "Effet narratif spécifique validé par le MJ."))
            else:
                st.info("Votre personnage n'a pas encore obtenu de titre honorifique au cours de cette chronique.")
                
            st.markdown("---")
            st.markdown("##### 🔍 Revendiquer un Titre du Catalogue")
            liste_titres_choix = ["-- Sélectionner un titre --"] + [t for t in catalogue_titres_l5r.keys() if t not in f["titres_obtenus"]]
            sel_t_honor = st.selectbox("Titres disponibles dans cette aventure :", liste_titres_choix, key="sb_titres_h")
            
            if sel_t_honor != "-- Sélectionner un titre --" and st.button("🏅 S'octroyer ce Titre", key="btn_add_titre_h"):
                f["titres_obtenus"].append(sel_t_honor)
                sauver_fiche(nom_id, f)
                st.success(f"Le titre '{sel_t_honor}' est désormais inscrit dans vos annales !")
                st.rerun()

        # =====================================================================
        # 🩸 INTERCEPTION DE L'ONGLET : CLINIQUE DES AFFLICTIONS
        # =====================================================================
        if onglet_actif == "🩸 S'infliger un État / Blessure":
            st.title("🩸 Tribunal des Afflictions et Blessures")
            st.info("🎯 Sélectionnez ici les malus ou blessures majeures imposés par le scénario ou le Maître du Jeu.")
            
            db_etats_source = CATALOGUE_ETATS_BLESSURES if 'CATALOGUE_ETATS_BLESSURES' in globals() else {}
            
            liste_options_dispo = ["-- Choisir un malus à appliquer --"]
            for categorie_aff, dict_contenu in db_etats_source.items():
                for nom_aff in dict_contenu.keys():
                    if nom_aff not in f.get("mes_etats", []):
                        liste_options_dispo.append(f"{nom_aff} ({categorie_aff})")
                        
            sel_nouvel_effet = st.selectbox("Sélectionner l'affliction à transférer sur votre feuille :", liste_options_dispo, key="sb_onglet_dedie_malus")
            
            if sel_nouvel_effet != "-- Choisir un malus à appliquer --":
                nom_propre_aff = sel_nouvel_effet.split(" (")[0]
                if "mes_etats" not in f: f["mes_etats"] = []
                f["mes_etats"].append(nom_propre_aff)
                sauver_fiche(nom_id, f)
                st.success(f"💥 L'état '{nom_propre_aff}' a été appliqué.")
                st.rerun()

        # =====================================================================
        # 🛒 INTERCEPTION DE L'ONGLET : MARCHÉ D'ÉMERAUDE
        # =====================================================================
        if onglet_actif == "🛒 Marché d'Émeraude":
            st.title("🛒 Le Marché de l'Empire d'Émeraude")
            st.info("🛍️ Achetez vos équipements ici. Les objets sélectionnés seront automatiquement ajoutés à votre Sac à Dos.")
            
            col_cat1, col_cat2, col_cat3 = st.columns(3)
            
            with col_cat1:
                st.markdown("**1. Catégorie : Armes**")
                w_achat = st.selectbox("Sélectionner une arme :", list(CATALOGUE_ARMES_AVANCE.keys()) if 'CATALOGUE_ARMES_AVANCE' in globals() else [], key="buy_w_sel")
                if w_achat and st.button("➕ Ajouter l'Arme", key="btn_buy_w"):
                    f["inventaire_sac"].append({
                        "id_obj": int(time.time()), "nom": f"{w_achat} standard", "modele_racine": w_achat, "type_cat": "Arme", 
                        "details": "Standard", "main_equipee": "Aucune", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": "Aucune"
                    })
                    sauver_fiche(nom_id, f)
                    st.success(f"✨ {w_achat} a été glissé dans votre sac !")
                    st.rerun()
                    
            with col_cat2:
                st.markdown("**2. Catégorie : Armures**")
                a_achat = st.selectbox("Sélectionner une armure :", list(CATALOGUE_ARMURES.keys()) if 'CATALOGUE_ARMURES' in globals() else [], key="buy_a_sel")
                if a_achat and st.button("➕ Ajouter l'Armure", key="btn_buy_a"):
                    f["inventaire_sac"].append({
                        "id_obj": int(time.time()), "nom": f"{a_achat} standard", "modele_racine": a_achat, "type_cat": "Armure", 
                        "details": "Standard", "equipe": False, "bonus_res_p": 0, "bonus_res_s": 0, "proprietes": "Aucune"
                    })
                    sauver_fiche(nom_id, f)
                    st.success(f"✨ {a_achat} a été suspendue dans votre sac !")
                    st.rerun()

            with col_cat3:
                st.markdown("**3. Catégorie : Objets Divers**")
                liste_divers = list(CATALOGUE_DIVERS.keys()) if 'CATALOGUE_DIVERS' in globals() else []
                if liste_divers:
                    d_achat = st.selectbox("Sélectionner un utilitaire :", liste_divers, key="boutique_divers_unique_sel")
                    if st.button("➕ Ajouter l'Objet Divers", key="btn_buy_d_sac"):
                        d_stats = CATALOGUE_DIVERS[d_achat]
                        f["inventaire_sac"].append({
                            "id_obj": int(time.time()), "nom": d_achat, "type_cat": "Divers", 
                            "details": f"Type : {d_stats['type']}.", "proprietes": d_stats["effet"], "equipe": False
                        })
                        sauver_fiche(nom_id, f)
                        st.success(f"✨ {d_achat} glissé dans le sac !")
                        st.rerun()
                else:
                    st.caption("ℹ️ Aucun objet divers disponible dans le catalogue.")

        # =====================================================================
        # 🔨 INTERCEPTION DE L'ONGLET : FORGE ET MODIFICATION
        # =====================================================================
        if onglet_actif == "🔨 Laboratoire de Forge & Recyclage":
            st.title("🔨 Forge et Modification")
            st.info("🔧 Modifiez, personnalisez et appliquez des techniques de forge ancestrales sur vos équipements.")
            
            liste_armes_sac_forge = [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme"]
            if liste_armes_sac_forge:
                w_a_forger = st.selectbox("Sélectionner l'arme à travailler :", liste_armes_sac_forge, key="sb_forge_w_v2")
                arme_forge_obj = next((w for w in f["inventaire_sac"] if w["nom"] == w_a_forger), None)
                
                if arme_forge_obj:
                    st.markdown(f"### ⚔️ Travail sur : **{arme_forge_obj['nom']}**")
                    
                    w_racine = arme_forge_obj.get("modele_racine", "Katana")
                    w_base = CATALOGUE_ARMES_AVANCE.get(w_racine, {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1", "proprietes": "Aucune"})
                    
                    st.caption(f"📦 Modèle d'origine : {w_racine} | Type : Sabre / Arme | Portée d'usine : {w_base.get('portee')}")
                    
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        arme_forge_obj["bonus_degats"] = st.number_input("➕ Modifier le bonus de Dégâts :", min_value=-5, max_value=10, value=arme_forge_obj.get("bonus_degats", 0), key=f"f_deg_{arme_forge_obj['id_obj']}")
                    with col_f2:
                        arme_forge_obj["bonus_danger"] = st.number_input("⚠️ Modifier le bonus de Danger :", min_value=-5, max_value=10, value=arme_forge_obj.get("bonus_danger", 0), key=f"f_dng_{arme_forge_obj['id_obj']}")
                    
                    new_nom_w = st.text_input("📝 Renommer l'arme sur l'enclume :", value=arme_forge_obj["nom"], key=f"f_nom_{arme_forge_obj['id_obj']}")
                    if new_nom_w != arme_forge_obj["nom"]:
                        arme_forge_obj["nom"] = new_nom_w
                        sauver_fiche(nom_id, f)
                        st.rerun()
                        
                    dict_methodes_forge = {
                        "Aucune": "Aucune modification de structure.",
                        "Pliage de l'Acier Kakita": "Ajoute la propriété 'Acérée'. Réduit de 1 la rareté théorique.",
                        "Forge Spirituelle Asahina": "Ajoute l'effet : Vous pouvez dépenser 1 aubaine du Vide pour infliger des dégâts surnaturels.",
                        "Trempe à l'Eau Kaiu": "Ajoute la propriété 'Solide'. L'arme ne peut jamais être brisée par un effet critique."
                    }
                    methode_actuelle = arme_forge_obj.get("methode_forge", "Aucune")
                    idx_default = list(dict_methodes_forge.keys()).index(methode_actuelle) if methode_actuelle in dict_methodes_forge else 0
                    
                    sel_methode = st.selectbox("⚒️ Sélectionner la Méthode de Forge :", list(dict_methodes_forge.keys()), index=idx_default, key=f"f_methode_{arme_forge_obj['id_obj']}")
                    
                    if sel_methode != methode_actuelle:
                        arme_forge_obj["methode_forge"] = sel_methode
                        arme_forge_obj["effet_methode"] = dict_methodes_forge[sel_methode]
                        sauver_fiche(nom_id, f)
                        st.rerun()
                        
                    if sel_methode != "Aucune":
                        st.info(f"✨ **Bonus de méthode actif :** {dict_methodes_forge[sel_methode]}")

                    arme_forge_obj["proprietes_custom"] = st.text_area("🔮 Propriétés additionnelles de l'arme (Ex: Cérémoniale) :", value=arme_forge_obj.get("proprietes_custom", w_base.get("proprietes", "Aucune")), key=f"f_prop_{arme_forge_obj['id_obj']}")
                    arme_forge_obj["effet_custom"] = st.text_area("📜 Effets spéciaux narratifs ou magiques :", value=arme_forge_obj.get("effet_custom", ""), key=f"f_eff_{arme_forge_obj['id_obj']}")
                    
                    if st.button("💾 Valider et Forger l'arme", key=f"btn_save_forge_{arme_forge_obj['id_obj']}"):
                        sauver_fiche(nom_id, f)
                        st.success("🔥 L'arme a été retrempée et mise à jour avec succès dans votre sac !")
                        st.rerun()
            else:
                st.warning("⚠️ Aucune arme dans votre sac à dos pour utiliser la forge.")

        # =====================================================================
        # 🏛️ INTERCEPTION DE L'ONGLET : GRAND CATALOGUE DES TECHNIQUES
        # =====================================================================
        if onglet_actif == "🏛️ Grand Catalogue des Techniques":
            st.title("🏛️ Le Grand Catalogue des Techniques d'Émeraude")
            st.info("💡 Parcourez les écoles de l'Empire. En apprenant une technique, elle s'ajoutera instantanément à votre Grimoire Personnel.")
            
            db_globale_tech = CATALOGUE_COMPLET if 'CATALOGUE_COMPLET' in globals() else {}
            db_descriptions = DESCRIPTIONS_LORE if 'DESCRIPTIONS_LORE' in globals() else {}

            liste_grands_types = ["-- Sélectionner --"] + list(db_globale_tech.keys())
            cat_selectionne = st.selectbox("🔍 1. Choisir la catégorie de Technique :", liste_grands_types, key="sb_grand_cat_dr")
            
            if cat_selectionne != "-- Sélectionner --":
                cle_fiche_cible = cles_techniques.get(f"{cat_selectionne} ") or cles_techniques.get(next((k for k in cles_techniques.keys() if cat_selectionne.split()[0] in k), ""))
                sous_categories_dict = db_globale_tech[cat_selectionne]
                
                liste_sous_types = ["-- Sélectionner --"] + list(sous_categories_dict.keys())
                filtre_sous_type = st.selectbox(f"🎯 2. Sous-catégorie ({cat_selectionne}) :", liste_sous_types, key="sb_dr_sub")
                
                if filtre_sous_type != "-- Sélectionner --":
                    rangs_disponibles_dict = sous_categories_dict[filtre_sous_type]
                    
                    liste_rangs = ["-- Sélectionner --"] + list(rangs_disponibles_dict.keys())
                    filtre_rang = st.selectbox("📊 3. Filtrer par Rang :", liste_rangs, key="sb_dr_rang")
                    
                    if filtre_rang != "-- Sélectionner --":
                        liste_noms_techniques = rangs_disponibles_dict[filtre_rang]
                        st.markdown(f"📋 **Techniques disponibles d'après votre fichier `techniques.py` :**")
                        
                        if not liste_noms_techniques:
                            st.info("ℹ️ Aucune technique n'est enregistrée dans cette sous-catégorie pour le moment.")
                        else:
                            for t_nom in liste_noms_techniques:
                                deja_apprise = t_nom in f.get(cle_fiche_cible, [])
                                texte_lore = db_descriptions.get(t_nom, "📜 *Description technique en attente de rédaction dans le fichier.*")
                                
                                with st.expander(f"{'✅ (Maîtrisé)' if deja_apprise else '✨'} {t_nom} ({filtre_sous_type})"):
                                    st.text(texte_lore)
                                    
                                    if deja_apprise:
                                        st.caption("✔️ Cette technique est déjà inscrite dans votre grimoire personnel.")
                                    else:
                                        if st.button(f"🧠 Apprendre {t_nom}", key=f"learn_dr_{cat_selectionne}_{t_nom.replace(' ', '_')}"):
                                            if cle_fiche_cible:
                                                f[cle_fiche_cible].append(t_nom)
                                                sauver_fiche(nom_id, f)
                                                st.success(f"🔮 {t_nom} a été mémorisé dans votre Grimoire !")
                                                st.rerun()

        # --- BLOC DE SAUVEGARDE UNIVERSELLE FILTRÉE & PERSISTANCE ---
        if nom_id and f:
            sauver_fiche(nom_id, f)
            st.session_state["fiche_active"] = f
