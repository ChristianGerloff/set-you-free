import streamlit as st

AVAILABLE_DATABASES = [
    "ACM",
    "arXiv",
    "bioRxiv",
    "IEEE",
    "medRxiv",
    "PubMed",
    "Scopus"
]

JOIN_TYPES = [
    "None",
    "(",
    ")",
    "AND",
    "OR",
    "(AND",
    "(OR"
]


def write():
    """Writes content to the app."""
    st.title("Set You Free")
    st.sidebar.title("Settings")

    st.sidebar.subheader("Please enter the following APIKeys")
    ieee_api_key = st.sidebar.text_input("IEEE APIKey", type="password")
    scopus_api_ley = st.sidebar.text_input("Scopus APIKey", type="password")
    st.sidebar.info("If you do not have an API key for scopus," +
                    " it can be obtained from " +
                    "[here](https://dev.elsevier.com/)")

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

    st.subheader("Date Picker :calendar:")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("start date")
    end_date = col2.date_input("end date")

    # https://blog.streamlit.io/session-state-for-streamlit/
    st.subheader("Search string :question:")
    str_col1, str_col2 = st.columns([3, 1])
    search_string = str_col1.text_input(
        "Please enter the search string", "")
    join_type = str_col2.selectbox(
        "Please select a type of join", JOIN_TYPES)
    add_button = st.button("Add")

    if "query_string" not in st.session_state:
        st.session_state.query_string = []

    if add_button:
        if join_type == "None":
            st.session_state.query_string.append("[" + search_string + "]")
        else:
            st.session_state.query_string.append(
                "[" + search_string + "]" + " " + join_type)

    st.write("**Query string** :astonished:")
    st.write(str(st.session_state.query_string))

    search_button = st.button("Search")
    if search_button:
        st.write("The search button is working.")
