import streamlit as st

AVAILABLE_DATABASES = [
    'ACM',
    'arXiv',
    'bioRxiv',
    'IEEE',
    'medRxiv',
    'PubMed',
    'Scopus'
]


def write():
    """Writes content to the app."""
    st.title("Set You Free")
    st.sidebar.title("Settings")

    st.subheader("Select the Database(s)")
    container = st.container()
    all = st.checkbox("Select all")

    if all:
        selected_options = container.multiselect(
            "Select one or more Databases:",
            options=AVAILABLE_DATABASES,
            default=AVAILABLE_DATABASES
        )
    else:
        selected_options = container.multiselect(
            "Select one or more Databases:",
            options=AVAILABLE_DATABASES
        )
