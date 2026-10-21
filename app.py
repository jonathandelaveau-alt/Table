import streamlit as st
import json
import os
import time

# 1. Configuration et Design Sombre L5A (Obligatoire tout en haut)
st.set_page_config(page_title="L5A - Table Tactique Évoluée", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    h1, h2, h3 { color: #f1c40f !important; font-family: 'Georgia', serif; }
    .stForm { background-color: #1e1e1e !important; border: 1px solid #d4af37 !important; padding: 20px; border-radius: 8px; }
    .stButton>button { background-color: #8b0000 !important; color: white !important; font-weight: bold; border: 1px solid #ff4500 !important; }
    [data-testid="stSidebar"] { background-color: #181818 !important; border-right: 1px solid #2b2b2b; }
    </style>
""", unsafe_allow_html=True)

DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
ACTIONS_FILE = "notifications_mj.json"

# Base de données officielle de l'univers L5A
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

# Catalogue d'objets physiques de référence pour le logiciel
CATALOGUE_ARMES = {
    "Wakizashi": {"degats": 3, "danger": 5, "portee": "0 - 1", "proprietes": "Acérée, Cérémoniale", "categorie": "Sabre"},
    "Katana": {"degats": 4, "danger": 5, "portee": "1", "proprietes": "Acérée, Cérémoniale", "categorie": "Sabre"},
    "Yumi (Arc)": {"degats": 5, "danger": 3, "portee": "2 - 5", "proprietes": "Encombrante", "categorie": "Arme à distance"},
    "Yari (Lance)": {"degats": 4, "danger": 6, "portee": "2", "proprietes": "Allonge", "categorie": "Arme d'hast"}
}

CATALOGUE_ARMURES = {
    "Armure de Tenue de Cérémonie": {"res_p": 1, "res_s": 0, "proprietes": "Cérémonielle, Magnifique"},
    "Armure de Cuir Bouilli": {"res_p": 2, "res_s": 0, "proprietes": "Pratique"},
    "Armure de Plaques Lourde": {"res_p": 4, "res_s": 0, "proprietes": "Encombrante, En acier"}
}

def sauver_fiche(nom_joueur, data):
    with open(os.path.join(DB_DIR, f"{nom_joueur.lower().strip()}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def charger_fiche(nom_joueur):
    path = os.path.join(DB_DIR, f"{nom_joueur.lower().strip()}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return None

role = st.sidebar.radio("🔑 Rôle :", ["Visiteur", "Joueur (Ma Fiche)", "Maître du Jeu (Hôte)"])

# ==================== VUE JOUEUR ====================
if role == "Joueur (Ma Fiche)":
    st.header("👤 Votre Feuille Dynamique")
    nom_id = st.text_input("Prénom (Identifiant de session) :").strip()
        # --- BOUTON DE SOUS-VERSION JOUEUR (ACTUALISATION MANUELLE) ---
    # Permet au joueur de forcer la réception des validations ou refus du MJ d'un seul clic
    if st.button("🔄 ACTUALISER MON PARCHEMIN (Vérifier les réponses du MJ)"):
        st.rerun()

    if nom_id:
        f = charger_fiche(nom_id) or {}
        
        # Affichage immédiat des réponses ou contraintes imposées par le MJ
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as file:
                    toutes_actions = json.load(file)
                actions_joueur = [a for a in toutes_actions if a["joueur"] == nom_id]
                if actions_joueur:
                    derniere_act = actions_joueur[-1]
                    if derniere_act["statut"] == "Validé":
                        st.success(f"✅ **Action validée par le MJ :** {derniere_act['description_mj']}")
                    elif derniere_act["statut"] == "Refusé":
                        st.error(f"❌ **Action refusée par le MJ :** {derniere_act['description_mj']}")
            except: pass

        if "inventaire_armes" not in f or not f["inventaire_armes"]: f["inventaire_armes"] = ["Wakizashi"]
        if "inventaire_armures" not in f or not f["inventaire_armures"]: f["inventaire_armures"] = ["Armure de Tenue de Cérémonie"]

        st.subheader("📝 Feuille du Personnage")
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

        st.subheader("🌀 Les Cinq Anneaux")
        sh_anneaux = st.checkbox("👁️ Partager mes 5 Anneaux avec le MJ", value=f.get("sh_anneaux", True))
        ca1, ca2, ca3, ca4, ca5 = st.columns(5)
        air = ca1.slider("Air 💨", 1, 5, value=f.get("air", 1))
        terre = ca2.slider("Terre 🏔️", 1, 5, value=f.get("terre", 1))
        feu = ca3.slider("Feu 🔥", 1, 5, value=f.get("feu", 1))
        eau = ca4.slider("Eau 💧", 1, 5, value=f.get("eau", 1))
        vide = ca5.slider("Vide 🌌", 1, 5, value=f.get("vide", 1))
        p_vide = st.number_input("Points de Vide Actuels", 0, vide, value=f.get("p_vide", 1))

        end_m, sf_m, attn, vigi = (terre + feu) * 2, (terre + eau) * 2, air + feu, (air + eau) / 2
        st.subheader("📊 Vitalité & Défenses")
        sh_vitalite = st.checkbox("👁️ Partager mes jauges avec le MJ", value=f.get("sh_vitalite", True))
        cv1, cv2 = st.columns(2)
        end_act = cv1.number_input(f"Endurance Actuelle (Max: {end_m}) :", 0, end_m, value=min(f.get("end_act", end_m), end_m))
        sf_act = cv2.number_input(f"Sang-froid Actuel (Max: {sf_m}) :", 0, sf_m, value=min(f.get("sf_act", sf_m), sf_m))

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
            cprof1, cprof2, cprof3, cprof4, cprof5 = st.columns(5)
            c_cmr, c_tra, c_nav, c_mag, c_sur = cprof1.slider("Commerce", 0, 6, value=f.get("c_cmr", 0)), cprof2.slider("Travail Manuel", 0, 6, value=f.get("c_tra", 0)), cprof3.slider("Navigation", 0, 6, value=f.get("c_nav", 0)), cprof4.slider("Magouille", 0, 6, value=f.get("c_mag", 0)), cprof5.slider("Survie", 0, 6, value=f.get("c_sur", 0))

        st.subheader("🛡️ Arsenal & Inventaire Cliquable")
        sh_equipement = st.checkbox("👁️ Partager mes équipements équipés avec le MJ", value=f.get("sh_equipement", True))
        
        st.markdown("#### 👘 Gestion des Armures")
        liste_armures_possedees = f.get("inventaire_armures", ["Armure de Tenue de Cérémonie"])
        col_add_arm, col_sel_arm = st.columns(2)
        nouvelle_arm_cat = col_add_arm.selectbox("Acheter / Ajouter une armure au catalogue :", list(CATALOGUE_ARMURES.keys()))
        if col_add_arm.button("➕ Ajouter l'armure à mon sac"):
            if nouvelle_arm_cat not in liste_armures_possedees:
                liste_armures_possedees.append(nouvelle_arm_cat)
                f["inventaire_armures"] = liste_armures_possedees
        armure_active = col_sel_arm.selectbox("Armure portée :", liste_armures_possedees, index=liste_armures_possedees.index(f.get("armure_active")) if f.get("armure_active") in liste_armures_possedees else 0)
        stats_armure = CATALOGUE_ARMURES.get(armure_active, {"res_p": 0, "res_s": 0, "proprietes": "Aucune"})
        res_p, res_s = stats_armure["res_p"], stats_armure["res_s"]

        st.markdown("#### 🗡️ Gestion des Armes")
        liste_armes_possedees = f.get("inventaire_armes", ["Wakizashi"])
        col_add_w, col_sel_w = st.columns(2)
        nouvelle_arme_cat = col_add_w.selectbox("Forger / Ajouter une arme au catalogue :", list(CATALOGUE_ARMES.keys()))
        if col_add_w.button("➕ Ajouter l'arme à mon sac"):
            if nouvelle_arme_cat not in liste_armes_possedees:
                liste_armes_possedees.append(nouvelle_arme_cat)
                f["inventaire_armes"] = liste_armes_possedees
        arme_active = col_sel_w.selectbox("Arme équipée :", liste_armes_possedees, index=liste_armes_possedees.index(f.get("arme_active")) if f.get("arme_active") in liste_armes_possedees else 0)
        stats_arme = CATALOGUE_ARMES.get(arme_active, {"degats": 0, "danger": 0, "portee": "0", "proprietes": "Aucune", "categorie": "Inconnue"})
        w_deg, w_dang_base, w_por = stats_arme["degats"], stats_arme["danger"], stats_arme["portee"]
        deux_mains = st.checkbox("Tenir cette arme à 2 mains ⚔️ (+2 Dangerosité)", value=f.get("deux_mains", False))

               # --- BASE DE DONNÉES DU CATALOGUE OFFICIEL DES TECHNIQUES ---
               # --- BASE DE DONNÉES ENRICHIE ET STRUCTURÉE DU CATALOGUE (RANG 1 À 5) ---
        CATALOGUE_COMPLET = {
            "Katas": {
                "Général": {
                    "Rang 1": ["Posture de la Sentinelle", "Éclat de la Lame"],
                    "Rang 2": ["Danse des Ombres"]
                },
                "Corps-à-corps": {
                    "Rang 1": ["Frappe du Tonnerre d'Acier"],
                    "Rang 2": ["Coup de l'Avalanche Crépusculaire"]
                },
                "Distance": {
                    "Rang 1": ["Visée du Faucon"],
                    "Rang 3": ["Flèche de Tempête"]
                },
                "Non-humain": {
                    "Rang 1": ["Esprit de la Meute"],
                    "Rang 4": ["Griffe du Dragon"]
                }
            },
            "Kíhos": {
                "Air": {"Rang 1": ["Souffle de la Brise"]},
                "Terre": {"Rang 1": ["Souffle de la Terre"]},
                "Feu": {"Rang 2": ["Flamme Intérieure"]},
                "Eau": {"Rang 1": ["Pureté des Flots"]},
                "Vide": {"Rang 3": ["Paume du Vide Éveillé"]}
            },
            "Invocations": {
                "Air": {"Rang 1": ["Murmure du Vent d'Air"]},
                "Terre": {"Rang 1": ["Communion de la Roche"]},
                "Feu": {"Rang 1": ["Appel des Esprits du Feu"]},
                "Eau": {"Rang 2": ["Colère des Flots d'Eau"]},
                "Vide": {"Rang 5": ["Équilibre Cosmique"]}
            },
            "Rituels": {
                "Général": {
                    "Rang 1": ["Communion avec les Ancêtres", "Purification du Sel"],
                    "Rang 2": ["Bénédiction de la Lignée"]
                }
            },
            "Shujis": {
                "Air": {"Rang 1": ["Insinuation Subtile"]},
                "Terre": {"Rang 1": ["Présence Majestueuse"]},
                "Feu": {"Rang 2": ["Parole Enflammée"]},
                "Eau": {"Rang 1": ["Sagesse du Fleuve"]},
                "Vide": {"Rang 6": ["Voix de l'Empereur"]} # Rang 6 exceptionnel Shuji
            },
            "Mahos": {
                "Général": {
                    "Rang 1": ["Offrande de Sang", "Malédiction de la Chair"],
                    "Rang 2": ["Éveil des Morts Déshonorés"]
                }
            },
            "Ninjutsus": {
                "Général": {
                    "Rang 1": ["Pas Sans Trace", "Dissimulation du Lotus"],
                    "Rang 2": ["Poison de l'Araignée Scorpion"]
                }
            },
            "Inversions": {
                "Général": {
                    "Rang 1": ["Altération Mineure"],
                    "Rang 5": ["Inversion des Éléments Éternels"]
                }
            }
        }

        st.subheader("📜 Grimoire Tactique & Catalogues de l'École")
        st.write("Sélectionnez vos maîtrises pour déployer les parchemins d'apprentissage :")

        # Cases à cocher pour filtrer l'affichage
        c_kat = st.checkbox("🥋 Ouvrir le Catalogue des Katas", value=f.get("ch_kat", False))
        c_kih = st.checkbox("🧘 Ouvrir le Catalogue des Kíhos", value=f.get("ch_kih", False))
        c_inv = st.checkbox("🔥 Ouvrir le Catalogue des Invocations", value=f.get("ch_inv", False))
        c_rit = st.checkbox("📿 Ouvrir le Catalogue des Rituels", value=f.get("ch_rit", False))
        c_shu = st.checkbox("🗣️ Ouvrir le Catalogue des Shujis", value=f.get("ch_shu", False))
        c_mah = st.checkbox("🩸 Ouvrir le Grimoire de la Maho", value=f.get("ch_mah", False))
        c_nin = st.checkbox("🥷 Ouvrir le Manuel de Ninjutsu", value=f.get("ch_nin", False))
        c_invs = st.checkbox("🔮 Ouvrir les Parchemins d'Inversion", value=f.get("ch_invs", False))

        # Assurer l'existence des listes de techniques apprises dans la mémoire du joueur
        for cle_grimoire in ["mes_katas", "mes_kihos", "mes_invocs", "mes_rituels", "mes_shujis", "mes_mahos", "mes_ninjutsus", "mes_inversions"]:
            if cle_grimoire not in f: f[cle_grimoire] = []

        # Fusion de toutes les techniques apprises pour remplir la boîte d'action
        grimoire_actif_total = (
            f.get("mes_katas", []) + f.get("mes_kihos", []) + f.get("mes_invocs", []) +
            f.get("mes_rituels", []) + f.get("mes_shujis", []) + f.get("mes_mahos", []) +
            f.get("mes_ninjutsus", []) + f.get("mes_inversions", [])
        )

        # Moteur d'affichage par Clicker/Sélecteur pour chaque catégorie cochée
        mapping_categories = [
            (c_kat, "Katas", "mes_katas"), (c_kih, "Kíhos", "mes_kihos"),
            (c_inv, "Invocations", "mes_invocs"), (c_rit, "Rituels", "mes_rituels"),
            (c_shu, "Shujis", "mes_shujis"), (c_mah, "Mahos", "mes_mahos"),
            (c_nin, "Ninjutsus", "mes_ninjutsus"), (c_invs, "Inversions", "mes_inversions")
        ]

        for coche, nom_cat, cle_sauvegardee in mapping_categories:
            if coche:
                st.markdown(f"### 📂 Catalogue : {nom_cat}")
                
                # Étape 1 : Choix de la sous-catégorie (ex: Général, Corps-à-corps...)
                sous_cats_dispo = list(CATALOGUE_COMPLET[nom_cat].keys())
                sub_sel = st.selectbox(f"Type de {nom_cat} :", sous_cats_dispo, key=f"sub_sel_{nom_cat}")
                
                # Étape 2 : Choix du Rang de puissance
                rangs_dispo = list(CATALOGUE_COMPLET[nom_cat][sub_sel].keys())
                rang_sel = st.selectbox(f"Sélectionner le niveau de maîtrise :", rangs_dispo, key=f"rang_sel_{nom_cat}_{sub_sel}")
                
                # Étape 3 : Liste des techniques trouvées à cet endroit précis
                liste_techs_trouvees = CATALOGUE_COMPLET[nom_cat][sub_sel][rang_sel]
                
                # Extraction du numéro de rang pour la règle visuelle
                num_rang = int(rang_sel.split()[-1])
                est_hors_ecole = num_rang > rang_ecole
                
                for t in liste_techs_trouvees:
                    if t in f[cle_sauvegardee]:
                        st.write(f"📜 {t} — *[Déjà appris et présent dans votre Grimoire Actif]*")
                    else:
                        c_txt, c_btn = st.columns([3, 1])
                        if est_hors_ecole:
                            c_txt.markdown(f"⚠️ *<span style='color:gray;'>{t} ({rang_sel}) — Exception (Scénario)</span>*", unsafe_allow_html=True)
                        else:
                            c_txt.write(f"✨ **{t}** ({rang_sel})")
                        
                        if c_btn.button("➕ Inscrire au Grimoire", key=f"btn_learn_{t}"):
                            f[cle_sauvegardee].append(t)
                            st.rerun()
        # --- REQUÊTE TACTIQUE (AVEC COLONNE TECHNIQUE APPRISE) ---
        st.markdown("---")
        st.subheader("📢 Poser une Question ou Lancer une Action au MJ")
        
        # Organisation en colonnes pour intégrer la sélection de la technique apprise
        c_a1, c_a2, c_a3 = st.columns(3)
        comp_c = c_a1.text_input("Compétence (FACULTATIF) :", placeholder="Ex: Corps-à-corps")
        elem_c = c_a2.selectbox("Élément combiné (FACULTATIF) :", ["Aucun / Simple texte", "Air 💨", "Terre 🏔️", "Feu 🔥", "Eau 💧", "Vide 🌌"])
        
        # Nouvelle colonne : choix parmi les techniques REELLEMENT apprises par le joueur
        if grimoire_actif_total:
            options_tech = ["Aucune technique associée"] + list(set(grimoire_actif_total))
            tech_c = c_a3.selectbox("Technique issue du Grimoire Actif :", options_tech)
        else:
            c_a3.caption("📖 Grimoire Actif vide (Apprenez des techniques ci-dessus)")
            tech_c = "Aucune technique associée"
            
        desc_a = st.text_area("Votre Message / Intention d'Attaque (Pourquoi faites-vous cela ?) :", placeholder="Écrivez ici vos détails...")
        
        if st.button("⚡ Soumettre la demande au MJ"):
            if desc_a and nom_perso:
                comp_final = comp_c if comp_c else "Texte pur"
                elem_final = elem_c if elem_c else "Aucun"
                
                actions = []
                if os.path.exists(ACTIONS_FILE):
                    try:
                        with open(ACTIONS_FILE, "r", encoding="utf-8") as file: actions = json.load(file)
                    except: actions = []
                actions.append({
                    "id": len(actions) + 1, "joueur": nom_id, "perso": nom_perso, 
                    "competence": comp_final, "element": elem_final, "technique": tech_c, "description": desc_a, 
                    "anneaux": {"air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide}, "statut": "En attente", "description_mj": ""
                })
                with open(ACTIONS_FILE, "w", encoding="utf-8") as file: json.dump(actions, file, indent=4, ensure_ascii=False)
                st.success("Action envoyée sur le panneau tactique du MJ.")

        # Sauvegarde automatique des parchemins et catalogues
        maj = {
            "perso": nom_perso, "clan": clan_actuel, "famille": famille_actuelle, "profil": roles_actuels, "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
            "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, "end_act": end_act, "sf_act": sf_act, "hon": hon, "glo": glo, "sta": sta, 
            "armure_active": armure_active, "res_p": res_p, "res_s": res_s, "arme_active": arme_active, "w_deg": w_deg, "deux_mains": deux_mains, "w_dang": w_dang_base, "w_por": w_por, 
            "ch_kat": c_kat, "ch_kih": c_kih, "ch_inv": c_inv, "ch_rit": c_rit, "ch_shu": c_shu, "ch_mah": c_mah, "ch_nin": c_nin, "ch_invs": c_invs,
            "mes_katas": f.get("mes_katas", []), "mes_kihos": f.get("mes_kihos", []), "mes_invocs": f.get("mes_invocs", []), "mes_rituels": f.get("mes_rituels", []),
            "mes_shujis": f.get("mes_shujis", []), "mes_mahos": f.get("mes_mahos", []), "mes_ninjutsus": f.get("mes_ninjutsus", []), "mes_inversions": f.get("mes_inversions", []),
            "c_est": c_est, "c_com": c_com, "c_sty": c_sty, "c_forg": c_forg, "c_for": c_for, "c_cac": c_cac, "c_dis": c_dis, "c_chu": c_chu, "c_med": c_med, "c_tac": c_tac,
            "c_cul": c_cul, "c_gou": c_gou, "c_mdc": c_mdc, "c_sen": c_sen, "c_the": c_the, "c_cmd": c_cmd, "c_crt": c_crt, "c_jeu": c_jeu, "c_org": c_org,
            "c_cmr": c_cmr, "c_tra": c_tra, "c_nav": c_nav, "c_mag": c_mag, "c_sur": c_sur
        }
        sauver_fiche(nom_id, maj)

# ==================== VUE MJ ====================
elif role == "Maître du Jeu (Hôte)":
    st.header("👁️ Panneau Tactique de l'Hôte")
    
    if st.button("🔄 ACTUALISER LA TABLE (Vérifier les PV, messages et actions)"):
        st.rerun()

    fichiers = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    if not fichiers:
        st.info("Aucun samouraï n'a partagé de données.")
    else:
        st.subheader("📋 Informations Autorisées par les Joueurs")
        for f in fichiers:
            chemin_fichier = os.path.join(DB_DIR, f)
            with open(chemin_fichier, "r", encoding="utf-8") as file: p = json.load(file)
            nom_j = f.replace('.json', '').capitalize()
            
            col_head1, col_head2 = st.columns(2)
            col_head1.markdown(f"### 🏯 Fiche de {nom_j}")
            if col_head2.button(f"❌ Supprimer {nom_j}", key=f"del_{nom_j}"):
                os.remove(chemin_fichier)
                st.warning(f"Fiche détruite."); st.rerun()
            
            av, tv, fv, ev = p.get('air', 1), p.get('terre', 1), p.get('feu', 1), p.get('eau', 1)
            em, sm, at, vi = (tv + fv) * 2, (tv + ev) * 2, av + fv, (av + ev) / 2
            ep, sp = em - p.get('end_act', em), sm - p.get('sf_act', sm)
            
            roles_bruts = p.get('profil', ['Bushi'])
            roles_txt = ", ".join(roles_bruts) if isinstance(roles_bruts, list) else roles_bruts
            titre_cadre = f"💮 {nom_j} : {p.get('famille','Inconnu')} {p.get('perso','Inconnu')} (Clan {p.get('clan','Inconnu')}) — Rang {p.get('rang_ecole',1)} [{roles_txt}] | Posture : {p.get('posture','Air')}"
            
            with st.expander(titre_cadre, expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**🌀 Éléments**")
                    if p.get("sh_anneaux", True):
                        st.write(f"💨 A: {av} | 🏔️ T: {tv} | 🔥 F: {fv} | 💧 E: {ev}")
                        st.write(f"🌌 Vide: {p.get('vide',1)} (Actuel: **{p.get('p_vide',0)}**)")
                    else: st.caption("🔒 Masqué par le joueur")
                with col2:
                    st.markdown("**🩸 Santé & Seuils**")
                    if p.get("sh_vitalite", True):
                        st.write(f"❤️ Endurance : **{p.get('end_act',em)} / {em}**")
                        if ep > 0: st.error(f"-{ep} PV")
                        st.write(f"🧠 Sang-froid : **{p.get('sf_act',sm)} / {sm}**")
                        if sp > 0: st.warning(f"Stress : -{sp}")
                        st.write(f"👁️ Vigilance : **{vi}** | 🧠 Attention : **{at}**")
                    else: st.caption("🔒 Masqué par le joueur")
                with col3:
                    st.markdown("**⚖️ Profil Social**")
                    if p.get("sh_social", True): st.write(f"🎖️ H: {p.get('hon',50)} | ⭐ G: {p.get('glo',50)} | 📜 S: {p.get('sta',50)}")
                    else: st.caption("🔒 Masqué par le joueur")
                with col4:
                    st.markdown("**⚔️ Arsenal Équipé**")
                    if p.get("sh_equipement", True):
                        df = (int(p.get('w_dang', 5)) + 2) if p.get('deux_mains', False) else int(p.get('w_dang', 5))
                        st.write(f"🗡️ Arme : **{p.get('arme_active','Aucune')}** ({'2 mains ⚔️' if p.get('deux_mains',False) else '1 main'})")
                        st.write(f"💥 Dégâts: {p.get('w_deg','3')} | Danger: **{df}** | 📏 Portée: {p.get('w_por','0 - 1')}")
                        st.write(f"👘 Armure: {p.get('armure_active','Aucune')} (P: {p.get('res_p',1)}/S: {p.get('res_s',0)})")
                    else: st.caption("🔒 Masqué par le joueur")
                
                # Récapitulatif des techniques apprises visibles par le MJ
                list_techs_mj = []
                for tk, tn in [("mes_katas", "Katas"), ("mes_kihos", "Kihos"), ("mes_invocs", "Invocations"), ("mes_rituels", "Rituels"), ("mes_shujis", "Shujis"), ("mes_mahos", "Maho ⚠️"), ("mes_ninjutsus", "Ninjutsu"), ("mes_inversions", "Inversions")]:
                    if p.get(tk): list_techs_mj.append(f"**{tn} :** " + ", ".join(p.get(tk)))
                if list_techs_mj:
                    st.markdown("📖 **Grimoire Actuel du Personnage :**")
                    for lt in list_techs_mj: st.write(lt)

                st.caption(f"📊 **Artisanat :** Esth: {p.get('c_est',0)}, Comp: {p.get('c_com',0)}, Sty: {p.get('c_sty',0)}, Forge: {p.get('c_forg',0)} | **Martial :** Forme: {p.get('c_for',0)}, CàC: {p.get('c_cac',0)}, Dist: {p.get('c_dis',0)}, Méd: {p.get('c_med',0)}, Tac: {p.get('c_tac',0)}")

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
                        # Affichage de la technique cliquée par le joueur
                        st.write(f"🎯 **Technique employée :** `{act.get('technique', 'Aucune')}`")
                        aj = act.get("anneaux", {})
                        st.caption(f"📈 *Anneaux :* Air: {aj.get('air',1)} | Terre: {aj.get('terre',1)} | Feu: {aj.get('feu',1)} | Eau: {aj.get('eau',1)}")
                        st.info(f"💬 **Message / Intention :** {act['description']}")
                    with colb:
                        commentaire_mj = st.text_input("Réponse ou contrainte du MJ :", key=f"txt_{act['id']}")
                        c_btn1, c_btn2 = st.columns(2)
                        
                        # Bouton vert : Autoriser la technique ou la question
                        if c_btn1.button("✅ Autoriser", key=f"val_{act['id']}"):
                            for a in actions:
                                if a["id"] == act["id"]: 
                                    a["statut"] = "Validé"
                                    a["description_mj"] = commentaire_mj if commentaire_mj else "Approuvé."
                            with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                                json.dump(actions, file, indent=4, ensure_ascii=False)
                            st.success("Validé !")
                            st.rerun()
                        
                        # Bouton rouge : Refuser la technique ou la question
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
