# Conventions du moteur démographique (phase 2)

Ce document consigne les choix de modélisation faits en codant le moteur, y compris ceux que le cahier des charges ne tranchait pas. Chacun est à valider ; aucun n'est une correction silencieuse.

## 1. Conventions d'indexation

| Objet | Convention |
|---|---|
| Sexe `s` | 0 = femmes, 1 = hommes (`src/conventions.py`, architecture §4) |
| Âge | âge **révolu au 1er janvier** ; classe ouverte A = 100 (100 ans et plus) |
| Population non segmentée | `n_pre[s, a]`, a = 0 à a0-1 |
| Population segmentée | `n[c, s, i]`, âge a0 + i, de a0 à A |
| Mortalité, fécondité, migrations de l'Insee | par **âge atteint dans l'année** ; l'âge révolu a au 1er janvier correspond à l'âge atteint a+1 |

## 2. Choix de calendrier et de calcul

1. **Naissances** : calculées sur les femmes présentes au 1er janvier t (cahier 3.7), avec le taux de l'âge atteint a+1 pour les femmes d'âge révolu a. Écart constaté avec l'Insee en 2026 : −0,40 % (l'Insee semble utiliser la moyenne des effectifs de début et de fin d'année : écart de +0,000 % avec cette variante). Écart documenté, non corrigé.
2. **Mortalité des nouveau-nés** : les naissances de l'année sont soumises au quotient de l'âge atteint 0 avant d'entrer dans la classe d'âge 0 au 1er janvier t+1 (c'est la définition du quotient de l'Insee).
3. **Solde migratoire de l'âge 0** : appliqué aux nouveau-nés, donc à l'étape « naissances » (la classe 0 est vide avant). C'est la seule entorse à la lettre du calendrier « mortalité → vieillissement → migrations → naissances » ; elle est inévitable puisque le solde de l'âge 0 de l'Insee est négatif (départs de nourrissons). **À valider.**
4. **Flux bruts** : la source ne donne que le solde par âge et sexe ; m+ = max(solde, 0), m- = max(-solde, 0). Le solde est préservé.
5. **Dépassement des départs** : politique `raise` (par défaut) : exception avec le détail ; politique `log_only` : alerte dans le journal, sans troncature (l'effectif peut devenir négatif et le test T2 l'attrape). Aucun dépassement n'a lieu avec les données de l'Insee.
6. **Quotient de la classe ouverte** : moyenne des quotients des âges 100 à 105+ pondérée par la population Insee du 1er janvier de l'année (pour « 105 ans ou plus » : quotient de l'âge atteint 106). Convention propre au modèle, à revoir en phase 3 (où la pondération devra venir du modèle lui-même).
7. **Mortalité identique pour toutes les catégories** (v0.1).

## 3. L'« ajustement » de la projection Insee

Le fichier `00_central.xlsx` contient, en plus des soldes migratoires, des onglets `ajustement`, `ajustementF` et `ajustementH` (par âge atteint et année ; 63 000 personnes en 2026, 16 000 en 2027, puis zéro à partir de 2028). Sans eux, l'écart sur la population de 2027 est de −0,09 % ; avec eux, −0,003 %. Le moteur les ajoute donc au solde migratoire (`demography.insee_adjustment_included: true`, statut `documented_hypothesis`). **Sa nature exacte n'est pas documentée dans le fichier : à confirmer dans la documentation de l'Insee.**

## 4. Champ géographique

La population « France » de POP3 est identique à celle de la projection et, d'après les notes du fichier, **inclut Mayotte à partir de 2014**. Le plan supposait « France hors Mayotte » : à corriger dans `docs/donnees.md` et `docs/plan-de-validation.md`. La décision D4 (Mayotte exclue) concerne les régimes de retraite, pas la démographie.

## 5. Modifications de l'architecture

| Date | Modification | Raison |
|---|---|---|
| 25/11/2026 | `src/io/` devient `src/data_io/` | Un paquet nommé `io` masque le module standard `io` : `from io.insee import ...` échoue. |
| 25/11/2026 | Les tests qui lisent `data/raw/` sont ignorés si les fichiers sont absents | GitHub Actions n'a pas accès à `data/raw/` (non versionné). |
| 25/11/2026 | `requirements.txt` : `matplotlib` n'apparaît qu'une fois | Deux lignes `matplotlib` provoquent « Double requirement given » dans pip. |
