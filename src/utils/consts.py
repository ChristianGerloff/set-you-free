"""Defines constants used in the project."""

DUPLICATION_DEFAULT_SLIDER = 0.9
DUPLICATION_MIN_SLIDER = 0.75
DUPLICATION_MAX_SLIDER = 1.0
DUPLICATION_STEP_SLIDER = 0.01
CITE_MIN_NUM = 0
CITE_MAX_NUM = 1000
RESULTS_MIN_SLIDER = 1
RESULTS_MAX_SLIDER = 1000
RESULTS_DEFAULT_SLIDER = 100
AVAILABLE_DATABASES = [
    "ACM",
    "arXiv",
    "bioRxiv",
    "IEEE",
    "medRxiv",
    "PubMed",
    "Scopus"
]
JOIN_TYPES = [
    "None",
    "(",
    ")",
    "AND",
    "OR",
    "(AND",
    "(OR"
]
SEARCH_STRING_TYPE = [
    "Insert search string directly",
    "Build search string"
]
AVAILABLE_PUBTYPES = [
        'all',
        'journal',
        'preprint',
        'conference proceedings',
        'book'
    ]
DEFAULT_PUBTYPES = ['all']
HELP_ENRICH = (
    "Enrich aims to combine information across different databases to complete "
    "missing information of a publication."
)
HELP_CROSS_REF = (
    "The cross-reference option uses the reference list and the citations "
    "of the found publications to extend the search results."
)
HELP_SEARCH_STRING = (
    "[term a] OR ([term b] AND ([term c] OR [term d]"
)
HELP_LEFTJOIN = (
    "If selected, all search publications of the initial search will be included "
    "in the final results even if they are not found in the new search."
)
ORDER_SEARCH_RESULTS = [
    'title',
    'journal_name',
    'date',
    'authors',
    'abstract',
    'keywords'
]

DEFAULT_HWORDS = [
    'review',
    'guideline',
    'protocol',
]