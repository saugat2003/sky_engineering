# Django Makefile

PYTHON=python3
MANAGE=$(PYTHON) manage.py

# Default target
help:
	@echo "Available commands:"
	@echo "  make run        - Run development server"
	@echo "  make migrate    - Apply migrations"
	@echo "  make makemigrations - Create migrations"
	@echo "  make shell      - Open Django shell"
	@echo "  make superuser  - Create superuser"
	@echo "  make collectstatic - Collect static files"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting (flake8)"
	@echo "  make format     - Format code (black)"
	@echo "  make clean      - Remove __pycache__ files"

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

shell:
	$(MANAGE) shell

superuser:
	$(MANAGE) createsuperuser

collectstatic:
	$(MANAGE) collectstatic --noinput

test:
	$(MANAGE) test

lint:
	flake8 .

format:
	black .

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete