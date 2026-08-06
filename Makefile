# ==============================================================================
# AI Documents Analyzer — Monorepository
# ==============================================================================
# Using: make <command>
# Examples:
#   make help         — show commands list
#   make up           — launch core services
#   make dev          — launch services in dev mode
#   make test         — launch all tests
# ==============================================================================

# Variables
COMPOSE := docker compose
COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env

# Color Schema
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

.DEFAULT_GOAL := help

# ==============================================================================
# Help
# ==============================================================================

.PHONY: help
help: ## Show commands list
	@echo ""
	@echo "$(GREEN)AI Documents Analyzer — Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# Launch services
# ==============================================================================

.PHONY: up
up: ## Launch core services (backend, frontend, postgres, chromadb)
	@echo "$(GREEN)Launch core services...$(NC)"
	$(COMPOSE) --profile core up -d

.PHONY: up-all
up-all: ## Launch ALL services (including observability and admin tools)
	@echo "$(GREEN)Launch ALL services...$(NC)"
	$(COMPOSE) --profile all up -d

.PHONY: up-observability
up-observability: ## Launch observability stack (loki, promtail, grafana)
	@echo "$(GREEN)Launch observability stack...$(NC)"
	$(COMPOSE) --profile observability up -d

.PHONY: up-admin
up-admin: ## Launch admin tools (pgAdmin)
	@echo "$(GREEN)Launch admin tools...$(NC)"
	$(COMPOSE) --profile admin up -d

.PHONY: dev
dev: ## Launch in dev mode (with backend hot-reload)
	@echo "$(GREN)Launch in dev mode...$(NC)"
	$(COMPOSE) --profile core up -d --build
	@echo "$(GREEN)Services are running:$(NC)"
	@echo "  - Frontend:  http://localhost:80"
	@echo "  - Backend:   http://localhost:8000"
	@echo "  - API Docs:  http://localhost:8000/docs"
	@echo "  - Backend ReDoc: http://localhost:8000/redoc"
	@echo "  - Postgres:  localhost:5432"
	@echo "  - ChromaDB:  http://localhost:8001"

.PHONY: down
down: ## Stop core services
	@echo "$(YELLOW)Stop core services...$(NC)"
	$(COMPOSE) --profile core down

.PHONY: down-all
down-all: ## Stop ALL services
	@echo "$(YELLOW)Stop ALL services...$(NC)"
	$(COMPOSE) --profile all down

.PHONY: down-observability
down-observability: ## Stop observability services
	@echo "$(YELLOW)Stop observability services...$(NC)"
	$(COMPOSE) --profile observability down

.PHONY: down-admin
down-admin: ## Stop admin tools
	@echo "$(YELLOW)Stop admin tools...$(NC)"
	$(COMPOSE) --profile admin down

.PHONY: restart
restart: down up ## Restart core services

.PHONY: restart-all
restart-all: down up-all ## Restart ALL services

.PHONY: restart-observability
restart-observability: down up-all ## Restart observability services

.PHONY: restart-admin
restart-admin: down up-admin ## Restart admin services

# ==============================================================================
# Build
# ==============================================================================

.PHONY: build
build: ## Build all Docker images
	@echo "$(GREEN)Build all Docker images...$(NC)"
	$(COMPOSE) --profile all build

.PHONY: build-backend
build-backend: ## Build backend Docker image
	@echo "$(GREEN)Build backend Docker image...$(NC)"
	$(COMPOSE) build doc-analyzer-backend

.PHONY: build-frontend
build-frontend: ## Build frontend Docker image
	@echo "$(GREEN)Build frontend Docker image...$(NC)"
	$(COMPOSE) build doc-analyzer-frontend

.PHONY: build-no-cache
build-no-cache: ## Build all Docker images without cache
	@echo "$(GREEN)Build all Docker images without cache...$(NC)"
	$(COMPOSE) --profile all build --no-cache

# ==============================================================================
# Shared
# ==============================================================================

.PHONY: install-shared
install-shared: ## Install shared packages locally (dev)
	@echo "$(GREEN)Install shared packages in editable mode...$(NC)"
	pip install -e shared/agent-enums
	pip install -e shared/db-repository
	pip install -e shared/rag-client
	@echo "$(GREEN)Shared packages installed$(NC)"

.PHONY: build-shared
build-shared: ## Build shared wheel-packages
	@echo "$(GREEN)Build shared wheel-packages...$(NC)"
	@for pkg in agent-enums db-repository rag-client; do \
		echo "  Building $$pkg..."; \
		cd shared/$$pkg && python -m build --wheel && cd ../..; \
	done
	@echo "$(GREEN)Shared packages built$(NC)"

# ==============================================================================
# Testing
# ==============================================================================

.PHONY: test
test: ## Launch all backend tests
	@echo "$(GREEN)Launch all backend tests...$(NC)"
	cd services/doc-analyzer-backend && pytest tests/ -v

.PHONY: test-packages
test-packages: ## Launch all shared packages tests
	@echo "$(GREEN)Launch all shared packages tests...$(NC)"
	@for pkg in agent-enums db-repository rag-client; do \
		echo "  Testing $$pkg..."; \
		cd shared/$$pkg && pytest tests/ -v && cd ../..; \
	done

.PHONY: test-coverage
test-coverage: ## Launch all backend tests with coverage
	@echo "$(GREEN)Launch all backend tests with coverage...$(NC)"
	cd services/doc-analyzer-backend && pytest tests/ --cov=. --cov-report=html

# ==============================================================================
# Status
# ==============================================================================

.PHONY: ps
ps: ## Status of all containers
	$(COMPOSE) --profile all ps

# ==============================================================================
# Logs and Debug
# ==============================================================================

.PHONY: logs
logs: ## Show all services logs
	$(COMPOSE) --profile all logs -f

.PHONY: logs-backend
logs-backend: ## Show backend logs
	$(COMPOSE) logs -f doc-analyzer-backend

.PHONY: logs-frontend
logs-frontend: ## Show frontend logs
	$(COMPOSE) logs -f doc-analyzer-frontend

# ==============================================================================
# Databases
# ==============================================================================

.PHONY: db-shell
db-shell: ## Connect to PostgreSQL shell
	$(COMPOSE) exec doc-analyzer-postgres psql -U $${DB_USER:-agent} -d $${DB_NAME:-agent_prompts}

.PHONY: db-seed
db-seed: ## Seed database with initial data
	@echo "$(YELLOW)Seed database...$(NC)"
	$(COMPOSE) exec doc-analyzer-backend python -m scripts.init_prompts

.PHONY: chroma-shell
chroma-shell: ## Connect to ChromaDB
	@echo "$(GREEN)ChromaDB UI: http://localhost:8001$(NC)"

# ==============================================================================
# Cleanup
# ==============================================================================

.PHONY: clean-build-cache
clean-build-cache: ## Docker build cache cleanup
	@echo "$(YELLOW)Docker build cache cleanup...$(NC)"
	docker builder prune -a
	@echo "$(GREEN)Docker build cache cleaned up$(NC)"

.PHONY: clean-system-cache
clean-system-cache: ## Docker system cache cleanup
	@echo "$(YELLOW)Docker system cache cleanup...$(NC)"
	docker system prune -f
	@echo "$(GREEN)Docker system cache cleaned up$(NC)"

.PHONY: clean-cache
clean-cache: clean-build-cache clean-system-cache ## Docker cache cleanup

.PHONY: clean
clean: ## Temporary files and cache cleanup
	@echo "$(YELLOW)Temporary files and cache cleanup...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find shared -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find shared -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find shared -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed$(NC)"

.PHONY: clean-images
clean-images: ## Docker images cleanup
	@echo "$(YELLOW)Docker images cleanup...$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ $$confirm = "y" ] || exit 1
	$(COMPOSE) --profile all down --rmi local --remove-orphans
	@echo "$(GREEN)Docker images cleanup$(NC)"

.PHONY: clean-docker-full
clean-docker-full: ## Docker images, volumes, network cleanup
	@echo "$(RED)ALL Docker images, volumes, network cleanup...$(NC)"
	@read -p "WARNING: data volumes will be deleted! Are you sure? [y/N] " confirm && [ $$confirm = "y" ] || exit 1
	$(COMPOSE) --profile all down -v --rmi local --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Docker cleaned up$(NC)"

.PHONY: clean-all
clean-all: clean clean-docker ## Full cleanup (files, cache, Docker images)

# ==============================================================================
# Environment configuration
# ==============================================================================

.PHONY: env-init
env-init: ## Create .env from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN).env file created from .env.example$(NC)"; \
		echo "$(YELLOW)Change default passwords!$(NC)"; \
	else \
		echo "$(YELLOW)File .env already exists$(NC)"; \
	fi

.PHONY: check-env
check-env: ## Check .env exists
	@echo "$(GREEN)Проверка .env...$(NC)"
	@test -f .env || (echo "$(RED).env not found, run: 'make env-init'$(NC)" && exit 1)
	@echo "$(GREEN).env exists$(NC)"

# ==============================================================================
# Linters and Formatters
# ==============================================================================

.PHONY: lint
lint: ## Launch linters (ruff, mypy)
	@echo "$(GREEN)Launch linters...$(NC)"
	cd services/doc-analyzer-backend && ruff check .
	cd services/doc-analyzer-backend && mypy .

.PHONY: format
format: ## Format code
	@echo "$(GREEN)Format code...$(NC)"
	cd services/doc-analyzer-backend && ruff format .
	cd services/doc-analyzer-backend && ruff check --fix .

# ==============================================================================
# Documentation
# ==============================================================================

.PHONY: docs
docs: ## Documentation
	@echo "$(GREEN)Documentation...$(NC)"
	@echo "  Backend API: http://localhost:8000/docs"
	@echo "  Backend ReDoc: http://localhost:8000/redoc"

# ==============================================================================
# Utilities
# ==============================================================================

.PHONY: shell-backend
shell-backend: ## Connect to backend container shell
	$(COMPOSE) exec doc-analyzer-backend bash

.PHONY: shell-frontend
shell-frontend: ## Connect to frontend container shell
	$(COMPOSE) exec doc-analyzer-frontend sh

.PHONY: status
status: ps ## Status of all containers (ps alias)

.PHONY: info
info: ## Show project info
	@echo ""
	@echo "$(GREEN)AI Documents Analyzer$(NC)"
	@echo "================================"
	@echo "  Version: 1.0.0"
	@echo "  Python: 3.11"
	@echo "  Node: 20"
	@echo ""
	@echo "$(GREEN)Shared packages:$(NC)"
	@echo "  - agent-enums       (v1.0.0)"
	@echo "  - db-repository     (v1.0.0)"
	@echo "  - rag-client        (v1.0.0)"
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@echo "  - Frontend:  http://localhost:80"
	@echo "  - Backend:   http://localhost:8000"
	@echo "  - Postgres:  http://localhost:5432"
	@echo "  - ChromaDB:  http://localhost:8001"
	@echo "  - pgAdmin:   http://localhost:5050"
	@echo "  - Grafana:   http://localhost:3000"
	@echo ""