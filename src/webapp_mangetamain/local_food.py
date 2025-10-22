import filter_data
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import math

def plot_cuisine_distributions(recipes_with_continent: pd.DataFrame):
    """
    Affiche trois boxplots comparant les recettes par continent :
    - log_minutes
    - n_steps
    - n_ingredients

    Paramètres :
        recipes_with_continent : DataFrame avec colonnes
            ['continent', 'log_minutes', 'n_steps', 'n_ingredients']

    Retourne :
        fig : matplotlib Figure
    """
    cols = ["log_minutes", "n_steps", "n_ingredients"]
    titles = {
        "log_minutes": "Temps de préparation (log)",
        "n_steps": "Nombre d'étapes",
        "n_ingredients": "Nombre d'ingrédients"
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 10))

    for i, col in enumerate(cols):
        sns.boxplot(
            x="continent", y=col, data=recipes_with_continent,
            ax=axes[i], palette="viridis"
        )
        axes[i].set_title(f"Distribution de {titles[col]} par continent")
        axes[i].tick_params(axis="x", rotation=45)
        axes[i].set_xlabel("")
        axes[i].set_ylabel("")

    fig.tight_layout()
    return fig


def plot_top_ingredients_by_continent(recipes_with_continent: pd.DataFrame, top_n: int = 10, global_threshold: float = 0.30):
    """
    Affiche les ingrédients les plus utilisés par continent,
    en excluant les ingrédients omniprésents.

    Paramètres :
        recipes_with_continent : DataFrame avec ['id', 'continent', 'ingredients']
        top_n : nombre d'ingrédients à afficher par continent
        global_threshold : exclut les ingrédients apparaissant dans plus de X% des recettes
    """
    df = recipes_with_continent.copy()
    df["ingredients"] = df["ingredients"].str.lower().str.strip()

    # --- 1. Calcul de la fréquence globale de chaque ingrédient
    total_recipes = df["id"].nunique()
    global_freq = (
        df.groupby("ingredients")["id"]
        .nunique()
        .div(total_recipes)
        .reset_index(name="global_freq")
    )

    # --- 2. Exclure les ingrédients trop fréquents
    common_ingredients = global_freq.query("global_freq > @global_threshold")["ingredients"]
    df = df[~df["ingredients"].isin(common_ingredients)]

    # --- 3. Compter les occurrences par continent
    counts = (
        df.groupby(["continent", "ingredients"])
        .size()
        .reset_index(name="count")
    )

    # --- 4. Top N par continent
    top_by_continent = (
        counts.sort_values(["continent", "count"], ascending=[True, False])
        .groupby("continent", group_keys=False)
        .head(top_n)
    )
    

    # --- 5. Trier les continents selon leur taille
    continent_order = (
        df["continent"]
        .value_counts()
        .index.tolist()
    )
    top_by_continent["continent"] = pd.Categorical(
        top_by_continent["continent"], categories=continent_order, ordered=True
    )
    print(top_by_continent)
    
    
    # --- 6. Visualisation
    
    continents = top_by_continent["continent"].unique()
    n = len(continents)
    fig, axes = plt.subplots(
        nrows=1, ncols=n, figsize=(5 * n, 10), sharey=False
    )

    ncols = 2
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols,
        figsize=(13, 4 * nrows),
        sharey=False
    )

    # Si un seul continent, axes devient une seule instance
    axes = np.array(axes).reshape(-1)

    # --- 6. Dessin des graphes
    for ax, continent in zip(axes, continents):
        subset = (
            top_by_continent[top_by_continent["continent"] == continent]
            .sort_values("count", ascending=True)
        )

        sns.barplot(
            data=subset,
            x="count", y="ingredients",
            ax=ax, palette="viridis"
        )
        ax.set_title(continent, fontsize=12, fontweight="bold")
        ax.set_xlabel("Occurrences")
        ax.set_ylabel("")
        ax.tick_params(axis="y", labelsize=9)
        ax.invert_yaxis()

    # --- 7. Cacher les axes vides
    for j in range(len(continents), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(
        f"Top {top_n} ingrédients typiques par continent (hors ingrédients omniprésents > {int(global_threshold*100)}%)",
        fontsize=14, fontweight="bold", y=1.02
    )
    plt.tight_layout()
    plt.show()
    return fig


plot_top_ingredients_by_continent(filter_data.ingredient_and_continent)

    