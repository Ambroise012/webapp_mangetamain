"""filter drinks and foods"""
import pandas as pd
import numpy as np
import re

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