import streamlit as st

import src.pages.main
import src.pages.home


def write_page(page):
    """Writes the specified page/module.

    Our app is structured into sub-files with a `def write()` function.

    Arguments:
        page {module} -- A module with a 'def write():' function
    """
    page.write()


PAGES = {
    "About": src.pages.home,
    "Main": src.pages.main
}

log = st.empty()

selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]

with st.spinner(f"Loading {selection} ..."):
    write_page(page)
st.sidebar.title("About")
