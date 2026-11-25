"""Étape 9 : les six vérifications de comparabilité (docs/plan-de-validation.md, section 2).

Usage :  python scripts/check_comparability.py
Écrit docs/comparabilite-insee.md avec la date du jour. Si une vérification échoue,
le script le dit et sort avec le code 1 : on ne lance pas la comparaison (étape 10).
"""
import datetime as dt
import sys

import numpy as np

import _bootstrap
from config import affiliation_shares, get_param, load_config, raw_data_path
from conventions import SEX_F
from data_io.insee import (
    aggregate_open_class, load_central_projection, load_population_2026, open_class_quotient,
    year_params,
)
from demography.engine import step_year
from demography.population import initial_population
import pandas as pd

R = _bootstrap.RACINE
cfg = load_config(R / "config" / "assumptions.yaml")
A = get_param(cfg, "demography.open_class_age")
a0 = get_param(cfg, "demography.entry_age_a0")
pi = affiliation_shares(cfg)
first = get_param(cfg, "horizon.start_year")
n_flow = get_param(cfg, "horizon.flow_years")
limit_total = get_param(cfg, "tests.insee_total_population_max_relative_error")

pop_path = raw_data_path(cfg, R, "insee_population_file")
proj_path = raw_data_path(cfg, R, "insee_projection_file")
n_init = load_population_2026(pop_path, get_param(cfg, "data_files.insee_population_sheet"),
                              get_param(cfg, "data_files.insee_population_scope"))
proj = load_central_projection(proj_path)
i0 = proj.year_index(first)
rows = []   # (n°, intitulé, ok, détail)

# 1. Population initiale
ref0 = proj.population[:, :, i0]
diff = float(np.abs(n_init - ref0).max())
rows.append((1, "Population initiale", diff <= 0.5,
             f"POP3 (onglet {get_param(cfg, 'data_files.insee_population_sheet')}) : {n_init.sum():,.0f} ; "
             f"projection ({first}) : {ref0.sum():,.0f} ; écart maximal par sexe et âge : {diff:.1f}."))

# 2. Champ géographique : lire les notes du fichier de projection
notes = pd.read_excel(proj_path, sheet_name="population", header=None).iloc[:, 0].astype(str)
k = notes.index[notes.str.strip() == "Champ :"][0]
champ = " ".join(s.strip() for s in notes.iloc[k + 1 : k + 4])
scope = get_param(cfg, "data_files.insee_population_scope")
rows.append((2, "Champ géographique", scope == "France" and "France à partir de 2014" in champ,
             f"Notes du fichier de projection : « {champ} ». Le bloc retenu dans POP3 est « {scope} » : "
             "même champ dans les deux fichiers, **Mayotte incluse** (et non « hors Mayotte » comme supposé "
             "dans le plan). La décision D4 exclut Mayotte pour les régimes de retraite, pas pour la démographie."))

# 3. Convention d'âge : une transition d'un an du moteur doit retrouver les âges de l'Insee
pi_run = pi
state0 = initial_population(aggregate_open_class(n_init, A), a0, pi_run)
res = step_year(state0, year_params(proj, first, A, include_adjustment=get_param(cfg, "demography.insee_adjustment_included")),
                pi_run, pi_run, first)
ref1 = aggregate_open_class(proj.population[:, :, i0 + 1], A)
ages = slice(1, A)   # âges 1..99 : issus du vieillissement des âges 0..98
err = np.abs(res.state.by_age()[:, ages] / ref1[:, ages] - 1).max()
shifted = np.abs(res.state.by_age()[:, ages] / ref1[:, 2 : A + 1] - 1).max()
rows.append((3, "Convention d'âge", err <= limit_total and shifted > 10 * err,
             "Population projetée en 2027 aux âges 1 à 99 (âge révolu au 1er janvier, quotients « âge atteint » : "
             f"l'âge révolu a au 1er janvier devient a+1) : écart relatif maximal {err:.4%} avec l'Insee ; "
             f"avec un décalage d'un an, l'écart serait {shifted:.2%}. POP3 et projection donnent les mêmes "
             "effectifs par âge révolu (vérification 1)."))

# 4. Âges extrêmes
agg = aggregate_open_class(ref0, A)
ok4 = np.isclose(agg.sum(), ref0.sum(), atol=1e-6) and np.allclose(agg[:, A], ref0[:, A:].sum(axis=1))
qo = open_class_quotient(proj.mortality[:, :, i0], ref0, A)
rows.append((4, "Âges extrêmes", bool(ok4),
             f"Agrégation 100 à 104 + 105 et plus vers {A} et plus : somme conservée ({agg[:, A].sum():,.0f} personnes en "
             f"classe ouverte en {first}). Quotient de la classe ouverte (moyenne pondérée) : femmes {qo[0]:.3f}, hommes {qo[1]:.3f}. "
             "Convention : pour « 105 ans ou plus », quotient de l'âge atteint 106."))

# 5. Mortalité
y_last = first + n_flow - 1
q = proj.mortality[:, :, i0 : proj.year_index(y_last) + 1]
ok5 = bool(np.isfinite(q).all() and (q > 0).all() and (q <= 1).all())
rows.append((5, "Mortalité", ok5,
             f"Quotients par âge atteint de 0 à 120 ans, années {first} à {y_last} : {q.shape[2]} années, "
             f"valeurs dans ]0 ; 1] (min {q.min():.2e}, max {q.max():.3f})."))

# 6. Naissances
fert = year_params(proj, first, A).fertility
births_jan1 = float((fert * aggregate_open_class(n_init, A)[SEX_F]).sum())
births_avg = float(sum(proj.fertility[j, i0] * 0.5 * (proj.population[SEX_F, a_att - 1, i0] + proj.population[SEX_F, a_att, i0 + 1])
                       for j, a_att in enumerate(range(15, 51))))
b_ins = float(proj.births_total[i0])
rows.append((6, "Naissances", abs(births_jan1 / b_ins - 1) <= limit_total,
             f"Insee {first} : {b_ins:,.0f}. Moteur (femmes présentes au 1er janvier, cahier 3.7) : {births_jan1:,.0f} "
             f"({births_jan1 / b_ins - 1:+.2%}). Avec la moyenne des effectifs de début et de fin d'année "
             f"(pratique apparente de l'Insee) : {births_avg:,.0f} ({births_avg / b_ins - 1:+.3%}). "
             "Écart de convention documenté, non corrigé par un ajustement."))

date = dt.date.today().isoformat()
lines = [f"# Vérifications de comparabilité avec la projection Insee 2026 (scénario central)", "",
         f"Date de l'exécution : {date}. Généré par `scripts/check_comparability.py`.", "",
         "| N° | Vérification | Résultat | Détail |", "|---|---|---|---|"]
for n, name, ok, detail in rows:
    lines.append(f"| {n} | {name} | {'OK' if ok else '**ÉCHEC**'} | {detail} |")
failed = [r for r in rows if not r[2]]
lines += ["", "**Conclusion :** " + ("toutes les vérifications sont satisfaites : la comparaison (étape 10) peut être lancée."
          if not failed else "au moins une vérification échoue : ne pas lancer la comparaison, documenter l'écart.")]
out = R / "docs" / "comparabilite-insee.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\nÉcrit : {out}")
sys.exit(1 if failed else 0)
