import re
import pickle
import streamlit as st
import graphviz as graphviz
import matplotlib.pyplot as plt
import findpapers as fp

from copy import copy
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from wordcloud import WordCloud
from utils.site_config import set_page_title
from utils.search_engine import convert_search_to_json
from utils.download import download_button

# configure page
set_page_title("Results of search")

if 'rayyan_df' not in st.session_state:
    st.error("Please run the search first.")
elif 'review' in st.session_state:
    final_search = copy(st.session_state.search)
    result_json = convert_search_to_json(final_search)
    ris = fp.RisExport(final_search)
    ris_file, ris_df = ris.generate_ris()

    remove_papers = ris_df.loc[
        ris_df["custom1"] == False,
        ['title', 'date', 'doi']
    ]

#    if not remove_papers.empty:
#        for _, p in remove_papers.iterrows():
#            # cut all after T in date
#            date = datetime.strptime(p.date.split('T')[0], '%Y-%m-%d')
#            paper_key = final_search.get_paper_key(
#                p.title, date, p.doi)
#            remove_paper = final_search.paper_by_key.get(paper_key, None)
#
#            # paper = final_search.get_paper(p.title, date)
#            if remove_paper is not None:
#                final_search.remove_paper(remove_paper)

    # ToDo.mus be reduced to the papers that are selected
    rayyan = fp.RayyanExport(final_search)
    rayyan_file, rayyan_df = rayyan.generate_rayyan_csv()

    st.subheader('PRISMA - Flow Diagram')
    databases = final_search.databases
    all_papers = ris_df.explode('name_of_database')
    selected_papers = ris_df[ris_df['custom1'] == True].explode('name_of_database')

    #count unique values in ris_df['custom3'] where custom3 is not None
    reasons_stats = str(
        ris_df['custom3'].value_counts()
    ).replace('\nName: custom3, dtype: int64', '\n ')
    reasons_stats = reasons_stats.replace('[', '')
    reasons_stats = reasons_stats.replace(']', '')

    # counts all papers per database
    db_counts = all_papers['name_of_database'].value_counts()
    db_counts.rename('number of papers', inplace=True)
    db_counts = db_counts.astype(int)
    # order index by lowcaps alphabet
    db_counts = db_counts.reindex(
        sorted(db_counts.index, key=str.lower)
    )

        # counts all papers per database
    selected_db_counts = selected_papers['name_of_database'].value_counts()
    selected_db_counts.rename('number of papers', inplace=True)
    selected_db_counts = selected_db_counts.astype(int)
    # order index by lowcaps alphabet
    selected_db_counts = selected_db_counts.reindex(
        sorted(selected_db_counts.index, key=str.lower)
    )

    # reduction by duplicates
    n_duplicates = len(all_papers) - len(ris_df)
    
    if rayyan_df is None:
        st.info("No papers to show. All the papers have been excluded by you.")
    else:
        n_removes = len(ris_df) - ris_df.where(ris_df['custom1'] == True).count()[0]

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
            sub.node(
                'Auto screening', 
                'Records after duplicates removed \n '
                f'(n={len(ris_df)})'
            )
            sub.node(
                'Duplicates',
                'Records excluded based on similarity index \n '
                f'(n={len(all_papers)-len(ris_df)})'
            )
        with prisma.subgraph() as sub:
            sub.attr(rank='same')
            sub.node(
                'Manual screening',
                (
                    'Records screened \n '
                    f"(n={sum(ris_df['custom1'] == True)})"
                )
            )
            sub.node(
                'TiAbs',
                'Records excluded based on \n title and abstract screening \n '
                f'(n={n_removes}) \n \n \n criteria: {reasons_stats}'
            )
        
        prisma.edge('Direct search', 'Auto screening') #label=str(n_duplicates))
        prisma.edge('Cross-references search', 'Auto screening')
        prisma.edge('Auto screening', 'Duplicates')
        prisma.edge('Auto screening', 'Manual screening')
        prisma.edge('Manual screening', 'TiAbs')

        #show prisma
        st.graphviz_chart(prisma)

        # download prisma
        prisma_result = prisma.pipe(format='svg')
        prisma_download_btn = download_button(
                prisma_result,
                'prisma.svg',
                'Download flow diagram'
            )
        st.markdown(prisma_download_btn, unsafe_allow_html=True)

        ## Results per database
        all_str = (
            '<p style="text-align: center;">'
            f'<b> All papers: n={len(all_papers)} </b>'
            '</p>'
        )
        selected_str = (
            '<p style="text-align: center;">'
            '<b> Selected papers (with duplicates): </b>'
            f'<b> n={len(selected_papers)} </b>'
            '</p>'
        )
        st.subheader('Results per database')
        all_db_col, selected_db_col = st.columns(2)
        if len(databases) == 2:
            with all_db_col:
                # add markdown text centered
                st.markdown(all_str)
                #venn2(db_counts,
                #      set_labels=db_counts.index)
                #st.pyplot(plt)
            with selected_db_col:
                st.markdown(selected_str)
                #venn2(selected_db_counts,
                #      set_labels=selected_db_counts.index)
                #st.pyplot(plt)
        elif len(databases) == 3:
            with all_db_col:
                st.markdown(all_str)
                venn3(db_counts,
                      set_labels=db_counts.index)
                st.pyplot(plt)
            with selected_db_col:
                st.markdown(selected_str)
                venn3(selected_db_counts,
                      set_labels=selected_db_counts.index)
                st.pyplot(plt)
        else:
            with all_db_col:
                st.markdown(all_str, unsafe_allow_html=True)
                st.bar_chart(
                    data=db_counts,
                    use_container_width=True
                )
            with selected_db_col:
                st.markdown(selected_str, unsafe_allow_html=True)
                st.bar_chart(
                    data=selected_db_counts,
                    use_container_width=True
                )

        # stats
        if len(selected_papers) > 0:
            st.subheader('Insights of selected papers')
            first_stats_col, sec_stats_col = st.columns(2)
            with first_stats_col:
                st.bar_chart(
                    data=ris_df.loc[ris_df['custom1'] == True, 'year'].value_counts(),
                    use_container_width=True
                )

            with sec_stats_col:
                # get all keyowrords, while keywords is a list of lists
                keywords = [i for i in ris_df.loc[ris_df['custom1'] == True, 'keywords']]
                if len(keywords) > 0:
                    keywords = [item for sublist in keywords for item in sublist]
                    # preprocessing replace 'N ' with''
                    keywords = [re.sub(r'N ', '', i) for i in keywords]
                    # replace strings with D and 6 subsequent numbers
                    keywords = [re.sub(r'D\d{6}', '', i) for i in keywords]
                    # replace strings with Jounral article
                    keywords = [re.sub(r'Journal Article', '', i) for i in keywords]
                    # replace strings with Research SUpport
                    keywords = [re.sub(r'Research Support', '', i) for i in keywords]
                    # replace strings with Support Non
                    keywords = [re.sub(r'Support Non', '', i) for i in keywords]
                    # replace strings with  , Non-U.S. Gov't
                    keywords = [re.sub(r', Non-U.S. Gov\'t', '', i) for i in keywords]
                    # replace strings with ' '
                    keywords = [re.sub(r'\'', '', i) for i in keywords]
                    # replace strings with  #text
                    keywords = [re.sub(r'#text', '', i) for i in keywords]
                    # replace strings with  @UI
                    keywords = [re.sub(r'@UI', '', i) for i in keywords]
                  
                    wordcloud = WordCloud(
                        width=800, height=800,
                        background_color='white',
                        min_font_size=10
                    ).generate(" ".join(keywords))
                    # Display the wordcloud in the Streamlit app
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    fig, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)

        # datetime.now().date() as yyyymmdd
        c_time = datetime.now().strftime('%Y%m%d')

        # download review
        st.subheader("Download results")
        search_pickle = pickle.dumps(final_search)
        pickle_download_btn = download_button(
                search_pickle,
                f"{datetime.now().strftime('%Y%m%d')}_all_results.syf",
                'All results - SYF'
            )
        st.markdown(pickle_download_btn, unsafe_allow_html=True)    
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
