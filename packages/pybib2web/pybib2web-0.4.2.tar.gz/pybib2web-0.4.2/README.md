<!--
This file is part of pybib2web, a translator of BibTeX to HTML.
https://gitlab.com/sosy-lab/software/pybib2web

SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

# pybib2web

Convert BibTeX .bib files into a directory of HTML files.

The created HTML provide individual HTML pages for publications by
year, publication type (category), author, keyword, and funding.
A single-page view is also available.
pybib2web provides semantics and easy customizability of each BibTeX element
through HTML ids and classes.

This makes it easy to choose the data to display and style the bibliography to your needs.

Send us a message or create an issue if you require any assistance and/or have feedback!

## Examples

You can find a raw example in [doc/example/index.html](doc/example/index.html).
This example is generated with:

```
pybib2web --config doc/example/config.yml --output doc/example doc/example/db.bib
```

Two pages that use pybib2web with styling:

- [Webpage of the Software and Computational Systems Lab (SoSy-Lab) at LMU Munich](https://www.sosy-lab.org/research/bib/All/index.html) uses full pybib2web directory structure with individual pages for author, keywords, etc..
- [Personal webpage of Thomas Lemberger](https://thomaslemberger.com/publications.html) uses `--singlepage` to display a single page with all entries.


## Requirements

- python 3.8

### Optional requirements

`detex` is required to detexify BibTeX-entries that use LaTeX commands,
e.g., `\sc{}` or `~`. If `detex` is not installed, these LaTeX commands will be visible
in the HTML output.


## Installation

After cloning the repository, run `pip install -e .` to install pybib2web and its dependencies.


## Usage

Run `pybib2web --help` to show all available command-line options.

Basic usage:

```
pybib2web BIBFILE(s)
```

This will write a directory of HTML files to `bib/`.
The index of these files is `bib/index.html`.

This will, among other things, create
an individual publication page for all authors that appear in the given BibTeX files.
Often, one only wants to create these author-centered pages for individual authors-
for example for oneself or a specific group of people.
pybib2web can be configured through a [config file](doc/config.yml) to do this:

```
pybib2web --config CONFIG_YAML BIBFILE(s)
```
