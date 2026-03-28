#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


START_PATTERN = re.compile(r"^<!--\s*AUTO-CODE:\s*(?P<path>[^>]+?)\s*-->$")
END_PATTERN = re.compile(r"^<!--\s*END AUTO-CODE\s*-->$")
FENCE_PATTERN = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)$")
LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".ps1": "powershell",
    ".sh": "bash",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".xml": "xml",
    ".json": "json",
    ".md": "markdown",
    ".txt": "text",
}


class SyncError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize fenced code blocks in Markdown from canonical source files.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional markdown files to sync. Defaults to every *.md file in the repository.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with status 1 if any file would change.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def markdown_files(root: Path, selected: list[str]) -> list[Path]:
    if selected:
        return [resolve_cli_path(root, value) for value in selected]

    return sorted(
        path
        for path in root.rglob("*.md")
        if ".git" not in path.parts
        and ".venv" not in path.parts
    )


def resolve_cli_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    if candidate.parts and candidate.parts[0] in {".", ".."}:
        return (Path.cwd() / candidate).resolve()
    return (root / candidate).resolve()


def infer_language(source_path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(source_path.suffix.lower(), "")


def read_text_preserve_newline(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    has_trailing_newline = text.endswith(("\n", "\r\n"))
    return text, newline, has_trailing_newline


def normalize_fence(indent: str, fence: str, info: str, source_path: Path) -> str:
    effective_info = info.strip() or infer_language(source_path)
    if effective_info:
        return f"{indent}{fence} {effective_info}"
    return f"{indent}{fence}"


def sync_markdown(path: Path, root: Path) -> bool:
    original_text, newline, has_trailing_newline = read_text_preserve_newline(path)
    lines = original_text.splitlines()
    output_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        match = START_PATTERN.match(line.strip())
        if match is None:
            output_lines.append(line)
            index += 1
            continue

        source_path = (root / match.group("path").strip()).resolve()
        if not source_path.exists():
            raise SyncError(f"{path}: missing AUTO-CODE source file {source_path}")

        if index + 1 >= len(lines):
            raise SyncError(f"{path}: AUTO-CODE marker at end of file")

        fence_line = lines[index + 1]
        fence_match = FENCE_PATTERN.match(fence_line)
        if fence_match is None:
            raise SyncError(f"{path}: AUTO-CODE marker must be followed by a fenced code block")

        indent = fence_match.group("indent")
        fence = fence_match.group("fence")
        info = fence_match.group("info")
        closing_fence = f"{indent}{fence}"

        closing_index = index + 2
        while closing_index < len(lines) and lines[closing_index] != closing_fence:
            closing_index += 1

        if closing_index >= len(lines):
            raise SyncError(f"{path}: fenced code block for AUTO-CODE marker is not closed")

        if closing_index + 1 >= len(lines) or END_PATTERN.match(lines[closing_index + 1].strip()) is None:
            raise SyncError(f"{path}: AUTO-CODE block must be followed by <!-- END AUTO-CODE -->")

        source_text, _, _ = read_text_preserve_newline(source_path)
        source_lines = source_text.splitlines()

        output_lines.append(line)
        output_lines.append(normalize_fence(indent, fence, info, source_path))
        output_lines.extend(source_lines)
        output_lines.append(closing_fence)
        output_lines.append(lines[closing_index + 1])

        index = closing_index + 2

    rendered = newline.join(output_lines)
    if has_trailing_newline:
        rendered += newline

    changed = rendered != original_text
    if changed and not args.check:
        path.write_text(rendered, encoding="utf-8", newline="")

    return changed


def main() -> int:
    root = repo_root()
    paths = markdown_files(root, args.files)
    changed_paths: list[Path] = []

    for path in paths:
        if sync_markdown(path, root):
            changed_paths.append(path)

    if changed_paths:
        action = "Would update" if args.check else "Updated"
        for path in changed_paths:
            print(f"{action} {path.relative_to(root)}")

    if args.check and changed_paths:
        return 1

    return 0


args = parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
