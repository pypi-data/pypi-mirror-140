# This file is part of pybib2web, a translator of BibTeX to HTML.
# https://gitlab.com/sosy-lab/software/pybib2web
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""Module concerned with exporting BibTeX entries to HTML."""

import re
from collections import namedtuple, defaultdict
import logging
from pathlib import Path
from typing import Sequence, Iterable, Dict

from . import categories, bibexport, util
from .config import Config
from .version import __version__

Category = namedtuple("Category", ["name", "link"])

CATEGORY_ARTICLES = Category(
    "Articles in journal or book chapters", "Category/articles.html"
)
CATEGORY_BOOKS = Category("Books and proceedings", "Category/books.html")
BIBTYPE_NAMES = {
    "inproceedings": Category(
        "Articles in conference or workshop proceedings", "Category/conferences.html"
    ),
    "book": CATEGORY_BOOKS,
    "proceedings": CATEGORY_BOOKS,
    "inbook": CATEGORY_ARTICLES,
    "incollection": CATEGORY_ARTICLES,
    "article": CATEGORY_ARTICLES,
    "techreport": Category("Internal reports", "Category/reports.html"),
    "misc": Category(
        "Theses and projects (PhD, MSc, BSc, Project)", "Category/misc.html"
    ),
    "conferencetalk": Category(
        "Conference and other Presentations", "Category/conference-talks.html"
    ),
    "invitedtalk": Category(
        "Guest lectures, invited talks, and tutorials", "Category/invited-talks.html"
    ),
    "defense": Category("Thesis defenses", "Category/defenses.html"),
}


def to_html(entry, *, config: Config) -> str:
    elements = [
        indent(0, f'<li class="bibentry" id="{html_id(entry)}">'),
        indent(1, '<span class="main-info">'),
        indent(2, authors_to_html(entry, config)),
        indent(2, publication_title_to_html(entry)),
        indent(2, talk_type_to_html(entry)),
        indent(2, publication_venue_to_html(entry, config)),
        indent(2, publisher_to_html(entry)),
        indent(2, doi_to_html(entry)),
        indent(1, "</span>"),
        indent(
            1,
            f'<a class="bibentry-link" href="#{html_id(entry)}"><img height="12px" width="12px" src="https://www.sosy-lab.org/images/transparent.gif" alt="Link to this entry"></a>',
        ),
        indent(1, '<span class="additional-info">'),
        indent(2, '<span class="inline-info">'),
        indent(3, note_to_html(entry)),
        indent(3, keywords_to_html(entry, config)),
        indent(3, funders_to_html(entry, config)),
        indent(2, "</span>"),
        indent(2, '<span class="link-list">'),
        indent(3, publisher_version_to_html(entry)),
        indent(3, articlelink_to_html(entry)),
        indent(3, presentationlink_to_html(entry)),
        indent(3, videolink_to_html(entry)),
        indent(3, materiallink_to_html(entry)),
        indent(2, "</span>"),
        indent(2, artifacts_to_html(entry)),
        indent(2, abstract_to_html(entry)),
        indent(2, bibtex_to_html(entry)),
        indent(2, annotations_to_html(entry)),
        indent(1, "</span>"),
        indent(0, "</li>"),
    ]

    # remove all empty lines
    elements = [e for e in elements if e.strip()]
    return "\n".join(elements)


def internal_link(
    text: str, href: str, config: Config, title: str = "", css_class: str = ""
) -> str:
    if not config.create_internal_links:
        return text
    if title:
        title = f' title="{title}"'
    if css_class:
        css_class = f' class="{css_class}"'
    return f'<a{css_class} href="{href}"{title}>{text}</a>'


def indent(n: int, content, single_indent: int = 2):
    lines = content.split("\n")
    spaces = n * single_indent * " "
    indented_lines = [spaces + line for line in lines]
    return "\n".join(indented_lines)


def publication_title_to_html(entry):
    title = entry.get("title")
    if not title:
        return ""
    return f'<span class="publication-title">{title}.</span>'


def talk_type_to_html(entry):
    html = ""
    entrytype = entry["ENTRYTYPE"]
    if entrytype == "conferencetalk":
        html = "Conference talk"
    if entrytype == "invitedtalk":
        html = "Invited talk"
    if entrytype == "defense":
        html = "Defense"
    if html:
        html = f'<span class="talk-type">{html}</span>'
    return html


def annotations_to_html(entry):
    annote = entry.get("annote", "")
    if annote:
        return _create_details(
            "Additional Infos", annote, "annote", open_by_default=True
        )
    return ""


def abstract_to_html(entry):
    abstract = entry.get("abstract", "").strip()
    if abstract:
        return _create_details("Abstract", abstract, html_class="abstract")
    return ""


def _create_details(
    summary: str, details: str, html_class: str, open_by_default=False
) -> str:
    summary = f"<summary>{summary}</summary>"
    details = f"<div>\n{indent(1, details)}\n</div>"
    open_html = ""
    if open_by_default:
        open_html = "open"

    return f'<details {open_html} class="{html_class}">\n{indent(1, summary)}\n{indent(1, details)}\n</details>'


def bibtex_to_html(entry):
    if "original" in entry:
        entry = entry["original"]
    return _create_details("BibTeX Entry", bibexport.writes(entry), html_class="bibtex")


def authors_to_html(entry, config: Config):
    try:
        if _put_editors_in_front(entry):
            authors = get_editors(entry)
            authors_html = (
                _get_list_of_names(authors, css_class="author", config=config)
                + ", editors"
                + "."
            )
        else:
            authors = get_authors(entry)
            authors_html = (
                _get_list_of_names(authors, css_class="author", config=config) + "."
            )
        return f'<span class="author-list">{authors_html}</span>'
    except KeyError:
        return ""


def _put_editors_in_front(entry):
    return (
        entry["ENTRYTYPE"] in ("book", "proceedings")
        and "author" not in entry
        and "editor" in entry
    )


def editors_to_html(entry, config: Config):
    try:
        editors = get_editors(entry)
        editors_html = (
            _get_list_of_names(editors, css_class="editor", config=config) + ", editors"
        )
    except KeyError:
        editors_html = ""
    if not editors_html:
        return ""
    return f'<span class="editor-list">{editors_html}</span>'


def funders_to_html(entry, config):
    try:
        funders = entry["funding"]
    except KeyError:
        return ""
    html_items = []
    for f in funders:
        html_items.append(
            internal_link(
                f, f"../Funding/{_keyword_to_link(f)}", config, css_class="funding"
            )
        )
    funders_html = ",\n".join(html_items)
    return f'<span class="funding-list">Funding:\n{indent(1, funders_html)}\n</span>'


def _name_to_html(name):
    first_name, last_name = util.split_name(name)
    return f'<span class="firstname">{first_name}</span> <span class="lastname">{last_name}</span>'


def _get_list_of_names(
    names,
    *,
    css_class,
    config: Config,
    delimiter_intermediate=",\n",
    delimiter_last=" and\n",
):
    ls = []
    for a in names:
        html_a = _name_to_html(a)
        if config.index_author(a):
            html_a = internal_link(html_a, f"../Author/{_author_to_link(a)}", config)
        ls.append(f'<span class="{css_class}">{html_a}</span>')
    if len(ls) > 2:
        ls = [delimiter_intermediate.join(ls[:-1]), ls[-1]]
        if not delimiter_last.startswith(","):
            delimiter_last = ", " + delimiter_last.strip() + "\n"
    assert (
        len(ls) <= 2
    ), f"There shouldn't be more than two elements after joining them with delimiter_intermediate: {ls}"
    return delimiter_last.join(ls)


def get_date_html(entry):
    def _get_day_html(entry):
        day = entry.get("day", None)
        if not day:
            return ""
        return f'<span class="day">{day}.</span>'

    def _get_month_html(entry):
        month = entry.get("month", None)
        if not month:
            return ""
        return f'<span class="month">{month}</span>'

    def _get_year_html(entry):
        year = get_year(entry)
        if not year:
            return ""
        return f'<span class="year">{year}</span>'

    return "\n".join(
        [
            e
            for e in [
                _get_day_html(entry),
                _get_month_html(entry),
                _get_year_html(entry),
            ]
            if e
        ]
    )


def _get_techreport_html(entry):
    if entry["ENTRYTYPE"] != "techreport" or "number" not in entry:
        return None
    return f'Technical report <span class="report-number">{entry["number"]}</span>'


def _get_publishing_institution(entry):
    try:
        return f'<span class="publishing-institution">{entry["institution"]}</span>'
    except KeyError:
        return None


def _get_explicit_venue(entry):
    try:
        return f'<span class="venue">at {entry["venue"]}</span>'
    except KeyError:
        return None


def _get_journal_info_html(entry):
    assert "journal" in entry
    try:
        pages = entry["pages"]
    except KeyError:
        pages = ""
    if pages:
        journal_pages = f'<span class="pages">:{pages}</span>'
    else:
        journal_pages = ""
    journal = f"<em class=\"journaltitle\">{entry['journal']}</em>"
    try:
        volume = f", <span class=\"journalvolume\">{entry['volume']}</span>"
    except KeyError:
        volume = ""
    try:
        number = f"<span class=\"journalnumber\">({entry['number']})</span>"
    except KeyError:
        number = ""
    return f'<span class="journal">{journal}{volume}{number}{journal_pages}</span>'


def _get_pages_html(entry):
    try:
        return f'<span class="pages">pages {entry["pages"]}</span>'
    except KeyError:
        return None


def _get_series_html(entry):
    try:
        return f"<span class=\"series\">{entry['series']}</span>"
    except KeyError:
        return None


def _get_booktitle_html(entry):
    try:
        return f"<em class=\"booktitle\">{indent(1, entry['booktitle'])}</em>"
    except KeyError:
        logging.debug("No booktitle for %s", entry)
        return None


def publication_venue_to_html(entry, config):
    date_html = get_date_html(entry)
    if date_html:
        date = f'<span class="publication-date">{indent(1, date_html)}</span>'
    else:
        date = ""

    # this is information that does not conform to the commonly seen
    # conference-, journal- and book-publications.
    special_publication_info = (
        _get_explicit_venue(entry),
        entry.get("howpublished", None),
        _get_techreport_html(entry),
        _get_publishing_institution(entry),
    )

    if any(special_publication_info):
        publication_method = ", ".join([i for i in special_publication_info if i])
        assert publication_method
        publication_method = (
            f'<span class="publicationmethod">{publication_method}</span>'
        )
    else:
        publication_method = None

    if "journal" in entry:
        venue = _get_journal_info_html(entry)
    else:
        if _put_editors_in_front(entry):
            # If the editors are put in front of the bibtex entry
            # like so:
            # Dirk Beyer and Damien Zufferey, editors. Proceedings of [...]
            # then we don't want to list the editors redundantly
            # as part of the publication venue, so we leave the editors blank here.
            editors = ""
        else:
            editors = editors_to_html(entry, config)
        booktitle = _get_booktitle_html(entry)
        pages = _get_pages_html(entry)
        series = _get_series_html(entry)
        venue = ",\n".join([k for k in (editors, booktitle, series, pages) if k])
        if booktitle:
            venue = f"In {venue}"
    all_infos = ",\n".join([e for e in (venue, publication_method, date) if e])
    return f'<span class="howpublished">\n{indent(1, all_infos)}.\n</span>'


def publisher_to_html(entry):
    try:
        return f"<span class=\"publisher\">{entry['publisher']}.</span>"
    except KeyError:
        return ""


def note_to_html(entry):
    try:
        return f'<span class="note">{entry["note"]}</span>'
    except KeyError:
        return ""


def artifacts_to_html(entry):
    artifact_keys = sorted([k for k in entry if re.match(r"artifact[0-9]*", k)])
    if not artifact_keys:
        return ""
    html_lines = []
    for artifact in [entry[k] for k in artifact_keys]:
        html_lines.append(f'<a href="https://doi.org/{artifact}">doi:{artifact}</a>')
    assert len(html_lines) > 0
    html_lines = [f'<li class="artifact">{line}</li>' for line in html_lines]
    artifacts_html = "\n".join(html_lines)
    artifacts_html = f"<ol>\n{indent(1, artifacts_html)}\n</ol>"
    return _create_details("Artifact(s)", artifacts_html, "artifact-list")


def keywords_to_html(entry, config):
    keywords = get_keywords(entry)
    if not keywords:
        return ""
    keyword_htmls = [
        internal_link(
            keyword,
            f"../Keyword/{_keyword_to_link(keyword)}",
            config,
            css_class="keyword",
        )
        for keyword in keywords
    ]
    keyword_html = ",\n".join(keyword_htmls)
    return f'<span class="keyword-list">Keyword(s):\n{indent(1, keyword_html)}\n</span>'


def articlelink_to_html(entry):
    try:
        link = entry["pdf"]
    except KeyError:
        return ""
    return f'<a class="pdf-link" href="{link}"><img alt="" height="17px" width="17px" src="https://www.sosy-lab.org/research/pub/Icons/pdf.gif">PDF</a>'


def presentationlink_to_html(entry):
    try:
        link = entry["presentation"]
    except KeyError:
        return ""
    return f'<a class="presentation-link" href="{link}"><img alt="" height="17px" width="17px" src="https://www.sosy-lab.org/research/pub/Icons/presentation.gif">Presentation</a>'


def materiallink_to_html(entry):
    try:
        link = entry["url"]
    except KeyError:
        return ""
    return f'<a class="material-link" href="{link}"><img alt="" height="15px" width="15px" src="https://www.sosy-lab.org/research/pub/Icons/www.gif">Supplement</a>'


def publisher_version_to_html(entry):
    description = "Link to official version of paper (may be a landing page with more information)"
    try:
        doi = get_doi(entry)
        return f'<a class="publishers-version-link doi-link" href="https://doi.org/{doi}" title="{description}"><img alt="" height="17px" width="17px" src="https://www.sosy-lab.org/research/pub/Icons/doi.svg">Publisher\'s Version</a>'
    except KeyError:
        pass
    try:
        urn = get_urn(entry)
        return f'<a class="publishers-version-link urn-link" href="https://nbn-resolving.org/process-urn-form?identifier={urn}&verb=REDIRECT" title="{description}">Publisher\'s Version</a>'
    except KeyError:
        pass
    try:
        publisher_url = get_publishers_version_url(entry)
        return f'<a class="publishers-version-link" href="{publisher_url}" title="{description}">Publisher\'s Version</a>'
    except KeyError:
        return ""


def doi_to_html(entry):
    try:
        doi = get_doi(entry)
    except KeyError:
        return ""
    return f'<a class="doi" href="https://doi.org/{doi}" data-doi="{doi}" title="The digital object identifier permanently identifies a digital article or document.">doi:{doi}</a>'


def videolink_to_html(entry):
    try:
        video_url = entry["video"]
    except KeyError:
        return ""
    return f'<a class="video-link" href="{video_url}" title="Link to video presentation related to paper"><img alt="" height="17px" width="17px" src="https://www.sosy-lab.org/research/pub/Icons/video.gif">Video</a>'


def get_year(entry):
    return entry.get("year", None)


def get_keywords(entry):
    try:
        return [k for k in entry["keyword"] if k]
    except KeyError:
        return None


def get_authors(entry):
    return entry["author"]


def get_editors(entry):
    return entry["editor"]


def get_doi(entry):
    doi = entry["doi"]
    if not doi:
        raise KeyError
    return doi


def get_urn(entry):
    urn = entry["urn"]
    if not urn:
        raise KeyError
    return urn


def get_publishers_version_url(entry):
    url = entry["urlpub"]
    if not url:
        raise KeyError
    return url


def html_id(entry):
    return entry["ID"].replace(" ", "")


def writes(
    categorized_entries: Dict[Category, Sequence[dict]],
    *,
    config,
    head=None,
    header_title=None,
) -> str:
    def gen():
        if head:
            yield head
        for category, entries in categorized_entries.items():
            if category.link:
                yield internal_link(
                    f"<h3>{category.name}</h3>", f"../{category.link}", config
                )
            else:
                yield f"<h3>{category.name}</h3>"
            yield ""
            yield f'<ol class="list-{header_title.lower().replace(" ", "-")}">'
            yield ""
            for entry in entries:
                yield to_html(entry, config=config)
                yield ""
            yield "</ol>"
        tail = config.tail
        if tail:
            yield tail

    return "\n".join(gen())


def write(
    entries: Dict[Category, Sequence[dict]],
    output_file,
    *,
    config,
    head=None,
    header_title=None,
):
    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, "w", encoding="UTF-8") as outp:
        html = writes(entries, config=config, head=head, header_title=header_title)
        write_html(outp, html)


def write_html(output_obj, html: str):
    start = f"<!-- This file was generated by pybib2web, version {__version__}: https://gitlab.com/sosy-lab/software/pybib2web/ -->"

    end = f'<footer id="generator">This file was generated by <a href="https://gitlab.com/sosy-lab/software/pybib2web/">pybib2web</a>, version {__version__}</footer>'
    output_obj.write(start)
    output_obj.write(html)
    output_obj.write(end)


def _get_header(header, config, show_link_to_index=True, show_link_to_all=True):
    def maybe_all():
        return (
            ['<a href="../All/index.html">Show all</a>']
            if config.create_internal_links and show_link_to_all
            else []
        )

    def maybe_index():
        return (
            ['<a href="../index.html">Index</a>']
            if config.create_internal_links and show_link_to_index
            else []
        )

    def links():
        links = maybe_all() + maybe_index()
        if not links:
            return ""
        return (
            f'<nav class="publication-navigation">({" &ndash; ".join(links)})</nav>\n'
        )

    return f"""
<input type="checkbox" id="show-compact">
<label for="show-compact">Compact view</label>
<h2 id="publications">{header}</h2>
{links()}"""


def write_html_tree(entries: Sequence[dict], output_root, *, config, header_title):
    output_root = Path(output_root)
    output_root.parent.mkdir(exist_ok=True)
    write_by_year(
        entries,
        output_file=output_root / "All" / "index.html",
        head=_get_header(header=header_title, config=config, show_link_to_all=False),
        header_title=header_title,
        config=config,
    )
    created_pages = {
        "all": [
            Category(
                f"Complete list of {header_title.lower()} as a single HTML page",
                "All/index.html",
            )
        ],
        "year": write_year_tree(
            entries, output_root / "Year", config=config, header_title=header_title
        ),
        "author": write_author_tree(
            entries,
            output_root / "Author",
            config=config,
            header_title=header_title,
        ),
        "funding": write_funding_tree(
            entries, output_root / "Funding", config=config, header_title=header_title
        ),
        "keyword": write_keyword_tree(
            entries, output_root / "Keyword", config=config, header_title=header_title
        ),
        "category": write_type_tree(
            entries, output_root / "Category", config=config, header_title=header_title
        ),
    }

    def name_sort(cat, key=None, **kwargs):
        if key is None:

            def key(n):
                return n

        return sorted(cat, key=lambda e: key(e.name), **kwargs)

    def index_page(header_title):
        yield _get_header(
            f"Index of {header_title}",
            config,
            show_link_to_all=False,
            show_link_to_index=False,
        )
        if created_pages["year"]:
            yield '<h3 id="years">Selection by year</h3>'
            yield "<ul>"
            for name, link in name_sort(created_pages["year"], reverse=True):
                yield f'<li><a href="{link}">{name}</a></li>'
            yield "</ul>"

        if created_pages["category"]:
            yield '<h3 id="categories">Selection by category</h3>'
            yield "<ul>"
            for name, link in name_sort(created_pages["category"]):
                yield f'<li><a href="{link}">{name}</a></li>'
            yield "</ul>"

        if created_pages["author"]:
            yield '<h3 id="authors">Selection by author</h3>'
            yield "<ul>"
            for name, link in name_sort(
                created_pages["author"], key=lambda e: util.split_name(e)[-1]
            ):
                yield f'<li><a href="{link}">{_name_to_html(name)}</a></li>'
            yield "</ul>"

        if created_pages["keyword"]:
            yield '<h3 id="research_interests">Selection by research interest</h3>'
            yield "<ul>"
            for name, link in name_sort(created_pages["keyword"]):
                yield f'<li><a href="{link}">{name}</a></li>'
            yield "</ul>"

        if created_pages["funding"]:
            yield '<h3 id="fundings">Selection by funding</h3>'
            yield "<ul>"
            for name, link in name_sort(created_pages["funding"]):
                yield f'<li><a href="{link}">{name}</a></li>'
            yield "</ul>"

        if created_pages["all"]:
            yield f'<h3 id="complete">Complete list of {header_title.lower()}</h3>'
            yield "<ul>"
            for name, link in created_pages["all"]:
                yield f'<li><a href="{link}">{name}</a></li>'
            yield "</ul>"

    with open(output_root / "index.html", "w", encoding="UTF-8") as outp:
        write_html(outp, "\n".join(index_page(header_title)))


def write_year_tree(entries: Sequence[dict], output_root, *, config, header_title):
    def _year_to_link(year):
        return f"{year}.html"

    def create():
        by_year = {
            Category(cat, Path(output_root.name) / _year_to_link(cat)): es
            for cat, es in categories.by_year(entries).items()
        }
        for year, es in by_year.items():
            output_file = output_root / year.link.name
            write_by_type(
                es,
                output_file,
                head=_get_header(f"{header_title} of year {year.name}", config),
                config=config,
                header_title=header_title,
            )
            yield year

    return list(create())  # to make sure that everything is executed


def _unite_same_authors_long_and_shortform(by_author):
    author_pages = {}
    Author = namedtuple("Author", ["name", "link", "entries"])
    for author, es in by_author.items():
        link = _author_to_link(author.name)
        if link not in author_pages:
            author_pages[link] = Author(author.name, link, [])
        assert util.equal_author(author.name, author_pages[link].name)
        if len(author.name) > len(author_pages[link].name):
            author_pages[link] = Author(
                author.name, author_pages[link].link, author_pages[link].entries
            )
        author_pages[link] = Author(
            author_pages[link].name,
            author_pages[link].link,
            author_pages[link].entries + es,
        )
    return {Category(a.name, a.link): a.entries for a in author_pages.values()}


def write_author_tree(
    entries: Sequence[dict], output_root, *, config, header_title
) -> Iterable[Category]:
    def create():
        by_author = {
            Category(cat, None): es
            for cat, es in categories.by_author(entries).items()
            if config.index_author(cat)
        }
        by_author = {
            Category(a.name, Path(output_root.name) / a.link): es
            for a, es in _unite_same_authors_long_and_shortform(by_author).items()
        }
        for author, es in by_author.items():
            output_file = output_root / author.link.name
            write_by_type(
                es,
                output_file,
                head=_get_header(f"{header_title} of {author.name}", config),
                config=config,
                header_title=header_title,
            )
            yield author

    return list(create())  # to make sure that everything is executed


def write_keyword_tree(
    entries: Sequence[dict], output_root, *, config, header_title
) -> Iterable[Category]:
    def create():
        by_keyword = {
            Category(cat, Path(output_root.name) / _keyword_to_link(cat)): es
            for cat, es in categories.by_keyword(entries).items()
            if cat
        }
        for keyword, es in by_keyword.items():
            output_file = output_root / keyword.link.name
            write_by_type(
                es,
                output_file,
                head=_get_header(f"{header_title} about {keyword.name}", config),
                config=config,
                header_title=header_title,
            )
            yield keyword

    return list(create())  # to make sure that everything is executed


def write_funding_tree(
    entries: Sequence[dict], output_root, *, config, header_title
) -> Iterable[Category]:
    def create():
        by_funding = {
            Category(cat, Path(output_root.name) / _keyword_to_link(cat)): es
            for cat, es in categories.by_funding(entries).items()
            if cat
        }
        for funding, es in by_funding.items():
            output_file = output_root / funding.link.name
            write_by_type(
                es,
                output_file,
                head=_get_header(f"Funding by {funding.name}", config),
                config=config,
                header_title=header_title,
            )
            yield funding

    return list(create())  # to make sure that everything is executed


def _get_named_types(entries):
    by_type = categories.by_type(entries)
    named_types = defaultdict(list)
    for bibtype, es in by_type.items():
        name = BIBTYPE_NAMES[bibtype]
        named_types[name] += es
    return {k: categories.sort_by_year(v) for k, v in named_types.items()}


def write_type_tree(
    entries: Sequence[dict], output_root, *, config, header_title
) -> Iterable[Category]:
    def create():
        for bibtype, es in _get_named_types(entries).items():
            link = Path(bibtype.link)
            assert (
                output_root.name == link.parent.name
            ), f"{output_root.name} != {link.parent.name}"
            output_file = output_root / f"{link.name}"
            output_file = output_root / f"{link.name}"
            write_by_year(es, output_file, config=config, header_title=header_title)
            yield Category(bibtype.name, link)

    return list(create())  # to make sure that everything is executed


def write_by_type(entries: Sequence[dict], output_file, *, config, head, header_title):
    by_type = _get_named_types(entries)
    write(by_type, output_file, head=head, config=config, header_title=header_title)


def write_by_year(entries, output_file, *, config, header_title, head=None):
    def to_link(year):
        return f"Year/{year}.html"

    by_year = {
        Category(cat, to_link(cat)): es
        for cat, es in categories.by_year(entries).items()
    }
    if head is None:
        head = f"<h2>{header_title} by year</h2>"
    write(by_year, output_file, head=head, config=config, header_title=header_title)


def html_by_year(entries, *, config, header_title, head=None):
    years = {Category(cat, None): es for cat, es in categories.by_year(entries).items()}
    if head is None:
        head = f"<h2>{header_title} by year</h2>"
    return writes(years, config=config, head=head, header_title=header_title)


def _keyword_to_link(keyword):
    assert keyword
    adjusted = re.sub("[()]", "", keyword.upper().replace(" ", "-"))
    return f"{adjusted}.html"


def _author_to_link(author):
    try:
        first_name, last_name = util.split_name(util.get_shortform(author))
        first_names = "".join(
            [f.upper()[0] for f in util.get_all_name_parts(first_name)]
        )
        return f"{last_name.upper()}-{first_names}.html"
    except IndexError:
        try:
            first_name, _, last_name = author.rpartition("~")
            return f"{last_name.upper()}-{first_name[0].upper()}.html"
        except IndexError:
            logging.info(
                "Author has no first name, author-link may be ambiguous: %s", author
            )
            return f"{author.upper()}.html"
