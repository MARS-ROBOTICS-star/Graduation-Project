#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


def collect_pdfs(source_root: Path) -> list[Path]:
    pdfs = set(source_root.glob("*.pdf"))
    for subdir in ("综述论文", "研究论文"):
        category_dir = source_root / subdir
        if category_dir.is_dir():
            pdfs.update(category_dir.rglob("*.pdf"))
    return sorted(pdfs, key=lambda path: path.relative_to(source_root).as_posix())


def find_best_markdown(output_root: Path, doc_name: str) -> Path | None:
    flat_candidate = output_root / f"{doc_name}.md"
    if flat_candidate.is_file():
        return flat_candidate

    doc_dir = output_root / doc_name
    if not doc_dir.is_dir():
        return None
    markdown_files = sorted(doc_dir.rglob("*.md"))
    if not markdown_files:
        return None
    for candidate in markdown_files:
        if candidate.stem == doc_dir.name:
            return candidate
    return markdown_files[0]


def find_assets_dir(output_root: Path, doc_name: str) -> Path | None:
    flat_candidate = output_root / f"{doc_name}_images"
    if flat_candidate.is_dir():
        return flat_candidate

    doc_dir = output_root / doc_name
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
    pdfs = collect_pdfs(source_root)
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
        md_path = find_best_markdown(output_root, pdf.stem)
        assets_dir = find_assets_dir(output_root, pdf.stem)
        status = "ready" if md_path else "pending"
        pdf_rel = Path(os.path.relpath(pdf, manifest_dir))
        md_rel = Path(os.path.relpath(md_path, manifest_dir)) if md_path else None
        assets_rel = Path(os.path.relpath(assets_dir, manifest_dir)) if assets_dir else None

        pdf_label = pdf.relative_to(source_root).as_posix()
        pdf_link = f"[{pdf_label}]({pdf_rel.as_posix()})"
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
