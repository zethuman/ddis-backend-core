
app:
	python manage.py runserver localhost:4020

migrate:
	python manage.py makemigrations && python manage.py migrate