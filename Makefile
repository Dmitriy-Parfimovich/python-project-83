PORT ?= 8000
start:
	poetry run gunicorn -w 1 -b 0.0.0.0:$(PORT) page_analyzer:app

all: db-create schema-load

dev-setup: db-reset schema-load

db-create:
	createdb mydb || echo 'skip'

db-reset:
	dropdb mydb || true
	createdb mydb

schema-load:
	psql mydb < database.sql

connect:
	psql -d mydb

install:
		poetry install

lint:
	poetry run flake8 page_analyzer

dev:
	poetry run flask --app page_analyzer:app --debug run

test:
	poetry run pytest -s tests/