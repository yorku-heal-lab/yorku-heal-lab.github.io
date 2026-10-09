#!/usr/bin/env python3
"""Download site spreadsheets from public Google Drive / Google Sheets links."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "scripts" / "data"
DEFAULT_LINKS = Path(__file__).resolve().parent / "drive-data-links.yml"

USER_AGENT = "Mozilla/5.0 (compatible; HEAL-Lab-Website-Sync/1.0)"

FILE_ID_PATTERNS = (
    re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)"),
    re.compile(r"[?&]id=([a-zA-Z0-9_-]+)"),
    re.compile(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--links",
        type=Path,
        default=DEFAULT_LINKS,
        help="YAML manifest mapping local filenames to share URLs",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory to write spreadsheets into",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without downloading")
    return parser.parse_args()


def extract_file_id(url: str) -> str:
    for pattern in FILE_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not parse Google Drive file id from URL: {url}")


def download_url_for_share_link(url: str) -> str:
    file_id = extract_file_id(url)
    if "docs.google.com/spreadsheets" in url or "/spreadsheets/" in url:
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def _confirm_token(html: str) -> str | None:
    match = re.search(r"confirm=([0-9A-Za-z_]+)", html)
    return match.group(1) if match else None


def download_bytes(url: str) -> bytes:
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    headers = {"User-Agent": USER_AGENT}

    request = urllib.request.Request(url, headers=headers)
    with opener.open(request, timeout=120) as response:
        data = response.read()
        content_type = (response.headers.get("Content-Type") or "").lower()

    if data.startswith(b"PK"):
        return data
    if "text/html" not in content_type and not data.startswith(b"<!"):
        return data

    html = data.decode("utf-8", errors="replace")
    token = _confirm_token(html)
    if not token:
        raise ValueError("Download returned HTML instead of a file (check link sharing: anyone with the link)")

    file_id = extract_file_id(url)
    confirm_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={token}"
    request = urllib.request.Request(confirm_url, headers=headers)
    with opener.open(request, timeout=120) as response:
        data = response.read()
        content_type = (response.headers.get("Content-Type") or "").lower()

    if "text/html" in content_type and not data[:2] == b"PK":
        raise ValueError("Download still returned HTML after confirm (check sharing permissions)")
    if not data:
        raise ValueError("Downloaded file was empty")
    return data


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Links manifest not found: {path} (copy drive-data-links.yml.example)")
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "files" not in raw:
        raise ValueError(f"{path}: expected top-level 'files' list")
    files = raw["files"]
    if not isinstance(files, list) or not files:
        raise ValueError(f"{path}: 'files' must be a non-empty list")
    entries: list[dict[str, str]] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: files[{index}] must be a mapping")
        name = item.get("path") or item.get("name")
        url = item.get("url") or item.get("link")
        if not name or not url:
            raise ValueError(f"{path}: files[{index}] needs 'path' and 'url'")
        entries.append({"path": str(name).strip(), "url": str(url).strip()})
    return entries


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    args = parse_args()
    entries = load_manifest(args.links)
    args.data_dir.mkdir(parents=True, exist_ok=True)

    updated = 0
    skipped = 0
    for entry in entries:
        rel = entry["path"]
        dest = args.data_dir / rel
        download_url = download_url_for_share_link(entry["url"])
        print(f"{rel} <- {entry['url']}")

        if args.dry_run:
            continue

        try:
            data = download_bytes(download_url)
        except (urllib.error.URLError, ValueError) as exc:
            print(f"ERROR: failed to download {rel}: {exc}", file=sys.stderr)
            return 1

        if not data.startswith(b"PK"):
            print(
                f"WARNING: {rel} does not look like an xlsx (missing ZIP magic); writing anyway.",
                file=sys.stderr,
            )

        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and sha256(dest.read_bytes()) == sha256(data):
            print(f"  unchanged")
            skipped += 1
            continue

        dest.write_bytes(data)
        print(f"  wrote {dest.relative_to(ROOT)} ({len(data)} bytes)")
        updated += 1

    print(f"Done: {updated} updated, {skipped} unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
