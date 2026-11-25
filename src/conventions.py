"""Conventions uniques du projet (docs/architecture.md, section 4).

Ces constantes sont des conventions d'indexation, pas des paramètres du modèle.
Elles évitent d'écrire « 0 » ou « 1 » sans sens dans le reste du code.
"""

# Indice du sexe dans tous les tableaux N[..., s, ...] : s in {0, 1} = (femmes, hommes).
SEX_F = 0
SEX_M = 1
SEX_LABELS = ("femmes", "hommes")
N_SEXES = 2

# Unités des fichiers Insee (conversion d'unité, pas des hypothèses) :
# les quotients de mortalité sont donnés « pour 100 000 », la fécondité « pour 10 000 ».
INSEE_MORTALITY_UNIT = 100_000.0
INSEE_FERTILITY_UNIT = 10_000.0
