import streamlit as st


def render_nutriscore_tab():
    """Render the Nutriscore tab content."""
    st.header("Nutriscore")
    st.subheader("Overview of nutritional scoring system")
    st.write(
        "Relation between tag and nutriscore."
        "Compute nutriscore with protein, fat, salt, sugar..."
        "What relation could we extract from nutriscore and other variable ?"
    )


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
