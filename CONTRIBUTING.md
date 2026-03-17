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
- Keep the document title as a single unnumbered `#` heading.
- Use manual decimal numbering in Markdown headings: `## 1. ...`, `### 1.1 ...`, `### 1.2 ...`.

### Word guides
- Greek guide: original `.docx`
- English guide: matching `.en.docx`
- Do not edit the `.docx` files manually unless you are intentionally updating the shared template.
- The docs build tooling is kept under `docs/` so it stays separate from the teaching material in `code/`.
- Use a local repo virtual environment at `.venv/` for the docs build; it is not committed and should be recreated locally when needed.
- Regenerate Word guides from Markdown with `python scripts/export_docx.py`, `scripts/export-docx.ps1`, or `make -C docs docx`.
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
3. Verify that code blocks, headings, and command examples still match.
4. Create the local docs virtual environment with `python -m venv .venv`.
5. Install the docs dependency with `.venv/bin/python -m pip install -r docs/requirements-docx.txt` on Linux/macOS or `.venv\\Scripts\\python.exe -m pip install -r docs/requirements-docx.txt` on Windows.
6. Regenerate the Word guides with `scripts/export-docx.ps1` or `make -C docs docx` on Windows, or `python scripts/export_docx.py` on Linux/macOS.
7. Spot-check the generated `.docx` files before committing.

## Pull request checklist
- [ ] Greek and English versions are both updated where needed
- [ ] File naming follows the `.en` convention
- [ ] Markdown heading numbering remains consistent (`1.`, `1.1`, `1.2`, ...)
- [ ] Code blocks were preserved accurately
- [ ] Links between README files and guides still work
- [ ] `scripts/export-docx.ps1` or `make -C docs docx` was run on Windows, or `python scripts/export_docx.py` was run on Linux/macOS, and the generated Word files were checked
