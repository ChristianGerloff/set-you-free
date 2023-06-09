import os
import re
from typing import List, Optional

import inquirer
from colorama import Back, Fore, Style, init

import findpapers.utils.common_utils as common_util
import findpapers.utils.persistence_utils as persistence_util
from findpapers.models.paper import Paper
from findpapers.models.search import Search


def _print_paper_details(
    paper: Paper,
    highlights: List[str],
    show_abstract: bool,
    show_extra_info: bool,
) -> None:  # pragma: no cover
    pass


def _get_select_question_input():  # pragma: no cover
    pass


def _get_category_question_input(categories: dict) -> None:  # pragma: no cover
    pass


def refine(
    search_path: str,
    categories: Optional[dict] = None,
    highlights: Optional[list] = None,
    show_abstract: Optional[bool] = False,
    show_extra_info: Optional[bool] = False,
    only_selected_papers: Optional[bool] = False,
    only_removed_papers: Optional[bool] = False,
    read_only: Optional[bool] = False,
    verbose: Optional[bool] = False,
) -> None:
    pass
