#!/usr/bin/env python3
"""Attach local PDFs from docs/literature to matching Zotero items in a collection.

Default mode is dry-run. Use --apply to modify the Zotero database and copy files
into the Zotero storage directory.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import shutil
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ATTACHMENT_ITEM_TYPE_ID = 3
TITLE_FIELD_ID = 1
KEY_ALPHABET = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
DEFAULT_MIN_SCORE = 70


@dataclass
class ParentItem:
    item_id: int
    key: str
    library_id: int
    version: int
    title: str
    pdf_count: int


@dataclass
class MatchPlan:
    parent: ParentItem
    source_pdf: Path
    score: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Path to zotero.sqlite")
    parser.add_argument("--storage-dir", required=True, help="Path to Zotero storage dir")
    parser.add_argument(
        "--literature-dir",
        default="/home/lbz/Graduation-Project/docs/literature",
        help="Local literature directory to search",
    )
    parser.add_argument(
        "--collection-name",
        default="核心参考-RL、Sim-to-Real",
        help="Exact Zotero collection name",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=DEFAULT_MIN_SCORE,
        help="Minimum title-match score required for auto-attachment",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes to the database")
    return parser.parse_args()


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
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


def preferred_rank(path: Path) -> tuple[int, str]:
    rel = str(path)
    if "/mineru_output/" in rel:
        return (3, rel)
    if "/rl_training_strategy_pdfs_" in rel:
        return (2, rel)
    return (1, rel)


def build_pdf_index(literature_dir: Path) -> list[tuple[Path, str, str]]:
    pdfs = sorted(literature_dir.rglob("*.pdf"), key=preferred_rank)
    entries: list[tuple[Path, str, str]] = []
    for path in pdfs:
        stem = path.stem
        core = re.sub(r"^.*? - \d{4}(?:-[^-]+)? - ", "", stem)
        entries.append((path, normalize(stem), normalize(core)))
    return entries


def score_match(title: str, stem_norm: str, core_norm: str) -> int:
    title_norm = normalize(title)
    if not title_norm:
        return 0
    if title_norm == core_norm or title_norm == stem_norm:
        return 100
    if title_norm in core_norm or title_norm in stem_norm:
        return 90
    tokens = [tok for tok in title_norm.split() if len(tok) > 2]
    if not tokens:
        return 0
    overlap = sum(1 for tok in tokens if tok in core_norm)
    ratio = overlap / len(tokens)
    if ratio >= 0.8:
        return int(ratio * 80)
    return 0


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def get_collection_id(con: sqlite3.Connection, collection_name: str) -> int:
    row = con.execute(
        "SELECT collectionID FROM collections WHERE collectionName = ?",
        (collection_name,),
    ).fetchone()
    if not row:
        raise SystemExit(f"Collection not found: {collection_name}")
    return int(row["collectionID"])


def get_missing_pdf_items(con: sqlite3.Connection, collection_id: int) -> list[ParentItem]:
    query = """
    WITH attach AS (
      SELECT parentItemID AS itemID,
             SUM(CASE WHEN lower(COALESCE(contentType, '')) = 'application/pdf' THEN 1 ELSE 0 END) AS pdf_count
      FROM itemAttachments
      GROUP BY parentItemID
    ),
    title_data AS (
      SELECT itemID, valueID
      FROM itemData
      WHERE fieldID = ?
    )
    SELECT i.itemID, i.key, i.libraryID, i.version, COALESCE(idv.value, '') AS title,
           COALESCE(a.pdf_count, 0) AS pdf_count
    FROM collectionItems ci
    JOIN items i ON i.itemID = ci.itemID
    JOIN itemTypesCombined it ON it.itemTypeID = i.itemTypeID
    LEFT JOIN attach a ON a.itemID = i.itemID
    LEFT JOIN title_data td ON td.itemID = i.itemID
    LEFT JOIN itemDataValues idv ON idv.valueID = td.valueID
    WHERE ci.collectionID = ?
      AND it.typeName != 'attachment'
      AND COALESCE(a.pdf_count, 0) = 0
    ORDER BY title
    """
    rows = con.execute(query, (TITLE_FIELD_ID, collection_id)).fetchall()
    return [
        ParentItem(
            item_id=int(row["itemID"]),
            key=row["key"],
            library_id=int(row["libraryID"]),
            version=int(row["version"]),
            title=row["title"],
            pdf_count=int(row["pdf_count"]),
        )
        for row in rows
    ]


def build_plan(
    items: list[ParentItem],
    pdf_index: list[tuple[Path, str, str]],
    min_score: int,
) -> list[MatchPlan]:
    plans: list[MatchPlan] = []
    for item in items:
        candidates: list[tuple[int, tuple[int, str], Path]] = []
        for path, stem_norm, core_norm in pdf_index:
            score = score_match(item.title, stem_norm, core_norm)
            if score >= min_score:
                candidates.append((score, preferred_rank(path), path))
        if candidates:
            candidates.sort(key=lambda entry: (-entry[0], entry[1]))
            best_score, _, best_path = candidates[0]
            plans.append(MatchPlan(parent=item, source_pdf=best_path, score=best_score))
    return plans


def next_item_id(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(itemID), 0) + 1 FROM items").fetchone()[0])


def next_version(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM items").fetchone()[0])


def ensure_value_id(con: sqlite3.Connection, value: str) -> int:
    row = con.execute("SELECT valueID FROM itemDataValues WHERE value = ?", (value,)).fetchone()
    if row:
        return int(row["valueID"])
    cur = con.execute("INSERT INTO itemDataValues(value) VALUES (?)", (value,))
    return int(cur.lastrowid)


def generate_key(con: sqlite3.Connection) -> str:
    while True:
        key = "".join(random.choice(KEY_ALPHABET) for _ in range(8))
        exists = con.execute("SELECT 1 FROM items WHERE key = ?", (key,)).fetchone()
        if not exists:
            return key


def attach_one(
    con: sqlite3.Connection,
    storage_dir: Path,
    plan: MatchPlan,
) -> tuple[str, str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attach_item_id = next_item_id(con)
    attach_key = generate_key(con)
    attach_version = next_version(con)
    parent_version = attach_version + 1
    filename = plan.source_pdf.name
    value_id = ensure_value_id(con, filename)

    con.execute(
        """
        INSERT INTO items(itemID, itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            attach_item_id,
            ATTACHMENT_ITEM_TYPE_ID,
            now,
            now,
            now,
            plan.parent.library_id,
            attach_key,
            attach_version,
        ),
    )
    con.execute(
        """
        INSERT INTO itemAttachments(itemID, parentItemID, linkMode, contentType, path, syncState)
        VALUES (?, ?, 0, 'application/pdf', ?, 0)
        """,
        (
            attach_item_id,
            plan.parent.item_id,
            f"storage:{filename}",
        ),
    )
    con.execute(
        "INSERT INTO itemData(itemID, fieldID, valueID) VALUES (?, ?, ?)",
        (attach_item_id, TITLE_FIELD_ID, value_id),
    )
    con.execute(
        """
        UPDATE items
        SET dateModified = ?, clientDateModified = ?, version = ?, synced = 0
        WHERE itemID = ?
        """,
        (now, now, parent_version, plan.parent.item_id),
    )

    target_dir = storage_dir / attach_key
    target_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(plan.source_pdf, target_dir / filename)
    return attach_key, filename


def main() -> int:
    args = parse_args()
    db_path = Path(args.db)
    storage_dir = Path(args.storage_dir)
    literature_dir = Path(args.literature_dir)

    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")
    if not storage_dir.is_dir():
        raise SystemExit(f"Storage dir not found: {storage_dir}")
    if not literature_dir.is_dir():
        raise SystemExit(f"Literature dir not found: {literature_dir}")

    pdf_index = build_pdf_index(literature_dir)
    con = connect(db_path)
    collection_id = get_collection_id(con, args.collection_name)
    items = get_missing_pdf_items(con, collection_id)
    plans = build_plan(items, pdf_index, args.min_score)

    writer = csv.writer(sys.stdout)
    writer.writerow(["mode", "parent_key", "parent_title", "score", "source_pdf"])
    for plan in plans:
        writer.writerow(
            [
                "apply" if args.apply else "dry-run",
                plan.parent.key,
                plan.parent.title,
                plan.score,
                str(plan.source_pdf),
            ]
        )

    if not args.apply:
        return 0

    try:
        with con:
            for plan in plans:
                attach_key, filename = attach_one(con, storage_dir, plan)
                print(
                    f"ATTACHED\tparent={plan.parent.key}\tattachment={attach_key}\tfile={filename}",
                    file=sys.stderr,
                )
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
