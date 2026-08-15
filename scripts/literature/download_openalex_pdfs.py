#!/usr/bin/env python3
"""Find and download OA PDFs for missing Zotero items via OpenAlex.

Reads the exported missing-PDF CSV, queries OpenAlex by title, and downloads
best-match PDFs into a local directory. The output directory can then be fed
to attach_local_pdfs_to_zotero_collection.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


@dataclass
class Candidate:
    title: str
    year: int | None
    score: float
    pdf_url: str | None
    landing_url: str | None
    doi: str | None
    source: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Missing-PDF CSV exported from Zotero")
    parser.add_argument("--output-dir", required=True, help="Directory to store downloaded PDFs")
    parser.add_argument("--manifest", required=True, help="CSV manifest path")
    parser.add_argument("--min-score", type=float, default=0.88, help="Minimum normalized title similarity")
    parser.add_argument("--language", choices=["english", "all"], default="english")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for testing")
    return parser.parse_args()


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = (
        text.replace(":", " ")
        .replace("-", " ")
        .replace("–", " ")
        .replace("—", " ")
        .replace("，", " ")
        .replace("：", " ")
        .replace("·", " ")
    )
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_english_title(title: str) -> bool:
    return not bool(re.search(r"[\u4e00-\u9fff]", title))


def safe_filename(title: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "_", title).strip().rstrip(".")
    return name[:180] or "untitled"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "From": "none@example.com",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def query_openalex(title: str) -> list[Candidate]:
    url = "https://api.openalex.org/works?per-page=5&search=" + urllib.parse.quote(title)
    data = fetch_json(url)
    target_norm = normalize(title)
    out: list[Candidate] = []
    for work in data.get("results", []):
        display_name = work.get("display_name") or ""
        display_norm = normalize(display_name)
        score = SequenceMatcher(None, target_norm, display_norm).ratio()
        primary = work.get("primary_location") or {}
        best_oa = work.get("best_oa_location") or {}
        pdf_url = primary.get("pdf_url") or best_oa.get("pdf_url")
        landing_url = primary.get("landing_page_url") or best_oa.get("landing_page_url")
        doi = work.get("doi")
        out.append(
            Candidate(
                title=display_name,
                year=work.get("publication_year"),
                score=score,
                pdf_url=pdf_url,
                landing_url=landing_url,
                doi=doi,
                source="openalex",
            )
        )
    out.sort(key=lambda c: c.score, reverse=True)
    return out


def fetch_pdf_url_from_html(url: str) -> str | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": url,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read(300000).decode("utf-8", "ignore")
    if "application/pdf" in content_type.lower():
        return url
    patterns = [
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+property=["\']og:pdf["\'][^>]+content=["\']([^"\']+)["\']',
        r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, body, flags=re.I)
        if match:
            return urllib.parse.urljoin(url, match.group(1))
    return None


def download_pdf(url: str, output_path: Path) -> tuple[bool, str]:
    referer = urllib.parse.urlunparse(urllib.parse.urlparse(url)._replace(path="", params="", query="", fragment=""))
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
            "Referer": referer,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
    except Exception as exc:  # noqa: BLE001
        return False, f"download_error: {exc}"

    is_pdf = "application/pdf" in content_type.lower() or data[:5] == b"%PDF-"
    if not is_pdf:
        return False, f"not_pdf_content_type: {content_type}"

    output_path.write_bytes(data)
    return True, "downloaded"


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    if args.language == "english":
        rows = [row for row in rows if is_english_title(row["title"])]
    if args.limit:
        rows = rows[: args.limit]

    results: list[dict[str, str]] = []
    for idx, row in enumerate(rows, start=1):
        title = row["title"]
        candidates = query_openalex(title)
        best = candidates[0] if candidates else None
        result = {
            "key": row["key"],
            "title": title,
            "status": "no_match",
            "score": "",
            "candidate_title": "",
            "pdf_url": "",
            "saved_file": "",
            "note": "",
        }
        if best:
            result["score"] = f"{best.score:.3f}"
            result["candidate_title"] = best.title
        if not best or best.score < args.min_score:
            results.append(result)
            time.sleep(0.2)
            continue

        pdf_url = best.pdf_url
        if not pdf_url and best.landing_url:
            try:
                pdf_url = fetch_pdf_url_from_html(best.landing_url)
            except Exception as exc:  # noqa: BLE001
                result["status"] = "landing_fetch_failed"
                result["note"] = str(exc)
                results.append(result)
                time.sleep(0.2)
                continue

        if not pdf_url:
            result["status"] = "no_pdf_url"
            results.append(result)
            time.sleep(0.2)
            continue

        ext = ".pdf"
        guessed_ext = mimetypes.guess_extension(mimetypes.guess_type(pdf_url)[0] or "")
        if guessed_ext == ".pdf":
            ext = guessed_ext
        output_path = output_dir / f"{safe_filename(title)}{ext}"
        ok, note = download_pdf(pdf_url, output_path)
        result["pdf_url"] = pdf_url
        result["note"] = note
        if ok:
            result["status"] = "downloaded"
            result["saved_file"] = str(output_path)
        else:
            result["status"] = "download_failed"
            if output_path.exists():
                output_path.unlink()
        results.append(result)
        print(f"[{idx}/{len(rows)}] {title} -> {result['status']}", flush=True)
        time.sleep(0.2)

    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["key", "title", "status", "score", "candidate_title", "pdf_url", "saved_file", "note"],
        )
        writer.writeheader()
        writer.writerows(results)

    downloaded = sum(1 for row in results if row["status"] == "downloaded")
    print(f"manifest={manifest_path}", flush=True)
    print(f"downloaded={downloaded} total={len(results)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
