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
    "Mante / Mineur": ["Yoritomo", "Kitsune", "Kasuga"]
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

# ==================== VUE JOUEUR ====================
if role == "Joueur (Ma Fiche)":
    st.header("👤 Votre Feuille Dynamique")
    nom_id = st.text_input("Prénom (Identifiant de session) :").strip()
    
    if nom_id:
        f = charger_fiche(nom_id) or {}
        
        # INITIALISATION INVENTAIRE SI ABSENT
        if "inventaire_armes" not in f or not f["inventaire_armes"]:
            f["inventaire_armes"] = ["Wakizashi"]
        if "inventaire_armures" not in f or not f["inventaire_armures"]:
            f["inventaire_armures"] = ["Armure de Tenue de Cérémonie"]

        st.subheader("📝 État-Civil Tactique (Changements instantanés)")
        col_civ1, col_civ2, col_civ3 = st.columns(3)
        
        # SÉLECTION DYNAMIQUE HORS DU FORMULAIRE POUR LE CLAN ET LA FAMILLE
        nom_perso = col_civ1.text_input("Nom du Personnage :", value=f.get("perso", ""))
        clan_actuel = col_civ2.selectbox("Sélectionnez votre Clan :", list(DATA_CLANS.keys()), index=list(DATA_CLANS.keys()).index(f.get("clan", "Grue")) if f.get("clan") in DATA_CLANS else 1)
        
        # Filtrage automatique de la famille selon le clan choisi sans rechargement
        liste_familles_filtrees = DATA_CLANS[clan_actuel]
        famille_actuelle = col_civ3.selectbox("Sélectionnez votre Famille :", liste_familles_filtrees, index=liste_familles_filtrees.index(f.get("famille")) if f.get("famille") in liste_familles_filtrees else 0)
        
        col_civ4, col_civ5, col_civ6 = st.columns(3)
        ecole = col_civ4.text_input("Nom de l'École :", value=f.get("ecole", ""))
        rang_ecole = col_civ5.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
        
        # POSSIBILITÉ DE SÉLECTIONNER PLUSIEURS RÔLES SIMULTANÉMENT
        roles_actuels = col_civ6.multiselect("Sélectionnez votre ou vos Rôles :", ROLES_LISTE, default=f.get("profil", ["Bushi"]))

        # RESTE DES DONNÉES EN FORMULAIRE POUR LA BASE DE DONNÉES
        with st.form("form_l5a_principal"):
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

            st.subheader("🎭 Grille des 25 Compétences")
            with st.expander("Éditer mes compétences de rang 0 à 6"):
                c_est, c_com, c_sty = st.slider("Esthétique", 0,6, f.get("c_est",0)), st.slider("Composition", 0,6, f.get("c_com",0)), st.slider("Stylisme", 0,6, f.get("c_sty",0))
                c_for, c_cac, c_dis = st.slider("Forme", 0,6, f.get("c_for",0)), st.slider("Corps-à-corps", 0,6, f.get("c_cac",0)), st.slider("Distance", 0,6, f.get("c_dis",0))
                c_chu, c_med, c_cul = st.slider("Corps Humain", 0,6, f.get("c_chu",0)), st.slider("Méditation", 0,6, f.get("c_med",0)), st.slider("Culture", 0,6, f.get("c_cul",0))
                c_gou, c_mdc, c_sen = st.slider("Gouvernement", 0,6, f.get("c_gou",0)), st.slider("Médecine", 0,6, f.get("c_mdc",0)), st.slider("Sentiment", 0,6, f.get("c_sen",0))
                c_the, c_cmd, c_crt = st.slider("Théologie", 0,6, f.get("c_the",0)), st.slider("Commandement", 0,6, f.get("c_cmd",0)), st.slider("Courtoisie", 0,6, f.get("c_crt",0))
                c_jeu, c_rep, c_cmr = st.slider("Jeu", 0,6, f.get("c_jeu",0)), st.slider("Représentation", 0,6, f.get("c_rep",0)), st.slider("Commerce", 0,6, f.get("c_cmr",0))
                c_tra, c_nav, c_mag = st.slider("Travail Manuel", 0,6, f.get("c_tra",0)), st.slider("Navigation", 0,6, f.get("c_nav",0)), st.slider("Magouille", 0,6, f.get("c_mag",0))
                c_sur = st.slider("Survie", 0,6, f.get("c_sur",0))
            st.subheader("🛡️ Arsenal & Inventaire Cliquable")
            sh_equipement = st.checkbox("👁️ Partager mes équipements équipés avec le MJ", value=f.get("sh_equipement", True))
            
            # --- GESTION DE L'ARMURE ---
            st.markdown("#### 👘 Gestion des Armures")
            liste_armures_possedees = f.get("inventaire_armures", ["Armure de Tenue de Cérémonie"])
            
            col_add_arm, col_sel_arm = st.columns(2)
            nouvelle_arm_cat = col_add_arm.selectbox("Acheter / Ajouter une armure au catalogue :", list(CATALOGUE_ARMURES.keys()))
            if col_add_arm.form_submit_button("➕ Ajouter l'armure à l'inventaire", help="Cliquez ici pour l'ajouter à vos choix possibles"):
                if nouvelle_arm_cat not in liste_armures_possedees:
                    liste_armures_possedees.append(nouvelle_arm_cat)
                    f["inventaire_armures"] = liste_armures_possedees
            
            armure_active = col_sel_arm.selectbox("Armure actuellement portée sur vous :", liste_armures_possedees, index=liste_armures_possedees.index(f.get("armure_active")) if f.get("armure_active") in liste_armures_possedees else 0)
            
            # Extraction des données de l'armure active
            stats_armure = CATALOGUE_ARMURES.get(armure_active, {"res_p": 0, "res_s": 0, "proprietes": "Aucune"})
            res_p = stats_armure["res_p"]
            res_s = stats_armure["res_s"]
            st.caption(f"📊 *Caractéristiques portées :* Résistance Physique : **{res_p}** | Surnaturelle : **{res_s}** | Propriétés : *{stats_armure['proprietes']}*")

            # --- GESTION DE L'ARME ---
            st.markdown("#### 🗡️ Gestion des Armes")
            liste_armes_possedees = f.get("inventaire_armes", ["Wakizashi"])
            
            col_add_w, col_sel_w = st.columns(2)
            nouvelle_arme_cat = col_add_w.selectbox("Forger / Ajouter une arme au catalogue :", list(CATALOGUE_ARMES.keys()))
            if col_add_w.form_submit_button("➕ Ajouter l'arme à l'inventaire", help="Ajoute cette arme dans votre sac de transport"):
                if nouvelle_arme_cat not in liste_armes_possedees:
                    liste_armes_possedees.append(nouvelle_arme_cat)
                    f["inventaire_armes"] = liste_armes_possedees
            
            arme_active = col_sel_w.selectbox("Arme dégainée / Équipée en main :", liste_armes_possedees, index=liste_armes_possedees.index(f.get("arme_active")) if f.get("arme_active") in liste_armes_possedees else 0)
            
            # Extraction et calcul de la prise en main (2 mains = Dangerosité + 2)
            stats_arme = CATALOGUE_ARMES.get(arme_active, {"degats": 0, "danger": 0, "portee": "0", "proprietes": "Aucune", "categorie": "Inconnue"})
            w_deg = stats_arme["degats"]
            w_dang_base = stats_arme["danger"]
            w_por = stats_arme["portee"]
            
            deux_mains = st.checkbox("Tenir cette arme à 2 mains ⚔️ (Applique le bonus mécanique de +2 en Dangerosité)", value=f.get("deux_mains", False))
            w_dang_final = (w_dang_base + 2) if deux_mains else w_dang_base
            st.caption(f"📊 *Caractéristiques en main :* Catégorie : **{stats_arme['categorie']}** | Dégâts : **{w_deg}** | Dangerosité Totale : **{w_dang_final}** | Portée : **{w_por}** | Propriétés : *{stats_arme['proprietes']}*")

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

            if st.form_submit_button("💾 Enregistrer et Sauvegarder ma Session"):
                maj = {
                    "perso": nom_perso, "clan": clan_actuel, "famille": famille_actuelle, "profil": roles_actuels, 
                    "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
                    "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, 
                    "end_act": end_act, "sf_act": sf_act, "hon": hon, "glo": glo, "sta": sta, 
                    "armure_active": armure_active, "res_p": res_p, "res_s": res_s, 
                    "arme_active": arme_active, "w_deg": w_deg, "deux_mains": deux_mains, "w_dang": w_dang_base, "w_por": w_por, 
                    "t_kat": t_kat, "t_kih": t_kih, "t_inv": t_inv, "t_rit": t_rit, "t_shu": t_shu, "t_mah": t_mah, "t_nin": t_nin, "t_invs": t_invs, 
                    "sh_anneaux": sh_anneaux, "sh_vitalite": sh_vitalite, "sh_social": sh_social, "sh_equipement": sh_equipement,
                    "inventaire_armes": liste_armes_possedees, "inventaire_armures": liste_armures_possedees,
                    "c_est": c_est, "c_com": c_com, "c_sty": c_sty, "c_for": c_for, "c_cac": c_cac, "c_dis": c_dis, "c_chu": c_chu, "c_med": c_med, 
                    "c_cul": c_cul, "c_gou": c_gou, "c_mdc": c_mdc, "c_sen": c_sen, "c_the": c_the, "c_cmd": c_cmd, "c_crt": c_crt, "c_jeu": c_jeu, 
                    "c_rep": c_rep, "c_cmr": c_cmr, "c_tra": c_tra, "c_nav": c_nav, "c_mag": c_mag, "c_sur": c_sur
                }
                sauver_fiche(nom_id, maj)
                st.success("Fiche synchronisée chez l'Hôte !"); st.rerun()

        st.markdown("---")
        st.subheader("📢 Lancer une Action / Technique au MJ")
        c_a1, c_a2 = st.columns(2)
        comp_c = c_a1.text_input("Compétence ciblée (ex: Méditation) :")
        elem_c = c_a2.selectbox("Élément combiné :", ["Air 💨", "Terre 🏔️", "Feu 🔥", "Eau 💧", "Vide 🌌"])
        desc_a = st.text_area("Description de l'action / Technique activée (ex: Je frappe avec mon Wakizashi) :")
        if st.button("⚡ Soumettre cette action au MJ"):
            if comp_c and nom_perso:
                notifier_mj(nom_id, nom_perso, comp_c, elem_c, desc_a, {"air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide})
                st.success("Action envoyée sur le panneau tactique du MJ.")

# ==================== VUE MJ ====================
elif role == "Maître du Jeu (Hôte)":
    st.header("👁️ Panneau Tactique de l'Hôte")
    fichiers = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    if not fichiers:
        st.info("Aucun samouraï n'a partagé de données.")
    else:
        for f in fichiers:
            with open(os.path.join(DB_DIR, f), "r", encoding="utf-8") as file: p = json.load(file)
            nom_j = f.replace('.json', '').capitalize()
            av, tv, fv, ev = p.get('air', 1), p.get('terre', 1), p.get('feu', 1), p.get('eau', 1)
            em, sm, at, vi = (tv + fv) * 2, (tv + ev) * 2, av + fv, (av + ev) / 2
            ep, sp = em - p.get('end_act', em), sm - p.get('sf_act', sm)
            
            # Gestion de l'affichage des rôles sous forme de liste propre
            roles_bruts = p.get('profil', ['Bushi'])
            roles_txt = ", ".join(roles_bruts) if isinstance(roles_bruts, list) else roles_bruts
            
            titre_cadre = f"🏯 {nom_j} : {p.get('famille','Inconnu')} {p.get('perso','Inconnu')} (Clan {p.get('clan','Inconnu')}) — [{roles_txt}] | Posture : {p.get('posture','Air')}"
            
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
                        st.write(f"💥 Dégâts: {p.get('w_deg','3')} | Dangerosité: **{df}** | 📏 Portée: {p.get('w_por','0 - 1')}")
                        st.write(f"👘 Armure: {p.get('armure_active','Aucune')} (P: {p.get('res_p',1)}/S: {p.get('res_s',0)})")
                    else: st.caption("🔒 Masqué par le joueur")

        st.markdown("---")
        st.subheader("🔔 Boîte de réception des Actions Soumises")
        if os.path.exists(ACTIONS_FILE):
            try:
