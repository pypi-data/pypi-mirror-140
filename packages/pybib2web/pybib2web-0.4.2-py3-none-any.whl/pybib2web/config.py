# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""Module for parsing config.yml"""

from datetime import datetime
from typing import Optional
import yaml
from . import util

ALL_AUTHORS = "consider_all_authors"


class Config:
    def __init__(self, config_dict, cmdline_params):
        self.create_internal_links = True

        if cmdline_params.create_single_page:
            self.create_internal_links = False
            # ignore authors to be indexed in config file
            self._authors_to_index = []
            config_dict.pop("authors_to_be_indexed", None)
        elif "authors_to_be_indexed" in config_dict:
            self._authors_to_index = [
                util.get_shortform(a) for a in config_dict.pop("authors_to_be_indexed")
            ]
        else:
            self._authors_to_index = ALL_AUTHORS

        self._tail = config_dict.pop("tail", "")

        if config_dict:
            raise ValueError(f"Unused configuration option(s): {config_dict.keys()}")

    def index_author(self, author):
        return (
            self._authors_to_index == ALL_AUTHORS
            or util.get_shortform(author) in self._authors_to_index
        )

    @property
    def tail(self):
        return self._tail.format(timestamp=self._get_timestamp())

    @staticmethod
    def _get_timestamp():
        return datetime.now().astimezone().strftime(r"%a %b %d %H:%M:%S %Y %Z")


def parse(config_file: Optional[str], args) -> Config:
    if config_file is None:
        return Config({}, args)
    with open(config_file, "rb") as inp:
        return Config(yaml.safe_load(inp), args)
