import streamlit as st
import json
import os

# 1. Configuration et Design Sombre L5A (Obligatoire tout en haut)
st.set_page_config(page_title="L5A - Table Tactique", layout="wide")
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
    st.header("👤 Votre Feuille Secrète")
    nom_id = st.text_input("Prénom (Identifiant de session) :").strip()
    if nom_id:
        f = charger_fiche(nom_id) or {}
        with st.form("form_l5a"):
            st.subheader("📝 État-Civil")
            c1, c2, c3, c4 = st.columns(4)
            nom_perso = c1.text_input("Nom du Personnage :", value=f.get("perso", ""))
            clan = c2.selectbox("Clan :", list(DATA_CLANS.keys()), index=list(DATA_CLANS.keys()).index(f.get("clan", "Grue")) if f.get("clan") in DATA_CLANS else 1)
            famille = c3.selectbox("Famille :", DATA_CLANS[clan], index=DATA_CLANS[clan].index(f.get("famille")) if f.get("famille") in DATA_CLANS[clan] else 0)
            profil = c4.selectbox("Rôle :", ROLES_LISTE, index=ROLES_LISTE.index(f.get("profil", "Bushi")) if f.get("profil") in ROLES_LISTE else 0)
            
            ecole = st.text_input("Nom de l'École :", value=f.get("ecole", ""))
            rang_ecole = st.number_input("Rang d'École (1 à 6) :", 1, 6, value=f.get("rang_ecole", 1))
            posture = st.selectbox("Posture Active :", ["Air", "Terre", "Feu", "Eau", "Vide"], index=["Air", "Terre", "Feu", "Eau", "Vide"].index(f.get("posture", "Air")))

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
            sh_vitalite = st.checkbox("👁️ Partager mes jauges (Endurance/Sang-froid) avec le MJ", value=f.get("sh_vitalite", True))
            cv1, cv2 = st.columns(2)
            end_act = cv1.number_input(f"Endurance Actuelle (Max: {end_m}) :", 0, end_m, value=min(f.get("end_act", end_m), end_m))
            sf_act = cv2.number_input(f"Sang-froid Actuel (Max: {sf_m}) :", 0, sf_m, value=min(f.get("sf_act", sf_m), sf_m))

            st.subheader("⚖️ Caractéristiques Sociales (0 à 100)")
            sh_social = st.checkbox("👁️ Partager mon Honneur / Gloire / Statut avec le MJ", value=f.get("sh_social", True))
            cs1, cs2, cs3 = st.columns(3)
            hon = cs1.slider("Honneur", 0, 100, value=f.get("hon", 50))
            glo = cs2.slider("Gloire", 0, 100, value=f.get("glo", 50))
            sta = cs3.slider("Statut", 0, 100, value=f.get("sta", 50))

            st.subheader("🎭 Grille des 25 Compétences (Toujours masquées de base)")
            with st.expander("Éditer mes compétences de rang 0 à 6"):
                c_est, c_com, c_sty = st.slider("Esthétique", 0,6, f.get("c_est",0)), st.slider("Composition", 0,6, f.get("c_com",0)), st.slider("Stylisme", 0,6, f.get("c_sty",0))
                c_for, c_cac, c_dis = st.slider("Forme", 0,6, f.get("c_for",0)), st.slider("Corps-à-corps", 0,6, f.get("c_cac",0)), st.slider("Distance", 0,6, f.get("c_dis",0))
                c_chu, c_med, c_cul = st.slider("Corps Humain", 0,6, f.get("c_chu",0)), st.slider("Méditation", 0,6, f.get("c_med",0)), st.slider("Culture", 0,6, f.get("c_cul",0))
                c_gou, c_mdc, c_sen = st.slider("Gouvernement", 0,6, f.get("c_gou",0)), st.slider("Médecine", 0,6, f.get("c_mdc",0)), st.slider("Sentiment", 0,6, f.get("c_sen",0))
                c_the, c_cmd, c_crt = st.slider("Théologie", 0,6, f.get("c_the",0)), st.slider("Commandement", 0,6, f.get("c_cmd",0)), st.slider("Courtoisie", 0,6, f.get("c_crt",0))
                c_jeu, c_rep, c_cmr = st.slider("Jeu", 0,6, f.get("c_jeu",0)), st.slider("Représentation", 0,6, f.get("c_rep",0)), st.slider("Commerce", 0,6, f.get("c_cmr",0))
                c_tra, c_nav, c_mag = st.slider("Travail Manuel", 0,6, f.get("c_tra",0)), st.slider("Navigation", 0,6, f.get("c_nav",0)), st.slider("Magouille", 0,6, f.get("c_mag",0))
                c_sur = st.slider("Survie", 0,6, f.get("c_sur",0))

            st.subheader("🛡️ Arsenal (Équipement)")
            sh_equipement = st.checkbox("👁️ Partager mon Arme et mon Armure avec le MJ", value=f.get("sh_equipement", True))
            a_nom = st.text_input("Armure (Réf : Tenue Cérémonie) :", value=f.get("a_nom", "Armure de Tenue de Cérémonie"))
            res_p, res_s = st.number_input("Résistance Physique :", 0,10, int(f.get("res_p", 1))), st.number_input("Résistance Surnaturelle :", 0,10, int(f.get("res_s", 0)))
            st.caption("ℹ️ *Propriétés d'armure de référence : Cérémonielle, Magnifique.*")
            
            w_nom = st.text_input("Arme (Réf : Wakizashi) :", value=f.get("w_nom", "Wakizashi"))
            w_deg = st.number_input("Dégâts :", 0,10, int(f.get("w_deg", 3)))
            deux_mains = st.checkbox("Tenir l'arme à 2 mains ⚔️ (+2 Dangerosité)", value=f.get("deux_mains", False))
            w_dang = st.number_input("Dangerosité de base :", 0,10, int(f.get("w_dang", 5)))
            w_por = st.selectbox("Portée :", ["0 - 1", "1", "2", "3", "4", "5"], index=["0 - 1", "1", "2", "3", "4", "5"].index(f.get("w_por", "0 - 1")))
            st.caption("ℹ️ *Propriétés d'arme de référence : Acérée, Cérémoniale.*")

            st.subheader("📜 Grimoire des Techniques Apprises")
            with st.expander("Éditer mon catalogue de techniques secretes"):
                t_kat, t_kih, t_inv = st.text_area("Katas :", f.get("t_kat","")), st.text_area("Kihos :", f.get("t_kih","")), st.text_area("Invocations :", f.get("t_inv",""))
                t_rit, t_shu, t_mah = st.text_area("Rituels :", f.get("t_rit","")), st.text_area("Shujis :", f.get("t_shu","")), st.text_area("Maho :", f.get("t_mah",""))
                t_nin, t_invs = st.text_area("Ninjutsu :", f.get("t_nin","")), st.text_area("Inversions :", f.get("t_invs",""))

            if st.form_submit_button("💾 Sauvegarder ma Fiche"):
                maj = {
                    "perso": nom_perso, "clan": clan, "famille": famille, "profil": profil, "ecole": ecole, "rang_ecole": rang_ecole, "posture": posture,
                    "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide, "p_vide": p_vide, "end_act": end_act, "sf_act": sf_act,
                    "hon": hon, "glo": glo, "sta": sta, "a_nom": a_nom, "res_p": res_p, "res_s": res_s, "w_nom": w_nom, "w_deg": w_deg,
                    "deux_mains": deux_mains, "w_dang": w_dang, "w_por": w_por, "t_kat": t_kat, "t_kih": t_kih, "t_inv": t_inv, "t_rit": t_rit,
                    "t_shu": t_shu, "t_mah": t_mah, "t_nin": t_nin, "t_invs": t_invs, "sh_anneaux": sh_anneaux, "sh_vitalite": sh_vitalite,
                    "sh_social": sh_social, "sh_equipement": sh_equipement, "c_est": c_est, "c_com": c_com, "c_sty": c_sty, "c_for": c_for,
                    "c_cac": c_cac, "c_dis": c_dis, "c_chu": c_chu, "c_med": c_med, "c_cul": c_cul, "c_gou": c_gou, "c_mdc": c_mdc, "c_sen": c_sen,
        st.markdown("---")
        st.subheader("📢 Lancer une Action / Technique au MJ")
        c_a1, c_a2 = st.columns(2)
        comp_c = c_a1.text_input("Compétence ciblée (ex: Méditation) :")
        elem_c = c_a2.selectbox("Élément combiné :", ["Air 💨", "Terre 🏔️", "Feu 🔥", "Eau 💧", "Vide 🌌"])
        desc_a = st.text_area("Description de l'action / Technique activée (ex: Kata - Frappe du Tonnerre) :")
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
            
            with st.expander(f"🏯 {nom_j} : {p.get('perso','Inconnu')} | Posture : {p.get('posture','Air')} (Rang {p.get('rang_ecole',1)})", expanded=True):
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
                        st.write(f"🗡️ Arme : **{p.get('w_nom','Aucune')}** ({'2 mains ⚔️' if p.get('deux_mains',False) else '1 main'})")
                        st.write(f"💥 Dégâts: {p.get('w_deg','3')} | Danger: **{df}** | 📏 Portée: {p.get('w_por','0 - 1')}")
                        st.write(f"👘 Armure: {p.get('a_nom','Aucune')} (P: {p.get('res_p',1)}/S: {p.get('res_s',0)})")
                    else: st.caption("🔒 Masqué par le joueur")

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
                    cola, colb = st.columns()
                    with cola:
                        st.warning(f"⚔️ **{act['joueur']}** ({act['perso']}) veut agir !")
                        st.write(f"🔹 **Jet :** Compétence **[{act['competence']}]** + Élément **[{act['element']}]**")
                        aj = act.get("anneaux", {})
                        st.caption(f"📈 *Anneaux du joueur :* Air: {aj.get('air',1)} | Terre: {aj.get('terre',1)} | Feu: {aj.get('feu',1)} | Eau: {aj.get('eau',1)} | Vide: {aj.get('vide',1)}")
                        if act['description']: st.info(f"📜 **Description / Technique :** {act['description']}")
                    if colb.button("Valider", key=f"btn_act_{act['id']}"):
                        for a in actions:
                            if a["id"] == act["id"]: a["statut"] = "Validé"
                        with open(ACTIONS_FILE, "w", encoding="utf-8") as file: json.dump(actions, file, indent=4, ensure_ascii=False)
                        st.success("Action validée !"); st.rerun()
        else: st.info("Aucune notification reçue.")
else: st.info("👈 Veuillez sélectionner votre accès dans le menu latéral gauche.")
