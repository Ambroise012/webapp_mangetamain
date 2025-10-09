"""filter drinks and foods, and """
import re

import pandas as pd
import numpy as np
import ast

from webapp_mangetamain.load_config import cfg, recipe

def general_complexity_prepocessing(df: pd.DataFrame):
    df = df.copy()
    
    for c in ["minutes", "n_steps", "n_ingredients"]:
        df = df[df[c] > 0]

    for c in ["minutes", "n_steps", "n_ingredients"]:
        q = df[c].quantile(0.99)
        df = df[df[c] <= q]
        
        df["log_minutes"] = np.log1p(df["minutes"])

    return df


recipes_clean = general_complexity_prepocessing(recipe)


def parse_ingredients_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme la colonne 'ingredients' en une vraie liste Python
    et crée un DataFrame (id, ingredient) propre pour analyse.
    """
    df = df[["id", "ingredients"]].copy()

    def parse_list(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            try:
                val = ast.literal_eval(x)
                if isinstance(val, list):
                    return val
                else:
                    return [val]
            except Exception:
                return [x]
        return []

    df["ingredients"] = df["ingredients"].apply(parse_list)

    exploded = df.explode("ingredients").dropna(subset=["ingredients"])

    exploded["ingredients"] = (
        exploded["ingredients"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    return exploded 


def preprocess_ingredients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode recipe ingredients and count occurrences.
    Returns a DataFrame with columns ['ingredient', 'count'].
    """
    # explode la colonne "ingredients" (liste)
    exploded = df.explode("ingredients")
    ingredient_counts = (
        exploded["ingredients"]
        .str.lower()
        .value_counts()
    )
    return ingredient_counts

ingredients_exploded = parse_ingredients_column(recipes_clean)
ingredient_counts = preprocess_ingredients(ingredients_exploded)

ingredient_counts = (
    ingredient_counts
    .rename("count")                # nomme la série
    .reset_index()                  # passe l'index en colonne
    .rename(columns={"index": "ingredient"})
)

co_occurrence = pd.read_csv("artifacts/co_occurrence.csv", index_col=0)
jaccard = pd.read_csv("artifacts/jaccard.csv", index_col=0)


def filter_counts_window(ingredient_counts: pd.DataFrame, min_count: int, max_count: int | None = None) -> pd.DataFrame:
    """
    Filtre les ingrédients dont la fréquence est dans [min_count, max_count] (ou >= min_count si max_count None).
    """
    if max_count is None:
        mask = ingredient_counts["count"] >= min_count
    else:
        mask = (ingredient_counts["count"] >= min_count) & (ingredient_counts["count"] <= max_count)
    return ingredient_counts.loc[mask].reset_index(drop=True)
recipes_clean = general_complexity_prepocessing(recipe)


# ################
# drinks vs foods
# ################

_drink_re = re.compile("|".join(cfg.DRINK_KEYWORDS), flags=re.IGNORECASE)

def separate_foods_drinks(recipes_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Sépare les recettes en deux DataFrames : boissons et nourriture.

    Args:
        recipes_df: DataFrame contenant les recettes avec une colonne 'tags'.

    Returns:
        Tuple de deux DataFrames : (food_recipes, drink_recipes).
    """
    tags_exploded = recipes_df.explode("tags")

    drink_ids = tags_exploded[
        tags_exploded["tags"].str.contains(_drink_re, regex=True)
    ]["id"].unique()

    drink_recipes = recipes_df[recipes_df["id"].isin(drink_ids)]
    food_recipes = recipes_df[~recipes_df["id"].isin(drink_ids)]

    return food_recipes, drink_recipes
