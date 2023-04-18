import datetime
import findpapers as fp
import streamlit as st
import utils.consts as cs

from stqdm import stqdm
from utils.site_config import set_page_title
from utils.search_engine import single_search_str, get_search_str
from utils.search_engine import set_single_btns
from utils.search_engine import convert_search_to_json

# configure page
set_page_title("Literature Search")

# sidebar
st.sidebar.title("Search settings")

# general settings
st.sidebar.write("We recommend using time-consuming enrich and cross-references "
                 "features only in console mode.")
enrich_col, cross_search_col = st.sidebar.columns(2)
enrich = enrich_col.checkbox("Enrich papers", value=False, help=cs.HELP_ENRICH)
cross_search = cross_search_col.checkbox(
    "Cross-references",
    value=False,
    help=cs.HELP_CROSS_REF
)

if enrich is True or cross_search is True:
    st.sidebar.info("We recommend using time-consuming enrich and" 
                    "cross-references features only in console mode.")

# publication types
pub_types = st.sidebar.multiselect("Select one or more publication types:",
                                   options=cs.AVAILABLE_PUBTYPES,
                                   default=cs.DEFAULT_PUBTYPES)
pub_types = None if pub_types == '' or 'all' else pub_types

# API keys
st.sidebar.subheader("Please enter the following API keys")
ieee_api_key = st.sidebar.text_input("IEEE API key", type="password")
scopus_api_key = st.sidebar.text_input("Scopus API key", type="password")

# replace empty keys
ieee_api_key = None if ieee_api_key == '' else ieee_api_key
scopus_api_key = None if scopus_api_key == '' else scopus_api_key

if scopus_api_key is None:
    st.sidebar.info("If you do not have an API key for scopus,"
                    " it can be obtained from "
                    "[here](https://dev.elsevier.com/)")

# result limits
st.sidebar.subheader("Maximum number of papers")
limit = st.sidebar.slider("Please select the maximum number of papers per database.",
                          min_value=cs.RESULTS_MIN_SLIDER,
                          max_value=cs.RESULTS_MAX_SLIDER,
                          value=cs.RESULTS_DEFAULT_SLIDER)

# Duplication threshold here inverse definition
st.sidebar.subheader("Duplication sensitivity")
senitivity = st.sidebar.slider(
    "Please select the maximum number of papers per database.",
    min_value=cs.DUPLICATION_MIN_SLIDER,
    max_value=cs.DUPLICATION_MAX_SLIDER,
    step=cs.DUPLICATION_STEP_SLIDER
)
similarity_threshold = 1 - (senitivity - cs.DUPLICATION_MIN_SLIDER)

# progress bar
st.sidebar.subheader("Show progress bar")
show_pbar = st.sidebar.checkbox("Show the progress bar while downloading the papers",
                                value=True)

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

st.session_state.databases = databases

# date picker
st.subheader("Publication Date :calendar:")
start_date_col, end_date_col = st.columns(2)
start_date = start_date_col.date_input("start date",
                                       datetime.date(2021, 10, 1))
end_date = end_date_col.date_input("end date")

# query
st.subheader("Search String")

search_str_txt = single_search_str()
search_state = set_single_btns(search_str_txt)


search_string = get_search_str()

# search
if search_state and search_string == "":
    st.error("Please enter a search string")
elif search_state and search_string != "":
    if ieee_api_key is None and 'IEEE' in databases:
        st.info('IEEE API token not found, skipping search on this database')
        databases.remove('IEEE')
    if scopus_api_key is None and 'Scopus' in databases:
        st.info('Scopus API token not found, skipping search on this database')
        databases.remove('Scopus')
    st.write("Please wait till the results are obtained")
    if show_pbar:
        pbar = stqdm(desc='Progess', total=limit*len(databases))
    else:
        pbar = None
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
                       similarity_threshold=similarity_threshold,
                       pbar=pbar)
    if show_pbar:
        pbar.close()

    if len(search.papers) == 0:
        st.warning("No search results found!")
        st.stop()

    # process search results
    result_json = convert_search_to_json(search)
    search_export = fp.RayyanExport(search)
    rayyan_file, rayyan_df = search_export.generate_rayyan_csv()
    ris = fp.RisExport(search)
    ris_file, ris_df = ris.generate_ris()

    # store session data
    if 'review' not in st.session_state:
        st.session_state.search = search
        st.session_state.ris_df = ris_df.copy()
        st.session_state.rayyan_df = rayyan_df.copy()
        st.session_state.review = ris_df.copy()
        st.session_state.review.insert(1, 'criteria', 'default')
        st.session_state.review.insert(1, 'decision', True)
        st.session_state.review.insert(1, 'reviewed', False)
    else:
        st.info("Override results!!!")
        if st.button("Yes I'm ready to override"):
            st.session_state.search = search
            st.session_state.ris_df = ris_df.copy()
            st.session_state.rayyan_df = rayyan_df.copy()
            st.session_state.review = ris_df.copy()
            st.session_state.review.insert(1, 'criteria', 'default')
            st.session_state.review.insert(1, 'decision', True)
            st.session_state.review.insert(1, 'reviewed', False)

        # display results
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