import datetime
import json
import logging
import os
import re
import urllib.parse
from typing import List, Optional

import requests
from lxml import html

import findpapers.utils.common_utils as common_util
import findpapers.utils.persistence_utils as persistence_util
from findpapers.models.search import Search
from findpapers.utils.requests_utils import DefaultSession


def download(
    search_path: str,
    output_directory: str,
    only_selected_papers: Optional[bool] = False,
    categories_filter: Optional[dict] = None,
    proxy: Optional[str] = None,
    verbose: Optional[bool] = False,
) -> None:
    pass
