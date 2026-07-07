# Analyse et prevision des ventes Walmart

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![Statsmodels](https://img.shields.io/badge/Statsmodels-SARIMA-8CAAE6)
![License](https://img.shields.io/badge/License-MIT-green)

Analyse complete et modelisation predictive des ventes hebdomadaires de 45 magasins Walmart (2010-2012), du nettoyage des donnees en Python jusqu'a un dashboard Power BI interactif de 5 pages.

---

## Apercu du projet

Ce projet part d'un jeu de donnees Kaggle de ventes retail et le transforme en deux livrables complementaires :

1. **Dashboard Power BI (5 pages)** : reporting interactif des ventes par magasin, type, rayon, periode et facteurs externes.
2. **Modele de prevision SARIMA** : projection des ventes totales sur 26 semaines, validee sur 6 mois hors echantillon (MAPE 2,2 %).

Source des donnees : [Walmart Recruiting - Store Sales Forecasting](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting) (Kaggle).

---

## Contexte metier

Walmart cherche a prevoir les ventes hebdomadaires par rayon et par magasin. Plusieurs elements donnent au probleme sa difficulte reelle :

- Le distributeur lance des operations promotionnelles (markdowns) avant quatre grandes periodes : Super Bowl, Labor Day, Thanksgiving et Noel.
- Dans la competition d'origine, les semaines feriees comptent **cinq fois plus** dans le score (metrique WMAE), car ce sont les semaines a fort enjeu commercial.
- Les donnees de promotions (MarkDown1 a 5) ne sont disponibles qu'a partir de novembre 2011, et de facon incomplete. Ce trou dans les donnees est assume et documente plus bas.

---

## Apercu du dashboard

### Vue d'ensemble
![Vue d'ensemble](img/01_vue_ensemble.png)

### Analyse par magasin
![Analyse par magasin](img/02_analyse_magasin.png)

### Facteurs externes
![Facteurs externes](img/03_facteurs_externes.png)

### Prevision SARIMA
![Prevision](img/04_prevision.png)

### Synthese
![Synthese](img/05_synthese.png)
---

## Donnees

| Caracteristique | Detail |
|---|---|
| Source | Kaggle, Walmart Recruiting Store Sales Forecasting |
| Grain | Magasin x Rayon x Semaine |
| Periode | Fevrier 2010 a octobre 2012 (143 semaines) |
| Perimetre | 45 magasins, environ 81 rayons, environ 420 000 lignes |
| Types de magasins | A (grands), B (moyens), C (petits) |
| Variables de contexte | Temperature, prix du carburant, CPI (inflation), taux de chomage, markdowns |

Fichiers d'origine : `stores.csv` (dimension magasins), `train.csv` (ventes avec cible), `test.csv` (ventes a predire, sans cible), `features.csv` (contexte regional).

---

## Architecture en 3 couches

```
data/raw/          CSV bruts Kaggle (non verses dans Git)
    |
    v
[Couche 1] src/clean.py
    |              Audit qualite, nettoyage, modele en etoile
    v
data/processed/    dim_stores.csv | fact_sales.csv | fact_features.csv
    |
    v
[Couche 2] src/prepare_forecast.py  -->  forecast_total.csv
           src/forecast.py          -->  forecast_results.csv
    |              Serie temporelle agregee + SARIMA(0,1,1)(0,1,1,52)
    v
[Couche 3] reports/walmart_sales.pbix
           Dashboard Power BI (5 pages)
```

---

## Comment reproduire

### Prerequis

```bash
git clone https://github.com/liliandoublet/Power-Bi-showcase.git
cd Power-Bi-showcase
pip install -r requirements.txt
```

Telecharger les CSV Kaggle et les placer dans `data/raw/` : `stores.csv`, `train.csv`, `features.csv`, `test.csv`.

### Execution dans l'ordre

```bash
# 1. Nettoyage, audit qualite et modele en etoile
python src/clean.py

# 2. Agregation en serie temporelle hebdomadaire
python src/prepare_forecast.py

# 3. Prevision SARIMA (environ 2 a 3 minutes)
python src/forecast.py
```

Les fichiers produits dans `data/processed/` sont prets a etre charges dans Power BI (modele en etoile, relations sur Store et Date).

---

## Le dashboard (5 pages)

| Page | Contenu |
|---|---|
| Vue d'ensemble | KPIs globaux, ventes par type, repartition du parc, courbe de saisonnalite |
| Analyse par magasin | Relation taille / ventes, efficacite au m2, classement, table detaillee |
| Facteurs externes | Ventes vs temperature, carburant, chomage, contexte economique, effet des feries |
| Prevision | Reel vs prevision SARIMA, projection a 6 mois, MAPE |
| Synthese | Chiffres cles et enseignements formules en langage metier |

---

## Mesures DAX principales

| Nom de la Mesure | A quoi elle répond |
|---|---|
| `Ventes Totales` | Chiffre d'affaires cumule (mesure de base) |
| `Uplift jours feries` | Surcroit de ventes des semaines feriees vs normales (+7,84 %) |
| `Ventes par m2` | Efficacite d'un magasin rapportee a sa surface |
| `% du Total` | Part de chaque type ou magasin dans le total |
| `Prevision Moyenne a Venir` | Niveau moyen des ventes projetees sur 6 mois |

---

## Insights cles

- **Concentration** : les magasins de **type A generent 64,3 % des ventes** (contre 29,7 % pour les B et 6 % pour les C), alors qu'ils representent 22 magasins sur 45. La valeur est fortement concentree.
- **Efficacite au m2** : les type A dominent en volume grace a leur taille, mais **rapporte a la surface, plusieurs magasins de type B sont plus efficaces**. La performance brute ne reflete pas le rendement operationnel.
- **Jours fériés** : une semaine fériée genere **+7,84 % de ventes** en moyenne, un levier pour la planification des stocks et du personnel.
- **Facteurs externes** : aucune variable de contexte prise isolement (meteo, carburant, chomage, inflation) n'explique fortement les ventes au niveau agrege. Ces variables refletent surtout l'evolution macroeconomique de la periode.
- **Prevision** : le modele SARIMA(0,1,1)(0,1,1,52) atteint un **MAPE de 2,2 %** sur 26 semaines hors echantillon.

---

## Choix methodologiques

Ces choix sont assumes et defendables, ils constituent une part importante de la valeur du projet.

- **Agregation au niveau total pour la prevision** : le grain magasin x rayon represente environ 3 000 series tres bruitees. La prevision est donc realisee sur les ventes totales, une maille lisible et stable. Une version par magasin est identifiee comme amelioration future.
- **Ventes negatives conservees** : environ 0,3 % des lignes ont des ventes negatives (retours superieurs aux ventes). Elles sont marquees par un drapeau plutot que supprimees, pour ne pas fausser la realite.
- **Markdowns manquants remplaces par 0** : avant novembre 2011, un markdown absent signifie une absence de suivi promotionnel, pas une donnee perdue. Le 0 a donc un sens metier.
- **Modele en etoile** : deux tables de faits (ventes et contexte) de grains differents, reliees par des dimensions conformes (magasin et calendrier), plutot qu'une table unique aplatie.
- **MAPE bas assume** : au niveau agrege, la loi des grands nombres lisse le bruit des magasins individuels, ce qui rend la serie plus previsible. Un MAPE de 2,2 % est donc coherent, il ne serait pas atteint au grain fin.

---

## Limites et ameliorations futures

- La **croissance annuelle** (YoY) est sensible aux annees partielles du jeu de donnees (debut en fevrier 2010, fin en octobre 2012). Elle est plus fiable filtree sur une annee complete que lue en chiffre global.
- La metrique officielle de la competition est le **WMAE** (semaines feriees ponderees x5), non implementee ici puisque la prevision porte sur le total agrege et non sur la soumission par rayon.
- Integrer les variables de contexte dans un modele **SARIMAX** pour tester leur apport predictif (le jeu de donnees fournit deja les valeurs futures de ces variables).
- Produire une **prevision par magasin** pour un pilotage plus fin.
- Comparer a d'autres approches : **Prophet**, **XGBoost** avec variables temporelles.
- Automatiser le pipeline (script shell ou ordonnanceur type Airflow).

---

## Stack technique

Python (pandas, numpy, statsmodels), Power BI (DAX, modele en etoile), Git.

---

## Auteur

**Lilian Doublet**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profil-0A66C2?logo=linkedin)](https://www.linkedin.com/in/lilian-doublet/)
[![GitHub](https://img.shields.io/badge/GitHub-liliandoublet-181717?logo=github)](https://github.com/liliandoublet)

