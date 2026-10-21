import streamlit as st
import json
import os

# Configuration visuelle pour le MJ (Écran large pour tout voir)
st.set_page_config(page_title="L5A - Hôte de Table", layout="wide")

# Dossier local de stockage automatique
DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

ACTIONS_FILE = "notifications_mj.json"

# --- FONCTIONS DE SAUVEGARDE ET SYNCHRONISATION ---
def sauver_fiche(nom_joueur, data):
    filename = os.path.join(DB_DIR, f"{nom_joueur.lower().strip().replace(' ', '_')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def charger_fiche(nom_joueur):
    filename = os.path.join(DB_DIR, f"{nom_joueur.lower().strip().replace(' ', '_')}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def notifier_mj(nom_joueur, nom_perso, tech):
    actions = []
    if os.path.exists(ACTIONS_FILE):
        try:
            with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
                actions = json.load(f)
        except: 
            actions = []
    actions.append({"joueur": nom_joueur, "perso": nom_perso, "technique": tech, "statut": "En attente"})
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=4, ensure_ascii=False)

# --- CORPS DE L'APPLICATION ---
st.title("⛩️ L'Empire d'Émeraude - Gestionnaire de Table L5A")

# Choix du rôle dans la barre latérale
role = st.sidebar.radio("🔑 Qui êtes-vous ?", ["Visiteur", "Joueur (Accès Secret)", "Maître du Jeu (Hôte)"])

# ==============================================================================
# VUE : JOUEUR (Écran 100% étanche - Ne voit que sa propre fiche)
# ==============================================================================
if role == "Joueur (Accès Secret)":
    st.header("👤 Votre Parchemin de Personnage")
    nom_identifiant = st.text_input("Entrez votre prénom (Sert de clé de connexion) :").strip()
    
    if nom_identifiant:
        fiche_chargee = charger_fiche(nom_identifiant)
        if fiche_chargee:
            st.success(f"🏯 Ravis de vous revoir, {nom_identifiant}. Vos données sont chargées.")
            data = fiche_chargee
        else:
            st.info("🆕 Aucun personnage trouvé à ce nom. Remplissez les champs pour créer votre héros.")
            data = {
                "perso": "", "air": 1, "terre": 1, "feu": 1, "eau": 1, "vide": 1,
                "vigi": 1, "attn": 1, "end_max": 10, "end_act": 10, "sf_max": 10, "sf_act": 10,
                "arme": "Aucune", "degats": "-", "armure": "Aucune", "res": "-", "secret_techniques": ""
            }
            
        with st.form("form_personnage"):
            st.subheader("📝 Identité & Concept")
            nom_perso = st.text_input("Nom du Personnage (ex: Doji Hotaru) :", value=data["perso"])
            
            st.subheader("🌀 Les Cinq Anneaux")
            c1, c2, c3, c4, c5 = st.columns(5)
            air = c1.number_input("Air 💨", 1, 5, value=data["air"])
            terre = c2.number_input("Terre 🏔️", 1, 5, value=data["terre"])
            feu = c3.number_input("Feu 🔥", 1, 5, value=data["feu"])
            eau = c4.number_input("Eau 💧", 1, 5, value=data["eau"])
            vide = c5.number_input("Vide 🌌", 1, 5, value=data["vide"])
            
            st.subheader("📊 Vigilance & Attention")
            c_v, c_a = st.columns(2)
            vigi = c_v.number_input("Vigilance 👀", 1, 5, value=data["vigi"])
            attn = c_a.number_input("Attention 🧠", 1, 5, value=data["attn"])
            
            st.subheader("🩸 Vitalité Dynamique")
            ce1, ce2, cs1, cs2 = st.columns(4)
            end_max = ce1.number_input("Endurance Max", 1, 40, value=data["end_max"])
            end_act = ce2.number_input("Endurance Actuelle", 0, end_max, value=data["end_act"])
            sf_max = cs1.number_input("Sang-froid Max", 1, 40, value=data["sf_max"])
            sf_act = cs2.number_input("Sang-froid Actuel", 0, sf_max, value=data["sf_act"])
            
            st.subheader("⚔️ Équipement de Combat")
            eq1, eq2, eq3, eq4 = st.columns(4)
            arme = eq1.text_input("Arme Prêtée / Équipée", value=data["arme"])
            degats = eq2.text_input("Dégâts de l'arme", value=data["degats"])
            armure = eq3.text_input("Armure Portée", value=data["armure"])
            res = eq4.text_input("Résistance d'Armure", value=data["res"])
            
            st.subheader("📜 Vos Techniques Secrètes (Cachées aux autres joueurs)")
            secret_tech = st.text_area("Vos capacités (Invisibles sur le tableau général)", value=data["secret_techniques"])
            
            if st.form_submit_button("💾 Sauvegarder mon Personnage"):
                maj_data = {
                    "perso": nom_perso, "air": air, "terre": terre, "feu": feu, "eau": eau, "vide": vide,
                    "vigi": vigi, "attn": attn, "end_max": end_max, "end_act": end_act, "sf_max": sf_max, "sf_act": sf_act,
                    "arme": arme, "degats": degats, "armure": armure, "res": res, "secret_techniques": secret_tech
                }
                sauver_fiche(nom_identifiant, maj_data)
                st.success("Fiche synchronisée chez l'Hôte !")
                st.rerun()

        # Notification Secrète
        st.markdown("---")
        st.subheader("📢 Proposer une action/technique au MJ")
        tech_nom = st.text_input("Nom de la technique secrète à soumettre :", placeholder="Ex: Frappe du Tonnerre d'Acier")
        if st.button("⚡ Envoyer secrètement au MJ"):
            if tech_nom and nom_perso:
                notifier_mj(nom_identifiant, nom_perso, tech_nom)
                st.success("Notification envoyée avec succès pour validation !")
            else:
                st.error("Remplissez votre nom de personnage et la technique d'abord.")

# ==============================================================================
# VUE : MAÎTRE DU JEU (L'Hôte qui contrôle tout)
# ==============================================================================
elif role == "Maître du Jeu (Hôte)":
    st.header("👁️ Panneau de Contrôle Central de l'Hôte")
    
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    fichiers = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    
    if not fichiers:
        st.info("En attente de connexion et de sauvegarde des joueurs...")
    else:
        st.subheader("📊 Tableau de bord en direct de la Table")
        
        for f in fichiers:
            with open(os.path.join(DB_DIR, f), "r", encoding="utf-8") as file:
                p = json.load(file)
                nom_j = f.replace('.json', '').capitalize()
                
                sf_perdu = p['sf_max'] - p['sf_act']
                end_perdu = p['end_max'] - p['end_act']
                
                # Interface épurée et sans bug pour l'affichage de chaque joueur
                with st.expander(f"🏯 **{nom_j}** joue **{p['perso']}** — ❤️ Endurance : {p['end_act']}/{p['end_max']} | 🧠 Sang-froid : {p['sf_act']}/{p['sf_max']}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown("**🌀 Anneaux**")
                        st.write(f"💨 Air : **{p['air']}** | 🏔️ Terre : **{p['terre']}**")
                        st.write(f"🔥 Feu : **{p['feu']}** | 💧 Eau : **{p['eau']}**")
                        st.write(f"🌌 Vide : **{p['vide']}**")
                    
                    with col2:
                        st.markdown("**🛡️ Caractéristiques**")
                        st.write(f"👀 Vigilance : **{p['vigi']}**")
                        st.write(f"🧠 Attention : **{p['attn']}**")
                        
                    with col3:
                        st.markdown("**⚔️ Arsenal Équipé**")
                        st.write(f"🗡️ **Arme :** {p['arme']} *(Dégâts : {p['degats']})*")
                        st.write(f"🛡️ **Armure :** {p['armure']} *(Résist : {p['res']})*")
                        
                    with col4:
                        st.markdown("**📉 États Actuels**")
                        if end_perdu > 0: 
                            st.error(f"Blessures : **-{end_perdu} PV**")
                        else: 
                            st.text("Frais physiquement")
                        
                        if sf_perdu > 0: 
                            st.warning(f"Sang-froid perdu : **-{sf_perdu}**")
                        else: 
                            st.text("Esprit calme")

        # --- RECEPTION DES ALERTES TECHNIQUES ---
        st.markdown("---")
        st.subheader("🔔 Boîte de réception des requêtes")
        
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as file:
                    actions = json.load(file)
            except: 
                actions = []
            
            actions_en_attente = [a for a in actions if a["statut"] == "En attente"]
            
            if not actions_en_attente:
                st.info("Aucune action en attente d'autorisation.")
            else:
                for idx, act in enumerate(actions_en_attente):
                    col_t1, col_t2 = st.columns([3, 1])
                    col_t1.warning(f"⚔️ **{act['joueur']}** ({act['perso']}) sollicite la technique : **{act['technique']}**")
                    
                    if col_t2.button("Autoriser", key=f"auth_{idx}"):
                        actions.remove(act)
                        with open(ACTIONS_FILE, "w", encoding="utf-8") as file:
                            json.dump(actions, file, indent=4, ensure_ascii=False)
                        st.success("Action validée !")
                        st.rerun()
        else:
