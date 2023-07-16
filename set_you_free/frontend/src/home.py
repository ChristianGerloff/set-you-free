from pathlib import Path

import streamlit as st
from utils.site_config import set_page_title


@st.cache
def get_home_md() -> str:
    """Return home.

    Returns:
        str -- The home as a string of MarkDown
    """
    url = Path(__file__).resolve().parent / "pages" / "md" / "home.md"
    with Path.open(url, mode="r") as file:
        readme_md_contents = "".join(file.readlines())
    return readme_md_contents.split("\n", 3)[-1]


set_page_title()


# add sidebar
st.sidebar.markdown("# Home 🎈")

# load page
with st.spinner("Loading Home ..."):
    st.title("Set You Free")
    home = get_home_md()
    st.markdown(home)
