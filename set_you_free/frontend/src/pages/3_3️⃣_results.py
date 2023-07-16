import numpy as np
import streamlit as st
import graphviz as graphviz
import matplotlib.pyplot as plt
import findpapers as fp

from datetime import datetime
from matplotlib_venn import venn2, venn3
from utils.site_config import set_page_title
from utils.search_engine import convert_search_to_json

# configure page
set_page_title("Results of search")

if 'rayyan_df' not in st.session_state:
    st.error("Please run the search first.")
elif 'review' in st.session_state:
    review = st.session_state.review.copy()
    final_search = st.session_state.search
    papers = review.loc[review["decision"] == False, ['title', 'date', 'doi']]

    if not papers.empty:
        for _, p in papers.iterrows():
            date = datetime.strptime(p.date, '%Y-%m-%d')
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
    stats_databses = all_papers.groupby(['databases'])['key'].apply(list)
    n_duplicates = len(all_papers) - len(rayyan_selection)
    
    if rayyan_df is None:
        st.info("No papers to show. All the papers have been excluded by you.")
    else:
        n_removes = len(rayyan_selection) - len(rayyan_df)

        prisma = graphviz.Digraph('PRISMA')
        prisma.attr('node', shape='box')
        prisma.node('Identification')
        prisma.node('Auto screening', f' {len(rayyan_selection)} records after duplicate removal')
        prisma.node('Manual screening', f' {len(rayyan_df)} records after manual screeening')
        prisma.edge('Identification', 'Auto screening', label=str(n_duplicates))
        prisma.edge('Auto screening', 'Manual screening', label=str(n_removes))

        prisma1_col, prisma2_col = st.columns(2)
        if len(databases) == 2:
            venn2([set(stats_databses[databases[0]]),
                set(stats_databses[databases[1]])],
                set_labels=databases)
            prisma1_col.graphviz_chart(prisma)
            prisma2_col.pyplot(plt)
        elif len(databases) == 3:
            venn3([set(stats_databses[databases[0]]),
                set(stats_databses[databases[1]]),
                set(stats_databses[databases[2]])],
                set_labels=databases)
            prisma1_col.graphviz_chart(prisma)
            prisma2_col.pyplot(plt)
        else:
            matches = []
            prisma1_col.graphviz_chart(prisma)
            unique_databases = [list(x) for x in set(tuple(x) for x in rayyan_df['databases'])]
            for n in unique_databases:
                matches.append(sum([n == i for i in rayyan_selection['databases']]))
            y_pos = np.arange(len(unique_databases))
            plt.bar(y_pos, matches)
            plt.xticks(y_pos, unique_databases)
            prisma2_col.pyplot(plt)



        # download review
        st.subheader("Download review")

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
