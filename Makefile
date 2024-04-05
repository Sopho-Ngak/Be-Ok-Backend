install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

migration:
	python manage.py  makemigrations

migrate:
	python manage.py migrate

run:
	python manage.py runserver

all-migrate: migration migrate

superuser:
	python manage.py createsuperuser

all: install migration migrate
