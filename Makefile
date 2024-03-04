install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

migration:
	python manage.py  makemigrations

migrate:
	python manage.py migrate

superuser:
	python manage.py createsuperuser
