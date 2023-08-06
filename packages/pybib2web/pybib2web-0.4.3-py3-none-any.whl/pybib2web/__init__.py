#!/usr/bin/env python3

# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""This module contains functionality to convert bibtex to html."""

import argparse
import logging
import sys

from . import bibparser, htmlexport, config
from .version import __version__

EXAMPLE_USAGE = "pybib2web mybibliography.bib"


def get_argparser():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX files to HTML",
        epilog=f"Example:\n\t{EXAMPLE_USAGE}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("bibfile", nargs="+", help="BibTeX file to convert")
    parser.add_argument(
        "-o", "--output", default="bib", help="Output directory to write HTML files to"
    )
    parser.add_argument(
        "--no-detex",
        dest="do_detex",
        action="store_false",
        default=True,
        help="Do not detexify entry values",
    )
    parser.add_argument(
        "--config",
        dest="config_file",
        default=None,
        help="Config file to use for extended configuration",
    )
    parser.add_argument(
        "--title",
        dest="header_title",
        default="Publications",
        help="Header title to use on web pages",
    )
    parser.add_argument(
        "--singlepage",
        dest="create_single_page",
        action="store_true",
        default=False,
        help="Create a single HTML page with all publications, instead of full directory structure with individual HTML pages for authors, keywords, etc.",
    )
    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = get_argparser().parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    conf = config.parse(args.config_file, args)

    bibtex_database = bibparser.parse(*args.bibfile, do_detex=args.do_detex)
    if args.create_single_page:
        html = htmlexport.html_by_year(
            bibtex_database.entries,
            config=conf,
            header_title=args.header_title,
        )
        htmlexport.write_html(sys.stdout, html)
    else:
        htmlexport.write_html_tree(
            bibtex_database.entries,
            output_root=args.output,
            config=conf,
            header_title=args.header_title,
        )
