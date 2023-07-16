import datetime
import json
import logging
import os
import re
import urllib.parse
from typing import List, Optional

import requests
from lxml import html

import set_you_free.backend.findpapers.utils.common_utils as common_util
import set_you_free.backend.findpapers.utils.persistence_utils as persistence_util
from set_you_free.backend.findpapers.models.search import Search
from set_you_free.backend.findpapers.utils.requests_utils import DefaultSession


def download(
    search_path: str,
    output_directory: str,
    only_selected_papers: Optional[bool] = False,
    categories_filter: Optional[dict] = None,
    proxy: Optional[str] = None,
    verbose: Optional[bool] = False,
) -> None:
    pass
