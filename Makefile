
app:
	python manage.py runserver localhost:4020

migrate:
	python manage.py makemigrations && python manage.py migrate

build:
	docker build -t registry.gitlab.com/d6763/backend-core:latest .

push:
	docker push registry.gitlab.com/d6763/backend-core:latest