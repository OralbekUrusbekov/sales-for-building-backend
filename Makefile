.DEFAULT_GOAL := help
COMPOSE := docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Build & start the whole stack
	$(COMPOSE) up --build -d

down: ## Stop the stack
	$(COMPOSE) down

nuke: ## Stop the stack and drop volumes (wipes the DB)
	$(COMPOSE) down -v

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

api-logs: ## Tail API logs
	$(COMPOSE) logs -f api

ps: ## Show service status
	$(COMPOSE) ps

shell: ## Open a shell inside the API container
	$(COMPOSE) exec api bash

psql: ## Open psql inside the DB container
	$(COMPOSE) exec db psql -U remonthub -d remonthub

migrate: ## Apply migrations
	$(COMPOSE) exec api alembic upgrade head

revision: ## Autogenerate a migration: make revision m="add table"
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(m)"

seed: ## Re-run the seed script
	$(COMPOSE) exec api python -m app.seed

.PHONY: help up down nuke logs api-logs ps shell psql migrate revision seed
