import logging
import os
from typing import Optional

from set_you_free.backend.findpapers.tools.bibtex_generator_tool import generate_bibtex
from set_you_free.backend.findpapers.tools.downloader_tool import download
from set_you_free.backend.findpapers.tools.rayyan_tool import RayyanExport
from set_you_free.backend.findpapers.tools.refiner_tool import refine
from set_you_free.backend.findpapers.tools.refman_tool import RisExport
from set_you_free.backend.findpapers.tools.search_runner_tool import search

# try:
#     import importlib.metadata as importlib_metadata
# except ModuleNotFoundError:
#     import importlib_metadata

# __version__ = importlib_metadata.version(__name__)
