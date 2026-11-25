# Plan de validation de la phase 2 (moteur démographique)

Ce document définit, **avant** d'écrire le moteur, ce que « validé » veut dire. Il applique les sections 7.1, 7.3 et 7.4 du cahier des charges (révision 6). Les seuils ne sont pas assouplis pour faire passer un test : toute modification est motivée par écrit dans ce fichier, avec la date et la raison.

## 1. Deux tests de nature différente

| Test | Ce qu'il montre | Ce qu'il ne montre pas |
|---|---|---|
| **Test 1 : validation mécanique** (cas jouet à trois classes d'âge, calculé à la main) | Le code applique correctement les règles écrites dans le cahier | Que les règles sont réalistes |
| **Test 2 : reproduction de la projection Insee 2026** (scénario central, mêmes hypothèses) | Que l'implémentation retrouve une projection officielle construite avec les mêmes données | Que le modèle sait **prévoir** la démographie : se rapprocher d'une projection qui utilise les mêmes hypothèses n'est pas une validation prédictive |

## 2. Vérifications de comparabilité (avant le test 2)

À effectuer et à consigner avec la date, **avant** de lancer la comparaison :

1. **Population initiale** : le total de l'onglet 2026 de POP3 est comparé à celui du fichier de projection pour la même date. Valeur attendue : environ 69,082 millions, à vérifier à la lecture et non à reprendre de ce document.
2. **Champ géographique** : les deux fichiers portent sur la même zone (France hors Mayotte, à confirmer dans les notes des fichiers).
3. **Convention d'âge** : âge atteint dans l'année ou âge au 1er janvier. La même convention doit s'appliquer aux deux fichiers et au moteur.
4. **Âges extrêmes** : la projection descend à 105 ans et plus alors que le modèle a une classe ouverte à 100 ans et plus. L'agrégation 100-104 + 105+ vers 100+ est faite explicitement et testée.
5. **Mortalité** : la table de mortalité du fichier est lue pour les mêmes années que la projection (quotients par âge de 0 à 120).
6. **Naissances** : le calcul à partir des femmes présentes au 1er janvier (cahier, 3.7) est comparé à celui de l'Insee ; un écart de convention est documenté, pas corrigé par un ajustement.

Si une vérification échoue, le test 2 n'est pas lancé : on documente l'écart et on décide si la référence est comparable.

## 3. Tests démographiques (section 7.1 du cahier)

| Réf. | Test | Critère |
|---|---|---|
| T1 | Conservation des effectifs hors naissances, décès et migrations | Écart absolu $\leq 10^{-9}$ (`pytest.approx`) |
| T2 | Aucun effectif négatif | Minimum $\geq 0$ pour toutes les classes et toutes les années |
| T3 | Cohérence des transitions par âge, sexe et catégorie | Chaque classe $(c, a, s)$ de $t+1$ est issue de la classe $(c, a-1, s)$ de $t$ |
| T4 | Attribution des catégories à $a_0$ | $\sum_c N_{c,a_0,s,t} = N_{a_0,s,t}$ |
| T5 | Conservation de la somme des catégories | Pour $a \geq a_0$ : $\sum_c N_{c,a,s,t} = N_{a,s,t}$, migrants et population initiale compris |
| T6 | Ordre du calendrier annuel | Mortalité, vieillissement, migrations, naissances, dans cet ordre, partout |
| T7 | Classe ouverte (100 ans et plus) | Reçoit les survivants des classes 99 ans et 100 ans et plus, sans perte ni création hors mortalité et migrations |
| T8 | Part de retraités $\rho$ | Vaut 0 ou 1 ; à génération fixée, ne décroît jamais avec l'âge |
| T9 | Migrations : solde total | Solde du moteur égal à celui de la source (tolérance $10^{-9}$) |
| T10 | Migrations : départs | Aucun effectif négatif ; tout dépassement des départs sur l'effectif présent est **signalé** (journal), jamais tronqué silencieusement |
| T11 | Taux d'emploi | $0 \leq e \leq 1$ pour toutes les classes, sans plafonnement ; une violation fait échouer le test (utile dès la phase 3) |
| T12 | Parts $\pi_c$ | Somme égale à 1 ; valeurs dans les plages du fichier `docs/hypotheses.md` |

## 4. Cas jouet (test 1)

- Trois classes d'âge, deux ou trois années, une seule catégorie puis trois.
- Tous les paramètres sont marqués `toy_example` dans `config/assumptions.yaml` et ne servent jamais à un résultat présenté.
- Le résultat attendu est calculé **à la main** et écrit dans le test (effectifs, naissances, migrants, retraités, cotisants).
- Le test échoue si un seul chiffre diffère à $10^{-9}$ près.

## 5. Reproduction de la projection Insee (test 2)

Le moteur est alimenté avec **les mêmes hypothèses** que la projection (fécondité, mortalité, migration du scénario central) et la même population de départ.

| Grandeur | Seuil initial | Fréquence |
|---|---|---|
| Population totale | Erreur relative $\leq 1\,\%$ | Chaque année de l'horizon |
| 0-19 ans | Erreur relative $\leq 2\,\%$ | Chaque année |
| 20-59 ans | Erreur relative $\leq 2\,\%$ | Chaque année |
| 60 ans et plus | Erreur relative $\leq 2\,\%$ | Chaque année |

Les classes à faible effectif sont traitées explicitement (cahier, 7.3). Les écarts sont **documentés avec leur cause probable** (convention d'âge, arrondis, classe ouverte, naissances) avant toute décision. Les seuils ne sont figés qu'après les vérifications de la section 2.

## 6. Qualité logicielle et reproductibilité (section 7.4)

- Graine fixe avec `np.random.default_rng`.
- Aucun paramètre numérique dans le code : tout vient de `config/assumptions.yaml`.
- `requirements.txt` ; après installation, `pip freeze` est enregistré pour fixer les versions.
- Tests `pytest` ; flottants comparés avec `pytest.approx`.
- GitHub Actions lance les tests à chaque push dès la phase 2.
- Données brutes dans `data/raw/` : jamais modifiées, jamais versionnées.

## 7. Critère de fin de la phase 2

La phase est terminée lorsque :

1. tous les tests T1 à T12 applicables sont verts en local et dans GitHub Actions ;
2. le cas jouet est reproduit à $10^{-9}$ ;
3. les vérifications de la section 2 sont consignées ;
4. la reproduction de la projection Insee est dans les seuils, ou chaque écart est documenté et justifié ;
5. tout est commité, avec une ligne dans `LEARNING.md` par notion apprise.

## 8. Journal des modifications de seuils

| Date | Seuil | Ancienne valeur | Nouvelle valeur | Raison |
|---|---|---|---|---|
| — | — | — | — | Aucune modification à ce jour |
