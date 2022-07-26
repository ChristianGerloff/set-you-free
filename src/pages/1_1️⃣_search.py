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
from utils.search_engine import convert_search_to_json

# configure page
set_page_title("Literature Search")


# sidebar
st.sidebar.title("Search settings")

# general settings
st.sidebar.write("We recommend using time-consuming enrich and cross-references features only in console mode.")
enrich_col, cross_search_col = st.sidebar.columns(2)
enrich = enrich_col.checkbox("Enrich papers", value=False)
cross_search = cross_search_col.checkbox("Cross-references", value=False)

if enrich is True or cross_search is True:
    st.sidebar.info("We recommend using time-consuming enrich and" 
                    "cross-references features only in console mode.")

# publication types
pub_types = st.sidebar.multiselect("Select one or more publication types:",
                                   options=cs.AVAILABLE_PUBTYPES,
                                   default=cs.DEFAULT_PUBTYPES)

# API keys
st.sidebar.subheader("Please enter the following API Keys")
ieee_api_key = st.sidebar.text_input("IEEE APIKey", type="password")
scopus_api_key = st.sidebar.text_input("Scopus APIKey", type="password")

if scopus_api_key is None:
    st.sidebar.info("If you do not have an API key for scopus,"
                    " it can be obtained from "
                    "[here](https://dev.elsevier.com/)")

# replace empty keys
ieee_api_key = None if ieee_api_key == '' else ieee_api_key
scopus_api_key = None if scopus_api_key == '' else scopus_api_key


# result limits
st.sidebar.subheader("Maximum number of papers")
limit = st.sidebar.slider("Please select the maximum number of papers per database.",
                          min_value=cs.RESULTS_MIN_SLIDER,
                          max_value=cs.RESULTS_MAX_SLIDER,
                          value=cs.RESULTS_DEFAULT_SLIDER)

# Duplication threshold here inverse definition
st.sidebar.subheader("Duplication sensitivity")
senitivity = st.sidebar.slider("Please select the maximum number of papers per database.",
                               min_value=cs.DUPLICATION_MIN_SLIDER,
                               max_value=cs.DUPLICATION_MAX_SLIDER,
                               step=cs.DUPLICATION_STEP_SLIDER)
similarity_threshold = 1 - (senitivity - cs.DUPLICATION_MIN_SLIDER)

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
    st.write("Please wait till the results are obtained")
    search = fp.search(None,
                       search_string,
                       start_date,
                       end_date,
                       limit=limit * len(databases),
                       limit_per_database=limit,
                       databases=databases,
                       publication_types=pub_types,
                       scopus_api_token=scopus_api_key,
                       ieee_api_token=ieee_api_key,
                       cross_reference_search=cross_search,
                       enrich=enrich,
                       similarity_threshold=similarity_threshold)

    # process search results
    result_json = convert_search_to_json(search)
    search_export = fp.RayyanExport(search)
    rayyan_file, rayyan_df = search_export.generate_rayyan_csv()
    ris = fp.RisExport(search)
    ris_file, ris_df = ris.generate_ris()
    st.dataframe(ris_df)

    # download results
    st.subheader("Download")
    download_json, download_ris, download_csv, = st.columns(3)
    download_json.download_button(label='Details - JSON',
                                  data=result_json,
                                  file_name='set_you_free_results.json',
                                  mime='text/plain')
    download_ris.download_button(label='CADIMA - RIS',
                                 data=ris_file,
                                 file_name='set_you_free_cadima.ris',
                                 mime='text/plain')                              
    download_csv.download_button(label='Rayyan - CSV',
                                 data=rayyan_file,
                                 file_name='set_you_free_rayyan.csv',
                                 mime='text/csv')

