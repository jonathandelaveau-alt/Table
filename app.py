import streamlit as st
import json
import os
import time

# 1. IMPORTATION LOGIQUE DES BASES DE DONNÉES DÉPORTÉES
from equipements import CATALOGUE_ARMURES, CATALOGUE_ARMES_AVANCE, CATALOGUE_DIVERS
from techniques import CATALOGUE_COMPLET, DESCRIPTIONS_LORE
from etats_blessures import CATALOGUE_ETATS_BLESSURES
from ecoles import CATALOGUE_ECOLES

# 2. Configuration et Design Sombre L5A
st.set_page_config(page_title="L5A - Table Tactique Évoluée", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    h1, h2, h3, h4 { color: #f1c40f !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #8b0000 !important; color: white !important; font-weight: bold; border: 1px solid #ff4500 !important; }
    [data-testid="stSidebar"] { background-color: #181818 !important; border-right: 1px solid #2b2b2b; }
    </style>
""", unsafe_allow_html=True)

DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
ACTIONS_FILE = "notifications_mj.json"

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

def sauver_fiche(nom_joueur, data):
    with open(os.path.join(DB_DIR, f"{nom_joueur.lower().strip()}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def charger_fiche(nom_joueur):
    path = os.path.join(DB_DIR, f"{nom_joueur.lower().strip()}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return None

@st.dialog("📜 Parchemin de Technique")
def afficher_details_technique(nom_technique):
    st.write(f"### {nom_technique}")
    texte_details = DESCRIPTIONS_LORE.get(nom_technique, "Aucune description détaillée enregistrée pour cette capacité d'école.")
    st.info(texte_details)
    if st.button("Fermer le parchemin"):
        st.rerun()

# =====================================================================
# ⛩️ CONFIGURATION DE LA BARRE LATÉRALE ET DE LA NAVIGATION
# =====================================================================
role = st.sidebar.selectbox(
    "👤 Choisissez votre rôle :", 
    ["Accueil", "Joueur (Ma Fiche)", "Maître du Jeu (Hôte)"], 
    key="sb_role_global"
)

# Initialisation par défaut pour éviter les erreurs de lecture plus bas
onglet_actif = "📜 Ma Feuille de Personnage"

if role == "Joueur (Ma Fiche)":
    nom_id = st.sidebar.text_input("⛩️ Saisissez votre prénom :", key="input_prenom_joueur").strip()
    
    if nom_id:
        f = charger_fiche(nom_id)
        if not f: 
            f = {}
            
        st.sidebar.markdown("---")
        st.sidebar.subheader("📌 Navigation")
        
        # Le sélecteur étendu à 7 onglets indépendants
        onglet_actif = st.sidebar.radio(
            "Choisir la zone à afficher :",
            [
                "📜 Ma Feuille de Personnage", 
                "🔨 Forge et Modification",
                "🎲 Calculateur de Dés Tactique",
                "🏛️ Grand Catalogue des Techniques", 
                "🛒 Marché d'Émeraude",
                "🩸 S'infliger un État / Blessure"  # <-- Nouvel onglet ajouté ici
            ],
            key="radio_navigation_globale"
        )

        if onglet_actif == "📜 Ma Feuille de Personnage":
            st.header(f"👤 Votre Feuille Dynamique — {nom_id}")
            # (Ici continue votre code habituel avec vos anneaux, caractéristiques, etc.)
        
        # --- RÉCUPÉRATION DES SÉCURITÉS INITIALES ---
        air_score = int(f.get("air", 1))
        terre_score = int(f.get("terre", 1))
        feu_score = int(f.get("feu", 1))
        eau_score = int(f.get("eau", 1))
        vide_score = int(f.get("vide", 1))
        
        # --- CENTRALISATION IMMÉDIATE DU DICTIONNAIRE DE SAUVEGARDE (MAJ) ---
        maj = {
            "perso": f.get("perso", ""), "clan": f.get("clan", "Grue"), "famille": f.get("famille", ""), 
            "profil": f.get("profil", ["Bushi"]), "ecole": f.get("ecole", ""), "rang_ecole": f.get("rang_ecole", 1), 
            "posture": f.get("posture", "Air"), "air": air_score, "terre": terre_score, "feu": feu_score, "eau": eau_score, "vide": vide_score, 
            "p_vide": f.get("p_vide", 1), "end_act": f.get("end_act", (terre_score + feu_score) * 2), "sf_act": f.get("sf_act", (terre_score + eau_score) * 2), 
            "hon": f.get("hon", 50), "glo": f.get("glo", 50), "sta": f.get("sta", 50), 
            "armure_active": f.get("armure_active", "Aucune"), "res_p": f.get("res_p", 1), "res_s": f.get("res_s", 0), 
            "arme_active": f.get("arme_active", "Aucune"), "w_deg": f.get("w_deg", 3), "deux_mains": f.get("deux_mains", False), 
            "w_dang": f.get("w_dang", 5), "w_por": f.get("w_por", "1"), 
            "ch_kat": f.get("ch_kat", False), "ch_kih": f.get("ch_kih", False), "ch_inv": f.get("ch_inv", False), 
            "ch_rit": f.get("ch_rit", False), "ch_shu": f.get("ch_shu", False), "ch_mah": f.get("ch_mah", False), 
            "ch_nin": f.get("ch_nin", False), "ch_invs": f.get("ch_invs", False),
            "score_b_air": f.get("score_b_air", 0), "score_b_terre": f.get("score_b_terre", 0), "score_b_feu": f.get("score_b_feu", 0), 
            "score_b_eau": f.get("score_b_eau", 0), "score_b_vide": f.get("score_b_vide", 0),
            "e_saignant": f.get("e_saignant", False), "e_etourdi": f.get("e_etourdi", False), "e_compromis": f.get("e_compromis", False), 
            "e_inconscient": f.get("e_inconscient", False), "e_aveugle": f.get("e_aveugle", False),
            "b_legere": f.get("b_legere", False), "b_grave": f.get("b_grave", False), "b_mutilante": f.get("b_mutilante", False),
            "mes_katas": f.get("mes_katas", []), "mes_kihos": f.get("mes_kihos", []), "mes_invocs": f.get("mes_invocs", []), 
            "mes_rituels": f.get("mes_rituels", []), "mes_shujis": f.get("mes_shujis", []), "mes_mahos": f.get("mes_mahos", []), 
            "mes_ninjutsus": f.get("mes_ninjutsus", []), "mes_inversions": f.get("mes_inversions", []),
            "tech_active_cliquee": f.get("tech_active_cliquee", "Aucune technique active"), 
            "sh_anneaux": f.get("sh_anneaux", True), "sh_vitalite": f.get("sh_vitalite", True), "sh_social": f.get("sh_social", True), 
            "sh_equipement": f.get("sh_equipement", True), "sh_grimoire": f.get("sh_grimoire", True), 
            "inventaire_sac": f.get("inventaire_sac", []),
            "c_est": f.get("c_est", 0), "c_com": f.get("c_com", 0), "c_sty": f.get("c_sty", 0), "c_forg": f.get("c_forg", 0), 
            "c_for": f.get("c_for", 0), "c_cac": f.get("c_cac", 0), "c_dis": f.get("c_dis", 0), "c_chu": f.get("c_chu", 0), 
            "c_med": f.get("c_med", 0), "c_tac": f.get("c_tac", 0), "c_cul": f.get("c_cul", 0), "c_gou": f.get("c_gou", 0), 
            "c_mdc": f.get("c_mdc", 0), "c_sen": f.get("c_sen", 0), "c_the": f.get("c_the", 0), "c_cmd": f.get("c_cmd", 0), 
            "c_crt": f.get("c_crt", 0), "c_jeu": f.get("c_jeu", 0), "c_org": f.get("c_org", 0), "c_cmr": f.get("c_cmr", 0), 
            "c_tra": f.get("c_tra", 0), "c_nav": f.get("c_nav", 0), "c_mag": f.get("c_mag", 0), "c_sur": f.get("c_sur", 0)
        }

        # --- TOUR DE CONTRÔLE : RAFRAÎCHISSEMENT & SAUVEGARDE MANUELLE ---
        col_ctrl1, col_ctrl2 = st.columns(2)
        if col_ctrl1.button("🔄 Actualiser mes données en direct", key="refresh_joueur_manuel"):
            st.rerun()
            
        if col_ctrl2.button("💾 Enregistrer mon Parchemin (Sécurité)", key="save_joueur_manuel"):
            sauver_fiche(nom_id, maj)
            st.success("📝 Vos données ont été gravées avec succès dans la base !")

        st.subheader("📝 État-Civil Tactique")
        col_civ1, col_civ2, col_civ3 = st.columns(3)
        nom_perso = col_civ1.text_input("Nom du Personnage :", value=f.get("perso", ""))
        clan_actuel = col_civ2.selectbox("Sélectionnez votre Clan :", list(DATA_CLANS.keys()), index=list(DATA_CLANS.keys()).index(f.get("clan", "Grue")) if f.get("clan") in DATA_CLANS else 1)
        liste_familles_filtrees = DATA_CLANS[clan_actuel]
        famille_actuelle = col_civ3.selectbox("Sélectionnez votre Famille :", liste_familles_filtrees, index=liste_familles_filtrees.index(f.get("famille")) if f.get("famille") in liste_familles_filtrees else 0)
        f["genre"] = st.selectbox("Genre :", ["Homme", "Femme", "Autre"], index=0 if f.get("genre") == "Homme" else 1 if f.get("genre") == "Femme" else 2, key="sb_mini_genre")
        f["espece"] = st.text_input("Espèce :", value=f.get("espece", "Humain"), key="ti_mini_espece")

        col_civ4, col_civ5, col_civ6 = st.columns(3)
        rang_ecole = col_civ5.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
        roles_actuels = col_civ6.multiselect("Sélectionnez votre ou vos Rôles :", ROLES_LISTE, default=f.get("profil", ["Bushi"]))
        # =====================================================================
        # 🏫 SÉLECTION D'ÉCOLE (TRIÉE PAR CLAN ET PAR ORDRE ALPHABÉTIQUE)
        # =====================================================================
        db_ecoles_source = CATALOGUE_ECOLES if 'CATALOGUE_ECOLES' in globals() else {}
        
        # 1. Tri des écoles : d'abord par le nom du Clan, puis par le nom de l'École
        ecoles_triees = sorted(
            db_ecoles_source.items(), 
            key=lambda x: (x[1].get("clan", ""), x[0])
        )
        
        # 2. Construction de la liste pour le menu déroulant avec repère visuel du Clan
        liste_choix_ecoles = ["-- Choisir une École Impériale --"]
        for nom_ecole, data_ecole in ecoles_triees:
            clan_nom = data_ecole.get("clan", "Sans Clan")
            liste_choix_ecoles.append(f"[{clan_nom}] {nom_ecole}")
            
        # 3. Récupération de l'école actuellement enregistrée sur la fiche du joueur
        ecole_actuelle = f.get("ecole", "")
        # Recherche de l'index par défaut dans la liste déroulante
        idx_defaut_ecole = 0
        if ecole_actuelle:
            for idx, option in enumerate(liste_choix_ecoles):
                if ecole_actuelle in option:
                    idx_defaut_ecole = idx
                    break
                    
        # 4. Affichage du menu de sélection
        sel_ecole_brute = st.selectbox(
            "🏫 Sélectionner votre École d'Origine :", 
            liste_choix_ecoles, 
            index=idx_defaut_ecole, 
            key="sb_selection_ecole_triee"
        )
        
        # 5. Si une école est sélectionnée, on enregistre et on affiche ses caractéristiques
        if sel_ecole_brute != "-- Choisir une École Rokugan --":
            # On extrait le vrai nom de l'école en enlevant le préfixe du clan
            vrai_nom_ecole = sel_ecole_brute.split("] ")[1]
            
            # Sauvegarde automatique si le joueur change d'école
            if f.get("ecole") != vrai_nom_ecole:
                f["ecole"] = vrai_nom_ecole
                sauver_fiche(nom_id, f)
                st.rerun()
                
            # Affichage des informations de l'école sélectionnée
            infos_ecole = db_ecoles_source[vrai_nom_ecole]
            tech_autorisees = ", ".join(infos_ecole.get("techniques_autorisees", []))
            
            st.markdown(
                f"ℹ️ **Informations de l'école :**\n"
                f"• **Clan Majeur :** {infos_ecole.get('clan')}\n"
                f"• **Rôle / Profil :** *{infos_ecole.get('role')}*\n"
                f"• **Enseignements autorisés :** `{tech_autorisees}`\n"
                f"• **Notes de l'école :** _{infos_ecole.get('notes', 'Aucune note particulière.')}_"
            )
        else:
            st.caption("⚠️ Aucune école sélectionnée pour le moment. Veuillez en choisir une dans la liste ci-dessus.")
            
# --- BOUTON D'ACTUALISATION ET SYNCHRONISATION EN DIRECT ---
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Actualiser les données en direct", key="btn_global_sync_refresh"):
    st.toast("⚡ Synchronisation avec le serveur réussie !", icon="🛸")
    st.rerun()

        posture = st.selectbox("Posture Active de combat :", ["Air", "Terre", "Feu", "Eau", "Vide"], index=["Air", "Terre", "Feu", "Eau", "Vide"].index(f.get("posture", "Air")))
        valeur_air_posture = 2 if int(rang_ecole) >= 4 else 1
        EFFETS_POSTURES = {
            "Air": f"💨 **Posture de l'Air :** Le niveau de difficulté des tests d'attaque/manipulation contre vous augmente de {valeur_air_posture}.",
            "Terre": "🏔️ **Posture de la Terre :** Vos adversaires ne peuvent pas dépenser leurs aubaines pour des coups critiques ou des États.",
            "Feu": "🔥 **Posture du Feu :** En cas de réussite, vous gagnez un succès BONUS par conflit sur les dégâts et dés gardés.",
            "Eau": "💧 **Posture de l'Eau :** Effectuez une seconde action (sans test requis, ni même type).",
            "Vide": "🌌 **Posture du Vide :** Les conflits obtenus lors des tests ne vous infligent aucun point de stress."
        }
        st.info(EFFETS_POSTURES[posture])

        st.subheader("📊 Vitalité & Défenses")
        sh_vitalite = st.checkbox("👁️ Partager mes jauges avec le MJ", value=f.get("sh_vitalite", True))
        
        air_score = int(f.get("air", 1))
        terre_score = int(f.get("terre", 1))
        feu_score = int(f.get("feu", 1))
        eau_score = int(f.get("eau", 1))
        
        end_m = (terre_score + feu_score) * 2
        sf_m = (terre_score + eau_score) * 2
        cv1, cv2 = st.columns(2)
        end_act = cv1.number_input(f"Endurance Actuelle (Max: {end_m}) :", 0, end_m, value=min(f.get("end_act", end_m), end_m))
        sf_act = cv2.number_input(f"Sang-froid Actuel (Max: {sf_m}) :", 0, sf_m, value=min(f.get("sf_act", sf_m), sf_m))
        
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
                # Extraction propre du nom
                nom_propre_aff = sel_nouvel_effet.split(" (")[0]
                
                if "mes_etats" not in f:
                    f["mes_etats"] = []
                    
                f["mes_etats"].append(nom_propre_aff)
                
                # --- SAUVEGARDE UNIVERSELLE AUTOMATIQUE ---
                sauver_fiche(nom_id, f)
                st.success(f"💥 L'état '{nom_propre_aff}' a été appliqué. Retrouvez-le sur votre onglet 'Feuille de Personnage' !")
                st.rerun()
            
        st.subheader("🌀 Les Cinq Anneaux")
        sh_anneaux = st.checkbox("👁️ Partager mes 5 Anneaux avec le MJ", value=f.get("sh_anneaux", True))
        air = st.slider("Air 💨", 1, 5, value=air_score)
        score_b_air = st.selectbox("Score de Blessure Critique - Air (0 à 16) :", list(range(0, 17)), index=int(f.get("score_b_air", 0)), key="sb_air")
        st.markdown("---")
        terre = st.slider("Terre 🏔️", 1, 5, value=terre_score)
        score_b_terre = st.selectbox("Score de Blessure Critique - Terre (0 à 16) :", list(range(0, 17)), index=int(f.get("score_b_terre", 0)), key="sb_terre")
        st.markdown("---")
        feu = st.slider("Feu 🔥", 1, 5, value=feu_score)
        score_b_feu = st.selectbox("Score de Blessure Critique - Feu (0 à 16) :", list(range(0, 17)), index=int(f.get("score_b_feu", 0)), key="sb_feu")
        st.markdown("---")
        eau = st.slider("Eau 💧", 1, 5, value=eau_score)
        score_b_eau = st.selectbox("Score de Blessure Critique - Eau (0 à 16) :", list(range(0, 17)), index=int(f.get("score_b_eau", 0)), key="sb_eau")
        st.markdown("---")
        vide = st.slider("Vide 🌌", 1, 5, value=int(f.get("vide", 1)))
        score_b_vide = st.selectbox("Score de Blessure Critique - Vide (0 à 16) :", list(range(0, 17)), index=int(f.get("score_b_vide", 0)), key="sb_vide")
        st.markdown("---")
        p_vide = st.number_input("Points de Vide Actuels", 0, vide, value=f.get("p_vide", 1))

        st.subheader("⚖️ Caractéristiques Sociales (0 à 100)")
        sh_social = st.checkbox("👁️ Partager mes caractéristiques sociales avec le MJ", value=f.get("sh_social", True))
        cs1, cs2, cs3 = st.columns(3)
        hon = cs1.slider("Honneur", 0, 100, value=f.get("hon", 50))
        glo = cs2.slider("Gloire", 0, 100, value=f.get("glo", 50))
        sta = cs3.slider("Statut", 0, 100, value=f.get("sta", 50))

        st.subheader("🎭 Grille des 25 Compétences Officielles")
        with st.expander("🎨 1. Compétences Artisanales"):
            cart1, cart2, cart3, cart4 = st.columns(4)
            c_est, c_com, c_sty, c_forg = cart1.slider("Esthétique", 0, 6, value=f.get("c_est", 0)), cart2.slider("Composition", 0, 6, value=f.get("c_com", 0)), cart3.slider("Stylisme", 0, 6, value=f.get("c_sty", 0)), cart4.slider("Forge 🔨", 0, 6, value=f.get("c_forg", 0))
        with st.expander("⚔️ 2. Compétences Martiales"):
            cm1, cm2, cm3, cm4, cm5, cm6 = st.columns(6)
            c_for, c_cac, c_dis, c_chu, c_med, c_tac = cm1.slider("Forme", 0, 6, value=f.get("c_for", 0)), cm2.slider("Corps-à-corps", 0, 6, value=f.get("c_cac", 0)), cm3.slider("Distance", 0, 6, value=f.get("c_dis", 0)), cm4.slider("Corps Humain", 0, 6, value=f.get("c_chu", 0)), cm5.slider("Méditation", 0, 6, value=f.get("c_med", 0)), cm6.slider("Tactique", 0, 6, value=f.get("c_tac", 0))
        with st.expander("📜 3. Compétences Savantes"):
            csav1, csav2, csav3, csav4, csav5 = st.columns(5)
            c_cul, c_gou, c_mdc, c_sen, c_the = csav1.slider("Culture", 0, 6, value=f.get("c_cul", 0)), csav2.slider("Gouvernement", 0, 6, value=f.get("c_gou", 0)), csav3.slider("Médecine", 0, 6, value=f.get("c_mdc", 0)), csav4.slider("Sentiment", 0, 6, value=f.get("c_sen", 0)), csav5.slider("Théologie", 0, 6, value=f.get("c_the", 0))
        with st.expander("🗣️ 4. Compétences Sociales"):
            csoc1, csoc2, csoc3, csoc4 = st.columns(4)
            c_cmd, c_crt, c_jeu, c_org = csoc1.slider("Commandement", 0, 6, value=f.get("c_cmd", 0)), csoc2.slider("Courtoisie", 0, 6, value=f.get("c_crt", 0)), csoc3.slider("Jeu", 0, 6, value=f.get("c_jeu", 0)), csoc4.slider("Organisation 📋", 0, 6, value=f.get("c_org", 0))
        with st.expander("🛠️ 5. Compétences Professionnelles"):
            cprof1, cprof2, cprof3, cprof4, fprof5 = st.columns(5)
            c_cmr, c_tra, c_nav, c_mag, c_sur = cprof1.slider("Commerce", 0, 6, value=f.get("c_cmr", 0)), cprof2.slider("Travail Manuel", 0, 6, value=f.get("c_tra", 0)), cprof3.slider("Navigation", 0, 6, value=f.get("c_nav", 0)), cprof4.slider("Magouille", 0, 6, value=f.get("c_mag", 0)), fprof5.slider("Survie", 0, 6, value=f.get("c_sur", 0))
        st.subheader("🛡️ Arsenal & Inventaire Global")
        sh_equipement = st.checkbox("👁️ Partager mes équipements équipés avec le MJ", value=f.get("sh_equipement", True))
        
        # --- INITIALISATION ROBUSTE DE L'INVENTAIRE SAC À DOS ---
        if "inventaire_sac" not in f:
            f["inventaire_sac"] = [
                {"id_obj": 1, "nom": "Katana d'école", "modele_racine": "Katana", "type_cat": "Arme", "details": "Modèle standard d'école.", "main_equipee": "Main Droite", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": "Acérée, Cérémoniale"},
                {"id_obj": 2, "nom": "Wakizashi de base", "modele_racine": "Wakizashi", "type_cat": "Arme", "details": "Lame courte de protection.", "main_equipee": "Aucune", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": "Acérée, Cérémoniale"},
                {"id_obj": 3, "nom": "Armure de Tenue de Cérémonie", "modele_racine": "Armure de Tenue de Cérémonie", "type_cat": "Armure", "details": "Modèle standard.", "equipe": True, "bonus_res_p": 0, "bonus_res_s": 0, "proprietes": "Cérémonielle, Magnifique"}
            ]

        # Nettoyage et synchronisation de sécurité pour chaque objet du sac
        for obj in f["inventaire_sac"]:
            if "main_equipee" not in obj: obj["main_equipee"] = "Aucune"
            if "prise_main" not in obj: obj["prise_main"] = "1 main"

        st.markdown("### ⚔️ Votre Équipement Tactique")
        col_arsenal_gauche, col_arsenal_droite = st.columns(2)
        
        with col_arsenal_gauche:
            st.markdown("##### 🎒 Objets en votre possession dans le sac")
            liste_armes_sac = [obj["nom"] for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme"]
            liste_armures_sac = [obj["nom"] for obj in f["inventaire_sac"] if obj["type_cat"] == "Armure"]
            st.write(f"• **Armes possédées :** {', '.join(liste_armes_sac) if liste_armes_sac else 'Aucune'}")
            st.write(f"• **Armures possédées :** {', '.join(liste_armures_sac) if liste_armures_sac else 'Aucune'}")

        # Initialisation sécurisée des métriques globales pour le MJ
        arme_active_nom = "Aucune"
        arme_active_degats = 0
        arme_active_danger = 0
        arme_active_portee = "0"
        res_p, res_s = 0, 0
        armure_active = "Aucune"

        with col_arsenal_droite:
            st.markdown("##### 🎯 Équipements Activement Portés")
            
            # Initialisation des variables de prise à 2 mains dans le Session State si absentes
            if "w_md_2mains" not in st.session_state: st.session_state["w_md_2mains"] = False
            if "w_mg_2mains" not in st.session_state: st.session_state["w_mg_2mains"] = False

            # Liste de toutes les armes disponibles dans le sac (permet de sélectionner des doublons)
            liste_toutes_armes = ["Aucune"] + [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme"]

            # Récupération des armes actuellement enregistrées dans la fiche
            arme_md_sauvee = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Droite"), None)
            nom_actuel_md = arme_md_sauvee["nom"] if arme_md_sauvee else "Aucune"

            arme_mg_sauvee = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Gauche"), None)
            nom_actuel_mg = arme_mg_sauvee["nom"] if arme_mg_sauvee else "Aucune"

            # --- 1. GESTION ET AFFICHAGE MAIN DROITE ---
            # La main droite est grisée si la main gauche est active ET tenue à 2 mains
            md_est_grisee = st.session_state["w_mg_2mains"] and nom_actuel_mg != "Aucune"
            
            if md_est_grisee:
                st.selectbox("✋ Arme en Main Droite :", [f"Grise ({nom_actuel_md} au fourreau ⚔️)"], disabled=True, key="sel_w_md_disabled")
                sel_md = nom_actuel_md  # On garde la sélection en mémoire sans l'effacer
                st.session_state["w_md_2mains"] = False
            else:
                idx_md = liste_toutes_armes.index(nom_actuel_md) if nom_actuel_md in liste_toutes_armes else 0
                sel_md = st.selectbox("✋ Arme en Main Droite :", liste_toutes_armes, index=idx_md, key="sel_w_md_live")
                
                if sel_md != "Aucune":
                    # Détection si le modèle est naturellement à 2 mains
                    obj_md_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_md), None)
                    stats_md_temp = CATALOGUE_ARMES_AVANCE.get(obj_md_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if obj_md_temp else {}
                    
                    if stats_md_temp.get("prise_autorisee") == "2 mains":
                        st.session_state["w_md_2mains"] = True
                        st.caption("ℹ️ Cette arme requiert obligatoirement vos deux mains.")
                    else:
                        st.session_state["w_md_2mains"] = st.checkbox("👐 Tenir à 2 mains (Main Droite)", value=st.session_state["w_md_2mains"], key="chk_2m_md")
                        if st.session_state["w_md_2mains"]:
                            st.session_state["w_mg_2mains"] = False  # Décoche l'autre main
                else:
                    st.session_state["w_md_2mains"] = False
            # --- 2. GESTION ET AFFICHAGE MAIN GAUCHE ---
            # La main gauche est grisée si la main droite est active ET tenue à 2 mains
            mg_est_grisee = st.session_state["w_md_2mains"] and sel_md != "Aucune"
            
            if mg_est_grisee:
                st.selectbox("🛡️ Arme / Équipement en Main Gauche :", [f"Grise ({nom_actuel_mg} au fourreau ⚔️)"], disabled=True, key="sel_w_mg_disabled")
                sel_mg = nom_actuel_mg  # On garde la sélection en mémoire sans l'effacer
                st.session_state["w_mg_2mains"] = False
            else:
                idx_mg = liste_toutes_armes.index(nom_actuel_mg) if nom_actuel_mg in liste_toutes_armes else 0
                sel_mg = st.selectbox("🛡️ Arme / Équipement en Main Gauche :", liste_toutes_armes, index=idx_mg, key="sel_w_mg_live")
                
                if sel_mg != "Aucune":
                    # Détection si le modèle est naturellement à 2 mains
                    obj_mg_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_mg), None)
                    stats_mg_temp = CATALOGUE_ARMES_AVANCE.get(obj_mg_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if obj_mg_temp else {}
                    
                    if stats_mg_temp.get("prise_autorisee") == "2 mains":
                        st.session_state["w_mg_2mains"] = True
                        st.caption("ℹ️ Cette arme requiert obligatoirement vos deux mains.")
                    else:
                        st.session_state["w_mg_2mains"] = st.checkbox("👐 Tenir à 2 mains (Main Gauche)", value=st.session_state["w_mg_2mains"], key="chk_2m_mg")
                        if st.session_state["w_mg_2mains"]:
                            st.session_state["w_md_2mains"] = False  # Décoche l'autre main
                else:
                    st.session_state["w_mg_2mains"] = False

            # --- 3. SYNCHRONISATION SYNTAXIQUE DIRECTE DES ÉTATS DANS LA BASE ---
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

            # Récupération finale des objets validés pour l'affichage des caractéristiques
            arme_md_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] == sel_md), None)
            arme_mg_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] == sel_mg), None)

            # --- 4. AFFICHAGE DES CARACTÉRISTIQUES INDIVIDUELLES EN DIRECT ---
            st.markdown("##### 📊 Statistiques de vos Mains")
            
            # Stats Main Droite
            if sel_md != "Aucune" and arme_md_finale:
                if md_est_grisee:
                    st.caption("✋ **Main Droite :** 😴 *Arme rangée au fourreau (Inutilisable actuellement)*")
                else:
                    w_base_md = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1"})
                    bonus_2m_md = 1 if st.session_state["w_md_2mains"] else 0
                    degats_totaux_md = w_base_md["degats"] + arme_md_finale.get("bonus_degats", 0) + bonus_2m_md
                    st.write(f"✋ **Main Droite ({sel_md}) :** Dégâts : `{degats_totaux_md}` | Danger : `{w_base_md['danger'] + arme_md_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_md.get('competence', 'Mêlée')}` | Portée : `{w_base_md.get('portee', '1')}`")
            else:
                st.caption("✋ **Main Droite :** Vide")

            # Stats Main Gauche
            if sel_mg != "Aucune" and arme_mg_finale:
                if mg_est_grisee:
                    st.caption("🛡️ **Main Gauche :** 😴 *Arme rangée au fourreau (Inutilisable actuellement)*")
                else:
                    w_base_mg = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1"})
                    bonus_2m_mg = 1 if st.session_state["w_mg_2mains"] else 0
                    degats_totaux_mg = w_base_mg["degats"] + arme_mg_finale.get("bonus_degats", 0) + bonus_2m_mg
                    st.write(f"🛡️ **Main Gauche ({sel_mg}) :** Dégâts : `{degats_totaux_mg}` | Danger : `{w_base_mg['danger'] + arme_mg_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_mg.get('competence', 'Mêlée')}` | Portée : `{w_base_mg.get('portee', '1')}`")
            else:
                st.caption("🛡️ **Main Gauche :** Vide")
            # --- 5. COMPILATION DES DONNÉES ENVOYÉES AU RAPPORT MJ ---
            if st.session_state["w_md_2mains"] and arme_md_finale:
                arme_active_nom = arme_md_finale["nom"] + " (À 2 mains 👐)"
                w_base = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                arme_active_degats = w_base["degats"] + arme_md_finale.get("bonus_degats", 0) + 1
                arme_active_danger = w_base["danger"] + arme_md_finale.get("bonus_danger", 0)
                arme_active_portee = w_base["portee"]
            elif st.session_state["w_mg_2mains"] and arme_mg_finale:
                arme_active_nom = arme_mg_finale["nom"] + " (À 2 mains 👐)"
                w_base = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                arme_active_degats = w_base["degats"] + arme_mg_finale.get("bonus_degats", 0) + 1
                arme_active_danger = w_base["danger"] + arme_mg_finale.get("bonus_danger", 0)
                arme_active_portee = w_base["portee"]
            else:
                txt_portes = []
                if sel_md != "Aucune" and arme_md_finale: txt_portes.append(f"MD: {sel_md}")
                if sel_mg != "Aucune" and arme_mg_finale: txt_portes.append(f"MG: {sel_mg}")
                arme_active_nom = " | ".join(txt_portes) if txt_portes else "Aucune"
                
                if sel_md != "Aucune" and arme_md_finale:
                    w_base = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                    arme_active_degats = w_base["degats"] + arme_md_finale.get("bonus_degats", 0)
                    arme_active_danger = w_base["danger"] + arme_md_finale.get("bonus_danger", 0)
                    arme_active_portee = w_base["portee"]

            # --- 6. GESTION DE L'ARMURE PORTÉE ---
            armure_active_obj = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Armure" and obj.get("equipe", False)), None)
            liste_armures_sac = ["Aucune"] + [a["nom"] for a in f["inventaire_sac"] if a["type_cat"] == "Armure"]
            nom_a_actuelle = armure_active_obj["nom"] if armure_active_obj else "Aucune"
            
            sel_armure = st.selectbox("👘 Sélectionner l'Armure Portée :", liste_armures_sac, index=liste_armures_sac.index(nom_a_actuelle) if nom_a_actuelle in liste_armures_sac else 0, key="sel_a_active_live")
            
            for a in f["inventaire_sac"]:
                if a["type_cat"] == "Armure":
                    a["equipe"] = (a["nom"] == sel_armure)
            
            armure_portee_obj = next((a for a in f["inventaire_sac"] if a["type_cat"] == "Armure" and a["equipe"]), None)
            if armure_portee_obj:
                a_base_stats = CATALOGUE_ARMURES.get(armure_portee_obj.get("modele_racine", "Armure de Cuir Bouilli"), {"res_p": 1, "res_s": 0})
                armure_active = armure_portee_obj["nom"]
                res_p = a_base_stats["res_p"] + armure_portee_obj.get("bonus_res_p", 0)
                res_s = a_base_stats["res_s"] + armure_portee_obj.get("bonus_res_s", 0)
                st.info(f"🔰 Résistance Physique : {res_p} | Surnaturelle : {res_s}")
            else:
                st.caption("❌ Aucune armure portée.")
             # =====================================================================
        # 🎒 INVENTAIRE INTERACTIF DU SAC À DOS
        # =====================================================================
        st.markdown("### 🎒 Inventaire Interactif du Sac à Dos")
        if "inventaire_sac" not in f or not f["inventaire_sac"]:
            st.info("Votre sac à dos est totalement vide.")
        else:
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
                    sauver_fiche(nom_id, f)
                    st.rerun()
            
                if f.get("objet_regarde_id"):
                    obj_analyse = next((obj for obj in f["inventaire_sac"] if obj["id_obj"] == f["objet_regarde_id"]), None)
                if obj_analyse:
                    st.markdown("---")
                    with st.chat_message("assistant", avatar="🔍"):
                        st.markdown(f"#### 🔍 Analyse de l'objet : **{obj_analyse['nom']}**")
                        
                        if obj_analyse.get("type_cat") == "Arme":
                            # Extraction synchronisée en direct depuis le fichier equipement.py
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
                            # Analyse standard pour les objets divers ou armures
                            st.markdown(
                                f"• **Catégorie :** {obj_analyse.get('type_cat', 'Divers')}\n"
                                f"• **Propriétés enregistrées :** {obj_analyse.get('proprietes', 'Aucune')}\n"
                                f"• **Détails :** {obj_analyse.get('details', 'Aucun.')}"
                            )
                        
                        if st.button("❌ Fermer l'analyse", key="btn_close_analyse_obj_sac"):
                            f["objet_regarde_id"] = None
                            st.rerun()

        # =====================================================================
        # 📜 LE GRIMOIRE DES TECHNIQUES IMPÉRIALES
        # =====================================================================
        st.markdown("---")
        st.subheader("📖 Le Grimoire des Techniques Impériales")
        
        categories_list = [
            ("Katas", "mes_katas", CATALOGUE_KATAS if 'CATALOGUE_KATAS' in globals() else {}),
            ("Kihos", "mes_kihos", CATALOGUE_KIHOS if 'CATALOGUE_KIHOS' in globals() else {}),
            ("Invocations", "mes_invocs", CATALOGUE_INVOCATIONS if 'CATALOGUE_INVOCATIONS' in globals() else {}),
            ("Rituels", "mes_rituels", CATALOGUE_RITUELS if 'CATALOGUE_RITUELS' in globals() else {}),
            ("Shujis", "mes_shujis", CATALOGUE_SHUJIS if 'CATALOGUE_SHUJIS' in globals() else {})
        ]

        for nom_cat, cle_fiche, cat_ref in categories_list:
            if cle_fiche not in f:
                f[cle_fiche] = []
                
            with st.expander(f"✨ {nom_cat} Maîtrisés ({len(f[cle_fiche])})"):
                if f[cle_fiche]:
                    for tech in f[cle_fiche]:
                        col_t_txt, col_t_btn = st.columns([3, 1])
                        col_t_txt.write(f"• {tech}")
                        if col_t_btn.button("❌", key=f"del_t_{cle_fiche}_{tech}"):
                            f[cle_fiche].remove(tech)
                            sauver_fiche(nom_id, f)
                            st.rerun()
                else:
                    st.caption(f"Aucun {nom_cat[:-1]} connu.")

                if cat_ref:
                    liste_choix = ["-- Apprendre --"] + [t for t in cat_ref.keys() if t not in f[cle_fiche]]
                    sel_t = st.selectbox(f"Sélectionner un {nom_cat[:-1]} :", liste_choix, key=f"add_select_{cle_fiche}")
                    if sel_t != "-- Apprendre --" and st.button("🧠 Valider", key=f"btn_add_val_{cle_fiche}"):
                        f[cle_fiche].append(sel_t)
                        sauver_fiche(nom_id, f)
                        st.rerun()

        # =====================================================================
        # 🛒 INTERCEPTION DE L'ONGLET : MARCHÉ D'ÉMERAUDE
        # =====================================================================
        # On ferme l'affichage précédent et on ouvre le code du marché partagé
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
                    
                    # Récupération des statistiques de base du fichier equipement.py
                    w_racine = arme_forge_obj.get("modele_racine", "Katana")
                    w_base = CATALOGUE_ARMES_AVANCE.get(w_racine, {"degats": 3, "danger": 5, "competence": "Martiales (Corps-à-corps)", "portee": "1", "proprietes": "Aucune"})
                    
                    # Rappel des caractéristiques brutes de la pièce
                    st.caption(f"📦 Modèle d'origine : {w_racine} | Type : Sabre / Arme | Portée d'usine : {w_base.get('portee')}")
                    
                    # 1. Variables de combat (Dégâts & Danger côte à côte)
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        arme_forge_obj["bonus_degats"] = st.number_input("➕ Modifier le bonus de Dégâts :", min_value=-5, max_value=10, value=arme_forge_obj.get("bonus_degats", 0), key=f"f_deg_{arme_forge_obj['id_obj']}")
                    with col_f2:
                        arme_forge_obj["bonus_danger"] = st.number_input("⚠️ Modifier le bonus de Danger :", min_value=-5, max_value=10, value=arme_forge_obj.get("bonus_danger", 0), key=f"f_dng_{arme_forge_obj['id_obj']}")
                    
                    # 2. Identité de l'arme
                    new_nom_w = st.text_input("📝 Renommer l'arme sur l'enclume :", value=arme_forge_obj["nom"], key=f"f_nom_{arme_forge_obj['id_obj']}")
                    if new_nom_w != arme_forge_obj["nom"]:
                        arme_forge_obj["nom"] = new_nom_w
                        sauver_fiche(nom_id, f)
                        st.rerun()
                        
                    # 3. Méthodes de forge (Catalogue évolutif L5R)
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

                    # 4. Saisie manuelle des Effets et Propriétés spécifiques
                    arme_forge_obj["proprietes_custom"] = st.text_area("🔮 Propriétés additionnelles de l'arme (Ex: Cérémoniale, Encombrante) :", value=arme_forge_obj.get("proprietes_custom", w_base.get("proprietes", "Aucune")), key=f"f_prop_{arme_forge_obj['id_obj']}")
                    arme_forge_obj["effet_custom"] = st.text_area("📜 Effets spéciaux narratifs ou magiques :", value=arme_forge_obj.get("effet_custom", ""), key=f"f_eff_{arme_forge_obj['id_obj']}")
                    
                    if st.button("💾 Valider et Forger l'arme", key=f"btn_save_forge_{arme_forge_obj['id_obj']}"):
                        sauver_fiche(nom_id, f)
                        st.success("🔥 L'arme a été retrempée et mise à jour avec succès dans votre sac !")
                        st.rerun()
            else:
                st.warning("⚠️ Aucune arme dans votre sac à dos pour utiliser la forge.")

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
            st.info("Votre grimoire est vide. Utilisez le catalogue ci-dessous pour apprendre des techniques.")

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
                st.error(f"⚠️ Alerte : Vos dépenses dépassent votre XP accumulée ! (Déficit de {xp_restante} XP)")
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
                    score_anneau = f.get(anneau_choisi.lower(), f.get(f"anneau_{anneau_choisi.lower()}", 2))
                    
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
                            liste_deroulante_comp.append(f"{comp} ({categorie.split()})")
                    
                    comp_choisie_brute = st.selectbox("📚 2. Choisir la Compétence Spécifique (D12) :", liste_deroulante_comp, key="sb_action_comp_advanced")
                    
                    score_comp = 0
                    nom_competence_propre = "Aucune"
                    
                    if comp_choisie_brute != "Aucune (0 dé)":
                        nom_competence_propre = comp_choisie_brute.split(" (")[0]
                        cat_parente_brute = comp_choisie_brute.split("(")[1].replace(")", "").lower()
                        
                        score_comp = f.get(nom_competence_propre.lower(), f.get(f"comp_{nom_competence_propre.lower()}", 0))
                        if score_comp == 0:
                            cat_cle = cat_parente_brute[:-1] if cat_parente_brute.endswith("s") else cat_parente_brute
                            score_comp = f.get(cat_cle, f.get(f"comp_{cat_cle}", 0))
                        
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
            
            # Catalogue interne temporaire (évolutif)
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
        # 🏛️ INTERCEPTION DE L'ONGLET : GRAND CATALOGUE DES TECHNIQUES
        # =====================================================================
        if onglet_actif == "🏛️ Grand Catalogue des Techniques":
            st.title("🏛️ Le Grand Catalogue des Techniques d'Émeraude")
            st.info("💡 Parcourez les écoles de l'Empire. En apprenant une technique, elle s'ajoutera instantanément à votre Grimoire Personnel.")
            
            db_globale_tech = CATALOGUE_COMPLET if 'CATALOGUE_COMPLET' in globals() else {}
            db_descriptions = DESCRIPTIONS_LORE if 'DESCRIPTIONS_LORE' in globals() else {}

            # Filtre 1 : Choix de la grande catégorie
            liste_grands_types = ["-- Sélectionner --"] + list(db_globale_tech.keys())
            cat_selectionne = st.selectbox("🔍 1. Choisir la catégorie de Technique :", liste_grands_types, key="sb_grand_cat_dr")
            
            if cat_selectionne != "-- Sélectionner --":
                cle_fiche_cible = cles_techniques.get(f"{cat_selectionne} ") or cles_techniques.get(next((k for k in cles_techniques.keys() if cat_selectionne.split()[0] in k), ""))
                sous_categories_dict = db_globale_tech[cat_selectionne]
                
                # Filtre 2 : Choix de la sous-catégorie (Général, Corps-à-corps, Air, Feu...)
                liste_sous_types = ["-- Sélectionner --"] + list(sous_categories_dict.keys())
                filtre_sous_type = st.selectbox(f"🎯 2. Sous-catégorie ({cat_selectionne}) :", liste_sous_types, key="sb_dr_sub")
                
                if filtre_sous_type != "-- Sélectionner --":
                    rangs_disponibles_dict = sous_categories_dict[filtre_sous_type]
                    
                    # Filtre 3 : Choix du Rang (Rang 1, Rang 2...)
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

        # --- BLOC DE SAUVEGARDE ABSOLUE ET SYSTÉMATIQUE DE TOUS LES ONGLETS ---
        st.markdown("---")
        sauver_fiche(nom_id, f)
        
