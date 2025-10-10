"main function of the stremlit app"
import logging

import ingredients_analyzer
import streamlit as st
import utils.filter_data as filter_data
from nutriscore_analyzer import (
    add_nutriscore_column,
    analyze_low_scores_with_health_label,
    correlation_matrix,
    filter_data_with_nutri,
    parse_nutrition,
    plot_nutriscore_comparison,
)
from recipe_complexity import (
    make_corr_heatmap_fig,
    make_pairplot_fig,
    make_univariate_figs,
)
from tag_analyzer import (
    create_tag_recipes_dataset,
    filter_tags_of_interest,
    get_general_tags_statistics,
    plot_tag_frequency_distribution,
    plot_tags_per_recipe_distribution,
    plot_top_tags,
    plot_top_tags_by_metric,
)
from utils.filter_data import recipes_clean, separate_foods_drinks

from webapp_mangetamain.load_config import recipe, recipe_rating

logger = logging.getLogger(__name__)


def render_nutriscore_tab():
    """Render the Nutriscore tab content in Streamlit."""
    st.header("Nutriscore")
    st.subheader("Overview of nutritional scoring system")
    st.markdown(
        """
        ### Nutriscore

        We want to evaluate whether the **tags provided by users** are truly correlated
        with the **nutritional values** of the recipes.

        The **Nutriscore**, used in several European countries, provides a quick and simple way
        to assess the nutritional quality of a product based on data such as **calories, proteins, sugar, fat, salt**, etc.
        👉 [Reference](https://docs.becpg.fr/fr/utilization/score5C.html)

        - Each nutrient receives a **score**.
        - Some are considered **positive** (proteins, fiber).
        - Others are considered **negative** (calories, fat, salt).
        - The **final Nutriscore** is calculated as:
        `Nutriscore = Positive Score – Negative Score`.

        The goal is to explore **what relationships** can be extracted between the Nutriscore and
        other variables (user tags, nutritional values).
        """
    )
    # ------------------------
    # Correlation matrix
    # ------------------------
    st.markdown("""
    First, we can observe the different Nutri-Score values and their correlations with each other.
    We already notice that certain categories emerge: the correlations are stronger between calories, sugar, and fat. These negative values are what primarily lower the score.
    """)
    nutrition_df = parse_nutrition(recipe)
    st.subheader("Correlation Matrix of Nutrients")
    st.pyplot(correlation_matrix(nutrition_df))

    # ------------------------
    # Compare with 'healthy' tag
    # ------------------------
    filtered_df = filter_data_with_nutri(nutrition_df)
    scored_df = add_nutriscore_column(filtered_df)

    st.subheader("Comparison with 'health' tagged recipes")
    plot_nutriscore_comparison(scored_df, recipe)
    st.markdown("""
        **Something is wrong!**

        We should only see orange "health tag" bars in **categories A and B**.
        However, we observe that there are also many in **categories D and E**.
        While the proportion is lower in D, there are actually **more health tags in category E than there are recipes in category E**.

        This discrepancy could be explained by:
        - Incorrectly entered values,
        - The fact that **foods and drinks** use different Nutri-Score calculations,
        - Or the inability to verify whether the data is standardized (e.g., per 100g).
        """)
    # ------------------------
    # Drinks vs Foods
    # ------------------------
    st.markdown(
        """
        ## Drinks / Foods
        Note that our dataset includes both drinks and foods.
        However, the calculation of the Nutri-Score for drinks differs significantly from that for foods.
        Therefore, we focus exclusively on food items, filtering our data and recommendations accordingly.
        """
    )
    food_recipes, drink_recipes = separate_foods_drinks(recipe)
    st.subheader("Recipe Statistics")
    st.write(f"**Food recipes:** {len(food_recipes)}")
    st.write(f"**Drink recipes:** {len(drink_recipes)}")
    food_nutrition_df = nutrition_df.loc[food_recipes.index]
    filtered_df_food = filter_data_with_nutri(food_nutrition_df)
    scored_df_food = add_nutriscore_column(filtered_df_food)
    plot_nutriscore_comparison(scored_df_food, food_recipes)
    st.markdown("""
        **Something is still wrong!**

        We are seen the same patern as before. Even when we remove drinks from recipes.

        So this discrepancy could be explained by:
        - Incorrectly entered values,
        - Whether the data is standardized (e.g., per 100g).
        """)
    analyze_low_scores_with_health_label(recipe_df=food_recipes, nutrition_df=scored_df_food)

def render_tags_tab():
    """Render the Tags tab content."""
    st.header("Tags Analysis")
    st.subheader("Food categorization and labeling")
    # ========================
    # General Statistics
    # ========================
    st.markdown("---")
    st.write("### General Tag Statistics")
    stats = get_general_tags_statistics(recipe_rating)
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Recipes", f"{stats['total_recipes']:,}")
    col2.metric("Unique Tags", stats['total_unique_tags'])
    col3.metric("Total Tags", f"{stats['total_tags']:,}")
    col4.metric("Avg Tags/Recipe", f"{stats['tags_per_recipe_mean']:.2f}")
    # All statistics in order
    with st.expander("View Complete Statistics"):
        st.write("#### Recipe-Level Statistics")
        st.write(f"- **Total recipes analyzed:** {stats['total_recipes']:,}")
        st.write(f"- **Average tags per recipe:** {stats['tags_per_recipe_mean']:.2f}")
        st.write(f"- **Median tags per recipe:** {stats['tags_per_recipe_median']:.0f}")
        st.write(f"- **Min tags per recipe:** {stats['tags_per_recipe_min']:.0f}")
        st.write(f"- **Max tags per recipe:** {stats['tags_per_recipe_max']:.0f}")
        st.write("#### Tag-Level Statistics")
        st.write(f"- **Total unique tags:** {stats['total_unique_tags']}")
        st.write(f"- **Total tags (with duplicates):** {stats['total_tags']:,}")
        st.write(f"- **Average occurrences per tag:** {stats['avg_tags_general']:.2f}")
        st.write("#### Distribution Details")
        st.write("**Tags per recipe (detailed):**")
        st.write(stats['tags_per_recipe_stats'])
        st.write("**Tag frequency (detailed):**")
        st.write(stats['tag_counts_stats'])
        st.write("#### Top 20 Most Frequent Tags")
        st.write(stats['top_20_tags'])

    # ========================
    # Visualizations
    # ========================
    st.markdown("---")
    st.write("### Tag Distributions")

    # Graph 1: Tag frequency first
    st.write("#### Tag Frequency Distribution")
    tag_counts = recipe_rating['tags_parsed'].explode().value_counts()
    plot_tag_frequency_distribution(tag_counts)
    st.info("Power law distribution: few tags used very frequently, many tags used rarely")

    # Graph 2: Top 20
    st.write("#### Top 20 Most Frequent Tags")
    plot_top_tags(tag_counts, top_n=20)
    st.info("Generic organizational tags dominate (preparation, time-to-make, course)")

    # Graph 3: Distribution per recipe
    st.write("#### Distribution of Tags per Recipe")
    plot_tags_per_recipe_distribution(recipe_rating)
    st.info("Most recipes have between 13-22 tags. Mean: 17.9, Median: 17.0")

    # ========================
    # Tags Analysis by Metrics
    # ========================
    st.markdown("---")
    st.write("### Tags Analysis by Metrics")
    tag_stats, _ = create_tag_recipes_dataset(recipe_rating, min_recipes_per_tag=50)
    st.info(f"Analyzing **{len(tag_stats)}** tags with at least 50 recipes")
    tags_of_interest = filter_tags_of_interest(tag_stats)
    st.success(f"Found **{len(tags_of_interest)}** tags of interest across **{tags_of_interest['category'].nunique()}** categories")
    # Show the 37 tags of interest
    with st.expander("View the tags of interest"):
        for category in sorted(tags_of_interest['category'].unique()):
            cat_tags = tags_of_interest[tags_of_interest['category'] == category]['tag'].tolist()
            st.write(f"**{category}** ({len(cat_tags)} tags): {', '.join(cat_tags)}")
    st.write("#### Top Tags by Number of Recipes")
    plot_top_tags_by_metric(tag_stats, metric='n_recipes', top_n=20)

    # ========================
    # Best Tags
    # ========================
    st.markdown("---")
    st.write("### 🏆 Best Tags by Criteria")
    # Simple best tags without function
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Fastest (by avg time):**")
        fastest = tags_of_interest.nsmallest(5, 'avg_minutes')[['tag', 'category', 'avg_minutes', 'n_recipes']]
        st.dataframe(fastest, hide_index=True)

        st.write("**Simplest (fewest ingredients):**")
        simplest = tags_of_interest.nsmallest(5, 'avg_ingredients')[['tag', 'category', 'avg_ingredients', 'n_recipes']]
        st.dataframe(simplest, hide_index=True)

    with col2:
        st.write("**Most Popular:**")
        popular = tags_of_interest.nlargest(5, 'n_recipes')[['tag', 'category', 'n_recipes', 'avg_minutes']]
        st.dataframe(popular, hide_index=True)
        st.write("**Fewest Steps:**")
        easy = tags_of_interest.nsmallest(5, 'avg_steps')[['tag', 'category', 'avg_steps', 'n_recipes']]
        st.dataframe(easy, hide_index=True)

def render_ingredient_tab():

    """
    ingredients_exploded: DataFrame avec colonnes ['id','ingredients'] (déjà normalisées)
    """
    st.header("Ingredients")

    # ===== 1) Distribution & résumé =====
    st.subheader("Distribution des fréquences")
    ingredient_counts = filter_data.ingredient_counts
    logger.info(f"Ingredient count:{ingredient_counts}")

    st.dataframe(ingredients_analyzer.summarize_ingredient_stats(ingredient_counts))
    st.pyplot(ingredients_analyzer.plot_ingredient_distribution(ingredient_counts))

    st.subheader("Top ingrédients")
    top_n = st.slider("Afficher les N ingrédients les plus fréquents", 10, 100, 30, 5)
    st.pyplot(ingredients_analyzer.make_top_ingredients_bar_fig(ingredient_counts, top_n))

    # ===== 2) Fenêtre de fréquence =====
    st.subheader("Sélection de la fenêtre de fréquence")
    min_count = st.number_input(
        "min_count (exclure les ingrédients trop rares)",
        1, int(ingredient_counts["count"].max()), 200
    )
    use_max = st.checkbox("Limiter les hyper-fréquents (max_count)", value=True)
    default_max = 5000
    max_count = st.number_input(
        "max_count", min_count, int(ingredient_counts["count"].max()),
        default_max, step=50
    ) if use_max else None

    kept_counts = filter_data.filter_counts_window(
        ingredient_counts, min_count=min_count, max_count=max_count
    )
    st.caption(
        f"Ingrédients conservés: **{len(kept_counts):,}** | "
        f"Occurrences cumulées: **{kept_counts['count'].sum():,}**"
    )
    st.subheader("Focus sur un ingrédient")
    c1, c2 = st.columns([2, 1])
    with c1:
        focus = st.selectbox("Choisir un ingrédient", sorted(filter_data.co_occurrence.columns.to_list()))
    with c2:
        k = st.slider("Top K", 5, 40, 15)

    min_co_focus = st.slider("Co-occurrence minimale (|A∩B|) pour le focus", 1, 200, 20)
    metric = st.radio("Mesure", ["Jaccard"], horizontal=True)

    if metric == "Jaccard":
        assoc = ingredients_analyzer.top_cooccurrences_for(focus, filter_data.jaccard, filter_data.co_occurrence, k=k, min_co=min_co_focus)
        x_field, title = "score", f"Top voisins Jaccard avec '{focus}'"
    else:
        assoc = ingredients_analyzer.top_conditional_for(focus, filter_data.co_occurrence, k=k, min_co=min_co_focus)
        x_field, title = "P(B|A)", f"Top co-occurrents (P(B|A)) avec '{focus}'"

    st.pyplot(ingredients_analyzer.make_association_bar_fig(assoc, title, x=x_field))
    st.dataframe(assoc)

def render_complexity_tab():
    df = recipes_clean
    """Render the Complexity tab content in Streamlit."""
    st.header("Complexity")
    st.markdown(
        """
        Explore how **time**, **number of steps**, and **number of ingredients** relate to each other.
        We first look at each feature individually, then we inspect their relationships (pairplot + correlation matrix).
        """
    )

    st.subheader("Univariate exploration")
    feature = st.radio(
        "Choose a feature:",
        ["minutes", "n_steps", "n_ingredients"],
        horizontal=True,
    )

    col1, col2 = st.columns(2)
    hist_fig, box_fig = make_univariate_figs(df, feature, hue=("kind" if "kind" in df.columns else None))
    with col1:
        st.pyplot(hist_fig)
    with col2:
        st.pyplot(box_fig)
    if feature == "minutes":
        st.caption("ℹ️ Showing **log(minutes)** for readability (long tail).")

    st.subheader("Relationships between features")
    features_rel = ["log_minutes", "n_steps", "n_ingredients"]
    pair_fig = make_pairplot_fig(df, features_rel, hue=("kind" if "kind" in df.columns else None))
    st.pyplot(pair_fig)

    st.subheader("Correlation matrix")
    corr_fig = make_corr_heatmap_fig(df, features_rel, "Correlation (log_minutes, n_steps, n_ingredients)")
    st.pyplot(corr_fig)

def render_other_tab():
    """Render the Other tab content."""
    st.header("Other")
    st.subheader("Additional section placeholder")
    st.info("This tab can be customized for additional features.")

def main():
    """Main function to run the MangeTaMain Dashboard."""
    # App title
    st.title("MangeTaMain Dashboard")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Nutriscore", "Tags", "Ingredient", "Complexity"])

    with tab1:
        render_nutriscore_tab()

    with tab2:
        render_tags_tab()

    with tab3:
        render_ingredient_tab()

    with tab4:
        render_complexity_tab()

if __name__ == "__main__":
    main()
