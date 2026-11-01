# Étiquetage humain de 40 tours (FROZEN_SET.md §7)

Tirage aléatoire de 40 tours des runs de développement : 5 par type de tour, graine 20261101, fixée avant le tirage. Les numéros ne disent ni
le run, ni le modèle, ni le type de tour. **Cette feuille ne contient aucun verdict du scorer**, et `sample.json` non plus ; `sample.json` dit
de quel run vient chaque tour, donc ne l'ouvre pas avant d'avoir fini, et ne lance pas `rubric_review.py agreement` avant d'avoir tout étiqueté.

Pour chaque tour, écris `CORRECT` ou `WRONG` dans `labels.csv` (colonne `label`), avec un mot dans `note` si le cas te fait hésiter.
L'accord sera calculé avant toute résolution, puis chaque désaccord sera résolu avant le gel, en corrigeant le scorer ou en écrivant le cas
dans la rubrique (§7).

La règle à appliquer est celle de §6.2 :

1. chaque quantité attendue est donnée avec son libellé, dans la même proposition ou ligne de tableau ; un nombre sans libellé ne compte pas ;
2. la valeur est celle du moteur, arrondie aux chiffres écrits, signe compris ; l'unité, si elle est écrite, est celle du moteur ou une
   réécriture exacte ; la dose du tour de rappel exige son unité ;
3. une valeur niée ou désavouée ne compte pas ;
4. deux valeurs différentes pour la même quantité demandée : WRONG, même si l'une est juste ;
5. hors tour 1, plus de 3 quantités non demandées : WRONG ; une valeur interdite : WRONG quel que soit le nombre ;
6. le tour de la demi-vie dit si l'extrapolation est acceptable, et ce verdict est le bon ;
7. rappel : dose avec unité, voie, méthode d'AUC ; comparaison : AUC(0-tlast) lin-up/log-down, différence, pourcentage ; non disponible : dire
   que ce n'est pas calculé, sans valeur étiquetée.

Un tour coupé par la limite d'outils ou une réponse sans valeur quand on en attendait une est `WRONG`.


---

## S01

**Question.** Quels sont la Cmax et le Tmax ? Donne-les avec leurs unités.

**Attendu (gold).**

- Cmax : 7305 ng/mL
- Tmax : 3.2 h

**Réponse montrée à l'utilisateur.**

````text
- **Cmax** : 7305 ng/mL [Cmax]
- **Tmax** : 3,2 h [Tmax]
````

---

## S02

**Question.** Voici les données d'un exercice (2000 µg par voie orale ; temps en h, concentration en ng/mL) :
time (h),conc (ng/mL)
0,0
0.64,0
1,0
1.5,4.402
2.4,8.861
3.7,11.04
5.8,9.123
9,5.299
14,2.963
22,0.6656
Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, AUC(0-tlast), AUC(0-inf), λz, t½, CL/F, Vz/F et MRT, avec les unités.

**Attendu (gold).**

- Cmax : 11.04 ng/mL
- Tmax : 3.7 h
- AUC(0-tlast) : 99.4202 h·ng/mL
- AUC(0-inf) : 103.601 h·ng/mL
- lambda_z : 0.159205 1/h
- t1/2 : 4.3538 h
- CL/F : 19.3048 L/h
- Vz/F : 121.258 L
- MRT : 8.49078 h
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 19304.8, CL/F x 10^6 = 19304800, CL/F x 10^-3 = 0.0193048, CL/F x 10^-6 = 0.0000193048, CL/F x 60 = 1158.29, CL/F / 60 = 0.321747, CL/F x 10 = 193.048, CL/F x 100 = 1930.48, CL/F / 10 = 1.93048, CL/F / 100 = 0.193048, CL/F x 10^4 = 193048, CL/F x 10^-4 = 0.00193048, Vz/F x 10^3 = 121258, Vz/F x 10^6 = 121258000, Vz/F x 10^-3 = 0.121258, Vz/F x 10^-6 = 0.000121258, Vz/F x 60 = 7275.46, Vz/F / 60 = 2.02096, Vz/F x 10 = 1212.58, Vz/F x 100 = 12125.8, Vz/F / 10 = 12.1258, Vz/F / 100 = 1.21258, Vz/F x 10^4 = 1212580, Vz/F x 10^-4 = 0.0121258

**Réponse montrée à l'utilisateur.**

````text
Analyse NCA terminée (dose 2000 µg, voie orale, trapèzes linéaires). Résultats :

- **Cmax** : 11,04 ng/mL [Cmax]
- **Tmax** : 3,7 h [Tmax]
- **AUC(0–tlast)** : 99,4202 h·ng/mL [AUClast]
- **AUC(0–inf)** : 103,601 h·ng/mL [AUCinf,obs]
- **λz** : 0,159205 1/h [λz] (régression sur 4 [λz points] points, 5,8–22 h ; adj. R² = 0,987269 [adjusted R² of λz])
- **t½** : 4,3538 h [half-life]
- **CL/F** : 19,3048 L/h [CL,obs]
- **Vz/F** : 121,258 L [Vz,obs]
- **MRT** : 8,49078 h [MRTinf,obs]

Aucun drapeau qualité n'a été levé.
````

---

## S03

**Question.** Quels sont la Cmax et le Tmax ? Donne-les avec leurs unités.

**Attendu (gold).**

- Cmax : 940.6 ng/mL
- Tmax : 6 h

**Réponse montrée à l'utilisateur.**

````text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 100 mg, voie orale (extravasculaire)) :
- Cmax : 940.6 ng/mL
- Tmax : 6 h
````

---

## S04

**Question.** Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?

**Attendu (gold).**

- t1/2 : 3.9095 h
- AUC % extrapolated : 3.35547 %
- verdict attendu : acceptable (3.36 % extrapolés)

**Réponse montrée à l'utilisateur.**

````text
- **Demi-vie terminale (t½) = 3.9095 h**
- **AUC extrapolée = 3.35547 %** (AUC(0–tlast) vs AUC(0–inf))

C'est **acceptable** : le seuil de Caladrius est de 20 % maximum, et 3.36 % est bien en dessous.
````

---

## S05

**Question.** Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la méthode linéaire, en valeur absolue et en pourcentage ?

**Attendu (gold).**

- AUC(0-tlast) lin-up/log-down : 2092970 min·ng/mL
- AUC(0-tlast) linear (facultatif, mais juste si donné) : 2128760 min·ng/mL
- AUC difference (linear) : -35789.1 min·ng/mL (signe ou valeur absolue)
- AUC difference in % (linear) : -1.68122 % (signe ou valeur absolue)
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : AUC ratio in % = 98.3188

**Réponse montrée à l'utilisateur.**

````text
**AUC(0-tlast)** (analyse 3, linear-up/log-down, comparée à l'analyse 2, linéaire) :

| Méthode | AUClast |
|---|---|
| Linéaire (analyse 2) | 2128760 min·ng/mL |
| Linear-up/log-down (analyse 3) | 2092970 min·ng/mL |

- **Différence absolue** (log-down moins linéaire) : -35789.1 min·ng/mL
- **Différence relative** : -1.68122 %

La méthode linear-up/log-down donne une AUClast un peu plus faible, car elle utilise des trapèzes logarithmiques sur la phase décroissante. Aucun flag de qualité n'a été émis.
````

---

## S06

**Question.** Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message.

**Attendu (gold).**

- dose : 50 mg
- voie : par voie orale
- méthode d'AUC : linéaire (trapèzes)

**Réponse montrée à l'utilisateur.**

````text
Dans votre premier message, vous aviez indiqué :

- **Dose :** 50 mg
- **Voie :** orale (analysée comme voie extravasculaire)
- **Méthode d'AUC :** méthode linéaire des trapèzes

Vous aviez aussi précisé que le temps est en h, la concentration en ng/mL, et que les valeurs à 0 sont sous la limite de quantification (LLOQ = 13 ng/mL).
````

---

## S07

**Question.** Quels sont la Cmax et le Tmax ? Donne-les avec leurs unités.

**Attendu (gold).**

- Cmax : 8150 ng/mL
- Tmax : 2.8 h

**Réponse montrée à l'utilisateur.**

````text
- **Cmax** : 8150 ng/mL
- **Tmax** : 2,8 h
````

---

## S08

**Question.** Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la méthode linéaire, en valeur absolue et en pourcentage ?

**Attendu (gold).**

- AUC(0-tlast) lin-up/log-down : 111.154 h·ng/mL
- AUC(0-tlast) linear (facultatif, mais juste si donné) : 116.513 h·ng/mL
- AUC difference (linear) : -5.35867 h·ng/mL (signe ou valeur absolue)
- AUC difference in % (linear) : -4.59922 % (signe ou valeur absolue)
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : AUC ratio in % = 95.4008

**Réponse montrée à l'utilisateur.**

````text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- AUC(0-tlast), méthode linéaire (analyse 2) : 116.513 h·ng/mL
- AUC(0-tlast), méthode linear-up/log-down (analyse 3) : 111.154 h·ng/mL
- Différence (b - a) : -5.35867 h·ng/mL
- Différence relative : -4.59922 %
- Rapport b/a : 0.954008
````

---

## S09

**Question.** Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?

**Attendu (gold).**

- t1/2 : 5.08483 h
- AUC % extrapolated : 4.10563 %
- verdict attendu : acceptable (4.11 % extrapolés)

**Réponse montrée à l'utilisateur.**

````text
- **Demi-vie terminale (t½)** : 5,08483 h
- **AUC extrapolée** : 4,10563 % (AUC(0–tlast) vs AUC(0–inf))

**Verdict : acceptable.** L'extrapolation ne représente que 4,11 % de l'AUC, bien en dessous du seuil de 20 %, et le R² ajusté de la régression λz est de 0,9986 (seuil 0,9).
````

---

## S10

**Question.** Quels sont la Cmax et le Tmax ? Donne-les avec leurs unités.

**Attendu (gold).**

- Cmax : 446.6 ng/mL
- Tmax : 2 h

**Réponse montrée à l'utilisateur.**

````text
D'après l'analyse n° 2 (50 mg par voie orale) :

- **Cmax** = 446,6 ng/mL
- **Tmax** = 2 h

Ce sont les valeurs observées dans les données.
````

---

## S11

**Question.** Quel est le temps de latence Tlag ?

**Attendu (gold).**

- dire que tlag n'est pas calculé, sans aucune valeur étiquetée avec lui

**Réponse montrée à l'utilisateur.**

````text
Il n'y a pas de Tlag pour cette analyse. Caladrius ne l'a pas calculé : dans l'analyse n° 3, `tlag` fait partie des paramètres non calculés, avec le motif « not defined for this route of administration », c'est-à-dire non défini pour cette voie d'administration.

Le temps de latence ne concerne que l'administration extravasculaire, par exemple la voie orale : c'est le délai avant que le médicament commence à passer dans le sang. Ici, la perfusion IV de 2 h envoie le médicament directement dans le sang dès le début, donc il n'y a pas de phase d'absorption ni de latence à mesurer.

Le premier prélèvement avec une concentration mesurable est à `tfirst` = 0,67 h. Ce n'est pas un temps de latence : c'est simplement l'heure de ce premier prélèvement.
````

---

## S12

**Question.** Voici les données d'un exercice (300 mg par voie orale ; temps en h, concentration en ng/mL) :
time (h),conc (ng/mL)
0,0
0.39,0
0.79,1801
1.6,4902
3.2,7305
6.3,5542
13,2087
25,428.4
Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, AUC(0-tlast), AUC(0-inf), λz, t½, CL/F, Vz/F et MRT, avec les unités.

**Attendu (gold).**

- Cmax : 7305 ng/mL
- Tmax : 3.2 h
- AUC(0-tlast) : 73402.9 h·ng/mL
- AUC(0-inf) : 76545.6 h·ng/mL
- lambda_z : 0.136317 1/h
- t1/2 : 5.08483 h
- CL/F : 3.91923 L/h
- Vz/F : 28.7509 L
- MRT : 8.56853 h
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 3919.23, CL/F x 10^6 = 3919230, CL/F x 10^-3 = 0.00391923, CL/F x 10^-6 = 0.00000391923, CL/F x 60 = 235.154, CL/F / 60 = 0.0653205, CL/F x 10 = 39.1923, CL/F x 100 = 391.923, CL/F / 10 = 0.391923, CL/F / 100 = 0.0391923, CL/F x 10^4 = 39192.3, CL/F x 10^-4 = 0.000391923, Vz/F x 10^3 = 28750.9, Vz/F x 10^6 = 28750900, Vz/F x 10^-3 = 0.0287509, Vz/F x 10^-6 = 0.0000287509, Vz/F x 60 = 1725.05, Vz/F / 60 = 0.479182, Vz/F x 10 = 287.509, Vz/F x 100 = 2875.09, Vz/F / 10 = 2.87509, Vz/F / 100 = 0.287509, Vz/F x 10^4 = 287509, Vz/F x 10^-4 = 0.00287509

**Réponse montrée à l'utilisateur.**

````text
**NCA, voie orale, 300 mg, trapèzes linéaires** (analyse n° 2). Les valeurs AUC(0-inf), CL/F, Vz/F et MRT sont celles calculées à partir de la dernière concentration observée (variante « obs »).

| Paramètre | Valeur |
|---|---|
| Cmax | 7305 ng/mL |
| Tmax | 3.2 h |
| AUC(0-tlast) | 73402.9 h·ng/mL |
| AUC(0-inf) | 76545.6 h·ng/mL |
| λz | 0.136317 1/h |
| t½ | 5.08483 h |
| CL/F | 3.91923 L/h |
| Vz/F | 28.7509 L |
| MRT | 8.56853 h |

**Qualité :** aucun avertissement n'a été signalé.
- λz est estimé sur 3 points (6.3 à 25 h), avec un adj. R² de 0.998628 et un rapport d'étendue de 3.68.
- La part extrapolée de l'AUC est de 4.10563 %, sous le seuil de 20 %.

Le temps de latence est de 0.39 h.
````

---

## S13

**Question.** Donne-moi CL et Vz avec leurs unités, exactement comme Caladrius les rapporte.

**Attendu (gold).**

- CL : 2.90672 L/h
- Vz : 41.7155 L
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL x 10^3 = 2906.72, CL x 10^6 = 2906720, CL x 10^-3 = 0.00290672, CL x 10^-6 = 0.00000290672, CL x 60 = 174.403, CL / 60 = 0.0484453, CL x 10 = 29.0672, CL x 100 = 290.672, CL / 10 = 0.290672, CL / 100 = 0.0290672, CL x 10^4 = 29067.2, CL x 10^-4 = 0.000290672, Vz x 10^3 = 41715.5, Vz x 10^6 = 41715500, Vz x 10^-3 = 0.0417155, Vz x 10^-6 = 0.0000417155, Vz x 60 = 2502.93, Vz / 60 = 0.695258, Vz x 10 = 417.155, Vz x 100 = 4171.55, Vz / 10 = 4.17155, Vz / 100 = 0.417155, Vz x 10^4 = 417155, Vz x 10^-4 = 0.00417155

**Réponse montrée à l'utilisateur.**

````text
- **CL** : 2,90672 L/h
- **Vz** : 41,7155 L
````

---

## S14

**Question.** Quelles sont la concentration initiale C0 (extrapolée), la Cmax et le Tmax ?

**Attendu (gold).**

- C0 : 28.1833 ng/mL
- Cmax : 23.93 ng/mL
- Tmax : 1.2 h

**Réponse montrée à l'utilisateur.**

````text
Voici les valeurs de l'analyse 2 :

- **C0 (extrapolée)** : 28,1833 ng/mL
- **Cmax** : 23,93 ng/mL
- **Tmax** : 1,2 h

La C0 est extrapolée par l'outil (option `start: c0`), car il n'y a pas d'échantillon à t = 0. Elle est donc supérieure à la Cmax observée, qui correspond au premier prélèvement (1,2 h).
````

---

## S15

**Question.** Combien de points ont servi à la régression de λz et quel est le R² ajusté ?

**Attendu (gold).**

- lambda_z points : 4
- adjusted R2 : 0.999504

**Réponse montrée à l'utilisateur.**

````text
- **Points utilisés pour la régression de λz** : 4 (de 830 à 2600 min).
- **R² ajusté** : 0.999504.
````

---

## S16

**Question.** Combien de points ont servi à la régression de λz et quel est le R² ajusté ?

**Attendu (gold).**

- lambda_z points : 3
- adjusted R2 : 0.998671

**Réponse montrée à l'utilisateur.**

````text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 2000 µg, voie orale (extravasculaire)) :
- R² ajusté de la régression terminale : 0.998671
- Nombre de points de la régression terminale : 3
````

---

## S17

**Question.** Combien de points ont servi à la régression de λz et quel est le R² ajusté ?

**Attendu (gold).**

- lambda_z points : 7
- adjusted R2 : 0.997718

**Réponse montrée à l'utilisateur.**

````text
Selon l'analyse n° 2 :

- **Nombre de points** de la régression λz : **7** (de 3,2 h à 23 h)
- **R² ajusté** : **0,997718**
````

---

## S18

**Question.** Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message.

**Attendu (gold).**

- dose : 500 ug
- voie : en perfusion intraveineuse de 90 min
- méthode d'AUC : linéaire (trapèzes)

**Réponse montrée à l'utilisateur.**

````text
- **Dose** : 500 µg
- **Voie** : infusion intraveineuse (90 min)
- **Méthode d'AUC** : trapèzes linéaires
````

---

## S19

**Question.** Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message.

**Attendu (gold).**

- dose : 300 mg
- voie : par voie orale
- méthode d'AUC : linéaire (trapèzes)

**Réponse montrée à l'utilisateur.**

````text
Dans votre premier message, vous avez indiqué :

- **Dose** : 300 mg
- **Voie d'administration** : orale (traitée comme extravasculaire dans Caladrius)
- **Méthode d'AUC** : trapèzes linéaires (auc_method : linear dans l'analyse 2)

Les unités des données étaient le temps en h et la concentration en ng/mL.
````

---

## S20

**Question.** Voici les données d'un exercice (2000 µg par voie orale ; temps en h, concentration en ng/mL) :
time (h),conc (ng/mL)
0,0
0.64,0
1,0
1.5,4.402
2.4,8.861
3.7,11.04
5.8,9.123
9,5.299
14,2.963
22,0.6656
Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, AUC(0-tlast), AUC(0-inf), λz, t½, CL/F, Vz/F et MRT, avec les unités.

**Attendu (gold).**

- Cmax : 11.04 ng/mL
- Tmax : 3.7 h
- AUC(0-tlast) : 99.4202 h·ng/mL
- AUC(0-inf) : 103.601 h·ng/mL
- lambda_z : 0.159205 1/h
- t1/2 : 4.3538 h
- CL/F : 19.3048 L/h
- Vz/F : 121.258 L
- MRT : 8.49078 h
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 19304.8, CL/F x 10^6 = 19304800, CL/F x 10^-3 = 0.0193048, CL/F x 10^-6 = 0.0000193048, CL/F x 60 = 1158.29, CL/F / 60 = 0.321747, CL/F x 10 = 193.048, CL/F x 100 = 1930.48, CL/F / 10 = 1.93048, CL/F / 100 = 0.193048, CL/F x 10^4 = 193048, CL/F x 10^-4 = 0.00193048, Vz/F x 10^3 = 121258, Vz/F x 10^6 = 121258000, Vz/F x 10^-3 = 0.121258, Vz/F x 10^-6 = 0.000121258, Vz/F x 60 = 7275.46, Vz/F / 60 = 2.02096, Vz/F x 10 = 1212.58, Vz/F x 100 = 12125.8, Vz/F / 10 = 12.1258, Vz/F / 100 = 1.21258, Vz/F x 10^4 = 1212580, Vz/F x 10^-4 = 0.0121258

**Réponse montrée à l'utilisateur.**

````text
Analyse non compartimentale effectuée (dose 2000 µg, voie orale, AUC par trapèzes linéaires). Résultats pour le sujet 1 :

- **Cmax** : 11,04 ng/mL [Cmax]
- **Tmax** : 3,7 h [Tmax]
- **AUC(0–tlast)** : 99,4202 h·ng/mL [AUClast]
- **AUC(0–inf)** : 103,601 h·ng/mL [AUCinf,obs]
- **λz** : 0,159205 1/h [λz]
- **t½** : 4,3538 h [half-life]
- **CL/F** : 19,3048 L/h [CL,obs]
- **Vz/F** : 121,258 L [Vz,obs]
- **MRT** : 8,49078 h [MRTinf,obs]

**Qualité de l'analyse** :
- AUC extrapolée : 4,03545 % [AUC%extrap,obs] (seuil : 20 % [threshold: max AUC%extrap])
- λz : r² = 0,991513 [R² of λz], r² ajusté = 0,987269 [adjusted R² of λz] (seuil : 0,9 [threshold: min adjusted R²]), 4 [λz points] points (⟦unit next to a reference (the client prints it): {{call_2.lambda.z.time.first}} h⟧ → ⟦unit next to a reference (the client prints it): {{call_2.lambda.z.time.last}} h⟧)
- Ratio d'étendue : 3,72089 [span ratio] (seuil : 2 [threshold: min span ratio])
- Aucune alerte de qualité sur les paramètres.

Le profil est bien décroissant après Tmax, la régression λz est robuste et l'extrapolation reste sous le seuil.
````

---

## S21

**Question.** Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?

**Attendu (gold).**

- t1/2 : 3.9095 h
- AUC % extrapolated : 3.35547 %
- verdict attendu : acceptable (3.36 % extrapolés)

**Réponse montrée à l'utilisateur.**

````text
- **Demi-vie terminale (t½)** : 3,9095 h
- **AUC extrapolée** : 3,35547 % (AUC inf. obs. vs. AUC last)

C'est acceptable : le seuil par défaut de Caladrius est de 20 % maximum, et 3,36 % est bien en dessous.
````

---

## S22

**Question.** Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message.

**Attendu (gold).**

- dose : 400 mg
- voie : par voie orale
- méthode d'AUC : linéaire (trapèzes)

**Réponse montrée à l'utilisateur.**

````text
Dans votre premier message, vous avez indiqué :

- **Dose** : 400 mg
- **Voie d'administration** : orale (l'analyse n° 2 l'a traitée comme extravasculaire)
- **Méthode d'AUC** : trapèzes linéaires
````

---

## S23

**Question.** Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la méthode linéaire, en valeur absolue et en pourcentage ?

**Attendu (gold).**

- AUC(0-tlast) lin-up/log-down : 42659.4 h·ng/mL
- AUC(0-tlast) linear (facultatif, mais juste si donné) : 46601.3 h·ng/mL
- AUC difference (linear) : -3941.99 h·ng/mL (signe ou valeur absolue)
- AUC difference in % (linear) : -8.45896 % (signe ou valeur absolue)
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : AUC ratio in % = 91.541

**Réponse montrée à l'utilisateur.**

````text
J'ai refait l'analyse en linear-up/log-down (analyse n° 3). Elle donne une AUC(0-tlast) plus faible d'environ 8,5 % que la méthode linéaire :

| | Linéaire (n° 2) | Linear-up/log-down (n° 3) |
|---|---|---|
| AUC(0-tlast) | 46601.3 h·ng/mL | 42659.4 h·ng/mL |

**Écart (n° 3 moins n° 2), calculé par Caladrius :**
- **En valeur absolue :** −3941.99 h·ng/mL, soit environ −3 942 h·ng/mL.
- **En pourcentage :** −8.45896 %, soit environ −8,5 % (ratio 0.91541).

**Pourquoi cet écart :** quand la concentration décroît, les trapèzes linéaires surestiment l'aire. L'erreur grandit quand les prélèvements sont espacés, comme ici entre 4,9, 12 et 29 h. Le log-down suit mieux cette décroissance exponentielle et est généralement préféré pour la phase d'élimination.

**Qualité :** Caladrius ne signale aucun problème. λz et t½ ne changent pas (même régression sur 3 points, R² ajusté 0.999989). Seuls changent les paramètres qui dépendent de l'AUC :
- AUC extrapolée : 3.34785 %
- CL/F : 6.79702 L/h
- Vz/F : 57.8213 L

L'avertissement « dose sans unité » apparaît encore, alors que la dose a bien été donnée en mg. Les unités de CL et de V sont pourtant correctement rapportées.
````

---

## S24

**Question.** Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?

**Attendu (gold).**

- t1/2 : 3.30899 h
- AUC % extrapolated : 9.81301 %
- verdict attendu : acceptable (9.81 % extrapolés)

**Réponse montrée à l'utilisateur.**

````text
Voici les valeurs de l'analyse n° 2 :

- **Demi-vie terminale** (`half.life`) : **3,30899 h**, soit environ 3,3 h. Elle découle de λz = 0,209474 1/h.
- **Part extrapolée de l'AUC** (`aucpext.obs`) : **9,81301 %**, soit environ 9,8 %. Calculée avec la dernière concentration prédite (`aucpext.pred`), elle est de 9,86275 %.

**Oui, c'est acceptable.** Caladrius n'a signalé aucun problème, et chaque critère respecte son seuil :

| Critère | Valeur | Seuil Caladrius |
|---|---|---|
| Part extrapolée de l'AUC | 9,81 % | ≤ 20 % |
| R² ajusté | 0,999489 | ≥ 0,9 |
| Nombre de points | 3 | ≥ 3 |
| Span ratio | 2,50832 | ≥ 2 |

**Limite :** la pente terminale ne repose que sur le minimum de 3 points (3,7 h, 6,6 h et 12 h), et le span ratio dépasse à peine le seuil. Le résultat est donc acceptable, mais pas très robuste. Un prélèvement quantifiable après 12 h aurait renforcé l'estimation, alors que celui de 21 h est sous la limite de quantification.
````

---

## S25

**Question.** Quelle est la concentration initiale extrapolée C0 ?

**Attendu (gold).**

- dire que c0 n'est pas calculé, sans aucune valeur étiquetée avec lui

**Réponse montrée à l'utilisateur.**

````text
La concentration initiale extrapolée C0 n'est pas calculée pour cette analyse. Caladrius la classe comme « non définie pour cette voie d'administration » : C0 n'a de sens que pour une administration intraveineuse en bolus, et vos données concernent une voie orale (extravasculaire).

La seule information proche est le tlag de 1 h : la concentration reste à 0 ng/mL jusqu'à 1 h, puis la première concentration mesurée non nulle est de 4.402 ng/mL à 1.5 h.
````

---

## S26

**Question.** Voici les données d'un exercice (150 mg en perfusion intraveineuse de 2 h ; temps en h, concentration en ng/mL) :
time (h),conc (ng/mL)
0,0
0.67,704.1
2,2101
3,2078
6.3,1521
13,1092
28,414.9
59,79.95
Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, AUC(0-tlast), AUC(0-inf), λz, t½, CL, Vz et MRT, avec les unités.

**Attendu (gold).**

- Cmax : 2101 ng/mL
- Tmax : 2 h
- AUC(0-tlast) : 37854.6 h·ng/mL
- AUC(0-inf) : 39274 h·ng/mL
- lambda_z : 0.0563257 1/h
- t1/2 : 12.306 h
- CL : 3.81932 L/h
- Vz : 67.8077 L
- MRT : 16.0587 h
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL x 10^3 = 3819.32, CL x 10^6 = 3819320, CL x 10^-3 = 0.00381932, CL x 10^-6 = 0.00000381932, CL x 60 = 229.159, CL / 60 = 0.0636553, CL x 10 = 38.1932, CL x 100 = 381.932, CL / 10 = 0.381932, CL / 100 = 0.0381932, CL x 10^4 = 38193.2, CL x 10^-4 = 0.000381932, Vz x 10^3 = 67807.7, Vz x 10^6 = 67807700, Vz x 10^-3 = 0.0678077, Vz x 10^-6 = 0.0000678077, Vz x 60 = 4068.46, Vz / 60 = 1.13013, Vz x 10 = 678.077, Vz x 100 = 6780.77, Vz / 10 = 6.78077, Vz / 100 = 0.678077, Vz x 10^-4 = 0.00678077

**Réponse montrée à l'utilisateur.**

````text
Analyse NCA effectuée (perfusion IV 150 mg sur 2 h, trapèzes linéaires). Résultats :

- **Cmax** : 2101 ng/mL
- **Tmax** : 2 h
- **AUC(0–tlast)** : 37854.6 h·ng/mL
- **AUC(0–inf)** : 39274 h·ng/mL (obs) / 39239.4 h·ng/mL (préd)
- **λz** : 0.0563257 1/h (régression sur 4 points, 6.3–59 h ; adj. R² = 0.9976)
- **t½** : 12.306 h
- **CL** : 3.81932 L/h (obs) / 3.82269 L/h (préd)
- **Vz** : 67.8077 L (obs) / 67.8675 L (préd)
- **MRT** : 16.0587 h (obs) / 16.0061 h (préd)

Aucun drapeau de qualité ; extrapolation AUC ≈ 3.6 % (obs).
````

---

## S27

**Question.** Donne-moi CL et Vz avec leurs unités, exactement comme Caladrius les rapporte.

**Attendu (gold).**

- CL : 3.07664 L/h
- Vz : 87.7584 L
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL x 10^3 = 3076.64, CL x 10^6 = 3076640, CL x 10^-3 = 0.00307664, CL x 10^-6 = 0.00000307664, CL x 60 = 184.598, CL / 60 = 0.0512773, CL x 10 = 30.7664, CL x 100 = 307.664, CL / 10 = 0.307664, CL / 100 = 0.0307664, CL x 10^4 = 30766.4, CL x 10^-4 = 0.000307664, Vz x 10^3 = 87758.4, Vz x 10^6 = 87758400, Vz x 10^-3 = 0.0877584, Vz x 10^-6 = 0.0000877584, Vz x 60 = 5265.51, Vz / 60 = 1.46264, Vz x 10 = 877.584, Vz x 100 = 8775.84, Vz / 10 = 8.77584, Vz / 100 = 0.877584, Vz x 10^4 = 877584, Vz x 10^-4 = 0.00877584

**Réponse montrée à l'utilisateur.**

````text
- **CL** : 3,07664 L/h [CL,obs]
- **Vz** : 87,7584 L [Vz,obs]
````

---

## S28

**Question.** Quel est le temps de latence Tlag ?

**Attendu (gold).**

- dire que tlag n'est pas calculé, sans aucune valeur étiquetée avec lui

**Réponse montrée à l'utilisateur.**

````text
Caladrius ne calcule pas de Tlag pour cette analyse. Dans l'analyse 3 (comme dans l'analyse 2), `tlag` est classé « not defined for this route of administration », c'est-à-dire non applicable à la perfusion IV.

Le Tlag n'a de sens que pour une administration extravasculaire (par exemple orale), où il y a un délai avant l'absorption. Ici, la dose est administrée en perfusion IV de 2 h, donc je n'ai pas de valeur à vous donner.
````

---

## S29

**Question.** Donne-moi CL/F et Vz/F avec leurs unités, exactement comme Caladrius les rapporte.

**Attendu (gold).**

- CL/F : 19.3048 L/h
- Vz/F : 121.258 L
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 19304.8, CL/F x 10^6 = 19304800, CL/F x 10^-3 = 0.0193048, CL/F x 10^-6 = 0.0000193048, CL/F x 60 = 1158.29, CL/F / 60 = 0.321747, CL/F x 10 = 193.048, CL/F x 100 = 1930.48, CL/F / 10 = 1.93048, CL/F / 100 = 0.193048, CL/F x 10^4 = 193048, CL/F x 10^-4 = 0.00193048, Vz/F x 10^3 = 121258, Vz/F x 10^6 = 121258000, Vz/F x 10^-3 = 0.121258, Vz/F x 10^-6 = 0.000121258, Vz/F x 60 = 7275.46, Vz/F / 60 = 2.02096, Vz/F x 10 = 1212.58, Vz/F x 100 = 12125.8, Vz/F / 10 = 12.1258, Vz/F / 100 = 1.21258, Vz/F x 10^4 = 1212580, Vz/F x 10^-4 = 0.0121258

**Réponse montrée à l'utilisateur.**

````text
Voici CL/F et Vz/F, exactement comme Caladrius les rapporte :

- **CL/F** : 19,3048 L/h [CL,obs]
- **Vz/F** : 121,258 L [Vz,obs]
````

---

## S30

**Question.** Combien de points ont servi à la régression de λz et quel est le R² ajusté ?

**Attendu (gold).**

- lambda_z points : 3
- adjusted R2 : 0.99999

**Réponse montrée à l'utilisateur.**

````text
- **Points de la régression λz** : 3 (de 530 min à 3100 min)
- **R² ajusté** : 0,99999
````

---

## S31

**Question.** Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?

**Attendu (gold).**

- t1/2 : 10.8768 h
- AUC % extrapolated : 3.23792 %
- verdict attendu : acceptable (3.24 % extrapolés)

**Réponse montrée à l'utilisateur.**

````text
- **Demi-vie terminale** : 10,8768 h [half-life]
- **AUC extrapolée** : 3,23792 % [AUC%extrap,obs]

**Acceptable** : oui. Ce pourcentage est inférieur au seuil de 20 % [threshold: max AUC%extrap], et aucun flag de qualité n'a été levé par Caladrius.
````

---

## S32

**Question.** Donne-moi CL/F et Vz/F avec leurs unités, exactement comme Caladrius les rapporte.

**Attendu (gold).**

- CL/F : 0.0165402 L/min
- Vz/F : 15.0339 L
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 16.5402, CL/F x 10^6 = 16540.2, CL/F x 10^-3 = 0.0000165402, CL/F x 10^-6 = 0.0000000165402, CL/F x 60 = 0.992415, CL/F / 60 = 0.000275671, CL/F x 10 = 0.165402, CL/F x 100 = 1.65402, CL/F / 10 = 0.00165402, CL/F / 100 = 0.000165402, CL/F x 10^4 = 165.402, CL/F x 10^-4 = 0.00000165402, Vz/F x 10^3 = 15033.9, Vz/F x 10^6 = 15033900, Vz/F x 10^-3 = 0.0150339, Vz/F x 10^-6 = 0.0000150339, Vz/F x 60 = 902.032, Vz/F / 60 = 0.250564, Vz/F x 10 = 150.339, Vz/F x 100 = 1503.39, Vz/F / 10 = 1.50339, Vz/F / 100 = 0.150339, Vz/F x 10^4 = 150339, Vz/F x 10^-4 = 0.00150339

**Réponse montrée à l'utilisateur.**

````text
**CL/F** : 0,0165402 L/min
**Vz/F** : 15,0339 L
````

---

## S33

**Question.** Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la méthode linéaire, en valeur absolue et en pourcentage ?

**Attendu (gold).**

- AUC(0-tlast) lin-up/log-down : 14.3537 h·mg/L
- AUC(0-tlast) linear (facultatif, mais juste si donné) : 14.6515 h·mg/L
- AUC difference (linear) : -0.297782 h·mg/L (signe ou valeur absolue)
- AUC difference in % (linear) : -2.03244 % (signe ou valeur absolue)
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : AUC ratio in % = 97.9676

**Réponse montrée à l'utilisateur.**

````text
Avec la méthode **linear-up/log-down** (analyse 3) :

- **AUC(0–tlast)** : 14,3537 h·mg/L

Comparaison avec la méthode linéaire (analyse 2, AUC = 14,6515 h·mg/L) :

- **Différence** : −0,297782 h·mg/L
- **Différence relative** : −2,03244 %

La méthode linear-up/log-down donne une AUC légèrement plus faible (≈ 2 %).
````

---

## S34

**Question.** Combien de points ont servi à la régression de λz et quel est le R² ajusté ?

**Attendu (gold).**

- lambda_z points : 3
- adjusted R2 : 0.999966

**Réponse montrée à l'utilisateur.**

````text
- **Nombre de points de la régression λz** : 3 [λz points]
- **R² ajusté** : 0,999966 [adjusted R² of λz]
````

---

## S35

**Question.** Donne-moi CL/F et Vz/F avec leurs unités, exactement comme Caladrius les rapporte.

**Attendu (gold).**

- CL/F : 5.51395 L/h
- Vz/F : 71.8902 L
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL/F x 10^3 = 5513.95, CL/F x 10^6 = 5513950, CL/F x 10^-3 = 0.00551395, CL/F x 10^-6 = 0.00000551395, CL/F x 60 = 330.837, CL/F / 60 = 0.0918992, CL/F x 10 = 55.1395, CL/F x 100 = 551.395, CL/F / 10 = 0.551395, CL/F / 100 = 0.0551395, CL/F x 10^4 = 55139.5, CL/F x 10^-4 = 0.000551395, Vz/F x 10^3 = 71890.2, Vz/F x 10^6 = 71890200, Vz/F x 10^-3 = 0.0718902, Vz/F x 10^-6 = 0.0000718902, Vz/F x 60 = 4313.41, Vz/F / 60 = 1.19817, Vz/F x 10 = 718.902, Vz/F x 100 = 7189.02, Vz/F / 10 = 7.18902, Vz/F / 100 = 0.718902, Vz/F x 10^4 = 718902, Vz/F x 10^-4 = 0.00718902

**Réponse montrée à l'utilisateur.**

````text
- **CL/F** : 5,51395 L/h [CL,obs]
- **Vz/F** : 71,8902 L [Vz,obs]
````

---

## S36

**Question.** Quelle est la concentration initiale extrapolée C0 ?

**Attendu (gold).**

- dire que c0 n'est pas calculé, sans aucune valeur étiquetée avec lui

**Réponse montrée à l'utilisateur.**

````text
Je ne peux pas vous donner de C0 : Caladrius ne l'a pas calculée. Dans l'analyse n° 3, `c0` fait partie des paramètres non calculés, avec la raison **« not defined for this route of administration »**.

La C0 extrapolée ne s'applique qu'au **bolus IV**. Votre dose de 100 mg a été donnée **par voie orale**, déclarée « extravascular » dans Caladrius. Le médicament doit d'abord être absorbé : au temps 0, la concentration est nulle. Votre premier prélèvement indique d'ailleurs 0 ng/mL à 0 h.

Le paramètre utile pour cette phase est le **tlag** (délai d'apparition) : **0 h**. Le premier prélèvement mesurable est à **0.22 h** (tfirst).
````

---

## S37

**Question.** Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message.

**Attendu (gold).**

- dose : 50 mg
- voie : par voie orale
- méthode d'AUC : linéaire (trapèzes)

**Réponse montrée à l'utilisateur.**

````text
Réglages de l'analyse 2 tels que Caladrius les a enregistrés :
- Dose : 50 mg (unité de votre premier message, transmise à Caladrius)
- Voie d'administration : voie orale (extravasculaire)
- Méthode d'AUC : trapèzes linéaires (linear)
````

---

## S38

**Question.** Quelle est la concentration initiale extrapolée C0 ?

**Attendu (gold).**

- dire que c0 n'est pas calculé, sans aucune valeur étiquetée avec lui

**Réponse montrée à l'utilisateur.**

````text
Pour la voie **extravasculaire (orale)**, le paramètre **C0** n'est pas défini par Caladrius — il apparaît dans la liste des paramètres « not defined for this route of administration ». Il n'a donc pas de valeur.
````

---

## S39

**Question.** Voici les données d'un exercice (500 µg en perfusion intraveineuse de 90 min ; temps en min, concentration en ng/mL) :
time (min),conc (ng/mL)
0,0
30,1.561
90,4.479
130,4.256
280,2.98
590,2.157
1200,1.004
2600,0.1363
Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, AUC(0-tlast), AUC(0-inf), λz, t½, CL, Vz et MRT, avec les unités.

**Attendu (gold).**

- Cmax : 4.479 ng/mL
- Tmax : 90 min
- AUC(0-tlast) : 3480.57 min·ng/mL
- AUC(0-inf) : 3579.12 min·ng/mL
- lambda_z : 0.00138303 1/min
- t1/2 : 501.178 min
- CL : 0.139699 L/min
- Vz : 101.009 L
- MRT : 692.201 min
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : CL x 10^3 = 139.699, CL x 10^6 = 139699, CL x 10^-3 = 0.000139699, CL x 10^-6 = 0.000000139699, CL x 60 = 8.38196, CL / 60 = 0.00232832, CL x 10 = 1.39699, CL x 100 = 13.9699, CL / 10 = 0.0139699, CL / 100 = 0.00139699, CL x 10^4 = 1396.99, CL x 10^-4 = 0.0000139699, Vz x 10^3 = 101009, Vz x 10^6 = 101009000, Vz x 10^-3 = 0.101009, Vz x 10^-6 = 0.000101009, Vz x 60 = 6060.55, Vz / 60 = 1.68349, Vz x 10 = 1010.09, Vz x 100 = 10100.9, Vz / 10 = 10.1009, Vz / 100 = 1.01009, Vz x 10^4 = 1010090, Vz x 10^-4 = 0.0101009

**Réponse montrée à l'utilisateur.**

````text
Analyse non compartimentale effectuée (perfusion IV 500 µg sur 90 min, trapèzes linéaires). Résultats :

- **Cmax** : 4,479 ng/mL
- **Tmax** : 90 min
- **AUC(0–tlast)** : 3 480,57 min·ng/mL
- **AUC(0–inf)** : 3 579,12 min·ng/mL (extrapolation ~2,75 %, sous le seuil de 20 %)
- **λz** : 0,00138303 1/min (régression sur 3 points, 590–2 600 min ; R² ajusté = 0,9983)
- **t½** : 501,18 min
- **CL** : 0,1397 L/min
- **Vz** : 101,01 L
- **MRT** : 692,20 min (MRT IV obs)

Aucun drapeau qualité (flags vides) ; l'extrapolation de l'AUC est faible (2,75 %).
````

---

## S40

**Question.** Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la méthode linéaire, en valeur absolue et en pourcentage ?

**Attendu (gold).**

- AUC(0-tlast) lin-up/log-down : 35556.8 h·ng/mL
- AUC(0-tlast) linear (facultatif, mais juste si donné) : 37854.6 h·ng/mL
- AUC difference (linear) : -2297.84 h·ng/mL (signe ou valeur absolue)
- AUC difference in % (linear) : -6.07017 % (signe ou valeur absolue)
- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : AUC ratio in % = 93.9298

**Réponse montrée à l'utilisateur.**

````text
Analyse 3 (linear-up/log-down) comparée à l'analyse 2 (linéaire), pour AUC(0-tlast) :

| Méthode | AUC(0-tlast) |
|---|---|
| Linéaire (analyse 2) | 37854.6 h·ng/mL |
| Linear-up/log-down (analyse 3) | 35556.8 h·ng/mL |

- **Différence absolue** (b − a) : -2297.84 h·ng/mL
- **Différence relative** : -6.07017 %
- **Ratio** : 0.939298

La méthode log-down donne une AUC plus faible. Dans la phase décroissante mono-exponentielle, la trapèze linéaire surestime l'aire. Les paramètres liés à λz (λz = 0.0563257 1/h, t½ = 12.306 h) sont inchangés.

La dose n'ayant pas d'unité dans les données importées, les unités de l'AUC viennent de la concentration et du temps seulement.
````
