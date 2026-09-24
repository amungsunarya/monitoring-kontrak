help:
	@echo "install / dev / prod / init-db / create-admin / sync-sheets / scheduler / backup / test / docker-up"

install:
	pip install -r requirements.txt

dev:
	python run.py

prod:
	gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app

init-db:
	flask init-db

create-admin:
	flask create-admin

sync-sheets:
	flask sync-sheets

scheduler:
	python -m scheduler.runner

backup:
	python scripts/backup.py

test:
	pytest tests/ -v

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d