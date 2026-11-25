# Hypothèses et paramètres du simulateur (v0.1)

Ce document accompagne la section 6 du cahier des charges (révision 6) et les fiches de provenance de `docs/donnees.md`. Chaque paramètre y a un **statut**, une **valeur ou méthode**, une **plage de test** et une **source**. Une case « à relever » ou « à calculer » signifie qu'**aucune valeur n'est retenue** : elle ne sera pas saisie de mémoire.

Statuts : **O** observé · **P** projection officielle · **C** calibré · **H** hypothèse documentée · **K** convention (voir 6.1 du cahier).

Dernière mise à jour : 25/11/2026.

## 1. Décisions validées le 25/11/2026

| N° | Décision | Statut | Valeur | Plage de test | Justification et limite |
|---|---|---|---|---|---|
| D1 | Âge d'entrée dans la vie active $a_0$ | K | 20 ans | 18 à 22 ans | Milieu de la tranche 15-24 ans, où le taux d'emploi n'est que de 34,5 % en 2025 (fiche 6). C'est un choix de projet, pas une donnée. |
| D2 | Parts d'affiliation $\pi_c$ (identiques pour les deux sexes et tous les âges $\geq a_0$) | H | Privé 0,70 ; public 0,19 ; indépendants 0,11 | public 0,17 à 0,21 ; indépendants 0,09 à 0,14 ; privé = solde | Ordre de grandeur issu de la DGAFP (5,85 millions d'agents), de la MSA (indépendants 11 %) et de l'Insee (4,0 millions de non-salariés, soit 13 %), rapportés à 30,6 millions d'emplois (COR). Champs différents, double comptage des pluriactifs possible (fiche 7). L'identité par âge et par sexe est une simplification : le public est plus féminin (64 % de femmes) et les indépendants plus âgés. |
| D3 | Migrants $\pi^{\text{mig}}_c$ | H | Égaux à $\pi_c$ pour $a \geq a_0$ ; stock non segmenté pour $a < a_0$ | Mêmes plages que D2 | Règle la plus simple qui conserve les effectifs (cahier, 3.5, point 4). |
| D4 | Rattachement des régimes à une catégorie | H | Régimes spéciaux (SNCF, RATP, industries électriques et gazières, etc.) rattachés au **public** ; Cavimac et Mayotte exclus (exclusion des **régimes de retraite** ; le moteur démographique couvre la France entière, Mayotte incluse : `docs/conventions-moteur.md`, section 4) | Sensibilité : rattacher les régimes spéciaux hors fonction publique au privé | Ces régimes à prestations définies ressemblent à ceux des fonctionnaires. Simplification à rappeler dans le README. |
| D5 | Âges légaux fractionnaires | K | Arrondi à l'entier le plus proche (0,5 arrondi vers le haut) ; les générations 1961 et 1965, coupées en deux périodes, sont moyennées au prorata de la durée | Arrondi inférieur et supérieur | Le modèle compte en âges entiers. L'écart résiduel est absorbé par $\delta_{c,s}$. Valeurs dans `config/assumptions.yaml`. |

## 2. Démographie

| Paramètre | Statut | Valeur ou méthode | Plage de test | Source |
|---|---|---|---|---|
| Population initiale (1er janvier 2026, âge × sexe) | O | Insee, POP3, estimation provisoire | Aucune (donnée) | Fiche 1 |
| Fécondité | P | Scénario central de l'Insee 2026, valeurs lues dans `00_central.xlsx` | Variantes de l'Insee ; repère COR : 1,2 à 1,7 enfant par femme | Fiche 4 ; COR |
| Mortalité $q_{a,s,t}$ (identique pour les trois catégories) | O et P | Quotients de l'Insee 2026 ; tendance stochastique en phase 5 | Variantes d'espérance de vie de l'Insee, à relever | Fiche 3 |
| Migration nette | P | Scénario central de l'Insee, par âge et sexe ; flux bruts $m^{+}$ et $m^{-}$ déduits du solde (cahier, 3.5) | Repère COR : 70 000 à 230 000 personnes par an | Fiche 5 ; COR |
| Classe ouverte | K | 100 ans et plus, $\rho = 1$, $e = 0$ | — | Cahier, 3.7 |
| Population initiale par catégorie $\pi^{2026}_{c,a,s}$ | H | Mêmes parts que D2 pour tous les âges $\geq a_0$ en v0.1 | Voir D2 | Fiche 7 |

Réserve sur la population initiale par catégorie : l'EACR compte les polypensionnés dans chaque régime (2,3 fois le total dédoublonné, fiche 7). On ne peut donc pas en déduire la répartition des retraités par catégorie. La règle de répartition **du stock de retraités** est un point ouvert décalé en phase 3 (voir section 6).

## 3. Emploi, salaires et cotisations

| Paramètre | Statut | Valeur ou méthode | Plage de test | Source |
|---|---|---|---|---|
| Taux d'emploi observé $e^{\text{obs}}$ | O | Enquête Emploi par sexe et tranche d'âge (3 tranches seulement) ; à affiner par âge quinquennal | À fixer en phase 3 | Fiche 6 |
| Taux d'emploi conditionnel $e$ | C | $e = e^{\text{obs}}/(1-\rho)$, sans plafonnement ; violation de $0 \leq e \leq 1$ : le test échoue | — | Cahier, 3.5 |
| Concept d'emploi | K | À arrêter : comptabilité nationale (COR : 30,6 millions en 2025) ou enquête Emploi (29,4 millions) | — | Fiches 6 et 7 |
| Salaire $w_{c,a,s}$ privé | O | Salaire net mensuel moyen en équivalent temps plein par sexe et tranche d'âge (2024) | À fixer en phase 3 | Fiche 8 |
| Salaire $w_{c,a,s}$ public | O | Fonction publique d'État et territoriale par tranche d'âge (2024) ; hospitalière : à compléter | À fixer en phase 3 | Fiche 8 |
| Salaire $w_{c,a,s}$ indépendants | O | Revenu d'activité net mensuel (2022), non comparable à un salaire en équivalent temps plein | À fixer en phase 3 | Fiche 8 |
| Passage brut-net | H | Rapport brut/net du public : environ 1,23 ; privé : à relever | À fixer en phase 3 | Fiche 8 |
| Assiette de cotisation | K | Masse salariale totale sans plafond | — | Cahier, 6.3 |
| Croissance réelle des salaires | P | Scénario de référence du COR : productivité horaire 0,7 % par an à partir de 2040 ; trajectoire 2026-2039 à relever | Productivité 0,4 % à 1,0 % ; chômage 5 % à 10 % | Fiche 11 ; COR |

## 4. Retraite : âges, pensions, indexation

| Paramètre | Statut | Valeur ou méthode | Plage de test | Source |
|---|---|---|---|---|
| Âge légal par génération $a^{lég}(g)$ | O | Tableau 1.4 du COR (loi de financement de la sécurité sociale pour 2026, suspension de la réforme de 2023), arrondi selon D5 | Variante sans suspension : levier de réforme | Fiche 9 |
| Écart $\delta_{c,s}$ entre âge effectif et âge légal | C | Âge conjoncturel de départ (EACR) moins âge légal de la génération concernée, arrondi à l'entier ; constant sur l'horizon | $\pm 1$ an | Fiches 9 et 10 ; **à calculer** |
| Stock de pensions de 2026 | O | EACR, `m1` (avantage principal de droit direct, perçu en décembre), indexé. **Dernière année observée : 2024** | — | Fiche 10 |
| Taux de liquidation $\theta_c$ | C | Pension des nouveaux liquidants / salaire à l'âge de départ de la même génération (3.6) ; contrôle par les cas types du COR ; à défaut, ratio de stock appelé « taux de remplacement apparent ». **Aucune valeur tant que le brut ou net de `m1` n'est pas confirmé** | À fixer en phase 3 | Fiche 10 |
| Indexation des pensions | O | Sur les prix ; +0,9 % au 1er janvier 2026 pour les pensions de base (COR) ; revalorisation 2025 : à relever | Variantes : salaire moyen, revenu de la catégorie | Fiches 9 et 10 |

## 5. Finances et incertitude

| Paramètre | Statut | Valeur ou méthode | Plage de test | Source |
|---|---|---|---|---|
| Taux de cotisation $\tau_0$ | C | $\tau_0 = B_{2026}/A_{2026}$ : taux de calibration du modèle, pas un taux légal ; l'équilibre de 2026 est une condition de calibration, pas un résultat | $\tau$ varie dans $[0, \tau_{\max}]$ pour $\tau^*$ | Cahier, 6.2 |
| Réserve initiale | K | $R_{2026} = k \times B_{2026}$ ; référence $k = 0$ | $k \in [0 ; 3]$ ; plage à justifier avec des réserves de régimes réels (phase 3) | Cahier, 4.1 |
| Financement externe $F_t$ | K | 0 dans le scénario central | — | Cahier, 4.2 |
| Rendement réel des réserves | H (provisoire) | **À sourcer.** Repère indicatif de la fiche 11 : environ 2,7 % à 3,1 % réel pour l'OAT à 10 ans (calcul indicatif à partir d'une source secondaire) ; ne vaut pas rendement d'un portefeuille | À fixer avec une source primaire (Agence France Trésor) | Fiche 11 |
| Taux d'actualisation réel | H | À définir en phase 4 | À définir | Cahier, 6.3 |
| Simulations | K | $N = 10\,000$ ; graine fixe ; $\alpha \in \{0{,}80 ; 0{,}90 ; 0{,}95\}$ ; borne de Wilson à 95 % | $N$ ajustable | Cahier, 4.4 |

## 6. Points ouverts décalés en phase 3

Ces points étaient dans la phase 1 du plan. Ils ne bloquent pas le moteur démographique (phase 2), mais bloquent le calibrage du moteur financier.

1. Brut ou net de `m1` : la documentation EACR ne le précise pas (fiche 10).
2. Répartition du stock de retraités par catégorie, compte tenu du double comptage des polypensionnés.
3. Passage de la dernière année observée (2024) à l'année de calibration (2026) : avancer le stock ou calibrer sur 2024.
4. Revalorisation 2025 des pensions de base.
5. Écart de 123 445 personnes entre les âges individuels et la ligne « Ensemble » de l'EACR.
6. Concept d'emploi (comptabilité nationale ou enquête Emploi) et taux d'emploi par âge détaillé.
7. Plages de test des paramètres financiers, plage de $k$ justifiée.
8. Rendement réel des réserves à partir d'une source primaire.
9. Effectif des professions libérales (CNAVPL) et salaires de la fonction publique hospitalière par âge.
