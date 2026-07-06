# Analyse et prevision des ventes Walmart

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

## Apercu du projet

Ce projet analyse les ventes hebdomadaires de 45 magasins Walmart sur 143 semaines (2010-2012) et produit deux livrables :

1. **Dashboard Power BI** -- 4 pages interactives pour explorer les ventes par magasin, rayon, periode et facteurs externes
2. **Modele de prevision SARIMA** -- projection des ventes totales sur 26 semaines avec intervalles de confiance, validee sur 6 mois hors echantillon (MAPE : 2,2 %)

Source des donnees : [Walmart Recruiting - Store Sales Forecasting](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting) (Kaggle)

---

## Donnees

| Caracteristique | Detail |
|---|---|
| Source | Kaggle -- Walmart Recruiting Store Sales Forecasting |
| Grain | Magasin x Rayon x Semaine |
| Periode | Fevrier 2010 -- Octobre 2012 (143 semaines) |
| Perimetre | 45 magasins, ~81 rayons, ~420 000 lignes |
| Types de magasins | A (grands), B (moyens), C (petits) |

---

## Architecture en 3 couches

```
data/raw/          CSV bruts Kaggle (non verses dans Git)
    |
    v
[Couche 1] src/clean.py
    |              Nettoyage, audit qualite, modele en etoile
    v
data/processed/    dim_stores.csv | fact_sales.csv | fact_features.csv
    |
    v
[Couche 2] src/prepare_forecast.py  -->  forecast_total.csv
              src/forecast.py        -->  forecast_results.csv
    |              Serie temporelle agregee + SARIMA(0,1,1)(0,1,1,52)
    v
[Couche 3] reports/walmart_sales.pbix
               Dashboard Power BI (Vue d'ensemble / Magasins / Facteurs / Prevision)
```

---

## Comment reproduire

### Prerequis

```bash
git clone https://github.com/<votre-username>/walmart-sales-forecasting.git
cd walmart-sales-forecasting
pip install -r requirements.txt
```

Telecharger les CSV Kaggle et les placer dans `data/raw/` :
`stores.csv`, `train.csv`, `features.csv`, `test.csv`

### Execution dans l'ordre

```bash
# 1. Nettoyage et creation du modele en etoile
python src/clean.py

# 2. Agregation pour la serie temporelle
python src/prepare_forecast.py

# 3. Prevision SARIMA (environ 2-3 minutes)
python src/forecast.py
```

Les fichiers produits dans `data/processed/` sont prets a etre charges dans Power BI.

---

## Insights cles

- Les magasins de **type A concentrent 64,3 % des ventes** ; les decisions de stock doivent etre priorisees sur ce segment
- Les **semaines de jours feries generent +7,84 % de ventes** par rapport aux semaines ordinaires (Super Bowl, Thanksgiving, Christmas)
- Une **saisonnalite forte en novembre-decembre** est capturee par le modele SARIMA avec une periode de 52 semaines
- Le modele SARIMA(0,1,1)(0,1,1,52) atteint une **MAPE de 2,2 %** sur 26 semaines hors echantillon, niveau satisfaisant pour un pilotage operationnel hebdomadaire

---

## Competences demontrees

| Domaine | Detail |
|---|---|
| Data Engineering | Nettoyage Python (pandas), audit qualite, modele en etoile, gestion des valeurs manquantes avec justification metier |
| Business Intelligence | Dashboard Power BI 4 pages, schema relationnel, mesures DAX |
| Data Science | Modelisation de serie temporelle, SARIMA, validation hors echantillon, metriques MAE/RMSE/MAPE |
| Methodologie | Pipeline reproductible en 3 etapes, separation nette nettoyage / prevision / reporting |

---

## Ameliorations futures

- Integrer les variables contextuelles (MarkDown, CPI, Temperature) dans un modele **SARIMAX** pour tester leur apport predictif
- Produire une prevision **par magasin** plutot qu'agregee, pour un pilotage operationnel plus fin
- Automatiser le pipeline avec un ordonnanceur (ex : Airflow ou simple script shell)
- Tester d'autres modeles de serie temporelle : Prophet, XGBoost avec features temporelles

---

## Auteur

**Lilian Doublet** -- Data Analyst Junior

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profil-0A66C2?logo=linkedin)](https://linkedin.com/in/<votre-profil>)
