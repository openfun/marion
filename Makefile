# /!\ /!\ /!\ /!\ /!\ /!\ /!\ DISCLAIMER /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# This Makefile is only meant to be used for DEVELOPMENT purpose as we are
# changing the user id that will run in the container.
#
# PLEASE DO NOT USE IT FOR YOUR CI/PRODUCTION/WHATEVER...
#
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# Note to developpers:
#
# While editing this file, please respect the following statements:
#
# 1. Every variable should be defined in the ad hoc VARIABLES section with a
#    relevant subsection
# 2. Every new rule should be defined in the ad hoc RULES section with a
#    relevant subsection depending on the targeted service
# 3. Rules should be sorted alphabetically within their section
# 4. When a rule has multiple dependencies, you should:
#    - duplicate the rule name to add the help string (if required)
#    - write one dependency per line to increase readability and diffs
# 5. .PHONY rule statement should be written after the corresponding rule
# ==============================================================================
# VARIABLES

# -- Database
DB_HOST              = postgresql
DB_PORT              = 5432

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker-compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_APP      = $(COMPOSE_RUN) marion
COMPOSE_TEST_RUN     = $(COMPOSE) run --rm -e DJANGO_CONFIGURATION=Test -e HOME=/tmp -w /usr/local/src/marion
COMPOSE_TEST_RUN_APP = $(COMPOSE_TEST_RUN) marion
MANAGE               = $(COMPOSE_RUN_APP) python manage.py
MANAGE_HOWARD        = $(COMPOSE) run --rm --workdir /usr/local/src/howard/howard marion /app/manage.py
WAIT_DB              = @$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s
MKDOCS               = $(COMPOSE_RUN) mkdocs

# ==============================================================================
# RULES

default: help

# -- Project

bootstrap: ## prepare Docker images for the project
bootstrap: \
 	data/media \
	build \
	migrate
.PHONY: bootstrap

data/media:
	@mkdir -p data/media

# -- Docker/compose
build: ## build the app container
	@$(COMPOSE) build marion
.PHONY: build

docs-build: ## build documentation site
	@$(MKDOCS) build
.PHONY: docs-build

docs-deploy: ## deploy documentation site
	@$(MKDOCS) gh-deploy
.PHONY: docs-deploy

docs-serve: ## run mkdocs live server
	@$(COMPOSE_RUN) --publish=8001:8001 mkdocs serve --dev-addr 0.0.0.0:8001
.PHONY: docs-serve

down: ## stop and remove containers, networks, images, and volumes
	@$(COMPOSE) down
.PHONY: down

logs: ## display app logs (follow mode)
	@$(COMPOSE) logs -f marion
.PHONY: logs

migrate: ## run database migrations
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) migrate
.PHONY: migrate

run: ## start the development server using Docker
	@$(COMPOSE) up -d
	@echo "Wait for postgresql to be up..."
	@$(WAIT_DB)
.PHONY: run

status: ## an alias for "docker-compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop the development server using Docker
	@$(COMPOSE) stop
.PHONY: stop

i18n-generate: ## generate .pot files used for i18n
	@$(MANAGE_HOWARD) makemessages -a --keep-pot
.PHONY: i18n-generate

i18n-compile: ## compile translations
	@$(MANAGE_HOWARD) compilemessages --ignore="venv/**/*"
.PHONY: i18n-compile

# -- Linters
# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint back-end python sources
lint: \
  lint-isort \
  lint-black \
  lint-flake8 \
  lint-bandit \
  lint-pylint
.PHONY: lint

lint-bandit: ## lint back-end python sources with bandit
	@echo 'lint:bandit started…'
	@$(COMPOSE_TEST_RUN_APP) bandit -c .banditrc -r . /usr/local/src/howard
.PHONY: lint-bandit

lint-black: ## lint back-end python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_TEST_RUN_APP) black . /usr/local/src/howard
.PHONY: lint-black

lint-flake8: ## lint back-end python sources with flake8
	@echo 'lint:flake8 started…'
	@$(COMPOSE_TEST_RUN_APP) flake8 . /usr/local/src/howard
.PHONY: lint-flake8

lint-isort: ## automatically re-arrange python imports in back-end code base
	@echo 'lint:isort started…'
	@$(COMPOSE_TEST_RUN_APP) isort --atomic . /usr/local/src/howard
.PHONY: lint-isort

lint-pylint: ## lint back-end python sources with pylint
	@echo 'lint:pylint started…'
	bin/pylint marion howard
.PHONY: lint-pylint

# -- Tests
test: ## perform backend tests
	bin/pytest marion /usr/local/src/howard --cov=howard
.PHONY: test

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
