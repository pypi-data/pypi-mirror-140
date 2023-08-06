# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""This module provides means to categorize BibTeX entries by different characteristics."""

from collections import defaultdict
import logging
from typing import Dict, Sequence, Callable, Optional


ENTRYTYPE_SORT_ORDER = (
    "book",
    "proceedings",
    "article",
    "incollection",
    "inproceedings",
    "techreport",
    "misc",
    "invitedtalk",
    "conferencetalk",
    "defense",
)


def by_year(entries: Sequence[dict]) -> Dict[str, Sequence[dict]]:
    """Split the given entries by year.

    :param entries: A sequence of BibTeX entries,
        as returned by :py:meth:`bibtexparser.bibdatabase.BibDatabase.entries`.
    :return: A dictionary '$year -> $year_entries'.
        The dictionary maps each year that occurred in the given entries
        to all entries that were published in that year.
    """
    return {
        k: sort_by_type(es)
        for k, es in _categorize(entries, _getter("year"), sort_reverse=True).items()
    }


def by_author(entries: Sequence[dict]) -> Dict[str, Sequence[dict]]:
    """Split the given entries by authors.

    :param entries: A sequence of BibTeX entries,
        as returned by :py:meth:`bibtexparser.bibdatabase.BibDatabase.entries`.
    :return: A dictionary '$author -> $author_entries'.
        The dictionary maps each author that occurred in the given entries
        to all entries that were (co-)published by that author.
        If an entry has multiple authors, it will appear in the author_entries
        of each listed author.
    """
    get_authors = _getter("author")
    get_editors = _getter("editor")

    def get_author_or_editor(entry):
        authors = get_authors(entry)
        if not authors:
            if entry["ENTRYTYPE"] not in ("proceedings", "misc"):
                logging.info("No author for %s", entry["ID"])
            authors = get_editors(entry)
        return authors

    return {
        k: sort_by_year(v)
        for k, v in _categorize(entries, get_author_or_editor).items()
    }


def by_keyword(entries: Sequence[dict]) -> Dict[str, Sequence[dict]]:
    """Split the given entries by keywords.

    :param entries: A sequence of BibTeX entries,
        as returned by :py:meth:`bibtexparser.bibdatabase.BibDatabase.entries`.
    :return: A dictionary '$keyword -> $keyword_entries'.
        The dictionary maps each keyword that occurred in the given entries
        to all entries that list that keyword.
        If an entry has multiple keywords, it will appear in the keyword_entries
        of each listed keyword.
    """
    return {
        k: sort_by_year(v) for k, v in _categorize(entries, _getter("keyword")).items()
    }


def by_funding(entries: Sequence[dict]) -> Dict[str, Sequence[dict]]:
    """Split the given entries by funding.

    :param entries: A sequence of BibTeX entries,
        as returned by :py:meth:`bibtexparser.bibdatabase.BibDatabase.entries`.
    :return: A dictionary '$funding -> $funding_entries'.
        The dictionary maps each funding that occurred in the given entries
        to all entries that list that funding.
        If an entry has multiple fundings, it will appear in the funding_entries
        of each listed funding.
    """
    return {
        k: sort_by_year(v) for k, v in _categorize(entries, _getter("funding")).items()
    }


def by_type(entries: Sequence[dict]) -> Dict[str, Sequence[dict]]:
    """Split the given entries by BibTeX entry type (e.g., inproceedings, article, book).
    The returned dictionaries keys are sorted by ENTRYTYPE_SORT_ORDER.

    :param entries: A sequence of BibTeX entries,
        as returned by :py:meth:`bibtexparser.bibdatabase.BibDatabase.entries`.
    :return: A dictionary '$type -> $type_entries'.
        The dictionary maps each type that occurred in the given entries
        to all entries that are of that type. The dictionary keys are sorted by ENTRYTYPE_SORT_ORDER.
    """
    categories = _categorize(entries, _getter("ENTRYTYPE"))
    sorted_entries = {}
    assert not (
        missed_cats := set(categories) - set(ENTRYTYPE_SORT_ORDER)
    ), f"Categories missed in sort order: {missed_cats}"
    # dictionary keys are sorted by insertion order, so add the categories and their entries by the sort order
    for category in [e for e in ENTRYTYPE_SORT_ORDER if e in categories]:
        sorted_entries[category] = sort_by_year(categories[category])
    assert len(sorted_entries) == len(categories)
    for cat, es in sorted_entries.items():
        assert len(es) == len(
            categories[cat]
        ), f"Inconsistent entries for {cat}: sorted: {len(es)} vs. original: {len(categories[cat])}"
    return sorted_entries


def _getter(key):
    def get(entry):
        value = entry.get(key, None)
        if not value:
            value = []
        if not isinstance(value, list):
            value = [value]
        if len(value) == 1 and value[0] == "":
            value = []
        return value

    return get


def _categorize(
    entries: Sequence[dict],
    get_category: Callable[[dict], Optional[Sequence[str]]],
    sort_reverse=False,
):
    categories = defaultdict(list)
    for entry in entries:
        categories_of_entry = get_category(entry) or []
        for cat in categories_of_entry:
            categories[cat].append(entry)
    sorted_categories = {}
    for category in sorted(categories, reverse=sort_reverse):
        entries = categories[category]
        sorted_categories[category] = entries
    return sorted_categories


def sort_by_type(entries: Sequence[dict]) -> Sequence[dict]:
    categories = by_type(entries)
    assert list(categories) == [
        e for e in ENTRYTYPE_SORT_ORDER if e in categories
    ]  # ensure same order
    return [e for es in categories.values() for e in es]


def sort_by_year(entries: Sequence[dict]) -> Sequence[dict]:
    return sorted(entries, key=_getter("year"), reverse=True)
