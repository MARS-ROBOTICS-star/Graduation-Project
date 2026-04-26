#!/usr/bin/env python3
"""Import reference rows from a markdown table into a local Zotero collection.

This script works directly on the local zotero.sqlite database. It is intended
for batches where Zotero MCP can manage collections but cannot create generic
manual items with custom metadata.

Default mode is dry-run. Use --apply only after closing Zotero Desktop.
"""

from __future__ import annotations

import argparse
import random
import re
import shutil
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


KEY_ALPHABET = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"


@dataclass
class RefEntry:
    section: str
    year: str
    title: str
    source: str
    origin: str


@dataclass
class ParsedSource:
    authors: list[str]
    publication_title: str | None
    publisher: str | None
    university: str | None
    thesis_type: str | None
    extra_lines: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Path to zotero.sqlite")
    parser.add_argument("--markdown", required=True, help="Source markdown table path")
    parser.add_argument("--collection-name", required=True, help="Exact Zotero collection name")
    parser.add_argument(
        "--backup-dir",
        default="",
        help="Optional directory for sqlite backups; defaults next to zotero.sqlite",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag text to append into Extra for created items",
    )
    parser.add_argument("--apply", action="store_true", help="Write changes to the database")
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


def read_entries(markdown_path: Path) -> list[RefEntry]:
    text = markdown_path.read_text(encoding="utf-8")
    entries: list[RefEntry] = []
    section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "## 国内文献":
            section = "国内"
            continue
        if line == "## 国外文献":
            section = "国外"
            continue
        if line.startswith("## ") and line not in ("## 国内文献", "## 国外文献"):
            section = None
            continue
        if section is None or not line.startswith("|"):
            continue
        if line.startswith("| ---") or "年份" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 4:
            continue
        year, title, source, origin = parts
        entries.append(
            RefEntry(
                section=section,
                year=year,
                title=title,
                source=source,
                origin=origin,
            )
        )
    return entries


def split_authors(author_text: str) -> list[str]:
    text = author_text.strip().rstrip("，,")
    text = re.sub(r"\bet\s+al\.?$", "", text, flags=re.I).strip()
    text = re.sub(r"等$", "", text).strip()
    if not text:
        return []
    if "、" in text:
        parts = [part.strip() for part in text.split("、")]
    elif "，" in text:
        parts = [part.strip() for part in text.split("，")]
    elif "," in text:
        parts = [part.strip() for part in text.split(",")]
    else:
        parts = [text]
    return [part for part in parts if part]


def parse_source(source: str) -> ParsedSource:
    text = source.strip()
    publication_title: str | None = None
    publisher: str | None = None
    university: str | None = None
    thesis_type: str | None = None
    extra_lines: list[str] = []

    author_text = ""
    if "`" in text:
        first_tick = text.find("`")
        second_tick = text.find("`", first_tick + 1)
        if second_tick != -1:
            publication_title = text[first_tick + 1 : second_tick].strip()
            author_text = text[:first_tick].rstrip("，, ")
            remainder = text[second_tick + 1 :].strip(" ，,")
            if remainder:
                extra_lines.append(remainder)
        else:
            author_text = text
    else:
        match = re.split(r"[，,]", text, maxsplit=1)
        author_text = match[0].strip()
        remainder = match[1].strip() if len(match) > 1 else ""
        if "学位论文" in remainder:
            university = remainder.replace("学位论文", "").strip(" ，,")
            thesis_type = "学位论文"
        elif "专著" in remainder:
            publisher = remainder.replace("专著", "").strip(" ，,")
        elif remainder:
            extra_lines.append(remainder)

    return ParsedSource(
        authors=split_authors(author_text),
        publication_title=publication_title,
        publisher=publisher,
        university=university,
        thesis_type=thesis_type,
        extra_lines=extra_lines,
    )


def infer_item_type(entry: RefEntry) -> str:
    if "学位论文" in entry.source:
        return "thesis"
    if "专著" in entry.source or "出版社" in entry.source:
        return "book"
    return "journalArticle"


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def connect_ro(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    return con


def backup_db(db_path: Path, backup_dir: Path | None) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_dir = backup_dir if backup_dir is not None else db_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    backup_path = target_dir / f"{db_path.name}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def fetch_constants(con: sqlite3.Connection) -> tuple[dict[str, int], dict[str, int], int]:
    item_types = {
        row["typeName"]: int(row["itemTypeID"])
        for row in con.execute(
            "SELECT itemTypeID, typeName FROM itemTypesCombined WHERE typeName IN ('journalArticle','book','thesis')"
        ).fetchall()
    }
    fields = {
        row["fieldName"]: int(row["fieldID"])
        for row in con.execute(
            """
            SELECT fieldID, fieldName FROM fieldsCombined
            WHERE fieldName IN ('title','date','publicationTitle','publisher','extra','thesisType','university')
            """
        ).fetchall()
    }
    author_type_id = int(
        con.execute("SELECT creatorTypeID FROM creatorTypes WHERE creatorType='author'").fetchone()[0]
    )
    return item_types, fields, author_type_id


def get_collection_id(con: sqlite3.Connection, collection_name: str) -> int:
    row = con.execute(
        "SELECT collectionID FROM collections WHERE collectionName = ?",
        (collection_name,),
    ).fetchone()
    if not row:
        raise SystemExit(f"Collection not found: {collection_name}")
    return int(row["collectionID"])


def build_existing_title_index(con: sqlite3.Connection) -> dict[str, list[int]]:
    query = """
    SELECT i.itemID, idv.value AS title
    FROM items i
    JOIN itemTypesCombined it ON it.itemTypeID = i.itemTypeID
    LEFT JOIN itemData id ON id.itemID = i.itemID AND id.fieldID = 1
    LEFT JOIN itemDataValues idv ON idv.valueID = id.valueID
    WHERE it.typeName != 'attachment'
      AND idv.value IS NOT NULL
    """
    index: dict[str, list[int]] = {}
    for row in con.execute(query):
        title_norm = normalize(row["title"])
        if title_norm:
            index.setdefault(title_norm, []).append(int(row["itemID"]))
    return index


def get_collection_item_ids(con: sqlite3.Connection, collection_id: int) -> set[int]:
    return {
        int(row["itemID"])
        for row in con.execute(
            "SELECT itemID FROM collectionItems WHERE collectionID = ?",
            (collection_id,),
        ).fetchall()
    }


def next_item_id(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(itemID), 0) + 1 FROM items").fetchone()[0])


def next_creator_id(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(creatorID), 0) + 1 FROM creators").fetchone()[0])


def next_value_id(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(valueID), 0) + 1 FROM itemDataValues").fetchone()[0])


def next_version(con: sqlite3.Connection) -> int:
    return int(con.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM items").fetchone()[0])


def next_collection_order(con: sqlite3.Connection, collection_id: int) -> int:
    return int(
        con.execute(
            "SELECT COALESCE(MAX(orderIndex), -1) + 1 FROM collectionItems WHERE collectionID = ?",
            (collection_id,),
        ).fetchone()[0]
    )


def ensure_value_id(con: sqlite3.Connection, value: str) -> int:
    row = con.execute("SELECT valueID FROM itemDataValues WHERE value = ?", (value,)).fetchone()
    if row:
        return int(row["valueID"])
    value_id = next_value_id(con)
    con.execute("INSERT INTO itemDataValues(valueID, value) VALUES (?, ?)", (value_id, value))
    return value_id


def ensure_creator_id(con: sqlite3.Connection, author: str) -> int:
    row = con.execute(
        """
        SELECT creatorID FROM creators
        WHERE firstName = '' AND lastName = ? AND fieldMode = 1
        """,
        (author,),
    ).fetchone()
    if row:
        return int(row["creatorID"])
    creator_id = next_creator_id(con)
    con.execute(
        "INSERT INTO creators(creatorID, firstName, lastName, fieldMode) VALUES (?, '', ?, 1)",
        (creator_id, author),
    )
    return creator_id


def generate_key(con: sqlite3.Connection) -> str:
    while True:
        key = "".join(random.choice(KEY_ALPHABET) for _ in range(8))
        exists = con.execute("SELECT 1 FROM items WHERE key = ?", (key,)).fetchone()
        if not exists:
            return key


def choose_existing_item(item_ids: list[int], collection_item_ids: set[int]) -> int:
    for item_id in item_ids:
        if item_id in collection_item_ids:
            return item_id
    return item_ids[0]


def add_item_to_collection(con: sqlite3.Connection, collection_id: int, item_id: int) -> None:
    exists = con.execute(
        "SELECT 1 FROM collectionItems WHERE collectionID = ? AND itemID = ?",
        (collection_id, item_id),
    ).fetchone()
    if exists:
        return
    con.execute(
        "INSERT INTO collectionItems(collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
        (collection_id, item_id, next_collection_order(con, collection_id)),
    )


def insert_creator(con: sqlite3.Connection, item_id: int, creator_type_id: int, author: str, order_index: int) -> None:
    creator_id = ensure_creator_id(con, author)
    con.execute(
        """
        INSERT INTO itemCreators(itemID, creatorID, creatorTypeID, orderIndex)
        VALUES (?, ?, ?, ?)
        """,
        (item_id, creator_id, creator_type_id, order_index),
    )


def insert_field(con: sqlite3.Connection, item_id: int, field_id: int, value: str | None) -> None:
    if value is None:
        return
    value = value.strip()
    if not value:
        return
    value_id = ensure_value_id(con, value)
    con.execute(
        "INSERT INTO itemData(itemID, fieldID, valueID) VALUES (?, ?, ?)",
        (item_id, field_id, value_id),
    )


def create_item(
    con: sqlite3.Connection,
    collection_id: int,
    item_types: dict[str, int],
    fields: dict[str, int],
    author_type_id: int,
    entry: RefEntry,
    tags: list[str],
) -> int:
    parsed = parse_source(entry.source)
    item_type = infer_item_type(entry)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item_id = next_item_id(con)
    item_key = generate_key(con)
    version = next_version(con)

    con.execute(
        """
        INSERT INTO items(itemID, itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
        VALUES (?, ?, ?, ?, ?, 1, ?, ?, 0)
        """,
        (item_id, item_types[item_type], now, now, now, item_key, version),
    )

    insert_field(con, item_id, fields["title"], entry.title)
    insert_field(con, item_id, fields["date"], entry.year)

    if item_type == "journalArticle":
        insert_field(con, item_id, fields["publicationTitle"], parsed.publication_title)
        if parsed.publisher:
            insert_field(con, item_id, fields["publisher"], parsed.publisher)
    elif item_type == "book":
        insert_field(con, item_id, fields["publisher"], parsed.publisher)
    elif item_type == "thesis":
        insert_field(con, item_id, fields["thesisType"], parsed.thesis_type or "学位论文")
        insert_field(con, item_id, fields["university"], parsed.university)

    extra_lines = [
        f"source_line: {entry.source}",
        f"section: {entry.section}",
        f"origin: {entry.origin}",
    ]
    extra_lines.extend(parsed.extra_lines)
    extra_lines.extend([f"tag: {tag}" for tag in tags])
    insert_field(con, item_id, fields["extra"], "\n".join(extra_lines))

    for idx, author in enumerate(parsed.authors):
        insert_creator(con, item_id, author_type_id, author, idx)

    add_item_to_collection(con, collection_id, item_id)
    return item_id


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).expanduser().resolve()
    markdown_path = Path(args.markdown).expanduser().resolve()
    backup_dir = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else None

    entries = read_entries(markdown_path)
    if not entries:
        raise SystemExit(f"No reference rows parsed from {markdown_path}")

    read_con = connect_ro(db_path)
    collection_id = get_collection_id(read_con, args.collection_name)
    title_index = build_existing_title_index(read_con)
    collection_item_ids = get_collection_item_ids(read_con, collection_id)
    item_types, fields, author_type_id = fetch_constants(read_con)

    reuse_count = 0
    create_count = 0
    pending: list[tuple[str, str, int | None]] = []
    for entry in entries:
        existing_ids = title_index.get(normalize(entry.title), [])
        if existing_ids:
            chosen = choose_existing_item(existing_ids, collection_item_ids)
            pending.append(("reuse", entry.title, chosen))
            reuse_count += 1
        else:
            pending.append(("create", entry.title, None))
            create_count += 1

    print(f"collection_id={collection_id}")
    print(f"parsed_entries={len(entries)} reuse_existing={reuse_count} create_new={create_count}")
    for action, title, item_id in pending[:10]:
        print(f"{action:>6} | {title} | {item_id if item_id is not None else '-'}")
    if len(pending) > 10:
        print(f"... ({len(pending) - 10} more)")

    if not args.apply:
        return 0

    backup_path = backup_db(db_path, backup_dir)
    print(f"backup_created={backup_path}")

    con = connect(db_path)
    try:
        collection_id = get_collection_id(con, args.collection_name)
        item_types, fields, author_type_id = fetch_constants(con)
        title_index = build_existing_title_index(con)
        collection_item_ids = get_collection_item_ids(con, collection_id)

        reused = 0
        created = 0
        for entry in entries:
            existing_ids = title_index.get(normalize(entry.title), [])
            if existing_ids:
                chosen = choose_existing_item(existing_ids, collection_item_ids)
                add_item_to_collection(con, collection_id, chosen)
                collection_item_ids.add(chosen)
                reused += 1
                continue

            item_id = create_item(
                con,
                collection_id,
                item_types,
                fields,
                author_type_id,
                entry,
                args.tag,
            )
            title_index.setdefault(normalize(entry.title), []).append(item_id)
            collection_item_ids.add(item_id)
            created += 1

        con.commit()
        print(f"applied reuse_existing={reused} create_new={created}")
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
