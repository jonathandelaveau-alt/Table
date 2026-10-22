import json
import os
import time
import streamlit as st

# =====================================================================
# 📂 1. CONFIGURATION DU DOSSIER DE STOCKAGE & DESIGN SOMBRE
# =====================================================================
DB_DIR = "sauvegardes_l5a"
if not os.path.exists(DB_DIR): 
    os.makedirs(DB_DIR)
ACTIONS_FILE = "notifications_mj.json"

st.set_page_config(page_title="L5A - Table Tactique Évoluée", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    h1, h2, h3, h4 { color: #f1c40f !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #8b0000 !important; color: white !important; font-weight: bold; border: 1px solid #ff4500 !important; }
    [data-testid="stSidebar"] { background-color: #181818 !important; border-right: 1px solid #2b2b2b; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 📜 2. IMPORTATION LOGIQUE DES BASES DE DONNÉES DÉPORTÉES
# =====================================================================
from equipements import CATALOGUE_ARMURES, CATALOGUE_ARMES_AVANCE, CATALOGUE_DIVERS
from techniques import CATALOGUE_COMPLET, DESCRIPTIONS_LORE
from etats_blessures import CATALOGUE_ETATS_BLESSURES
from ecoles import CATALOGUE_ECOLES

# Récupération automatique pour les listes
CATALOGUE_KATAS = CATALOGUE_COMPLET.get("Katas", {})
CATALOGUE_KIHOS = CATALOGUE_COMPLET.get("Kihos", {})
CATALOGUE_INVOCATIONS = CATALOGUE_COMPLET.get("Invocations", {})
CATALOGUE_RITUELS = CATALOGUE_COMPLET.get("Rituels", {})
CATALOGUE_SHUJIS = CATALOGUE_COMPLET.get("Shujis", {})
CATALOGUE_INVERSIONS = CATALOGUE_COMPLET.get("Inversions", {})

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
