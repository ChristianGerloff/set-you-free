"""Search functionalities definition."""

import json
import streamlit as st
import findpapers as fp
import utils.consts as cs


#@st.cache_data
def convert_search_to_json(_search: fp.models.search):
    """Cachs the converted search results

    Args:
        search (findpapers.models.search): search results

    Returns:
        json (meme): encoded json
    """
    results = fp.models.search.Search.to_dict(_search)
    result = json.dumps(results, indent=2, sort_keys=True)
    return result


def set_search_str():
    """Single search string definition.

    Returns:
        str: Search string.
    """
    if "query_string" not in st.session_state:
        st.session_state.query_string = []

    search_string = st.text_input(
        (
            "Please enter the search string"
            "(e.g., [term a] OR ([term b] AND ([term c] OR [term d])"
        ),
        "",
        help=cs.HELP_SEARCH_STRING,
    )
    st.session_state.query_string = search_string

def set_search_btn():
    """Set the search buttons.
    """
    
    search_btn = st.button("Search")
    if search_btn is False:
        st.stop()
    elif search_btn is True and st.session_state.query_string == "":
        st.error("The search query can not be empty.")
        st.stop()
