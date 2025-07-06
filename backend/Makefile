# Makefile for TravelStyle AI Backend

# Configuration
PYTHON := python
PIP := pip
APP_DIR := app
REPORT_DIR := reports
COVERAGE_MIN := 80
HOST := 127.0.0.1
PORT := 8000

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Create reports directory
$(REPORT_DIR):
	@mkdir -p $(REPORT_DIR)

# Help target
.PHONY: help
help:
	@echo "$(BLUE)TravelStyle AI Backend - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  install-all    - Install all dependencies"
	@echo ""
	@echo "$(YELLOW)Quality Checks:$(NC)"
	@echo "  lint           - Run pylint with colorized output"
	@echo "  security       - Run bandit security scan"
	@echo "  test           - Run pytest with coverage"
	@echo "  check          - Run all quality checks"
	@echo ""
	@echo "$(YELLOW)CI/CD Targets:$(NC)"
	@echo "  ci-lint        - Run lint for CI (JSON + GitHub format)"
	@echo "  ci-security    - Run security scan for CI (JSON + HTML)"
	@echo "  ci-test        - Run tests for CI (XML + coverage)"
	@echo "  ci-check       - Run all CI checks"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  run            - Start development server"
	@echo "  test-fast      - Run tests with fail-fast"
	@echo "  test-watch     - Run tests in watch mode"
	@echo "  clean          - Clean up generated files"
	@echo ""

# Installation targets
.PHONY: install install-dev install-all
install:
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev:
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-test.txt

install-all: install install-dev
	@echo "$(GREEN)All dependencies installed successfully!$(NC)"

# Linting targets
.PHONY: lint lint-json lint-parseable lint-colorized lint-github ci-lint
lint: lint-colorized

lint-json: | $(REPORT_DIR)
	@echo "$(BLUE)Running pylint (JSON format)...$(NC)"
	pylint $(APP_DIR) -f json > $(REPORT_DIR)/pylint_report.json || true
	@echo "$(GREEN)Pylint JSON report generated: $(REPORT_DIR)/pylint_report.json$(NC)"

lint-parseable:
	@echo "$(BLUE)Running pylint (parseable format)...$(NC)"
	pylint $(APP_DIR) -f parseable

lint-colorized:
	@echo "$(BLUE)Running pylint (colorized format)...$(NC)"
	pylint $(APP_DIR) -f colorized

lint-github:
	@echo "$(BLUE)Running pylint (GitHub format)...$(NC)"
	pylint $(APP_DIR) -f github

ci-lint: | $(REPORT_DIR)
	@echo "$(BLUE)Running CI lint checks...$(NC)"
	pylint $(APP_DIR) -f github || true
	pylint $(APP_DIR) -f json > $(REPORT_DIR)/pylint_report.json || true
	@if command -v pylint >/dev/null 2>&1; then \
		pylint $(APP_DIR) --output-format=html > $(REPORT_DIR)/pylint_report.html || true; \
	fi
	# Extract score to a simple text file
	@pylint $(APP_DIR) 2>/dev/null | grep "Your code has been rated at" | grep -o '[0-9]\+\.[0-9]\+' > $(REPORT_DIR)/pylint_score.txt || echo "0.0" > $(REPORT_DIR)/pylint_score.txt
	@echo "$(GREEN)CI lint checks completed$(NC)"

# Security targets
.PHONY: security security-json security-html security-high security-github ci-security
security:
	@echo "$(BLUE)Running bandit security scan...$(NC)"
	bandit -r $(APP_DIR)

security-json: | $(REPORT_DIR)
	@echo "$(BLUE)Running bandit (JSON format)...$(NC)"
	bandit -r $(APP_DIR) -f json -o $(REPORT_DIR)/bandit_report.json || true
	@echo "$(GREEN)Bandit JSON report generated: $(REPORT_DIR)/bandit_report.json$(NC)"

security-html: | $(REPORT_DIR)
	@echo "$(BLUE)Running bandit (HTML format)...$(NC)"
	bandit -r $(APP_DIR) -f html -o $(REPORT_DIR)/bandit_report.html || true
	@echo "$(GREEN)Bandit HTML report generated: $(REPORT_DIR)/bandit_report.html$(NC)"

security-high:
	@echo "$(BLUE)Running bandit (high severity only)...$(NC)"
	bandit -r $(APP_DIR) -lll

security-github: | $(REPORT_DIR)
	@echo "$(BLUE)Running bandit (GitHub format)...$(NC)"
	bandit -r $(APP_DIR) -f json -o $(REPORT_DIR)/bandit_report.json || true

ci-security: | $(REPORT_DIR)
	@echo "$(BLUE)Running CI security checks...$(NC)"
	bandit -r $(APP_DIR) -f json -o $(REPORT_DIR)/bandit_report.json || true
	bandit -r $(APP_DIR) -f html -o $(REPORT_DIR)/bandit_report.html || true
	@echo "$(GREEN)CI security checks completed$(NC)"

# Testing targets
.PHONY: test test-cov test-cov-json test-fast test-github test-watch ci-test
test:
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v

test-cov: | $(REPORT_DIR)
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest --cov=$(APP_DIR) \
		--cov-report=html:$(REPORT_DIR)/htmlcov \
		--cov-report=term \
		--cov-report=json:$(REPORT_DIR)/coverage.json \
		--cov-fail-under=$(COVERAGE_MIN)
	@echo "$(GREEN)Coverage report generated: $(REPORT_DIR)/htmlcov/index.html$(NC)"

test-cov-json: | $(REPORT_DIR)
	@echo "$(BLUE)Running tests with JSON coverage...$(NC)"
	pytest --cov=$(APP_DIR) \
		--cov-report=json:$(REPORT_DIR)/coverage.json \
		--cov-report=term

test-fast:
	@echo "$(BLUE)Running tests (fail-fast)...$(NC)"
	pytest -x -v

test-github: | $(REPORT_DIR)
	@echo "$(BLUE)Running tests (GitHub format)...$(NC)"
	pytest --tb=short -v \
		--junitxml=$(REPORT_DIR)/test-results.xml

test-watch:
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch

ci-test: | $(REPORT_DIR)
	@echo "$(BLUE)Running CI tests...$(NC)"
	pytest --tb=short -v \
		--junitxml=$(REPORT_DIR)/test-results.xml \
		--cov=$(APP_DIR) \
		--cov-report=json:$(REPORT_DIR)/coverage.json \
		--cov-report=term \
		--cov-report=html:$(REPORT_DIR)/htmlcov || true
	@echo "$(GREEN)CI tests completed$(NC)"

# Combined check targets
.PHONY: check check-cov check-cov-json check-github ci-check
check: lint security test
	@echo "$(GREEN)All quality checks completed!$(NC)"

check-cov: lint-colorized security-html test-cov
	@echo "$(GREEN)All quality checks with coverage completed!$(NC)"

check-cov-json: lint-json security-json test-cov-json
	@echo "$(GREEN)All quality checks with JSON output completed!$(NC)"

check-github: lint-github security-github test-github
	@echo "$(GREEN)All GitHub-formatted checks completed!$(NC)"

ci-check: ci-lint ci-security ci-test
	@echo "$(GREEN)All CI checks completed!$(NC)"

# Development targets
.PHONY: run run-prod dev
run: dev

dev:
	@echo "$(GREEN)Starting development server...$(NC)"
	@echo "$(YELLOW)Server will be available at: http://$(HOST):$(PORT)$(NC)"
	uvicorn $(APP_DIR).main:app --reload --host $(HOST) --port $(PORT)

# Utility targets
.PHONY: clean clean-reports clean-cache clean-all
clean: clean-reports clean-cache

clean-reports:
	@echo "$(YELLOW)Cleaning reports...$(NC)"
	rm -rf $(REPORT_DIR)
	rm -f pylint_report.json pylint_report.html
	rm -f bandit_report.json bandit_report.html
	rm -f coverage.json test-results.xml
	rm -rf htmlcov
	rm -f .coverage*

clean-cache:
	@echo "$(YELLOW)Cleaning cache...$(NC)"
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean
	@echo "$(YELLOW)Deep cleaning...$(NC)"
	rm -rf venv
	rm -rf .venv
	rm -rf node_modules

# Version and info targets
.PHONY: info version
info:
	@echo "$(BLUE)TravelStyle AI Backend Information$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "App directory: $(APP_DIR)"
	@echo "Report directory: $(REPORT_DIR)"
	@echo "Coverage minimum: $(COVERAGE_MIN)%"

version:
	@echo "$(shell $(PYTHON) --version)"