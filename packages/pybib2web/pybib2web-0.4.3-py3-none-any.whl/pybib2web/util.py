# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""Utility methods for pybib2web."""

import re
from typing import Optional, Tuple, List


def equal_author(author1, author2) -> bool:
    """Return whether the two given authors are the same.

    Takes care of BibTeX short-forms.

    Example:
        equal_author("Dirk Beyer", "D. Beyer") = True
    """
    return get_shortform(author1) == get_shortform(author2)


def split_name(author: str) -> Tuple[str, str]:
    """Split author name into first name(s) and last name."""
    parts = get_all_name_parts(author)
    return " ".join(parts[:-1]), parts[-1]


def get_all_name_parts(name: str) -> List[str]:
    """Split given name into all of its parts.

    Examples:
        "Dirk Beyer" -> ["Dirk", "Beyer"]
        "Mehmet Erkan Keremoglu" -> ["Mehmet", "Erkan", "Keremoglu"]
        "Max-Erwin Mustermann" -> ["Max-Erwin", "Mustermann"]
    """
    return re.split(r" |~", name.strip())


def get_shortform(author_name: str) -> str:
    """Get shortform of author name.

    Examples:
        "Dirk Beyer" -> "D. Beyer"
        "Mehmet Erkan Keremoglu" -> "M. E. Keremoglu"
    """

    def handle_apostrophes(name):
        try:
            position_of_apostrophe = name.index("'")
        except ValueError:
            return f"{name[0]}."
        if position_of_apostrophe in (1, 2):
            # example: MC'Riley -> MC'R.
            # example: O'Hearn -> O'H.
            return f"{name[:(position_of_apostrophe+2)]}."
        return f"{name[0]}."

    def handle_dashes(first_name, handle_single_name):
        return "-".join([handle_single_name(p) for p in first_name.split("-")])

    first_names_concatenated, last_name = split_name(author_name)
    first_names = get_all_name_parts(first_names_concatenated)
    first_names_short = []
    for name in [name for name in first_names if name]:
        first_names_short.append(handle_dashes(name, handle_apostrophes))
    return " ".join(first_names_short + [last_name])


def get_download_link(doi: str) -> Optional[str]:
    """Compute a link for downloading the paper PDF for the given DOI."""
    link = None
    if doi.startswith("10.1007/"):
        link = f"https://link.springer.com/content/pdf/{doi}.pdf"
    if doi.startswith("10.1145/"):
        link = f"https://dl.acm.org/doi/pdf/{doi}"
    return link
