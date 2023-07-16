"""General site settings"""

import streamlit as st


def set_page_title(title: str = "Set You Free"):
    """Set the page title.

    Args:
        title (str, optional): The title. Defaults to "Set You Free".
    """
    st.set_page_config(page_title=title,
                       page_icon="📊",
                       initial_sidebar_state="expanded")
    set_page_style()


def set_page_style():
    """Set the page style."""
    # adjust styling
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
