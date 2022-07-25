"""Search functionalities definition."""

import json
import streamlit as st
import findpapers as fp
import utils.consts as cs


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


def get_search_str():
    """Get the search string.

    Returns:
        str: search string.
    """
    if isinstance(st.session_state.query_string, list):
        query = st.session_state.query_string
        search_string = join_string_in_list(query)
    else:
        search_string = st.session_state.query_string
    return search_string


def build_search_str():
    """Builds the search string.

    Returns:
        str: Search string.
    """
    search_str_col, operator_col = st.columns([3, 1])
    search_string = search_str_col.text_input("Please enter the search string", "")
    operator = operator_col.selectbox("Please select how to join your search strings", cs.JOIN_TYPES)
    add_button = st.button("Add")

    if "query_string" not in st.session_state:
        st.session_state.query_string = []

    if add_button and search_string == "":
        st.error("The search query can not be empty.")

    # append search string current session data
    elif add_button and search_string != "":
        st.session_state.query_string.append(f"[{search_string}]")
        if operator != "None":
            st.session_state.query_string.append(operator)

    search_str_txt = st.empty()
    if search_string != "":
        st.write("**Query** :astonished:")
        search_string = join_string_in_list(st.session_state.query_string)
        search_str_txt.write(search_string)
    return search_str_txt


def single_search_str():
    """Single search string definition.

    Returns:
        str: Search string.
    """
    if "query_string" not in st.session_state:
        st.session_state.query_string = []

    search_string = st.text_input(
        "Please enter the search string", "")
    add_button = st.button("Add")

    if add_button and search_string == "":
        st.error("Please enter a search string")

    search_str_txt = st.empty()
    if search_string != "":
        st.write("**Query** :astonished:")
        search_str_txt.write(search_string)
        st.session_state.query_string = search_string

    return search_str_txt


def clear_search_str(search_str_txt, clear_all: bool = False):
    """Clears the search string.

    Args:
        search_str_txt (streamlit label): Search string label
        clear_all (bool, optional): Clear all search string. Defaults to False.
    """
    # None operator
    if (len(st.session_state.query_string) > 1 and
       clear_all is False):
        del st.session_state.query_string[-1:]
    # operator
    elif (len(st.session_state.query_string) > 1 and
          clear_all is True and
          st.session_state.query_string[-2] in cs.JOIN_TYPES):
        del st.session_state.query_string[-2:]
    elif isinstance(st.session_state.query_string, list):
        st.session_state.query_string.clear()
    elif isinstance(st.session_state.query_string, str):
        st.session_state.query_string = ""
    search_string = join_string_in_list(st.session_state.query_string)
    search_str_txt.write(search_string)


def set_build_btns(search_str_txt) -> bool:
    """Set the build search buttons.

    Args:
        search_str_txt (streamlit label): Search string label

    Returns:
        bool: search button state
    """

    search_col, clear_col, remove_last_col = st.columns(3)
    search_btn = search_col.button("Search")
    clear_btn = clear_col.button("Clear all")
    remove_last_btn = remove_last_col.button("Remove the last query")

    # query cleaning
    if clear_btn:
        clear_search_str(search_str_txt, clear_all=True)
    if remove_last_btn:
        clear_search_str(search_str_txt, clear_all=False)

    return search_btn


def set_single_btns(search_str_txt):
    """Set the search buttons.

    Args:
        search_str_txt (streamlit label): Search string label

    Returns:
        bool: search button state
    """
    search_col, clear_col = st.columns(2)
    search_btn = search_col.button("Search")
    clear_btn = clear_col.button("Clear all")

    # query cleaning
    if clear_btn:
        clear_search_str(search_str_txt, clear_all=True)
    return search_btn
