"""
Class, which fetches scientific publications from multiple sources.
"""


# import findpapers as fp

from datetime import datetime
import findpapers as fp
# from findpapers import findpapers as fp


class Search:

    def __init__(self,
                 start_date: datetime,
                 end_date: datetime,
                 source_limit: int = 5,
                 total_limit: int = 20,
                 sources: list = ['biorxiv', 'medrxiv'],
                 scopus_key: str = None,
                 ieee_key: str = None):

        self.start_date = start_date
        self.end_date = end_date
        self.source_limit = source_limit
        self.total_limit = total_limit
        self.sources = sources
        self.scopus_key = scopus_key
        self.ieee_key = ieee_key

    def search(self,
               search_string: str,
               filename: str):
        fp.search(filename,
                  search_string,
                  None,
                  None,
                  self.total_limit,
                  self.source_limit,
                  self.sources,
                  None,
                  self.scopus_key,
                  self.ieee_key)
