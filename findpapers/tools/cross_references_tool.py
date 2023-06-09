from typing import List, Tuple

import requests

OPENCITATIONS_API = "https://opencitations.net/index/api/v1/metadata/"
REFERENCES_SPLIT = "; "
CITATIONS_SPLIT = "; "


def get_cross_references(doi: str = "") -> Tuple[List[str], List[str]]:
    pass
