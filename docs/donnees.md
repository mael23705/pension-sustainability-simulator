# Données du projet : fiches de provenance

Une fiche par jeu de données. Les fichiers bruts sont dans `data/raw/` (jamais modifiés, non versionnés dans Git). Chaque fiche permet de retrouver la source, la date et la licence, et de refaire le téléchargement.

\---

## Fiche 1 : Population au 1er janvier 2026 (par sexe et âge)

|Champ|Contenu|
|-|-|
|Nom et organisme|POP3 – Population au 1er janvier par sexe et âge détaillé (en années révolues). Insee, « Données nationales – Population : état civil et estimations de population » (Insee Résultats)|
|URL de la page|https://www.insee.fr/fr/statistiques/8999013|
|URL du fichier|https://www.insee.fr/fr/statistiques/fichier/8999013/3\_Pop1janv\_age.xlsx|
|Date de publication|15/06/2026|
|Date de téléchargement|23/11/2026|
|Millésime|Population au 1er janvier 2026, **estimation provisoire** (onglet `2026`). Source indiquée dans le fichier : « Insee, recensements et estimations de population »|
|Champ|Deux blocs de colonnes : **France métropolitaine** et **France**. Le fichier utilise « France hors Mayotte » jusqu'en 2013 et « France » à partir de 2014, ce qui indique que « France » inclut Mayotte (même formulation dans le fichier des projections, fiche 2)|
|Granularité|Sexe (Ensemble, Hommes, Femmes) × âge en années révolues : 106 lignes, de 0 à 104 ans puis une classe « 105 ou plus ». La colonne « Année de naissance » est aussi fournie (dernière ligne : « 1920 ou avant »)|
|Licence|Licence Ouverte 2.0 (Etalab), sauf mention contraire. Conditions : citer « Source : Insee », indiquer la date de dernière mise à jour des données (ici 15/06/2026) et ne pas altérer le sens des informations. Mentions légales : https://www.insee.fr/fr/information/2008466 (mises à jour le 13/04/2026)|
|Format|xlsx, 786 746 octets (768 Ko). Un onglet par année : 1901 à 1914 et 1920 à 2026|
|Transformations prévues|Lire l'onglet `2026`, colonnes « France » (Hommes, Femmes). Nettoyer les espaces en fin de texte et convertir l'année de naissance en entier. Agréger les âges 100 à « 105 ou plus » en une classe ouverte 100+ (convention du cahier des charges). Produire une table (âge, sexe, effectif) dans `data/processed/`|
|Version du simulateur|v0.1|

### Contrôles réalisés le 23/11/2026

* Total « France » : **69 081 996** (Hommes 33 551 197, Femmes 35 530 799), soit environ 69,08 millions, cohérent avec le total publié par l'Insee.
* Pour toutes les lignes, Ensemble = Hommes + Femmes.
* Total « France métropolitaine » : 66 792 845.

### Remarques et points à traiter

* **Données provisoires** : le fichier l'indique pour 2024, 2025 et 2026. Les valeurs peuvent être révisées lors des publications suivantes.
* **Classe ouverte** : la source s'arrête à « 105 ou plus », alors que le cahier des charges fixe la classe ouverte à 100+. Décision : agréger les âges 100 à 105+ dans la classe 100+ lors du chargement, et le documenter. Vérifié avec la fiche 2 : les projections utilisent aussi « 105+ ». Les quotients de mortalité sont en revanche fournis jusqu'à 120 ans : il faudra en déduire un quotient pour la classe ouverte 100+ (voir fiche 2).
* **Champ géographique** : choisir « France », comme les projections INSEE (vérifié : la population 2026 de la fiche 2 est identique, âge par âge et par sexe), et noter le choix dans `hypotheses.md`.
* **Types hétérogènes** : dans l'onglet, certaines années de naissance sont du texte et d'autres des nombres. À convertir au chargement.

\---

## Fiche 2 : Projections de population 2026, scénario central

|Champ|Contenu|
|-|-|
|Nom et organisme|Projection de population 2026, France, **scénario central** (fichier `00\_central.xlsx`). Insee, Insee Résultats « Projections de population 2026 pour la France »|
|URL de la page|https://www.insee.fr/fr/statistiques/8991068|
|URL du fichier|À compléter : clic droit sur le lien de téléchargement du scénario central, puis « Copier l'adresse du lien »|
|Date de publication|08/06/2026|
|Date de téléchargement|23/11/2026 (à corriger si le téléchargement a eu lieu un autre jour)|
|Millésime et champ|Projections de population 2026, horizon 2070. Champ : France (note du fichier : France métropolitaine jusqu'en 1994, France hors Mayotte de 1995 à 2013, France à partir de 2014). Source indiquée : Insee, estimations de population jusqu'en 2023, projections de population 2026 à partir de 2024|
|Granularité|Annuelle, de 1962 à 2070 (109 colonnes d'années), par âge et par sexe (ensemble, femmes, hommes). Âges 0 à 104 puis « 105+ ». Mortalité par âge de 0 à 120 ans|
|Licence|Licence Ouverte 2.0 (Etalab), comme la fiche 1 : citer « Source : Insee », indiquer la date de mise à jour (08/06/2026), ne pas altérer le sens des informations|
|Format|xlsx, 2 450 989 octets (2,45 Mo), 18 onglets|
|Transformations prévues|Extraire les âges 0 à 105+ de `populationF` et `populationH` ; extraire les quotients de mortalité de `hyp\_mortaliteF` et `hyp\_mortaliteH` ; extraire la fécondité de `hyp\_fecondite` et les naissances de `naissance` ; extraire le solde migratoire de `solde\_migratoire`. Ne garder que 2026 à 2070 pour le benchmark. Produire des tables au format long dans `data/processed/`|
|Version du simulateur|v0.1 (validation et hypothèses centrales)|

### Contenu des onglets utiles

|Onglet|Contenu|
|-|-|
|`lisezmoi`|Notice : hypothèses des quatre scénarios (centrale, basse, haute, de travail) et index des onglets|
|`population`, `populationF`, `populationH`|Population au 1er janvier par âge (0 à 104, 105+) et année ; blocs de synthèse sous le tableau (groupes d'âge, rapport de dépendance, évolution annuelle)|
|`deces`, `decesF`, `decesH`|Décès par âge atteint dans l'année et année|
|`hyp\_mortaliteF`, `hyp\_mortaliteH`|Quotients de mortalité pour 100 000 par âge atteint (0 à 120 ans), survie, espérances de vie à la naissance, à 60 ans et à 65 ans|
|`naissance`|Naissances par âge de la mère et année|
|`hyp\_fecondite`|Taux de fécondité par âge de la mère (pour 10 000), indicateur conjoncturel de fécondité (ICF), âge moyen à l'accouchement|
|`solde\_migratoire`, `hyp\_soldemigF`, `hyp\_soldemigH`|Solde migratoire par âge atteint et année, total en bas de tableau|
|`ajustement`, `ajustementF`, `ajustementH`|Ajustements par âge et sexe (à comprendre avant usage, voir remarques)|
|`desc finale`|Descendance finale par génération|

### Hypothèses du scénario central (lues dans `lisezmoi` et les onglets)

* **Fécondité** : ICF de 1,564 en 2025, puis 1,526 en 2026, 1,488 en 2027 et 1,45 à partir de 2028. Âge moyen à l'accouchement en hausse jusqu'à 33,0 ans en 2050, stable ensuite.
* **Espérance de vie à la naissance en 2070** : 89,5 ans pour les femmes, 86,7 ans pour les hommes.
* **Migrations** : solde de +150 000 par an à partir de 2026 (176 000 en 2025).
* **Autres scénarios** : fécondité basse 1,20 et haute 1,70 à partir de 2030 ; espérance de vie 2070 de 86,5 et 83,7 ans (basse), 92,5 et 89,7 ans (haute) ; migrations +70 000 et +230 000 par an. Le scénario « de travail » fige l'espérance de vie à son niveau de 2025 et annule le solde migratoire.

### Contrôles réalisés le 23/11/2026

* Population 2026, ensemble : **69 081 996**, identique à la fiche 1. Hommes 33 551 197 et femmes 35 530 799 : identiques aussi.
* Comparaison âge par âge et par sexe avec POP3 pour 2026 : **écart maximal de 0**.
* Population 2070 : 65 887 156 (environ 65,9 millions).
* Les totaux des onglets `population`, `populationF` et `populationH` sont cohérents entre eux pour 2026.

### Remarques et points à traiter

* **Convention d'âge de la mortalité** : les décès et les quotients sont donnés par « âge atteint dans l'année », alors que la population est donnée par âge au 1er janvier. Le fichier fournit une ligne « proportion de décès dans l'année avant la date anniversaire » (à partir de 2023). À traiter en phase 2 : définir comment appliquer ces quotients à la population par âge révolu au 1er janvier, et le documenter dans `hypotheses.md`.
* **Classe ouverte** : population arrêtée à « 105+ », mortalité jusqu'à 120 ans. Pour la classe ouverte 100+ du cahier, il faut construire un quotient moyen pondéré par les effectifs des âges 100 à 105+. À documenter.
* **Fécondité** : les taux sont par âge de la mère (à partir de 15 ans ; borne haute à relever dans l'onglet), à utiliser avec la population féminine pour calculer les naissances.
* **Migration** : le fichier donne un **solde** par âge, pas de flux bruts d'arrivées et de départs. Le cahier des charges prévoit alors la séparation en $m^{+} = \\max(m, 0)$ et $m^{-} = \\max(-m, 0)$, avec contrôle du solde total. À vérifier : certains âges ont-ils un solde négatif ?
* **Onglets d'ajustement** : leur rôle n'est pas détaillé dans la notice. À comprendre avant de reproduire le scénario (ils peuvent expliquer un écart entre un calcul à partir des composantes et la population publiée).
* **Années d'estimation** : la note indique des estimations jusqu'en 2023 et des projections à partir de 2024. Pour le scénario central, les valeurs de 2024 à 2026 reprennent les estimations du bilan démographique. Ce point est à garder en tête pour le benchmark : le test de reproduction part de la population observée de 2026.
* **Autres scénarios** : seuls le scénario central coïncide avec la population observée de 2026. Les variantes sont projetées dès 2024 et ne servent pas au benchmark.

