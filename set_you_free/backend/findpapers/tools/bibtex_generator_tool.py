import datetime
import logging
from typing import Optional

import set_you_free.backend.findpapers.utils.common_utils as common_util
import set_you_free.backend.findpapers.utils.persistence_utils as persistence_util


def generate_bibtex(
    search_path: str,
    outputpath: str,
    only_selected_papers: Optional[bool] = False,
    categories_filter: Optional[dict] = None,
    add_findpapers_citation: Optional[bool] = False,
    verbose: Optional[bool] = False,
) -> None:
    pass
