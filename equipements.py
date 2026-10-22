CATALOGUE_ARMURES = {
    "Armure de Tenue de Cérémonie": {"res_p": 1, "res_s": 0, "proprietes": "Cérémonielle, Magnifique"},
    "Armure de Cuir Bouilli": {"res_p": 2, "res_s": 0, "proprietes": "Pratique"},
    "Armure de Plaques Lourde": {"res_p": 4, "res_s": 0, "proprietes": "Encombrante, En acier"}
}

CATALOGUE_ARMES_AVANCE = {
    "Wakizashi": {
        "competence": "Martiales (Corps-à-corps)", "portee": "0 - 1", "degats": 3, "danger": 5, "rareté": 4,
        "prise_autorisee": "1 main ou 2 mains", "effet_2_mains": {"danger": 2, "degats": 0, "portee": 0, "texte": "+2 Dangerosité"},
        "proprietes": "Acérée, Cérémoniale"
    },
    "Katana": {
        "competence": "Martiales (Corps-à-corps)", "portee": "1", "degats": 4, "danger": 5, "rareté": 5,
        "prise_autorisee": "1 main ou 2 mains", "effet_2_mains": {"danger": 0, "degats": 1, "portee": 0, "texte": "+1 Dégât"},
        "proprietes": "Acérée, Cérémoniale"
    },
    "Yari (Lance)": {
        "competence": "Martiales (Corps-à-corps)", "portee": "2", "degats": 4, "danger": 6, "rareté": 3,
        "prise_autorisee": "2 mains uniquement", "effet_2_mains": {"danger": 0, "degats": 0, "portee": 0, "texte": "Aucun (Prise fixe)"},
        "proprietes": "Allonge, Solide"
    },
    "Yumi (Arc)": {
        "competence": "Martiales (Distance)", "portee": "2 - 5", "degats": 5, "danger": 3, "rareté": 3,
        "prise_autorisee": "2 mains uniquement", "effet_2_mains": {"danger": 0, "degats": 0, "portee": 0, "texte": "Aucun (Prise fixe)"},
        "proprietes": "Encombrante, Militaire"
    }
}
