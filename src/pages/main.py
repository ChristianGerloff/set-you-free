import datetime
import pandas as pd
import streamlit as st
import findpapers as fp


RESULTS_MIN_SLIDER = 1
RESULTS_MAX_SLIDER = 1000
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


@st.cache
def convert_results(search: pd.DataFrame):
    """Cachs the converted search results

    Args:
        search (pd.DataFrame): rayyan search results

    Returns:
        csv (meme): encoded csv of rayyan compatible results
    """
    csv = search.to_csv().encode('utf-8')
    return csv


def join_string_in_list(list_of_string: list) -> str:
    """Joins the list of queries into one complete query.

    Args:
        list_of_string (list): List of queries.

    Returns:
        str: All queries combined.
    """
    return ' '.join(list_of_string)


def write():
    """Writes content to the app."""

    st.title("Set You Free")
    st.sidebar.title("Settings")

    st.sidebar.subheader("Please enter the following APIKeys")
    ieee_api_key = st.sidebar.text_input("IEEE APIKey", type="password")
    scopus_api_ley = st.sidebar.text_input("Scopus APIKey", type="password")

    # replace empty keys
    ieee_api_key = None if ieee_api_key == '' else ieee_api_key
    scopus_api_ley = None if scopus_api_ley == '' else scopus_api_ley
    
    st.sidebar.info("If you do not have an API key for scopus," +
                    " it can be obtained from " +
                    "[here](https://dev.elsevier.com/)")

    st.sidebar.subheader("Results required")
    limit = st.sidebar.slider("Please select the number of results required",
                              min_value=RESULTS_MIN_SLIDER,
                              max_value=RESULTS_MAX_SLIDER)

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
    start_date = col1.date_input("start date",
                                 datetime.date(2021, 10, 1))
    end_date = col2.date_input("end date")

    st.subheader("Search string :question:")
    str_col1, str_col2 = st.columns([3, 1])
    search_string = str_col1.text_input(
        "Please enter the search string", "")
    join_type = str_col2.selectbox(
        "Please select a type of join", JOIN_TYPES)
    add_button = st.button("Add")

    if "query_string" not in st.session_state:
        st.session_state.query_string = []

    if add_button and search_string == "":
        st.error("The search query can not be empty.")

    elif add_button and search_string != "":
        if join_type == "None":
            st.session_state.query_string.append("[" + search_string + "]")
        else:
            st.session_state.query_string.append(
                "[" + search_string + "]" + " " + join_type)

    if search_string != "":
        st.write("**Query string** :astonished:")
        search_string = join_string_in_list(st.session_state.query_string)
        st.write(search_string)

    search_button = st.button("Search")
    if search_button:
        search = fp.search(None,
                           search_string,
                           start_date,
                           end_date,
                           limit*len(selected_options),
                           limit,
                           selected_options,
                           None,
                           scopus_api_ley,
                           ieee_api_key)
        search_export = fp.RayyanExport(search)
        rayyan = pd.DataFrame(search_export.rayyan)
        rayyan_csv = convert_results(rayyan)
        results_as_df = st.sidebar.checkbox("View the results as dataframe",
                                            True)
        if results_as_df:
            st.dataframe(rayyan)

        st.subheader("Download the results")
        button_col_1, button_col_2 = st.columns(2)
        button_col_1.download_button(label="Download CSV",
                                     data=rayyan_csv,
                                     file_name='set_you_free_results.csv',
                                     mime='text/csv')
        #bib_download_button = button_col_2.button("Download Bib")
        #if bib_download_button:
            #st.write("Bib download button is working.")
