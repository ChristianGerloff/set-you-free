import findpapers as fp
import streamlit as st
import utils.consts as cs
import pandas as pd
import pickle
import datetime

from stqdm import stqdm
from streamlit_tags import st_tags

from utils.site_config import set_page_title
from utils.search_engine import set_search_str, set_search_btn
from utils.search_engine import convert_search_to_json
from utils.download import download_button

# configure page
set_page_title("Literature Search")

# set hwords to None
hwords = None
top_cite = 0

# user selection between loading and searching 
st.subheader("Search")
search_type = st.radio(
    "Select the search type:",
    options=["Load search", "Update search", "New search"]
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
elif search_type == "Update search":
    st.subheader("Load search")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # load pickle
        try:
            bytes_pickle = uploaded_file.getvalue()
            initial_search = pickle.loads(bytes_pickle)
            
            # get list of dbs but exclude crossref
            initial_databases = list(
                initial_search.papers_by_database.keys()
            )

            st.session_state.query_string = initial_search.query
            start_date = initial_search.since

        except Exception as e:
            st.warning("Please upload a file")
            st.stop()
    else:
        st.stop()

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

    # Add initial Abstract Title filter words to sitebar
    with st.sidebar:
        st.subheader("Filter keywords")
        hwords = st_tags(
            label='Enter words to exclude studies upfront',
            text='Press enter to add more',
            value=None,
            suggestions=cs.DEFAULT_HWORDS,
            maxtags=-1,
        )
    # Select only top citated papers of final search
    with st.sidebar:
        st.subheader("Top N citated papers")
        top_cite = st.number_input(
            "Select the top N citated papers",
            value=0,
            min_value=cs.CITE_MIN_NUM,
            max_value=cs.CITE_MAX_NUM,
            format="%i",
            step=1)
        # ensure that top_cite is integer
        top_cite = int(top_cite)


    # Duplication threshold here inverse definition
    st.sidebar.subheader("Duplication sensitivity")
    senitivity = st.sidebar.slider(
        "Required similarity between papers to be considered as duplicates.",
        value=cs.DUPLICATION_DEFAULT_SLIDER,
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
    databases = container.multiselect(
        "Select one or more Databases:",
        options=cs.AVAILABLE_DATABASES,
        default=initial_databases
    )

    # date picker
    st.subheader("Publication Date :calendar:")
    end_date = st.date_input("end date", min_value=start_date)

    # add two columns
    st.subheader("Search")
    search_col1, search_col2 = st.columns(2)
    with search_col2:
        ensure_left_join = st.checkbox(
            "Always inculde all initially selected papers",
            help=cs.HELP_LEFTJOIN,
            value=True
        )
    with search_col1:
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

    # Update new search by initial ratings to ensure that paper details are current (citations etc)
    # first check if a paper is in the initial search
    initial_keys = initial_search.paper_by_key.keys()
    # itterate over the dictionary search.paper_by_key.items()
    for key, paper in search.paper_by_key.items():
        if key in initial_keys:
            initial_paper = initial_search.paper_by_key.get(key, None)
            selected = None
            reasons = None
            if initial_paper.selected is not None:
                selected = initial_paper.selected
                reasons = initial_paper.criteria
            paper.review(
                selected=selected,
                criteria=reasons,
            )

    # Check if a paper was in the inital search but is no loger in the new search
    final_keys = search.paper_by_key.keys()
    left_disjoint = set(initial_keys).difference(final_keys)

    # warning if papers were left out
    if len(left_disjoint) > 0:
        st.warning(
            f"{len(left_disjoint)} papers from initial search were not found in the new search. \n"
            "A reason could be that a preprint was published."
            "Please check if the papers are still relevant."
        )
        # show papers left out in a table
        left_out = pd.DataFrame()
        for key in left_disjoint:
            paper = initial_search.paper_by_key.get(key, None)
            left_out_dict ={
                    'title': paper.title,
                    'authors': paper.authors,
                    'date': paper.publication_date,
                    'selected': paper.selected,
                    'criteria': paper.criteria
                }
            left_out = pd.concat(
                [left_out, pd.DataFrame.from_dict([left_out_dict])],
                ignore_index=True
            )

            if ensure_left_join:
                # add paper to search
                search.add_paper(paper)

        st.subheader("Papers no found in new search")
        st.dataframe(left_out, use_container_width=True)
        

    st.subheader("Update Information")
    # add markdown table
    st.markdown(f"""
        | **Parameter** | **Value** |
        | --- | --- |
        | Search string | {search.query} |
        | End date (initial) | {initial_search.since} |
        | End date | {search.until} |
        | Updated at | {search.processed_at} |
        | Results (initial) | {len(initial_search.papers)} | 
        | Results | {len(search.papers)} |
        | Reviewed (initial)| {sum([p.reviewed == True for p in initial_search.papers])} |
        | Reviewed | {sum([p.reviewed == True for p in search.papers])} |
    """
    )
        

elif search_type == "New search":
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

    # Add initial Abstract Title filter words to sitebar
    with st.sidebar:
        st.subheader("Filter keywords")
        hwords = st_tags(
            label='Enter words to exclude studies upfront',
            text='Press enter to add more',
            value=None,
            suggestions=cs.DEFAULT_HWORDS,
            maxtags=-1,
        )
    # Select only top citated papers
    with st.sidebar:
        st.subheader("Top N citated papers")
        top_cite = st.number_input(
            "Select the top N citated papers",
            value=0,
            min_value=cs.CITE_MIN_NUM,
            max_value=cs.CITE_MAX_NUM,
            format="%i",
            step=1)
        # ensure that top_cite is integer
        top_cite = int(top_cite)

    # Duplication threshold here inverse definition
    st.sidebar.subheader("Duplication sensitivity")
    senitivity = st.sidebar.slider(
        "Required similarity between papers to be considered as duplicates.",
        value=cs.DUPLICATION_DEFAULT_SLIDER,
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
    start_date = start_date_col.date_input(
        "start date",
        datetime.date(2000, 1, 1),
        max_value=datetime.date.today()
    )
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

# Update using the filter words from the sidebar if any word in hwords
if hwords is not None:
    for paper in search.papers:
        # check if filter words from the sidebar are in tile or abstract
        if (any(word in paper.title for word in hwords)
        or any(word in paper.abstract for word in hwords)
        or any(word in paper.keywords for word in hwords)):
            # reason based on hwords
            reasons = [f'title:{word}' for word in hwords if word in paper.title]
            reasons += [f'abstract:{word}' for word in hwords if word in paper.abstract]
            reasons += [f'keywords:{word}' for word in hwords if word in paper.keywords]
            paper.review(selected=False, criteria=reasons)

# filter top 100
if top_cite > 0:
    # sort set by highest citations if paper selected is True
    query = sorted(search.papers, key=lambda x: x.citations, reverse=True)

    # consider only paper where paper.selected is True
    query = [paper for paper in query if paper.selected is not False]

    # if length of query is greater than 100, take only the last 100
    if len(query) > 100:
        for paper in query[100:]:
            reasons = ['citations']
            paper.review(selected=False, criteria=reasons)

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
else:
    st.info("Override results!!!")
    if st.button("Yes I'm ready to override"):
        st.session_state.search = search
        st.session_state.ris_df = ris_df.copy()
        st.session_state.rayyan_df = rayyan_df.copy()
        st.session_state.review = ris_df.copy()

# display results   
ris_df = ris_df[cs.ORDER_SEARCH_RESULTS + 
                ris_df.columns.difference(cs.ORDER_SEARCH_RESULTS).tolist()]

if search_type == "Load search":
    st.subheader("Information")
    # add markdown table
    st.markdown(f"""
    | **Parameter** | **Value** |
    | --- | --- |
    | Databases | {', '.join(map(str, st.session_state.databases))} |
    | Search string | {st.session_state.search.query} |
    | Start date | {search.since} |
    | End date | {search.until} |
    | Processed | {search.processed_at} |
    | Limit per database | {search.limit_per_database} |
    | Total results | {len(search.papers)} |
    | Reviewed | {sum([p.reviewed == True for p in search.papers])} |
    """
)
    # convert list (st.session_state.databases) to string

    

    st.dataframe(ris_df, use_container_width=True)
    st.subheader("Download")
    json_download_col, ris_download_col, csv_download_col = st.columns(3)
else:
    st.dataframe(ris_df, use_container_width=True)
    st.subheader("Download")
    (pickle_download_col,
     json_download_col,
     ris_download_col,
     csv_download_col) = st.columns(4)
    with pickle_download_col:
        search_pickle = pickle.dumps(search)
        pickle_download_btn = download_button(
            search_pickle,
            f"{datetime.datetime.now().strftime('%Y%m%d')}_all_results.syf",
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