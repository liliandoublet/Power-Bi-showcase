"""
Prevision des ventes Walmart par un modele SARIMA (saisonnalite annuelle).

Demarche :
    1. Charger la serie hebdomadaire (data/processed/forecast_total.csv)
    2. Couper en apprentissage / test (les 26 dernieres semaines servent de test)
    3. Entrainer SARIMA, mesurer l'erreur sur le test (MAE, RMSE, MAPE)
    4. Reentrainer sur toute la serie et projeter 26 semaines dans le futur
    5. Exporter data/processed/forecast_results.csv au format long pour Power BI

Prerequis :
    pip install -r requirements.txt

Usage :
    source .venv/bin/activate
    python src/forecast.py
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")  # masque les avertissements de convergence

CLEAN = Path("data/processed")

# Horizons (en semaines)
H_TEST = 26     # taille du jeu de test pour valider le modele
H_FUTURE = 26   # nombre de semaines projetees dans le futur

# Parametres SARIMA : modele "airline" (0,1,1)(0,1,1,52), un standard robuste.
# (p,d,q) = composante non saisonniere, (P,D,Q,s) = composante saisonniere,
# s = 52 car la saisonnalite se repete tous les ans (52 semaines).
ORDER = (0, 1, 1)
SEASONAL_ORDER = (0, 1, 1, 52)


def charger_serie():
    """Charge la serie et impose une frequence hebdomadaire (vendredis)."""
    df = pd.read_csv(CLEAN / "forecast_total.csv", parse_dates=["Date"])
    df = df.sort_values("Date").set_index("Date")
    # Les dates Walmart tombent le vendredi, d'ou la frequence W-FRI
    serie = df["Ventes"].asfreq("W-FRI")
    # Securite si une semaine manque : on interpole
    serie = serie.interpolate()
    return serie


def evaluer(reel, prevu):
    """Calcule les metriques d'erreur classiques."""
    erreur = reel - prevu
    mae = np.mean(np.abs(erreur))
    rmse = np.sqrt(np.mean(erreur ** 2))
    mape = np.mean(np.abs(erreur / reel)) * 100
    return mae, rmse, mape


def main():
    serie = charger_serie()
    print(f"Serie chargee : {len(serie)} semaines "
          f"({serie.index.min().date()} -> {serie.index.max().date()})")

    # 1. Decoupage apprentissage / test
    train = serie.iloc[:-H_TEST]
    test = serie.iloc[-H_TEST:]

    # 2. Entrainement sur l'apprentissage et prevision sur le test
    print("\nEntrainement du modele de validation (cela peut prendre 1 a 2 min)...")
    modele_val = SARIMAX(
        train, order=ORDER, seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False, enforce_invertibility=False,
    ).fit(disp=False)

    prev_test = modele_val.get_forecast(steps=H_TEST)
    prev_test_moy = prev_test.predicted_mean
    ic_test = prev_test.conf_int(alpha=0.20)  # intervalle a 80%

    # 3. Mesure de la qualite sur le test
    mae, rmse, mape = evaluer(test.values, prev_test_moy.values)
    print("\n===== Performance sur le jeu de test =====")
    print(f"  MAE  : {mae:,.0f}")
    print(f"  RMSE : {rmse:,.0f}")
    print(f"  MAPE : {mape:.2f} %   (erreur moyenne en pourcentage)")

    # 4. Reentrainement sur TOUTE la serie, puis projection future
    print("\nReentrainement sur la serie complete et projection...")
    modele_final = SARIMAX(
        serie, order=ORDER, seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False, enforce_invertibility=False,
    ).fit(disp=False)

    prev_futur = modele_final.get_forecast(steps=H_FUTURE)
    prev_futur_moy = prev_futur.predicted_mean
    ic_futur = prev_futur.conf_int(alpha=0.20)

    # 5. Construction de la table de sortie au format long
    #    Serie "Reel" : tout l'historique observe
    reel = pd.DataFrame({
        "Date": serie.index,
        "Serie": "Réel",
        "Phase": "Historique",
        "Valeur": serie.values,
        "Borne_Basse": np.nan,
        "Borne_Haute": np.nan,
    })

    #    Serie "Prévision" sur le test (pour visualiser la qualite de l'ajustement)
    prev_t = pd.DataFrame({
        "Date": test.index,
        "Serie": "Prévision",
        "Phase": "Test",
        "Valeur": prev_test_moy.values,
        "Borne_Basse": ic_test.iloc[:, 0].values,
        "Borne_Haute": ic_test.iloc[:, 1].values,
    })

    #    Serie "Prévision" sur le futur
    prev_f = pd.DataFrame({
        "Date": prev_futur_moy.index,
        "Serie": "Prévision",
        "Phase": "Futur",
        "Valeur": prev_futur_moy.values,
        "Borne_Basse": ic_futur.iloc[:, 0].values,
        "Borne_Haute": ic_futur.iloc[:, 1].values,
    })

    resultats = pd.concat([reel, prev_t, prev_f], ignore_index=True)
    resultats.to_csv(CLEAN / "forecast_results.csv", index=False)

    print(f"\nExport : {(CLEAN / 'forecast_results.csv').resolve()}")
    print(f"  {len(reel)} lignes historiques, "
          f"{len(prev_t)} de test, {len(prev_f)} de prevision future.")


if __name__ == "__main__":
    main()
