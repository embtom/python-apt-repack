#!/usr/bin/env python3
#
#  get_ubuntu_lp_mirrors.py
#
#  Download the latest list with available Ubuntu mirrors from Launchpad.net
#  and extract the hosts from the raw page
#
#  Copyright (c) 2006 Free Software Foundation Europe
#
#  Author: Sebastian Heinlein <glatzor@ubuntu.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

import sys

import feedparser
from feedparser import FeedParserDict

FEED_URL = "https://launchpad.net/ubuntu/+archivemirrors-rss"


def request_feed(url: str) -> list[FeedParserDict]:
    """
    Fetch and parse the RSS/Atom feed from the given URL.
    Returns a list of feed entries on success, or an empty list on error.
    """
    d: FeedParserDict = feedparser.parse(url)

    status = getattr(d, "status", None)

    # Handle bozo/feedparser errors
    if d.bozo:
        sys.stderr.write("W: feedparser bozo=1 – parse/format issue detected.\n")
        if getattr(d, "bozo_exception", None):
            sys.stderr.write(f"Exception: {d.bozo_exception}\n")
        if status is not None:
            sys.stderr.write(f"HTTP status code: {status}\n")

    # HTTP network failure
    if status is not None and status >= 400:
        sys.stderr.write(f"E: HTTP error {status}: could not retrieve feed.\n")
        return []

    return getattr(d, "entries", [])


def parse_country_links(entries: list[object]) -> dict[str, set[str]]:
    """
    Parse the feed entries to extract mirror URLs categorized by country code.
    Returns a dictionary mapping country codes to sets of mirror URLs.
    """
    countries: dict[str, set[str]] = {}

    for entry in entries:
        # Safely access attributes using getattr
        countrycode = getattr(entry, "mirror_countrycode", None)
        if not countrycode:
            # Skip entries without a country code
            sys.stderr.write("W: Entry without 'mirror_countrycode' skipped.\n")
            continue

        if countrycode not in countries:
            countries[countrycode] = set()

        links = getattr(entry, "links", []) or []
        if not isinstance(links, list):
            sys.stderr.write("W: 'links' is not a list; skipped.\n")
            continue

        for link in links:
            href = getattr(link, "href", None)
            if href:
                countries[countrycode].add(href)
            else:
                sys.stderr.write("W: Link without 'href' skipped.\n")

    return countries


def main() -> int:
    """
    Main function to fetch and process Ubuntu mirrors from Launchpad RSS feed.
    """
    entries: list[object] = request_feed(FEED_URL)
    if not entries:
        sys.stderr.write("E: No entries retrieved from the feed.\n")
        return 1

    countries: dict[str, set[str]] = parse_country_links(entries)
    keys = sorted(countries)
    if len(keys) == 0:
        sys.stderr.write("E: Could not extract any mirror URLs by country.\n")
        return 1

    print("mirror://mirrors.ubuntu.com/mirrors.txt")
    for country in keys:
        print(f"#LOC:{country}")
        print("\n".join(sorted(countries[country])))

    return 0


if __name__ == "__main__":
    sys.exit(main())
