import logging
import os
from typing import Optional

from findpapers.tools.bibtex_generator_tool import generate_bibtex
from findpapers.tools.downloader_tool import download
from findpapers.tools.rayyan_tool import RayyanExport
from findpapers.tools.refiner_tool import refine
from findpapers.tools.refman_tool import RisExport
from findpapers.tools.search_runner_tool import search

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)
