import streamlit as st
import json
import os
import time

# 1. IMPORTATION LOGIQUE DES BASES DE DONNÉES DÉPORTÉES
from equipements import CATALOGUE_ARMURES, CATALOGUE_ARMES_AVANCE, CATALOGUE_DIVERS
from techniques import CATALOGUE_COMPLET, DESCRIPTIONS_LORE

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

role = st.sidebar.radio("🔑 Rôle :", ["Visiteur", "Joueur (Ma Fiche)", "Maître du Jeu (Hôte)"])

# ==================== VUE JOUEUR ====================
if role == "Joueur (Ma Fiche)":
    st.header("👤 Votre Feuille Dynamique")
    nom_id = st.text_input("Prénom (Identifiant de session) :").strip()
    
    if nom_id:
        f = charger_fiche(nom_id) or {}
        
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
        
        col_civ4, col_civ5, col_civ6 = st.columns(3)
        ecole = col_civ4.text_input("Nom de l'École :", value=f.get("ecole", ""))
        rang_ecole = col_civ5.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
        roles_actuels = col_civ6.multiselect("Sélectionnez votre ou vos Rôles :", ROLES_LISTE, default=f.get("profil", ["Bushi"]))

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
        
        armure_actuelle_nom = f.get("armure_active", "Armure de Tenue de Cérémonie")
        stats_armure_actuelle = CATALOGUE_ARMURES.get(armure_actuelle_nom, {"res_p": 1, "res_s": 0, "proprietes": "Cérémonielle"})
        st.markdown(f"🛡️ **Équipement de Protection Actif :** *{armure_actuelle_nom}*")
        st.info(f"🔰 **Résistance Physique :** {stats_armure_actuelle['res_p']} | **Résistance Surnaturelle :** {stats_armure_actuelle['res_s']} \n\n*Propriétés : {stats_armure_actuelle['proprietes']}*")

        st.markdown("##### 🩺 États & Blessures Subis")
        col_sante1, col_sante2 = st.columns(2)
        with col_sante1:
            e_blinde = st.checkbox("Saignant 🩸", value=f.get("e_saignant", False), key="chk_saignant")
            e_etourdi = st.checkbox("Étourdi 😵‍💫", value=f.get("e_etourdi", False), key="chk_etourdi")
            e_compromis = st.checkbox("Compromis ⚖️", value=f.get("e_compromis", False), key="chk_compromis")
            e_inconscient = st.checkbox("Inconscient 💤", value=f.get("e_inconscient", False), key="chk_inconscient")
            e_aveugle = st.checkbox("Aveuglé 🙈", value=f.get("e_aveugle", False), key="chk_aveugle")
        with col_sante2:
            b_legere = st.checkbox("Blessure Mineure / Légère", value=f.get("b_legere", False), key="chk_b_legere")
            b_grave = st.checkbox("Blessure Majeure / Grave", value=f.get("b_grave", False), key="chk_b_grave")
            b_mutilante = st.checkbox("Blessure Mutilante / Permanente", value=f.get("b_mutilante", False), key="chk_b_mutilante")

        messages_etats = []
        if e_blinde: messages_etats.append("• **Saignant :** Vous subissez 1 dégât physique à la fin de chacune de vos actions.")
        if e_etourdi: messages_etats.append("• **Étourdi :** Pas d'actions nécessitant une concentration majeure.")
        if e_compromis: messages_etats.append("• **Compromis :** Impossible de garder des dés contenant des symboles de conflit.")
        if e_inconscient: messages_etats.append("• **Inconscient :** Sans défense. Difficulté des attaques contre vous égale à 1.")
        if e_aveugle: messages_etats.append("• **Aveuglé :** Difficulté des tests basés sur la vue augmentée de +2.")
        if messages_etats: st.error("⚠️ **EFFETS DES ÉTATS :**\n" + "\n".join(messages_etats))

        messages_blessures = []
        if b_legere: messages_blessures.append("• **Blessure Légère :** Coût en opportunités augmenté de +1 sur vos actions martiales.")
        if b_grave: messages_blessures.append("• **Blessure Grave :** Difficulté de tous vos tests physiques augmentée de +1.")
        if b_mutilante: messages_blessures.append("• **Blessure Mutilante :** Malus permanent sur l'anneau associé.")
        if messages_blessures: st.warning("🚨 **EFFETS DES BLESSURES :**\n" + "\n".join(messages_blessures))
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

        # Initialisation sécurisée des métriques globales de combat pour le MJ
        arme_active_nom = "Aucune"
        arme_active_degats = 0
        arme_active_danger = 0
        arme_active_portee = "0"
        res_p, res_s = 0, 0
        armure_active = "Aucune"

        with col_arsenal_droite:
            st.markdown("##### 🎯 Équipements Activement Portés")
            
            # 1. Extraction préliminaire sécurisée des objets actuellement équipés
            arme_md_actuelle = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Droite"), None)
            nom_w_md = arme_md_actuelle["nom"] if arme_md_actuelle else "Aucune"
            
            arme_mg_actuelle = next((obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("main_equipee") == "Main Gauche"), None)
            nom_w_mg = arme_mg_actuelle["nom"] if arme_mg_actuelle else "Aucune"

            # Initialisation des états de prise volontaire à 2 mains
            if "w_md_2mains" not in st.session_state: st.session_state["w_md_2mains"] = False
            if "w_mg_2mains" not in st.session_state: st.session_state["w_mg_2mains"] = False

            # --- VÉRIFICATION DES CONTRAINTES DE LA MAIN GAUCHE POUR BLOQUER LA MAIN DROITE ---
            md_bloquee_par_nature = False
            if arme_mg_actuelle:
                stats_nat_mg = CATALOGUE_ARMES_AVANCE.get(arme_mg_actuelle.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"})
                if stats_nat_mg.get("prise_autorisee") == "2 mains":
                    md_bloquee_par_nature = True

            bloque_md = (st.session_state["w_mg_2mains"] or md_bloquee_par_nature) and nom_w_mg != "Aucune"

            # --- CONFIGURATION ET AFFICHAGE MAIN DROITE ---
            if bloque_md:
                st.selectbox("✋ Arme en Main Droite :", ["Grise (Main Gauche tenue à 2 mains 👐)"], disabled=True, key="sel_w_md_disabled")
                sel_md = "Aucune"
                st.session_state["w_md_2mains"] = False
            else:
                liste_choix_md = ["Aucune"] + [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] != nom_w_mg]
                sel_md = st.selectbox("✋ Arme en Main Droite :", liste_choix_md, index=liste_choix_md.index(nom_w_md) if nom_w_md in liste_choix_md else 0, key="sel_w_md_live")
                
                # Gestion de la prise Main Droite
                if sel_md != "Aucune":
                    arme_md_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_md), None)
                    stats_md_temp = CATALOGUE_ARMES_AVANCE.get(arme_md_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if arme_md_temp else {}
                    
                    if stats_md_temp.get("prise_autorisee") == "2 mains":
                        st.session_state["w_md_2mains"] = True
                        st.caption("ℹ️ Cette arme requiert obligatoirement vos deux mains.")
                    else:
                        st.session_state["w_md_2mains"] = st.checkbox("👐 Tenir cette arme à 2 mains (Main Droite)", value=st.session_state["w_md_2mains"], key="chk_2m_md")
                else:
                    st.session_state["w_md_2mains"] = False

            # Application en base pour la Main Droite
            for w in f["inventaire_sac"]:
                if w["type_cat"] == "Arme":
                    if w["nom"] == sel_md:
                        w["main_equipee"] = "Main Droite"
                        w["prise_main"] = "2 mains" if st.session_state["w_md_2mains"] else "1 main"
                    elif w["main_equipee"] == "Main Droite":
                        w["main_equipee"] = "Aucune"

            # Re-calcul immédiat après attribution de la main droite
            arme_md_active = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["main_equipee"] == "Main Droite"), None)
            
            md_bloquante_pour_mg = False
            if arme_md_active:
                stats_nat_md = CATALOGUE_ARMES_AVANCE.get(arme_md_active.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"})
                if stats_nat_md.get("prise_autorisee") == "2 mains":
                    md_bloquante_pour_mg = True

            bloque_mg = (st.session_state["w_md_2mains"] or md_bloquante_pour_mg) and sel_md != "Aucune"

            # --- CONFIGURATION ET AFFICHAGE MAIN GAUCHE (TOUTES ARMES ACCEPTÉES) ---
            if bloque_mg:
                st.selectbox("🛡️ Arme / Équipement en Main Gauche :", ["Grise (Main Droite tenue à 2 mains 👐)"], disabled=True, key="sel_w_mg_disabled")
                sel_mg = "Aucune"
                st.session_state["w_mg_2mains"] = False
            else:
                liste_choix_mg = ["Aucune"] + [w["nom"] for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["nom"] != sel_md]
                sel_mg = st.selectbox("🛡️ Arme / Équipement en Main Gauche :", liste_choix_mg, index=liste_choix_mg.index(nom_w_mg) if nom_w_mg in liste_choix_mg else 0, key="sel_w_mg_live")
                
                # Gestion de la prise Main Gauche
                if sel_mg != "Aucune":
                    arme_mg_temp = next((w for w in f["inventaire_sac"] if w["nom"] == sel_mg), None)
                    stats_mg_temp = CATALOGUE_ARMES_AVANCE.get(arme_mg_temp.get("modele_racine", "Katana"), {"prise_autorisee": "1 main"}) if arme_mg_temp else {}
                    
                    if stats_mg_temp.get("prise_autorisee") == "2 mains":
                        st.session_state["w_mg_2mains"] = True
                        st.caption("ℹ️ Cette arme requiert obligatoirement vos deux mains.")
                    else:
                        st.session_state["w_mg_2mains"] = st.checkbox("👐 Tenir cette arme à 2 mains (Main Gauche)", value=st.session_state["w_mg_2mains"], key="chk_2m_mg")
                else:
                    st.session_state["w_mg_2mains"] = False

            # Application en base pour la Main Gauche
            for w in f["inventaire_sac"]:
                if w["type_cat"] == "Arme":
                    if w["nom"] == sel_mg:
                        w["main_equipee"] = "Main Gauche"
                        w["prise_main"] = "2 mains" if st.session_state["w_mg_2mains"] else "1 main"
                    elif w["main_equipee"] == "Main Gauche":
                        w["main_equipee"] = "Aucune"

            # --- AFFICHAGE DYNAMIQUE DES CARACTÉRISTIQUES ET COMPÉTENCES SOUS LES MENUS ---
            arme_md_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["main_equipee"] == "Main Droite"), None)
            arme_mg_finale = next((w for w in f["inventaire_sac"] if w["type_cat"] == "Arme" and w["main_equipee"] == "Main Gauche"), None)

            if arme_md_finale:
                w_base_md = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "comp_requise": "Arts Martiaux (Mêlée)"})
                bonus_2m_md = 1 if w_md_finale.get("prise_main") == "2 mains" else 0
                st.caption(f"📊 **Stats Main Droite :** Dégâts : `{w_base_md['degats'] + arme_md_finale.get('bonus_degats', 0) + bonus_2m_md}` | Danger : `{w_base_md['danger'] + arme_md_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_md.get('comp_requise', 'Mêlée')}`")

            if arme_mg_finale:
                w_base_mg = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "comp_requise": "Arts Martiaux (Mêlée)"})
                bonus_2m_mg = 1 if w_mg_finale.get("prise_main") == "2 mains" else 0
                st.caption(f"📊 **Stats Main Gauche :** Dégâts : `{w_base_mg['degats'] + arme_mg_finale.get('bonus_degats', 0) + bonus_2m_mg}` | Danger : `{w_base_mg['danger'] + arme_mg_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_mg.get('comp_requise', 'Mêlée')}`")

            # --- SYNCHRONISATION DU TEXTE DE COMPILATION POUR LE MJ ---
            if arme_md_finale and arme_md_finale.get("prise_main") == "2 mains":
                arme_active_nom = arme_md_finale["nom"] + " (À 2 mains 👐)"
                w_base = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                arme_active_degats = w_base["degats"] + arme_md_finale.get("bonus_degats", 0) + 1
                arme_active_danger = w_base["danger"] + arme_md_finale.get("bonus_danger", 0)
                arme_active_portee = w_base["portee"]
            elif arme_mg_finale and arme_mg_finale.get("prise_main") == "2 mains":
                arme_active_nom = arme_mg_finale["nom"] + " (À 2 mains 👐)"
                w_base = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                arme_active_degats = w_base["degats"] + arme_mg_finale.get("bonus_degats", 0) + 1
                arme_active_danger = w_base["danger"] + arme_mg_finale.get("bonus_danger", 0)
                arme_active_portee = w_base["portee"]
            else:
                txt_portes = []
                if arme_md_finale: txt_portes.append(f"MD: {arme_md_finale['nom']}")
                if arme_mg_finale: txt_portes.append(f"MG: {arme_mg_finale['nom']}")
                arme_active_nom = " | ".join(txt_portes) if txt_portes else "Aucune"
                
                if arme_md_finale:
                    w_base = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1"})
                    arme_active_degats = w_base["degats"] + arme_md_finale.get("bonus_degats", 0)
                    arme_active_danger = w_base["danger"] + arme_md_finale.get("bonus_danger", 0)
                    arme_active_portee = w_base["portee"]

            # --- SÉLECTION DE L'ARMURE PORTÉE ---
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

        # --- LE GRAND LABORATOIRE DE RECYCLAGE & ENCHANTEMENT ---
        st.markdown("#### 🧪 Laboratoire d'Altération & Forgeron Évolué")
        st.caption("ℹ️ Note : Sélectionnez un objet déjà possédé pour le transmuter ou modifier ses bonus/propriétés.")
        
        type_alteration = st.radio("Quel type d'équipement du sac voulez-vous transmuter ?", ["Arme", "Armure"], horizontal=True, key="radio_lab_type")
        
        if type_alteration == "Arme":
            armes_dispo_sac = [w for w in f["inventaire_sac"] if w["type_cat"] == "Arme"]
            if not armes_dispo_sac:
                st.warning("❌ Vous ne possédez aucune arme dans votre sac à dos à modifier.")
            else:
                arme_cible_nom = st.selectbox("Choisir l'arme de votre sac à altérer :", [w["nom"] for w in armes_dispo_sac], key="lab_w_target")
                arme_cible_obj = next((w for w in armes_dispo_sac if w["nom"] == arme_cible_nom))
                
                c_l1, c_l2 = st.columns(2)
                b_deg = c_l1.number_input("Nouveaux Dégâts Bonus :", value=int(arme_cible_obj.get("bonus_degats", 0)), key="lab_w_deg")
                b_dang = c_l2.number_input("Nouvelle Dangerosité Bonus :", value=int(arme_cible_obj.get("bonus_danger", 0)), key="lab_w_dang")
                nom_enchante_w = st.text_input("Donner un nom personnalisé (Ex: Katana de Feu) :", value=arme_cible_obj["nom"], key="lab_w_custom_name")
                props_w_lab = st.text_input("Propriétés ajoutées / Brûlures / Désenchantement :", value=arme_cible_obj.get("proprietes", ""), key="lab_w_props")
                
                if st.button("🔨 Forger / Améliorer et Remplacer l'arme", key="btn_forge_w"):
                    arme_cible_obj["nom"] = nom_enchante_w.strip() if nom_enchante_w.strip() else arme_cible_obj["nom"]
                    arme_cible_obj["bonus_degats"] = b_deg
                    arme_cible_obj["bonus_danger"] = b_dang
                    arme_cible_obj["proprietes"] = props_w_lab
                    arme_cible_obj["details"] = f"Équipement transmuté au laboratoire. Racine historique : {arme_cible_obj.get('modele_racine','Katana')}"
                    
                    sauver_fiche(nom_id, f)
                    st.success(f"✨ L'ancien équipement a été recyclé ! `{nom_enchante_w}` a pris sa place.")
                    st.rerun()

        elif type_alteration == "Armure":
            armures_dispo_sac = [a for a in f["inventaire_sac"] if a["type_cat"] == "Armure"]
            if not armures_dispo_sac:
                st.warning("❌ Vous ne possédez aucune armure dans votre sac à dos à modifier.")
            else:
                armure_cible_nom = st.selectbox("Choisir l'armure de votre sac à altérer :", [a["nom"] for a in armures_dispo_sac], key="lab_a_target")
                armure_cible_obj = next((a for a in armures_dispo_sac if a["nom"] == armure_cible_nom))
                
                c_la1, c_la2 = st.columns(2)
                b_resp = c_la1.number_input("Nouvelle Résistance Physique supplémentaire :", value=int(armure_cible_obj.get("bonus_res_p", 0)), key="lab_a_resp")
                b_ress = c_la2.number_input("Nouvelle Résistance Surnaturelle supplémentaire :", value=int(armure_cible_obj.get("bonus_res_s", 0)), key="lab_a_ress")
                nom_enchante_a = st.text_input("Nom de l'armure personnalisé :", value=armure_cible_obj["nom"], key="lab_a_custom_name")
                props_a_lab = st.text_input("Propriétés ajoutées / Résistances :", value=armure_cible_obj.get("proprietes", ""), key="lab_a_props")
                
                if st.button("🛡️ Forger / Améliorer et Remplacer l'armure", key="btn_forge_a"):
                    armure_cible_obj["nom"] = nom_enchante_a.strip() if nom_enchante_a.strip() else armure_cible_obj["nom"]
                    armure_cible_obj["bonus_res_p"] = b_resp
                    armure_cible_obj["bonus_res_s"] = b_ress
                    armure_cible_obj["proprietes"] = props_a_lab
                    
                    sauver_fiche(nom_id, f)
                    st.success(f"✨ Armure transmutée avec succès en `{nom_enchante_a}` !")
                    st.rerun()
        # --- LE GRAND INVENTAIRE DU SAC À DOS INTERACTIF ---
        st.markdown("### 🎒 Inventaire Interactif du Sac à Dos")
        if not f["inventaire_sac"]:
            st.info("Votre sac à dos est totalement vide.")
        else:
            for item in f["inventaire_sac"]:
                col_item_nom, col_item_eq, col_item_oeil, col_item_croix = st.columns(4)
                
                # Indicateur d'emplacement visuel à l'écran
                statut_port_arme = "📦 [Sac]"
                if item["type_cat"] == "Arme":
                    if item.get("main_equipee") in ["Main Droite", "Main Gauche"]:
                        statut_port_arme = f"🎯 [{item['main_equipee']}]"
                elif item["type_cat"] == "Armure" and item.get("equipe"):
                    statut_port_arme = "🎯 [Portée]"
                    
                col_item_nom.write(f"**{statut_port_arme} {item['nom']}**")
                col_item_eq.write(f"*{item['type_cat']}* — `{item.get('prise_main', '1 main')}`")

                # Bouton Œil 👁️ pour afficher l'analyse détaillée
                if col_item_oeil.button("👁️", key=f"oeil_obj_{item['id_obj']}"):
                    f["objet_regarde_id"] = item["id_obj"]
                
                # Bouton Croix ❌ pour supprimer définitivement du sac
                if col_item_croix.button("❌", key=f"del_obj_{item['id_obj']}"):
                    f["inventaire_sac"].remove(item)
                    sauver_fiche(nom_id, f)
                    st.success(f"{item['nom']} jeté du sac.")
                    st.rerun()
            
               # Fenêtre d'analyse approfondie (Oeil cliqué)
            if f.get("objet_regarde_id"):
                obj_analyse = next((obj for obj in f["inventaire_sac"] if obj["id_obj"] == f["objet_regarde_id"]), None)
                if obj_analyse:
                    # Analyse dynamique si c'est une arme
                    if obj_analyse["type_cat"] == "Arme":
                        w_nat = CATALOGUE_ARMES_AVANCE.get(obj_analyse.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "portee": "1", "comp_requise": "Mêlée", "type_w": "Inconnu", "proprietes": "Aucune"})
                        st.info(f"🔍 **Analyse Mystique de l'Arme :** *{obj_analyse['nom']}*\n\n"
                                f"• **Type d'Arme :** `{w_nat.get('type_w', 'Arme de poing')}` | Modèle d'origine : `{obj_analyse.get('modele_racine')}`\n"
                                f"• **Dégâts Naturels :** `{w_nat['degats']}` | **Dégâts Bonus Forgeron :** `+{obj_analyse.get('bonus_degats', 0)}` \n"
                                f"• **Dangerosité Naturelle :** `{w_nat['danger']}` | **Dangerosité Bonus :** `+{obj_analyse.get('bonus_danger', 0)}` \n"
                                f"• **Portée de Combat :** `{w_nat['portee']}` \n"
                                f"• **Art Martial requis :** `{w_nat.get('comp_requise', 'Arts Martiaux (Mêlée)')}` \n"
                                f"• **Propriétés & Nouveaux Enchantements :** *{obj_analyse.get('proprietes', w_nat['proprietes'])}*")
                    
                    # Analyse dynamique si c'est une armure
                    elif obj_analyse["type_cat"] == "Armure":
                        a_nat = CATALOGUE_ARMURES.get(obj_analyse.get("modele_racine"), {"res_p": 1, "res_s": 0, "proprietes": "Aucune"})
                        st.info(f"🔍 **Analyse Mystique de l'Armure :** *{obj_analyse['nom']}*\n\n"
                                f"• **Modèle de base :** `{obj_analyse.get('modele_racine')}` \n"
                                f"• **Résistance Physique :** `{a_nat['res_p']} (+{obj_analyse.get('bonus_res_p', 0)} Magie/Acier)` \n"
                                f"• **Résistance Surnaturelle :** `{a_nat['res_s']} (+{obj_analyse.get('bonus_res_s', 0)} Éléments)` \n"
                                f"• **Propriétés & Attributs :** *{obj_analyse.get('proprietes', a_nat['proprietes'])}*")
                    
                    # Analyse si c'est un objet divers
                    else:
                        st.info(f"🔍 **Analyse approfondie de l'Objet Divers :** *{obj_analyse['nom']}*\n\n"
                                f"• **Catégorie d'inventaire :** `{obj_analyse['type_cat']}` \n"
                                f"• **Notes & Effets en jeu :** {obj_analyse.get('proprietes', 'Aucun effet magique actif.')}")

        # --- PANNEAU DE CONSULTATION INTERACTIF DES CATALOGUES ---
        st.markdown("---")
        with st.expander("📖 Consulter les Grands Catalogues impériaux (Armes, Armures, Divers)"):
            w_tab, a_tab, d_tab = st.tabs(["🗡️ Catalogue des Armes", "👘 Catalogue des Armures", "📦 Catalogue des Objets Divers"])
            
            with w_tab:
                st.markdown("##### Base de données officielle des Armes")
                for nom_w, stats_w in CATALOGUE_ARMES_AVANCE.items():
                    st.write(f"• **{nom_w}** | Dégâts : `{stats_w['degats']}` | Danger : `{stats_w['danger']}` | Portée : `{stats_w['portee']}` | Rareté : `{stats_w['rareté']}`")
                    st.caption(f"  *Propriétés : {stats_w['proprietes']} | Prise : {stats_w['prise_autorisee']}*")
            
            with a_tab:
                st.markdown("##### Base de données officielle des Armures")
                for nom_a, stats_a in CATALOGUE_ARMURES.items():
                    st.write(f"• **{nom_a}** | Résistance Physique : `{stats_a['res_p']}` | Résistance Surnaturelle : `{stats_a['res_s']}`")
                    st.caption(f"  *Propriétés : {stats_a['proprietes']}*")
            
            with d_tab:
                st.markdown("##### Base de données officielle des Objets Divers")
                if 'CATALOGUE_DIVERS' in globals() and CATALOGUE_DIVERS:
                    for nom_d, stats_d in CATALOGUE_DIVERS.items():
                        st.write(f"• **{nom_d}** | Catégorie : `{stats_d['type']}` | Rareté : `{stats_d['rarete']}`")
                        st.info(f"  🎯 **Effet en jeu :** {stats_d.get('effet', 'Aucun effet')}")

        # --- ZONE D'ACHAT UNIFIÉE (MAGASIN COMPATIBLE SÉCURISÉ) ---
        st.markdown("---")
        st.subheader("🛒 Ajouter Objet (Magasin & Sac)")
        col_cat1, col_cat2, col_cat3 = st.columns(3)
        
        with col_cat1:
            st.markdown("**1. Catégorie : Armes**")
            w_achat = st.selectbox("Sélectionner une arme du catalogue :", list(CATALOGUE_ARMES_AVANCE.keys()), key="buy_w_sel")
            if st.button("➕ Ajouter l'Arme", key="btn_buy_w"):
                f["inventaire_sac"].append({
                    "id_obj": int(time.time()), "nom": f"{w_achat} standard", "modele_racine": w_achat, "type_cat": "Arme", 
                    "details": "Achetée au catalogue d'école standard.", "main_equipee": "Aucune", "prise_main": "1 main", "bonus_degats": 0, "bonus_danger": 0, "proprietes": CATALOGUE_ARMES_AVANCE[w_achat]["proprietes"]
                })
                sauver_fiche(nom_id, f)
                st.success(f"✨ {w_achat} a été glissé dans votre sac !")
                st.rerun()
                
        with col_cat2:
            st.markdown("**2. Catégorie : Armures**")
            a_achat = st.selectbox("Sélectionner une armure du catalogue :", list(CATALOGUE_ARMURES.keys()), key="buy_a_sel")
            if st.button("➕ Ajouter l'Armure", key="btn_buy_a"):
                f["inventaire_sac"].append({
                    "id_obj": int(time.time()), "nom": f"{a_achat} standard", "modele_racine": a_achat, "type_cat": "Armure", 
                    "details": "Achetée au catalogue de protection standard.", "equipe": False, "bonus_res_p": 0, "bonus_res_s": 0, "proprietes": CATALOGUE_ARMURES[a_achat]["proprietes"]
                })
                sauver_fiche(nom_id, f)
                st.success(f"✨ {a_achat} a été suspendue dans votre sac !")
                st.rerun()

        with col_cat3:
            st.markdown("**3. Catégorie : Objets Divers**")
            liste_divers = list(CATALOGUE_DIVERS.keys()) if 'CATALOGUE_DIVERS' in globals() else []
            if liste_divers:
                d_achat = st.selectbox("Sélectionner un objet utilitaire :", liste_divers, key="boutique_divers_unique_sel")
                d_stats = CATALOGUE_DIVERS[d_achat]
                if st.button("➕ Ajouter l'Objet Divers", key="btn_buy_d_sac"):
                    f["inventaire_sac"].append({
                        "id_obj": int(time.time()), "nom": d_achat, "type_cat": "Divers", 
                        "details": f"Type : {d_stats['type']}. Niveau de Rareté : {d_stats['rarete']}.", 
                        "proprietes": d_stats["effet"], "equipe": False
                    })
                    sauver_fiche(nom_id, f)
                    st.success(f"✨ {d_achat} glissé dans le sac !")
                    st.rerun()
        
        st.subheader("📜 Gestion des techniques")
        for cle_g in ["mes_katas", "mes_kihos", "mes_invocs", "mes_rituels", "mes_shujis", "mes_mahos", "mes_ninjutsus", "mes_inversions"]:
            if cle_g not in f: f[cle_g] = []

        grimoire_actif_total = f.get("mes_katas", []) + f.get("mes_kihos", []) + f.get("mes_invocs", []) + f.get("mes_rituels", []) + f.get("mes_shujis", []) + f.get("mes_mahos", []) + f.get("mes_ninjutsus", []) + f.get("mes_inversions", [])
        col_catalogue, col_grimoire_actif = st.columns(2)

        with col_catalogue:
            st.markdown("### 📂 Choix des Catalogues")
            sh_grimoire = st.checkbox("👁️ Autoriser le MJ à voir mon Grimoire", value=f.get("sh_grimoire", True))
            c_kat = st.checkbox("🥋 Katas", value=f.get("ch_kat", False))
            c_kih = st.checkbox("🧘 Kíhos", value=f.get("ch_kih", False))
            c_inv = st.checkbox("🔥 Invocations", value=f.get("ch_inv", False))
            c_rit = st.checkbox("📿 Rituels", value=f.get("ch_rit", False))
            c_shu = st.checkbox("🗣️ Shujis", value=f.get("ch_shu", False))
            c_mah = st.checkbox("🩸 Maho", value=f.get("ch_mah", False))
            c_nin = st.checkbox("🥷 Ninjutsu", value=f.get("ch_nin", False))
            c_invs = st.checkbox("🔮 Inversions", value=f.get("ch_invs", False))

            mapping_categories = [
                (c_kat, "Katas", "mes_katas"), (c_kih, "Kíhos", "mes_kihos"), 
                (c_inv, "Invocations", "mes_invocs"), (c_rit, "Rituels", "mes_rituels"), 
                (c_shu, "Shujis", "mes_shujis"), (c_mah, "Mahos", "mes_mahos"), 
                (c_nin, "Ninjutsus", "mes_ninjutsus"), (c_invs, "Inversions", "mes_inversions")
            ]
            
            for coche, nom_cat, cle_sauvegardee in mapping_categories:
                if coche:
                    st.markdown(f"#### 📂 Filtres : {nom_cat}")
                    sub_options = list(CATALOGUE_COMPLET.get(nom_cat, {}).keys())
                    sub_sel = st.selectbox(f"Sous-catégorie ({nom_cat}) :", sub_options, key=f"sub_{nom_cat}")
                    rangs_options = list(CATALOGUE_COMPLET.get(nom_cat, {}).get(sub_sel, {}).keys())
                    rang_sel = st.selectbox(f"Niveau ({nom_cat}) :", rangs_options, key=f"rng_{nom_cat}")
                    techs_disponibles = CATALOGUE_COMPLET.get(nom_cat, {}).get(sub_sel, {}).get(rang_sel, [])
                    
                    for t in techs_disponibles:
                        if t in f.get(cle_sauvegardee, []):
                            st.caption(f"🔹 {t} — [Appris]")
                        else:
                            c_txt, c_btn = st.columns(2)
                            c_txt.write(f"✨ **{t}**")
                            if c_btn.button("➕ Inscrire", key=f"add_{nom_cat}_{t}"):
                                f[cle_sauvegardee].append(t)
                                sauver_fiche(nom_id, f)
                                st.rerun()

        with col_grimoire_actif:
            st.markdown("### 📖 Grimoire des techniques actives")
            if grimoire_actif_total:
                cats_possedees = [n for c, n, k in mapping_categories if f.get(k)]
                if cats_possedees:
                    g_cat = st.selectbox("Filtrer par Type :", sorted(list(set(cats_possedees))), key="g_cat_filter")
                    cle_g_map = {"Katas": "mes_katas", "Kíhos": "mes_kihos", "Invocations": "mes_invocs", "Rituels": "mes_rituels", "Shujis": "mes_shujis", "Mahos": "mes_mahos", "Ninjutsus": "mes_ninjutsus", "Inversions": "mes_inversions"}[g_cat]
                    
                    st.write(f"📂 Vos parchemins enregistrés en **{g_cat}** :")
                    liste_specifique = f.get(cle_g_map, [])
                    
                    for tech_apprise in liste_specifique:
                        c_t_nom, c_t_oeil, c_t_del = st.columns(3)
                        est_active = f.get("tech_active_cliquee") == tech_apprise
                        label_click = f"🎯 {tech_apprise} (Prête)" if est_active else f"📜 {tech_apprise}"
                        
                        if c_t_nom.button(label_click, key=f"click_active_{tech_apprise}"):
                            f["tech_active_cliquee"] = tech_apprise
                            sauver_fiche(nom_id, f)
                            st.rerun()
                        if c_t_oeil.button("👁️", key=f"oeil_details_{tech_apprise}"):
                            afficher_details_technique(tech_apprise)
                        if c_t_del.button("❌", key=f"del_g_{tech_apprise}"):
                            if tech_apprise == f.get("tech_active_cliquee"): 
                                f["tech_active_cliquee"] = "Aucune technique active"
                            f[cle_g_map].remove(tech_apprise)
                            sauver_fiche(nom_id, f)
                            st.rerun()
            else:
                st.info("Grimoire vide.")
        st.markdown("---")
        st.subheader("📢 Poser une Question au MJ")
        c_a1, c_a2, c_a3 = st.columns(3)
        comp_c = c_a1.text_input("Compétence :")
        elem_c = c_a2.selectbox("Élément :", ["Aucun", "Air 💨", "Terre 🏔️", "Feu 🔥", "Eau 💧", "Vide 🌌"])
        tech_choisie_automatique = f.get("tech_active_cliquee", "Aucune technique active")
        c_a3.markdown(f"🎯 **Technique préparée :** `{tech_choisie_automatique}`")
        desc_a = st.text_area("Votre Message / Intention :")
        
        if st.button("⚡ Soumettre la demande"):
            if desc_a and nom_perso:
                actions = []
                if os.path.exists(ACTIONS_FILE):
                    try:
                        with open(ACTIONS_FILE, "r", encoding="utf-8") as file: actions = json.load(file)
                    except: actions = []
                actions.append({"id": len(actions) + 1, "joueur": nom_id, "perso": nom_perso, "competence": comp_c if comp_c else "Texte pur", "element": elem_c, "technique": tech_choisie_automatique, "description": desc_a, "anneaux": {"air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide}, "statut": "En attente", "description_mj": ""})
                with open(ACTIONS_FILE, "w", encoding="utf-8") as file: json.dump(actions, file, indent=4, ensure_ascii=False)
                st.success("Action envoyée au MJ !")

        # --- SÉCURISATION DES VALEURS PAR DÉFAUT AVANT SAUVEGARDE ---
        if 'res_p' not in locals(): res_p = 1
        if 'res_s' not in locals(): res_s = 0
        if 'arme_active_nom' not in locals(): arme_active_nom = "Aucune"
        if 'arme_active_degats' not in locals(): arme_active_degats = 3
        if 'arme_active_danger' not in locals(): arme_active_danger = 5
        if 'arme_active_portee' not in locals(): arme_active_portee = "1"
        if 'armure_active' not in locals(): armure_active = "Aucune"
        if 'armes_equipees' not in locals(): armes_equipees = []

        sauver_fiche(nom_id, maj)
    else:
        st.info("⛩️ Saisissez votre prénom ci-dessus pour déplier votre parchemin de personnage.")

# ==================== VUE MJ ====================
elif role == "Maître du Jeu (Hôte)":
    st.header("👁️ Panneau Tactique de l'Hôte")
    if st.button("🔄 ACTUALISER LA TABLE"): st.rerun()

    fichiers = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    if not fichiers:
        st.info("Aucun samouraï n'a partagé de données.")
    else:
        st.subheader("📋 Informations Autorisées par les Joueurs")
        for f_name in fichiers:
            chemin_fichier = os.path.join(DB_DIR, f_name)
            with open(chemin_fichier, "r", encoding="utf-8") as file: p = json.load(file)
            nom_j = f_name.replace('.json', '').capitalize()
            
            col_head1, col_head2 = st.columns(2)
            col_head1.markdown(f"### 🏯 Fiche de {nom_j}")
            if col_head2.button(f"❌ Supprimer {nom_j}", key=f"del_{nom_j}"):
                os.remove(chemin_fichier)
                st.warning("Fiche détruite."); st.rerun()
            
            av, tv, fv, ev = p.get('air', 1), p.get('terre', 1), p.get('feu', 1), p.get('eau', 1)
            em, sm = (tv + fv) * 2, (tv + ev) * 2
            ep, sp = em - p.get('end_act', em), sm - p.get('sf_act', sm)
            
            roles_bruts = p.get('profil', ['Bushi'])
            roles_txt = ", ".join(roles_bruts) if isinstance(roles_bruts, list) else roles_bruts
            titre_cadre = f"💮 {nom_j} : {p.get('famille','Inconnu')} {p.get('perso','Inconnu')} (Clan {p.get('clan','Inconnu')}) — Rang {p.get('rang_ecole',1)} [{roles_txt}] | Posture : {p.get('posture','Air')}"
            
            with st.expander(titre_cadre, expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**🌀 Éléments & Gravités**")
                    if p.get("sh_anneaux", True):
                        st.write(f"💨 A: {av} (Blessure: {p.get('score_b_air',0)}) | 🏔️ T: {tv} (Blessure: {p.get('score_b_terre',0)})")
                        st.write(f"🔥 F: {fv} (Blessure: {p.get('score_b_feu',0)}) | 💧 E: {ev} (Blessure: {p.get('score_b_eau',0)})")
                        st.write(f"🌌 Vide: {p.get('vide',1)} (Actuel: **{p.get('p_vide',0)}** | Blessure: {p.get('score_b_vide',0)})")
                    else: st.caption("🔒 Masqué")
                with col2:
                    st.markdown("**🩸 Santé & Seuils**")
                    if p.get("sh_vitalite", True):
                        st.write(f"❤️ Endurance : **{p.get('end_act',em)} / {em}**")
                        if ep > 0: st.error(f"-{ep} PV")
                        st.write(f"🧠 Sang-froid : **{p.get('sf_act',sm)} / {sm}**")
                        if sp > 0: st.warning(f"Stress : -{sp}")
                    else: st.caption("🔒 Masqué")
                with col3:
                    st.markdown("**⚖️ Profil Social**")
                    if p.get("sh_social", True): st.write(f"🎖️ H: {p.get('hon',50)} | ⭐ G: {p.get('glo',50)} | 📜 S: {p.get('sta',50)}")
                    else: st.caption("🔒 Masqué")
                with col4:
                    st.markdown("**⚔️ Arsenal Équipé**")
                    if p.get("sh_equipement", True):
                        st.write(f"🗡️ Arme : **{p.get('arme_active','Aucune')}** ({'2 mains ⚔️' if p.get('deux_mains',False) else '1 main'})")
                        st.write(f"💥 Dégâts: {p.get('w_deg','3')} | Danger: **{p.get('w_dang',5)}** | 📏 Portée: {p.get('w_por','1')}")
                        st.write(f"👘 Armure: {p.get('armure_active','Aucune')} (P: {p.get('res_p',1)}/S: {p.get('res_s',0)})")
                    else: st.caption("🔒 Masqué")
                
                if p.get("sh_grimoire", True):
                    st.markdown("🎯 **Technique activement préparée :**")
                    st.info(f"`{p.get('tech_active_cliquee', 'Aucune')}`")

                comp_visibles = []
                dic_noms = {"c_est": "Esthétique", "c_com": "Composition", "c_sty": "Stylisme", "c_forg": "Forge 🔨", "c_for": "Forme", "c_cac": "Corps-à-corps", "c_dis": "Distance", "c_chu": "Corps Humain", "c_med": "Méditation", "c_tac": "Tactique", "c_cul": "Culture", "c_gou": "Gouvernement", "c_mdc": "Médecine", "c_sen": "Sentiment", "c_the": "Théologie", "c_cmd": "Commandement", "c_crt": "Courtoisie", "c_jeu": "Jeu", "c_org": "Organisation 📋", "c_cmr": "Commerce", "c_tra": "Travail Manuel", "c_nav": "Navigation", "c_mag": "Magouille", "c_sur": "Survie"}
                for k_code, n_aff in dic_noms.items():
                    if p.get(k_code, 0) > 0: comp_visibles.append(f"{n_aff}: **{p[k_code]}**")
                if comp_visibles: st.caption(f"📊 **Compétences (Rang ≥ 1) :** " + " | ".join(comp_visibles))

        st.markdown("---")
        st.subheader("🔔 Boîte de réception des Actions Soumises")
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as file: actions = json.load(file)
            except: actions = []
            en_attente = [a for a in actions if a["statut"] == "En attente"]
            if not en_attente: st.info("Aucune action en attente.")
            else:
                for act in en_attente:
                    st.markdown("---")
                    cola, colb = st.columns(2)
                    with cola:
                        st.warning(f"⚔️ **{act['joueur']}** ({act['perso']}) veut agir !")
                        st.write(f"🔹 **Jet :** Compétence **[{act['competence']}]** + Élément **[{act['element']}]**")
                        st.write(f"🎯 **Technique employée :** `{act.get('technique', 'Aucune')}`")
                        aj = act.get("anneaux", {})
                        st.caption(f"📈 *Anneaux :* Air: {aj.get('air',1)} | Terre: {aj.get('terre',1)} | Feu: {aj.get('feu',1)} | Eau: {aj.get('eau',1)}")
                        st.info(f"💬 **Message / Intention :** {act['description']}")
                    with colb:
                        commentaire_mj = st.text_input("Réponse ou contrainte du MJ :", key=f"txt_{act['id']}")
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("✅ Autoriser", key=f"val_{act['id']}"):
                            for a in actions:
                                if a["id"] == act["id"]: 
                                    a["statut"] = "Validé"
                                    a["description_mj"] = commentaire_mj if commentaire_mj else "Approuvé."
                            with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                                json.dump(actions, file, indent=4, ensure_ascii=False)
                            st.success("Validé !")
                            st.rerun()
                            
                        if c_btn2.button("⛔ Refuser", key=f"ref_{act['id']}"):
                            for a in actions:
                                if a["id"] == act["id"]: 
                                    a["statut"] = "Refusé"
                                    a["description_mj"] = commentaire_mj if commentaire_mj else "Refusé."
                            with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                                json.dump(actions, file, indent=4, ensure_ascii=False)
                            st.error("Refusé !")
                            st.rerun()
        else: 
            st.info("Aucune notification reçue.")
else: 
    st.info("👈 Veuillez sélectionner votre accès dans le menu latéral gauche.")
