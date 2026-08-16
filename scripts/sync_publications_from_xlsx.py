#!/usr/bin/env python3
"""Sync publications from the downloaded publications spreadsheet."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import openpyxl
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XLSX = ROOT / "scripts" / "data" / "publications.xlsx"
DEFAULT_PUBLICATIONS_YML = ROOT / "_data" / "publications.yml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=DEFAULT_XLSX,
        help="Input publications spreadsheet path",
    )
    parser.add_argument(
        "--publications-yml",
        type=Path,
        default=DEFAULT_PUBLICATIONS_YML,
        help="Output publications data file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and summarize without writing publications.yml",
    )
    return parser.parse_args()


def setup_yaml() -> None:
    def represent_str(dumper: yaml.Dumper, data: str) -> yaml.nodes.ScalarNode:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
        if len(data) > 100:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, represent_str)


def dump_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(data, handle, sort_keys=False, allow_unicode=True, width=1000)


def normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_year(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    match = re.search(r"(19|20)\d{2}", normalize(value))
    return int(match.group(0)) if match else 0


def extract_year_from_text(text: str) -> int:
    matches = re.findall(r"(19|20)\d{2}", text)
    return int(matches[-1]) if matches else 0


def row_values(row: tuple[object, ...]) -> tuple[object, ...]:
    return tuple(cell.value for cell in row)


def cell_hyperlink(cell: object) -> str:
    hyperlink = getattr(cell, "hyperlink", None)
    if hyperlink is None:
        return ""
    return normalize(getattr(hyperlink, "target", None))


def is_title_row(values: tuple[object, ...]) -> bool:
    if not values or not normalize(values[0]):
        return False
    if parse_year(values[2] if len(values) > 2 else None):
        return True
    if len(values) > 1 and isinstance(values[1], (int, float)):
        return True
    return False


def is_detail_row(values: tuple[object, ...]) -> bool:
    if not values or not normalize(values[0]):
        return False
    return normalize(values[1] if len(values) > 1 else None) == "" and normalize(values[2] if len(values) > 2 else None) == ""


def normalize_title(title: str) -> str:
    cleaned = title.lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def read_publications(xlsx_path: Path) -> tuple[list[dict], list[str]]:
    workbook = openpyxl.load_workbook(xlsx_path)
    worksheet = workbook.active
    rows = list(worksheet.iter_rows())

    publications: list[dict] = []
    warnings: list[str] = []
    index = 0

    while index < len(rows):
        row = rows[index]
        values = row_values(row)
        if not is_title_row(values):
            index += 1
            continue

        if index + 2 >= len(rows):
            warnings.append(f"Row {index + 1}: incomplete publication block for '{normalize(values[0])}'")
            break

        author_row = rows[index + 1]
        venue_row = rows[index + 2]
        author_values = row_values(author_row)
        venue_values = row_values(venue_row)

        if not is_detail_row(author_values) or not is_detail_row(venue_values):
            warnings.append(f"Row {index + 1}: expected author/venue rows after '{normalize(values[0])}'")
            index += 1
            continue

        title = normalize(values[0])
        authors = normalize(author_values[0])
        venue = normalize(venue_values[0])
        year = parse_year(values[2] if len(values) > 2 else None) or extract_year_from_text(venue)
        paper_url = cell_hyperlink(row[0])

        if not title or not authors or not venue:
            warnings.append(f"Row {index + 1}: missing title, authors, or venue")
            index += 1
            continue

        publication = {
            "title": title,
            "authors": authors,
            "venue": venue,
            "year": year,
        }
        if paper_url:
            publication["paper_url"] = paper_url
        publications.append(publication)
        index += 3

    return publications, warnings


def publication_completeness(publication: dict) -> tuple[int, int, int, int, int]:
    return (
        1 if publication.get("paper_url") else 0,
        1 if publication.get("year") else 0,
        len(publication.get("venue", "")),
        len(publication.get("authors", "")),
        len(publication.get("title", "")),
    )


def merge_publication_records(primary: dict, secondary: dict) -> dict:
    if publication_completeness(secondary) > publication_completeness(primary):
        primary, secondary = secondary, primary

    merged = dict(primary)
    for field in ("year", "authors", "venue", "paper_url", "code_url"):
        if not merged.get(field) and secondary.get(field):
            merged[field] = secondary[field]
    return merged


def dedupe_publications(publications: list[dict]) -> tuple[list[dict], int]:
    duplicates = 0
    by_title: dict[str, dict] = {}

    for publication in publications:
        key = normalize_title(publication["title"])
        if not key:
            continue

        existing = by_title.get(key)
        if existing is None:
            by_title[key] = publication
            continue

        duplicates += 1
        by_title[key] = merge_publication_records(existing, publication)

    deduped = list(by_title.values())
    by_url: dict[str, dict] = {}
    without_url: list[dict] = []

    for publication in deduped:
        paper_url = publication.get("paper_url")
        if not paper_url:
            without_url.append(publication)
            continue

        existing = by_url.get(paper_url)
        if existing is None:
            by_url[paper_url] = publication
            continue

        duplicates += 1
        by_url[paper_url] = merge_publication_records(existing, publication)

    return without_url + list(by_url.values()), duplicates


def sort_publications(publications: list[dict]) -> list[dict]:
    return sorted(
        publications,
        key=lambda pub: (
            -int(pub.get("year") or 0),
            pub.get("authors", "").casefold(),
            pub.get("title", "").casefold(),
        ),
    )


def main() -> int:
    setup_yaml()
    args = parse_args()

    if not args.xlsx.exists():
        print(f"Spreadsheet not found: {args.xlsx}", file=sys.stderr)
        return 1

    publications, warnings = read_publications(args.xlsx)
    parsed_count = len(publications)
    publications, duplicate_count = dedupe_publications(publications)
    publications = sort_publications(publications)

    print(f"Parsed {parsed_count} publication(s) from {args.xlsx.name}")
    if duplicate_count:
        print(f"Deduplicated {duplicate_count} duplicate(s); kept {len(publications)} unique publication(s)")
    else:
        print(f"Kept {len(publications)} unique publication(s)")

    if warnings:
        print(f"Warnings ({len(warnings)}):", file=sys.stderr)
        for warning in warnings[:10]:
            print(f"  - {warning}", file=sys.stderr)
        if len(warnings) > 10:
            print(f"  - ... and {len(warnings) - 10} more", file=sys.stderr)

    if not publications:
        print("No publications parsed. Existing publications.yml was not changed.", file=sys.stderr)
        return 1

    years = [pub["year"] for pub in publications if pub.get("year")]
    if years:
        print(f"Year range: {min(years)}-{max(years)}")

    with_paper_links = sum(1 for publication in publications if publication.get("paper_url"))
    print(f"Links: {with_paper_links} paper")

    if args.dry_run:
        print("Dry run complete; no files written.")
        for publication in publications[:5]:
            link_note = " [paper]" if publication.get("paper_url") else ""
            print(f"  [{publication['year']}] {publication['title']}{link_note}")
        if len(publications) > 5:
            print(f"  ... and {len(publications) - 5} more")
        return 0

    dump_yaml(args.publications_yml, publications)
    print(f"Updated {args.publications_yml.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
