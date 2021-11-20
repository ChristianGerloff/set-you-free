import datetime
import json

import findpapers as fp
import graphviz as graphviz
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib_venn import venn2, venn3

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
SEARCH_STRING_TYPE = [
    "Insert search string directly",
    "Build search string"
]


@st.cache
def convert_search_to_json(search: fp.models.search):
    """Cachs the converted search results

    Args:
        search (findpapers.models.search): search results

    Returns:
        json (meme): encoded json
    """
    results = fp.models.search.Search.to_dict(search)
    result = json.dumps(results, indent=2, sort_keys=True)
    return result


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
    scopus_api_key = st.sidebar.text_input("Scopus APIKey", type="password")

    # replace empty keys
    ieee_api_key = None if ieee_api_key == '' else ieee_api_key
    scopus_api_key = None if scopus_api_key == '' else scopus_api_key

    st.sidebar.info("If you do not have an API key for scopus," +
                    " it can be obtained from " +
                    "[here](https://dev.elsevier.com/)")

    st.sidebar.subheader("Result Limit")
    limit = st.sidebar.slider("Please select the maximum number of papers per database.",
                              min_value=RESULTS_MIN_SLIDER,
                              max_value=RESULTS_MAX_SLIDER)

    st.subheader("Select the Database(s)")
    container = st.container()
    all_db_selected = st.checkbox("Select all", value=True)

    if all_db_selected:
        databases = container.multiselect(
            "Select one or more Databases:",
            options=AVAILABLE_DATABASES,
            default=AVAILABLE_DATABASES
        )
    else:
        databases = container.multiselect(
            "Select one or more Databases:",
            options=AVAILABLE_DATABASES
        )

    st.subheader("Date Picker :calendar:")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("start date",
                                 datetime.date(2021, 10, 1))
    end_date = col2.date_input("end date")

    st.subheader("Search string :question:")
    search_string_type = st.selectbox(
        "How would you like to enter the search string?",
        SEARCH_STRING_TYPE
    )
    if search_string_type == "Build search string":
        str_col1, str_col2 = st.columns([3, 1])
        search_string = str_col1.text_input(
            "Please enter the search string", "")
        join_type = str_col2.selectbox(
            "Please select how to join your search strings", JOIN_TYPES)
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
                    "[" + search_string + "]")
                st.session_state.query_string.append(join_type)

        search_string_op = st.empty()
        if search_string != "":
            st.write("**Query string** :astonished:")
            search_string = join_string_in_list(st.session_state.query_string)
            search_string_op.write(search_string)

    else:
        if "query_string" not in st.session_state:
            st.session_state.query_string = []

        search_string = st.text_input(
            "Please enter the search string", "")
        if search_string == "":
            st.error("Please enter a search string")

        search_string_op = st.empty()
        if search_string != "":
            st.write("**Query string** :astonished:")
            search_string_op.write(search_string)

    search_col, clear_col, remove_last_string_col = st.columns(3)
    search_button = search_col.button("Search")
    clear_button = clear_col.button("Clear the entire query")
    remove_last_string_button = remove_last_string_col.button(
        "Remove the last query")

    if clear_button:
        st.session_state.query_string.clear()
        search_string_op.write("")
        st.warning("Your query has been cleared")

    if remove_last_string_button:
        if len(st.session_state.query_string) > 1 and st.session_state.query_string[-2] in JOIN_TYPES:
            del st.session_state.query_string[-2:]
            search_string_op.write(join_string_in_list(
                st.session_state.query_string
            ))
        elif len(st.session_state.query_string) == 1:
            st.warning("Please press the **Clear the " +
                       "entire query** button to delete the entire query")

    if search_button and search_string == "":
        st.error("The query can not be empty")
    elif search_button and search_string != "":
        st.write("Please wait till the results are obtained")
        search = fp.search(None,
                           search_string,
                           start_date,
                           end_date,
                           limit*len(databases),
                           limit,
                           databases,
                           None,
                           scopus_api_key,
                           ieee_api_key)
        search_export = fp.RayyanExport(search)
        rayyan_csv, rayyan = search_export.generate_rayyan_csv()

        result_json = convert_search_to_json(search)
        results_as_df = st.sidebar.checkbox("View the results as dataframe",
                                            True)
        if results_as_df:
            st.dataframe(rayyan)

        st.subheader('PRISMA Information')
        all_papers = rayyan.explode('databases')
        stats_databses = all_papers.groupby(['databases'])['key'].apply(list)
        n_duplicates = len(all_papers)-len(rayyan)

        prisma = graphviz.Digraph('PRISMA')
        prisma.attr('node', shape='box')
        prisma.node('Identification')
        prisma.node('Screening')
        prisma.edge('Identification', 'Screening', label=str(n_duplicates))

        if len(databases) == 2:
            col_prisma_1, col_prisma_2 = st.columns(2)
            venn2([set(stats_databses[databases[0]]),
                   set(stats_databses[databases[1]])],
                  set_labels=databases)
            col_prisma_1.graphviz_chart(prisma)
            col_prisma_2.pyplot(plt)
        elif len(databases) == 3:
            col_prisma_1, col_prisma_2 = st.columns(2)
            venn3([set(stats_databses[databases[0]]),
                   set(stats_databses[databases[1]]),
                   set(stats_databses[databases[1]])],
                  set_labels=databases)
            col_prisma_1.graphviz_chart(prisma)
            col_prisma_2.pyplot(plt)
        else:
            st.graphviz_chart(prisma)

        st.subheader("Download")
        download_csv, download_json = st.columns(2)
        download_csv.download_button(label='Rayyan - CSV',
                                     data=rayyan_csv,
                                     file_name='set_you_free_rayyan.csv',
                                     mime='text/csv')
        download_json.download_button(label='Details - JSON',
                                      data=result_json,
                                      file_name='set_you_free_results.json',
                                      mime='text/plain')
