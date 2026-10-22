import streamlit as st
import json
import os
import time

# 1. IMPORTATION LOGIQUE DES BASES DE DONNÉES DÉPORTÉES
from equipements import CATALOGUE_ARMURES, CATALOGUE_ARMES_AVANCE
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
        
        # --- MINUTEUR JOUEUR (RÉCEPTION DES REFUS / VALIDATIONS MJ EN DIRECT) ---
        st.components.v1.html("""
            <script>
                setTimeout(function() {
                    window.parent.postMessage({type: 'streamlit:render'}, '*');
                }, 3000);
            </script>
        """, height=0, width=0)

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
                {"id_obj": 1, "nom": "Katana", "type_cat": "Arme", "details": "Modèle standard de base.", "equipe": True, "bonus_degats": 0, "bonus_danger": 0, "prise": "2 mains", "proprietes": "Acérée, Cérémoniale"},
                {"id_obj": 2, "nom": "Armure de Tenue de Cérémonie", "type_cat": "Armure", "details": "Modèle standard de base.", "equipe": True, "res_p": 1, "res_s": 0, "proprietes": "Cérémonielle, Magnifique"}
            ]

        # --- AFFICHEUR ARSENAL ACTIF (SCINDÉ GAUCHE ET DROITE) ---
        st.markdown("### ⚔️ Votre Équipement Tactique")
        col_arsenal_gauche, col_arsenal_droite = st.columns(2)
        
        with col_arsenal_gauche:
            st.markdown("##### 🎒 Objets en votre possession dans le sac")
            liste_armes_sac = [obj["nom"] for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme"]
            liste_armures_sac = [obj["nom"] for obj in f["inventaire_sac"] if obj["type_cat"] == "Armure"]
            st.write(f"• **Armes possédées :** {', '.join(liste_armes_sac) if liste_armes_sac else 'Aucune'}")
            st.write(f"• **Armures possédées :** {', '.join(liste_armures_sac) if liste_armures_sac else 'Aucune'}")

        with col_arsenal_droite:
            st.markdown("##### 🎯 Équipements Activement Portés")
            # Extraction des objets équipés
            armes_equipees = [obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Arme" and obj.get("equipe", False)]
            armures_equipees = [obj for obj in f["inventaire_sac"] if obj["type_cat"] == "Armure" and obj.get("equipe", False)]
            
            # Choix de l'arme principale active
            if armes_equipees:
                choix_w_active = st.selectbox("Sélectionner l'Arme en Main :", [w["nom"] for w in armes_equipees], key="sel_w_active_main")
                arme_portee_obj = next((w for w in armes_equipees if w["nom"] == choix_w_active), armes_equipees[0])
                w_base_stats = CATALOGUE_ARMES_AVANCE.get(arme_portee_obj["nom"].split(" (")[0], {"degats": 3, "danger": 5, "portee": "1"})
                
                # Prise en compte des altérations du laboratoire
                arme_active_nom = arme_portee_obj["nom"]
                arme_active_degats = w_base_stats["degats"] + arme_portee_obj.get("bonus_degats", 0)
                arme_active_danger = w_base_stats["danger"] + arme_portee_obj.get("bonus_danger", 0)
                arme_active_portee = w_base_stats["portee"]
                
                st.info(f"🗡️ **Arme Équipée :** {arme_active_nom} ({arme_portee_obj.get('prise', '1 main')}) \n💥 Dégâts : {arme_active_degats} | Danger : {arme_active_danger} | 📏 Portée : {arme_active_portee}")
            else:
                arme_active_nom, arme_active_degats, arme_active_danger, arme_active_portee = "Aucune", 0, 0, "0"
                st.caption("❌ Aucune arme équipée.")

            # Choix de l'armure active
            if armures_equipees:
                choix_a_active = st.selectbox("Sélectionner l'Armure Portée :", [a["nom"] for a in armures_equipees], key="sel_a_active_corps")
                armure_portee_obj = next((a for a in armures_equipees if a["nom"] == choix_a_active), armures_equipees[0])
                a_base_stats = CATALOGUE_ARMURES.get(armure_portee_obj["nom"].split(" (")[0], {"res_p": 1, "res_s": 0})
                
                armure_active = armure_portee_obj["nom"]
                res_p = a_base_stats["res_p"] + armure_portee_obj.get("bonus_res_p", 0)
                res_s = a_base_stats["res_s"] + armure_portee_obj.get("bonus_res_s", 0)
                
                st.info(f"👘 **Armure Portée :** {armure_active} \n🔰 Résistance Physique : {res_p} | Surnaturelle : {res_s}")
            else:
                armure_active, res_p, res_s = "Aucune", 0, 0
                st.caption("❌ Aucune armure portée.")

        # --- LE GRAND LABORATOIRE DE CRÉATION & FORGERON ---
        st.markdown("#### 🧪 Laboratoire d'Altération & Forgeron")
        type_alteration = st.radio("Quel type d'objet voulez-vous forger / altérer ?", ["Arme", "Armure"], horizontal=True)
        
        if type_alteration == "Arme":
            w_lab_base = st.selectbox("Choisir un modèle d'arme de base :", list(CATALOGUE_ARMES_AVANCE.keys()), key="w_lab_sel")
            w_stats = CATALOGUE_ARMES_AVANCE[w_lab_base]
            
            c_l1, c_l2 = st.columns(2)
            b_deg = c_l1.number_input("Dégâts bonus ou d'altération :", value=0, key="lab_w_deg")
            b_dang = c_l2.number_input("Dangerosité bonus ou d'altération :", value=0, key="lab_w_dang")
            nom_enchante_w = st.text_input("Nom personnalisé (Ex: Sabre Maudit de Hida) :", value="", key="lab_w_custom_name")
            prise_w_lab = st.radio("Prise configurée :", ["1 main", "2 mains"], key="lab_w_prise")
            props_w_lab = st.text_input("Propriétés ajoutées / Enchantement :", value="", key="lab_w_props")
            
            if st.button("🔨 Forger / Améliorer l'Arme", key="btn_forge_w"):
                final_name = nom_enchante_w.strip() if nom_enchante_w.strip() else f"{w_lab_base} Artisanal"
                nouvel_obj = {
                    "id_obj": int(time.time()), "nom": final_name, "type_cat": "Arme", 
                    "details": f"Arme forgée. Modèle de base : {w_lab_base}.", "equipe": False,
                    "bonus_degats": b_deg, "bonus_danger": b_dang, "prise": prise_w_lab, "proprietes": props_w_lab if props_w_lab else w_stats["proprietes"]
                }
                f["inventaire_sac"].append(nouvel_obj)
                st.success(f"✨ {final_name} a été ajouté à votre Inventaire Sac à dos !")
                st.rerun()

        elif type_alteration == "Armure":
            a_lab_base = st.selectbox("Choisir un modèle d'armure de base :", list(CATALOGUE_ARMURES.keys()), key="a_lab_sel")
            a_stats = CATALOGUE_ARMURES[a_lab_base]
            
            c_la1, c_la2 = st.columns(2)
            b_resp = c_la1.number_input("Résistance Physique supplémentaire :", value=0, key="lab_a_resp")
            b_ress = c_la2.number_input("Résistance Surnaturelle supplémentaire :", value=0, key="lab_a_ress")
            nom_enchante_a = st.text_input("Nom personnalisé (Ex: Mailles Sacrées d'Asahina) :", value="", key="lab_a_custom_name")
            props_a_lab = st.text_input("Propriétés ajoutées / Enchantement :", value="", key="lab_a_props")
            
            if st.button("🛡️ Forger / Améliorer l'Armure", key="btn_forge_a"):
                final_name = nom_enchante_a.strip() if nom_enchante_a.strip() else f"{a_lab_base} Artisanale"
                nouvel_obj = {
                    "id_obj": int(time.time()), "nom": final_name, "type_cat": "Armure", 
                    "details": f"Armure façonnée. Modèle de base : {a_lab_base}.", "equipe": False,
                    "bonus_res_p": b_resp, "bonus_res_s": b_ress, "proprietes": props_a_lab if props_a_lab else a_stats["proprietes"]
                }
                f["inventaire_sac"].append(nouvel_obj)
                st.success(f"✨ {final_name} a été ajoutée à votre Inventaire Sac à dos !")
                st.rerun()

        # --- LE GRAND INVENTAIRE DU SAC À DOS INTERACTIF ---
        st.markdown("### 🎒 Inventaire Interactif du Sac à Dos")
        if not f["inventaire_sac"]:
            st.info("Votre sac à dos est totalement vide.")
        else:
            for item in f["inventaire_sac"]:
                col_item_nom, col_item_eq, col_item_oeil, col_item_croix = st.columns([4, 2, 1, 1])
                
                # Affichage du statut Équipé ou Non
                prefixe = "🎯 [Équipé] " if item.get("equipe", False) else "📦 [Dans le sac] "
                col_item_nom.write(f"{prefixe} **{item['nom']}** *({item['type_cat']})*")
                
                # Bouton Équiper / Déséquiper
                if item["type_cat"] in ["Arme", "Armure"]:
                    label_bouton_eq = "Déséquiper" if item.get("equipe", False) else "Équiper"
                    if col_item_eq.button(label_bouton_eq, key=f"eq_toggle_{item['id_obj']}"):
                        # Si on équipe, on peut déséquiper les autres du même type si nécessaire ou cumuler
                        item["equipe"] = not item.get("equipe", False)
                        sauver_fiche(nom_id, f)
                        st.rerun()
                else:
                    col_item_eq.write("—")

                # Bouton Oeil 👁️ pour afficher les détails de l'objet
                if col_item_oeil.button("👁️", key=f"oeil_obj_{item['id_obj']}"):
                    st.toast(f"ℹ️ **Détails de {item['nom']}** : {item.get('details', '')} | Propriétés/Effets : {item.get('proprietes', 'Aucune')}")
                    f["objet_regarde_id"] = item["id_obj"]
                
                # Bouton Croix ❌ pour jeter l'objet du sac
                if col_item_croix.button("❌", key=f"del_obj_{item['id_obj']}"):
                    f["inventaire_sac"].remove(item)
                    sauver_fiche(nom_id, f)
                    st.success("Objet retiré de l'inventaire.")
                    st.rerun()
            
                        # Affichage de la boîte d'analyse détaillée de l'œil si cliqué
            if f.get("objet_regarde_id"):
                obj_analyse = next((obj for obj in f["inventaire_sac"] if obj["id_obj"] == f["objet_regarde_id"]), None)
                if obj_analyse:
                    st.info(f"🔍 **Analyse approfondie de l'objet :** *{obj_analyse['nom']}*\n\n"
                            f"• **Catégorie :** {obj_analyse['type_cat']} \n"
                            f"• **Notes & Origine :** {obj_analyse.get('details','Modèle standard')} \n"
                            f"• **Modificateurs appliqués :** Dégâts/Résistance Bonus : {obj_analyse.get('bonus_degats', obj_analyse.get('bonus_res_p', 0))} \n"
                            f"• **Enchantements & Propriétés :** {obj_analyse.get('proprietes','Aucune')}")
        # --- PANNEAU DE CONSULTATION INTERACTIF DES CATALOGUES ---
        st.markdown("---")
        with st.expander("📖 Consulter les Grands Catalogues impériaux (Armes, Armures, Divers)"):
            onglet_cat = st.tabs(["🗡️ Catalogue des Armes", "👘 Catalogue des Armures", "📦 Catalogue des Objets Divers"])
            
            with onglet_cat[0]:
                st.markdown("##### Base de données officielle des Armes")
                for nom_w, stats_w in CATALOGUE_ARMES_AVANCE.items():
                    st.write(f"• **{nom_w}** | Dégâts : `{stats_w['degats']}` | Danger : `{stats_w['danger']}` | Portée : `{stats_w['portee']}` | Rareté : `{stats_w['rareté']}`")
                    st.caption(f"  *Propriétés : {stats_w['proprietes']} | Prise : {stats_w['prise_autorisee']}*")
            
            with onglet_cat[1]:
                st.markdown("##### Base de données officielle des Armures")
                for nom_a, stats_a in CATALOGUE_ARMURES.items():
                    st.write(f"• **{nom_a}** | Résistance Physique : `{stats_a['res_p']}` | Résistance Surnaturelle : `{stats_a['res_s']}`")
                    st.caption(f"  *Propriétés : {stats_a['proprietes']}*")
            
            with onglet_cat[2]:
                st.markdown("##### Base de données officielle des Objets Divers")
                if 'CATALOGUE_DIVERS' in globals() and CATALOGUE_DIVERS:
                    for nom_d, stats_d in CATALOGUE_DIVERS.items():
                        st.write(f"• **{nom_d}** | Catégorie : `{stats_d['type']}` | Rareté : `{stats_d['rarete']}`")
                        st.info(f"  🎯 **Effet en jeu :** {stats_d['proprietes'] if 'proprietes' in stats_d else stats_d.get('effet', 'Aucun effet renseigné')}")
                else:
                    st.warning("Le catalogue divers n'a pas pu être lu depuis le fichier d'équipements.")
        # --- ZONE D'ACHAT UNIFIÉE (AJOUTER OBJET EN BAS DE LA PAGE) ---
        st.markdown("---")
        st.subheader("🛒 Ajouter Objet (Magasin & Sac)")
        col_cat1, col_cat2, col_cat3 = st.columns(3)
        
        with col_cat1:
            st.markdown("**1. Catégorie : Armes**")
            w_achat = st.selectbox("Sélectionner une arme du catalogue :", list(CATALOGUE_ARMES_AVANCE.keys()), key="buy_w_sel")
            if st.button("➕ Ajouter l'Arme", key="btn_buy_w"):
                f["inventaire_sac"].append({
                    "id_obj": int(time.time()), "nom": w_achat, "type_cat": "Arme", 
                    "details": "Achetée au catalogue d'école standard.", "equipe": False
                })
                sauver_fiche(nom_id, f)
                st.success(f"{w_achat} ajouté au sac !")
                st.rerun()
                
        with col_cat2:
            st.markdown("**2. Catégorie : Armures**")
            a_achat = st.selectbox("Sélectionner une armure du catalogue :", list(CATALOGUE_ARMURES.keys()), key="buy_a_sel")
            if st.button("➕ Ajouter l'Armure", key="btn_buy_a"):
                f["inventaire_sac"].append({
                    "id_obj": int(time.time()), "nom": a_achat, "type_cat": "Armure", 
                    "details": "Achetée au catalogue de protection standard.", "equipe": False
                })
                sauver_fiche(nom_id, f)
                st.success(f"{a_achat} ajoutée au sac !")
                st.rerun()

        with col_cat3:
            st.markdown("**3. Catégorie : Objets Divers**")
            # Sécurité au cas où le catalogue externe met du temps à charger
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
                    st.success(f"{d_achat} glissé dans le sac !")
                    st.rerun()
            else:
                st.error("Le catalogue des objets divers est introuvable ou vide.")
        
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

        maj = {
            "perso": nom_perso, "clan": clan_actuel, "famille": famille_actuelle, "profil": roles_actuels, "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
            "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, "end_act": end_act, "sf_act": sf_act, "hon": hon, "glo": glo, "sta": sta, 
            "armure_active": armure_active, "res_p": res_p, "res_s": res_s, 
            "arme_active": arme_active_nom, "w_deg": arme_active_degats, 
            "deux_mains": "2 mains" in arme_active_nom if armes_equipees else False, 
            "w_dang": arme_active_danger, "w_por": arme_active_portee, 
            "ch_kat": c_kat, "ch_kih": c_kih, "ch_inv": c_inv, "ch_rit": c_rit, "ch_shu": c_shu, "ch_mah": c_mah, "ch_nin": c_nin, "ch_invs": c_invs,
            "score_b_air": score_b_air, "score_b_terre": score_b_terre, "score_b_feu": score_b_feu, "score_b_eau": score_b_eau, "score_b_vide": score_b_vide,
            "e_saignant": e_blinde, "e_etourdi": e_etourdi, "e_compromis": e_compromis, "e_inconscient": e_inconscient, "e_aveugle": e_aveugle,
            "b_legere": b_legere, "b_grave": b_grave, "b_mutilante": b_mutilante,
            "mes_katas": f.get("mes_katas", []), "mes_kihos": f.get("mes_kihos", []), "mes_invocs": f.get("mes_invocs", []), "mes_rituels": f.get("mes_rituels", []), "mes_shujis": f.get("mes_shujis", []), "mes_mahos": f.get("mes_mahos", []), "mes_ninjutsus": f.get("mes_ninjutsus", []), "mes_inversions": f.get("mes_inversions", []),
            "tech_active_cliquee": tech_choisie_automatique, "sh_anneaux": sh_anneaux, "sh_vitalite": sh_vitalite, "sh_social": sh_social, "sh_equipement": sh_equipement, "sh_grimoire": sh_grimoire, 
            "inventaire_sac": f.get("inventaire_sac", []),
            "c_est": c_est, "c_com": c_com, "c_sty": c_sty, "c_forg": c_forg, "c_for": c_for, "c_cac": c_cac, "c_dis": c_dis, "c_chu": c_chu, "c_med": c_med, "c_tac": c_tac, "c_cul": c_cul, "c_gou": c_gou, "c_mdc": c_mdc, "c_sen": c_sen, "c_the": c_the, "c_cmd": c_cmd, "c_crt": c_crt, "c_jeu": c_jeu, "c_org": c_org, "c_cmr": c_cmr, "c_tra": c_tra, "c_nav": c_nav, "c_mag": c_mag, "c_sur": c_sur
        }
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
