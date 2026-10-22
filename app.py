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

        st.subheader("🛡️ Arsenal & Inventaire Cliquable")
        sh_equipement = st.checkbox("👁️ Partager mes équipements équipés avec le MJ", value=f.get("sh_equipement", True))
        
        st.markdown("#### 👘 Gestion des Armures")
        liste_armures_possedees = f.get("inventaire_armures", ["Armure de Tenue de Cérémonie"])
        col_add_arm, col_sel_arm = st.columns(2)
        nouvelle_arm_cat = col_add_arm.selectbox("Acheter une armure :", list(CATALOGUE_ARMURES.keys()))
        if col_add_arm.button("➕ Ajouter l'armure"):
            if nouvelle_arm_cat not in liste_armures_possedees:
                liste_armures_possedees.append(nouvelle_arm_cat)
                f["inventaire_armures"] = liste_armures_possedees
        armure_active = col_sel_arm.selectbox("Armure portée :", liste_armures_possedees, index=liste_armures_possedees.index(f.get("armure_active")) if f.get("armure_active") in liste_armures_possedees else 0)
        stats_armure = CATALOGUE_ARMURES.get(armure_active, {"res_p": 1, "res_s": 0, "proprietes": "Aucune"})
        res_p, res_s = stats_armure["res_p"], stats_armure["res_s"]

        st.markdown("#### 🗡️ Galerie Tactique des Armes")
        liste_armes_possedees = f.get("inventaire_armes_complexe", [])
        if not liste_armes_possedees:
            liste_armes_possedees = [{"nom_modele": "Wakizashi", "degats_bonus": 0, "danger_bonus": 0, "portee_modifiee": "", "props_ajoutees": "", "rarete_modifiee": 4, "notes_mj": "", "prise_choisie": "1 main"}]
            f["inventaire_armes_complexe"] = liste_armes_possedees

        col_add_w1, col_add_w2 = st.columns(2)
        arme_selectionnee_catalogue = col_add_w1.selectbox("Sélectionner un modèle :", list(CATALOGUE_ARMES_AVANCE.keys()))
        if col_add_w2.button("➕ Forger et ajouter"):
            base_stats = CATALOGUE_ARMES_AVANCE[arme_selectionnee_catalogue]
            liste_armes_possedees.append({"nom_modele": arme_selectionnee_catalogue, "degats_bonus": 0, "danger_bonus": 0, "portee_modifiee": "", "props_ajoutees": "", "rarete_modifiee": base_stats["rareté"], "notes_mj": "", "prise_choisie": "1 main"})
            f["inventaire_armes_complexe"] = liste_armes_possedees
            st.rerun()

        noms_armes_sac = [item['nom_modele'] for item in liste_armes_possedees]
        arme_choisie_nom = st.selectbox("Arme active en main :", noms_armes_sac, key="w_active_name")
        idx_arme = noms_armes_sac.index(arme_choisie_nom)
        w_joueur = liste_armes_possedees[idx_arme]
        w_base = CATALOGUE_ARMES_AVANCE.get(w_joueur["nom_modele"], {"competence": "Inconnue", "portee": "1", "degats": 3, "danger": 5, "rareté": 4, "prise_autorisee": "1 main", "effet_2_mains": {"danger":0,"degats":0,"portee":0,"texte":""}, "proprietes": "Ordinaire"})

        with st.expander("🛠️ Laboratoire d'Altération & Forgeron"):
            w_joueur["degats_bonus"] = st.number_input("Dégâts bonus :", value=int(w_joueur.get("degats_bonus", 0)), key=f"alt_deg_{idx_arme}")
            w_joueur["danger_bonus"] = st.number_input("Dangerosité bonus :", value=int(w_joueur.get("danger_bonus", 0)), key=f"alt_dang_{idx_arme}")
            w_joueur["portee_modifiee"] = st.text_input("Portée modifiée :", value=w_joueur.get("portee_modifiee", ""), key=f"alt_port_{idx_arme}")
            w_joueur["rarete_modifiee"] = st.number_input("Rareté ajustée :", value=int(w_joueur.get("rarete_modifiee", w_base["rareté"])), key=f"alt_rar_{idx_arme}")
            w_joueur["props_ajoutees"] = st.text_input("Propriétés ajoutées :", value=w_joueur.get("props_ajoutees", ""), key=f"alt_prop_{idx_arme}")
            w_joueur["notes_mj"] = st.text_area("Notes de l'objet :", value=w_joueur.get("notes_mj", ""), key=f"alt_notes_{idx_arme}")

        prise_legale = w_base["prise_autorisee"]
        if "1 main ou 2 mains" in prise_legale:
            w_joueur["prise_choisie"] = st.radio("Prise :", ["1 main", "2 mains"], index=0 if w_joueur.get("prise_choisie", "1 main") == "1 main" else 1, key=f"prise_w_radio_{idx_arme}")
        else:
            w_joueur["prise_choisie"] = "2 mains" if "2 mains" in prise_legale else "1 main"

        degats_finals = w_base["degats"] + int(w_joueur.get("degats_bonus", 0))
        danger_final = w_base["danger"] + int(w_joueur.get("danger_bonus", 0))
        portee_finale = w_joueur["portee_modifiee"] if w_joueur.get("portee_modifiee", "").strip() else w_base["portee"]
        if w_joueur["prise_choisie"] == "2 mains" and "1 main ou 2 mains" in prise_legale:
            degats_finals += w_base.get("effet_2_mains", {}).get("degats", 0)
            danger_final += w_base.get("effet_2_mains", {}).get("danger", 0)

        arme_active_nom = w_joueur["nom_modele"]
        arme_active_degats = degats_finals
        arme_active_danger = danger_final
        arme_active_portee = portee_finale

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

        maj = {
            "perso": nom_perso, "clan": clan_actuel, "famille": famille_actuelle, "profil": roles_actuels, "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
            "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, "end_act": end_act, "sf_act": sf_act, "hon": hon, "glo": glo, "sta": sta, 
            "armure_active": armure_active, "res_p": res_p, "res_s": res_s, "arme_active": arme_active_nom, "w_deg": arme_active_degats, "deux_mains": "2 mains" in w_joueur["prise_choisie"], "w_dang": arme_active_danger, "w_por": arme_active_portee, 
            "ch_kat": c_kat, "ch_kih": c_kih, "ch_inv": c_inv, "ch_rit": c_rit, "ch_shu": c_shu, "ch_mah": c_mah, "ch_nin": c_nin, "ch_invs": c_invs,
            "score_b_air": score_b_air, "score_b_terre": score_b_terre, "score_b_feu": score_b_feu, "score_b_eau": score_b_eau, "score_b_vide": score_b_vide,
            "e_saignant": e_blinde, "e_etourdi": e_etourdi, "e_compromis": e_compromis, "e_inconscient": e_inconscient, "e_aveugle": e_aveugle,
            "b_legere": b_legere, "b_grave": b_grave, "b_mutilante": b_mutilante,
            "mes_katas": f.get("mes_katas", []), "mes_kihos": f.get("mes_kihos", []), "mes_invocs": f.get("mes_invocs", []), "mes_rituels": f.get("mes_rituels", []), "mes_shujis": f.get("mes_shujis", []), "mes_mahos": f.get("mes_mahos", []), "mes_ninjutsus": f.get("mes_ninjutsus", []), "mes_inversions": f.get("mes_inversions", []),
            "tech_active_cliquee": tech_choisie_automatique, "sh_anneaux": sh_anneaux, "sh_vitalite": sh_vitalite, "sh_social": sh_social, "sh_equipement": sh_equipement, "sh_grimoire": sh_grimoire, "inventaire_armes_complexe": liste_armes_possedees, "inventaire_armures": liste_armures_possedees,
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
