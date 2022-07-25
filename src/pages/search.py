import datetime
import json
import numpy as np
import findpapers as fp
import graphviz as graphviz
import matplotlib.pyplot as plt
import streamlit as st
import utils.consts as cs

from matplotlib_venn import venn2, venn3
from utils.site_config import set_page_title
from utils.search_engine import build_search_str, single_search_str, get_search_str
from utils.search_engine import set_build_btns, set_single_btns

# configure page
set_page_title("Literature Search")

# sidebar
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

# result limits
st.sidebar.subheader("Result Limit")
limit = st.sidebar.slider("Please select the maximum number of papers per database.",
                          min_value=cs.RESULTS_MIN_SLIDER,
                          max_value=cs.RESULTS_MAX_SLIDER)

# database selection
st.subheader("Select the Database(s)")
container = st.container()
all_db_selected = st.checkbox("Select all", value=True)
if all_db_selected:
    databases = container.multiselect("Select one or more Databases:",
                                      options=cs.AVAILABLE_DATABASES,
                                      default=cs.AVAILABLE_DATABASES)
else:
    databases = container.multiselect("Select one or more Databases:",
                                      options=cs.AVAILABLE_DATABASES)

# date picker
st.subheader("Publication Date :calendar:")
start_date_col, end_date_col = st.columns(2)
start_date = start_date_col.date_input("start date",
                                       datetime.date(2021, 10, 1))
end_date = end_date_col.date_input("end date")

# query
st.subheader("Search String")
search_str_type = st.selectbox(
    "How would you like to enter the search string?",
    cs.SEARCH_STRING_TYPE
)

if search_str_type == cs.SEARCH_STRING_TYPE[1]:
    search_str_txt = build_search_str()
    search_state = set_build_btns(search_str_txt)
elif search_str_type == cs.SEARCH_STRING_TYPE[0]:
    search_str_txt = single_search_str()
    search_state = set_single_btns(search_str_txt)


search_string = get_search_str()

# search
if search_state and search_string == "":
    st.error("Please enter a search string")
elif search_state and search_string != "":
    search = fp.search(None,
                search_string,
                start_date,
                end_date,
                limit=limit * len(databases),
                limit_per_database=limit,
                databases=databases,
                publication_types=None,
                scopus_api_token=scopus_api_key,
                ieee_api_token=ieee_api_key,
                cross_reference_search=False,
                enrich=False,
                similarity_threshold=0.95)
    ris = fp.RisExport(search)
    ris_file, ris_df = ris.generate_ris('tmp.ris')
    results_as_df = st.sidebar.checkbox("View the results as dataframe",
        True)

    if results_as_df:
        st.dataframe(ris_df)