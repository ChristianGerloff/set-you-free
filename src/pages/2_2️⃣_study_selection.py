import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from utils.site_config import set_page_title


# configure page
set_page_title("Study selection")

st.subheader("Manual selection of publications")

if 'review' not in st.session_state:
    st.error("Please run the search first.")
else:
    # sidebar
    st.sidebar.title("Inspection settings")

    # criteria
    criterias = st.sidebar.multiselect("Select one or more criterias:",
                                       options=['default'],
                                       default='default')
    criterias = 'default' if criterias == '' else criterias

    st.sidebar.info(
        f"Reviewed papers: {len(st.session_state.review[st.session_state.review.reviewed == True])} of "
        f"{len(st.session_state.review)}"
    )

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
    selected_df = pd.DataFrame(selected)

    with st.spinner("Load publication..."):
        if not selected_df.empty:
            st.markdown(f"## {selected_df.loc[0, 'title']} \n"
                        f"***{selected_df.loc[0, 'doi']}***")
            st.markdown("## Abstract \n"
                        f"{selected_df.loc[0, 'abstract']}")

            # exclusion
            st.subheader("Decision...")

            exclude_col, submit_col = st.columns(2)

            exclude = exclude_col.checkbox(f"Exclude because: {criterias}", value=False)

            submit = submit_col.button("submit")

            if submit:
                st.session_state.review.loc[
                    st.session_state.review.id == selected_df.loc[0, 'id'],
                    'reviewed'
                ] = True
                st.session_state.review.loc[
                    st.session_state.review.id == selected_df.loc[0, 'id'],
                    'decision'
                ] = not exclude

        

