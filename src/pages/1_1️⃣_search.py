import datetime
import findpapers as fp
import streamlit as st
import utils.consts as cs
import pickle

from stqdm import stqdm
from utils.site_config import set_page_title
from utils.search_engine import set_search_str, set_search_btn
from utils.search_engine import convert_search_to_json
from utils.download import download_button

# configure page
set_page_title("Literature Search")

# user selection between loading and searching 
st.subheader("Search")
search_type = st.radio(
    "Select the search type:",
    options=["Load search", "New search"]
)

# load search
if search_type == "Load search":
    st.subheader("Load search")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # load pickle
        try:
            bytes_pickle = uploaded_file.getvalue()
            search = pickle.loads(bytes_pickle)
            # get list of dbs but exclude crossref
            st.session_state.databases = list(
                search.papers_by_database.keys()
            )
        except Exception as e:
            st.warning("Please upload a file")
            st.stop()
    else:
        st.stop()
else:

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
        st.sidebar.info(
            "If you do not have an API key for scopus,"
            " it can be obtained from "
            "[here](https://dev.elsevier.com/)"
    )

    # result limits
    st.sidebar.subheader("Maximum number of papers")
    limit = st.sidebar.slider(
        "Please select the maximum number of papers per database.",
        min_value=cs.RESULTS_MIN_SLIDER,
        max_value=cs.RESULTS_MAX_SLIDER,
        value=cs.RESULTS_DEFAULT_SLIDER
    )

    # Duplication threshold here inverse definition
    st.sidebar.subheader("Duplication sensitivity")
    senitivity = st.sidebar.slider(
        "Required similarity between papers to be considered as duplicates.",
        min_value=cs.DUPLICATION_MIN_SLIDER,
        max_value=cs.DUPLICATION_MAX_SLIDER,
        step=cs.DUPLICATION_STEP_SLIDER
    )
    similarity_threshold = 1 - (senitivity - cs.DUPLICATION_MIN_SLIDER)

    # progress bar
    st.sidebar.subheader("Show progress bar")
    show_pbar = st.sidebar.checkbox(
        "Show the progress bar while downloading the papers",
        value=True
    )

    # database selection
    st.subheader("Select the Database(s)")
    container = st.container()
    all_db_selected = st.checkbox("Select all", value=True)
    databases = container.multiselect(
        "Select one or more Databases:",
        options=cs.AVAILABLE_DATABASES,
        default=cs.AVAILABLE_DATABASES if all_db_selected else None
    )

    st.session_state.databases = databases

    # date picker
    st.subheader("Publication Date :calendar:")
    start_date_col, end_date_col = st.columns(2)
    start_date = start_date_col.date_input("start date",
                                        datetime.date(2000, 1, 1))
    end_date = end_date_col.date_input("end date")

    # query
    st.subheader("Search String")
    set_search_str()
    set_search_btn()

    # search
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

    # search
    search = fp.search(
        None,
        st.session_state.query_string,
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
        pbar=pbar
    )
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
        st.session_state.review.insert(1, 'decision_reasons', None)
        st.session_state.review.insert(1, 'decision', True)
        st.session_state.review.insert(1, 'reviewed', False)

# display results   
ris_df = ris_df[cs.ORDER_SEARCH_RESULTS + 
                ris_df.columns.difference(cs.ORDER_SEARCH_RESULTS).tolist()]
st.dataframe(ris_df,
             use_container_width=True)

# download results via link since download button performs refresh of the page
st.subheader("Download")

if search_type == "Load search": 
    json_download_col, ris_download_col, csv_download_col = st.columns(3)
else:
    (pickle_download_col,
     json_download_col,
     ris_download_col,
     csv_download_co) = st.columns(4)
    with pickle_download_col:
        search_pickle = pickle.dumps(search)
        pickle_download_btn = download_button(
                search_pickle,
                'results.syf',
                'All results - SYF'
            )
        st.markdown(pickle_download_btn, unsafe_allow_html=True)    
with json_download_col:
    json_download_btn = download_button(
        result_json,
        'set_you_free_results.json',
        'Overview - JSON'
    )
    st.markdown(json_download_btn, unsafe_allow_html=True)
with ris_download_col:
    ris_download_btn = download_button(
        ris_file,
        'set_you_free_cadima.ris',
        'CADIMA - RIS'
    )
    st.markdown(ris_download_btn, unsafe_allow_html=True)
with csv_download_col:
    csv_download_btn = download_button(
        rayyan_file,
        'set_you_free_rayyan.csv',
        'Rayyan - CSV'
    )
    st.markdown(csv_download_btn, unsafe_allow_html=True)