import logging
from datetime import datetime
from pathlib import Path
from typing import List

import typer

import findpapers

app = typer.Typer()


@app.command("search")
def search(
    outputpath: str = typer.Argument(..., help="A valid file path where the search result JSON file will be placed"),
    query: str = typer.Option(
        None,
        "-q",
        "--query",
        show_default=True,
        help="A query string that will be used to perform the papers search (If not provided it will be loaded from the environment variable FINDPAPERS_QUERY). E.g. [term A] AND ([term B] OR [term C]) AND NOT [term D]",
    ),
    query_filepath: str = typer.Option(
        None,
        "-f",
        "--query-file",
        show_default=True,
        help="A file path that contains the query string that will be used to perform the papers search",
    ),
    since: datetime = typer.Option(
        None,
        "-s",
        "--since",
        show_default=True,
        help="A lower bound (inclusive) date that will be used to filter the search results. Following the pattern YYYY-MM-DD. E.g. 2020-12-31",
        formats=["%Y-%m-%d"],
    ),
    until: datetime = typer.Option(
        None,
        "-u",
        "--until",
        show_default=True,
        help="A upper bound (inclusive) date that will be used to filter the search results. Following the pattern YYYY-MM-DD. E.g. 2020-12-31",
        formats=["%Y-%m-%d"],
    ),
    limit: int = typer.Option(None, "-l", "--limit", show_default=True, help="The max number of papers to collect"),
    limit_per_database: int = typer.Option(
        None,
        "-ld",
        "--limit-db",
        show_default=True,
        help="The max number of papers to collect per each database",
    ),
    databases: str = typer.Option(
        None,
        "-d",
        "--databases",
        show_default=True,
        help="A comma-separated list of databases where the search should be performed, if not specified all databases will be used (this parameter is case insensitive)",
    ),
    publication_types: str = typer.Option(
        None,
        "-p",
        "--publication-types",
        show_default=True,
        help="A comma-separated list of publication types to filter when searching, if not specified all the publication types will be collected (this parameter is case insensitive). The available publication types are: journal, conference proceedings, book, other",
    ),
    scopus_api_token: str = typer.Option(
        None,
        "-ts",
        "--token-scopus",
        show_default=True,
        help="A API token used to fetch data from Scopus database. If you don't have one go to https://dev.elsevier.com and get it. (If not provided it will be loaded from the environment variable FINDPAPERS_SCOPUS_API_TOKEN)",
    ),
    ieee_api_token: str = typer.Option(
        None,
        "-ti",
        "--token-ieee",
        show_default=True,
        help="A API token used to fetch data from IEEE database. If you don't have one go to https://developer.ieee.org and get it. (If not provided it will be loaded from the environment variable FINDPAPERS_IEEE_API_TOKEN)",
    ),
    proxy: str = typer.Option(
        None,
        "-x",
        "--proxy",
        show_default=True,
        help="proxy URL that can be used during requests",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        show_default=True,
        help="If you wanna a verbose mode logging",
    ),
) -> None:
    try:
        since = since.date() if since else None
        until = until.date() if until else None
        databases = [x.strip() for x in databases.split(",")] if databases else None
        publication_types = [x.strip() for x in publication_types.split(",")] if publication_types else None

        if query is None and query_filepath:
            with Path(query_filepath).open("r") as f:
                query = f.read().strip()

        findpapers.search(
            outputpath,
            query,
            since,
            until,
            limit,
            limit_per_database,
            databases,
            publication_types,
            scopus_api_token,
            ieee_api_token,
            proxy,
            verbose,
        )
    except Exception as e:
        if verbose:
            logging.debug(e, exc_info=True)
        else:
            typer.echo(e)
        raise typer.Exit(code=1)


@app.command("refine")
def refine(
    filepath: str = typer.Argument(..., help="A valid file path for the search result file"),
    categories: List[str] = typer.Option(
        [],
        "-c",
        "--categories",
        show_default=True,
        help="A comma-separated list of categories to assign to the papers with their facet following the pattern: <facet>:<term_b>,<term_c>,...",
    ),
    highlights: str = typer.Option(
        None,
        "-h",
        "--highlights",
        show_default=True,
        help="A comma-separated list of terms to be highlighted on the abstract",
    ),
    show_abstract: bool = typer.Option(
        False,
        "-a",
        "--abstract",
        show_default=True,
        help="A flag to indicate if the paper's abstract should be shown or not",
    ),
    show_extra_info: bool = typer.Option(
        False,
        "-e",
        "--extra-info",
        show_default=True,
        help="A flag to indicate if the paper's extra info should be shown or not",
    ),
    only_selected_papers: bool = typer.Option(
        False,
        "-s",
        "--selected",
        show_default=True,
        help="If only the selected papers will be refined",
    ),
    only_removed_papers: bool = typer.Option(
        False,
        "-r",
        "--removed",
        show_default=True,
        help="If only the removed papers will be refined",
    ),
    read_only: bool = typer.Option(
        False,
        "-l",
        "--list",
        show_default=True,
        help="If this flag is present, this function call will only list the papers",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        show_default=True,
        help="If you wanna a verbose mode logging",
    ),
) -> None:
    try:
        highlights = [x.strip() for x in highlights.split(",")] if highlights else None

        categories_by_facet = {} if len(categories) > 0 else None
        for categories_string in categories:
            string_split = categories_string.split(":")
            facet = string_split[0].strip()
            categories_by_facet[facet] = [x.strip() for x in string_split[1].split(",")]

        findpapers.refine(
            filepath,
            categories_by_facet,
            highlights,
            show_abstract,
            show_extra_info,
            only_selected_papers,
            only_removed_papers,
            read_only,
            verbose,
        )
    except Exception as e:
        if verbose:
            logging.debug(e, exc_info=True)
        else:
            typer.echo(e)
        raise typer.Exit(code=1)


@app.command("download")
def download(
    filepath: str = typer.Argument(..., help="A valid file path for the search result file"),
    outputpath: str = typer.Argument(..., help="A valid directory path where the downloaded papers will be placed"),
    only_selected_papers: bool = typer.Option(
        False,
        "-s",
        "--selected",
        show_default=True,
        help="A flag to indicate if only selected papers (selections can be done on refine command) will be downloaded",
    ),
    categories: List[str] = typer.Option(
        [],
        "-c",
        "--categories",
        show_default=True,
        help="A comma-separated list of categories (categorization can be done on refine command) that will be used to filter which papers will be downloaded, using the following pattern: <facet>:<term_b>,<term_c>,...",
    ),
    proxy: str = typer.Option(
        None,
        "-x",
        "--proxy",
        show_default=True,
        help="proxy URL that can be used during requests",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        show_default=True,
        help="If you wanna a verbose mode logging",
    ),
) -> None:
    try:
        categories_by_facet = {} if len(categories) > 0 else None
        for categories_string in categories:
            string_split = categories_string.split(":")
            facet = string_split[0].strip()
            categories_by_facet[facet] = [x.strip() for x in string_split[1].split(",")]

        findpapers.download(filepath, outputpath, only_selected_papers, categories_by_facet, proxy, verbose)
    except Exception as e:
        if verbose:
            logging.debug(e, exc_info=True)
        else:
            typer.echo(e)
        raise typer.Exit(code=1)


@app.command("bibtex")
def bibtex(
    filepath: str = typer.Argument(..., help="A valid file path for the search result file"),
    outputpath: str = typer.Argument(..., help="A valid directory path where the generated bibtex will be placed"),
    only_selected_papers: bool = typer.Option(
        False,
        "-s",
        "--selected",
        show_default=True,
        help="A flag to indicate if only selected papers (selections be done on refine command) will be used for bibtex generation",
    ),
    categories: List[str] = typer.Option(
        [],
        "-c",
        "--categories",
        show_default=True,
        help="A comma-separated list of categories (categorization can be done on refine command) that will be used to filter which papers will be used for bibtex generation, using the following pattern: <facet>:<term_b>,<term_c>,...",
    ),
    add_findpapers_citation: bool = typer.Option(
        False,
        "-f",
        "--findpapers",
        show_default=True,
        help="A flag to indicate if you want to add an entry for Findpapers in your BibTeX output file",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        show_default=True,
        help="If you wanna a verbose mode logging",
    ),
) -> None:
    try:
        categories_by_facet = {} if len(categories) > 0 else None
        for categories_string in categories:
            string_split = categories_string.split(":")
            facet = string_split[0].strip()
            categories_by_facet[facet] = [x.strip() for x in string_split[1].split(",")]

        findpapers.generate_bibtex(
            filepath,
            outputpath,
            only_selected_papers,
            categories_by_facet,
            add_findpapers_citation,
            verbose,
        )
    except Exception as e:
        if verbose:
            logging.debug(e, exc_info=True)
        else:
            typer.echo(e)
        raise typer.Exit(code=1)


@app.command("version")
def version() -> None:
    typer.echo(f"findpapers {findpapers.__version__}")


def main() -> None:
    app()
