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
    all_db_selected = st.checkbox("Select all", value=True)

    if all_db_selected:
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

    print(selected_options)

    st.subheader("Date Picker")
    start_date = st.date_input("start date")
    end_date = st.date_input("end date")
