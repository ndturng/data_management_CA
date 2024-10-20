# Makefile for Django Project Management

# Variables
VENV_PATH=venv/bin/activate
DJANGO_MANAGE=python manage.py
MYSQL_SERVICE=mysql

# Start the MySQL service
start-mysql:
	  sudo service $(MYSQL_SERVICE) start

# Connect to MySQL
connect-mysql:
	  mysql -u root -p

# Activate the virtual environment
activ-env:
	  source $(VENV_PATH)

# Run Django development server
runserver:
	  $(DJANGO_MANAGE) runserver

# Run Django migrations
migrate:
	  $(DJANGO_MANAGE) migrate

# Make migrations
makemigrations:
	  $(DJANGO_MANAGE) makemigrations

# Create a superuser
createsuperuser:
	  $(DJANGO_MANAGE) createsuperuser

# Check Django project
check:
	  $(DJANGO_MANAGE) check

# start mysql service and run the server
start: start-mysql runserver

# active virtual environment
# active_env:
# 	source venv/bin/activate