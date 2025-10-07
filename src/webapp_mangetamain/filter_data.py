"""filter drinks and foods"""
import pandas as pd
import numpy as np
import load_config


recipes = load_config.recipe


def general_complexity_prepocessing(df: pd.DataFrame):
    df = df.copy()
    
    for c in ["minutes", "n_steps", "n_ingredients"]:
        df = df[df[c] > 0]

    for c in ["minutes", "n_steps", "n_ingredients"]:
        q = df[c].quantile(0.99)
        df = df[df[c] <= q]
        
        df["log_minutes"] = np.log1p(df["minutes"])

    return df


recipes_clean = general_complexity_prepocessing(recipes)
