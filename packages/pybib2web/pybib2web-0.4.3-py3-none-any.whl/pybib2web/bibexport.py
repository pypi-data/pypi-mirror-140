# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""Module concerned with exporting BibTeX entries to BibTeX."""

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


def writes(entry: dict) -> str:
    db = BibDatabase()
    db.entries = [_flatten(entry)]
    return _get_writer().write(db)


def _flatten(entry: dict) -> dict:
    def _flat(k, v):
        if isinstance(v, list):
            if k in ("author", "editor"):
                delimiter = " and "
            else:
                delimiter = ", "
            v = delimiter.join(v)
        return v.replace("\n", " ").strip()

    return {k: _flat(k, v) for k, v in entry.items() if k != "original"}


def _get_writer():
    writer = BibTexWriter()
    writer.add_trailing_comma = True
    writer.indent = ""
    writer.display_order = (
        "author",
        "title",
        "journal",
        "booktitle",
        "editor",
        "volume",
        "number",
        "pages",
        "year",
        "series",
        "publisher",
        "isbn",
        "doi",
        "sha256",
        "url",
        "pdf",
        "postscript",
        "presentation",
        "abstract",
        "keyword",
    )
    return writer
