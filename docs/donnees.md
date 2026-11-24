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
| URL du fichier | À compléter : clic droit sur le lien de téléchargement du scénario central, puis « Copier l'adresse du lien » |
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

## Fiches restantes (phase 1)

- [ ] Fiche 6 : emploi et chômage par âge et sexe (INSEE Enquête Emploi, DARES).
- [ ] Fiche 7 : effectifs de cotisants et de retraités par catégorie (DREES, rapports des caisses).
- [ ] Fiche 8 : salaires par catégorie et sexe, profil par âge si disponible (INSEE).
- [ ] Fiche 9 : règles de cotisation et de pension (âge légal par génération, indexation ; Légifrance, Urssaf, service-public.fr).
- [ ] Fiche 10 : pensions du stock de 2026, pension des nouveaux liquidants, salaire à l'âge de départ, cas types (DREES, COR).
- [ ] Fiche 11 : macroéconomie (scénario de référence du COR, rendements ; Agence France Trésor).
