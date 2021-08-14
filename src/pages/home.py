import pathlib

import streamlit as st


@st.cache
def get_home_md() -> str:
    """Returns home

    Returns:
        str -- The home as a string of MarkDown
    """
    url = pathlib.Path(__file__).resolve().parent / "md" / "home.md"
    with open(url, mode="r") as file:
        readme_md_contents = "".join(file.readlines())
    return readme_md_contents.split("\n", 3)[-1]


# pylint: disable=line-too-long
def write():
    """Used to write the page in the app.py file"""
    with st.spinner("Loading Home ..."):
        st.title("Home of Set You Free")
        home = get_home_md()
        st.markdown(home)
