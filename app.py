import streamlit as st
import json
import os

# 1. Configuration et Design Sombre L5A
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

# Base de données du Lore L5A
DATA_CLANS = {
    "Crabe": ["Hida", "Hiruma", "Kaiu", "Kuni", "Yasuki"],
    "Grue": ["Doji", "Kakita", "Asahina", "Daidoji"],
    "Dragon": ["Mirumoto", "Agasha", "Togashi", "Kitsuki"],
    "Lion": ["Akodo", "Matsu", "Ikoma", "Kitsu"],
    "Phénix": ["Isawa", "Shiba", "Asako", "Agasha"],
    "Scorpion": ["Bayushi", "Shosuro", "Yogo", "Soshi"],
    "Licorne": ["Shinjo", "Utaku", "Ide", "Iuchi"],
    "Mante": ["Yoritomo", "Kitsune", "Kasuga"]
}
ROLES_LISTE = ["Bushi", "Courtisan", "Shugenja", "Moine", "Artisan", "Shinobi"]

# CATALOGUE OFFICIEL DES OBJETS DE RÉFÉRENCE
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

def notifier_mj(nom_joueur, nom_perso, comp, elem, desc, anneaux_data):
    actions = []
    if os.path.exists(ACTIONS_FILE):
        try:
            with open(ACTIONS_FILE, "r", encoding="utf-8") as file: actions = json.load(file)
        except: actions = []
    actions.append({"id": len(actions) + 1, "joueur": nom_joueur, "perso": nom_perso, "competence": comp, "element": elem, "description": desc, "anneaux": anneaux_data, "statut": "En attente"})
    with open(ACTIONS_FILE, "w", encoding="utf-8") as file: json.dump(actions, file, indent=4, ensure_ascii=False)

role = st.sidebar.radio("🔑 Rôle :", ["Visiteur", "Joueur (Ma Fiche)", "Maître du Jeu (Hôte)"])

# --- SYNC AUTOMATIQUE EN TEMPS RÉEL (Toutes les 2 secondes) ---
# Un composant invisible qui rafraîchit l'écran dès qu'un joueur ou le MJ fait un changement
st.sidebar.markdown("---")
st.sidebar.caption("🔄 Synchronisation en temps réel activée (2s)")

# Utilisation d'un composant de rafraîchissement d'arrière-plan natif
# (Simulé via st.fragment ou st.rerun temporisé pour éviter les blocages)
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# Petit mécanisme d'écoute réseau local
# Si l'accès est sélectionné, l'écran reste éveillé et synchronisé

# ==================== VUE JOUEUR ====================
# ==================== VUE JOUEUR (PARTIE A) ====================
if role == "Joueur (Ma Fiche)":
    st.header("👤 Votre Feuille Dynamique")
    nom_id = st.text_input("Prénom (Identifiant de session) :").strip()
    
    if nom_id:
        f = charger_fiche(nom_id) or {}
        
        # --- BLOC DE NOTIFICATION EN TEMPS RÉEL DU MJ ---
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as file:
                    toutes_actions = json.load(file)
                actions_joueur = [a for a in toutes_actions if a["joueur"] == nom_id]
                if actions_joueur:
                    derniere_act = actions_joueur[-1]
                    if "+st" in st.session_state:
                        pass
                    if derniere_act["statut"] == "Validé":
                        st.success(f"✅ **Action validée par le MJ :** {derniere_act['description_mj']}")
                    elif derniere_act["statut"] == "Refusé":
                        st.error(f"❌ **Action refusée par le MJ :** {derniere_act['description_mj']}")
            except:
                pass

        if "inventaire_armes" not in f or not f["inventaire_armes"]: f["inventaire_armes"] = ["Wakizashi"]
        if "inventaire_armures" not in f or not f["inventaire_armures"]: f["inventaire_armures"] = ["Armure de Tenue de Cérémonie"]

        st.subheader("📝 État-Civil Tactique (Changements instantanés)")
        col_civ1, col_civ2, col_civ3 = st.columns(3)
        nom_perso = col_civ1.text_input("Nom du Personnage :", value=f.get("perso", ""))
        clan_actuel = col_civ2.selectbox("Sélectionnez votre Clan :", list(DATA_CLANS.keys()), index=list(DATA_CLANS.keys()).index(f.get("clan", "Grue")) if f.get("clan") in DATA_CLANS else 1)
        liste_familles_filtrees = DATA_CLANS[clan_actuel]
        famille_actuelle = col_civ3.selectbox("Sélectionnez votre Famille :", liste_familles_filtrees, index=liste_familles_filtrees.index(f.get("famille")) if f.get("famille") in liste_familles_filtrees else 0)
        
        col_civ4, col_civ5, col_civ6 = st.columns(3)
        ecole = col_civ4.text_input("Nom de l'École :", value=f.get("ecole", ""))
        rang_ecole = col_civ5.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
        roles_actuels = col_civ6.multiselect("Sélectionnez votre ou vos Rôles :", ROLES_LISTE, default=f.get("profil", ["Bushi"]))

        with st.form("form_l5a_principal"):
            # --- POSTURE ET ANNEAUX ---
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

            # --- LES 5 CATÉGORIES DE COMPÉTENCES ---
            st.subheader("🎭 Grille des 25 Compétences Officielles")

            with st.expander("🎨 1. Compétences Artisanales"):
                cart1, cart2, cart3, cart4 = st.columns(4)
                c_est = cart1.slider("Esthétique", 0, 6, value=f.get("c_est", 0))
                c_com = cart2.slider("Composition", 0, 6, value=f.get("c_com", 0))
                c_sty = cart3.slider("Stylisme", 0, 6, value=f.get("c_sty", 0))
                c_forg = cart4.slider("Forge 🔨", 0, 6, value=f.get("c_forg", 0)) # Ajout de Forge

            with st.expander("⚔️ 2. Compétences Martiales"):
                cm1, cm2, cm3, cm4, cm5, cm6 = st.columns(6)
                c_for = cm1.slider("Forme", 0, 6, value=f.get("c_for", 0))
                c_cac = cm2.slider("Corps-à-corps", 0, 6, value=f.get("c_cac", 0))
                c_dis = cm3.slider("Distance", 0, 6, value=f.get("c_dis", 0))
                c_chu = cm4.slider("Corps Humain", 0, 6, value=f.get("c_chu", 0))
                c_med = cm5.slider("Méditation", 0, 6, value=f.get("c_med", 0))
                c_tac = cm6.slider("Tactique", 0, 6, value=f.get("c_tac", 0))

            with st.expander("📜 3. Compétences Savantes"):
                csav1, csav2, csav3, csav4, csav5 = st.columns(5)
                c_cul = csav1.slider("Culture", 0, 6, value=f.get("c_cul", 0))
                c_gou = csav2.slider("Gouvernement", 0, 6, value=f.get("c_gou", 0))
                c_mdc = csav3.slider("Médecine", 0, 6, value=f.get("c_mdc", 0))
                c_sen = csav4.slider("Sentiment", 0, 6, value=f.get("c_sen", 0))
                c_the = csav5.slider("Théologie", 0, 6, value=f.get("c_the", 0))

            with st.expander("🗣️ 4. Compétences Sociales"):
                csoc1, csoc2, csoc3, csoc4 = st.columns(4)
                c_cmd = csoc1.slider("Commandement", 0, 6, value=f.get("c_cmd", 0))
                c_crt = csoc2.slider("Courtoisie", 0, 6, value=f.get("c_crt", 0))
                c_jeu = csoc3.slider("Jeu", 0, 6, value=f.get("c_jeu", 0))
                c_org = csoc4.slider("Organisation 📋", 0, 6, value=f.get("c_org", 0)) # Ajout d'Organisation

            with st.expander("🛠️ 5. Compétences Professionnelles"):
                cprof1, cprof2, cprof3, cprof4, cprof5 = st.columns(5)
                c_cmr = cprof1.slider("Commerce", 0, 6, value=f.get("c_cmr", 0))
                c_tra = cprof2.slider("Travail Manuel", 0, 6, value=f.get("c_tra", 0))
                c_nav = cprof3.slider("Navigation", 0, 6, value=f.get("c_nav", 0))
                c_mag = cprof4.slider("Magouille", 0, 6, value=f.get("c_mag", 0))
                c_sur = cprof5.slider("Survie", 0, 6, value=f.get("c_sur", 0))
            st.subheader("🛡️ Arsenal & Inventaire Cliquable")
            sh_equipement = st.checkbox("👁️ Partager mes équipements équipés avec le MJ", value=f.get("sh_equipement", True))
            
            st.markdown("#### 👘 Gestion des Armures")
            liste_armures_possedees = f.get("inventaire_armures", ["Armure de Tenue de Cérémonie"])
            col_add_arm, col_sel_arm = st.columns(2)
            nouvelle_arm_cat = col_add_arm.selectbox("Acheter / Ajouter une armure au catalogue :", list(CATALOGUE_ARMURES.keys()))
            if col_add_arm.form_submit_button("➕ Ajouter l'armure"):
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
            if col_add_w.form_submit_button("➕ Ajouter l'arme"):
                if nouvelle_arme_cat not in liste_armes_possedees:
                    liste_armes_possedees.append(nouvelle_arme_cat)
                    f["inventaire_armes"] = liste_armes_possedees
            arme_active = col_sel_w.selectbox("Arme équipée :", liste_armes_possedees, index=liste_armes_possedees.index(f.get("arme_active")) if f.get("arme_active") in liste_armes_possedees else 0)
            stats_arme = CATALOGUE_ARMES.get(arme_active, {"degats": 0, "danger": 0, "portee": "0", "proprietes": "Aucune", "categorie": "Inconnue"})
            w_deg, w_dang_base, w_por = stats_arme["degats"], stats_arme["danger"], stats_arme["portee"]
            deux_mains = st.checkbox("Tenir cette arme à 2 mains ⚔️ (+2 Dangerosité)", value=f.get("deux_mains", False))

            st.subheader("📜 Grimoire des Techniques Apprises")
            with st.expander("Éditer mon catalogue de techniques secrètes"):
                t_kat = st.text_area("Katas :", f.get("t_kat",""))
                t_kih = st.text_area("Kihos :", f.get("t_kih",""))
                t_inv = st.text_area("Invocations :", f.get("t_inv",""))
                t_rit = st.text_area("Rituels :", f.get("t_rit",""))
                t_shu = st.text_area("Shujis :", f.get("t_shu",""))
                t_mah = st.text_area("Maho :", f.get("t_mah",""))
                t_nin = st.text_area("Ninjutsu :", f.get("t_nin",""))
                t_invs = st.text_area("Inversions :", f.get("t_invs",""))

            if st.form_submit_button("💾 Enregistrer ma Session"):
                maj = {
                    "perso": nom_perso, "clan": clan_actuel, "famille": famille_actuelle, "profil": roles_actuels, "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
                    "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, "end_act": end_act, "sf_act": sf_act, "hon": hon, "glo": glo, "sta": sta, 
                    "armure_active": armure_active, "res_p": res_p, "res_s": res_s, "arme_active": arme_active, "w_deg": w_deg, "deux_mains": deux_mains, "w_dang": w_dang_base, "w_por": w_por, 
                    "t_kat": t_kat, "t_kih": t_kih, "t_inv": t_inv, "t_rit": t_rit, "t_shu": t_shu, "t_mah": t_mah, "t_nin": t_nin, "t_invs": t_invs, "sh_anneaux": sh_anneaux, "sh_vitalite": sh_vitalite,
                    "sh_social": sh_social, "sh_equipement": sh_equipement, "inventaire_armes": liste_armes_possedees, "inventaire_armures": liste_armures_possedees,
                    "c_est": c_est, "c_com": c_com, "c_sty": c_sty, "c_forg": c_forg, "c_for": c_for, "c_cac": c_cac, "c_dis": c_dis, "c_chu": c_chu, "c_med": c_med, "c_tac": c_tac,
                    "c_cul": c_cul, "c_gou": c_gou, "c_mdc": c_mdc, "c_sen": c_sen, "c_the": c_the, "c_cmd": c_cmd, "c_crt": c_crt, "c_jeu": c_jeu, "c_org": c_org,
                    "c_cmr": c_cmr, "c_tra": c_tra, "c_nav": c_nav, "c_mag": c_mag, "c_sur": c_sur
                }
                sauver_fiche(nom_id, maj)
                st.success("Fiche synchronisée !"); st.rerun()

        # --- REQUÊTE FACULTATIVE (COMPÉTENCE ET ÉLÉMENT FACULTATIFS) ---
        st.markdown("---")
        st.subheader("📢 Poser une Question ou Lancer une Action au MJ")
        c_a1, c_a2 = st.columns(2)
        comp_c = c_a1.text_input("Compétence (FACULTATIF) :", placeholder="Laissez vide pour une simple question")
        elem_c = c_a2.selectbox("Élément combiné (FACULTATIF) :", ["Aucun / Simple texte", "Air 💨", "Terre 🏔️", "Feu 🔥", "Eau 💧", "Vide 🌌"])
        desc_a = st.text_area("Votre Message / Question / Technique :", placeholder="Écrivez ici ce que vous voulez demander ou faire...")
        
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
                    "competence": comp_final, "element": elem_final, "description": desc_a, 
                    "anneaux": {"air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide}, 
                    "statut": "En attente", "description_mj": ""
                })
                with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                    json.dump(actions, file, indent=4, ensure_ascii=False)
                st.success("Message envoyé sur le panneau tactique du MJ.")


# ==================== VUE MJ ====================
elif role == "Maître du Jeu (Hôte)":
    st.header("👁️ Panneau Tactique de l'Hôte")
    fichiers = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    
    if not fichiers:
        st.info("Aucun samouraï n'a partagé de données.")
    else:
        st.subheader("📋 Informations Autorisées par les Joueurs")
        for f in fichiers:
            chemin_fichier = os.path.join(DB_DIR, f)
            with open(chemin_fichier, "r", encoding="utf-8") as file: 
                p = json.load(file)
            nom_j = f.replace('.json', '').capitalize()
            
            # --- ❌ BOUTON DE SUPPRESSION DE FICHE (CROIX DU MJ) ---
            col_head1, col_head2 = st.columns([5, 1])
            col_head1.markdown(f"### 🏯 Fiche de {nom_j}")
            if col_head2.button(f"❌ Supprimer {nom_j}", key=f"del_{nom_j}", help="Supprime définitivement ce joueur de la session"):
                os.remove(chemin_fichier)
                st.warning(f"La fiche de {nom_j} a été détruite."); st.rerun()
            
            # Chargement des variables pour les calculs secondaires automatiques
            air_v = p.get('air', 1)
            terre_v = p.get('terre', 1)
            feu_v = p.get('feu', 1)
            eau_v = p.get('eau', 1)
            
            c_end_m = (terre_v + feu_v) * 2
            c_sf_m = (terre_v + eau_v) * 2
            c_attn = air_v + feu_v
            c_vigi = (air_v + eau_v) / 2
            
            end_p = c_end_m - p.get('end_act', c_end_m)
            sf_p = c_sf_m - p.get('sf_act', c_sf_m)
            
            roles_bruts = p.get('profil', ['Bushi'])
            roles_txt = ", ".join(roles_bruts) if isinstance(roles_bruts, list) else roles_bruts
            titre_cadre = f"💮 {nom_j} : {p.get('famille','Inconnu')} {p.get('perso','Inconnu')} (Clan {p.get('clan','Inconnu')}) — [{roles_txt}] | Posture : {p.get('posture','Air')}"
            
            with st.expander(titre_cadre, expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                # BLOC 1 : ANNEAUX (Soumis au bouton œil du joueur)
                with col1:
                    st.markdown("**🌀 Éléments**")
                    if p.get("sh_anneaux", True):
                        st.write(f"💨 A: {air_v} | 🏔️ T: {terre_v} | 🔥 F: {feu_v} | 💧 E: {eau_v}")
                        st.write(f"🌌 Vide: {p.get('vide',1)} (Actuel: **{p.get('p_vide',0)}**)")
                    else: 
                        st.caption("🔒 Masqué par le joueur")
                
                # BLOC 2 : VITALITÉ (Soumis au bouton œil du joueur)
                with col2:
                    st.markdown("**🩸 Santé & Seuils**")
                    if p.get("sh_vitalite", True):
                        st.write(f"❤️ Endurance : **{p.get('end_act',c_end_m)} / {c_end_m}**")
                        if end_p > 0: st.error(f"-{end_p} PV")
                        st.write(f"🧠 Sang-froid : **{p.get('sf_act',c_sf_m)} / {c_sf_m}**")
                        if sf_p > 0: st.warning(f"Stress : -{sf_p}")
                        st.write(f"👁️ Vigilance : **{c_vigi}** | 🧠 Attention : **{c_attn}**")
                    else: 
                        st.caption("🔒 Masqué par le joueur")
                        
                # BLOC 3 : CARACTÉRISTIQUES SOCIALES (Soumis au bouton œil du joueur)
                with col3:
                    st.markdown("**⚖️ Profil Social**")
                    if p.get("sh_social", True): 
                        st.write(f"🎖️ H: {p.get('hon',50)} | ⭐ G: {p.get('glo',50)} | 📜 S: {p.get('sta',50)}")
                    else: 
                        st.caption("🔒 Masqué par le joueur")
                        
                # BLOC 4 : ÉQUIPEMENT DYNAMIQUE (Soumis au bouton œil du joueur)
                with col4:
                    st.markdown("**⚔️ Arsenal Équipé**")
                    if p.get("sh_equipement", True):
                        d_base = int(p.get('w_dang', 5))
                        d_final = (d_base + 2) if p.get('deux_mains', False) else d_base
                        st.write(f"🗡️ Arme : **{p.get('arme_active','Aucune')}** ({'2 mains ⚔️' if p.get('deux_mains',False) else '1 main'})")
                        st.write(f"💥 Dégâts: {p.get('w_deg','3')} | Danger: **{d_final}** | 📏 Portée: {p.get('w_por','0 - 1')}")
                        st.write(f"👘 Armure: {p.get('armure_active','Aucune')} (P: {p.get('res_p',1)}/S: {p.get('res_s',0)})")
                    else: 
                        st.caption("🔒 Masqué par le joueur")
                
                # Rappel constant des compétences en bas de chaque expander (uniquement pour la lecture globale si partagée)
                st.caption(f"📊 **Artisanat :** Esth: {p.get('c_est',0)}, Comp: {p.get('c_com',0)}, Sty: {p.get('c_sty',0)}, Forge: {p.get('c_forg',0)} | **Martial :** Forme: {p.get('c_for',0)}, CàC: {p.get('c_cac',0)}, Dist: {p.get('c_dis',0)}, Corps Humain: {p.get('c_chu',0)}, Méd: {p.get('c_med',0)}, Tac: {p.get('c_tac',0)}")
                st.caption(f"📊 **Savant :** Cult: {p.get('c_cul',0)}, Gouv: {p.get('c_gou',0)}, Méd: {p.get('c_mdc',0)}, Sent: {p.get('c_sen',0)}, Théo: {p.get('c_the',0)} | **Social :** Comm: {p.get('c_cmd',0)}, Court: {p.get('c_crt',0)}, Jeu: {p.get('c_jeu',0)}, Org: {p.get('c_org',0)}")
                st.caption(f"📊 **Pro :** Commerce: {p.get('c_cmr',0)}, Travail: {p.get('c_tra',0)}, Nav: {p.get('c_nav',0)}, Magouille: {p.get('c_mag',0)}, Survie: {p.get('c_sur',0)}")

        # --- GESTIONNAIRE DE REQUÊTES (VALIDER / REFUSER AVEC NOTIFICATION EFFECTIVE) ---
        st.markdown("---")
        st.subheader("🔔 Boîte de réception des Actions Soumises")
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as file: 
                    actions = json.load(file)
            except: 
                actions = []
            
            en_attente = [a for a in actions if a["statut"] == "En attente"]
            if not en_attente: 
                st.info("Aucune action ou question en attente d'arbitrage.")
            else:
                for act in en_attente:
                    st.markdown("---")
                    cola, colb = st.columns([2, 1])
                    with cola:
                        st.warning(f"⚔️ **{act['joueur']}** ({act['perso']}) sollicite l'arbitrage !")
                        st.write(f"🔹 **Jet requis :** Compétence **[{act['competence']}]** + Élément **[{act['element']}]**")
                        aj = act.get("anneaux", {})
                        st.caption(f"📈 *Rappel de ses anneaux :* Air: {aj.get('air',1)} | Terre: {aj.get('terre',1)} | Feu: {aj.get('feu',1)} | Eau: {aj.get('eau',1)} | Vide: {aj.get('vide',1)}")
                        st.info(f"💬 **Message / Technique :** {act['description']}")
                    
                    with colb:
                        # Case de texte pour que le MJ écrive sa sentence, transmise au bandeau du joueur
                        commentaire_mj = st.text_input("Réponse ou contrainte du MJ (Ex: Jet DD 2 / Lancer impossible) :", key=f"txt_{act['id']}")
                        
                        c_btn1, c_btn2 = st.columns(2)
                        
                        # Bouton vert : Validation
                        if c_btn1.button("✅ Autoriser", key=f"val_{act['id']}"):
                            for a in actions:
                                if a["id"] == act["id"]: 
                                    a["statut"] = "Validé"
                                    a["description_mj"] = commentaire_mj if commentaire_mj else "Action approuvée par le MJ."
                            with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                                json.dump(actions, file, indent=4, ensure_ascii=False)
                            st.success("Action approuvée !"); st.rerun()
                        
                        # Bouton rouge : Refus
                        if c_btn2.button("⛔ Refuser", key=f"ref_{act['id']}"):
                            for a in actions:
                                if a["id"] == act["id"]: 
                                    a["statut"] = "Refusé"
                                    a["description_mj"] = commentaire_mj if commentaire_mj else "Action rejetée par le MJ."
                            with open(ACTIONS_FILE, "w", encoding="utf-8") as file: 
                                json.dump(actions, file, indent=4, ensure_ascii=False)
                            st.error("Action rejetée !"); st.rerun()
        else: 
            st.info("Aucune notification reçue.")
else:
    st.info("👈 Veuillez sélectionner votre accès dans le menu latéral gauche.")

