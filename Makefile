# Executables (local)
DOCKER_COMPOSE = docker compose

# Docker containers
APP_CONTAINER = $(DOCKER_COMPOSE) run --rm app python seigaiha.py

# Misc
.DEFAULT_GOAL : help
.PHONY : help up down seigaiha

help:
	@printf "\033[33m%s:\033[0m\n" 'Available commands'
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-30s\033[0m %s\n", $$1, $$2}'

up: ## Up the application
	$(DOCKER_COMPOSE) up -d --build

down: ## Down and remove-orphans
	$(DOCKER_COMPOSE) down --remove-orphans

seigaiha: ## Run seigaiha with specified preset: make seigaiha preset="preset/pattern_preset.json" output="output"
	$(APP_CONTAINER) -p $(preset) -o $(output)