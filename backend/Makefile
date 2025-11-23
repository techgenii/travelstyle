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
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
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
	@echo "  check-updates  - Check for outdated packages"
	@echo "  update-packages - Update all packages to latest versions"
	@echo "  show-versions  - Show current versions of key packages"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  test           - Run all tests with warnings disabled"
	@echo "  test-quick     - Run tests quickly (no coverage)"
	@echo "  test-chat      - Run chat-related tests only"
	@echo "  test-currency  - Run currency-related tests only"
	@echo "  test-orchestrator - Run orchestrator tests only"
	@echo "  test-recommendations - Run recommendations tests only"
	@echo "  test-watch     - Run tests in watch mode"
	@echo "  test-lint      - Run ruff linting"
	@echo "  test-security  - Run bandit security scan"
	@echo ""
	@echo "$(YELLOW)Development (Local Testing):$(NC)"
	@echo "  dev            - Run all dev checks (lint, security, test)"
	@echo "  dev-clean      - Run dev checks with clean output"
	@echo "  run            - Start development server"
	@echo "  clean          - Clean up generated files"
	@echo ""
	@echo "$(YELLOW)Production (CI/CD):$(NC)"
	@echo "  prod           - Run all prod checks (lint, security, test)"
	@echo "  prod-clean     - Run prod checks with clean output"
	@echo ""

# Installation targets
.PHONY: install install-dev
install:
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-test.txt

# Package update targets
.PHONY: check-updates update-packages show-versions
check-updates:
	@echo "$(BLUE)Checking for outdated packages...$(NC)"
	@echo ""
	@if $(PIP) list --outdated 2>/dev/null | grep -q .; then \
		echo "$(YELLOW)Outdated packages found:$(NC)"; \
		$(PIP) list --outdated; \
		echo ""; \
		echo "$(YELLOW)Run 'make update-packages' to update all packages$(NC)"; \
	else \
		echo "$(GREEN)All packages are up to date!$(NC)"; \
	fi

update-packages:
	@echo "$(BLUE)Updating all packages to latest versions...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-test.txt
	@echo "$(GREEN)Packages updated! Run 'make test-quick' to verify everything works.$(NC)"

show-versions:
	@echo "$(BLUE)Current key package versions:$(NC)"
	@echo ""
	@echo "$(YELLOW)Core packages:$(NC)"
	@$(PIP) show supabase fastapi pydantic 2>/dev/null | grep -E "^Name:|^Version:" | paste - - | sed 's/Name: //;s/Version: /: /' || echo "  (not installed)"
	@echo ""
	@echo "$(YELLOW)Authentication:$(NC)"
	@$(PIP) show python-jose passlib 2>/dev/null | grep -E "^Name:|^Version:" | paste - - | sed 's/Name: //;s/Version: /: /' || echo "  (not installed)"
	@echo ""
	@echo "$(YELLOW)AI & External APIs:$(NC)"
	@$(PIP) show openai httpx 2>/dev/null | grep -E "^Name:|^Version:" | paste - - | sed 's/Name: //;s/Version: /: /' || echo "  (not installed)"

# Testing targets (improved with warnings disabled)
.PHONY: test test-quick test-chat test-currency test-orchestrator test-recommendations test-watch test-lint test-security
test: | $(REPORT_DIR)
	@echo "$(BLUE)Running all tests with warnings disabled...$(NC)"
	pytest --tb=short -v --disable-warnings \
		--junitxml=$(REPORT_DIR)/pytest-results.xml \
		--cov=$(APP_DIR) \
		--cov-report=json:$(REPORT_DIR)/pytest-coverage.json \
		--cov-report=xml:$(REPORT_DIR)/pytest-coverage.xml \
		--cov-report=term | tee $(REPORT_DIR)/pytest-coverage.txt || true
	@echo "$(GREEN)Test results generated: $(REPORT_DIR)/pytest-results.xml$(NC)"

test-quick:
	@echo "$(BLUE)Running tests quickly (no coverage)...$(NC)"
	pytest --tb=short -v --disable-warnings

test-chat:
	@echo "$(BLUE)Running chat-related tests...$(NC)"
	pytest tests/test_chat.py -v --disable-warnings

test-currency:
	@echo "$(BLUE)Running currency-related tests...$(NC)"
	pytest tests/test_currency.py -v --disable-warnings

test-orchestrator:
	@echo "$(BLUE)Running orchestrator tests...$(NC)"
	pytest tests/test_orchestrator.py -v --disable-warnings

test-recommendations:
	@echo "$(BLUE)Running recommendations tests...$(NC)"
	pytest tests/test_recommendations.py -v --disable-warnings

test-watch:
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest --tb=short -v --disable-warnings -f

test-lint:
	@echo "$(BLUE)Running ruff linting...$(NC)"
	ruff check $(APP_DIR)

test-security:
	@echo "$(BLUE)Running bandit security scan...$(NC)"
	bandit -r $(APP_DIR)

# Development targets (HTML output)
.PHONY: dev dev-clean dev-lint dev-security dev-test
dev: dev-lint dev-security dev-test clean
	@echo "$(GREEN)All dev checks completed!$(NC)"

dev-clean: dev-lint dev-security test clean
	@echo "$(GREEN)All dev checks completed with clean test output!$(NC)"

dev-lint: | $(REPORT_DIR)
	@echo "$(BLUE)Running ruff linting for CI...$(NC)"
	ruff check $(APP_DIR) --output-format=junit > $(REPORT_DIR)/ruff_junit.xml || true
	@echo "$(GREEN)Ruff JUnit report generated: $(REPORT_DIR)/ruff_junit.xml$(NC)"

dev-security: | $(REPORT_DIR)
	@echo "$(BLUE)Running bandit security scan for CI...$(NC)"
	bandit -r $(APP_DIR) -f json -o $(REPORT_DIR)/bandit_report.json || true
	@echo "$(GREEN)Bandit JSON report generated: $(REPORT_DIR)/bandit_report.json$(NC)"

dev-test: | $(REPORT_DIR)
	@echo "$(BLUE)Running tests for CI...$(NC)"
	pytest --tb=short -v \
		--junitxml=$(REPORT_DIR)/pytest-results.xml \
		--cov=$(APP_DIR) \
		--cov-report=json:$(REPORT_DIR)/pytest-coverage.json \
		--cov-report=xml:$(REPORT_DIR)/pytest-coverage.xml \
		--cov-report=term | tee $(REPORT_DIR)/pytest-coverage.txt || true
	@echo "$(GREEN)Test results generated: $(REPORT_DIR)/pytest-results.xml$(NC)"

# Production targets (JUnit/XML output for CI)
.PHONY: prod prod-clean prod-lint prod-security prod-test
prod: prod-lint prod-security prod-test
	@echo "$(GREEN)All prod checks completed!$(NC)"

prod-clean: prod-lint prod-security test
	@echo "$(GREEN)All prod checks completed with clean test output!$(NC)"

prod-lint: | $(REPORT_DIR)
	@echo "$(BLUE)Running ruff linting for CI...$(NC)"
	ruff check $(APP_DIR) --output-format=junit > $(REPORT_DIR)/ruff_junit.xml || true
	@echo "$(GREEN)Ruff JUnit report generated: $(REPORT_DIR)/ruff_junit.xml$(NC)"

prod-security: | $(REPORT_DIR)
	@echo "$(BLUE)Running bandit security scan for CI...$(NC)"
	bandit -r $(APP_DIR) -f json -o $(REPORT_DIR)/bandit_report.json || true
	@echo "$(GREEN)Bandit JSON report generated: $(REPORT_DIR)/bandit_report.json$(NC)"

prod-test: | $(REPORT_DIR)
	@echo "$(BLUE)Running tests for CI...$(NC)"
	pytest --tb=short -v \
		--junitxml=$(REPORT_DIR)/pytest-results.xml \
		--cov=$(APP_DIR) \
		--cov-report=json:$(REPORT_DIR)/pytest-coverage.json \
		--cov-report=xml:$(REPORT_DIR)/pytest-coverage.xml \
		--cov-report=term | tee $(REPORT_DIR)/pytest-coverage.txt || true
	@echo "$(GREEN)Test results generated: $(REPORT_DIR)/pytest-results.xml$(NC)"

# Development server
.PHONY: run
run:
	@echo "$(GREEN)Starting development server...$(NC)"
	@echo "$(YELLOW)Server will be available at: http://$(HOST):$(PORT)$(NC)"
	uvicorn $(APP_DIR).travelstyle:travelstyle_app --reload --host $(HOST) --port $(PORT)

# Cleanup (dev only)
.PHONY: clean clean-reports clean-cache
clean: clean-reports clean-cache
	@echo "$(YELLOW)Cleanup completed$(NC)"

clean-reports:
	@echo "$(YELLOW)Cleaning reports...$(NC)"
	rm -rf $(REPORT_DIR)
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
