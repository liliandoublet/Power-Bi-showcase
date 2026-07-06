"""
Preparation du jeu de donnees pour la PREVISION (couche 2 du projet Walmart).

Le reporting utilise le grain magasin x rayon x semaine.
La prevision a besoin d'une serie temporelle agregee : une ligne par semaine,
avec les ventes totales (la cible) et le contexte (les variables explicatives).

Produit : data/processed/forecast_total.csv

Usage :
    source .venv/bin/activate
    python src/prepare_forecast.py
"""

from pathlib import Path
import pandas as pd

DATA = Path("data/raw")
CLEAN = Path("data/processed")
CLEAN.mkdir(exist_ok=True)

MARKDOWN_COLS = [f"MarkDown{i}" for i in range(1, 6)]


def main():
    train = pd.read_csv(DATA / "train.csv", parse_dates=["Date"])
    features = pd.read_csv(DATA / "features.csv", parse_dates=["Date"])

    # 1. La cible : ventes totales par semaine (toutes enseignes et rayons confondus)
    ventes = (
        train.groupby("Date", as_index=False)["Weekly_Sales"]
        .sum()
        .rename(columns={"Weekly_Sales": "Ventes"})
    )

    # 2. Le contexte, agrege a la maille semaine
    #    - promos manquantes (avant nov. 2011) = pas de promo = 0
    #    - indices economiques : moyenne entre magasins
    #    - promos : somme (volume total de demarque)
    feat = features.copy()
    feat[MARKDOWN_COLS] = feat[MARKDOWN_COLS].fillna(0)
    feat["MarkDown_total"] = feat[MARKDOWN_COLS].sum(axis=1)

    contexte = feat.groupby("Date", as_index=False).agg(
        Temperature=("Temperature", "mean"),
        Fuel_Price=("Fuel_Price", "mean"),
        CPI=("CPI", "mean"),
        Unemployment=("Unemployment", "mean"),
        MarkDown_total=("MarkDown_total", "sum"),
        IsHoliday=("IsHoliday", "max"),
    )

    # 3. Jointure. Le merge interne ne garde que les semaines avec ventes reelles
    #    (la periode train), les dates futures de features sont donc ecartees ici.
    df = ventes.merge(contexte, on="Date", how="left").sort_values("Date")

    # 4. Controle qualite avant export
    print(f"Periode      : {df['Date'].min().date()} -> {df['Date'].max().date()}")
    print(f"Nb semaines  : {len(df)}")
    print(f"Manquants    :\n{df.isna().sum()[df.isna().sum() > 0].to_string() or '  aucun'}")

    df.to_csv(CLEAN / "forecast_total.csv", index=False)
    print(f"\nExport : {(CLEAN / 'forecast_total.csv').resolve()}")  # -> data/processed/


if __name__ == "__main__":
    main()
