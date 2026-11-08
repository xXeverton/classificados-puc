.DEFAULT_GOAL := check

PYTHON ?= python

.PHONY: install lint test check

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m flake8

test:
	$(PYTHON) -m pytest

check: lint test
