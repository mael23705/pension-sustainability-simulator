# Données du projet : fiches de provenance

Une fiche par jeu de données. Les fichiers bruts sont dans `data/raw/` (jamais modifiés, non versionnés dans Git). Chaque fiche permet de retrouver la source, la date et la licence, et de refaire le téléchargement.

---

## Fiche 1 : Population au 1er janvier 2026 (par sexe et âge)

| Champ | Contenu |
|---|---|
| Nom et organisme | POP3 – Population au 1er janvier par sexe et âge détaillé (en années révolues). Insee, « Données nationales – Population : état civil et estimations de population » (Insee Résultats) |
| URL de la page | https://www.insee.fr/fr/statistiques/8999013 |
| URL du fichier | https://www.insee.fr/fr/statistiques/fichier/8999013/3_Pop1janv_age.xlsx |
| Date de publication | 15/06/2026 |
| Date de téléchargement | 23/11/2026 (à corriger si le téléchargement a eu lieu un autre jour) |
| Millésime | Population au 1er janvier 2026, **estimation provisoire** (onglet `2026`). Source indiquée dans le fichier : « Insee, recensements et estimations de population » |
| Champ | Deux blocs de colonnes : **France métropolitaine** et **France**. Le fichier utilise « France hors Mayotte » jusqu'en 2013 et « France » à partir de 2014, ce qui indique que « France » inclut Mayotte (même formulation dans le fichier des projections, fiche 2) |
| Granularité | Sexe (Ensemble, Hommes, Femmes) × âge en années révolues : 106 lignes, de 0 à 104 ans puis une classe « 105 ou plus ». La colonne « Année de naissance » est aussi fournie (dernière ligne : « 1920 ou avant ») |
| Licence | Licence Ouverte 2.0 (Etalab), sauf mention contraire. Conditions : citer « Source : Insee », indiquer la date de dernière mise à jour des données (ici 15/06/2026) et ne pas altérer le sens des informations. Mentions légales : https://www.insee.fr/fr/information/2008466 (mises à jour le 13/04/2026) |
| Format | xlsx, 786 746 octets (768 Ko). Un onglet par année : 1901 à 1914 et 1920 à 2026 |
| Transformations prévues | Lire l'onglet `2026`, colonnes « France » (Hommes, Femmes). Nettoyer les espaces en fin de texte et convertir l'année de naissance en entier. Agréger les âges 100 à « 105 ou plus » en une classe ouverte 100+ (convention du cahier des charges). Produire une table (âge, sexe, effectif) dans `data/processed/` |
| Version du simulateur | v0.1 |

### Contrôles réalisés le 23/11/2026

- Total « France » : **69 081 996** (Hommes 33 551 197, Femmes 35 530 799), soit environ 69,08 millions, cohérent avec le total publié par l'Insee.
- Pour toutes les lignes, Ensemble = Hommes + Femmes.
- Total « France métropolitaine » : 66 792 845.

### Remarques et points à traiter

- **Données provisoires** : le fichier l'indique pour 2024, 2025 et 2026. Les valeurs peuvent être révisées lors des publications suivantes.
- **Classe ouverte** : la source s'arrête à « 105 ou plus », alors que le cahier des charges fixe la classe ouverte à 100+. Décision : agréger les âges 100 à 105+ dans la classe 100+ lors du chargement, et le documenter. Vérifié avec la fiche 2 : les projections utilisent aussi « 105+ ». Les quotients de mortalité sont en revanche fournis jusqu'à 120 ans : il faudra en déduire un quotient pour la classe ouverte 100+ (voir fiche 2).
- **Champ géographique** : choisir « France », comme les projections INSEE (vérifié : la population 2026 de la fiche 2 est identique, âge par âge et par sexe), et noter le choix dans `hypotheses.md`.
- **Types hétérogènes** : dans l'onglet, certaines années de naissance sont du texte et d'autres des nombres. À convertir au chargement.

---

## Fiche 2 : Projections de population 2026, scénario central

| Champ | Contenu |
|---|---|
| Nom et organisme | Projection de population 2026, France, **scénario central** (fichier `00_central.xlsx`). Insee, Insee Résultats « Projections de population 2026 pour la France » |
| URL de la page | https://www.insee.fr/fr/statistiques/8991068 |
| URL du fichier | Non relevée ; fichier `00_central.xlsx` téléchargé depuis la page ci-dessus |
| Date de publication | 08/06/2026 |
| Date de téléchargement | 23/11/2026 (à corriger si le téléchargement a eu lieu un autre jour) |
| Millésime et champ | Projections de population 2026, horizon 2070. Champ : France (note du fichier : France métropolitaine jusqu'en 1994, France hors Mayotte de 1995 à 2013, France à partir de 2014). Source indiquée : Insee, estimations de population jusqu'en 2023, projections de population 2026 à partir de 2024 |
| Granularité | Annuelle, de 1962 à 2070 (109 colonnes d'années), par âge et par sexe (ensemble, femmes, hommes). Âges 0 à 104 puis « 105+ ». Mortalité par âge de 0 à 120 ans |
| Licence | Licence Ouverte 2.0 (Etalab), comme la fiche 1 : citer « Source : Insee », indiquer la date de mise à jour (08/06/2026), ne pas altérer le sens des informations |
| Format | xlsx, 2 450 989 octets (2,45 Mo), 18 onglets |
| Transformations prévues | Extraire les âges 0 à 105+ de `populationF` et `populationH` ; extraire les quotients de mortalité de `hyp_mortaliteF` et `hyp_mortaliteH` ; extraire la fécondité de `hyp_fecondite` et les naissances de `naissance` ; extraire le solde migratoire de `solde_migratoire`. Ne garder que 2026 à 2070 pour le benchmark. Produire des tables au format long dans `data/processed/` |
| Version du simulateur | v0.1 (validation et hypothèses centrales) |

### Contenu des onglets utiles

| Onglet | Contenu |
|---|---|
| `lisezmoi` | Notice : hypothèses des quatre scénarios (centrale, basse, haute, de travail) et index des onglets |
| `population`, `populationF`, `populationH` | Population au 1er janvier par âge (0 à 104, 105+) et année ; blocs de synthèse sous le tableau (groupes d'âge, rapport de dépendance, évolution annuelle) |
| `deces`, `decesF`, `decesH` | Décès par âge atteint dans l'année et année |
| `hyp_mortaliteF`, `hyp_mortaliteH` | Quotients de mortalité pour 100 000 par âge atteint (0 à 120 ans), survie, espérances de vie à la naissance, à 60 ans et à 65 ans |
| `naissance` | Naissances par âge de la mère et année |
| `hyp_fecondite` | Taux de fécondité par âge de la mère (pour 10 000), indicateur conjoncturel de fécondité (ICF), âge moyen à l'accouchement |
| `solde_migratoire`, `hyp_soldemigF`, `hyp_soldemigH` | Solde migratoire par âge atteint et année, total en bas de tableau |
| `ajustement`, `ajustementF`, `ajustementH` | Ajustement par âge et année : terme de réconciliation de la population, non nul jusqu'en 2027 (voir remarques) |
| `desc finale` | Descendance finale par génération |

### Hypothèses du scénario central (lues dans `lisezmoi` et les onglets)

- **Fécondité** : ICF de 1,564 en 2025, puis 1,526 en 2026, 1,488 en 2027 et 1,45 à partir de 2028. Âge moyen à l'accouchement en hausse jusqu'à 33,0 ans en 2050, stable ensuite.
- **Espérance de vie à la naissance en 2070** : 89,5 ans pour les femmes, 86,7 ans pour les hommes.
- **Migrations** : solde de +150 000 par an à partir de 2026 (176 000 en 2025).
- **Autres scénarios** : fécondité basse 1,20 et haute 1,70 à partir de 2030 ; espérance de vie 2070 de 86,5 et 83,7 ans (basse), 92,5 et 89,7 ans (haute) ; migrations +70 000 et +230 000 par an. Le scénario « de travail » fige l'espérance de vie à son niveau de 2025 et annule le solde migratoire.

### Contrôles réalisés le 23/11/2026

- Population 2026, ensemble : **69 081 996**, identique à la fiche 1. Hommes 33 551 197 et femmes 35 530 799 : identiques aussi.
- Comparaison âge par âge et par sexe avec POP3 pour 2026 : **écart maximal de 0**.
- Population 2070 : 65 887 156 (environ 65,9 millions).
- Les totaux des onglets `population`, `populationF` et `populationH` sont cohérents entre eux pour 2026.

### Remarques et points à traiter

- **Convention d'âge de la mortalité** : les décès et les quotients sont donnés par « âge atteint dans l'année », alors que la population est donnée par âge au 1er janvier. Le fichier fournit une ligne « proportion de décès dans l'année avant la date anniversaire » (à partir de 2023). À traiter en phase 2 : définir comment appliquer ces quotients à la population par âge révolu au 1er janvier, et le documenter dans `hypotheses.md`.
- **Classe ouverte** : population arrêtée à « 105+ », mortalité jusqu'à 120 ans. Pour la classe ouverte 100+ du cahier, il faut construire un quotient moyen pondéré par les effectifs des âges 100 à 105+. À documenter.
- **Fécondité** : les taux sont par âge de la mère (de 16 à 50 ans dans l'onglet `hyp_fecondite`), à utiliser avec la population féminine pour calculer les naissances.
- **Migration** : le fichier donne un **solde** par âge, pas de flux bruts d'arrivées et de départs. Le cahier des charges prévoit alors la séparation en $m^{+} = \max(m, 0)$ et $m^{-} = \max(-m, 0)$, avec contrôle du solde total. Vérifié pour 2026 : 121 âges (0 à 120), somme égale à 150 000, **26 âges ont un solde négatif** (minimum −41 062, maximum +9 187). La règle du cahier s'applique donc réellement ; vérifier que les départs ne dépassent jamais l'effectif présent. Les âges 105 à 120 sont à agréger avec la classe ouverte.
- **Ajustement** : identité vérifiée dans le fichier : population(t+1) − population(t) = naissances(t) − décès(t) + solde migratoire(t) + ajustement(t), avec un écart nul pour 2025, 2026, 2027, 2028, 2035 et 2060. L'ajustement total vaut 60 000 en 2025, 63 000 en 2026, 16 000 en 2027, puis 0 à partir de 2028. Pour le test de reproduction INSEE (phase 2), le moteur doit intégrer les ajustements de 2026 et 2027 (environ 0,11 % de la population au total) ou documenter l'écart qu'ils créent.
- **Années observées et projetées** : population : estimations jusqu'en 2023, projections à partir de 2024. Mortalité, fécondité, migration et naissances : statistiques de l'état civil et estimations jusqu'en 2022, projections à partir de 2023 (données provisoires de 2019 à 2021 pour les naissances). Le test de reproduction part de la population observée de 2026.
- **Autres scénarios** : seuls le scénario central coïncide avec la population observée de 2026. Les variantes sont projetées dès 2024 et ne servent pas au benchmark.

---

## Fiche 3 : Mortalité (quotients par sexe et âge)

| Champ | Contenu |
|---|---|
| Source | Même fichier que la fiche 2 : `00_central.xlsx` (Insee, projections de population 2026). Onglets `hyp_mortaliteF` et `hyp_mortaliteH` (quotients) ; `deces`, `decesF`, `decesH` (décès) |
| Date de publication et licence | Identiques à la fiche 2 |
| Période | **1962 à 2022 : observé** (statistiques de l'état civil et estimations de population), soit 61 ans ; **2023 à 2070 : projeté** |
| Granularité | Quotients de mortalité pour 100 000, par sexe et par **âge atteint dans l'année**, de 0 à 120 ans. Le fichier donne aussi la survie et les espérances de vie à la naissance, à 60 ans et à 65 ans |
| Transformations prévues | Convertir l'âge atteint en âge révolu au 1er janvier ; construire un quotient pour la classe ouverte 100+ ; stocker en format long dans `data/processed/` |
| Version du simulateur | v0.1 (hypothèses centrales) ; la série historique 1962-2022 servira de base à la mortalité stochastique de la phase 5 |

**Remarques :** l'exigence « séries d'au moins 30 ans » est satisfaite par la série observée. La Human Mortality Database n'est pas nécessaire en v0.1 ; elle pourra servir de comparaison en phase 5.

---

## Fiche 4 : Fécondité et naissances

| Champ | Contenu |
|---|---|
| Source | Même fichier que la fiche 2. Onglets `hyp_fecondite` (taux par âge de la mère pour 10 000, indicateur conjoncturel de fécondité, âge moyen à l'accouchement), `naissance` (naissances par âge de la mère) et `desc finale` (descendance finale par génération) |
| Date de publication et licence | Identiques à la fiche 2 |
| Période | **1962 à 2022 : observé** ; **2023 à 2070 : projeté**. Données provisoires de 2019 à 2021 pour les naissances |
| Granularité | Taux par âge de la mère de 16 à 50 ans, annuels. Naissances totales de 2026 : 630 843 |
| Transformations prévues | Calculer les naissances à partir des taux par âge et de la population féminine ; contrôler le résultat avec l'onglet `naissance` |
| Version du simulateur | v0.1 |

**Remarques :** l'onglet `hyp_fecondite` indexe l'âge par « âge atteint dans l'année », alors que l'onglet `naissance` utilise « âge au 1er janvier ». Cette différence de convention est à traiter en phase 2, comme celle de la mortalité.

---

## Fiche 5 : Migration (solde net par âge)

| Champ | Contenu |
|---|---|
| Source | Même fichier que la fiche 2. Onglets `solde_migratoire`, `hyp_soldemigF`, `hyp_soldemigH` |
| Date de publication et licence | Identiques à la fiche 2 |
| Période | **1962 à 2022 : observé** ; **2023 à 2070 : projeté**. Scénario central : +150 000 par an à partir de 2026 (176 000 en 2025) |
| Granularité | Solde par âge atteint dans l'année, de 0 à 120 ans, avec une ligne « Total » |
| Transformations prévues | Séparer arrivées et départs ($m^{+}$ et $m^{-}$) ; agréger les âges 105 à 120 avec la classe ouverte ; contrôler que la somme reste égale au total publié |
| Version du simulateur | v0.1 (solde central) ; flux bruts éventuels en v0.2 |

**Remarques :** le fichier ne contient **pas de flux bruts** (arrivées et départs séparés). Chercher en phase 1, dans les publications de l'Insee et d'Eurostat, si de tels flux existent à un niveau utilisable. Sinon, la règle $m^{+}$ / $m^{-}$ du cahier des charges s'applique au solde. En 2026, 26 âges ont un solde négatif.

---

## Fiche 6 : Emploi et chômage par sexe et tranche d'âge (brouillon)

| Champ | Contenu |
|---|---|
| Nom et organisme | Insee, enquêtes Emploi, séries longues sur le marché du travail : `marc-empl-nbr-taux-empl-sexe-age-2.xlsx` (figure 1 : nombre ; figure 2 : taux d'emploi) et `marc-cho-nbr-taux-sexe-age-2.xlsx` (figure 1 : nombre ; figure 2 : taux de chômage) |
| URL, licence | Site : https://www.insee.fr (rubrique « séries longues sur le marché du travail », enquêtes Emploi) ; page exacte et licence à relever |
| Date de publication | À compléter (données « révisées », dernière année 2025) |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Millésime et champ | 1975 à 2025 (51 années). Personnes vivant en logement ordinaire, 15 ans ou plus ; chômeurs au sens du BIT ; France (France hors Mayotte pour les taux d'emploi) |
| Granularité | Sexe (femmes, hommes, ensemble) × trois tranches d'âge : 15-24, 25-49, 50-64 ans (emploi) ; 15-24, 25-49, 50 ans ou plus (chômage) |
| Version du simulateur | v0.1 : taux d'emploi observé $e^{\text{obs}}$ et repère de chômage |

**Valeurs de contrôle (2025)**

| | Femmes | Hommes | Ensemble |
|---|---:|---:|---:|
| Emploi, 15-24 ans (milliers) | 1 245 | 1 502 | 2 748 |
| Emploi, 25-49 ans | 8 341 | 8 657 | 16 998 |
| Emploi, 50-64 ans | 4 487 | 4 553 | 9 040 |
| Emploi, 15-64 ans | 14 074 | 14 713 | 28 786 |
| Emploi, 15 ans ou plus | 14 343 | 15 040 | 29 383 |
| Taux d'emploi 15-24 ans (%) | 31,8 | 37,0 | 34,5 |
| Taux d'emploi 25-49 ans | 79,5 | 86,2 | 82,8 |
| Taux d'emploi 50-64 ans | 67,1 | 71,5 | 69,2 |
| Taux d'emploi 15-64 ans | 66,7 | 71,9 | 69,3 |
| Taux de chômage 15-24 ans (%) | 19,6 | 20,0 | 19,8 |
| Taux de chômage 25-49 ans | 7,1 | 6,8 | 6,9 |
| Taux de chômage 50 ans ou plus | 4,9 | 5,0 | 5,0 |
| Taux de chômage, ensemble | 7,6 | 7,8 | 7,7 |

### Taux d'emploi par âge individuel (enquête Emploi 2025, ajouté le 25/11/2026)

| Champ | Contenu |
|---|---|
| Nom et organisme | Insee, enquête Emploi, fichier annuel détaillé `DD_EEC_ANNUEL_2025_CSV_FR.zip` (données et métadonnées) |
| Date de téléchargement | 25/11/2026 (page, licence et date de publication à relever) |
| Millésime | 2025 |
| Champ | Non indiqué dans les métadonnées du fichier : à confirmer (la fiche 6 plus haut retient France hors Mayotte pour la série longue) |
| Mesures utilisées | `POP` (population, milliers), `PT_EMPSTA_IN_POP` (part du statut d'emploi dans la population totale, par âge), `EMPRATE` (taux d'emploi, seulement par tranches de 5 ans) |

**Méthode.** Le fichier ne donne le taux d'emploi que par tranches de 5 ans. La mesure `PT_EMPSTA_IN_POP` existe par âge individuel, mais elle est rapportée à la population des **deux sexes**. Le taux par sexe $s$ et âge $a$ s'obtient donc par :

$e^{\text{obs}}_{s,a} = \dfrac{\text{PT\_EMPSTA\_IN\_POP}_{s,a}}{\text{POP}_{s,a} / \text{POP}_{\text{ensemble},a}}$

Table dérivée : `data/processed/taux-emploi-age-sexe-2025.csv` (non versionnée ; colonnes `age`, `sexe`, `taux_emploi_pct`, `population_milliers`, `part_emploi_dans_pop_totale_pct`).

**Contrôle (25/11/2026).** En pondérant les taux individuels par la population, on retrouve les taux officiels `EMPRATE` des tranches de 5 ans à 0,1 point près : 50-54 ans (F 81,1 ; H 86,7), 55-59 ans (F 76,4 ; H 81,3), 60-64 ans (F 43,4 ; H 45,4) ; 25-29 ans : F 75,0 et H 79,8 contre 79,7 publié. Les taux de 15-64 ans du fichier (F 66,7 ; H 71,9 ; ensemble 69,3) sont identiques à ceux de la série longue plus haut.

**Valeurs autour de l'âge de départ (taux d'emploi, % de la population totale de l'âge, 2025).**

| Âge | 55 | 56 | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Femmes | 80,0 | 79,2 | 75,9 | 73,1 | 74,3 | 66,0 | 58,8 | 44,0 | 27,4 | 21,1 |
| Hommes | 85,1 | 83,5 | 82,8 | 81,4 | 73,5 | 68,2 | 58,6 | 43,2 | 30,4 | 23,8 |

Au-delà de 64 ans, seules des tranches existent (femmes ; hommes) : 65-69 ans (9,4 % ; 12,2 %), 70-74 ans (2,8 % ; 4,2 %), 75 ans ou plus (0,5 % ; 1,2 %).

**Limites.**
- Les taux par âge individuel sont des estimations d'enquête, donc bruitées. La part d'emploi est arrondie au dixième : l'erreur de conversion est d'environ 0,2 point.
- Ce sont des taux sur la **population totale** de l'âge, pas conditionnels aux non-retraités : la conversion $e = e^{\text{obs}}/(1-\rho)$ reste à faire avec $\rho$ (fiche 10).
- **Concept d'emploi décidé le 25/11/2026 (D6)** : comptabilité nationale pour le niveau (30,6 millions, COR) ; ces taux par âge fournissent le profil, mis à l'échelle par un facteur unique (environ 1,04) à calculer en phase 3.

### Limites et points à traiter

- **Tranches d'âge trop larges** : trois tranches pour un modèle par âge. La tranche 50-64 ans mélange les actifs de 50 à 61 ans et la zone de départ à la retraite (62 à 64 ans), précisément celle où $e$ varie le plus. Il faut une série par âge détaillé (âges quinquennaux ou individuels) pour calibrer $e_{c,a,s}$ ; ce fichier ne suffit qu'à contrôler les ordres de grandeur. **Levé pour 15-64 ans le 25/11/2026** par le fichier annuel détaillé (voir la sous-section ci-dessus).
- **Les 65 ans ou plus** ne sont pas détaillés : l'emploi à 65 ans et plus se déduit par différence (15 ans ou plus moins 15-64 ans : 269 000 femmes et 327 000 hommes en 2025). Le fichier annuel détaillé de 2025 donne les tranches 65-69, 70-74 et 75 ans ou plus (voir ci-dessus).
- **Taux d'emploi sur la population totale de la tranche** : le modèle utilise un taux conditionnel aux non-retraités, $e = e^{\text{obs}}/(1-\rho)$ ; la part de retraités par âge vient de la fiche 10.
- **Emploi du COR et emploi de l'enquête Emploi** : 29,4 millions (enquête, logement ordinaire, 2025) contre 30,6 millions (COR, comptabilité nationale, 2025). Les concepts diffèrent ; l'écart de 1,2 million (4 %) n'est pas expliqué ici. **Décision D6 (25/11/2026) : comptabilité nationale** pour le niveau, enquête Emploi pour le profil par âge.
- **Emploi n'est pas cotisation** : l'enquête compte les personnes en emploi, alors que les cotisants des fiches 7 incluent des situations (chômeurs indemnisés, stagiaires) et excluent certaines personnes en emploi (par exemple des régimes non couverts).
- **Chômage** : 7,7 % en 2025, contre 7,0 % pour la cible du COR à partir de 2040 et 7,9 % prévus par le Consensus pour 2026.

---

## Fiche 7 : Effectifs de retraités et de cotisants (brouillon, partielle)

| Champ | Contenu |
|---|---|
| Nom et organisme | Drees, enquête annuelle auprès des caisses de retraite (EACR), enrichie avec le modèle Ancetre : fichier `62_EACR_diffusée_Part_1 - version du 26 mai 2026.xlsx` (onglet `A-Cadrage`) et documentation `DocumentationEACR_mai2026.pdf` (version du 18 mai 2026). Complément : tableau « Cotisants, retraités et rapport démographique tous régimes » (`reve-protec-cotisant-retraite.xlsx`) |
| URL | Site : https://data.drees.solidarites-sante.gouv.fr (jeux de données de la Drees) ; pages exactes à relever |
| Date de publication | EACR : 26 mai 2026 (documentation du 18 mai 2026). Tableau cotisants-retraités : à compléter |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Millésime et champ | EACR : 2004 à 2024, stock au 31 décembre. Tableau cotisants-retraités : 2004 à 2023 ; cotisants = emploi intérieur ; retraités ayant perçu un droit direct, résidant en France ou à l'étranger, vivants au 31 décembre |
| Granularité | EACR : par régime (29 régimes dans `A-Cadrage`, plus la ligne « Tous régimes »), sexe, résidence (Ensemble ou France), type de droit (direct, dérivé). Tableau cotisants-retraités : totaux annuels uniquement |
| Licence | Licence Ouverte 2.0. Mention à afficher : « Source : Drees, enquête annuelle auprès des caisses de retraite (EACR), enrichie avec le modèle Ancetre » |
| Format | xlsx (EACR : 24 Mo, 6 onglets ; `A-Cadrage` : 21 210 lignes) |
| Version du simulateur | v0.1 |

### Contrôles réalisés le 25/11/2026

- **Tous régimes, retraités de droit direct, 2024** : 17 298 245 (résidence « Ensemble »), dont 16 429 118 résidant en France.
- **Cohérence avec le tableau cotisants-retraités** : 16 712 078 en 2019 et 16 974 753 en 2022 dans l'EACR, contre 16,712 et 16,975 millions dans le tableau ; en 2023, 17 184 263 contre 17,198 millions (écart d'environ 0,08 %).
- **Rapport démographique tous régimes** : 1,77 en 2023 (30,4236 millions de cotisants pour 17,198 millions de retraités) ; 1,72 en 2019 ; 2,02 en 2004. C'est une cible de contrôle pour la calibration de 2026.

### Limites et points à traiter

- **Double comptage entre régimes** : la somme des retraités de droit direct de tous les régimes vaut 39 789 942 en 2024, soit **2,3 fois** le total dédoublonné. Les polypensionnés sont comptés dans chaque régime. On ne peut donc pas obtenir les effectifs par catégorie en additionnant des régimes ; il faut utiliser la ligne « Tous régimes » pour le total et décider d'une règle d'attribution à une catégorie.
- **Fusion du régime général et de la SSI en 2020** (code 15) : les salariés du privé et les indépendants ne sont plus séparables pour le régime de base. Seuls les régimes complémentaires (Agirc-Arrco pour les salariés du privé, RCI pour les indépendants) permettent encore de les distinguer, avec des recouvrements.
- **Cotisants par catégorie : absents de l'EACR** (seul le total est donné). Trois sources complémentaires sont documentées ci-dessous ; elles n'ont ni le même champ ni la même définition, et aucune ne donne directement « privé / public / indépendants ».
- **Rattachement des régimes aux trois catégories** (proposition à valider, à documenter dans `hypotheses.md`) :

| Catégorie | Régimes (code) |
|---|---|
| Privé | Régime général (15), Agirc-Arrco (5600), MSA salariés (21) |
| Public | SRE civils (12), SRE militaires (13), CNRACL (32), FSPOEIE (33), Ircantec (1000), ERAFP (3000) |
| Indépendants | RCI (43), CNAVPL (2100, 2200), CNBF (2201, 2202), MSA exploitants (22, 23) |
| À décider | Régimes spéciaux (SNCF, RATP, CNIEG, ENIM, CANSSM, CRPCEN, Banque de France), Cavimac, Mayotte |

---

### Sources complémentaires pour les cotisants (téléchargées le 25/11/2026)

| Source | Référence | Date | Champ |
|---|---|---|---|
| MSA, « Compensation démographique 2024 » | `Compensation-demographique-2024.pdf`, tableau 1 | Synthèse de mars 2026 | Cotisants vieillesse 2024, **France métropolitaine**, par régime ; comprend les chômeurs, stagiaires et apprentis imputés au régime |
| DGAFP, « Chiffres clés de la fonction publique », édition 2026 | `cc-2026-web.pdf`, tableaux 2 et 6 | 2026 | Emplois principaux au 31/12/2024, **France hors Mayotte**, hors contrats aidés (Siasp, Insee) |
| COR, Rapport annuel de juin 2026 | `RA_2026_def_1.pdf`, partie 2, chapitre 2 (rapport cotisants/retraités, p. 72-73) | Juin 2026 | Emploi total en comptabilité nationale, tous régimes |

URL (communiquées par Maël ; licence non précisée sur les pages consultées) :

- MSA : https://statistiques.msa.fr/wp-content/uploads/2026/03/Compensation-demographique-2024.pdf
- DGAFP : https://www.fonction-publique.gouv.fr/files/files/publications/publications-dgafp/cc-2026-web.pdf
- COR (page du rapport, publié le 11 juin 2026) : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france

**Cotisants vieillesse 2024 (MSA, France métropolitaine)**

| Régime | Effectif | Part |
|---|---:|---:|
| Régime général | 24 925 614 | 72,7 % |
| Salariés agricoles (dont 766 966 actifs cotisants) | 815 093 | 2,4 % |
| Non-salariés agricoles | 412 121 | 1,2 % |
| Indépendants (SSI) | 2 880 146 | 8,4 % |
| Régimes spéciaux | 5 257 682 | 15,3 % |
| **Total** | **34 290 656** | 100 % |

**Fonction publique (DGAFP, 31/12/2024)** : 5 848 300 agents (FPE 2 581 900 dont 312 900 militaires ; FPT 2 017 800 ; FPH 1 248 600). Par statut : 3 745 800 fonctionnaires, 1 407 700 contractuels, 312 900 militaires, 381 900 « autres catégories et statuts ». Âge moyen 44 ans, 15 % ont moins de 30 ans, 38 % ont 50 ans ou plus, 64 % sont des femmes.

**COR** : emploi total de 30,6 millions en 2025 (28,9 millions en 2070) ; retraités de droit direct 17,4 millions en 2025 (22,1 millions en 2070), France et étranger.

**Ce qu'on peut et ne peut pas en tirer**

- Les « régimes spéciaux » de la MSA (5,26 millions) **ne sont pas le secteur public** : ils regroupent la fonction publique d'État et territoriale mais aussi SNCF, RATP, industries électriques et gazières, etc. À l'inverse, les contractuels du public (1,41 million) cotisent au régime général et à l'Ircantec.
- Le total de la MSA (34,3 millions, métropole, avec chômeurs et stagiaires) dépasse l'emploi du COR (30,6 millions, 2025) : les deux ne sont pas additionnables ni comparables sans retraitement.
- Les cotisants du régime des indépendants (SSI, 2,88 millions) incluent les micro-entrepreneurs, dont le revenu est souvent faible : un cotisant n'est pas un équivalent temps plein.
- **Ordre de grandeur, non retenu à ce stade** : public ≈ 5,85 millions (19 % de 30,6) ; indépendants ≈ 3,3 millions (SSI + non-salariés agricoles, hors professions libérales, dont l'effectif n'est pas dans les fichiers) soit environ 11 % ; privé par solde ≈ 21,5 millions (environ 70 %), borne haute. Ces parts sont à utiliser seulement comme repère pour les $\pi_c$, la règle d'attribution restant à décider.
- **Indépendants, source complémentaire (Insee Références, « Emploi et revenus des indépendants », édition 2025, base Non-salariés 2022)** : 4,4 millions d'indépendants fin 2022, dont 4,0 millions de non-salariés (3,6 millions hors agriculture, 0,4 million dans l'agriculture) et 0,3 million d'assimilés salariés (cotisant au régime général). Parmi les 3,6 millions hors agriculture : 1,77 million de micro-entrepreneurs (49 %) et 1,297 million de professions libérales. Champ : France hors Mayotte, activité non salariée à titre principal ou en complément d'une activité salariée (**pluriactifs inclus** : 31 % des micro-entrepreneurs et 9 % des non-salariés classiques cumulent avec un emploi salarié). Le chiffre est supérieur à celui de la MSA (SSI + non-salariés agricoles : 3,29 millions en 2024) ; l'écart d'environ 0,7 million correspond peut-être aux professions libérales (hypothèse non vérifiée). **Part des indépendants dans l'emploi : de 11 % (MSA) à 13 % (4,0 sur 30,6 millions, Insee)** selon la source, avec un risque de double comptage des pluriactifs.
- **Manquants** : l'effectif des professions libérales affiliées à la CNAVPL (non fourni) et l'année la plus récente (2022 pour les indépendants).
- **CNAVPL, effectif trouvé le 25/11/2026** : la fiche du COR « Les régimes de retraite des professions libérales » (projections de juin 2024, source CNAVPL) indique que les cotisants au régime de base sont passés de 625 000 en 2010 à 992 000 en 2023. La hausse vient surtout de l'affiliation à la CIPAV de micro-entrepreneurs ; la grande majorité d'entre eux relève désormais de la SSI, donc l'effectif devrait diminuer. Ce 992 000 est un effectif de cotisants à un régime : il n'est pas comparable au 1,297 million de professions libérales de l'Insee (autre champ et autre définition) et ne doit pas être additionné avec lui. **La règle d'attribution aux trois catégories reste à décider.**

---

## Fiche 8 : Salaires (brouillon, partielle : privé, fonction publique d'État et territoriale)

| Champ | Contenu |
|---|---|
| Nom et organisme | Insee, Base Tous salariés (BTS), « Salaires dans le secteur privé selon le sexe et l'âge » (`TAB_BTS_SEX_AGE_2024.xlsx`, jeu `DS_BTS_SAL_EQTP_SEX_AGE`) et « selon le sexe et la PCS » (`TAB_BTS_SEX_PCS_2024.xlsx`) |
| URL | Site : https://catalogue-donnees.insee.fr (catalogue Melodi de l'Insee) ; page exacte à relever |
| Date de publication | Fichiers créés le 30/07/2026 |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Millésime et champ | Années 2023 et 2024. France : salariés du privé, y compris alternants, stagiaires et contrats aidés, **hors agriculture et particuliers employeurs** |
| Granularité | Salaire **net** mensuel moyen en équivalent temps plein, en euros, par sexe et par tranche d'âge (moins de 25 ans, 25-39, 40-49, 50-54, 55 ans ou plus) ou par PCS (cadres y compris chefs d'entreprise, professions intermédiaires, employés, ouvriers). Onglet utile : `FRANCE` ; les autres onglets sont géographiques (`s` = secret statistique) |
| Licence | À confirmer sur la page du jeu de données (licence ouverte de l'Insee attendue) |
| Format | xlsx, 5,0 Mo (PCS) et 5,9 Mo (âge) |
| Version du simulateur | v0.1 pour la catégorie « privé » |

### Valeurs de contrôle (France, 2024, euros nets par mois)

- Ensemble : 2 733 € ; femmes 2 514 € ; hommes 2 891 €.
- Par âge (ensemble) : moins de 25 ans 1 622 ; 25-39 ans 2 547 ; 40-49 ans 3 007 ; 50-54 ans 3 174 ; 55 ans ou plus 3 266.
- Par PCS (ensemble) : cadres 4 629 ; professions intermédiaires 2 633 ; employés 1 941 ; ouvriers 2 051.

### Fonction publique (compléments téléchargés le 25/11/2026)

| Champ | Contenu |
|---|---|
| Nom et organisme | Insee Première n° 2100 (FPE) et n° 2101 (FPT), « Les salaires dans la fonction publique … en 2024 » : classeurs `IP2100.xlsx` et `IP2101.xlsx` (onglets « Figure 1 » à « Figure 5 » et « Tableaux complémentaires ») ; DGAFP, Chiffres clés 2026, tableau 16 |
| URL, licence | Insee Première n° 2100 (FPE) : https://www.insee.fr/fr/statistiques/8986474 ; n° 2101 (FPT) : https://www.insee.fr/fr/statistiques/8984823 (liens communiqués, non ouverts à la dernière vérification : erreur du serveur) ; DGAFP : voir la fiche 7. Licence à compléter |
| Millésime et champ | 2024 ; salaire mensuel **net** moyen en équivalent temps plein, France hors Mayotte, agents civils (hors militaires, apprentis, internes) ; en euros courants de 2024 |
| Version du simulateur | v0.1 pour la catégorie « public » |

**Valeurs de contrôle (2024, net mensuel EQTP, euros)**

| | FPE | FPT | Ensemble FP (DGAFP) | Privé (DGAFP) |
|---|---:|---:|---:|---:|
| Ensemble | 3 018 | 2 317 | 2 742 | 2 814 |
| Femmes | 2 870 | 2 248 | 2 638 | 2 585 |
| Hommes | 3 263 | 2 418 | 2 934 | 2 979 |
| Brut moyen | 3 736 | 2 851 | 3 382 | n.d. |
| Rapport brut/net | 1,238 | 1,230 | 1,233 | n.d. |

FPH (ensemble) : 2 896 net (femmes 2 757, hommes 3 407) d'après la DGAFP ; pas de détail par âge (Insee Première n° 2102 non fourni).

**Par tranche d'âge (net mensuel EQTP, part des effectifs en EQTP)**

| Âge | FPE | FPT |
|---|---:|---:|
| Moins de 30 ans | 2 138 (11 %) | 1 930 (9 %) |
| 30 à 39 ans | 2 606 (19 %) | 2 153 (18 %) |
| 40 à 49 ans | 3 033 (29 %) | 2 380 (26 %) |
| 50 à 59 ans | 3 375 (31 %) | 2 401 (34 %) |
| 60 ans ou plus | 3 657 (10 %) | 2 488 (12 %) |

Contrôle : la moyenne pondérée des tranches retrouve 3 022 € pour la FPE (publié : 3 018) et 2 318 € pour la FPT après renormalisation des parts (publié : 2 317).

### Compléments du 25/11/2026 : brut/net du privé et fonction publique hospitalière

**Rapport brut/net du privé.** Insee Première n° 2079 (octobre 2025, `insee.fr/fr/statistiques/8657156`) : en 2024, le salaire moyen en équivalent temps plein du privé est de **3 602 euros brut** et **2 733 euros net** par mois (même champ que le net de la fiche : France, privé hors agriculture et particuliers employeurs, alternants et stagiaires inclus). Le rapport brut/net vaut donc **1,318** (calcul : 3 602 / 2 733). Une édition plus récente existe (Insee Première n° 2132, données 2025 : 2 797 euros net en moyenne) : à examiner, car la calibration porte sur 2026 ; elle n'est pas retenue ici.

**Fonction publique hospitalière (FPH).** Insee Première n° 2102 (mai 2026, Insee et DREES, source Siasp), données `IP2102.xlsx` et PDF `ip2102.pdf` téléchargés le 25/11/2026. Salaire net moyen en équivalent temps plein, 2024 : **2 896 euros** par mois pour l'ensemble de la FPH (fonctionnaires : 3 314 euros brut et 2 691 euros net).

| Âge (figure 4, FPH, 2024) | Moins de 30 ans | 30-39 ans | 40-49 ans | 50-59 ans | 60 ans ou plus | Ensemble |
|---|---:|---:|---:|---:|---:|---:|
| Salaire net moyen (euros) | 2 274 | 2 851 | 2 925 | 2 994 | 3 789 | 2 896 |
| Part des effectifs en EQTP (%) | 14 | 25 | 26 | 27 | 7 | 100 |

Contrôle : le rapport brut/net des fonctionnaires de la FPH (3 314 / 2 691 = 1,2315, calcul) est cohérent avec le rapport de 1,23 retenu pour le public.

**Limites.**
- La FPH est donnée par âge **sans croisement avec le sexe** (le fichier donne le sexe séparément : 2 757 euros pour les femmes et 3 407 pour les hommes, tous âges, médecins inclus).
- La tranche « 60 ans ou plus » (7 % des effectifs) inclut les personnels médicaux : elle est tirée vers le haut et ne représente pas le salaire à l'âge de départ.
- La grille d'âge de la FPH (moins de 30, 30-39, 40-49, 50-59, 60 ou plus) diffère de celles du privé, du public d'État et territorial et des indépendants : **la grille commune reste à définir**.
- **Aucune source trouvée ne donne le salaire à 62-64 ans** (privé : tranche « 55 ans ou plus » ; public et FPH : « 60 ans ou plus »). Une hypothèse documentée sera nécessaire ; elle n'est pas décidée.

### Limites et points à traiter

- **Indépendants : source trouvée, mais avec un champ et une définition différents** (voir le bloc suivant).
- **Champ « privé » différent selon la source** : 2 814 € (DGAFP, hors apprentis, stagiaires, agricoles et particuliers employeurs) contre 2 733 € (BTS de la fiche 8, hors agriculture et particuliers employeurs, avec alternants et stagiaires). Pour comparer public et privé, utiliser un seul champ ; sinon documenter l'écart.
- **Public : seulement cinq tranches d'âge, sans croisement avec le sexe** : les salaires par âge et sexe de la v0.1 seront obtenus en combinant le profil par âge et l'écart par sexe (hypothèse d'indépendance à documenter).
- **Tranche « 60 ans ou plus »** : trop large pour lire le salaire à l'âge de départ (comme pour le privé).
### Indépendants (Insee Références, « Emploi et revenus des indépendants », édition 2025)

| Champ | Contenu |
|---|---|
| Nom et organisme | Insee, base Non-salariés 2022, PDF `ERI2025.pdf` (fiches 1.2, 1.6, 1.7) et classeur `ERI2025-F12.xlsx` (fiche 1.12 : professions libérales) |
| URL, licence | Site : https://www.insee.fr (collection Insee Références, « Emploi et revenus des indépendants », édition 2025) ; page exacte à relever ; reproduction partielle autorisée avec mention de la source (© Insee 2025) |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Millésime et champ | **2022** (année de référence de la plupart des statistiques) ; France hors Mayotte ; non-salariés hors agriculture ; revenu d'activité **net mensuel moyen**, un revenu déficitaire étant compté nul ; hors taxés d'office |
| Version du simulateur | v0.1 pour la catégorie « indépendants » |

**Valeurs de contrôle (2022, euros nets par mois, hors agriculture)**

| | Ensemble | Classiques | Micro-entrepreneurs |
|---|---:|---:|---:|
| Revenu moyen | 2 420 | 4 030 | 670 |
| Effectifs au 31/12 (milliers) | 3 615 | 1 850 | 1 766 |
| Femmes | 1 980 | 3 470 | 600 |
| Hommes | 2 720 | 4 360 | 720 |
| Professions libérales (1 297 000 personnes) | 3 870 | 5 790 | 870 |

Par tranche d'âge (ensemble des non-salariés hors agriculture) : moins de 30 ans 990 € (12,6 % des effectifs) ; 30 à 44 ans 2 220 € (37,7 %) ; 45 à 59 ans 3 000 € (35,7 %) ; 60 ans ou plus 2 590 € (14,0 %). Revenu médian des non-salariés classiques : 2 900 € ; 10,6 % ont un revenu nul ou déficitaire.

**Limites propres aux indépendants**

- **Revenu d'activité annuel ramené au mois**, avec revenus déficitaires comptés nuls : ce n'est pas un salaire en équivalent temps plein. Il n'est pas directement comparable aux salaires des privés et du public ci-dessus.
- **Un revenu moyen très dispersé** : micro-entrepreneurs 670 € contre 4 030 € pour les classiques. Le revenu moyen de la catégorie dépend donc fortement de la part de micro-entrepreneurs (49 % en 2022, 41 % en 2019), ce qui rend la catégorie instable dans le temps.
- **Année 2022**, en euros courants, alors que le public est de 2024 : à actualiser ou à documenter.
- **Tranches d'âge de l'Insee** (moins de 30, 30-44, 45-59, 60 ou plus) différentes de celles du public et du privé : une grille commune sera à définir.
- **Cotisations et pensions** : le revenu est net ; le lien avec l'assiette de cotisation des indépendants n'est pas établi.
- **Conversion brut-net** : seulement disponible pour le public (rapport d'environ 1,23, qui dépend du taux de primes et des cotisations des fonctionnaires). Rien d'équivalent trouvé pour le privé.
- **Salaire net** alors que le taux de liquidation $\theta_c$ est défini en brut : prévoir une conversion brut-net documentée, ou travailler en net des deux côtés.
- **Tranche « 55 ans ou plus »** : trop large pour lire « le salaire à l'âge de départ » (âges 62 à 64 ans environ). À traiter par une hypothèse ou une autre source.
- **Équivalent temps plein** : cohérent avec un salaire moyen par cotisant à temps plein, mais pas avec une masse salariale réelle (temps partiel). À documenter pour l'assiette $A_t$.
- **Pas de PCS en v0.1** : la PCS est réservée à la v0.2, ce fichier est conservé pour cette version.

---

## Fiche 10 : Pensions (stock et nouveaux liquidants) (brouillon, partielle)

| Champ | Contenu |
|---|---|
| Nom et organisme | Drees, EACR, onglet `C-Droits_directs` (ligne « Tous régimes », issue du modèle Ancetre), même fichier que la fiche 7 |
| Date de publication, licence, téléchargement | Identiques à la fiche 7 |
| Millésime et champ | Stock de retraités de droit direct au 31 décembre 2024 ; flux de nouveaux liquidants de 2024 (vivants au 31 décembre). Données jusqu'en **2024** seulement |
| Granularité | Sexe, âge au 31 décembre (âges individuels de 22 à 109 ans, plus des lignes « Ensemble » et « plus de 95 »), lieu de naissance, résidence ; effectifs, avantage principal moyen de droit direct (`m1`), pension totale moyenne (`mont`) |
| Version du simulateur | v0.1 |

### Valeurs de contrôle (tous régimes, 2024, résidence « Ensemble »)

- Stock : 17 298 245 retraités (ligne « Ensemble ») ; femmes 9 102 269, hommes 8 072 506 sur les âges individuels.
- Avantage principal moyen (`m1`) : 1 646,9 € par mois pour l'ensemble ; femmes 1 324 € et hommes 2 018 € en moyenne sur les âges individuels.
- Nouveaux liquidants de 2024 : 857 880 (ligne « Ensemble »), `m1` moyen 1 664,7 € par mois ; femmes 1 393 € (435 323 personnes), hommes 1 945 € (422 340 personnes).
- Âges de liquidation : pic à 62 ans (222 824 liquidants), puis 63 ans (159 442) et 67 ans (90 563).
- Âge conjoncturel de départ 2024 (onglet `A-Age_conjoncturel`) : Régime général 63,60 ans (femmes 63,70 ; hommes 63,50) ; Agirc-Arrco 63,43 ; SRE civils 63,18 ; CNRACL 62,46 ; ERAFP 63,47.

### Limites et points à traiter

- **Dernière année disponible : 2024**, alors que la calibration porte sur **2026**. Décision à prendre : faire avancer le stock de 2024 à 2026 (revalorisations des pensions, décès, nouvelles liquidations) ou fixer l'année de calibration à 2024. Les taux de revalorisation de 2025 et 2026 sont à relever à la source (non vérifiés). **Taux de 2025 relevé le 25/11/2026 : +2,2 %** (voir « Compléments du 25/11/2026 » plus bas).
- **Définition de `m1` (documentation EACR, table A)** : avantage principal moyen de **droit direct**, perçu en **décembre** (ni effectifs ni montants ne sont des moyennes annuelles ; effectifs × `m1` × 12 ne retrouve donc pas exactement les dépenses de l'année). Il **comprend** les minima de pension (minimum contributif, minimum garanti) ; il **exclut** le droit dérivé (`m2`), la majoration pour trois enfants, la majoration pour tierce personne, le minimum vieillesse et l'ASI. La variable `mont` inclut ces éléments. Les données portent seulement sur les prestations versées en rente (pas de versement forfaitaire unique). Ce qui reste à confirmer : si la ligne « Tous régimes » somme bien base et complémentaire pour un même retraité (elle provient du modèle Ancetre).
- **Conséquence pour $\theta_c$** : `m1` exclut la majoration pour trois enfants, ce qui sous-estime la pension effectivement versée ; la comparaison avec les taux de remplacement des cas types du COR (qui incluent pensions de base et complémentaires) doit en tenir compte.
- **Brut ou net** : la documentation ne le dit pas explicitement pour `m1`. Elle traite les prélèvements sociaux (CSG, CRDS, Casa, cotisation maladie) dans une table distincte (`A-Prelev_sociaux`), ce qui laisse penser que `m1` est **avant prélèvements** (donc brut), mais ce n'est pas confirmé. À vérifier auprès de la Drees ou dans la fiche 23 du panorama « Les retraités et les retraites » avant tout rapprochement avec les salaires nets des fiches 8.
- **Âge moyen de liquidation (`ageliq`)** : défini dans la table C comme l'âge moyen de liquidation, mais vide pour « Tous régimes ». On utilise la distribution des liquidants par âge (colonne `Age`, âge en fin d'année) ou l'âge conjoncturel de départ par régime. Attention : `Age` est l'âge en fin d'année, pas l'âge à la liquidation.
- **Écart de 123 445 personnes** (0,7 %) entre la somme des âges individuels (17 174 800) et la ligne « Ensemble » : non expliqué par la documentation. **Hypothèses non vérifiées** : (i) la ligne « Tous régimes » provient du modèle Ancetre et la table A est actualisée l'année suivante (principe de « double interrogation », variable `PlusRécent`) alors que la table C n'est cohérente avec la table A que pour la même édition ; (ii) la ligne « plus de 95 » ou des cellules masquées. À tester : comparer `PlusRécent` et recalculer la somme sans la ligne « plus de 95 ».
- **Âges extrêmes et aberrants** : des liquidants apparaissent à partir de 22 ans (anciens invalides de la fonction publique) ; la classe 100+ du cahier doit être construite en agrégeant les âges 100 à 109.
- **Revalorisations** : +0,9 % au 1er janvier 2026 pour les retraites de base (COR, juin 2026, partie 1, chapitre 2 ; LFSS 2026). Pour 2025, le taux n'apparaît pas dans les documents fournis : à relever à la source. Pour l'Agirc-Arrco, la valeur de service du point n'a **pas été revalorisée en 2025** (pas d'accord entre partenaires sociaux) ; en 2026 elle suit l'inflation hors tabac moins 0,4 point. **Mise à jour du 25/11/2026 : le taux de 2025 est relevé (+2,2 %, coefficient 1,022)** ; voir « Compléments du 25/11/2026 » plus bas.
- **Cas types du COR** : récupérés (tableau ci-dessous). Ils servent de contrôle de $\theta_c$, avec les réserves indiquées.

### Compléments du 25/11/2026 : revalorisation 2025 et panorama DREES 2026

**Revalorisation 2025 relevée.** Les pensions de retraite de base ont été revalorisées d'un coefficient de **1,022 au 1er janvier 2025, soit +2,2 %** (instruction interministérielle DSS/SD3A/DB/2024/176 du 13 décembre 2024, publiée sur `legislation.lassuranceretraite.fr`). Le Panorama DREES (édition 2025, fiche 4) confirme le taux de 2,2 % au 1er janvier 2025. Avec +0,9 % au 1er janvier 2026 (COR), le facteur indicatif pour faire avancer une pension de base de décembre 2024 à 2026 est 1,022 × 1,009 ≈ **1,031** (calcul). Il ne vaut que pour les pensions de base : la complémentaire Agirc-Arrco suit d'autres règles (non revalorisée en 2025, voir plus haut). L'inflation moyenne de 2025 est de +0,9 % (Insee Première n° 2132) : en euros constants, les pensions de base ont donc gagné environ 1,3 point en 2025 (1,022 / 1,009, calcul).

**Panorama DREES « Les retraités et les retraites », édition 2026 (PDF de 314 pages, téléchargé le 25/11/2026).**
- Pension moyenne de droit direct, fin 2024, retraités résidant en France : **1 752 euros brut** et **1 626 euros** après prélèvements sociaux par mois (rapport net/brut d'environ 0,93, calcul). **Cette pension est l'avantage principal de droit direct y compris la majoration pour trois enfants ou plus** (source : EIR et modèle ANCETRE). Elle n'est donc pas comparable au `m1` de l'EACR (1 646,9 euros), qui exclut la majoration d'après la documentation EACR.
- **Part de retraités par âge** (fiche 15 : proportion de personnes retraitées de droit direct parmi les personnes de cet âge résidant en France), fin 2024 : **9 % à 60 ans** (génération 1964), **19 % à 61 ans** (génération 1963), **48 % à 62 ans** (génération 1962). La série complète par âge de 50 à 70 ans est au graphique 3 de la fiche 15 ; seuls ces trois points sont relevés dans le texte. C'est la définition utile pour $\rho$.

**Panorama DREES 2026 : tableaux 3 et 4 (fin 2024, régime principal), utilisés comme contrôle (D14, ajouté le 25/11/2026).**

| Régime principal | Effectif (milliers) | Part | Pension brute mensuelle moyenne (euros, avec majoration, tous retraités de droit direct) |
|---|---|---|---|
| Régime général (inclut l'ex-SSI depuis 2020) | 12 130 | 70 % | 1 610 |
| FPE civils | 1 560 | 9 % | 2 570 |
| FPE militaires | 350 | 2 % | 2 260 |
| CNRACL | 1 110 | 6 % | 1 860 |
| Régimes spéciaux | 480 | 3 % | 2 740 |
| MSA salariés | 500 | 3 % | 1 720 |
| Autre régime de non-salarié | 820 | 5 % | 1 420 |
| Ensemble des retraités de droit direct | 17 300 | 100 % | 1 750 |

- Public (FPE civils, FPE militaires, CNRACL, régimes spéciaux) : 3 500 milliers sur 17 300, soit 20,2 % (calcul), proche de $\pi_{\text{public}} = 0{,}19$ (D2).
- Les effectifs de ce tableau sont arrondis aux dizaines de milliers et peuvent varier d'une année à l'autre (note du panorama).
- Ordre des pensions : public supérieur au régime général, lui-même supérieur aux non-salariés. Ce classement sert de contrôle de signe pour $\theta_c$ en phase 3.

### Taux de remplacement des cas types du COR (juin 2026)

Source : COR, Rapport annuel de juin 2026, partie 3, chapitre 3, tableau 3.3 (calculs Drees, modèle Trajectoire). Taux de remplacement **net**, pensions de base et complémentaires, scénario de référence ; génération 1964 sauf aide-soignant (1969), policier (1974) et médecin (1960). Le salaire de fin de carrière est exprimé en multiple du revenu moyen par tête (RMPT). URL : https://www.cor-retraites.fr/sites/default/files/2026-06/RA_Part3_Chap3.pdf.

| Cas type | Salaire de fin de carrière | Âge d'ouverture des droits | Taux de remplacement à cet âge |
|---|---|---:|---:|
| 1 Cadre | 2,51 × RMPT | 62,75 | 51,9 % |
| 2 Non-cadre | 0,74 × RMPT | 62,75 | 75,2 % |
| 3 Non-cadre avec chômage | 0,62 × RMPT | 62,75 | 66,7 % |
| 4 Femme, deux enfants | 0,62 × RMPT | 62,75 | 80,9 % |
| 5 Catégorie B sédentaire | 0,99 × RMPT (30 % de primes) | 62,75 | 58,3 % |
| 6 Catégorie A, faibles primes | 1,51 × RMPT (15 % de primes) | 62,75 | 62,3 % |
| 7 Catégorie A+, fortes primes | 2,31 × RMPT (44 % de primes) | 62,75 | 39,9 % |
| 8 Policier | 1,02 × RMPT (44 % de primes) | 52,75 | 40,4 % |
| 9 Aide-soignant | 0,83 × RMPT (25 % de primes) | 57,75 | 63,4 % |
| 10 Adjoint technique territorial | 0,79 × RMPT (20 % de primes) | 62,75 | 70,9 % |
| 11 Attaché territorial | 1,48 × RMPT (27 % de primes) | 62,75 | 60,1 % |
| 12 Exploitant agricole | 0,52 × RMPT | 62,75 | 78,3 % |
| 13 Médecin | 2,66 × RMPT | 62 | 44,9 % |

Les taux dépendent fortement du niveau de revenu (de 40 % à 81 %) : un $\theta_c$ unique par catégorie ne peut en être qu'une moyenne. Pour un départ à 67 ans (annulation de la décote), les taux vont de 51,9 % à 94,7 %.

**Réserves pour la comparaison avec $\theta_c$** : (i) les cas types sont des taux **nets** de carrière complète et de salaire de fin de carrière, alors que $\theta_c$ est un taux moyen sur des liquidants réels (carrières incomplètes incluses) ; (ii) génération 1964, alors que les liquidants de 2026 sont des générations 1960 à 1964 ; (iii) base et complémentaire sont incluses. On compare donc des ordres de grandeur, pas des valeurs.
- Les pensions de **droit dérivé** (réversion) sont hors périmètre de la v0.1, mais figurent dans l'onglet `D-Droits_dérivés`.

---

## Fiche 9 : Âge légal de départ et durée d'assurance par génération

| Champ | Contenu |
|---|---|
| Nom et organisme | COR, Rapport annuel de juin 2026, partie 1, chapitre 2, section 1.2 et tableau 1.4 (d'après la loi n° 2025-1403 de financement de la sécurité sociale pour 2026) |
| URL, licence | https://www.cor-retraites.fr/sites/default/files/2026-06/RA_Part1_Chap2.pdf (page du rapport : voir la fiche 7). Rapport publié le 11 juin 2026 ; licence non indiquée sur la page |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Champ | Salariés du privé, non-salariés et fonctionnaires sédentaires ; pensions liquidées à compter du **1er septembre 2026** |
| Version du simulateur | v0.1 : table $a^{\text{lég}}(g)$ du fichier de configuration |

**Âge d'ouverture des droits et durée d'assurance pour le taux plein, après suspension de la réforme de 2023**

| Génération | Âge d'ouverture des droits | Durée requise (trimestres) |
|---|---:|---:|
| 1960 | 62 ans | 167 |
| 1961 (1er janvier au 31 août) | 62 ans | 168 |
| 1961 (1er septembre au 31 décembre) | 62 ans et 3 mois | 169 |
| 1962 | 62 ans et 6 mois | 169 |
| 1963 | 62 ans et 9 mois | 170 |
| 1964 | 62 ans et 9 mois | 170 |
| 1965 (1er janvier au 31 mars) | 62 ans et 9 mois | 170 |
| 1965 (1er avril au 31 décembre) | 63 ans | 171 |
| 1966 | 63 ans et 3 mois | 172 |
| 1967 | 63 ans et 6 mois | 172 |
| 1968 | 63 ans et 9 mois | 172 |
| 1969 et suivantes | 64 ans | 172 |

La montée en charge de la réforme de 2023 est suspendue pour la génération 1964 et les assurés nés du 1er janvier au 31 mars 1965, puis reprend : 64 ans est atteint pour la génération 1969 (et non 1968), 172 trimestres pour la génération 1966 (et non 1965).

### Limites et points à traiter

- **Âges fractionnaires** (trimestres) alors que le modèle fonctionne en âges entiers : une convention est à choisir et à documenter (par exemple arrondir à l'entier supérieur, ou interpoler entre deux âges). Elle change l'âge effectif de départ de plusieurs générations (1961 à 1968).
- **Fonctionnaires de catégorie active** : règles distinctes (âge d'ouverture de 59 ans pour la génération 1974 après suspension, 172 trimestres pour la génération 1971). Hors v0.1, mais à signaler dans les limites.
- **Retraites anticipées** (carrière longue, incapacité) : hors périmètre v0.1 (cahier des charges, section 3.4) ; le tableau ci-dessus ne les couvre pas.
- **Âge de départ observé** supérieur à l'âge légal : le paramètre $\delta_{c,s}$ est calibré sur l'écart entre l'âge conjoncturel de départ (fiche 10) et l'âge légal de la génération concernée.
- **Règles d'indexation** : l'article du code de la sécurité sociale fondant l'indexation des pensions de base sur les prix n'a pas été relu à la source (Légifrance) ; seul le principe figure dans le rapport du COR. À vérifier.

---

## Fiche 11 : Hypothèses macroéconomiques (brouillon, partielle)

| Champ | Contenu |
|---|---|
| Nom et organisme | COR, Rapport annuel de juin 2026 (hypothèses de la partie 1, chapitre 1, section 3, p. 43-45) ; trajectoire 2026-2029 du Rapport d'avancement annuel d'avril 2026 |
| URL, licence | Page du rapport : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france (publié le 11 juin 2026). Le chapitre sur les taux de cotisation (https://www.cor-retraites.fr/sites/default/files/2026-06/RA_Part3_Chap1.pdf) n'a pas encore été lu. Guide sur les bons du Trésor : URL à identifier |
| Date de téléchargement | 25/11/2026 (à corriger si besoin) |
| Version du simulateur | v0.1 : repères pour calibrer les distributions du Monte-Carlo (phase 5), pas valeurs centrales du simulateur |

**Scénario de référence du COR**

- Démographie : hypothèses centrales de l'Insee (gains d'espérance de vie, fécondité de 1,45 enfant par femme à partir de 2028, solde migratoire net de 150 000 personnes par an).
- Croissance de la productivité horaire du travail : 0,7 % par an à partir de 2040. Variantes : 0,4 % et 1,0 %.
- Taux de chômage : 7,0 % à partir de 2040. Variantes : 5,0 % et 10,0 %.
- Croissance du PIB : 0,9 % en 2026, 1,0 % en 2027, 1,2 % en 2028 et en 2029 (révisée à la baisse en avril 2026).
- Inflation (prévision du gouvernement, utilisée pour la revalorisation des pensions) : 1,9 % en 2026, 1,6 % en 2027 ; Consensus Forecasts de mai 2026 : 2,0 % et 1,7 %.
- Chômage prévu par le Consensus : 7,9 % en 2026 et 2027.
- La rémunération horaire évolue comme la productivité horaire si le partage de la valeur ajoutée et la durée du travail sont stables.

### Limites et points à traiter

- **Cohérence avec la démographie des fiches 2 à 5** : le COR retient une fécondité de 1,45 à partir de 2028 ; à comparer à l'hypothèse lue dans `hyp_fecondite` de l'Insee avant de supposer qu'elles coïncident.
- **Croissance réelle des salaires** : le repère du COR est 0,7 % par an à long terme. Toute valeur provisoire nettement supérieure (par exemple 2 %) devra être justifiée ou remplacée.
- **Rendement des réserves (repère de marché, source secondaire)** : le fichier fourni est un guide pédagogique grand public (« Les bons du Trésor », vérifié le 7 novembre 2026, auteur et URL à identifier) qui reprend les communiqués de l'Agence France Trésor. **À recouper avec les communiqués de l'AFT avant tout usage dans `config/assumptions.yaml`.** Taux nominaux moyens pondérés des adjudications : BTF à 12 mois 3,352 % (2 novembre 2026) ; OAT 2,40 % septembre 2029 : 3,59 % (17 septembre) ; OAT 3,70 % novembre 2036 (environ 10 ans) : 4,74 % (5 novembre). Taux de la facilité de dépôt de la BCE : 2,50 % depuis le 16 septembre 2026.
- **Passage au réel (calcul indicatif, non sourcé)** : 4,74 % moins une inflation de 1,6 % à 2,0 % (fourchette du COR et du Consensus pour 2026-2027) donne environ **2,7 % à 3,1 % réel** pour l'OAT à 10 ans. Ce n'est pas le rendement d'un portefeuille de réserves (qui comporterait des actifs risqués) ni un rendement garanti, et le taux à 10 ans de 2026 ne dit rien du rendement moyen sur 40 ans. Un taux réel direct (OAT indexées) n'est pas dans le fichier fourni.
- **Rendements des obligations indexées (AFT, adjudications du 15/10/2026, relevés le 25/11/2026)** : taux moyen pondéré de **1,83 %** pour l'OAT€i 3,15 % 25/07/2032, de **2,71 %** pour l'OAT€i 1,80 % 25/07/2040 et de **2,87 %** pour l'OATi 0,55 % 01/03/2039 (page « Dernières adjudications », `aft.gouv.fr`). Ces titres sont indexés sur l'inflation : le taux est très probablement réel, mais la page ne le précise pas. **À confirmer dans la documentation de l'AFT avant tout usage.** Ce sont des rendements ponctuels à 6-14 ans d'échéance, ni un rendement moyen sur 40 ans ni celui d'un portefeuille de réserves. Les PDF « récapitulatif mensuel des opérations » de l'AFT ne contiennent pas de colonne de rendement exploitable. **Repère seulement : aucune valeur n'est reprise comme valeur retenue** dans `config/assumptions.yaml`.
- **Taux de cotisation** : non recherchés. Le taux $\tau_0$ est calibré par construction et ne dépend donc pas d'une donnée externe, mais une valeur de contrôle serait utile.

---

## Fiches restantes (phase 1)

- [x] Fiche 6 : taux d'emploi par âge individuel obtenu (15-64 ans ; tranches au-delà) ; concept d'emploi décidé le 25/11/2026 (comptabilité nationale, D6). Reste le champ géographique du fichier détaillé à confirmer et le facteur d'échelle à calculer en phase 3.
- [~] Fiche 7 : cotisants par catégorie, ordre de grandeur obtenu (public 19 %, indépendants 11 à 13 %, privé par solde). Règle d'attribution tranchée le 25/11/2026 (D11) : $\pi$ inchangé, CNAVPL en contrôle. Stock de retraités par catégorie : règle D14, contrôle sur le tableau 3 du panorama.
- [~] Fiche 8 : privé, public (FPE, FPT, FPH par âge sans sexe) et indépendants (2022) renseignés ; brut/net du privé relevé (1,318). Tranché le 25/11/2026 : salaire à 62-64 ans par proxy (D9), grille en escalier par catégorie (D10). Reste à écrire, par catégorie, la moyenne par sexe utilisée pour D10.
- [x] Fiche 9 : âge légal et durée par génération (article d'indexation à relire sur Légifrance).
- [~] Fiche 10 : revalorisation 2025 relevée (+2,2 %). Tranché le 25/11/2026 : `m1` traité comme brut (D7), stock avancé à 2026 (D8), écart de 123 445 non corrigé (D13). Reste à relire la définition de `m1` dans la documentation EACR si elle devient disponible.
- [~] Fiche 11 : repères COR renseignés ; rendements des obligations indexées de l'AFT relevés le 25/11/2026 (réel à confirmer). Valeur centrale du rendement réel posée le 25/11/2026 : 1,0 %, plage de −1 % à +3 % (D12).

Légende : [x] complète, [~] utilisable avec les réserves indiquées, [ ] non commencée.
