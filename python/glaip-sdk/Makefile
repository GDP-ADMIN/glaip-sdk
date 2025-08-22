#!/usr/bin/env bash
# =============================================================================
# AI Agent Platform SDK - Makefile
# =============================================================================

# Force bash shell
SHELL := /bin/bash

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Robust .env loader (handles quotes, spaces, Windows line endings)
define load_env
	@if [ -f .env ]; then \
		echo "📋 Loading environment variables from .env..."; \
		set -a; . .env; set +a; \
		echo "✅ .env loaded"; \
	else \
		echo "⚠️  No .env found; using current environment"; \
	fi
endef

# Colored echo functions
define echo_info
	@echo "$(BLUE)$(1)$(NC)"
endef

define echo_success
	@echo "$(GREEN)$(1)$(NC)"
endef

define echo_warning
	@echo "$(YELLOW)$(1)$(NC)"
endef

define echo_error
	@echo "$(RED)$(1)$(NC)"
endef

.PHONY: help
help:
	@echo "🚀 AI Agent Platform SDK - Available Commands"
	@echo ""
	@echo "🔧 Development:"
	@echo "  install                   Install dependencies"
	@echo "  pre-commit                Run pre-commit hooks on staged files"
	@echo "  pre-commit-all            Run pre-commit hooks on all files"
	@echo "  test-with-checks          Run tests + pre-commit checks"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test                      Run all tests with coverage (parallel)"
	@echo "  test-unit                 Run unit tests only"
	@echo "  test-integration          Run integration tests only"
	@echo ""
	@echo "🚀 Demos:"
	@echo "  demo-sdk                  Run Python SDK demo"
	@echo "  demo-cli                  Run CLI demo"
	@echo "  demo-all                  Run both demos"
	@echo ""
	@echo "🔍 Status:"
	@echo "  check-backend             Check if backend is running"
	@echo ""
	@echo "🧹 Utilities:"
	@echo "  clean                     Clean Python artifacts"
	@echo "  clean-all                 Deep clean including coverage"

.PHONY: install
install:
	$(call echo_info,📦 Installing dependencies...)
	@poetry install --with dev
	$(call echo_success,✅ Dependencies installed!)

.PHONY: test
test: clean
	$(call echo_info,🧪 Running all tests in parallel...)
	$(call load_env)
	@poetry run python -m pytest tests/ -n auto --cov=glaip_sdk --cov-report=term-missing --cov-fail-under=90

.PHONY: test-unit
test-unit: clean
	$(call echo_info,🧪 Running unit tests...)
	@poetry run python -m pytest tests/unit/ -v --cov=glaip_sdk --cov-report=term-missing --cov-fail-under=90

.PHONY: test-integration
test-integration: clean
	$(call echo_info,🧪 Running integration tests...)
	$(call load_env)
	@poetry run python -m pytest tests/integration/ -v --cov=glaip_sdk --cov-report=term-missing --cov-fail-under=90

.PHONY: test-with-checks
test-with-checks: pre-commit test
	$(call echo_info,🧪 Running tests with pre-commit checks...)
	$(call echo_success,✅ Tests and pre-commit checks completed!)







.PHONY: demo-sdk
demo-sdk:
	$(call echo_info,🚀 Running Python SDK Demo...)
	$(call load_env)
	@export AIP_API_KEY="secretkey" && export AIP_API_URL="http://localhost:8000" && poetry run python examples/demo/demo_sdk_workflow.py
	$(call echo_success,✅ SDK Demo completed!)

.PHONY: demo-cli
demo-cli:
	$(call echo_info,🚀 Running CLI Demo...)
	$(call load_env)
	@export AIP_API_KEY="secretkey" && export AIP_API_URL="http://localhost:8000" && poetry run python examples/demo/demo_cli_workflow.py
	$(call echo_success,✅ CLI Demo completed!)

.PHONY: demo-all
demo-all:
	$(call echo_info,🚀 Running All Demos...)
	$(call load_env)
	@export AIP_API_KEY="secretkey" && export AIP_API_URL="http://localhost:8000" && poetry run python examples/demo/demo_sdk_workflow.py && poetry run python examples/demo/demo_cli_workflow.py
	$(call echo_success,✅ All Demos completed!)

.PHONY: check-backend
check-backend:
	$(call echo_info,🔍 Checking backend health with retry...)
	@curl -fsS --retry 5 --retry-delay 1 --retry-connrefused \
	     --max-time 3 "http://localhost:8000/health-check" >/dev/null \
	&& echo "✅ Backend is running" || (echo "❌ Backend not reachable at http://localhost:8000"; exit 1)

.PHONY: pre-commit
pre-commit:
	$(call echo_info,🔍 Running pre-commit hooks on staged files...)
	@poetry run pre-commit run
	$(call echo_success,✅ Pre-commit checks passed!)

.PHONY: pre-commit-all
pre-commit-all:
	$(call echo_info,🔍 Running pre-commit hooks on all files...)
	@poetry run pre-commit run --all-files
	$(call echo_success,✅ Pre-commit checks passed!)

.PHONY: clean
clean:
	$(call echo_info,🧹 Cleaning Python artifacts...)
	@rm -f .coverage .coverage.*
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	$(call echo_success,✅ Cleanup completed!)

.PHONY: clean-all
clean-all: clean
	$(call echo_info,🧹 Deep cleaning...)
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	$(call echo_success,✅ Deep cleanup completed!)
