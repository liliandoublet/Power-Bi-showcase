"""
Nettoyage du dataset Walmart Store Sales Forecasting (Kaggle).
Objectif : produire des fichiers propres prets a etre charges dans Power BI
selon un modele en etoile (DimStores, FactSales, FactFeatures).

Usage :
    1. Place les CSV Kaggle dans le dossier ./data/raw
       (stores.csv, train.csv, features.csv, test.csv)
    2. python src/clean.py
    3. Les fichiers nettoyes sont ecrits dans ./data/processed

Auteur : Lilian Doublet
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = Path("data/raw")
CLEAN_DIR = Path("data/processed")
CLEAN_DIR.mkdir(exist_ok=True)

MARKDOWN_COLS = ["MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5"]


# ---------------------------------------------------------------------------
# 1. Chargement
# ---------------------------------------------------------------------------
def load_data():
    """Charge les CSV bruts en parsant les dates des le depart."""
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    train = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["Date"])
    features = pd.read_csv(DATA_DIR / "features.csv", parse_dates=["Date"])
    return stores, train, features


# ---------------------------------------------------------------------------
# 2. Audit (toujours auditer avant de nettoyer)
# ---------------------------------------------------------------------------
def audit(name, df):
    """Affiche un rapport rapide de qualite des donnees."""
    print(f"\n===== AUDIT : {name} =====")
    print(f"Lignes : {len(df):,} | Colonnes : {df.shape[1]}")
    print("Types :")
    print(df.dtypes.to_string())
    na = df.isna().sum()
    na = na[na > 0]
    if len(na):
        print("Valeurs manquantes :")
        print(na.to_string())
    else:
        print("Aucune valeur manquante.")
    print(f"Doublons (lignes entieres) : {df.duplicated().sum()}")
    if "Date" in df.columns:
        print(f"Periode : {df['Date'].min().date()} -> {df['Date'].max().date()}")


# ---------------------------------------------------------------------------
# 3. Nettoyage de la dimension magasins
# ---------------------------------------------------------------------------
def clean_stores(stores):
    """DimStores : 45 magasins, leur type (A/B/C) et leur surface."""
    df = stores.copy()
    df["Store"] = df["Store"].astype("int16")
    df["Type"] = df["Type"].astype("category")
    df["Size"] = df["Size"].astype("int32")
    df = df.rename(columns={"Type": "StoreType", "Size": "StoreSize"})
    return df


# ---------------------------------------------------------------------------
# 4. Nettoyage des ventes (table de faits principale)
# ---------------------------------------------------------------------------
def clean_sales(train):
    """
    FactSales : grain magasin x departement x semaine.

    Point de vigilance : Weekly_Sales contient des valeurs negatives
    (retours superieurs aux ventes sur la semaine). On NE les supprime PAS
    a l'aveugle : on les conserve et on ajoute un drapeau pour pouvoir les
    isoler dans Power BI si besoin. Supprimer une donnee reelle sans raison
    metier est une erreur que tu dois savoir defendre en entretien.
    """
    df = train.copy()
    df["Store"] = df["Store"].astype("int16")
    df["Dept"] = df["Dept"].astype("int16")
    df["Weekly_Sales"] = df["Weekly_Sales"].astype("float32")
    df["IsHoliday"] = df["IsHoliday"].astype("bool")

    # Drapeau qualite plutot que suppression
    df["IsNegativeSale"] = df["Weekly_Sales"] < 0
    nb_neg = df["IsNegativeSale"].sum()
    print(f"\n[FactSales] Ventes negatives detectees : {nb_neg:,} "
          f"({nb_neg / len(df):.2%}) -> conservees et marquees.")

    # Verification de l'unicite du grain
    dupes = df.duplicated(subset=["Store", "Dept", "Date"]).sum()
    print(f"[FactSales] Doublons sur (Store, Dept, Date) : {dupes}")

    return df


# ---------------------------------------------------------------------------
# 5. Nettoyage des variables contextuelles
# ---------------------------------------------------------------------------
def clean_features(features):
    """
    FactFeatures : grain magasin x semaine.

    - Les MarkDown1-5 sont vides avant nov. 2011 (les promos n'etaient pas
      encore suivies). Un null = pas de promo cette semaine, donc on remplace
      par 0 (sens metier coherent).
    - CPI et Unemployment ont quelques null sur la periode future (dates du
      jeu de test) : on les laisse en l'etat, elles seront filtrees cote
      Power BI si on ne garde que la periode des ventes reelles.
    - On supprime IsHoliday ici pour garder une seule source de verite
      (celle de FactSales).
    """
    df = features.copy()
    df["Store"] = df["Store"].astype("int16")

    # MarkDowns manquants -> 0
    df[MARKDOWN_COLS] = df[MARKDOWN_COLS].fillna(0).astype("float32")

    # On retire IsHoliday (doublon avec FactSales)
    if "IsHoliday" in df.columns:
        df = df.drop(columns=["IsHoliday"])

    # Types
    for col in ["Temperature", "Fuel_Price", "CPI", "Unemployment"]:
        df[col] = df[col].astype("float32")

    return df


# ---------------------------------------------------------------------------
# 6. Pipeline complet
# ---------------------------------------------------------------------------
def main():
    print("Chargement des donnees brutes...")
    stores, train, features = load_data()

    # Audit avant nettoyage
    for name, df in [("stores", stores), ("train", train), ("features", features)]:
        audit(name, df)

    # Nettoyage
    dim_stores = clean_stores(stores)
    fact_sales = clean_sales(train)
    fact_features = clean_features(features)

    # Export pour Power BI
    dim_stores.to_csv(CLEAN_DIR / "dim_stores.csv", index=False)
    fact_sales.to_csv(CLEAN_DIR / "fact_sales.csv", index=False)
    fact_features.to_csv(CLEAN_DIR / "fact_features.csv", index=False)

    print("\n===== EXPORT TERMINE =====")
    print(f"Fichiers ecrits dans : {CLEAN_DIR.resolve()}")
    print(f"  dim_stores.csv     : {len(dim_stores):,} lignes")
    print(f"  fact_sales.csv     : {len(fact_sales):,} lignes")
    print(f"  fact_features.csv  : {len(fact_features):,} lignes")


if __name__ == "__main__":
    main()
