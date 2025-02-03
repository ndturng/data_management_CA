# data_management_CA
 This project aim to create a web application that allows users to manage the data of police officers. The application will <br> allow users to view, add, update, and delete the data of police officers. The application will also provide a search functionality <br> to search for police officers based on different criteria. Besides, the application also stores the images, PDFs related to the <br> specific police officer.

## I. Setup Development Environment (with Internet Connection)
### 1. Install Python
  - Ensure that Python 3.10.13 (or a compatible version)
  - Check the version of Python:
      ```python --version```

### 2. Install dependencies
  - For development, install the dependencies in the `requirements-dev.txt` file:
  ```pip install -r requirements-dev.txt```
<br>
  - For production, install the dependencies in the `requirements.txt` file:
  ```pip install -r requirements.txt```


### 3. Install MySQL server
  Install using the following commands:
    ```sudo apt-get update```
    ```sudo apt-get install mysql-server```


### 4. Set Up MySQL Database
  ##### - Start the MySQL server:
  ```sudo service mysql start```
  ##### - Connect to the MySQL server:
  ```sudo mysql -u root -p```
  ##### - Create Database and User:
  - In the MySQL shell, run the following commands:
    - For Localhost Connection:
          - `CREATE DATABASE OFFICERS_TABLE;`
          - `CREATE USER 'manager'@'localhost' IDENTIFIED BY 'manager@123';`
          - `GRANT ALL PRIVILEGES ON OFFICERS_TABLE.* TO 'manager'@'localhost';`
          - `FLUSH PRIVILEGES;`
          - `EXIT;`
<br>
    - For TCP/IP Connection:
          - `CREATE DATABASE OFFICERS_TABLE;`
          - `CREATE USER 'manager'@'127.0.0.1' IDENTIFIED BY 'manager@123';`
          - `GRANT ALL PRIVILEGES ON OFFICERS_TABLE.* TO 'manager'@'127.0.0.1';`
          - `FLUSH PRIVILEGES;`
          - `EXIT;`

### 5. Run the Django migrations
  ##### - Apply the database migrations to set up the schema:
  - Make Migrations:
  ```make makemigrations``` 
  or 
  ```python manage.py makemigrations```
<br>
  - Apply Migrations:
  ```make migrate``` 
  or 
  ```python manage.py migrate```

### 6. Run the Django server
  - Run the Django server:
    ```make start``` 
    or 
    ```python manage.py runserver```

### 7. Create a superuser
  Create a superuser to access the Django admin panel and login to the application.

  - Create a superuser:
  ```python manage.py createsuperuser```
<br>
  - Enter the required details:
    - Username
    - Email
    - Password
  
### 8. Access the application
- Django Admin Panel:
```http://127.0.0.1:8000/admin/```

- Access the application:
```http://127.0.0.1:8000/officers/```


## II. Setup Development Environment (without Internet Connection - Offline - Production)
### 1. Clone the repository
  - Clone the repository to the local system
  - Or download the repository as a zip file and extract it to the local system.
  - 
### 2. Prepare packages
  - Download the Python installer for 3.10.13 (or a compatible version).   
<br>

  - Download the dependencies:
  ```pip download -r requirements.txt -d packages```
    The packages will be downloaded to the `packages` directory.
<br>

  - Download MySQL server installer:
  https://dev.mysql.com/downloads/mysql/
    - Make sure to download the correct version 8.0.41 or compatible version.
    - Choose the appropriate installer: `Windows (x86, 64-bit), ZIP Archive`

### 3. Install Python
  - Install Python 3.10.13 (or a compatible version)
  - Check the version of Python:
      ```python --version```

### 4. Create a virtual environment and install dependencies
  - Create a virtual environment to isolate the dependencies:
  ```python -m venv prod_venv```
<br>

  - Activate the virtual environment:
  ```source prod_venv/bin/activate```
    - For Windows, run this command to temporarily allow the execution of the script for the current session:
      ```Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass```
<br>
    - Run the following command to activate the virtual environment:
      ```.\prod_venv\Scripts\Activate```

  - Install the dependencies from the downloaded packages:
  ```pip install --no-index --find-links=packages -r requirements.txt```
    Replace `packages` with the path to the downloaded packages.

### 5. Install MySQL server
  - Install MySQL server:
    - Extract the downloaded MySQL server ZIP archive.
  - Initialize the database:
    - Run the following command:
      ```bin\mysqld --initialize-insecure```
      
  - Start the MySQL server:
      ```bin\mysqld -u root```

Change the path to the `bin` directory where the `mysqld.exe` executable is located, the `bin` directory is located in the extracted MySQL server directory.
  - In the MySQL shell, run the following commands:
    - For Localhost Connection:
          - `CREATE DATABASE OFFICERS_TABLE;`
          - `CREATE USER 'manager'@'localhost' IDENTIFIED BY 'manager@123';`
          - `GRANT ALL PRIVILEGES ON OFFICERS_TABLE.* TO 'manager'@'localhost';`
          - `FLUSH PRIVILEGES;`
          - `EXIT;`


### 6. Run the Django migrations
  Apply the database migrations to set up the schema:
  - Make Migrations:
  ```python manage.py makemigrations```
<br>
  - Apply Migrations:
  ```python manage.py migrate```

### 7. Create a superuser
  Create a superuser to access the Django admin panel and login to the application.

  - Create a superuser:
  ```python manage.py createsuperuser```

## III. NOTICE:
### 1. Replace the following in the `settings.py` file:
  - Add the IP address of the machine that will host the app (use the commnad: ipconfig,...)
    - `ALLOWED_HOSTS = [ '127.0.0.1', 'localhost', '192.168.1.10'] `
    - This allows the Django app to be accessed from the specified IP address.
    - To check the IP address of the machine, run the following command:
      - `ipconfig` (Windows)
      - `ifconfig` (Linux)
<br>
  - Update the database settings:
    - ```DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': 'OFFICERS_TABLE',
                    'USER': 'manager',
                    'PASSWORD': 'manager@123',
                    'HOST': '127.0.0.1',
                    'PORT': '3306',
                }
            }
  
#### 2. Add the bat file to run the server (Windows)
Create a bat file start_app.bat with the following content:

```@echo off

REM -------- Start MySQL Server --------
echo Starting MySQL Server...
start "DATA Server" /min "D:\Project\Data_Manager_CA\Installer\mysql-8.0.41-winx64\bin\mysqld.exe"

REM Wait for MySQL to start
timeout /t 5 /nobreak >nul

REM -------- Activate Virtual Environment --------
echo Activating virtual environment...
call D:\Project\Data_Manager_CA\Installer\data_management_CA-main\prod_env\Scripts\activate

REM -------- Navigate to the Django Project Folder --------
echo Changing directory to Django project...
cd D:\Project\Data_Manager_CA\Installer\data_management_CA-main

REM -------- Start Django Server --------
echo Starting Django server...
python manage.py runserver 0.0.0.0:8000

REM Pause to keep the terminal window open
pause
