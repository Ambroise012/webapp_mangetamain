import streamlit as st

from webapp_mangetamain.load_config import recipe
from nutriscore_analyzer import (
    parse_nutrition,
    filter_data_with_nutri,
    add_nutriscore_column,
    correlation_matrix,
    plot_nutriscore_comparison
)

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

def render_tags_tab():
    """Render the Tags tab content."""
    st.header("Tags")
    st.subheader("Food categorization and labeling")
    st.write(
        "Notes / time / complexity per tags"
    )

def render_ingredient_tab():
    """Render the Ingredient tab content."""
    st.header("Ingredient")
    st.subheader("List of ingredients and details")
    st.write(
        "Frequancy of ingredient / note per ingredients, time correlated with some ingredient..."
    )

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
    tab1, tab2, tab3, tab4 = st.tabs(["Nutriscore", "Tags", "Ingredient", "Other"])

    with tab1:
        render_nutriscore_tab()

    with tab2:
        render_tags_tab()

    with tab3:
        render_ingredient_tab()

    with tab4:
        render_other_tab()

if __name__ == "__main__":
    main()
