# Insights metier -- Analyse des ventes Walmart

## 1. Structure du parc de magasins

- 45 magasins repartis en 3 types : A (grands), B (moyens), C (petits)
- Les magasins de type A concentrent **64,3 %** des ventes totales sur la periode
- Les magasins de type B representent 29,7 % ; les type C seulement 6,0 %
- Consequence operationnelle : les decisions de stock et de promotion doivent etre priorisees sur les type A

## 2. Qualite des donnees

- Grain principal (FactSales) : magasin x rayon x semaine, ~420 000 lignes
- Ventes negatives conservees et marquees (IsNegativeSale = True) : representent des semaines ou les retours clients depassent les ventes brutes -- supprimer ces lignes serait une erreur metier
- MarkDown1-5 absents avant novembre 2011 : les promotions n'etaient pas encore tracees, les valeurs nulles ont ete imputees a 0 (sens metier : pas de promo cette semaine)

## 3. Saisonnalite

- Saisonnalite annuelle marquee avec des pics en novembre et decembre (periode des fetes)
- La decomposition temporelle confirme une composante saisonniere forte a la frequence 52 semaines
- Le modele SARIMA capture cette saisonnalite via l'ordre (0,1,1)(0,1,1,52)

## 4. Impact des jours feries

- Les semaines marquees IsHoliday = True enregistrent en moyenne **+7,84 %** de ventes par rapport aux semaines ordinaires
- Les evenements les plus impactants : Super Bowl, Labour Day, Thanksgiving, Christmas
- A integrer dans les plans d'approvisionnement avec 2 a 4 semaines d'avance

## 5. Performance du modele de prevision SARIMA

- Modele : SARIMA(0,1,1)(0,1,1,52) -- modele "airline", robuste et parcimonieux
- Validation hors echantillon : 26 dernieres semaines de la periode (environ 6 mois)
- MAPE (erreur moyenne en pourcentage) : **2,2 %**
- Interpretation : en moyenne, la prevision s'ecarte de 2,2 % des ventes reelles -- niveau de precision satisfaisant pour un pilotage operationnel hebdomadaire
- Les intervalles de confiance a 80 % sont exportes dans forecast_results.csv pour la visualisation Power BI

## 6. Variables contextuelles (FactFeatures)

- Temperature, Fuel_Price, CPI, Unemployment : suivies par magasin et par semaine
- MarkDown_total (somme des 5 types de promotions) : variable potentiellement predictive a tester dans une version amelioree du modele
- Ces variables ne sont pas integrees dans le modele SARIMA actuel (modelisation univariee) mais sont disponibles pour une extension SARIMAX

---

*Ces insights sont bases sur le dataset "Walmart Recruiting -- Store Sales Forecasting" (Kaggle), periode 2010-2012.*
