# Vérifications de comparabilité avec la projection Insee 2026 (scénario central)

Date de l'exécution : 2026-11-25. Généré par `scripts/check_comparability.py`.

| N° | Vérification | Résultat | Détail |
|---|---|---|---|
| 1 | Population initiale | OK | POP3 (onglet 2026) : 69,081,996 ; projection (2026) : 69,081,996 ; écart maximal par sexe et âge : 0.0. |
| 2 | Champ géographique | OK | Notes du fichier de projection : « France métropolitaine jusqu'en 1994, France hors Mayotte de 1995 à 2013, France à partir de 2014. ». Le bloc retenu dans POP3 est « France » : même champ dans les deux fichiers, **Mayotte incluse** (et non « hors Mayotte » comme supposé dans le plan). La décision D4 exclut Mayotte pour les régimes de retraite, pas pour la démographie. |
| 3 | Convention d'âge | OK | Population projetée en 2027 aux âges 1 à 99 (âge révolu au 1er janvier, quotients « âge atteint » : l'âge révolu a au 1er janvier devient a+1) : écart relatif maximal 0.1021% avec l'Insee ; avec un décalage d'un an, l'écart serait 63.90%. POP3 et projection donnent les mêmes effectifs par âge révolu (vérification 1). |
| 4 | Âges extrêmes | OK | Agrégation 100 à 104 + 105 et plus vers 100 et plus : somme conservée (37,000 personnes en classe ouverte en 2026). Quotient de la classe ouverte (moyenne pondérée) : femmes 0.348, hommes 0.403. Convention : pour « 105 ans ou plus », quotient de l'âge atteint 106. |
| 5 | Mortalité | OK | Quotients par âge atteint de 0 à 120 ans, années 2026 à 2065 : 40 années, valeurs dans ]0 ; 1] (min 3.72e-05, max 0.613). |
| 6 | Naissances | OK | Insee 2026 : 630,843. Moteur (femmes présentes au 1er janvier, cahier 3.7) : 628,347 (-0.40%). Avec la moyenne des effectifs de début et de fin d'année (pratique apparente de l'Insee) : 630,846 (+0.000%). Écart de convention documenté, non corrigé par un ajustement. |

**Conclusion :** toutes les vérifications sont satisfaites : la comparaison (étape 10) peut être lancée.
