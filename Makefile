.PHONY: help install run test lint clean migrate messages docker-build docker-up docker-down

# Variables
PYTHON = python
PIP = pip
MANAGE = $(PYTHON) manage.py
DOCKER_COMPOSE = docker-compose

help:
	@echo "Available commands:"
	@echo "install      - Install dependencies"
	@echo "run         - Run development server"
	@echo "test        - Run tests"
	@echo "lint        - Run code quality checks"
	@echo "clean       - Remove generated files"
	@echo "migrate     - Run database migrations"
	@echo "messages    - Update translation files"
	@echo "docker-build- Build Docker images"
	@echo "docker-up   - Start Docker containers"
	@echo "docker-down - Stop Docker containers"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-local.txt

run:
	$(MANAGE) runserver 0.0.0.0:8000

test:
	pytest
	$(MANAGE) test

lint:
	black .
	isort .
	flake8 .
	mypy .

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".tox" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache
	rm -rf .mypy_cache

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

messages:
	$(MANAGE) makemessages -l en
	$(MANAGE) makemessages -l es
	$(MANAGE) compilemessages

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

setup-dev: install migrate
	$(MANAGE) loaddata fixtures/sample_data.json
	$(MANAGE) createsuperuser

collect-static:
	$(MANAGE) collectstatic --noinput

check:
	$(MANAGE) check --deploy
	$(MANAGE) validate_templates
	$(MANAGE) check_permissions
	$(MANAGE) check_urls

backup:
	$(MANAGE) dumpdata --exclude auth.permission --exclude contenttypes > fixtures/backup_$(shell date +%Y%m%d_%H%M%S).json

restore:
	$(MANAGE) loaddata $(filter-out $@,$(MAKECMDGOALS))

shell:
	$(MANAGE) shell_plus --ipython

coverage:
	coverage run -m pytest
	coverage report
	coverage html

requirements:
	pip-compile requirements.in
	pip-compile requirements-local.in

update-requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-local.in

security-check:
	safety check
	bandit -r .

format:
	black .
	isort .

validate:
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-check
	$(MAKE) check

# Docker development commands
docker-dev:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

docker-test:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

docker-logs:
	$(DOCKER_COMPOSE) logs -f

docker-shell:
	$(DOCKER_COMPOSE) exec web bash

docker-django-shell:
	$(DOCKER_COMPOSE) exec web python manage.py shell_plus

docker-db-shell:
	$(DOCKER_COMPOSE) exec db psql -U nexus -d nexus

docker-redis-shell:
	$(DOCKER_COMPOSE) exec redis redis-cli

# Production commands
prod-deploy:
	git pull origin main
	$(MAKE) docker-build
	$(MAKE) docker-up
	$(MAKE) collect-static
	$(MAKE) migrate

prod-backup:
	$(MAKE) backup
	aws s3 cp fixtures/backup_$(shell date +%Y%m%d_%H%M%S).json s3://nexus-backups/

# Monitoring commands
check-logs:
	tail -f logs/django.log

monitor-celery:
	celery -A nexus flower

# Database commands
createdb:
	createdb nexus

dropdb:
	dropdb nexus

# Documentation commands
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8001

# Default target
all: install migrate run
