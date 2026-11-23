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
| Champ | Deux blocs de colonnes : **France métropolitaine** et **France**. Le fichier utilise « France hors Mayotte » jusqu'en 2013 et « France » à partir de 2014 ; le périmètre exact de « France » est à confirmer dans la documentation de l'Insee |
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
- **Classe ouverte** : la source s'arrête à « 105 ou plus », alors que le cahier des charges fixe la classe ouverte à 100+. Décision : agréger les âges 100 à 105+ dans la classe 100+ lors du chargement, et le documenter. À revérifier quand la fiche 2 (projections) sera remplie, pour que les deux sources utilisent la même classe ouverte.
- **Champ géographique** : choisir « France » pour être cohérent avec les projections INSEE, et noter le choix dans `hypotheses.md`.
- **Types hétérogènes** : dans l'onglet, certaines années de naissance sont du texte et d'autres des nombres. À convertir au chargement.

---

## Fiche 2 : Projections de population 2026, scénario central

À compléter après récupération du fichier Excel du scénario central sur https://www.insee.fr/fr/statistiques/8991068.

Points à relever :

- onglets et années couvertes (1er janvier 2026 à 2070) ;
- classe d'âge la plus élevée ;
- contenu : population par sexe et âge, décès et quotients de mortalité par sexe et âge, naissances ou fécondité, solde migratoire ;
- champ (France) ;
- total de population en 2026, à comparer à 69 081 996 (fiche 1).
