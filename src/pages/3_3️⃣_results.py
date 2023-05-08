import pandas as pd
import streamlit as st
import graphviz as graphviz
import matplotlib.pyplot as plt
import findpapers as fp

from datetime import datetime
from matplotlib_venn import venn2, venn3
from utils.site_config import set_page_title
from utils.search_engine import convert_search_to_json
from utils.download import download_button

# configure page
set_page_title("Results of search")

if 'rayyan_df' not in st.session_state:
    st.error("Please run the search first.")
elif 'review' in st.session_state:
    review = st.session_state.review.copy()
    final_search = st.session_state.search
    papers = review.loc[
        review["decision"] == False,
        ['title', 'date', 'doi']
    ]

    if not papers.empty:
        for _, p in papers.iterrows():
            # cut all after T in date
            date = datetime.strptime(p.date.split('T')[0], '%Y-%m-%d')
            paper_key = final_search.get_paper_key(
                p.title, date, p.doi)
            paper = final_search.paper_by_key.get(paper_key, None)

            # paper = final_search.get_paper(p.title, date)
            if paper is not None:
                final_search.remove_paper(paper)

    result_json = convert_search_to_json(final_search)
    search_export = fp.RayyanExport(final_search)
    rayyan_file, rayyan_df = search_export.generate_rayyan_csv()
    ris = fp.RisExport(final_search)
    ris_file, ris_df = ris.generate_ris()

    st.subheader('PRISMA')
    rayyan_selection = st.session_state.rayyan_df
    databases = st.session_state.databases
    all_papers = rayyan_selection.explode('databases')
    
    # count number papers per database for each database in `databases`
    db_frame = all_papers.groupby(['databases'])['key'].count().to_frame()
    # rename column
    db_frame = db_frame.rename(columns={'key': 'number of papers'})
    # add zero for missing databases
    db_frame = db_frame.reindex(databases, fill_value=0)
    # change type to int
    db_frame = db_frame.astype(int)

    # reduction by duplicates
    n_duplicates = len(all_papers) - len(rayyan_selection)
    
    if rayyan_df is None:
        st.info("No papers to show. All the papers have been excluded by you.")
    else:
        n_removes = len(rayyan_selection) - len(rayyan_df)

        prisma = graphviz.Digraph('PRISMA')
        prisma.attr('node', shape='box')
        with prisma.subgraph() as sub:
            sub.attr(rank='same')
            sub.node('Direct search',
                     f'Direct database search\n (n={len(all_papers)})')
            sub.node('Cross-references search',
                     f'Cross-references search \n (n={0})')
        with prisma.subgraph() as sub:
            sub.attr(rank='same')
            sub.node('Auto screening', 
                        'Records after duplicates removed \n '
                        f'(n={len(rayyan_selection)})')
            sub.node('TiAbs',
                     'Records excluded based on \n title and abstract screening \n '
                     f'(n={n_removes})')
        with prisma.subgraph() as sub:
            sub.attr(rank='same')
            sub.node('Manual screening', f'Records screened \n (n={len(rayyan_df)})')
        
        prisma.edge('Direct search', 'Auto screening') #label=str(n_duplicates))
        prisma.edge('Cross-references search', 'Auto screening')
        prisma.edge('Auto screening', 'TiAbs')
        prisma.edge('Auto screening', 'Manual screening')

        # save prisma
        prisma_result = prisma.pipe(format='svg')

        prisma1_col, prisma2_col = st.columns(2)
        if len(databases) == 2:
            venn2(db_sets,
                  set_labels=databases)
            prisma1_col.graphviz_chart(prisma)
            prisma2_col.pyplot(plt)
        elif len(databases) == 3:
            venn3(db_sets,
                  set_labels=databases)
            prisma1_col.graphviz_chart(prisma)
            prisma2_col.pyplot(plt)
        else:
            with prisma1_col:
                st.graphviz_chart(prisma)
            with prisma2_col:
                st.bar_chart(
                    data=db_frame,
                    use_container_width=True
                )
        # download prisma
        prisma_download_btn = download_button(
                prisma_result,
                'prisma.svg',
                'Download flow diagram'
            )
        st.markdown(prisma_download_btn, unsafe_allow_html=True)

        # download review
        st.subheader("Download results")
        json_download_col, ris_download_col, csv_download_col = st.columns(3)
        with json_download_col:
            json_download_btn = download_button(
                result_json,
                'set_you_free_results.json',
                'Details - JSON'
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
