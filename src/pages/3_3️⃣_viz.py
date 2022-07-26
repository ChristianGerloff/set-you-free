import numpy as np
import streamlit as st
import graphviz as graphviz
import matplotlib.pyplot as plt

from matplotlib_venn import venn2, venn3
from utils.site_config import set_page_title


# configure page
set_page_title("Visualization of search")

if 'rayyan_df' not in st.session_state:
    st.error("Please run the search first.")

elif 'rayyan_df' in st.session_state:
    st.subheader('PRISMA')
    rayyan_df = st.session_state.rayyan_df
    databases = st.session_state.databases
    all_papers = rayyan_df.explode('databases')
    stats_databses = all_papers.groupby(['databases'])['key'].apply(list)
    n_duplicates = len(all_papers) - len(rayyan_df)

    prisma = graphviz.Digraph('PRISMA')
    prisma.attr('node', shape='box')
    prisma.node('Identification')
    prisma.node('Screening', f' {len(rayyan_df)} records after duplicate removal')
    prisma.edge('Identification', 'Screening', label=str(n_duplicates))

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
            matches.append(sum([n == i for i in rayyan_df['databases']]))
        y_pos = np.arange(len(unique_databases))
        plt.bar(y_pos, matches)
        plt.xticks(y_pos, unique_databases)
        prisma2_col.pyplot(plt)