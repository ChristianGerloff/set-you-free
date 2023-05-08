import base64
import json
import pickle
import uuid
import re
import io

import streamlit as st
import pandas as pd
from streamlit import runtime

def download_button(data, filename, button_text, mimetype: str = "text/plain"):
    """
    Generates a link to download the given object_to_download.

    Args:
        data (str, bytes, pd.DataFrame): The data to download.
        filename (str): The filename to save the data to.
        button_text (str): The text to display on the download button (e.g. 'click here to download file').
        mimetype (str, optional): The mimetype of the data. Defaults to "text/plain".

    Returns:
        str: A link to download the given data.
    """

    data_as_bytes: bytes
    if isinstance(data, str):
        data_as_bytes = data.encode()
        mimetype = mimetype or "text/plain"
    elif isinstance(data, io.TextIOWrapper):
        string_data = data.read()
        data_as_bytes = string_data.encode()
        mimetype = mimetype or "text/plain"
    elif isinstance(data, pd.DataFrame):
        data_as_bytes = data.to_csv(index=False)
        mimetype = mimetype or "text/plain"
    # Assume bytes; try methods until we run out.
    elif isinstance(data, bytes):
        data_as_bytes = data
    elif isinstance(data, io.BytesIO):
        data.seek(0)
        data_as_bytes = data.getvalue()
        mimetype = mimetype or "application/octet-stream"
    elif isinstance(data, io.BufferedReader):
        data.seek(0)
        data_as_bytes = data.read()
        mimetype = mimetype or "application/octet-stream"
    elif isinstance(data, io.RawIOBase):
        data.seek(0)
        data_as_bytes = data.read() or b""
        mimetype = mimetype or "application/octet-stream"
    else:
        raise RuntimeError("Invalid binary data format: %s" % type(data))


    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(data.encode()).decode()
    except AttributeError as e:
        b64 = base64.b64encode(data).decode()
    #if runtime.exists():
    #    file_url = runtime.get_instance().media_file_mgr.add(
    #        data_as_bytes,
    #        mimetype,
    #        coordinates,
    #        file_name=filename,
    #        is_for_static_download=True,
    #    )
    #else:
    #    file_url = None 
    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = (
    custom_css + f'<a download="{filename}" id="{button_id}" '
    f'href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    )

    return dl_link