# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import re
import subprocess

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode, keyword

from . import util


def parse(*files, do_detex=True) -> bibtexparser.bibdatabase.BibDatabase:
    def concat_files(files):
        concatenated_content = b""
        for f in files:
            with open(f, "rb") as inp:
                concatenated_content += inp.read()
        return concatenated_content

    parser = BibTexParser()
    parser.customization = get_customization_func(
        do_detex=do_detex, add_pdf_for_doi=True
    )
    parser.ignore_nonstandard_types = False
    return bibtexparser.loads(concat_files(files), parser=parser)


def get_customization_func(*, do_detex: bool, add_pdf_for_doi: bool):
    if do_detex and not _which("detex"):
        logging.warning(
            "No executable 'detex' found on system. Not detexifying publication titles"
        )
        do_detex = False

    def customize(entry):
        copy = dict(entry.items())

        entry = {k: v for k, v in entry.items() if v.strip()}
        entry = convert_to_unicode(keyword(entry))
        if do_detex:
            entry = detex(entry)
        if add_pdf_for_doi:
            entry = add_pdf(entry)
        entry = split_lists(entry)
        entry["original"] = copy
        return entry

    return customize


def add_pdf(entry):
    if "pdf" not in entry:
        try:
            pdf_link = util.get_download_link(entry["doi"])
            if pdf_link:
                entry["pdf"] = pdf_link
        except KeyError:
            pass
    return entry


def split_lists(entry):
    for key in ("author", "editor"):
        try:
            entry[key] = _split_authors(entry[key])
        except KeyError:
            pass
    for key in ("funding",):
        try:
            entry[key] = [a.strip() for a in entry[key].split(",")]
        except KeyError:
            pass
    return entry


def _split_authors(author_str):
    return [a.strip() for a in re.split(r"\s+and\s+", author_str.strip())]


def detex(entry):
    if isinstance(entry, str):
        return subprocess.check_output(
            ["detex", "/dev/stdin"], input=entry.encode()
        ).decode()
    if isinstance(entry, list):
        return [detex(e) for e in entry]
    for field in (
        "author",
        "title",
        "howpublished",
        "venue",
        "booktitle",
        "series",
        "publisher",
        "editor",
        "pages",
        "note",
        "abstract",
    ):
        try:
            entry[field] = detex(entry[field])
        except KeyError:
            pass
    return entry


# Copied from https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def _which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
