#!/usr/bin/python3
#  get_debian_mirrors.py - Parse Mirrors.masterlist and create a mirror list.
#
#  Copyright (c) 2010-2011 Julian Andres Klode <jak@debian.org>
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
import collections
import sys
import urllib.request
from collections.abc import Iterable

from debian import deb822


def main() -> int:
    """
    Main function to parse the Debian mirrors
    """
    try:
        masterlist = urllib.request.urlopen(
            "https://mirror-master.debian.org/status/Mirrors.masterlist"
        )
    except Exception as e:
        sys.stderr.write(f"E: Could not retrieve Mirrors.masterlist: {e}\n")
        return 1

    mirror_map: dict[str, set[str]] = collections.defaultdict(set)

    mirrors: Iterable[deb822.Deb822] = deb822.Deb822.iter_paragraphs(masterlist)
    for mirror in mirrors:
        country_field = mirror.get("country")
        if not country_field:
            continue

        country = country_field.split(None, 1)[0]

        site = mirror.get("site")
        if not site:
            continue

        for proto in ("http", "ftp"):
            key = f"archive-{proto}"
            path = mirror.get(key)

            if path:
                url = f"{proto}://{site}{path}"
                mirror_map[country].add(url)

    # error if nothing parsed
    if not mirror_map:
        sys.stderr.write("E: Could not read any mirrors from the master list\n")
        return 1

    # output mirrors sorted by country
    for country in sorted(mirror_map):
        print(f"#LOC:{country}")
        print("\n".join(sorted(mirror_map[country])))

    return 0


if __name__ == "__main__":
    sys.exit(main())
