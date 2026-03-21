#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def find_best_markdown(doc_dir: Path) -> Path | None:
    if not doc_dir.is_dir():
        return None
    markdown_files = sorted(doc_dir.rglob("*.md"))
    if not markdown_files:
        return None
    for candidate in markdown_files:
        if candidate.stem == doc_dir.name:
            return candidate
    return markdown_files[0]


def find_assets_dir(doc_dir: Path) -> Path | None:
    if not doc_dir.is_dir():
        return None
    for name in ("images", "assets"):
        candidate = doc_dir / name
        if candidate.is_dir():
            return candidate
    for child in sorted(doc_dir.iterdir()):
        if child.is_dir() and any(child.iterdir()):
            return child
    return None


def build_manifest(source_root: Path, output_root: Path, manifest_path: Path) -> None:
    pdfs = sorted(source_root.glob("*.pdf"))
    manifest_dir = manifest_path.parent
    lines = [
        "# Literature Catalog",
        "",
        "This catalog maps each source PDF to its MinerU-derived Markdown output.",
        "",
        "| Status | PDF | Markdown | Assets |",
        "| --- | --- | --- | --- |",
    ]

    for pdf in pdfs:
        doc_dir = output_root / pdf.stem
        md_path = find_best_markdown(doc_dir)
        assets_dir = find_assets_dir(doc_dir)
        status = "ready" if md_path else "pending"
        pdf_rel = pdf.relative_to(manifest_dir)
        md_rel = md_path.relative_to(manifest_dir) if md_path else None
        assets_rel = assets_dir.relative_to(manifest_dir) if assets_dir else None

        pdf_link = f"[{pdf.name}]({pdf_rel.as_posix()})"
        md_link = f"[{md_rel.name}]({md_rel.as_posix()})" if md_rel else "-"
        assets_link = f"[{assets_rel.name}]({assets_rel.as_posix()})" if assets_rel else "-"
        lines.append(f"| {status} | {pdf_link} | {md_link} | {assets_link} |")

    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Markdown catalog for literature PDFs and MinerU outputs.")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_manifest(args.source_root.resolve(), args.output_root.resolve(), args.manifest.resolve())


if __name__ == "__main__":
    main()
