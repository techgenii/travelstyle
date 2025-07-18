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
	@echo ""
	@echo "$(YELLOW)Development (Local Testing):$(NC)"
	@echo "  dev            - Run all dev checks (lint, security, test)"
	@echo "  run            - Start development server"
	@echo "  clean          - Clean up generated files"
	@echo ""
	@echo "$(YELLOW)Production (CI/CD):$(NC)"
	@echo "  prod           - Run all prod checks (lint, security, test)"
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

# Development targets (HTML output)
.PHONY: dev dev-lint dev-security dev-test
dev: dev-lint dev-security dev-test clean
	@echo "$(GREEN)All dev checks completed!$(NC)"

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
.PHONY: prod prod-lint prod-security prod-test
prod: prod-lint prod-security prod-test
	@echo "$(GREEN)All prod checks completed!$(NC)"

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
	uvicorn $(APP_DIR).main:app --reload --host $(HOST) --port $(PORT)

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
