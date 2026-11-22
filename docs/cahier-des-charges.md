# Pension Sustainability Simulator
## Cahier des charges — révision 2 (brouillon)

**Projet :** Simulation de la soutenabilité d'un système de retraite  
**Type :** Projet actuariel, démographique, financier et informatique  
**Horizon :** 40 années de flux (2026 à 2065) ; réserves observées de $R_{2027}$ à $R_{2066}$  
**Unité monétaire :** euros constants 2026  
**Langage principal :** Python  
**Date de la révision :** 22 novembre 2026

> Dans ce document, « v0.1 » et « v0.2 » désignent les versions du **simulateur**. Le document lui-même est numéroté par révisions.

---

## 1. Contexte et problématique

Les systèmes de retraite sont confrontés à des évolutions démographiques, économiques et sociales susceptibles de modifier durablement leur équilibre financier. Le vieillissement de la population, l'évolution de la natalité, les gains de longévité, l'emploi et les salaires influencent le rapport entre cotisants et retraités.

Dans un régime par répartition, ces facteurs affectent directement les recettes de cotisations et les dépenses de pensions. Les déséquilibres peuvent nécessiter des ajustements portant sur les cotisations, les prestations, l'âge de départ ou le financement externe.

Le projet vise à construire un modèle actuariel permettant de projeter l'évolution démographique et financière d'un régime de retraite, d'évaluer les risques de déficit et d'étudier les mécanismes permettant d'assurer sa soutenabilité sur le long terme.

---

## 2. Question décisionnelle

**Dans quelles conditions un régime de retraite peut-il maintenir ses réserves non négatives sur 40 ans, et quels ajustements permettent d'atteindre cet objectif tout en analysant leurs conséquences entre générations ?**

Le simulateur devra quantifier les conséquences des différents scénarios et identifier les paramètres les plus influents sur l'équilibre du régime.

En v0.x, l'équité intergénérationnelle est **descriptive**. L'expression « charge excessive » n'est pas utilisée comme critère de décision tant qu'un indicateur d'équité n'a pas été défini et justifié.

---

## 3. Périmètre du modèle

### 3.1. Nature du régime

Le modèle représente un **régime consolidé fictif de retraite**, inspiré d'ordres de grandeur et de mécanismes du système français, sans reproduire ses règles institutionnelles exactes.

Il comprend :

- un régime par répartition à prestations définies simplifiées ;
- trois catégories d'affiliation ;
- une seule réserve financière consolidée $R_t$ (il n'existe pas trois réserves indépendantes) ;
- une projection par âge, sexe et catégorie d'affiliation ;
- des flux financiers exprimés en euros constants de 2026.

Le modèle ne reproduit pas les mécanismes réels de financement de la fonction publique, notamment la contribution d'équilibre de l'État. Le **financement externe** $F_t$ est **nul dans le scénario central** : un régime dont l'équilibre dépend d'un financement implicite ne permettrait pas de mesurer le déséquilibre. $F_t$ n'intervient que comme levier dans des scénarios explicites.

### 3.2. Versions progressives du simulateur

**v0.1 — Modèle par grandes catégories d'affiliation**

Trois catégories sont retenues :

- secteur privé ;
- secteur public, branches regroupées ;
- travailleurs indépendants.

La segmentation est utile dès la v0.1 car les catégories diffèrent par :

- leurs effectifs et leur structure d'âge ;
- leurs taux d'emploi ;
- leur salaire moyen et leur assiette de cotisation ;
- leurs profils d'âge effectif de départ ;
- leurs salaires de référence et leurs pensions.

Le **taux de cotisation $\tau$ est unique** : il s'applique à l'assiette de chaque catégorie. Cela garantit que le taux d'équilibre est un nombre unique.

Les paramètres différenciés seront issus de données disponibles, ou documentés comme hypothèses de travail faute de données.

**v0.2 — Modèle enrichi**

Ajout des PCS, d'une segmentation plus fine des revenus, des trajectoires professionnelles et d'une plus grande hétérogénéité des comportements.

### 3.3. Éléments inclus

- Projection démographique par cohortes.
- Mortalité, fécondité et migration.
- Emploi, chômage et population cotisante.
- Salaires et assiette des cotisations.
- Calcul des pensions et départs en retraite.
- Cotisations, dépenses, réserves et rendements.
- Calibration du régime en année initiale.
- Scénarios économiques et démographiques.
- Simulation Monte-Carlo.
- Sensibilité et analyse de soutenabilité.
- Comparaison de réformes.
- Analyse descriptive intergénérationnelle.

### 3.4. Éléments exclus de la v0.1

| Élément exclu | Justification |
|---|---|
| Carrières incomplètes | Nécessitent des trajectoires individuelles ou une modélisation détaillée des carrières |
| Pension de réversion | Introduit des droits dérivés et des mécanismes de dépendance supplémentaires |
| Minimum vieillesse et minimum contributif | Nécessitent des règles complémentaires de redistribution et de conditions de ressources |
| Retraite anticipée et dispositifs spéciaux | Multiplient les conditions d'éligibilité et les cas particuliers |
| Décote, surcote et bonus-malus détaillés | Non indispensables au moteur initial et complexifient la liquidation |
| Hétérogénéité complète des revenus | Reportée à la v0.2 pour limiter la dimension du modèle |
| Microsimulation individuelle | Le moteur initial fonctionne par cohortes agrégées et non par individus |

Le modèle ne vise pas à reproduire exactement le système français ni à produire des recommandations politiques.

---

## 4. Conventions et critères de soutenabilité

### 4.1. Convention temporelle

- $R_t$ désigne la **réserve au 1er janvier de l'année $t$**.
- Les flux de l'année $t$ (cotisations, prestations, financement externe, produits financiers) sont projetés pour $t \in \lbrace 2026, \ldots, 2065 \rbrace$, soit **40 années de flux**.
- $R_{t+1}$ est la réserve à la fin de l'année $t$. Ainsi $R_{2027}$ est la réserve à la fin de 2026, et $R_{2066}$ la réserve à la fin de 2065, dernière année projetée.
- $R_{2026}$ est la **réserve initiale**.

**Réserve initiale.** On pose $R_{2026} = k \times B_{2026}$, où $B_{2026}$ est le montant des prestations de 2026 et $k$ un nombre d'années de prestations.

- Valeur centrale : $k = 1$ (convention de régime fictif, à justifier dans le document des hypothèses).
- Plage de sensibilité : $k \in [0 ; 3]$.
- Le cas $k = 0$ est un **cas de stress** : sans aucune réserve, toute année déficitaire entraîne une réserve négative.
- Les résultats, en particulier les taux d'équilibre, sont présentés **en fonction de $k$**, et pas pour une seule valeur.

### 4.2. Flux et dynamique des réserves

Pour $t \in \lbrace 2026, \ldots, 2065 \rbrace$ :

$$
C_t = \tau \, A_t, \qquad D_t = B_t - C_t - F_t, \qquad R_{t+1} = R_t (1 + r_t) - D_t
$$

où :

- $A_t$ : assiette de cotisation totale des trois catégories ;
- $C_t$ : cotisations encaissées ;
- $B_t$ : prestations versées ;
- $F_t$ : financements externes explicitement modélisés (nuls dans le scénario central) ;
- $D_t$ : **déficit de fonctionnement**, qui n'inclut **pas** les produits financiers ;
- $r_t$ : rendement réel des réserves, appliqué au stock d'ouverture $R_t$ (convention simplifiée, sans produits sur les flux intra-annuels).

### 4.3. Critère A — Soutenabilité déterministe

Dans un scénario donné, le régime est soutenable si ses réserves restent non négatives à chaque date observée :

$$
R_t \geq 0, \qquad \forall t \in \lbrace 2027, \ldots, 2066 \rbrace
$$

Ce critère est testé pour un jeu d'hypothèses donné et sert de test du moteur.

### 4.4. Critère B — Soutenabilité probabiliste (critère principal)

Le régime satisfait le niveau de soutenabilité cible $\alpha$ lorsque :

$$
\mathbb{P}\left( \min_{t \in \lbrace 2027, \ldots, 2066 \rbrace} R_t \geq 0 \right) \geq \alpha,
\qquad \alpha \in \lbrace 0{,}80 ;\ 0{,}90 ;\ 0{,}95 \rbrace
$$

Le niveau $\alpha$ est une **probabilité cible de soutenabilité**. Ce n'est ni un montant de réserves ni un intervalle de confiance statistique.

**Estimation.** Pour $N$ trajectoires simulées, $\hat p = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}\left( \min_t R_t^{(i)} \geq 0 \right)$. Le nombre initial de simulations est fixé à $N = 10\,000$, sous réserve des tests de performance et de précision.

**Erreur Monte-Carlo.**

$$
SE(\hat p) = \sqrt{\frac{\hat p (1 - \hat p)}{N}}
$$

Elle mesure uniquement l'erreur due au nombre fini de simulations, pas l'incertitude de modèle, de données ou de calibration.

**Règle de décision.** Soit $L_N$ la borne inférieure de l'intervalle de Wilson à 95 % pour $p$. Le régime est déclaré soutenable au niveau $\alpha$ si $L_N \geq \alpha$. Si l'intervalle contient $\alpha$, le résultat est déclaré **inconclusif** et $N$ pourra être augmenté. Pour $p$ voisin de 0,9 et $N = 10\,000$, il faut environ $\hat p \geq \alpha + 0{,}6$ point pour conclure.

Les probabilités obtenues sont conditionnelles au modèle et aux hypothèses : elles ne constituent pas une probabilité objective de survie du système réel.

### 4.5. Sources d'aléa

Les simulations pourront intégrer des variations aléatoires de :

- mortalité et longévité ;
- fécondité ;
- migration ;
- productivité et croissance des salaires ;
- rendement des réserves ;
- emploi et chômage.

La phase 5 commence par **trois sources** (rendement, productivité et salaires, mortalité) et en ajoute d'autres si le temps le permet. Les distributions, dépendances et corrélations sont estimées à partir de séries documentées lorsque c'est possible. Sinon, les choix sont qualifiés d'hypothèses et testés en sensibilité.

### 4.6. Taux de cotisation d'équilibre

**Déterministe.** Pour le scénario central :

$$
\tau^*_A = \min \lbrace \tau : R_t(\tau) \geq 0, \ \forall t \in \lbrace 2027, \ldots, 2066 \rbrace \rbrace
$$

La fonction $g(\tau) = \min_t R_t(\tau)$ est continue : on peut chercher la racine de $g$ par `scipy.optimize.brentq` ou par bissection.

**Probabiliste.** Au niveau cible $\alpha$ :

$$
\tau^*_\alpha = \inf \left\lbrace \tau : \mathbb{P}\left( \min_t R_t(\tau) \geq 0 \right) \geq \alpha \right\rbrace
$$

L'estimateur $\hat\tau_\alpha$ est le plus petit $\tau$ pour lequel la règle de décision de la section 4.4 est satisfaite ($L_N(\tau) \geq \alpha$). Il est donc **prudent**.

**Réutilisation des tirages.** Les mêmes tirages aléatoires sont utilisés pour toutes les valeurs de $\tau$ testées (*common random numbers*).

**Monotonie.** Si $\tau$ n'agit que sur les cotisations, sans réaction de l'emploi ni des salaires, alors pour chaque trajectoire $R_t(\tau)$ est croissante en $\tau$ (car $1 + r_t > 0$). Avec des tirages communs, $\hat p(\tau)$ est donc une fonction en escalier croissante, et la **bissection** s'applique. `brentq` suppose une fonction continue et ne convient pas ici. Si une réforme introduit une réaction comportementale, la monotonie doit être revérifiée.

---

## 5. Indicateurs de sortie

| Indicateur | Définition | Unité | Phase |
|---|---|---|---:|
| Réserves | Réserve $R_t$ à chaque date | € constants 2026 | 3 |
| Déficit de fonctionnement | $D_t = B_t - C_t - F_t$, hors produits financiers | € constants/an | 3 |
| Ratio cotisants/retraités | Nombre de cotisants rapporté au nombre de retraités | Ratio | 3 |
| Taux de cotisation d'équilibre déterministe | $\tau^*_A$ (critère A) | % de l'assiette | 4 |
| Âge de retraite d'équilibre | Plus petit âge légal satisfaisant le critère A, toutes choses égales par ailleurs | Années | 4 |
| Engagements futurs | Valeur actuelle des pensions futures au taux d'actualisation réel retenu | € constants 2026 | 4 |
| Bilan actuariel | Valeur actuelle des ressources moins celle des engagements | € constants 2026 | 4 |
| Taux de cotisation d'équilibre probabiliste | $\tau^*_\alpha$, pour chaque $\alpha$ et chaque $k$ | % de l'assiette | 5 |
| Rendement interne générationnel | Rendement implicite des cotisations et prestations d'une génération | % annuel | 6 |

La valorisation des engagements nécessite un **taux d'actualisation réel documenté**, calibré ou fixé selon la source retenue (voir section 6.3).

Un déficit est qualifié de **structurel** lorsque le déficit de fonctionnement $D_t$ est positif trois années consécutives. Ce seuil est une convention de projet, testée en sensibilité.

L'équité intergénérationnelle est **descriptive** en v0.x : comparaison des cotisations, prestations, durées de retraite et rendements internes par génération. Aucun seuil d'équité n'est normatif tant qu'il n'a pas été justifié.

---

## 6. Hypothèses, données et calibration

### 6.1. Principe

Les paramètres ne sont pas fixés arbitrairement lorsque des données observées ou des projections officielles peuvent être mobilisées. Le modèle distingue :

1. **Données observées** : effectifs, salaires, emploi, pensions, mortalité.
2. **Hypothèses officielles** : projections et scénarios issus d'organismes reconnus.
3. **Paramètres calibrés** : valeurs déduites des données pour reproduire une situation de référence.
4. **Hypothèses de modèle** : éléments nécessaires au fonctionnement du moteur faute de données, documentés comme tels.
5. **Paramètres de sensibilité** : plages explorées autour des valeurs centrales.

### 6.2. Calibration de l'année initiale

La calibration repose sur **une équation et une inconnue** :

1. Le taux de remplacement de la formule de pension est **fixé à partir des données** (DREES, COR), et non calibré.
2. Les prestations $B_{2026}$ s'en déduisent à partir des effectifs de retraités et des salaires de référence.
3. Avec $F_{2026} = 0$, le solde de fonctionnement nul en 2026 ($D_{2026} = 0$) donne le taux de cotisation de départ :

$$
\tau_0 = \frac{B_{2026}}{A_{2026}}
$$

4. La réserve initiale est ensuite $R_{2026} = k \times B_{2026}$ (section 4.1).

### 6.3. Tableau des paramètres

Les valeurs ci-dessous sont **provisoires**. Elles proviennent du document de contexte du projet, relevé le 20 novembre 2026, et seront revérifiées à la source avant usage. Les plages de test ne sont pas choisies pour produire des résultats favorables.

| Paramètre | Valeur centrale provisoire | Plage de test | Source | Statut |
|---|---|---|---|---|
| Année initiale | 2026 | Fixée | Convention de projet | Fixé |
| Horizon | 40 années de flux (2026-2065) | Fixé | Convention de projet | Fixé |
| Taux de cotisation $\tau$ (unique) | $\tau_0 = B_{2026}/A_{2026}$ | À définir autour de $\tau_0$ (phase 3) | Calibration (6.2) | Calibré |
| Taux de remplacement de la formule | 60 % | 50 à 70 % | DREES, COR (cas types) | À vérifier |
| Salaire de référence | Salaire moyen de la génération à la liquidation | Variantes à définir | INSEE, DREES | Convention |
| Âge légal | 62 ans (générique) | 60 à 67 ans | Convention ; le droit réel dépend de la génération | Hypothèse illustrative |
| Âge effectif de départ | Profil par catégorie et par sexe | Variantes documentées | DREES | À documenter |
| Croissance réelle des salaires | 1 %/an | 0 à 2 % | COR (productivité horaire 0,7 %/an, cible 2040), INSEE | À vérifier |
| Rendement réel des réserves | 1 %/an | -1 à 3 % | Agence France Trésor, données de rendement | À vérifier |
| Taux d'actualisation réel | Égal au rendement réel | Sensibilité à définir | Convention actuarielle | À documenter |
| Assiette de cotisation | Masse salariale totale, sans plafond en v0.1 | Sensibilité éventuelle | Urssaf, Légifrance (plafond de la Sécurité sociale 2026 : 48 060 €) | Convention, à vérifier |
| Indexation des pensions | Prix (pensions constantes en termes réels) | Salaire moyen, revenu de la catégorie | Règle documentée | Convention ; effets d'équité à documenter |
| Réserve initiale | $k = 1$ an de prestations | $k \in [0 ; 3]$ | Convention de régime fictif | Convention |
| Financement externe $F_t$ | 0 | Scénarios explicites | Convention de projet | Fixé |
| Fécondité | 1,56 enfant/femme en 2025, convergence vers 1,45 dès 2028 | 1,20 à 1,70 | INSEE, projections 2026 | À vérifier |
| Mortalité | Tables par sexe et âge, tendance stochastique en phase 5 | Variantes INSEE | INSEE | À vérifier |
| Migration nette | +150 000/an, profil par âge et sexe | +70 000 à +230 000/an | INSEE, projections 2026 | À vérifier |
| Emploi par âge, sexe et catégorie | Niveau observé (chômage cible de 7 % en 2040) | ± 5 points | INSEE, DARES, COR | À vérifier |

### 6.4. Convention monétaire

Les flux et stocks sont exprimés en euros constants de 2026. Les taux économiques appliqués aux montants réels sont cohérents avec cette convention.

L'inflation n'est pas appliquée aux montants constants. Elle sert à convertir les données nominales et à définir les règles d'indexation. Les salaires sont modélisés comme inflation plus productivité, et les variables économiques sont variées ensemble pour éviter les combinaisons incohérentes (par exemple salaires nominaux +2 % avec inflation +2 %, soit une croissance réelle nulle).

### 6.5. Sources envisagées

- INSEE : population, démographie, salaires, emploi, projections.
- COR : hypothèses macroéconomiques et projections de retraite.
- DREES, Urssaf, Légifrance : pensions, taux de remplacement, règles de cotisation.
- Agence France Trésor et sources financières documentées : rendements.

Chaque jeu de données est accompagné d'une fiche de provenance (lien, date, licence, millésime, transformations effectuées). Les données brutes de `data/raw/` ne sont jamais modifiées.

---

## 7. Tests et critères d'acceptation

### 7.1. Tests démographiques

- Conservation des effectifs, hors naissances, décès et migrations.
- Absence de populations négatives.
- Cohérence des transitions par âge, sexe et catégorie d'affiliation.
- Tolérance numérique de conservation de $10^{-9}$ sur les tests adaptés.

### 7.2. Tests actuariels

- Vérification manuelle sur un exemple de trois classes d'âge, reproduit exactement.
- Cohérence entre cotisations, pensions, déficit et réserves.
- Vérification des limites de l'âge de retraite.
- Après calibration : $D_{2026} = 0$ (à la tolérance numérique près) et $R_{2026} = k \times B_{2026}$.
- Croissance de $R_t$ avec $\tau$ trajectoire par trajectoire et croissance de $\hat p(\tau)$ avec les tirages communs.

### 7.3. Calibration démographique par rapport à l'INSEE

La population projetée est comparée à la **projection INSEE 2026, scénario central**, de même date initiale (1er janvier 2026) et de même champ. Le moteur est alimenté avec **les mêmes hypothèses** de fécondité, de mortalité et de migration que ce scénario. Sans cela, un écart ne serait pas interprétable.

Critères d'acceptation, vérifiés **pour chaque année de l'horizon** :

- erreur relative sur la population totale ≤ 1 % ;
- erreur relative sur les grands groupes d'âge (0-19 ans, 20-59 ans, 60 ans et plus) ≤ 2 %, sous réserve du traitement des classes à faible effectif (par exemple 100 ans et plus) ;
- documentation de l'écart, des données de référence et des éventuelles exceptions.

Ces seuils sont fixés avant les tests. Ils ne sont pas modifiés après observation des résultats sans justification écrite. La comparaison avec l'INSEE contrôle le moteur démographique, mais ne valide pas à elle seule le moteur financier ou actuariel.

### 7.4. Reproductibilité et qualité logicielle

- Graine aléatoire fixe (`np.random.default_rng`).
- Paramètres centralisés dans la configuration (`config/assumptions.yaml`).
- Données et hypothèses versionnées et documentées.
- Environnement Python reproductible (`requirements.txt`).
- Tests automatisés avec Pytest ; comparaisons de flottants avec `pytest.approx`.
- **GitHub Actions mis en place dès la phase 2** pour exécuter les tests à chaque modification.
- Moteur financier **vectorisé avec NumPy** (phase 3), sans boucle Python sur les simulations.

---

## 8. Phases, durée et livrables

Le projet est conçu pour un rythme moyen de **6 à 8 heures par semaine**, avec les périodes d'examens, la recherche de stage et une disponibilité variable.

### Cœur du projet (phases 1 à 5)

| Phase | Durée cible | Contenu et critère de fin |
|---|---:|---|
| 1. Conception | 2 semaines | Cahier des charges validé, inventaire des données (accès, format, millésime), hypothèses, architecture, README, critères de validation de la phase 2 |
| 2. Moteur démographique | 4 semaines | Cohortes fonctionnelles, tests verts, conservation des populations, comparaison INSEE dans les seuils, **GitHub Actions configurées** |
| 3. Moteur financier | 4 semaines | Cotisations, prestations, réserves, bilan annuel cohérents, calibration de l'année initiale, moteur vectorisé, tests verts |
| 4. Indicateurs actuariels | 2 semaines | Ratio, déficit, $\tau^*_A$, âge d'équilibre, engagements et bilan actuariel ; README, documentation, premier graphique ; v0.1 publiable |
| Marge | 1 semaine | À utiliser dans les phases 2 à 5 selon les imprévus |
| 5. Incertitude | 4 semaines | Scénarios, Monte-Carlo vectorisé, critères A et B opérationnels, probabilités à 80/90/95 %, précision Monte-Carlo mesurée, $\hat\tau_\alpha$, sensibilités |

**Jalon portfolio — fin de la phase 4.** Une première version présentable sur GitHub, exploitable dans les candidatures de stage : modèle, tests automatisés, README clair, hypothèses documentées et au moins un graphique de projection.

**Dates cibles indicatives**, sous réserve des périodes d'examens : jalon portfolio en mars 2027, critère B opérationnel en mai 2027.

### Phases optionnelles

| Phase | Durée cible | Contenu et critère de fin |
|---|---:|---|
| 6. Réformes et équité | 3 semaines | Comparaison de réformes, rendement interne par génération, analyse générationnelle descriptive ; optimisation si faisable |
| 7. Agent IA | 3 semaines | Agent utilisant des outils Python validés, capable d'analyser les scénarios et de rédiger une note sans inventer de résultats |
| 8. Produit final | 2 semaines | Streamlit, documentation finale, rapport de synthèse |

La priorité est de terminer solidement les phases 1 à 5.

**Charge estimée.** Le cœur du projet représente 17 semaines, soit environ 100 à 135 heures. Avec les phases optionnelles, le total est d'environ 25 semaines, soit 150 à 200 heures.

Chaque phase est validée par une liste de critères de fin mesurables avant le passage à la suivante.

### Livrables de la phase 1

- Cahier des charges validé.
- Documentation des données (`donnees.md`) et des hypothèses (`hypotheses.md`).
- Architecture logicielle préliminaire.
- Structure du dépôt GitHub et README initial.
- Plan de validation de la phase 2.

---

## 9. Risques et limites

- La disponibilité et la granularité des données peuvent limiter la calibration.
- Le régime consolidé est fictif et ne reproduit pas les transferts institutionnels réels du système français.
- Les résultats dépendent fortement de la réserve initiale ($k$) : un régime sans réserve ($k = 0$) est un cas de stress, pas une référence.
- Certaines règles de pension sont simplifiées.
- Les résultats dépendent des données, des hypothèses et de la structure du modèle.
- Les probabilités Monte-Carlo ne mesurent pas l'incertitude de modèle.
- Une projection cohérente n'est pas une prévision certaine.
- L'équité intergénérationnelle n'est pas évaluée par un seuil normatif en v0.x.

Le projet privilégie la transparence, la traçabilité, la validation, la reproductibilité et la qualité de l'implémentation plutôt que la sophistication prématurée.

---

**Statut :** brouillon, révision 2.  
**Condition de démarrage du développement :** validation du périmètre et des conventions de la phase 1.
