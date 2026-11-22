.DEFAULT_GOAL := check

ifeq ($(OS),Windows_NT)
VENV_PYTHON := .venv/Scripts/python.exe
else
VENV_PYTHON := .venv/bin/python
endif

PYTHON ?= $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),python)
SYSTEM_PYTHON ?= python

.PHONY: criar-ambiente-virtual ativar-ambiente-virtual install lint test check backend front front-test demo-data

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

check: lint test front-test

backend:
	$(PYTHON) -m flask --app server.app:create_app run --debug

front:
	node front/dev_server.js

front-test:
	cd front && node --test

demo-data:
	$(PYTHON) -m flask --app server.app:create_app criar-dados-demo
