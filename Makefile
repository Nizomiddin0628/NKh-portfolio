.PHONY: install dev migrate seed admin messages test lint static

install:
	pip install -r requirements-dev.txt
	cp -n .env.example .env || true

dev:
	python manage.py runserver

migrate:
	python manage.py makemigrations && python manage.py migrate

seed:
	python manage.py seed

admin:
	python manage.py createsuperuser

messages:      ## .po -> .mo (gettext talab qilinmaydi)
	python scripts/compile_po.py

static:
	python manage.py collectstatic --noinput

test:
	pytest

lint:
	ruff check .

setup: install migrate seed messages
	@echo ""
	@echo "Tayyor. Endi:  make admin   keyin:  make dev"
