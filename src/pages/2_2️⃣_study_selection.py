
import re
import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from utils.site_config import set_page_title

def highlight_words(text, words_to_highlight):
    for word in words_to_highlight:
        # replace word with highlighted version indepent of lower or upper case
        compiled = re.compile(re.escape(word), re.IGNORECASE)
        text = compiled.sub(
            f'<span style="color:#e05c54">{word}</span>',
            text
        )
        #text = text.replace(word, f'<span style="color:#e05c54">{word}</span>')
    return text


def updata_review(data: pd.DataFrame,
                  decision: bool = True,
                  reasons: list = None):
    """Update the review dataframe with the selected data.

    Args:
        data (pd.DataFrame): Dataframe with the selected data.
        decision (bool, optional): Decision of the reviewer,
            True means include, False means exclude. Defaults to True.
        reasons (list, optional): Reasons for the decision.
    """

    # get first entry of data
    data = data.iloc[0:1, :]

    if 'review' in st.session_state:                  
        st.session_state.review.loc[
            st.session_state.review.id.isin(data['id'].values),
            'custom2'
        ] = True
        st.session_state.review.loc[
            st.session_state.review.id.isin(data['id'].values),
            'custom1'
        ] = decision
        st.session_state.review.loc[
            st.session_state.review.id.isin(data['id'].values),
            'custom3'
        ] = reasons

    # update search object
    paper = st.session_state.search.get_paper(
        data['title'].values[0],
        pd.to_datetime(data['date'].values[0]).date(),
        data['doi'].values[0]
    )
    paper.review(selected=decision, criteria=reasons)

# configure page
set_page_title("Study screening")

if 'review' not in st.session_state:
    st.error("Please run the search first.")
    st.stop()
    
# sidebar
st.sidebar.title("Inspection settings")

# criteria
criterias = st.sidebar.multiselect("Select one or more criterias:",
                                   options=['default'],
                                   default='default')
criterias = 'default' if criterias == '' else criterias

n_reviewed = len(
    st.session_state.review[
        st.session_state.review.custom2 == True
    ]
)
st.sidebar.info(
    f"Reviewed papers: {n_reviewed} of "
    f"{len(st.session_state.review)}"
)

paper_pick = st.sidebar.radio(
            "Pick paper for review:",
            options=["auto", "manual"],
)

# prepare words for highlighting
hwords = st.session_state.search.query    
replace = ['[', ']', '(', ')', 'AND', 'OR']
for item in replace:
    hwords = hwords.replace(item, '')
# seperate each word by ' ' and create a list and delete empty entries and duplicates
hwords = list(set(hwords.split(' ')))

# remove ''
if '' in hwords:
    hwords.remove('')

if paper_pick == "manual":
    st.subheader("Manual selection of publications")
    # select study
    st.info(
        "You can use the checkbox in the table (see doi) to select a publication. "
        "The decision column describes which publications are included in your results."
    )

    gb = GridOptionsBuilder.from_dataframe(st.session_state.review)
    gb.configure_column(field='custom1', editable=True)
    gb.configure_column(field='custom2', editable=True)
    gb.configure_column(field='custom3')
    gb.configure_column(field='abstract', hide=True)
    gb.configure_column(field='id', hide=True)
    gb.configure_column(field='authors', hide=True)
    #gb.configure_column(field='title', pinned='left')
    gb.configure_column(field='doi', pinned='left', checkboxSelection=True)
    gb.configure_selection('single')  # use_checkbox=True
    gb.configure_grid_options(stopEditingWhenCellsLoseFocus=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    build_gb = gb.build()
    grid = AgGrid(
        data=st.session_state.review,
        update_mode=GridUpdateMode.__members__['MODEL_CHANGED'],
        data_return_mode=DataReturnMode.__members__['AS_INPUT'],
        gridOptions=build_gb,
        fit_columns_on_grid_load=False,
        theme='streamlit',
        enable_enterprise_modules=True)

    st.session_state.review = grid['data']
    selected = grid['selected_rows']
    selected_df = pd.DataFrame(selected).head(1)
else:
    # select first paper that is not reviewed
    selected_df = st.session_state.review[
        st.session_state.review.custom2 == False
    ].head(1)
with st.spinner("Load publication..."):
    if not selected_df.empty:
        abstract = highlight_words(
            selected_df.iloc[0]['abstract'],
            hwords
        )
        title = highlight_words(
            selected_df.iloc[0]['title'],
            hwords
        )

        paper = st.session_state.search.get_paper(
            selected_df['title'].values[0],
            pd.to_datetime(selected_df['date'].values[0]).date(),
            selected_df['doi'].values[0]
        )

        first_author = paper.authors[0]
        if len(paper.authors) > 1:
            other_authrors = paper.authors[1:]
            other_authrors_str = ' | '+ ' | '.join(other_authrors)
        else:
            other_authrors_str = ''
        
        st.markdown(
            f"## {title} \n"
            f"***{first_author}***"
            f"{other_authrors_str} \n \n"
            f"***{selected_df.iloc[0]['doi']}***",
            unsafe_allow_html=True
        )
        st.markdown(
            f"## Abstract \n {abstract}",
            unsafe_allow_html=True
        )
        # exclusion
        st.subheader("Decision...")
        include_col, exclude_col = st.columns(2)

        decision_str = st.radio(
            "Select the search type:",
            options=["include", "exclude"]
        )
        decision = True if decision_str == "include" else False

        if decision:
            reason = None
            st.success("Paper will be included if you submit")
        else:
            reason = st.multiselect(
                'Exlcusion reason:',
                options=criterias,
                default=criterias
            )
            st.error("Paper will be excluded if you submit")
        
        submit = st.button(
                 "Submit",
                 on_click=updata_review,
                 args=(selected_df, decision, reason)
        )

        # if submit next paper
        if submit and paper_pick != "manual":
            st.experimental_rerun()
            