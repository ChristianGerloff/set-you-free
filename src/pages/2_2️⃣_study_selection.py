import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from utils.site_config import set_page_title

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

    if 'review' in st.session_state:                  
        st.session_state.review.loc[
            st.session_state.review.id == data['id'],
            'reviewed'
        ] = True
        st.session_state.review.loc[
            st.session_state.review.id == data['id'],
            'decision'
        ] = decision
        st.session_state.review.loc[
            st.session_state.review.id == data['id'],
            'decision_reasons'
        ] = reasons

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
        st.session_state.review.reviewed == True
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
    gb.configure_column(field='abstract', hide=True)
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
        st.session_state.review.reviewed == False
    ].head(1)
with st.spinner("Load publication..."):
    if not selected_df.empty:
        st.markdown(f"## {selected_df.iloc[0]['title']} \n"
                    f"***{selected_df.iloc[0]['doi']}***")
        st.markdown("## Abstract \n"
                    f"{selected_df.iloc[0]['abstract']}")
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
