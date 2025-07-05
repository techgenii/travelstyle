# Makefile for TravelStyle AI Backend

.PHONY: lint security check install test run

install:
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt

lint:
	pylint app/

lint-json:
	pylint app/ -f json -o pylint_report.json

lint-parseable:
	pylint app/ -f parseable

lint-colorized:
	pylint app/ -f colorized

lint-github:
	pylint app/ -f github

security:
	bandit -r app/

security-json:
	bandit -r app/ -f json -o bandit_report.json

security-html:
	bandit -r app/ -f html -o bandit_report.html

security-high:
	bandit -r app/ -lll

security-github:
	bandit -r app/ -f json -o bandit_report.json

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

test-fast:
	pytest -x -v

test-github:
	pytest --tb=short -v

check: lint security test

check-cov: lint security-json test-cov

check-github: lint-github security-github test-github

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 