.DEFAULT_GOAL := check

ifeq ($(OS),Windows_NT)
VENV_PYTHON := .venv/Scripts/python.exe
else
VENV_PYTHON := .venv/bin/python
endif

PYTHON ?= $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),python)
SYSTEM_PYTHON ?= python

.PHONY: criar-ambiente-virtual ativar-ambiente-virtual install lint test check

criar-ambiente-virtual:
	$(SYSTEM_PYTHON) -m venv .venv

ativar-ambiente-virtual:
	@echo "PowerShell: .\.venv\Scripts\Activate.ps1"
	@echo "Git Bash: source .venv/Scripts/activate"

install:
	$(PYTHON) -m pip install -r server/requirements.txt

lint:
	$(PYTHON) -m flake8 server tests

test:
	$(PYTHON) -m pytest

check: lint test
