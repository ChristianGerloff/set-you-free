from findpapers.searchers import (
    acm_searcher,
    arxiv_searcher,
    biorxiv_searcher,
    cross_ref_searcher,
    ieee_searcher,
    medrxiv_searcher,
    opencitations_searcher,
    pubmed_searcher,
    scopus_searcher,
)

AVAILABLE_DATABASES: list[str] = [
    scopus_searcher.DATABASE_LABEL,
    ieee_searcher.DATABASE_LABEL,
    pubmed_searcher.DATABASE_LABEL,
    arxiv_searcher.DATABASE_LABEL,
    acm_searcher.DATABASE_LABEL,
    medrxiv_searcher.DATABASE_LABEL,
    biorxiv_searcher.DATABASE_LABEL,
    opencitations_searcher.DATABASE_LABEL,
    cross_ref_searcher.DATABASE_LABEL,
]
