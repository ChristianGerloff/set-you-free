import json
from pathlib import Path

from set_you_free.backend.findpapers.models.search import Search


def save(search: Search, outputpath: str) -> None:
    """Save the search result in a JSON representation.

    Args:
        search (Search): A Search instance.
        outputpath (str): A valid file path used to save the search results.
    """
    with Path(outputpath).open("w") as jsonfile:
        json.dump(Search.to_dict(search), jsonfile, indent=2, sort_keys=True)


def load(search_path: str) -> Search:
    """Load a search result using a JSON representation.

    Args:
        search_path (str): A valid file path containing a JSON representation of the search results.

    Returns:
        Search: Search instance as dict.
    """
    with Path(search_path).open("r") as jsonfile:
        return Search.from_dict(json.load(jsonfile))
