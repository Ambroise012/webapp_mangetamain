"""filter drinks and foods"""
import pandas as pd
import numpy as np
import re
import json

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

def load_keywords(config_path="config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config["DRINK_KEYWORDS"], config["DRINK_FALSE_POSITIVES"], config["FOOD_KEYWORDS"]


_drink_re = re.compile("|".join(cfg.DRINK_KEYWORDS), flags=re.IGNORECASE)
# _drink_fp_re = re.compile("|".join(cfg.DRINK_FALSE_POSITIVES), flags=re.IGNORECASE)
# _food_re = re.compile("|".join(cfg.FOOD_KEYWORDS), flags=re.IGNORECASE)

# def tag_is_drink(tag: str) -> bool:
#     """Verify if a tag correspond to a drinks."""
#     if not isinstance(tag, str):
#         return False
#     t = tag.strip().lower()
#     if _drink_fp_re.search(t):
#         return False
#     return _drink_re.search(t) is not None

def separate_foods_drinks(recipes_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Sépare les recettes en deux DataFrames : boissons et nourriture.

    Args:
        recipes_df: DataFrame contenant les recettes avec une colonne 'tags'.

    Returns:
        Tuple de deux DataFrames : (food_recipes, drink_recipes).
    """
    # Explosion des tags pour analyse
    tags_exploded = recipes_df.explode("tags")

    # Identification des IDs de boissons
    drink_ids = tags_exploded[
        tags_exploded["tags"].str.contains(_drink_re, regex=True)
    ]["id"].unique()

    # Séparation des recettes
    drink_recipes = recipes_df[recipes_df["id"].isin(drink_ids)]
    food_recipes = recipes_df[~recipes_df["id"].isin(drink_ids)]

    return food_recipes, drink_recipes