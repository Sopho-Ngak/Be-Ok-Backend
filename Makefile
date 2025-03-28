install:
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

shell:
	python manage.py shell

all: install migration migrate
