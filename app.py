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
                    w_base_md = CATALOGUE_ARMES_AVANCE.get(arme_md_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "comp_requise": "Arts Martiaux (Mêlée)"})
                    bonus_2m_md = 1 if st.session_state["w_md_2mains"] else 0
                    degats_totaux_md = w_base_md["degats"] + arme_md_finale.get("bonus_degats", 0) + bonus_2m_md
                    st.write(f"✋ **Main Droite ({sel_md}) :** Dégâts : `{degats_totaux_md}` | Danger : `{w_base_md['danger'] + arme_md_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_md.get('comp_requise', 'Mêlée')}`")
            else:
                st.caption("✋ **Main Droite :** Vide")

            # Stats Main Gauche
            if sel_mg != "Aucune" and arme_mg_finale:
                if mg_est_grisee:
                    st.caption("🛡️ **Main Gauche :** 😴 *Arme rangée au fourreau (Inutilisable actuellement)*")
                else:
                    w_base_mg = CATALOGUE_ARMES_AVANCE.get(arme_mg_finale.get("modele_racine", "Katana"), {"degats": 3, "danger": 5, "comp_requise": "Arts Martiaux (Mêlée)"})
                    bonus_2m_mg = 1 if st.session_state["w_mg_2mains"] else 0
                    degats_totaux_mg = w_base_mg["degats"] + arme_mg_finale.get("bonus_degats", 0) + bonus_2m_mg
                    st.write(f"🛡️ **Main Gauche ({sel_mg}) :** Dégâts : `{degats_totaux_mg}` | Danger : `{w_base_mg['danger'] + arme_mg_finale.get('bonus_danger', 0)}` | Compétence : `{w_base_mg.get('comp_requise', 'Mêlée')}`")
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
                    st.info(f"🔍 **Analyse de l'objet :** *{obj_analyse['nom']}*\n\n"
                            f"• **Catégorie :** {obj_analyse.get('type_cat')} | Racine : `{obj_analyse.get('modele_racine','Inconnue')}`\n"
                            f"• **Propriétés :** *{obj_analyse.get('proprietes','Aucune')}*")

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
        # 🛒 SECTION DU JOUEUR : BOUTIQUE D'ACHAT & CATALOGUES
        # =====================================================================
        st.markdown("---")
        st.subheader("🛒 Ajouter Objet (Magasin & Sac)")
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
                    st.rerun()

             # =====================================================================
        # 📜 LE GRIMOIRE DES TECHNIQUES IMPÉRIALES (LIEN CATALOGUES)
        # =====================================================================
        st.markdown("---")
        st.subheader("📖 Le Grimoire des Techniques Impériales")
        
        # Liste de correspondance entre vos clés de fiche et vos catalogues importés
        categories_list = [
            ("Katas", "mes_katas", CATALOGUE_KATAS if 'CATALOGUE_KATAS' in globals() else {}),
            ("Kihos", "mes_kihos", CATALOGUE_KIHOS if 'CATALOGUE_KIHOS' in globals() else {}),
            ("Invocations", "mes_invocs", CATALOGUE_INVOCATIONS if 'CATALOGUE_INVOCATIONS' in globals() else {}),
            ("Rituels", "mes_rituels", CATALOGUE_RITUELS if 'CATALOGUE_RITUELS' in globals() else {}),
            ("Shujis", "mes_shujis", CATALOGUE_SHUJIS if 'CATALOGUE_SHUJIS' in globals() else {}),
            ("Mahos", "mes_mahos", CATALOGUE_MAHOS if 'CATALOGUE_MAHOS' in globals() else {}),
            ("Ninjutsus", "mes_ninjutsus", CATALOGUE_NINJUTSUS if 'CATALOGUE_NINJUTSUS' in globals() else {}),
            ("Inversions", "mes_inversions", CATALOGUE_INVERSIONS if 'CATALOGUE_INVERSIONS' in globals() else {})
        ]

        for nom_cat, cle_fiche, cat_ref in categories_list:
            if cle_fiche not in f:
                f[cle_fiche] = []
                
            # Création d'un volet déroulant par catégorie de technique
            with st.expander(f"✨ {nom_cat} Maîtrisés ({len(f[cle_fiche])})"):
                # 1. Affichage des techniques déjà apprises par le joueur
                if f[cle_fiche]:
                    for tech in f[cle_fiche]:
                        col_t_txt, col_t_btn = st.columns([3, 1])
                        col_t_txt.write(f"• **{tech}**")
                        # Bouton de suppression en croix pour oublier la technique
                        if col_t_btn.button("❌", key=f"del_t_{cle_fiche}_{tech}"):
                            f[cle_fiche].remove(tech)
                            sauver_fiche(nom_id, f)
                            st.rerun()
                else:
                    st.caption(f"Aucun {nom_cat[:-1]} connu.")

                # 2. Formulaire pour apprendre une nouvelle technique depuis le catalogue racine
                if cat_ref:
                    # On filtre pour ne pas proposer des techniques que le joueur connaît déjà
                    liste_choix = ["-- Apprendre une technique --"] + [t for t in cat_ref.keys() if t not in f[cle_fiche]]
                    sel_t = st.selectbox(f"Choisir dans le catalogue des {nom_cat} :", liste_choix, key=f"add_select_{cle_fiche}")
                    
                    if sel_t != "-- Apprendre une technique --" and st.button("🧠 Valider l'apprentissage", key=f"btn_add_val_{cle_fiche}"):
                        f[cle_fiche].append(sel_t)
                        sauver_fiche(nom_id, f)
                        st.success(f"🔮 Technique apprise avec succès !")
                        st.rerun()
                else:
                    st.warning(f"⚠️ Le fichier technique.py ne contient pas de catalogue pour {nom_cat}.")

        # --- SAUVEGARDE FINALE DE L'ESPACE DU JOUEUR ---
        st.markdown("---")
        sauver_fiche(nom_id, f)

# =====================================================================
# ⛩️ SECTION ACCUEIL : ÉCRAN PARCHEMIN (SI AUCUNE CONNEXION)
# =====================================================================
else:
    st.info("⛩️ Saisissez votre prénom ci-dessus pour déplier votre parchemin de personnage.")
