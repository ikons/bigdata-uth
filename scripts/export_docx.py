#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor


ACCENT_COLOR = RGBColor(0x1F, 0x4E, 0x79)
DEFAULT_MANIFEST = "docs/docx-manifest.json"
DEFAULT_REFERENCE_DOC = "templates/reference.docx"
DEFAULT_WINDOWS_PANDOC_PATHS = (
    Path.home() / "AppData" / "Local" / "Pandoc" / "pandoc.exe",
    Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "pandoc.exe",
    Path("C:/Program Files/Pandoc/pandoc.exe"),
)


def resolve_argument_path(value: str, repo_root: Path) -> Path:
    raw_path = Path(value)
    if raw_path.is_absolute():
        return raw_path.resolve()

    if raw_path.parts and raw_path.parts[0] in {".", ".."}:
        return (Path.cwd() / raw_path).resolve()

    return (repo_root / raw_path).resolve()


def resolve_pandoc_executable() -> str:
    explicit = os.environ.get("PANDOC_EXECUTABLE")
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_absolute() or any(separator in explicit for separator in ("/", "\\")):
            if candidate.exists():
                return str(candidate.resolve())
        else:
            resolved = shutil.which(explicit)
            if resolved:
                return resolved

    resolved = shutil.which("pandoc")
    if resolved:
        return resolved

    if sys.platform == "win32":
        for candidate in DEFAULT_WINDOWS_PANDOC_PATHS:
            if candidate.exists():
                return str(candidate.resolve())

    raise FileNotFoundError(
        "Pandoc executable not found. Install pandoc or set the PANDOC_EXECUTABLE environment variable."
    )


def set_title_style(paragraph) -> None:
    paragraph.style = "Title"
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = ACCENT_COLOR


def apply_postprocessing(document_path: Path) -> None:
    document = Document(document_path)

    title_paragraph = next((paragraph for paragraph in document.paragraphs if paragraph.text.strip()), None)
    if title_paragraph is not None:
        set_title_style(title_paragraph)

    document.save(document_path)


def export_entry(repo_root: Path, reference_doc: Path, pandoc_executable: str, entry: dict) -> None:
    source_path = (repo_root / entry["source"]).resolve()
    output_path = (repo_root / entry["output"]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pandoc_executable,
        str(source_path),
        "--from=gfm",
        "--to=docx",
        "--toc",
        "--toc-depth=3",
        "--shift-heading-level-by=-1",
        "--metadata",
        f"toc-title={entry['tocTitle']}",
        f"--reference-doc={reference_doc}",
        f"--resource-path={source_path.parent}{os.pathsep}{repo_root}",
        f"--output={output_path}",
    ]

    print(f"Exporting {entry['source']} -> {output_path.relative_to(repo_root)}")
    subprocess.run(command, check=True)

    apply_postprocessing(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Markdown guides to DOCX.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Manifest path.")
    parser.add_argument("--reference-doc", default=DEFAULT_REFERENCE_DOC, help="Reference DOCX path.")
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="Optional manifest ids, source paths, or output paths to export.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = resolve_argument_path(args.manifest, repo_root)
    reference_doc = resolve_argument_path(args.reference_doc, repo_root)
    pandoc_executable = resolve_pandoc_executable()

    if not reference_doc.exists():
        template_script = repo_root / "scripts" / "create_reference_template.py"
        subprocess.run(
            [sys.executable, str(template_script), "--output", str(reference_doc)],
            check=True,
        )

    with manifest_path.open(encoding="utf-8") as handle:
        entries = json.load(handle)

    only = set(args.only)
    selected = [
        entry
        for entry in entries
        if not only
        or entry["id"] in only
        or entry["source"] in only
        or entry["output"] in only
    ]

    if not selected:
        raise SystemExit("No manifest entries matched the requested selection.")

    for entry in selected:
        export_entry(repo_root, reference_doc, pandoc_executable, entry)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

