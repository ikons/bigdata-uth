# Contributing

## Language and file naming convention

This repository is maintained in both Greek and English.

### General rule
- Keep the original Greek files unchanged when possible.
- Add English versions as parallel files using the `.en` suffix before the extension.

Examples:
- `README.md` -> Greek
- `README.en.md` -> English
- `guide.docx` -> Greek
- `guide.en.docx` -> English

## Documentation rules

### Markdown guides
- Greek guide: `README.md`
- English guide: `README.en.md`
- Keep the same structure, section order, code blocks, and examples across both versions.
- When updating one language, update the corresponding file in the other language as soon as possible.
- Student-facing prose in Greek should read as natural Greek, not as a word-for-word translation from English.
- In Greek guides, prefer Greek wording for general instructional text and keep English only for established technical terms such as `API`, `Spark UI`, `Docker`, `Kubernetes`, commands, file names, and object names.
- Keep the document title as a single unnumbered `#` heading.
- Use manual decimal numbering in Markdown headings: `## 1. ...`, `### 1.1 ...`, `### 1.2 ...`.
- For code snippets that must stay identical to repository files, prefer `AUTO-CODE` blocks instead of manually copying code.
- `AUTO-CODE` blocks are synchronized from canonical source files with `python scripts/sync_markdown_code.py`.
- Paths inside `AUTO-CODE` blocks are repository-root relative, for example `<!-- AUTO-CODE: code/RddQ2.py -->`.
- Student-facing terminal commands should prefer the tested **WSL-first** path unless a guide explicitly targets Windows PowerShell.
- When a guide assumes the repository already exists locally, refer to it consistently as `~/bigdata-uth`.
- Local guides should assume `.venv` activation inside the repo; remote guides should remind the reader to leave `.venv` and reload `~/bigdata-env.sh` before `spark-submit`.

### Word guides
- Greek guide: original `.docx`
- English guide: matching `.en.docx`
- Do not edit the `.docx` files manually unless you are intentionally updating the shared template.
- The docs build tooling is kept under `docs/` so it stays separate from the teaching material in `code/`.
- Use a local repo virtual environment at `.venv/` for the docs build; it is not committed and should be recreated locally when needed.
- Regenerate Word guides from Markdown with `python scripts/export_docx.py`, `scripts/export-docx.ps1`, or `make -C docs docx`.
- Before exporting Word guides or committing docs updates, run `python scripts/sync_markdown_code.py` or `make -C docs sync`.
- The DOCX source/output mapping lives in `docs/docx-manifest.json`.
- The shared Word styling template is `templates/reference.docx`.
- The template itself is generated from code with `python scripts/create_reference_template.py`.
- The generated `.docx` files use a real Word table-of-contents field emitted by Pandoc.
- On Windows, `scripts/export-docx.ps1` and `make -C docs docx` also refresh the TOC through Microsoft Word COM automation after Pandoc export.

## Code comments and teaching material
- Prefer English for inline comments inside code snippets that are intended for international students or collaborators.
- Do not change commands, file names, or Kubernetes/Docker object names unless there is a technical reason.
- Keep placeholders such as `<username>` exactly as they are.

## Style guidelines for English content
- Use clear technical English.
- Prefer instructional phrasing such as "Run the following command" or "Create the file below".
- Keep terminology consistent across all guides:
  - container
  - image
  - deployment
  - service
  - secret
  - configmap
  - persistent volume claim

## Recommended workflow for future updates
1. Edit the Greek Markdown guide if it is the canonical teaching version.
2. Update the corresponding English Markdown guide.
3. If the guide contains repo-local commands, verify that they still make sense from `~/bigdata-uth`.
4. If the guide moves from local execution to remote execution, verify that the handoff from `.venv` to `~/bigdata-env.sh` is explicit.
5. Run `python scripts/sync_markdown_code.py` or `make -C docs sync`.
6. Verify that headings, commands, and non-generated prose still match across languages.
7. Create the local docs virtual environment with `python -m venv .venv`.
8. Install the docs dependency with `.venv/bin/python -m pip install -r docs/requirements-docx.txt` on Linux/macOS or `.venv\\Scripts\\python.exe -m pip install -r docs/requirements-docx.txt` on Windows.
9. Regenerate the Word guides with `scripts/export-docx.ps1` or `make -C docs docx` on Windows, or `python scripts/export_docx.py` on Linux/macOS.
10. Spot-check the generated `.docx` files before committing.

## Pull request checklist
- [ ] Greek and English versions are both updated where needed
- [ ] File naming follows the `.en` convention
- [ ] Markdown heading numbering remains consistent (`1.`, `1.1`, `1.2`, ...)
- [ ] `AUTO-CODE` blocks were synchronized where applicable
- [ ] Links between README files and guides still work
- [ ] `python scripts/sync_markdown_code.py --check` passes
- [ ] `scripts/export-docx.ps1` or `make -C docs docx` was run on Windows, or `python scripts/export_docx.py` was run on Linux/macOS, and the generated Word files were checked
