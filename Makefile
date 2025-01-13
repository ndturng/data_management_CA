include .env

# Makefile for Django Project Management
# Variables
DJANGO_MANAGE=python manage.py
MYSQL_SERVICE=mysql

BACKUP_DIR="./backups"
TIMESTAMP="$(shell date +%Y%m%d_%H%M%S)"

# Create the backup file
backup-db:
	@echo "Backing up database $(DB_NAME)..."
	@mkdir -p "$(BACKUP_DIR)"
	
	@mysqldump -u $(DB_USER) -p$(DB_PASSWORD) -h $(DB_HOST) -P $(DB_PORT) $(DB_NAME) > $(BACKUP_DIR)/$(DB_NAME)_$(TIMESTAMP).sql

	@echo "Backup complete. File saved to $(BACKUP_DIR)/$(DB_NAME)_$(TIMESTAMP).sql"

# Restore the database from backup file # working on this
restore-db:
	@echo "Restoring database $(DB_NAME) from backup..."
	sudo mysql -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) < $(BACKUP_FILE)
	@echo "Database $(DB_NAME) has been restored."
	

# Drop and recreate the database
reset-db:
	@echo "Dropping database $(DB_NAME)..."
	@mysql -u $(DB_USER) -p$(DB_PASSWORD) -h $(DB_HOST) -P $(DB_PORT) -e "DROP DATABASE IF EXISTS $(DB_NAME);"

	@echo "Creating database $(DB_NAME)..."
	@mysql -u $(DB_USER) -p$(DB_PASSWORD) -h $(DB_HOST) -P $(DB_PORT) -e "CREATE DATABASE $(DB_NAME);"
	@echo "Database $(DB_NAME) has been recreated."


	@echo "Granting privileges to user '$(DB_USER)'..."
	@sudo mysql -u root -e "GRANT ALL PRIVILEGES ON $(DB_NAME).* TO '$(DB_USER)'@'localhost'; FLUSH PRIVILEGES;"


	@echo "Running migrations..."
	$(DJANGO_MANAGE) makemigrations
	$(DJANGO_MANAGE) migrate

	@echo "Creating superuser..."
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('${USER_NAME}', '${USER_EMAIL}', '${USER_PASS}')" | python manage.py shell

	@echo "Database reset complete."


# Start the MySQL service
start-mysql:
	  sudo service $(MYSQL_SERVICE) start

# Connect to MySQL
connect-mysql:
	  mysql -u root -p

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

# start the tailwind watch
tailwind:
	cd theme/static_src && npm run dev