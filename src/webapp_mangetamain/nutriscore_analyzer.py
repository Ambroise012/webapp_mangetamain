"Utils function and vaariable for the nutrition analyzer tab"
import ast
from typing import Dict

import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from webapp_mangetamain.load_config import cfg


# -------------------------
# Configuration setup
# -------------------------

NUTRISCORE = {
    tuple(map(int, k.strip("()").split(","))): v
    for k, v in cfg.NUTRISCORE.__dict__.items()
}

nutrient_labels = cfg.nutrient_labels
THRESHOLDS = cfg.THRESHOLDS.__dict__
NUTRITION_LIMITS = {
    k: v.__dict__ for k, v in cfg.NUTRITION_LIMITS.__dict__.items()
}

# -------------------------
# Functions
# -------------------------

def plot_nutriscore_comparison(subset_df: pd.DataFrame, recipe: pd.DataFrame) -> None:
    """
    Compare NutriScore distributions between all recipes
    and those with 'health' in their tags.
    """
    subset_tags = recipe.loc[subset_df.index, "tags"]

    health_mask = subset_tags.apply(
        lambda tags: any("health" in str(t).lower() for t in (tags if isinstance(tags, list) else [tags]))
    )

    health_subset = subset_df.loc[health_mask].copy()
    non_health_subset = subset_df.loc[~health_mask].copy()

    st.write(f"**Total recipes:** {len(subset_df)}")
    st.write(f"**Recipes with 'health' tag:** {len(health_subset)}")
    st.write(f"**Recipes without 'health' tag:** {len(non_health_subset)}")

    # ---- Count Nutri-Scores ----
    score_counts_all = subset_df["nutri_score"].value_counts().sort_index()
    score_counts_health = health_subset["nutri_score"].value_counts().sort_index()

    # ---- Normalize to percentages ----
    score_pct_all = score_counts_all / score_counts_all.sum() * 100
    score_pct_health = score_counts_health / score_counts_health.sum() * 100

    # ---- Align indexes (A–E) in case one set misses a grade ----
    all_indexes = sorted(set(score_counts_all.index).union(score_counts_health.index))
    score_pct_all = score_pct_all.reindex(all_indexes, fill_value=0)
    score_pct_health = score_pct_health.reindex(all_indexes, fill_value=0)

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(all_indexes))

    ax.bar([i - 0.2 for i in x], score_pct_all.values, width=0.4, label="All recipes")
    ax.bar([i + 0.2 for i in x], score_pct_health.values, width=0.4, label="'Health' tagged")

    ax.set_xticks(x)
    ax.set_xticklabels(all_indexes)
    ax.set_xlabel("Nutri-Score")
    ax.set_ylabel("Percentage of recipes (%)")
    ax.set_title("Nutri-Score comparison: all vs. 'health' tagged")
    ax.legend()

    st.pyplot(fig)

def get_points(value: float, thresholds: list) -> int:
    """Assign points based on thresholds."""
    for i, t in enumerate(thresholds):
        if value <= t:
            return i
    return len(thresholds)

def compute_nutriscore(nutrition: Dict[str, float]) -> str:
    """Compute the Nutri-Score from nutrition composition."""
    total_points = 0
    for nutrient, thresholds in THRESHOLDS.items():
        if nutrient in nutrition:
            points = get_points(nutrition[nutrient], thresholds)
            if nutrient == "protein":
                total_points -= points
            else:
                total_points += points

    for (low, high), grade in NUTRISCORE.items():
        if low <= total_points <= high:
            return grade
    return "E"

def parse_nutrition(recipe_df: pd.DataFrame) -> pd.DataFrame:
    """Expand recipe nutrition JSON column into numeric DataFrame."""
    nutrition = recipe_df["nutrition"].apply(ast.literal_eval)
    nutrition_df = pd.DataFrame(nutrition.tolist(), columns=nutrient_labels)
    return nutrition_df

def filter_data_with_nutri(nutrition_df: pd.DataFrame) -> pd.DataFrame:
    """Filter out extreme values for clean analysis using config limits."""
    mask = pd.Series(True, index=nutrition_df.index)

    for nutrient, limits in NUTRITION_LIMITS.items():
        if nutrient in nutrition_df.columns:
            mask &= nutrition_df[nutrient].between(limits["min"], limits["max"], inclusive="both")

    return nutrition_df[mask].copy()

def add_nutriscore_column(nutrition_df: pd.DataFrame) -> pd.DataFrame:
    """Compute and add Nutri-Score column to dataframe."""
    df = nutrition_df.copy()
    df["nutri_score"] = df.apply(lambda row: compute_nutriscore(row.to_dict()), axis=1)
    return df

def correlation_matrix(nutrition_df: pd.DataFrame):
    """Return a matplotlib figure for correlation matrix heatmap."""
    corr_matrix = nutrition_df.corr()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        cbar_kws={"shrink": .8},
        ax=ax
    )
    ax.set_title("Correlation matrix", fontsize=14, pad=12)
    fig.tight_layout()
    return fig