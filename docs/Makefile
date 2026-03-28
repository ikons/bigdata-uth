ROOT := ..
VENV := $(ROOT)/.venv
REQUIREMENTS := requirements-docx.txt
TEMPLATE_SCRIPT := $(ROOT)/scripts/create_reference_template.py
EXPORT_SCRIPT := $(ROOT)/scripts/export_docx.py
SYNC_SCRIPT := $(ROOT)/scripts/sync_markdown_code.py
REFERENCE_DOC := $(ROOT)/templates/reference.docx
MANIFEST := $(ROOT)/docs/docx-manifest.json
DOCX_ARGS := --manifest $(MANIFEST) --reference-doc $(REFERENCE_DOC)

ifeq ($(OS),Windows_NT)
PYTHON ?= python
VENV_PYTHON := $(VENV)/Scripts/python.exe
DOCX_WRAPPER := powershell -NoProfile -ExecutionPolicy Bypass -File $(ROOT)/scripts/export-docx.ps1 -PythonExecutable "$(VENV_PYTHON)"
else
PYTHON ?= python3
VENV_PYTHON := $(VENV)/bin/python
DOCX_WRAPPER := $(VENV_PYTHON) $(EXPORT_SCRIPT)
endif

.PHONY: all venv install sync check-sync template docx \
	docx-preparatory docx-preparatory-el docx-preparatory-en \
	docx-pycharm docx-pycharm-el docx-pycharm-en \
	docx-vscode docx-vscode-el docx-vscode-en \
	docx-local-spark docx-local-spark-el docx-local-spark-en \
	docx-lab1-docker docx-lab1-docker-el docx-lab1-docker-en \
	docx-lab1-k8s docx-lab1-k8s-el docx-lab1-k8s-en \
	docx-lab2 docx-lab2-el docx-lab2-en

all: docx

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PYTHON) -m pip install -r $(REQUIREMENTS)

sync:
	$(PYTHON) $(SYNC_SCRIPT)

check-sync:
	$(PYTHON) $(SYNC_SCRIPT) --check

template: install
	$(VENV_PYTHON) $(TEMPLATE_SCRIPT) --output $(REFERENCE_DOC)

docx: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS)

docx-preparatory: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only preparatory-el preparatory-en

docx-preparatory-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only preparatory-el

docx-preparatory-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only preparatory-en

docx-pycharm: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only pycharm-el pycharm-en

docx-pycharm-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only pycharm-el

docx-pycharm-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only pycharm-en

docx-vscode: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only vscode-el vscode-en

docx-vscode-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only vscode-el

docx-vscode-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only vscode-en

docx-local-spark: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only local-spark-el local-spark-en

docx-local-spark-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only local-spark-el

docx-local-spark-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only local-spark-en

docx-lab1-docker: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-docker-el lab1-docker-en

docx-lab1-docker-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-docker-el

docx-lab1-docker-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-docker-en

docx-lab1-k8s: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-k8s-el lab1-k8s-en

docx-lab1-k8s-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-k8s-el

docx-lab1-k8s-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab1-k8s-en

docx-lab2: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab2-el lab2-en

docx-lab2-el: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab2-el

docx-lab2-en: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS) --only lab2-en
